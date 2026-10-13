"""Enumerate declared reviewer counterexamples; no historical calibration."""
import argparse
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(f'Refusing existing output: {args.output}')
    results={}
    stock={}
    for horizon in [3,4]:
        path=list(range(4,4-horizon-1,-1))
        stock[str(horizon)]={'path':path,'safe':all(x>=1 for x in path),'renewal_actions_available':0}
    results['finite_stock']={'cases':stock,'rejected_implication':'Finite-horizon survival always requires an available renewal route.'}
    joint={}
    for budget in [1,2]:
        actions=[u for u in product([0,1],repeat=2) if sum(u)<=budget]
        joint[str(budget)]={'admissible_actions':actions,'joint_safe_actions':[u for u in actions if min(u)>=1],
                            'separate_safe_actions':[[u[i] for u in actions if u[i]>=1] for i in [0,1]]}
    results['joint_budget']={'cases':joint,'rejected_implication':'A feasible plan for each service separately implies one jointly feasible plan.'}
    matrix={str(u):{str(w):u==w for w in [0,1]} for u in [0,1]}
    results['observation_timing']={'safe_matrix':matrix,
        'action_before_shock':any(all(matrix[str(u)][str(w)] for w in [0,1]) for u in [0,1]),
        'shock_observed_before_action':all(any(matrix[str(u)][str(w)] for u in [0,1]) for w in [0,1]),
        'rejected_implication':'Robust feasibility is unchanged when current-shock observation timing changes.'}
    profiles=[(0,0),(1,0),(0,1)]
    def payoff(u,i):return int(any(u))-2*u[i]
    equilibria=[]
    for u in profiles:
        stable=True
        for i in [0,1]:
            for alternative in profiles:
                if alternative[1-i]==u[1-i] and payoff(alternative,i)>payoff(u,i):stable=False
        if stable:equilibria.append(u)
    results['implementation']={'feasible_profiles':profiles,'safe_profiles':[u for u in profiles if any(u)],
        'pure_generalized_nash_equilibria':equilibria,'equilibrium_safe_profiles':[u for u in equilibria if any(u)],
        'payoffs':{str(u):[payoff(u,i) for i in [0,1]] for u in profiles},
        'rejected_implication':'Existence of a joint resource-feasible repair plan establishes voluntary implementation.'}
    allocations=[(i,2-i) for i in range(3)]
    results['distribution']={'allocations':allocations,'aggregate_safe':[a for a in allocations if sum(a)>=2],
        'resident_safe':[a for a in allocations if min(a)>=1],
        'rejected_implication':'Aggregate provision implies every selected resident receives its stated minimum.'}
    imports={}
    for horizon,allowed in product([3,4],[[0],[0,1]]):
        paths=[]
        for sequence in product(allowed,repeat=horizon):
            x,external=1,3;path=[(x,external)];safe=True
            for m in sequence:
                x=x-1+m;external=external-m;path.append((x,external))
                if x<1 or external<0:safe=False
            if safe:paths.append({'imports':sequence,'state_path':path})
        imports[f'h{horizon}_imports{max(allowed)}']={'safe_paths':paths}
    results['open_boundary']={'cases':imports,'rejected_implication':'Local safe supply proves local self-sufficiency or unlimited upstream renewability.'}
    assertions={
        'stock_3_safe_4_unsafe':stock['3']['safe'] and not stock['4']['safe'],
        'budget_1_no_joint_budget_2_joint':not joint['1']['joint_safe_actions'] and bool(joint['2']['joint_safe_actions']),
        'quantifier_order_differs':not results['observation_timing']['action_before_shock'] and results['observation_timing']['shock_observed_before_action'],
        'feasible_safety_without_safe_equilibrium':bool(results['implementation']['safe_profiles']) and not results['implementation']['equilibrium_safe_profiles'],
        'aggregate_does_not_imply_resident_safety':len(results['distribution']['aggregate_safe'])>len(results['distribution']['resident_safe']),
        'imports_hide_finite_external_stock':bool(imports['h3_imports1']['safe_paths']) and not imports['h4_imports1']['safe_paths'] and not imports['h3_imports0']['safe_paths']}
    if not all(assertions.values()):raise AssertionError(assertions)
    args.output.mkdir(parents=True)
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(),scope='Invented reviewer laws; no historical verification',
                input_hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['PROTOCOL.md','COUNTEREXAMPLES-PROTOCOL.md','counterexamples.py']},
                results=results,assertions=assertions)
    (args.output/'counterexamples.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(assertions))

if __name__=='__main__':main()
