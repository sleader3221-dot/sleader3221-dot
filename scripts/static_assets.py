#!/usr/bin/env python3
"""Generates the profile README header banner.

    python scripts/static_assets.py      ->  assets/header.svg
"""
from __future__ import annotations

import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "header.svg"

W, H = 1200, 240
BG = "#0d1117"
LINE = "#263247"
ACCENT = "#58a6ff"
TEXT = "#f0f6fc"
MUTED = "#8b949e"
SANS = "'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"


def traces(seed: int, side: str) -> str:
    """Subtle right-angled circuit traces along one edge of the banner."""
    rnd = random.Random(seed)
    out = []
    for i in range(7):
        y = 28 + i * 31 + rnd.randint(-4, 4)
        length = rnd.randint(90, 150)
        bend = rnd.choice([-18, 0, 18])
        if side == "left":
            xm = rnd.randint(30, length - 30)
            d = f"M0 {y} H{xm} L{xm + abs(bend)} {y + bend} H{length}"
            end = (length, y + bend)
        else:
            xm = W - rnd.randint(30, length - 30)
            d = f"M{W} {y} H{xm} L{xm - abs(bend)} {y + bend} H{W - length}"
            end = (W - length, y + bend)
        out.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="2"/>')
        out.append(f'<circle cx="{end[0]}" cy="{end[1]}" r="3.5" fill="{BG}" stroke="{LINE}" stroke-width="2"/>')
    return "\n  ".join(out)


def main() -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"
     aria-label="Karthik M Achalakar - Embedded Systems and IoT, Full-Stack Development, AI">
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  {traces(7, "left")}
  {traces(11, "right")}
  <g text-anchor="middle" font-family="{SANS}">
    <text x="600" y="108" font-size="50" font-weight="700" fill="{TEXT}" letter-spacing="1">Karthik M Achalakar</text>
    <text x="600" y="150" font-size="20" font-weight="500" fill="{ACCENT}">Embedded Systems and IoT  |  Full-Stack Development  |  AI</text>
    <text x="600" y="186" font-size="16" fill="{MUTED}">Electrical and Electronics Engineering, Ramaiah Institute of Technology, Bengaluru</text>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#30363d"/>
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
