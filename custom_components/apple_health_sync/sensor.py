"""Sensor platform for Apple Health Sync."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MANUFACTURER,
    METRICS,
    MODEL,
    MetricDefinition,
    signal_new_data,
)
from .helpers import metric_is_allowed
from .store import HealthDataStore, MetricValue

_LOGGER = logging.getLogger(__name__)

# The sensor platform listens for new data and creates entities lazily. This
# keeps a fresh install free of 27 "unknown" entities and means the allow-list
# is respected without needing a restart.


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up dynamic sensors for one config entry."""
    store: HealthDataStore | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if store is None:
        _LOGGER.error("No data store found for Apple Health Sync entry %s", entry.entry_id)
        return

    entities: dict[str, AppleHealthSensor] = {}

    @callback
    def _handle_data(metric_keys: set[str] | None = None) -> None:
        """Create entities for new metrics and refresh existing ones."""
        keys = set(store.values) if metric_keys is None else metric_keys
        new_entities: list[AppleHealthSensor] = []

        for key in keys:
            value = store.get(key)
            if value is None:
                continue

            entity = entities.get(key)
            if entity is not None:
                entity.async_write_ha_state()
                continue

            if not metric_is_allowed(entry, key):
                continue

            entity = AppleHealthSensor(
                store=store,
                entry=entry,
                metric_key=key,
                initial_value=value,
            )
            entities[key] = entity
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

    # Pick up any values that arrived between setup and platform forwarding.
    _handle_data()

    entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            signal_new_data(entry.entry_id),
            _handle_data,
        )
    )


class AppleHealthSensor(SensorEntity):
    """A sensor backed by the latest value in the per-entry store."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        *,
        store: HealthDataStore,
        entry: ConfigEntry,
        metric_key: str,
        initial_value: MetricValue,
    ) -> None:
        """Initialize a sensor for a metric."""
        self._store = store
        self._metric_key = metric_key
        self._definition: MetricDefinition | None = METRICS.get(metric_key)

        self._attr_unique_id = f"{entry.entry_id}_{metric_key}"
        self._attr_name = (
            self._definition.name if self._definition is not None else _display_name(metric_key)
        )
        self._attr_native_unit_of_measurement = initial_value.unit
        self._attr_device_class = (
            self._definition.device_class if self._definition is not None else None
        )
        self._attr_state_class = (
            self._definition.state_class
            if self._definition is not None
            else SensorStateClass.MEASUREMENT
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        """Return whether a value has been received."""
        return self._store.get(self._metric_key) is not None

    @property
    def native_value(self) -> float | int | None:
        """Return the latest value."""
        value = self._store.get(self._metric_key)
        return value.value if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose sync metadata without backdating HA state timestamps."""
        value = self._store.get(self._metric_key)
        if value is None:
            return {}

        attributes: dict[str, Any] = {
            "last_sync": value.last_sync,
            "received_at": value.received_at,
        }
        if value.device_id is not None:
            attributes["source_device_id"] = value.device_id
        if value.device_name is not None:
            attributes["source_device_name"] = value.device_name
        if value.generic:
            attributes["generic_metric"] = True
            attributes["metric_key"] = self._metric_key
        return attributes


def _display_name(metric_key: str) -> str:
    """Turn an unknown metric key into a readable sensor name."""
    return metric_key.replace("_", " ").title()
