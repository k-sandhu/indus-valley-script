"""Render the source pages used by the plate checks to local PNG files.

Usage: python render_pages.py [label=source:pdfpage:zoom ...]
Without arguments renders the default Check 1 pages. Images go to
data/raw/2026-10-13-plate-checks/pages/; the locator, zoom, pixel size and SHA-256 of each
render are appended to page-renders.json in this directory.
"""
import hashlib
import json
import sys
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "data/raw/2026-10-13-plate-checks/pages"
SOURCES = {
    "cisi1": ROOT / "research/literature/sources/joshi_parpola_1987_cisi1.pdf",
    "cisi2": ROOT / "data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf",
    "frenez2005": ROOT / "data/six-hour/lothal/frenez-tosi2005.pdf",
    "mackay1943": ROOT / "research/literature/sources/mackay_1943_chandaro.pdf",
}
DEFAULT = [
    "cisi1:312:4", "cisi1:313:4", "cisi1:314:4", "cisi1:409:4", "cisi1:28:2", "cisi1:29:2",
    "cisi2:120:6", "cisi2:471:6", "frenez2005:39:3",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(spec):
    src, page, zoom = spec.split(":")
    page, zoom = int(page), float(zoom)
    doc = fitz.open(SOURCES[src])
    pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / ("%s-pdf%03d.png" % (src, page))
    pix.save(out)
    return {"file": str(out.relative_to(ROOT)).replace("\\", "/"), "source": str(SOURCES[src].relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": sha256(SOURCES[src]), "pdf_page": page, "zoom": zoom,
            "page_points": [round(doc[page - 1].rect.width, 1), round(doc[page - 1].rect.height, 1)],
            "pixels": [pix.width, pix.height], "sha256": sha256(out)}


def main():
    specs = sys.argv[1:] or DEFAULT
    log = HERE / "page-renders.json"
    rows = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    for spec in specs:
        rec = render(spec)
        rows = [r for r in rows if r["file"] != rec["file"]] + [rec]
        print(rec["file"], rec["pixels"])
    log.write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
