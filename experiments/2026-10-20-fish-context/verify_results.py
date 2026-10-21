"""Independent arithmetic and source-integrity checks; this is not peer review."""
from collections import Counter,defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import re

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-20-fish-context'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def rows(path):return [json.loads(t) for t in Path(path).read_text(encoding='utf-8').splitlines() if t.strip()]
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    checks=[]
    def check(name,value):checks.append({'check':name,'pass':bool(value)})
    frozen=read(HERE/'round.json')
    f=frozen['shots']['fish']['frozen']
    check('prediction freeze unchanged',digest(HERE/'PREDICTIONS.json')==f['predictions_sha256'])
    for path,h in f['artifacts'].items():check('frozen '+str(Path(path).relative_to(ROOT)),digest(path)==h)
    access=rows(HERE/'round.access.jsonl')
    opens=[r for r in access if r['half']=='confirmation' and r['allowed']]
    check('exactly one logged confirmation read',len(opens)==1)
    check('freeze precedes confirmation',f['utc']<opens[0]['utc'])
    check('historical exposure declared',opens[0]['fresh_claim_allowed'] is False)
    d=rows(RAW/'discovery-v2/discovery-faces.jsonl')
    c=rows(RAW/'confirmation-v1/confirmation-faces.jsonl')
    check('all source faces retained across halves',len(d)+len(c)==5680)
    check('components disjoint',{r['component'] for r in d}.isdisjoint(r['component'] for r in c))
    def seals(rs):
        texts={}
        for r in sorted(rs,key=lambda r:r['record_id']):
            if r['clean_rtl_singleline'] and r['object_type'].upper().split(':')[0]=='SEAL':
                seq=tuple(r['signs_reading_rtl']);texts.setdefault(seq,r)
        return texts
    ds,cs=seals(d),seals(c)
    check('two-or-more-sign seal texts stay in one half',not ({x for x in ds if len(x)>=2}&{x for x in cs if len(x)>=2}))
    result=read(HERE/'confirmation-v1/results.json')['comparisons']['primary_seals']
    model=read(HERE/'discovery-v2/model.json')
    order=model['order']['codes'];rank={v:i for i,v in enumerate(order)}
    margins=Counter();pairs=forward=0
    for seq,r in cs.items():
        for a,b in zip(seq,seq[1:]):
            if a in rank and b in rank and a!=b:
                z=1 if rank[a]<rank[b] else -1
                margins[r['component']]+=z;pairs+=1;forward+=z>0
    k=sum(v>0 for v in margins.values());n=sum(v!=0 for v in margins.values())
    p=float(sum(Fraction(math.comb(n,i),2**n) for i in range(k,n+1)))
    check('order component votes independently recovered',k==result['order']['positive'] and n-k==result['order']['negative'])
    check('order pairs independently recovered',pairs==result['order']['pairs'] and forward==result['order']['forward_pairs'])
    check('exact binomial order tail',abs(p-result['order']['p_one_sided'])<1e-15)

    import csv
    with (ROOT/'experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv').open(encoding='utf-8') as stream:
        table={r['code']:r for r in csv.DictReader(stream,delimiter='\t')}
    fish={s for s,r in table.items() if r['base']=='B220'}
    numeral={s:(r['base'],int(r['count'])) for s,r in table.items() if r['base'] in ['B001','B031'] and r['count']}
    gains=defaultdict(list);canonical=Counter();events=0;valcounts=Counter()
    for seq,r in cs.items():
        for a,b in zip(seq,seq[1:]):
            if a not in numeral or b not in fish:continue
            family,v=numeral[a]
            if v not in model['numbers']['values']:continue
            qd=model['numbers']['quantity_counts'].get('seal|'+family,model['numbers']['quantity_counts']['all'])
            q=Fraction(2*qd.get(str(v),0)+1,2*sum(qd.values())+len(model['numbers']['values']))
            ld=model['numbers']['local_counts'].get('seal|'+family+'|'+b,{})
            l=(ld.get(str(v),0)+8*q)/(sum(ld.values())+8)
            gains[r['component']].append(math.log2(float(l/q)))
            events+=1;valcounts[v]+=1
            if b=='220' and family=='B001':canonical[v]+=1
    averages=[sum(v)/len(v) for v in gains.values()]
    mean=sum(averages)/len(averages)
    positive=sum(x>1e-12 for x in averages);negative=sum(x< -1e-12 for x in averages)
    pnum=float(sum(Fraction(math.comb(positive+negative,i),2**(positive+negative)) for i in range(positive,positive+negative+1)))
    check('number event count independently recovered',events==result['numbers']['events'])
    check('number distribution independently recovered',{str(k):v for k,v in valcounts.items()}==result['numbers']['values'])
    check('fractional probability score matches',abs(mean-result['numbers']['mean_component_value'])<1e-12)
    check('number exact sign tail',abs(pnum-result['numbers']['p_one_sided'])<1e-20)
    check('canonical short-stroke counts match',{str(k):v for k,v in canonical.items()}==result['numbers']['narrow_celestial']['values'])

    # Enumerate the 120 distinct label allocations in the carrier comparison.
    objects=rows(RAW/'confirmation-v1/confirmation-objects.jsonl')
    mapping=read(HERE/'discovery-v2/map.json');codes=sorted(mapping)
    y=np.array([r['properties']['seal'] for r in objects],dtype=float)
    strata=defaultdict(list)
    for i,r in enumerate(objects):strata[(r['properties']['site'],r['properties']['length_bin'])].append(i)
    for ids in strata.values():y[ids]-=np.mean(y[ids])
    incidence=np.array([[code in r['signs'] for r in objects] for code in codes],dtype=float)
    effect=(incidence@y)/incidence.sum(axis=1)
    groups=defaultdict(list)
    for i,code in enumerate(codes):groups[json.dumps(mapping[code]['band'])].append(i)
    allocations=[]
    for idx in groups.values():
        howmany=sum(mapping[codes[i]]['label']=='fish' for i in idx)
        allocations.append(list(itertools.combinations(idx,howmany)))
    def contrast(ids):
        mask=np.zeros(len(codes),dtype=bool);mask[list(ids)]=True
        return float(effect[mask].mean()-effect[~mask].mean())
    actual_ids=[i for i,code in enumerate(codes) if mapping[code]['label']=='fish']
    actual=contrast(actual_ids)
    scores=[contrast([i for part in combo for i in part]) for combo in itertools.product(*allocations)]
    exact_p=sum(v>=actual-1e-12 for v in scores)/len(scores)
    bench=read(HERE/'confirmation-v1/meaning-map.json')
    check('carrier contrast independently recovered',abs(actual-bench['components']['fish_on_seals']['score'])<1e-12)
    check('120 unique label allocations',len(scores)==120)
    check('Monte Carlo carrier p agrees with exact enumeration',abs(exact_p-bench['primary']['p_one_sided'])<.02)

    reg=rows(RAW/'register-v3/objects.jsonl');cov=read(HERE/'register-v1/coverage.json')
    check('fish-object denominator',len(reg)==cov['population']['objects']==1246)
    check('every registered object contains fish',all(r['fish_codes'] for r in reg))
    check('all object faces retained',sum(len(r['faces']) for r in reg)==1520)
    placeholders={'','-','--','- -','?','??','unknown'}
    depth=sum(any(re.sub(r'\s+',' ',str(m.get('depth') or '')).strip().lower() not in placeholders
                  for m in r['metadata_by_face'].values()) for r in reg)
    check('depth coverage excludes placeholders',depth==748)
    images={i['local_path']:i['sha256'] for r in reg for i in r['images']}
    check('all image files present',all((ROOT/p).is_file() for p in images))
    check('all indexed image hashes agree',all(digest(ROOT/p)==h for p,h in images.items()))
    check('source image rights remain recorded',all(i['asset_rights']['status']=='rights-unverified' for r in reg for i in r['images']))
    controls=rows(RAW/'register-v2/source-controls.jsonl')
    check('H-912 is the fish-bearing source control',next(x for x in controls if x['cisi']=='H-912')['fish_register_member'])
    check('H-902 remains a separate nonfish control',not next(x for x in controls if x['cisi']=='H-902')['fish_register_member'])
    check('source observation records exist',len(read(HERE/'source-observations-v1.json')['observations'])==13)
    output={'verification_tier':'submitted; author arithmetic and source-integrity audit',
            'pass':all(c['pass'] for c in checks),'checks':checks,'checks_count':len(checks),
            'exact_carrier_reference':{'allocations':len(scores),'p_inclusive':exact_p,'observed_contrast':actual,
                                       'bench_monte_carlo_p':bench['primary']['p_one_sided']},
            'independent_calculation':{'order_p':p,'number_gain_bits':mean,'number_p':pnum},
            'source_scope':'Hash and identity checks do not adjudicate every photograph or every archaeological context.',
            'provenance':{'verification_code_sha256':digest(__file__),
                          'register_sha256':digest(RAW/'register-v3/objects.jsonl')}}
    target=HERE/'verification-v1.json'
    with target.open('x',encoding='utf-8') as f:json.dump(output,f,indent=2)
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
