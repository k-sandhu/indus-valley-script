"""Review source channels in response coordinates and replay mapping outcomes."""
from collections import defaultdict
import csv
import hashlib
from itertools import combinations, permutations
import json
import math
from pathlib import Path
import types
import numpy as np
from scipy.special import gammaln

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'experiments/2026-10-02-six-hour/correlated-sources'

def scores_reference_coordinates(observed,reference,maps):
    starts,pairs,_=observed;rs,rp,_=reference
    inverse=np.argsort(maps,axis=1)
    ms=starts[inverse];mp=pairs[inverse[:,:,None],inverse[:,None,:]]
    a=rs+1;b=rp+1
    v=gammaln(a.sum())-gammaln(a.sum()+starts.sum())
    v=v+(gammaln(a+ms)-gammaln(a)).sum(axis=1)
    v=v+(gammaln(b.sum(axis=1))-gammaln(b.sum(axis=1)+mp.sum(axis=2))).sum(axis=1)
    return (v+(gammaln(b+mp)-gammaln(b)).sum(axis=(1,2)))/math.log(2)

def source_probability(maps,codes,responses,q):
    # A source transposition is self-inverse. Transform the reported values,
    # rather than every candidate mapping, to enumerate latent states.
    observed=np.asarray(responses)
    probability=(1-q)*np.all(maps[:,codes]==observed,axis=1).astype(float)
    for first,second in combinations(range(8),2):
        changed=observed.copy()
        changed[observed==first]=second;changed[observed==second]=first
        probability+=(q/28)*np.all(maps[:,codes]==changed,axis=1)
    return probability

def summarize(scores,maps,truth):
    finite=np.isfinite(scores)
    if not finite.any():
        return {'compatible_maps':0,'selected_map':None,'selected_map_mass':None,'true_map_mass':0.0,'exact_mapping_recovered':False,'confident_wrong_selection':False}
    selected=int(np.argmax(scores));w=np.exp2(scores-scores[selected]);w/=w.sum()
    correct=maps[selected].tolist()==truth
    ti=np.flatnonzero(np.all(maps==truth,axis=1))[0]
    return {'compatible_maps':int(finite.sum()),'selected_map':maps[selected].tolist(),'selected_map_mass':float(w[selected]),
            'true_map_mass':float(w[ti]),'exact_mapping_recovered':correct,'confident_wrong_selection':bool(not correct and w[selected]>=.95)}

