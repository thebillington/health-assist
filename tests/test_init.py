"""Tests for entry setup and teardown."""

from __future__ import annotations

from homeassistant.components import webhook as ha_webhook
from homeassistant.core import HomeAssistant

from .helpers import TEST_WEBHOOK_ID, make_entry, post_payload, setup_entry


async def test_webhook_is_registered_and_unregistered(hass: HomeAssistant) -> None:
    """The webhook exists only while the config entry is loaded."""
    entry = make_entry()
    await setup_entry(hass, entry)

    assert TEST_WEBHOOK_ID in hass.data[ha_webhook.DOMAIN]

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert TEST_WEBHOOK_ID not in hass.data[ha_webhook.DOMAIN]


async def test_reload_keeps_a_single_working_webhook(hass: HomeAssistant) -> None:
    """Reloading must not leave a duplicate webhook handler behind."""
    entry = make_entry()
    await setup_entry(hass, entry)

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert TEST_WEBHOOK_ID in hass.data[ha_webhook.DOMAIN]
    response = await post_payload(hass, TEST_WEBHOOK_ID, {"metrics": {"weight": {"value": 72.4}}})
    assert response.status == 200
