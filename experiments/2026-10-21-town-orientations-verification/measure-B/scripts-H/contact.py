"""Working aid: contact sheet of PDF page thumbnails, labelled with one-based page numbers.

Usage: contact.py <pdf> <out.png> <first> <last> [--dpi 30] [--cols 6]
"""
import sys
sys.dont_write_bytecode = True
import argparse
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import fitz
from PIL import Image, ImageDraw


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pdf")
    p.add_argument("out")
    p.add_argument("first", type=int)
    p.add_argument("last", type=int)
    p.add_argument("--dpi", type=int, default=30)
    p.add_argument("--cols", type=int, default=6)
    a = p.parse_args()
    if Path(a.out).exists():
        raise FileExistsError(a.out)
    thumbs = []
    with fitz.open(a.pdf) as d:
        for n in range(a.first, min(a.last, d.page_count) + 1):
            pix = d[n - 1].get_pixmap(dpi=a.dpi, alpha=False)
            im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ImageDraw.Draw(im).text((3, 3), f"p{n}", fill="red", stroke_width=2, stroke_fill="white")
            thumbs.append(im)
    w = max(t.width for t in thumbs)
    h = max(t.height for t in thumbs)
    rows = (len(thumbs) + a.cols - 1) // a.cols
    sheet = Image.new("RGB", (w * a.cols, h * rows), "white")
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % a.cols) * w, (i // a.cols) * h))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
