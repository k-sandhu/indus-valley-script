"""Audit acquisition histories and summarize paired system-level outcomes."""
from __future__ import annotations
from collections import defaultdict
import csv
import hashlib
import inspect
from itertools import permutations
import json
import math
from pathlib import Path
import types
import numpy as np
from scipy.special import gammaln

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'experiments/2026-10-02-six-hour/active-identities'

def h(prob):
    positive=prob[prob>0]
    return float(-(positive*np.log2(positive)).sum())

def independent_scores(observed,reference,maps):
    start,pairs,_=observed
    rs,rp,_=reference
    inverse=np.argsort(maps,axis=1)
    moved_start=start[inverse]
    moved_pairs=pairs[inverse[:,:,None],inverse[:,None,:]]
    prior_start=rs+1
    prior_pairs=rp+1
    value=gammaln(prior_start.sum())-gammaln(prior_start.sum()+start.sum())
    value=value+(gammaln(prior_start+moved_start)-gammaln(prior_start)).sum(axis=1)
    value=value+(gammaln(prior_pairs.sum(axis=1))-gammaln(prior_pairs.sum(axis=1)+moved_pairs.sum(axis=2))).sum(axis=1)
    value=value+(gammaln(prior_pairs+moved_pairs)-gammaln(prior_pairs)).sum(axis=(1,2))
    return value/math.log(2)

