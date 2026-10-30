"""Tests for the Apple Health webhook contract."""

from __future__ import annotations

import json

from homeassistant.core import HomeAssistant

from custom_components.apple_health_sync.const import (
    DOMAIN,
    MAX_METRICS_PER_PAYLOAD,
    MAX_PAYLOAD_BYTES,
)

from .helpers import (
    TEST_SECRET,
    TEST_WEBHOOK_ID,
    make_entry,
    post_payload,
    setup_entry,
)


def sample_payload(metrics: dict | None = None) -> dict:
    """Return a realistic payload."""
    return {
        "device_id": "iphone-abc123",
        "device_name": "Simon's iPhone",
        "timestamp": "2026-10-30T08:15:00Z",
        "metrics": metrics
        or {
            "weight": {"value": 72.4, "unit": "kg"},
            "steps": {"value": 8432, "unit": "steps"},
        },
    }


async def test_valid_payload_is_stored(hass: HomeAssistant) -> None:
    """A valid payload is accepted and stored."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(hass, TEST_WEBHOOK_ID, sample_payload())

    assert response.status == 200
    assert json.loads(response.body) == {"status": "ok", "accepted": 2, "ignored": 0}

    store = hass.data[DOMAIN][entry.entry_id]
    weight = store.get("weight")
    assert weight is not None
    assert weight.value == 72.4
    assert weight.unit == "kg"
    assert weight.last_sync == "2026-10-30T08:15:00Z"
    assert weight.device_id == "iphone-abc123"
    assert weight.device_name == "Simon's iPhone"

    steps = store.get("steps")
    assert steps is not None
    assert steps.value == 8432
    assert steps.unit == "steps"


async def test_units_fall_back_to_registry(hass: HomeAssistant) -> None:
    """Missing units use the registry defaults."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        sample_payload(
            {
                "weight": {"value": 72.4},
                "body_fat": {"value": 18.5},
                "distance": {"value": 1200},
            }
        ),
    )

    assert response.status == 200
    store = hass.data[DOMAIN][entry.entry_id]
    assert store.get("weight").unit == "kg"
    assert store.get("body_fat").unit == "%"
    assert store.get("distance").unit == "m"


async def test_payload_unit_overrides_registry_default(hass: HomeAssistant) -> None:
    """An explicit payload unit is used when supplied."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        sample_payload({"weight": {"value": 160.0, "unit": "lb"}}),
    )

    assert response.status == 200
    assert hass.data[DOMAIN][entry.entry_id].get("weight").unit == "lb"


async def test_unknown_metric_becomes_generic(hass: HomeAssistant) -> None:
    """Unknown metric keys become generic sensors with the payload unit."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        sample_payload({"blood_glucose": {"value": 5.4, "unit": "mmol/L"}}),
    )

    assert response.status == 200
    value = hass.data[DOMAIN][entry.entry_id].get("blood_glucose")
    assert value is not None
    assert value.value == 5.4
    assert value.unit == "mmol/L"
    assert value.generic is True


async def test_metric_keys_are_slugified(hass: HomeAssistant) -> None:
    """Arbitrary keys are normalized before they reach the store."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        sample_payload(
            {
                "Blood Glucose": {"value": 5.4, "unit": "mmol/L"},
                "<script>alert(1)</script>": {"value": 1, "unit": "count"},
            }
        ),
    )

    assert response.status == 200
    store = hass.data[DOMAIN][entry.entry_id]
    assert "blood_glucose" in store.values
    assert "script_alert_1_script" in store.values
    assert all(key.replace("_", "").isalnum() for key in store.values)


async def test_invalid_timestamp_is_ignored(hass: HomeAssistant) -> None:
    """An invalid optional timestamp does not reject the payload."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "timestamp": "not-a-date",
            "metrics": {"weight": {"value": 72.4}},
        },
    )

    assert response.status == 200
    value = hass.data[DOMAIN][entry.entry_id].get("weight")
    assert value.last_sync != "not-a-date"
    assert value.last_sync.endswith("Z")


