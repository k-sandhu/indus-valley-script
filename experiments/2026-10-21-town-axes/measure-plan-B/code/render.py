"""Render PDF pages to PNG for plan measurement (plan-B role).

Usage (from repository root):
  python experiments/2026-10-21-town-axes/measure-plan-B/code/render.py PDF PAGEINDEX [DPI] [--name NAME]
  python experiments/2026-10-21-town-axes/measure-plan-B/code/render.py PDF --thumbs START END [--dpi 40]

PAGEINDEX is zero-based. Images go to data/raw/2026-10-21-town-axes/plan-B/renders/.
Prints the output path, pixel size and SHA-256 of the PNG.
"""
import hashlib
import os
import sys

import fitz  # PyMuPDF

OUT = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B", "renders")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def render(pdf, idx, dpi, name=None):
    os.makedirs(OUT, exist_ok=True)
    doc = fitz.open(pdf)
    page = doc[idx]
    pix = page.get_pixmap(dpi=dpi)
    base = name or os.path.splitext(os.path.basename(pdf))[0]
    out = os.path.join(OUT, f"{base}_p{idx:04d}_{dpi}dpi.png")
    pix.save(out)
    print(out, pix.width, pix.height, sha(out), "rotation", page.rotation, "rect", tuple(round(v, 1) for v in page.rect))
    return out


def thumbs(pdf, start, end, dpi=40, name=None, cols=6):
    """Contact sheet of pages start..end-1 to find plates quickly."""
    from PIL import Image, ImageDraw
    doc = fitz.open(pdf)
    ims = []
    for i in range(start, min(end, doc.page_count)):
        pix = doc[i].get_pixmap(dpi=dpi)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        im.thumbnail((260, 260))
        canvas = Image.new("RGB", (270, 285), "white")
        canvas.paste(im, (5, 20))
        ImageDraw.Draw(canvas).text((5, 3), f"idx {i}", fill="red")
        ims.append(canvas)
    if not ims:
        return
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 270, rows * 285), "white")
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * 270, (k // cols) * 285))
    os.makedirs(os.path.join(OUT, "thumbs"), exist_ok=True)
    base = name or os.path.splitext(os.path.basename(pdf))[0]
    out = os.path.join(OUT, "thumbs", f"{base}_{start:04d}-{end:04d}.png")
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    name = None
    if "--name" in args:
        k = args.index("--name")
        name = args[k + 1]
        del args[k:k + 2]
    if "--thumbs" in args:
        k = args.index("--thumbs")
        s, e = int(args[k + 1]), int(args[k + 2])
        dpi = 40
        if "--dpi" in args:
            dpi = int(args[args.index("--dpi") + 1])
        thumbs(args[0], s, e, dpi, name)
    else:
        render(args[0], int(args[1]), int(args[2]) if len(args) > 2 else 200, name)
