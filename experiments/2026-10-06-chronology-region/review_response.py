"""Second D1 amendment. Small, component-based schedules with explicit output paths.

Run from the repository root: --output-dir FRESH_DIR --raw-dir FRESH_LOCAL_DIR.
This imports preserved code; it never changes an existing endpoint.
"""
from __future__ import annotations
import argparse, collections, hashlib, inspect, itertools, json, math, os, re, time
from pathlib import Path
for option in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']: os.environ[option]='1'
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.stats import hypergeom
import analyze as base
import post_launch as pl

OWN, ROOT, RAW = base.OWN, base.ROOT, base.RAW
ORIGIN='second post-launch amendment'
SEEDS=[21,22]

def save(path,value):
    base.save(path,{'origin':ORIGIN,'status':'Exploratory',**value})
def table(path,values):
    base.csv(path,[{'origin':ORIGIN,'status':'Exploratory',**x} for x in values])
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def origin(c,i):
    metadata=c.rows[i]['metadata']
    if 'stratum' in str(metadata.get('phase','')).lower(): return 'stratum'
    return 'period_field' if str(metadata.get('period','')).strip() not in ['', '-', 'None'] else 'label_without_period_field'
def mound(c,i):
    area=str(c.rows[i]['metadata'].get('area-section',''))
    return next((name for name in ['AB','E','F','J'] if area.startswith(name)),'unknown')
def hnums(c,i): return [int(x) for x in re.findall(r'\bH-?(\d+)',str(c.rows[i]['source_cisi']),re.I)]
def js_batch(p,q):
    midpoint=(p+q)/2
    with np.errstate(divide='ignore',invalid='ignore'):
        value=np.sum(np.where(p>0,p*np.log2(p/midpoint),0)+np.where(q>0,q*np.log2(q/midpoint),0),axis=1)/2
    value[~(np.isfinite(p).all(axis=1)&np.isfinite(q).all(axis=1))]=np.nan
    return value
def norm_rows(x):
    total=x.sum(axis=-1,keepdims=True)
    return np.divide(x,total,out=np.full_like(x,np.nan),where=total>0)

def prepare(c,a,b,name,closure=False):
    target={int(i):0 for i in a}; target.update({int(i):1 for i in b})
    units=[]; excluded=collections.Counter()
    for members in (c.textgroups if closure else c.physical):
        ids=[i for i in members if i in target]
        if not ids: continue
        if len({target[i] for i in ids})!=1: excluded['mixed_label_faces']+=len(ids); continue
        if len({c.type[i] for i in ids})!=1: excluded['mixed_type_faces']+=len(ids); continue
        units.append((ids,target[ids[0]],str(c.type[ids[0]]),len(ids)))
    aa=np.asarray([i for u in units if u[1]==0 for i in u[0]],int)
    bb=np.asarray([i for u in units if u[1]==1 for i in u[0]],int)
    types=base.common_types(c,aa,bb)
    units=[u for u in units if u[2] in types]
    blocks=collections.defaultdict(list)
    for j,u in enumerate(units): blocks[(u[2],u[3])].append(j)
    movable=sum(len(ix) for ix in blocks.values() if len({units[j][1] for j in ix})==2)
    aa=aa[np.isin(c.type[aa],types)]; bb=bb[np.isin(c.type[bb],types)]
    result={'comparison':name,'unit':'full_text_closure' if closure else 'physical_component',
        'excluded':dict(excluded),'common_types':types,'movable_components':movable,'components':len(units),
        'a':c.denom(aa),'b':c.denom(bb)}
    if not types or movable<20 or min(result['a']['physical_components'],result['b']['physical_components'])<10:
        return {'result':{**result,'reference_status':'Failed','reason':'unmovable-or-insufficient-support'}}
    nt,v=len(types),c.v
    rr,cc,values=[],[],[]
    for j,(ids,label,typ,n) in enumerate(units):
        t=types.index(typ)
        for channel, matrix in enumerate([c.matrix,c.initial,c.terminal]):
            counts=matrix[ids].sum(axis=0)
            nz=np.flatnonzero(counts)
            rr.extend([j]*len(nz)); cc.extend((channel*nt*v+t*v+nz).tolist()); values.extend(counts[nz].tolist())
        rr.extend([j,j]); cc.extend([3*nt*v+t,3*nt*v+nt+t]); values.extend([n,float(c.length[ids].sum())])
    x=csr_matrix((values,(rr,cc)),shape=(len(units),3*nt*v+2*nt),dtype=float)
    position_types=base.common_types(c,aa[c.clear[aa]],bb[c.clear[bb]])
    return {'result':result,'units':units,'blocks':blocks,'labels':np.asarray([u[1] for u in units],int),
        'types':types,'position_types':[types.index(t) for t in position_types], 'X':x,
        'total':np.asarray(x.sum(axis=0)).ravel(),'v':v,'nt':nt,'indices':(aa,bb)}

