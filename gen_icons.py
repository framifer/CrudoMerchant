#!/usr/bin/env python3
"""Genera le icone PWA per Crudo Merchant: ancora dorata su sfondo a tema."""
from PIL import Image, ImageDraw
import math

BG = (21, 21, 31)        # #15151f  sfondo app
BG2 = (30, 30, 46)       # #1e1e2e  theme color
GOLD = (214, 178, 92)    # ancora
GOLD_DK = (168, 138, 66)


def draw_anchor(d, cx, cy, s, color, dk):
    """Disegna un'ancora stilizzata centrata in (cx,cy) con 'scala' s (raggio)."""
    lw = max(2, int(s * 0.12))
    # anello superiore
    r = s * 0.20
    top = cy - s
    d.ellipse([cx - r, top, cx + r, top + 2 * r], outline=color, width=lw)
    # asta verticale
    shaft_top = top + 2 * r
    shaft_bot = cy + s * 0.78
    d.line([(cx, shaft_top), (cx, shaft_bot)], fill=color, width=lw)
    # traversa orizzontale (stock)
    arm = s * 0.55
    ay = cy - s * 0.30
    d.line([(cx - arm, ay), (cx + arm, ay)], fill=color, width=lw)
    # bracci curvi inferiori (le marre)
    left = s * 0.85
    d.arc([cx - left, cy - s * 0.15, cx + left, shaft_bot + s * 0.15],
          start=20, end=160, fill=color, width=lw)
    # punte delle marre
    for sign in (-1, 1):
        px = cx + sign * left * 0.92
        py = cy + s * 0.52
        d.polygon([
            (px, py - s * 0.12),
            (px + sign * s * 0.22, py),
            (px, py + s * 0.14),
        ], fill=color)


def make_icon(size, maskable=False, path="icon.png"):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # sfondo: cerchio pieno a tema (maskable = riempi tutto per la safe zone)
    if maskable:
        d.rectangle([0, 0, size, size], fill=BG)
        scale = size * 0.24   # ancora piu' piccola: safe zone maskable
    else:
        margin = int(size * 0.06)
        d.rounded_rectangle([margin, margin, size - margin, size - margin],
                            radius=int(size * 0.18), fill=BG)
        # bordo sottile
        d.rounded_rectangle([margin, margin, size - margin, size - margin],
                            radius=int(size * 0.18), outline=BG2,
                            width=max(2, int(size * 0.02)))
        scale = size * 0.30
    draw_anchor(d, size / 2, size / 2, scale, GOLD, GOLD_DK)
    img.save(path)
    print("wrote", path)


base = "/home/frferrar/shared/crudo-merchant-pwa/icons"
make_icon(192, False, f"{base}/icon-192.png")
make_icon(512, False, f"{base}/icon-512.png")
make_icon(192, True, f"{base}/icon-192-maskable.png")
make_icon(512, True, f"{base}/icon-512-maskable.png")
print("done")
