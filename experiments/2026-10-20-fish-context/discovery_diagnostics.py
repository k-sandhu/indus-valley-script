"""Vectorized audit of one bench mean contrast and its discovery power law.

The shared power helper uses alpha=.05 internally even when the enclosing run
specifies a different alpha. We retain that run and check the study's .05/3 rule
here, using the same incidence, planting law, permutations and influence test.
"""
from collections import Counter
import json
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from bench.common import read_json,read_rows,permutation_indices,write_json,sha256
from bench.meaning_map import units


def main():
    rows=read_rows(ROOT/'data/raw/2026-10-20-fish-context/discovery-v2/discovery-objects.jsonl')
    mapping=read_json(HERE/'discovery-v2/map.json')
    pred=read_json(HERE/'discovery-v2/bench-predictions.json')['predictions'][0]
    us=units(rows,pred)
    codes=sorted(mapping)
    A=np.array([[s in u['signs'] for u in us] for s in codes],dtype=float)
    n=A.sum(axis=1)
    labels=np.array([mapping[s]['label']=='fish' for s in codes])
    groups={}
    for i,u in enumerate(us):groups.setdefault(u['controls'],[]).append(i)
    bands=[mapping[s]['band'] for s in codes]
    eligible=n>=pred['min_units']
    banks={}
    def weights(seed):
        if seed not in banks:
            ls=np.array([labels[p] for p in permutation_indices(bands,199,seed)])
            pos=ls*eligible;neg=(~ls)*eligible
            banks[seed]=pos/pos.sum(axis=1)[:,None]-neg/neg.sum(axis=1)[:,None]
        return banks[seed]
    def evaluate(response,seed):
        y=np.array(response,dtype=float)
        for ids in groups.values():y[ids]-=y[ids].mean()
        sums=A@y
        means=sums/n
        w=labels*eligible/(labels*eligible).sum()-(~labels)*eligible/((~labels)*eligible).sum()
        score=float(w@means)
        null=weights(seed)@means
        p=float((1+(null>=score).sum())/(len(null)+1))
        # This matches bench's deletion after constructing and residualizing units.
        denominators=n[:,None]-A
        keep=denominators>=pred['min_units']
        positives=labels[:,None]*keep;negatives=(~labels)[:,None]*keep
        loo_weights=positives/positives.sum(axis=0)[None,:]-negatives/negatives.sum(axis=0)[None,:]
        loo_means=(sums[:,None]-A*y[None,:])/denominators
        minimum=float(np.min(np.sum(loo_weights*loo_means,axis=0)))
        return {'score':score,'p':p,'minimum_loo':minimum,'null_mean':float(null.mean()),'null_sd':float(null.std())}
    original=evaluate([u['value'] for u in us],20261013)
    bench=read_json(HERE/'discovery-v2/bench-diagnostics.json')
    b=bench['components']['fish_on_seals']
    checks={
        'contrast_matches_bench':abs(original['score']-b['score'])<1e-12,
        'null_mean_matches_bench':abs(original['null_mean']-b['null_mean'])<1e-12,
        'null_sd_matches_bench':abs(original['null_sd']-b['null_sd'])<1e-12,
        'p_matches_bench':abs(original['p']-b['p_one_sided'])<.011,
        'deletion_matches_bench':abs(original['minimum_loo']-bench['influence']['fish_on_seals']['minimum_contrast'])<1e-12}
    exposure=(A*labels[:,None]).sum(axis=0)/np.maximum(A.sum(axis=0),1)
    power=[]
    for effect in (0,.25,.5,1):
        passes05=passes_study=0
        for trial in range(12):
            rng=np.random.default_rng(20261013+1000+trial)
            y=rng.normal(size=len(us))+effect*exposure
            r=evaluate(y,20261013+2000+trial)
            passes05+=r['p']<=.05 and r['minimum_loo']>0
            passes_study+=r['p']<=.05/3 and r['minimum_loo']>0
        power.append({'effect_sd':effect,'trials':12,'passes_alpha_05':int(passes05),
                      'passes_alpha_study':int(passes_study),'study_alpha':.05/3,
                      'rate_at_study_alpha':passes_study/12})
    checks['power_reproduces_shared_helper_at_05']=all(p['passes_alpha_05']==b['success'] for p,b in zip(power,bench['power']))
    allocations=1
    descriptions=[]
    bg={}
    for s,v in mapping.items():bg.setdefault(json.dumps(v['band']),[]).append(v['label'])
    import math
    for band,values in bg.items():
        k=values.count('fish');n=len(values);ways=math.comb(n,k);allocations*=ways
        descriptions.append({'band':json.loads(band),'signs':n,'fish':k,'allocations':ways})
    result={'status':'discovery only','checks':checks,'pass':all(checks.values()),'original':original,
            'power':power,'power_scope':'Component-shared normal outcomes; 12 trials per effect; estimates have substantial Monte Carlo uncertainty.',
            'shared_helper_alpha':.05,'study_alpha':.05/3,'label_allocations':allocations,'bands':descriptions,
            'provenance':{'code_sha256':sha256(__file__),'bench_sha256':sha256(ROOT/'bench/meaning_map.py')}}
    write_json(HERE/'discovery-v2/power-audit.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