def metrics(frame,aggregate):
    aggregate=np.atleast_2d(aggregate)
    other=frame['total'][None,:]-aggregate
    nt,v=frame['nt'],frame['v']
    a=aggregate[:,:3*nt*v].reshape(-1,3,nt,v)
    b=other[:,:3*nt*v].reshape(-1,3,nt,v)
    pa=norm_rows(a[:,0]); pb=norm_rows(b[:,0])
    values={'frequency_js_bits':js_batch(pa.mean(axis=1),pb.mean(axis=1)),
        'raw_frequency_js_bits':js_batch(norm_rows(a[:,0].sum(axis=1)),norm_rows(b[:,0].sum(axis=1)))}
    for channel,label in [(1,'initial'),(2,'terminal')]:
        values[f'raw_{label}_js_bits']=js_batch(norm_rows(a[:,channel].sum(axis=1)),norm_rows(b[:,channel].sum(axis=1)))
        if frame['position_types']:
            aa=norm_rows(a[:,channel,frame['position_types']]); bb=norm_rows(b[:,channel,frame['position_types']])
            values[f'{label}_js_bits']=js_batch(aa.mean(axis=1),bb.mean(axis=1))
    slots_a=aggregate[:,3*nt*v+nt:]; slots_b=other[:,3*nt*v+nt:]
    n_a=aggregate[:,3*nt*v:3*nt*v+nt]; n_b=other[:,3*nt*v:3*nt*v+nt]
    values['mean_length_b_minus_a']=np.mean(slots_b/n_b-slots_a/n_a,axis=1)
    return values,pb.mean(axis=1)-pa.mean(axis=1)

