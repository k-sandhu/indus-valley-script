"""Reviewer pixel check of the printed chart digits (package P review).

Reads the embedded 1-bit page images of chart pages 20-21 from the PDF, segments the
class-number line and the code line of every cell by connected components, and classifies
each digit by normalised correlation with mean digit templates. The templates come only from
review/independent-readings.json (cells read by eye by the reviewer), never from the package's
readings. Output: review/pixel-check-all-cells.json.

Run from the repository root:  python experiments/2026-10-08-chart-reference-audit/review/pixel_check.py
"""
import json
import sys

import fitz
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

PDF = 'research/corpus/primary/koskenniemi_parpola1979.pdf'
MANIFEST = 'data/raw/2026-10-08-chart-reference-audit/render-manifest.json'   # geometry only
READINGS = 'experiments/2026-10-08-chart-reference-audit/review/independent-readings.json'
OUT = 'experiments/2026-10-08-chart-reference-audit/review/pixel-check-all-cells.json'
XREF = {20: 61, 21: 64}
IMG_X0, IMG_Y0, SCALE = 5.0, 0.661865234375, 4880 / 585.0   # image placement on the page, px per point
TW, TH = 26, 38

doc = fitz.open(PDF)
_pages = {}


def page_bits(pg):
    if pg not in _pages:
        pm = fitz.Pixmap(doc, XREF[pg])
        a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width * pm.n)
        if pm.n > 1:
            a = a[:, ::pm.n]
        _pages[pg] = a < 128
    return _pages[pg]


def label_components(bits, clip, xmax=27.0, ymin=8.0, ymax=26.0):
    x0, y0 = clip[0], clip[1]
    px0 = int(round((x0 - IMG_X0) * SCALE)); px1 = int(round((x0 + xmax - IMG_X0) * SCALE))
    py0 = int(round((y0 + ymin - IMG_Y0) * SCALE)); py1 = int(round((y0 + ymax - IMG_Y0) * SCALE))
    sub = bits[py0:py1, px0:px1]
    lab, n = ndi.label(sub, structure=np.ones((3, 3)))
    H, W = sub.shape
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < 12:
            continue
        c = dict(i=i, x0=int(xs.min()), x1=int(xs.max()), y0=int(ys.min()), y1=int(ys.max()), area=len(ys))
        h = c['y1'] - c['y0'] + 1; w = c['x1'] - c['x0'] + 1
        if c['x0'] <= 1 or c['y0'] <= 1 or c['y1'] >= H - 2 or c['x1'] >= W - 2:
            continue
        if h < 8 and w > 10:
            continue
        comps.append(c)
    return comps, lab


def cell_digits(bits, clip, xmax=27.0):
    comps, lab = label_components(bits, clip, xmax=xmax)
    if len(comps) < 2:
        return None
    cy = sorted((c['y0'] + c['y1']) / 2 for c in comps)
    gaps = [(cy[i + 1] - cy[i], (cy[i + 1] + cy[i]) / 2) for i in range(len(cy) - 1)]
    mid = max(gaps)[1]
    lines = [[], []]
    for c in comps:
        lines[0 if (c['y0'] + c['y1']) / 2 < mid else 1].append(c)
    out = []
    for L in lines:
        L = sorted(L, key=lambda c: c['x0'])
        groups = []
        for c in L:
            if groups and c['x0'] <= groups[-1]['x1'] + 1:
                g = groups[-1]
                g['x1'] = max(g['x1'], c['x1']); g['y0'] = min(g['y0'], c['y0']); g['y1'] = max(g['y1'], c['y1']); g['ids'].append(c['i'])
            else:
                groups.append(dict(x0=c['x0'], x1=c['x1'], y0=c['y0'], y1=c['y1'], ids=[c['i']]))
        # drop groups separated from the rest of the line by more than 40 px (ink of a neighbouring drawing)
        while len(groups) > 1 and groups[1]['x0'] - groups[0]['x1'] > 40:
            groups.pop(0)
        while len(groups) > 1 and groups[-1]['x0'] - groups[-2]['x1'] > 40:
            groups.pop()
        digs = []
        for g in groups:
            m = np.isin(lab, g['ids'])[g['y0']:g['y1'] + 1, g['x0']:g['x1'] + 1]
            digs.append(dict(img=m, x0=g['x0'], w=g['x1'] - g['x0'] + 1, h=g['y1'] - g['y0'] + 1))
        out.append(digs)
    return out


