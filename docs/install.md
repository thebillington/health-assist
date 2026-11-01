# Install

## Requirements

- Home Assistant 2024.1 or newer.
- HACS, or manual installation.
- For the iOS app: iOS 18+, Xcode 16+ and a development team for signing.
- HTTPS if the phone is outside the LAN. Plain HTTP works on a trusted LAN.

## HACS custom repository

Health Bridge is not in the default HACS store yet.

1. Open **HACS → Integrations**.
2. Open the three-dot menu → **Custom repositories**.
3. Add:

   ```text
   https://github.com/thebillington/health-assist
   ```

   Category: **Integration**.
4. Search for **Home Assistant Health Bridge**, install it and restart Home Assistant.
5. Open **Settings → Devices & services → Add integration → Home Assistant Health Bridge**.

## Manual installation

Copy `custom_components/apple_health_sync` from the repository into your Home
Assistant `config/custom_components/` directory, then restart Home Assistant.

## Updating

HACS: update from the integration page as usual.

Manual: replace the component directory and restart Home Assistant.

The iOS app is built from source; see [iOS app](ios.md). Reinstall after pulling
a new version.

## Uninstall

Remove the config entry first, then the custom component and restart Home
Assistant. Imported long-term statistics remain in the recorder database until
purged.
