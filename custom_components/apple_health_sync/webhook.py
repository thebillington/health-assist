"""Webhook parsing and validation for Health Bridge."""

from __future__ import annotations

import hmac
import json
import logging
import math
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from typing import Any

from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .const import (
    MAX_HISTORY_SAMPLES,
    MAX_METRIC_KEY_LENGTH,
    MAX_METRICS_PER_PAYLOAD,
    MAX_PAYLOAD_BYTES,
    MAX_TEXT_LENGTH,
    MAX_UNIT_LENGTH,
    METRICS,
    SECRET_HEADER,
    signal_new_data,
)
from .helpers import get_entry_secret, metric_is_allowed
from .history import HistoryMetric, HistorySample, async_import_history, isoformat
from .store import HealthDataStore, MetricValue

_LOGGER = logging.getLogger(__name__)


class InvalidPayload(ValueError):
    """Raised when a webhook payload does not match the contract."""


async def async_handle_webhook(
    hass: HomeAssistant,
    entry: ConfigEntry,
    store: HealthDataStore,
    request: web.Request,
) -> web.Response:
    """Handle an incoming Apple Health payload.

    The webhook ID is treated as a credential by Home Assistant. An additional
    shared secret can be required with the X-Webhook-Secret header.
    """
    secret = get_entry_secret(entry)
    if secret and not _secret_matches(request, secret):
        _LOGGER.warning("Rejected Apple Health webhook with an invalid secret")
        return _error(HTTPStatus.UNAUTHORIZED, "invalid secret")

    # Check Content-Length first so oversized bodies are rejected before being
    # read into memory. Chunked requests are capped by reading at most one byte
    # beyond the limit below.
    content_length = getattr(request, "content_length", None)
    if content_length is not None and content_length > MAX_PAYLOAD_BYTES:
        _LOGGER.warning("Rejected Apple Health webhook larger than %s bytes", MAX_PAYLOAD_BYTES)
        return _error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "payload too large")

    # Read in bounded chunks until EOF. A single StreamReader.read(n) can
    # return less than n for a large/chunked request through a reverse proxy,
    # which would otherwise truncate the JSON body.
    chunks: list[bytes] = []
    remaining = MAX_PAYLOAD_BYTES + 1
    content = request.content
    while remaining > 0:
        chunk = await content.read(min(remaining, 64 * 1024))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    body = b"".join(chunks)
    if len(body) > MAX_PAYLOAD_BYTES:
        _LOGGER.warning("Rejected Apple Health webhook larger than %s bytes", MAX_PAYLOAD_BYTES)
        return _error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "payload too large")

    try:
        payload = json.loads(body)
    except (ValueError, RecursionError):
        # ValueError covers JSONDecodeError, invalid UTF-8 and integers that
        # exceed Python's digit limit; RecursionError covers deeply nested JSON.
        _LOGGER.debug("Rejected Apple Health webhook with invalid JSON")
        return _error(HTTPStatus.BAD_REQUEST, "invalid JSON")

    if not isinstance(payload, dict):
        return _error(HTTPStatus.BAD_REQUEST, "payload must be a JSON object")

    raw_metrics = payload.get("metrics", {})
    raw_history = payload.get("history", {})
    if not isinstance(raw_metrics, dict) or not isinstance(raw_history, dict):
        return _error(HTTPStatus.BAD_REQUEST, "invalid metrics or history object")
    if not raw_metrics and not raw_history:
        return _error(
            HTTPStatus.BAD_REQUEST,
            "missing metrics/history: provide 'metrics' or 'history'",
        )
    if len(raw_metrics) > MAX_METRICS_PER_PAYLOAD:
        return _error(HTTPStatus.BAD_REQUEST, "too many metrics in payload")
    if len(raw_history) > MAX_METRICS_PER_PAYLOAD:
        return _error(HTTPStatus.BAD_REQUEST, "too many history metrics in payload")

    received_at = _utc_now_iso()
    last_sync = _parse_timestamp(payload.get("timestamp")) or received_at
    device_id = _clean_text(payload.get("device_id"), MAX_TEXT_LENGTH)
    device_name = _clean_text(payload.get("device_name"), MAX_TEXT_LENGTH)

    try:
        values, ignored = _parse_metrics(
            raw_metrics,
            entry=entry,
            received_at=received_at,
            last_sync=last_sync,
            device_id=device_id,
            device_name=device_name,
        )
        history, history_values, history_ignored = _parse_history(
            raw_history,
            entry=entry,
            received_at=received_at,
            device_id=device_id,
            device_name=device_name,
            existing_units={key: value.unit for key, value in values.items()},
        )
    except InvalidPayload as err:
        _LOGGER.debug("Rejected Apple Health webhook: %s", err)
        return _error(HTTPStatus.BAD_REQUEST, str(err))

    ignored += history_ignored
    # A live metrics snapshot wins over the latest historical value; a
    # history-only request uses the latest sample to create/update sensors.
    for key, value in history_values.items():
        values.setdefault(key, value)

    updated = store.update(
        values,
        device_id=device_id,
        device_name=device_name,
        received_at=received_at,
    )
    accepted = len(updated)

    if updated:
        async_dispatcher_send(hass, signal_new_data(entry.entry_id), updated)
    if history:

        async def _import() -> None:
            # Serialise history imports for this entry. Two overlapping
            # exports must not write the same hours at the same time.
            async with store.history_lock:
                await async_import_history(hass, entry, history)

        entry.async_create_task(hass, _import(), "apple_health_sync history")

    _LOGGER.debug(
        "Apple Health webhook for entry %s: %s metric(s) accepted, %s ignored, "
        "%s history metric(s)",
        entry.entry_id,
        accepted,
        ignored,
        len(history),
    )
    result: dict[str, Any] = {
        "status": "ok",
        "accepted": accepted,
        "ignored": ignored,
    }
    if history:
        result["history"] = {
            "metrics": len(history),
            "samples": sum(len(metric.samples) for metric in history.values()),
        }
    return web.json_response(result)