def main():
    out=BASE/'review'
    if out.exists():
        raise RuntimeError('Fresh review required.')
    result=json.loads((BASE/'main/results.json').read_text(encoding='utf-8'))
    mod=types.ModuleType('source_frozen');mod.__file__=str(ROOT/'src/six_hour/correlated_sources.py')
    exec(compile((BASE/'main/code_snapshot.py').read_text(encoding='utf-8'),mod.__file__,'exec'),mod.__dict__)
    maps=np.asarray(list(permutations(range(8))),dtype=np.int8)
    keys=['family','seed','training_texts','domain_shift','source_a_state','second_correct_source','reported_codes','assumed_source_swap_probability','source_a_copies','model']
    saved={tuple(r[k] for k in keys):r for r in result['rows']}
    claims={tuple(c[k] for k in ['family','seed','source_state','reported_codes']):c for c in result['source_claims']}
    assert len(saved)==len(result['rows'])==73728
    invariants=defaultdict(list)
    outcome_fields=['compatible_maps','selected_map','selected_map_mass','true_map_mass','exact_mapping_recovered','confident_wrong_selection']
    all_invariant=True;all_fields=True
    for row in result['rows']:
        if row['model']!='independent_copied':
            invariants[tuple(row[k] for k in keys if k!='source_a_copies')].append({k:row[k] for k in outcome_fields})
        all_fields &= row['compatible_maps']==0 or (row['selected_map_mass']>0 and row['selected_map_mass']<=1 and 0<=row['true_map_mass']<=1)
        all_fields &= row['compatible_maps']==0 or row['confident_wrong_selection']==(not row['exact_mapping_recovered'] and row['selected_map_mass']>=.95)
    all_invariant=all(len(rows)==3 and rows[0]==rows[1]==rows[2] for rows in invariants.values())
    replayed=0;max_score_error=0.;max_mass_error=0.;max_channel_error=0.;all_selected=True;hard_conflicts=True
    for si,system_record in enumerate(result['systems']):
        family=system_record['family'];seed=system_record['seed'];truth=system_record['true_map']
        train_n=40 if si%2==0 else 160;shift=0 if si%3==0 else .35
        system=mod.module.generator.system(seed,family)
        reference=mod.module.generator.counts(mod.module.generator.sample(system,400,seed+1))
        encoding=np.random.default_rng(seed+4).permutation(8)
        training=mod.module.generator.encode(mod.module.generator.sample(system,160,seed+2,shift),encoding)
        observed=mod.module.generator.counts(training[:train_n])
        base=scores_reference_coordinates(observed,reference,maps)
        max_score_error=max(max_score_error,float(np.max(np.abs(base-mod.module.integrated_score(observed,reference,maps)))))
        for state in ['correct','swapped']:
            for n in [1,2,4,8]:
                claim=claims[family,seed,state,n];codes=claim['codes'];a=np.asarray(claim['source_a_responses']);b=np.asarray(claim['source_b_correct_responses'])
                assert b.tolist()==[truth[c] for c in codes]
                for q in [.1,.5]:
                    ap=source_probability(maps,codes,a,q);bp=source_probability(maps,codes,b,q)
                    max_channel_error=max(max_channel_error,float(np.max(np.abs(ap-mod.coupled_probability(maps,codes,a,q)))))
                    al=np.where(maps[:,codes]==a,math.log2(1-q/4),math.log2(q/28)).sum(axis=1)
                    bl=np.where(maps[:,codes]==b,math.log2(1-q/4),math.log2(q/28)).sum(axis=1)
                    for second in [False,True]:
                        hard=np.all(maps[:,codes]==a,axis=1)
                        if second:hard &= np.all(maps[:,codes]==b,axis=1)
                        hard_conflicts &= (not hard.any())==(second and np.any(a!=b))
                        probability=ap*(bp if second else 1)
                        channel_log=np.full(len(maps),-np.inf);valid=probability>0;channel_log[valid]=np.log2(probability[valid])
                        fixed={'hard':np.where(hard,base,-np.inf),'independent_once':base+al+(bl if second else 0),'coupled_source':base+channel_log}
                        for copies in [1,3,10]:
                            candidates={**fixed,'independent_copied':base+copies*al+(bl if second else 0)}
                            for model,score in candidates.items():
                                r=saved[family,seed,train_n,shift,state,second,n,q,copies,model]
                                recomputed=summarize(score,maps,truth)
                                all_selected &= all(r[k]==recomputed[k] for k in ['compatible_maps','selected_map','exact_mapping_recovered','confident_wrong_selection'])
                                for field in ['selected_map_mass','true_map_mass']:
                                    if r[field] is not None:
                                        max_mass_error=max(max_mass_error,abs(r[field]-recomputed[field]))
                                replayed+=1
        print(json.dumps({'systems_reviewed':si+1,'rows_replayed':replayed}),flush=True)
    grouped=defaultdict(list)
    groupkeys=['family','domain_shift','source_a_state','second_correct_source','reported_codes','assumed_source_swap_probability','source_a_copies','model']
    for row in result['rows']:grouped[tuple(row[k] for k in groupkeys)].append(row)
    summaries=[]
    for key,rows in sorted(grouped.items()):
        summaries.append(dict(zip(groupkeys,key),conditions=len(rows),systems=len({r['seed'] for r in rows}),
            exact_recoveries=sum(r['exact_mapping_recovered'] for r in rows),
            confident_wrong_selections=sum(r['confident_wrong_selection'] for r in rows),
            empty_candidate_sets=sum(r['compatible_maps']==0 for r in rows),
            mean_true_map_mass=float(np.mean([r['true_map_mass'] for r in rows]))))
    comparisons=[];rng=np.random.default_rng(6193401)
    for family in ['transition','administrative_form']:
        for shift in [0,.35]:
            for second in [False,True]:
                for n in [2,4,8]:
                    q=.1;seeds=sorted({r['seed'] for r in result['systems'] if r['family']==family})
                    for comparator in ['independent_once','coupled_source']:
                        errors=[];recoveries=[]
                        for seed in seeds:
                            base_rows=[saved[family,seed,t,shift,'swapped',second,n,q,10,'independent_copied'] for t in [40,160]]
                            compare_rows=[saved[family,seed,t,shift,'swapped',second,n,q,10,comparator] for t in [40,160]]
                            errors.append(np.mean([r['confident_wrong_selection'] for r in base_rows])-np.mean([r['confident_wrong_selection'] for r in compare_rows]))
                            recoveries.append(np.mean([r['exact_mapping_recovered'] for r in base_rows])-np.mean([r['exact_mapping_recovered'] for r in compare_rows]))
                        e=np.asarray(errors);a=np.asarray(recoveries);draw=rng.integers(0,len(seeds),size=(20000,len(seeds)))
                        comparisons.append({'family':family,'domain_shift':shift,'second_correct_source':second,'reported_codes':n,'q':q,
                            'comparison':'ten_copied_minus_'+comparator,'systems':len(seeds),
                            'wrong_confidence_difference':float(e.mean()),'wrong_confidence_interval95':np.quantile(e[draw].mean(axis=1),[.025,.975]).tolist(),
                            'recovery_difference':float(a.mean()),'recovery_interval95':np.quantile(a[draw].mean(axis=1),[.025,.975]).tolist()})
    checks={'rows_73728_unique':len(saved)==73728,'systems_48':len(result['systems'])==48,
        'each_summary_48_conditions_24_systems':all(r['conditions']==48 and r['systems']==24 for r in summaries),
        'copied_reports_leave_three_source_once_treatments_unchanged':bool(all_invariant),
        'mass_and_confidence_fields_consistent':bool(all_fields),'hard_conflicts_match_report_disagreement':bool(hard_conflicts),
        'inverse_response_channel_matches':max_channel_error<1e-12,'independent_likelihood_matches':max_score_error<1e-8,
        '18432_replayed_outcomes_match':bool(all_selected) and replayed==18432,'replayed_masses_match':max_mass_error<1e-8,
        'code_hash_matches':hashlib.sha256((BASE/'main/code_snapshot.py').read_bytes()).hexdigest()==result['code_sha256'],
        'protocol_hash_matches':hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest()==result['protocol_sha256']}
    if not all(checks.values()):raise AssertionError(checks)
    out.mkdir();(out/'checks.json').write_text(json.dumps({'checks':checks,'max_score_error_bits':max_score_error,'max_channel_error':max_channel_error,'max_mass_error':max_mass_error},indent=2)+'\n',encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n',encoding='utf-8')
    (out/'paired-system-comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n',encoding='utf-8')
    with (out/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(summaries[0]));writer.writeheader();writer.writerows(summaries)
    (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks_passed':len(checks),'rows_replayed':replayed,'groups':len(summaries),'max_mass_error':max_mass_error}))

if __name__=='__main__':main()
