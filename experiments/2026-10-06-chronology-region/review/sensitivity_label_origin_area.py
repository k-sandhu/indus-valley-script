"""Reviewer exploratory sensitivity (not a package result).

Question: how much of the Harappa 3B-versus-3C contrast comes from differences in which
excavation and which labelling scheme supplied the records of each period?

Two label origins exist in the export for Harappa faces:
  * 'harp_label'  : metadata.phase does not mention a Stratum (Period / phase from the HARP catalogue)
  * 'stratum'     : metadata.phase is 'Stratum I..VII' and the period label ('3C-1' ...) is derived from it
and the metadata.area-section field names the excavated mound / trench.

This script re-uses the package's own functions (analyze.Corpus, analyze.effects,
analyze.permutation, post_launch.media_effect) on subsets and writes aggregates only to
review/sensitivity_label_origin_area.json. Seeds are fixed (20261007).
"""
import sys, os, json, collections
from pathlib import Path
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
import numpy as np
import analyze as base
import post_launch as pl

c = base.Corpus()
rng = np.random.default_rng(20261007)

def origin_of_face(i):
    ph = c.rows[i]['metadata'].get('phase', '')
    return 'stratum' if 'Stratum' in ph else 'harp_label'

def mound_of_face(i):
    a = c.rows[i]['metadata'].get('area-section', '')
    if a.startswith('AB'): return 'AB'
    if a.startswith('E'): return 'E'
    if a.startswith('F'): return 'F'
    if a.startswith('J'): return 'J'
    return 'unknown'

out = {'status': 'Reviewer exploratory sensitivity; not part of the package endpoints', 'seed': 20261007}

# ------------------------------------------------------------------ composition of the dated Harappa faces
comp = collections.Counter()
for i, r in enumerate(c.rows):
    if r['site'] == 'Harappa' and r['major'] in ('3B', '3C'):
        comp[(r['major'], origin_of_face(i), mound_of_face(i))] += 1
out['face_composition_by_period_origin_mound'] = [{'period': k[0], 'label_origin': k[1], 'mound': k[2], 'faces': v} for k, v in sorted(comp.items())]
orig = collections.Counter((r['major'], origin_of_face(i)) for i, r in enumerate(c.rows) if r['site'] == 'Harappa' and r['major'] in ('3B', '3C'))
out['faces_by_period_and_label_origin'] = {f'{k[0]}|{k[1]}': v for k, v in sorted(orig.items())}
mnd = collections.Counter((r['major'], mound_of_face(i)) for i, r in enumerate(c.rows) if r['site'] == 'Harappa' and r['major'] in ('3B', '3C'))
out['faces_by_period_and_mound'] = {f'{k[0]}|{k[1]}': v for k, v in sorted(mnd.items())}
# exact type mix by origin
tm = collections.Counter((r['major'], origin_of_face(i), c.type[i]) for i, r in enumerate(c.rows) if r['site'] == 'Harappa' and r['major'] in ('3B', '3C'))
out['type_mix'] = [{'period': k[0], 'label_origin': k[1], 'type': k[2], 'faces': v} for k, v in sorted(tm.items())]
# CISI number ranges (identify HARP excavation numbers vs earlier catalogue numbers)
import re, statistics
def hnum(i):
    m = re.fullmatch(r'H-?(\d+)[A-Za-z]?', str(c.rows[i]['source_cisi']).strip()); return int(m[1]) if m else None
rng_rows = []
for p in ('3B', '3C'):
    for o in ('harp_label', 'stratum'):
        nums = [hnum(i) for i, r in enumerate(c.rows) if r['site'] == 'Harappa' and r['major'] == p and origin_of_face(i) == o]
        nums = [n for n in nums if n is not None]
        rng_rows.append({'period': p, 'label_origin': o, 'faces_with_H_number': len(nums), 'min': min(nums) if nums else None, 'median': statistics.median(nums) if nums else None, 'max': max(nums) if nums else None})
out['cisi_H_number_ranges'] = rng_rows

# ------------------------------------------------------------------ media diversity on subsets (same code as the package)
units = pl.harappa_units(c)
for u in units:
    faces = u['indices']
    origins = {origin_of_face(i) for i in faces}
    u['origin'] = 'stratum' if 'stratum' in origins else 'harp_label'
    u['mixed_origin'] = len(origins) > 1
    mounds = {mound_of_face(i) for i in faces}
    u['mound'] = sorted(mounds)[0] if len(mounds) == 1 else 'mixed'
