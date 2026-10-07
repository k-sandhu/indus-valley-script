"""Object-grouped observational analysis; see PROTOCOL.md for the frozen design.

Run from repository root. All record-level derivatives stay in local RAW.
Dependencies: Python 3, numpy, scipy. No model or plot installation is required.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib, json, math, os, re, sys, time
from pathlib import Path
import numpy as np
from scipy.special import expit, xlogy
from scipy.stats import rankdata, spearmanr

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'
INPUT = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
MISSING_MOTIFS = {'', '-', '?', 'None', 'Unknown'}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')

def bh(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    adj = np.minimum.accumulate((ps[order] * len(ps) / np.arange(1, len(ps)+1))[::-1])[::-1]
    out = np.empty(len(ps)); out[order] = np.minimum(adj, 1)
    return out.tolist()

def blocks(keys):
    ds = defaultdict(list)
    for i, k in enumerate(keys): ds[k].append(i)
    return [np.array(v, dtype=int) for _, v in sorted(ds.items())]

def shuffle(values, strata, rng):
    out = values.copy()
    for ix in strata:
        if len(ix) > 1: out[ix] = rng.permutation(values[ix])
    return out

def tail(observed, null, absolute=False):
    null = np.asarray(null, float)
    exceed = int(np.count_nonzero(np.abs(null) >= abs(observed)-1e-12)) if absolute else int(np.count_nonzero(null >= observed-1e-12))
    return {'observed': float(observed), 'p': (exceed+1)/(len(null)+1), 'exceedances': exceed,
            'references': len(null), 'null_mean': float(null.mean()),
            'null_95_interval': np.quantile(null, [.025, .975]).tolist()}

def wilson(k, n):
    if n == 0: return None
    z = 1.959963984540054; p = k/n; den=1+z*z/n
    m=(p+z*z/(2*n))/den; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,m-h), min(1,m+h)]

class UnionFind:
    # Same physical-family union approach as src/context_study.py; no text links.
    def __init__(self, n): self.parent = list(range(n))
    def find(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]; a = self.parent[a]
        return a
    def union(self, a, b):
        a,b=self.find(a),self.find(b)
        if a != b: self.parent[max(a,b)] = min(a,b)

def grouping(rows):
    uf=UnionFind(len(rows)); seen={}; unresolved=[]
    for i,r in enumerate(rows):
        cisi=(r.get('source_cisi') or '').strip()
        match=re.fullmatch(r'([A-Za-z][A-Za-z0-9]*-\d+)[A-Za-z]?', cisi)
        keys=[('family', r['object_family_id'])]
        if match: keys.append(('cisi',match[1]))
        elif cisi not in {'','-','--'}: unresolved.append({'record_id':r['record_id'],'reference':cisi})
        for key in keys:
            if key in seen: uf.union(i,seen[key])
            else: seen[key]=i
    gs=defaultdict(list)
    for i,r in enumerate(rows): gs[uf.find(i)].append(r)
    # Reuse prior principal-face rule: longest raw sequence, then identifier.
    def representative(rs): return min(rs,key=lambda r:(-len(r['signs_reading_rtl']),r['record_id']))
    principal=[representative(rs) for _,rs in sorted(gs.items()) if any(r['signs_reading_rtl'] for r in rs)]
    seals=[representative([r for r in rs if r['object_type'].startswith('SEAL')])
           for _,rs in sorted(gs.items()) if any(r['object_type'].startswith('SEAL') for r in rs)]
    audit={'components':[{'component':k,'record_ids':[r['record_id'] for r in rs],
                         'families':sorted({r['object_family_id'] for r in rs}),
                         'sites':sorted({r['site'] for r in rs}),
                         'types':sorted({r['object_type'] for r in rs})} for k,rs in sorted(gs.items())],
           'unresolved_nonblank_cisi':unresolved}
    return list(gs.values()), principal, seals, audit

def counts(rows, signs):
    cs=[Counter(s for s in r['signs_reading_rtl'] if s != '000') for r in rows]
    return np.array([[c[s] for s in signs] for c in cs],float),np.array([sum(c.values()) for c in cs],float)

def bootstrap_sites(groups, signs, B, rng):
    by=defaultdict(list)
    for rs in groups:
        for site in sorted({r['site'] for r in rs}):
            rr=[r for r in rs if r['site']==site]
            y,n=counts(rr,signs)
            by[site].append((y.sum(axis=0),n.sum(),len(rr),sum(len(r['signs_reading_rtl']) for r in rr)))
    out=[]
    for site,payload in sorted(by.items()):
        ys=np.array([p[0] for p in payload]); ns=np.array([p[1] for p in payload]); N=float(ns.sum()); Y=ys.sum(axis=0)
        intervals=[None]*len(signs)
        if len(payload)>1 and N:
            # Multinomial weights are exactly equivalent to resampling whole groups.
            w=rng.multinomial(len(payload),np.repeat(1/len(payload),len(payload)),size=B)
            denom=w@ns; vals=(w@ys)/np.where(denom[:,None]>0,denom[:,None],np.nan)
            intervals=np.nanquantile(vals,[.025,.975],axis=0).T.tolist()
        for j,s in enumerate(signs):
            out.append({'site':site,'sign':s,'count':int(Y[j]),'readable_positions':int(N),
                        'all_positions':sum(p[3] for p in payload),'faces':sum(p[2] for p in payload),
                        'components':len(payload),'readable_frequency':float(Y[j]/N) if N else None,
                        'all_position_frequency':float(Y[j]/sum(p[3] for p in payload)) if sum(p[3] for p in payload) else None,
                        'component_bootstrap_95_ci':intervals[j]})
    return out

def binomial_model(y,n,X,cluster,names):
    rank=int(np.linalg.matrix_rank(X))
    if rank < X.shape[1]: return {'status':'rank deficient','rank':rank,'columns':X.shape[1]}
    b=np.zeros(X.shape[1]); converged=False
    for it in range(120):
        p=np.clip(expit(X@b),1e-10,1-1e-10)
        w=np.maximum(n*p*(1-p),1e-10)
        ridge=np.eye(X.shape[1])*1e-6; ridge[0,0]=0
        h=X.T@(w[:,None]*X)+ridge
        step=np.linalg.lstsq(h,X.T@(y-n*p)-ridge@b,rcond=1e-12)[0]
        # Step limiting is a numerical device, not a coefficient constraint.
        step=step/max(1.,float(np.max(np.abs(step)))/5.)
        b+=step
        if np.max(np.abs(step))<1e-7: converged=True; break
    p=np.clip(expit(X@b),1e-10,1-1e-10); h=X.T@((n*p*(1-p))[:,None]*X)+ridge
    bread=np.linalg.pinv(h); scores=[]
    for cl in sorted(set(cluster)):
        ix=np.array([v==cl for v in cluster]); scores.append(X[ix].T@(y[ix]-n[ix]*p[ix]))
    G=len(scores); meat=np.array(scores).T@np.array(scores)
    cov=bread@meat@bread * (G/(G-1) if G>1 else 1)
    se=np.sqrt(np.maximum(np.diag(cov),0))
    return {'status':'converged' if converged else 'nonconverged; possible sparse-type separation',
            'iterations':it+1,'rank':rank,'objects':len(y),'site_clusters':G,'ridge_nonintercept':1e-6,
            'coefficients':{name:{'log_odds':float(v),'site_cluster_se':float(e),
                                   'odds_ratio':float(np.exp(np.clip(v,-700,700)))} for name,v,e in zip(names,b,se)}}

def design(rows, key):
    levels=sorted(set(key(r) for r in rows)); baseline=max(levels,key=lambda v:sum(key(r)==v for r in rows))
    others=[v for v in levels if v != baseline]
    return np.array([[1.]+[float(key(r)==v) for v in others] for r in rows]), ['intercept']+others,baseline

def sign_analysis(principal, signs, table, B, rng, raw_run):
    rr=[r for r in principal if any(s!='000' for s in r['signs_reading_rtl'])]
    Y,N=counts(rr,signs); types=[r['object_type'] for r in rr]; strata=blocks(types)
    P=np.zeros_like(Y); typeout=[]
    sealref=(np.array(types)=='SEAL:S'); sealp=Y[sealref].sum(0)/N[sealref].sum()
    for ix in strata:
        p=Y[ix].sum(0)/N[ix].sum(); P[ix]=p
        for j,s in enumerate(signs):
            odds=lambda v:v/(1-v) if v<1 else None
            typeout.append({'object_type':types[ix[0]],'sign':s,'objects':len(ix),'readable_positions':int(N[ix].sum()),
                            'count':int(Y[ix,j].sum()),'frequency':float(p[j]),
                            'odds_ratio_to_SEAL:S':float(odds(p[j])/odds(sealp[j])) if 0<sealp[j]<1 and p[j]<1 else None})
    expected=N[:,None]*P; var=N[:,None]*P*(1-P)
    sites=sorted(s for s,c in Counter(r['site'] for r in rr).items() if c>=20)
    label=np.array([sites.index(r['site']) if r['site'] in sites else -1 for r in rr])
    def statistic(labels):
        value=np.zeros(len(signs))
        for k in range(len(sites)):
            ix=labels==k; v=var[ix].sum(0); d=(Y[ix]-expected[ix]).sum(0)
            value+=np.divide(d*d,v,out=np.zeros_like(v),where=v>0)
        return value
    obs=statistic(label); null=np.empty((B,len(signs)))
    for b in range(B): null[b]=statistic(shuffle(label,strata,rng))
    tests=[dict(sign=s,**tail(obs[j],null[:,j])) for j,s in enumerate(signs)]
    for v,q in zip(tests,bh([v['p'] for v in tests])): v['q_bh']=q
    residual=[]
    for site in sorted(set(r['site'] for r in rr)):
        ix=np.array([r['site']==site for r in rr]); den=float(N[ix].sum())
        for j,s in enumerate(signs):
            residual.append({'site':site,'sign':s,'objects':int(ix.sum()),'count':int(Y[ix,j].sum()),
                             'readable_positions':int(den),'type_expected_count':float(expected[ix,j].sum()),
                             'frequency_minus_type_expected':float((Y[ix,j]-expected[ix,j]).sum()/den)})
    tab={t['site']:t for t in table['sites']}; size_sites=sorted(t for t in tab if sum(r['site']==t for r in rr)>=3)
    sizeout={}; allnull=[]
    for variant in ['reference','min','max','exclude_two_cities']:
        ss=[s for s in size_sites if variant!='exclude_two_cities' or s not in {'Harappa','Mohenjo-daro'}]
        area=np.array([tab[s]['area_'+ ('reference' if variant=='exclude_two_cities' else variant)] for s in ss])
        area_rank=rankdata(np.log2(area)); area_rank-=area_rank.mean()
        residual_matrix=np.array([[next(v['frequency_minus_type_expected'] for v in residual if v['site']==s and v['sign']==c) for c in signs] for s in ss])
        R=np.apply_along_axis(rankdata,0,residual_matrix); R-=R.mean(0)
        den=np.sqrt((area_rank@area_rank)*(R*R).sum(0))
        ob=np.divide(area_rank@R,den,out=np.zeros(len(signs)),where=den>0)
        nu=np.array([rng.permutation(area_rank)@R/den for _ in range(B)])
        tt=[dict(sign=s,**tail(ob[j],nu[:,j],True)) for j,s in enumerate(signs)]
        for t,q in zip(tt,bh([v['p'] for v in tt])): t['q_bh']=q
        sizeout[variant]={'sites':ss,'independent_sites':len(ss),'areas':area.tolist(),'tests':tt}
        allnull.append(nu)
    mask=np.array([r['site'] in size_sites for r in rr]); sr=[r for r in rr if r['site'] in size_sites]
    X,names,base=design(sr,lambda r:r['object_type']); logarea=np.log2([tab[r['site']]['area_reference'] for r in sr])
    T,tnames,tbase=design(sr,lambda r:tab[r['site']]['site_type'])
    models={}
    for j,s in enumerate(signs):
        models[s]={}
        for name,x,nm in [('area',np.column_stack([X,logarea]),names+['log2_area']),
                          ('site_type',np.column_stack([X,T[:,1:]]),names+['site_type:'+v for v in tnames[1:]]),
                          ('joint',np.column_stack([X,T[:,1:],logarea]),names+['site_type:'+v for v in tnames[1:]]+['log2_area'])]:
            models[s][name]=binomial_model(Y[mask,j],N[mask],x,[r['site'] for r in sr],nm)
    np.savez_compressed(raw_run/'sign_nulls.npz',site=null,size=np.array(allnull))
    return {'object_type_frequencies':typeout,'site_omnibus':{'eligible_sites':sites,'tests':tests,
             'objects':len(rr),'blocks':len(strata),'site_label_movable_objects':sum(len(ix) for ix in strata if len(set(label[ix]))>1)},
            'site_residuals':residual,'size_comparisons':sizeout,'binomial_models':models,
            'model_baselines':{'object_type':base,'site_type':tbase},'sourced_site_eligibility':[
                {**t,'principal_readable_objects':sum(r['site']==t['site'] for r in rr),'in_size_model':t['site'] in size_sites} for t in table['sites']]}

def motif(raw): return 'unicorn' if raw.startswith('Bull1') else None if raw in MISSING_MOTIFS else raw
def period(row, coarse=False):
    p=row['metadata'].get('time','-')
    return 'Period 3C (pooled)' if coarse and p.startswith('Period 3C') else p

def concentration(seals):
    out=[]
    for population,rr in [('all_seals',seals),('square_seals',[r for r in seals if r['object_type']=='SEAL:S'])]:
        for level,key in [('global',lambda r:'all'),('site',lambda r:r['site']),('region',lambda r:r['region']),
                          ('Harappa_time',lambda r:period(r)),('Harappa_coarse_time',lambda r:period(r,True))]:
            rs=[r for r in rr if r['site']=='Harappa'] if level.startswith('Harappa') else rr
            ds=defaultdict(list)
            for r in rs: ds[key(r)].append(r)
            for group,rows in sorted(ds.items()):
                c=Counter(motif(r['symbol']) for r in rows); unknown=c.pop(None,0); n=sum(c.values())
                ranked=sorted(c.items(),key=lambda v:(-v[1],v[0])); hhi=sum((v/n)**2 for v in c.values()) if n else None
                out.append({'population':population,'level':level,'group':group,'objects':len(rows),'known_motif_objects':n,
                            'unknown_or_absent_motif_objects':unknown,'unicorn_count':c['unicorn'],
                            'unicorn_share':c['unicorn']/n if n else None,'unicorn_wilson_95_ci':wilson(c['unicorn'],n),
                            'motif_categories':len(c),'hhi':hhi,'effective_categories':1/hhi if hhi else None,
                            'rank_abundance':[{'rank':i+1,'motif':k,'count':v,'share':v/n} for i,(k,v) in enumerate(ranked)]})
    return out

def js(a,b):
    a=a/a.sum() if a.sum() else a; b=b/b.sum() if b.sum() else b; m=(a+b)/2
    return float((xlogy(a,np.divide(a,m,out=np.ones_like(a),where=m>0)).sum()+
                  xlogy(b,np.divide(b,m,out=np.ones_like(b),where=m>0)).sum())/(2*np.log(2)))

def motif_test(rows, B, rng, conditioned_site=True):
    if not rows or len(set(motif(r['symbol'])=='unicorn' for r in rows))<2: return {'status':'inadequate two-cohort data'}
    y=np.array([motif(r['symbol'])=='unicorn' for r in rows],int)
    seq=[tuple(r['signs_reading_rtl']) for r in rows]; signlist=sorted({s for text in seq for s in text}); si={s:i for i,s in enumerate(signlist)}
    A=np.zeros((len(rows),len(signlist))); F=A.copy(); L=A.copy()
    for i,text in enumerate(seq):
        for s in text: A[i,si[s]]+=1
        F[i,si[text[0]]]=1; L[i,si[text[-1]]]=1
    texts={s:i for i,s in enumerate(sorted(set(seq)))}; ti=np.array([texts[t] for t in seq]); totaltext=np.bincount(ti,minlength=len(texts))
    lengths=A.sum(1); sums=[m.sum(0) for m in [A,F,L]]
    strata=blocks([(r['site'],r['object_type']) for r in rows]); mixed=[ix for ix in strata if len(set(y[ix]))>1]
    def stats(labels):
        n1=labels.sum(); n0=len(labels)-n1; vectors=[labels@m for m in [A,F,L]]
        tx=np.bincount(ti,weights=labels,minlength=len(texts))
        return np.array([js(v,t-v) for v,t in zip(vectors,sums)]+[
            float(np.count_nonzero(vectors[0])-np.count_nonzero(sums[0]-vectors[0])),
            np.count_nonzero(tx)/n1-np.count_nonzero(totaltext-tx)/n0,
            labels@lengths/n1-(1-labels)@lengths/n0])
    ob=stats(y); nu=np.empty((B,6))
    for b in range(B): nu[b]=stats(shuffle(y,strata,rng))
    names=['sign_distribution_js_bits','initial_js_bits','terminal_js_bits','inventory_richness_unicorn_minus_other',
           'distinct_text_rate_unicorn_minus_other','length_unicorn_minus_other']
    ts=[dict(outcome=name,**tail(ob[j],nu[:,j],j>=3)) for j,name in enumerate(names)]
    for t,q in zip(ts,bh([t['p'] for t in ts])): t['q_bh']=q
    def desc(lab):
        ix=y==lab; c=A[ix].sum(0); tx=np.bincount(ti[ix],minlength=len(texts))
        return {'objects':int(ix.sum()),'token_positions':int(c.sum()),'inventory':int(np.count_nonzero(c)),
                'distinct_texts':int(np.count_nonzero(tx)),'distinct_text_rate':float(np.count_nonzero(tx)/ix.sum()),
                'singleton_text_objects':int(np.count_nonzero(tx==1)),'mean_length':float(lengths[ix].mean()),
                'length_quantiles':np.quantile(lengths[ix],[0,.25,.5,.75,1]).tolist()}
    return {'status':'Frozen evaluation','unicorn':desc(1),'other':desc(0),'tests':ts,
            'site_type_blocks':len(strata),'mixed_blocks':len(mixed),'movable_objects':sum(len(ix) for ix in mixed),
            'motif_categories_other':dict(Counter(motif(r['symbol']) for r in rows if motif(r['symbol'])!='unicorn'))},nu

def motif_analysis(seals,B,rng,raw_run):
    c=Counter(motif(r['symbol']) for r in seals); c.pop(None,0); n=sum(c.values())
    rare={k for k,v in c.items() if k!='unicorn' and v/n<.05}
    valid=[r for r in seals if r['complete_observed'] and r['single_line'] and r['direction'] in {'R/L','L/R'} and
           r['signs_reading_rtl'] and '000' not in r['signs_reading_rtl'] and motif(r['symbol']) is not None]
    primary=[r for r in valid if motif(r['symbol']) in rare|{'unicorn'}]
    out={'rare_definition':{'threshold':.05,'denominator_known_seals':n,'categories':sorted(rare)},
         'seal_components':len(seals),'eligible_clean_texts':len(valid),'primary_clean_texts':len(primary),'by_site':{}}
    for key,rows in [('primary_rare',primary),('all_nonunicorn_sensitivity',valid)]:
        result=motif_test(rows,B,rng)
        if isinstance(result,tuple):
            out[key],nu=result; np.save(raw_run/(key+'_motif_null.npy'),nu)
        else: out[key]=result
    for site in sorted({r['site'] for r in primary}):
        rr=[r for r in primary if r['site']==site]; lab=Counter(motif(r['symbol'])=='unicorn' for r in rr)
        if min(lab.get(True,0),lab.get(False,0))>=5:
            result,nu=motif_test(rr,B,rng); out['by_site'][site]=result
            np.save(raw_run/(re.sub(r'[^A-Za-z0-9]','_',site)+'_motif_null.npy'),nu)
    ts=[t for v in out['by_site'].values() for t in v['tests']]
    for t,q in zip(ts,bh([t['p'] for t in ts])): t['q_bh_across_sites_and_outcomes']=q
    return out,rare

def positive(value):
    try:
        v=float(value)
        return v if np.isfinite(v) and v>0 else None
    except (TypeError,ValueError): return None

def numeric_summary(values):
    a=np.asarray(values,float)
    if not len(a): return {'n':0}
    sd=float(a.std(ddof=1)) if len(a)>1 else None; mean=float(a.mean())
    return {'n':len(a),'mean':mean,'sample_sd':sd,'cv':sd/mean if sd is not None else None,
            'quantiles_0_025_25_50_75_975_100':np.quantile(a,[0,.025,.25,.5,.75,.975,1]).tolist()}

def dimension_analysis(seals,rare,B,rng,raw_run):
    square=[r for r in seals if r['object_type']=='SEAL:S']; fields=['horizontal(mm)','vertical(mm)','thickness(mm)']
    dimensions=[]
    for r in square:
        h,v,th=[positive(r['metadata'].get(k)) for k in fields]
        dimensions.append({'row':r,'h':h,'v':v,'th':th,'area':h*v if h and v else None,
                           'size':math.sqrt(h*v) if h and v else None})
    primary=[d for d in dimensions if d['area'] and d['row']['metadata'].get('preservation')=='complete']
    valid=[d for d in dimensions if d['area']]
    out={'square_seal_components':len(square),'positive_dimensions':{k:sum(d[k] is not None for d in dimensions) for k in ['h','v','th']},
         'both_face_dimensions':len(valid),'complete_preservation_both_dimensions':len(primary),
         'preservation_counts':dict(Counter(d['row']['metadata'].get('preservation') for d in valid)),
         'all_square_dimension_summaries':{k:numeric_summary([d[k] for d in dimensions if d[k] is not None]) for k in ['h','v','th']},
         'groups':[]}
    for pop,ds in [('complete_square',primary),('all_preservation_square',valid)]:
        for level,key in [('global',lambda d:'all'),('motif',lambda d:motif(d['row']['symbol']) or 'unknown_or_absent'),
                          ('site',lambda d:d['row']['site']),('Harappa_time',lambda d:period(d['row'])),
                          ('Harappa_coarse_time',lambda d:period(d['row'],True))]:
            rr=[d for d in ds if d['row']['site']=='Harappa'] if level.startswith('Harappa') else ds
            by=defaultdict(list)
            for d in rr: by[key(d)].append(d)
            for group,dd in sorted(by.items()):
                sizes=np.array([d['size'] for d in dd]); hist,edges=np.histogram(sizes,bins=np.arange(0,102,2))
                out['groups'].append({'population':pop,'level':level,'group':group,
                    'characteristic_size_mm':numeric_summary(sizes),'face_area_mm2':numeric_summary([d['area'] for d in dd]),
                    'horizontal_mm':numeric_summary([d['h'] for d in dd]),'vertical_mm':numeric_summary([d['v'] for d in dd]),
                    'histogram_2mm':{'edges':edges.tolist(),'counts':hist.tolist(),'greater_than_100mm':int((sizes>100).sum())}})
    # Label permutations for CV compare complete square seals within exact type/site.
    dd=[d for d in primary if motif(d['row']['symbol']) in rare|{'unicorn'}]; tests=[]
    y=np.array([motif(d['row']['symbol'])=='unicorn' for d in dd]); sizes=np.array([d['size'] for d in dd])
    strata=blocks([(d['row']['site'],d['row']['object_type']) for d in dd])
    def cv(a): return float(a.std(ddof=1)/a.mean())
    if y.sum()>1 and (~y).sum()>1:
        obs=cv(sizes[y])-cv(sizes[~y]); nu=[cv(sizes[lab])-cv(sizes[~lab]) for lab in (shuffle(y,strata,rng) for _ in range(B))]
        tests.append(dict(outcome='cv_unicorn_minus_rare',**tail(obs,nu,True),unicorn_objects=int(y.sum()),rare_objects=int((~y).sum())))
        np.save(raw_run/'dimension_cv_null.npy',nu)
    # Controls are fixed for all references; use Frisch-Waugh partial regression.
    rows=[d['row'] for d in primary]
    if len(rows)>3:
        X,names,base=design(rows,lambda r:r['site']); M,mnames,mbase=design(rows,lambda r:motif(r['symbol']) or 'unknown_or_absent')
        Z=np.column_stack([X,M[:,1:]]); logarea=np.log2([d['area'] for d in primary]); lengths=np.array([len(r['signs_reading_rtl']) for r in rows],float)
        rx=logarea-Z@np.linalg.lstsq(Z,logarea,rcond=None)[0]; denom=rx@rx
        if denom>1e-10:
            slope=float(rx@lengths/denom); strata=blocks([(r['site'],motif(r['symbol']) or 'unknown_or_absent',r['object_type']) for r in rows])
            nu=np.array([rx@shuffle(lengths,strata,rng)/denom for _ in range(B)])
            t=dict(outcome='length_per_doubling_area_adjusted_site_motif',**tail(slope,nu,True),objects=len(rows),
                   controls_rank=int(np.linalg.matrix_rank(Z)),controls_columns=Z.shape[1],
                   movable_objects=sum(len(ix) for ix in strata if len(set(lengths[ix]))>1),
                   spearman_unadjusted=float(spearmanr(logarea,lengths).statistic))
            tests.append(t); np.save(raw_run/'dimension_length_null.npy',nu)
            residual=lengths-np.column_stack([Z,logarea])@np.linalg.lstsq(np.column_stack([Z,logarea]),lengths,rcond=None)[0]
            t['partial_ols_se']=float(np.sqrt((residual@residual)/(len(rows)-np.linalg.matrix_rank(np.column_stack([Z,logarea])))/denom))
    for t,q in zip(tests,bh([t['p'] for t in tests])): t['q_bh']=q
    out['tests']=tests
    audit=[{'record_id':d['row']['record_id'],'family':d['row']['object_family_id'],'site':d['row']['site'],
            'motif':d['row']['symbol'],'preservation':d['row']['metadata'].get('preservation'),
            **{k:d['row']['metadata'].get(k) for k in fields+['h','v','th']},
            'area_mm2':d['area'],'length_positions':len(d['row']['signs_reading_rtl'])} for d in dimensions]
    write(raw_run/'dimensions-audit.json',audit)
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',default='run-2026-10-07-01')
    ap.add_argument('--permutations',type=int,default=9999); ap.add_argument('--bootstraps',type=int,default=2000)
    ap.add_argument('--seed',type=int,default=2026100701); args=ap.parse_args()
    out=OWN/args.run; raw_run=RAW/args.run
    if out.exists() or raw_run.exists(): raise FileExistsError('Choose a new run name; endpoints are never overwritten.')
    out.mkdir(); raw_run.mkdir(parents=True); tmp=RAW/'tmp'; tmp.mkdir(exist_ok=True)
    for key in ['TMP','TEMP','MPLCONFIGDIR']: os.environ[key]=str(tmp)
    started=time.time(); rng=np.random.default_rng(args.seed)
    rows=[json.loads(l) for l in INPUT.read_text(encoding='utf-8').splitlines()]
    groups,principal,seals,audit=grouping(rows); write(raw_run/'grouping-audit.json',audit)
    c=Counter(s for r in rows for s in r['signs_reading_rtl']); signs=[s for s,n in sorted(c.items(),key=lambda v:(-v[1],v[0])) if s!='000'][:10]
    summary={'status':'Frozen evaluation','input_sha256':sha(INPUT),'protocol_sha256':sha(OWN/'PROTOCOL.md'),
             'site_table_sha256':sha(OWN/'site-table.json'),'code_sha256':sha(__file__),'seed':args.seed,
             'permutations':args.permutations,'bootstraps':args.bootstraps,'faces':len(rows),'all_positions':sum(c.values()),
             'readable_positions':sum(c.values())-c['000'],'unreadable_positions':c['000'],'physical_components':len(groups),
             'numeric_object_families':len(set(r['object_family_id'] for r in rows)),'principal_faces':len(principal),
             'seal_components':len(seals),'top_signs':signs,'top_sign_counts':{s:c[s] for s in signs},
             'components_with_multiple_sites':sum(len(v['sites'])>1 for v in audit['components']),
             'components_with_multiple_types':sum(len(v['types'])>1 for v in audit['components']),
             'unresolved_nonblank_cisi':len(audit['unresolved_nonblank_cisi']),
             'retrieved_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'numpy':np.__version__}
    write(out/'input-summary.json',summary); print('input',summary['faces'],summary['physical_components'],signs,flush=True)
    write(out/'site-frequencies.json',bootstrap_sites(groups,signs,args.bootstraps,rng)); print('site intervals done',flush=True)
    table=json.loads((OWN/'site-table.json').read_text(encoding='utf-8'))
    write(out/'sign-analysis.json',sign_analysis(principal,signs,table,args.permutations,rng,raw_run)); print('sign tests done',flush=True)
    write(out/'motif-concentration.json',concentration(seals))
    ma,rare=motif_analysis(seals,args.permutations,rng,raw_run); write(out/'motif-association.json',ma); print('motif tests done',flush=True)
    write(out/'dimensions.json',dimension_analysis(seals,rare,args.permutations,rng,raw_run)); print('dimension tests done',flush=True)
    summary['runtime_seconds']=time.time()-started; summary['outputs']={p.name:sha(p) for p in sorted(out.glob('*.json')) if p.name!='input-summary.json'}
    write(out/'input-summary.json',summary)

if __name__=='__main__': main()
