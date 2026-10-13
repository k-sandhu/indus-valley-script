"""Pixel measurements on page renders for the plate checks.

extent(page, box): width and height in pixels of the photographed object inside box
(x0, y0, x1, y1), measured as the median, over the central half of rows (for width) or
columns (for height), of the distance between the first and last pixel darker than the
page background. The background level is the 90th percentile of the box border.

grid(page, box, out, step): writes an enlarged copy of the box with a labelled ruled grid,
so that feature coordinates can be read off by eye in page pixels.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]


def load(page):
    return Image.open(ROOT / page).convert("L")


def extent(page, box, margin=18):
    im = load(page).crop(box).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(im, dtype=float)
    border = np.concatenate([a[:4].ravel(), a[-4:].ravel(), a[:, :4].ravel(), a[:, -4:].ravel()])
    bg = np.percentile(border, 90)
    mask = a < bg - margin
    h, w = mask.shape
    widths, heights = [], []
    for row in mask[h // 4: 3 * h // 4]:
        idx = np.flatnonzero(row)
        if idx.size:
            widths.append(idx[-1] - idx[0] + 1)
    for col in mask[:, w // 4: 3 * w // 4].T:
        idx = np.flatnonzero(col)
        if idx.size:
            heights.append(idx[-1] - idx[0] + 1)
    return {"box": list(box), "background": round(float(bg), 1),
            "width_px": float(np.median(widths)) if widths else None,
            "height_px": float(np.median(heights)) if heights else None,
            "width_px_p90": float(np.percentile(widths, 90)) if widths else None,
            "height_px_p90": float(np.percentile(heights, 90)) if heights else None}


def grid(page, box, out, step=20, scale=3):
    im = load(page).crop(box)
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS).convert("RGB")
    d = ImageDraw.Draw(im)
    x0, y0 = box[0], box[1]
    for gx in range((x0 // step + 1) * step, box[2], step):
        X = (gx - x0) * scale
        major = gx % (step * 5) == 0
        d.line([(X, 0), (X, im.height)], fill=(255, 0, 0) if major else (255, 170, 170), width=1)
        if major:
            d.text((X + 2, 2), str(gx), fill=(255, 0, 0))
    for gy in range((y0 // step + 1) * step, box[3], step):
        Y = (gy - y0) * scale
        major = gy % (step * 5) == 0
        d.line([(0, Y), (im.width, Y)], fill=(0, 0, 255) if major else (170, 170, 255), width=1)
        if major:
            d.text((2, Y + 2), str(gy), fill=(0, 0, 255))
    im.save(ROOT / out)
    return out


def ruler(page, box, out, step=10, scale=4, margin=36):
    """Enlarged copy of box with tick marks in a margin on all four sides (no lines over the image)."""
    im = load(page).crop(box)
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    W, H = im.width + 2 * margin, im.height + 2 * margin
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(im.convert("RGB"), (margin, margin))
    d = ImageDraw.Draw(canvas)
    x0, y0 = box[0], box[1]
    for gx in range((x0 // step + 1) * step, box[2], step):
        X = margin + (gx - x0) * scale
        major = gx % (step * 5) == 0
        L = 14 if major else 6
        d.line([(X, margin - L), (X, margin)], fill=(255, 0, 0), width=1)
        d.line([(X, H - margin), (X, H - margin + L)], fill=(255, 0, 0), width=1)
        if major:
            d.text((X - 8, 2), str(gx), fill=(255, 0, 0))
            d.text((X - 8, H - 12), str(gx), fill=(255, 0, 0))
    for gy in range((y0 // step + 1) * step, box[3], step):
        Y = margin + (gy - y0) * scale
        major = gy % (step * 5) == 0
        L = 14 if major else 6
        d.line([(margin - L, Y), (margin, Y)], fill=(0, 0, 255), width=1)
        d.line([(W - margin, Y), (W - margin + L, Y)], fill=(0, 0, 255), width=1)
        if major:
            d.text((0, Y - 6), str(gy), fill=(0, 0, 255))
            d.text((W - margin + 2, Y - 6), str(gy), fill=(0, 0, 255))
    canvas.save(ROOT / out)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "extent":
        page = sys.argv[2]
        box = tuple(int(v) for v in sys.argv[3].split(","))
        print(json.dumps(extent(page, box)))
    elif cmd == "grid":
        page, box, out = sys.argv[2], tuple(int(v) for v in sys.argv[3].split(",")), sys.argv[4]
        step = int(sys.argv[5]) if len(sys.argv) > 5 else 20
        scale = int(sys.argv[6]) if len(sys.argv) > 6 else 3
        print(grid(page, box, out, step, scale))
    elif cmd == "ruler":
        page, box, out = sys.argv[2], tuple(int(v) for v in sys.argv[3].split(",")), sys.argv[4]
        step = int(sys.argv[5]) if len(sys.argv) > 5 else 10
        scale = int(sys.argv[6]) if len(sys.argv) > 6 else 4
        print(ruler(page, box, out, step, scale))
