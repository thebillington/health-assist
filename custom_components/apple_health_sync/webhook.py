"""Webhook parsing and validation for Apple Health Sync."""

from __future__ import annotations

import hmac
import json
import logging
import math
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any

from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .const import (
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

    body = await request.content.read(MAX_PAYLOAD_BYTES + 1)
    if len(body) > MAX_PAYLOAD_BYTES:
        _LOGGER.warning("Rejected Apple Health webhook larger than %s bytes", MAX_PAYLOAD_BYTES)
        return _error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "payload too large")

    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        _LOGGER.debug("Rejected Apple Health webhook with invalid JSON")
        return _error(HTTPStatus.BAD_REQUEST, "invalid JSON")

    if not isinstance(payload, dict):
        return _error(HTTPStatus.BAD_REQUEST, "payload must be a JSON object")

    raw_metrics = payload.get("metrics")
    if not isinstance(raw_metrics, dict) or not raw_metrics:
        return _error(HTTPStatus.BAD_REQUEST, "missing or invalid 'metrics' object")

    if len(raw_metrics) > MAX_METRICS_PER_PAYLOAD:
        return _error(HTTPStatus.BAD_REQUEST, "too many metrics in payload")

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
    except InvalidPayload as err:
        _LOGGER.debug("Rejected Apple Health webhook: %s", err)
        return _error(HTTPStatus.BAD_REQUEST, str(err))

    accepted = len(values)
    store.update(
        values,
        device_id=device_id,
        device_name=device_name,
        received_at=received_at,
    )

    if values:
        async_dispatcher_send(hass, signal_new_data(entry.entry_id), set(values))

    _LOGGER.debug(
        "Apple Health webhook for entry %s: %s metric(s) accepted, %s ignored",
        entry.entry_id,
        accepted,
        ignored,
    )
    return web.json_response(
        {
            "status": "ok",
            "accepted": accepted,
            "ignored": ignored,
        }
    )


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
    if not isinstance(raw_timestamp, str) or not raw_timestamp.strip():
        return None

    text = raw_timestamp.strip()
    if text.endswith(("Z", "z")):
        text = f"{text[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        _LOGGER.debug("Ignoring invalid timestamp in Apple Health payload")
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


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
