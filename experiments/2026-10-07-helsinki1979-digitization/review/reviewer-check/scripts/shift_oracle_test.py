"""Reviewer feasibility test (Exploratory, post-outcome): move the static number-field window by a page-column offset
measured from the source PDF's OCR text layer, force upright orientation, and rerun the frozen recognizer.

The offset for each (page, column) is the median left edge of the OCR layer's 4-digit words minus the pipeline's nominal
left edge (review/reviewer-check/diagnosis/ocr-field-drift.json). It uses no reference data and no pipeline output.
Everything else (row anchoring, segmentation, matcher, digit classifier, calibration) is the frozen code and weights.
Rows without an offset estimate keep the static window (reported separately).

  python shift_oracle_test.py --out <json>
"""
import argparse
import json
import sys
from pathlib import Path

import pymupdf as fitz

HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import pipeline as P  # noqa: E402
from evaluate import score_row, aggregate  # noqa: E402

DRIFT = json.loads((Path(__file__).resolve().parents[1] / 'diagnosis/ocr-field-drift.json').read_text())['rows']
SHIFT = {(r['page'], r['column']): r['shift_pt'] for r in DRIFT}
CURRENT = {}


def layout_orientation_shifted(gray, side):
    """pipeline.layout_orientation with the right-margin field window moved by CURRENT[col] (2x pixels)."""
    h, w = gray.shape
    regions = []
    score = 0
    for c in range(2):
        base = c * 0.443 * w
        if side == 'right':
            n0, n1 = round(base + 0.429 * w), round(base + 0.470 * w)
            n0 += CURRENT.get(c, 0)
            n1 += CURRENT.get(c, 0)
            gx0, gx1 = round(base + 0.060 * w), n0 - 3
        else:
            n0, n1 = round(base + 0.095 * w), round(base + 0.142 * w)
            gx0, gx1 = n1 + 3, round(base + 0.440 * w)
        y0, y1 = round(h * .073), round(h * .933)
        patch = gray[y0:y1, n0:n1] < P.PARAM['threshold']
        bands = [(a + y0, b + y0) for a, b in P.runs(patch.sum(1) >= 2, max_gap=5) if 9 <= b - a <= 29]
        score += sum(1 for a, b in bands if 15 <= b - a <= 25)
        centers = [(a + b) / 2 - 7 for a, b in bands]
        ink = (gray[y0:y1, gx0:gx1] < P.PARAM['threshold']).sum(1)
        observed = [(a + y0, b + y0) for a, b in P.runs(ink >= 2, max_gap=3) if b - a >= 8]
        extras = [(a + b) / 2 for a, b in observed if centers and min(abs((a + b) / 2 - z) for z in centers) > 21]
        for center in extras:
            bands.append((round(center + 4), round(center + 16)))
            centers.append(center)
        ordered = sorted(zip(centers, bands))
        centers = [z for z, _ in ordered]
        bands = [b for _, b in ordered]
        blanks = [(a + y0, b + y0) for a, b in P.runs(ink < 2) if b - a >= 2]
        edges = [y0]
        for previous, following in zip(centers, centers[1:]):
            mid = (previous + following) / 2
            eligible = [(a + b) / 2 for a, b in blanks if previous + 7 < (a + b) / 2 < following - 7]
            edges.append(round(min(eligible, key=lambda z: abs(z - mid))) if eligible else round(mid))
        edges.append(y1)
        rows = []
        for i, ((a, b), center) in enumerate(zip(bands, centers)):
            low, high = edges[i], edges[i + 1]
            rows.append(dict(pdf_column=c, row_index=i, margin_xyxy_2x=[n0, a - 2, n1, b + 2], glyph_xyxy_2x=[gx0, low, gx1, high],
                             row_anchor_y_2x=center,
                             flags=(['possible_continuation_without_margin'] if center in extras else []) +
                                   ([] if len(centers) > 10 else ['few_margin_anchors'])))
        regions.extend(rows)
    return score, regions


