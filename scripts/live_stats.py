#!/usr/bin/env python3
"""Builds live GitHub stat cards from the GitHub GraphQL API (runs daily in Actions).

    GITHUB_TOKEN=... python scripts/live_stats.py

Outputs: assets/generated/overview.svg, assets/generated/languages.svg
Self-hosted on purpose: no third-party stats service that can rate-limit or go down.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"
USER = os.environ.get("PROFILE_USER", "sleader3221-dot")

SURFACE = "#0d1117"
BORDER = "#30363d"
ACCENT = "#58a6ff"
CYAN = VIOLET = PINK = GREEN = AMBER = ACCENT
TEXT, MUTED = "#f0f6fc", "#8b949e"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Consolas, monospace"

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def gql(variables: dict) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def fetch() -> dict:
    user = gql({"login": USER, "cursor": None})
    repos = user["repositories"]["nodes"]
    while user["repositories"]["pageInfo"]["hasNextPage"]:
        nxt = gql({"login": USER, "cursor": user["repositories"]["pageInfo"]["endCursor"]})
        repos += nxt["repositories"]["nodes"]
        user["repositories"]["pageInfo"] = nxt["repositories"]["pageInfo"]
    user["repositories"]["nodes"] = repos
    return user


def streaks(days: list) -> tuple[int, int, int]:
    """(current streak, longest streak, active days) from the contribution calendar."""
    today = date.today().isoformat()
    counts = [(d["date"], d["contributionCount"]) for d in days if d["date"] <= today]
    longest = run = 0
    for _, c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    for i, (d, c) in enumerate(reversed(counts)):
        if c:
            current += 1
        elif i == 0:  # today without contributions yet doesn't break the streak
            continue
        else:
            break
    return current, longest, sum(1 for _, c in counts if c)


def overview_svg(u: dict) -> str:
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    cur, longest, active = streaks(days)
    repos = u["repositories"]["nodes"]
    stats = [
        ("Contributions (1y)", cc["contributionCalendar"]["totalContributions"], CYAN),
        ("Commits (1y)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"], VIOLET),
        ("Public repos", u["repositories"]["totalCount"], PINK),
        ("Stars earned", sum(r["stargazerCount"] for r in repos), AMBER),
        ("Current streak", f"{cur} d", GREEN),
        ("Longest streak", f"{longest} d", CYAN),
        ("Active days (1y)", active, VIOLET),
        ("Pull requests (1y)", cc["totalPullRequestContributions"], PINK),
    ]
    # mini sparkline of the last 26 weeks
    weeks = cc["contributionCalendar"]["weeks"][-26:]
    totals = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    peak = max(totals) or 1
    pts = " ".join(f"{30 + i * (540 / max(1, len(totals) - 1)):.1f},{290 - v / peak * 50:.1f}" for i, v in enumerate(totals))
    cells = []
    for i, (label, value, color) in enumerate(stats):
        col, row = i % 4, i // 4
        x, y = 30 + col * 138, 78 + row * 82
        cells.append(
            f'<g class="cell" transform="translate({x} {y})">'
            f'<rect width="128" height="70" rx="8" fill="#161b22" stroke="{BORDER}"/>'
            f'<text x="12" y="34" class="v">{escape(str(value))}</text>'
            f'<text x="12" y="56" class="l">{escape(label)}</text></g>')
    updated = datetime.now(timezone.utc).strftime("%d %b %Y")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="320" viewBox="0 0 600 320" role="img" aria-label="GitHub stats">
<defs>
  <linearGradient id="e" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
  <linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".25"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .h {{ font: 600 18px {SANS}; fill:{TEXT}; }} .sub {{ font: 500 12px {MONO}; fill:{MUTED}; }}
  .v {{ font: 700 24px {SANS}; fill:{TEXT}; }} .l {{ font: 500 11.5px {SANS}; fill:{MUTED}; }}
</style>
<rect x="1" y="1" width="598" height="318" rx="16" fill="{SURFACE}" stroke="{BORDER}"/>
<text x="30" y="44" class="h">GitHub Activity</text>
<text x="570" y="44" text-anchor="end" class="sub">updated {updated}</text>
{''.join(cells)}
<polyline points="30,290 {pts} 570,290" fill="url(#a)" stroke="none"/>
<polyline class="spark" points="{pts}" fill="none" stroke="{CYAN}" stroke-width="2.2" stroke-linejoin="round"/>
<text x="30" y="312" class="sub">last 26 weeks of contributions</text>
</svg>
"""


def languages_svg(u: dict) -> str:
    sizes: Counter = Counter()
    colors = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] += e["size"]
            colors[e["node"]["name"]] = e["node"]["color"] or MUTED
    total = sum(sizes.values()) or 1
    top = sizes.most_common(8)
    bar, x = [], 30.0
    for name, size in top:
        wpx = 540 * size / total
        bar.append(f'<rect x="{x:.1f}" y="70" width="{max(wpx, 0):.1f}" height="12" fill="{colors[name]}"/>')
        x += wpx
    rows = []
    for i, (name, size) in enumerate(top):
        col, row = i % 2, i // 2
        rx, ry = 30 + col * 275, 118 + row * 46
        pct = 100 * size / total
        rows.append(
            f'<g class="row" transform="translate({rx} {ry})">'
            f'<circle cx="7" cy="-5" r="6" fill="{colors[name]}"/>'
            f'<text x="22" y="0" class="n">{escape(name)}</text>'
            f'<text x="255" y="0" text-anchor="end" class="p">{pct:.1f}%</text>'
            f'<rect x="22" y="9" width="233" height="4" rx="2" fill="#1c2740"/>'
            f'<rect x="22" y="9" width="{233 * size / top[0][1]:.1f}" height="4" rx="2" fill="{colors[name]}"'
            f'/></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="320" viewBox="0 0 600 320" role="img" aria-label="Top languages">
<defs>
  <linearGradient id="e" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
  <clipPath id="c"><rect x="30" y="70" width="540" height="12" rx="6"/></clipPath>
</defs>
<style>
  .h {{ font: 600 18px {SANS}; fill:{TEXT}; }} .sub {{ font: 500 12px {MONO}; fill:{MUTED}; }}
  .n {{ font: 600 14px {SANS}; fill:{TEXT}; }} .p {{ font: 600 13px {MONO}; fill:{MUTED}; }}
</style>
<rect x="1" y="1" width="598" height="318" rx="16" fill="{SURFACE}" stroke="{BORDER}"/>
<text x="30" y="44" class="h">Most Used Languages</text>
<text x="570" y="44" text-anchor="end" class="sub">based on {len(u['repositories']['nodes'])} public repositories</text>
<g clip-path="url(#c)"><g class="bar">{''.join(bar)}</g></g>
{''.join(rows)}
</svg>
"""


def main() -> None:
    u = fetch()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "overview.svg").write_text(overview_svg(u), encoding="utf-8")
    (OUT / "languages.svg").write_text(languages_svg(u), encoding="utf-8")
    print("wrote assets/generated/overview.svg and languages.svg")


if __name__ == "__main__":
    main()
