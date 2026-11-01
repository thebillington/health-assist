# App Store screenshots

Five 1290 × 2796 boards. Each board has a large explanation and a smaller
screenshot of the relevant app section.

| # | Board | Screenshot |
| --- | --- | --- |
| 1 | Setup | The full setup screen. |
| 2 | Sync | The Sync and Result sections. |
| 3 | Latest Values | The metric list. |
| 4 | Privacy | The data flow, Keychain and transport rows. |
| 5 | Tip Jar | The optional StoreKit tips and the links. |

Boards 2–5 use cropped app sections rather than a full phone screen. The text is
an overlay; every board still shows the app's own UI.

The files are written to `promo/images/appstore/` for the local preview and the
App Store upload. They are **not committed and not published** on the docs site.

## Rebuild

```bash
# Setup screen, only needed if the app UI changes
python3 osg/make_screens.py

# All five App Store boards
python3 osg/make_appstore.py
```

## Files

- `make_screens.py` renders `screenshots/01-setup.png`.
- `make_appstore.py` renders the five final screenshots.
- `../screenshots/01-app.png` is the real simulator capture, kept for reference.

## Notes

- The container has no Xcode, so the app sections are HTML mockups of the real
  UI. They must match the shipped app before upload.
- Keep the large explanation text short enough to stay readable in the App
  Store carousel.
- The HACS walkthrough lives in the app's **HACS setup guide** and in the docs,
  not in the App Store screenshots.
