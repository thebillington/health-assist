#!/usr/bin/env python3
# ruff: noqa: E501
"""Render the setup-screen mockup used by the App Store screenshot.

The real app screenshot comes from the simulator; this is a matching mockup for
the setup screen so the first board can show an "Authorized" state. It is plain
HTML rendered with headless Chrome, so the copy and layout stay editable.

    python3 osg/make_screens.py

Set CHROME to a Chrome/Chromium binary if the default guess is wrong.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "screenshots"
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

STATUS_LIGHT = """
<svg width="170" height="34" viewBox="0 0 170 34" fill="none" aria-hidden="true">
  <rect x="0" y="18" width="5" height="10" rx="1.5" fill="#000"/>
  <rect x="8" y="14" width="5" height="14" rx="1.5" fill="#000"/>
  <rect x="16" y="10" width="5" height="18" rx="1.5" fill="#000"/>
  <rect x="24" y="5" width="5" height="23" rx="1.5" fill="#000"/>
  <path d="M48 16c4-4 10-4 14 0M52 20c2-2 6-2 8 0" stroke="#000" stroke-width="3" stroke-linecap="round"/>
  <circle cx="56" cy="27" r="2" fill="#000"/>
  <rect x="82" y="8" width="38" height="18" rx="5" stroke="#000" stroke-width="2"/>
  <rect x="86" y="12" width="28" height="10" rx="2" fill="#000"/>
  <rect x="123" y="12" width="3" height="10" rx="1.5" fill="#000"/>
</svg>
"""

STATUS_DARK = STATUS_LIGHT.replace('fill="#000"', 'fill="#fff"').replace(
    'stroke="#000"', 'stroke="#fff"'
)

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {
  --bg: #F2F2F7; --card: #FFFFFF; --label: #000000; --secondary: #8E8E93;
  --separator: #E5E5EA; --teal: #0F766E; --green: #34C759; --blue: #007AFF;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; width: 1206px; height: 2622px; overflow: hidden; }
body {
  background: var(--bg); color: var(--label);
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}
.statusbar {
  height: 132px; display: flex; align-items: flex-end; justify-content: space-between;
  padding: 0 54px 20px; font-size: 34px; font-weight: 600; letter-spacing: .2px;
}
.statusbar .right { display: flex; align-items: center; gap: 16px; }
.nav { padding: 20px 48px 6px; font-size: 42px; font-weight: 700; letter-spacing: -.4px; }
.large-title { padding: 30px 48px 6px; font-size: 82px; font-weight: 700; letter-spacing: -2px; }
.subtitle { padding: 0 48px 8px; font-size: 30px; color: var(--secondary); }
.section { margin-top: 34px; }
.section-title { padding: 0 48px 14px; font-size: 32px; font-weight: 500; color: #6D6D72; }
.card { margin: 0 32px; background: var(--card); border-radius: 28px; overflow: hidden; }
.row {
  display: flex; align-items: center; justify-content: space-between; gap: 24px;
  min-height: 104px; padding: 24px 32px; font-size: 40px;
  border-bottom: 1px solid var(--separator);
}
.row:last-child { border-bottom: 0; }
.row .value { color: var(--secondary); font-variant-numeric: tabular-nums; }
.row .value.teal { color: var(--teal); }
.row.teal, .teal { color: var(--teal); }
.footer { padding: 14px 48px 0; font-size: 30px; line-height: 1.38; color: var(--secondary); }
.toggle { width: 88px; height: 52px; border-radius: 26px; background: var(--green); position: relative; flex: 0 0 auto; }
.toggle::after {
  content: ""; position: absolute; top: 4px; right: 4px; width: 44px; height: 44px;
  border-radius: 50%; background: #fff; box-shadow: 0 2px 6px rgba(0,0,0,.18);
}
.toggle.off { background: var(--separator); }
.toggle.off::after { right: auto; left: 4px; }
.icon { width: 44px; height: 44px; flex: 0 0 auto; }
.pill {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 104px; padding: 10px 26px; border-radius: 999px;
  background: var(--blue); color: #fff; font-size: 30px; font-weight: 700;
}
.mono { font-family: "DejaVu Sans Mono", monospace; }
"""


def statusbar(dark: bool = False) -> str:
    return f'<div class="statusbar"><span>15:28</span><span class="right">{STATUS_DARK if dark else STATUS_LIGHT}</span></div>'