def permutation(c,frame,rng,budget,seed,theme,local,check=False):
    result=dict(frame['result']); result.update(theme=theme,seed=seed,requested_permutations=budget)
    if 'X' not in frame: return result,[]
    labels=frame['labels']; units=frame['units']; x=frame['X']
    point,d=metrics(frame,np.asarray(x.T.dot((labels==0).astype(float))).ravel())
    totals=np.asarray(x[:,:frame['nt']*frame['v']].sum(axis=0)).reshape(frame['nt'],frame['v']).sum(axis=0)
    tests=np.flatnonzero(totals>=20)
    tails=np.zeros(len(tests),int); fields=list(point)
    nulls=np.empty((budget,len(fields))); keep_signs=[j for j in tests if c.vocab[j] in ['034','390']]
    if not keep_signs and len(tests): keep_signs=[int(tests[0])]
    sampled=np.empty((budget,len(keep_signs))); replay=[]
    for start in range(0,budget,64):
        number=min(64,budget-start)
        masks=np.empty((number,len(units)),float)
        for row in range(number):
            perm=labels.copy()
            for ix in frame['blocks'].values():
                perm[ix]=rng.permutation(perm[ix])
                assert int(np.sum(perm[ix]))==int(np.sum(labels[ix]))
            masks[row]=perm==0
            if start+row<3: replay.append(perm.tolist())
        aggregate=np.asarray(x.T.dot(masks.T).T)
        statistic,delta=metrics(frame,aggregate)
        nulls[start:start+number]=np.column_stack([statistic[f] for f in fields])
        tails+=np.sum(np.abs(delta[:,tests])>=np.abs(d[0,tests])-1e-12,axis=0)
        if keep_signs: sampled[start:start+number]=delta[:,keep_signs]
    # Match review/sign_test_resolution.py's B=2 RNG advancement exactly.
    for _ in range(2):
        for label in [0,1]:
            ix=np.where(labels==label)[0]; rng.choice(ix,len(ix),replace=True)
    stats={}
    for j,field in enumerate(fields):
        valid=np.isfinite(nulls[:,j]); estimate=float(point[field][0]); mean=float(nulls[valid,j].mean()) if valid.any() else None
        stats[field]={'observed':estimate if math.isfinite(estimate) else None,'null_mean':mean,
            'excess_over_null':estimate-mean if mean is not None and math.isfinite(estimate) else None,
            'finite_null_draws':int(valid.sum()),'magnitude_interval95':None,
            'interval_status':'No usable interval for divergence magnitude' if 'js_bits' in field else 'See subset length bootstrap'}
    observed=stats['frequency_js_bits']['observed']; draws=nulls[:,fields.index('frequency_js_bits')]
    p=(1+int(np.sum(draws>=observed-1e-12)))/(budget+1)
    result.update(reference_status='Verified computation',effect_js_bits=observed,p=p,monte_carlo_se=math.sqrt(p*(1-p)/(budget+1)),
        null_js_mean=stats['frequency_js_bits']['null_mean'],excess_js_bits=stats['frequency_js_bits']['excess_over_null'],
        permutations=budget,block_margin_checks_passed=budget,statistics=stats)
    signs=[{'theme':theme,'comparison':result['comparison'],'seed':seed,'unit':result['unit'],'sign':c.vocab[j],
        'known_tokens':int(totals[j]),'type_adjusted_b_minus_a':float(d[0,j]),'tail_count':int(tails[k]),
        'permutations':budget,'p':(1+int(tails[k]))/(budget+1)} for k,j in enumerate(tests)]
    if local is not None:
        stem=f"{theme}_{result['comparison']}_{result['unit']}_seed{seed}".replace('/','-')
        np.savez_compressed(local/(stem+'.npz'),fields=np.asarray(fields),nulls=nulls,
            selected_signs=np.asarray([c.vocab[j] for j in keep_signs]),selected_sign_nulls=sampled)
        save(local/(stem+'_replay.json'),{'units':[{'indices':u[0],'label':u[1],'type':u[2],'faces':u[3]} for u in units],
            'first_three_permuted_labels':replay})
        result['local_draw_file']=(local/(stem+'.npz')).as_posix()
    return result,signs

def validate_acceleration(c,frames):
    checks=[]
    for frame in frames:
        if 'X' not in frame: continue
        a,b=frame['indices']; closure=frame['result']['unit']=='full_text_closure'
        old,old_signs=base.permutation(c,a,b,'validation',np.random.default_rng(71),31,2,closure)
        # Start from full original selections: mixed components were already dropped.
        new,signs=permutation(c,frame,np.random.default_rng(71),31,71,'validation',None)
        assert abs(old['effect_js_bits']-new['effect_js_bits'])<2e-12
        assert abs(old['null_js_mean']-new['null_js_mean'])<2e-12
        assert old['p']==new['p']
        for old_row,new_row in zip(old_signs,signs):
            assert old_row['sign']==new_row['sign'] and old_row['p']==new_row['p']
        checks.append({'comparison':frame['result']['comparison'],'unit':frame['result']['unit'],'draws':31,
            'sign_p_values_checked':len(signs),'point_and_null_mean_match':True})
    return checks

def composition(c,out):
    groups=collections.defaultdict(list)
    for i,r in enumerate(c.rows):
        if r['site']=='Harappa' and r['major'] in ['3B','3C']:
            groups[(r['major'],origin(c,i),mound(c,i))].append(i)
    records=[]; ranges=[]
    for (period,source,area),ids in sorted(groups.items()):
        numbers=[hnums(c,i) for i in ids]
        records.append({'period':period,'label_source':source,'mound':area,**c.denom(ids),
            'faces_with_earlier_catalogue_number':sum(bool(ns) and all(n<=1520 or n==2590 for n in ns) for ns in numbers),
            'faces_without_parseable_H_number':sum(not ns for ns in numbers)})
    for period in ['3B','3C']:
        for source in ['period_field','stratum','label_without_period_field']:
            ids=[i for key,vs in groups.items() if key[:2]==(period,source) for i in vs]
            if not ids: continue
            flat=[n for i in ids for n in hnums(c,i)]
            ranges.append({'period':period,'label_source':source,'faces':len(ids),'faces_with_H_number':sum(bool(hnums(c,i)) for i in ids),
                'minimum_H_number':min(flat) if flat else None,'maximum_H_number':max(flat) if flat else None,
                'faces_earlier_proxy':sum(bool(hnums(c,i)) and all(n<=1520 or n==2590 for n in hnums(c,i)) for i in ids)})
    table(out/'excavation_composition.csv',records); table(out/'catalogue_number_ranges.csv',ranges)

