# App Store release pack

Status: **prepared, not submitted.** Nothing in this directory publishes or
submits anything. Use it to fill in App Store Connect, then submit manually when
you are ready.

The app is distributed **free** (price tier 0, no in-app purchases). The optional
**Sponsor My Work** link opens <https://github.com/sponsors/thebillington> in
Safari and unlocks no features.

## App Store Connect fields

| Field | Value |
| --- | --- |
| App name | Health Assist |
| Subtitle | Apple Health to Home Assistant |
| Bundle ID | `uk.co.thebillington.applehealthsync` |
| SKU | `healthassist-ios` (or any private SKU) |
| Primary language | English (UK) |
| Primary category | Health & Fitness |
| Secondary category | Utilities |
| Price | Free (tier 0) |
| In-app purchases | None |
| Age rating | 4+ |
| Copyright | 2026 Billy Rebecchi |
| Support URL | <https://healthassist.thebillington.co.uk/support/> |
| Marketing URL | <https://healthassist.thebillington.co.uk/> |
| Privacy policy URL | <https://healthassist.thebillington.co.uk/privacy/> |

The privacy policy must be live at that URL before you submit. It is committed
at `docs/privacy.md` and deploys with the docs site.

## Metadata

Copy-paste ready in `metadata/en-GB/`:

- `name.txt` — 30-character limit
- `subtitle.txt` — 30-character limit
- `keywords.txt` — 100-character limit, comma separated
- `promotional_text.txt` — 170-character limit
- `description.txt` — 4,000-character limit
- `release_notes.txt`
- `support_url.txt`, `marketing_url.txt`, `privacy_url.txt`

Only English (UK) is provided. Add more locales with fastlane-style directories
if needed (`metadata/<locale>/…`).

## App Privacy answers

Recommended: **Data Not Collected.**

Rationale: the app transmits health data only to the Home Assistant endpoint the
user supplies. The developer never receives it, has no server in the path, and
cannot access it. There are no analytics, advertising, tracking or
crash-reporting SDKs, and no developer-operated backend.

If App Review questions the answer, the conservative alternative is to declare:

- **Health & Fitness** data;
- collected only for **App Functionality**;
- **not linked** to the user's identity;
- **not used for tracking**.

Either answer must match `docs/privacy.md`, which explains the full data flow.

## Screenshots

Apple requires at least one screenshot for each supported device family.

- iPhone 6.9" (1290 × 2796): `docs/images/store/01-health-assist.png` exists.
- Add 3–5 boards for a better listing. The OSG project is in `osg/`.
- The app is **iPhone-only** (`TARGETED_DEVICE_FAMILY = "1"`), so no iPad
  screenshots are required.

## Reviewer access

The app has no account and no developer backend, but it needs a Home Assistant
webhook to sync. `review-notes.txt` explains this. To let App Review test the
full sync path without a Home Assistant install, deploy the tiny mock receiver
in `demo-webhook/` and put its URL in the review notes.

The mock endpoint must:

- accept `POST` with a JSON body;
- return HTTP 200 with `{"accepted":1,"ignored":0}`;
- store and log nothing.

## Sponsor link and App Review

The **Sponsor My Work** row is an optional donation to the individual developer,
not a purchase. It is placed in the Support section, opens in Safari, and no
feature is locked behind it. `review-notes.txt` states this explicitly. Do not
add any wording that suggests sponsorship buys features, data access or
priority support.

## Submission checklist

- [ ] Apple Developer Program membership is active.
- [ ] App ID `uk.co.thebillington.applehealthsync` exists with **HealthKit** enabled.
- [ ] App Store Connect app record created with the fields above.
- [ ] Privacy policy live at <https://healthassist.thebillington.co.uk/privacy/>.
- [ ] App Privacy answers completed and consistent with the policy.
- [ ] iPhone 6.9" screenshots uploaded (iPhone-only; no iPad screenshots needed).
- [ ] `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION` bumped in
      `ios/project.yml`.
- [ ] Archive built, exported and uploaded to TestFlight.
- [ ] Tested from TestFlight on a physical iPhone and a clean install.
- [ ] Review notes filled in, including the demo webhook URL if used.
- [ ] Price set to Free; no in-app purchases configured.
- [ ] Submitted manually by the owner.

See `docs/release.md` for the build and signing commands.
