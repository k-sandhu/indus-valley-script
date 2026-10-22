"""Run reproducible synthetic checks for all three analysis scripts."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import score_frozen,compare,calibrate
from predict import theta,theta_many,validation_gate,write_table
import numpy as np

def run():
    validation_gate()
    print('score selftest',flush=True);score=score_frozen.selftest()
    print('compare selftest',flush=True);comp=compare.selftest()
    print('calibration selftest',flush=True);cal=calibrate.selftest()
    vector=[]
    for target in TARGETS[:3]:
        for ext,hor in [('base','dem'),('k020','dem'),('k045','dem'),('none','dem'),('base','flat')]:
            years=np.array([-3499.,-2999.,-2499.,-1999.,-1499.,2026.8])
            actual=theta_many(target,27.324,68.136,years,ext,hor)
            expected=np.array([theta(target,27.324,68.136,float(y),ext,hor) for y in years])
            difference=float(max(abs(actual-expected)))
            vector.append(dict(target=target,extinction=ext,horizon=hor,max_difference_deg=difference,pass_=difference<.001))
    good=score['all_pass'] and comp['all_pass'] and cal['all_pass'] and all(x['pass_'] for x in vector)
    return dict(all_pass=good,score_frozen=score,compare=comp,calibrate=cal,vector_scalar=vector)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists(): raise FileExistsError(a.output)
    result=run()
    write_json(a.output,'analysis-selftests',result,inputs=[RAW/'intcal20.14c',OUT/'stars-retrieved-v1.json',OUT/'validation-v1.json',OUT/'horizon/mohenjo-daro.json'],
       codes=list(Path(__file__).parent.glob('*.py'))+list((PACKAGE/'astronomy').glob('*.py')),synthetic=True)
    print('all_pass',result['all_pass'])
    for k in ('score_frozen','compare','calibrate'): print(k,result[k]['checks'])
    if not result['all_pass']:raise SystemExit(1)
