"""Reviewer sensitivity test (Exploratory, post-outcome): does render resolution limit the frozen matcher?

Re-runs the frozen matching method (chamfer distance on aspect-preserving canvases plus 0.03 x CNN negative log
probability, same weights, same constants expressed in 2x pixels and scaled by f = scale / 2) on the frozen unit
boundaries of the 57 non-rotated sample rows, with the unchanged PDF rendered at several scales. Unit boxes,
crop defects, merges and the reference are identical across scales, so differences isolate resolution.
Scale 2 must reproduce the frozen top-5 template keys; this is checked and reported.

  python resolution_test.py --scales 1 2 4 6 8.34 --out <json>
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pymupdf as fitz
import torch
from scipy.ndimage import distance_transform_edt

HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import pipeline as P  # noqa: E402
from evaluate import align  # noqa: E402

ROOT = P.ROOT
THRESH = P.PARAM['threshold']


def render_scale(doc, page_no, s):
    pix = doc[page_no - 1].get_pixmap(matrix=fitz.Matrix(s, s), colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()


def shape_canvas_f(b, f):
    b = P.tight(b)
    h, w = b.shape
    H, W = int(round(64 * f)), int(round(96 * f))
    h = min(h, int(56 * f))
    w = min(w, int(88 * f))
    a = np.zeros((H, W), bool)
    y0, x0 = (H - h) // 2, (W - w) // 2
    a[y0:y0 + h, x0:x0 + w] = b[:h, :w]
    return a


class ScaledRecognizer:
    def __init__(self, s, doc):
        self.s, self.f = s, s / 2.0
        f = self.f
        labels = json.loads(P.CHART.read_text(encoding='utf-8'))
        pages = {p: render_scale(doc, p, s) for p in (20, 21)}
        self.lib = []
        for row in labels['rows']:
            p, c, r = row['pdf_page'], row['column'], row['row']
            x = (176 if p == 20 else 153) + 100.4 * c
            y = 152.6 + 40.1 * r
            xy = [round((x - 20) * f), round((y - 19.5) * f), round((x + 31) * f), round((y + 19.5) * f)]
            b = P.tight(pages[p][xy[1]:xy[3], xy[0]:xy[2]] < THRESH)
            self.lib.append(dict(key=f'{p}:{c}:{r}', codes=sorted(set([row['code']] + row['alternatives'])), rank=row['rank'],
                                 rank_candidates=sorted(set([row['rank']] + row.get('rank_alternatives', []))),
                                 width=int(b.shape[1]), height=int(b.shape[0]), binary=b))
        self.model = P.Net(len(self.lib)).to(P.DEVICE)
        self.model.load_state_dict(torch.load(P.HERE / 'development/classifier.pt', map_location=P.DEVICE, weights_only=True))
        self.model.eval()
        self.base = np.stack([shape_canvas_f(t['binary'], f) for t in self.lib])
        self.dt = np.stack([distance_transform_edt(~a) for a in self.base]).astype('float32')
        self.dt_flat = self.dt.reshape(len(self.lib), -1)
        positions = [np.flatnonzero(a.ravel()) for a in self.base]
        mx = max(len(x) for x in positions)
        self.points = np.zeros((len(self.lib), mx), np.int32)
        self.pw = np.zeros((len(self.lib), mx), np.float32)
        for i, pos in enumerate(positions):
            self.points[i, :len(pos)] = pos
            self.pw[i, :len(pos)] = 1 / max(1, len(pos))
        self.widths = np.array([t['width'] for t in self.lib])

    def alternatives(self, binary):
        f = self.f
        b = P.tight(binary)
        ink = shape_canvas_f(b, f)
        dt = distance_transform_edt(~ink)
        valid = np.flatnonzero(np.abs(self.widths - b.shape[1]) <= np.maximum(4 * f, .25 * self.widths))
        if not len(valid):
            valid = np.arange(len(self.lib))
        chamfer = np.full(len(self.lib), 100., np.float32)
        best = np.full(len(valid), 100., np.float32)
        for dy in (-3, 0, 3):
            for dx in (-2, 0, 2):
                dyy, dxx = int(round(dy * f)), int(round(dx * f))
                shifted = np.roll(ink, (dyy, dxx), (0, 1))
                shifted_dt = np.roll(dt, (dyy, dxx), (0, 1))
                q = np.flatnonzero(shifted.ravel())
                d = (self.dt_flat[np.ix_(valid, q)].mean(1) + (shifted_dt.ravel()[self.points[valid]] * self.pw[valid]).sum(1)) / 2
                best = np.minimum(best, d)
        chamfer[valid] = best / f + .035 * np.abs(self.widths[valid] - b.shape[1]) / f
        net = P.canvas(b)
        with torch.inference_mode():
            logp = torch.log_softmax(self.model(torch.tensor(net[None, None], device=P.DEVICE)), 1)[0].cpu().numpy()
        score = chamfer - P.PARAM['learned_weight'] * logp
        order = np.argsort(score, kind='stable')[:5]
        return [dict(template_key=self.lib[int(i)]['key'], codes=self.lib[int(i)]['codes'], score=float(score[i])) for i in order]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scales', type=float, nargs='+', default=[1, 2, 4, 6, 8.34])
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
    print('aligned pairs', len(pairs), flush=True)
    results = {}
    with fitz.open(P.PDF) as doc:
        for s in a.scales:
            rec = ScaledRecognizer(s, doc)
            cache = {}
            hits1 = hits5 = 0
            eq1 = eq5 = eqn = 0
            same_keys = 0
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
                if abs(s - 2) < 1e-9:
                    # exactly the frozen path
                    strip = gray[y0:y1, x0:x1]
                    body = strip < THRESH
                    body = body[:, ux0:ux1]
                else:
                    Y0, Y1 = int(round(y0 * f)), int(round(y1 * f))
                    X0, X1 = int(round((x0 + ux0) * f)), int(round((x0 + ux1) * f))
                    body = gray[Y0:Y1, X0:X1] < THRESH
                if not body.any():
                    per.append(dict(sample_index=row['sample_index'], unit=pi, top1=False, top5=False))
                    continue
                alts = rec.alternatives(body)
                c1 = {int(c) for c in alts[0]['codes']}
                c5 = {int(c) for al in alts for c in al['codes']}
                h1, h5 = bool(c1 & truth), bool(c5 & truth)
                hits1 += h1
                hits5 += h5
                if eq:
                    eqn += 1
                    eq1 += h1
                    eq5 += h5
                froz = [al['template_key'] for al in u['alternatives'][:5]]
                same_keys += froz == [al['template_key'] for al in alts]
                per.append(dict(sample_index=row['sample_index'], unit=pi, top1=h1, top5=h5, top1_key=alts[0]['template_key']))
            results[str(s)] = dict(top1=hits1, top5=hits5, n=len(pairs), equal_count_top1=eq1, equal_count_top5=eq5, equal_count_n=eqn,
                                   identical_top5_keys_to_frozen=same_keys, units=per)
            print(s, {k: v for k, v in results[str(s)].items() if k != 'units'}, flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(results, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
