"""Fetch the public contribution calendar (no token) and render contrib-heatmap.svg."""
import datetime as dt
import re
import sys
import urllib.request

USER = "yaznhijazii"
OUT = "contrib-heatmap.svg"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 40, 46
W = 881  # = ascii-portrait (391) + info-card (490), so the edges line up in the README


def fetch(user):
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions",
                                 headers={"User-Agent": "profile-heatmap"})
    return urllib.request.urlopen(req, timeout=30).read().decode()


def parse(html):
    counts = {}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"([\d,]+) contribution", text)
        counts[cid] = int(m.group(1).replace(",", "")) if m else 0
    days = []
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        date = re.search(r'data-date="([^"]+)"', td)
        if not date:
            continue
        cid = re.search(r'id="([^"]+)"', td).group(1)
        level = int(re.search(r'data-level="(\d)"', td).group(1))
        days.append((dt.date.fromisoformat(date.group(1)), level, counts.get(cid, 0)))
    days.sort()
    if not days:
        sys.exit("no contribution cells found: GitHub markup changed?")
    return days


def stats(days):
    total = sum(c for _, _, c in days)
    longest = run = 0
    for _, _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    # today may still be empty; don't break the streak for it
    for i, (_, _, c) in enumerate(reversed(days)):
        if c:
            current += 1
        elif i:
            break
    best = max(days, key=lambda d: d[2])
    return total, current, longest, best


def render(days):
    total, current, longest, best = stats(days)
    start = days[0][0] - dt.timedelta(days=(days[0][0].weekday() + 1) % 7)  # Sunday column start
    weeks = (days[-1][0] - start).days // 7 + 1
    H = TOP + 7 * STEP + 62
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
           "<style>.c{opacity:0;transform-box:fill-box;transform-origin:center;"
           "animation:in .45s cubic-bezier(.2,.8,.2,1) forwards}"
           "@keyframes in{from{opacity:0;transform:translateY(-6px) scale(.4)}to{opacity:1;transform:none}}"
           ".t{fill:#8b949e;font-size:11px}.h{fill:#39d353;font-size:12px}</style>",
           f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           f'<text x="16" y="24" class="h">$ git log --since="1 year ago" | heatmap</text>']

    last_month = None
    for w in range(weeks):
        d = start + dt.timedelta(weeks=w)
        if d.month != last_month and w < weeks - 2:
            out.append(f'<text x="{LEFT + w * STEP}" y="{TOP - 6}" class="t">{d:%b}</text>')
            last_month = d.month
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="10" y="{TOP + row * STEP + 10}" class="t">{name}</text>')

    for date, level, count in days:
        w, r = (date - start).days // 7, (date - start).days % 7
        delay = (w + r) * 0.018
        out.append(f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{LEFT + w * STEP}" '
                   f'y="{TOP + r * STEP}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[level]}">'
                   f"<title>{count} on {date:%b %d, %Y}</title></rect>")

    y = TOP + 7 * STEP + 26
    out.append(f'<text x="{LEFT}" y="{y}" class="t"><tspan fill="#e6edf3">{total:,}</tspan> contributions '
               f'· current streak <tspan fill="#e6edf3">{current}d</tspan> · longest '
               f'<tspan fill="#e6edf3">{longest}d</tspan> · best day <tspan fill="#e6edf3">{best[2]}</tspan> '
               f'({best[0]:%b %d})</text>')
    lx = W - 16 - len(PALETTE) * STEP - 34
    out.append(f'<text x="{lx - 34}" y="{y}" class="t">Less</text>')
    for i, c in enumerate(PALETTE):
        out.append(f'<rect x="{lx + i * STEP}" y="{y - 10}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>')
    out.append(f'<text x="{lx + len(PALETTE) * STEP + 4}" y="{y}" class="t">More</text>')
    out.append(f'<text x="{LEFT}" y="{y + 20}" class="t" opacity=".6">updated {dt.date.today():%Y-%m-%d}</text>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    days = parse(fetch(sys.argv[1] if len(sys.argv) > 1 else USER))
    assert len(days) > 300 and all(0 <= l < len(PALETTE) for _, l, _ in days)
    open(OUT, "w", encoding="utf-8").write(render(days))
    print(f"wrote {OUT}: {len(days)} days, {stats(days)[0]} contributions")
