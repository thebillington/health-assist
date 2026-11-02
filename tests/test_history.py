"""Tests for the historical statistics import."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from custom_components.apple_health_sync.history import _importable_hours


def _row(start: datetime) -> dict:
    return {"start": start, "mean": 1.0}


def test_skips_hours_the_recorder_already_holds() -> None:
    cutoff = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
    hour = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
    assert (
        _importable_hours(
            [_row(hour)],
            {("sensor.x", hour.timestamp())},
            statistic_id="sensor.x",
            cutoff=cutoff,
        )
        == []
    )


def test_keeps_missing_old_hours() -> None:
    cutoff = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
    hour = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
    statistics = [_row(hour)]
    assert (
        _importable_hours(statistics, set(), statistic_id="sensor.x", cutoff=cutoff) == statistics
    )


def test_drops_hours_inside_the_settle_window() -> None:
    cutoff = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
    statistics = [_row(cutoff + timedelta(minutes=30))]
    assert _importable_hours(statistics, set(), statistic_id="sensor.x", cutoff=cutoff) == []


def test_ignores_rows_belonging_to_another_entity() -> None:
    cutoff = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
    hour = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
    statistics = [_row(hour)]
    assert (
        _importable_hours(
            statistics,
            {("sensor.y", hour.timestamp())},
            statistic_id="sensor.x",
            cutoff=cutoff,
        )
        == statistics
    )
