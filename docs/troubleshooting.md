# Troubleshooting

## No sensors appear

- The app must send at least one accepted metric.
- Entities are created on the first accepted payload, not when the entry is
  added.
- Check the integration entry and its device.
- Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.apple_health_sync: debug
```

## 401 invalid secret

The request did not include the configured `X-Webhook-Secret`, or it does not
match. Re-scan the QR or clear the secret in Configure.

## 400 responses

Check that:

- the body is valid JSON;
- at least one of `metrics` or `history` is present;
- every metric has a finite numeric `value`;
- every history sample has a valid ISO 8601 `timestamp`;
- there are no more than 256 live metrics or 2,000 history samples per request.

## 413 payload too large

The request body exceeds 256 KB. The app chunks history automatically; a custom
client must do the same.

## Sleep sensors are missing or old

The app uses the most recent sleep session from the last seven days, not only
last night. If the watch was not worn, the latest session may be older. Check
the Sleep permission and confirm HealthKit actually contains recent sleep
samples.

## Sensors unavailable after a restart

Live values are in memory. Trigger a sync from the app; imported statistics
remain in the recorder.

## QR scanner unavailable

The in-app scanner needs a physical iPhone and camera permission. On the
simulator, use **Send a Test Payload** or paste the URL manually.

## Statistics not visible

- Wait for the recorder commit interval.
- Confirm the sensor has `state_class: measurement`.
- Look in **Developer Tools → Statistics**.
- The integration needs the recorder component. Home Assistant's default
  configuration provides it.

## The HA URL is only a path in the QR

Home Assistant could not detect an external/internal URL. Set one under
**Settings → System → Network**.
