# Maintainer documentation

These notes are for people working on Health Bridge itself. They are kept out of
the published documentation site (`docs/`, served at
<https://healthassist.thebillington.co.uk/>) so that site stays end-user
facing: install, setup, iOS app, history, security, privacy, troubleshooting and
support.

- [Development](development.md) — repository layout, test commands, CI and
  documentation build.
- [Webhook contract](webhook.md) — the JSON payload the iOS app sends, response
  codes and the metric registry. The README also covers this.
- [Release](release.md) — App Store Connect setup, Codemagic/TestFlight builds
  and the listing checklist.
- [Gotchas](gotchas.md) — non-obvious Home Assistant, iOS and deployment
  behaviour worth knowing before changing the history import or background
  sync.
