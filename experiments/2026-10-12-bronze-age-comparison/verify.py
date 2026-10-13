"""Separate arithmetic, source-integrity and held-out exclusion checks.

This checker does not import the analysis implementation. It checks the observed
position statistic against a Counter calculation and the shuffle mean against
an exact finite-population variance formula.
"""
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
LOCAL=ROOT/'data/raw/2026-10-12-bronze-age-comparison'
RUN=sys.argv[1] if len(sys.argv)>1 else 'run-v2'
NORMALIZED=sys.argv[2] if len(sys.argv)>2 else 'normalized-v4'
OUT=PACKAGE/RUN
checks=[]
def check(name,condition,detail=None):
    checks.append({'name':name,'passed':bool(condition),'detail':detail})
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def hashfile(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for b in iter(lambda:handle.read(1024*1024),b''):value.update(b)
    return value.hexdigest()

manifest=read(OUT/'manifest.json')
recordfile=LOCAL/NORMALIZED/'records.jsonl'
records=[json.loads(line) for line in recordfile.read_text(encoding='utf-8').splitlines()]
check('normalized input hash',hashfile(recordfile)==manifest['records_sha256'])
for file,key in [('analyze.py','analysis_code_sha256'),('reference_sources.py','parser_code_sha256'),('PROTOCOL.md','protocol_sha256'),('COHORT-SPEC.md','cohort_spec_sha256')]:
    check('current '+file+' agrees with run',hashfile(PACKAGE/file)==manifest[key])
for name,value in read(OUT/'output-hashes.json').items():check('frozen output '+name,hashfile(OUT/name)==value)
for row in records:
    check('word/category/unit alignment '+row['id'],len(row['words'])==len(row['gold'])==len(row['word_units']))
    if row['corpus']=='indus':check('no IVS word/meaning key '+row['id'],row['words']==row['gold']==[])

structural=read(OUT/'structural-results.json')
references=read(LOCAL/RUN/'structural-references.json')
for key,result in structural.items():
    corpus,kind=key.split('/')
    eligible=[r for r in records if r['corpus']==corpus and r['kind']==kind and 3<=len(r['units'])<=12]
    selected={}
    for row in sorted(eligible,key=lambda r:r['id']):selected.setdefault(tuple(row['units']),row)
    sequences=list(selected);counts=Counter();positions=Counter();variances=Counter()
    for seq in sequences:
        local=Counter(seq);length=len(seq)
        for j,u in enumerate(seq):counts[u]+=1;positions[u]+=j/(length-1)
        variance=(length+1)/(12*(length-1))
        for u,n in local.items():variances[u]+=n*(length-n)/(length-1)*variance
    keep=[u for u,n in counts.items() if n>=5];denom=sum(counts[u] for u in keep)
    observed=sum(counts[u]*(positions[u]/counts[u]-.5)**2 for u in keep)/denom if denom else None
    expected=sum(variances[u]/counts[u] for u in keep)/denom if denom else None
    null=references[key]['null']
    check(key+' exact distinct-sequence count',len(sequences)==result['distinct_sequences'])
    check(key+' token count',sum(counts.values())==result['tokens'])
    check(key+' inventory count',len(counts)==result['types'])
    check(key+' independent observed statistic',observed is None if result['statistic'] is None else abs(observed-result['statistic'])<1e-12)
    if null:
        se=float(np.std(null,ddof=1))/math.sqrt(len(null))
        check(key+' analytic shuffle expectation',abs(float(np.mean(null))-expected)<=5*se+1e-12,
              {'analytic_mean':expected,'monte_carlo_mean':float(np.mean(null)),'mean_standard_error':se})
        p=(1+sum(v>=observed-1e-15 for v in null))/(1+len(null))
        check(key+' permutation tail',p==result['permutation_p'])
        check(key+' reference count',len(null)==1999)

valid=sorted((v['permutation_p'],k) for k,v in structural.items() if v['permutation_p'] is not None)
bound=0
for i,(p,key) in enumerate(valid):
    bound=max(bound,min(1,(len(valid)-i)*p));check(key+' whole-family Holm',bound==structural[key]['holm_p_all_structural_cohorts'])

categories=read(OUT/'category-results.json')
for key,result in categories.items():
    corpus,stratum=key.split('/')
    kinds={'whole_tablet','seal','whole_jar_inscription','whole_document'} if stratum=='whole' else {'natural_line','source_sentence'}
    rows=[r for r in records if r['corpus']==corpus and r['kind'] in kinds and 3<=len(r['words'])<=12]
    check(key+' category row census',len(rows)==result['rows'])
    if result['status']!='complete':continue
    detail=read(LOCAL/RUN/(key.replace('/','-')+'-categories.json'));predictions=detail['predictions'];folds=detail['folds']
    support=Counter(p['gold'] for p in predictions)
    check(key+' class support',dict(support)==result['overall']['class_support'])
    check(key+' scored token count',len(predictions)==result['overall']['tokens'])
    for fold in range(5):
        train=[r for r,f in zip(rows,folds) if f!=fold];test=[r for r,f in zip(rows,folds) if f==fold]
        check(key+f' fold {fold} physical/source alias exclusion',not {a for r in train for a in r['aliases']}&{a for r in test for a in r['aliases']})
        check(key+f' fold {fold} exact-word-sequence exclusion',not {tuple(r['words']) for r in train}&{tuple(r['words']) for r in test})
    for model,scores in result['overall']['models'].items():
        correct=Counter(p['gold'] for p in predictions if p['predictions'][model]==p['gold'])
        accuracy=sum(correct.values())/len(predictions)
        balanced=sum(correct[c]/support[c] for c in support)/len(support)
        check(key+' '+model+' micro accuracy',abs(accuracy-scores['accuracy'])<1e-12)
        check(key+' '+model+' balanced accuracy',abs(balanced-scores['balanced_accuracy'])<1e-12)
    check(key+' withheld source labels retained',all(rows[p['row']]['gold'][p['slot']]==p['gold'] for p in predictions))
    known_words={fold:{w for row,f in zip(rows,folds) if f!=fold for w,t in zip(row['words'],row['gold']) if t!='UNKNOWN'} for fold in range(5)}
    check(key+' identity known flag',all(p['known_identity']==(rows[p['row']]['words'][p['slot']] in known_words[p['fold']])
          for p in predictions[::max(1,len(predictions)//30)]))
    check(key+' anonymous identities are unique',len(set(detail['anonymous_map'].values()))==len(detail['anonymous_map']))

lexical=read(OUT/'lexical-ambiguity.json')
inventories=defaultdict(set)
for row in records:
    for units,tag in zip(row['word_units'],row['gold']):
        if 2<=len(units)<=8 and tag not in {'NUMBER','UNKNOWN'}:inventories[row['corpus']].add(tuple(units))
def pattern(seq):
    ordered=[];out=[]
    for item in seq:
        if item not in ordered:ordered.append(item)
        out.append(ordered.index(item))
    return tuple(out)
targets={tuple(r['units']) for r in records if r['corpus']=='indus' and 3<=len(r['units'])<=8}
check('lexical target census',len(targets)==lexical['target_unique_faces'])
for corpus,inventory in inventories.items():
    counts=Counter(pattern(entry) for entry in inventory);matches=[counts[pattern(t)] for t in targets]
    check(corpus+' lexicon count',len(inventory)==lexical['natural_lexicon_sizes'][corpus])
    check(corpus+' per-face compatibility',sum(v>0 for v in matches)==lexical['natural'][corpus]['compatible_faces'])
    check(corpus+' per-face ambiguity',sum(v>1 for v in matches)==lexical['natural'][corpus]['faces_with_multiple_candidates'])
    bound=lexical['global_injection_necessary_condition'][corpus]
    check(corpus+' reference unit count',len({u for word in inventory for u in word})==bound['reference_distinct_units'])

baseline=read(PACKAGE/'baseline-v1.json')
for item in baseline['files'][5:]:check('previous non-navigation bytes '+item['path'],hashfile(ROOT/item['path'])==item['sha256'])
rawpaths=[str(p.relative_to(ROOT)).replace('\\','/') for p in LOCAL.rglob('*') if p.is_file()]
ignore=subprocess.run(['git','check-ignore','-z','--stdin'],cwd=ROOT,input=b''.join(p.encode()+b'\0' for p in rawpaths),capture_output=True,check=False)
ignored={p.decode() for p in ignore.stdout.split(b'\0') if p}
check('all new raw/derived files remain ignored',set(rawpaths)<=ignored,{'files':len(rawpaths)})
summary={'status':'passed' if all(c['passed'] for c in checks) else 'failed','checks':len(checks),
         'passed':sum(c['passed'] for c in checks),'failed':[c for c in checks if not c['passed']],
         'analytic_reference_checks':[c for c in checks if 'analytic shuffle' in c['name']],
         'scope':'Implementation, source preservation and declared exclusions; no historical-language authentication.'}
destination=OUT/'verification.json'
with destination.open('x',encoding='utf-8') as handle:json.dump(summary,handle,indent=2);handle.write('\n')
print(json.dumps({k:summary[k] for k in ['status','checks','passed','failed']}))
if summary['status']!='passed':raise SystemExit(1)
