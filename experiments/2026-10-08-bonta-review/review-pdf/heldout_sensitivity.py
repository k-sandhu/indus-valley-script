"""Reviewer sensitivity: a partial held-out split for the early values, from the paper's derivation tables.

Objects whose MH or ICIT label appears in the inventory rows from PDF pp. 39-77 (the derivation narrative and
Tables 7-17) are treated as derivation objects. Early values are those fixed or proposed by p. 76 (PU, PATI, ma,
pala, dhana, tra, mina and the 2014 predicate values). The subset keeps selected readings whose roles are all
early values, with and without derivation objects. This is Exploratory and post-outcome: the paper says the early
values were adopted after repeated confirmation (p. 76), so the later objects were not sealed from the author.
From the repository root:
    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/heldout_sensitivity.py
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lexical_recheck as L

W = ROOT / 'data/raw/2026-10-08-bonta-review/pdf-2026-10-09-v1'
inv = {r['reading_id']: r for r in json.loads((W / 'reading-inventory-v4.json').read_text(encoding='utf-8'))}
sel = json.loads((W / 'lexical-selection-v2.json').read_text(encoding='utf-8'))
deriv = {r['primary_label'] for r in inv.values() if 39 <= r['source_page'] <= 77}
b0 = {int(k): v for k, v in sel['table18_role_variants_slp1'].items()}
init = sel['initial_only_slp1']
EARLY = {5, 47, 6, 17, 18, 19, 36, 29, 50, 51, 52}
NO_DICT = {6, 17, 18, 19, 36, 29, 50, 51, 52}
out = {'status': 'Exploratory (reviewer sensitivity, post-outcome)', 'derivation_object_labels': len(deriv),
       'early_roles': sorted(EARLY)}
pop = [r for r in sel['readings'] if r['basis'].startswith('explicit caption') and len(r['roles']) >= 2]
for name, roles, bundles in (('early values incl. PU and PATI, exact bundles', EARLY, b0),
                             ('early values without PU and PATI, maha and bala removed', NO_DICT,
                              {**b0, 6: ['ma', 'mA'], 17: ['pala', 'pAla']})):
    sub = [r for r in pop if set(r['roles']) <= roles]
    held = [r for r in sub if r['primary_label'] not in deriv]
    res = {'occurrences_all': len(sub), 'occurrences_outside_derivation_objects': len(held)}
    for label, rows in (('all objects', sub), ('outside derivation objects', held)):
        seqs = sorted({tuple(r['roles']) for r in rows})
        res[label] = {ep: (L.run(seqs, bundles, init, ep) if seqs else None) for ep in ('exact', 'normalized')}
        for ep in ('exact', 'normalized'):
            if res[label][ep]:
                res[label][ep].pop('null_histogram', None)
    res['held_out_labels_and_roles'] = sorted({(r['primary_label'], tuple(r['roles'])) for r in held})
    out[name] = res
(Path(__file__).resolve().parent / 'heldout-sensitivity.json').write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
for k, v in out.items():
    if isinstance(v, dict) and 'occurrences_all' in v:
        print(k)
        for lab in ('all objects', 'outside derivation objects'):
            for ep in ('exact', 'normalized'):
                r = v[lab][ep]
                print('  ', lab, ep, None if r is None else (r['observed'], r['sequences'], r['null_mean'], r['tail'], r['matched_sequences']))
