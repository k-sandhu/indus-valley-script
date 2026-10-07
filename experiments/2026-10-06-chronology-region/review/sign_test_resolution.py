"""Reviewer check: does 'no sign passes BH .05' depend on the 499-permutation budget?

Re-runs the package's `analyze.permutation` (unchanged) with more permutations and applies the
package's own Benjamini-Hochberg correction jointly across all sign tests of each question.
Aggregates only (sign codes, effects, p, q); writes review/sign_test_resolution_seed{seed}.json.

Usage: python -B .../sign_test_resolution.py TIME_P REGION_P SEED
"""
import sys, os, json, itertools, time
from pathlib import Path
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
import numpy as np
import analyze as base

time_p, region_p, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
c = base.Corpus(); rng = np.random.default_rng(seed)
out = {'status': 'Reviewer check, not a package result', 'seed': seed}

def summarize(theme, signs, perms):
    ps = [s['p'] for s in signs]; qs = base.bh(ps)
    for s, q in zip(signs, qs): s['bh_q'] = q
    floor = 1 / (perms + 1)
    passing = [s for s in signs if s['bh_q'] < .05]
    return {'theme': theme, 'permutations': perms, 'p_floor': floor, 'sign_tests': len(signs), 'tests_at_floor': sum(abs(p - floor) < 1e-12 for p in ps),
            'min_p': min(ps), 'min_bh_q': min(qs), 'tests_passing_bh_05': len(passing),
            'passing': [{'comparison': s['comparison'], 'sign': s['sign'], 'known_tokens': s['known_tokens'], 'type_adjusted_b_minus_a': s['type_adjusted_b_minus_a'], 'p': s['p'], 'bh_q': s['bh_q']} for s in passing]}

har = c.all[(c.site == 'Harappa') & (c.known > 0)]
signs = []
for a, b in [('2', '3B'), ('2', '3C'), ('3B', '3C')]:
    aa = har[c.major[har] == a]; bb = har[c.major[har] == b]
    res, sig = base.permutation(c, aa, bb, f'{a}__{b}', rng, time_p, 2, False)
    signs.extend(sig); print('time', a, b, res.get('status'), len(sig), flush=True)
out['time'] = summarize('time', signs, time_p); print({k: v for k, v in out['time'].items() if k != 'passing'}, flush=True)

ids = c.all[np.isin(c.region, base.CORE) & (c.known > 0)]
selected = [r for r in base.CORE if len(set(c.pid[c.all[(c.region == r) & (c.known > 0)]])) >= 30]
signs = []
for a, b in itertools.combinations(selected, 2):
    aa = ids[c.region[ids] == a]; bb = ids[c.region[ids] == b]
    res, sig = base.permutation(c, aa, bb, f'{a}__{b}', rng, region_p, 2, False)
    signs.extend(sig); print('region', a, b, len(sig), flush=True)
out['region'] = summarize('region', signs, region_p); print({k: v for k, v in out['region'].items() if k != 'passing'}, flush=True)
Path(__file__).with_name(f'sign_test_resolution_seed{seed}.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print('written', flush=True)
