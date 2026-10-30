# Apple Health Sync

A free, open-source Home Assistant custom integration (HACS) that receives Apple
Health data from an iOS app over a local webhook and exposes it as native
sensor entities.

- **Local push only** — no cloud, no polling, no telemetry, no outbound calls.
- **No external Python dependencies** — runs with a stock Home Assistant.
- **Dynamic sensors** — entities appear after the first sync, with stable
  unique IDs, correct units and long-term statistics support.
- **Multi-device** — add the integration once per iPhone/iPad. Each phone gets
  its own webhook, device and entities.
- **No YAML required.**

This repository is the Home Assistant half of a paired project. The iOS app is
built separately and must follow the [webhook contract](#webhook-contract)
below.

> **Screenshots:** add setup, device and statistics screenshots under
> `docs/images/` after the first release.

---

## Requirements

- Home Assistant 2024.1 or newer (tested against 2026.2).
- HACS (recommended) or manual installation.
- An HTTPS-reachable Home Assistant URL if the phone is not on the same LAN.
  The webhook can be used over plain HTTP on a trusted LAN, but HTTPS is
  strongly recommended because the webhook URL is a credential.

## Installation

### HACS (custom repository)

This integration is not in the default HACS store yet.

1. Open **HACS → Integrations**.
2. Select the three-dot menu → **Custom repositories**.
3. Add `https://github.com/thebillington/homeassist-apple-health-importer`
   with category **Integration**.
4. Search for **Apple Health Sync**, install it, and restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration → Apple Health
   Sync**.

### Manual installation

Copy `custom_components/apple_health_sync` into your Home Assistant
`config/custom_components/` directory, then restart Home Assistant.

## Setup

1. Add the integration and give it a name, for example `Simon's iPhone`.
2. Optionally set a **shared secret**. If set, every request must include it in
   the `X-Webhook-Secret` header.
3. Choose which metrics should become entities. Leave the allow-list empty to
   enable every built-in metric.
4. Select **Submit**. The next screen shows the full webhook URL and the shared
   secret. Copy both into the iOS app.
5. Trigger a sync in the app. Sensors appear within a few seconds.

The webhook URL looks like:

```text
https://home.example.com/api/webhook/4f8c2f0e8f6d4d8bb0d7a0d3f9c1e2a7...
```

Treat the entire URL as a password. Anyone who has it can POST data to that
config entry. The optional shared secret adds a second factor.

To use two phones, add the integration twice. Each entry has a separate URL,
device and set of entities.

### Changing settings later

Open the integration entry → **Configure**. You can change the shared secret
and the metric allow-list without changing the webhook URL. The entry reloads
after saving; sensors return after the app's next sync.

> Removing a metric from the allow-list stops new values from being accepted,
> but Home Assistant may keep the old entity registry entry. Delete it manually
> under **Settings → Devices & services → Entities** if you want it gone.

---

## Webhook contract

### Endpoint

```http
POST /api/webhook/<webhook_id>
Content-Type: application/json
X-Webhook-Secret: <optional shared secret>
```

### Payload

```json
{
  "device_id": "iphone-abc123",
  "device_name": "Simon's iPhone",
  "timestamp": "2026-10-30T08:15:00Z",
  "metrics": {
    "weight": { "value": 72.4, "unit": "kg" },
    "steps": { "value": 8432, "unit": "steps" }
  }
}
```

| Field | Required | Description |
| --- | --- | --- |
| `metrics` | Yes | Object keyed by metric name. Must not be empty. Maximum 256 metrics per request. |
| `metrics.<key>.value` | Yes | Finite JSON number (not a string or boolean). |
| `metrics.<key>.unit` | No | String, 1–32 characters. Falls back to the registry unit for known metrics. |
| `device_id` | No | Stable app/device identifier. Stored as a sensor attribute. |
| `device_name` | No | Human-readable device name. Stored as a sensor attribute. |
| `timestamp` | No | ISO 8601 timestamp. Stored as the `last_sync` attribute. |

Notes:

- `device_id` and `device_name` are metadata only. The Home Assistant device is
  derived from the config entry, not from the payload.
- `timestamp` does **not** backdate the Home Assistant state. The state is
  recorded at receipt time; the app timestamp is exposed as `last_sync`. This
  avoids writing history out of order.
- Keys are slugified (`body fat` → `body_fat`) and bounded to 64 characters
  before they are used. Keys that cannot be slugified are ignored.
- Unknown metric keys are accepted and create a generic sensor using the
  payload unit. They are logged at debug level.
- Known metrics outside the configured allow-list are accepted but ignored,
  and counted in the response's `ignored` field.
- Unknown metrics are always exposed, even when an allow-list is configured.
  This lets the app add new Apple Health categories without an integration
  update. If you need a strict allow-list, use a reverse proxy or a network
  rule to restrict the webhook.
- The maximum request body is **256 KB**. Larger requests receive `413`.

### Responses

| Status | Meaning |
| --- | --- |
| `200` | Accepted. Body: `{"status":"ok","accepted":2,"ignored":0}`. A payload whose metrics were all filtered is still `200`. |
| `400` | Invalid JSON, missing/empty `metrics`, an invalid metric value, or too many metrics. |
| `401` | The shared secret is missing or does not match. |
| `405` | A method other than `POST` was used. |
| `413` | The request body is larger than 256 KB. |

The request is validated as a whole. If any metric is malformed, nothing from
that request is stored.

### Example

```bash
curl -i -X POST \
  "http://homeassistant.local:8123/api/webhook/YOUR_WEBHOOK_ID" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR_SECRET" \
  -d '{
    "device_id": "iphone-abc123",
    "device_name": "Simon iPhone",
    "timestamp": "2026-10-30T08:15:00Z",
    "metrics": {
      "weight": {"value": 72.4, "unit": "kg"},
      "steps": {"value": 8432, "unit": "steps"},
      "sleep_total": {"value": 7.5, "unit": "h"}
    }
  }'
```

Expected response:

```json
{"status":"ok","accepted":3,"ignored":0}
```

---

## Metric registry

All built-in sensors use `state_class: measurement`, so they are eligible for
Home Assistant long-term statistics.

| Key | Sensor name | Unit | Device class |
| --- | --- | --- | --- |
| `weight` | Weight | `kg` | `weight` |
| `bmi` | BMI | — | — |
| `body_fat` | Body fat | `%` | — |
| `lean_body_mass` | Lean body mass | `kg` | `weight` |
| `muscle_mass` | Muscle mass | `kg` | `weight` |
| `bone_mass` | Bone mass | `kg` | `weight` |
| `body_water` | Body water | `%` | — |
| `basal_metabolic_rate` | Basal metabolic rate | `kcal` | — |
| `steps` | Steps | `steps` | — |
| `distance` | Distance | `m` | `distance` |
| `active_energy` | Active energy | `kcal` | — |
| `resting_heart_rate` | Resting heart rate | `bpm` | — |
| `heart_rate` | Heart rate | `bpm` | — |
| `heart_rate_variability` | Heart rate variability | `ms` | — |
| `respiratory_rate` | Respiratory rate | `breaths/min` | — |
| `blood_oxygen` | Blood oxygen | `%` | — |
| `systolic` | Systolic blood pressure | `mmHg` | — |
| `diastolic` | Diastolic blood pressure | `mmHg` | — |
| `sleep_total` | Sleep total | `h` | `duration` |
| `sleep_deep` | Deep sleep | `h` | `duration` |
| `sleep_rem` | REM sleep | `h` | `duration` |
| `sleep_core` | Core sleep | `h` | `duration` |
| `sleep_awake` | Awake time | `h` | `duration` |
| `vo2_max` | VO2 max | `mL/kg/min` | — |
| `flights_climbed` | Flights climbed | `flights` | — |
| `stand_hours` | Stand hours | `h` | `duration` |
| `water_intake` | Water intake | `mL` | `volume` |

The canonical units are part of the contract. The app should send these units.
If it sends a different unit, that unit is used for the entity; Home Assistant
may not be able to convert it for statistics if it is not a recognised unit.

### Entity IDs

Entities are named after the config entry device and the metric. For a device
named `Simon's iPhone`, weight becomes:

```text
sensor.simon_s_iphone_weight
```

Unique IDs are stable and follow `{entry_id}_{metric_key}`, for example
`01J..._weight`. Renaming the entity does not break updates.

---

## Long-term statistics and restarts

Every sensor has a numeric state, a unit (where applicable) and
`state_class: measurement`. Home Assistant records long-term statistics for
these sensors once the recorder sees data. They appear in **Developer Tools →
Statistics** and in the History/Statistics dashboards.

The integration keeps values in memory for v1:

- On restart, the entity registry still knows the entities and their stable
  unique IDs, but states are unavailable until the app syncs again.
- The app should sync on launch and periodically in the background.
- Health data is not persisted a second time by the integration; Home
  Assistant's recorder remains the source of history.

If statistics do not appear immediately, wait for the recorder commit interval
and confirm the entity has a numeric state with a state class.

---

## Security

- The webhook ID is the primary secret. The full URL is a credential; do not
  paste it into public issues, screenshots or chat.
- Set a shared secret in the config flow and configure the same value in the
  app. Requests without it receive `401`.
- Put Home Assistant behind HTTPS (Nabu Casa Cloud, a reverse proxy, or a VPN)
  if the phone is outside the LAN. Do not expose plain HTTP to the internet.
- The integration intentionally does **not** set `local_only` on the webhook,
  because the phone may connect through a reverse proxy or cloud URL. If you
  want LAN-only delivery, restrict `/api/webhook/` at your reverse proxy.
- The shared secret is stored in the Home Assistant config entry (in
  `.storage`) like other integration credentials. Protect backups accordingly.
- Diagnostics redact the webhook ID, shared secret, device identifiers and all
  metric values. Metric keys, units and timestamps remain visible.
- There are no outbound network calls and no telemetry.

---

## Troubleshooting

### `401 invalid secret`

The request did not include `X-Webhook-Secret`, or the value does not match the
entry's configured secret. Re-copy the secret in the app, or clear it in
**Configure** if you do not want to use one.

### `400` responses

Check that:

- the body is valid JSON;
- `metrics` is a non-empty object (not an array or string);
- every metric is an object with a numeric, finite `value`;
- `unit`, if present, is a short string;
- there are no more than 256 metrics.

### `413 payload too large`

Split large syncs into multiple requests of at most 256 KB. A typical daily
sync is far below the limit.

### No sensors appear

- The app must send at least one metric that is in the allow-list (or an
  unknown metric).
- Entity creation happens on the first accepted payload, not when the entry is
  added.
- Check **Settings → Devices & services → Apple Health Sync** and open the
  device to see whether entities exist.
- Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.apple_health_sync: debug
```

### Sensors are unavailable after a restart

This is expected for v1. Trigger a sync from the app; the same entities become
available again. Their unique IDs and history are preserved.

### The URL shown is only a path

Home Assistant could not detect an external/internal URL. Set one under
**Settings → System → Network**, or prepend your base URL to the path shown in
the setup dialog.

### I changed the allow-list but old entities remain

Home Assistant keeps entity registry entries after an entity stops being
provided. Delete unwanted entities manually. Their history remains in the
recorder until purged.

### Testing with curl works but the app does not

- Confirm the app uses `POST`, not `GET`.
- Confirm the phone can reach the exact host/port in the URL (try a browser on
  the phone's network).
- If using a reverse proxy, make sure it forwards `POST` bodies and the
  `X-Webhook-Secret` header.
- Check the Home Assistant log with debug logging enabled.

---

## Development

The test suite uses
[`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
and runs against Home Assistant 2026.2.3.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pytest
ruff check .
```

Project layout:

```text
custom_components/apple_health_sync/
  __init__.py       entry setup, webhook registration, unload
  config_flow.py    UI + options flow
  const.py          domain, limits, 27-metric registry
  diagnostics.py    redacted dump
  helpers.py        allow-list + secret helpers
  manifest.json
  sensor.py         dynamic entities
  store.py          per-entry in-memory store
  strings.json
  translations/en.json
  webhook.py        parsing, validation, dispatch
tests/
  test_webhook.py
  test_config_flow.py
  test_sensor.py
  test_diagnostics.py
scripts/
  send_sample_payload.py
hacs.json
.github/workflows/   pytest, hassfest, ruff
```

### End-to-end test on the homelab

Use the non-production test container (CT 103), **not** the production energy
instance (CT 107):

```bash
docker run -d --name ha-apple-health-test \
  -p 8124:8123 \
  -v "$PWD/custom_components/apple_health_sync:/config/custom_components/apple_health_sync:ro" \
  ghcr.io/home-assistant/home-assistant:stable
```

Complete onboarding at `http://<CT103-IP>:8124`, add the integration, copy the
webhook URL, then send a payload:

```bash
curl -i -X POST "http://<CT103-IP>:8124/api/webhook/<webhook_id>" \
  -H "Content-Type: application/json" \
  -d '{"metrics":{"weight":{"value":72.4,"unit":"kg"}}}'
```

### Simulator

`scripts/send_sample_payload.py` posts realistic payloads without third-party
dependencies:

```bash
python scripts/send_sample_payload.py \
  --url "https://home.example.com/api/webhook/YOUR_ID" \
  --secret "YOUR_SECRET" \
  --interval 5 \
  --count 12
```

Use `--insecure` only for a self-signed certificate on a trusted test network.

### CI

GitHub Actions runs:

- `pytest` with `pytest-homeassistant-custom-component`;
- `ruff check`;
- `hassfest` validation.

### Releasing

Tag the repository (for example `v1.0.0`) and publish a GitHub release after
pushing. HACS uses the release/tag and the `version` in `manifest.json` when
offering updates.

---

## Roadmap

v1 intentionally stops at push-to-sensor. Planned for later:

- backfill / historical imports;
- event entities for workouts, ECG and other discrete records;
- more Apple Health categories;
- default HACS store listing;
- a published iOS app link.

## License

MIT. See [LICENSE](LICENSE).
