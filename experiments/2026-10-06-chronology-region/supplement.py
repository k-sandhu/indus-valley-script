"""Post-outcome support-preserving uncertainty and descriptive coverage additions."""
from __future__ import annotations
import argparse, collections, json, math, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
from analyze import Corpus, CORE, EXTERNAL, PERIODS, Model, OWN, RAW, csv, save, ci, effects, common_types, digest

def sampler(c,ids,site):
    comps=collections.defaultdict(list)
    for j,i in enumerate(ids):comps[int(c.pid[i])].append(j)
    cells=collections.defaultdict(list)
    for g,ix in comps.items():
        # Include clear/partial availability so positional cells survive as well.
        signature=tuple(sorted({(c.site[ids[j]] if site else '',c.type[ids[j]],bool(c.clear[ids[j]])) for j in ix}))
        cells[signature].append(g)
    def draw(rng):
        mult=collections.Counter()
        for gs in cells.values():mult.update(rng.choice(gs,len(gs),replace=True).tolist())
        return np.array([mult[int(c.pid[i])] for i in ids],float)
    return draw

def resample_effects(c,primary,rng,B,regional):
    results=[]
    for res in primary:
        a,b=res['comparison'].split('__')
        aa=c.all[(c.region==a)&(c.known>0)] if regional else c.all[(c.site=='Harappa')&(c.major==a)&(c.known>0)]
        bb=c.all[(c.region==b)&(c.known>0)] if regional else c.all[(c.site=='Harappa')&(c.major==b)&(c.known>0)]
        ts=res['common_types'];result={'comparison':res['comparison'],'status':'Exploratory','common_types':ts}
        if not ts:result['reason']='no-common-types';results.append(result);continue
        aa=aa[np.isin(c.type[aa],ts)];bb=bb[np.isin(c.type[bb],ts)]
        da=sampler(c,aa,regional);db=sampler(c,bb,regional)
        modes=[('type_adjusted',False)]+([('site_type_adjusted',True)] if regional else [])
        observed={mode:effects(c,aa,bb,ts,site)[0] for mode,site in modes};boots={mode:collections.defaultdict(list) for mode,_ in modes}
        for _ in range(B):
            wa,wb=da(rng),db(rng)
            for mode,site in modes:
                val,_=effects(c,aa,bb,ts,site,(wa,wb))
                if val:
                    for k,v in val.items():boots[mode][k].append(v)
        for mode,site in modes:
            result[mode]={}
            for key,val in observed[mode].items():
                qq=ci(boots[mode][key]);basic=[max(0,2*val-qq[1]),min(1,2*val-qq[0])] if key.endswith('js_bits') and qq[0] is not None else None
                result[mode][key]={'effect':val if np.isfinite(val) else None,'percentile_interval95':qq,'basic_centered_interval95':basic,'valid_bootstraps':int(np.isfinite(boots[mode][key]).sum())}
        result['a']=c.denom(aa);result['b']=c.denom(bb);results.append(result)
        print('supplement interval',res['comparison'],flush=True)
    return results

def model_intervals(c,preds,rng,B):
    results=[]
    for region in CORE:
        ps=[p for p in preds if p['region']==region]
        if not ps:continue
        ids=np.array([p['i'] for p in ps],int);ts=sorted(set(c.type[ids]));draw=sampler(c,ids,True)
        cols=['type_within','type_other','type_excess','size_within','size_other','size_excess']
        values={k:np.array([p[k] for p in ps]) for k in cols};observed={k:float(np.average(v,weights=c.weights(ids,ts,True))) for k,v in values.items()};boot=collections.defaultdict(list)
        for _ in range(B):
            w=c.weights(ids,ts,True,draw(rng));assert w is not None
            for k,v in values.items():boot[k].append(float(np.average(v,weights=w)))
        results.append({'region':region,'status':'Exploratory','test':c.denom(ids),'supported_types':ts,'losses':{k:{'mean':observed[k],'ci95':ci(boot[k]),'valid_bootstraps':B} for k in cols}})
    return results

