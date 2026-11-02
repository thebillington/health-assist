# Release the iOS app

Health Bridge ships as a **free** app. The optional Tip Jar uses in-app purchase
and unlocks nothing.

This page covers the manual Apple steps. The repository side — privacy policy,
usage descriptions, listing copy and review notes — is already prepared in
`appstore/` and `docs/privacy.md`.

!!! warning "Submitting is a manual, owner-only step"
    Nothing in this repository submits an app for review. Do not run a final
    submit or release action without the owner explicitly asking for it.

## Before you begin

- An active Apple Developer Program membership.
- A Codemagic account (free tier is fine) **or** a Mac with Xcode 16 or newer
  (iOS 18 SDK) for a manual build.
- Access to App Store Connect for the account that owns the bundle ID.
- The docs site deployed, so the privacy policy is live at
  <https://healthassist.thebillington.co.uk/privacy/>.

## 1. App ID and capabilities

1. In the Apple Developer portal, create or open the App ID
   `uk.co.thebillington.applehealthsync`.
2. Enable **HealthKit** for that App ID. Background delivery is included in the
   app's entitlements.
3. In App Store Connect, create the app record:
   - platform iOS;
   - name **Home Assistant Health Bridge**;
   - primary language **English (UK)**;
   - bundle ID `uk.co.thebillington.applehealthsync`;
   - SKU `healthassist-ios`;
   - price **Free** (tier 0);
   - Tip Jar: three consumables (see `appstore/README.md`).

## 1a. Tip Jar products

Create three **consumable** in-app purchases in App Store Connect:

- `uk.co.thebillington.applehealthsync.tip.small` — Small tip, £1.99
- `uk.co.thebillington.applehealthsync.tip.medium` — Medium tip, £4.99
- `uk.co.thebillington.applehealthsync.tip.large` — Large tip, £9.99

Use the Tip Jar screenshot as the review screenshot for each product. Tips
unlock nothing; the app is fully functional without them.

## 2. Bump the version

Edit `ios/project.yml`:

```yaml
MARKETING_VERSION: "1.2.0"
CURRENT_PROJECT_VERSION: "1"
```

`CURRENT_PROJECT_VERSION` must increase for every upload. The Codemagic
workflow increments it automatically from TestFlight (`latest + 1`). If you
build manually (Option B), bump it yourself before archiving.

Then regenerate the project:

```bash
cd ios
xcodegen generate
```

The generated `Info.plist` and entitlements are committed, so regenerate rather
than hand-editing them.

## 3. Build and upload

### Option A: Codemagic (no Mac required)

`codemagic.yaml` defines a manual **iOS Release (TestFlight)** workflow. It runs
the Swift package tests, increments the build number from TestFlight, builds a
signed IPA and uploads it to App Store Connect. It sets
`submit_to_app_store: false`, so it never submits for App Review.

One-time setup:

1. Add this repository to Codemagic and select the `ios-release` workflow.
2. In **Team settings → Developer Portal**, reuse the team's existing
   **`Codemagic`** App Store Connect API key (App Manager access). No new key is
   needed.
3. In App Store Connect, open the app's **General → App Information** and copy
   the **Apple ID** into `APP_STORE_APPLE_ID` in `codemagic.yaml` (replacing the
   `0000000000` placeholder).
4. Under **Team settings → Code signing identities**:
   - **iOS certificates** — reuse the existing **Apple Distribution**
     certificate.
   - **iOS provisioning profiles** — use **Fetch profiles** with the shared API
     key to fetch an **App Store** profile for
     `uk.co.thebillington.applehealthsync`, or upload one. Profiles are tied to
     a bundle ID, so the Steno or Revision profile cannot be reused.
5. Start the workflow manually in Codemagic, or push to a `ci/*` branch or an
   `ios-v*` tag. The Codemagic GitHub webhook triggers the build
   automatically; no GitHub Action or API token is involved. Integration
   releases use plain semver tags such as `1.1.2`, so they do not trigger an
   iOS build.

If the workflow cannot find a certificate or profile, add the profile once under
**Code signing identities**, then rerun.

### Option B: Manual Mac

Open `ios/AppleHealthSync.xcodeproj`, select the `AppleHealthSync` scheme, set
your team under **Signing & Capabilities**, then:

```bash
cd ios
xcodebuild \
  -project AppleHealthSync.xcodeproj \
  -scheme AppleHealthSync \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath build/HealthAssist.xcarchive \
  archive
```

Export with an `ExportOptions.plist` based on `ios/ExportOptions.plist.example`
(set your `teamID`):

```bash
cp ExportOptions.plist.example ExportOptions.plist
# edit teamID
xcodebuild \
  -exportArchive \
  -archivePath build/HealthAssist.xcarchive \
  -exportPath build/export \
  -exportOptionsPlist ExportOptions.plist
```

Upload the exported `.ipa` with **Xcode → Window → Organizer → Distribute App →
App Store Connect**, or with the Transporter app. Do not use `--submit` style
automation.

## 4. Test on TestFlight

Add yourself as an internal tester and install from TestFlight on a physical
iPhone. Check:

- the Health permission sheet appears and the app requests read-only access;
- the QR scanner imports a webhook URL and secret;
- **Send a Test Payload** succeeds against a real Home Assistant webhook;
- **Sync Now** creates sensors in Home Assistant;
- a full history export completes or resumes;
- background delivery and the weekly fallback are scheduled;
- the Tip Jar loads its products and a sandbox purchase completes;
- the **Privacy Policy** and **Terms of Use** links open the docs site.

## 5. Fill in the listing

Use `appstore/README.md` for the field table and `appstore/metadata/en-GB/` for
the copy. In App Store Connect also complete:

- **App Privacy** — see `appstore/README.md`. Recommended answer: *Data Not
  Collected*, because the developer never receives the data and the app has no
  analytics or developer backend.
- **Age rating** — 4+.
- **Screenshots** — render the six section screenshots with
  `osg/make_appstore.py` and upload them in order: Free, Setup, Sync, Latest
  Values, Privacy, Tip Jar. The target is iPhone-only (`TARGETED_DEVICE_FAMILY = "1"`),
  so no iPad screenshots are required.
- **Export compliance** — `ITSAppUsesNonExemptEncryption` is already `false`;
  the app only uses standard HTTPS.
- **Review notes** — copy `appstore/review-notes.txt` and fill in the contact
  details and demo webhook URL.

## 6. Reviewer demo endpoint

App Review cannot install Home Assistant. The app includes **Send a Test
Payload**, and `appstore/demo-webhook/` contains a tiny stateless receiver that
returns the JSON the app expects. Deploy it, put the URL in the review notes,
and keep it live until review finishes. It must not log or store payloads.

## 7. Submit

Submitting for review is a manual action for the owner. Confirm the checklist in
`appstore/README.md`, then submit from App Store Connect yourself.

## 8. After release

- Tag the release, for example `ios-v1.2.0`, and publish a GitHub release.
- Update `README.md`, `docs/index.md`, `docs/ios.md` and both `llms.txt` files:
  switch the TestFlight wording to the live App Store listing.
- Link the App Store listing from the README, docs home and iOS page.
- Keep the Tip Jar wording: free, optional, unlocks no features.
