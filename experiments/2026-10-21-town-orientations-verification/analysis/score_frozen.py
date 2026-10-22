"""The frozen target choice, P0--P3, power, credence and Wanzke checks."""
from pathlib import Path
import sys,itertools,math,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from predict import predict,theta_many,validation_gate
import numpy as np
from scipy.stats import chi2,rankdata

SIGMA_INT=1.0
SEED=20261021

def corr(x,y):
    x=np.asarray(x)-np.mean(x); y=np.asarray(y)-np.mean(y)
    den=np.linalg.norm(x)*np.linalg.norm(y)
    return float(x@y/den) if den else float('nan')

def permutation_p(x,y,rng,draws=200000):
    x=np.asarray(x,float);y=np.asarray(y,float)
    xc=x-x.mean();yc=y-y.mean()
    if not np.linalg.norm(xc)*np.linalg.norm(yc): return 1.,'undefined correlation',0
    observed=xc@yc; n=len(x)
    ge=0; total=0
    if n<=9:
        it=itertools.permutations(yc)
        while True:
            chunk=list(itertools.islice(it,10000))
            if not chunk: break
            dots=np.asarray(chunk) @ xc
            ge+=int(np.sum(dots>=observed-1e-12*max(1,abs(observed))))
            total+=len(chunk)
        return ge/total,'exact all permutations',total
    for start in range(0,draws,10000):
        count=min(10000,draws-start)
        perm=rng.permuted(np.broadcast_to(yc,(count,n)),axis=1)
        dots=perm @ xc
        ge+=int(np.sum(dots>=observed-1e-12*max(1,abs(observed))))
    return (ge+1)/(draws+1),'random permutations, plus-one p',draws

def p0(rows,rng):
    n=len(rows)
    x=np.array([r['D_year'] for r in rows]);y=np.array([r['theta_deg'] for r in rows])
    r=corr(x,y) if n>1 else float('nan')
    rho=corr(rankdata(x),rankdata(y)) if n>1 else float('nan')
    if n>=2: p,method,draws=permutation_p(x,y,rng)
    else: p,method,draws=None,'not enough towns',0
    loo=[dict(omitted=rows[i]['slug'],r=corr(np.delete(x,i),np.delete(y,i))) for i in range(n)] if n>2 else []
    survives=bool(loo) and all(v['r']>0 for v in loo)
    passed=p is not None and p<.05 and rho>0 and survives
    status='undecided' if n<8 else 'pass' if passed else 'fail'
    return dict(n=n,r=r,spearman_rho=rho,one_sided_p=p,p_method=method,permutations=draws,
                leave_one_out=loo,all_leave_one_out_positive=survives,status=status)

def slope(x,y,w):
    x,y,w=np.asarray(x),np.asarray(y),np.asarray(w)
    if len(x)<2 or w.sum()<=0: return float('nan')
    mx=np.average(x,weights=w);my=np.average(y,weights=w)
    den=np.sum(w*(x-mx)**2)
    return float(np.sum(w*(x-mx)*(y-my))/den) if den else float('nan')

def fit_slope(rows,rng,draws=20000):
    n=len(rows); x=np.array([r['D_year'] for r in rows]);y=np.array([r['theta_deg'] for r in rows])
    w=1/(np.array([r['sigma_theta_deg'] for r in rows])**2+SIGMA_INT**2)
    actual=slope(x,y,w)
    if n<2: return dict(slope_deg_per_year=actual,interval95_deg_per_year=[None,None],resamples=0,valid_resamples=0,reference_deg_per_century=.5)
    ix=rng.integers(0,n,(draws,n));xx=x[ix];yy=y[ix];ww=w[ix]
    mx=np.sum(xx*ww,axis=1)/ww.sum(axis=1);my=np.sum(yy*ww,axis=1)/ww.sum(axis=1)
    den=np.sum(ww*(xx-mx[:,None])**2,axis=1)
    num=np.sum(ww*(xx-mx[:,None])*(yy-my[:,None]),axis=1)
    bs=np.divide(num,den,out=np.full(draws,np.nan),where=den>0)
    valid=bs[np.isfinite(bs)]
    interval=np.quantile(valid,[.025,.975]).tolist() if len(valid) else [None,None]
    return dict(slope_deg_per_year=actual,slope_deg_per_century=actual*100,
      interval95_deg_per_year=interval,interval95_deg_per_century=[v*100 if v is not None else None for v in interval],
      resamples=draws,valid_resamples=len(valid),reference_deg_per_century=.5,
      bootstrap='paired resampling of towns with replacement; zero-date-variance resamples excluded')