def detect_layout_upright(gray):
    score, rows = layout_orientation_shifted(gray, 'right')
    return gray, rows, dict(rotation=0, margin_side='right', anchor_score=score, competing_scores=[])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    P.layout_orientation = layout_orientation_shifted
    P.detect_layout = detect_layout_upright
    sel = json.loads((HERE / 'blind/selection-source-only.json').read_text())['rows']
    frozen = {r['sample_index']: r for r in json.loads((P.ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']}
    refs = {}
    for n in 'abc':
        for r in json.loads((HERE / f'blind/reference-{n}.json').read_text(encoding='utf-8'))['rows']:
            refs[r['sample_index']] = r
    rec = P.Recognizer(P.templates(), P.HERE / 'development/classifier.pt')
    out_rows = []
    with fitz.open(P.PDF) as doc:
        for page in sorted({r['pdf_page'] for r in sel}):
            for c in (0, 1):
                s = SHIFT.get((page, c))
                CURRENT[c] = int(round(2 * s)) if s is not None else 0
            gray, rows, meta = P.process_page(doc, page, recognizer=None)
            for chosen in sel:
                if chosen['pdf_page'] != page:
                    continue
                i = chosen['sample_index']
                orig = frozen[i]
                cands = [r for r in rows if r['pdf_column'] == orig['pdf_column']]
                if not cands:
                    continue
                row = min(cands, key=lambda r: abs(r['row_anchor_y_2x'] - orig['row_anchor_y_2x']))
                x0, y0, x1, y1 = row['glyph_xyxy_2x']
                units, cost = rec.segment(gray[y0:y1, x0:x1])
                row['units'] = units
                row['sample_index'] = i
                row['occurrence_key'] = orig['occurrence_key']
                row['pdf_page'] = page
                scored = score_row(row, refs[i])
                scored['shift_applied_pt'] = SHIFT.get((page, orig['pdf_column']))
                scored['anchor_distance_px'] = abs(row['row_anchor_y_2x'] - orig['row_anchor_y_2x'])
                out_rows.append(scored)
    res = {}
    for name, sel_rows in (('all_60', out_rows), ('with_offset_estimate', [r for r in out_rows if r['shift_applied_pt'] is not None]),
                           ('without_offset_estimate', [r for r in out_rows if r['shift_applied_pt'] is None])):
        if not sel_rows:
            continue
        agg = aggregate(sel_rows)
        res[name] = dict(rows=len(sel_rows), count_agrees=agg['drawn_unit_count_agreement']['success'], number_correct=agg['inscription_number_accuracy']['success'],
                         classification_correct=agg['classification_exact_accuracy']['success'],
                         strict_top1_whole=agg['strict_top1']['whole_rows_all_sample']['success'], strict_top5_whole=agg['strict_top5']['whole_rows_all_sample']['success'])
        base = [frozen_row for frozen_row in out_rows if frozen_row['sample_index'] in {r['sample_index'] for r in sel_rows}]
    frozen_metrics = {r['sample_index']: r for r in json.loads((HERE / 'evaluation/2026-10-07-frozen-v1/metrics.json').read_text())['rows']}
    for name, idxs in (('all_60', set(frozen_metrics)), ('with_offset_estimate', {r['sample_index'] for r in out_rows if r['shift_applied_pt'] is not None}),
                       ('without_offset_estimate', {r['sample_index'] for r in out_rows if r['shift_applied_pt'] is None})):
        fr = [frozen_metrics[i] for i in sorted(idxs)]
        if fr:
            res.setdefault(name, {})['frozen_same_rows'] = dict(
                rows=len(fr), count_agrees=sum(bool(r['count_agrees']) for r in fr), number_correct=sum(bool(r['number_correct']) for r in fr),
                classification_correct=sum(bool(r['classification_correct']) for r in fr),
                strict_top1_whole=sum(bool(r['strict_top1']['whole_row_compatible']) for r in fr),
                strict_top5_whole=sum(bool(r['strict_top5']['whole_row_compatible']) for r in fr))
    a.out.write_text(json.dumps(dict(summary=res, rows=[{k: v for k, v in r.items() if k != 'calibration_items'} for r in out_rows]), indent=1), encoding='utf-8')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