def subset_data(c):
    units=pl.harappa_units(c); mixed_origin=mixed_mound=0
    for unit in units:
        sources={origin(c,i) for i in unit['indices']}; areas={mound(c,i) for i in unit['indices']}
        unit['label_source']=next(iter(sources)) if len(sources)==1 else 'mixed'
        unit['mound']=next(iter(areas)) if len(areas)==1 else 'mixed'
        mixed_origin+=len(sources)>1; mixed_mound+=len(areas)>1
    filters={'all':lambda u:True,'period_labelled':lambda u:u['label_source']=='period_field',
        'mound_e':lambda u:u['mound']=='E'}
    subsets={name:[u for u in units if keep(u)] for name,keep in filters.items()}
    return units,subsets,{'mixed_origin_families':mixed_origin,'mixed_mound_families':mixed_mound}

def length_results(c,subsets,out,local):
    result=[]; per_type=[]
    for name,units in list(subsets.items())+[('all_tablets',subsets['all'])]:
        a=np.asarray([i for u in units if u['period']=='3B' for i in u['indices'] if c.known[i]>0],int)
        b=np.asarray([i for u in units if u['period']=='3C' for i in u['indices'] if c.known[i]>0],int)
        types=['TAB:B','TAB:I'] if name=='all_tablets' else base.common_types(c,a,b)
        aa=a[np.isin(c.type[a],types)]; bb=b[np.isin(c.type[b],types)]
        raw=float(c.length[b].mean()-c.length[a].mean())
        effect=float(np.mean([c.length[bb[c.type[bb]==t]].mean()-c.length[aa[c.type[aa]==t]].mean() for t in types]))
        rng=np.random.default_rng(21); boots=[]
        groups=[]
        for ids in [aa,bb]:
            signatures=collections.defaultdict(list)
            for pid in sorted(set(c.pid[ids])):
                members=[int(i) for i in ids if c.pid[i]==pid]
                assert len({c.type[i] for i in members})==1
                signatures[(str(c.type[members[0]]),len(members))].append(members)
            groups.append(signatures)
        for _ in range(999):
            samples=[]
            for signatures in groups:
                sample=[i for pool in signatures.values() for choice in rng.integers(0,len(pool),len(pool)) for i in pool[int(choice)]]
                samples.append(np.asarray(sample,int))
            x,y=samples
            boots.append(float(np.mean([c.length[y[c.type[y]==t]].mean()-c.length[x[c.type[x]==t]].mean() for t in types])))
        result.append({'subset':name,'all_known_a':c.denom(a),'all_known_b':c.denom(b),'common_a':c.denom(aa),'common_b':c.denom(bb),
            'common_types':types,'raw_length_difference_slots':raw,'equal_type_length_difference_slots':effect,
            'length_interval95':np.quantile(boots,[.025,.975]).tolist(),'bootstrap_draws':999,'bootstrap_seed':21})
        for period,ids in [('3B',a),('3C',b)]:
            for t in sorted(set(c.type[ids])):
                selected=ids[c.type[ids]==t]
                if len(selected)<5: continue
                per_type.append({'subset':name,'period':period,'type':t,**c.denom(selected),'mean_observed_length':float(c.length[selected].mean())})
        save(local/(name+'_length_draws.json'),{'draws':boots})
    save(out/'length_comparisons.json',{'comparisons':result,'interval_scope':'Whole physical-family bootstrap within observed exact-type/face-count signatures; conditional on this excavation frame.'})
    table(out/'length_type_means.csv',per_type)

