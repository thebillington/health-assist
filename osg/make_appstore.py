#!/usr/bin/env python3
# ruff: noqa: E501
"""Render the App Store set: large explanation text with a small section screenshot.

Each 1290x2796 board has a headline, a short explanation, and a phone-sized
screenshot of the relevant app section. The screenshots are the app's own UI,
not text-only marketing panels.

    python3 osg/make_appstore.py
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
OUT = ROOT / "promo" / "images" / "appstore"
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
body { background: #F2F2F7; color: #000; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; -webkit-font-smoothing: antialiased; }
.page { position: relative; height: 100%; padding: 90px 90px 0; }
.brand { display: flex; align-items: center; gap: 18px; }
.brand img { width: 64px; height: 64px; border-radius: 16px; }
.eyebrow { font-size: 26px; font-weight: 600; letter-spacing: .12em; color: #0F766E; text-transform: uppercase; }
h1 { margin: 18px 0 14px; font-size: 76px; line-height: 1.02; letter-spacing: -2px; }
.body { max-width: 1090px; margin: 0; color: #475569; font-size: 34px; line-height: 1.45; }
.footer { position: absolute; left: 90px; right: 90px; bottom: 64px; color: #8E8E93; font-size: 26px; line-height: 1.4; }
.visual { position: absolute; left: 195px; top: 820px; width: 900px; }
.full-shot { display: block; width: 800px; margin: 0 auto; border: 2px solid #E2E8F0; border-radius: 32px; box-shadow: 0 26px 70px rgba(15, 23, 42, .18); }
.shot-card { width: 900px; padding: 24px; border: 2px solid #E2E8F0; border-radius: 32px; background: #F2F2F7; box-shadow: 0 26px 70px rgba(15, 23, 42, .18); }
.screen { padding: 0; }
.section-title { padding: 12px 12px 8px; color: #6D6D72; font-size: 30px; }
.card { margin-bottom: 24px; overflow: hidden; border-radius: 22px; background: #fff; }
.row { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 84px; padding: 16px 22px; border-bottom: 1px solid #E5E5EA; font-size: 30px; }
.row:last-child { border-bottom: 0; }
.muted { color: #8E8E93; }
.small { font-size: 26px; }
.teal { color: #0F766E; }
.toggle { width: 58px; height: 36px; border-radius: 18px; background: #34C759; position: relative; flex: 0 0 auto; }
.toggle::after { content: ""; position: absolute; top: 3px; right: 3px; width: 30px; height: 30px; border-radius: 50%; background: #fff; }
.flow { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 20px 22px; }
.flow .box { flex: 1; text-align: center; }
.flow .circle { width: 66px; height: 66px; margin: 0 auto 8px; border-radius: 18px; background: #ECFDF5; display: flex; align-items: center; justify-content: center; font-size: 30px; color: #0F766E; }
.flow .name { font-size: 22px; font-weight: 600; }
.flow .sub { margin-top: 2px; color: #8E8E93; font-size: 18px; }
.flow .arrow { font-size: 24px; color: #0F766E; }
"""


def header(eyebrow: str, title: str, body: str) -> str:
    return (
        f'<div class="brand"><img src="file://{ICON}" alt=""><div class="eyebrow">{eyebrow}</div></div>'
        f'<h1>{title}</h1><p class="body">{body}</p>'
    )


def row(
    left: str, right: str = "", muted: bool = False, small: bool = False, teal: bool = False
) -> str:
    cls = "row"
    if muted:
        cls += " muted"
    if small:
        cls += " small"
    if teal:
        cls += " teal"
    return f'<div class="{cls}"><span>{left}</span><span>{right}</span></div>'


def toggle_row(left: str) -> str:
    return f'<div class="row"><span>{left}</span><div class="toggle"></div></div>'


