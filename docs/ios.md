# iOS app

The companion app is SwiftUI + HealthKit, with no third-party runtime
dependencies.

## Build and run

```bash
open ios/AppleHealthSync.xcodeproj
```

Select the `AppleHealthSync` scheme and an iPhone simulator or device.

For a physical iPhone:

1. Open the target → **Signing & Capabilities**.
2. Choose your development team.
3. Keep the HealthKit capability (background delivery is included in the
   entitlements).
4. Run on the device.

The HealthKit capability must include **Background Delivery** and the app needs
the **Background Modes → Background fetch** capability for the weekly fallback.

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

**Settings → Privacy & Security → Health → Health Sync → Turn On All**

The simulator intentionally disables HealthKit. Use **Send a Test Payload** to
verify the webhook and HA entities there.

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

## Distribution

The development build is signed with the developer's team. A distribution build
requires the same HealthKit/background entitlements and a provisioning profile
that includes them.

The app is not yet distributed through the App Store or TestFlight. The release
pack is in `appstore/` and the signing, TestFlight and listing steps are in
[Release](release.md). The app is free, with an optional **Tip Jar**
using in-app purchase. Tips unlock nothing.