def heart_icon(color: str = "#0F766E") -> str:
    return f'<svg class="icon" viewBox="0 0 24 24" fill="{color}"><path d="M12 21s-8-5.1-8-11a4.6 4.6 0 018-3 4.6 4.6 0 018 3c0 5.9-8 11-8 11z"/></svg>'


def shield_icon(color: str = "#0F766E") -> str:
    return f'<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M12 3l7 3v5c0 4.4-3 8.2-7 10-4-1.8-7-5.6-7-10V6l7-3z"/><path d="M9 12l2 2 4-4"/></svg>'


def book_icon(color: str = "#0F766E") -> str:
    return f'<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"><path d="M4 4h9a3 3 0 013 3v13H7a3 3 0 01-3-3V4z"/><path d="M16 7h3a2 2 0 012 2v11H12"/></svg>'


def search_icon(color: str = "#8E8E93") -> str:
    return f'<svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>'


def qr_svg(size: int = 25) -> str:
    """A deterministic QR-looking matrix, not a readable code."""
    modules = []
    finder = {(0, 0), (size - 7, 0), (0, size - 7)}

    def in_finder(x: int, y: int) -> bool:
        return any(fx <= x < fx + 7 and fy <= y < fy + 7 for fx, fy in finder)

    def finder_on(x: int, y: int) -> bool:
        for fx, fy in finder:
            if fx <= x < fx + 7 and fy <= y < fy + 7:
                lx, ly = x - fx, y - fy
                if lx in (0, 6) or ly in (0, 6):
                    return True
                return 2 <= lx <= 4 and 2 <= ly <= 4
        return False

    for y in range(size):
        for x in range(size):
            on = False
            if in_finder(x, y):
                on = finder_on(x, y)
            elif x == 6 or y == 6:
                on = (x + y) % 2 == 0
            else:
                on = ((x * 7 + y * 13 + x * y * 3) % 17) < 8
            if on:
                modules.append(f'<rect x="{x}" y="{y}" width="1" height="1"/>')

    return (
        f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" '
        f'shape-rendering="crispEdges"><rect width="{size}" height="{size}" fill="#fff"/>'
        f'<g fill="#000">{"".join(modules)}</g></svg>'
    )


def screen_02_sync() -> str:
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head><body>
      {statusbar()}
      <div class="large-title">Health Sync</div>
      <div class="subtitle">Sync and history</div>

      <section class="section">
        <div class="section-title">Apple Health</div>
        <div class="card">
          <div class="row"><span>Status</span><span class="value">Authorized</span></div>
          <div class="row teal"><span>Request Health Access</span></div>
          <div class="row"><span>Include additional<br>HealthKit metrics</span><div class="toggle"></div></div>
        </div>
        <div class="footer">Read-only access. The app never writes to Apple Health. iOS does not reveal which read permissions were granted.</div>
      </section>

      <section class="section">
        <div class="section-title">Sync</div>
        <div class="card">
          <div class="row teal"><span>Sync Now</span></div>
          <div class="row"><span>Send a Test Payload</span></div>
          <div class="row"><span>Re-export All History</span></div>
        </div>
        <div class="footer">The first sync exports your full HealthKit history in resumable chunks, then keeps it up to date.</div>
      </section>

      <section class="section">
        <div class="section-title">Result</div>
        <div class="card">
          <div class="row" style="display:block"><div style="font-size:31px;line-height:1.4;color:#8E8E93">Sync complete — 24 metrics sent, 0 ignored.</div></div>
          <div class="row"><span>Last successful sync</span><span class="value">Today, 15:24</span></div>
          <div class="row"><span>Last background sync</span><span class="value">Today, 14:00</span></div>
        </div>
      </section>

      <section class="section">
        <div class="section-title">Latest Values</div>
        <div class="card">
          <div class="row"><span>Steps</span><span style="display:flex;align-items:baseline;gap:10px"><span style="font-size:42px">8,412</span><span style="font-size:28px;color:#8E8E93">steps</span></span></div>
          <div class="row"><span>Resting heart rate</span><span style="display:flex;align-items:baseline;gap:10px"><span style="font-size:42px">58</span><span style="font-size:28px;color:#8E8E93">bpm</span></span></div>
          <div class="row"><span>Sleep</span><span style="font-size:42px">7h 32m</span></div>
        </div>
      </section>
    </body></html>
    """


def screen_03_values() -> str:
    rows = [
        ("Steps", "8,412", "steps", False),
        ("Resting heart rate", "58", "bpm", False),
        ("Sleep", "7h 32m", "", False),
        ("Weight", "74.2", "kg", False),
        ("Active energy", "612", "kcal", False),
        ("Heart rate variability", "48", "ms", True),
        ("Blood oxygen", "98", "%", False),
        ("Flights climbed", "9", "flights", False),
        ("Water", "1.8", "L", True),
        ("Body fat", "18.4", "%", False),
        ("VO₂ max", "47.2", "mL/kg·min", False),
        ("Respiratory rate", "14.6", "br/min", False),
        ("Stand hours", "11", "h", False),
    ]
    body = "".join(
        f'<div class="row"><span>{name}'
        + (
            '<br><span style="font-size:24px;color:#8E8E93">Additional metric</span>'
            if extra
            else ""
        )
        + f"</span>"
        f'<span style="display:flex;align-items:baseline;gap:10px"><span style="font-size:42px;font-variant-numeric:tabular-nums">{value}</span>'
        f'<span style="font-size:28px;color:#8E8E93">{unit}</span></span></div>'
        for name, value, unit, extra in rows
    )
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head><body>
      {statusbar()}
      <div class="nav">Health Sync</div>
      <div class="large-title">Latest Values</div>
      <div class="subtitle">Last sync: 2 minutes ago</div>

      <section class="section">
        <div class="section-title">HealthKit</div>
        <div class="card">{body}</div>
        <div class="footer">Values are read from Apple Health and sent to your Home Assistant instance. Sensors appear automatically after the first sync.</div>
      </section>

      <section class="section">
        <div class="section-title">Sync</div>
        <div class="card">
          <div class="row teal"><span>Sync Now</span></div>
        </div>
      </section>
    </body></html>
    """


