"""Independent accounting, reference-population and prediction replay checks."""
import argparse, collections, hashlib, itertools, json, math, os, re, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OWN=Path(__file__).resolve().parent;RAW=ROOT/'data/raw/2026-10-06-chronology-region'
for key in ['TMP','TEMP','MPLCONFIGDIR']:os.environ[key]=str(RAW/'tmp')
import pandas as pd

CORE=['Inter-Riverine','Lower Indus','Gujarat/Kutch','Eastern Headwaters','Upper Indus']
EXTERNAL=['Persian Gulf','Mesopotamia','Iranian Plateau','Central Asia']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):assert abs(a-b)<1e-10,(a,b)
def counter(rows):return collections.Counter(s for r in rows for s in r['signs_reading_rtl'] if s!='000')
def dist(rows):
    ct=counter(rows);total=sum(ct.values());return {s:n/total for s,n in ct.items()}
def js(a,b):
    v=0
    for s in set(a)|set(b):
        p=a.get(s,0);q=b.get(s,0);m=(p+q)/2
        if p:v+=.5*p*math.log2(p/m)
        if q:v+=.5*q*math.log2(q/m)
    return v
def standardized(rows,types,sites=False):
    result=collections.defaultdict(float)
    for t in types:
        rr=[r for r in rows if r['type']==t];ss=sorted({r['site'] for r in rr}) if sites else [None]
        for s in ss:
            cell=rr if s is None else [r for r in rr if r['site']==s]
            for k,v in dist(cell).items():result[k]+=v/len(types)/len(ss)
    return dict(result)

