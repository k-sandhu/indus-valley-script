"""Cut reading tiles from a rendered CISI 2 basic-data page.

Usage (from the repository root):
  python experiments/2026-10-13-cisi2-basic-data-pilot/tiles.py <pdfpage> <half> <split_x> [y_start y_end step scale]

<half> is left or right; the half-column spans x 150-1500 (left) or 1650-3200 (right) of a
zoom-8.34 render. Each band of `step` pixels (default 450, with 30 px overlap) is cut
into two tiles, columns 1-4 (half start to split_x + 40) and column 5 (split_x - 20 to
half end), enlarged by `scale` (default 1.6). Tiles go to
data/raw/2026-10-13-cisi2-basic-data-pilot/tiles/ (local only).
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot/pages"
OUT = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot/tiles"
HALVES = {"left": (150, 1500), "right": (1650, 3200)}


def main():
    page, half, split = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    y0 = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    y1 = int(sys.argv[5]) if len(sys.argv) > 5 else 4400
    step = int(sys.argv[6]) if len(sys.argv) > 6 else 450
    scale = float(sys.argv[7]) if len(sys.argv) > 7 else 1.6
    im = Image.open(PAGES / ("cisi2-pdf%03d.png" % page))
    hx0, hx1 = HALVES[half]
    OUT.mkdir(parents=True, exist_ok=True)
    y = y0
    while y < y1:
        top, bot = max(0, y - 30), min(im.height, y + step + 30)
        for tag, (a, b) in (("c14", (hx0, split + 40)), ("c5", (split - 20, hx1))):
            t = im.crop((a, top, b, bot))
            t = t.resize((int(t.width * scale), int(t.height * scale)), Image.BICUBIC)
            name = "p%03d-%s-y%04d-%s.png" % (page, half, y, tag)
            t.save(OUT / name)
            print(name)
        y += step


if __name__ == "__main__":
    main()
