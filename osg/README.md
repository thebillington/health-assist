# Promotion assets

The App Store set is a custom OSG project, not a template: a technical
blueprint style with a thin grid, Space Grotesk headlines, teal accents and a
straight-on iPhone frame. It is committed as `project.json`; `out/` is
disposable.

## Boards

| # | Board | Source screen |
| --- | --- | --- |
| 1 | Setup | `screenshots/01-setup.png` (`01-app.png` is the real simulator capture) |
| 2 | History | `screenshots/02-sync.png` |
| 3 | Sensors | `screenshots/03-values.png` |
| 4 | Privacy | `screenshots/04-privacy.png` |
| 5 | Sponsor | `screenshots/08-sponsor.png` |
| 6 | QR setup | `screenshots/05-qr.png` |
| 7 | App Store search | `screenshots/06-search.png` |
| 8 | App Store product | `screenshots/07-product.png` |

Screens 02–08 are HTML mockups (`make_screens.py`) so they can be regenerated
without a Mac. The copy, alt text and social posts live in
[`appstore/PROMOTION.md`](../appstore/PROMOTION.md).

## Rebuild everything

```bash
# Logo, app icon and docs icons (pure Python, no dependencies)
python3 ios/scripts/make_icon.py

# App-screen mockups and the 1200x630 social card
# Set CHROME if the default browser path is wrong.
python3 osg/make_screens.py

# Rebuild the committed OSG project from the screenshots
python3 osg/build_project.py

# Render and audit the 1290x2796 boards
osg render --formats ios-6-9
osg verify
```

Copy the eight rendered boards to `docs/images/store/` using the names in
`docs/screenshots.md`, and copy `01` to `docs/images/app.png` for the docs home
page.

## Files

- `osg.config.ts` pins the format (`ios-6-9`) and the output directory.
- `project.json` is the design source of truth. Edit it with `osg studio`, or
  edit `build_project.py` and regenerate.
- `make_screens.py` renders the app mockups and `docs/images/og.png`.
- `build_project.py` writes `project.json` with the copy and layout.
- `out/` is ignored; the committed renders live in `docs/images/store/`.

## Known limits

- The container has no Xcode, so screens 02–08 are mockups, not device captures.
- WebGL uses SwiftShader, so the 3D device frame can differ slightly from a Mac.
- No preview video: Chrome for Testing lacks proprietary codecs.
- Use `/usr/local/bin/osg` (the pinned Node 20 wrapper), not a system `npx`.
