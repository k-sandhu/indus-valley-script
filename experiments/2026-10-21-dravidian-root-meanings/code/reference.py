"""Prepare local pools: python -I code/reference.py. Sampling functions accept probabilities."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import itertools
from common import LOCAL,RUN,ENTRY,VALUES,read,write
import numpy as np
from coding import CLASSES,code_entry
GRAMMATICAL_HEADS={'pl','obl','n','adj','adv','v.i','v.t','intr','tr','caus','imper','past','fut','neg','inf','ger'}

def build_pool(entry,assigned,predicates=None,exclude_doubtful=False):
    candidates=set(); excluded=set(); counts={'grammatical_or_empty':0,'cross_reference':0}
    for form in entry['forms']:
        if form['loan'] or not form['tips'] or (exclude_doubtful and form['doubtful']): continue
        for segment in form['segments']:
            drop=segment.get('reference_dropped',segment['dropped'])
            if drop:
                counts[drop]+=1; continue
            h=segment['head']
            if not h or h in GRAMMATICAL_HEADS: counts['grammatical_or_empty']+=1; continue
            candidates.add(h)
            if any((predicates or CLASSES)[m](segment['normalised']) for m in assigned): excluded.add(h)
    pool={h:code_entry(entry,lambda s,target=h:__import__('dedr_parse').head(s)==target,exclude_doubtful)
          for h in sorted(candidates-excluded)}
    return pool,counts

def draw(probabilities,pools,n=10000,seed=20261021):
    rng=np.random.default_rng(seed)
    included=[m for m in probabilities if len(pools.get(m,[]))]
    excluded=[m for m in probabilities if m not in included]
    samples=np.empty((n,len(included)))
    indices=rng.integers(0,np.array([len(pools[m]) for m in included]),size=(n,len(included))) if included else np.empty((n,0),dtype=int)
    for j,m in enumerate(included):
        pool=np.asarray(pools[m],dtype=float)
        if np.any(~np.isfinite(pool)) or np.any((pool<0)|(pool>1)): raise ValueError('Invalid reference probability')
        samples[:,j]=pool[indices[:,j]]
    def stats(columns):
        subset=samples[:,columns]
        names=[included[j] for j in columns]
        actual=np.array([probabilities[m] for m in names])
        t=int(np.sum(actual>.5)); ts=np.sum(subset>.5,axis=1)
        unique,counts=np.unique(ts,return_counts=True)
        return dict(mean_root_probability=float(actual.mean()) if len(actual) else None,
                    reference_mean_root_probability=float(subset.mean()) if subset.size else None,
                    T=t,mean_T_star=float(ts.mean()),p_value=float((1+np.sum(ts>=t))/(1+n)),
                    reference_distribution={str(int(k)):int(v) for k,v in zip(unique,counts)},
                    included=names)
    return dict(seed=seed,draws=n,excluded_empty_pools=excluded,
                all=stats(list(range(len(included)))),value_meanings=stats([j for j,m in enumerate(included) if m in VALUES]))

def exact_distribution(pools):
    total=1
    for pool in pools: total*=len(pool)
    dist={}
    for values in itertools.product(*pools):
        count=sum(v>.5 for v in values); dist[count]=dist.get(count,0)+1/total
    return dist

def main():
    sizes={}; counts={}; by_meaning={}; removed_heads={}
    for key in sorted(set(ENTRY.values())):
        assigned=[m for m,e in ENTRY.items() if e==key]
        entry=read(LOCAL/'parsed'/(key+'.json'))
        pool,removed=build_pool(entry,assigned)
        excluded={'grammatical_or_empty':set(),'cross_reference':set()}
        for form in entry['forms']:
            if form['loan'] or not form['tips']: continue
            for segment in form['segments']:
                reason=segment.get('reference_dropped',segment['dropped'])
                if not reason and segment['head'] in GRAMMATICAL_HEADS: reason='grammatical_or_empty'
                if reason: excluded[reason].add(segment['head'])
        removed_heads[key]={reason:len(heads) for reason,heads in excluded.items()}
        write(LOCAL/'reference'/(key+'.json'),pool)
        sizes[key]=len(pool); counts[key]=removed
        for m in assigned: by_meaning[m]=len(pool)
    write(RUN/'pool-sizes.json',dict(entries=sizes,meanings=by_meaning,removed_segments=counts,removed_distinct_heads=removed_heads))

if __name__=='__main__': main()
