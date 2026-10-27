"""Separate Decimal arithmetic and matrix least-squares checks of saved readings."""
from decimal import Decimal, localcontext
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

P=Path(__file__).resolve().parent
R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test')

def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def d(value): return Decimal(str(value))

def length(a,b):
    return sum((d(x)-d(y))**2 for x,y in zip(a,b)).sqrt()

def calculate(points,bar,s,e,eb):
    with localcontext() as ctx:
        ctx.prec=50
        chord=length(*points);cal=length(*bar)
        estimate=d(s)*chord/cal
        low=d(s)*max(Decimal(0),chord-2*d(e))/(cal+2*d(eb))
        high=d(s)*(chord+2*d(e))/(cal-2*d(eb))
        return [float(estimate),float(low),float(high)]

def compare(label,calc,held,tolerance):
    differences=[abs(x-y) for x,y in zip(calc,held)]
    return {'id':label,'independent_result':calc,'held_result':held,
            'tolerance':tolerance,'maximum_difference':max(differences),
            'passed':max(differences)<=tolerance}

def main(tag):
    out=P/f'measurement-review-{tag}.json'
    if out.exists():raise FileExistsError('Preserve review.')
    inputs=[R/'plans-east/manual-endpoints-v1.json',R/'plans-west/traces-v1.json',
            R/'mohenjo-control/measurement-inputs-v1.json']
    checks=[]
    east={r['id']:r for r in read(P/'modules/plans-east/measurements.json')['measured']}
    for r in read(inputs[0])['measurements']:
        if r['id'] not in east:continue # withdrawn angle remains withdrawn
        target=east[r['id']]
        if r['kind']=='length':
            calc=calculate(r['points'],r['scale_points'],r['scale_m'],r['endpoint_radius_px'],r['bar_endpoint_radius_px'])
        else:
            a,v,b=r['points'];u=[x-y for x,y in zip(a,v)];w=[x-y for x,y in zip(b,v)]
            angle=math.degrees(math.atan2(abs(u[0]*w[1]-u[1]*w[0]),sum(x*y for x,y in zip(u,w))))
            delta=sum(math.degrees(math.asin(2*r['endpoint_radius_px']/math.hypot(*arm))) for arm in (u,w))
            calc=[angle,max(0,angle-delta),min(180,angle+delta)]
        checks.append(compare(r['id'],calc,[target['value'],*target['reading_bound']],0.00051))
    west=read(P/'modules/plans-west/measurements.json')
    byid={r['id']:r for r in west['measurements']}
    traces=read(inputs[1])
    for r in traces['measurements']:
        target=byid[r['id']]
        calc=calculate(r['feature_endpoints'],r['scale_endpoints'],r['scale_metres'],r['feature_endpoint_radius_px'],r['scale_endpoint_radius_px'])
        checks.append(compare(r['id'],calc,[target['metres'],*target['digitization_sensitivity_metres']],1e-11))
    md={r['id']:r for r in read(P/'modules/mohenjo-control/measurements.json')['rows']}
    for r in read(inputs[2])['items']:
        if r['feature'] is None:continue
        target=md[r['id']]
        calc=calculate(r['feature'],r['bar'],r['bar_metres'],r['feature_radius_px'],r['bar_radius_px'])
        checks.append(compare(r['id'],calc,[target['estimate_m'],target['reading_lower_m'],target['reading_upper_m']],1e-11))
        if r.get('alternative_feature'):
            alt=calculate(r['alternative_feature'],r['bar'],r['bar_metres'],r['feature_radius_px'],r['bar_radius_px'])
            held=target['alternative_edge']
            checks.append(compare(r['id']+'-alternative',alt,[held['estimate_m'],held['reading_lower_m'],held['reading_upper_m']],1e-11))
    registration=[]
    summaries={r['panel']:r for r in west['registration']['fits']}
    for panel,control in traces['registration']['controls'].items():
        # Independent real matrix parameterisation, not module's complex formula.
        X=[];Y=[]
        for c in control:
            x,y=c['pixel'];E,N=c['grid']
            X.extend([[x,y,1,0],[-y,x,0,1]])
            Y.extend([E-2355,N-1015])
        beta=np.linalg.lstsq(np.array(X,float),np.array(Y,float),rcond=None)[0]
        residuals=(np.array(X)@beta-np.array(Y)).reshape(-1,2)
        rmse=float(np.sqrt(np.mean(np.sum(residuals**2,axis=1))))
        held=[]
        for c in traces['registration']['held_out_controls'][panel]:
            x,y=c['pixel'];E,N=c['grid']
            estimate=np.array([[x,y,1,0],[-y,x,0,1]])@beta
            held.append(float(np.linalg.norm(estimate-np.array([E-2355,N-1015]))))
        registration.append(compare(panel,[rmse,max(held)],
                                    [summaries[panel]['grid_fit_rmse_metres'],summaries[panel]['held_out_max_error_metres']],1e-10))
    result={'method':'Separate Decimal50 Euclidean length arithmetic, atan2 angle, and real matrix least-squares registration; saved clicks reused.',
            'input_hashes':[{'physical_path':str(f),'sha256':sha(f)} for f in inputs],
            'quantity_checks':checks,'registration_checks':registration,
            'limits':'Checks saved arithmetic, not correctness of ancient survey or independence of archaeological events. Visual source review is recorded separately.',
            'passed':all(c['passed'] for c in checks+registration)}
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'quantity_checks':len(checks),'registration_checks':len(registration),'passed':result['passed'],
                      'failures':[c for c in checks+registration if not c['passed']]}))
    assert result['passed']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--tag',default='v1')
    main(parser.parse_args().tag)
