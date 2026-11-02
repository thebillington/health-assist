# Home Assistant Health Bridge

![Home Assistant Health Bridge](images/logo.svg)

**Apple Health → Home Assistant, without a cloud service.**

Home Assistant Health Bridge is a free, open-source Home Assistant integration and companion
iOS app. The app reads Apple Health with HealthKit and pushes the data over a
local webhook. Home Assistant exposes it as native sensors and long-term
statistics.

<img src="images/app.png" alt="Home Assistant Health Bridge iOS app" style="display:block;width:100%;max-width:420px;margin:0 auto;border-radius:18px">

## Why

- **Local-first** — no analytics, no telemetry, no vendor cloud.
- **Full history** — the first sync exports all available Apple Health history,
  not just a snapshot.
- **Future updates** — live syncs, hourly HealthKit background delivery and a
  weekly fallback keep the data current.
- **Two phones, one HA** — each iPhone is a separate config entry with its own
  webhook, device and entities.
- **HACS-friendly** — one custom repository, no YAML.

## Quick start

1. [Install the Home Assistant integration](install.md).
2. [Add a device and scan the QR code](setup.md) from the iOS app.
3. Grant Apple Health access and run the first sync.

## Get the app

The iOS app is in TestFlight now, with the App Store release coming shortly.
Both are free, and the optional **Tip Jar** unlocks nothing. Building from
source is still available for developers; see [iOS app](ios.md).

## Project status

Health Bridge is under active development. The webhook sync and long-term
statistics are working end to end. Workouts, ECG and clinical records are not
yet exported.

## Repository

- [Home Assistant integration + iOS app](https://github.com/thebillington/health-assist)
- [Report an issue](https://github.com/thebillington/health-assist/issues)
- [MIT license](https://github.com/thebillington/health-assist/blob/main/LICENSE)
- [Privacy policy](privacy.md)
- [Terms of use](terms.md)

## Support My Work

Health Bridge is free, with no paid tier or account. The iOS app has an optional
**Tip Jar** using Apple's in-app purchase. Tips unlock nothing. You can also
[support my work on GitHub Sponsors](https://github.com/sponsors/thebillington).
Support is optional and does not unlock any features.

Apple Health is a trademark of Apple Inc. Home Assistant is a trademark of
Nabu Casa. Health Bridge is not affiliated with Apple, Nabu Casa or the Home
Assistant project.