def diversity_tables(n,m):
    k=np.arange(n+1)
    richness=hypergeom.sf(0,n,k,m)
    draws=np.arange(1,m+1,dtype=float)
    entropy_terms=np.sum(hypergeom.pmf(draws[:,None],n,k[None,:],m)*(draws*np.log2(draws))[:,None],axis=0)/m
    return richness,entropy_terms

def media_reference(units,name,seed,local):
    a=[u for u in units if u['period']=='3B' and u['type'] is not None]
    b=[u for u in units if u['period']=='3C' and u['type'] is not None]
    pool=a+b; types=sorted({u['type'] for u in pool}); categories=np.asarray([types.index(u['type']) for u in pool])
    na,nb,m=len(a),len(b),min(len(a),len(b)); ra,ha=diversity_tables(na,m); rb,hb=diversity_tables(nb,m)
    def calc(ia,ib):
        ca=np.bincount(categories[ia],minlength=len(types)); cb=np.bincount(categories[ib],minlength=len(types))
        def entropy(counts,n): return -sum((x/n)*math.log2(x/n) for x in counts if x)
        return np.asarray([np.count_nonzero(cb)-np.count_nonzero(ca),entropy(cb,nb)-entropy(ca,na),
            np.sum(rb[cb])-np.sum(ra[ca]),np.sum(ha[ca])-np.sum(hb[cb])],float)
    observed=calc(np.arange(na),np.arange(na,len(pool)))
    assert np.allclose(observed,pl.media_effect(a,b,m=m),atol=2e-10)
    rng=np.random.default_rng(seed); boot=[]
    for _ in range(999): boot.append(calc(rng.integers(0,na,na),rng.integers(na,len(pool),nb)))
    blocks=collections.defaultdict(list)
    for i,u in enumerate(pool): blocks[u['faces']].append(i)
    draws=[]
    for _ in range(9999):
        aa,bb=[],[]
        for positions in blocks.values():
            n=sum(i<na for i in positions); chosen=rng.permutation(positions)
            aa.extend(chosen[:n]); bb.extend(chosen[n:])
        assert len(aa)==na and sum(pool[i]['faces'] for i in aa)==sum(u['faces'] for u in a)
        draws.append(calc(aa,bb))
    draws=np.asarray(draws); boot=np.asarray(boot)
    fields=['raw_richness_difference','raw_shannon_difference_bits','rarefied_richness_difference','rarefied_shannon_difference_bits']
    ps=[(1+int(np.sum(draws[:,j]>=observed[j]-1e-12)))/10000 for j in [2,3]]
    effects={f:{'effect':float(observed[j]),'interval95':np.quantile(boot[:,j],[.025,.975]).tolist(),
        'null_mean':float(draws[:,j].mean())} for j,f in enumerate(fields)}
    for j,q in enumerate(base.holm(ps)):
        effects[fields[j+2]].update(p=ps[j],holm_p=q)
    np.savez_compressed(local/f'media_{name}_seed{seed}.npz',permutation=draws,bootstrap=boot,fields=np.asarray(fields))
    return {'subset':name,'seed':seed,'families_3B':na,'families_3C':nb,'faces_3B':sum(u['faces'] for u in a),
        'faces_3C':sum(u['faces'] for u in b),'type_richness_3B':len({u['type'] for u in a}),
        'type_richness_3C':len({u['type'] for u in b}),'family_budget':m,'effects':effects,
        'permutations':9999,'bootstrap':999,'margin_checks':9999}

def disclosure(out):
    folder=out/'disclosure_safe'; folder.mkdir()
    summaries=[]
    for prefix in ['site_type','region_type','harappa_label_type','harappa_major_type','all_site_time']:
        source=OWN/'main-2026-10-07-v1'/f'{prefix}_strata.csv'
        frame=pd.read_csv(source,dtype=str,keep_default_na=False)
        fields={'site_type':['site','type'],'region_type':['region','type'],'harappa_label_type':['time','type'],
            'harappa_major_type':['major','type'],'all_site_time':['site','time']}[prefix]
        counts=frame['faces'].astype(int); keep=counts>=5
        summaries.append({'table':prefix,'cells':len(frame),'single_face_cells':int((counts==1).sum()),
            'suppressed_cells_under_five':int((~keep).sum()),'suppressed_faces':int(counts[~keep].sum()),'retained_cells':int(keep.sum())})
        allowed=set(tuple(row) for row in frame.loc[keep,fields].itertuples(index=False,name=None))
        for path in sorted(source.parent.glob(prefix+'_*.csv')):
            data=pd.read_csv(path,dtype=str,keep_default_na=False)
            mask=[tuple(row) in allowed for row in data[fields].itertuples(index=False,name=None)]
            data=data.loc[mask].copy(); data.insert(0,'status','Exploratory'); data.insert(0,'origin',ORIGIN)
            data.to_csv(folder/path.name,index=False)
    save(out/'disclosure.json',{'minimum_faces_per_retained_cell':5,'tables':summaries,
        'historical_endpoint_handling':'Unchanged historical single-face tables remain private source-derived disclosures; these filtered copies are the current presentation tables, not a general anonymity guarantee.'})

