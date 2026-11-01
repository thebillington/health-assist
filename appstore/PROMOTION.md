# Health Assist — promotion copy

Everything below is ready to reuse for the App Store listing, GitHub, the docs
site and social posts. Replace the App Store link once the listing is live.

## Positioning

**Apple Health → Home Assistant. Free, local-first, no vendor cloud.**

Health Assist is a free, open-source Home Assistant integration and iOS app. It
reads Apple Health with HealthKit, read-only, and sends the data to a webhook on
the user's own Home Assistant. No account, no analytics, no vendor cloud.

## App Store listing

| Field | Copy |
| --- | --- |
| Name | Health Assist |
| Subtitle | Apple Health to Home Assistant |
| Promotional text | Lightweight, local-first Apple Health sync for Home Assistant. Full history, background updates, no account and no vendor cloud. |
| Keywords | `home assistant,apple health,healthkit,health,sensors,automation,self-hosted,local,privacy,webhook` |
| Support URL | <https://healthassist.thebillington.co.uk/support/> |
| Marketing URL | <https://healthassist.thebillington.co.uk/> |
| Privacy URL | <https://healthassist.thebillington.co.uk/privacy/> |
| Price | Free |
| In-app purchases | None |

The long description lives in `metadata/en-GB/description.txt`. Release notes
live in `metadata/en-GB/release_notes.txt`.

## Screenshot captions

All eight boards are 1290 × 2796 (iPhone 6.9"). Files are in
`../docs/images/store/`.

| # | File | Headline | Caption | Alt text |
| --- | --- | --- | --- | --- |
| 1 | `01-setup.png` | Your health, in your home. | A free, local-first bridge from Apple Health to your own Home Assistant. No vendor cloud. No account. No telemetry. | Dark teal promotion board showing the Health Assist setup screen on an iPhone. |
| 2 | `02-history.png` | Every record, not just today. | The first sync exports all available HealthKit history, then keeps it current in the background. | Health Assist sync and history screen showing Apple Health status, sync actions and last sync times. |
| 3 | `03-sensors.png` | Every metric, as a sensor. | Steps, sleep, heart rate, weight and more become Home Assistant sensors with long-term statistics. | Health Assist latest values screen listing steps, heart rate, sleep, weight and other metrics. |
| 4 | `04-privacy.png` | Your data stays yours. | No analytics. No telemetry. No vendor cloud. The webhook URL and secret live in the iOS Keychain. | Health Assist privacy screen showing the iPhone → HTTPS → Home Assistant data flow and security settings. |
| 5 | `05-sponsor.png` | Free software, funded by you. | MIT licensed on both sides. Sponsor My Work is optional and unlocks nothing. | Health Assist support screen with the Sponsor My Work, Privacy Policy and Documentation links. |
| 6 | `06-qr-setup.png` | Scan once. Sync forever. | The QR code carries the webhook URL and secret. Import it, grant Health access, and sensors appear. | Health Assist QR scanner pointing at a Home Assistant setup code. |
| 7 | `07-appstore-search.png` | Find it on the App Store. | Search "health assist". Free, local-first, built for Home Assistant. | App Store search results showing Health Assist as the top result. |
| 8 | `08-appstore-product.png` | Built for your home. | Free on the App Store. No subscription, no account, no in-app purchases. | App Store product page for Health Assist with GET button, screenshots and description. |

## Social copy

### Short (X, Bluesky, Mastodon)

> Your health, in your home.
>
> Health Assist is a free, local-first bridge from Apple Health to Home
> Assistant: full history, native sensors, no account, no vendor cloud.
>
> Open source: github.com/thebillington/health-assist

### Long (Mastodon, Threads, LinkedIn)

> Apple Health finally speaks Home Assistant.
>
> Health Assist is a free, open-source iOS app plus a Home Assistant custom
> integration. It reads HealthKit read-only and pushes the data to a webhook on
> your own Home Assistant instance. The first sync exports your available
> history, then background delivery keeps it current.
>
> You get native sensors and long-term statistics for steps, sleep, heart rate,
> weight and more — no account, no analytics and no vendor cloud.
>
> iOS 18+, Home Assistant 2024.1+, MIT licensed.
>
> github.com/thebillington/health-assist

### Home Assistant community / Reddit

> Hi all — I built **Health Assist**, a free, open-source iOS app and custom
> integration that pushes Apple Health data to your own Home Assistant over a
> webhook.
>
> What it does today:
>
> - exports all available HealthKit history on the first sync, in resumable
>   chunks, then keeps it up to date;
> - turns the readings into native HA sensors with stable IDs, units and
>   long-term statistics;
> - supports one config entry per iPhone;
> - keeps the webhook URL and optional shared secret in the iOS Keychain;
> - has no account, analytics, telemetry or vendor cloud.
>
> It is read-only: the app never writes to Apple Health. Setup is paste the
> webhook (or scan the QR from the integration) and grant Health access.
>
> Repo and docs: github.com/thebillington/health-assist
>
> I would especially appreciate feedback on sensor naming, statistics metadata
> and anything that breaks on a real device.

### GitHub release

> **Health Assist 1.2.0 — first App Store release**
>
> - Free, local-first Apple Health → Home Assistant sync.
> - Full available HealthKit history on first sync, in resumable chunks.
> - Native sensors with stable IDs, units and long-term statistics.
> - Background delivery plus a weekly fallback.
> - QR setup for the webhook URL and optional shared secret.
> - Sponsor My Work is optional and unlocks no features.
>
> The iOS app is now on the App Store. The Home Assistant integration remains
> available through HACS or a manual copy.

## Boilerplate

> Health Assist is a free, open-source Home Assistant integration and iOS app
> that turns Apple Health data into native sensors. It is local-first: the app
> reads HealthKit read-only and sends data only to the user's own Home
> Assistant. MIT licensed. Apple Health is a trademark of Apple Inc.; Health
> Assist is not affiliated with Apple.

### One-line version

> Health Assist — Apple Health to Home Assistant, free and local-first.

## Asset inventory

| Asset | Path | Use |
| --- | --- | --- |
| Logo lockup | `docs/images/logo.svg` | README, docs, press |
| Mark | `docs/images/logo-mark.svg` | Icon-only contexts |
| App icon | `docs/images/icon-512.png`, `icon-192.png` | Docs, favicon, web |
| iOS app icon | `ios/AppleHealthSync/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png` | App Store build |
| App Store boards | `docs/images/store/01-setup.png` … `08-appstore-product.png` | App Store, website, social |
| Social card | `docs/images/og.png` | Open Graph, link previews |
| Source app screens | `screenshots/01-setup.png` … `08-sponsor.png` (`01-app.png` is the real simulator capture) | Mockup source |
| OSG project | `osg/project.json` | Re-render the boards |

## Notes

- Do not claim the app is on the App Store until the listing is live. Boards 7
  and 8 say "on the App Store" and are intended for the live listing.
- Sponsor My Work is a donation link, not a purchase. Never imply it unlocks a
  feature, data or support.
- The app is free with no in-app purchases. Keep that consistent everywhere.
- Health data is sent only to the address the user configures. Do not describe
  it as "collected by us".
- Apple Health is a trademark of Apple Inc. Health Assist is not affiliated with
  or endorsed by Apple.
