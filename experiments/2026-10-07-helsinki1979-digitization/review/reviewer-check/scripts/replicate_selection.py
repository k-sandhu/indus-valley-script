"""Reviewer: replicate the seeded row selection from the frozen layout code and compare with blind/selection.json.

Rebuilds the frame (layout detection only, pages 31-79, no OCR, no recognition) and draws
random.Random(20261007).sample(frame, 60) exactly as pipeline.sample() does, then compares the occurrence keys.
Writes nothing to the package except the JSON named by --out.
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

import pymupdf as fitz

HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import pipeline as P  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    frame = []
    per_page = collections.Counter()
    with fitz.open(P.PDF) as doc:
        for page in range(P.PARAM['evaluation_pages'][0], P.PARAM['evaluation_pages'][1] + 1):
            _, rows, meta = P.process_page(doc, page, ocr=False)
            frame.extend(rows)
            per_page[page] = len(rows)
    chosen = sorted(random.Random(P.SEED).sample(frame, 60), key=lambda r: (r['pdf_page'], r['pdf_column'], r['row_index']))
    keys = [r['occurrence_key'] for r in chosen]
    sel = json.loads((HERE / 'blind/selection.json').read_text())
    sel_keys = [r['occurrence_key'] for r in sel['rows']]
    pages_sel = collections.Counter(r['pdf_page'] for r in sel['rows'])
    expected = {p: 60 * n / len(frame) for p, n in per_page.items()}
    res = dict(frame_rows=len(frame), selection_frame_rows=sel['frame_rows'], same_frame_size=len(frame) == sel['frame_rows'],
               same_60_keys=keys == sel_keys, n_matching=len(set(keys) & set(sel_keys)),
               rows_per_page_in_frame={str(p): n for p, n in per_page.items()},
               sample_rows_per_page={str(p): n for p, n in sorted(pages_sel.items())},
               page78_frame_rows=per_page[78], page78_sample_rows=pages_sel[78], page78_expected_sample_rows=round(expected[78], 2),
               max_sample_rows_one_page=max(pages_sel.values()))
    a.out.write_text(json.dumps(res, indent=1), encoding='utf-8')
    print(json.dumps({k: v for k, v in res.items() if not k.startswith('rows_per') and k != 'sample_rows_per_page'}, indent=1))


if __name__ == '__main__':
    main()
