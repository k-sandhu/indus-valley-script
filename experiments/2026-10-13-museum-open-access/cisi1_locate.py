"""Locate numbers in the CISI 1 basic-data pages and crop the table rows for reading by eye.

The OCR (tesseract, word boxes) is used only to find candidate rows; every decision is
made by reading the cropped page image. Pages are PDF 401-411 (printed 365-375) of the
local CISI 1 scan (research/literature/sources/joshi_parpola_1987_cisi1.pdf), rendered at
300 dpi into data/raw/2026-10-13-museum-open-access/cisi1-pages/.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/cisi1_locate.py LABEL NUMBER [NUMBER ...]
Writes one stacked crop per label to data/raw/2026-10-13-museum-open-access/cisi1-crops/.
"""
import csv
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "data/raw/2026-10-13-museum-open-access/cisi1-pages"
OUT = ROOT / "data/raw/2026-10-13-museum-open-access/cisi1-crops"


def words(page):
    rows = []
    with open(PAGES / f"pdf-{page:03d}.tsv", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r.get("text") and r["text"].strip():
                rows.append({k: (int(r[k]) if k in ("left", "top", "width", "height") else r[k]) for k in r})
    return rows


def locate(numbers, pages=range(401, 412)):
    hits = []
    for p in pages:
        for w in words(p):
            digits = re.sub(r"\D", "", w["text"])
            for n in numbers:
                if digits and (digits == n or (len(n) >= 4 and n in digits)):
                    hits.append((p, n, w))
    return hits


def crop(hits, label):
    OUT.mkdir(parents=True, exist_ok=True)
    tiles = []
    for p, n, w in hits:
        im = Image.open(PAGES / f"pdf-{p:03d}.png")
        W, H = im.size
        half = (0, W // 2 + 30) if w["left"] < W // 2 else (W // 2 - 30, W)
        y0 = max(0, w["top"] - 70)
        y1 = min(H, w["top"] + w["height"] + 70)
        t = im.crop((half[0], y0, half[1], y1))
        tiles.append((f"PDF {p} '{n}' at y={w['top']}", t))
    if not tiles:
        return None
    width = max(t.size[0] for _, t in tiles)
    total = sum(t.size[1] + 6 for _, t in tiles)
    canvas = Image.new("RGB", (width, total), "white")
    y = 0
    for _, t in tiles:
        canvas.paste(t, (0, y))
        y += t.size[1] + 6
    scale = min(1.0, 1300 / width)
    canvas = canvas.resize((int(width * scale), int(total * scale)))
    path = OUT / f"{label}.png"
    canvas.save(path)
    return path, [x for x, _ in tiles]


if __name__ == "__main__":
    label, nums = sys.argv[1], sys.argv[2:]
    res = crop(locate(nums), label)
    print(res if res else "no hits")
