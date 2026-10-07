"""Exploratory amendment. Reuses v1 algorithms and preserves their inputs/outputs.

Run from repository root with --verify, or --output a-new-directory.
All source-level inputs and per-query results remain in the local raw directory.
"""
import argparse
from collections import Counter
import itertools
import json
import math
from pathlib import Path
import random

import analyze as legacy

OWN, ROOT, RAW = legacy.OWN, legacy.ROOT, legacy.RAW
V2RAW = RAW / 'amendment-20261007'
NAMES = ('indus', 'ogham', 'tifinagh')
RULES = dict(legacy.RULES, R3S=legacy.INTEGER + ['symmetry'])

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def records(value):
    return value if isinstance(value, list) else value.get('records', value.get('rows'))

def hits(rows, name, rule):
    refs = {tuple(r[k] for k in RULES[rule]) for r in rows if r['inventory'] == name}
    return [tuple(q[k] for k in RULES[rule]) in refs for q in rows if q['inventory'] == 'tamil']

def overlay(base, patch):
    lookup = {r['id']: r for r in patch}
    return [dict(r, **{k:lookup[r['id']][k] for k in legacy.FIELDS}) if r['id'] in lookup else r for r in base]

def check_preserved():
    witness = read(OWN/'preserved-v1-review.json')
    for rel, expected in witness.items():
        assert legacy.digest(ROOT/rel) == expected, rel
    original_digest = legacy.digest
    frozen = OWN/'history/2026-10-07-before-amendment/PROTOCOL.md'
    legacy.digest = lambda p: original_digest(frozen if p == OWN/'PROTOCOL.md' else p)
    try:
        aggregates, queries = legacy.compute()
        for name, value in aggregates.items():
            assert read(OWN/'run-v1'/name) == value, name
        assert read(RAW/'run-v1-query-matches.json') == queries
    finally:
        legacy.digest = original_digest
    return {'preserved_hashes':len(witness),'v1_aggregate_files_exact':len(aggregates),'v1_queries_exact':True}

def sensitivity(base, repeat, reviewer):
    sets = {'primary':base,'second_pass_overlay':overlay(base,repeat),'reviewer_overlay':overlay(base,reviewer)}
    results=[]
    for qname,rname in itertools.product(sets,repeat=2):
        combined=[r for r in sets[qname] if r['inventory']=='tamil']+[r for r in sets[rname] if r['inventory']!='tamil']
        for inv,rule in itertools.product(NAMES,RULES):
            results.append({'query_coding':qname,'reference_coding':rname,'inventory':inv,'rule':rule,'matched':sum(hits(combined,inv,rule)),'queries':42})
    ranges=[]
    for inv,rule in itertools.product(NAMES,RULES):
        cells=[r for r in results if r['inventory']==inv and r['rule']==rule]
        homogeneous=[r['matched'] for r in cells if r['query_coding']==r['reference_coding']]
        ranges.append({'inventory':inv,'rule':rule,'homogeneous_min':min(homogeneous),'homogeneous_max':max(homogeneous),'all_nine_min':min(r['matched'] for r in cells),'all_nine_max':max(r['matched'] for r in cells)})
    return {'status':'Exploratory','overlay_coverage':{'primary':130,'second_pass_overlay':len(repeat),'reviewer_overlay':len(reviewer)},'cells':results,'ranges':ranges}

def agreement(base, repeat, reviewer):
    a={r['id']:r for r in base}; b={r['id']:r for r in repeat}; c={r['id']:r for r in reviewer}
    def pair(left,right,ids):
        return {'n':len(ids),'fields':{k:sum(left[i][k]==right[i][k] for i in ids) for k in legacy.FIELDS},'complete':sum(all(left[i][k]==right[i][k] for k in legacy.FIELDS) for i in ids),'without_orientation':sum(all(left[i][k]==right[i][k] for k in RULES['R3S']) for i in ids),'rules':{rule:sum(all(left[i][k]==right[i][k] for k in cols) for i in ids) for rule,cols in RULES.items()}}
    common=sorted(a.keys() & b.keys() & c.keys())
    return {'primary_reviewer_113':pair(a,c,sorted(a.keys() & c.keys())),'shared_sample':{'primary_second':pair(a,b,common),'primary_reviewer':pair(a,c,common),'second_reviewer':pair(b,c,common)},'note':'Original unadjudicated codings. Reviewer saw matched IDs, second-pass notes and T18 correction; T07 was corrected after comparison. Neither overlay is a full independent inventory.'}

