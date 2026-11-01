#!/usr/bin/env python3
# ruff: noqa: E501
"""Render the App Store screenshot set from individual app sections.

Board 1 is the real setup screen. Boards 2-5 are single sections of the app
(Sync, Latest Values, Privacy, Tip Jar), enlarged on a plain background so the
screenshot shows actual app UI rather than a marketing panel.

    python3 osg/make_sections.py
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
OUT = ROOT / "promo" / "images" / "sections"
SCREEN = SHOTS / "01-setup.png"
ICON = (
    ROOT / "ios" / "AppleHealthSync" / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon-1024.png"
)

CHROME_CANDIDATES = (
    os.environ.get("CHROME"),
    "/home/dev/.cache/open-screenshot-generator/browsers/chrome/linux-155.0.8059.84/chrome-linux64/chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; width: 1290px; height: 2796px; overflow: hidden; }
body {
  background: #F2F2F7;
  color: #000;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}
.page { position: relative; display: flex; flex-direction: column; justify-content: center; height: 100%; padding: 90px 90px 0; }
.brand { display: flex; align-items: center; gap: 18px; }
.brand img { width: 64px; height: 64px; border-radius: 16px; }
.eyebrow { font-size: 26px; font-weight: 600; letter-spacing: .12em; color: #0F766E; text-transform: uppercase; }
h1 { margin: 18px 0 14px; font-size: 88px; line-height: 1.02; letter-spacing: -2px; }
.caption { max-width: 1080px; margin: 0; color: #6D6D72; font-size: 38px; line-height: 1.4; }
.card { margin-top: 46px; overflow: hidden; border-radius: 36px; background: #fff; }
.label { padding: 32px 36px 10px; color: #6D6D72; font-size: 34px; }
.row {
  display: flex; align-items: center; justify-content: space-between; gap: 24px;
  min-height: 140px; padding: 32px 40px; border-bottom: 1px solid #E5E5EA; font-size: 50px;
}
.row:last-child { border-bottom: 0; }
.muted { color: #8E8E93; }
.small { font-size: 34px; }
.teal { color: #0F766E; }
.toggle { width: 96px; height: 58px; border-radius: 29px; background: #34C759; position: relative; flex: 0 0 auto; }
.toggle::after { content: ""; position: absolute; top: 4px; right: 4px; width: 50px; height: 50px; border-radius: 50%; background: #fff; }
.flow { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 34px 36px; }
.flow .box { flex: 1; text-align: center; }
.flow .circle { width: 108px; height: 108px; margin: 0 auto 14px; border-radius: 28px; background: #ECFDF5; display: flex; align-items: center; justify-content: center; font-size: 46px; color: #0F766E; }
.flow .name { font-size: 32px; font-weight: 600; }
.flow .sub { margin-top: 4px; color: #8E8E93; font-size: 26px; }
.flow .arrow { font-size: 34px; color: #0F766E; }
.footer { position: absolute; left: 90px; right: 90px; bottom: 70px; color: #8E8E93; font-size: 28px; line-height: 1.4; }
.full { height: 100%; padding: 86px 41px; background: #fff; }
.full img { display: block; width: 1208px; height: 2626px; border: 2px solid #E2E8F0; border-radius: 24px; }
"""


def header(eyebrow: str, title: str, caption: str) -> str:
    return f'<div class="brand"><img src="file://{ICON}" alt=""><div class="eyebrow">{eyebrow}</div></div><h1>{title}</h1><p class="caption">{caption}</p>'


def row(left: str, right: str = "", muted: bool = False, small: bool = False) -> str:
    cls = "row"
    if muted:
        cls += " muted"
    if small:
        cls += " small"
    return f'<div class="{cls}"><span>{left}</span><span>{right}</span></div>'


def toggle_row(left: str) -> str:
    return f'<div class="row"><span>{left}</span><div class="toggle"></div></div>'


def board_01() -> str:
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="full"><img src="file://{SCREEN}"></div></body></html>'


def board_02() -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  {header("HEALTH SYNC", "Sync", "Manual sync, test payload and full history.")}
  <div class="card">
    {row("Sync Now", "", small=False).replace('class="row"', 'class="row teal"')}
    {row("Send a Test Payload")}
    {row("Re-export All History")}
  </div>
  <div class="card">
    <div class="label">Result</div>
    {row("Sync complete — 24 metrics sent, 0 ignored.", "", small=True)}
    {row("Last successful sync", "Today, 15:24", muted=True)}
    {row("Last background sync", "Today, 14:00", muted=True)}
  </div>
  <div class="footer">The first sync exports your full HealthKit history. Later syncs send only new data.</div>
</div></body></html>"""


def board_03() -> str:
    rows = [
        ("Steps", "8,412"),
        ("Resting heart rate", "58 bpm"),
        ("Sleep", "7h 32m"),
        ("Weight", "74.2 kg"),
        ("Active energy", "612 kcal"),
        ("Heart rate variability", "48 ms"),
        ("Blood oxygen", "98%"),
        ("Flights climbed", "9"),
    ]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  {header("HEALTH SYNC", "Latest Values", "The readings the app has sent.")}
  <div class="card">
    {"".join(row(name, value, muted=True) for name, value in rows)}
  </div>
  <div class="footer">Read from Apple Health and sent to your Home Assistant. The app never writes to Apple Health.</div>
</div></body></html>"""


def board_04() -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  {header("HEALTH SYNC", "Privacy", "Read-only Apple Health access. Nothing else.")}
  <div class="card">
    <div class="flow">
      <div class="box"><div class="circle">♥</div><div class="name">iPhone</div><div class="sub">HealthKit</div></div>
      <div class="arrow">→</div>
      <div class="box"><div class="circle">TLS</div><div class="name">HTTPS</div><div class="sub">webhook</div></div>
      <div class="arrow">→</div>
      <div class="box"><div class="circle">⌂</div><div class="name">Home</div><div class="sub">Assistant</div></div>
    </div>
    {row("Webhook &amp; secret", "iOS Keychain", muted=True)}
    {row("Data stored by app", "None", muted=True)}
    {row("Transport", "HTTPS", muted=True)}
  </div>
  <div class="footer">No account, no analytics, no telemetry and no vendor cloud. The app never writes to Apple Health.</div>
</div></body></html>"""


def board_05() -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  {header("HEALTH SYNC", "Tip Jar", "Optional. Unlocks nothing.")}
  <div class="card">
    <div class="label">Choose a tip</div>
    {row("Small tip")}
    {row("Medium tip")}
    {row("Large tip")}
  </div>
  <div class="card">
    {row("Privacy Policy")}
    {row("Documentation")}
    {row("HACS setup guide")}
  </div>
  <div class="footer">Tips are optional and unlock nothing. Prices are shown in the app. The app is complete without a tip.</div>
</div></body></html>"""


BOARDS = {
    "01": board_01,
    "02": board_02,
    "03": board_03,
    "04": board_04,
    "05": board_05,
}


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("Chrome not found; set CHROME to a Chrome/Chromium binary.")


def main() -> None:
    chrome = find_chrome()
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="health-sync-sections-") as tmp:
        tmpdir = Path(tmp)
        for name, factory in BOARDS.items():
            html = tmpdir / f"{name}.html"
            html.write_text(factory(), encoding="utf-8")
            out = OUT / f"{name}.png"
            subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    "--allow-file-access-from-files",
                    "--force-device-scale-factor=1",
                    "--window-size=1290,2796",
                    "--virtual-time-budget=10000",
                    f"--screenshot={out}",
                    html.as_uri(),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
