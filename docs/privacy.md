# Privacy policy

**Effective date: 2 November 2026**

**Applies to:** the Home Assistant Health Bridge iOS app distributed by Billy
Rebecchi ("I", "me") through TestFlight and the App Store, and this
documentation site. See [Scope](#scope) for what is not covered.

The Home Assistant integration runs on your own Home Assistant server, under
your control.

## Summary

- Health Bridge reads Apple Health data only after you grant permission.
- The app sends that data directly to the Home Assistant address you configure.
- I do not receive, see, sell, rent or share your health data.
- There is no account, no analytics, no advertising, no tracking and no
  telemetry.
- Support is optional and unlocks no features.

## Scope

This policy covers the iOS app I distribute through TestFlight and the App
Store, and this documentation site. It describes the data that build sends and
what I do with it.

It does not cover:

- **copies you build yourself** from the open-source repository — they come from
  the same source and behave the same way with your data, but I do not
  distribute or run them and cannot verify or support that build;
- **the Home Assistant integration**, whether installed through HACS as a custom
  repository or copied in manually — it runs on your hardware, inside your Home
  Assistant, and I receive nothing from it.

Installing or building the software yourself is your own responsibility, on the
terms in the [Terms of use](terms.md). In every case the data flow is the same:
the app talks directly to the Home Assistant address you configure, and I do not
operate a server that receives it.

## Data the app reads

With your permission, Health Bridge reads HealthKit data needed to build its
sensors. This can include activity, body measurements, heart and respiratory
metrics, sleep analysis, nutrition, and other health and fitness samples. You
choose which data types to allow in the iOS Health permission sheet. iOS does
not tell the app which permissions you denied.

The app only reads from Apple Health. It never writes to Apple Health.

You can revoke access at any time in **Settings → Privacy & Security → Health →
Health Bridge**, or by deleting the app.

## Where the data goes

The app sends the selected readings, and on the first sync your available
HealthKit history, to the webhook URL you enter. That URL normally points to
your own Home Assistant instance.

If you reach Home Assistant through a remote-access service — for example Nabu
Casa Cloud, a VPN, or your own reverse proxy — the data also passes through that
service under its own terms. I do not operate that destination and cannot access
the data sent to it.

## What is stored on your device

- The webhook URL and optional shared secret are stored in the iOS Keychain.
- App settings and sync checkpoints (dates, not health values) are stored in app
  preferences.
- Latest health readings are held in memory while the app is open so they can be
  displayed. The developer does not write them to an app database.

Deleting the app removes its preferences and Keychain items. Removing the Health
Assist integration in Home Assistant deletes that config entry; data already
imported into Home Assistant is kept according to your Home Assistant recorder
settings.

## What I collect

Nothing. The app contains no analytics, crash-reporting, advertising or
telemetry SDK, and it makes no calls to servers I operate.

Apple may provide me with aggregated App Store analytics and crash reports if
you choose to share them with developers in iOS settings. Apple controls that
data and it is not linked to your identity by me.

## Third parties

- **Apple** — HealthKit, App Store distribution and the optional Tip Jar in-app purchase. Apple handles the payment; I never receive your name, email or payment details.
- **Your Home Assistant instance**, and any network or remote-access provider
  you use to reach it.
- **GitHub Sponsors** — the project website and README link to GitHub Sponsors.
  The iOS app does not open GitHub Sponsors. GitHub's privacy policy applies if
  you use that link. Support is optional and does not unlock any features.

I do not sell data and I do not share it with advertisers or data brokers.

## Security

Use an `https://` webhook URL whenever the phone is not on a trusted local
network. The optional shared secret is sent in the `X-Webhook-Secret` header.
Treat the webhook URL, the shared secret and the setup QR code as passwords.

## Children

Health Bridge is not directed at children under 13, and I do not knowingly
collect data from children.

## Changes

I may update this policy from time to time. The effective date above will
change, and material changes will be noted in the app's release notes.

## Contact

Open an issue at
[thebillington/health-assist](https://github.com/thebillington/health-assist/issues).
Do not include health data, webhook URLs or shared secrets in an issue.

Apple Health is a trademark of Apple Inc. Home Assistant is a trademark of
Nabu Casa. Health Bridge is not affiliated with Apple, Nabu Casa or the Home
Assistant project.
