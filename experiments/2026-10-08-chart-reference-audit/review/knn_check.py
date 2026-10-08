"""Whole-chart consistency check of every 5, 6 and 8 in the class numbers and codes of chart-reference-v2.json.

For each digit (excluding thin 1-like strokes) the script finds its seven most similar digits among the 5/6/8 digits of
other cells (normalised correlation of the native 1-bit pixels, as in pixel_check.py) and reports the majority label.
Labels come from v2, so a v2 digit that disagrees with its neighbours is a candidate misreading.

Run from the repository root:  python experiments/2026-10-08-chart-reference-audit/review/knn_check.py
Output: experiments/2026-10-08-chart-reference-audit/review/knn-5-6-8-check.json
"""
import json
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixel_check as pc

PK = 'experiments/2026-10-08-chart-reference-audit/'
man = json.load(open(pc.MANIFEST, encoding='utf-8'))
geo = {c['cell']: c['clip_pdf_points'] for c in man['cells']}
v2 = json.load(open(PK + 'chart-reference-v2.json', encoding='utf-8'))
V = {f"p{r['pdf_page']}_c{r['column']}_r{r['row']}": r for r in v2['rows']}

lib = []
for cell in sorted(geo):
    dl = pc.cell_digits(pc.page_bits(int(cell[1:3])), geo[cell])
    if dl is None:
        continue
    for li, (line, txt) in enumerate(((dl[0], str(V[cell]['rank'])), (dl[1], str(V[cell]['code'])))):
        if len(line) != len(txt):
            continue
        for k, (d, ch) in enumerate(zip(line, txt)):
            if ch in '568' and d['w'] / d['h'] >= 0.45:
                lib.append(dict(cell=cell, line='class' if li == 0 else 'code', idx=k, label=ch, a=pc.norm(d['img'])))

A = np.stack([x['a'].ravel() for x in lib])
A = A - A.mean(axis=1, keepdims=True)
A = A / np.linalg.norm(A, axis=1, keepdims=True)
S = A @ A.T
cells = np.array([x['cell'] for x in lib])
out, bad = [], []
for i, x in enumerate(lib):
    s = S[i].copy()
    s[cells == x['cell']] = -2          # leave the whole cell out
    top = np.argsort(-s)[:7]
    votes = Counter(lib[j]['label'] for j in top)
    pred = votes.most_common(1)[0][0]
    rec = dict(cell=x['cell'], line=x['line'], digit_index=x['idx'], v2_label=x['label'], knn_label=pred, votes=dict(votes),
               best_similarity=round(float(s[top[0]]), 3))
    out.append(rec)
    if pred != x['label']:
        bad.append(rec)
summary = dict(digits=len(lib), counts=dict(Counter(x['label'] for x in lib)), agree=len(lib) - len(bad), disagree=len(bad))
json.dump(dict(status='Exploratory reviewer consistency check', summary=summary, disagreements=bad, k=7), open(PK + 'review/knn-5-6-8-check.json', 'w'), indent=1)
print(json.dumps(summary), bad)
