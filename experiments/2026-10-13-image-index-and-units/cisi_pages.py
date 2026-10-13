"""Read the running headings and captions of the CISI 1 and CISI 2 scans.

Usage (from the repository root):
    python -P experiments/2026-10-13-image-index-and-units/cisi_pages.py [--volumes 1 2] [--zoom 3]

For each PDF page (CISI 1: pages 1-431, the first copy of the repeated book scan; CISI 2:
all 486 pages) the page is rendered in grey at the given zoom and read with tesseract
(page segmentation mode 11, sparse text). For CISI 2 the PDF text layer is saved as well.
Output is local only, because it is text from copyrighted catalogues:
data/raw/2026-10-13-image-index-and-units/cisi-pages/cisi{1,2}-pages.jsonl with one
record per page: volume, pdf_page, ocr text, text layer (CISI 2), render size and the
SHA-256 of the source PDF. Existing output files are not overwritten.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

import fitz

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/2026-10-13-image-index-and-units/cisi-pages"
SOURCES = {
    1: ROOT / "research/literature/sources/joshi_parpola_1987_cisi1.pdf",
    2: ROOT / "data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf",
}
LAST_PAGE = {1: 431, 2: None}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--volumes", nargs="+", type=int, default=[1, 2])
    ap.add_argument("--zoom", type=float, default=3.0)
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    for vol in a.volumes:
        out = RAW / f"cisi{vol}-pages.jsonl"
        if out.exists():
            sys.exit(f"refusing to overwrite {out}")
        src = SOURCES[vol]
        digest = sha256(src)
        doc = fitz.open(src)
        last = LAST_PAGE[vol] or doc.page_count
        with tempfile.TemporaryDirectory() as tmp, out.open("w", encoding="utf-8") as fh:
            for p in range(1, last + 1):
                page = doc[p - 1]
                pix = page.get_pixmap(matrix=fitz.Matrix(a.zoom, a.zoom), colorspace=fitz.csGRAY)
                png = pathlib.Path(tmp) / "page.png"
                pix.save(png)
                r = subprocess.run(["tesseract", str(png), "-", "--psm", "11"], capture_output=True, text=True, encoding="utf-8", errors="replace")
                rec = {"volume": vol, "pdf_page": p, "ocr": r.stdout, "render": [pix.width, pix.height], "zoom": a.zoom,
                       "source_sha256": digest}
                if vol == 2:
                    rec["text_layer"] = page.get_text()
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if p % 50 == 0:
                    print(vol, p, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