def norm(img):
    rows = np.where(img.any(axis=1))[0]; cols = np.where(img.any(axis=0))[0]
    im = img[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    pil = Image.fromarray((im * 255).astype(np.uint8)).resize((TW, TH), Image.BILINEAR)
    return ndi.gaussian_filter(np.asarray(pil).astype(float) / 255, 1.0)


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def build_templates(geo, bits_of):
    rd = json.load(open(READINGS, encoding='utf-8'))
    libs = {str(d): [] for d in range(10)}
    for c in rd['cells']:
        if c['changed_after_pixel_check'] or c['confidence'] not in ('high', 'medium-high'):
            continue
        cell = c['cell']
        dl = cell_digits(bits_of(cell), geo[cell])
        if dl is None:
            continue
        for line, txt in ((dl[0], str(c['class_number'])), (dl[1], str(c['code']))):
            if len(line) != len(txt):
                continue
            for d, ch in zip(line, txt):
                if d['w'] / d['h'] < 0.45:
                    continue
                libs[ch].append(norm(d['img']))
    return {ch: np.mean(v, axis=0) for ch, v in libs.items() if v}, {ch: len(v) for ch, v in libs.items()}


def main():
    man = json.load(open(MANIFEST, encoding='utf-8'))
    geo = {c['cell']: c['clip_pdf_points'] for c in man['cells']}
    bits_of = lambda cell: page_bits(int(cell[1:3]))
    templ, counts = build_templates(geo, bits_of)
    res = {}
    def classify(dl):
        rec = {}
        for name, line in (('class', dl[0]), ('code', dl[1])):
            digs = []
            for d in line:
                if d['w'] / d['h'] < 0.45:     # thin vertical stroke (a 1, possibly with a detached dot)
                    digs.append(dict(best='1', best_score=1.0, second='-', second_score=0.0, rule='aspect'))
                    continue
                a = norm(d['img'])
                sc = {ch: corr(a, T) for ch, T in templ.items()}
                order = sorted(sc, key=lambda k: -sc[k])
                digs.append(dict(best=order[0], best_score=round(sc[order[0]], 3), second=order[1], second_score=round(sc[order[1]], 3)))
            rec[name] = dict(read=''.join(d['best'] for d in digs), digits=digs)
        return rec

    def quality(rec):
        # lower is better: invalid lengths, then number of weak digits
        bad = sum(1 for k in ('class', 'code') if not 1 <= len(rec[k]['read']) <= 3)
        weak = sum(1 for k in ('class', 'code') for d in rec[k]['digits'] if d['best_score'] < 0.6)
        return (bad, weak)

    for cell in sorted(geo):
        best = None
        for xmax in (27.0, 31.0, 35.0):
            dl = cell_digits(bits_of(cell), geo[cell], xmax=xmax)
            if dl is None:
                continue
            rec = classify(dl)
            rec['label_region_width_pt'] = xmax
            if best is None or quality(rec) < quality(best):
                best = rec
            if quality(best) == (0, 0):
                break
        res[cell] = best if best is not None else dict(error='fewer than two components')
    json.dump(dict(status='Exploratory reviewer pixel check; not an expert certification', template_counts=counts,
                   templates_from=READINGS, cells=res), open(OUT, 'w'), indent=1)
    print('cells', len(res), 'template counts', counts)


if __name__ == '__main__':
    main()
