# Apple Health Sync for iOS

The companion iOS app for the [Apple Health Sync Home Assistant
integration](../README.md). It reads Apple Health with HealthKit and POSTs the
webhook contract to your Home Assistant instance.

- SwiftUI, iOS 18+, no third-party dependencies.
- Read-only HealthKit access; the app never writes health data.
- No analytics, no telemetry, no cloud service.
- Webhook URL and shared secret stored in the iOS Keychain.
- Manual sync plus optional sync when the app opens.
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

The app has no App Store distribution configuration; signing and provisioning
are intentionally left to whoever builds it.

## Configure

1. In Home Assistant, add the **Apple Health Sync** integration. Copy the
   webhook URL and optional shared secret.
2. In the app, paste the URL and secret in the **Home Assistant** section.
3. Tap **Request Health Access** and grant read access.
4. Tap **Sync Now**.

If the app is on the same LAN, an `http://homeassistant.local:8123/...` or
`http://192.168.x.x:8123/...` URL works. `NSAllowsLocalNetworking` is enabled
for local HTTP. For remote access, use HTTPS (Nabu Casa Cloud, a reverse proxy,
or a VPN).

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

In the simulator, HealthKit may be unavailable or contain no data. Use **Send a
Test Payload** to verify the URL, secret, network route, and Home Assistant
entities without needing HealthKit.

## Known limitations

- No background delivery yet. The app syncs manually or when opened
  (`Sync when the app opens`).
- Only the latest sample is sent for point-in-time metrics; activity totals are
  today's cumulative totals.
- Workouts, ECG, clinical records, symptoms and other category/event data are
  not sent in this version.
- HealthKit read authorization is intentionally opaque: iOS does not tell apps
  which read types were granted. If values are missing, check **Settings →
  Privacy & Security → Health → Apple Health Sync**.
