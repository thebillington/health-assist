"""Diagnostics support for Health Assist."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_METRICS, CONF_SECRET, CONF_WEBHOOK_ID, DOMAIN

REDACTED = "**REDACTED**"


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return a redacted diagnostic dump."""
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    data = dict(entry.data)
    if CONF_SECRET in data:
        data[CONF_SECRET] = REDACTED
    if CONF_WEBHOOK_ID in data:
        data[CONF_WEBHOOK_ID] = REDACTED

    options = dict(entry.options)
    if CONF_SECRET in options:
        options[CONF_SECRET] = REDACTED

    diagnostics: dict[str, Any] = {
        "entry": {
            "title": entry.title,
            "data": data,
            "options": options,
        },
        "store": {
            "loaded": store is not None,
            "metrics": {},
            "last_payload_at": None,
            "last_device_id": None,
            "last_device_name": None,
        },
    }

    if store is None:
        return diagnostics

    diagnostics["store"]["last_payload_at"] = store.last_payload_at
    diagnostics["store"]["last_device_id"] = REDACTED if store.last_device_id is not None else None
    diagnostics["store"]["last_device_name"] = (
        REDACTED if store.last_device_name is not None else None
    )
    diagnostics["store"]["metrics"] = {
        key: {
            "value": REDACTED,
            "unit": value.unit,
            "last_sync": value.last_sync,
            "received_at": value.received_at,
            "device_id": REDACTED if value.device_id is not None else None,
            "device_name": REDACTED if value.device_name is not None else None,
            "generic": value.generic,
        }
        for key, value in store.values.items()
    }
    diagnostics["store"]["allow_list"] = list(
        entry.options.get(CONF_METRICS, entry.data.get(CONF_METRICS, []))
    )
    return diagnostics
