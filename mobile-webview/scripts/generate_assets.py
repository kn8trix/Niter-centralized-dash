#!/usr/bin/env python3
"""Generate native assets for the Niter Campus Hub Android wrapper.

Produces:
  * ``ic_launcher.png`` / ``ic_launcher_round.png`` at every mipmap density
    (mdpi 48 · hdpi 72 · xhdpi 96 · xxhdpi 144 · xxxhdpi 192) — a modern
    campus-student-hub monogram: charcoal ``#2B2927`` rounded square (circle
    for the round variant) with a bold beige ``#EADCC9`` "N", matching the
    adaptive vector foreground already used by the app.
  * ``res/raw/emergency_siren.wav`` — a 6-second two-tone emergency siren
    (600 Hz / 900 Hz) that the app plays for EMERGENCY_ALERT pushes.

Requires Pillow (``pip install Pillow``). Run from the repo root:

    python3 mobile-webview/scripts/generate_assets.py
"""

import math
import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw

APP_RES = Path('mobile-webview/app/src/main/res')

# Brand palette (matches theme.css / the adaptive icon).
INK = (43, 41, 39)      # #2B2927 — charcoal background
BEIGE = (234, 220, 201)  # #EADCC9 — monogram strokes

# Mipmap density -> launcher icon size in px.
DENSITIES = {
    'mdpi': 48,
    'hdpi': 72,
    'xhdpi': 96,
    'xxhdpi': 144,
    'xxxhdpi': 192,
}

# Master canvas: 10x the 108dp adaptive viewport so downscaling anti-aliases.
MASTER = 1080
# "N" monogram geometry from drawable/ic_launcher_foreground.xml (108 viewport),
# scaled by 10. Stroke width 9dp -> 90px at master resolution.
N_POINTS = [(38, 70), (38, 38), (70, 70), (70, 38)]
N_STROKE = 90


def _master_base(round_icon: bool) -> Image.Image:
    """Charcoal background shape (rounded square or circle) at master res."""
    img = Image.new('RGBA', (MASTER, MASTER), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if round_icon:
        draw.ellipse([0, 0, MASTER, MASTER], fill=INK)
    else:
        radius = int(MASTER * 0.22)  # ~22% corner radius, standard launcher look
        draw.rounded_rectangle([0, 0, MASTER, MASTER], radius=radius, fill=INK)
    return img


def _draw_n(img: Image.Image) -> Image.Image:
    """Beige 'N' monogram with round caps, centred on the master canvas."""
    draw = ImageDraw.Draw(img)
    # Scale the 108-viewport coordinates onto the master canvas.
    pts = [(int(x * MASTER / 108), int(y * MASTER / 108)) for x, y in N_POINTS]
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = pts
    segments = [(x1, y1, x2, y2), (x2, y2, x3, y3), (x3, y3, x4, y4)]
    for sx, sy, ex, ey in segments:
        draw.line([sx, sy, ex, ey], fill=BEIGE, width=N_STROKE, joint='curve')
    # Round the stroke caps/joins with endpoint discs.
    radius = N_STROKE // 2
    for cx, cy in pts:
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius], fill=BEIGE,
        )
    return img


def generate_icons() -> None:
    """Render every mipmap density for both launcher icon variants."""
    for round_icon, name in ((False, 'ic_launcher'), (True, 'ic_launcher_round')):
        master = _draw_n(_master_base(round_icon))
        for density, size in DENSITIES.items():
            out_dir = APP_RES / f'mipmap-{density}'
            out_dir.mkdir(parents=True, exist_ok=True)
            # Keep RGBA — launcher icons must ship transparent corners so the
            # launcher's own mask shows the rounded shape on any wallpaper.
            icon = master.resize((size, size), Image.LANCZOS)
            out_path = out_dir / f'{name}.png'
            icon.save(out_path, 'PNG', optimize=True)
            print(f'Wrote {out_path.relative_to(".")} ({size}x{size})')


def generate_banner() -> None:
    """Wide emergency-notification banner (BigPicture fallback image).

    A full-bleed charcoal band with the beige 'N' monogram — used by the
    native emergency notification when the push carries no picture URL.
    """
    banner_w, banner_h = 1200, 480
    banner = Image.new('RGBA', (banner_w, banner_h), INK + (255,))
    logo = _draw_n(_master_base(round_icon=False)).resize((300, 300), Image.LANCZOS)
    banner.alpha_composite(logo, (int((banner_w - 300) / 2), int((banner_h - 300) / 2)))
    out_dir = APP_RES / 'drawable'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'emergency_banner.png'
    banner.save(out_path, 'PNG', optimize=True)
    print(f'Wrote {out_path.relative_to(".")} ({banner_w}x{banner_h})')


def generate_siren() -> None:
    """Write a 6-second two-tone (600/900 Hz) emergency siren WAV."""
    raw_dir = APP_RES / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    sample_rate = 22050
    tone_seconds = 0.75
    cycles = 4  # 4 x (600 Hz + 900 Hz) = 6 s
    total_samples = int(sample_rate * tone_seconds * 2 * cycles)

    samples = []
    for cycle in range(cycles):
        for freq in (600, 900):
            n = int(sample_rate * tone_seconds)
            for i in range(n):
                t = i / sample_rate
                # Short fade in/out per tone removes audible clicks.
                fade = min(1.0, i / (sample_rate * 0.03), (n - i) / (sample_rate * 0.03))
                value = 0.5 * math.sin(2 * math.pi * freq * t) * max(fade, 0.0)
                samples.append(int(value * 32767))

    with wave.open(str(raw_dir / 'emergency_siren.wav'), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b''.join(struct.pack('<h', s) for s in samples))
    print('Wrote mobile-webview/app/src/main/res/raw/emergency_siren.wav')


if __name__ == '__main__':
    generate_icons()
    generate_banner()
    generate_siren()
