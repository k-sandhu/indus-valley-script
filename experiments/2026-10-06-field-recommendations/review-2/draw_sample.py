"""Reproduce the random draw of rows for the second review of Package F.

Read-only on the package; writes only review-2/sample.json.
The lecture rows (F01-F04) and the Frenez 2018 footnote row (F39) are checked
separately, so the 15 random rows come from the remaining 54 rows.
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
SEED = 20261007
FIXED = ['F01', 'F02', 'F03', 'F04', 'F39']

rows = json.loads((PACKAGE / 'recommendations.json').read_text(encoding='utf-8'))
ids = [row['id'] for row in rows]
frame = [i for i in ids if i not in FIXED]
sample = random.Random(SEED).sample(frame, 15)
result = dict(seed=SEED, python=sys.version.split()[0], rows=len(ids), frame_size=len(frame),
              fixed_rows=FIXED, sample_in_draw_order=sample, sample_sorted=sorted(sample))
with open(HERE / 'sample.json', 'w', encoding='utf-8', newline='\n') as handle:
    handle.write(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
