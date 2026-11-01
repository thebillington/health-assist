# App Store screenshots

The set is deliberately simple: five 1290 × 2796 boards.

| # | Board | Source |
| --- | --- | --- |
| 1 | App screenshot | `screenshots/01-setup.png` (`01-app.png` is the real simulator capture) |
| 2 | Full history | text panel |
| 3 | Native sensors | text panel |
| 4 | Local-first | text panel |
| 5 | Free and open source | text panel |

No phone frames, marketing props, App Store search panels or social card. The
first board is the app; the rest explain a feature in plain text.

The rendered set is **not committed and not published** on the docs site. Use
`promo/` (gitignored) for a local preview.

## Rebuild

```bash
# Setup-screen mockup for board 1. Set CHROME if the default path is wrong.
python3 osg/make_screens.py

# Rebuild the committed OSG project
python3 osg/build_project.py

# Render and audit the 1290x2796 boards
osg render --formats ios-6-9
osg verify
```

Rendered files land in `osg/out/`. Copy them to `promo/images/simple/` for the
local preview, or use them directly for the App Store upload.

## Files

- `osg.config.ts` pins the format (`ios-6-9`) and the output directory.
- `project.json` is the design source of truth.
- `build_project.py` writes the five boards and their copy.
- `make_screens.py` renders the setup-screen mockup.
- `out/` is ignored.

## Known limits

- The container has no Xcode, so `screenshots/01-setup.png` is an HTML mockup,
  not a device capture. `screenshots/01-app.png` is the real simulator capture.
- Use `/usr/local/bin/osg` (the pinned Node 20 wrapper), not a system `npx`.
