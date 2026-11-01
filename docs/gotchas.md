# Gotchas

These are the non-obvious failures found while building and testing Health
Assist. They are worth reading before changing the history import, the iOS
background code or the deployment.

## Home Assistant

### Statistics are not state history

Home Assistant does not let a custom integration backfill normal entity state
history. Historical Apple Health samples are imported as **long-term statistics**
under the sensor entity's `statistic_id`. They show in Statistics, not as old
state changes in the History panel.

### `recorder` is an after-dependency

The history importer imports recorder APIs. The manifest declares:

```json
"after_dependencies": ["recorder"]
```

`hassfest` fails if the component is imported without declaring it. Use
`after_dependencies` rather than a hard dependency so live-only installs still
load when the recorder is absent.

### Recorder must actually be running

`async_import_statistics` raises `KeyError: recorder_instance` if `recorder` is
not loaded. Minimal test configs need `recorder:` or `default_config:`. The
integration catches the failure and logs it; it does not fail the webhook.

### Imported statistics timestamps must be top-of-hour

`async_import_statistics` rejects timestamps with non-zero minutes or seconds.
History samples are bucketed to UTC hours before import.

### Metadata shape changed

Older Home Assistant releases use `has_mean`; newer ones use
`mean_type`/`unit_class`. The importer feature-detects `StatisticMeanType` and
falls back to the older shape. A missing `unit_class` can cause unit conversion
mismatches.

### Dynamic entities and import timing

Sensors are created lazily on the first value. The history importer waits for
the entity registry entries before mapping statistics to `sensor.<entity>`. If
an entity never appears (allow-list or setup failure), that metric's history is
skipped and retried on a later sync.

### Historical chunks must not overwrite live values

History is uploaded oldest-to-newest, but a live sync can happen in parallel.
`MetricValue.historical` marks history values; only a non-historical value (or a
newer historical value) may replace the latest state.

### The webhook body can arrive in pieces

A single `StreamReader.read(n)` is not guaranteed to return the whole body for a
large chunked request through a reverse proxy. The webhook reads in bounded
chunks until EOF. The original single-read implementation produced
`400 invalid JSON` on large history chunks.

### The 256 KB cap is per request

The app sends 1,000 history samples per request, below the integration's 2,000
sample and 256 KB limits. Custom clients must chunk similarly.

### The sensor store is in memory

After an HA restart, live states are unavailable until the next app sync.
Statistics remain in the recorder. This is intentional: the integration does not
write health data to a second persistent store.

### Ansible and hand edits

The production component is deployed from the homelab `energy` role, not edited
on the box. The role vendors the component from this repository; the
`scripts/sync-apple-health-sync.sh` helper refreshes the role copy. A manual edit
on the HA host is drift and will be overwritten.

## iOS / HealthKit

### HealthKit percentages are 0–1

Body fat and oxygen saturation values from HealthKit are fractions. The app
multiplies by 100 for HA. The code leaves values above 1 alone to tolerate
sources that already use 0–100.

### “Last night” is not always present

Sleep data can end more than 12 hours ago if the watch was not worn. The live
sensor uses the latest sleep session from the last seven days with at least one
hour of sleep; it does not require samples from last night.

### Sleep samples overlap across devices

Samples from an iPhone and Watch can overlap. The app merges intervals per stage
before summing, and groups sessions with a four-hour gap threshold.

### HealthKit read authorization is opaque

iOS does not tell an app which read permissions were granted. A successful
`requestAuthorization` does not mean the user enabled every category. Missing
sensors usually mean missing permission or no samples, not necessarily a code
bug.

### Some registry metrics do not exist in HealthKit

HealthKit has no identifiers for muscle mass, bone mass, body water or basal
metabolic rate. The app sends basal energy burned as the generic
`basal_energy_burned` metric. The server still accepts the missing keys from
other sources.

### The simulator is not a HealthKit device

The app disables HealthKit in the simulator. Use **Send a Test Payload** to test
the webhook and HA side. Background delivery and the camera QR scanner also need
a physical device.

### Background work is best-effort

HealthKit observer delivery is coalesced/throttled; `BGTaskScheduler` may defer
the weekly task. Force-quitting the app stops background work. Do not promise a
fixed weekly clock time.

### The camera scanner needs iOS permission

`NSCameraUsageDescription` must be present or the app crashes when presenting the
scanner. The scanner is unavailable in the simulator.

### Custom URL schemes need the Info.plist entry

`applehealthsync` is registered through `CFBundleURLTypes`. Scanning a QR
without it opens nothing. The app's handler validates the scheme, host and
webhook URL before saving anything.

### Xcode signing is per-machine

A fresh machine has no valid Apple Development identity even if Xcode is
installed. The original certificate may be expired. Use
`-allowProvisioningDeviceRegistration`; the device must be registered with the
team. A locked iPhone rejects `devicectl ... process launch` with
`FBSOpenApplicationErrorDomain error 7`.

### The simulator may not have a runtime

Accept the Xcode license and install an iOS simulator runtime. On recent Xcode,
`Simulator.app` may be replaced by DeviceHub; `xcrun simctl` still works.

## QR and credentials

- The QR contains the webhook URL and secret. A screenshot is a credential.
- HA's QR selector was added after the integration's 2024.1 floor. The config
  flow feature-detects it and falls back to text-only setup on older versions.
- The QR uses Home Assistant's current external URL. If the external URL changes
  (for example a domain rename), regenerate/scan the QR.
- The secret field is a password field; the URL is a separate read-only field so
  it is not confused with the secret.

## Documentation

- `mkdocs build --strict` fails on broken internal links. Keep docs links inside
  `docs/` or use full GitHub URLs.
- The docs site is published from `main` via GitHub Pages at
  `healthassist.thebillington.co.uk`.
- Apple Health is an Apple trademark; the project is not affiliated with Apple.

## OSG and marketing assets

- OSG generates **store screenshots**, not logos. The app icon comes from
  `ios/scripts/make_icon.py`; the wordmark is a normal SVG.
- The committed `osg/project.json` is custom-built by
  `osg/build_project.py`: one app screenshot and five text panels.
- `screenshots/01-setup.png` is an HTML mockup rendered by `osg/make_screens.py`;
  `screenshots/01-app.png` is the real simulator capture.
- The dev container's Chrome for Testing has no proprietary codecs, so
  `osg video`/MP4 is unavailable. PNG rendering and `osg verify` work.
- WebGL uses SwiftShader, so 3D device frames render differently from a real
  GPU.
- Use `/usr/local/bin/osg` (pinned Node 20), not a system `npx`.
- Render output is disposable and gitignored. Do not commit it to `docs/`; use
  `promo/` for a local preview and the rendered files for the App Store upload.
