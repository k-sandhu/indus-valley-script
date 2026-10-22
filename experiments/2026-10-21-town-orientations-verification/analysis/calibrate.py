"""IntCal20 likelihood calibration on an annual grid and oldest-phase statistics."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np
from scipy.special import logsumexp

def curve(path):
    raw=np.loadtxt(path,delimiter=',',comments='#')
    raw=raw[np.argsort(raw[:,0])]
    if np.any(np.diff(raw[:,0])<=0): raise ValueError('curve dates not unique')
    return raw[:,:3]

def calibrate(bp,sigma,curve_path=RAW/'intcal20.14c'):
    if not math.isfinite(bp) or not math.isfinite(sigma) or sigma<=0: raise ValueError('BP finite; sigma positive')
    data=curve(curve_path)
    calbp=np.arange(math.ceil(data[0,0]),math.floor(data[-1,0])+1,dtype=float)
    mu=np.interp(calbp,data[:,0],data[:,1]);sc=np.interp(calbp,data[:,0],data[:,2])
    variance=sigma*sigma+sc*sc
    logp=-.5*((bp-mu)**2/variance+np.log(2*np.pi*variance))
    prob=np.exp(logp-logsumexp(logp))
    median=float(calbp[np.searchsorted(np.cumsum(prob),.5)])
    return dict(BP=bp,sigma_BP=sigma,cal_BP=calbp,astronomical_year=1950-calbp,
       probability=prob,median_cal_BP=median,median_astronomical_year=1950-median,
       assumptions='Uniform prior over 0..55000 cal BP. Linear interpolation of IntCal20 mean and sigma. Gaussian laboratory and curve errors added in quadrature. No reservoir correction.')

def phase(determinations,curve_path=RAW/'intcal20.14c'):
    if not determinations: raise ValueError('empty phase')
    results=[calibrate(float(d['BP']),float(d['sigma_BP']),curve_path) for d in determinations]
    # Oldest = maximum calendar BP. For independent dates, its CDF is the
    # product of their CDFs. Difference the product to obtain its annual PMF.
    cdfs=np.array([np.cumsum(r['probability']) for r in results])
    cdf=np.prod(np.clip(cdfs,0,1),axis=0)
    p=np.diff(np.r_[0,cdf]);p=np.maximum(p,0);p/=p.sum()
    grid=results[0]['cal_BP'];median=float(grid[np.searchsorted(np.cumsum(p),.5)])
    return dict(determinations=[{k:r[k] for k in ('BP','sigma_BP','median_cal_BP','median_astronomical_year')} for r in results],
       cal_BP=grid,astronomical_year=1950-grid,probability_oldest=p,
       median_oldest_cal_BP=median,median_oldest_astronomical_year=1950-median,
       oldest_individual_median_cal_BP=max(r['median_cal_BP'] for r in results),
       interpretation='Median of the distribution of the oldest determination, computed as the maximum cal BP of independent calibrated determinations. Shared curve error covariance is not modelled; this is not a Bayesian phase-start boundary.',
       assumptions=results[0]['assumptions'])

def selftest():
    data=curve(RAW/'intcal20.14c')
    checks={};reports=[]
    # At a curve knot, the likelihood must use the published 14C age and error.
    for knot in [1000,3000,4500,5500,8000]:
        i=np.argmin(abs(data[:,0]-knot));c,mu,sc=data[i]
        r=calibrate(float(mu),20.)
        grid=r['cal_BP'];j=int(c-grid[0])
        variance=20**2+np.interp(grid,data[:,0],data[:,2])**2
        expected=np.exp(-.5*((mu-np.interp(grid,data[:,0],data[:,1]))**2/variance+np.log(variance)))
        expected/=expected.sum()
        error=float(np.max(abs(expected-r['probability'])))
        checks[f'curve_value_{int(c)}']=abs(r['probability'].sum()-1)<1e-12 and error<1e-12 and abs(r['median_cal_BP']-c)<250
        reports.append(dict(curve_cal_BP=c,curve_14C_BP=mu,curve_sigma=sc,median_cal_BP=r['median_cal_BP'],median_error_years=r['median_cal_BP']-c,max_probability_difference=error))
    one=phase([dict(BP=4000,sigma_BP=30)])
    single=calibrate(4000,30)
    checks['one_phase_equals_single']=np.max(abs(one['probability_oldest']-single['probability']))<1e-12
    two=phase([dict(BP=4000,sigma_BP=30),dict(BP=5000,sigma_BP=30)])
    checks['oldest_older_than_each_median']=two['median_oldest_cal_BP']>=two['oldest_individual_median_cal_BP']
    checks['phase_normalizes']=abs(sum(two['probability_oldest'])-1)<1e-12
    return dict(all_pass=all(checks.values()),checks=checks,curve_value_tests=reports,
        oldest_test=dict(median_cal_BP=two['median_oldest_cal_BP'],oldest_individual_median_cal_BP=two['oldest_individual_median_cal_BP']))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bp',type=float);ap.add_argument('--sigma',type=float)
    ap.add_argument('--determinations',type=Path,help='JSON list of {BP,sigma_BP}')
    ap.add_argument('--curve',type=Path,default=RAW/'intcal20.14c')
    ap.add_argument('--selftest',action='store_true');ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists(): raise FileExistsError(a.output)
    inputs=[a.curve]
    if a.selftest: result=selftest()
    elif a.determinations:
        result=phase(json.loads(a.determinations.read_text()),a.curve);inputs.append(a.determinations)
    else:
        if a.bp is None or a.sigma is None: ap.error('--bp and --sigma required')
        result=calibrate(a.bp,a.sigma,a.curve)
    write_json(a.output,'intcal20-calibration',result,inputs=inputs,
               codes=[__file__,Path(__file__).with_name('common.py')],synthetic=a.selftest)
    print('wrote',a.output)
