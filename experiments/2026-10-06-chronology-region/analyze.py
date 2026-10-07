"""Bounded, component-aware chronology/region analysis. Run from repository root.

No corpus rows or predictions are exported into the tracked experiment directory.
Existing endpoint names are refused. All randomness has a declared seed.
"""
from __future__ import annotations
import argparse, collections, hashlib, itertools, json, math, os, re, sys, time
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-chronology-region'
TMP = RAW / 'tmp'; TMP.mkdir(parents=True, exist_ok=True)
for key in ['TMP', 'TEMP', 'MPLCONFIGDIR']: os.environ[key] = str(TMP)
import numpy as np
import pandas as pd
from scipy.stats import norm
sys.path.insert(0, str(ROOT / 'src/methods'))
from conditional_structure import group_records, make_folds

CORE = ['Inter-Riverine', 'Lower Indus', 'Gujarat/Kutch', 'Eastern Headwaters', 'Upper Indus']
EXTERNAL = ['Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia']
PERIODS = ['1','2','3A','3B','3C','4','5']
DATES = {'1':[3700,2800],'2':[2800,2600],'3A':[2600,2450], '3B':[2450,2200], '3C':[2200,1900], '4':[1900,1800],'5':[1800,1300]}

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
def csv(path, records): pd.DataFrame(records).to_csv(path, index=False, encoding='utf-8')
def ci(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [float(v) for v in np.quantile(x,[.025,.975])] if len(x) else [None,None]
def js(p,q):
    if p is None or q is None: return float('nan')
    m = (p+q)/2
    return float(sum(np.sum(z[z>0]*np.log2(z[z>0]/m[z>0]))/2 for z in [p,q]))
def entropy(c):
    c = np.asarray(c, float); p = c[c>0]/c.sum() if c.sum() else np.array([])
    return float(-np.sum(p*np.log2(p)))
def pnorm(x): return x/x.sum() if x.sum()>0 else None
def bh(ps):
    ps=np.asarray(ps,float); n=len(ps); order=np.argsort(ps); q=np.empty(n)
    q[order]=np.minimum.accumulate((ps[order]*n/np.arange(1,n+1))[::-1])[::-1].clip(0,1)
    return q.tolist()
def holm(ps):
    ps=np.asarray(ps,float); n=len(ps); order=np.argsort(ps); q=np.empty(n)
    q[order]=np.maximum.accumulate(ps[order]*(n-np.arange(n))).clip(0,1)
    return q.tolist()
def simple_cisi(s):
    m = re.fullmatch(r'([A-Za-z]+)-?(\d+)(?:[A-Za-z])?', str(s).strip())
    return f'{m[1].upper()}-{int(m[2])}' if m else None
def periods(label):
    s=str(label).removeprefix('Period ').strip()
    if s=='3B/C': return ['3B','3C']
    if s=='3': return ['3A','3B','3C']
    m=re.fullmatch(r'(1|2|3A|3B|3C|4|5)(?:[ABC]|-[1-4])?',s)
    return [m[1]] if m else []

class DSU:
    def __init__(self,n): self.p=list(range(n))
    def find(self,i):
        while self.p[i]!=i: self.p[i]=self.p[self.p[i]]; i=self.p[i]
        return i
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b: self.p[max(a,b)]=min(a,b)

def physical_groups(rows):
    d=DSU(len(rows)); seen={}
    for i,r in enumerate(rows):
        aliases=[('family',r['object_family_id'])]
        c=simple_cisi(r['source_cisi'])
        if c: aliases.append(('cisi',c))
        for key in aliases:
            if key in seen: d.union(i,seen[key])
            else: seen[key]=i
    groups=collections.defaultdict(list)
    for i in range(len(rows)): groups[d.find(i)].append(i)
    return list(groups.values())

class Corpus:
    def __init__(self):
        self.path=ROOT/'data/normalized/lipi_observed_faces.jsonl'
        self.rows=[json.loads(x) for x in self.path.read_text(encoding='utf-8').splitlines() if x.strip()]
        self.vocab=sorted({s for r in self.rows for s in r['signs_reading_rtl'] if s!='000'})
        self.vi={s:i for i,s in enumerate(self.vocab)}; self.n=len(self.rows); self.v=len(self.vocab)
        self.physical=physical_groups(self.rows); self.pid=np.zeros(self.n,int)
        for g,ids in enumerate(self.physical): self.pid[ids]=g
        self.groups=collections.defaultdict(list)
        for i,r in enumerate(self.rows):
            r['type']= {'POsT:T:g':'POT:T:g','POT:T:S':'POT:T:s'}.get(r['object_type'],r['object_type'])
            r['seq']=tuple(r['signs_reading_rtl']); r['admissible']=periods(r['metadata'].get('time')) if r['site']=='Harappa' else []
            r['major']=r['admissible'][0] if len(r['admissible'])==1 else 'interval' if r['admissible'] else 'undated'
            r['clear']=bool(r['complete_observed'] and r['single_line'] and r['direction']=='R/L' and not r['has_blank_space'] and r['seq'] and '000' not in r['seq'])
            r['physical']=int(self.pid[i]); self.groups[r['physical']].append(i)
        # Exact-text closure is computed before direction/length/site selection.
        prep=[]
        for i,r in enumerate(self.rows):
            valid=r['complete_observed'] and r['single_line'] and r['seq'] and '000' not in r['seq'] and not r['has_blank_space']
            prep.append({'artifact':str(r['physical']), 'seq':r['seq'] if valid else ('__INELIGIBLE__',str(i))})
        self.textgroups=group_records(prep); self.tid=np.zeros(self.n,int)
        for g,ids in enumerate(self.textgroups): self.tid[ids]=g
        assigned,loads=make_folds(prep,self.textgroups,5,20261006)
        self.fold=np.array([assigned[i] for i in range(self.n)])
        self.foldloads=loads
        self.type=np.array([r['type'] for r in self.rows]); self.site=np.array([r['site'] for r in self.rows])
        self.region=np.array([r['region'] for r in self.rows]); self.major=np.array([r['major'] for r in self.rows])
        self.clear=np.array([r['clear'] for r in self.rows]); self.length=np.array([len(r['seq']) for r in self.rows],float)
        self.matrix=np.zeros((self.n,self.v)); self.initial=np.zeros_like(self.matrix); self.terminal=np.zeros_like(self.matrix)
        for i,r in enumerate(self.rows):
            for s in r['seq']:
                if s!='000': self.matrix[i,self.vi[s]]+=1
            if r['clear']:
                self.initial[i,self.vi[r['seq'][0]]]=1; self.terminal[i,self.vi[r['seq'][-1]]]=1
        self.known=self.matrix.sum(1); self.all=np.arange(self.n)

    def denom(self,ids):
        ids=np.asarray(ids,int)
        return {'faces':len(ids),'physical_components':len(set(self.pid[ids])), 'text_components':len(set(self.tid[ids])), 'known_tokens':int(self.known[ids].sum()),'observed_slots':int(self.length[ids].sum()), 'unreadable_tokens':int(self.length[ids].sum()-self.known[ids].sum()),'clear_faces':int(self.clear[ids].sum())}

    def weights(self,ids,types=None,site_balance=False,base=None):
        ids=np.asarray(ids,int); w=np.ones(len(ids)) if base is None else np.asarray(base,float).copy()
        if types is None: return w
        w*=np.isin(self.type[ids],types)
        if not w.sum(): return None
        for t in types:
            ti=self.type[ids]==t
            if not w[ti].sum(): return None
            if site_balance:
                ss=sorted(set(self.site[ids[ti]]))
                for s in ss:
                    cell=ti & (self.site[ids]==s); total=w[cell].sum()
                    if not total: return None
                    w[cell]/=total*len(ss)*len(types)
            else: w[ti]/=w[ti].sum()*len(types)
        return w

    def distribution(self,ids,mat,types=None,site_balance=False,base=None):
        # Frequencies standardize normalized token distributions per type/site,
        # rather than averaging individual face-relative frequencies.
        ids=np.asarray(ids,int); base=np.ones(len(ids)) if base is None else np.asarray(base,float)
        if types is None: return pnorm(np.sum(mat[ids]*base[:,None],axis=0))
        acc=np.zeros(self.v)
        for t in types:
            mask=self.type[ids]==t
            sites=sorted(set(self.site[ids[mask]])) if site_balance else [None]
            if not len(sites): return None
            for s in sites:
                cell=mask if s is None else mask & (self.site[ids]==s)
                p=pnorm(np.sum(mat[ids[cell]]*base[cell,None],axis=0))
                if p is None: return None
                acc+=p/(len(types)*len(sites))
        return acc

    def summary(self,ids):
        ids=np.asarray(ids,int); clear=ids[self.clear[ids]]
        pairs=collections.Counter((a,b) for i in clear for a,b in zip(self.rows[i]['seq'],self.rows[i]['seq'][1:]))
        prev=collections.Counter()
        for (a,b),v in pairs.items(): prev[a]+=v
        h=-sum(v/sum(pairs.values())*math.log2(v/prev[a]) for (a,b),v in pairs.items()) if pairs else None
        return {**self.denom(ids), 'mean_observed_length':float(self.length[ids].mean()) if len(ids) else None, 'mean_known_length':float(self.known[ids].mean()) if len(ids) else None, 'distinct_signs':int(np.count_nonzero(self.matrix[ids].sum(0))), 'known_sign_entropy_bits':entropy(self.matrix[ids].sum(0)), 'internal_bigram_tokens':sum(pairs.values()), 'distinct_internal_bigrams':len(pairs),'conditional_bigram_entropy_bits':h, 'distinct_clear_texts':len({self.rows[i]['seq'] for i in clear})}

def stratified_tables(c,out):
    specs={'region_type':['region','type'], 'site_type':['site','type'], 'harappa_label_type':['time','type'], 'harappa_major_type':['major','type'], 'all_site_time':['site','time']}
    for name,fields in specs.items():
        groups=collections.defaultdict(list)
        for i,r in enumerate(c.rows):
            if name.startswith('harappa') and r['site']!='Harappa': continue
            key=tuple(r['metadata'].get('time','-') if f=='time' else r[f] for f in fields);groups[key].append(i)
        table=[];signs=[];positions=[]; lengths=[]
        for key,ids in sorted(groups.items()):
            fieldsrow=dict(zip(fields,key)); table.append({**fieldsrow,**c.summary(ids)})
            for j,n in enumerate(c.matrix[ids].sum(0)):
                if n: signs.append({**fieldsrow,'sign':c.vocab[j],'known_token_count':int(n)})
            for pos,mat in [('initial',c.initial),('terminal',c.terminal)]:
                for j,n in enumerate(mat[ids].sum(0)):
                    if n: positions.append({**fieldsrow,'position':pos,'sign':c.vocab[j],'face_count':int(n)})
            for le,n in sorted(collections.Counter(int(c.length[i]) for i in ids).items()): lengths.append({**fieldsrow,'observed_length':le,'faces':n})
        csv(out/(name+'_strata.csv'),table)
        if name!='all_site_time':
            csv(out/(name+'_sign_counts.csv'),signs); csv(out/(name+'_positions.csv'),positions);csv(out/(name+'_lengths.csv'),lengths)

def common_types(c,a,b,mincomp=10,clear=False):
    if clear: a=a[c.clear[a]]; b=b[c.clear[b]]
    return sorted(t for t in set(c.type[a]) & set(c.type[b]) if len(set(c.pid[a[c.type[a]==t]]))>=mincomp and len(set(c.pid[b[c.type[b]==t]]))>=mincomp)

def boot_base(c,ids,rng,sites=False,group='physical'):
    gid=c.pid if group=='physical' else c.tid
    cells=collections.defaultdict(set)
    for i in ids: cells[c.site[i] if sites else 'all'].add(gid[i])
    mult=collections.Counter()
    for gs in cells.values():
        gs=sorted(gs); mult.update(rng.choice(gs,len(gs),replace=True).tolist())
    return np.array([mult[gid[i]] for i in ids],float)

def effects(c,a,b,types,site=False,bases=None):
    wa,wb=(None,None) if bases is None else bases
    pa=c.distribution(a,c.matrix,types,site,wa);pb=c.distribution(b,c.matrix,types,site,wb)
    freq=js(pa,pb); vals={'frequency_js_bits':freq}
    if pa is None or pb is None: return None,None
    x=c.weights(a,types,site,wa); y=c.weights(b,types,site,wb)
    vals['mean_length_b_minus_a']=float(np.average(c.length[b],weights=y)-np.average(c.length[a],weights=x)) if x is not None and y is not None else float('nan')
    ac=a[c.clear[a]];bc=b[c.clear[b]]; ct=common_types(c,ac,bc) if types is not None else None
    if types is not None: ct=[t for t in types if t in ct]
    for key,mat in [('initial',c.initial),('terminal',c.terminal)]:
        av=None if wa is None else wa[c.clear[a]];bv=None if wb is None else wb[c.clear[b]]
        vals[key+'_js_bits']=js(c.distribution(ac,mat,ct,site,av), c.distribution(bc,mat,ct,site,bv)) if len(ac) and len(bc) and (ct is None or ct) else float('nan')
    return vals,pb-pa

def compare(c,a,b,name,rng,B,regional=False):
    a=np.asarray(a,int);b=np.asarray(b,int);types=common_types(c,a,b)
    result={'comparison':name,'a':c.denom(a),'b':c.denom(b),'common_types':types, 'positional_common_types':common_types(c,a,b,clear=True)}
    ac=a[np.isin(c.type[a],types)];bc=b[np.isin(c.type[b],types)]
    result['common_support_a']=c.denom(ac);result['common_support_b']=c.denom(bc)
    for mode,aa,bb,ts,site in [('raw',a,b,None,False),('raw_common_support',ac,bc,None,False),('type_adjusted',ac,bc,types,False),('site_type_adjusted',ac,bc,types,True)] if regional else [('raw',a,b,None,False),('raw_common_support',ac,bc,None,False),('type_adjusted',ac,bc,types,False)]:
        if not len(aa) or not len(bb) or ts==[]: result[mode]={'status':'insufficient-support'};continue
        obs,d=effects(c,aa,bb,ts,site);boots=collections.defaultdict(list)
        for _ in range(B):
            ba=boot_base(c,aa,rng,regional);bbas=boot_base(c,bb,rng,regional)
            ev,_=effects(c,aa,bb,ts,site,(ba,bbas))
            if ev:
                for k,v in ev.items(): boots[k].append(v)
        result[mode]={k:{'effect':float(v) if np.isfinite(v) else None,'ci95':ci(boots[k]),'valid_bootstraps':int(np.isfinite(boots[k]).sum())} for k,v in obs.items()}
    sens={}
    for label,aa,bb,unique in [('clear',a[c.clear[a]],b[c.clear[b]],False),('equal_whole_text',a,b,True)]:
        ts=common_types(c,aa,bb)
        if ts:
            aa=aa[np.isin(c.type[aa],ts)];bb=bb[np.isin(c.type[bb],ts)]
            bases=None
            if unique:
                ca=collections.Counter((c.type[i],c.site[i] if regional else '',c.rows[i]['seq']) for i in aa)
                cb=collections.Counter((c.type[i],c.site[i] if regional else '',c.rows[i]['seq']) for i in bb)
                bases=(np.array([1/ca[(c.type[i],c.site[i] if regional else '',c.rows[i]['seq'])] for i in aa]), np.array([1/cb[(c.type[i],c.site[i] if regional else '',c.rows[i]['seq'])] for i in bb]))
            val,_=effects(c,aa,bb,ts,regional,bases)
            sens[label]={'common_types':ts,'a':c.denom(aa),'b':c.denom(bb),'effects':{k:float(v) if np.isfinite(v) else None for k,v in val.items()}}
        else: sens[label]={'status':'insufficient-support'}
    result['sensitivity']=sens
    return result

def permutation(c,a,b,name,rng,P,B,closure=False):
    gid=c.tid if closure else c.pid; target={int(i):0 for i in a};target.update({int(i):1 for i in b})
    # Membership is assessed on the full physical/text component, not selected faces.
    allgroups=c.textgroups if closure else c.physical;units=[];excluded=collections.Counter()
    for ids in allgroups:
        selected=[i for i in ids if i in target]
        if not selected: continue
        if len({target[i] for i in selected})!=1: excluded['mixed_label_faces']+=len(selected);continue
        if len({c.type[i] for i in selected})!=1:excluded['mixed_type_faces']+=len(selected);continue
        # Unselected aliases are held together, but only selected faces enter counts.
        units.append((selected,target[selected[0]],c.type[selected[0]],len(selected)))
    aa=np.array([i for ids,l,t,n in units if l==0 for i in ids],int);bb=np.array([i for ids,l,t,n in units if l==1 for i in ids],int)
    ts=common_types(c,aa,bb);units=[u for u in units if u[2] in ts]
    blocks=collections.defaultdict(list)
    for j,u in enumerate(units):blocks[(u[2],u[3])].append(j)
    movable=sum(len(js_) for js_ in blocks.values() if len({units[j][1] for j in js_})==2)
    result={'comparison':name,'unit':'full_text_closure' if closure else 'physical_component','excluded':dict(excluded),'common_types':ts,'movable_components':movable,'components':len(units), 'a':c.denom(aa[np.isin(c.type[aa],ts)]), 'b':c.denom(bb[np.isin(c.type[bb],ts)])}
    if not ts or movable<20 or min(result['a']['physical_components'],result['b']['physical_components'])<10:
        result['status']='unmovable-or-insufficient-support'; return result,[]
    x=np.array([c.matrix[u[0]].sum(0) for u in units]);labels=np.array([u[1] for u in units]);typ=np.array([u[2] for u in units])
    def calc(l,m=None):
        m=np.ones(len(units)) if m is None else m
        ps=[]
        for g in [0,1]:
            q=[]
            for t in ts:
                sel=(l==g)&(typ==t);p=pnorm(np.sum(x[sel]*m[sel,None],axis=0))
                if p is None:return None,None
                q.append(p)
            ps.append(np.mean(q,axis=0))
        return js(*ps),ps[1]-ps[0]
    obs,d=calc(labels);null=[];nd=[]
    original_margin=collections.Counter((u[1],u[2],u[3]) for u in units)
    for _ in range(P):
        l=labels.copy()
        for ix in blocks.values(): l[ix]=rng.permutation(l[ix])
        assert collections.Counter((int(l[j]),u[2],u[3]) for j,u in enumerate(units))==original_margin
        s,z=calc(l);null.append(s);nd.append(z)
    null=np.array(null);nd=np.array(nd)
    result.update(status='computed',effect_js_bits=obs,p=(1+int(np.sum(null>=obs-1e-12)))/(P+1),permutations=P, null_js_mean=float(null.mean()), block_margin_checks_passed=P)
    bdiff=[]
    for _ in range(B):
        mult=np.zeros(len(units))
        for g in [0,1]:
            ix=np.where(labels==g)[0]; drawn=rng.choice(ix,len(ix),replace=True);mult+=np.bincount(drawn,minlength=len(units))
        s,z=calc(labels,mult)
        if z is not None:bdiff.append(z)
    bd=np.array(bdiff);sig=[]
    for j,total in enumerate(x.sum(0)):
        if total>=20:
            sig.append({'comparison':name,'sign':c.vocab[j],'known_tokens':int(total),'type_adjusted_b_minus_a':float(d[j]),'ci95_low':float(np.quantile(bd[:,j],.025)), 'ci95_high':float(np.quantile(bd[:,j],.975)), 'p':(1+int(np.sum(np.abs(nd[:,j])>=abs(d[j])-1e-12)))/(P+1),'unit':result['unit']})
    return result,sig

def rarefaction(c,a,b,rng,R=200):
    a=np.asarray(a,int);b=np.asarray(b,int); ts=common_types(c,a,b); result={}
    for mode,types in [('raw',[None]),('type_adjusted',ts)]:
        if not types:result[mode]={'status':'insufficient-support'};continue
        budgets={}; draws=[]
        counts=[]
        for t in types:
            aa=a if t is None else a[c.type[a]==t];bb=b if t is None else b[c.type[b]==t]
            x=c.matrix[aa].sum(0).astype(int);y=c.matrix[bb].sum(0).astype(int);budget=min(x.sum(),y.sum());budgets[str(t)]=int(budget)
            counts.append((x,y,budget))
        for _ in range(R):
            xs=[];ys=[]
            for x,y,n in counts:
                xs.append(rng.multivariate_hypergeometric(x,int(n))/n);ys.append(rng.multivariate_hypergeometric(y,int(n))/n)
            draws.append(js(np.mean(xs,axis=0),np.mean(ys,axis=0)))
        result[mode]={'token_budgets':budgets,'draws':R,'mean_js_bits':float(np.mean(draws)),'simulation_interval95':ci(draws)}
    return result

def attestation(c,out):
    ids=[i for i,r in enumerate(c.rows) if r['site']=='Harappa' and r['admissible'] and c.known[i]>0]
    table=[]; presence=[]
    for sign in sorted({s for i in ids for s in c.rows[i]['seq'] if s!='000'}):
        bearing=[i for i in ids if sign in c.rows[i]['seq']]
        admissible=[c.rows[i]['admissible'] for i in bearing]
        earliest_lo=min(PERIODS.index(p) for a in admissible for p in a);earliest_hi=min(max(PERIODS.index(p) for p in a) for a in admissible)
        latest_lo=max(min(PERIODS.index(p) for p in a) for a in admissible);latest_hi=max(PERIODS.index(p) for a in admissible for p in a)
        table.append({'sign':sign,'dated_faces_bearing_sign':len(bearing),'physical_components_bearing_sign':len(set(c.pid[bearing])),'earliest_observed_lo':PERIODS[earliest_lo],'earliest_observed_hi':PERIODS[earliest_hi],'latest_observed_lo':PERIODS[latest_lo],'latest_observed_hi':PERIODS[latest_hi],'interval_faces_bearing_sign':sum(len(a)>1 for a in admissible)})
        for p in PERIODS:
            pop=[i for i in ids if c.rows[i]['admissible']==[p]];n=len(set(c.pid[pop]));k=len({c.pid[i] for i in pop if sign in c.rows[i]['seq']})
            z=norm.ppf(.975)
            center=(k/n+z*z/(2*n))/(1+z*z/n) if n else None
            delta=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n) if n else None
            presence.append({'sign':sign,'period':p,'components':n,'components_bearing':k,'presence_fraction':k/n if n else None,'wilson95_low':center-delta if n else None,'wilson95_high':center+delta if n else None,'zero_count_one_sided95_upper':1-.05**(1/n) if n and k==0 else None})
    csv(out/'harappa_attestation_bounds.csv',table);csv(out/'harappa_component_presence.csv',presence)