out['families_with_mixed_label_origin'] = sum(u['mixed_origin'] for u in units)
out['families_with_mixed_mound'] = sum(u['mound'] == 'mixed' for u in units)

def media_for(label, keep):
    a = [u for u in units if u['period'] == '3B' and u['type'] is not None and keep(u)]
    b = [u for u in units if u['period'] == '3C' and u['type'] is not None and keep(u)]
    if not a or not b: return {'subset': label, 'status': 'empty arm', 'families_3B': len(a), 'families_3C': len(b)}
    m = min(len(a), len(b))
    eff = pl.media_effect(a, b, m=m)
    boots = []
    for _ in range(999):
        ba = [a[int(i)] for i in rng.integers(0, len(a), len(a))]; bb = [b[int(i)] for i in rng.integers(0, len(b), len(b))]
        boots.append(pl.media_effect(ba, bb, m=m))
    boots = np.asarray(boots)
    return {'subset': label, 'families_3B': len(a), 'families_3C': len(b), 'common_budget': m,
            'types_3B': len({u['type'] for u in a}), 'types_3C': len({u['type'] for u in b}),
            'type_counts_3B': dict(collections.Counter(u['type'] for u in a)), 'type_counts_3C': dict(collections.Counter(u['type'] for u in b)),
            'rarefied_richness_difference': float(eff[2]), 'rarefied_richness_interval95': [float(x) for x in np.quantile(boots[:, 2], [.025, .975])],
            'rarefied_shannon_difference_bits': float(eff[3]), 'rarefied_shannon_interval95': [float(x) for x in np.quantile(boots[:, 3], [.025, .975])]}

out['media_subsets'] = [
    media_for('all unambiguous families (package analysis)', lambda u: True),
    media_for('HARP-labelled families only (no Stratum in phase)', lambda u: u['origin'] == 'harp_label'),
    media_for('Stratum-labelled families only', lambda u: u['origin'] == 'stratum'),
    media_for('Mound E families only', lambda u: u['mound'] == 'E'),
    media_for('Mound F families only', lambda u: u['mound'] == 'F'),
    media_for('Mound AB families only', lambda u: u['mound'] == 'AB'),
    media_for('HARP-labelled and Mound E only', lambda u: u['origin'] == 'harp_label' and u['mound'] == 'E'),
]

# ------------------------------------------------------------------ frequency comparison on subsets (same code as the package)
def freq_for(label, keep_face):
    har = c.all[(c.site == 'Harappa') & (c.known > 0)]
    a = np.array([i for i in har if c.major[i] == '3B' and keep_face(i)], int)
    b = np.array([i for i in har if c.major[i] == '3C' and keep_face(i)], int)
    ts = base.common_types(c, a, b)
    row = {'subset': label, 'faces_3B': len(a), 'faces_3C': len(b), 'families_3B': len(set(c.pid[a])), 'families_3C': len(set(c.pid[b])), 'common_types': ts}
    if not ts: row['status'] = 'no common type with >=10 families on both sides'; return row
    aa = a[np.isin(c.type[a], ts)]; bb = b[np.isin(c.type[b], ts)]
    ev, _ = base.effects(c, aa, bb, ts)
    row.update(faces_in_common_support=(len(aa), len(bb)), equal_type_js_bits=float(ev['frequency_js_bits']), mean_length_b_minus_a=float(ev['mean_length_b_minus_a']))
    res, _ = base.permutation(c, a, b, label, rng, 499, 2, False)
    row['family_reference'] = {k: res.get(k) for k in ('status', 'effect_js_bits', 'p', 'components', 'movable_components')}
    return row

out['frequency_subsets'] = [
    freq_for('all unambiguous faces (package analysis, re-run with this script RNG)', lambda i: True),
    freq_for('HARP-labelled faces only', lambda i: origin_of_face(i) == 'harp_label'),
    freq_for('Mound E faces only', lambda i: mound_of_face(i) == 'E'),
    freq_for('Mound F faces only', lambda i: mound_of_face(i) == 'F'),
]

Path(__file__).with_name('sensitivity_label_origin_area.json').write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
print('written')