def _parse_metrics(
    raw_metrics: dict[str, Any],
    *,
    entry: ConfigEntry,
    received_at: str,
    last_sync: str,
    device_id: str | None,
    device_name: str | None,
) -> tuple[dict[str, MetricValue], int]:
    """Validate and normalize all metrics in a payload."""
    values: dict[str, MetricValue] = {}
    ignored = 0
    seen: set[str] = set()

    for raw_key, raw_metric in raw_metrics.items():
        key = _normalize_metric_key(raw_key)
        if key is None:
            ignored += 1
            _LOGGER.debug("Ignored metric with an unusable key")
            continue

        parsed = _parse_metric_value(raw_metric)
        if parsed is None:
            raise InvalidPayload(f"invalid value for metric '{key}'")
        value, payload_unit = parsed

        if key in seen:
            _LOGGER.warning("Duplicate metric key '%s' in payload; using last value", key)
        seen.add(key)

        if not metric_is_allowed(entry, key):
            ignored += 1
            _LOGGER.debug("Ignored metric '%s' because it is not in the allow-list", key)
            continue

        definition = METRICS.get(key)
        if definition is None:
            unit = payload_unit
            generic = True
            _LOGGER.debug(
                "Creating a generic sensor for unknown metric '%s' (unit=%s)",
                key,
                unit,
            )
        else:
            # The payload unit wins when supplied; the registry unit is the
            # documented fallback.
            unit = payload_unit or definition.unit
            generic = False

        values[key] = MetricValue(
            value=value,
            unit=unit,
            last_sync=last_sync,
            received_at=received_at,
            device_id=device_id,
            device_name=device_name,
            generic=generic,
        )

    return values, ignored


def _parse_metric_value(raw_metric: Any) -> tuple[float | int, str | None] | None:
    """Return a validated (value, unit) pair or None for an invalid entry."""
    if not isinstance(raw_metric, dict) or "value" not in raw_metric:
        return None

    value = raw_metric["value"]
    # bool is a subclass of int in Python, but is not a valid sensor value.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        if not math.isfinite(float(value)):
            return None
    except (OverflowError, ValueError):
        return None

    unit = raw_metric.get("unit")
    if unit is not None:
        if not isinstance(unit, str):
            return None
        unit = unit.strip()
        if (
            not unit
            or len(unit) > MAX_UNIT_LENGTH
            or any(ord(char) < 32 or ord(char) == 127 for char in unit)
        ):
            return None

    return value, unit


def _normalize_metric_key(raw_key: Any) -> str | None:
    """Slugify and bound a metric key so it can safely become an entity key."""
    if not isinstance(raw_key, str):
        return None
    key = slugify(raw_key, separator="_")[:MAX_METRIC_KEY_LENGTH].strip("_")
    return key or None


def _parse_timestamp(raw_timestamp: Any) -> str | None:
    """Parse an ISO 8601 timestamp and normalize it to UTC, if possible."""
    parsed = _parse_timestamp_datetime(raw_timestamp)
    if parsed is None:
        _LOGGER.debug("Ignoring invalid timestamp in Apple Health payload")
        return None
    return isoformat(parsed)