def interval_sensitivity(c,rng):
    families=collections.defaultdict(list)
    for i,r in enumerate(c.rows):
        if r['site']=='Harappa' and r['admissible'] and c.known[i]>0:families[c.pid[i]].append(i)
    feasible={};conflicts=[]
    for g,ids in families.items():
        a=set(c.rows[ids[0]]['admissible'])
        for i in ids:a &= set(c.rows[i]['admissible'])
        if a:feasible[g]=[p for p in PERIODS if p in a]
        else:conflicts.extend(ids)
    def run(mode):
        labels={}
        for g,ps in feasible.items():
            if len(ps)==1:labels[g]=ps[0]
            elif mode=='uniform':labels[g]=rng.choice(ps)
            elif ps==['3B','3C']:labels[g]=mode
        a=np.array([i for g,ids in families.items() if labels.get(g)=='3B' for i in ids],int)
        b=np.array([i for g,ids in families.items() if labels.get(g)=='3C' for i in ids],int)
        ts=common_types(c,a,b);aa=a[np.isin(c.type[a],ts)];bb=b[np.isin(c.type[b],ts)]
        ev,_=effects(c,aa,bb,ts)
        return {'a':c.denom(a),'b':c.denom(b),'common_types':ts,'effects':{k:float(v) if np.isfinite(v) else None for k,v in ev.items()}}
    result={'conflicting_faces':len(conflicts),'conflicting_components':len({c.pid[i] for i in conflicts}),'all_3BC_to_3B':run('3B'),'all_3BC_to_3C':run('3C')}
    draws=[run('uniform') for _ in range(100)]
    result['uniform_allocation']={'draws':100,'metric_envelopes':{k:{'min':float(min(x['effects'][k] for x in draws if x['effects'][k] is not None)), 'max':float(max(x['effects'][k] for x in draws if x['effects'][k] is not None)), 'mean':float(np.mean([x['effects'][k] for x in draws if x['effects'][k] is not None]))} for k in draws[0]['effects']}}
    return result

