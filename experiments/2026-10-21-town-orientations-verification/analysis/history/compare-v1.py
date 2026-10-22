"""Compare independent settlement measurements, dates and astronomical tables."""
from pathlib import Path
import sys,csv,json,math
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np

def compare_settlements(first,second):
    a={r['slug']:r for r in first};b={r['slug']:r for r in second}
    common=sorted(a.keys()&b.keys())
    if not common: raise ValueError('no common settlements')
    diffs=[]
    for slug in common:
        r,s=a[slug],b[slug]
        delta=r['theta_deg']-s['theta_deg']
        variance=r['sigma_theta_deg']**2+s['sigma_theta_deg']**2
        if variance<=0: raise ValueError('zero combined measurement variance')
        dd=r['D_year']-s['D_year'];limit=max(100,s['sigma_D_years'])
        diffs.append(dict(slug=slug,part_first=r['part'],part_second=s['part'],
          theta_delta_deg=delta,combined_sigma_deg=math.sqrt(variance),z=delta/math.sqrt(variance),
          date_delta_years=dd,date_tolerance_years=limit,date_agree=abs(dd)<=limit))
    delta=np.array([r['theta_delta_deg'] for r in diffs]);z=np.array([r['z'] for r in diffs])
    weights=1/np.array([r['combined_sigma_deg']**2 for r in diffs])
    mean=float(np.average(delta,weights=weights));se=float(1/np.sqrt(weights.sum()))
    fraction=float(np.mean(np.abs(z)<=2.5));datefraction=float(np.mean([r['date_agree'] for r in diffs]))
    bearings=dict(weighted_mean_delta_deg=mean,weighted_mean_standard_error_deg=se,
        median_absolute_delta_deg=float(np.median(abs(delta))),
        root_mean_square_delta_deg=float(np.sqrt(np.mean(delta*delta))),
        fraction_abs_z_le_2p5=fraction,abs_z_gt_2=[r['slug'] for r in diffs if abs(r['z'])>2],
        abs_z_gt_3=[r['slug'] for r in diffs if abs(r['z'])>3],
        verdict='agree' if (abs(mean)<=2*se or abs(mean)<=.5) and fraction>=.8 else 'disagree')
    return dict(n_common=len(common),only_first=sorted(a.keys()-b.keys()),only_second=sorted(b.keys()-a.keys()),
        deviations=bearings,dates=dict(fraction_within_tolerance=datefraction,verdict='agree' if datefraction>=.8 else 'disagree'),
        towns=diffs)

def read_astro(path):
    data={}
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            year=float(row.get('year',row.get('D_year','nan')))
            lat,lon=float(row['lat']),float(row['lon'])
            if not all(map(math.isfinite,[year,lat,lon])): raise ValueError('astronomy coordinates and date required')
            if row.get('target'):
                vals={row['target']:float(row.get('theta_base',row.get('theta_deg','nan')))}
            else: vals={c:float(row['thetac_'+c]) for c in TARGETS if row.get('thetac_'+c,'')!=''}
            for c,t in vals.items():
                if c not in TARGETS or not math.isfinite(t): raise ValueError('invalid astronomy value')
                key=(row['slug'],lat,lon,year,c)
                if key in data: raise ValueError('duplicate astronomy key')
                data[key]=t
    return data

def compare_astronomy(a,b):
    if set(a)!=set(b): raise ValueError('astronomy tables must have identical town, coordinate, date and target keys')
    result={}
    for c in TARGETS:
        vals=[(k,abs(a[k]-b[k])) for k in a if k[-1]==c]
        worst=max(vals,key=lambda x:x[1]) if vals else None
        result[c]=dict(n=len(vals),max_absolute_difference_deg=worst[1] if worst else None,
            worst_key=list(worst[0]) if worst else None,
            verdict='undecided' if worst is None else 'agree' if worst[1]<=.1+1e-12 else 'disagree')
    return dict(targets=result,verdict='agree' if all(v['verdict']=='agree' for v in result.values()) else
                'disagree' if any(v['verdict']=='disagree' for v in result.values()) else 'undecided')

def selftest():
    a=[dict(slug=f'test-{i}',part='whole',role='confirmation',lat=25.,lon=70.,theta_deg=float(i),
            sigma_theta_deg=1.,D_year=-2500.+i*100,sigma_D_years=150.) for i in range(10)]
    b=[dict(r,theta_deg=r['theta_deg']-.4,D_year=r['D_year']-100) for r in a]
    good=compare_settlements(a,b)
    bad=compare_settlements(a,[dict(r,theta_deg=r['theta_deg']-10,D_year=r['D_year']-400) for r in a])
    astro={(r['slug'],r['lat'],r['lon'],r['D_year'],c):float(i) for i,r in enumerate(a) for c in TARGETS}
    astrogood=compare_astronomy(astro,{k:v+.05 for k,v in astro.items()})
    astrobad=compare_astronomy(astro,{k:v+.11 for k,v in astro.items()})
    checks=dict(agreement=good['deviations']['verdict']=='agree',date_agreement=good['dates']['verdict']=='agree',
        disagreement=bad['deviations']['verdict']=='disagree',date_disagreement=bad['dates']['verdict']=='disagree',
        weighted_mean=abs(good['deviations']['weighted_mean_delta_deg']-.4)<1e-12,
        standard_error=abs(good['deviations']['weighted_mean_standard_error_deg']-math.sqrt(.2))<1e-12,
        astronomy_agree=astrogood['verdict']=='agree',astronomy_disagree=astrobad['verdict']=='disagree')
    # One outlier is listed with the correct signed z.
    one=[dict(r) for r in b];one[0]['theta_deg']-=10
    out=compare_settlements(a,one)
    checks['outlier_lists']='test-0' in out['deviations']['abs_z_gt_3']
    return dict(all_pass=all(checks.values()),checks=checks,agree_case=good,
                astronomy_good=astrogood,astronomy_bad=astrobad)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('first',type=Path,nargs='?');ap.add_argument('second',type=Path,nargs='?')
    ap.add_argument('--astro-first',type=Path);ap.add_argument('--astro-second',type=Path)
    ap.add_argument('--selftest',action='store_true');ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists(): raise FileExistsError(a.output)
    inputs=[]
    if a.selftest: result=selftest()
    else:
        result={}
        if a.first and a.second:
            result['settlements']=compare_settlements(read_table(a.first),read_table(a.second));inputs += [a.first,a.second]
        elif a.first or a.second: ap.error('both settlement files required')
        if a.astro_first and a.astro_second:
            result['astronomy']=compare_astronomy(read_astro(a.astro_first),read_astro(a.astro_second));inputs += [a.astro_first,a.astro_second]
        elif a.astro_first or a.astro_second: ap.error('both astronomy files required')
        if not result: ap.error('supply settlement or astronomy pair')
    write_json(a.output,'compare-town-tables',result,inputs=inputs,codes=[__file__,Path(__file__).with_name('common.py')],synthetic=a.selftest)
    print(json.dumps(clean(result),indent=2))