async def test_missing_timestamp_uses_receipt_time(hass: HomeAssistant) -> None:
    """Without an app timestamp, last_sync is the receipt time."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {"metrics": {"weight": {"value": 72.4}}},
    )

    assert response.status == 200
    value = hass.data[DOMAIN][entry.entry_id].get("weight")
    assert value.last_sync == value.received_at


async def test_secret_is_enforced(hass: HomeAssistant) -> None:
    """The optional shared secret is validated."""
    entry = make_entry(secret=TEST_SECRET)
    await setup_entry(hass, entry)

    wrong = await post_payload(hass, TEST_WEBHOOK_ID, sample_payload(), secret="wrong")
    missing = await post_payload(hass, TEST_WEBHOOK_ID, sample_payload(), secret=None)
    correct = await post_payload(hass, TEST_WEBHOOK_ID, sample_payload(), secret=TEST_SECRET)

    assert wrong.status == 401
    assert missing.status == 401
    assert correct.status == 200


async def test_secret_is_optional(hass: HomeAssistant) -> None:
    """An entry without a secret accepts requests without the header."""
    entry = make_entry(secret="")
    await setup_entry(hass, entry)

    response = await post_payload(hass, TEST_WEBHOOK_ID, sample_payload(), secret=None)

    assert response.status == 200


async def test_allow_list_filters_canonical_metrics(hass: HomeAssistant) -> None:
    """Canonical metrics outside the allow-list are accepted but ignored."""
    entry = make_entry(metrics=["weight"])
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        sample_payload(
            {
                "weight": {"value": 72.4},
                "steps": {"value": 8432},
                "blood_glucose": {"value": 5.4, "unit": "mmol/L"},
            }
        ),
    )

    assert response.status == 200
    body = json.loads(response.body)
    assert body["accepted"] == 2
    assert body["ignored"] == 1

    store = hass.data[DOMAIN][entry.entry_id]
    assert store.get("weight") is not None
    assert store.get("steps") is None
    # Unknown metrics are not part of the allow-list and become generic sensors.
    assert store.get("blood_glucose") is not None


async def test_entries_are_isolated(hass: HomeAssistant) -> None:
    """Two phones on one instance keep separate stores."""
    entry_one = make_entry(webhook_id="phone-one", title="Phone One", entry_id="entry-one")
    entry_two = make_entry(webhook_id="phone-two", title="Phone Two", entry_id="entry-two")
    await setup_entry(hass, entry_one)
    await setup_entry(hass, entry_two)

    response = await post_payload(hass, "phone-one", sample_payload({"weight": {"value": 70.0}}))

    assert response.status == 200
    assert hass.data[DOMAIN][entry_one.entry_id].get("weight").value == 70.0
    assert hass.data[DOMAIN][entry_two.entry_id].get("weight") is None


async def test_invalid_json_returns_400(hass: HomeAssistant) -> None:
    """Non-JSON bodies are rejected."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(hass, TEST_WEBHOOK_ID, b"{not json")

    assert response.status == 400
    assert json.loads(response.body)["error"] == "invalid JSON"


async def test_non_object_payload_returns_400(hass: HomeAssistant) -> None:
    """Top-level arrays are not accepted."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(hass, TEST_WEBHOOK_ID, [])

    assert response.status == 400


async def test_missing_metrics_returns_400(hass: HomeAssistant) -> None:
    """Payloads without a metrics object are rejected."""
    entry = make_entry()
    await setup_entry(hass, entry)

    missing = await post_payload(hass, TEST_WEBHOOK_ID, {"device_id": "x"})
    empty = await post_payload(hass, TEST_WEBHOOK_ID, {"metrics": {}})
    wrong_type = await post_payload(hass, TEST_WEBHOOK_ID, {"metrics": {"weight": 1}})

    assert missing.status == 400
    assert empty.status == 400
    assert wrong_type.status == 400


async def test_invalid_metric_values_return_400(hass: HomeAssistant) -> None:
    """Each metric must have a finite numeric value and a string unit."""
    entry = make_entry()
    await setup_entry(hass, entry)

    for metrics in (
        {"weight": {"value": "heavy"}},
        {"weight": {"value": True}},
        {"weight": {"value": None}},
        {"weight": {"unit": "kg"}},
        {"weight": {"value": 72.4, "unit": 12}},
        {"weight": {"value": float("nan")}},
        {"weight": {"value": float("inf")}},
    ):
        response = await post_payload(hass, TEST_WEBHOOK_ID, {"metrics": metrics})
        assert response.status == 400, metrics


async def test_too_many_metrics_returns_400(hass: HomeAssistant) -> None:
    """A payload cannot contain an unbounded number of metrics."""
    entry = make_entry()
    await setup_entry(hass, entry)

    metrics = {f"metric_{index}": {"value": index} for index in range(MAX_METRICS_PER_PAYLOAD + 1)}
    response = await post_payload(hass, TEST_WEBHOOK_ID, {"metrics": metrics})

    assert response.status == 400


async def test_oversize_payload_returns_413(hass: HomeAssistant) -> None:
    """Bodies larger than 256 KB are rejected."""
    entry = make_entry()
    await setup_entry(hass, entry)

    body = b'{"metrics":{"weight":{"value":72.4}},"padding":"' + (b"x" * MAX_PAYLOAD_BYTES) + b'"}'
    response = await post_payload(hass, TEST_WEBHOOK_ID, body)

    assert response.status == 413


async def test_only_post_is_allowed(hass: HomeAssistant) -> None:
    """The webhook only accepts POST."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(hass, TEST_WEBHOOK_ID, sample_payload(), method="GET")

    assert response.status == 405


async def test_http_endpoint_accepts_real_requests(
    hass: HomeAssistant, hass_client_no_auth
) -> None:
    """The registered route accepts a real aiohttp POST."""
    entry = make_entry()
    await setup_entry(hass, entry)
    client = await hass_client_no_auth()

    response = await client.post(
        f"/api/webhook/{TEST_WEBHOOK_ID}",
        json=sample_payload({"weight": {"value": 72.4}}),
        headers={"X-Webhook-Secret": TEST_SECRET},
    )

    assert response.status == 200
    assert await response.json() == {"status": "ok", "accepted": 1, "ignored": 0}

    unauthorized = await client.post(
        f"/api/webhook/{TEST_WEBHOOK_ID}",
        json=sample_payload(),
    )
    assert unauthorized.status == 401