class Model:
    def __init__(self,c,ids):
        self.c=c;self.ids=np.asarray(ids,int);self.u=(c.matrix[self.ids].sum(0)+.5);self.u/=self.u.sum()
        self.b=collections.defaultdict(collections.Counter);self.ng={n:set() for n in [2,3]}
        self.seen=set()
        for i in ids:
            s=c.rows[i]['seq'];self.seen.update(s)
            for a,b in zip(('BOS',)+s,s):self.b[a][b]+=1
            for n in [2,3]:self.ng[n].update(tuple(s[j:j+n]) for j in range(len(s)-n+1))
        self.total={a:sum(v.values()) for a,v in self.b.items()};self.cache={}
    def probs(self,prev):
        if prev not in self.cache:
            x=20*self.u.copy()
            for s,n in self.b.get(prev,{}).items():x[self.c.vi[s]]+=n
            x/=20+self.total.get(prev,0);assert abs(x.sum()-1)<1e-10;self.cache[prev]=x
        return self.cache[prev]
    def score(self,i):
        s=self.c.rows[i]['seq'];loss=[-math.log2(self.probs(a)[self.c.vi[b]]) for a,b in zip(('BOS',)+s,s)]
        out={'loss_bits_per_sign':float(np.mean(loss)), 'token_losses':loss, 'unseen_signs':sum(x not in self.seen for x in s)}
        for n in [2,3]:
            grams=[tuple(s[j:j+n]) for j in range(len(s)-n+1)];out[f'novel{n}']=sum(g not in self.ng[n] for g in grams)/len(grams) if grams else None
        return out

