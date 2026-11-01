"""Helpers shared by the Health Bridge tests."""

from __future__ import annotations

import json
from typing import Any

from homeassistant.components.webhook import async_handle_webhook
from homeassistant.core import HomeAssistant
from homeassistant.util.aiohttp import MockRequest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.apple_health_sync.const import (
    CONF_METRICS,
    CONF_SECRET,
    CONF_WEBHOOK_ID,
    DOMAIN,
)

TEST_SECRET = "correct horse battery staple"
TEST_WEBHOOK_ID = "test-webhook-id"


def make_entry(
    *,
    webhook_id: str = TEST_WEBHOOK_ID,
    title: str = "Test Phone",
    secret: str = TEST_SECRET,
    metrics: list[str] | None = None,
    entry_id: str | None = None,
) -> MockConfigEntry:
    """Create a config entry for a test."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=title,
        data={
            CONF_WEBHOOK_ID: webhook_id,
            CONF_SECRET: secret,
            CONF_METRICS: metrics or [],
        },
        unique_id=webhook_id,
        entry_id=entry_id,
    )


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Add and set up a config entry."""
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def post_payload(
    hass: HomeAssistant,
    webhook_id: str,
    payload: Any,
    *,
    secret: str | None = TEST_SECRET,
    method: str = "POST",
):
    """Post a payload through the real Home Assistant webhook dispatcher."""
    if isinstance(payload, (dict, list)):
        body = json.dumps(payload).encode("utf-8")
    elif isinstance(payload, str):
        body = payload.encode("utf-8")
    else:
        body = payload

    headers: dict[str, str] = {}
    if secret is not None:
        headers["X-Webhook-Secret"] = secret

    request = MockRequest(
        content=body,
        mock_source="test",
        method=method,
        headers=headers,
    )
    return await async_handle_webhook(hass, webhook_id, request)
