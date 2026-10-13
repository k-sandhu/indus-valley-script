"""Frozen structural, held-out category and lexical-ambiguity calculations."""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
from reference_sources import PACKAGE,ROOT,LOCAL,digest

SEED=20261012
CLASSES=['NAME','NUMBER','VERB','FUNCTION','NOMINAL']

def dump(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def entropy(counts):
    total=sum(counts)
    return -sum((v/total)*math.log2(v/total) for v in counts if v) if total else None
def equality(sequence):
    ids={}
    return tuple(ids.setdefault(u,len(ids)) for u in sequence)
def length_range(sequence):return 3<=len(sequence)<=12

def closure(rows,sequence_key):
    parent=list(range(len(rows)))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    aliases={};seqs={}
    for i,row in enumerate(rows):
        for alias in row['aliases']:
            if alias in aliases:union(i,aliases[alias])
            else:aliases[alias]=i
        seq=tuple(row[sequence_key])
        if seq in seqs:union(i,seqs[seq])
        else:seqs[seq]=i
    return [find(i) for i in range(len(rows))]

def unique(rows):
    groups=closure(rows,'units');seen={};result=[]
    for i,row in sorted(enumerate(rows),key=lambda p:p[1]['id']):
        seq=tuple(row['units'])
        if seq not in seen:seen[seq]=True;result.append(dict(row,group=groups[i]))
    return result,{'eligible_records':len(rows),'distinct_sequences':len(result),'duplicate_records':len(rows)-len(result),
                   'groups':len({r['group'] for r in result}),'largest_group_distinct_sequences':max(Counter(r['group'] for r in result).values(),default=0)}

def structural(rows,seed):
    rows,summary=unique(rows)
    sequences=[r['units'] for r in rows]
    inventory=sorted({u for seq in sequences for u in seq});index={u:i for i,u in enumerate(inventory)}
    k=len(inventory);matrix=defaultdict(list);freq=np.zeros(k,dtype=int);sums=np.zeros(k)
    openers=Counter();closers=Counter();pairs=Counter()
    for seq in sequences:
        coded=[index[u] for u in seq];matrix[len(seq)].append(coded)
        freq+=np.bincount(coded,minlength=k)
        sums+=np.bincount(coded,weights=np.linspace(0,1,len(seq)),minlength=k)
        openers[seq[0]]+=1;closers[seq[-1]]+=1;pairs.update(zip(seq[:-1],seq[1:]))
    keep=freq>=5;denom=int(freq[keep].sum())
    observed=float(np.sum(freq[keep]*(sums[keep]/freq[keep]-.5)**2)/denom) if denom else None
    null=[];rng=np.random.default_rng(seed)
    if denom:
        arrays={length:np.array(values,dtype=int) for length,values in matrix.items()}
        for start in range(0,1999,40):
            batch=min(40,1999-start);nsums=np.zeros((batch,k))
            for length,array in arrays.items():
                order=np.argsort(rng.random((batch,*array.shape)),axis=-1)
                shuffled=np.take_along_axis(np.broadcast_to(array,(batch,*array.shape)),order,axis=-1)
                for rep in range(batch):
                    nsums[rep]+=np.bincount(shuffled[rep].ravel(),weights=np.tile(np.linspace(0,1,length),len(array)),minlength=k)
            null.extend((np.sum(freq[keep]*(nsums[:,keep]/freq[keep]-.5)**2,axis=1)/denom).tolist())
    summary.update({'encoding':sorted({r['encoding'] for r in rows}),'length_counts':dict(sorted(Counter(map(len,sequences)).items())),
                    'tokens':int(freq.sum()),'types':k,'types_with_at_least_five_tokens':int(keep.sum()),
                    'statistic':observed,'reference_mean':float(np.mean(null)) if null else None,
                    'reference_sd':float(np.std(null,ddof=1)) if null else None,'references':len(null),
                    'permutation_p':(1+sum(v>=observed-1e-15 for v in null))/(1+len(null)) if null else None,
                    'statistic_minus_reference_mean':observed-float(np.mean(null)) if null else None,
                    'opener_entropy_bits':entropy(openers.values()),'closer_entropy_bits':entropy(closers.values()),
                    'largest_opener_share':max(openers.values(),default=0)/len(rows) if rows else None,
                    'largest_closer_share':max(closers.values(),default=0)/len(rows) if rows else None,
                    'distinct_adjacent_pairs':len(pairs),'repeated_adjacent_pair_occurrences':sum(v-1 for v in pairs.values()),
                    'dates':dict(Counter(r.get('date','unknown') for r in rows)),'genres':dict(Counter(str(r.get('genre','unknown')) for r in rows))})
    return summary,{'observed':observed,'null':null,'records':[r['id'] for r in rows]}

def fold_assign(rows,groups):
    sizes=Counter()
    for row,group in zip(rows,groups):sizes[group]+=sum(t!='UNKNOWN' for t in row['gold'])
    rng=np.random.default_rng(SEED);tie={g:float(rng.random()) for g in sorted(sizes)}
    loads=[0]*5;assignment={}
    for group in sorted(sizes,key=lambda g:(-sizes[g],tie[g])):
        fold=min(range(5),key=lambda i:(loads[i],i));assignment[group]=fold;loads[fold]+=sizes[group]
    return [assignment[g] for g in groups],loads

def feature_rows(rows):
    vocab=sorted({w for row in rows for w in row['words']});rng=np.random.default_rng(SEED)
    order=rng.permutation(len(vocab));anonymous={w:f'U{int(i):06d}' for w,i in zip(vocab,order)}
    tokens=[]
    for i,row in enumerate(rows):
        seq=row['words'];length=len(seq);lb='3-5' if length<=5 else '6-8' if length<=8 else '9-12'
        for j,(word,tag) in enumerate(zip(seq,row['gold'])):
            if tag=='UNKNOWN':continue
            tokens.append({'row':i,'slot':j,'tag':tag,'features':[anonymous[word],anonymous[seq[j-1]] if j else 'START',
                anonymous[seq[j+1]] if j+1<length else 'END',str(min(4,int(5*j/(length-1)))),lb]})
    return tokens,anonymous

class Bayes:
    def __init__(self,train,features,classes,labels=None):
        self.features=features;self.classes=classes;self.class_counts=Counter();self.counts=[defaultdict(Counter) for _ in range(5)]
        self.vocab=[set() for _ in range(5)]
        for n,row in enumerate(train):
            tag=row['tag'] if labels is None else labels[n];self.class_counts[tag]+=1
            for f in features:self.counts[f][tag][row['features'][f]]+=1;self.vocab[f].add(row['features'][f])
        self.total=len(train)
    def predict(self,row):
        scores={}
        for tag in self.classes:
            score=math.log((self.class_counts[tag]+1)/(self.total+len(self.classes)))
            for f in self.features:
                value=row['features'][f] if row['features'][f] in self.vocab[f] else '__OOV__'
                score+=math.log((self.counts[f][tag][value]+1)/(self.class_counts[tag]+len(self.vocab[f])+1))
            scores[tag]=score
        return max(self.classes,key=lambda tag:scores[tag])

def score_category(rows):
    groups=closure(rows,'words');folds,loads=fold_assign(rows,groups)
    if len(set(groups))<5:return {'status':'insufficient-independent-groups','rows':len(rows),'groups':len(set(groups))},[]
    tokens,anonymous=feature_rows(rows)
    classes=['NUMBER','LOGOGRAM','SYLLABIC'] if rows[0]['corpus']=='mycenaean' else CLASSES
    predictions=[];audits=[]
    for fold in range(5):
        train=[t for t in tokens if folds[t['row']]!=fold];test=[t for t in tokens if folds[t['row']]==fold]
        if not train or not test:continue
        train_groups={g for g,f in zip(groups,folds) if f!=fold};test_groups={g for g,f in zip(groups,folds) if f==fold}
        assert not train_groups&test_groups
        majority=max(classes,key=lambda c:sum(t['tag']==c for t in train))
        rng=np.random.default_rng(SEED+fold);labels=rng.permutation([t['tag'] for t in train]).tolist()
        models={'POSITION':Bayes(train,[3,4],classes),'IDENTITY':Bayes(train,[0],classes),
                'CONTEXT':Bayes(train,[0,1,2,3,4],classes),'SHUFFLED_LABELS':Bayes(train,[0,1,2,3,4],classes,labels)}
        known={t['features'][0] for t in train}
        for token in test:
            predictions.append({'record_id':rows[token['row']]['id'],'row':token['row'],'slot':token['slot'],'fold':fold,
                                'gold':token['tag'],'known_identity':token['features'][0] in known,
                                'predictions':dict(MAJORITY=majority,**{name:model.predict(token) for name,model in models.items()})})
        audits.append({'fold':fold,'train_tokens':len(train),'test_tokens':len(test),'train_groups':len(train_groups),
                       'test_groups':len(test_groups),'shared_groups':0,'shuffled_label_margins_preserved':Counter(labels)==Counter(t['tag'] for t in train)})
    def summarize(subset):
        support=Counter(p['gold'] for p in subset);out={}
        for model in ['MAJORITY','POSITION','IDENTITY','CONTEXT','SHUFFLED_LABELS']:
            correct=Counter(p['gold'] for p in subset if p['predictions'][model]==p['gold'])
            out[model]={'accuracy':sum(correct.values())/len(subset) if subset else None,
                        'balanced_accuracy':sum(correct[c]/support[c] for c in support)/len(support) if support else None,
                        'per_class_correct':dict(correct)}
        return {'tokens':len(subset),'class_support':dict(support),'models':out}
    result={'status':'complete','rows':len(rows),'groups':len(set(groups)),'largest_group_rows':max(Counter(groups).values()),
            'fold_token_loads':loads,'source_unknown_targets':sum(t=='UNKNOWN' for r in rows for t in r['gold']),
            'task':'written-unit-type prediction' if rows[0]['corpus']=='mycenaean' else 'source-word-category prediction',
            'overall':summarize(predictions),'known_identity':summarize([p for p in predictions if p['known_identity']]),
            'unseen_identity':summarize([p for p in predictions if not p['known_identity']]),'fold_audits':audits}
    return result,{'predictions':predictions,'anonymous_map':anonymous,'folds':folds,'groups':groups}

def lexical(records,indus_rows):
    lexica=defaultdict(set)
    for row in records:
        if row['corpus']=='indus':continue
        for word,units,tag in zip(row['words'],row['word_units'],row['gold']):
            if 2<=len(units)<=8 and tag not in {'NUMBER','UNKNOWN'}:lexica[row['corpus']].add(tuple(units))
    inventories={c:sorted(lexica[c]) for c in ['sumerian','akkadian','egyptian','mycenaean']}
    targets=sorted({tuple(r['units']) for r in indus_rows if 3<=len(r['units'])<=8})
    patterns=[equality(t) for t in targets];hist=Counter(patterns)
    result={'assumptions':['one complete IVS face is one word','bijection between reading/glyph units','no phonetic anchor'],
            'target_unique_faces':len(targets),'target_equality_patterns':len(hist),'natural_lexicon_sizes':{c:len(v) for c,v in inventories.items()},
            'natural':{},'matched':{}}
    for corpus,inventory in inventories.items():
        counts=Counter(map(equality,inventory));support=[counts[p] for p in patterns]
        result['natural'][corpus]={'compatible_faces':sum(v>0 for v in support),'faces_with_multiple_candidates':sum(v>1 for v in support),
                                   'median_candidates_per_face':float(np.median(support)),'max_candidates_per_face':max(support,default=0)}
    n=min(200,*(len(v) for v in inventories.values()));result['matched_lexicon_size']=n
    rng=np.random.default_rng(SEED)
    for corpus,inventory in inventories.items():
        coverage=[];ambiguity=[]
        for rep in range(500):
            indices=rng.choice(len(inventory),n,replace=False);counts=Counter(equality(inventory[int(i)]) for i in indices)
            coverage.append(sum(counts[p]>0 for p in patterns)/len(patterns));ambiguity.append(sum(counts[p]>1 for p in patterns)/len(patterns))
        result['matched'][corpus]={'mean_compatible_fraction':float(np.mean(coverage)),
                                  'central_subset_95_interval':np.quantile(coverage,[.025,.975]).tolist(),
                                  'mean_multiple_candidate_fraction':float(np.mean(ambiguity)),'samples':500}
    return result

def main(run):
    destination=PACKAGE/run;destination.mkdir(exist_ok=False)
    detail=LOCAL/run;detail.mkdir(parents=True,exist_ok=False)
    records_file=LOCAL/'normalized-v1/records.jsonl'
    records=[json.loads(line) for line in records_file.read_text(encoding='utf-8').splitlines()]
    dump(destination/'manifest.json',{'started_utc':datetime.now(timezone.utc).isoformat(),'seed':SEED,'records_sha256':digest(records_file),
         'analysis_code_sha256':digest(__file__),'parser_code_sha256':digest(PACKAGE/'reference_sources.py'),
         'protocol_sha256':digest(PACKAGE/'PROTOCOL.md'),'cohort_spec_sha256':digest(PACKAGE/'COHORT-SPEC.md'),
         'scope':'exploratory source-observed comparisons; no inferred historical language identity'})
    cohorts=defaultdict(list)
    for row in records:
        if length_range(row['units']):cohorts[(row['corpus'],row['kind'])].append(row)
    results={};raw={}
    for i,((corpus,kind),rows) in enumerate(sorted(cohorts.items())):
        key=corpus+'/'+kind;results[key],raw[key]=structural(rows,SEED+i)
        print(json.dumps({'stage':'structure','cohort':key,'distinct_sequences':results[key]['distinct_sequences'],'p':results[key]['permutation_p']}),flush=True)
    valid=sorted([(v['permutation_p'],key) for key,v in results.items() if v['permutation_p'] is not None])
    bound=0
    for i,(p,key) in enumerate(valid):bound=max(bound,min(1,(len(valid)-i)*p));results[key]['holm_p_all_structural_cohorts']=bound
    dump(destination/'structural-results.json',results);dump(detail/'structural-references.json',raw)
    role_cohorts=defaultdict(list)
    for row in records:
        if row['corpus']=='indus' or not length_range(row['words']):continue
        # Whole-object/source-text cohorts and extensions remain separate.
        if row['kind'] in {'whole_tablet','seal','whole_jar_inscription','whole_document'}:
            role_cohorts[(row['corpus'],'whole')].append(row)
        elif row['kind'] in {'natural_line','source_sentence'}:
            role_cohorts[(row['corpus'],'extension')].append(row)
    roles={}
    for (corpus,kind),rows in sorted(role_cohorts.items()):
        key=corpus+'/'+kind;roles[key],predictions=score_category(rows)
        dump(detail/(key.replace('/','-')+'-categories.json'),predictions)
        print(json.dumps({'stage':'categories','cohort':key,'status':roles[key]['status']}),flush=True)
    dump(destination/'category-results.json',roles)
    ambiguity=lexical(records,[r for r in records if r['corpus']=='indus'])
    dump(destination/'lexical-ambiguity.json',ambiguity)
    dump(destination/'normalization-census.json',json.loads((LOCAL/'normalized-v1/manifest.json').read_text())['census'])
    dump(destination/'output-hashes.json',{p.name:digest(p) for p in sorted(destination.glob('*.json')) if p.name!='output-hashes.json'})
    print(json.dumps({'status':'complete','structural_cohorts':len(results),'category_cohorts':len(roles)}),flush=True)

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'run-v1')
