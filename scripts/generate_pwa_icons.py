#!/usr/bin/env python3
"""Generate the PWA app icons without any image library.

Draws a rounded-square badge in the brand palette (main #2B2927 background,
white "N" glyph) and writes RGBA PNGs (192, 512, and 180 for Apple touch).
Pure stdlib (struct + zlib) so it runs anywhere.

Usage:  python scripts/generate_pwa_icons.py
Output: static/pwa/icon-192.png, icon-512.png, icon-180.png
"""

import struct
import zlib
from pathlib import Path

# Brand palette (theme.css tokens)
BG = (43, 41, 39)        # --color-main #2B2927
GLYPH = (255, 255, 255)  # white "N"
RADIUS_RATIO = 0.22      # corner radius as a fraction of the icon size

OUT_DIR = Path(__file__).resolve().parent.parent / 'static' / 'pwa'
SIZES = (192, 512, 180)


def _inside_round_rect(x, y, size, r):
    """True when (x, y) is inside a centered rounded square of side `size`."""
    cx = min(max(x, r), size - r)
    cy = min(max(y, r), size - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def _on_n_glyph(x, y, size):
    """White 'N': two vertical bars joined by a diagonal (thickness-based)."""
    t = size * 0.045
    top, bottom = size * 0.16, size * 0.84
    bar_l = size * 0.24 <= x <= size * 0.33
    bar_r = size * 0.67 <= x <= size * 0.76

    def dist_to_segment(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        t_f = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
        cx, cy = ax + t_f * dx, ay + t_f * dy
        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

    on_diag = dist_to_segment(
        x, y, size * 0.33, top, size * 0.67, bottom,
    ) <= t / 2
    return (bar_l or bar_r) and top <= y <= bottom or on_diag


def _render(size):
    r = int(size * RADIUS_RATIO)
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            if not _inside_round_rect(x + 0.5, y + 0.5, size, r):
                row += bytes((0, 0, 0, 0))
            elif _on_n_glyph(x + 0.5, y + 0.5, size):
                row += bytes((*GLYPH, 255))
            else:
                row += bytes((*BG, 255))
        rows.append(row)
    return rows


def _chunk(tag, data):
    out = struct.pack('>I', len(data)) + tag + data
    return out + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)


def _write_png(path, size, rows):
    raw = b''.join(b'\x00' + bytes(row) for row in rows)  # filter 0 per scanline
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    png += _chunk(b'IDAT', zlib.compress(raw, 9))
    png += _chunk(b'IEND', b'')
    path.write_bytes(png)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        path = OUT_DIR / ('icon-%d.png' % size)
        _write_png(path, size, _render(size))
        print('wrote %s (%d bytes)' % (path, path.stat().st_size))


if __name__ == '__main__':
    main()
