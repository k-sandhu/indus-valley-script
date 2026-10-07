"""Reviewer exploration: Harappa period labels, site names, family label consistency.
Imports the package analyzer unchanged (read-only use). Prints aggregates only."""
import sys, os, collections, json
from pathlib import Path
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
import analyze as base
import numpy as np

c = base.Corpus()
rows = c.rows

# 1. site names containing 'Harappa'
print('SITE NAMES containing "arappa":', collections.Counter(r['site'] for r in rows if 'arappa' in r['site'].lower()))
# 2. all-site time labels outside Harappa
tl = collections.Counter((r['site'], r['metadata'].get('time', '-')) for r in rows if r['site'] != 'Harappa' and r['metadata'].get('time', '-') not in ('-', '', None))
print('NON-HARAPPA time labels by site (top 25):')
for k, v in tl.most_common(25): print('  ', k, v)
sites_with_time = collections.Counter(r['site'] for r in rows if r['site'] != 'Harappa' and r['metadata'].get('time', '-') not in ('-', '', None))
print('sites with time labels outside Harappa:', dict(sites_with_time))
# 3. all distinct time labels at Harappa
print('HARAPPA labels:', collections.Counter(r['metadata'].get('time', '-') for r in rows if r['site'] == 'Harappa'))
# 4. unrecognized labels (non-empty but mapping to [])
unrec = collections.Counter(r['metadata'].get('time') for r in rows if r['site'] == 'Harappa' and r['metadata'].get('time') not in (None, '-', '') and not r['admissible'])
print('UNRECOGNIZED Harappa labels:', dict(unrec))
# 5. family-level label consistency within Harappa physical families
fam_sets = collections.defaultdict(list)
for i, r in enumerate(rows):
    if r['site'] == 'Harappa':
        fam_sets[int(c.pid[i])].append(tuple(r['admissible']))
n_multi_face = sum(len(v) > 1 for v in fam_sets.values())
distinct = {g: set(v) for g, v in fam_sets.items() if len(set(v)) > 1}
print('Harappa families:', len(fam_sets), 'multi-face:', n_multi_face, 'with >1 distinct admissible set among faces:', len(distinct))
kinds = collections.Counter(tuple(sorted(s)) for s in distinct.values())
for k, v in kinds.most_common(): print('   ', k, v)
inter_empty = 0; inter_single_from_mixed = 0; union_interval_but_intersection_single = 0
for g, v in fam_sets.items():
    sets = [set(s) for s in v if s]
    if not sets: continue
    u = set().union(*sets); it = set.intersection(*sets)
    if not it: inter_empty += 1
    if len(u) > 1 and len(it) == 1: union_interval_but_intersection_single += 1
print('families with empty intersection:', inter_empty, '; union is interval but intersection is a single period:', union_interval_but_intersection_single)
# 6. per-period family counts under both rules
def label_union(g):
    s = set().union(*[set(x) for x in fam_sets[g]]); return s
period_union = collections.Counter()
period_inter = collections.Counter()
for g in fam_sets:
    sets = [set(s) for s in fam_sets[g] if s]
    if not sets: period_union['undated'] += 1; period_inter['undated'] += 1; continue
    u = set().union(*sets); it = set.intersection(*sets)
    period_union[sorted(u)[0] if len(u) == 1 else 'interval'] += 1
    period_inter[sorted(it)[0] if len(it) == 1 else ('interval' if it else 'conflict')] += 1
print('families by period (union rule, as in post-launch):', dict(period_union))
print('families by period (intersection rule, as in original interval_sensitivity):', dict(period_inter))

# 7. label-origin table for Harappa faces: export time label, period field, phase field class
import csv
tab = collections.Counter()
for i, r in enumerate(rows):
    if r['site'] != 'Harappa': continue
    ph = r['metadata'].get('phase', '').strip()
    tab[(r['metadata'].get('time', '-'), r['metadata'].get('period', '-'), 'Stratum' if 'Stratum' in ph else (ph or '-'))] += 1
with open(Path(__file__).with_name('harappa_label_origin.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(['export_time_label', 'export_period_field', 'export_phase_field_(Stratum_if_a_stratum_number)', 'harappa_faces'])
    for k, v in sorted(tab.items()): w.writerow([*k, v])
print('wrote harappa_label_origin.csv with', len(tab), 'rows')
