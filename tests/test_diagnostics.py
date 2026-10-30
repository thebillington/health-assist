"""Tests for the redacted diagnostics dump."""

from __future__ import annotations

import json

from homeassistant.core import HomeAssistant

from custom_components.apple_health_sync.const import CONF_SECRET, CONF_WEBHOOK_ID
from custom_components.apple_health_sync.diagnostics import (
    REDACTED,
    async_get_config_entry_diagnostics,
)

from .helpers import TEST_SECRET, TEST_WEBHOOK_ID, make_entry, post_payload, setup_entry


async def test_diagnostics_are_redacted(hass: HomeAssistant) -> None:
    """Secrets, the webhook id, device identifiers and values are redacted."""
    entry = make_entry()
    await setup_entry(hass, entry)

    await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "device_id": "iphone-abc123",
            "device_name": "Simon's iPhone",
            "metrics": {"weight": {"value": 72.4, "unit": "kg"}},
        },
    )
    await hass.async_block_till_done()

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    serialized = json.dumps(diagnostics)

    assert diagnostics["entry"]["data"][CONF_SECRET] == REDACTED
    assert diagnostics["entry"]["data"][CONF_WEBHOOK_ID] == REDACTED
    assert diagnostics["store"]["last_device_id"] == REDACTED
    assert diagnostics["store"]["last_device_name"] == REDACTED
    assert diagnostics["store"]["metrics"]["weight"]["value"] == REDACTED
    assert diagnostics["store"]["metrics"]["weight"]["device_id"] == REDACTED
    assert diagnostics["store"]["metrics"]["weight"]["device_name"] == REDACTED
    assert diagnostics["store"]["metrics"]["weight"]["unit"] == "kg"

    assert TEST_SECRET not in serialized
    assert TEST_WEBHOOK_ID not in serialized
    assert "iphone-abc123" not in serialized
    assert "Simon's iPhone" not in serialized
    assert "72.4" not in serialized