def screen_04_privacy() -> str:
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head><body>
      {statusbar()}
      <div class="large-title" style="font-size:70px">Your data<br>stays yours</div>
      <div class="subtitle" style="padding-top:10px">Local-first by design.</div>

      <section class="section">
        <div class="section-title">Data flow</div>
        <div class="card" style="padding:34px 32px">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:14px;text-align:center">
            <div style="flex:1"><div style="width:96px;height:96px;margin:0 auto 14px;border-radius:26px;background:#ECFDF5;display:flex;align-items:center;justify-content:center;font-size:44px">♥</div><div style="font-size:26px;font-weight:600">iPhone</div><div style="font-size:22px;color:#8E8E93">HealthKit</div></div>
            <div style="font-size:30px;color:#0F766E">→</div>
            <div style="flex:1"><div style="width:96px;height:96px;margin:0 auto 14px;border-radius:26px;background:#F1F5F9;display:flex;align-items:center;justify-content:center;font-size:30px;color:#0F766E">TLS</div><div style="font-size:26px;font-weight:600">HTTPS</div><div style="font-size:22px;color:#8E8E93">webhook</div></div>
            <div style="font-size:30px;color:#0F766E">→</div>
            <div style="flex:1"><div style="width:96px;height:96px;margin:0 auto 14px;border-radius:26px;background:#ECFDF5;display:flex;align-items:center;justify-content:center;font-size:44px">⌂</div><div style="font-size:26px;font-weight:600">Home</div><div style="font-size:22px;color:#8E8E93">Assistant</div></div>
          </div>
        </div>
        <div class="footer">No analytics, no telemetry and no cloud service. The webhook URL and shared secret are stored in the iOS Keychain.</div>
      </section>

      <section class="section">
        <div class="section-title">Support</div>
        <div class="card">
          <div class="row teal"><span style="display:flex;align-items:center;gap:22px">{heart_icon()}<span>Support Me</span></span></div>
          <div class="row teal"><span style="display:flex;align-items:center;gap:22px">{shield_icon()}<span>Privacy Policy</span></span></div>
          <div class="row teal"><span style="display:flex;align-items:center;gap:22px">{book_icon()}<span>Documentation</span></span></div>
        </div>
        <div class="footer">Health Sync is free and open source. Sponsorship is optional and unlocks no features.</div>
      </section>

      <section class="section">
        <div class="section-title">Security</div>
        <div class="card">
          <div class="row"><span>Webhook URL &amp; secret</span><span class="value">iOS Keychain</span></div>
          <div class="row"><span>Transport</span><span class="value">HTTPS</span></div>
          <div class="row"><span>Data stored by app</span><span class="value">None</span></div>
        </div>
        <div class="footer">Revoke Apple Health access at any time in Settings → Privacy &amp; Security → Health → Health Sync.</div>
      </section>
    </body></html>
    """


def screen_05_qr() -> str:
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
      body {{ background:#000; color:#fff; }}
      .top {{ display:flex; align-items:center; justify-content:space-between; padding: 26px 48px; font-size:36px; }}
      .top .cancel {{ color:#2DD4BF; }}
      .top .title {{ font-weight:600; }}
      .camera {{ position:relative; height:1960px; background:radial-gradient(circle at 50% 40%, #164E63 0%, #0B1220 55%, #020617 100%); }}
      .finder {{ position:absolute; left:50%; top:50%; width:760px; height:760px; transform:translate(-50%,-50%); border-radius:48px; }}
      .corner {{ position:absolute; width:120px; height:120px; border:10px solid #5EEAD4; }}
      .tl {{ left:0; top:0; border-right:0; border-bottom:0; border-radius:44px 0 0 0; }}
      .tr {{ right:0; top:0; border-left:0; border-bottom:0; border-radius:0 44px 0 0; }}
      .bl {{ left:0; bottom:0; border-right:0; border-top:0; border-radius:0 0 0 44px; }}
      .br {{ right:0; bottom:0; border-left:0; border-top:0; border-radius:0 0 44px 0; }}
      .qr {{ position:absolute; left:50%; top:50%; width:540px; height:540px; transform:translate(-50%,-50%); border-radius:20px; overflow:hidden; }}
      .hint {{ padding: 46px 90px 0; text-align:center; color:#CBD5E1; font-size:34px; line-height:1.4; }}
      .scanline {{ position:absolute; left:0; right:0; top:48%; height:6px; background:linear-gradient(90deg, transparent, #5EEAD4, transparent); opacity:.9; }}
    </style></head><body>
      {statusbar(dark=True)}
      <div class="top"><span class="cancel">Cancel</span><span class="title">Scan QR Code</span><span style="width:110px"></span></div>
      <div class="camera">
        <div class="finder">
          <div class="corner tl"></div><div class="corner tr"></div><div class="corner bl"></div><div class="corner br"></div>
          <div class="scanline"></div>
        </div>
        <div class="qr">{qr_svg()}</div>
      </div>
      <div class="hint">Point your iPhone at the QR code in Home Assistant to import the webhook URL and shared secret.</div>
    </body></html>
    """


