# Support Health Assist

Health Assist is free and open source. There is no paid tier, no account and no
subscription.

## Sponsor My Work

If Health Assist saves you time, you can sponsor ongoing maintenance through
[GitHub Sponsors](https://github.com/sponsors/thebillington). Sponsorship is
optional and does not unlock any features.

## Report a problem

When the source repository is public, open an issue at
[thebillington/health-assist](https://github.com/thebillington/health-assist/issues).

Include:

- the Home Assistant version;
- the Health Assist integration version;
- whether the problem happens on a manual sync, a background sync, or both;
- the relevant Home Assistant log lines with secrets removed.

Never paste your webhook URL or shared secret into an issue. Treat both as
credentials.

## Before you report

- Check [Troubleshooting](troubleshooting.md) and [Gotchas](gotchas.md).
- Confirm the webhook URL is the full URL shown in the integration, not just the
  path.
- Try a manual **Sync Now** from the iOS app and check the app's result message.
- Send a test payload with `scripts/send_sample_payload.py` to separate an app
  problem from a Home Assistant problem.
