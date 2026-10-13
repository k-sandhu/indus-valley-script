"""Reconstruct sampled held-out decisions with an independent Counter scorer."""
from collections import Counter,defaultdict
import json
import math
import sys
from pathlib import Path
import numpy as np

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[1]
LOCAL=ROOT/'data/raw/2026-10-12-bronze-age-comparison'
PRIMARY=sys.argv[1] if len(sys.argv)>1 else 'run-v2'
SIGNS=sys.argv[2] if len(sys.argv)>2 else 'sign-control-v2'
NORMALIZED=sys.argv[3] if len(sys.argv)>3 else 'normalized-v4'
records=[json.loads(line) for line in (LOCAL/NORMALIZED/'records.jsonl').read_text(encoding='utf-8').splitlines()]
checks=[]
for endpoint in [PRIMARY,SIGNS]:
    results=json.loads((PACKAGE/endpoint/('category-results.json' if endpoint==PRIMARY else 'results.json')).read_text())
    for key,result in results.items():
        if result['status']!='complete':continue
        corpus,stratum=key.split('/')
        rows=[]
        for row in records:
            if row['corpus']!=corpus:continue
            if endpoint==PRIMARY:
                allowed={'whole_tablet','seal','whole_jar_inscription','whole_document'} if stratum=='whole' else {'natural_line','source_sentence'}
                if row['kind'] in allowed and 3<=len(row['words'])<=12:rows.append(row)
            else:
                allowed={'glyph_sentence'} if stratum=='glyph_sentence' else {'natural_line'} if stratum=='extension' else {'whole_tablet','seal','whole_document'}
                if row['kind'] in allowed and 3<=len(row['units'])<=12:
                    rows.append(dict(row,words=row['units'],gold=[tag for units,tag in zip(row['word_units'],row['gold']) for _ in units]))
        suffix='-categories.json' if endpoint==PRIMARY else '-predictions.json'
        detail=json.loads((LOCAL/endpoint/(key.replace('/','-')+suffix)).read_text())
        anonymous=detail['anonymous_map'];folds=detail['folds']
        classes=['NUMBER','LOGOGRAM','SYLLABIC'] if corpus=='mycenaean' else ['NAME','NUMBER','VERB','FUNCTION','NOMINAL']
        tokens=[]
        for index,row in enumerate(rows):
            words=row['words'];length=len(words)
            for slot,(word,tag) in enumerate(zip(words,row['gold'])):
                if tag=='UNKNOWN':continue
                f=(anonymous[word],anonymous[words[slot-1]] if slot else 'START',anonymous[words[slot+1]] if slot+1<length else 'END',
                   str(min(4,int(5*slot/(length-1)))),'3-5' if length<=5 else '6-8' if length<=8 else '9-12')
                tokens.append((index,slot,tag,f))
        lookup={(row,slot):f for row,slot,tag,f in tokens}
        for fold in range(5):
            train=[t for t in tokens if folds[t[0]]!=fold]
            sample=[p for p in detail['predictions'] if p['fold']==fold]
            if not sample:continue
            sample=sample[::max(1,len(sample)//12)][:12]
            tags=[t[2] for t in train]
            shuffled=np.random.default_rng(20261012+fold).permutation(tags).tolist()
            for model,fields,labels in [('POSITION',[3,4],tags),('IDENTITY',[0],tags),('CONTEXT',[0,1,2,3,4],tags),('SHUFFLED_LABELS',[0,1,2,3,4],shuffled)]:
                prior=Counter(labels);vocabulary={field:{t[3][field] for t in train} for field in fields}
                counts={field:Counter((label,t[3][field]) for t,label in zip(train,labels)) for field in fields}
                for prediction in sample:
                    features=lookup[prediction['row'],prediction['slot']]
                    values=[]
                    for label in classes:
                        value=math.log((prior[label]+1)/(len(train)+len(classes)))
                        for field in fields:
                            token=features[field] if features[field] in vocabulary[field] else '__OOV__'
                            value+=math.log((counts[field][label,token]+1)/(prior[label]+len(vocabulary[field])+1))
                        values.append(value)
                    guessed=classes[max(range(len(classes)),key=lambda index:values[index])]
                    checks.append({'endpoint':endpoint,'cohort':key,'fold':fold,'model':model,
                                   'passed':guessed==prediction['predictions'][model]})
summary={'status':'passed' if all(c['passed'] for c in checks) else 'failed','decisions_replayed':len(checks),
         'passed':sum(c['passed'] for c in checks),'failed':[c for c in checks if not c['passed']],
         'scope':'Sampled held-out predictions from all available folds and both endpoints; separate Counter implementation.'}
path=PACKAGE/'category-replay-verification-v2.json'
with path.open('x',encoding='utf-8') as handle:json.dump(summary,handle,indent=2);handle.write('\n')
print(json.dumps(summary))
assert summary['status']=='passed'
