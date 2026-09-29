# -*- coding: utf-8 -*-
"""Site icon: a symmetric histogram (a bell-shaped distribution) in white on the site's teal.
Geometry lives on a 16-unit grid, so bar edges fall on whole pixels at 16, 32 and 48 px.
Writes favicon.svg, favicon.ico (16/32/48) and apple-touch-icon.png (180, full-bleed, as iOS expects)."""
import io, pathlib, sys
from PIL import Image, ImageDraw

TEAL, WHITE = (22, 128, 140, 255), (255, 255, 255, 255)
BARS = [(1, 3), (4, 6), (7, 10), (10, 6), (13, 3)]   # (left x, height) in grid units; width 2, baseline y = 13
BASE, W, RADIUS = 13, 2, 3.5


def draw(size, rounded=True, inset=0.0):
    """inset: fraction of the tile left empty around the bars (for the full-bleed Apple icon)."""
    ss = 8
    S = size * ss
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=RADIUS / 16 * S, fill=TEAL)
    else:
        d.rectangle([0, 0, S, S], fill=TEAL)
    k = S / 16 * (1 - 2 * inset)          # grid unit in supersampled pixels
    off = S * inset
    for x, h in BARS:
        d.rectangle([off + x * k, off + (BASE - h) * k, off + (x + W) * k - 1, off + BASE * k - 1], fill=WHITE)
    return im.resize((size, size), Image.LANCZOS)


def svg():
    bars = "".join(f'<rect x="{x * 2}" y="{(BASE - h) * 2}" width="{W * 2}" height="{h * 2}"/>' for x, h in BARS)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            f'<rect width="32" height="32" rx="{RADIUS * 2:g}" fill="#16808c"/>'
            f'<g fill="#fff">{bars}</g></svg>\n')


def write_all(out):
    out = pathlib.Path(out)
    (out / "favicon.svg").write_text(svg(), encoding="utf-8")
    base = draw(48)
    base.save(out / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)],
              append_images=[draw(16), draw(32)])
    draw(180, rounded=False, inset=0.16).convert("RGB").save(out / "apple-touch-icon.png", optimize=True)


if __name__ == "__main__":
    write_all(sys.argv[1] if len(sys.argv) > 1 else ".")
