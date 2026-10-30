"""Set up the Apple Health Sync integration."""

from __future__ import annotations

import logging

from aiohttp.hdrs import METH_POST
from aiohttp.web import Request, Response
from homeassistant.components import webhook as ha_webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_WEBHOOK_ID, DOMAIN
from .store import HealthDataStore
from .webhook import async_handle_webhook

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one iPhone/iPad from a config entry."""
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    store = HealthDataStore(entry.entry_id)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = store

    async def _handle_webhook(
        hass: HomeAssistant,
        _webhook_id: str,
        request: Request,
    ) -> Response:
        return await async_handle_webhook(hass, entry, store, request)

    try:
        ha_webhook.async_register(
            hass,
            DOMAIN,
            entry.title,
            webhook_id,
            _handle_webhook,
            allowed_methods=[METH_POST],
        )
    except ValueError:
        _LOGGER.exception("Could not register the Apple Health webhook")
        hass.data[DOMAIN].pop(entry.entry_id, None)
        return False

    unsub_update = entry.add_update_listener(_async_update_listener)
    entry.async_on_unload(unsub_update)

    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        unsub_update()
        ha_webhook.async_unregister(hass, webhook_id)
        hass.data[DOMAIN].pop(entry.entry_id, None)
        raise

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when the secret or metric allow-list changes."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and stop accepting data for it."""
    ha_webhook.async_unregister(hass, entry.data[CONF_WEBHOOK_ID])

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
