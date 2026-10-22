"""Neofetch-style info card. Edit LINES, then: python scripts/info_card.py  (STATIC=1 for a frozen frame)."""
import os
from xml.sax.saxutils import escape

OUT = "info-card.svg"
W, H = 490, 356  # H matches ascii-portrait.svg so the columns line up
FS, LH, PAD = 13, 19, 18
KEY, VAL, DIM, ACCENT = "#39d353", "#c9d1d9", "#8b949e", "#58a6ff"
STATIC = os.environ.get("STATIC") == "1"

# (key, value); key=None prints value as a plain/dim line, ("", "") is a spacer
LINES = [
    (None, "yazan@github"),
    (None, "-" * 12),
    ("Name", "Yazan Hijazi"),
    ("Location", "Amman, Jordan"),
    ("Role", "Automation Engineer & BI Developer"),
    ("Now", "Jo Academy · since Oct 2024"),
    ("Prev", "Data Analyst Intern · SHAI for AI"),
    ("Study", "BSc Data Science · Al-Balqa' '24"),
    ("", ""),
    ("Impact", "60+ processes automated · ~700 users"),
    ("", "Bitrix24 ERP/CRM + HR integration"),
    ("n8n", "IVR · WhatsApp bot · email approvals"),
    ("BI", "Metabase · Power BI · Python · SQL"),
    ("Built", "Together · Cairn · Candor"),
    ("", ""),
    ("Links", "yaznhijazi.runs-on.dev"),
]


def render():
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FS}">',
           "<style>.l{opacity:0;animation:in .4s ease-out forwards}"
           "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
           + (".l{opacity:1;animation:none}" if STATIC else "") + "</style>",
           f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>']
    # title bar
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{18 + i * 16}" cy="16" r="5" fill="{c}"/>')
    out.append(f'<text x="{W / 2}" y="20" text-anchor="middle" fill="{DIM}" font-size="11">~ neofetch</text>')

    y = 34 + LH
    for i, (k, v) in enumerate(LINES):
        delay = f"animation-delay:{0.6 + i * 0.12:.2f}s"
        if k is None:
            color = ACCENT if i == 0 else DIM
            out.append(f'<text class="l" style="{delay}" x="{PAD}" y="{y}" fill="{color}">{escape(v)}</text>')
        elif k or v:
            key = f'<tspan fill="{KEY}" font-weight="bold">{escape(k)}</tspan>' if k else ""
            out.append(f'<text class="l" style="{delay}" x="{PAD}" y="{y}">{key}'
                       f'<tspan x="{PAD + 90}" fill="{VAL}">{escape(v)}</tspan></text>')
        y += LH if (k or v) else LH // 2
    # palette strip, like neofetch's color blocks
    for i, c in enumerate(("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#58a6ff", "#bc8cff", "#ff7b72")):
        out.append(f'<rect class="l" style="animation-delay:{0.6 + len(LINES) * 0.12:.2f}s" '
                   f'x="{PAD + i * 22}" y="{y - 4}" width="20" height="12" rx="2" fill="{c}"/>')
    assert y + 12 < H, "card overflows; raise H"
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    open(OUT, "w", encoding="utf-8").write(render())
    print(f"wrote {OUT}")
