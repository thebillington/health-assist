"""Config and options flows for Health Bridge."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import webhook as ha_webhook
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.network import NoURLAvailableError
from homeassistant.helpers.selector import ConstantSelector, ConstantSelectorConfig

try:  # QrCodeSelector was added after the integration's HA 2024.1 floor.
    from homeassistant.helpers.selector import (
        QrCodeSelector,
        QrCodeSelectorConfig,
    )

    QR_CODE_AVAILABLE = True
except ImportError:
    QR_CODE_AVAILABLE = False

from .const import (
    CONF_METRICS,
    CONF_QR_CODE,
    CONF_SECRET,
    CONF_WEBHOOK_ID,
    CONF_WEBHOOK_URL,
    DEFAULT_NAME,
    DOMAIN,
    METRIC_NAMES,
)
from .helpers import get_entry_metrics, get_entry_secret


def _build_webhook_url(hass, webhook_id: str) -> str:
    """Return the full webhook URL, or the path if HA cannot detect a URL."""
    try:
        return ha_webhook.async_generate_url(hass, webhook_id)
    except NoURLAvailableError:
        return ha_webhook.async_generate_path(webhook_id)


def _qr_field(webhook_url: str, secret: str) -> dict:
    """Return a display-only QR selector field when supported by this HA."""
    if not QR_CODE_AVAILABLE or not webhook_url.startswith(("http://", "https://")):
        return {}

    query = urlencode({"url": webhook_url, "secret": secret})
    data = f"applehealthsync://configure?{query}"
    return {vol.Optional(CONF_QR_CODE): QrCodeSelector(QrCodeSelectorConfig(data=data, scale=6))}


def _build_schema() -> vol.Schema:
    """Build the config flow schema."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_SECRET, default=""): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                )
            ),
            vol.Optional(CONF_METRICS, default=[]): cv.multi_select(METRIC_NAMES),
        }
    )


class AppleHealthSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle adding an Health Bridge device."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._pending_data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Collect the webhook name, optional secret and metric allow-list."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input.get(CONF_NAME, "")).strip()
            if not name:
                errors[CONF_NAME] = "name_required"
            else:
                webhook_id = ha_webhook.async_generate_id()
                await self.async_set_unique_id(webhook_id)
                self._pending_data = {
                    CONF_NAME: name,
                    CONF_WEBHOOK_ID: webhook_id,
                    CONF_SECRET: str(user_input.get(CONF_SECRET) or "").strip(),
                    CONF_METRICS: list(user_input.get(CONF_METRICS, [])),
                }
                return await self.async_step_webhook()

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(),
            errors=errors,
            description_placeholders={"metric_count": str(len(METRIC_NAMES))},
        )

    async def async_step_webhook(self, user_input: dict[str, Any] | None = None):
        """Show the generated webhook URL before creating the entry."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._pending_data[CONF_NAME],
                data=self._pending_data,
            )

        webhook_id = self._pending_data[CONF_WEBHOOK_ID]
        webhook_url = _build_webhook_url(self.hass, webhook_id)
        secret = self._pending_data[CONF_SECRET]

        schema = {
            vol.Optional(CONF_WEBHOOK_URL): ConstantSelector(
                ConstantSelectorConfig(label="Webhook URL", value=webhook_url)
            )
        }
        schema.update(_qr_field(webhook_url, secret))

        return self.async_show_form(
            step_id="webhook",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "webhook_url": webhook_url,
                "secret": secret or "Not set",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
    ) -> AppleHealthSyncOptionsFlow:
        """Return the options flow."""
        return AppleHealthSyncOptionsFlow()


class AppleHealthSyncOptionsFlow(config_entries.OptionsFlow):
    """Update the secret and metric allow-list without changing the URL."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the integration options."""
        # Using self.handler keeps this compatible with HA 2024.1, where
        # OptionsFlow did not yet expose a config_entry property.
        entry = self.hass.config_entries.async_get_entry(self.handler)
        if entry is None:
            return self.async_abort(reason="unknown_entry")

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SECRET: str(user_input.get(CONF_SECRET) or "").strip(),
                    CONF_METRICS: list(user_input.get(CONF_METRICS, [])),
                },
            )

        secret = get_entry_secret(entry)
        webhook_id = entry.data.get(CONF_WEBHOOK_ID)
        webhook_url = (
            _build_webhook_url(self.hass, str(webhook_id))
            if webhook_id is not None
            else "Not available"
        )

        schema: dict = {
            vol.Optional(CONF_WEBHOOK_URL): ConstantSelector(
                ConstantSelectorConfig(label="Webhook URL", value=webhook_url)
            ),
            vol.Optional(CONF_SECRET, default=secret): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                )
            ),
        }
        if webhook_id is not None:
            schema.update(_qr_field(webhook_url, secret))
        schema[vol.Optional(CONF_METRICS, default=get_entry_metrics(entry))] = cv.multi_select(
            METRIC_NAMES
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            description_placeholders={
                "metric_count": str(len(METRIC_NAMES)),
                "webhook_url": webhook_url,
            },
        )
