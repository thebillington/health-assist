# App Store screenshots

Five 1290 × 2796 screenshots: one full app screen and four individual app
sections.

| # | Screenshot | What it shows |
| --- | --- | --- |
| 1 | Setup | The full app screen: webhook, secret, Health access and sync. |
| 2 | Sync | Sync Now, test payload, re-export and the result card. |
| 3 | Latest Values | The metrics the app has sent. |
| 4 | Privacy | The iPhone → HTTPS → Home Assistant flow and Keychain storage. |
| 5 | Tip Jar | The optional StoreKit tips and the docs links. |

Screenshots 2–5 are individual app sections rendered from HTML mockups, not full
device captures. The first is the full setup screen. No marketing panels or
App Store walkthroughs.

The rendered files are **not committed and not published** on the docs site.
They are written to `promo/images/sections/` for the local preview and for the
App Store upload.

## Rebuild

```bash
# Setup screen used by screenshot 1 (set CHROME if the default path is wrong)
python3 osg/make_screens.py

# Screenshots 1-5
python3 osg/make_sections.py
```

## Files

- `make_screens.py` renders `screenshots/01-setup.png`.
- `make_sections.py` renders the five App Store screenshots.
- `../screenshots/01-app.png` is the real simulator capture, kept for reference.

## Notes

- The container has no Xcode, so the screenshots are HTML mockups of the app's
  own sections. They must still match the shipped UI before upload.
- The first screenshot is a full app screen; the rest are sections, so every
  image shows actual app UI rather than a text-only marketing panel.
