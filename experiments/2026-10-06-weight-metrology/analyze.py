"""Frozen mass-series fits, stratified summaries and cosine quantograms.

Rerun from repository root; always choose a fresh endpoint directory.
Per-object assignments and bootstrap draws remain local-only.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import json
import math
import os
from pathlib import Path
import platform
import time
from parse_catalogue import ROOT, RAW, RUN, sha, write_json
from validation_audit import wilson
import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.signal import find_peaks

INDUS = np.array([1/32,1/16,1/8,1/4,1/2,1,2,4,10,12.5,20,40,100,200,400,1000])
BINARY = 2.0 ** np.arange(-5,11)
NE = np.array([1/8,1/4,1/2,1,2,3,4,5,6,8,10,12,15,20,30,40,50,60,100,120,150,180,240,300,600,1200,1800])
MODELS = {'indus_binary_decimal':(INDUS,(12.5,15.0)), 'pure_binary':(BINARY,(12.5,15.0)),
          'shekel_7_8':(NE,(7.4,8.0)), 'shekel_8_4':(NE,(8.1,8.7)), 'shekel_9_4':(NE,(9.1,9.7))}
LOCAL = ['shekel_7_8','shekel_8_4','shekel_9_4']
BG = 1 / math.log(100000/.01)
COLLISIONS = {119,120,129}
DISAGREEMENTS = {224,598,603}

def density(x, c, unit, sigma, p):
    residual = x[:,None] - np.log(c)[None,:] - math.log(unit)
    comp = np.exp(-.5*(residual/sigma)**2)/(sigma*math.sqrt(2*math.pi)*len(c))
    return p*comp.sum(axis=1)+(1-p)*BG

def fit(masses, model):
    c, bounds = MODELS[model]
    values, counts = np.unique(np.log(np.asarray(masses)),return_counts=True)
    residual_base = values[:,None]-np.log(c)[None,:]
    def objective(v):
        mu, ls, p = v; sigma = math.exp(ls)
        residual = residual_base-mu
        norm = np.exp(-.5*(residual/sigma)**2)/(sigma*math.sqrt(2*math.pi)*len(c))
        f = p*norm.sum(axis=1)+(1-p)*BG
        comp_post = p*norm/f[:,None]
        signal_post = comp_post.sum(axis=1)
        grad_mu = (comp_post*residual/sigma**2).sum(axis=1)
        grad_ls = (comp_post*((residual/sigma)**2-1)).sum(axis=1)
        grad_p = signal_post/p-(1-signal_post)/(1-p)
        return -float(np.dot(counts,np.log(f))), -np.array([np.dot(counts,grad_mu),np.dot(counts,grad_ls),np.dot(counts,grad_p)])
    limits=[(math.log(bounds[0]),math.log(bounds[1])),(math.log(.005),math.log(.20)),(.05,.99)]
    candidates=[]
    for u in np.linspace(*bounds,5):
        for sigma in [.02,.08]:
            opt=minimize(objective,[math.log(u),math.log(sigma),.8],method='L-BFGS-B',jac=True,
                         bounds=limits,options={'ftol':1e-10,'gtol':1e-6,'maxiter':300})
            candidates.append(opt)
    best=min(candidates,key=lambda a:a.fun)
    unit=math.exp(best.x[0]); sigma=math.exp(best.x[1]); p=float(best.x[2])
    n=len(masses); ll=-float(best.fun)
    return {'model':model,'n':n,'unit_g':unit,'sigma_log':sigma,
            'signal_cv_percent':100*math.sqrt(math.expm1(sigma*sigma)), 'signal_probability':p,
            'log_likelihood':ll,'aic':6-2*ll, 'background_aic':-2*n*math.log(BG),
            'aic_minus_background':6-2*ll+2*n*math.log(BG),
            'unit_at_boundary':min(abs(unit-bounds[0]),abs(unit-bounds[1]))<.0001,
            'sigma_at_boundary':min(abs(sigma-.005),abs(sigma-.20))<.00001,
            'signal_at_boundary':min(abs(p-.05),abs(p-.99))<.00001,
            'optimizer_success':bool(best.success),'optimizer_message':str(best.message),
            'starts':10, 'successful_starts':sum(bool(a.success) for a in candidates)}

def bootstrap(masses, model, seed, iterations):
    rng=np.random.default_rng(seed); draws=[]
    masses=np.array(masses)
    for i in range(iterations):
        r=fit(rng.choice(masses,len(masses),replace=True),model)
        draws.append({k:r[k] for k in ['unit_g','signal_cv_percent','signal_probability','unit_at_boundary','sigma_at_boundary','optimizer_success']})
    return {'iterations':iterations,'seed':seed,'unit_ci95_g':np.quantile([r['unit_g'] for r in draws],[.025,.975]).tolist(),
            'signal_cv_ci95_percent':np.quantile([r['signal_cv_percent'] for r in draws],[.025,.975]).tolist(),
            'signal_probability_ci95':np.quantile([r['signal_probability'] for r in draws],[.025,.975]).tolist(),
            'unit_boundary_draws':sum(r['unit_at_boundary'] for r in draws),
            'sigma_boundary_draws':sum(r['sigma_at_boundary'] for r in draws),
            'unsuccessful_draws':sum(not r['optimizer_success'] for r in draws)},draws

def material_group(row):
    mat=row['material'] or 'unprovided'
    if 'chert' in mat: return 'chert'
    if mat in ('clay','terracotta','shell','copper','bronze','silver','lead','bone','faience','bitumen'): return 'non-stone'
    if mat in ('unprovided','gate'): return 'unresolved'
    return 'other-stones'

def eligible(row, frame='primary'):
    if row['mass_g'] is None or row['mass_g']<=0 or row['missing_mass']: return False
    if frame=='primary': return row['primary_eligible']
    if frame=='wear': return not row['damage'] and (row['intact_condition'] or row['worn'])
    if frame=='all-complete': return True
    raise ValueError(frame)

def series_diagnostic(group, result):
    c=MODELS[result['model']][0]; u=result['unit_g']
    masses=np.array([r['mass_g'] for r in group]); x=np.log(masses)
    res=x[:,None]-np.log(u*c)[None,:]; ix=np.argmin(abs(res),axis=1)
    signed=res[np.arange(len(masses)),ix]
    percent=100*abs(np.expm1(signed))
    return {'nearest_error_median_percent':float(np.median(percent)),
            'nearest_error_p90_percent':float(np.quantile(percent,.9)),
            'within_3_percent_n':int((percent<=3).sum()),
            'within_3_percent_fraction':float((percent<=3).mean()),
            'denomination_assignment_counts':{str(c[i]):int((ix==i).sum()) for i in sorted(set(ix))}},

def write_csv(path, rows, fields):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader()
        w.writerows({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v) for k,v in r.items()} for r in rows)

def quantogram(group, seed, simulations, out, name):
    selected=[r for r in group if r['mass_g']<=100]
    if len(selected)<8: return {'group':name,'n':len(selected),'status':'Proposed: below eight-object minimum'}
    masses=np.array([r['mass_g'] for r in selected]); n=len(masses)
    q=np.arange(40,1501)/100.0
    observed=np.cos(2*np.pi*masses[:,None]/q[None,:]).sum(axis=0)*math.sqrt(2/n)
    rng=np.random.default_rng(seed); sims=np.empty((simulations,len(q)))
    for i in range(simulations):
        perturbed=masses*np.exp(rng.uniform(-.15,.15,n))
        sims[i]=np.cos(2*np.pi*perturbed[:,None]/q[None,:]).sum(axis=0)*math.sqrt(2/n)
    maxima=sims.max(axis=1); global95=float(np.quantile(maxima,.95))
    point95=np.quantile(sims,.95,axis=0)
    peaks=list(find_peaks(observed,distance=20)[0])
    # The search endpoints are explicitly eligible maxima as well.
    if observed[0]>observed[1]: peaks.append(0)
    if observed[-1]>observed[-2]: peaks.append(len(q)-1)
    peaks=sorted(peaks,key=lambda i:observed[i],reverse=True)[:5]
    grid=[{'q_g':float(a),'q_observed':float(b),'pointwise_mc95':float(c),'global_mc95':global95} for a,b,c in zip(q,observed,point95)]
    write_csv(out/f'{name}.csv',grid,['q_g','q_observed','pointwise_mc95','global_mc95'])
    return {'group':name,'n':n,'mass_cap_g':100,'seed':seed,'simulations':simulations,
            'q_range_g':[.4,15],'step_g':.01,'maximum_q_g':float(q[observed.argmax()]),
            'maximum_q_score':float(observed.max()),'global_mc95':global95,
            'global_mc_p':(1+int((maxima>=observed.max()).sum()))/(simulations+1),
            'score_at_13_65':float(observed[np.where(q==13.65)[0][0]]),
            'top_separated_peaks':[{'quantum_g':float(q[i]),'score':float(observed[i])} for i in peaks],
            'grid_file':f'quantograms/{name}.csv'}

def western_compare(group, indus_unit, local_units, label, threshold=.03):
    details=[]
    for row in group:
        x=math.log(row['mass_g'])
        def nearest(c,u):
            ix=int(np.argmin(abs(x-np.log(c*u)))); signed=x-math.log(c[ix]*u)
            return abs(signed),abs(math.expm1(signed)),float(c[ix])
        i_log,i_error,i_mult=nearest(INDUS,indus_unit)
        units=local_units.get(row['site'],dict(zip(LOCAL,[7.8,8.4,9.4])))
        alternatives=[(model,*nearest(NE,units[model])) for model in LOCAL]
        winner=min(alternatives,key=lambda r:r[1]); l_log,l_error,l_mult=winner[1:]
        geometric=i_log<l_log
        close=geometric and i_error<=threshold and l_error-i_error>=.01
        indus_density=density(np.array([x]),INDUS,indus_unit,.03,.8)[0]
        western_density=max(density(np.array([x]),NE,units[model],.03,.8)[0] for model in LOCAL)
        details.append({'cat':row['cat'],'site':row['site'],'indus_error_fraction':i_error,
                        'best_local_error_fraction':l_error,'best_local_model':winner[0],
                        'indus_multiple':i_mult,'best_local_multiple':l_mult,
                        'geometric_preference':bool(geometric),'close_preference':bool(close),
                        'mixture_preference':bool(indus_density>western_density),
                        'mixture_log_density_advantage':float(math.log(indus_density/western_density)),
                        'source_printed_pages':row['source_printed_pages']})
    n=len(group); k=sum(r['geometric_preference'] for r in details); c=sum(r['close_preference'] for r in details)
    mix=sum(r['mixture_preference'] for r in details)
    discord=sum(r['geometric_preference']!=r['mixture_preference'] for r in details)
    bysite=[]
    for site in sorted(set(r['site'] for r in details)):
        g=[r for r in details if r['site']==site]; ns=len(g); cs=sum(r['close_preference'] for r in g)
        bysite.append({'site':site,'n':ns,'geometric_preference_n':sum(r['geometric_preference'] for r in g),
                       'close_preference_n':cs,'close_preference_fraction':cs/ns,
                       'close_preference_wilson95':wilson(cs,ns),'mixture_preference_n':sum(r['mixture_preference'] for r in g)})
    result={'frame':label,'n':n,'indus_reference_unit_g':indus_unit,'close_threshold':threshold,
            'geometric_preference_n':k,'geometric_preference_fraction':k/n,'geometric_preference_wilson95':wilson(k,n),
            'close_preference_n':c,'close_preference_fraction':c/n,'close_preference_wilson95':wilson(c,n),
            'mixture_preference_n':mix,'mixture_preference_fraction':mix/n,'mixture_preference_wilson95':wilson(mix,n),
            'geometric_mixture_disagreement_n':discord,'site_counts':bysite,
            'driving_catalogue_ids':[r['cat'] for r in details if r['close_preference']]}
    return result,details

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/runs/2026-10-06-main')
    ap.add_argument('--raw-output',default='data/raw/2026-10-06-weight-metrology/main')
    ap.add_argument('--rows',default='data/raw/2026-10-06-weight-metrology/extraction-v6/catalogue-rows.json')
    ap.add_argument('--bootstrap',type=int,default=200); ap.add_argument('--monte-carlo',type=int,default=999)
    args=ap.parse_args(); out=ROOT/args.output; raw=ROOT/args.raw_output; rowpath=ROOT/args.rows
    if out.exists() or raw.exists(): raise FileExistsError('Choose new endpoint paths')
    rows=json.loads(rowpath.read_text(encoding='utf-8'))
    assert len(rows)==2058 and [r['cat'] for r in rows]==list(range(1,2059))
    out.mkdir(parents=True); raw.mkdir(parents=True); (out/'quantograms').mkdir()
    start=time.time()
    meta={'status':'Frozen evaluation','endpoint_created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
          'source_rows_path':args.rows,'source_rows_sha256':sha(rowpath),'analysis_sha256':sha(Path(__file__)),
          'protocol_sha256':sha(RUN/'PROTOCOL.md'),'python':platform.python_version(),'numpy':np.__version__,
          'scipy':scipy.__version__,'bootstrap_iterations':args.bootstrap,'mc_simulations':args.monte_carlo,
          'models':{k:{'multiples':v[0].tolist(),'unit_range_g':list(v[1])} for k,v in MODELS.items()},
          'background_log_density':BG}
    write_json(out/'manifest.json',meta)
    site_counts=[]; site_groups={}
    for site in sorted(set(r['site'] for r in rows)):
        allsite=[r for r in rows if r['site']==site]
        western=allsite[0]['cat']<1121
        primary=[r for r in allsite if eligible(r) and r['balance_class']!='excluded-related-find'
                 and (not western or (r['balance_class'] in ('class-unresolved','certain') and r['cat'] not in COLLISIONS))]
        if site=='Dholavira': primary=[r for r in primary if r['balance_class']=='certain']
        site_counts.append({'site':site,'catalogue_n':len(allsite),'primary_n':len(primary),
                            'mass_missing_n':sum(r['mass_g'] is None for r in allsite),
                            'plus_x_n':sum(r['missing_mass'] for r in allsite),
                            'balance_classes':dict(Counter(r['balance_class'] for r in allsite))})
        if len(primary)>=8: site_groups[site]=primary
    write_json(out/'counts.json',{'sites':site_counts,'catalogue_n':2058,'greater_indus_n':938})
    comparisons=[]; point_fits={}; local_units={}; boot_details={}
    for idx,(site,group) in enumerate(site_groups.items()):
        print(f'Fitting {site}: n={len(group)}',flush=True)
        fits=[]; masses=[r['mass_g'] for r in group]
        for model in MODELS:
            result=fit(masses,model); result.update(series_diagnostic(group,result)[0]); result['group']=site
            fits.append(result)
        winner=min(fits,key=lambda r:r['aic']); point_fits[site]={r['model']:r for r in fits}
        western=group[0]['cat']<1121
        target=min((r for r in fits if r['model'] in LOCAL),key=lambda r:r['aic']) if western else point_fits[site]['indus_binary_decimal']
        bs,draws=bootstrap(masses,target['model'],20261008+idx,args.bootstrap)
        target['bootstrap']=bs; boot_details[site]=draws
        if western: local_units[site]={m:point_fits[site][m]['unit_g'] for m in LOCAL}
        for result in fits:
            result['aic_minus_best']=result['aic']-winner['aic']
            comparisons.append(result)
        print(f'Completed {site}; best={winner["model"]}',flush=True)
    write_json(out/'model-comparisons.json',{'fits':comparisons,'local_units':local_units})
    write_csv(out/'model-comparisons.csv',comparisons,['group','model','n','unit_g','signal_cv_percent','signal_probability','aic','aic_minus_best','aic_minus_background','within_3_percent_n','within_3_percent_fraction','unit_at_boundary','sigma_at_boundary','signal_at_boundary','bootstrap'])
    write_json(raw/'bootstrap-draws.json',boot_details)
    dh=[r for r in rows if r['site']=='Dholavira' and r['balance_class']!='excluded-related-find']
    strata=[]; assignments=[]
    strata_groups={}
    for frame in ['primary','wear','all-complete']:
        allgroup=[r for r in dh if eligible(r,frame)]
        strata_groups[f'Dholavira/all-classes/{frame}']=allgroup
        certain=[r for r in allgroup if r['balance_class']=='certain']
        strata_groups[f'Dholavira/certain/{frame}']=certain
    certain=[r for r in dh if eligible(r) and r['balance_class']=='certain']
    allprimary=[r for r in dh if eligible(r)]
    for frame_name,frame in [('certain',certain),('all-classes',allprimary)]:
        for field,keyfun in [('material',material_group),('shape',lambda r:r['shape'])]:
            keys=sorted(set(keyfun(r) for r in frame))
            for key in keys:
                strata_groups[f'Dholavira/{frame_name}/{field}/{key}']=[r for r in frame if keyfun(r)==key]
    for field,keyfun in [('class',lambda r:r['balance_class']),('area',lambda r:r['area'] or 'unprovided'),
                         ('period',lambda r:r['period_stage'] or 'unprovided'),
                         ('condition',lambda r:'perfect' if 'perfect' in r['condition_literal'].lower() else 'good')]:
        frame=allprimary if field=='class' else certain
        for key in sorted(set(keyfun(r) for r in frame)):
            strata_groups[f'Dholavira/{field}/{key}']=[r for r in frame if keyfun(r)==key]
    for name,group in strata_groups.items():
        if len(group)<8: continue
        result=fit([r['mass_g'] for r in group],'indus_binary_decimal')
        result.update(series_diagnostic(group,result)[0]); result['group']=name; strata.append(result)
        c=INDUS; res=np.log([r['mass_g'] for r in group])[:,None]-np.log(c*result['unit_g'])[None,:]
        ix=np.argmin(abs(res),axis=1)
        for row,i in zip(group,ix): assignments.append({'group':name,'cat':row['cat'],'assigned_multiple':float(c[i]),'unit_g':result['unit_g']})
    write_json(out/'stratified-estimates.json',{'fits':strata,'minimum_n':8,'bootstrap':'point estimates only'})
    write_csv(out/'stratified-estimates.csv',strata,['group','n','unit_g','signal_cv_percent','signal_probability','within_3_percent_n','within_3_percent_fraction','nearest_error_median_percent','nearest_error_p90_percent','unit_at_boundary','sigma_at_boundary'])
    write_json(raw/'stratum-assignments.json',assignments)
    west=[r for r in rows if r['cat']<1121 and eligible(r) and r['balance_class'] in ('class-unresolved','certain') and r['cat'] not in COLLISIONS]
    reference=point_fits['Dholavira']['indus_binary_decimal']['unit_g']
    configs=[('primary',west,reference,.03),('threshold-2-percent',west,reference,.02),
             ('threshold-5-percent',west,reference,.05),('canonical-13-65',west,13.65,.03),
             ('remove-source-disagreements',[r for r in west if r['cat'] not in DISAGREEMENTS],reference,.03),
             ('expanded-uncertain-classes',[r for r in rows if r['cat']<1121 and eligible(r) and r['cat'] not in COLLISIONS],reference,.03)]
    western=[]; driving=[]
    for name,group,unit,threshold in configs:
        result,details=western_compare(group,unit,local_units,name,threshold); western.append(result)
        write_json(raw/f'western-{name}.json',details)
        if name=='primary': driving=[{k:r[k] for k in ['cat','site','indus_error_fraction','best_local_error_fraction','best_local_model','indus_multiple','mixture_preference','source_printed_pages']} for r in details if r['close_preference']]
    write_json(out/'western-compatibility.json',{'comparisons':western,'local_units':local_units,
               'interval_scope':'Wilson binomial intervals conditional on recorded sample, fitted units and fixed denominations; no fit-parameter uncertainty propagated'})
    write_json(out/'western-driving-objects.json',{'selection':'primary close preference <=3% error and >=1 percentage-point advantage', 'objects':driving})
    quant=[]
    for idx,(site,group) in enumerate(site_groups.items()):
        name=re_slug(site)
        print(f'Quantogram {site}',flush=True)
        quant.append(quantogram(group,20261007+idx,args.monte_carlo,out/'quantograms',name))
    quant.append(quantogram(allprimary,20261099,args.monte_carlo,out/'quantograms','dholavira-all-classes'))
    write_json(out/'quantogram-peaks.json',{'status':'Frozen evaluation with Synthetic Monte Carlo controls','samples':quant})
    write_json(raw/'selection-ids.json',{'site_primary_ids':{s:[r['cat'] for r in g] for s,g in site_groups.items()},
                                       'stratum_ids':{s:[r['cat'] for r in g] for s,g in strata_groups.items() if len(g)>=8},
                                       'western_primary_ids':[r['cat'] for r in west]})
    write_json(out/'completion.json',{'status':'Verified computation','elapsed_seconds':time.time()-start,
                                    'site_fit_groups':len(site_groups),'model_fits':len(comparisons),
                                    'stratum_fits':len(strata),'quantogram_groups':len(quant),
                                    'bootstrap_refits':len(site_groups)*args.bootstrap,
                                    'nonconverged_main_fits':sum(not r['optimizer_success'] for r in comparisons),
                                    'raw_derivatives_path':args.raw_output,
                                    'output_hashes':{p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}})
    print('Completed endpoint '+str(out),flush=True)

def re_slug(text):
    import re
    return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')

if __name__=='__main__': main()
