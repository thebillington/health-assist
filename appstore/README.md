# App Store release pack

Status: **prepared, not submitted.** Nothing in this directory publishes or
submits anything. Use it to fill in App Store Connect, then submit manually when
you are ready.

The app is distributed **free** (price tier 0). The optional **Tip Jar** uses
three consumable in-app purchases handled by Apple and unlocks no features.

## App Store Connect fields

| Field | Value |
| --- | --- |
| App name | Health Sync for Home Assistant |
| Subtitle | Read-only health data sync |
| Bundle ID | `uk.co.thebillington.applehealthsync` |
| SKU | `healthassist-ios` (or any private SKU) |
| Primary language | English (UK) |
| Primary category | Health & Fitness |
| Secondary category | Utilities |
| Price | Free (tier 0) |
| In-app purchases | Yes — Tip Jar (3 consumables) |
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

The set is five 1290 × 2796 screenshots: one full app screen, then four
individual app sections.

1. Setup — the full app screen.
2. Sync — the Sync and Result sections.
3. Latest Values — the metric list.
4. Privacy — the data flow and security rows.
5. Tip Jar — the optional in-app purchases and links.

They are rendered locally by `osg/make_sections.py`; see `osg/README.md`. The
files are not committed and are not published on the docs site. Upload them in
this order.

The app is **iPhone-only** (`TARGETED_DEVICE_FAMILY = "1"`), so no iPad
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

## Tip Jar in-app purchases

Create three **consumable** in-app purchases in App Store Connect:

| Product ID | Display name | Suggested price |
| --- | --- | --- |
| `uk.co.thebillington.applehealthsync.tip.small` | Small tip | Lowest tier |
| `uk.co.thebillington.applehealthsync.tip.medium` | Medium tip | Middle tier |
| `uk.co.thebillington.applehealthsync.tip.large` | Large tip | Higher tier |

Tips unlock nothing. The app has no paid tier and no locked features. Use the
Tip Jar screenshot as the review screenshot for each product. `review-notes.txt`
states this explicitly. Do not add wording that suggests a tip buys features,
data access or support.

## Submission checklist

- [ ] Apple Developer Program membership is active.
- [ ] App ID `uk.co.thebillington.applehealthsync` exists with **HealthKit** enabled.
- [ ] App Store Connect app record created with the fields above.
- [ ] Privacy policy live at <https://healthassist.thebillington.co.uk/privacy/>.
- [ ] App Privacy answers completed and consistent with the policy.
- [ ] iPhone 6.9" screenshots uploaded (iPhone-only; no iPad screenshots needed).
- [ ] `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION` bumped in
      `ios/project.yml`.
- [ ] Archive built, exported and uploaded to TestFlight (Codemagic
      `ios-release` workflow, or manual Option B).
- [ ] Tested from TestFlight on a physical iPhone and a clean install.
- [ ] Review notes filled in, including the demo webhook URL if used.
- [ ] Price set to Free.
- [ ] Three Tip Jar consumables created with the product IDs above.
- [ ] Tip Jar tested in TestFlight; tips unlock nothing.
- [ ] Submitted manually by the owner.

See `docs/release.md` for the build and signing commands.
