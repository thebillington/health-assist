# Security

## The webhook URL is a password

The webhook ID is the primary secret. Anyone with the full URL can POST data to
that config entry. Do not paste it into public issues, screenshots or chat.

Use the optional shared secret as a second factor. It is sent in the
`X-Webhook-Secret` header and compared in constant time.

## QR codes

The Configure dialog's QR contains the webhook URL and secret. The in-app
scanner and the iPhone Camera can import it. Treat any screenshot or printout of
the QR as a credential.

## HTTPS

Use HTTPS when the phone is not on the same LAN. Common options:

- Nabu Casa Cloud
- a reverse proxy with a trusted certificate
- a VPN/Tailscale connection

The integration intentionally does not set `local_only` on the webhook, because
the phone may connect through a proxy. To restrict access to the LAN, block
`/api/webhook/` at your reverse proxy.

## Stored data

- The shared secret and webhook URL are stored in the iOS Keychain.
- Home Assistant stores the config entry (including the secret) in `.storage`,
  like other integration credentials. Protect backups.
- Historical samples are imported into the Home Assistant recorder database.
- Diagnostics redact the webhook ID, secret, device identifiers and values.
  Metric keys, units and timestamps remain visible.

## Network behavior

- No analytics, telemetry or cloud service.
- No outbound calls from the integration.
- The app only sends to the configured webhook URL.
