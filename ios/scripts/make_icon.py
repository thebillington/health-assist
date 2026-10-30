#!/usr/bin/env python3
"""Generate the 1024x1024 app icon without third-party dependencies."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIZE = 1024
SCALE = 2  # supersample for simple anti-aliasing
OUT = (
    Path(__file__).resolve().parent.parent
    / "AppleHealthSync"
    / "Assets.xcassets"
    / "AppIcon.appiconset"
    / "AppIcon-1024.png"
)


def inside_heart(x: float, y: float) -> bool:
    """Return whether a normalized point is inside a heart."""
    return (x * x + y * y - 1) ** 3 - x * x * y**3 <= 0


def pixel(x: int, y: int) -> tuple[int, int, int, int]:
    samples = []
    for dx in range(SCALE):
        for dy in range(SCALE):
            px = x + (dx + 0.5) / SCALE
            py = y + (dy + 0.5) / SCALE

            # Diagonal teal gradient.
            t = (px + py) / (2 * SIZE)
            red = int(14 + (21 - 14) * t)
            green = int(116 + (94 - 116) * t)
            blue = int(144 + (117 - 144) * t)

            # Heart in the centre, drawn in image coordinates.
            hx = (px - SIZE / 2) / (SIZE * 0.30)
            hy = -(py - SIZE * 0.47) / (SIZE * 0.30)
            if inside_heart(hx, hy):
                red, green, blue = 255, 255, 255

            samples.append((red, green, blue))

    count = len(samples)
    return (
        sum(s[0] for s in samples) // count,
        sum(s[1] for s in samples) // count,
        sum(s[2] for s in samples) // count,
        255,
    )


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def main() -> None:
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)  # filter type 0
        for x in range(SIZE):
            raw.extend(pixel(x, y))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(png)
    print(f"wrote {OUT} ({len(png):,} bytes)")


if __name__ == "__main__":
    main()
