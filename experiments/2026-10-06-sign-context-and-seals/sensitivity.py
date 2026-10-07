"""Post-outcome sensitivities specified in AMENDMENT-2026-10-07.md."""
import argparse, json, time
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
import analyze as main

def correlations(Y,N,expected,labels,selected,area):
    R=[]
    for k in selected:
        ix=labels==k
        R.append((Y[ix]-expected[ix]).sum(0)/N[ix].sum())
    R=np.apply_along_axis(rankdata,0,np.array(R)); R-=R.mean(0)
    ar=rankdata(np.log2(area)); ar-=ar.mean()
    den=np.sqrt((ar@ar)*(R*R).sum(0))
    return np.divide(ar@R,den,out=np.zeros(Y.shape[1]),where=den>0)

def run():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',default='exploratory-2026-10-07-01'); args=ap.parse_args()
    out=main.OWN/args.run; raw=main.RAW/args.run
    if out.exists() or raw.exists(): raise FileExistsError('Use a fresh run directory.')
    out.mkdir(); raw.mkdir(); start=time.time(); rng=np.random.default_rng(2026100702); B=9999
    rows=[json.loads(l) for l in main.INPUT.read_text(encoding='utf-8').splitlines()]
    groups,principal,seals,_=main.grouping(rows)
    original=json.loads((main.OWN/'run-2026-10-07-01/input-summary.json').read_text(encoding='utf-8'))
    signs=original['top_signs']; rr=[r for r in principal if any(s!='000' for s in r['signs_reading_rtl'])]
    Y,N=main.counts(rr,signs); strata=main.blocks([r['object_type'] for r in rr]); P=np.zeros_like(Y)
    for ix in strata: P[ix]=Y[ix].sum(0)/N[ix].sum()
    expected=N[:,None]*P
    site_names=sorted({r['site'] for r in rr}); labels=np.array([site_names.index(r['site']) for r in rr])
    table=json.loads((main.OWN/'site-table.json').read_text(encoding='utf-8')); tab={v['site']:v for v in table['sites']}
    comparisons={}; settings=[]
    for minimum in [3,20]:
        ss=[s for s in site_names if s in tab and sum(r['site']==s for r in rr)>=minimum]
        indices=[site_names.index(s) for s in ss]; areas=[tab[s]['area_reference'] for s in ss]
        ob=correlations(Y,N,expected,labels,indices,areas)
        settings.append((ss,indices,areas,ob,minimum))
    null=np.empty((B,2,len(signs)))
    for b in range(B):
        lab=main.shuffle(labels,strata,rng)
        for j,(ss,indices,areas,ob,minimum) in enumerate(settings):
            null[b,j]=correlations(Y,N,expected,lab,indices,areas)
    for j,(ss,indices,areas,ob,minimum) in enumerate(settings):
        ts=[dict(sign=s,**main.tail(ob[k],null[:,j,k],True)) for k,s in enumerate(signs)]
        for t,q in zip(ts,main.bh([t['p'] for t in ts])): t['q_bh']=q
        comparisons[str(minimum)]={'minimum_readable_objects':minimum,'sites':ss,'independent_sites':len(ss),'tests':ts}
    np.save(raw/'site_size_grouped_null.npy',null)
    ma=json.loads((main.OWN/'run-2026-10-07-01/motif-association.json').read_text(encoding='utf-8'))
    rare=set(ma['rare_definition']['categories'])
    texts=[r for r in seals if r['complete_observed'] and r['single_line'] and r['direction'] in {'R/L','L/R'} and
           r['signs_reading_rtl'] and '000' not in r['signs_reading_rtl'] and main.motif(r['symbol']) in rare|{'unicorn'}]
    # The existing function takes an object_type block key. Extend ONLY that
    # computational key with exact length; retain original rows and metadata.
    conditioned=[dict(r,object_type=r['object_type']+'|length='+str(len(r['signs_reading_rtl']))) for r in texts]
    mt,nu=main.motif_test(conditioned,B,rng)
    assert np.allclose(nu[:,-1],mt['tests'][-1]['observed'],rtol=0,atol=1e-12)
    for t,q in zip(mt['tests'][:-1],main.bh([t['p'] for t in mt['tests'][:-1]])): t['q_bh_five_variable_outcomes']=q
    mt['conditioning']='site, original exact object type, exact token length'
    mt['length_invariance_verified']=True
    np.save(raw/'motif_length_conditioned_null.npy',nu)
    main.write(out/'results.json',{'status':'Exploratory','seed':2026100702,'permutations':B,
        'input_sha256':main.sha(main.INPUT),'amendment_sha256':main.sha(main.OWN/'AMENDMENT-2026-10-07.md'),
        'analysis_code_sha256':main.sha(main.OWN/'analyze.py'),'sensitivity_code_sha256':main.sha(__file__),
        'site_size_grouped_permutation':comparisons,'motif_length_conditioned':mt,'runtime_seconds':time.time()-start})
    print('sensitivity complete',time.time()-start,flush=True)

if __name__=='__main__': run()