def attestation_types(c,out):
    bounds=[];pres=[]
    for t in sorted(set(c.type[c.site=='Harappa'])):
        ids=[i for i,r in enumerate(c.rows) if r['site']=='Harappa' and r['type']==t and r['admissible'] and c.known[i]>0]
        for s in sorted({x for i in ids for x in c.rows[i]['seq'] if x!='000'}):
            bearing=[i for i in ids if s in c.rows[i]['seq']];sets=[c.rows[i]['admissible'] for i in bearing]
            bounds.append({'type':t,'sign':s,'components_bearing_sign':len(set(c.pid[bearing])),'earliest_lo':PERIODS[min(PERIODS.index(x) for a in sets for x in a)],'earliest_hi':PERIODS[min(max(PERIODS.index(x) for x in a) for a in sets)],'latest_lo':PERIODS[max(min(PERIODS.index(x) for x in a) for a in sets)],'latest_hi':PERIODS[max(PERIODS.index(x) for a in sets for x in a)]})
            for p in PERIODS:
                pop=[i for i in ids if c.rows[i]['admissible']==[p]];n=len(set(c.pid[pop]));k=len({c.pid[i] for i in pop if s in c.rows[i]['seq']});z=1.959963984540054
                center=(k/n+z*z/(2*n))/(1+z*z/n) if n else None;delta=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n) if n else None
                pres.append({'type':t,'sign':s,'period':p,'components':n,'components_bearing':k,'wilson95_low':center-delta if n else None,'wilson95_high':center+delta if n else None,'zero_count_upper95':1-.05**(1/n) if n and k==0 else None})
    csv(out/'attestation_by_type.csv',bounds);csv(out/'presence_by_type.csv',pres)

def coverage(c,out,rawout):
    table=[]
    for region in EXTERNAL:
        ids=c.all[c.region==region]
        for site in sorted(set(c.site[ids])):
            ss=ids[c.site[ids]==site]
            for t in sorted(set(c.type[ss])):
                tt=ss[c.type[ss]==t]
                for direction in sorted({c.rows[i]['direction'] for i in tt}):
                    cell=np.array([i for i in tt if c.rows[i]['direction']==direction],int)
                    table.append({'region':region,'site':site,'type':t,'direction':direction,**c.denom(cell)})
    csv(out/'external_coverage.csv',table)
    core=c.all[c.clear & np.isin(c.region,CORE)];ext=c.all[c.clear & np.isin(c.region,EXTERNAL)];bad=set(c.tid[ext]);core=core[~np.isin(c.tid[core],list(bad))]
    raw=Model(c,core);typed={t:Model(c,core[c.type[core]==t]) for t in set(c.type[ext]) if np.sum(c.type[core]==t)>0};pred=[]
    for i in ext:
        p={'i':int(i),'record_id':c.rows[i]['record_id'],'region':c.region[i],'site':c.site[i],'type':c.type[i],'length':int(c.length[i]),'core_type_training_faces':int(np.sum(c.type[core]==c.type[i])),'raw':raw.score(i)}
        p['type_model']=typed[c.type[i]].score(i) if c.type[i] in typed else None;pred.append(p)
    save(rawout/'unpaired_external_predictions.json',pred)
    aggregate=[]
    for t in sorted(set(c.type[ext])):
        ps=[p for p in pred if p['type']==t]
        aggregate.append({'type':t,'external_faces':len(ps),'core_type_training_faces':ps[0]['core_type_training_faces'],'raw_mean_bits_per_sign':float(np.mean([p['raw']['loss_bits_per_sign'] for p in ps])),'type_mean_bits_per_sign':float(np.mean([p['type_model']['loss_bits_per_sign'] for p in ps if p['type_model']])) if any(p['type_model'] for p in ps) else None,'status':'Exploratory; unpaired; model trained on all eligible core'})
    csv(out/'unpaired_external_scores.csv',aggregate)
    # Site-level corroboration has narrower scope than identity/transcription checking.
    check=[]
    for site in sorted(set(c.site[np.isin(c.region,EXTERNAL)])):
        source='';location='';scope='not located in the inspected passages'
        if site in ['Kish','Tell Umma','Ur','Failaka','Altyn Depe','Gonur Depe','Shortughai']:
            source='parpola2018';location='section I.C, author-proof PDF pages 4–6';scope='site/type context corroborated; individual row identity and codes unchecked'
        if site in ['Salut',"Ra's al-Junayz"]:
            source='frenez2023';location='Harappa review image 2 and Oman discussion';scope='Oman context/caption lead; individual row identity and codes unchecked'
        if site=='Susa':source='frenez2023';location='Harappa review image 1 caption Q';scope='Susa cylinder-seal caption lead; individual row identity and codes unchecked'
        check.append({'site':site,'faces':int(np.sum(c.site==site)),'source_id':source,'location':location,'scope':scope})
    csv(out/'external_literature_check.csv',check)

