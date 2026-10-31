"""Keep the iOS app's metric catalog aligned with the server registry."""

from __future__ import annotations

import plistlib
import re
from pathlib import Path

from custom_components.apple_health_sync.const import METRICS

IOS_CATALOG = (
    Path(__file__).resolve().parents[1] / "ios" / "AppleHealthSync" / "MetricCatalog.swift"
)
IOS_HEALTH_MANAGER = IOS_CATALOG.with_name("HealthKitManager.swift")
IOS_BACKGROUND_MANAGER = IOS_CATALOG.with_name("BackgroundSyncManager.swift")
IOS_INFO = IOS_CATALOG.with_name("Info.plist")
IOS_ENTITLEMENTS = IOS_CATALOG.with_name("AppleHealthSync.entitlements")

# HealthKit does not expose identifiers for these Apple Health concepts.
# They remain supported by the server for data from other sources.
NOT_AVAILABLE_IN_HEALTHKIT = {
    "muscle_mass",
    "bone_mass",
    "body_water",
    "basal_metabolic_rate",
}

# These are emitted from category samples rather than the quantity catalog.
CATEGORY_METRICS = {
    "sleep_total",
    "sleep_deep",
    "sleep_rem",
    "sleep_core",
    "sleep_awake",
    "stand_hours",
}


def read_catalog() -> str:
    """Return the Swift catalog source."""
    return IOS_CATALOG.read_text(encoding="utf-8")


def canonical_keys() -> list[str]:
    """Extract canonical keys from the Swift catalog."""
    source = read_catalog()
    block = source.split("static let canonical: [QuantityMetric] = [", 1)[1].split(
        "static let extras", 1
    )[0]
    return re.findall(r'key:\s*"([a-z0-9_]+)"', block)


def test_ios_canonical_keys_cover_server_registry() -> None:
    """Every HealthKit-backed server metric exists in the app catalog."""
    keys = canonical_keys()

    assert len(keys) == len(set(keys))
    expected = set(METRICS) - NOT_AVAILABLE_IN_HEALTHKIT - CATEGORY_METRICS
    assert set(keys) == expected


def test_ios_catalog_includes_sleep_and_stand_metrics() -> None:
    """Sleep and stand-hour metrics are emitted by HealthKitManager."""
    source = IOS_HEALTH_MANAGER.read_text(encoding="utf-8")
    for key in CATEGORY_METRICS:
        assert f'"{key}"' in source


def test_ios_catalog_keys_are_slug_safe() -> None:
    """Catalog keys can be used directly as Home Assistant metric keys."""
    for key in canonical_keys():
        assert re.fullmatch(r"[a-z0-9_]+", key), key


def test_ios_background_sync_configuration() -> None:
    """Background delivery and the weekly task are wired consistently."""
    info = plistlib.loads(IOS_INFO.read_bytes())
    entitlements = plistlib.loads(IOS_ENTITLEMENTS.read_bytes())
    source = IOS_BACKGROUND_MANAGER.read_text(encoding="utf-8")

    identifier_match = re.search(r'weeklyTaskIdentifier\s*=\s*"([^"]+)"', source)
    assert identifier_match is not None
    identifier = identifier_match.group(1)

    assert "fetch" in info["UIBackgroundModes"]
    assert identifier in info["BGTaskSchedulerPermittedIdentifiers"]
    assert entitlements["com.apple.developer.healthkit"] is True
    assert entitlements["com.apple.developer.healthkit.background-delivery"] is True
