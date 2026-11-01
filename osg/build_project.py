#!/usr/bin/env python3
"""Build the simple Health Assist App Store screenshot set.

Five boards: one real app screenshot, then four plain text panels explaining
the features. No marketing props, no phone frames, no App Store mockups.

    python3 osg/build_project.py
    osg render --formats ios-6-9
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
PROJECT = ROOT / "osg" / "project.json"

W, H = 1290, 2796
INK = "#0B1220"
MUTED = "#475569"
TEAL = "#0F766E"
PAPER = "#FFFFFF"
SOFT = "#F8FAFC"
LINE = "#E2E8F0"


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
        "textAlign": "left",
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


def image(name: str, path: Path, x: int, y: int, w: int, h: int) -> dict:
    data = base64.b64encode(path.read_bytes()).decode()
    return {
        "id": name,
        "type": "image",
        "name": name,
        "position": {"x": x, "y": y},
        "size": {"width": w, "height": h},
        "rotation": 0,
        "scale": 1,
        "imageSrc": "data:image/png;base64," + data,
        "objectFit": "fill",
    }


def screenshot_board() -> dict:
    shot = SHOTS / "01-setup.png"
    return {
        "id": "ab_01",
        "name": "01 App screenshot",
        "position": {"x": 15, "y": 15},
        "size": {"width": W, "height": H},
        "backgroundColor": PAPER,
        "zoom": 1,
        "backgroundType": "solid",
        "backgroundGradient": {"color1": PAPER, "color2": PAPER, "angle": 180},
        "elements": [
            shape("shot-border", 37, 82, 1216, 2634, PAPER, 24, LINE, 2),
            image("shot", shot, 41, 86, 1208, 2626),
        ],
    }


def feature_board(index: int, name: str, number: str, headline: str, body: str) -> dict:
    return {
        "id": f"ab_{index:02d}",
        "name": name,
        "position": {"x": 15 + (index - 1) * 402, "y": 15},
        "size": {"width": W, "height": H},
        "backgroundColor": SOFT,
        "zoom": 1,
        "backgroundType": "solid",
        "backgroundGradient": {"color1": SOFT, "color2": SOFT, "angle": 180},
        "elements": [
            text("number", 90, 170, 200, 60, number, 12, "600", TEAL),
            shape("rule", 90, 270, 120, 6, TEAL),
            text("headline", 90, 330, 1110, 430, headline, 46, "700", INK, 1.04),
            text("body", 90, 850, 1030, 470, body, 18, "400", MUTED, 1.45),
            text(
                "footer",
                90,
                2650,
                1110,
                40,
                "HEALTH ASSIST · APPLE HEALTH → HOME ASSISTANT",
                9,
                "500",
                "#94A3B8",
            ),
        ],
    }


FEATURES = (
    (
        "02 Full history",
        "02",
        "Full history,\nnot just today.",
        "The first sync exports all available HealthKit history in resumable chunks. "
        "Later syncs only send what is new, and you can re-export everything from the app.",
    ),
    (
        "03 Native sensors",
        "03",
        "Native sensors,\nreal statistics.",
        "Steps, sleep, heart rate, weight, blood oxygen and more become Home Assistant "
        "sensors with stable IDs, correct units and long-term statistics.",
    ),
    (
        "04 Local-first",
        "04",
        "Local-first,\nby design.",
        "Data goes from your iPhone to your own Home Assistant. No account, no analytics, "
        "no telemetry and no vendor cloud. The webhook and secret stay in the iOS Keychain.",
    ),
    (
        "05 Free and open source",
        "05",
        "Free and\nopen source.",
        "The app and the integration are MIT licensed. There is no paid tier and no in-app "
        "purchase. Sponsor My Work is optional and unlocks nothing.",
    ),
)


def main() -> None:
    project = {
        "id": "project_health_assist_simple",
        "name": "Health Assist",
        "description": "Simple App Store screenshots: one app screen and four feature text panels.",
        "category": "screenshots",
        "timestamp": "2026-11-01T00:00:00.000Z",
        "projectData": [screenshot_board()]
        + [
            feature_board(i, name, number, headline, body)
            for i, (name, number, headline, body) in enumerate(FEATURES, start=2)
        ],
        "osg": {
            "command": "build_project",
            "createdAt": "2026-11-01T00:00:00.000Z",
            "template": None,
            "device": None,
            "format": "ios-6-9",
            "screenshots": [{"file": "screenshots/01-setup.png", "width": 1206, "height": 2622}],
        },
    }
    PROJECT.write_text(json.dumps(project, indent=2), encoding="utf-8")
    print(
        f"wrote {PROJECT} ({PROJECT.stat().st_size:,} bytes, {len(project['projectData'])} boards)"
    )


if __name__ == "__main__":
    main()