def _parse_timestamp_datetime(raw_timestamp: Any) -> datetime | None:
    """Parse an ISO 8601 timestamp into an aware UTC datetime."""
    if not isinstance(raw_timestamp, str) or not raw_timestamp.strip():
        return None

    text = raw_timestamp.strip()
    if text.endswith(("Z", "z")):
        text = f"{text[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    parsed = parsed.astimezone(UTC)
    # Reject timestamps that are clearly wrong. A far-future timestamp would
    # otherwise make the store ignore every later historical sample for that
    # metric until that date arrives.
    if parsed > datetime.now(UTC) + timedelta(days=1):
        return None
    return parsed


def _clean_text(raw_value: Any, max_length: int) -> str | None:
    """Return a trimmed, bounded string or None."""
    if not isinstance(raw_value, str):
        return None
    value = raw_value.strip()
    if not value:
        return None
    return value[:max_length]


def _secret_matches(request: web.Request, secret: str) -> bool:
    """Compare the optional shared secret in constant time."""
    provided = request.headers.get(SECRET_HEADER, "")
    return hmac.compare_digest(provided.encode("utf-8"), secret.encode("utf-8"))


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return dt_util.utcnow().isoformat().replace("+00:00", "Z")


def _error(status: HTTPStatus, message: str) -> web.Response:
    """Build a small JSON error response."""
    return web.json_response({"error": message}, status=status)


def _parse_history(
    raw_history: dict[str, Any],
    *,
    entry: ConfigEntry,
    received_at: str,
    device_id: str | None,
    device_name: str | None,
    existing_units: dict[str, str | None],
) -> tuple[dict[str, HistoryMetric], dict[str, MetricValue], int]:
    """Validate and normalize historical samples."""
    history: dict[str, HistoryMetric] = {}
    values: dict[str, MetricValue] = {}
    ignored = 0
    total_samples = 0

    for raw_key, raw_samples in raw_history.items():
        if not isinstance(raw_samples, list) or not raw_samples:
            raise InvalidPayload("history entries must be non-empty arrays")

        total_samples += len(raw_samples)
        if total_samples > MAX_HISTORY_SAMPLES:
            raise InvalidPayload("too many history samples in payload")

        key = _normalize_metric_key(raw_key)
        if key is None:
            ignored += 1
            _LOGGER.debug("Ignored history metric with an unusable key")
            continue

        definition = METRICS.get(key)
        unit = existing_units.get(key)
        if unit is None and definition is not None:
            unit = definition.unit

        samples: list[HistorySample] = []
        for raw_sample in raw_samples:
            parsed = _parse_history_sample(raw_sample)
            if parsed is None:
                raise InvalidPayload(f"invalid history sample for metric '{key}'")
            timestamp, value, sample_unit = parsed
            if unit is None:
                unit = sample_unit
            elif sample_unit is not None and sample_unit != unit:
                # Averaging values in different units would silently corrupt
                # the statistic, so reject the request instead.
                raise InvalidPayload(f"mixed units for history metric '{key}'")
            samples.append(
                HistorySample(
                    timestamp=timestamp,
                    value=value,
                    unit=sample_unit or unit,
                )
            )

        if not metric_is_allowed(entry, key):
            ignored += 1
            _LOGGER.debug(
                "Ignored history metric '%s' because it is not in the allow-list",
                key,
            )
            continue

        metric = HistoryMetric(unit=unit, samples=tuple(samples))
        history[key] = metric
        latest = metric.latest

        values[key] = MetricValue(
            value=latest.value,
            unit=latest.unit or unit,
            last_sync=isoformat(latest.timestamp),
            received_at=received_at,
            device_id=device_id,
            device_name=device_name,
            generic=definition is None,
            historical=True,
        )

    return history, values, ignored


def _parse_history_sample(raw_sample: Any) -> tuple[datetime, float | int, str | None] | None:
    """Return a validated (timestamp, value, unit) history sample."""
    if not isinstance(raw_sample, dict) or "timestamp" not in raw_sample:
        return None

    timestamp = _parse_timestamp_datetime(raw_sample["timestamp"])
    if timestamp is None:
        return None

    parsed_value = _parse_metric_value(
        {"value": raw_sample.get("value"), "unit": raw_sample.get("unit")}
    )
    if parsed_value is None:
        return None

    value, unit = parsed_value
    return timestamp, value, unit
