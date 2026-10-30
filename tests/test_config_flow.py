"""Tests for the config and options flows."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.apple_health_sync.const import (
    CONF_METRICS,
    CONF_SECRET,
    CONF_WEBHOOK_ID,
    DOMAIN,
    METRICS,
)

from .helpers import TEST_SECRET, TEST_WEBHOOK_ID, make_entry, post_payload, setup_entry


async def test_user_flow_creates_entry_and_shows_url(hass: HomeAssistant) -> None:
    """The two-step flow shows the full URL before creating the entry."""
    hass.config.external_url = "https://ha.example.com"

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Simon's iPhone",
            CONF_SECRET: "s3cret",
            CONF_METRICS: ["weight", "steps"],
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "webhook"

    webhook_url = result["description_placeholders"]["webhook_url"]
    secret = result["description_placeholders"]["secret"]
    assert webhook_url.startswith("https://ha.example.com/api/webhook/")
    assert secret == "s3cret"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Simon's iPhone"

    entry = result["result"]
    assert entry.data[CONF_SECRET] == "s3cret"
    assert entry.data[CONF_METRICS] == ["weight", "steps"]
    assert entry.data[CONF_NAME] == "Simon's iPhone"
    assert webhook_url.endswith(entry.data[CONF_WEBHOOK_ID])
    assert entry.unique_id == entry.data[CONF_WEBHOOK_ID]

    await hass.async_block_till_done()
    assert entry.state is config_entries.ConfigEntryState.LOADED

    response = await post_payload(
        hass,
        entry.data[CONF_WEBHOOK_ID],
        {"metrics": {"weight": {"value": 72.4}}},
        secret="s3cret",
    )
    assert response.status == 200


async def test_name_is_required(hass: HomeAssistant) -> None:
    """A blank device name keeps the user on the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_NAME: "   ", CONF_SECRET: "", CONF_METRICS: []}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {CONF_NAME: "name_required"}


async def test_empty_allow_list_means_all_metrics(hass: HomeAssistant) -> None:
    """An empty multi-select stores an empty allow-list (all metrics)."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "All Metrics", CONF_SECRET: "", CONF_METRICS: []},
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].data[CONF_METRICS] == []
    assert len(METRICS) == 27


async def test_options_update_secret_and_allow_list(hass: HomeAssistant) -> None:
    """Options can change the secret and allow-list without changing the URL."""
    entry = make_entry(secret="old", metrics=[])
    await setup_entry(hass, entry)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_SECRET: "new-secret", CONF_METRICS: ["weight"]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert entry.options[CONF_SECRET] == "new-secret"
    assert entry.options[CONF_METRICS] == ["weight"]

    # The old secret no longer works and the allow-list is applied on reload.
    old_secret = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {"metrics": {"weight": {"value": 72.4}}},
        secret="old",
    )
    assert old_secret.status == 401

    response = await post_payload(
        hass,
        TEST_WEBHOOK_ID,
        {
            "metrics": {
                "weight": {"value": 72.4},
                "steps": {"value": 8432},
            }
        },
        secret="new-secret",
    )
    assert response.status == 200

    store = hass.data[DOMAIN][entry.entry_id]
    assert store.get("weight").value == 72.4
    assert store.get("steps") is None
    assert entry.data[CONF_WEBHOOK_ID] == TEST_WEBHOOK_ID
    assert entry.data[CONF_SECRET] == "old"


async def test_options_schema_uses_current_values(hass: HomeAssistant) -> None:
    """The options form is prefilled with the current settings."""
    entry = make_entry(secret=TEST_SECRET, metrics=["steps", "weight"])
    await setup_entry(hass, entry)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    data = result["data_schema"]({})

    assert data[CONF_SECRET] == TEST_SECRET
    assert data[CONF_METRICS] == ["steps", "weight"]
