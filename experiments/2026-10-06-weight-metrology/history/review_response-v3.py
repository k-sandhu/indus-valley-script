"""Post-review extraction audit and Exploratory metrology endpoint.

Run from repository root; source rows and per-object scores remain local.
Reuses parse_catalogue.py, analyze.py and reviewer comparison designs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import time

import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.stats import norm
import analyze as a
from parse_catalogue import ROOT, RAW, RUN, SOURCE, parse, sha, write_json as source_write_json

STATUS = 'Exploratory'
REV = '2026-10-07-review-response-v3'
BASE_ROWS = RAW / 'extraction-v6/catalogue-rows.json'
CANONICAL = dict(zip(a.LOCAL, [7.8, 8.4, 9.4]))
BANDS = [('below-1.3', 0, 1.3), ('1.3-to-5', 1.3, 5), ('5-to-100', 5, 100.0000001), ('above-100', 100.0000001, math.inf)]
SUSA_HARAPPAN = [34,35,81,82,224,233,324,487,499,504,601,628,680,694,698,699,700]
SUSA_WESTERN = [20,70,80,220,530,669]

def write_json(path, obj):
    obj = json.loads(json.dumps(obj, default=lambda v:v.item() if isinstance(v,np.generic) else str(v), allow_nan=False))
    source_write_json(path, obj)

def dimension_screen(rows):
    checked = []; flags = []
    for r in rows:
        if r['shape'] not in ('Cuboid', 'Parallelepiped') or r['mass_g'] is None or r['missing_mass']:
            continue
        dims = {d['axis']: d['value_cm'] for d in r['dimensions']}
        if not all(dims.get(k, 0) > 0 for k in ('L', 'H', 'W')):
            continue
        density = r['mass_g'] / math.prod(dims[k] for k in ('L','H','W'))
        checked.append({'cat':r['cat'], 'box_density_g_cm3':density, 'plus_x':r['missing_mass']})
        if density < 1 or density > 5: flags.append(checked[-1])
    return {'screened_n':len(checked), 'median_box_density_g_cm3':float(np.median([r['box_density_g_cm3'] for r in checked])),
            'flagged_n':len(flags), 'flagged_catalogue_ids':[r['cat'] for r in flags],
            'plus_x_flagged_n':sum(r['plus_x'] for r in flags), 'thresholds_g_cm3':[1,5]}, flags

def extract(out, raw):
    doc, rows = parse(); rows = json.loads(json.dumps(rows))
    old = json.loads(BASE_ROWS.read_text(encoding='utf8'))
    changes = [{'cat':r['cat'], 'fields':[k for k in r if r[k] != old[r['cat']-1][k]]} for r in rows if r != old[r['cat']-1]]
    write_json(raw/'catalogue-rows.json', rows)
    write_json(raw/'field-changes.json', [{'cat':c['cat'], 'changes':{k:{'old':old[c['cat']-1][k], 'new':rows[c['cat']-1][k]} for k in c['fields']}} for c in changes])
    before, bf = dimension_screen(old); after, af = dimension_screen(rows)
    write_json(raw/'dimension-flags.json', {'before':bf,'after':af})
    caption_ids = [r['cat'] for r in old if re.search(r'[pqtus]?Fig\. [456]\.',r['entry_literal'])]
    assert caption_ids == [887,1069,1083,1121,1137,1148,1173]
    assert not any(re.search(r'[pqtus]?Fig\. [456]\.',r['entry_literal']) for r in rows)
    assert rows[1200]['mass_g']==4.44 and rows[1200]['missing_mass']
    assert rows[1729]['mass_g']==1.84 and rows[1729]['primary_eligible']
    assert rows[592]['entry_unit_attribution'] == ['(= 180)']
    assert all(not r['grids'] for r in rows if r['site'] != 'Dholavira')
    assert sum(r['primary_eligible'] and r['site']=='Dholavira' and r['balance_class']=='certain' for r in rows)==298
    audit = {'status':STATUS, 'source_pdf_sha256':sha(SOURCE), 'rows_sha256':sha(raw/'catalogue-rows.json'),
             'catalogue_n':len(rows), 'greater_indus_n':sum(r['cat']>=1121 for r in rows),
             'changed_entries_n':len(changes), 'changed_field_counts':dict(Counter(k for c in changes for k in c['fields'])),
             'changed_entries':changes, 'decimal_comma_corrections':[1201,1730], 'decimal_comma_error_fraction':2/2058,
             'false_grid_entries_n':sum(bool(r['grids']) for r in old if r['site']!='Dholavira'),
             'false_grid_tepe_yahya_n':sum(bool(r['grids']) for r in old if r['site']=='Tepe Yahya'),
             'caption_entry_ids':caption_ids, 'caption_entries_n':len(caption_ids),
             'joint_material_corrections_n':sum(r['material']=='copper/bronze' for r in rows),
             'recovered_numeric_attribution_ids':[593], 'dimension_screen_before':before, 'dimension_screen_after':after,
             'original_random_audit':{'n':60,'pre_repair_period_error_entries':5,'mass_errors_seen':0,
                                     'limit':'Zero observed sample mass errors does not bound the mass error rate at zero; whole-catalogue scan found two decimal-comma errors.'},
             'review_random_audit':{'n':36,'seed':20261011,'witness':'review/row-audit.csv'},
             'frozen_primary_selection_unchanged':True,
             'raw_change_log':(raw/'field-changes.json').relative_to(ROOT).as_posix(),
             'raw_flags':(raw/'dimension-flags.json').relative_to(ROOT).as_posix()}
    write_json(out/'parser-audit.json',audit)
    # Source-selected list, reused from the review's heading-intersection method.
    txt='\n'.join(doc[p].get_text() for p in (183,184,185))
    sec=txt[txt.find('The weights are:'):txt.find('The Western group (Cat. no. 1310')]
    ents=re.findall(r'Cat\. no\. (\d+): ([\d.,]+) g (?:x|÷) ([\d⁄/ ]+?) = ([\d.,]+) g',sec)
    ranges=[(1296,1296),(1303,1303),(1316,1321),(1340,1340),(1657,1657),(1665,1665),(1676,1682),(1696,1699),(1721,1736),(1758,1761),(1763,1764),(1796,1825),(1875,1878),(1881,1884),(1916,1921),(1952,1954),(1965,1966),(1971,1971),(1991,1991),(1999,1999),(2007,2007),(2055,2055)]
    head={i for lo,hi in ranges for i in range(lo,hi+1)}
    book=[{'cat':int(e[0]),'printed_normalized_unit_g':float(e[3].replace(',','.'))} for e in ents if int(e[0]) in head]
    assert len({r['cat'] for r in book})==95
    write_json(raw/'ascalone-dholavira-heavier-list.json', {'source_printed_pages':[169,170,171], 'rows':book})
    write_json(raw/'ascalone-susa-lists.json',{'source_printed_pages':[69,70], 'harappan_ids':SUSA_HARAPPAN, 'western_ids':SUSA_WESTERN,
                                             'proposed_import_ids':[694,698], 'explicit_local_typology_ids':[34,35,81,82,224,233,324,487,499,504,601,628]})
    return rows, book, set(after['flagged_catalogue_ids'])

def fixed_fit(masses, model, unit):
    c=a.MODELS[model][0]; x=np.log(masses)
    def obj(v):return -float(np.log(a.density(x,c,unit,math.exp(v[0]),v[1])).sum())
    opts=[minimize(obj,[math.log(s),.8],bounds=[(math.log(.005),math.log(.2)),(.05,.99)],method='L-BFGS-B',options={'ftol':1e-11}) for s in (.02,.08)]
    b=min(opts,key=lambda r:r.fun); sig=math.exp(b.x[0]);ll=-float(b.fun)
    return {'model':model,'n':len(masses),'unit_g':unit,'sigma_log':sig,'signal_cv_percent':100*math.sqrt(math.expm1(sig**2)),
            'signal_probability':float(b.x[1]),'log_likelihood':ll,'aic':4-2*ll,'parameter_count':2,'unit_fixed':True,
            'unit_at_boundary':False,'sigma_at_boundary':min(abs(sig-.005),abs(sig-.2))<1e-5,
            'signal_at_boundary':min(abs(b.x[1]-.05),abs(b.x[1]-.99))<1e-5,
            'aic_minus_background':4-2*ll+2*len(masses)*math.log(a.BG),'optimizer_success':bool(b.success)}

def custom_fit(masses, kind, cap=.2):
    """Normalized densities in log mass; no variance depending on observed x."""
    x=np.log(masses);c=a.INDUS
    def objective(v):
        if kind=='two-unit':
            u1,u2,s1,s2,w,p=v
            signal=w*a.density(x,c,u1,s1,1)+(1-w)*a.density(x,c,u2,s2,1)
        else:
            u,s,extra,p=v;target=u*c
            if kind=='absolute-error': sd=np.sqrt(s*s+(extra/target)**2);means=np.log(target)
            else: sd=s;means=np.log(target+extra*(target<5))
            signal=norm.pdf(x[:,None],loc=means,scale=sd).mean(axis=1)
        return -float(np.log(p*signal+(1-p)*a.BG).sum())
    if kind=='two-unit':
        bounds=[(12.5,15),(12.5,15),(.005,cap),(.005,cap),(.01,.99),(.05,.99)]
        starts=[[u1,u2,min(s,cap),min(s,cap),.5,.8] for u1 in (13.5,13.7,14) for u2 in (14.3,14.5,14.8) for s in (.015,.03)]
        rng=np.random.default_rng(1)
        starts += [[rng.uniform(12.5,15),rng.uniform(12.5,15),rng.uniform(.005,cap),rng.uniform(.005,cap),rng.uniform(.1,.9),rng.uniform(.5,.9)] for _ in range(30)]
    else:
        bounds=[(12.5,15),(.005,.2),(0,.2 if kind=='absolute-error' else .4),(.05,.99)]
        starts=[[u,s,e,.8] for u in (13.5,13.7,14,14.5) for s in (.015,.05) for e in (0,.05,.15)]
    opts=[minimize(objective,v,bounds=bounds,method='L-BFGS-B',options={'ftol':1e-11,'maxiter':700}) for v in starts]
    b=min(opts,key=lambda r:r.fun);v=list(map(float,b.x));k=len(v)
    if kind=='two-unit' and v[0]>v[1]:v=[v[1],v[0],v[3],v[2],1-v[4],v[5]]
    result={'model':kind,'n':len(masses),'parameter_count':k,'sigma_cap':cap,'log_likelihood':-float(b.fun),'aic':2*k+2*float(b.fun),
            'parameters':v,'optimizer_success':bool(b.success),'successful_starts':sum(r.success for r in opts),'starts':len(opts),
            'boundary_parameters':[i for i,(value,(lo,hi)) in enumerate(zip(v,bounds)) if min(abs(value-lo),abs(value-hi))<1e-5]}
    if kind=='two-unit':result.update(unit1_g=v[0],unit2_g=v[1],cv1_percent=100*math.sqrt(math.expm1(v[2]**2)),cv2_percent=100*math.sqrt(math.expm1(v[3]**2)),unit1_signal_fraction=v[4],signal_probability=v[5])
    else:result.update(unit_g=v[0],sigma_relative=v[1],extra_g=v[2],signal_probability=v[3])
    return result

def comparison(group,unit,units,levels,label,threshold=.03):
    # Same nearest-log rule as the original, now canonical units and optional fractions.
    masses=np.array([r['mass_g'] for r in group]);x=np.log(masses)
    targets=np.concatenate([levels*u for u in units]);res=x[:,None]-np.log(targets)[None,:]
    il=x[:,None]-np.log(unit*a.INDUS)[None,:]; ii=np.argmin(abs(il),axis=1);li=np.argmin(abs(res),axis=1)
    ir=il[np.arange(len(x)),ii];lr=res[np.arange(len(x)),li]
    ie=abs(np.expm1(ir));le=abs(np.expm1(lr));geo=abs(ir)<abs(lr);close=geo&(ie<=threshold)&(le-ie>=.01)
    mix=a.density(x,a.INDUS,unit,.03,.8)>np.max([a.density(x,levels,u,.03,.8) for u in units],axis=0)
    details=[{'cat':r['cat'],'site':r['site'],'indus_error_fraction':float(ie[i]),'best_local_error_fraction':float(le[i]),
              'indus_multiple':float(a.INDUS[ii[i]]),'best_local_unit_g':float(units[li[i]//len(levels)]),
              'best_local_multiple':float(levels[li[i]%len(levels)]),'geometric_preference':bool(geo[i]),'close_preference':bool(close[i]),
              'mixture_preference':bool(mix[i]),'source_printed_pages':r['source_printed_pages']} for i,r in enumerate(group)]
    n=len(group);g=int(geo.sum());k=int(close.sum())
    return {'frame':label,'n':n,'indus_reference_unit_g':unit,'canonical_local_units_g':units,'local_levels':levels.tolist(),
            'close_threshold':threshold,'geometric_preference_n':g,'geometric_preference_fraction':g/n,'geometric_preference_wilson95':a.wilson(g,n),
            'close_preference_n':k,'close_preference_fraction':k/n,'close_preference_wilson95':a.wilson(k,n),
            'mixture_preference_n':int(mix.sum()),'geometric_mixture_disagreement_n':int((mix!=geo).sum()),
            'close_catalogue_ids':[r['cat'] for r in details if r['close_preference']]},details

def nearest_scores(logm, targets):
    # Binary search avoids allocating records x targets for every null draw.
    targets=np.sort(np.log(targets)); pos=np.searchsorted(targets,logm);lo=np.clip(pos-1,0,len(targets)-1);hi=np.clip(pos,0,len(targets)-1)
    lower=logm-targets[lo];upper=logm-targets[hi];signed=np.where(abs(lower)<=abs(upper),lower,upper)
    return abs(signed),abs(np.expm1(signed))

def western_controls(group,reference_configs,legacy_units,draws,raw,out):
    masses=np.array([r['mass_g'] for r in group]);sites=np.array([r['site'] for r in group]);logm=np.log(masses)
    masks={s:sites==s for s in set(sites)}
    def localscore(x,legacy=False):
        if not legacy:return nearest_scores(x,np.concatenate([a.NE*u for u in CANONICAL.values()]))
        lr=np.zeros(len(x));le=lr.copy()
        for s,mask in masks.items():lr[mask],le[mask]=nearest_scores(x[mask],np.concatenate([a.NE*u for u in legacy_units.get(s,CANONICAL).values()]))
        return lr,le
    def counts(x,u,lr,le):
        ir,ie=nearest_scores(x,a.INDUS*u);geo=ir<lr;return [int(geo.sum()),int((geo&(ie<=.03)&(le-ie>=.01)).sum())]
    observed={label:counts(logm,u,*localscore(logm,legacy)) for label,u,legacy in reference_configs}
    rng=np.random.default_rng(20261010);aggregate=[];rawcounts={}
    for method in ('jitter-0.15','jitter-0.35','site-log-uniform'):
        frame={label:[] for label,_,_ in reference_configs}
        for i in range(draws):
            if method.startswith('jitter'):x=logm+rng.uniform(-float(method.split('-')[1]),float(method.split('-')[1]),len(logm))
            else:
                x=np.empty(len(logm))
                for s,mask in sorted(masks.items()):x[mask]=rng.uniform(logm[mask].min(),logm[mask].max(),int(mask.sum()))
            local=localscore(x);oldlocal=localscore(x,True)
            for label,u,legacy in reference_configs:frame[label].append(counts(x,u,*(oldlocal if legacy else local)))
        for label,values in frame.items():
            arr=np.array(values);obs=observed[label]
            aggregate.append({'frame':label,'null':method,'draws':draws,'observed_geometric_n':obs[0],'observed_close_n':obs[1],
                              'geometric_mean':float(arr[:,0].mean()),'close_mean':float(arr[:,1].mean()),
                              'geometric_simulation_interval95':np.quantile(arr[:,0],[.025,.975]).tolist(),
                              'close_simulation_interval95':np.quantile(arr[:,1],[.025,.975]).tolist(),
                              'fraction_ge_observed_geometric':float((arr[:,0]>=obs[0]).mean()),'fraction_ge_observed_close':float((arr[:,1]>=obs[1]).mean())})
        rawcounts[method]=frame
    write_json(raw/'western-null-counts.json',rawcounts)
    sweep=[];summaries=[]
    for legacy in (True,False):
        local=localscore(logm,legacy);frame='legacy-site-fitted' if legacy else 'canonical-7.8-8.4-9.4'
        values=[]
        for u in np.arange(1250,1501)/100:
            g,k=counts(logm,u,*local);record={'frame':frame,'unit_g':float(u),'geometric_n':g,'close_n':k};sweep.append(record);values.append(record)
        summaries.append({'frame':frame,'unit_range_g':[12.5,15],'step_g':.01,'points':251,'close_min':min(r['close_n'] for r in values),
                          'close_max':max(r['close_n'] for r in values),'close_mean':float(np.mean([r['close_n'] for r in values])),
                          'points_close_at_least_18':sum(r['close_n']>=18 for r in values),
                          'fraction_close_at_least_18':sum(r['close_n']>=18 for r in values)/251})
    a.write_csv(out/'western-unit-sweep.csv',sweep,['frame','unit_g','geometric_n','close_n'])
    write_json(out/'western-chance-baselines.json',{'status':STATUS,'controls_status':'Synthetic','seed':20261010,'n':len(group),
                                                  'nulls':aggregate,'sweep_summary':summaries,
                                                  'inference':'These counts give no evidence of Indus-standard weights in the western assemblages.'})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=f'experiments/2026-10-06-weight-metrology/runs/{REV}')
    ap.add_argument('--raw-output',default=f'data/raw/2026-10-06-weight-metrology/{REV}')
    ap.add_argument('--bootstrap',type=int,default=200);ap.add_argument('--monte-carlo',type=int,default=999);ap.add_argument('--null-draws',type=int,default=2000)
    args=ap.parse_args();out=ROOT/args.output;raw=ROOT/args.raw_output
    if out.exists() or raw.exists():raise FileExistsError('Choose new owned/raw output paths')
    out.mkdir(parents=True);raw.mkdir(parents=True);(out/'quantograms').mkdir();start=time.time()
    rows,book,flags=extract(out,raw);print('Corrected rows and parser audit saved',flush=True)
    manifest={'status':STATUS,'date':'2026-10-07','rows_path':(raw/'catalogue-rows.json').relative_to(ROOT).as_posix(),
              'rows_sha256':sha(raw/'catalogue-rows.json'),'protocol_sha256':sha(RUN/'PROTOCOL.md'),
              'code_hashes':{f:sha(RUN/f) for f in ('review_response.py','parse_catalogue.py','analyze.py')},
              'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
              'bootstrap_iterations':args.bootstrap,'mc_simulations':args.monte_carlo,'western_null_draws':args.null_draws,
              'common_quantogram_seed':20261007,'canonical_local_units_g':list(CANONICAL.values()),
              'selection':'Original eligibility/classes/collision exclusions; corrected numeric masses. Density flags are sensitivity exclusions only.'}
    write_json(out/'manifest.json',manifest)
    groups={};counts=[];fits=[];boots={};selections={};strata={}
    for site in sorted(set(r['site'] for r in rows)):
        allsite=[r for r in rows if r['site']==site];west=allsite[0]['cat']<1121
        prim=[r for r in allsite if a.eligible(r) and r['balance_class']!='excluded-related-find' and
              (not west or (r['balance_class'] in ('certain','class-unresolved') and r['cat'] not in a.COLLISIONS))]
        if site=='Dholavira':prim=[r for r in prim if r['balance_class']=='certain']
        counts.append({'site':site,'catalogue_n':len(allsite),'primary_n':len(prim),'classes':dict(Counter(r['balance_class'] for r in allsite))})
        if len(prim)>=8:groups[site]=prim
    write_json(out/'counts.json',{'catalogue_n':2058,'greater_indus_n':938,'sites':counts})
    for idx,(site,group) in enumerate(groups.items()):
        print('Site fits '+site,flush=True);m=[r['mass_g'] for r in group];sitefits=[]
        for model in a.MODELS:
            f=fixed_fit(m,model,CANONICAL[model]) if model in a.LOCAL else a.fit(m,model)
            f.update(a.series_diagnostic(group,f)[0]);f['group']=site;sitefits.append(f)
        best=min(sitefits,key=lambda f:f['aic'])
        for f in sitefits:f['aic_minus_best']=f['aic']-best['aic'];fits.append(f)
        if group[0]['cat']>=1121:
            bs,draw=a.bootstrap(m,'indus_binary_decimal',20261008+idx,args.bootstrap)
            next(f for f in sitefits if f['model']=='indus_binary_decimal')['bootstrap']=bs;boots[site]=draw
        selections[site]=[r['cat'] for r in group]
    write_json(out/'model-comparisons.json',{'status':STATUS,'fits':fits,'note':'Canonical local unit is fixed (two parameters); Indus/binary scales have three parameters.'})
    a.write_csv(out/'model-comparisons.csv',fits,['group','model','n','unit_g','signal_cv_percent','signal_probability','log_likelihood','aic','aic_minus_best','unit_fixed','bootstrap'])
    dh=[r for r in rows if r['site']=='Dholavira' and r['balance_class']!='excluded-related-find'];primary=groups['Dholavira']
    for frame in ('primary','wear','all-complete'):
        framegroup=[r for r in dh if a.eligible(r,frame)]
        strata['Dholavira/all-classes/'+frame]=framegroup
        strata['Dholavira/certain/'+frame]=[r for r in framegroup if r['balance_class']=='certain']
    allprimary=strata['Dholavira/all-classes/primary']
    for label,group in [('certain',primary),('all-classes',allprimary)]:
        for field,keyfun in [('material',a.material_group),('shape',lambda r:r['shape'])]:
            for key in sorted(set(keyfun(r) for r in group)):strata[f'Dholavira/{label}/{field}/{key}']=[r for r in group if keyfun(r)==key]
    fields=[('class',lambda r:r['balance_class']),('area',lambda r:r['area'] or 'unprovided'),('period',lambda r:r['period_stage'] or 'unprovided'),
            ('condition',lambda r:'perfect' if 'perfect' in r['condition_literal'].lower() else 'good')]
    for field,keyfun in fields:
        group=allprimary if field=='class' else primary
        for key in sorted(set(keyfun(r) for r in group)):strata[f'Dholavira/{field}/{key}']=[r for r in group if keyfun(r)==key]
    bandfits=[]
    for idx,(label,lo,hi) in enumerate(BANDS):
        band=[r for r in primary if lo<=r['mass_g']<hi]
        if len(band)<8:continue
        f=a.fit([r['mass_g'] for r in band],'indus_binary_decimal');f.update(a.series_diagnostic(band,f)[0]);f['group']=label
        bs,draw=a.bootstrap([r['mass_g'] for r in band],'indus_binary_decimal',20261020+idx,args.bootstrap);f['bootstrap']=bs;boots[label]=draw;bandfits.append(f)
        strata['Dholavira/band/'+label]=band
        if label in ('1.3-to-5','5-to-100'):
            for field,keyfun in [('material',a.material_group),('shape',lambda r:r['shape'])]+fields[1:]:
                for key in sorted(set(keyfun(r) for r in band)):strata[f'Dholavira/band/{label}/{field}/{key}']=[r for r in band if keyfun(r)==key]
            for frame in ('wear','all-complete'):
                strata[f'Dholavira/band/{label}/{frame}']=[r for r in dh if r['balance_class']=='certain' and a.eligible(r,frame) and lo<=r['mass_g']<hi]
    strata['Dholavira/certain/primary-density-flags-excluded']=[r for r in primary if r['cat'] not in flags]
    strata['Dholavira/all-classes/primary-density-flags-excluded']=[r for r in allprimary if r['cat'] not in flags]
    bookids={r['cat'] for r in book}
    strata['Dholavira/book-heavier-list']=[r for r in primary if r['cat'] in bookids]
    strata['Dholavira/not-in-book-heavier-list']=[r for r in primary if r['cat'] not in bookids]
    sfits=[]
    for name,group in strata.items():
        if len(group)<8:continue
        f=a.fit([r['mass_g'] for r in group],'indus_binary_decimal');f.update(a.series_diagnostic(group,f)[0]);f['group']=name;sfits.append(f)
    write_json(out/'stratified-estimates.json',{'status':STATUS,'fits':sfits,'minimum_n':8,'intervals':'Point estimates only; band bootstraps are in mass-band-estimates.json.'})
    a.write_csv(out/'stratified-estimates.csv',sfits,['group','n','unit_g','signal_cv_percent','signal_probability','within_3_percent_n','unit_at_boundary','sigma_at_boundary'])
    write_json(out/'mass-band-estimates.json',{'status':STATUS,'fits':bandfits,'boundaries':'[0,1.3), [1.3,5), [5,100], (100,infinity)'})
    write_json(raw/'bootstrap-draws.json',boots)
    write_json(raw/'selection-ids.json',{'sites':selections,'strata':{name:[r['cat'] for r in group] for name,group in strata.items() if len(group)>=8}})
    m=[r['mass_g'] for r in primary];base=a.fit(m,'indus_binary_decimal');custom=[]
    for cap in (.2,.05,.03):print('Two-unit cap',cap,flush=True);custom.append(custom_fit(m,'two-unit',cap))
    for model in ('absolute-error','small-target-offset'):custom.append(custom_fit(m,model))
    fixed=fixed_fit(m,'indus_binary_decimal',13.65)
    for f in custom:f['aic_improvement_over_single_unit']=base['aic']-f['aic']
    bandloss=[]
    for label,lo,hi in BANDS:
        band=[r for r in primary if lo<=r['mass_g']<hi]
        if band:
            x=np.log([r['mass_g'] for r in band]);ll1=float(np.log(a.density(x,a.INDUS,base['unit_g'],base['sigma_log'],base['signal_probability'])).sum())
            ll0=float(np.log(a.density(x,a.INDUS,13.65,fixed['sigma_log'],fixed['signal_probability'])).sum())
            bandloss.append({'band':label,'n':len(band),'ll_free':ll1,'ll_fixed':ll0,'ll_loss':ll1-ll0})
    a.MODELS['indus-extra-fractions']=(np.array(sorted(set(a.INDUS.tolist()+[1/6,1/12,1/24]))),(12.5,15))
    ext=a.fit(m,'indus-extra-fractions');rng=np.random.default_rng(20261012);deltas=[]
    for i in range(120):
        a.MODELS['random-extra-fractions']=(np.array(sorted(a.INDUS.tolist()+np.exp(rng.uniform(math.log(1/32),math.log(4),3)).tolist())),(12.5,15))
        deltas.append(a.fit(m,'random-extra-fractions')['log_likelihood']-base['log_likelihood'])
    delta=ext['log_likelihood']-base['log_likelihood']
    write_json(raw/'random-extra-levels-gains.json',deltas)
    write_json(out/'dholavira-model-tests.json',{'status':STATUS,'single_unit':base,'fixed_13_65':fixed,'log_likelihood_loss_by_band':bandloss,'alternative_models':custom,
              'extra_fractions':ext,'extra_fractions_ll_gain':delta,'random_extra_levels':{'status':'Synthetic','seed':20261012,'draws':120,'ll_gain_mean':float(np.mean(deltas)),
              'll_gain_percentile95':float(np.quantile(deltas,.95)),'ll_gain_max':max(deltas),'fraction_ge_declared_gain':float(np.mean(np.array(deltas)>=delta))},
              'book_heavier_list':{'enumerated_n':len(book),'mean_printed_normalized_unit_g':float(np.mean([r['printed_normalized_unit_g'] for r in book])),
              'primary_members_n':sum(r['cat'] in bookids for r in primary),'primary_small_band_members_n':sum(r['cat'] in bookids and 1.3<=r['mass_g']<5 for r in primary),
              'source_printed_pages':[169,170,171],'selection_limit':'Book group was selected metrologically; conditional partitions cannot establish regional origin.'}})
    residuals=[]
    for unit in (13.65,13.70):
        mass=np.array(m);ix=np.argmin(abs(np.log(mass[:,None]/(a.INDUS*unit)[None,:])),axis=1)
        for j in sorted(set(ix)):
            v=mass[ix==j]-a.INDUS[j]*unit
            residuals.append({'reference_unit_g':unit,'multiple':float(a.INDUS[j]),'n':len(v),'target_mass_g':float(a.INDUS[j]*unit),
                              'median_signed_offset_g':float(np.median(v)),'median_signed_relative_percent':float(100*np.median(v)/(a.INDUS[j]*unit)),
                              'positive_n':int((v>0).sum()),'negative_n':int((v<0).sum())})
    write_json(out/'denomination-residuals.json',{'status':STATUS,'strata':residuals,'assignment':'Nearest log denomination at fixed reference; not historical attribution.'})
    qgroups=list(groups.items())+[('Dholavira all classes',allprimary)]+[(label,strata['Dholavira/band/'+label]) for label in ('1.3-to-5','5-to-100')]
    quant=[]
    for name,group in qgroups:print('Quantogram',name,flush=True);quant.append(a.quantogram(group,20261007,args.monte_carlo,out/'quantograms',a.re_slug(name)))
    write_json(out/'quantogram-peaks.json',{'status':STATUS,'controls_status':'Synthetic','samples':quant})
    west=[r for r in rows if r['cat']<1121 and a.eligible(r) and r['balance_class'] in ('certain','class-unresolved') and r['cat'] not in a.COLLISIONS]
    heavy=next(f['unit_g'] for f in bandfits if f['group']=='5-to-100');oldunit=14.002900605263344
    units=list(CANONICAL.values());extended=units+[7.83,8.36,11.75];fractions=np.array(sorted(set(a.NE.tolist()+[1/24,1/12,1/6,1/5,1/3,2/3,5/6])))
    configs=[('canonical-13.65',13.65,units,a.NE),('canonical-mass-band-reference',heavy,units,a.NE),('canonical-old-pooled-reference',oldunit,units,a.NE),
             ('extended-units-13.65',13.65,extended,a.NE),('extended-fractions-13.65',13.65,extended,fractions),
             ('extended-fractions-mass-band-reference',heavy,extended,fractions),('gulf-overlap-13.65',13.65,extended+[13.5],fractions)]
    western=[];detailsby={}
    for name,unit,us,cs in configs:
        result,details=comparison(west,unit,us,cs,name);western.append(result);detailsby[name]=details;write_json(raw/f'western-{name}.json',details)
    for threshold in (.02,.05):
        name=f'canonical-13.65-threshold-{threshold}';result,details=comparison(west,13.65,units,a.NE,name,threshold);western.append(result);write_json(raw/f'western-{name}.json',details)
    write_json(out/'western-compatibility.json',{'status':STATUS,'comparisons':western,'interpretation':'These counts give no evidence of Indus-standard weights in the western assemblages.',
              'interval_scope':'Wilson intervals describe the selected records at fixed standards; they do not estimate import prevalence.'})
    primarydetails=detailsby['canonical-13.65'];hits=[r for r in primarydetails if r['close_preference']]
    assert 220 not in [r['cat'] for r in hits]
    write_json(out/'western-screen-objects.json',{'status':STATUS,'selection':'Canonical 13.65 g; close-screen objects requiring archaeological follow-up. No Indus provenance inferred.',
              'objects':hits})
    allsusagroup=[r for r in rows if r['cat'] in SUSA_HARAPPAN]
    _,susadetails=comparison(allsusagroup,13.65,units,a.NE,'book-list-all-conditions')
    write_json(raw/'ascalone-susa-list-scores.json',susadetails)
    selected={r['cat'] for r in west};bookcomparison=[]
    for name,_,_,_ in configs:
        ds=detailsby[name];present=[r for r in ds if r['cat'] in SUSA_HARAPPAN]
        bookcomparison.append({'frame':name,'book_harappan_n':17,'book_harappan_eligible_n':len(present),'book_harappan_geometric_n':sum(r['geometric_preference'] for r in present),
                               'book_harappan_close_n':sum(r['close_preference'] for r in present),'book_harappan_close_ids':[r['cat'] for r in present if r['close_preference']],
                               'screen_close_susa_n':sum(r['close_preference'] and r['site']=='Susa' for r in ds),
                               'book_western_eligible_n':sum(i in selected for i in SUSA_WESTERN),
                               'book_western_close_ids':[r['cat'] for r in ds if r['close_preference'] and r['cat'] in SUSA_WESTERN]})
    write_json(out/'ascalone-susa-comparison.json',{'status':STATUS,'source_printed_pages':[69,70],'comparisons':bookcomparison,
              'ineligible_book_harappan_ids':[i for i in SUSA_HARAPPAN if i not in selected],
              'cat_220_canonical_score':next(r for r in primarydetails if r['cat']==220),
              'book_proposed_imports':[694,698], 'explicit_local_typology_count':12,
              'note':'Book lists include different shapes, fractions and conditions. This screen is not a reproduction or disproof of archaeological attributions.'})
    legacy=json.loads((RUN/'runs/2026-10-06-main/model-comparisons.json').read_text())['local_units']
    print('Western chance controls',flush=True)
    western_controls(west,[('legacy-frozen-rule',oldunit,True),('canonical-13.65',13.65,False),('canonical-mass-band-reference',heavy,False)],legacy,args.null_draws,raw,out)
    frozen=json.loads((RUN/'history/2026-10-07-before-review-response/frozen-hashes.json').read_text())
    assert all(sha(RUN/'runs/2026-10-06-main'/f)==h for f,h in frozen.items())
    write_json(out/'completion.json',{'status':STATUS,'computation_status':'Verified computation','elapsed_seconds':time.time()-start,'site_groups':len(groups),
              'site_model_fits':len(fits),'stratum_fits':len(sfits),'bootstrap_refits':sum(map(len,boots.values())),'quantogram_groups':len(quant),
              'nonconverged_site_fits':sum(not f['optimizer_success'] for f in fits),'frozen_files_unchanged':len(frozen),
              'output_hashes':{p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}})
    print('Completed',out,flush=True)

if __name__=='__main__':main()
