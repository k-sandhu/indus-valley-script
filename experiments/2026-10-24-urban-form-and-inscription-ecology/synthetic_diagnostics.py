"""Exact generated controls for orientation summaries and future sample planning."""
from pathlib import Path
import argparse
import cmath
import hashlib
import json
import math

def q4(angles):
    return abs(sum(cmath.exp(4j*math.radians(a)) for a in angles)/len(angles))

def tail(n,k,p):
    return math.fsum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))

def main(out):
    out.mkdir()
    grids=[]
    for angle in [0,15,30,45]:
        a=[0,90]*50
        b=[angle,angle+90]*50
        grids.append(dict(district_offset_degrees=angle,angles_by_district=[a,b],global_q4=q4(a+b),local_q4=[q4(a),q4(b)]))
    power=[]
    for n in [20,40,80,120]:
        critical=next(k for k in range(n+1) if tail(n,k,.5)<=.025)
        for p in [.60,.65,.70,.75]:
            power.append(dict(independent_non_tied_pairs=n,critical_positive_pairs=critical,one_sided_alpha=.025,
                              attained_null_alpha=tail(n,critical,.5),true_positive_pair_probability=p,power=tail(n,critical,p)))
    tests=dict(perfect_grid=math.isclose(q4([0,90,180,270]),1,abs_tol=1e-12),
               thirty_degree_mosaic=math.isclose(grids[2]['global_q4'],.5,abs_tol=1e-12),
               forty_five_degree_mosaic=grids[3]['global_q4']<1e-12,
               rotation_invariance=math.isclose(q4([1,89,23,110]),q4([a+17 for a in [1,89,23,110]]),abs_tol=1e-12),
               binomial_mass=math.isclose(tail(20,0,.7),1,abs_tol=1e-12),
               exact_null_n20=math.isclose(tail(20,15,.5),21700/1048576,abs_tol=1e-12))
    # 21,700 = sum(C(20,j), j=15,...,20), an independent integer certificate.
    result=dict(status_class='synthetic',synthetic=True,archaeological_measurements=0,
                orientation_source='Barthelemy and Boeing 2026 v1, III.3; formula applied only to generated angles, no clustering reproduced',
                orientation=grids,power=power,checks=tests,passed=all(tests.values()),
                power_scope='Exact sign-test power for independent non-tied pairs. An optimistic planning reference; clustered towns, dependent contexts, ties and recovery bias are not represented.',
                code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],checks=tests,power_at_p70=[r for r in power if r['true_positive_pair_probability']==.7]),indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',required=True,type=Path)
    raise SystemExit(main(parser.parse_args().out))
