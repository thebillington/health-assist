"""In-memory data store for a single Health Bridge config entry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetricValue:
    """A single metric value received from the iOS app."""

    value: float | int
    unit: str | None
    last_sync: str
    received_at: str
    device_id: str | None = None
    device_name: str | None = None
    generic: bool = False
    historical: bool = False


class HealthDataStore:
    """Hold the latest value of every metric for one config entry.

    The store is intentionally in-memory. State restoration in Home Assistant
    keeps the entity registry entries, and the next sync repopulates the state.
    Persisting values would mean writing health data to disk a second time, so
    that is deliberately left out of v1.
    """

    def __init__(self, entry_id: str) -> None:
        """Initialize an empty store for a config entry."""
        self.entry_id = entry_id
        self._values: dict[str, MetricValue] = {}
        self.last_payload_at: str | None = None
        self.last_device_id: str | None = None
        self.last_device_name: str | None = None

    @property
    def values(self) -> dict[str, MetricValue]:
        """Return the latest values keyed by canonical metric key."""
        return self._values

    def get(self, key: str) -> MetricValue | None:
        """Return the latest value for a metric, if present."""
        return self._values.get(key)

    def update(
        self,
        values: dict[str, MetricValue],
        *,
        device_id: str | None,
        device_name: str | None,
        received_at: str,
    ) -> set[str]:
        """Store new values and return the keys that were updated.

        Historical chunks can arrive out of order relative to a live sync, so a
        value only replaces an existing one when its timestamp is not older.
        ISO 8601 UTC strings sort lexicographically.
        """
        updated: set[str] = set()
        for key, value in values.items():
            existing = self._values.get(key)
            if existing is None or not value.historical or value.last_sync >= existing.last_sync:
                self._values[key] = value
                updated.add(key)

        self.last_payload_at = received_at
        self.last_device_id = device_id
        self.last_device_name = device_name
        return updated