class IndependentModel:
    def __init__(self,rows,vocab):
        self.counts=counter(rows);self.total=sum(self.counts.values());self.v=len(vocab)
        self.b=collections.Counter();self.bt=collections.Counter();self.grams={2:set(),3:set()}
        for r in rows:
            ss=r['signs_reading_rtl']
            for a,b in zip(['BOS']+ss,ss):self.b[a,b]+=1;self.bt[a]+=1
            for n in [2,3]:self.grams[n].update(tuple(ss[k:k+n]) for k in range(len(ss)-n+1))
    def score(self,r):
        ss=r['signs_reading_rtl'];loss=[]
        for a,b in zip(['BOS']+ss,ss):
            u=(self.counts[b]+.5)/(self.total+.5*self.v)
            p=(self.b[a,b]+20*u)/(self.bt[a]+20);loss.append(-math.log2(p))
        return sum(loss)/len(ss),loss
    def novelty(self,r,n):
        ss=r['signs_reading_rtl'];grams=[tuple(ss[k:k+n]) for k in range(len(ss)-n+1)]
        return sum(g not in self.grams[n] for g in grams)/len(grams) if grams else None

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='main-2026-10-07-v1');p.add_argument('--output',default='verification-2026-10-07-v1.json');args=p.parse_args()
    dest=OWN/args.output;assert not dest.exists()
    endpoint=OWN/args.run;raw=RAW/args.run;assert (endpoint/'completion.json').exists()
    rows=[json.loads(x) for x in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    members=json.loads((raw/'record_membership.json').read_text());m={x['record_id']:x for x in members};rd={r['record_id']:r for r in rows}
    for r in rows:r.update(m[r['record_id']])
    audit=json.loads((endpoint/'audit.json').read_text());assert len(rows)==audit['population']['faces']==5680
    assert sum(len(r['signs_reading_rtl']) for r in rows)==audit['population']['observed_slots']==19946
    assert sum(r['signs_reading_rtl'].count('000') for r in rows)==audit['population']['unreadable_tokens']==1879
    assert sum(counter(rows).values())==audit['population']['known_tokens']==18067
    vocab=sorted(counter(rows));assert len(vocab)==audit['vocabulary_known_signs']==713
    assert audit['input_sha256']==sha(ROOT/'data/normalized/lipi_observed_faces.jsonl')
    assert audit['code_sha256']==sha(OWN/'analyze.py')
    assert audit['protocol_sha256']==sha(OWN/'PROTOCOL.md')
    assert audit['clarification_sha256']==sha(OWN/'PRECOMPUTATION_CLARIFICATION.md')
    fam=collections.defaultdict(list);seq=collections.defaultdict(list)
    for r in rows:
        fam[r['object_family_id']].append(r)
        s=r['signs_reading_rtl']
        if r['complete_observed'] and r['single_line'] and s and '000' not in s and not r['has_blank_space']:seq[tuple(s)].append(r)
        assert r['clear']==bool(r['complete_observed'] and r['single_line'] and r['direction']=='R/L' and not r['has_blank_space'] and s and '000' not in s)
    for rs in fam.values():assert len({r['physical'] for r in rs})==1 and len({r['fold'] for r in rs})==1
    for rs in seq.values():assert len({r['text_component'] for r in rs})==1 and len({r['fold'] for r in rs})==1
    for filename,keys,selection in [('region_type_sign_counts.csv',['region','type'],rows),('site_type_sign_counts.csv',['site','type'],rows),('harappa_label_type_sign_counts.csv',['time','type'],[r for r in rows if r['site']=='Harappa'])]:
        expected=collections.Counter()
        for r in selection:
            key=tuple(r['metadata']['time'] if k=='time' else r[k] for k in keys)
            for s in r['signs_reading_rtl']:
                if s!='000':expected[key+(s,)]+=1
        frame=pd.read_csv(endpoint/filename,dtype={'sign':str});observed={tuple(rec[k] for k in keys)+(rec['sign'],):int(rec['known_token_count']) for rec in frame.to_dict('records')}
        assert dict(expected)==observed,filename
    recomputed=0
    for theme,file in [('time','time_comparisons.json'),('region','region_comparisons.json')]:
        results=json.loads((endpoint/file).read_text())
        for res in results:
            a,b=res['comparison'].split('__')
            def selected(r,label):return r['site']=='Harappa' and r['periods']==[label] if theme=='time' else r['region']==label
            aa=[r for r in rows if selected(r,a) and any(s!='000' for s in r['signs_reading_rtl'])];bb=[r for r in rows if selected(r,b) and any(s!='000' for s in r['signs_reading_rtl'])]
            assert len(aa)==res['a']['faces'] and len(bb)==res['b']['faces']
            close(js(dist(aa),dist(bb)),res['raw']['frequency_js_bits']['effect']);recomputed+=1
            ts=res['common_types']
            if ts:
                x=[r for r in aa if r['type'] in ts];y=[r for r in bb if r['type'] in ts]
                close(js(standardized(x,ts),standardized(y,ts)),res['type_adjusted']['frequency_js_bits']['effect']);recomputed+=1
                if theme=='region':close(js(standardized(x,ts,True),standardized(y,ts,True)),res['site_type_adjusted']['frequency_js_bits']['effect']);recomputed+=1
    regional=json.loads((raw/'regional_predictions.json').read_text());sample=regional[::max(1,len(regional)//25)]
    core=[r for r in rows if r['clear'] and r['region'] in CORE];model_replays=0
    for rec in sample:
        r=rd[rec['record_id']];f=rec['fold'];reg=rec['region']
        for col,same,typed in [('raw_within',True,False),('raw_other',False,False),('type_within',True,True),('type_other',False,True)]:
            train=[x for x in core if x['fold']!=f and (x['region']==reg)==same and (not typed or x['type']==r['type'])]
            assert r['text_component'] not in {x['text_component'] for x in train}
            close(IndependentModel(train,vocab).score(r)[0],rec[col]);model_replays+=1
    external=json.loads((raw/'external_predictions.json').read_text());exall=[r for r in rows if r['clear'] and r['region'] in EXTERNAL]
    bad={r['text_component'] for r in exall};usable=[r for r in core if r['text_component'] not in bad];external_replays=0
    for rec in external:
        r=rd[rec['record_id']];f=rec['fold'];cell=[x for x in usable if x['type']==r['type'] and len(x['signs_reading_rtl'])==len(r['signs_reading_rtl'])];assert len(cell)>=20
        match=[rd[k] for k in rec['match_ids']];assert len(match)>=2 and len(match)==rec['match_faces']
        assert all(x['fold']==f and x['type']==r['type'] and len(x['signs_reading_rtl'])==len(r['signs_reading_rtl']) and x['region'] in CORE for x in match)
        for mode,typed in [('raw',False),('type',True)]:
            tr=[x for x in usable if x['fold']!=f and (not typed or x['type']==r['type'])];assert not {x['text_component'] for x in tr}&{r['text_component'],*(x['text_component'] for x in match)}
            model=IndependentModel(tr,vocab);score,loss=model.score(r);close(score,rec[mode+'_loss'])
            for a,b in zip(loss,rec[mode+'_token_losses']):close(a,b)
            mean=sum(model.score(x)[0] for x in match)/len(match);close(mean,rec[mode+'_core_loss']);close(score-mean,rec[mode+'_excess'])
            for n in [2,3]:
                nov=model.novelty(r,n)
                if nov is not None:
                    close(nov,rec[mode+f'_novel{n}']);baseline=sum(model.novelty(x,n) for x in match)/len(match);close(baseline,rec[mode+f'_core_novel{n}'])
            external_replays+=1
    tests=json.loads((endpoint/'permutation_tests.json').read_text())
    for t in tests:
        if 'p' in t:assert t['block_margin_checks_passed']==t['permutations']==499 and t['p']>=1/500 and t['holm_p']>=t['p']-1e-12
    acq=json.loads((RAW/'sources-2026-10-06-v1/acquisition.json').read_text());source_checks=0
    for a in acq:
        if 'local_path' in a:
            file=ROOT/a['local_path'];assert file.stat().st_size==a['bytes'] and sha(file)==a['sha256'];source_checks+=1
    result={'status':'Verified computation','run':args.run,'input_accounting':'passed','sign_count_tables_rebuilt':3,'whole_family_and_text_fold_checks':'passed','js_effects_independently_recomputed':recomputed,'regional_prediction_models_independently_replayed':model_replays,'external_prediction_models_independently_replayed':external_replays,'external_match_and_overlap_checks':'passed','source_payload_hashes_checked':source_checks,'permutation_margin_assertions_checked':sum(t.get('block_margin_checks_passed',0) for t in tests),'limitations':['Permutation draws and bootstrap intervals require a full rerun; they are not independently replayed by this checker.','Training-size sensitivity scores are rerunnable but are not independently replayed here.'],'files_sha256':{p.name:sha(p) for p in sorted(endpoint.iterdir()) if p.is_file()}}
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='files_sha256'},indent=2))

if __name__=='__main__':main()