def page(title: str, body: str, phone: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
  {header("HEALTH BRIDGE", title, body)}
  <div class="visual">{phone}</div>
  <div class="footer">HEALTH BRIDGE · APPLE HEALTH → HOME ASSISTANT</div>
</div></body></html>"""


def board_free() -> str:
    phone = f"""
    <div class="shot-card"><div class="screen">
      <div class="section-title">Sync</div>
      <div class="card">
        {row("Sync Now", teal=True)}
        {row("Send a Test Payload")}
        {row("Re-export All History")}
      </div>
      <div class="section-title">Result</div>
      <div class="card">
        {row("Sync complete — 24 metrics sent, 0 ignored.", small=True)}
        {row("Last successful sync", "Today, 15:24", muted=True, small=True)}
        {row("Last background sync", "Today, 14:00", muted=True, small=True)}
      </div>
    </div></div>"""
    return page(
        "Free.",
        "Scheduled Apple Health sync to your Home Assistant. No subscription. No account.",
        phone,
    )


def board_01() -> str:
    return page(
        "Set up once.",
        "Install the integration through HACS or manually. Paste the webhook URL or scan the QR code, then grant read-only Health access. The phone must be able to reach Home Assistant directly: the same Wi-Fi, a VPN such as Tailscale, or a remote URL such as Nabu Casa.",
        f'<img class="full-shot" src="file://{SCREEN}" alt="">',
    )


def board_02() -> str:
    phone = f"""
    <div class="shot-card"><div class="screen">
      <div class="section-title">Sync</div>
      <div class="card">
        {row("Sync Now", teal=True)}
        {row("Send a Test Payload")}
        {row("Re-export All History")}
      </div>
      <div class="section-title">Result</div>
      <div class="card">
        {row("Sync complete — 24 metrics sent, 0 ignored.", small=True)}
        {row("Last successful sync", "Today, 15:24", muted=True, small=True)}
        {row("Last background sync", "Today, 14:00", muted=True, small=True)}
      </div>
    </div></div>"""
    return page(
        "Sync when you want.",
        "Sync Now sends the latest readings. Send a Test Payload checks the webhook. Re-export All History sends everything again. The result shows what was sent and ignored.",
        phone,
    )


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
    phone = f"""
    <div class="shot-card"><div class="screen">
      <div class="section-title">Latest Values</div>
      <div class="card">
        {"".join(row(name, value, muted=True) for name, value in rows)}
      </div>
    </div></div>"""
    return page(
        "See what was sent.",
        "Steps, sleep, heart rate, weight and other readings become Home Assistant sensors with units and long-term statistics. The first sync sends all available history; later syncs send new data.",
        phone,
    )


def board_04() -> str:
    phone = f"""
    <div class="shot-card"><div class="screen">
      <div class="section-title">Privacy</div>
      <div class="card">
        <div class="flow">
          <div class="box"><div class="circle">♥</div><div class="name">iPhone</div><div class="sub">HealthKit</div></div>
          <div class="arrow">→</div>
          <div class="box"><div class="circle">TLS</div><div class="name">HTTPS</div><div class="sub">webhook</div></div>
          <div class="arrow">→</div>
          <div class="box"><div class="circle">⌂</div><div class="name">Home</div><div class="sub">Assistant</div></div>
        </div>
        {row("Webhook &amp; secret", "iOS Keychain", muted=True, small=True)}
        {row("Data stored by app", "None", muted=True, small=True)}
        {row("Transport", "HTTPS", muted=True, small=True)}
      </div>
    </div></div>"""
    return page(
        "Read-only and local.",
        "The app reads Apple Health and never writes to it. The webhook URL and secret stay in the iOS Keychain. There is no account, analytics, telemetry or vendor cloud.",
        phone,
    )


def board_05() -> str:
    phone = f"""
    <div class="shot-card"><div class="screen">
      <div class="section-title">Tip Jar</div>
      <div class="card">
        {row("Small tip")}
        {row("Medium tip")}
        {row("Large tip")}
      </div>
      <div class="section-title">Links</div>
      <div class="card">
        {row("Privacy Policy")}
        {row("Documentation")}
        {row("HACS setup guide")}
      </div>
    </div></div>"""
    return page(
        "Free, with an optional tip.",
        "The app and integration are free and MIT licensed. The Tip Jar uses Apple's in-app purchase and unlocks nothing. The app is complete without a tip.",
        phone,
    )


BOARDS = {
    "01": board_free,
    "02": board_01,
    "03": board_02,
    "04": board_03,
    "05": board_04,
    "06": board_05,
}


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("Chrome not found; set CHROME to a Chrome/Chromium binary.")


def main() -> None:
    chrome = find_chrome()
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="health-sync-appstore-") as tmp:
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
