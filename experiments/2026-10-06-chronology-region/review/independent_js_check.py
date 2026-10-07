"""Reviewer check: recompute the headline 3B-versus-3C equal-type Jensen-Shannon divergence without package code.

Reads only data/normalized/lipi_observed_faces.jsonl. Maps the Harappa `time` labels by an explicit list,
normalizes the two object-type typos, keeps faces with at least one known sign, averages the per-type
token distributions with equal weight over SEAL:S, TAB:B and TAB:I, and computes the divergence in bits.
Writes review/independent_js_check.json (counts and one number).
"""
import json, math, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
rows = [json.loads(l) for l in open(ROOT / 'data/normalized/lipi_observed_faces.jsonl', encoding='utf-8')]
P3B = {'Period 3B', 'Period 3B-1', 'Period 3B-2'}; P3C = {'Period 3C', 'Period 3C-1', 'Period 3C-2', 'Period 3C-3', 'Period 3C-4'}
fix = {'POsT:T:g': 'POT:T:g', 'POT:T:S': 'POT:T:s'}
types = ('SEAL:S', 'TAB:B', 'TAB:I')
cnt = {(p, t): collections.Counter() for p in ('3B', '3C') for t in types}
faces = collections.Counter(); fams = collections.defaultdict(set)
for r in rows:
    if r['site'] != 'Harappa': continue
    label = r['metadata']['time'].strip()
    p = '3B' if label in P3B else '3C' if label in P3C else None
    t = fix.get(r['object_type'], r['object_type'])
    known = [s for s in r['signs_reading_rtl'] if s != '000']
    if p is None or not known or t not in types: continue
    cnt[(p, t)].update(known); faces[(p, t)] += 1; fams[(p, t)].add(r['object_family_id'])
def dist(p):
    d = collections.defaultdict(float)
    for t in types:
        tot = sum(cnt[(p, t)].values())
        for s, n in cnt[(p, t)].items(): d[s] += n / tot / len(types)
    return d
a, b = dist('3B'), dist('3C'); js = 0.0
for s in set(a) | set(b):
    pa, pb = a.get(s, 0), b.get(s, 0); m = (pa + pb) / 2
    if pa: js += 0.5 * pa * math.log2(pa / m)
    if pb: js += 0.5 * pb * math.log2(pb / m)
out = {'status': 'Reviewer check, not a package result', 'equal_type_js_bits_3B_vs_3C': round(js, 6),
       'faces_by_period_and_type': {f'{k[0]}|{k[1]}': v for k, v in sorted(faces.items())},
       'families_by_period_and_type': {f'{k[0]}|{k[1]}': len(v) for k, v in sorted(fams.items())},
       'known_tokens': {p: sum(sum(cnt[(p, t)].values()) for t in types) for p in ('3B', '3C')},
       'package_value': 0.190483}
Path(__file__).with_name('independent_js_check.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps(out, indent=2))
