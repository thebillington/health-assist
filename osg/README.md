# Marketing assets

The store screenshot project is generated with
[Open Screenshot Generator](https://github.com/dotnetdreamer/open-screenshot-generator)
(`osg`). The project file is committed; rendered output is disposable.

```bash
# from the repository root, with osg installed
osg fill --screenshots screenshots --force
osg render
osg verify
```

- `screenshots/01-app.png` is the source app screenshot.
- `osg/osg.config.ts` pins the template and formats.
- `osg/project.json` is the design; edit copy here (or with `osg studio`).
- `osg/out/` is ignored. Copy the chosen PNG to
  `docs/images/store/` before committing.

The template used is `template_somnia-sleep` with Health Assist copy. Replace
the screenshot and rerun `fill --force` for a new board. The generated board is
`docs/images/store/01-health-assist.png`.

The app icon is generated separately, without OSG:

```bash
python3 ios/scripts/make_icon.py
```

Known dev-container limitations:

- No MP4 preview video: Chrome for Testing lacks proprietary codecs.
- WebGL uses SwiftShader, so 3D device frames can differ.
- Use `/usr/local/bin/osg` (the pinned Node 20 wrapper), not a system `npx`.
