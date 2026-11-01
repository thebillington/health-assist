"""Tests for dynamic sensor creation and updates."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.apple_health_sync.const import DOMAIN, METRICS

from .helpers import TEST_WEBHOOK_ID, make_entry, post_payload, setup_entry


async def test_no_entities_before_first_sync(hass: HomeAssistant) -> None:
    """Entities are only created when data arrives."""
    entry = make_entry()
    await setup_entry(hass, entry)

    assert hass.states.get("sensor.test_phone_weight") is None
    assert hass.states.get("sensor.test_phone_steps") is None


async def test_entities_are_created_on_first_sync(hass: HomeAssistant) -> None:
    """Weight and steps become native sensors with correct metadata."""
    entry = make_entry()
    await setup_entry(hass, entry)

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "device_id": "iphone-abc123",
            "device_name": "Simon's iPhone",
            "timestamp": "2026-10-30T08:15:00Z",
            "metrics": {
                "weight": {"value": 72.4, "unit": "kg"},
                "steps": {"value": 8432, "unit": "steps"},
            },
        },
    )
    assert response.status == 200
    await hass.async_block_till_done()

    weight = hass.states.get("sensor.test_phone_weight")
    assert weight is not None
    assert weight.state == "72.4"
    assert weight.attributes["unit_of_measurement"] == "kg"
    assert weight.attributes["device_class"] == "weight"
    assert weight.attributes["state_class"] == "measurement"
    assert weight.attributes["last_sync"] == "2026-10-30T08:15:00Z"
    assert weight.attributes["source_device_id"] == "iphone-abc123"
    assert weight.attributes["source_device_name"] == "Simon's iPhone"

    steps = hass.states.get("sensor.test_phone_steps")
    assert steps is not None
    assert steps.state == "8432"
    assert steps.attributes["unit_of_measurement"] == "steps"
    assert steps.attributes["state_class"] == "measurement"
    assert "device_class" not in steps.attributes


async def test_second_sync_updates_state(hass: HomeAssistant) -> None:
    """New payloads update existing entities without creating duplicates."""
    entry = make_entry()
    await setup_entry(hass, entry)

    await post_payload(hass, TEST_WEBHOOK_ID, {"metrics": {"weight": {"value": 72.4}}})
    await hass.async_block_till_done()
    assert hass.states.get("sensor.test_phone_weight").state == "72.4"

    await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "timestamp": "2026-10-30T09:00:00Z",
            "metrics": {"weight": {"value": 73.1}},
        },
    )
    await hass.async_block_till_done()

    weight = hass.states.get("sensor.test_phone_weight")
    assert weight.state == "73.1"
    assert weight.attributes["last_sync"] == "2026-10-30T09:00:00Z"
    assert len(hass.states.async_entity_ids("sensor")) == 1


async def test_allow_list_prevents_entity_creation(hass: HomeAssistant) -> None:
    """Metrics outside the allow-list never become entities."""
    entry = make_entry(metrics=["weight"])
    await setup_entry(hass, entry)

    await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "metrics": {
                "weight": {"value": 72.4},
                "steps": {"value": 8432},
            }
        },
    )
    await hass.async_block_till_done()

    assert hass.states.get("sensor.test_phone_weight") is not None
    assert hass.states.get("sensor.test_phone_steps") is None


async def test_unknown_metric_creates_generic_sensor(hass: HomeAssistant) -> None:
    """Unknown metrics become generic measurement sensors."""
    entry = make_entry()
    await setup_entry(hass, entry)

    await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "metrics": {
                "blood_glucose": {"value": 5.4, "unit": "mmol/L"},
            }
        },
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.test_phone_blood_glucose")
    assert state is not None
    assert state.state == "5.4"
    assert state.attributes["unit_of_measurement"] == "mmol/L"
    assert state.attributes["state_class"] == "measurement"
    assert state.attributes["generic_metric"] is True
    assert state.attributes["metric_key"] == "blood_glucose"


async def test_entity_registry_unique_id_and_device(hass: HomeAssistant) -> None:
    """Unique IDs are stable and every metric belongs to the entry device."""
    entry = make_entry()
    await setup_entry(hass, entry)

    await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "metrics": {
                "weight": {"value": 72.4},
                "steps": {"value": 8432},
            }
        },
    )
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    weight_entry = entity_registry.async_get("sensor.test_phone_weight")
    steps_entry = entity_registry.async_get("sensor.test_phone_steps")

    assert weight_entry is not None
    assert steps_entry is not None
    assert weight_entry.unique_id == f"{entry.entry_id}_weight"
    assert steps_entry.unique_id == f"{entry.entry_id}_steps"
    assert weight_entry.device_id == steps_entry.device_id

    device = dr.async_get(hass).async_get(weight_entry.device_id)
    assert device is not None
    assert device.name == "Test Phone"
    assert device.manufacturer == "Health Assist"


async def test_two_phones_create_two_devices(hass: HomeAssistant) -> None:
    """Two config entries produce separate devices and entities."""
    entry_one = make_entry(webhook_id="phone-one", title="Phone One", entry_id="entry-one")
    entry_two = make_entry(webhook_id="phone-two", title="Phone Two", entry_id="entry-two")
    await setup_entry(hass, entry_one)
    await setup_entry(hass, entry_two)

    await post_payload(hass, "phone-one", {"metrics": {"weight": {"value": 70.0}}})
    await post_payload(hass, "phone-two", {"metrics": {"weight": {"value": 85.0}}})
    await hass.async_block_till_done()

    one = hass.states.get("sensor.phone_one_weight")
    two = hass.states.get("sensor.phone_two_weight")
    assert one is not None and one.state == "70.0"
    assert two is not None and two.state == "85.0"

    entity_registry = er.async_get(hass)
    one_entry = entity_registry.async_get("sensor.phone_one_weight")
    two_entry = entity_registry.async_get("sensor.phone_two_weight")
    assert one_entry.device_id != two_entry.device_id


async def test_all_registry_metrics_create_entities(hass: HomeAssistant) -> None:
    """Every canonical metric gets the documented unit and statistics metadata."""
    entry = make_entry()
    await setup_entry(hass, entry)

    await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {"metrics": {key: {"value": 1} for key in METRICS}},
    )
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    for key, definition in METRICS.items():
        entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
        assert entity_id is not None, key

        state = hass.states.get(entity_id)
        assert state is not None, key
        assert state.attributes["state_class"] == "measurement", key
        if definition.unit is None:
            assert "unit_of_measurement" not in state.attributes, key
        else:
            assert state.attributes["unit_of_measurement"] == definition.unit, key
        if definition.device_class is None:
            assert "device_class" not in state.attributes, key
        else:
            assert state.attributes["device_class"] == definition.device_class.value, key


async def test_payload_unit_is_reflected_in_entity(hass: HomeAssistant) -> None:
    """A supplied payload unit is used by the created sensor."""
    entry = make_entry()
    await setup_entry(hass, entry)

    await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {"metrics": {"weight": {"value": 160.0, "unit": "lb"}}},
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.test_phone_weight")
    assert state.attributes["unit_of_measurement"] == "lb"
    assert state.attributes["device_class"] == "weight"


async def test_store_is_cleared_on_unload(hass: HomeAssistant) -> None:
    """Unloading removes the entry store so stale data is not exposed."""
    entry = make_entry()
    await setup_entry(hass, entry)
    assert entry.entry_id in hass.data[DOMAIN]

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.entry_id not in hass.data[DOMAIN]
    assert hass.states.get("sensor.test_phone_weight") is None