def predictions(rows,extinction_variant,horizon_variant):
    values={}; sources=[]
    missing=any(any(r.get(k,'')=='' for k in ('thetac_'+c,'rate_'+c)) for r in rows for c in TARGETS)
    if missing: validation_gate()
    for r in rows:
        values[r['slug']]={}
        for c in TARGETS:
            tk,rk='thetac_'+c,'rate_'+c
            if r.get(tk,'')!='' and r.get(rk,'')!='':
                t,rate=r[tk],r[rk]; source='supplied CSV'
            else:
                t,rate=predict(c,r['lat'],r['lon'],r['D_year'],extinction_variant,horizon_variant)
                source='independent predictor'
            values[r['slug']][c]=(float(t),float(rate))
            sources.append(dict(slug=r['slug'],target=c,theta_deg=t,rate_deg_per_year=rate,source=source))
    return values,sources

def chisq(rows,c,values):
    return sum((r['theta_deg']-values[r['slug']][c][0])**2/
        (r['sigma_theta_deg']**2+(values[r['slug']][c][1]*r['sigma_D_years'])**2+SIGMA_INT**2) for r in rows)

def power(rows,rng,extinction_variant,horizon_variant,simulations=20000,permutations=2000,model=None):
    n=len(rows)
    if n<8: return dict(simulations=0,probability_P0_pass=None,reason='P0 requires at least eight towns')
    if model is None: validation_gate()
    dates=np.array([r['D_year'] for r in rows]); st=np.array([r['sigma_theta_deg'] for r in rows])
    sd=np.array([r['sigma_D_years'] for r in rows])
    drawdates=dates+rng.normal(size=(simulations,n))*sd
    means=np.empty_like(drawdates)
    for j,row in enumerate(rows):
        if model is None:
            means[:,j]=theta_many('alcyone',row['lat'],row['lon'],drawdates[:,j],extinction_variant,horizon_variant)
        else: means[:,j]=model(drawdates[:,j],j)
    y=means+rng.normal(size=(simulations,n))*st+rng.normal(size=(simulations,n))*SIGMA_INT
    dc=dates-dates.mean();rankc=rankdata(dates);rankc-=rankc.mean()
    count=0
    for start in range(0,simulations,100):
        yy=y[start:start+100];yc=yy-yy.mean(axis=1)[:,None]
        dot=yc@dc
        perm=rng.permuted(np.broadcast_to(dc,(len(yy),permutations,n)),axis=2)
        pdot=np.einsum('bpn,bn->bp',perm,yc,optimize=True)
        pp=(1+np.sum(pdot>=dot[:,None]-1e-12*np.maximum(1,np.abs(dot[:,None])),axis=1))/(permutations+1)
        rho_pos=(rankdata(yy,axis=1)@rankc)>0
        loo=np.all(dot[:,None]-n/(n-1)*yc*dc>0,axis=1)
        count+=int(np.sum((pp<.05)&rho_pos&loo))
    estimate=count/simulations
    return dict(simulations=simulations,permutations_per_simulation=permutations,
        p_method='2000 independent random permutations for each simulation, plus-one p; even for n <=9',
        probability_P0_pass=estimate,monte_carlo_standard_error=math.sqrt(estimate*(1-estimate)/simulations),
        generating_model='thetaAlcyone(D+Normal(0,sigmaD))+Normal(0,sigmaTheta)+Normal(0,1deg)',
        date_evaluation='direct vector evaluation of space motion, precession and horizon iteration at every drawn year',
        optional_columns='Optional theta/rate columns are used for observed scores. Power evaluates our Alcyone model at drawn dates.')

