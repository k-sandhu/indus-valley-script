"""Reviewer's independent recomputation of the package's observed counts and exact expectations.

Uses only coder-a.json and run-v1 outputs; does not import the package code.
  1. Observed match counts (direct pair loop) against run-v1/observed.json.
  2. Exact finite-subset means (hypergeometric) against run-v1/subsampling.json.
  3. Exact collision means sum_d p(d)(1-(1-p(d))^n) against run-v1/synthetic-null.json (surrogate and fixed query).
  4. Complexity band counts against run-v1/manifest.json.
Prints one line per check family and exits non-zero on any mismatch.
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-resemblance-baseline'
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'

INT = 'segments curved loops L T X Y other terminals components dots'.split()
RULES = {'R1': ['segments', 'loops'], 'R2': INT, 'R3': INT + ['symmetry', 'orientation']}

rows = [r for r in json.loads((RAW / 'coder-a.json').read_text(encoding='utf-8')) if r.get('readable', True)]
tam = [r for r in rows if r['inventory'] == 'tamil']
inv = {k: [r for r in rows if r['inventory'] == k] for k in ('indus', 'ogham', 'tifinagh')}
sig = lambda r, rule: tuple(r[f] for f in RULES[rule])

failures = 0

# 1 observed
obs = json.loads((PKG / 'run-v1/observed.json').read_text(encoding='utf-8'))
n1 = 0
for o in obs:
    refs = inv[o['inventory']]
    hits = sum(any(sig(q, o['rule']) == sig(r, o['rule']) for r in refs) for q in tam)
    if hits != o['matched']:
        failures += 1
        print('observed mismatch', o['inventory'], o['rule'], hits, o['matched'])
    n1 += 1
print('observed counts checked:', n1)

# 2 exact subsampling means
sub = json.loads((PKG / 'run-v1/subsampling.json').read_text(encoding='utf-8'))
for s in sub:
    refs = inv[s['inventory']]
    N, n = len(refs), s['n']
    cnt = Counter(sig(r, s['rule']) for r in refs)
    tot = 0.0
    for q in tam:
        c = cnt.get(sig(q, s['rule']), 0)
        tot += 0.0 if c == 0 else (1.0 if N - c < n else 1 - math.comb(N - c, n) / math.comb(N, n))
    if abs(tot / 42 - s['exact_mean']) > 1e-12:
        failures += 1
        print('subsampling mismatch', s['inventory'], s['rule'], n)
print('finite-subset exact means checked:', len(sub))

# 3 collision means
syn = json.loads((PKG / 'run-v1/synthetic-null.json').read_text(encoding='utf-8'))
for s in syn:
    refs = inv[s['inventory']]
    cnt = Counter(sig(r, s['rule']) for r in refs)
    p = {k: v / len(refs) for k, v in cnt.items()}
    n = s['n']
    surrogate = sum(v * (1 - (1 - v) ** n) for v in p.values())
    fixed = sum(1 - (1 - p.get(sig(q, s['rule']), 0)) ** n for q in tam) / 42
    if abs(surrogate - s['surrogate_query']['exact_mean']) > 1e-12 or abs(fixed - s['fixed_tamil_query']['exact_mean']) > 1e-12:
        failures += 1
        print('collision mismatch', s['inventory'], s['rule'], n)
print('collision exact means checked:', len(syn))

# 4 bands
band = lambda r: '1-3' if r['segments'] <= 3 else ('4-6' if r['segments'] <= 6 else '7+')
man = json.loads((PKG / 'run-v1/manifest.json').read_text(encoding='utf-8'))['counts']
for k, v in {'tamil': tam, **inv}.items():
    got = dict(Counter(band(r) for r in v))
    if got != man[k]['complexity_counts'] or len(v) != man[k]['coded'] or sum(r['uncertain'] for r in v) != man[k]['uncertain']:
        failures += 1
        print('manifest mismatch', k, got)
print('manifest counts checked: 4 inventories')
print('failures:', failures)
sys.exit(1 if failures else 0)
