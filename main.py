#!/usr/bin/env python3
"""VESPERA — a travel poster for a place that does not exist.

Draws a 1024x1024 travel poster with PIL only (stdlib + Pillow, no network,
no randomness except a fixed seed) and writes it to /output/entry.png.

The place: VESPERA, a cliff town on a sea where the sun sets twice.
One landmark (the lighthouse), one promise (two suns over a calm sea),
one name set large into the picture. No other copy.
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HORIZON = 620
OUT = "/output/entry.png"

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "DejaVuSerif-Bold.ttf")


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, width, y0, y1, stops):
    """Vertical gradient between (offset, color) stops, offsets in 0..1."""
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        for i in range(len(stops) - 1):
            o0, c0 = stops[i]
            o1, c1 = stops[i + 1]
            if o0 <= t <= o1:
                f = 0 if o1 == o0 else (t - o0) / (o1 - o0)
                draw.line([(0, y), (width, y)], fill=lerp(c0, c1, f))
                break


def glow(overlay, cx, cy, r, color, steps=24):
    """Soft radial glow: concentric circles fading out."""
    d = ImageDraw.Draw(overlay)
    for i in range(steps, 0, -1):
        rr = r * i / steps
        alpha = int(70 * (1 - i / steps) ** 2) + 8
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (alpha,))


def main():
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # --- sky: indigo dusk melting into amber at the horizon ---
    vgrad(draw, W, 0, HORIZON, [
        (0.00, (20, 26, 51)),
        (0.35, (61, 52, 104)),
        (0.58, (122, 74, 126)),
        (0.78, (201, 111, 74)),
        (1.00, (242, 166, 94)),
    ])

    # --- sea: teal darkening with depth ---
    vgrad(draw, W, HORIZON, H, [
        (0.00, (42, 74, 99)),
        (0.45, (24, 48, 74)),
        (1.00, (10, 26, 44)),
    ])

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # --- two suns: the big one low over the water, its twin higher right ---
    glow(overlay, 430, 560, 190, (255, 207, 125))
    glow(overlay, 700, 470, 120, (255, 220, 150))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    draw.ellipse([430 - 64, 560 - 64, 430 + 64, 560 + 64], fill=(255, 233, 176, 255))
    draw.ellipse([700 - 38, 470 - 38, 700 + 38, 470 + 38], fill=(255, 243, 208, 255))
    # small bright cores
    draw.ellipse([430 - 40, 560 - 40, 430 + 40, 560 + 40], fill=(255, 246, 214, 255))
    draw.ellipse([700 - 22, 470 - 22, 700 + 22, 470 + 22], fill=(255, 250, 226, 255))

    # --- sun roads: shimmering reflections under each sun (fixed seed) ---
    rng = random.Random(7)
    for cx, half in ((430, 95), (700, 60)):
        for row in range(16):
            y = HORIZON + 12 + row * 22
            wdt = int(half * (1 - row / 22) * rng.uniform(0.55, 1.0))
            x0 = cx - wdt + rng.randint(-14, 14)
            x1 = cx + wdt + rng.randint(-14, 14)
            alpha = int(150 * (1 - row / 18))
            draw.line([(x0, y), (x1, y)], fill=(247, 200, 115, alpha), width=3)

    # --- cliff silhouette, left foreground, with the lighthouse ---
    cliff = [(0, H), (0, 700), (120, 640), (210, 590), (285, 560),
             (330, 620), (360, 700), (360, H)]
    draw.polygon(cliff, fill=(14, 20, 36, 255))
    # lighthouse on the cliff top
    tx, ty = 268, 470  # tower top centre
    draw.polygon([(tx - 26, 585), (tx - 17, ty + 18), (tx + 17, ty + 18),
                  (tx + 26, 585)], fill=(243, 230, 200, 255))
    draw.polygon([(tx - 21, 545), (tx + 21, 545), (tx + 19, 520),
                  (tx - 19, 520)], fill=(42, 47, 69, 255))
    draw.polygon([(tx - 24, 500), (tx + 24, 500), (tx + 22, 478),
                  (tx - 22, 478)], fill=(42, 47, 69, 255))
    # lamp room + dome
    draw.rectangle([tx - 16, ty, tx + 16, ty + 20], fill=(30, 32, 48, 255))
    draw.rectangle([tx - 12, ty + 4, tx + 12, ty + 16], fill=(255, 233, 176, 255))
    draw.polygon([(tx - 18, ty), (tx + 18, ty), (tx, ty - 16)],
                 fill=(179, 58, 46, 255))
    # light beam sweeping right over the sea
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(tx + 10, ty + 10), (tx + 14, ty + 18), (640, 640), (620, 600)],
               fill=(255, 233, 176, 55))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img)

    # --- rocky outcrop, bottom right ---
    draw.polygon([(1024, H), (1024, 880), (940, 830), (860, 900),
                  (800, 980), (820, H)], fill=(12, 18, 32, 255))
    draw.polygon([(1024, 940), (980, 900), (940, 940), (960, H), (1024, H)],
                 fill=(20, 28, 46, 255))

    # --- birds ---
    for bx, by, s in ((620, 250, 16), (670, 285, 12), (560, 300, 10),
                      (760, 210, 13), (820, 260, 9)):
        draw.line([(bx - s, by), (bx, by - s // 2), (bx + s, by)],
                  fill=(26, 20, 48, 255), width=3)

    # --- stars in the upper sky, above the name (fixed seed) ---
    srng = random.Random(21)
    for _ in range(60):
        sx = srng.randint(20, W - 20)
        sy = srng.randint(24, 80)
        sr = srng.choice([1, 1, 2])
        sa = srng.randint(90, 220)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(255, 243, 214, sa))

    # --- the name, set large into the picture, nothing else ---
    font = ImageFont.truetype(FONT_PATH, 118)
    name = "VESPERA"
    tracking = 26
    widths = [draw.textlength(ch, font=font) for ch in name]
    total = sum(widths) + tracking * (len(name) - 1)
    x = (W - total) // 2
    y = 96
    for ch, wch in zip(name, widths):
        draw.text((x + 4, y + 6), ch, font=font, fill=(26, 20, 48, 255))
        x += wch + tracking
    x = (W - total) // 2
    for ch, wch in zip(name, widths):
        draw.text((x, y), ch, font=font, fill=(255, 243, 214, 255))
        x += wch + tracking
    # thin double rule under the name, small diamond in the middle
    ry = y + 148
    draw.line([(W // 2 - 210, ry), (W // 2 - 24, ry)], fill=(255, 243, 214, 255), width=2)
    draw.line([(W // 2 + 24, ry), (W // 2 + 210, ry)], fill=(255, 243, 214, 255), width=2)
    cx = W // 2
    draw.polygon([(cx, ry - 7), (cx + 7, ry), (cx, ry + 7), (cx - 7, ry)],
                 fill=(255, 243, 214, 255))

    img = img.convert("RGB")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG")
    print(f"wrote {OUT} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