def score(rows,fixed_target=None,extinction_variant='base',horizon_variant='dem',
          seed=SEED,bootstrap=20000,simulations=20000,power_permutations=2000,model=None,values_override=None):
    rng=np.random.default_rng(seed)
    discovery=[r for r in rows if r['role']=='discovery']; conf=[r for r in rows if r['role']=='confirmation']
    if values_override is None: values,pred=predictions(rows,extinction_variant,horizon_variant)
    else: values,pred=values_override,[]
    scores={c:chisq(discovery,c,values) for c in TARGETS}
    choice=min(TARGETS,key=lambda c:scores[c]) if len(discovery)>=2 else None
    if fixed_target is not None and fixed_target not in TARGETS: raise ValueError('target')
    chosen=fixed_target or choice
    stage=dict(n=len(discovery),chi2=scores,would_choose=choice,chosen=chosen,choice_fixed=fixed_target is not None,
       threshold99=float(chi2.ppf(.99,len(discovery))) if discovery else None,
       discovery_failure=bool(choice is not None and scores[choice]>chi2.ppf(.99,len(discovery))),
       status='evaluated' if choice is not None else 'undecided: fewer than two discovery towns')
    allp=p0(rows,rng); confp=p0(conf,rng); fit=fit_slope(rows,rng,bootstrap)
    conf_fit=fit_slope(conf,rng,bootstrap)
    w=np.array([1/(r['sigma_theta_deg']**2+SIGMA_INT**2) for r in rows])
    dates=np.array([r['D_year'] for r in rows])
    alc=np.array([values[r['slug']]['alcyone'][0] for r in rows])
    predicted_slope=slope(dates,alc,w)
    lo,hi=fit['interval95_deg_per_year']
    positive=sum(r['theta_deg']>0 for r in rows); no_negative=all(r['theta_deg']>=-2*r['sigma_theta_deg'] for r in rows)
    interval_ok=lo is not None and lo<=predicted_slope<=hi and (hi<0 or lo>0)
    p1=dict(status='pass' if len(rows)>0 and positive/len(rows)>=.8 and no_negative and interval_ok else 'fail',
        positive_fraction=positive/len(rows) if rows else None,no_town_below_minus_2sigma=no_negative,
        interval_contains_predicted_and_excludes_zero=interval_ok,alcyone_predicted_slope_deg_per_year=predicted_slope,
        alcyone_mean_rate_deg_per_year=float(np.mean([values[r['slug']]['alcyone'][1] for r in rows])) if rows else None,
        interpretation='The predicted slope is the WLS slope of Alcyone theta at the observed town dates, with weights 1/(sigmaTheta^2+1deg^2). The mean local Alcyone rate is reported separately.')
    eligible=[r for r in rows if abs(values[r['slug']]['aldebaran'][0])>.5]
    matches=[r for r in eligible if r['theta_deg']*values[r['slug']]['aldebaran'][0]>0]
    p2=dict(eligible_n=len(eligible),sign_match_n=len(matches),
        sign_match_fraction=len(matches)/len(eligible) if eligible else None,
        status='undecided' if len(eligible)<8 else 'pass' if len(matches)/len(eligible)>=.8 else 'fail')
    offset=float(np.average([r['theta_deg'] for r in discovery],
            weights=[1/(r['sigma_theta_deg']**2+SIGMA_INT**2) for r in discovery])) if discovery else None
    def p3_metrics(sample):
        target=chisq(sample,chosen,values)
        cardinal=sum(r['theta_deg']**2/(r['sigma_theta_deg']**2+SIGMA_INT**2) for r in sample)
        constant=sum((r['theta_deg']-offset)**2/(r['sigma_theta_deg']**2+SIGMA_INT**2) for r in sample)
        return dict(target=target,cardinal=cardinal,constant_offset=constant)
    if chosen and conf and offset is not None:
        q=p3_metrics(conf);tail=float(chi2.sf(q['target'],len(conf)))
        order=lambda v:tuple(sorted(v,key=lambda k:(v[k],('target','cardinal','constant_offset').index(k))))
        fullorder=order(q)
        loo=[]
        for i,row in enumerate(conf):
            v=p3_metrics(conf[:i]+conf[i+1:])
            loo.append(dict(omitted=row['slug'],chi2=v,ordering=list(order(v)),
                            complete_order_survives=order(v)==fullorder,
                            target_remains_better=v['target']<min(v['cardinal'],v['constant_offset'])))
        p3=dict(status='pass' if q['target']<min(q['cardinal'],q['constant_offset']) and tail>.05 else 'fail',
          chi2=q,degrees_of_freedom=len(conf),target_upper_tail_probability=tail,
          discovery_constant_offset_deg=offset,ordering=list(fullorder),leave_one_out=loo,
          complete_order_survives_all=all(v['complete_order_survives'] for v in loo),
          target_better_survives_all=all(v['target_remains_better'] for v in loo))
    else: p3=dict(status='undecided',reason='requires selected target, discovery offset and confirmation towns')
    if len(rows)<8: cred,status=.10,'open'
    elif allp['status']=='fail': cred,status=.02,'dead'
    elif allp['status']=='pass' and p3['status']=='pass': cred,status=.40,'open'
    elif allp['status']=='pass' and p3['status']=='fail': cred,status=.15,'open'
    else: cred,status=.10,'open'
    d1=[]
    for row in rows:
        if row['slug']=='mohenjo-daro':
            t,s=row['theta_deg'],row['sigma_theta_deg']
            d1.append(dict(slug=row['slug'],theta_deg=t,sigma_deg=s,
               figure_7p2_within_2sigma=abs(t-7.2)<=2*s,
               interval_1_to_2_intersects_2sigma=(t+2*s>=1 and t-2*s<=2),
               whole_interval_1_to_2_within_2sigma=(t-2*s<=1 and t+2*s>=2),
               interval_interpretation='The interval is compatible when it intersects [theta-2sigma,theta+2sigma]; full containment is also reported.'))
    pw=power(rows,rng,extinction_variant,horizon_variant,simulations,power_permutations,model)
    return dict(n=len(rows),sigma_int_deg=SIGMA_INT,seed=seed,target_order=TARGETS,
        variant=dict(extinction=extinction_variant,horizon=horizon_variant),
        stage1=stage,P0=allp,P0_confirmation=confp,WLS_all=fit,WLS_confirmation=conf_fit,
        P1=p1,P2=p2,P3=p3,power=pw,credence=cred,status=status,D1=d1,predictions=pred)

