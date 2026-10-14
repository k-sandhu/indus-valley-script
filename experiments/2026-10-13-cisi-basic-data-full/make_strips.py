"""Render the CISI 1 and CISI 2 basic-data pages and cut reading strips for every block.

Usage (from the repository root):
  python experiments/2026-10-13-cisi-basic-data-full/make_strips.py

A block is one half-column of one printed page (PROCEDURE.md of the CISI 2 pilot). Each block's
half-column, from its first to its last line of text, is cut into windows of about fourteen lines
with about two lines of overlap; each cut is moved to the lightest pixel row nearby, so that it
falls between lines. Strips are saved at the render resolution (1:1). Renders and strips stay local in data/raw/2026-10-13-cisi-basic-data-full/;
blocks.json in this directory lists each block's page, half, strip count and render hash, with no
transcribed values.
"""
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "data/raw/2026-10-13-cisi-basic-data-full"
VOLUMES = {
    "cisi2": {"pdf": ROOT / "data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf",
              "offset": 35, "printed": range(437, 448), "zoom": 8.34,
              "halves": {"L": (150, 1500), "R": (1650, 3200)}, "window": 640, "overlap": 90, "band": 25},
    "cisi1": {"pdf": ROOT / "research/literature/sources/joshi_parpola_1987_cisi1.pdf",
              "offset": 36, "printed": range(366, 376), "zoom": 4.0,
              "halves": {"L": (100, 1175), "R": (1165, 2347)}, "window": 460, "overlap": 65, "band": 15},
}
EXTRA = [("cisi2-p435-M595", "cisi2", 435, "L")]  # the one entry of p. 435 the pilot left out


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(vol, printed):
    v = VOLUMES[vol]
    out = RAW / "pages" / f"{vol}-pdf{printed + v['offset']:03d}.png"
    if not out.exists():
        doc = fitz.open(v["pdf"])
        pix = doc[printed + v["offset"] - 1].get_pixmap(matrix=fitz.Matrix(v["zoom"], v["zoom"]), colorspace=fitz.csGRAY)
        out.parent.mkdir(parents=True, exist_ok=True)
        pix.save(out)
    return out


def text_rows(a, x0, x1, thresh=128, min_dark=4, min_gap=3):
    dark = (a[:, x0:x1] < thresh).sum(axis=1) >= min_dark
    rows, start, gap = [], None, 0
    for y, on in enumerate(dark):
        if on:
            if start is None:
                start = y
            gap = 0
        elif start is not None:
            gap += 1
            if gap >= min_gap:
                rows.append((start, y - gap + 1))
                start, gap = None, 0
    if start is not None:
        rows.append((start, len(dark)))
    return [r for r in rows if r[1] - r[0] >= 6]


def cut(block, vol, printed, half):
    v = VOLUMES[vol]
    page = render(vol, printed)
    im = Image.open(page)
    a = np.asarray(im, dtype=np.uint8)
    x0, x1 = v["halves"][half]
    rows = text_rows(a, x0, x1)
    outdir = RAW / "strips" / block
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob("*.png"):
        old.unlink()
    # Fixed windows of about fourteen lines with two lines of overlap; each cut is moved to the
    # lightest pixel row within a search band so that it falls between lines of text.
    ink = (a[:, x0:x1] < 128).sum(axis=1)
    top = max(0, rows[0][0] - 12) if rows else 0
    bottom = min(im.height, rows[-1][1] + 12) if rows else im.height
    height, overlap, band = v["window"], v["overlap"], v["band"]

    def snap(y):
        lo, hi = max(top, y - band), min(bottom, y + band)
        return lo + int(np.argmin(ink[lo:hi])) if hi > lo else y

    strips, y0 = [], top
    while True:
        y1 = bottom if y0 + height >= bottom else snap(y0 + height)
        name = outdir / f"s{len(strips) + 1:02d}.png"
        im.crop((x0, y0, x1, y1)).save(name)
        strips.append({"file": name.relative_to(ROOT).as_posix(), "y": [y0, y1], "x": [x0, x1]})
        if y1 >= bottom:
            break
        y0 = snap(y1 - overlap)
    return {"block": block, "volume": vol, "printed_page": printed, "pdf_page": printed + v["offset"], "half": half,
            "render": page.relative_to(ROOT).as_posix(), "render_sha256": sha256(page), "zoom": v["zoom"],
            "text_rows": len(rows), "strips": strips}


def main():
    blocks = []
    for vol, v in VOLUMES.items():
        for printed in v["printed"]:
            for half in ("L", "R"):
                blocks.append(cut(f"{vol}-p{printed}{half}", vol, printed, half))
    for block, vol, printed, half in EXTRA:
        blocks.append(cut(block, vol, printed, half))
    (RAW / "strips.json").write_text(json.dumps(blocks, indent=1), encoding="utf-8")
    tracked = [{k: b[k] for k in ("block", "volume", "printed_page", "pdf_page", "half", "zoom", "render_sha256", "text_rows")}
               | {"strips": len(b["strips"])} for b in blocks]
    (HERE / "blocks.json").write_text(json.dumps(tracked, indent=1) + "\n", encoding="utf-8")
    for b in tracked:
        print(b["block"], b["text_rows"], "rows", b["strips"], "strips")


if __name__ == "__main__":
    main()