def other_references(c,units,out,local):
    membership=load(RAW/'post-launch-2026-10-07-v1/external_membership.json')
    counts=np.column_stack([c.matrix[:,[c.vi[s] for s in signs if s in c.vi]].sum(axis=1) for signs in pl.TARGETS.values()])
    external=[]; early=[]; flips=[]
    src=inspect.getsource(pl.early_adjusted)
    src=src.replace('local, name):','local, name, permutation_budget=9999):').replace('1999','permutation_budget').replace('/ 2000','/ (permutation_budget + 1)')
    namespace={**pl.__dict__,'save':save}; exec(compile(src,'parameterized_early_adjusted','exec'),namespace)
    save(local/'early_parameterization.json',{'source_sha256':base.digest(OWN/'post_launch.py'),
        'changes':['Function argument permutation_budget=9999','1999 allocations replaced by permutation_budget','2000 denominator replaced by permutation_budget + 1'],
        'code_sha256':hashlib.sha256(src.encode()).hexdigest()})
    matrix=np.zeros((len(units),c.v),bool)
    for i,u in enumerate(units):
        for sign in u['codes']: matrix[i,c.vi[sign]]=True
    populations=load(RAW/'post-launch-2026-10-07-v1/early_raw_draws.json')
    old_scores=load(RAW/'main-2026-10-07-v1/external_predictions.json')
    for seed in SEEDS:
        rng=np.random.default_rng(seed)
        for kind in ['physical','text']:
            reference,draws=pl.grouped_reference(c,membership['external_indices'],membership['core_indices'],counts,rng,9999,kind)
            reference['seed']=seed; reference['permutations']=9999
            if draws is not None:
                reference['null_means']={t:float(draws[:,j].mean()) for j,t in enumerate(pl.TARGETS)}
                np.savez_compressed(local/f'external_targets_{kind}_seed{seed}.npz',draws=draws,targets=np.asarray(list(pl.TARGETS)))
            external.append(reference)
        rng=np.random.default_rng(seed)
        rows=[]
        for name,key in [('type',lambda u:(u['type'],)),('type_length',lambda u:(u['type'],u['slots']))]:
            result=namespace['early_adjusted'](units,matrix,populations['early_unit_indices'],populations['later_unit_indices'],key,rng,local,f'{name}_seed{seed}',9999)
            result.update(adjustment=name,seed=seed,permutations=9999); rows.append(result)
        for row,q in zip(rows,base.holm([r['one_sided_p'] for r in rows])): row['holm_p']=q
        for row,q in zip(rows,base.holm([r['text_component_sensitivity']['one_sided_p'] for r in rows])): row['text_component_sensitivity']['holm_p']=q
        early.extend(rows)
        rng=np.random.default_rng(seed); rows=[]
        for key in [x for x in old_scores[0] if x.endswith('_excess')]:
            good=[p for p in old_scores if p[key] is not None]
            values=np.asarray([p[key] for p in good]); groups=sorted({p['physical'] for p in good})
            weights=np.asarray([sum(p[key] for p in good if p['physical']==g)/len(good) for g in groups])
            draws=rng.choice([-1,1],size=(9999,len(groups)))@weights
            exact=np.asarray(list(itertools.product([-1,1],repeat=len(groups))))@weights
            observed=float(values.mean()); p=(1+int(np.sum(np.abs(draws)>=abs(observed)-1e-12)))/10000
            rows.append({'statistic':key,'seed':seed,'faces':len(good),'families':len(groups),'effect':observed,'tail_count':int(np.sum(np.abs(draws)>=abs(observed)-1e-12)),
                'null_mean':float(draws.mean()),'p':p,'exact_sign_flip_p':float(np.mean(np.abs(exact)>=abs(observed)-1e-12)), 'permutations':9999})
        for row,q in zip(rows,base.holm([r['p'] for r in rows])): row['holm_p']=q
        flips.extend(rows)
    save(out/'other_permutation_references.json',{'external_targets':external,'early_inventory':early,'external_score_sign_flips':flips})
    old=load(OWN/'post-launch-2026-10-07-v1/early_inventory.json')
    diagnostics=[]
    for name in ['type','type_length']:
        samples=load(RAW/f'post-launch-2026-10-07-v1/early_{name}_draws.json')['bootstrap']
        observed=old['adjusted'][name]['early_minus_later']
        diagnostics.append({'adjustment':name,'observed':observed,'bootstrap_mean':float(np.mean(samples)),
            'bootstrap_median':float(np.median(samples)),'mean_minus_observed':float(np.mean(samples)-observed),
            'historical_interval95':old['adjusted'][name]['interval95']})
    save(out/'early_interval_diagnostics.json',{'diagnostics':diagnostics,'scope':'Resampling with replacement reduces distinct families and signs; the difference bootstrap is not centered on the observed union estimand.'})

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True); parser.add_argument('--raw-dir',required=True)
    args=parser.parse_args(); out=Path(args.output_dir).resolve(); local=Path(args.raw_dir).resolve()
    if out.exists() or local.exists(): raise FileExistsError('Choose new output and raw directories.')
    out.mkdir(parents=True); local.mkdir(parents=True)
    start=time.perf_counter(); c=base.Corpus(); composition(c,out)
    units,subsets,mixed=subset_data(c)
    save(local/'subset_units.json',{'units':units,'subset_physical_ids':{name:[u['physical'] for u in us] for name,us in subsets.items()}})
    length_results(c,subsets,out,local); disclosure(out)
    har=c.all[(c.site=='Harappa')&(c.known>0)]
    core=c.all[np.isin(c.region,base.CORE)&(c.known>0)]
    selected=[r for r in base.CORE if len(set(c.pid[core[c.region[core]==r]]))>=30]
    tasks=[]
    for theme,pairs,ids,labels in [('time',[('2','3B'),('2','3C'),('3B','3C')],har,c.major),
                                  ('region',list(itertools.combinations(selected,2)),core,c.region)]:
        for a,b in pairs:
            for closure in [False,True]: tasks.append((theme,prepare(c,ids[labels[ids]==a],ids[labels[ids]==b],a+'__'+b,closure)))
    subset_tasks=[]
    for name in ['period_labelled','mound_e']:
        ids=np.asarray([i for u in subsets[name] for i in u['indices'] if c.known[i]>0],int)
        for closure in [False,True]: subset_tasks.append(('subset',prepare(c,ids[c.major[ids]=='3B'],ids[c.major[ids]=='3C'],name,closure)))
    checks=validate_acceleration(c,[f for _,f in tasks+subset_tasks])
    save(out/'acceleration_checks.json',{'checks':checks,'check_budget':31})
    print('Component acceleration checks passed; running larger schedules.',flush=True)
    results=[]; sign_rows=[]
    for seed in SEEDS:
        for closure in [False,True]:
            rng=np.random.default_rng(seed+100000 if closure else seed)
            for theme,frame in tasks:
                if (frame['result']['unit']=='full_text_closure')!=closure: continue
                result,signs=permutation(c,frame,rng,19999 if theme=='time' else 9999,seed,theme,local)
                results.append(result)
                if not closure: sign_rows.extend(signs)
                print('schedule',seed,theme,frame['result']['comparison'],frame['result']['unit'],result.get('p'),flush=True)
            rng=np.random.default_rng(seed+100000 if closure else seed)
            for theme,frame in subset_tasks:
                if (frame['result']['unit']=='full_text_closure')!=closure: continue
                result,_=permutation(c,frame,rng,19999,seed,theme,local); results.append(result)
        for theme in ['time','region','subset']:
            for unit in ['physical_component','full_text_closure']:
                family=[r for r in results if r['seed']==seed and r['theme']==theme and r['unit']==unit and 'p' in r]
                for r,q in zip(family,base.holm([r['p'] for r in family])): r['holm_p']=q
        for theme in ['time','region']:
            family=[r for r in sign_rows if r['seed']==seed and r['theme']==theme]
            for r,q in zip(family,base.bh([r['p'] for r in family])):
                r['bh_q']=q; r['monte_carlo_se']=math.sqrt(r['p']*(1-r['p'])/(r['permutations']+1))
    save(out/'permutation_tests.json',{'tests':results})
    table(out/'sign_tests.csv',sign_rows)
    baselines=[{'seed':r['seed'],'theme':r['theme'],'comparison':r['comparison'],'unit':r['unit'],'statistic':key,
        **values} for r in results if 'statistics' in r for key,values in r['statistics'].items()]
    table(out/'divergence_baselines.csv',baselines)
    agreement=[]
    for theme in ['time','region','subset']:
        for name,unit in sorted({(r['comparison'],r['unit']) for r in results if r['theme']==theme and 'p' in r}):
            pair=[r for r in results if r['theme']==theme and r['comparison']==name and r['unit']==unit]
            agreement.append({'theme':theme,'comparison':name,'unit':unit,'seeds':[r['seed'] for r in pair],
                'p_values':[r['p'] for r in pair],'holm_values':[r['holm_p'] for r in pair],
                'agreement_at_05':len({r['holm_p']<.05 for r in pair})==1})
    sign_summary=[]
    for seed in SEEDS:
        for theme in ['time','region']:
            family=[r for r in sign_rows if r['seed']==seed and r['theme']==theme]
            sign_summary.append({'seed':seed,'theme':theme,'tests':len(family),'minimum_bh_q':min(r['bh_q'] for r in family),
                'passing':[{'comparison':r['comparison'],'sign':r['sign'],'p':r['p'],'bh_q':r['bh_q']} for r in family if r['bh_q']<.05]})
    save(out/'seed_agreement.json',{'frequency_tests':agreement,'sign_tests':sign_summary})
    media=[]
    for seed in SEEDS:
        for name,subset in subsets.items():
            media.append(media_reference(subset,name,seed,local)); print('media',seed,name,'complete',flush=True)
    save(out/'media_comparisons.json',{'comparisons':media})
    media_counts=[]
    for name,subset in subsets.items():
        for period in ['3B','3C']:
            for typ in sorted({u['type'] for u in subset if u['period']==period and u['type'] is not None}):
                us=[u for u in subset if u['period']==period and u['type']==typ]
                # Type counts alone, no individual signs/positions/lengths.
                media_counts.append({'subset':name,'period':period,'type':typ,'families':len(us),'faces':sum(u['faces'] for u in us)})
    table(out/'media_type_counts.csv',media_counts)
    print('Running the other saved-population references.',flush=True)
    other_references(c,units,out,local)
    audit={'input_sha256':base.digest(c.path),'code_sha256':base.digest(Path(__file__)),
        'protocol_sha256':base.digest(OWN/'PROTOCOL.md'),'amendment_sha256':base.digest(OWN/'REVIEW-AMENDMENT-2026-10-07.md'),
        'reused_analyzer_sha256':base.digest(OWN/'analyze.py'),'reused_post_launch_sha256':base.digest(OWN/'post_launch.py'),
        'review_sha256':base.digest(OWN/'REVIEW.md'),'population':c.denom(c.all),'seeds':SEEDS,
        'time_permutations':19999,'other_permutations':9999,'mixed_family_counts':mixed,
        'elapsed_seconds':time.perf_counter()-start,'raw_directory':str(local),
        'aggregate_bytes':sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),
        'local_bytes':sum(p.stat().st_size for p in local.rglob('*') if p.is_file())}
    save(out/'audit.json',audit); save(out/'completion.json',{'elapsed_seconds':audit['elapsed_seconds'],'all_schedules_complete':True})
    print(json.dumps({k:audit[k] for k in ['elapsed_seconds','aggregate_bytes','local_bytes']}),flush=True)

if __name__=='__main__': main()
