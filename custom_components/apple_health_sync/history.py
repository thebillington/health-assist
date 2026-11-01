"""Historical sample handling for Health Bridge.

Home Assistant cannot backfill normal entity state history through an
integration, so historical HealthKit samples are imported as long-term
statistics for the sensor entity that represents that metric.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
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


async def async_import_history(
    hass: HomeAssistant, entry: ConfigEntry, history: dict[str, HistoryMetric]
) -> None:
    """Import history as long-term statistics for the sensor entities.

    The sensor platform creates entities lazily when the first value arrives.
    Wait briefly for those registry entries, then import the historical hours.
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

    for key, metric in history.items():
        entity_id = entity_ids.get(key)
        if entity_id is None:
            continue

        statistics = build_hourly_statistics(metric.samples)
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
