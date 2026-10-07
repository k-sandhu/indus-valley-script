"""Reviewer check: Monte Carlo stability of the headline permutation p-values.

The package uses 499 label permutations, so a p-value near .02 carries a Monte Carlo
standard error of about .006 and Holm-adjusted values near .05 can change side. This script
re-runs the package's own `analyze.permutation` (unchanged, imported) with many more
permutations and new seeds for (a) the two Harappa time comparisons that form the
Holm family and (b) the six regional pairs under the physical-component reference.
It writes aggregates only to review/permutation_stability.json.

Usage: python -B .../permutation_stability.py TIME_P REGION_P SEED
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
c = base.Corpus()
rng = np.random.default_rng(seed)
out = {'status': 'Reviewer check, not a package result', 'seed': seed, 'time_permutations': time_p, 'region_permutations': region_p, 'time': [], 'region': []}

har = c.all[(c.site == 'Harappa') & (c.known > 0)]
def sel_time(p): return har[c.major[har] == p]
t0 = time.time()
for a, b, closure in [('2', '3C', False), ('3B', '3C', False), ('3B', '3C', True), ('2', '3B', False)]:
    res, _ = base.permutation(c, sel_time(a), sel_time(b), f'{a}__{b}', rng, time_p, 2, closure)
    row = {'comparison': f'{a}__{b}', 'unit': res['unit'], 'status': res.get('status'), 'effect_js_bits': res.get('effect_js_bits'), 'p': res.get('p'), 'null_js_mean': res.get('null_js_mean'), 'components': res.get('components'), 'permutations': res.get('permutations')}
    out['time'].append(row); print(row, flush=True)
phys = [r for r in out['time'] if r['unit'] == 'physical_component' and r['p'] is not None]
for r, q in zip(phys, base.holm([r['p'] for r in phys])): r['holm_p'] = q
txt = [r for r in out['time'] if r['unit'] == 'full_text_closure' and r['p'] is not None]
for r, q in zip(txt, base.holm([r['p'] for r in txt])): r['holm_p'] = q
print('time block done in %.0f s' % (time.time() - t0), flush=True)

ids = c.all[np.isin(c.region, base.CORE) & (c.known > 0)]
selected = [r for r in base.CORE if len(set(c.pid[c.all[(c.region == r) & (c.known > 0)]])) >= 30]
for a, b in itertools.combinations(selected, 2):
    aa = ids[c.region[ids] == a]; bb = ids[c.region[ids] == b]
    t1 = time.time()
    res, _ = base.permutation(c, aa, bb, f'{a}__{b}', rng, region_p, 2, False)
    row = {'comparison': f'{a}__{b}', 'unit': res['unit'], 'effect_js_bits': res.get('effect_js_bits'), 'p': res.get('p'), 'null_js_mean': res.get('null_js_mean'), 'components': res.get('components'), 'permutations': res.get('permutations'), 'seconds': round(time.time() - t1, 1)}
    out['region'].append(row); print(row, flush=True)
for r, q in zip(out['region'], base.holm([r['p'] for r in out['region']])): r['holm_p'] = q
Path(__file__).with_name(f'permutation_stability_seed{seed}.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print('written', flush=True)