def selftest():
    def rows_for(sign=1,n=11):
        rows=[]
        for i in range(n):
            d=-2999+i*100
            r=dict(slug=['mohenjo-daro','harappa','kalibangan'][i] if i<3 else f'synthetic-{i}',part='whole',
                role='discovery' if i<3 else 'confirmation',lat=27.324,lon=68.136,
                theta_deg=sign*(1+.01*(d+2999)),sigma_theta_deg=.3,D_year=d,sigma_D_years=0.)
            for j,c in enumerate(TARGETS):
                r['thetac_'+c]=1+.01*(d+2999)+(0 if j==0 else j*8)
                r['rate_'+c]=.01
            rows.append(r)
        return rows
    rows=rows_for()
    # Full production counts exercise permutation, bootstrap and power code.
    model=lambda d,j:1+.01*(d+2999)
    result=score(rows,model=model)
    dead=score(rows_for(-1),model=model,simulations=100)
    short=score(rows_for(n=7),model=model)
    fixed=score(rows,fixed_target='procyon',model=model,simulations=100)
    failrows=rows_for()
    for r in failrows: r['theta_deg']+=100
    failure=score(failrows,model=model,simulations=100)
    tied=rows_for()
    for r in tied:
        for c in TARGETS: r['thetac_'+c]=r['thetac_alcyone']
    tievalues,_=predictions(tied,'base','flat')
    # Test tie order without repeating an expensive simulation.
    ds=[r for r in tied if r['role']=='discovery']
    choice=min(TARGETS,key=lambda c:chisq(ds,c,tievalues))
    exact=p0(rows[:8],np.random.default_rng(SEED))
    checks=dict(monotone_P0=result['P0']['status']=='pass',monotone_P1=result['P1']['status']=='pass',
       monotone_P2=result['P2']['status']=='pass',alcyone_selected=result['stage1']['chosen']=='alcyone',
       perfect_model_P3=result['P3']['status']=='pass',credence_point4=result['credence']==.4,
       negative_dead=dead['status']=='dead' and dead['credence']==.02,
       short_open=short['P0']['status']=='undecided' and short['credence']==.1,
       fixed_target=fixed['stage1']['chosen']=='procyon' and fixed['stage1']['would_choose']=='alcyone',
       discovery_failure=failure['stage1']['discovery_failure'],tie_order=choice=='alcyone',
       exact_permutations=exact['permutations']==math.factorial(8) and abs(exact['one_sided_p']-1/math.factorial(8))<1e-15,
       power_high=result['power']['probability_P0_pass']>.95)
    return dict(all_pass=all(checks.values()),checks=checks,positive_case=result,
                negative_summary=dict(P0=dead['P0']['status'],credence=dead['credence']),
                short_summary=dict(P0=short['P0']['status'],credence=short['credence']),
                exact_eight=dict(p=exact['one_sided_p'],permutations=exact['permutations']))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('csv',type=Path,nargs='?');ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--fixed-target',choices=TARGETS);ap.add_argument('--seed',type=int,default=SEED)
    ap.add_argument('--extinction',choices=['base','k020','k045','none'],default='base')
    ap.add_argument('--horizon',choices=['dem','flat'],default='dem');ap.add_argument('--selftest',action='store_true')
    a=ap.parse_args()
    if a.output.exists(): raise FileExistsError(a.output)
    if a.selftest: result=selftest();inputs=[]
    else:
        if a.csv is None: ap.error('CSV required')
        result=score(read_table(a.csv),a.fixed_target,a.extinction,a.horizon,a.seed);inputs=[a.csv]
        if (OUT/'validation-v1.json').exists(): inputs += [OUT/'validation-v1.json',OUT/'stars-retrieved-v1.json']
        inputs += list((OUT/'horizon').glob('*.json'))
    codes=list(Path(__file__).parent.glob('*.py'))+list((PACKAGE/'astronomy').glob('*.py'))
    write_json(a.output,'score-frozen',result,inputs=inputs,codes=codes,synthetic=a.selftest)
    print(json.dumps(clean(result),indent=2))
