"""Reviewer sensitivity test (Exploratory, post-outcome): an alternative matcher on the same frozen unit boundaries.

The corpus glyphs were drawn by a pen plotter from the same stroke font as the sign chart (1979 edition, section 7
technical notes), so a unit and its chart template should coincide up to registration. This script scores each frozen
unit crop against size-compatible chart templates with normalized cross-correlation of lightly blurred binary images
(cv2.matchTemplate, TM_CCOEFF_NORMED) at 2x, 4x and 8.34x render scales, and compares top-1 and top-5 compatibility with
the strict reference against the frozen chamfer + CNN matcher on identical units. No learned parameters, no tuning on
the reference: the blur sigma, size tolerance and shift margin were fixed before the first run.

  python ncc_test.py --scales 2 4 8.34 --out <json>
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf as fitz

HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import pipeline as P  # noqa: E402
from evaluate import align  # noqa: E402

ROOT = P.ROOT
THRESH = P.PARAM['threshold']
SIGMA_PT = 0.30  # blur sigma in points (0.6 px at 2x, 2.5 px at 8.34x); fixed in advance


def render_scale(doc, page_no, s):
    pix = doc[page_no - 1].get_pixmap(matrix=fitz.Matrix(s, s), colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()


def blur(b, s):
    sigma = max(0.5, SIGMA_PT * s)
    return cv2.GaussianBlur(b.astype(np.float32), (0, 0), sigma)


def templates_at(doc, s):
    f = s / 2.0
    labels = json.loads(P.CHART.read_text(encoding='utf-8'))
    pages = {p: render_scale(doc, p, s) for p in (20, 21)}
    lib = []
    for row in labels['rows']:
        p, c, r = row['pdf_page'], row['column'], row['row']
        x = (176 if p == 20 else 153) + 100.4 * c
        y = 152.6 + 40.1 * r
        xy = [round((x - 20) * f), round((y - 19.5) * f), round((x + 31) * f), round((y + 19.5) * f)]
        b = P.tight(pages[p][xy[1]:xy[3], xy[0]:xy[2]] < THRESH)
        lib.append(dict(codes=sorted(set([int(row['code'])] + [int(a) for a in row['alternatives']])), key=f'{p}:{c}:{r}', b=b, img=blur(b, s)))
    return lib


def score_unit(body, lib, s):
    q = P.tight(body)
    h, w = q.shape
    m = int(round(0.12 * max(h, w))) + 3
    pad = np.zeros((h + 2 * m, w + 2 * m), np.float32)
    pad[m:m + h, m:m + w] = blur(q, s)
    out = []
    for t in lib:
        th, tw = t['b'].shape
        if abs(tw - w) > max(0.2 * tw, 3 * s / 2) or abs(th - h) > max(0.2 * th, 4 * s / 2):
            continue
        if th > pad.shape[0] or tw > pad.shape[1]:
            continue
        res = cv2.matchTemplate(pad, t['img'], cv2.TM_CCOEFF_NORMED)
        out.append((float(res.max()), t['codes'], t['key']))
    out.sort(key=lambda z: -z[0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scales', type=float, nargs='+', default=[2, 4, 8.34])
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    pred = json.loads((ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']
    refs = {}
    for n in 'abc':
        for r in json.loads((HERE / f'blind/reference-{n}.json').read_text(encoding='utf-8'))['rows']:
            refs[r['sample_index']] = r
    pairs = []
    for row in pred:
        i = row['sample_index']
        if i in (14, 15, 16):
            continue
        truth = [set(int(c) for c in u['strict_candidate_codes']) for u in refs[i]['units']]
        g5 = [{int(c) for al in u['alternatives'][:5] for c in al['codes']} for u in row['units']]
        for pi, ti in align(g5, truth)['alignment']:
            if pi is not None and ti is not None:
                pairs.append((row, pi, truth[ti], len(row['units']) == len(truth)))
    results = {}
    with fitz.open(P.PDF) as doc:
        for s in a.scales:
            lib = templates_at(doc, s)
            tmpl_w = {tuple(t['codes']): t['b'].shape for t in lib}
            cache = {}
            per = []
            for (row, pi, truth, eq) in pairs:
                pg = row['pdf_page']
                if pg not in cache:
                    cache = {pg: render_scale(doc, pg, s)}
                gray = cache[pg]
                x0, y0, x1, y1 = row['glyph_xyxy_2x']
                u = row['units'][pi]
                ux0, ux1 = u['x_bounds']
                f = s / 2.0
                Y0, Y1 = int(round(y0 * f)), int(round(y1 * f))
                X0, X1 = int(round((x0 + ux0) * f)), int(round((x0 + ux1) * f))
                body = gray[Y0:Y1, X0:X1] < THRESH
                if not body.any():
                    per.append(dict(sample_index=row['sample_index'], unit=pi, top1=False, top5=False, clean=False, eq=eq))
                    continue
                q = P.tight(body)
                ranked = score_unit(body, lib, s)
                top1 = bool(ranked and set(ranked[0][1]) & truth)
                top5 = bool(any(set(r_[1]) & truth for r_ in ranked[:5]))
                # geometry-plausible unit: crop size within 10% of the correct template's size
                clean = False
                for t in lib:
                    if set(t['codes']) & truth:
                        th, tw = t['b'].shape
                        if abs(tw - q.shape[1]) <= max(0.1 * tw, 2 * f) and abs(th - q.shape[0]) <= max(0.1 * th, 2 * f):
                            clean = True
                            break
                froz1 = bool({int(c) for c in u['alternatives'][0]['codes']} & truth) if u['alternatives'] else False
                froz5 = bool({int(c) for al in u['alternatives'][:5] for c in al['codes']} & truth)
                per.append(dict(sample_index=row['sample_index'], unit=pi, top1=top1, top5=top5, clean=clean, eq=eq, frozen_top1=froz1,
                                frozen_top5=froz5, n_candidates=len(ranked)))
            def agg(sel):
                n = len(sel)
                return dict(n=n, ncc_top1=sum(p['top1'] for p in sel), ncc_top5=sum(p['top5'] for p in sel),
                            frozen_top1=sum(p.get('frozen_top1', False) for p in sel), frozen_top5=sum(p.get('frozen_top5', False) for p in sel))
            results[str(s)] = dict(all_aligned=agg(per), equal_count_rows=agg([p for p in per if p['eq']]),
                                   geometry_plausible_units=agg([p for p in per if p['clean']]),
                                   geometry_plausible_equal_count=agg([p for p in per if p['clean'] and p['eq']]), units=per)
            print(s, {k: v for k, v in results[str(s)].items() if k != 'units'}, flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(results, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
