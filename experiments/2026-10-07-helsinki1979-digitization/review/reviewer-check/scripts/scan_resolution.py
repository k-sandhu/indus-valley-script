"""Reviewer: scan resolution and pixels per glyph.

Reports the embedded page image resolution for all 180 PDF pages, then measures glyph size and stroke width in native
pixels for the sampled corpus units (frozen unit boundaries), and the same quantities at the pipeline's 2x render.
"""
import io
import json
import statistics
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf as fitz
from PIL import Image
from scipy.ndimage import distance_transform_edt

HERE = Path(__file__).resolve().parents[3]
ROOT = HERE.parents[1]
PDF = ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'
RAW = ROOT / 'data/raw/2026-10-07-helsinki1979-digitization'
out = {}
doc = fitz.open(PDF)
formats = {}
for p in range(1, doc.page_count + 1):
    page = doc[p - 1]
    imgs = page.get_images(full=True)
    for im in imgs:
        info = doc.extract_image(im[0])
        rect = page.get_image_rects(im[0])[0]
        key = (info['width'], info['height'], info['bpc'], info['ext'], round(info['width'] / (rect.width / 72)))
        formats.setdefault(key, []).append(p)
out['image_formats'] = [dict(width=k[0], height=k[1], bits_per_component=k[2], codec=k[3], dpi=k[4], pages=len(v),
                             page_list=v if len(v) < 10 else f'{v[:3]}...{v[-3:]}') for k, v in sorted(formats.items(), key=lambda kv: -len(kv[1]))]

pred = json.loads((RAW / 'frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']
heights_native, widths_native, strokes_native, heights_2x, widths_2x = [], [], [], [], []
cache = {}
for row in pred:
    if row['sample_index'] in (14, 15, 16):
        continue
    p = row['pdf_page']
    page = doc[p - 1]
    if p not in cache:
        xref = page.get_images(full=True)[0][0]
        info = doc.extract_image(xref)
        arr = np.array(Image.open(io.BytesIO(info['image'])).convert('L'))
        rect = page.get_image_rects(xref)[0]
        cache = {p: ((arr < 128), rect, arr.shape[1] / rect.width, arr.shape[0] / rect.height)}
    ink, rect, sx, sy = cache[p]
    x0, y0, x1, y1 = row['glyph_xyxy_2x']
    for u in row['units']:
        if not u['alternatives']:
            continue
        ux0, ux1 = u['x_bounds']
        X0 = int(round(((x0 + ux0) / 2 - rect.x0) * sx)); X1 = int(round(((x0 + ux1) / 2 - rect.x0) * sx))
        Y0 = int(round((y0 / 2 - rect.y0) * sy)); Y1 = int(round((y1 / 2 - rect.y0) * sy))
        crop = ink[Y0:Y1, X0:X1]
        if crop.sum() < 50:
            continue
        ys, xs = np.where(crop)
        heights_native.append(int(ys.max() - ys.min() + 1))
        widths_native.append(int(xs.max() - xs.min() + 1))
        heights_2x.append(u['y_bounds'][1] - u['y_bounds'][0])
        widths_2x.append(ux1 - ux0)
        # stroke width: ink area divided by skeleton length
        m = crop.astype(np.uint8)
        dt = distance_transform_edt(m)
        # approximate skeleton by local maxima of the distance transform along ridges via morphological thinning
        thin = cv2.ximgproc.thinning(m * 255) if hasattr(cv2, 'ximgproc') else None
        if thin is not None:
            L = int((thin > 0).sum())
            if L > 20:
                strokes_native.append(float(m.sum() / L))
        else:
            ridge = dt[(dt >= cv2.dilate(dt.astype(np.float32), np.ones((3, 3), np.uint8)) - 1e-6) & (dt > 0)]
            if len(ridge) > 20:
                strokes_native.append(float(2 * np.median(ridge)))


def q(v):
    v = sorted(v)
    n = len(v)
    return dict(n=n, min=v[0], p10=v[int(.1 * (n - 1))], median=statistics.median(v), p90=v[int(.9 * (n - 1))], max=v[-1])


out['units_measured'] = len(heights_native)
out['unit_height_native_px'] = q(heights_native)
out['unit_width_native_px'] = q(widths_native)
out['stroke_width_native_px'] = q(strokes_native) if strokes_native else None
out['unit_height_2x_px'] = q(heights_2x)
out['unit_width_2x_px'] = q(widths_2x)
out['native_px_per_pt'] = 8.342
out['pipeline_px_per_pt'] = 2
out['linear_downsampling_factor'] = round(8.342 / 2, 3)
dest = Path(__file__).resolve().parents[1] / 'diagnosis' / 'scan-resolution.json'
dest.write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out, indent=1))
