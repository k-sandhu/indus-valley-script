"""Source observations and frozen-score composition sensitivity. Never writes signs."""
import csv, hashlib, json, statistics, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-20-foreign-script-audit'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    with p.open('x',encoding='utf-8') as f: json.dump(x,f,indent=2,ensure_ascii=False)
def annotations():
    frame=json.loads((HERE/'frame.json').read_text(encoding='utf-8'))
    # Joins use a publication/excavation number, never equality of catalogue suffixes.
    secure={'114.1':(1,'Mackay 1943 plate LI:23; CISI C-32'),
      '2912.1':(2,'Marshall 1931 plate CX:309; excavation HR4393/309'),
      '3668.1':(3,'Laursen p109 explicitly identifies M-1369; Marshall 478'),
      '2913.1':(4,'Marshall 1931 plate CXII:383; excavation DK-E1886/383'),
      '2911.1':(5,'Mackay 1937-38 plate XCVI:500; excavation DK6844/500'),
      '3899.1':(16,'Gadd no15 U.8685; Gadd PDF24 printed p13'),
      '3898.1':(17,'Gadd no16 U.17649 / BM123208; Gadd PDF24-25 printed pp13-14'),
      '6000.1':(17,'BM123208 same object as U.17649; Gadd PDF24-25')}
    candidates={'2153.1':[15],'3881.1':[14],'5222.1':[22],'5232.1':[10],
      '147.1':[12,13],'148.1':[12,13],'3863.1':[6,8],
      '5227.1':[7,11,56],'5228.1':[7,11,56],'5230.1':[7,11,56],'5229.1':[9]}
    out=[]
    for r in frame:
        rid=r['record_id']; row=dict(record_id=rid,cisi=r['cisi'],site=r['site'],image_count=len(r['images']),
          table1_number=secure.get(rid,(None,None))[0],join_basis=secure.get(rid,(None,None))[1],
          candidate_table1_numbers=candidates.get(rid,[]),code_verification='unresolved: no source-to-Wells graphic concordance',
          direction='both orders retained; photo does not independently establish direction',
          proposed_exclusion=None)
        if rid=='2977.1': row.update(proposed_exclusion='incised tablet in CISI1 PDF161, heading TABLETS incised; not a circular stamp seal',table1_number=None)
        if rid=='2913.1': row.update(proposed_exclusion='sensitivity only: joined-animal composition; surviving text not securely separable in photograph')
        if rid in ['3898.1','6000.1']: row['source_disagreement']='Gadd describes four characters; export records six/five positions in alternate witnesses. Damage and token segmentation require adjudication.'
        if rid=='3668.1': row['source_note']='Laursen Fig8/3 and Fig11/3 render a damaged seal fragment; Figure11 is in impression polarity.'
        out.append(row)
    put(HERE/'annotations.json',out)
    put(HERE/'annotation-freeze.json',dict(annotations_sha256=sha(HERE/'annotations.json'),protocol_sha256=sha(HERE/'PROTOCOL.md'),code_sha256=sha(Path(__file__)),independent_review_freeze_sha256=sha(ROOT/'experiments/2026-10-20-foreign-script-blind-review/freeze.json'),stage='before composition sensitivity',exposure='author saw legacy scores; independent reviewer did not'))
    print('Annotation freeze saved; no scores loaded.')
def scores():
    freeze=json.loads((HERE/'annotation-freeze.json').read_text()); assert sha(HERE/'annotations.json')==freeze['annotations_sha256']
    old=ROOT/'experiments/2026-10-12-published-claim-tests/foreign-finds'
    west=list(csv.DictReader((old/'run-2026-10-12/objects.csv').open(encoding='utf-8')))
    west=[r for r in west if r['group']=='west_asia' and r['medium']=='round' and r['scorable']=='True' and r['record_id']!='6000.1']
    south=[json.loads(s) for s in (ROOT/'data/raw/2026-10-12-decipherment-claim-tests/foreign-finds/run-2026-10-12/peripheral_rows.jsonl').read_text().splitlines()]
    south=[r for r in south if r.get('peripheral_group')=='south_asian_round' and r['scorable']]
    def mean(a): return statistics.mean(float(r['u_surprisal']) for r in a)
    def boot(a,rng):
        fam={}
        for r in a: fam.setdefault(r['family'],[]).append(r)
        keys=list(fam)
        return mean([r for k in rng.choices(keys,k=len(keys)) for r in fam[k]])
    def result(w,s):
        rng=random.Random(20261020); draws=sorted(boot(w,rng)-boot(s,rng) for _ in range(10000))
        loo_w=[mean([q for q in w if q['family']!=r['family']])-mean(s) for r in w]
        loo_s=[mean(w)-mean([q for q in s if q['family']!=r['family']]) for r in s]
        return dict(west_faces=len(w),south_faces=len(s),west_families=len({r['family'] for r in w}),south_families=len({r['family'] for r in s}),west_mean_u=mean(w),south_mean_u=mean(s),difference=mean(w)-mean(s),bootstrap_95=[draws[249],draws[9749]],leave_one_family_out_range=[min(loo_w+loo_s),max(loo_w+loo_s)])
    wc=[r for r in west if r['object_type']=='SEAL:C']; sc=[r for r in south if r['object_type']=='SEAL:C']
    variants={ 'legacy_pooled':result(west,south),'circular_only':result(wc,sc),
      'circular_exclude_tablet':result(wc,[r for r in sc if r['record_id']!='2977.1']),
      'circular_exclude_tablet_and_uncertain_composition':result(wc,[r for r in sc if r['record_id'] not in ['2977.1','2913.1']])}
    # Exact common observed lengths, retaining the fixed old per-object ranks.
    lengths=sorted(set(int(r['length']) for r in wc)&set(int(r['length']) for r in sc if r['record_id']!='2977.1'))
    bylength={str(n):result([r for r in wc if int(r['length'])==n],[r for r in sc if int(r['length'])==n and r['record_id']!='2977.1']) for n in lengths if sum(int(r['length'])==n for r in wc)>1 and sum(int(r['length'])==n and r['record_id']!='2977.1' for r in sc)>1}
    put(HERE/'sensitivity.json',dict(schema_version='1.0',status='spent exploratory source-informed eligibility sensitivity',estimand='mean of the unchanged October12 per-object ranks; no model refitting or corrected sign-code scoring',variants=variants,common_observed_lengths=lengths,length_cells_with_at_least_two_per_side=bylength,dated_matching='infeasible: no calendar-dated South Asian circular comparison frame',site_matching='infeasible: foreign and South Asian site labels have no overlap',source_corrected_code_comparison='infeasible: zero code-verified foreign objects',input_hashes={str(p.relative_to(ROOT)):sha(p) for p in [old/'run-2026-10-12/objects.csv',ROOT/'data/raw/2026-10-12-decipherment-claim-tests/foreign-finds/run-2026-10-12/peripheral_rows.jsonl']}))
    print(json.dumps(variants,indent=2))
if __name__=='__main__': {'annotate':annotations,'score':scores}[sys.argv[1]]()

