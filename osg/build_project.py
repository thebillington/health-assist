#!/usr/bin/env python3
# ruff: noqa: E501
"""Build the committed OSG promotion project for Health Assist.

Run from the repository root:

    python3 osg/build_project.py
    osg render --formats ios-6-9

The project uses a technical blueprint style: dark slate background, a thin
grid, teal accents, and a straight-on iPhone frame for each screen.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
PROJECT = ROOT / "osg" / "project.json"

W, H = 1290, 2796
BG = "#0B1220"
GRID = "#16233A"
INK = "#F8FAFC"
MUTED = "#94A3B8"
TEAL = "#2DD4BF"
TEAL_DARK = "#134E4A"
CARD = "#0E1A2F"
CARD_EDGE = "#1E3A5F"


def text(
    name: str,
    x: int,
    y: int,
    w: int,
    h: int,
    content: str,
    size: int,
    weight: str = "400",
    color: str = INK,
    align: str = "left",
    line_height: float = 1.1,
) -> dict:
    return {
        "id": name,
        "type": "text",
        "name": name,
        "position": {"x": x, "y": y},
        "size": {"width": w, "height": h},
        "rotation": 0,
        "scale": 1,
        "content": content,
        "fontSize": size,
        "color": color,
        "fontFamily": "Space Grotesk",
        "fontWeight": weight,
        "textAlign": align,
        "lineHeight": line_height,
    }


def shape(
    name: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fill: str,
    radius: int = 0,
    stroke: str = "transparent",
    stroke_width: int = 0,
) -> dict:
    return {
        "id": name,
        "type": "shape",
        "name": name,
        "position": {"x": x, "y": y},
        "size": {"width": w, "height": h},
        "rotation": 0,
        "scale": 1,
        "shapeType": "rectangle",
        "borderRadius": radius,
        "fillColor": fill,
        "strokeColor": stroke,
        "strokeWidth": stroke_width,
    }


def device(name: str, path: Path, x: int, y: int, w: int, h: int) -> dict:
    data = base64.b64encode(path.read_bytes()).decode()
    return {
        "id": name,
        "type": "device",
        "name": name,
        "position": {"x": x, "y": y},
        "size": {"width": w, "height": h},
        "rotation": 0,
        "scale": 1,
        "deviceType": "iphone-15",
        "styleType": "normal",
        "screenshotSrc": "data:image/png;base64," + data,
        "naturalScreenshotWidth": 1206,
        "naturalScreenshotHeight": 2622,
        "screenshotObjectFit": "cover",
        "screenshotRect": {"left": 0, "top": 0, "width": 100, "height": 100},
    }


def grid() -> list[dict]:
    elements = []
    for i, x in enumerate(range(0, W + 1, 215)):
        elements.append(shape(f"v{i}", x, 0, 2, H, GRID))
    for i, y in enumerate(range(0, H + 1, 280)):
        elements.append(shape(f"h{i}", 0, y, W, 2, GRID))
    return elements


def board(
    index: int, name: str, eyebrow: str, headline: str, subline: str, screenshot: Path
) -> dict:
    elements: list[dict] = []
    elements += grid()

    # Small teal corner ticks for the technical look.
    elements += [
        shape("tick-tl-h", 54, 112, 36, 3, TEAL),
        shape("tick-tl-v", 54, 112, 3, 36, TEAL),
        shape("tick-br-h", 1200, 2681, 36, 3, TEAL),
        shape("tick-br-v", 1233, 2651, 3, 33, TEAL),
    ]

    elements += [
        text("eyebrow", 90, 140, 890, 54, eyebrow.upper(), 14, "600", TEAL),
        text("headline", 90, 210, 1110, 300, headline, 42, "700", INK, line_height=1.04),
        text("subline", 90, 540, 940, 220, subline, 15, "400", MUTED, line_height=1.38),
        shape("rule", 90, 790, 120, 6, TEAL),
        shape("chip", 1010, 140, 190, 56, TEAL_DARK, 28),
        text("chip-text", 1010, 150, 190, 36, "FREE", 12, "700", TEAL, "center"),
        shape("phone-card", 215, 850, 860, 1800, CARD, 80, CARD_EDGE, 3),
        device("phone", screenshot, 245, 880, 800, 1740),
        text(
            "footer",
            90,
            2690,
            1110,
            40,
            "HEALTH ASSIST · APPLE HEALTH → HOME ASSISTANT · FREE + OPEN SOURCE",
            9,
            "500",
            "#64748B",
        ),
    ]

    return {
        "id": f"ab_{index:02d}",
        "name": name,
        "position": {"x": 15 + (index - 1) * 402, "y": 15},
        "size": {"width": W, "height": H},
        "backgroundColor": BG,
        "zoom": 1,
        "backgroundType": "gradient",
        "backgroundGradient": {"color1": "#0B1220", "color2": "#0F1B30", "angle": 160},
        "elements": elements,
    }


BOARDS = (
    (
        "01 Setup",
        "APPLE HEALTH → HOME ASSISTANT",
        "Your health,\nin your home.",
        "A free, local-first bridge from Apple Health to Home Assistant. No vendor cloud, no account, no telemetry.",
        SHOTS / "01-setup.png",
    ),
    (
        "02 History",
        "FULL HISTORY",
        "Every record,\nnot just today.",
        "The first sync exports all available HealthKit history, then keeps it current in the background.",
        SHOTS / "02-sync.png",
    ),
    (
        "03 Sensors",
        "NATIVE SENSORS",
        "Every metric,\nas a sensor.",
        "Steps, sleep, heart rate, weight and more become Home Assistant sensors with long-term statistics.",
        SHOTS / "03-values.png",
    ),
    (
        "04 Privacy",
        "LOCAL-FIRST",
        "Your data\nstays yours.",
        "No analytics. No telemetry. No vendor cloud. The webhook URL and secret live in the iOS Keychain.",
        SHOTS / "04-privacy.png",
    ),
    (
        "05 Sponsor",
        "FREE + OPEN SOURCE",
        "Free software,\nfunded by you.",
        "MIT licensed on both sides. Sponsor My Work is optional and unlocks nothing.",
        SHOTS / "08-sponsor.png",
    ),
    (
        "06 QR setup",
        "SET UP IN SECONDS",
        "Scan once.\nSync forever.",
        "The QR code carries the webhook URL and secret. Import it, grant Health access, and sensors appear.",
        SHOTS / "05-qr.png",
    ),
    (
        "07 App Store search",
        "APP STORE SEARCH",
        "Find it on\nthe App Store.",
        "Search “health assist”. Free, local-first, built for Home Assistant.",
        SHOTS / "06-search.png",
    ),
    (
        "08 App Store product",
        "APP STORE PRODUCT PAGE",
        "Built for\nyour home.",
        "Free on the App Store. No subscription, no account, no in-app purchases.",
        SHOTS / "07-product.png",
    ),
)


def main() -> None:
    project = {
        "id": "project_health_assist_promo",
        "name": "Health Assist",
        "description": "Technical promotion set for Health Assist: Apple Health to Home Assistant.",
        "category": "screenshots",
        "timestamp": "2026-11-01T00:00:00.000Z",
        "projectData": [
            board(i, name, eyebrow, headline, subline, shot)
            for i, (name, eyebrow, headline, subline, shot) in enumerate(BOARDS, start=1)
        ],
        "osg": {
            "command": "build_project",
            "createdAt": "2026-11-01T00:00:00.000Z",
            "template": None,
            "device": "iphone-15",
            "format": "ios-6-9",
            "screenshots": [
                {"file": f"screenshots/{shot.name}", "width": 1206, "height": 2622}
                for _, _, _, _, shot in BOARDS
            ],
        },
    }
    PROJECT.write_text(json.dumps(project, indent=2), encoding="utf-8")
    print(
        f"wrote {PROJECT} ({PROJECT.stat().st_size:,} bytes, {len(project['projectData'])} boards)"
    )


if __name__ == "__main__":
    main()