def main():
    output=BASE/'review'
    if output.exists():
        raise RuntimeError('Use a fresh review endpoint.')
    result=json.loads((BASE/'main/results.json').read_text(encoding='utf-8'))
    mod=types.ModuleType('active_frozen')
    mod.__file__=str(ROOT/'src/six_hour/active_identities.py')
    exec(compile((BASE/'main/code_snapshot.py').read_text(encoding='utf-8'),mod.__file__,'exec'),mod.__dict__)
    histories=defaultdict(list)
    for row in result['records']:
        key=tuple(row[k] for k in ['family','seed','domain_shift','reference_texts','training_texts','policy'])
        histories[key].append(row)
    summary=[]
    all_observations_ok=True
    monotone=True
    for key,rows in histories.items():
        rows.sort(key=lambda r:r['observed_identities'])
        if [r['observed_identities'] for r in rows]!=list(range(9)):
            raise AssertionError('Prefix coverage')
        correct=[r['exact_mapping_recovered'] for r in rows]
        monotone &= all(not correct[i] or correct[i+1] for i in range(8))
        for row in rows:
            k=row['observed_identities']
            all_observations_ok &= row['compatible_maps']==math.factorial(8-k)
            all_observations_ok &= len(row['revealed'])==k and len({a for a,b in row['revealed']})==k
            all_observations_ok &= all(row['true_map'][a]==b and row['best_map'][a]==b for a,b in row['revealed'])
            all_observations_ok &= (row['best_map']==row['true_map'])==row['exact_mapping_recovered']
            if k<8:
                all_observations_ok &= row['next_query'] not in [a for a,b in row['revealed']]
                all_observations_ok &= rows[k+1]['revealed']==row['revealed']+[[row['next_query'],row['true_map'][row['next_query']]]]
        first=next(r for r in rows if r['exact_mapping_recovered'])
        stop=next(r for r in rows if r['best_map_mass']>=.95)
        summary.append(dict(zip(['family','seed','domain_shift','reference_texts','training_texts','policy'],key),
              first_correct_prefix=first['observed_identities'],confidence_stop_prefix=stop['observed_identities'],
              wrong_confidence_stop=not stop['exact_mapping_recovered'],wrong_stop_at_zero=(not stop['exact_mapping_recovered'] and stop['observed_identities']==0)))
    conditions=defaultdict(list)
    for row in summary:
        conditions[tuple(row[k] for k in ['family','domain_shift','reference_texts','training_texts','policy'])].append(row)
    table=[]
    for key,rows in sorted(conditions.items()):
        table.append(dict(zip(['family','domain_shift','reference_texts','training_texts','policy'],key),
             systems=len(rows),mean_queries=float(np.mean([r['first_correct_prefix'] for r in rows])),
             wrong_confidence_stops=sum(r['wrong_confidence_stop'] for r in rows),
             wrong_stops_without_observation=sum(r['wrong_stop_at_zero'] for r in rows)))
    # Bootstrap paired averages over the four sample-size conditions within each
    # generated system. These 24 system averages are the resampling units.
    comparisons=[]
    rng=np.random.default_rng(493001)
    pooled=defaultdict(dict)
    for row in summary:
        key=(row['family'],row['domain_shift'],row['seed'],row['policy'])
        pooled.setdefault(key,[]).append(row)
    for family in ['transition','administrative_form']:
        for shift in [0,.35,.7]:
            seeds=sorted({r['seed'] for r in summary if r['family']==family})
            for comparator in ['random','frequency']:
                query_delta=[];error_delta=[]
                for seed in seeds:
                    active=pooled[family,shift,seed,'entropy'];control=pooled[family,shift,seed,comparator]
                    query_delta.append(np.mean([r['first_correct_prefix'] for r in active])-np.mean([r['first_correct_prefix'] for r in control]))
                    error_delta.append(np.mean([r['wrong_confidence_stop'] for r in active])-np.mean([r['wrong_confidence_stop'] for r in control]))
                picks=rng.integers(0,len(seeds),size=(20000,len(seeds)))
                q=np.asarray(query_delta);e=np.asarray(error_delta)
                comparisons.append({'family':family,'domain_shift':shift,'comparison':'entropy_minus_'+comparator,
                    'independent_systems':len(seeds),'mean_query_difference':float(q.mean()),
                    'query_interval_95':np.quantile(q[picks].mean(axis=1),[.025,.975]).tolist(),
                    'mean_wrong_stop_difference':float(e.mean()),
                    'wrong_stop_interval_95':np.quantile(e[picks].mean(axis=1),[.025,.975]).tolist()})
    maps=np.asarray(list(permutations(range(8))),dtype=np.int8)
    score_error=0.;mass_error=0.;replayed=0;query_ok=True;best_ok=True
    # Replay every policy for one system in each of the 24 source conditions.
    for family in ['transition','administrative_form']:
        seed=min(r['seed'] for r in summary if r['family']==family)
        system=mod.module.generator.system(seed,family)
        reference_texts=mod.module.generator.sample(system,400,seed+1)
        encoding=np.random.default_rng(seed+4).permutation(8)
        for shift in [0,.35,.7]:
            training=mod.module.generator.encode(mod.module.generator.sample(system,160,seed+2,shift),encoding)
            for ref_n in [40,400]:
                reference=mod.module.generator.counts(reference_texts[:ref_n])
                for n in [40,160]:
                    counts=mod.module.generator.counts(training[:n])
                    scores=independent_scores(counts,reference,maps)
                    score_error=max(score_error,float(np.max(np.abs(scores-mod.module.integrated_score(counts,reference,maps)))))
                    for policy in ['random','entropy','frequency']:
                        rng_policy=np.random.default_rng(seed+17+ref_n+n+int(shift*100))
                        for row in histories[family,seed,shift,ref_n,n,policy]:
                            mask=np.ones(len(maps),dtype=bool)
                            for a,b in row['revealed']:
                                mask &= maps[:,a]==b
                            compatible=maps[mask];current=scores[mask]
                            prob=np.exp2(current-current.max());prob/=prob.sum()
                            best_ok &= compatible[np.argmax(prob)].tolist()==row['best_map']
                            mass_error=max(mass_error,abs(float(prob.max())-row['best_map_mass']))
                            remaining=[c for c in range(8) if c not in [a for a,b in row['revealed']]]
                            if remaining:
                                if policy=='random': query=int(rng_policy.choice(remaining))
                                elif policy=='frequency': query=min(remaining,key=lambda c:(-counts[2][c],c))
                                else:
                                    ent={c:h(np.bincount(compatible[:,c],weights=prob,minlength=8)) for c in remaining}
                                    query=min(remaining,key=lambda c:(-ent[c],c))
                                query_ok &= query==row['next_query']
                            replayed+=1
    checks={'prefix_records_15552':len(result['records'])==15552,'histories_1728':len(histories)==1728,
        'conditions_72':len(conditions)==72,'each_condition_24_systems':all(len(v)==24 for v in conditions.values()),
        'observation_histories_and_map_counts_match':bool(all_observations_ok),
        'correct_selection_monotone_under_fixed_score_restriction':bool(monotone),
        'independent_reindexed_likelihood_matches':score_error<1e-8,
        'selected_maps_replayed':bool(best_ok),'queries_replayed':bool(query_ok),'masses_replayed':mass_error<1e-9,
        'query_signature_has_no_truth_or_oracle':not any(k in inspect.signature(mod.choose_query).parameters for k in ['truth','oracle','answers']),
        'program_hash_matches':hashlib.sha256((BASE/'main/code_snapshot.py').read_bytes()).hexdigest()==result['code_sha256'],
        'protocol_hash_matches':hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest()==result['protocol_sha256']}
    if not all(checks.values()):
        raise AssertionError(checks)
    output.mkdir()
    for filename,rows in [('conditions.csv',table),('histories.csv',summary)]:
        with (output/filename).open('w',encoding='utf-8',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (output/'paired-system-comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n',encoding='utf-8')
    (output/'checks.json').write_text(json.dumps({'checks':checks,'replayed_prefix_records':replayed,
        'max_independent_score_error_bits':score_error,'max_mass_error':mass_error},indent=2)+'\n',encoding='utf-8')
    (output/'review_code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks':checks,'score_error':score_error,'mass_error':mass_error,'replayed':replayed}))

if __name__=='__main__':
    main()