def sequence_summary(c,out):
    a=c.all[(c.site=='Harappa')&(c.major=='3B')&c.clear];b=c.all[(c.site=='Harappa')&(c.major=='3C')&c.clear];ts=common_types(c,a,b)
    result={'status':'Exploratory descriptive summary','common_types':ts,'periods':[]}
    for p,ids in [('3B',a),('3C',b)]:
        h=c.summary(ids);cells=[{'type':t,**c.summary(ids[c.type[ids]==t])} for t in ts]
        result['periods'].append({'period':p,'raw':h,'type_cells':cells,'equal_type_mean_conditional_bigram_entropy_bits':float(np.mean([x['conditional_bigram_entropy_bits'] for x in cells]))})
    save(out/'sequence_summary.json',result)

def main():
    p=argparse.ArgumentParser();p.add_argument('--main',default='main-2026-10-07-v1');p.add_argument('--run',required=True);p.add_argument('--bootstrap',type=int,default=499);a=p.parse_args()
    assert re_safe(a.run);out=OWN/a.run;rawout=RAW/a.run;out.mkdir(exist_ok=False);rawout.mkdir(exist_ok=False)
    start=time.monotonic();c=Corpus();rng=np.random.default_rng(20261007);primary=OWN/a.main
    for theme in ['time','region']:
        data=json.loads((primary/(theme+'_comparisons.json')).read_text())
        save(out/(theme+'_intervals.json'),resample_effects(c,data,rng,a.bootstrap,theme=='region'))
    pred=json.loads((RAW/a.main/'regional_predictions.json').read_text());save(out/'model_intervals.json',model_intervals(c,pred,rng,a.bootstrap))
    attestation_types(c,out);coverage(c,out,rawout);sequence_summary(c,out)
    fold=[{'fold':f,'faces':int(np.sum(c.fold==f)),'observed_slots':int(c.length[c.fold==f].sum()),'clear_faces':int(np.sum(c.clear&(c.fold==f))),'clear_tokens':int(c.length[c.clear&(c.fold==f)].sum())} for f in range(5)]
    save(out/'actual_fold_counts.json',fold)
    assert sum(x['observed_slots'] for x in fold)==19946 and sum(x['clear_faces'] for x in fold)==2930
    save(out/'completion.json',{'status':'Exploratory','seed':20261007,'bootstrap':a.bootstrap,'code_sha256':digest(__file__),'analyzer_sha256':digest(OWN/'analyze.py'),'amendment_sha256':digest(OWN/'AMENDMENT-2026-10-07.md'),'elapsed_seconds':time.monotonic()-start,'files':sorted(x.name for x in out.iterdir()),'local_details':str(rawout.relative_to(c.path.parents[2])).replace('\\','/')})
    print('supplement complete',flush=True)

def re_safe(s):return bool(s) and all(x.isalnum() or x in '-_' for x in s)
if __name__=='__main__':main()
