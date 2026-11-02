"""Tests for the historical statistics import."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from custom_components.apple_health_sync.history import _importable_hours


def _row(start: datetime) -> dict:
    return {"start": start, "mean": 1.0}


def test_keeps_hours_the_recorder_has_finished() -> None:
    cutoff = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
    hour = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
    statistics = [_row(hour)]
    assert _importable_hours(statistics, cutoff=cutoff) == statistics


def test_drops_hours_inside_the_settle_window() -> None:
    cutoff = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
    statistics = [_row(cutoff + timedelta(minutes=30))]
    assert _importable_hours(statistics, cutoff=cutoff) == []


def test_existing_hours_are_not_skipped() -> None:
    """Re-export must be able to update an hour that is already stored."""
    cutoff = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
    hour = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
    statistics = [_row(hour)]
    assert _importable_hours(statistics, cutoff=cutoff) == statistics
