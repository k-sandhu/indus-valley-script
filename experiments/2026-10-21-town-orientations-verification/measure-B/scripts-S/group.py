"""Assign system labels by greedy maximum-length 6-degree windows of folded deviation.

Used where a source's deviations form a continuum with no architectural feature to separate them.
Repeatedly: among unassigned lines, find the closed window [t, t+6] (t at each line's theta) holding
the greatest total length (ties: more lines, then lower t); label those lines <prefix>-1, -2, ... in
order. Prints a JSON mapping {line_id: system} for a build_town spec, and a summary.

Usage: group.py <lines.json> <prefix> [--exclude id1,id2] [--window 6]
"""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('lines'); p.add_argument('prefix')
p.add_argument('--exclude', default=''); p.add_argument('--window', type=float, default=6.0)
a = p.parse_args()
ex = set(x for x in a.exclude.split(',') if x)
rows = [l for l in json.loads(Path(a.lines).read_text(encoding='utf-8'))['lines'] if l['id'] not in ex]
left = {l['id']: (l['theta_deg'], l['length_m']) for l in rows}
out = {}; k = 0; summ = []
while left:
    best = None
    for t0 in sorted(set(v[0] for v in left.values())):
        ids = [i for i, (t, L) in left.items() if t0 - 1e-9 <= t <= t0 + a.window + 1e-9]
        key = (sum(left[i][1] for i in ids), len(ids), -t0)
        if best is None or key > best[0]:
            best = (key, ids, t0)
    k += 1
    lab = f'{a.prefix}-{k}'
    for i in best[1]:
        out[i] = lab
        del left[i]
    summ.append((lab, len(best[1]), round(best[0][0], 1), round(best[2], 2), round(best[2] + a.window, 2)))
print(json.dumps(out))
for s in summ:
    print('#', *s)
