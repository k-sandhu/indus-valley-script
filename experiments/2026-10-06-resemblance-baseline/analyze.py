"""Run the declared descriptor pilot. No network access; all source rows stay local.

python experiments/2026-10-06-resemblance-baseline/analyze.py --output run-v1
Use --verify for a read-only recomputation against a frozen endpoint.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'
for name in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[name] = str(RAW / 'tmp')
(RAW / 'tmp').mkdir(exist_ok=True)
import numpy as np

INTEGER = ['segments', 'curved', 'loops', 'L', 'T', 'X', 'Y', 'other', 'terminals', 'components', 'dots']
FIELDS = INTEGER + ['symmetry', 'orientation']
RULES = {'R1': ['segments', 'loops'], 'R2': INTEGER, 'R3': FIELDS}
SEED = 20261007
REPLICATES = 2000

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def signature(row, rule):
    return tuple(row[k] for k in RULES[rule])

def band(row):
    return '1-3' if row['segments'] <= 3 else ('4-6' if row['segments'] <= 6 else '7+')

def interval(values):
    a = np.asarray(values)
    return {'mean': float(a.mean()), 'q025': float(np.quantile(a, .025)), 'q975': float(np.quantile(a, .975)),
            'mc_se_mean': float(a.std(ddof=1) / np.sqrt(len(a)))}

def validate(rows):
    assert len({(r['inventory'], r['id']) for r in rows}) == len(rows)
    for r in rows:
        if not r.get('readable', True):
            continue
        assert all(isinstance(r[k], int) and r[k] >= 0 for k in INTEGER), r['id']
        assert r['curved'] <= r['segments'] and r['dots'] <= r['segments'], r['id']
        assert r['symmetry'] in {'none', 'vertical', 'horizontal', 'both', 'diagonal'}
        assert r['orientation'] in {'vertical', 'horizontal', 'mixed', 'diagonal'}
        # Euler's planar graph identity where all degrees are known. Dots and
        # other-degree junctions need extra modelling and are excluded here.
        if not r['other'] and not r['dots']:
            expected = r['T'] + r['Y'] + 2*r['X'] - 2*r['loops'] + 2*r['components']
            assert expected == r['terminals'], (r['id'], expected, r['terminals'])

def compute():
    all_rows = json.loads((RAW / 'coder-a.json').read_text(encoding='utf-8'))
    repeat = json.loads((RAW / 'coder-b.json').read_text(encoding='utf-8'))
    if isinstance(repeat, dict):
        repeat = repeat.get('records', repeat.get('rows', []))
    validate(all_rows)
    validate(repeat)
    by_id = {r['id']: r for r in all_rows}
    comparable = [(by_id[b['id']], b) for b in repeat if by_id[b['id']].get('readable', True)]
    agreement = {
        'assigned': len(repeat), 'comparable': len(comparable),
        'excluded_primary_ids': [b['id'] for b in repeat if not by_id[b['id']].get('readable', True)],
        'fields': {f: {'agree': sum(a[f] == b[f] for a,b in comparable), 'denominator': len(comparable),
                       'fraction': sum(a[f] == b[f] for a,b in comparable)/len(comparable)} for f in FIELDS},
        'complete_vector': {'agree': sum(all(a[f] == b[f] for f in FIELDS) for a,b in comparable),
                            'denominator': len(comparable)},
        'rule_vector': {rule: {'agree': sum(signature(a,rule) == signature(b,rule) for a,b in comparable),
                               'denominator':len(comparable)} for rule in RULES},
        'interpretation': 'Independent agent passes, unadjudicated; not trained-human reliability.'
    }
    rows = [r for r in all_rows if r.get('readable', True)]
    inventories = {name: [r for r in rows if r['inventory'] == name] for name in ('tamil','indus','ogham','tifinagh')}
    assert {k:len(v) for k,v in inventories.items()} == {'tamil':42,'indus':36,'ogham':20,'tifinagh':32}
    audit = {'protocol_sha256':digest(OWN/'PROTOCOL.md'), 'coder_a_sha256':digest(RAW/'coder-a.json'),
             'coder_b_sha256':digest(RAW/'coder-b.json'), 'indus_selection_sha256':digest(RAW/'indus-selection.json'),
             'code_sha256':digest(Path(__file__)), 'seed':SEED, 'replicates':REPLICATES,
             'status':'Exploratory', 'null_status':'Synthetic', 'selected_indus_cells':42,
             'excluded_indus_cells':[r['id'] for r in all_rows if not r.get('readable',True)],
             'counts': {name:{'coded':len(inv),'uncertain':sum(r['uncertain'] for r in inv),
                              'complexity_counts':dict(Counter(band(r) for r in inv))} for name,inv in inventories.items()}}
    observed, subsampling, synthetic, queries = [], [], [], []
    query = inventories['tamil']
    rng = random.Random(SEED)
    for name in ('indus', 'ogham', 'tifinagh'):
        inv = inventories[name]
        for rule in RULES:
            sigs = [signature(r,rule) for r in inv]
            support = set(sigs)
            qs = [signature(r,rule) for r in query]
            hits = [q in support for q in qs]
            strata = {b: [i for i,r in enumerate(query) if band(r)==b] for b in ('1-3','4-6','7+')}
            observed.append({'inventory':name,'rule':rule,'reference_size':len(inv),'matched':sum(hits),
                             'queries':42,'rate':sum(hits)/42,'descriptor_classes':len(support),
                             'complexity':{b:{'matched':sum(hits[i] for i in inds),'queries':len(inds),
                                             'rate':sum(hits[i] for i in inds)/len(inds)} for b,inds in strata.items()}})
            for q,hit in zip(query,hits):
                queries.append({'inventory':name,'rule':rule,'query_id':q['id'],'matched':hit,
                                'references':[r['id'] for r in inv if signature(q,rule)==signature(r,rule)]})
            for n in sorted(set([s for s in (5,10,20,len(inv)) if s<=len(inv)])):
                values, by_band = [], {b: [] for b in strata}
                for _ in range(REPLICATES):
                    ref = set(rng.sample(sigs,n))
                    h = [q in ref for q in qs]
                    values.append(sum(h)/42)
                    for b,inds in strata.items():
                        by_band[b].append(sum(h[i] for i in inds)/len(inds))
                counts = Counter(sigs)
                # Exact mean under sampling without replacement of inventory rows.
                import math
                denominator = math.comb(len(inv),n)
                exact = sum(1-(math.comb(len(inv)-counts[q],n)/denominator if len(inv)-counts[q]>=n else 0)
                            for q in qs)/42
                stats=interval(values)
                assert abs(stats['mean']-exact) <= max(.003, 5*stats['mc_se_mean'])
                subsampling.append({'inventory':name,'rule':rule,'n':n,**stats,'exact_mean':exact,
                                    'complexity':{b:interval(v) for b,v in by_band.items()}})
            counts = Counter(sigs)
            p = {key:c/len(inv) for key,c in counts.items()}
            for n in (5,10,20,42,100,400):
                collisions, fixed = [], []
                for _ in range(REPLICATES):
                    ref=set(rng.choices(sigs,k=n))
                    synthetic_query=rng.choices(sigs,k=42)
                    collisions.append(sum(q in ref for q in synthetic_query)/42)
                    fixed.append(sum(q in ref for q in qs)/42)
                exact = sum(prob*(1-(1-prob)**n) for prob in p.values())
                exact_fixed = sum(1-(1-p.get(q,0))**n for q in qs)/42
                stats=interval(collisions)
                assert abs(stats['mean']-exact) <= max(.004,5*stats['mc_se_mean'])
                synthetic.append({'inventory':name,'rule':rule,'n':n,'surrogate_query':{**stats,'exact_mean':exact},
                                  'fixed_tamil_query':{**interval(fixed),'exact_mean':exact_fixed},
                                  'support_ceiling_fixed_tamil':sum(hits)/42})
    # Strictness is nested for every inventory and every individual query.
    for name in ('indus','ogham','tifinagh'):
        rates = [r['rate'] for r in observed if r['inventory']==name]
        assert rates[0] >= rates[1] >= rates[2]
    outputs={'manifest.json':audit,'observed.json':observed,'agreement.json':agreement,
             'subsampling.json':subsampling,'synthetic-null.json':synthetic}
    return outputs, queries

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',default='run-v1',help='New directory name inside owned directory.')
    p.add_argument('--verify',action='store_true')
    args=p.parse_args()
    target=(OWN/args.output).resolve()
    assert target.parent == OWN.resolve(), 'Output must be a direct child of owned directory.'
    outputs,queries=compute()
    if args.verify:
        for name,value in outputs.items():
            assert json.loads((target/name).read_text(encoding='utf-8')) == value, name
        assert json.loads((RAW/(args.output+'-query-matches.json')).read_text(encoding='utf-8')) == queries
        print('Verified exact aggregate and per-query recomputation:',target.name)
        return
    if target.exists():
        raise FileExistsError('Frozen output exists; choose a new directory or use --verify.')
    target.mkdir()
    for name,value in outputs.items():
        (target/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (RAW/(args.output+'-query-matches.json')).write_text(json.dumps(queries,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(target.relative_to(ROOT)),'observed':outputs['observed.json'],
                      'agreement':outputs['agreement.json']},indent=2))

if __name__=='__main__':
    main()