def screen_06_search() -> str:
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
      body {{ background:#F2F2F7; }}
      .searchbar {{ display:flex; align-items:center; gap:18px; margin: 6px 32px 0; padding: 20px 28px; background:#E3E3E8; border-radius:24px; font-size:38px; color:#3C3C43; }}
      .searchbar .field {{ flex:1; }}
      .searchbar .cancel {{ color:#007AFF; font-size:34px; }}
      .label {{ padding: 40px 48px 16px; font-size:30px; font-weight:600; color:#6D6D72; }}
      .result {{ display:flex; align-items:center; gap:26px; background:#fff; margin:0 32px; padding:26px 28px; border-radius:28px; }}
      .appicon {{ width:150px; height:150px; border-radius:34px; }}
      .meta {{ flex:1; min-width:0; }}
      .name {{ font-size:40px; font-weight:600; }}
      .sub {{ font-size:30px; color:#8E8E93; margin-top:6px; }}
      .rating {{ font-size:26px; color:#8E8E93; margin-top:10px; }}
      .stars {{ color:#F5A623; letter-spacing:2px; }}
      .row2 {{ display:flex; align-items:center; justify-content:space-between; margin: 26px 32px 0; padding: 24px 30px; background:#fff; border-radius:24px; }}
      .row2 .left {{ display:flex; align-items:center; gap:22px; }}
      .dot {{ width:96px; height:96px; border-radius:24px; background:#E2E8F0; display:flex; align-items:center; justify-content:center; font-size:38px; }}
    </style></head><body>
      {statusbar()}
      <div class="searchbar">{search_icon()}<span class="field">health assist</span><span class="cancel">Cancel</span></div>
      <div class="label">TOP RESULT</div>
      <div class="result">
        <img class="appicon" src="file://{ICON}">
        <div class="meta">
          <div class="name">Health Sync</div>
          <div class="sub">Apple Health to Home Assistant</div>
          <div class="rating"><span class="stars">★★★★★</span> 4.9 · Health &amp; Fitness</div>
        </div>
        <span class="pill">GET</span>
      </div>
      <div class="label">YOU MIGHT ALSO LIKE</div>
      <div class="row2"><div class="left"><div class="dot">⌂</div><div><div style="font-size:34px;font-weight:600">Home Assistant</div><div style="font-size:26px;color:#8E8E93">Utilities</div></div></div><span class="pill" style="background:#E5E5EA;color:#007AFF">GET</span></div>
      <div class="row2"><div class="left"><div class="dot">♥</div><div><div style="font-size:34px;font-weight:600">Health</div><div style="font-size:26px;color:#8E8E93">Health &amp; Fitness</div></div></div><span class="pill" style="background:#E5E5EA;color:#007AFF">OPEN</span></div>
      <div class="label">RECENT SEARCHES</div>
      <div class="card" style="margin:0 32px">
        <div class="row"><span>health assist</span><span class="value">↗</span></div>
        <div class="row"><span>home assistant</span><span class="value">↗</span></div>
        <div class="row"><span>healthkit webhook</span><span class="value">↗</span></div>
      </div>
    </body></html>
    """


def screen_07_product() -> str:
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
      body {{ background:#fff; }}
      .top {{ display:flex; align-items:center; justify-content:space-between; padding: 10px 40px 0; font-size:34px; color:#007AFF; }}
      .hero {{ display:flex; gap:30px; padding: 36px 40px 0; }}
      .appicon {{ width:210px; height:210px; border-radius:48px; flex:0 0 auto; box-shadow:0 8px 22px rgba(15,23,42,.12); }}
      .hero .meta {{ flex:1; padding-top:6px; }}
      .name {{ font-size:46px; font-weight:700; letter-spacing:-.5px; }}
      .sub {{ font-size:32px; color:#8E8E93; margin-top:6px; }}
      .getrow {{ display:flex; align-items:center; justify-content:space-between; margin-top:26px; }}
      .get {{ padding: 10px 44px; border-radius:999px; background:#007AFF; color:#fff; font-weight:700; font-size:32px; }}
      .share {{ width:52px; height:52px; color:#007AFF; }}
      .facts {{ display:flex; justify-content:space-between; padding: 40px 48px 30px; border-bottom:1px solid #E5E5EA; margin: 30px 0 0; }}
      .fact {{ text-align:center; flex:1; }}
      .fact .big {{ font-size:34px; font-weight:600; color:#3C3C43; }}
      .fact .small {{ font-size:24px; color:#8E8E93; margin-top:6px; text-transform:uppercase; letter-spacing:.5px; }}
      .strip {{ display:flex; gap:20px; padding: 36px 40px 0; overflow:hidden; }}
      .shot {{ width:258px; height:560px; border-radius:22px; object-fit:cover; object-position:top; border:1px solid #E5E5EA; }}
      .desc {{ padding: 40px 48px 0; font-size:32px; line-height:1.45; color:#1C1C1E; }}
      .desc b {{ color:#000; }}
    </style></head><body>
      {statusbar()}
      <div class="top"><span>&lsaquo; Search</span><svg class="share" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M8 7l4-4 4 4"/><path d="M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"/></svg></div>
      <div class="hero">
        <img class="appicon" src="file://{ICON}">
        <div class="meta">
          <div class="name">Health Sync</div>
          <div class="sub">Apple Health to Home Assistant</div>
          <div class="getrow"><span class="get">GET</span><span style="font-size:28px;color:#8E8E93">In-App<br>Purchases: No</span></div>
        </div>
      </div>
      <div class="facts">
        <div class="fact"><div class="big">4.9</div><div class="small">★★★★★</div></div>
        <div class="fact"><div class="big">4+</div><div class="small">Age</div></div>
        <div class="fact"><div class="big">#1</div><div class="small">Health &amp; Fitness</div></div>
        <div class="fact"><div class="big">Free</div><div class="small">Price</div></div>
      </div>
      <div class="strip">
        <img class="shot" src="file://{SCREENSHOTS / "02-sync.png"}">
        <img class="shot" src="file://{SCREENSHOTS / "03-values.png"}">
        <img class="shot" src="file://{SCREENSHOTS / "04-privacy.png"}">
        <img class="shot" src="file://{SCREENSHOTS / "05-qr.png"}">
      </div>
      <div class="desc"><b>Apple Health, meet Home Assistant.</b><br>A free, local-first bridge that turns your HealthKit data into native sensors — no cloud, no account, no telemetry.</div>
      <div class="label" style="padding-top:40px">WHAT'S NEW</div>
      <div class="desc" style="padding-top:0"><b>Version 1.2.0</b><br>Full history export, background sync, QR setup and an optional Support Me link.</div>
      <div class="desc" style="padding-top:24px">
        • Read-only HealthKit access<br>
        • Native sensors and long-term statistics<br>
        • Webhook URL and secret in the iOS Keychain<br>
        • Free and open source, no account
      </div>
    </body></html>
    """


def screen_08_sponsor() -> str:
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head><body>
      {statusbar()}
      <div class="large-title" style="font-size:74px">Support<br>Health Sync</div>
      <div class="subtitle" style="padding-top:10px">Free and open source, on both sides.</div>

      <section class="section">
        <div class="section-title">Why sponsor</div>
        <div class="card">
          <div class="row"><span>Paid tier</span><span class="value">None</span></div>
          <div class="row"><span>Account required</span><span class="value">No</span></div>
          <div class="row"><span>Sponsor unlocks</span><span class="value">Nothing</span></div>
        </div>
        <div class="footer">Sponsorship funds maintenance, device testing and App Store fees. It never gates a feature.</div>
      </section>

      <section class="section">
        <div class="section-title">Sponsor</div>
        <div class="card">
          <div class="row teal" style="min-height:130px"><span style="display:flex;align-items:center;gap:22px">{heart_icon()}<span>Support Me</span></span><span style="color:#8E8E93;font-size:30px">↗</span></div>
          <div class="row"><span style="font-size:28px;color:#8E8E93">github.com/sponsors/thebillington</span></div>
        </div>
        <div class="footer">MIT licensed. Sponsorship is optional and unlocks nothing — the app is complete without it.</div>
      </section>

      <section class="section">
        <div class="section-title">More</div>
        <div class="card">
          <div class="row teal"><span style="display:flex;align-items:center;gap:22px">{shield_icon()}<span>Privacy Policy</span></span></div>
          <div class="row teal"><span style="display:flex;align-items:center;gap:22px">{book_icon()}<span>Documentation</span></span></div>
        </div>
      </section>
    </body></html>
    """


def qr_icon(color: str = "#0F766E") -> str:
    return (
        f'<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v3M14 20h3M20 20h1"/>'
        "</svg>"
    )


def screen_01_setup() -> str:
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head><body>
      {statusbar()}
      <div class="large-title">Health Sync</div>

      <section class="section">
        <div class="section-title">Home Assistant</div>
        <div class="card">
          <div class="row"><span class="value" style="font-size:33px">https://home.example.com/api/webhook/…</span></div>
          <div class="row"><span class="value" style="font-size:33px">Optional shared secret</span></div>
          <div class="row"><span>Sync when the app opens</span><div class="toggle"></div></div>
          <div class="row teal"><span style="display:flex;align-items:center;gap:22px">{qr_icon()}<span>Scan QR Code</span></span></div>
        </div>
        <div class="footer">Create a webhook under Settings → Devices &amp; services → Health Sync. The full URL is a credential; keep it private.</div>
      </section>

      <section class="section">
        <div class="section-title">Apple Health</div>
        <div class="card">
          <div class="row"><span>Status</span><span class="value">Authorized</span></div>
          <div class="row teal"><span>Request Health Access</span></div>
          <div class="row"><span>Include additional<br>HealthKit metrics</span><div class="toggle"></div></div>
        </div>
        <div class="footer">Read-only access. The app never writes to Apple Health. If values are missing, check Settings → Privacy &amp; Security → Health → Health Sync.</div>
      </section>

      <section class="section">
        <div class="section-title">Sync</div>
        <div class="card">
          <div class="row teal"><span>Sync Now</span></div>
          <div class="row"><span>Send a Test Payload</span></div>
          <div class="row"><span>Re-export All History</span></div>
        </div>
        <div class="footer">The first sync exports your full HealthKit history, then keeps it current in the background.</div>
      </section>

      <section class="section">
        <div class="section-title">Result</div>
        <div class="card">
          <div class="row" style="display:block"><div style="font-size:31px;line-height:1.4;color:#8E8E93">Sync complete — 24 metrics sent, 0 ignored.</div></div>
          <div class="row"><span>Last successful sync</span><span class="value">Today, 15:24</span></div>
        </div>
      </section>

      <section class="section">
        <div class="section-title">Latest Values</div>
        <div class="card">
          <div class="row"><span>Steps</span><span style="font-size:42px">8,412</span></div>
          <div class="row"><span>Resting heart rate</span><span style="font-size:42px">58 bpm</span></div>
          <div class="row"><span>Sleep</span><span style="font-size:42px">7h 32m</span></div>
        </div>
      </section>
    </body></html>
    """


SCREENS = {
    "01-setup": screen_01_setup,
}


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("Chrome not found; set CHROME to a Chrome/Chromium binary.")


def make_og(chrome: str) -> None:
    out = ROOT / "docs" / "images" / "og.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
      html, body {{ width:1200px; height:630px; margin:0; overflow:hidden; background:#0B1220;
        font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color:#F8FAFC; }}
      .grid {{ position:absolute; inset:0; opacity:.85;
        background-image:linear-gradient(#16233A 1px,transparent 1px),linear-gradient(90deg,#16233A 1px,transparent 1px);
        background-size:90px 90px; }}
      .glow {{ position:absolute; right:-140px; top:-180px; width:720px; height:720px; border-radius:50%;
        background:radial-gradient(circle,rgba(15,118,110,.45),transparent 70%); }}
      .content {{ position:absolute; left:64px; top:56px; width:650px; }}
      .brand {{ display:flex; align-items:center; gap:18px; }}
      .icon {{ width:72px; height:72px; border-radius:18px; box-shadow:0 10px 24px rgba(0,0,0,.5); }}
      .name {{ font-size:30px; font-weight:700; }}
      .eyebrow {{ margin-top:46px; color:#2DD4BF; font-size:16px; font-weight:600; letter-spacing:1.5px; }}
      h1 {{ margin:14px 0 0; font-size:60px; line-height:1.03; letter-spacing:-2px; }}
      p {{ margin:18px 0 0; font-size:22px; line-height:1.4; color:#94A3B8; }}
      .badges {{ display:flex; gap:12px; margin-top:28px; }}
      .badge {{ padding:10px 18px; border-radius:999px; background:#134E4A; color:#5EEAD4; font-size:14px; font-weight:600; }}
      .phone {{ position:absolute; right:-30px; top:70px; width:350px; height:700px; border-radius:46px;
        border:11px solid #000; box-shadow:0 30px 80px rgba(0,0,0,.65); object-fit:cover; object-position:top;
        transform:rotate(-5deg); }}
    </style></head><body>
      <div class="grid"></div><div class="glow"></div>
      <div class="content">
        <div class="brand"><img class="icon" src="file://{ICON}"><div class="name">Health Sync</div></div>
        <div class="eyebrow">APPLE HEALTH → HOME ASSISTANT</div>
        <h1>Your health,<br>in your home.</h1>
        <p>A free, local-first bridge from Apple Health to your own Home Assistant. No vendor cloud, no account, no telemetry.</p>
        <div class="badges"><span class="badge">FREE + OPEN SOURCE</span><span class="badge">NO ACCOUNT</span><span class="badge">LOCAL-FIRST</span></div>
      </div>
      <img class="phone" src="file://{SCREENSHOTS / "02-sync.png"}">
    </body></html>"""
    with tempfile.TemporaryDirectory(prefix="health-assist-og-") as tmp:
        path = Path(tmp) / "og.html"
        path.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--hide-scrollbars",
                "--allow-file-access-from-files",
                "--force-device-scale-factor=1",
                "--window-size=1200,630",
                "--virtual-time-budget=10000",
                f"--screenshot={out}",
                path.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    print(f"wrote {out}")


def main() -> None:
    chrome = find_chrome()
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="health-assist-screens-") as tmp:
        tmpdir = Path(tmp)
        for name, factory in SCREENS.items():
            html = tmpdir / f"{name}.html"
            html.write_text(factory(), encoding="utf-8")
            out = SCREENSHOTS / f"{name}.png"
            subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    "--allow-file-access-from-files",
                    "--force-device-scale-factor=1",
                    "--window-size=1206,2622",
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
