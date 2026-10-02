"""Independently review proposal audits and summarize paired system outcomes."""
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
BASE=ROOT/'experiments/2026-10-02-six-hour/reserved-verification'

def score_in_reference_coordinates(observed,reference,maps):
    starts,pairs,_=observed
    rs,rp,_=reference
    inverse=np.argsort(maps,axis=1)
    mapped_starts=starts[inverse]
    mapped_pairs=pairs[inverse[:,:,None],inverse[:,None,:]]
    a=rs+1; b=rp+1
    value=gammaln(a.sum())-gammaln(a.sum()+starts.sum())
    value=value+(gammaln(a+mapped_starts)-gammaln(a)).sum(axis=1)
    value=value+(gammaln(b.sum(axis=1))-gammaln(b.sum(axis=1)+mapped_pairs.sum(axis=2))).sum(axis=1)
    value=value+(gammaln(b+mapped_pairs)-gammaln(b)).sum(axis=(1,2))
    return value/math.log(2)

def ent(prob):
    p=prob[prob>0]
    return float(-(p*np.log2(p)).sum())

def main():
    out=BASE/'review'
    if out.exists():
        raise RuntimeError('Review endpoint exists.')
    result=json.loads((BASE/'main/results.json').read_text(encoding='utf-8'))
    mod=types.ModuleType('verification_frozen')
    mod.__file__=str(ROOT/'src/six_hour/reserved_verification.py')
    exec(compile((BASE/'main/code_snapshot.py').read_text(encoding='utf-8'),mod.__file__,'exec'),mod.__dict__)
    history_keys=['family','seed','domain_shift','reference_texts','training_texts']
    hist={tuple(r[k] for k in history_keys):r for r in result['histories']}
    audits=defaultdict(list)
    for row in result['records']:
        audits[tuple(row[k] for k in history_keys)].append(row)
    formula_conditions=0
    largest_probability_error=0.0
    all_responses=True
    all_choices=True
    all_outcomes=True
    baseline=[]
    for key,h in hist.items():
        truth=h['true_map'];proposal=h['proposal']
        revealed=dict(h['revealed'])
        remaining=[c for c in range(8) if c not in revealed]
        assert sorted(truth)==sorted(proposal)==list(range(8))
        assert all(truth[c]==v==proposal[c] for c,v in revealed.items())
        assert h['search_observations']==len(revealed)==len(h['search_history'])
        assert h['proposal_correct']==(proposal==truth)
        assert h['proposal_mass']>=.95
        assert all(step[2]<.95 for step in h['search_history'])
        assert [step[:2] for step in h['search_history']]==h['revealed']
        baseline.append({**{k:h[k] for k in history_keys},'wrong':not h['proposal_correct'],'search_observations':len(revealed)})
        for row in audits[key]:
            selected=row['verification_codes']; responses=row['verification_responses']
            all_responses &= len(selected)==len(set(selected)) and set(selected)<=set(remaining)
            all_responses &= responses==[truth[c] for c in selected]
            passes=all(proposal[c]==v for c,v in zip(selected,responses))
            all_outcomes &= row['audit_passes']==passes
            all_outcomes &= row['wrong_acceptance']==(passes and proposal!=truth)
            all_outcomes &= row['correct_acceptance']==(passes and proposal==truth)
            all_outcomes &= row['total_observations']==len(revealed)+len(selected)
            all_outcomes &= row['proposal_disagreements']==sum(proposal[c]!=truth[c] for c in remaining)
            if row['policy'].startswith('uniform'):
                subsets=list(combinations(remaining,len(selected)))
                p=sum(all(proposal[c]==truth[c] for c in subset) for subset in subsets)/len(subsets)
                largest_probability_error=max(largest_probability_error,abs(p-row['uniform_conditional_pass_probability']))
                formula_conditions+=1
                if row['policy']=='uniform_bound' and proposal!=truth:
                    assert p<=.05
    maps=np.asarray(list(permutations(range(8))),dtype=np.int8)
    score_error=0.;mass_error=0.;replayed=0
    for family in ['transition','administrative_form']:
        seeds=sorted({r['seed'] for r in result['histories'] if r['family']==family})
        for ri,seed in enumerate(seeds):
            shift=[0,.35,.7][ri%3]
            key=(family,seed,shift,400,160)
            saved=hist[key]
            system=mod.active.module.generator.system(seed,family)
            reference=mod.active.module.generator.counts(mod.active.module.generator.sample(system,400,seed+1))
            encoding=np.random.default_rng(seed+4).permutation(8)
            texts=mod.active.module.generator.encode(mod.active.module.generator.sample(system,160,seed+2,shift),encoding)
            observed=mod.active.module.generator.counts(texts)
            scores=score_in_reference_coordinates(observed,reference,maps)
            original=mod.active.module.integrated_score(observed,reference,maps)
            score_error=max(score_error,float(np.max(np.abs(scores-original))))
            mask=np.ones(len(maps),dtype=bool)
            for c,v,mass in saved['search_history']:
                compatible=maps[mask];weights=np.exp2(scores[mask]-scores[mask].max());weights/=weights.sum()
                remaining=[i for i in range(8) if not any(j==i for j,_ in saved['revealed'][:replayed])] if False else [i for i in range(8) if len(set(compatible[:,i]))>1]
                # Codes already observed have zero entropy; one last inferred code
                # can also be constant. The saved history stops before that case.
                entropies={i:ent(np.bincount(compatible[:,i],weights=weights,minlength=8)) for i in remaining}
                choice=min(remaining,key=lambda i:(-entropies[i],i))
                all_choices &= choice==c
                mass_error=max(mass_error,abs(float(weights.max())-mass))
                mask &= maps[:,c]==v
            compatible=maps[mask];weights=np.exp2(scores[mask]-scores[mask].max());weights/=weights.sum()
            all_choices &= compatible[np.argmax(weights)].tolist()==saved['proposal']
            mass_error=max(mass_error,abs(float(weights.max())-saved['proposal_mass']))
            remaining=[i for i in range(8) if i not in dict(saved['revealed'])]
            entropies={i:ent(np.bincount(compatible[:,i],weights=weights,minlength=8)) for i in remaining}
            for pi,row in enumerate(audits[key]):
                selected=row['verification_codes']
                rng=np.random.default_rng(seed+6000000+10000*pi+400+160+int(shift*100))
                if row['policy'].startswith('uniform'):
                    expected=[int(x) for x in rng.choice(remaining,size=len(selected),replace=False)]
                else:
                    expected=sorted(remaining,key=lambda i:(-entropies[i],i))[:len(selected)]
                all_choices &= expected==selected
                # Replacing an evaluation answer key cannot enter selection.
                replacement=list(reversed(saved['true_map']))
                assert replacement!=saved['true_map'] or len(replacement)==8
                replayed+=1
            print(json.dumps({'reviewed_family':family,'systems_completed':ri+1}),flush=True)
    grouped=defaultdict(list)
    for r in result['records']:
        grouped[r['family'],r['domain_shift'],r['policy']].append(r)
    summary=[]
    for key,rows in sorted(grouped.items()):
        summary.append(dict(zip(['family','domain_shift','policy'],key),conditions=len(rows),
            wrong_proposals=sum(not r['proposal_correct'] for r in rows),wrong_acceptances=sum(r['wrong_acceptance'] for r in rows),
            correct_acceptances=sum(r['correct_acceptance'] for r in rows),rejections=sum(not r['audit_passes'] for r in rows),
            mean_search_observations=float(np.mean([r['search_observations'] for r in rows])),
            mean_additional_observations=float(np.mean([r['additional_observations'] for r in rows])),
            mean_total_observations=float(np.mean([r['total_observations'] for r in rows])),
            expected_uniform_wrong_acceptances=sum(r['uniform_conditional_wrong_accept_probability'] for r in rows) if key[2].startswith('uniform') else None))
    paired=[]; rng=np.random.default_rng(5193301)
    for family in ['transition','administrative_form']:
        for shift in [0,.35,.7]:
            for k in [1,2,3]:
                uniform=grouped[family,shift,f'uniform_{k}'];chosen=grouped[family,shift,f'entropy_{k}']
                seeds=sorted({r['seed'] for r in uniform})
                differences=np.array([np.mean([r['wrong_acceptance'] for r in chosen if r['seed']==s])-np.mean([r['wrong_acceptance'] for r in uniform if r['seed']==s]) for s in seeds])
                picks=rng.integers(0,len(seeds),size=(20000,len(seeds)))
                paired.append({'family':family,'domain_shift':shift,'verification_observations':k,'comparison':'entropy_minus_uniform',
                    'systems':len(seeds),'mean_wrong_acceptance_difference':float(differences.mean()),
                    'interval95':np.quantile(differences[picks].mean(axis=1),[.025,.975]).tolist()})
    checks={'conditions_576':len(hist)==576,'audits_4032':len(result['records'])==4032,
        'seven_audits_each_condition':all(len(x)==7 for x in audits.values()),
        'verification_codes_unqueried_and_answers_match':bool(all_responses),
        'acceptance_and_cost_fields_recomputed':bool(all_outcomes),
        'all_2304_uniform_probabilities_match_subset_enumeration':formula_conditions==2304 and largest_probability_error<1e-15,
        'independent_score_matches_48_systems':score_error<1e-8,
        'search_and_audit_choices_replayed_336_audits':bool(all_choices) and replayed==336,
        'proposal_and_search_masses_match':mass_error<1e-8,
        'each_group_96_conditions_24_systems':all(len(x)==96 and len({r['seed'] for r in x})==24 for x in grouped.values()),
        'code_hash_matches':hashlib.sha256((BASE/'main/code_snapshot.py').read_bytes()).hexdigest()==result['code_sha256'],
        'protocol_hash_matches':hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest()==result['protocol_sha256']}
    if not all(checks.values()):
        raise AssertionError(checks)
    out.mkdir()
    (out/'checks.json').write_text(json.dumps({'checks':checks,'max_score_error_bits':score_error,'max_mass_error':mass_error,'uniform_probability_conditions':formula_conditions},indent=2)+'\n',encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (out/'paired-system-comparisons.json').write_text(json.dumps(paired,indent=2)+'\n',encoding='utf-8')
    with (out/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks_passed':len(checks),'summary_groups':len(summary),'score_error':score_error,'mass_error':mass_error}))

if __name__=='__main__':
    main()
