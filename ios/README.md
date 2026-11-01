# Health Sync for Home Assistant — iOS app

The companion iOS app for the [Health Sync for Home Assistant
integration](../README.md). It reads Apple Health with HealthKit and POSTs the
webhook contract to your Home Assistant instance.

- SwiftUI, iOS 18+, no third-party dependencies.
- Read-only HealthKit access; the app never writes health data.
- No analytics, no telemetry, no cloud service.
- Webhook URL and shared secret stored in the iOS Keychain.
- Manual sync, optional sync when the app opens, HealthKit background
  delivery, and a weekly background fallback.
- Full historical export on first sync, with resumable per-metric checkpoints
  and a **Re-export All History** action.
- "Send a Test Payload" works without HealthKit, including in the iOS
  Simulator.

## Open and run

The Xcode project is generated from `project.yml` and is committed, so you can
open it directly:

```bash
open ios/AppleHealthSync.xcodeproj
```

Or regenerate it after changing `project.yml`:

```bash
brew install xcodegen
cd ios
xcodegen generate
```

Select the `AppleHealthSync` scheme and an iPhone simulator, then Run.

From the command line, after the simulator runtime is installed:

```bash
ios/scripts/run_in_simulator.sh "iPhone 16 Pro"
```

To run on a physical iPhone:

1. Open the project in Xcode.
2. Select the `AppleHealthSync` target → **Signing & Capabilities**.
3. Choose your development team and replace the bundle identifier if needed.
4. Ensure the **HealthKit** capability is present (it is defined in
   `AppleHealthSync/AppleHealthSync.entitlements`).
5. Run on the device and grant Health access.

The app is free and not yet on the App Store. Signing and provisioning are left
to whoever builds it; the release pack, privacy policy and reviewer notes are in
`../appstore/` and `../docs/release.md`. `../codemagic.yaml` builds and uploads
to TestFlight manually, without submitting for review. The app has an optional
StoreKit **Tip Jar**; tips unlock nothing.

## Configure

1. In Home Assistant, add the **Health Sync for Home Assistant** integration. Copy the
   webhook URL and optional shared secret.
2. In the app, paste the URL and secret in the **Home Assistant** section.
3. Tap **Request Health Access** and grant read access.
4. Tap **Sync Now**.

If the app is on the same LAN, an `http://homeassistant.local:8123/...` or
`http://192.168.x.x:8123/...` URL works. `NSAllowsLocalNetworking` is enabled
for local HTTP. For remote access, use HTTPS (Nabu Casa Cloud, a reverse proxy,
or a VPN).

## Historical export

The first successful sync exports the complete HealthKit history from 2014,
not just a snapshot. Each metric is queried with an appropriate granularity:

- discrete samples (weight, body fat, blood pressure, VO2 max, …) are sent as
  individual samples;
- cumulative activity metrics (steps, distance, energy, water, …) are sent as
  daily totals;
- high-frequency metrics (heart rate, HRV, respiratory rate, oxygen, audio
  exposure, …) are sent as hourly averages;
- sleep is sent as one total/stage row per sleep session;
- stand hours are sent as one count per day.

Samples are uploaded in chunks of 1,000 with per-metric checkpoints stored in
UserDefaults. If the app is interrupted, the next sync resumes where it stopped.
Home Assistant imports the samples as long-term statistics under the
corresponding sensor entity, so the Statistics dashboard contains the full
history. Normal state history cannot be backfilled retroactively by an
integration.

**Re-export All History** resets every checkpoint and uploads everything again.

## QR configuration

The integration's Configure dialog generates a QR code containing a deep link:

```text
applehealthsync://configure?url=<webhook URL>&secret=<shared secret>
```

Scan it with the app's **Scan QR Code** button (under Home Assistant), or with
the iPhone Camera; iOS opens **Health Sync** and imports the URL and
secret. If the app already has a URL or secret, it asks for confirmation before
replacing them. The in-app scanner uses the rear camera and requires camera
permission. The QR reflects the saved secret, so save and reopen Configure after
changing it. Treat the QR/screenshot as a credential.

This requires a Home Assistant version whose frontend includes the QR selector;
older versions still show the URL and secret as copyable text.

## Background sync

The app uses two best-effort mechanisms on a physical iPhone:

- **HealthKit background delivery** — observer queries for the enabled metric
  types, delivered at an hourly frequency. When new Health data arrives, iOS
  wakes the app and it sends a normal webhook payload.
