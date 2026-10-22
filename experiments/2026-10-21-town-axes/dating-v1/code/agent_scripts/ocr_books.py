"""OCR image-only scans page by page into scratch text files (one file per book)."""
import concurrent.futures as cf
import os
import pathlib
import subprocess
import sys
import tempfile

import fitz

TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
OUT = pathlib.Path(sys.argv[1])
BOOKS = sys.argv[2:]


def ocr(args):
    pdf, i, tag = args
    out = OUT / tag / ("p%04d.txt" % (i + 1))
    if out.exists():
        return
    doc = fitz.open(pdf)
    pg = doc[i]
    pix = pg.get_pixmap(dpi=200, colorspace=fitz.csGRAY)
    with tempfile.TemporaryDirectory() as td:
        png = os.path.join(td, "p.png")
        pix.save(png)
        r = subprocess.run([TESS, png, "stdout", "--psm", "3"], capture_output=True)
        out.write_bytes(r.stdout)


def main():
    jobs = []
    for spec in BOOKS:
        tag, pdf = spec.split("=", 1)
        (OUT / tag).mkdir(parents=True, exist_ok=True)
        n = fitz.open(pdf).page_count
        jobs += [(pdf, i, tag) for i in range(n)]
    with cf.ProcessPoolExecutor(max_workers=18) as ex:
        for k, _ in enumerate(ex.map(ocr, jobs, chunksize=4)):
            if k % 100 == 0:
                print(k, len(jobs), flush=True)


if __name__ == "__main__":
    main()
