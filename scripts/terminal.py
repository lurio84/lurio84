"""Generate terminal.svg: a Claude Code-style session that types itself out once and stays."""
from html import escape
from pathlib import Path

# (kind, segments) — kind "type" reveals char by char, "out" fades the whole line in.
# segments are (css class, text).
LINES = [
    ("type", [("p", "> "), ("", 'claude "who is lurio84?"')]),
    ("gap", []),
    ("out", [("t", "● Read"), ("", "(profile.md)")]),
    ("out", [("d", "  └ Software Engineering · University of Seville")]),
    ("out", [("d", "  └ Erasmus · Università di Pavia")]),
    ("out", [("d", "  └ Internships: CATEC (3D vision) · NTT Data (Java)")]),
    ("gap", []),
    ("out", [("t", "● Bash"), ("", "(gh repo list --source --limit 4)")]),
    ("out", [("d", "  └ gitpad · waystone · CryptoTrader · claude-skills")]),
    ("gap", []),
    ("type", [("p", "● "), ("", "Builds small tools and uses them every day:")]),
    ("type", [("", "  Rust, TypeScript, Python, Java.")]),
]
W, LH, X0, Y0 = 737, 22, 22, 62
TYPE_MS, OUT_MS, PAUSE_MS = 38, 260, 450

rows, t, y = [], 400, Y0
for kind, segs in LINES:
    if kind == "gap":
        y += LH // 2; t += PAUSE_MS // 2; continue
    if kind == "out":
        inner = "".join(f'<tspan class="{c}">{escape(s)}</tspan>' for c, s in segs)
        rows.append(f'<text x="{X0}" y="{y}" class="o" xml:space="preserve" style="animation-delay:{t}ms">{inner}</text>')
        t += OUT_MS
    else:
        spans = []
        for c, s in segs:
            for ch in s:
                spans.append(f'<tspan class="k {c}" style="animation-delay:{t}ms">{escape(ch)}</tspan>')
                t += TYPE_MS
        rows.append(f'<text x="{X0}" y="{y}" xml:space="preserve">{"".join(spans)}</text>')
        t += PAUSE_MS
    y += LH
y += LH // 2
rows.append(f'<text x="{X0}" y="{y}" class="o" style="animation-delay:{t}ms"><tspan class="p">&gt; </tspan><tspan class="cur">▌</tspan></text>')
H = y + 24

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal session: Lucas Ronquillo, Software Engineering at the University of Seville">
<style>
text{{font:14px ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;fill:#e3e8e5;white-space:pre}}
.p{{fill:#6fd3a5}}.t{{fill:#e7a85c}}.d{{fill:#8a958f}}
.k,.o{{opacity:0;animation:in 1ms forwards}}
.o{{animation-duration:220ms}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes in{{to{{opacity:1}}}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.k,.o{{animation:none;opacity:1}}.cur{{animation:none}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#151817"/>
<circle cx="22" cy="22" r="6" fill="#ff5f57"/><circle cx="42" cy="22" r="6" fill="#febc2e"/><circle cx="62" cy="22" r="6" fill="#28c840"/>
<text x="{W // 2}" y="27" text-anchor="middle" class="d" style="font-size:12px">lurio84 — claude</text>
{chr(10).join(rows)}
</svg>
'''
out = Path(__file__).parent.parent / "assets" / "terminal.svg"
out.write_text(svg, encoding="utf-8")
print(out, f"{t} ms total")
