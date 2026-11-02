"""Historical sample handling for Health Bridge.

Home Assistant cannot backfill normal entity state history through an
integration, so historical HealthKit samples are imported as long-term
statistics for the sensor entity that represents that metric.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, METRICS

_LOGGER = logging.getLogger(__name__)

# How long to wait for the sensor platform to register entities before giving up
# on the statistics import for a request.
_ENTITY_WAIT_ATTEMPTS = 20
_ENTITY_WAIT_SECONDS = 0.1

# The recorder summarises each hour into long-term statistics at the top of the
# following hour. Importing an hour it has already written violates the unique
# constraint on statistics(metadata_id, start_ts), and because the recorder
# inserts a whole batch in one transaction that collision discards the hour for
# every statistic, not just this integration's. Only import hours the recorder
# has certainly finished with.
_STATISTICS_SETTLE_TIME = timedelta(hours=2)


@dataclass(frozen=True, slots=True)
class HistorySample:
    """A timestamped historical value."""

    timestamp: datetime
    value: float | int
    unit: str | None


@dataclass(frozen=True, slots=True)
class HistoryMetric:
    """A metric's historical samples plus the unit to use."""

    unit: str | None
    samples: tuple[HistorySample, ...]

    @property
    def latest(self) -> HistorySample:
        """Return the newest sample."""
        return max(self.samples, key=lambda sample: sample.timestamp)


def isoformat(value: datetime) -> str:
    """Return a UTC ISO 8601 timestamp."""
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def build_hourly_statistics(
    samples: tuple[HistorySample, ...],
) -> list[dict[str, Any]]:
    """Collapse arbitrary samples into one mean value per UTC hour."""
    buckets: dict[datetime, list[float]] = {}

    for sample in samples:
        start = sample.timestamp.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
        buckets.setdefault(start, []).append(float(sample.value))

    return [
        {
            "start": start,
            "mean": sum(values) / len(values),
        }
        for start, values in sorted(buckets.items())
    ]


def _importable_hours(
    statistics: list[dict[str, Any]],
    existing: set[tuple[str, float]],
    *,
    statistic_id: str,
    cutoff: datetime,
) -> list[dict[str, Any]]:
    """Drop hours the recorder has already summarised, or is still filling."""
    cutoff_ts = cutoff.timestamp()
    return [
        row
        for row in statistics
        if row["start"].timestamp() <= cutoff_ts
        and (statistic_id, row["start"].timestamp()) not in existing
    ]


async def _existing_hours(
    hass: HomeAssistant,
    statistic_ids: set[str],
    *,
    since: datetime,
    cutoff: datetime,
) -> set[tuple[str, float]] | None:
    """Return the (statistic_id, start_ts) rows the recorder already holds.

    ``since`` is the oldest hour in the payload and ``cutoff`` the newest hour
    that may be imported, so the query stays bounded without guessing how far
    back a payload can reach.

    Returns None when the recorder is unavailable, in which case the caller must
    not import anything.
    """
    if not statistic_ids:
        return set()

    try:
        from homeassistant.components.recorder import get_instance
        from homeassistant.components.recorder.db_schema import Statistics, StatisticsMeta
    except ImportError:  # pragma: no cover - recorder internals unavailable
        return None

    def _query(session: Any) -> set[tuple[str, float]]:
        rows = (
            session.query(StatisticsMeta.statistic_id, Statistics.start_ts)
            .join(Statistics, Statistics.metadata_id == StatisticsMeta.id)
            .filter(
                StatisticsMeta.statistic_id.in_(sorted(statistic_ids)),
                Statistics.start_ts >= since.timestamp(),
                Statistics.start_ts <= cutoff.timestamp(),
            )
        )
        return {(statistic_id, float(start_ts)) for statistic_id, start_ts in rows}

    try:
        return await get_instance(hass).async_add_executor_job(_query)
    except Exception:  # pragma: no cover - recorder not running
        _LOGGER.debug("Recorder unavailable; skipping history statistics", exc_info=True)
        return None


async def async_import_history(
    hass: HomeAssistant, entry: ConfigEntry, history: dict[str, HistoryMetric]
) -> None:
    """Import history as long-term statistics for the sensor entities.

    The sensor platform creates entities lazily when the first value arrives.
    Wait briefly for those registry entries, then import the historical hours
    the recorder has not already summarised.
    """
    if not history:
        return

    registry = er.async_get(hass)
    entity_ids: dict[str, str] = {}
    pending = set(history)

    for _ in range(_ENTITY_WAIT_ATTEMPTS):
        for key in pending:
            entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
            if entity_id is not None:
                entity_ids[key] = entity_id
        pending.difference_update(entity_ids)
        if not pending:
            break
        await asyncio.sleep(_ENTITY_WAIT_SECONDS)

    if pending:
        _LOGGER.debug(
            "Skipping history import for metrics without sensor entities: %s",
            ", ".join(sorted(pending)),
        )

    try:
        from homeassistant.components.recorder.statistics import (
            STATISTIC_UNIT_TO_UNIT_CONVERTER,
            async_import_statistics,
        )
    except ImportError:
        _LOGGER.warning(
            "Home Assistant recorder statistics API is unavailable; "
            "historical samples were not imported"
        )
        return

    # mean_type/unit_class were added after HA 2024.1. Keep the older
    # has_mean metadata shape for older installations.
    try:
        from homeassistant.components.recorder.models import (
            StatisticMeanType,
        )
    except ImportError:
        StatisticMeanType = None  # type: ignore[assignment,misc]

    cutoff = datetime.now(UTC) - _STATISTICS_SETTLE_TIME

    # Build every metric's hourly buckets once, so the recorder query can be
    # bounded by the oldest hour actually present in the payload.
    candidates: dict[str, list[dict[str, Any]]] = {}
    oldest: datetime | None = None
    for key, metric in history.items():
        if entity_ids.get(key) is None:
            continue
        rows = build_hourly_statistics(metric.samples)
        if not rows:
            continue
        candidates[key] = rows
        first = min(row["start"] for row in rows)
        if oldest is None or first < oldest:
            oldest = first

    if not candidates:
        return

    assert oldest is not None
    existing = await _existing_hours(hass, set(entity_ids.values()), since=oldest, cutoff=cutoff)
    if existing is None:
        _LOGGER.debug(
            "Recorder statistics unavailable; skipping historical import for %s",
            entry.title,
        )
        return

    for key, metric in history.items():
        entity_id = entity_ids.get(key)
        if entity_id is None:
            continue

        statistics = _importable_hours(
            candidates.get(key, []),
            existing,
            statistic_id=entity_id,
            cutoff=cutoff,
        )
        if not statistics:
            continue

        definition = METRICS.get(key)
        name = definition.name if definition is not None else key.replace("_", " ").title()

        metadata = {
            "has_mean": True,
            "has_sum": False,
            "name": f"{entry.title} {name}",
            "source": "recorder",
            "statistic_id": entity_id,
            "unit_of_measurement": metric.unit,
        }
        if StatisticMeanType is not None:
            converter = STATISTIC_UNIT_TO_UNIT_CONVERTER.get(metric.unit)
            metadata["mean_type"] = StatisticMeanType.ARITHMETIC
            metadata["unit_class"] = converter.UNIT_CLASS if converter is not None else None

        try:
            async_import_statistics(hass, metadata, statistics)
        except Exception:
            _LOGGER.exception("Could not import historical statistics for %s", key)

    _LOGGER.debug(
        "Imported historical statistics for %s metric(s) on %s",
        len(entity_ids),
        entry.title,
    )