def score_summary(c,pred,cols,B,rng,adjust=True):
    ids=np.array([p['i'] for p in pred],int);types=sorted(set(c.type[ids]));vals={}
    for col in cols:
        arr=np.array([p[col] for p in pred],float)
        def calc(base=None):
            w=c.weights(ids,types,True,base) if adjust else (np.ones(len(ids)) if base is None else base)
            return float(np.average(arr,weights=w)) if w is not None else float('nan')
        samples=[calc(boot_base(c,ids,rng,True)) for _ in range(B)]
        vals[col]={'mean':calc(),'ci95':ci(samples),'valid_bootstraps':int(np.isfinite(samples).sum()), 'token_weighted_mean':float(np.average(arr,weights=c.length[ids]))}
    return {'test':c.denom(ids),'types':types,'losses':vals}

def equal_component_sample(c,a,b,rng):
    ga=sorted(set(c.tid[a]));gb=sorted(set(c.tid[b]));n=min(len(ga),len(gb))
    sa=set(rng.choice(ga,n,replace=False).tolist());sb=set(rng.choice(gb,n,replace=False).tolist())
    return a[np.isin(c.tid[a],list(sa))], b[np.isin(c.tid[b],list(sb))]

def regional_models(c,out,rawout,B,rng):
    core=c.all[c.clear & np.isin(c.region,CORE)];results=[];saved=[]
    for region in CORE:
        target=core[c.region[core]==region];other=core[c.region[core]!=region]
        counts=[];ts=[]
        for t in sorted(set(c.type[target])):
            ok=True
            for f in range(5):
                a=target[(c.fold[target]!=f)&(c.type[target]==t)];b=other[(c.fold[other]!=f)&(c.type[other]==t)]
                if min(len(a),len(b))<20:ok=False
                counts.append({'region':region,'type':t,'fold':f,'within_faces':len(a),'other_faces':len(b),'supported':min(len(a),len(b))>=20})
            if ok:ts.append(t)
        preds=[];train=[]
        for f in range(5):
            te=target[(c.fold[target]==f)&np.isin(c.type[target],ts)];a=target[c.fold[target]!=f];b=other[c.fold[other]!=f]
            if not len(te):continue
            assert not set(c.tid[te]) & (set(c.tid[a])|set(c.tid[b]))
            ma,mb=Model(c,a),Model(c,b)
            for t in sorted(set(c.type[te])):
                aa=a[c.type[a]==t];bb=b[c.type[b]==t];ta,tb=Model(c,aa),Model(c,bb)
                da,db=equal_component_sample(c,aa,bb,rng);msa,msb=Model(c,da),Model(c,db)
                train.append({'fold':f,'type':t,'within':c.denom(aa),'other':c.denom(bb),'size_matched_within':c.denom(da),'size_matched_other':c.denom(db)})
                for i in te[c.type[te]==t]:
                    sa,sb=ma.score(i),mb.score(i);sc,sd=ta.score(i),tb.score(i);se,sf=msa.score(i),msb.score(i)
                    p={'i':int(i),'region':region,'fold':f,'raw_within':sa['loss_bits_per_sign'],'raw_other':sb['loss_bits_per_sign'],'type_within':sc['loss_bits_per_sign'],'type_other':sd['loss_bits_per_sign'],'size_within':se['loss_bits_per_sign'],'size_other':sf['loss_bits_per_sign'],'other_unseen_signs':sd['unseen_signs'],'within_unseen_signs':sc['unseen_signs']}
                    for prefix in ['raw','type','size']:p[prefix+'_excess']=p[prefix+'_other']-p[prefix+'_within']
                    preds.append(p);saved.append({**p,'record_id':c.rows[i]['record_id'],'physical':int(c.pid[i]),'text_component':int(c.tid[i])})
        item={'region':region,'eligible':c.denom(target),'supported_types':ts,'excluded_faces':len(target)-len(preds),'training':train,'support_by_fold':counts}
        if preds:
            cols=[f'{x}_{y}' for x in ['raw','type','size'] for y in ['within','other','excess']]
            item['raw']=score_summary(c,preds,cols[:3],B,rng,False)
            item['adjusted']=score_summary(c,preds,cols[3:],B,rng,True)
            item['unseen_sign_counts']={k:sum(p[k] for p in preds) for k in ['other_unseen_signs','within_unseen_signs']}
        else:item['status']='insufficient-training-support'
        # Site-held-out prediction is separate from same-site held-out families.
        site_results=[]
        for site in sorted(set(c.site[target])):
            te=target[c.site[target]==site];bad=set(c.tid[te]);tr=target[(c.site[target]!=site)&~np.isin(c.tid[target],list(bad))]
            eligible_types=[t for t in sorted(set(c.type[te])) if np.sum(c.type[tr]==t)>=20]
            te=te[np.isin(c.type[te],eligible_types)]
            if not len(te):continue
            assert not set(c.tid[te]) & set(c.tid[tr])
            pooled=Model(c,tr);tp={t:Model(c,tr[c.type[tr]==t]) for t in eligible_types};pred=[]
            for i in te:pred.append({'i':int(i),'raw':pooled.score(i)['loss_bits_per_sign'],'type':tp[c.type[i]].score(i)['loss_bits_per_sign']})
            site_results.append({'site':site,'test':c.denom(te),'train':c.denom(tr),'raw_mean_bits':float(np.mean([p['raw'] for p in pred])),'type_mean_bits':float(np.mean([p['type'] for p in pred]))})
        item['within_region_leave_site_out']=site_results;results.append(item)
        print('regional model',region,len(preds),flush=True)
    save(rawout/'regional_predictions.json',saved);save(out/'regional_models.json',results)
    return results

