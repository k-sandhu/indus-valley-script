"""Follow-up known-category calibration without supplied word boundaries."""
from collections import defaultdict
from datetime import datetime,timezone
import json
from pathlib import Path
from analyze import score_category,dump
from reference_sources import PACKAGE,LOCAL,digest

output=PACKAGE/'sign-control-v1';output.mkdir(exist_ok=False)
details=LOCAL/'sign-control-v1';details.mkdir(parents=True,exist_ok=False)
source=LOCAL/'normalized-v3/records.jsonl'
records=[json.loads(line) for line in source.read_text(encoding='utf-8').splitlines()]
cohorts=defaultdict(list);alignment_checks=0
for row in records:
    if row['corpus']=='indus' or not 3<=len(row['units'])<=12:continue
    kinds={'whole_tablet','seal','whole_document','glyph_sentence','natural_line'}
    if row['kind'] not in kinds:continue
    units=[u for word in row['word_units'] for u in word]
    assert units==row['units'],row['id']
    gold=[tag for word,tag in zip(row['word_units'],row['gold']) for _ in word]
    assert len(units)==len(gold);alignment_checks+=1
    stratum='glyph_sentence' if row['kind']=='glyph_sentence' else 'extension' if row['kind']=='natural_line' else 'whole'
    cohorts[row['corpus']+'/'+stratum].append(dict(row,words=units,gold=gold,word_units=[[u] for u in units]))
result={}
for key,rows in sorted(cohorts.items()):
    result[key],predictions=score_category(rows)
    dump(details/(key.replace('/','-')+'-predictions.json'),predictions)
    print(json.dumps({'cohort':key,'status':result[key]['status'],'rows':len(rows)}),flush=True)
dump(output/'results.json',result)
dump(output/'manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'source_records_sha256':digest(source),
     'code_sha256':digest(__file__),'model_code_sha256':digest(PACKAGE/'analyze.py'),
     'protocol_sha256':digest(PACKAGE/'AMENDMENT-SIGN-CONTROL.md'),'alignment_checks':alignment_checks,
     'word_boundaries_available_to_predictor':False,'training_source_categories_available':True,
     'exploratory_post_word_outcome_refinement':True})

# Recount the saved predictions and independently check each declared split.
checks=[]
for key,rows in sorted(cohorts.items()):
    record=result[key]
    if record['status']!='complete':continue
    p=json.loads((details/(key.replace('/','-')+'-predictions.json')).read_text());folds=p['folds']
    for fold in range(5):
        train=[r for r,f in zip(rows,folds) if f!=fold];test=[r for r,f in zip(rows,folds) if f==fold]
        checks.append(not {a for r in train for a in r['aliases']}&{a for r in test for a in r['aliases']})
        checks.append(not {tuple(r['units']) for r in train}&{tuple(r['units']) for r in test})
    for model,scores in record['overall']['models'].items():
        correct=sum(v['predictions'][model]==v['gold'] for v in p['predictions'])
        checks.append(abs(correct/len(p['predictions'])-scores['accuracy'])<1e-12)
dump(output/'verification.json',{'status':'passed' if all(checks) else 'failed','split_and_metric_checks':len(checks),
     'passed':sum(checks),'alignment_checks':alignment_checks,'scope':'category alignment, source-group exclusion and saved-prediction recount'})
assert all(checks)
