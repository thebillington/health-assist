#!/usr/bin/env python3
"""Generate the Health Assist app icon and docs icons without third-party deps.

The mark is a white heart containing a house and a health plus: Apple Health
meets Home Assistant. It is drawn mathematically so the repository needs no
image toolchain to reproduce the PNGs.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = ROOT / "ios" / "AppleHealthSync" / "Assets.xcassets" / "AppIcon.appiconset"
DOCS = ROOT / "docs" / "images"

OUTPUTS = (
    (1024, ASSETS / "AppIcon-1024.png"),
    (512, DOCS / "icon-512.png"),
    (192, DOCS / "icon-192.png"),
)

# House polygon in normalized coordinates, matching docs/images/logo-mark.svg.
HOUSE = (
    (0.5000, 0.3828),
    (0.6484, 0.5020),
    (0.6055, 0.5020),
    (0.6055, 0.6484),
    (0.3945, 0.6484),
    (0.3945, 0.5020),
    (0.3516, 0.5020),
)

# The health plus, as two normalized rectangles.
PLUS_H = (0.4531, 0.5742, 0.5469, 0.6055)
PLUS_V = (0.4844, 0.5430, 0.5156, 0.6367)

HEART_SCALE = 0.262
HEART_CENTER = 0.516


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def inside_heart(x: float, y: float) -> bool:
    """Return whether a normalized point is inside the heart."""
    return (x * x + y * y - 1) ** 3 - x * x * y**3 <= 0


def inside_rect(x: float, y: float, rect: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = rect
    return x0 <= x <= x1 and y0 <= y <= y1


def inside_polygon(x: float, y: float, points: tuple[tuple[float, float], ...]) -> bool:
    inside = False
    j = len(points) - 1
    for i, (xi, yi) in enumerate(points):
        xj, yj = points[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def pixel(x: int, y: int, size: int, samples: int = 2) -> tuple[int, int, int]:
    accum = [0.0, 0.0, 0.0]
    total = samples * samples

    for dx in range(samples):
        for dy in range(samples):
            px = x + (dx + 0.5) / samples
            py = y + (dy + 0.5) / samples
            nx = px / size
            ny = py / size

            # Diagonal teal gradient.
            t = (nx + ny) / 2
            red = lerp(20, 15, t)
            green = lerp(184, 118, t)
            blue = lerp(166, 110, t)

            # Soft highlight in the top-left.
            hx, hy = nx - 0.23, ny - 0.19
            highlight = max(0.0, 1.0 - (hx * hx + hy * hy) ** 0.5 / 0.41)
            if highlight > 0:
                amount = 0.07 * highlight
                red = lerp(red, 255, amount)
                green = lerp(green, 255, amount)
                blue = lerp(blue, 255, amount)

            # Subtle depth in the bottom-right.
            dx2, dy2 = nx - 0.84, ny - 0.88
            shade = max(0.0, 1.0 - (dx2 * dx2 + dy2 * dy2) ** 0.5 / 0.35)
            if shade > 0:
                amount = 0.10 * shade
                red = lerp(red, 4, amount)
                green = lerp(green, 47, amount)
                blue = lerp(blue, 46, amount)

            # Heart.
            heart_x = (nx - 0.5) / HEART_SCALE
            heart_y = -(ny - HEART_CENTER) / HEART_SCALE
            if inside_heart(heart_x, heart_y):
                # Near-white vertical gradient.
                red, green, blue = 255, lerp(255, 240, ny), lerp(255, 250, ny)

                if inside_polygon(nx, ny, HOUSE):
                    red, green, blue = 15, 118, 110
                    if inside_rect(nx, ny, PLUS_H) or inside_rect(nx, ny, PLUS_V):
                        red, green, blue = 255, 255, 255

            accum[0] += red
            accum[1] += green
            accum[2] += blue

    return (
        int(accum[0] / total),
        int(accum[1] / total),
        int(accum[2] / total),
    )


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def render(size: int) -> bytes:
    samples = 2 if size >= 512 else 4
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0
        for x in range(size):
            raw.extend(pixel(x, y, size, samples))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main() -> None:
    for size, out in OUTPUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        png = render(size)
        out.write_bytes(png)
        print(f"wrote {out} ({len(png):,} bytes)")


if __name__ == "__main__":
    main()
