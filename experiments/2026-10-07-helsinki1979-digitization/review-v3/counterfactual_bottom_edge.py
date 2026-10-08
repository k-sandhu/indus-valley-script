"""Reviewer counterfactual (Exploratory, post hoc): re-run the frozen v3 unit segmentation and
recognizer on crop-stage rows with the row box shortened at the bottom edge.

The frozen code, model, digits, chart snapshot and calibration are imported unchanged and
nothing is written into the package; results go to a new JSON under review-v3/. The run first
checks that the unmodified box reproduces the frozen prediction for each row. It is a
sensitivity probe, not a rescoring and not a new evaluation.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG))
import crop_v3 as C  # noqa: E402
import pipeline as P  # noqa: E402

RUN = PKG / 'repair/2026-10-08-v3'


def codes(alts, n):
    s = set()
    for a in alts[:n]:
        s.update(a['codes'])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--rows', type=int, nargs='+', required=True)
    ap.add_argument('--deltas', type=float, nargs='+', default=[0.5, 1.0, 1.5])
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit('output exists')
    pred = {r['sample_index']: r for r in json.loads((RUN / 'predictions.json').read_text())['rows']}
    ref = {r['sample_index']: r for r in json.loads((RUN / 'blind/adjudicated-reference.json').read_text())['rows']}
    rec = P.Recognizer(P.templates(), PKG / 'development/classifier.pt')
    result = {}
    with P.fitz.open(P.PDF) as doc:
        pages = {}
        for i in args.rows:
            page = pred[i]['pdf_page']
            if page not in pages:
                pages[page] = C.process(doc, page, None, True)
            gray4, gray2, found, meta = pages[page]
            row = next(r for r in found if r['occurrence_key'] == pred[i]['occurrence_key'])
            entry = {}
            for delta in [0.0] + list(args.deltas):
                line = dict(row)
                box = list(row['glyph_pdf_box'])
                box[3] = box[3] - delta
                line['glyph_pdf_box'] = box
                units, _ = C.segment_units(gray4, gray2, line, rec)
                rc = [set(u['strict_candidate_codes']) for u in ref[i]['units']]
                detail = []
                if len(units) == len(rc):
                    for k, (u, s) in enumerate(zip(units, rc)):
                        detail.append(dict(unit=k, ref=sorted(s), top1=u['alternatives'][0]['codes'],
                                           in_top5=bool(s & codes(u['alternatives'], 5)) if s else None))
                entry[str(delta)] = dict(units=len(units), reference_units=len(rc),
                                         top1=[u['alternatives'][0]['codes'] for u in units], per_unit=detail,
                                         top5_whole_row=bool(detail) and all(d['in_top5'] for d in detail if d['in_top5'] is not None) and all(d['ref'] for d in detail))
            frozen_top1 = [u['alternatives'][0]['codes'] for u in pred[i]['units']]
            entry['reproduces_frozen_top1_at_delta0'] = entry['0.0']['top1'] == frozen_top1
            result[str(i)] = entry
            print(i, entry['reproduces_frozen_top1_at_delta0'],
                  {d: (v['units'], v['top5_whole_row']) for d, v in entry.items() if d != 'reproduces_frozen_top1_at_delta0'}, flush=True)
    args.out.write_text(json.dumps(result, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
