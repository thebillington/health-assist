# iOS app

The companion app is SwiftUI + HealthKit, with no third-party runtime
dependencies.

## Get the app

The app is in TestFlight now, with the App Store release coming shortly. Both
are free, and the optional **Tip Jar** unlocks nothing.

### Build from source (optional)

The app is open source, so you can also build it yourself:

```bash
open ios/AppleHealthSync.xcodeproj
```

Select the `AppleHealthSync` scheme, pick your development team under
**Signing & Capabilities**, then run on an iPhone simulator or a device. A
physical iPhone needs an Apple ID team for signing and Health access.

The simulator has no HealthKit data. Use **Send a Test Payload** to check the
webhook and Home Assistant entities without a phone.

## Configuration

Paste the webhook URL and secret, or tap **Scan QR Code** under **Home
Assistant** and scan the QR from the integration's Configure dialog. If details
are already set, the app asks before replacing them.

The deep link is:

```text
applehealthsync://configure?url=<webhook URL>&secret=<secret>
```

The QR contains credentials. Treat a screenshot as a password.

## Health access

The app requests read-only access. iOS does not reveal which read types were
granted. If values are missing, check:

**Settings → Privacy & Security → Health → Health Bridge → Turn On All**

The simulator has no HealthKit. Use **Send a Test Payload** to verify the
webhook and Home Assistant entities there.

## Background behavior

- HealthKit observer queries trigger an hourly up-to-date sync when data
  changes.
- A weekly `BGTaskScheduler` app-refresh task is queued as a fallback.
- iOS may defer or skip background work. Force-quitting the app stops background
  work until it is opened again.
- Low Power Mode and system scheduling can delay both mechanisms.

## First sync

The first sync exports full history from 2014. It may take minutes; progress is
shown per metric and checkpoints allow resuming. Later syncs export only
incremental history.

## Availability

The app runs on iOS 18 or newer and targets iPhone. It is free, with an optional
**Tip Jar** using in-app purchase. Tips unlock nothing.
