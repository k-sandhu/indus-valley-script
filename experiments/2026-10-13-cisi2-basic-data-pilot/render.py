"""Render CISI 2 basic-data pages and cut legible strips for transcription.

Usage (from the repository root):
  python experiments/2026-10-13-cisi2-basic-data-pilot/render.py page <pdfpage> [zoom]
  python experiments/2026-10-13-cisi2-basic-data-pilot/render.py strip <pdfpage> <y0> <y1> [x0 x1] [scale]
  python experiments/2026-10-13-cisi2-basic-data-pilot/render.py rows <pdfpage>

`page` renders a full page in greyscale at the given zoom (default 8.34, which matches
the 600 dpi foreground layer of the archive.org scan). `strip` cuts a horizontal band
(page-render pixel coordinates) and enlarges it by `scale` (default 1) for reading.
`rows` finds text rows by horizontal projection of dark pixels and prints their y ranges.
All images go to data/raw/2026-10-13-cisi2-basic-data-pilot/pages/ (local only); the
locator, zoom, size and SHA-256 of each full-page render are appended to
renders.json in this directory.
"""
import hashlib
import json
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot/pages"
SRC = ROOT / "data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf"
ZOOM = 8.34


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def page_path(pdfpage):
    return OUT / ("cisi2-pdf%03d.png" % pdfpage)


def render(pdfpage, zoom=ZOOM):
    doc = fitz.open(SRC)
    page = doc[pdfpage - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    OUT.mkdir(parents=True, exist_ok=True)
    out = page_path(pdfpage)
    pix.save(out)
    rec = {"file": str(out.relative_to(ROOT)).replace("\\", "/"),
           "source": str(SRC.relative_to(ROOT)).replace("\\", "/"),
           "pdf_page": pdfpage, "zoom": zoom,
           "page_points": [round(page.rect.width, 1), round(page.rect.height, 1)],
           "pixels": [pix.width, pix.height], "sha256": sha256(out)}
    log = HERE / "renders.json"
    rows = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    rows = [r for r in rows if r["file"] != rec["file"]] + [rec]
    log.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return rec


def strip(pdfpage, y0, y1, x0=None, x1=None, scale=1.0):
    im = Image.open(page_path(pdfpage))
    x0 = 0 if x0 is None else x0
    x1 = im.width if x1 is None else x1
    crop = im.crop((x0, y0, x1, y1))
    if scale != 1.0:
        crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
    out = OUT / ("strip-pdf%03d-y%04d-%04d-x%04d-%04d.png" % (pdfpage, y0, y1, x0, x1))
    crop.save(out)
    return str(out.relative_to(ROOT)).replace("\\", "/")


def rows(pdfpage, thresh=128, min_dark=3):
    a = np.asarray(Image.open(page_path(pdfpage)), dtype=np.uint8)
    dark = (a < thresh).sum(axis=1)
    on = dark >= min_dark
    spans, start = [], None
    for y, v in enumerate(on):
        if v and start is None:
            start = y
        elif not v and start is not None:
            spans.append((start, y))
            start = None
    if start is not None:
        spans.append((start, len(on)))
    return spans


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "page":
        zoom = float(sys.argv[3]) if len(sys.argv) > 3 else ZOOM
        print(json.dumps(render(int(sys.argv[2]), zoom)))
    elif cmd == "strip":
        p, y0, y1 = (int(v) for v in sys.argv[2:5])
        x0 = int(sys.argv[5]) if len(sys.argv) > 5 else None
        x1 = int(sys.argv[6]) if len(sys.argv) > 6 else None
        sc = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
        print(strip(p, y0, y1, x0, x1, sc))
    elif cmd == "rows":
        for s in rows(int(sys.argv[2])):
            print(s[0], s[1], s[1] - s[0])
