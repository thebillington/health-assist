# Webhook contract

The iOS app is the only client. It sends two kinds of request to the same
endpoint: a live snapshot and historical chunks.

## Endpoint

```http
POST /api/webhook/<webhook_id>
Content-Type: application/json
X-Webhook-Secret: <optional shared secret>
```

The webhook ID is the primary credential. The shared secret is a second factor.

## Live snapshot

```json
{
  "device_id": "iphone-abc123",
  "device_name": "Billy's iPhone",
  "timestamp": "2026-10-30T08:15:00Z",
  "metrics": {
    "weight": { "value": 72.4, "unit": "kg" },
    "steps": { "value": 8432, "unit": "steps" }
  }
}
```

## Historical chunk

```json
{
  "device_id": "iphone-abc123",
  "history": {
    "weight": [
      { "timestamp": "2026-10-29T08:00:00Z", "value": 72.0, "unit": "kg" },
      { "timestamp": "2026-10-30T08:00:00Z", "value": 72.4, "unit": "kg" }
    ]
  }
}
```

Provide at least one of `metrics` or `history`.

| Field | Required | Notes |
| --- | --- | --- |
| `metrics` | No* | Live values. Maximum 256 metric keys. |
| `metrics.<key>.value` | Yes | Finite JSON number, not a string or boolean. |
| `metrics.<key>.unit` | No | Falls back to the registry unit for known metrics. |
| `history` | No* | Historical samples. Maximum 2,000 samples per request. |
| `history.<key>[].timestamp` | Yes | ISO 8601 timestamp. |
| `history.<key>[].value` | Yes | Finite JSON number. |
| `history.<key>[].unit` | No | Falls back to the registry unit. |
| `device_id` | No | Stored as a sensor attribute. |
| `device_name` | No | Stored as a sensor attribute. |
| `timestamp` | No | Stored as `last_sync` for live metrics. |

\* One of `metrics` / `history` is required.

## Rules

- Metric keys are slugified and bounded to 64 characters.
- Unknown metric keys create generic sensors using the payload unit.
- Known metrics outside the allow-list are accepted but ignored.
- Unknown metrics are always exposed, even with an allow-list. Use a reverse
  proxy/network rule if you need a strict allow-list.
- The request body limit is **256 KB**; larger requests return `413`.
- Historical samples are grouped into UTC-hour means. Re-importing an hour
  overwrites it.
- `timestamp` does not backdate live state. Historical data is imported
  separately as long-term statistics.

## Responses

| Status | Meaning |
| --- | --- |
| `200` | Accepted. |
| `400` | Invalid JSON, no metrics/history, invalid value, or too many entries. |
| `401` | Missing or incorrect shared secret. |
| `405` | Method other than POST. |
| `413` | Body larger than 256 KB. |

Example history response:

```json
{
  "status": "ok",
  "accepted": 2,
  "ignored": 0,
  "history": { "metrics": 2, "samples": 4 }
}
```

## Metric registry

| Key | Unit | Device class |
| --- | --- | --- |
| `weight` | `kg` | `weight` |
| `bmi` | — | — |
| `body_fat` | `%` | — |
| `lean_body_mass` | `kg` | `weight` |
| `muscle_mass` | `kg` | `weight` |
| `bone_mass` | `kg` | `weight` |
| `body_water` | `%` | — |
| `basal_metabolic_rate` | `kcal` | — |
| `steps` | `steps` | — |
| `distance` | `m` | `distance` |
| `active_energy` | `kcal` | — |
| `resting_heart_rate` | `bpm` | — |
| `heart_rate` | `bpm` | — |
| `heart_rate_variability` | `ms` | — |
| `respiratory_rate` | `breaths/min` | — |
| `blood_oxygen` | `%` | — |
| `systolic` | `mmHg` | — |
| `diastolic` | `mmHg` | — |
| `sleep_total` | `h` | `duration` |
| `sleep_deep` | `h` | `duration` |
| `sleep_rem` | `h` | `duration` |
| `sleep_core` | `h` | `duration` |
| `sleep_awake` | `h` | `duration` |
| `vo2_max` | `mL/kg/min` | — |
| `flights_climbed` | `flights` | — |
| `stand_hours` | `h` | `duration` |
| `water_intake` | `mL` | `volume` |

HealthKit does not expose identifiers for muscle mass, bone mass, body water or
basal metabolic rate. The server still accepts those keys from other sources.
