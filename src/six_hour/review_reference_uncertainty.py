"""Summarize the finite-reference grid and independently check saved rows."""
from __future__ import annotations
import csv
import hashlib
import json
import types
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/reference-uncertainty'

def main():
    output = BASE / 'review'
    if output.exists():
        raise RuntimeError('Use a fresh review endpoint.')
    result = json.loads((BASE/'main/results.json').read_text(encoding='utf-8'))
    # The saved program locates its helper relative to its original src path.
    # Execute the frozen bytes with that path context without editing the snapshot.
    module = types.ModuleType('reference_frozen')
    module.__file__ = str(ROOT/'src/six_hour/reference_uncertainty.py')
    snapshot = (BASE/'main/code_snapshot.py').read_text(encoding='utf-8')
    exec(compile(snapshot,module.__file__,'exec'),module.__dict__)
    rows = result['trials']
    keys = ['family','domain_shift','reference_texts','training_texts','anchor_condition','model']
    grouped = defaultdict(list)
    lookup = {}
    for row in rows:
        grouped[tuple(row[k] for k in keys)].append(row)
        unit = tuple(row[k] for k in ['family','seed','domain_shift','reference_texts','training_texts','model','anchor_condition'])
        if unit in lookup:
            raise AssertionError('Duplicate trial')
        lookup[unit] = row
    summaries = []
    paired = []
    failures = []
    for key, group in sorted(grouped.items()):
        summaries.append(dict(zip(keys,key), systems=len(group),
            exact_recoveries=sum(r['exact_mapping_recovered'] for r in group),
            wrong_at_mass_95=sum(not r['exact_mapping_recovered'] and r['best_map_mass']>=.95 for r in group),
            mean_symbol_accuracy=float(np.mean([r['symbol_mapping_accuracy'] for r in group])),
            mean_heldout_bits=float(np.mean([r['heldout_bits_per_sign'] for r in group]))))
    for row in rows:
        if not row['exact_mapping_recovered'] and row['best_map_mass'] >= .95:
            failures.append(row)
        if row['anchor_condition'] == 'one_correct_one_wrong':
            base = tuple(row[k] for k in ['family','seed','domain_shift','reference_texts','training_texts','model'])
            free = lookup[base+('none',)]
            good = lookup[base+('two_correct',)]
            paired.append(dict(zip(['family','seed','domain_shift','reference_texts','training_texts','model'],base),
                wrong_minus_free_bits=row['heldout_bits_per_sign']-free['heldout_bits_per_sign'],
                wrong_minus_correct_bits=row['heldout_bits_per_sign']-good['heldout_bits_per_sign'],
                wrong_map_mass=row['best_map_mass'],free_exact=free['exact_mapping_recovered'],correct_exact=good['exact_mapping_recovered']))
    identity_ok = all(sorted(r['best_map'])==list(range(8)) and sorted(r['true_map'])==list(range(8)) for r in rows)
    anchors_ok = all(all(r['best_map'][a]==b for a,b in r['anchor_pairs']) for r in rows)
    truth_ok = all(r['exact_mapping_recovered']==(r['best_map']==r['true_map']) and
                   r['truth_permitted']==(r['anchor_condition']!='one_correct_one_wrong') for r in rows)
    accuracy_ok = all(abs(r['symbol_mapping_accuracy']-np.mean(np.array(r['best_map'])==r['true_map']))<1e-15 for r in rows)
    hash_ok = hashlib.sha256((BASE/'main/code_snapshot.py').read_bytes()).hexdigest()==result['code_sha256']
    protocol_ok = hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest()==result['protocol_sha256']
    generator_ok = hashlib.sha256(module.FROZEN.read_bytes()).hexdigest()==result['generator_sha256']
    # Independent sequential prediction regenerates one row from each of the
    # 216 conditions. It checks held-out scores without the vectorized gamma implementation.
    error = 0.0
    for group in grouped.values():
        row = group[0]
        system = module.generator.system(row['seed'],row['family'])
        reference_texts = module.generator.sample(system,4000,row['seed']+1)[:row['reference_texts']]
        rng = np.random.default_rng(row['seed']+4)
        encoding = rng.permutation(8)
        training = module.generator.encode(module.generator.sample(system,640,row['seed']+2,row['domain_shift']),encoding)[:row['training_texts']]
        test = module.generator.encode(module.generator.sample(system,400,row['seed']+3,row['domain_shift']),encoding)
        reference = module.generator.counts(reference_texts)
        mapping = np.asarray(row['best_map'])
        if row['model']=='integrated':
            held = module.direct_predictive(training+test,reference,mapping)-module.direct_predictive(training,reference,mapping)
        else:
            starts,pairs,_ = reference
            held = sum(np.log2((starts[mapping[t[0]]]+1)/(starts.sum()+8))+
                       sum(np.log2((pairs[mapping[a],mapping[b]]+1)/(pairs[mapping[a]].sum()+8)) for a,b in zip(t,t[1:])) for t in test)
        error = max(error,abs(-held/sum(map(len,test))-row['heldout_bits_per_sign']))
    checks = {'trial_grid_is_2592':len(rows)==2592,'condition_count_is_216':len(grouped)==216,
              'each_condition_has_12_systems':all(len(v)==12 for v in grouped.values()),
              'maps_are_bijections':identity_ok,'asserted_anchors_respected':anchors_ok,
              'truth_allowed_and_recovery_match':truth_ok,'symbol_accuracy_matches_maps':accuracy_ok,
              'frozen_code_hash_matches':hash_ok,'protocol_hash_matches':protocol_ok,'generator_hash_matches':generator_ok,
              'independent_heldout_scores_match':error<1e-10}
    if not all(checks.values()):
        raise AssertionError(checks)
    output.mkdir()
    for filename,records in [('conditions.csv',summaries),('wrong-anchor-heldout.csv',paired)]:
        with (output/filename).open('w',encoding='utf-8',newline='') as handle:
            writer = csv.DictWriter(handle,fieldnames=list(records[0]))
            writer.writeheader(); writer.writerows(records)
    (output/'confident-failures.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
    (output/'checks.json').write_text(json.dumps({'checks':checks,'max_independent_heldout_error':error,
        'independently_scored_conditions':len(grouped),'wrong_anchor_pairs':len(paired),'confident_wrong_trials':len(failures)},indent=2)+'\n',encoding='utf-8')
    (output/'review_code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks':checks,'max_error':error,'confident_wrong':len(failures)}))

if __name__=='__main__':
    main()