- **Weekly BGTaskScheduler fallback** — an app refresh task with an earliest
  begin date seven days out, re-queued after every run. This catches weeks
  where no HealthKit observer fired.

iOS treats both as suggestions, not guaranteed schedules. The weekly task may
run later than seven days, or not at all if the phone is idle, low on power, or
the app was force-quit. Opened the app recently? It resets the weekly timer,
but it also syncs, so that is normally fine.

Background delivery requires the **HealthKit** capability with **Background
Delivery** enabled, plus the `fetch` background mode. Those are already in
`AppleHealthSync.entitlements` and `Info.plist`. If you use automatic signing
and Xcode cannot provision the background-delivery entitlement, enable the
capability under **Signing & Capabilities** for your team.

To debug the weekly task from Xcode while the app is running, pause execution
and use:

```text
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"uk.co.thebillington.applehealthsync.weekly-sync"]
```

## What is read

The canonical metrics match the Home Assistant registry:

Weight, BMI, body fat, lean body mass, steps, distance, active energy, resting
heart rate, heart rate, heart rate variability, respiratory rate, blood oxygen,
systolic/diastolic blood pressure, VO2 max, flights climbed, water intake,
sleep total/deep/REM/core/awake, and stand hours.

HealthKit does not expose identifiers for **muscle mass**, **bone mass**,
**body water** or **basal metabolic rate**. Those server sensors remain
available for other data sources but are not sent by this app. `basalEnergyBurned`
is sent as the generic `basal_energy_burned` sensor instead.

The optional **additional HealthKit metrics** setting also sends a broad set of
quantity types as generic Home Assistant sensors, including glucose, body
temperature, nutrition, mobility, audio exposure, daylight, insulin and
distance-by-activity. Generic metric keys are derived from the HealthKit
identifier, for example:

```text
HKQuantityTypeIdentifierBloodGlucose -> blood_glucose
```

These become generic sensors on the Home Assistant side because they are not in
the canonical registry.

Sleep values are calculated over the last sleep window (from noon yesterday to
now) and overlapping samples from multiple devices are merged so they are not
double counted. Stand hours are the number of Apple Stand Hour samples marked
"stood" today.

## Testing without a simulator runtime

The shared payload/math logic is a Swift package with its own tests:

```bash
ios/scripts/test.sh
```

or directly:

```bash
swift test --package-path ios/AppleHealthSyncCore
```

If `xcode-select` points at CommandLineTools and Swift Testing cannot be found,
the local workaround is:

```bash
FW=/Library/Developer/CommandLineTools/Library/Developer/Frameworks
LIB=/Library/Developer/CommandLineTools/Library/Developer/usr/lib
swift test --package-path ios/AppleHealthSyncCore \
  -Xswiftc -F -Xswiftc "$FW" \
  -Xlinker -F -Xlinker "$FW" \
  -Xlinker -rpath -Xlinker "$FW" \
  -Xlinker -rpath -Xlinker "$LIB"
```

In the simulator, HealthKit is intentionally disabled by the app; use **Send a
Test Payload** to verify the URL, secret, network route, and Home Assistant
entities without needing HealthKit. For repeatable automated checks, launch the
app with these environment variables through `simctl`:

```bash
SIMCTL_CHILD_AHS_WEBHOOK_URL="http://127.0.0.1:8124/api/webhook/<id>" \
SIMCTL_CHILD_AHS_SECRET="<secret>" \
SIMCTL_CHILD_AHS_AUTO_TEST_PAYLOAD="1" \
xcrun simctl launch "iPhone 18 Pro" uk.co.thebillington.applehealthsync
```

This sends the test payload automatically on launch and is useful for CI or
end-to-end checks.

## Known limitations

- Background execution is not an exact schedule; iOS may defer the weekly task
  and coalesce HealthKit delivery. Force-quitting the app stops background work
  until it is opened again.
- Background delivery needs a physical iPhone. The simulator uses the test
  payload path instead.
- Live sensor values use the latest sample; history is imported separately as
  long-term statistics. High-frequency history is hourly-averaged (HA
  statistics are hourly).
- Workouts, ECG, clinical records, symptoms and other category/event data are
  not sent in this version.
- HealthKit read authorization is intentionally opaque: iOS does not tell apps
  which read types were granted. If values are missing, check **Settings →
  Privacy & Security → Health → Health Sync**.
