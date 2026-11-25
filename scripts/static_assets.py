#!/usr/bin/env python3
"""Generates the hand-designed animated SVGs for the profile README.

    python scripts/static_assets.py

Outputs: assets/header.svg, assets/terminal.svg, assets/divider.svg,
         assets/footer.svg, assets/cards/*.svg
"""
from __future__ import annotations

import random
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

BG = "#070b14"
SURFACE = "#0d1424"
CYAN = "#22d3ee"
VIOLET = "#a78bfa"
PINK = "#f472b6"
GREEN = "#34d399"
AMBER = "#fbbf24"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace"


def write(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(svg).strip() + "\n", encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# Header: PCB traces with current pulses + gradient name
# ---------------------------------------------------------------------------
def pcb_traces(seed: int, w: int, h: int, side: str) -> tuple[str, str]:
    """Return (traces, vias) SVG fragments of right-angled PCB routes."""
    rnd = random.Random(seed)
    traces, vias = [], []
    for i in range(9):
        y = 30 + i * 32 + rnd.randint(-6, 6)
        if side == "left":
            x0, x1 = -10, rnd.randint(110, 175)
            bend = rnd.choice([-24, 24, 0])
            xm = rnd.randint(40, x1 - 40)
            d = f"M{x0} {y} H{xm} L{xm + abs(bend)} {y + bend} H{x1}"
            end = (x1, y + bend)
        else:
            x0, x1 = w + 10, w - rnd.randint(110, 175)
            bend = rnd.choice([-24, 24, 0])
            xm = rnd.randint(x1 + 40, w - 40)
            d = f"M{x0} {y} H{xm} L{xm - abs(bend)} {y + bend} H{x1}"
            end = (x1, y + bend)
        color = [CYAN, VIOLET, PINK][i % 3]
        dur = round(rnd.uniform(2.6, 4.8), 2)
        delay = round(rnd.uniform(0, 3), 2)
        traces.append(f'<path d="{d}" class="trace"/>')
        traces.append(f'<path d="{d}" class="pulse" stroke="{color}" '
                      f'style="animation-duration:{dur}s;animation-delay:-{delay}s"/>')
        vias.append(f'<circle cx="{end[0]}" cy="{end[1]}" r="4.5" class="via" stroke="{color}" '
                    f'style="animation-delay:-{delay}s"/>')
    return "\n    ".join(traces), "\n    ".join(vias)


def header() -> None:
    w, h = 1200, 320
    lt, lv = pcb_traces(7, w, h, "left")
    rt, rv = pcb_traces(11, w, h, "right")
    write(ASSETS / "header.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"
         aria-label="Karthik M Achalakar - Embedded Systems and IoT, Full-Stack Development, AI">
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="{BG}"/><stop offset=".55" stop-color="#0f0a24"/><stop offset="1" stop-color="#04141c"/>
      </linearGradient>
      <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
        <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0;-1 0" dur="8s" repeatCount="indefinite"/>
      </linearGradient>
      <linearGradient id="nameBase" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">
        <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
      </linearGradient>
      <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
        <path d="M24 0H0V24" fill="none" stroke="#ffffff" stroke-opacity=".035"/>
      </pattern>
      <radialGradient id="glow" cx=".5" cy=".5" r=".5">
        <stop offset="0" stop-color="{VIOLET}" stop-opacity=".28"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
      </radialGradient>
      <filter id="blur"><feGaussianBlur stdDeviation="2.2"/></filter>
    </defs>
    <style>
      .trace {{ fill:none; stroke:#1c2740; stroke-width:2.2; }}
      .pulse {{ fill:none; stroke-width:2.6; stroke-linecap:round; stroke-dasharray:46 520;
               animation: flow linear infinite; filter:url(#blur); }}
      .via {{ fill:{BG}; stroke-width:2; animation: pulse 2.4s ease-in-out infinite; }}
      .name {{ font: 800 58px {SANS}; letter-spacing:2px; }}
      .role {{ font: 600 18px {MONO}; letter-spacing:3px; fill:{TEXT}; }}
      .meta {{ font: 500 15px {SANS}; fill:{MUTED}; letter-spacing:.5px; }}
      .in1 {{ animation: rise 1s ease-out both; }}
      .in2 {{ animation: rise 1s .35s ease-out both; }}
      .in3 {{ animation: rise 1s .7s ease-out both; }}
      .orb {{ animation: breathe 6s ease-in-out infinite; transform-origin:600px 160px; }}
      @keyframes flow {{ from {{ stroke-dashoffset:566; }} to {{ stroke-dashoffset:0; }} }}
      @keyframes pulse {{ 0%,100% {{ stroke-opacity:.35; }} 50% {{ stroke-opacity:1; }} }}
      @keyframes rise {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:none; }} }}
      @keyframes breathe {{ 0%,100% {{ transform:scale(1); opacity:.8; }} 50% {{ transform:scale(1.12); opacity:1; }} }}
    </style>
    <rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
    <rect width="{w}" height="{h}" rx="18" fill="url(#grid)"/>
    <ellipse class="orb" cx="600" cy="160" rx="420" ry="150" fill="url(#glow)"/>
    {lt}
    {rt}
    {lv}
    {rv}
    <g text-anchor="middle">
      <text class="name in1" x="600" y="150" fill="url(#nameBase)">KARTHIK M ACHALAKAR</text>
      <text class="name in1" x="600" y="150" fill="url(#name)" opacity=".85">KARTHIK M ACHALAKAR</text>
      <text class="role in2" x="600" y="200">EMBEDDED SYSTEMS &amp; IoT  ·  FULL-STACK  ·  AI</text>
      <text class="meta in3" x="600" y="242">EEE @ Ramaiah Institute of Technology  ·  Full Stack Engineer Intern @ DukaanSe  ·  Bengaluru</text>
    </g>
    <rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="17" fill="none" stroke="url(#nameBase)" stroke-opacity=".45" stroke-width="1.5"/>
    </svg>
    """)


# ---------------------------------------------------------------------------
# Terminal "about me" with typing effect
# ---------------------------------------------------------------------------
def terminal() -> None:
    prompt = "karthik@ramaiah:~$ "
    lines = [
        ("cmd", "whoami"),
        ("out", "Karthik M Achalakar  -  B.E. Electrical & Electronics, Ramaiah Institute of Technology (2024-28)"),
        ("cmd", "cat focus.txt"),
        ("out", "Building across the hardware-software boundary: ESP32 firmware, 12 V power design, production web apps"),
        ("cmd", "./now --role"),
        ("out", "Full Stack Engineer Intern @ DukaanSe  ->  Next.js, MERN, APIs, databases"),
        ("cmd", "ls ./achievements"),
        ("out", "3rd SANS 'Find Evil'  ·  2nd HackMars 3.0 NEON  ·  Rank 22 NIT Jamshedpur FPGA  ·  52 hackathons"),
    ]
    w = 1200
    line_h = 30
    top = 70
    h = top + line_h * (len(lines) + 1) + 20
    rows = []
    t = 0.4
    char_w = 9.0  # monospace 15px approx
    for i, (kind, text) in enumerate(lines):
        y = top + i * line_h
        if kind == "cmd":
            n = len(text)
            dur = max(0.5, n * 0.07)
            x_text = 32 + len(prompt) * char_w
            rows.append(
                f'<g class="ln" style="animation-delay:{t:.2f}s">'
                f'<text x="32" y="{y}" class="p">{escape(prompt)}</text>'
                f'<text x="{x_text:.0f}" y="{y}" class="c">{escape(text)}</text>'
                f'<rect x="{x_text - 2:.0f}" y="{y - 18}" width="{n * char_w + 14:.0f}" height="26" fill="{SURFACE}" '
                f'class="type" style="animation-delay:{t:.2f}s;animation-duration:{dur:.2f}s;'
                f'animation-timing-function:steps({n})"/>'
                f'</g>')
            t += dur + 0.25
        else:
            rows.append(f'<text x="32" y="{y}" class="o ln" style="animation-delay:{t:.2f}s">'
                        f'<tspan fill="{GREEN}">&#8627; </tspan>{escape(text)}</text>')
            t += 0.55
    y_last = top + len(lines) * line_h
    x_cur = 32 + len(prompt) * char_w
    rows.append(f'<g class="ln" style="animation-delay:{t:.2f}s"><text x="32" y="{y_last}" class="p">{escape(prompt)}</text>'
                f'<rect x="{x_cur:.0f}" y="{y_last - 16}" width="10" height="20" fill="{CYAN}" class="cursor"/></g>')
    body = "\n      ".join(rows)
    write(ASSETS / "terminal.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="About Karthik">
    <style>
      .p {{ font: 600 15px {MONO}; fill:{CYAN}; }}
      .c {{ font: 600 15px {MONO}; fill:{TEXT}; }}
      .o {{ font: 400 15px {MONO}; fill:{MUTED}; }}
      .ln {{ opacity:0; animation: show .01s forwards; }}
      .type {{ transform-box: fill-box; transform-origin: right center; animation-name: type; animation-fill-mode: both; }}
      .cursor {{ animation: blink 1s steps(1) infinite; }}
      @keyframes show {{ to {{ opacity:1; }} }}
      @keyframes type {{ from {{ transform: scaleX(1); }} to {{ transform: scaleX(0); }} }}
      @keyframes blink {{ 50% {{ opacity:0; }} }}
    </style>
    <defs>
      <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
    </defs>
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{SURFACE}" stroke="url(#edge)" stroke-opacity=".5"/>
    <rect x="1" y="1" width="{w - 2}" height="38" rx="14" fill="#111a2e"/>
    <rect x="1" y="26" width="{w - 2}" height="13" fill="#111a2e"/>
    <circle cx="26" cy="20" r="6.5" fill="#ff5f57"/><circle cx="48" cy="20" r="6.5" fill="#febc2e"/><circle cx="70" cy="20" r="6.5" fill="#28c840"/>
    <text x="{w // 2}" y="25" text-anchor="middle" style="font:500 13px {MONO}; fill:{MUTED}">karthik@ramaiah: ~/profile  -  zsh</text>
    <g>
      {body}
    </g>
    </svg>
    """)


# ---------------------------------------------------------------------------
# Project cards
# ---------------------------------------------------------------------------
PROJECTS = [
    dict(slug="proofsift", title="ProofSIFT", subtitle="Autonomous DFIR Triage Agent",
         badge="3RD PLACE  ·  SANS “FIND EVIL”", badge_color=AMBER, accent=CYAN, icon="shield",
         desc="Triage engine linking every finding to forensic artifacts, timestamps and SHA-256 hashes; "
              "correlates memory, disk, EVTX, PowerShell, YARA and network evidence into an SQLite evidence graph.",
         tech=["Python", "TypeScript", "SQLite", "MITRE ATT&CK"]),
    dict(slug="velosense", title="VeloSense", subtitle="Retrofit Blind-Spot Warning System",
         badge="FINALIST ENTRY  ·  SEVA FIRST 2026", badge_color=GREEN, accent=VIOLET, icon="chip",
         desc="ESP32 prototype grading adjacent-lane distance every 100 ms into SAFE / WARNING / DANGER zones, "
              "with haptics and a Bluetooth app. Gen 1 two-layer PCB with dual 24 GHz radar and IMU.",
         tech=["ESP32", "Embedded C/C++", "UART · I2C", "PCB Design"]),
    dict(slug="finwise", title="FinWise", subtitle="Gamified Financial Literacy Platform",
         badge="2ND OVERALL  ·  HACKMARS 3.0 NEON", badge_color=PINK, accent=PINK, icon="chart",
         desc="A platform that teaches teens budgeting, saving and investing through quizzes and "
              "progress tracking, designed around playful fintech UX.",
         tech=["React", "Product Design", "Fintech UX"]),
    dict(slug="tuitionbridge", title="TuitionBridge", subtitle="Cross-Border Tuition Payment Agent",
         badge="FINTECHATHON 2026", badge_color=CYAN, accent=GREEN, icon="globe",
         desc="A simulated agent that handles cross-border tuition payments end to end, "
              "built for the 2026 FinTechathon.",
         tech=["Python", "AI Agents", "FinTech"]),
]

ICONS = {
    "shield": '<path d="M0 -16 L13 -10 V1 C13 9 7 14 0 17 C-7 14 -13 9 -13 1 V-10 Z" fill="none" stroke-width="2.2"/>'
              '<path d="M-5 0 L-1 4 L6 -4" fill="none" stroke-width="2.4" stroke-linecap="round"/>',
    "chip": '<rect x="-10" y="-10" width="20" height="20" rx="3" fill="none" stroke-width="2.2"/>'
            '<path d="M-5 -10V-16M0 -10V-16M5 -10V-16M-5 10V16M0 10V16M5 10V16M-10 -5H-16M-10 0H-16M-10 5H-16'
            'M10 -5H16M10 0H16M10 5H16" stroke-width="2"/>',
    "chart": '<path d="M-14 12 L-5 2 L1 7 L13 -9" fill="none" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
             '<path d="M6 -9 H13 V-2" fill="none" stroke-width="2.4" stroke-linecap="round"/>',
    "globe": '<circle r="14" fill="none" stroke-width="2.2"/><ellipse rx="6" ry="14" fill="none" stroke-width="1.8"/>'
             '<path d="M-14 0 H14" stroke-width="1.8"/>',
}


def card(p: dict) -> None:
    w, h = 600, 250
    a = p["accent"]
    desc_lines = textwrap.wrap(p["desc"], 70)[:3]
    desc = "".join(f'<tspan x="28" dy="{0 if i == 0 else 21}">{escape(l)}</tspan>' for i, l in enumerate(desc_lines))
    chips, x = [], 28
    for t in p["tech"]:
        cw = int(len(t) * 7.4 + 22)
        chips.append(f'<g transform="translate({x} 206)"><rect width="{cw}" height="26" rx="13" fill="{a}" fill-opacity=".12" '
                     f'stroke="{a}" stroke-opacity=".45"/><text x="{cw / 2}" y="17.5" text-anchor="middle" class="chip">{escape(t)}</text></g>')
        x += cw + 8
    bw = int(len(p["badge"]) * 7.2 + 26)
    write(ASSETS / "cards" / f"{p['slug']}.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(p['title'])}">
    <defs>
      <linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".2"/></linearGradient>
      <radialGradient id="g" cx="1" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity=".22"/><stop offset=".6" stop-color="{a}" stop-opacity="0"/></radialGradient>
    </defs>
    <style>
      .t {{ font: 800 27px {SANS}; fill:{TEXT}; }}
      .s {{ font: 600 15px {SANS}; fill:{a}; }}
      .d {{ font: 400 14.5px {SANS}; fill:{MUTED}; }}
      .chip {{ font: 600 12px {MONO}; fill:{TEXT}; }}
      .badge {{ font: 700 11.5px {MONO}; fill:{p['badge_color']}; letter-spacing:.6px; }}
      .ring {{ animation: spin 14s linear infinite; transform-origin: 548px 50px; }}
      .scan {{ animation: scan 5s ease-in-out infinite; }}
      @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
      @keyframes scan {{ 0%,100% {{ transform: translateX(0); opacity:0; }} 15% {{ opacity:.6; }} 50% {{ transform: translateX(560px); opacity:0; }} }}
    </style>
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" fill="{SURFACE}"/>
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" fill="url(#g)"/>
    <rect class="scan" x="20" y="2" width="40" height="3" rx="1.5" fill="{a}"/>
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" fill="none" stroke="url(#b)" stroke-width="1.6"/>
    <g transform="translate(28 22)"><rect width="{bw}" height="24" rx="6" fill="{p['badge_color']}" fill-opacity=".12" stroke="{p['badge_color']}" stroke-opacity=".5"/>
      <text x="{bw / 2}" y="16.5" text-anchor="middle" class="badge">{escape(p['badge'])}</text></g>
    <circle class="ring" cx="548" cy="50" r="30" fill="none" stroke="{a}" stroke-opacity=".5" stroke-dasharray="6 8"/>
    <g transform="translate(548 50)" stroke="{a}">{ICONS[p['icon']]}</g>
    <text x="28" y="88" class="t">{escape(p['title'])}</text>
    <text x="28" y="112" class="s">{escape(p['subtitle'])}</text>
    <text y="142" class="d">{desc}</text>
    {''.join(chips)}
    </svg>
    """)


# ---------------------------------------------------------------------------
# Divider & footer
# ---------------------------------------------------------------------------
def divider() -> None:
    write(ASSETS / "divider.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="14" viewBox="0 0 1200 14">
    <defs><linearGradient id="d" x1="0" x2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".3" stop-color="{CYAN}"/>
      <stop offset=".5" stop-color="{VIOLET}"/><stop offset=".7" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
    </linearGradient></defs>
    <style>.dot {{ animation: run 4s ease-in-out infinite; }} @keyframes run {{ 0% {{ transform: translateX(0); }} 50% {{ transform: translateX(1100px); }} 100% {{ transform: translateX(0); }} }}</style>
    <rect x="0" y="6" width="1200" height="2" rx="1" fill="url(#d)"/>
    <circle class="dot" cx="50" cy="7" r="4" fill="{TEXT}"/>
    </svg>
    """)


def footer() -> None:
    write(ASSETS / "footer.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="120" viewBox="0 0 1200 120">
    <defs><linearGradient id="f" x1="0" x2="1">
      <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/>
    </linearGradient></defs>
    <style>
      .w1 {{ animation: wave 9s ease-in-out infinite; }} .w2 {{ animation: wave 12s ease-in-out infinite reverse; }}
      @keyframes wave {{ 0%,100% {{ transform: translateX(0); }} 50% {{ transform: translateX(-200px); }} }}
      .q {{ font: 600 17px {MONO}; fill:{TEXT}; letter-spacing:2px; }}
    </style>
    <path class="w1" d="M0 70 C200 30 400 110 600 70 S1000 30 1200 70 S1600 110 1400 70 V120 H0 Z" fill="url(#f)" fill-opacity=".18"/>
    <path class="w2" d="M0 85 C250 55 450 115 700 85 S1100 55 1400 85 V120 H0 Z" fill="url(#f)" fill-opacity=".28"/>
    <text x="600" y="40" text-anchor="middle" class="q">HARDWARE  &lt;/&gt;  SOFTWARE  &lt;/&gt;  INTELLIGENCE</text>
    </svg>
    """)


if __name__ == "__main__":
    header()
    terminal()
    divider()
    footer()
    for p in PROJECTS:
        card(p)
