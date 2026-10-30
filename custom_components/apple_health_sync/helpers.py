"""Small helpers shared by the Apple Health Sync platforms."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry

from .const import CONF_METRICS, CONF_SECRET, METRICS


def get_entry_secret(entry: ConfigEntry) -> str:
    """Return the configured shared secret, if any.

    Options take precedence over the original config entry data so that the
    secret and allow-list can be changed later without recreating the entry and
    changing the webhook URL.
    """
    return str(entry.options.get(CONF_SECRET, entry.data.get(CONF_SECRET, ""))).strip()


def get_entry_metrics(entry: ConfigEntry) -> list[str]:
    """Return the configured metric allow-list.

    An empty list means "all canonical metrics are allowed".
    """
    metrics = entry.options.get(CONF_METRICS, entry.data.get(CONF_METRICS, []))
    return [str(key) for key in metrics]


def metric_is_allowed(entry: ConfigEntry, key: str) -> bool:
    """Return whether a metric may be exposed as an entity.

    The allow-list only applies to canonical metrics. Unknown metrics are
    accepted as generic sensors so the iOS app can add new Apple Health
    categories without requiring an integration update.
    """
    if key not in METRICS:
        return True
    allowed = get_entry_metrics(entry)
    return not allowed or key in allowed