def external_models(c,out,rawout,B,P,rng):
    ext=c.all[c.clear & np.isin(c.region,EXTERNAL)];bad=set(c.tid[ext]);core=c.all[c.clear & np.isin(c.region,CORE) & ~np.isin(c.tid,list(bad))]
    removed=c.all[c.clear & np.isin(c.region,CORE) & np.isin(c.tid,list(bad))]
    preds=[];excluded=[];training=[]
    for f in range(5):
        tr=core[c.fold[core]!=f];held=core[c.fold[core]==f];ex=ext[c.fold[ext]==f]
        if not len(ex):continue
        assert not set(c.tid[ex]) & set(c.tid[tr]);assert not set(c.tid[held]) & set(c.tid[tr])
        raw=Model(c,tr);tp={t:Model(c,tr[c.type[tr]==t]) for t in sorted(set(c.type[ex])) if np.sum(c.type[tr]==t)>=20}
        training.append({'fold':f,'train':c.denom(tr),'heldout_core':c.denom(held),'external':c.denom(ex)})
        for i in ex:
            t=c.type[i];le=c.length[i];full=core[(c.type[core]==t)&(c.length[core]==le)];match=held[(c.type[held]==t)&(c.length[held]==le)]
            if len(full)<20 or len(match)<2 or t not in tp:
                excluded.append({'record_id':c.rows[i]['record_id'],'i':int(i),'region':c.region[i],'site':c.site[i],'type':t,'length':int(le),'available_cell_faces':len(full),'fold_match_faces':len(match),'reason':'length_type_or_training_support'});continue
            p={'i':int(i),'record_id':c.rows[i]['record_id'],'region':c.region[i],'site':c.site[i],'type':t,'length':int(le),'fold':f,'physical':int(c.pid[i]),'text_component':int(c.tid[i]),'match_ids':[c.rows[j]['record_id'] for j in match],'match_faces':len(match),'match_physical_components':len(set(c.pid[match]))}
            for mode,model in [('raw',raw),('type',tp[t])]:
                score=model.score(i);refs=[model.score(j) for j in match]
                p[mode+'_loss']=score['loss_bits_per_sign'];p[mode+'_core_loss']=float(np.mean([x['loss_bits_per_sign'] for x in refs]));p[mode+'_excess']=p[mode+'_loss']-p[mode+'_core_loss']
                p[mode+'_unseen_signs']=score['unseen_signs'];p[mode+'_token_losses']=score['token_losses']
                for n in [2,3]:
                    k=f'novel{n}';p[mode+'_'+k]=score[k];p[mode+'_core_'+k]=float(np.mean([x[k] for x in refs])) if score[k] is not None else None
                    p[mode+'_'+k+'_excess']=p[mode+'_'+k]-p[mode+'_core_'+k] if score[k] is not None else None
            preds.append(p)
    result={'external_all':c.denom(c.all[np.isin(c.region,EXTERNAL)]),'external_eligible':c.denom(ext),'core_eligible_after_external_closure_exclusion':c.denom(core),'removed_core_overlap':c.denom(removed),'training':training,'matched_faces':len(preds),'matched_components':len({p['physical'] for p in preds}),'excluded_faces':len(excluded),'matched_cells':[], 'results':{},'by_region':[]}
    cells=collections.defaultdict(list)
    for p in preds:cells[(p['type'],p['length'])].append(p)
    result['matched_cells']=[{'type':t,'length':l,'external_faces':len(ps),'external_components':len({p['physical'] for p in ps}),'min_fold_core_matches':min(p['match_faces'] for p in ps),'max_fold_core_matches':max(p['match_faces'] for p in ps)} for (t,l),ps in sorted(cells.items())]
    def summarize(ps):
        vals={}
        for col in ['raw_loss','raw_core_loss','raw_excess','type_loss','type_core_loss','type_excess','raw_novel2_excess','raw_novel3_excess','type_novel2_excess','type_novel3_excess']:
            good=[p for p in ps if p[col] is not None]
            if not good: vals[col]={'status':'no-ngrams'};continue
            ids=np.array([p['i'] for p in good],int);v=np.array([p[col] for p in good]);boots=[]
            for _ in range(B):boots.append(float(np.average(v,weights=boot_base(c,ids,rng))))
            component_mean={g:float(np.mean(v[c.pid[ids]==g])) for g in set(c.pid[ids])};loco=[]
            for g in component_mean:
                keep=c.pid[ids]!=g
                if keep.any():loco.append(float(v[keep].mean()))
            vals[col]={'mean':float(v.mean()),'ci95':ci(boots),'faces':len(good),'components':len(component_mean),'leave_one_component_out_range':[min(loco),max(loco)] if loco else [None,None]}
            if col.endswith('excess'):
                null=[]
                gs=sorted(component_mean)
                for _ in range(P):
                    signs=dict(zip(gs,rng.choice([-1,1],len(gs))));null.append(float(np.mean([z*signs[c.pid[i]] for i,z in zip(ids,v)])))
                vals[col]['sign_flip_p']=(1+sum(abs(x)>=abs(v.mean())-1e-12 for x in null))/(P+1)
        return vals
    if preds:
        result['results']=summarize(preds)
        result['by_region']=[{'region':r,'faces':len(ps),'components':len({p['physical'] for p in ps}),'results':summarize(ps)} for r in EXTERNAL if (ps:=[p for p in preds if p['region']==r])]
        columns=[k for k in result['results'] if k.endswith('excess') and 'sign_flip_p' in result['results'][k]]
        corrected=holm([result['results'][k]['sign_flip_p'] for k in columns])
        for k,q in zip(columns,corrected):result['results'][k]['holm_p']=q
    save(rawout/'external_predictions.json',preds);save(rawout/'external_exclusions.json',excluded);save(out/'external_models.json',result)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);parser.add_argument('--bootstrap',type=int,default=499);parser.add_argument('--permutations',type=int,default=499);args=parser.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9_-]+',args.run)
    out=OWN/args.run;rawout=RAW/args.run;out.mkdir(exist_ok=False);rawout.mkdir(exist_ok=False)
    start=time.monotonic();rng=np.random.default_rng(20261006);c=Corpus()
    audit={'input_sha256':digest(c.path),'code_sha256':digest(__file__),'protocol_sha256':digest(OWN/'PROTOCOL.md'),'clarification_sha256':digest(OWN/'PRECOMPUTATION_CLARIFICATION.md'),'reused_group_code_sha256':digest(ROOT/'src/methods/conditional_structure.py'),'seed':20261006,'bootstrap':args.bootstrap,'permutations':args.permutations,'vocabulary_known_signs':c.v,'population':c.denom(c.all),'regions':dict(collections.Counter(c.region)),'object_type_corrections':dict(collections.Counter(r['object_type'] for r in c.rows if r['object_type']!=r['type'])),'physical_component_sizes':dict(collections.Counter(map(len,c.physical))),'text_component_sizes':dict(collections.Counter(map(len,c.textgroups))),'largest_physical_component':max(map(len,c.physical)),'largest_text_component':max(map(len,c.textgroups)),'fold_token_loads':c.foldloads,'site_region_multimapping':sum(len(set(c.region[c.site==s]))>1 for s in set(c.site))}
    assert c.n==5680 and len({r['object_family_id'] for r in c.rows})==4695
    assert int(c.length.sum())==19946
    assert np.array_equal(c.length,c.known+np.array([r['seq'].count('000') for r in c.rows]))
    assert all(len(set(c.fold[ids]))==1 for ids in c.physical+c.textgroups)
    assert audit['site_region_multimapping']==0
    audit['accounting_checks']='passed';save(out/'audit.json',audit)
    save(rawout/'record_membership.json',[{'record_id':r['record_id'],'physical':int(c.pid[i]),'text_component':int(c.tid[i]),'fold':int(c.fold[i]),'clear':bool(c.clear[i]),'periods':r['admissible'],'type':r['type']} for i,r in enumerate(c.rows)])
    mapping=[]
    for label in sorted({r['metadata']['time'] for r in c.rows if r['site']=='Harappa'}):
        ps=periods(label);mapping.append({'label':label,'admissible_periods':ps,'bce_oldest':max(DATES[p][0] for p in ps) if ps else None,'bce_youngest':min(DATES[p][1] for p in ps) if ps else None,'faces':sum(r['site']=='Harappa' and r['metadata']['time']==label for r in c.rows)})
    save(out/'period_mapping.json',mapping);save(out/'region_mapping.json',{'core':CORE,'external':EXTERNAL,'excluded':['South India','Other']})
    stratified_tables(c,out);attestation(c,out);print('tables complete',flush=True)
    time_results=[];region_results=[];tests=[];signs=[];rare=[]
    har=c.all[(c.site=='Harappa')&(c.known>0)]
    pselected=[p for p in PERIODS if len(set(c.pid[har[c.major[har]==p]]))>=30]
    rselected=[r for r in CORE if len(set(c.pid[c.all[(c.region==r)&(c.known>0)]]))>=30]
    for theme,selected,ids,labels in [('time',pselected,har,c.major),('region',rselected,c.all[np.isin(c.region,CORE)&(c.known>0)],c.region)]:
        for a,b in itertools.combinations(selected,2):
            aa=ids[labels[ids]==a];bb=ids[labels[ids]==b];name=a+'__'+b
            result=compare(c,aa,bb,name,rng,args.bootstrap,theme=='region')
            (time_results if theme=='time' else region_results).append(result)
            for closure in [False,True]:
                test,sig=permutation(c,aa,bb,name,rng,args.permutations,args.bootstrap,closure);test['theme']=theme;tests.append(test)
                if not closure:
                    for s in sig:s['theme']=theme
                    signs.extend(sig)
            if theme=='region':rare.append({'comparison':name,**rarefaction(c,aa,bb,rng)})
            print('comparison',theme,name,flush=True)
    for theme in ['time','region']:
        for unit in ['physical_component','full_text_closure']:
            keep=[t for t in tests if t['theme']==theme and t['unit']==unit and 'p' in t]
            for t,q in zip(keep,holm([t['p'] for t in keep])):t['holm_p']=q
        keep=[s for s in signs if s['theme']==theme]
        for s,q in zip(keep,bh([s['p'] for s in keep])):s['bh_q']=q
    save(out/'time_comparisons.json',time_results);save(out/'region_comparisons.json',region_results);save(out/'permutation_tests.json',tests);csv(out/'sign_tests.csv',signs);save(out/'rarefaction.json',rare)
    save(out/'interval_sensitivity.json',interval_sensitivity(c,rng));print('inference complete',flush=True)
    regional_models(c,out,rawout,args.bootstrap,rng);external_models(c,out,rawout,args.bootstrap,args.permutations,rng)
    audit['elapsed_seconds']=time.monotonic()-start;save(out/'audit.json',audit)
    save(out/'completion.json',{'status':'Verified computation','elapsed_seconds':audit['elapsed_seconds'],'aggregate_files':sorted(p.name for p in out.iterdir()),'local_details':str(rawout.relative_to(ROOT)).replace('\\','/')})
    print(json.dumps({'run':args.run,'elapsed_seconds':audit['elapsed_seconds'],'status':'complete'}),flush=True)

if __name__=='__main__':main()
