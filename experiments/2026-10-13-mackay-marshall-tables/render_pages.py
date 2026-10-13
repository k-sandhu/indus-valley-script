"""Extract the table pages of Mackay 1938 vol. I and Marshall 1931 vol. II as images.

Run from the repository root:
    python -P experiments/2026-10-13-mackay-marshall-tables/render_pages.py

Mackay: printed pp. 368-392 from the archive.org DLI scan (PDF index = printed page + 22).
Marshall: printed pp. 402-405 from the DLI scan saved by the evidence census
(PDF index 52-55). The embedded page image is written unchanged at its native resolution.
All outputs are local-only page images.
"""
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/2026-10-13-mackay-marshall-tables"
MACKAY = RAW / "mackay1938/mackay1938_vol1_dli70071.pdf"
MARSHALL = ROOT / "data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/marshall-alt-pdf.body"


def extract(doc, index: int, out: Path):
    xref = doc[index].get_images()[0][0]
    pix = fitz.Pixmap(doc, xref)
    if pix.n - pix.alpha > 3 or pix.alpha:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    pix.save(out)
    return pix.width, pix.height


def main():
    (RAW / "mackay1938/pages").mkdir(parents=True, exist_ok=True)
    (RAW / "marshall1931").mkdir(parents=True, exist_ok=True)
    d = fitz.open(MACKAY)
    for printed in range(368, 393):
        print("mackay", printed, extract(d, printed + 22, RAW / f"mackay1938/pages/p{printed}.png"))
    d = fitz.open(MARSHALL, filetype="pdf")
    for printed, index in zip(range(402, 406), range(52, 56)):
        print("marshall", printed, extract(d, index, RAW / f"marshall1931/p{printed}.png"))


if __name__ == "__main__":
    main()
