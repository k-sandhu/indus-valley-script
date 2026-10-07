"""Reviewer check: how far does the number field sit from the pipeline's static position?

Uses only the source PDF's OCR text layer (x positions of 4-digit words) for the numbered section,
pages 22-78. Nominal field left edges in PDF points follow pipeline.layout_orientation for margin_side
'right': n0 = round(base + 0.429*w) with w = 1190 (2x px), base = col*0.443*w.
"""
import json
import re
import statistics
from pathlib import Path
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[5]
doc = fitz.open(ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf')
w2 = 1190
nominal = {c: round(c * 0.443 * w2 + 0.429 * w2) / 2 for c in (0, 1)}
band = {0: (225, 300), 1: (490, 570)}
rows = []
for p in range(22, 79):
    words = doc[p - 1].get_text('words')
    for c in (0, 1):
        xs = [w[0] for w in words if re.fullmatch(r'[1-9]\d{3}[A-Z]?', w[4]) and band[c][0] <= w[0] <= band[c][1]
              and 10 <= (w[2] - w[0]) <= 24]
        if len(xs) >= 3:
            rows.append(dict(page=p, column=c, n_words=len(xs), median_x0=statistics.median(xs), nominal_x0=nominal[c],
                             shift_pt=statistics.median(xs) - nominal[c]))
shifts = [r['shift_pt'] for r in rows]
summary = dict(
    pages_columns_measured=len(rows),
    nominal_left_edge_pt=nominal,
    shift_pt_min=min(shifts), shift_pt_max=max(shifts), shift_pt_median=statistics.median(shifts),
    abs_shift_gt_2pt=sum(abs(s) > 2 for s in shifts), abs_shift_gt_4pt=sum(abs(s) > 4 for s in shifts),
    abs_shift_gt_8pt=sum(abs(s) > 8 for s in shifts),
    negative_shift_gt_1pt=sum(s < -1 for s in shifts),
    note='negative shift: number field starts left of the static field, so leading digits fall into the glyph strip and are clipped from the number field')
out = Path(__file__).resolve().parents[1] / 'diagnosis' / 'ocr-field-drift.json'
out.write_text(json.dumps(dict(summary=summary, rows=rows), indent=1), encoding='utf-8')
print(json.dumps(summary, indent=1))
