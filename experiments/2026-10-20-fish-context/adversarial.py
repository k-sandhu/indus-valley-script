"""Post-outcome challengers, declared in AMENDMENT-2 before their computation."""
from collections import Counter,defaultdict
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fish_study',HERE/'study.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)


def main():
    dest=HERE/'adversarial-v1';dest.mkdir(exist_ok=False)
    table=s.coding();fish=s.fish_codes(table)
    model=s.read_json(HERE/'discovery-v2/model.json')
    disc=s.sequences(s.read_rows(s.RAW/'discovery-v2/discovery-faces.jsonl'))
    conf=s.sequences(s.read_rows(s.RAW/'confirmation-v1/confirmation-faces.jsonl'),seals=True)
    training=s.number_events(disc,table,fish)
    events=[e for e in s.number_events(conf,table,fish) if e['fish']]
    pool,left=defaultdict(Counter),defaultdict(Counter)
    for e in training:
        if e['fish']:pool[s.key(e['genre'],e['stroke_family'])][e['value']]+=1
        left[s.key(e['genre'],e['stroke_family'],e['left'])][e['value']]+=1
    comparisons={}
    for label,es in [('all_strokes',events),('short_strokes',[e for e in events if e['stroke_family']=='B001']),
                     ('long_strokes',[e for e in events if e['stroke_family']=='B031']),
                     ('excluding_value_two',[e for e in events if e['value']!=2])]:
        diffs=defaultdict(lambda:defaultdict(list))
        scores=defaultdict(list)
        for e in es:
            q,l,c=s.probability(e,model['numbers'])
            pc=pool[s.key(e['genre'],e['stroke_family'])]
            pooled=(pc[e['value']]+8*q)/(sum(pc.values())+8)
            lc=left[s.key(e['genre'],e['stroke_family'],e['left'])]
            preceding=(lc[e['value']]+8*q)/(sum(lc.values())+8)
            two=.9 if e['value']==2 else .1/(len(s.VALUES)-1)
            ps={'Q':q,'L':l,'pooled_fish':pooled,'preceding_context':preceding,'constant_two':two}
            for k,p in ps.items():scores[k].append(math.log2(p))
            for name,a,b in [('L_minus_Q',l,q),('L_minus_pooled',l,pooled),('L_minus_preceding',l,preceding),
                             ('L_minus_constant_two',l,two),('pooled_minus_Q',pooled,q)]:
                diffs[name][e['component']].append(math.log2(a/b))
        comparisons[label]={'events':len(es),'value_counts':dict(Counter(e['value'] for e in es)),
                            'mean_log2_probability':{k:float(np.mean(v)) for k,v in scores.items()},
                            'contrasts':{name:s.sign_result({c:float(np.mean(v)) for c,v in by.items()}) for name,by in diffs.items()}}

    # A positional reference with discovery-only frequency backoff.
    order=model['order']['codes'];rank={code:i for i,code in enumerate(order)}
    ds=[r for r in disc if s.is_seal(r)]
    global_counts=Counter(x for r in ds for x in r['seq'] if x in rank)
    counts=defaultdict(Counter)
    def slot(seq,i):return (min(len(seq),12),min(3,int(4*i/max(1,len(seq)))))
    for r in ds:
        for i,x in enumerate(r['seq']):
            if x in rank:counts[slot(r['seq'],i)][x]+=1
    def pp(code,seq,i):
        prior=(global_counts[code]+.5)/(sum(global_counts.values())+.5*len(rank))
        cc=counts[slot(seq,i)]
        return (cc[code]+8*prior)/(sum(cc.values())+8)
    p_order=(model['order']['discovery_forward_pairs']+.5)/(model['order']['discovery_pairs']+1)
    gains=defaultdict(list);detail=[]
    for r in conf:
        for i,(a,b) in enumerate(zip(r['seq'],r['seq'][1:])):
            if a not in rank or b not in rank or a==b:continue
            f=rank[a]<rank[b]
            p=p_order if f else 1-p_order
            a_score=pp(a,r['seq'],i)*pp(b,r['seq'],i+1)
            b_score=pp(b,r['seq'],i)*pp(a,r['seq'],i+1)
            reference=a_score/(a_score+b_score)
            gain=math.log2(p/reference)
            gains[r['component']].append(gain)
            detail.append({'record_id':r['record_id'],'component':r['component'],'order_probability':p,
                           'position_probability':reference,'gain_bits':gain})
    ordered=s.sign_result({c:float(np.mean(v)) for c,v in gains.items()})
    outside,_=s.score_order([r for r in conf if r['site']!='Mohenjo-daro'],fish,model)
    result={'status_class':'exploratory','post_outcome':True,'number_models':comparisons,
            'order_over_independent_positions':ordered,'order_without_mohenjo_daro':outside,
            'source_hashes':{str(p.relative_to(s.ROOT)):s.sha256(p) for p in [HERE/'AMENDMENT-2.md',Path(__file__),HERE/'discovery-v2/model.json']}}
    s.write_json(dest/'results.json',result)
    local=s.RAW/'adversarial-v1';local.mkdir(exist_ok=False)
    s.write_json(local/'order-comparisons.json',detail)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
