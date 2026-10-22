"""Photo -> one-color ASCII portrait that types itself in, row by row. Run locally when the photo changes.

usage: python scripts/ascii.py photo.jpg
"""
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

OUT = "ascii-portrait.svg"
RAMP = " .`:-=+*cs#%@"  # dark (sparse) -> bright (dense): reads as a lit photo on a dark panel
COLS = 72
BG = 232                # grayscale above this counts as background (tune per photo)
FS = 8.5                # font size
CW, LH = FS * 0.6, FS   # monospace char width, line height
PAD = 12
ROW_DELAY, ROW_DUR = 0.05, 0.35


def to_rows(path):
    img = ImageOps.exif_transpose(Image.open(path)).convert("L")
    rows = round(COLS * img.height / img.width * CW / LH)
    img = img.resize((COLS, rows), Image.LANCZOS)
    # near-white = background -> blank; equalize only the subject so the face gets real shadows
    subject = img.point(lambda p: 255 if p < BG else 0)
    img = ImageOps.equalize(img, mask=subject)
    px, bg = img.tobytes(), subject.tobytes()
    n = len(RAMP) - 1
    return ["".join(RAMP[1 + px[i] * (n - 1) // 255] if bg[i] else " "
                    for i in range(r * COLS, (r + 1) * COLS)).rstrip()
            for r in range(rows)]


def render(rows):
    w = round(PAD * 2 + COLS * CW)
    h = round(PAD * 2 + len(rows) * LH)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FS}">',
           f'<rect width="{w}" height="{h}" rx="10" fill="#0d1117" stroke="#30363d"/>']
    for i, line in enumerate(rows):
        if not line:
            continue
        y = PAD + i * LH
        begin = f"{i * ROW_DELAY:.2f}s"
        full = len(line) * CW + 1
        out.append(f'<clipPath id="r{i}"><rect x="{PAD}" y="{y}" width="0" height="{LH}">'
                   f'<animate attributeName="width" from="0" to="{full:.1f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
                   f"</rect></clipPath>")
        out.append(f'<text clip-path="url(#r{i})" x="{PAD}" y="{y + LH * 0.8:.1f}" fill="#c9d1d9" '
                   f'xml:space="preserve">{escape(line)}</text>')
        # block cursor riding the wipe edge, gone once the row is printed
        out.append(f'<rect x="{PAD}" y="{y}" width="{CW:.1f}" height="{LH}" fill="#39d353" opacity="0">'
                   f'<set attributeName="opacity" to="1" begin="{begin}"/>'
                   f'<animate attributeName="x" from="{PAD}" to="{PAD + full:.1f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
                   f'<set attributeName="opacity" to="0" begin="{i * ROW_DELAY + ROW_DUR:.2f}s"/>'
                   f"</rect>")
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    rows = to_rows(sys.argv[1])
    while rows and not rows[0]:
        rows.pop(0)
    assert rows and all(len(r) <= COLS for r in rows)
    open(OUT, "w", encoding="utf-8").write(render(rows))
    print(f"wrote {OUT}: {COLS}x{len(rows)}")
    print("\n".join(rows))
