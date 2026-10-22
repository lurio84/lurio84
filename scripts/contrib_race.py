"""Generate contrib-race.svg: the real contribution calendar with a pixel car lapping it; cells light up as it passes."""
import json, subprocess, sys
from datetime import date
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "lurio84"
Q = '{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}' % USER
cal = json.loads(subprocess.check_output(["gh", "api", "graphql", "-f", f"query={Q}"]))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks, total = cal["weeks"], cal["totalContributions"]

CELL, GAP, X0, Y0 = 10, 3, 34, 58
STEP = CELL + GAP
W = X0 + len(weeks) * STEP + 14
TRACK_Y = Y0 + 7 * STEP + 8
H = TRACK_Y + 32
LAP, DRIVE = 10.0, 7.5  # seconds per lap, seconds the car is on screen
PAL = ["#1f2523", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
level = lambda c: 0 if c == 0 else 1 if c < 3 else 2 if c < 8 else 3 if c < 16 else 4

out = []
# Month labels at the first week that starts a new month
prev, last_i = None, -9
for i, w in enumerate(weeks):
    m = date.fromisoformat(w["contributionDays"][-1]["date"]).month
    if m != prev and i > 0 and i - last_i >= 3 and i < len(weeks) - 2:
        out.append(f'<text x="{X0 + i * STEP}" y="{Y0 - 8}" class="d">{MONTHS[m - 1]}</text>')
        last_i = i
    prev = m
for j, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    out.append(f'<text x="4" y="{Y0 + j * STEP + 9}" class="d">{lbl}</text>')

# Cells; active ones get a glow animation timed to the car passing their column
for i, w in enumerate(weeks):
    x = X0 + i * STEP
    delay = (i + 0.5) / len(weeks) * DRIVE
    for day in w["contributionDays"]:
        c = day["contributionCount"]
        y = Y0 + date.fromisoformat(day["date"]).isoweekday() % 7 * STEP
        out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{PAL[level(c)]}"/>')
        if c:
            out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="#ffd33d" class="hit" style="animation-delay:{delay:.2f}s"/>')

# Track: dashed lane + finish line
out.append(f'<line x1="{X0}" y1="{TRACK_Y + 15}" x2="{W - 14}" y2="{TRACK_Y + 15}" stroke="#2f3733" stroke-width="2" stroke-dasharray="6 6"/>')
fx = W - 20
for k in range(6):
    out.append(f'<rect x="{fx + (k % 2) * 3}" y="{TRACK_Y - 1 + (k // 2) * 4}" width="3" height="4" fill="{"#e3e8e5" if (k + k // 2) % 2 == 0 else "#151817"}"/>')

# Pixel car (3px units), drawn at origin then animated along the track
CAR = ["....rrrrrr....", "...rrwwrwwr...", "rrrrrrrrrrrrrr", "rrrrrrrrrrrryy", ".kk.......kk..."]
COL = {"r": "#e5484d", "w": "#bfe3ff", "y": "#ffd33d", "k": "#0b0d0c"}
car = "".join(f'<rect x="{i * 3}" y="{j * 3}" width="3" height="3" fill="{COL[ch]}"/>' for j, r in enumerate(CAR) for i, ch in enumerate(r) if ch != ".")
start, end = X0 - 50, W + 10
pct = DRIVE / LAP * 100

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} GitHub contributions in the last year">
<style>
text{{font:11px ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;fill:#e3e8e5}}
.d{{fill:#8a958f}}.h{{font-size:13px}}
.hit{{opacity:0;animation:glow {LAP}s linear infinite}}
@keyframes glow{{0%,3%{{opacity:1}}22%,100%{{opacity:0}}}}
.car{{animation:drive {LAP}s linear infinite}}
@keyframes drive{{0%{{transform:translate({start}px,{TRACK_Y}px)}}{pct:.1f}%,100%{{transform:translate({end}px,{TRACK_Y}px)}}}}
@media (prefers-reduced-motion:reduce){{.hit,.car{{animation:none}}.car{{transform:translate({X0 + len(weeks) * STEP * 0.6:.0f}px,{TRACK_Y}px)}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#151817"/>
<text x="14" y="24" class="h"><tspan fill="#6fd3a5">{total}</tspan> contributions in the last year</text>
{chr(10).join(out)}
<g class="car">{car}</g>
</svg>
'''
p = Path(__file__).parent.parent / "assets" / "contrib-race.svg"
p.write_text(svg, encoding="utf-8")
print(p, W, H, total)
