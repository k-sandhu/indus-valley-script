"""Contrast-enhanced inspection view (CLAHE on luminance) with a labelled grid (role img-B).

Usage: python enhance.py <mosaic.png> <x0> <y0> <x1> <y1> <out.png> [grid_step] [scale] [clip]
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from view import crop_grid  # noqa: E402


def enhance(src, x0, y0, x1, y1, out, step=100, scale=1.0, clip=3.0):
    im = cv2.imread(str(src))[y0:y1, x0:x1]
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    cl = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
    lab[..., 0] = cl.apply(lab[..., 0])
    im2 = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    from PIL import Image
    crop_grid(Image.fromarray(im2), x0, y0, x1, y1, out, step, scale)

if __name__ == "__main__":
    a = sys.argv
    enhance(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]), a[6],
            int(a[7]) if len(a) > 7 else 100, float(a[8]) if len(a) > 8 else 1.0, float(a[9]) if len(a) > 9 else 3.0)