def paired(rows, rule, n=20, max_segments=None):
    queries=[r for r in rows if r['inventory']=='tamil']
    refs={name:[r for r in rows if r['inventory']==name and (max_segments is None or r['segments']<=max_segments)] for name in NAMES}
    rng=random.Random(legacy.SEED + 91 + list(RULES).index(rule) + (100 if max_segments else 0))
    sig=lambda r:tuple(r[k] for k in RULES[rule])
    qs=[sig(q) for q in queries]
    values={name:[] for name in NAMES}; strata={name:{b:[] for b in ('1-3','4-6','7+')} for name in NAMES}
    for _ in range(legacy.REPLICATES):
        for name in NAMES:
            support={sig(r) for r in rng.sample(refs[name],n)}
            hit=[q in support for q in qs]
            values[name].append(sum(hit)/42)
            for band in ('1-3','4-6','7+'):
                inds=[i for i,q in enumerate(queries) if legacy.band(q)==band]
                strata[name][band].append(sum(hit[i] for i in inds)/len(inds))
    comparisons=[]
    for left,right in itertools.combinations(NAMES,2):
        comparisons.append({'left':left,'right':right,'difference_left_minus_right':legacy.interval([a-b for a,b in zip(values[left],values[right])])})
    return {'rule':rule,'n':n,'reference_segment_limit':max_segments,'eligible_sizes':{k:len(v) for k,v in refs.items()},'inventories':{name:{**legacy.interval(v),'complexity':{b:legacy.interval(w) for b,w in strata[name].items()}} for name,v in values.items()},'paired':comparisons,'interval_interpretation':'Central 95% over independently sampled reference-subset pairs, same fixed 42 queries. Not a population confidence interval.'}

def discordance(rows):
    out=[]
    for rule in RULES:
        for left,right in itertools.combinations(NAMES,2):
            a,b=hits(rows,left,rule),hits(rows,right,rule)
            x=sum(u and not v for u,v in zip(a,b));y=sum(v and not u for u,v in zip(a,b));d=x+y
            p=min(1,2*sum(math.comb(d,k) for k in range(min(x,y)+1))/2**d) if d else 1
            out.append({'rule':rule,'left':left,'right':right,'only_left':x,'only_right':y,'exact_two_sided_p':p,'difference':(x-y)/42})
    return {'cells':out,'interpretation':'Exact paired discordance test on full selected inventories. A binomial sign test assumes exchangeable independent discordant query types; repeated shape classes challenge that assumption. Exploratory, unadjusted, not a historical transmission test.'}

def compute():
    checks=check_preserved()
    all_rows=read(V2RAW/'coder-a.json'); old=read(RAW/'coder-a.json'); changes=read(V2RAW/'corrections-v2.json')
    expected=json.loads(json.dumps(old)); lookup={r['id']:r for r in expected}
    for change in changes:
        row=lookup[change['id']]
        for field,delta in change['changes'].items():
            assert row[field]==delta['old'];row[field]=delta['new']
        row['notes']+=' Corrected 2026-10-07 after review: '+change['reason']
    assert expected==all_rows
    legacy.validate(all_rows)
    legacy.RAW=V2RAW;legacy.RULES=RULES
    try:
        outputs,queries=legacy.compute()
    finally:
        legacy.RAW=RAW;legacy.RULES={k:v for k,v in RULES.items() if k!='R3S'}
    outputs['manifest.json'].update({'status':'Exploratory','amendment_date':'2026-10-07','amendment_code_sha256':legacy.digest(Path(__file__)),'corrections_sha256':legacy.digest(V2RAW/'corrections-v2.json'),'reviewer_coding_sha256':legacy.digest(OWN/'review/reviewer-coding.json'),'strict_rule':'R3S: integer fields plus symmetry; orientation excluded','random_mark_generator_built':False,'preservation_checks':checks})
    base=[r for r in old if r.get('readable',True)]; rows=[r for r in all_rows if r.get('readable',True)]
    repeat=[r for r in records(read(RAW/'coder-b.json')) if r['id'] in {a['id'] for a in base}]
    reviewer=read(OWN/'review/reviewer-coding.json')
    outputs['coding-sensitivity.json']=sensitivity(base,repeat,reviewer)
    outputs['inter-coder-reliability.json']=agreement(base,repeat,reviewer)
    outputs['paired-size-comparisons.json']=[dict(version=version,**paired(r,rule,n,limit)) for version,r in [('v1',base),('v2',rows)] for rule in RULES for n,limit in [(20,None),(16,6)]]
    outputs['paired-full-inventory.json']={v:discordance(r) for v,r in [('v1',base),('v2',rows)]}
    original=read(OWN/'run-v1/observed.json')
    old_s=[{'inventory':inv,'rule':'R3S','matched':sum(hits(base,inv,'R3S')),'queries':42} for inv in NAMES]
    outputs['v1-v2-comparison.json']={'status':'Exploratory','cells':[{'inventory':cell['inventory'],'rule':cell['rule'],'v1_matched':next(x['matched'] for x in original+old_s if x['inventory']==cell['inventory'] and x['rule']==cell['rule']),'v2_matched':cell['matched'],'queries':42} for cell in outputs['observed.json']],'corrected_ids':[c['id'] for c in changes]}
    return outputs,queries

def main():
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--output',default='run-v2');args=p.parse_args()
    target=(OWN/args.output).resolve();assert target.parent==OWN.resolve()
    outputs,queries=compute()
    if args.verify:
        for name,value in outputs.items():assert read(target/name)==value,name
        assert read(RAW/(args.output+'-query-matches.json'))==queries
        print('Verified v1 preservation and exact v2 recomputation:', len(outputs),'aggregate files')
    else:
        if target.exists():raise FileExistsError(target)
        target.mkdir()
        for name,value in outputs.items():(target/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        (RAW/(args.output+'-query-matches.json')).write_text(json.dumps(queries,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(outputs['v1-v2-comparison.json'],indent=2))

if __name__=='__main__':main()
