# Setup

## Home Assistant

1. Go to **Settings → Devices & services → Add integration**.
2. Choose **Home Assistant Health Bridge**.
3. Enter a device name, for example `Billy's iPhone`.
4. Optionally set a **shared secret**. The app will send it in the
   `X-Webhook-Secret` header.
5. Choose the metric allow-list, or leave it empty for all metrics.
6. Select **Submit**.

The next screen shows:

- the full webhook URL,
- the shared secret,
- a QR code containing both.

The URL is a credential. Anyone who has it can POST data to that config entry.

## iPhone

1. Install the app (see [iOS app](ios.md)).
2. Either paste the webhook URL and secret, or tap **Scan QR Code** under the
   **Home Assistant** section.
3. If details are already present, confirm **Replace**.
4. Tap **Request Health Access** and allow read access.
5. Tap **Sync Now**. The first sync also exports all available history.

If the QR is shown on the phone itself, use the Camera on another device or
display the QR on a computer and scan it with the phone.

## Network

The app sends data directly to the webhook URL. It does not relay through a
service. The phone must be able to open that URL itself: the same Wi-Fi, a VPN
such as Tailscale, or a remote address such as Nabu Casa. If the phone cannot
reach the address, the sync fails.

## Multiple phones

Add the integration once per phone. Each config entry has its own webhook,
device, entity IDs and statistics.

## Changing settings

Open the integration → **Configure**. The dialog shows the read-only webhook
URL, the secret, the QR code and the metric allow-list. Changing the secret does
not change the URL. Save and reopen the dialog to refresh the QR.

Removing a metric from the allow-list stops new values from being accepted.
Home Assistant may keep the old entity registry entry; delete it manually if
desired.

## Re-exporting history

The app has **Re-export All History** in the Sync section. It resets all
per-metric checkpoints and uploads the complete history again. This is safe:
Home Assistant upserts statistics by hour.

## Background updates

On a physical iPhone the app registers HealthKit background delivery (hourly)
and a weekly `BGTaskScheduler` fallback. iOS decides when background work
actually runs. Force-quitting the app stops background work until it is opened
again.
