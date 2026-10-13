"""Independent finite transition/game reconstruction; never imports root code."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import product, combinations
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
STATES=set(product(range(3),range(3),range(4)))
SAFE={s for s in STATES if min(s[:2])>0}
SUPPORTS={'none':[(0,0)],'focal':[(0,0),(1,0)],
          'common':[(0,0),(1,1)],'full':[(0,0),(1,0),(0,1),(1,1)]}
PRIMARY=(2,2,3)
TASKS=('renew_A','renew_B','train')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def admissible(s,budget,age,after_age=False):
    skill=s[2]-age if after_age else s[2]
    for u in product([0,1],repeat=3):
        if sum(u)<=budget and (not any(u) or skill>0):yield u

def next_state(s,u,w,age,severity=1):
    aged=[max(0,s[i]-1) for i in range(2)]
    assets=[2 if u[i] else aged[i] for i in range(2)]
    k=3 if u[2] else max(0,s[2]-age)
    return tuple(max(0,assets[i]-severity*w[i]) for i in range(2))+(k,)

def reconstruction(budget,age,support,mode,severity=1,after_age=False):
    # Build the action-successor relation once. Then eliminate losing vertices.
    relation={s:[(u,{next_state(s,u,w,age,severity) for w in SUPPORTS[support]})
                  for u in admissible(s,budget,age,after_age)] for s in SAFE}
    current=set(SAFE);layers=[set(current)]
    while True:
        if mode=='robust':
            new={s for s in SAFE if any(successors<=current for u,successors in relation[s])}
        else:
            new={s for s in SAFE if any(bool(successors & current) for u,successors in relation[s])}
        if new==current:break
        if not new<=current:raise AssertionError('Elimination ceased to be descending')
        layers.append(set(new));current=new
    finite=[layers[h] if h<len(layers) else current for h in range(13)]
    max_safe=None if PRIMARY in current else max(h for h,v in enumerate(layers) if PRIMARY in v)
    return dict(layers=layers,finite=finite,kernel=current,max_safe=max_safe,relation=relation)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(f'Refusing existing output: {args.output}')
    result_path=ROOT/'coordinator/run-v1/results.json'
    root=json.loads(result_path.read_text(encoding='utf-8'))
    checks=[]
    def check(label,value):
        checks.append({'check':label,'passed':bool(value)})
        if not value:raise AssertionError(label)
    check('36 declared states',root['state_count']==len(STATES)==36)
    check('16 declared safe states',root['safe_state_count']==len(SAFE)==16)
    check('root protocol hash',root['protocol_sha256']==digest(ROOT/'coordinator/MODEL-PROTOCOL.md'))
    check('root code hash',root['code_sha256']==digest(ROOT/'coordinator/renewal_model.py'))
    keys={(w['budget'],w['skill_age'],w['shock_support']) for w in root['worlds']}
    check('all and only 32 worlds',keys==set(product(range(4),range(2),SUPPORTS)))
    reconstructed=[]
    for w in root['worlds']:
        b,age,support=w['budget'],w['skill_age'],w['shock_support']
        world={'budget':b,'skill_age':age,'shock_support':support}
        for mode in ['possible','robust']:
            rebuilt=reconstruction(b,age,support,mode);given=w[mode];prefix=f'{b}/{age}/{support}/{mode}'
            check(prefix+' quantifier',given['quantifier']==('exists_action_forall_shocks' if mode=='robust' else 'exists_action_exists_shock'))
            check(prefix+' horizon keys',[r['transitions'] for r in given['finite_horizons']]==list(range(13)))
            for h,row in enumerate(given['finite_horizons']):
                check(prefix+f' V{h} states',{tuple(s) for s in row['states']}==rebuilt['finite'][h])
                check(prefix+f' V{h} counts',row['count']==len(rebuilt['finite'][h])==len(row['states']))
                check(prefix+f' V{h} primary',row['primary_viable']==(PRIMARY in rebuilt['finite'][h]))
            check(prefix+' fixed-point layer count',len(given['fixed_point_layers'])==len(rebuilt['layers']))
            for h,row in enumerate(given['fixed_point_layers']):
                check(prefix+f' fixed layer {h}',row['iteration']==h and {tuple(s) for s in row['states']}==rebuilt['layers'][h] and row['count']==len(rebuilt['layers'][h]))
            check(prefix+' infinite set',{tuple(s) for s in given['infinite_kernel']}==rebuilt['kernel'])
            check(prefix+' infinite count',given['infinite_count']==len(rebuilt['kernel'])==len(given['infinite_kernel']))
            check(prefix+' primary result',given['primary']['infinite_viable']==(PRIMARY in rebuilt['kernel']) and given['primary']['maximum_safe_transitions_if_finite']==rebuilt['max_safe'])
            policy=given['infinite_policy']
            check(prefix+' policy domain',{tuple(r['state']) for r in policy}==rebuilt['kernel'] and len(policy)==len(rebuilt['kernel']))
            for row in policy:
                s=tuple(row['state']);u=tuple(int(name in row['action']) for name in TASKS)
                check(prefix+' permitted policy '+str(s),set(row['action'])<=set(TASKS) and len(row['action'])==sum(u) and u in list(admissible(s,b,age)))
                by_shock={tuple(r['shock']):r for r in row['successors']}
                check(prefix+' complete policy shocks '+str(s),set(by_shock)==set(SUPPORTS[support]) and len(by_shock)==len(row['successors']))
                membership=[]
                for shock,r in by_shock.items():
                    dest=next_state(s,u,shock,age);inside=dest in rebuilt['kernel'];membership.append(inside)
                    check(prefix+' policy successor '+str(s)+'/'+str(shock),tuple(r['state'])==dest and r['in_kernel']==inside)
                check(prefix+' policy quantifier '+str(s),all(membership) if mode=='robust' else any(membership))
            world[mode]={'finite_counts':[len(v) for v in rebuilt['finite']],
                         'fixed_point_layers':[sorted(v) for v in rebuilt['layers']],
                         'infinite_kernel':sorted(rebuilt['kernel']),'primary_max_safe':rebuilt['max_safe']}
        reconstructed.append(world)
    dependency=[]
    for case in root['dependency_cases']:
        components=case['components'];services=case['services'];losses={}
        for bits in product([0,1],repeat=len(components)):
            failed=frozenset(c for c,v in zip(components,bits) if v)
            lost=tuple(k for k,routes in services.items() if all(bool(set(route)&failed) for route in routes))
            if lost:losses[failed]=lost
        minimal={s:lost for s,lost in losses.items() if not any(t<s for t in losses)}
        given={frozenset(r['failed_components']):tuple(r['lost_services']) for r in case['inclusion_minimal_service_failure_sets']}
        check('dependency complete enumeration '+str(case['shared_input']),case['failure_sets_enumerated']==2**len(components))
        check('dependency minimal sets '+str(case['shared_input']),given==minimal)
        check('dependency minimum '+str(case['shared_input']),case['minimum_failure_cardinality']==min(map(len,minimal)))
        check('dependency no probabilities '+str(case['shared_input']),case['probabilities'] is None)
        dependency.append({'shared_input':case['shared_input'],'minimal_failure_sets':[sorted(v) for v in sorted(minimal,key=lambda v:(len(v),sorted(v)))],'minimum':min(map(len,minimal))})
    inverse=[]
    for case in root['inverse_bound_controls']:
        supply=[case[k] for k in ['maximum_initial_usable_stock','maximum_imported_service','maximum_nonrenewal_exogenous_supply']]
        complete=all(v is not None for v in supply)
        bound=max(0,case['minimum_cumulative_demand']-sum(supply)) if complete else 0
        check('inverse bound '+case['case'],case['additional_renewal_lower_bound']==bound and case['finite_supply_bounds_available']==complete and not case['mechanism_identified'])
        inverse.append({'case':case['case'],'bound':bound})
    sensitivities=[]
    for variant,severity,after_age in [('shock_severity_two',2,False),('eligibility_after_skill_age',1,True)]:
        rows=[]
        for w in root['worlds']:
            b,age,support=w['budget'],w['skill_age'],w['shock_support']
            for mode in ['possible','robust']:
                rebuilt=reconstruction(b,age,support,mode,severity,after_age)
                baseline={tuple(v) for v in w[mode]['infinite_kernel']}
                rows.append({'budget':b,'skill_age':age,'shock_support':support,'mode':mode,
                             'infinite_count':len(rebuilt['kernel']),'infinite_kernel':sorted(rebuilt['kernel']),
                             'primary_infinite':PRIMARY in rebuilt['kernel'],'primary_max_safe':rebuilt['max_safe'],
                             'removed_from_baseline':sorted(baseline-rebuilt['kernel']),'added_to_baseline':sorted(rebuilt['kernel']-baseline)})
        sensitivities.append({'variant':variant,'scope':'Declared reviewer law change, not a defect in the baseline implementation','world_modes':rows})
    args.output.mkdir(parents=True)
    out={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Independent exact finite model reconstruction and invented law sensitivities; no historical calibration',
         'root_results_sha256':digest(result_path),'review_protocol_sha256':digest(HERE/'CHECKER-PROTOCOL.md'),
         'checker_sha256':digest(Path(__file__)),'checks_passed':len(checks),'checks':checks,
         'reconstruction':reconstructed,'dependency_cases':dependency,'inverse_bound_controls':inverse,'sensitivities':sensitivities}
    (args.output/'checks.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checks_passed':len(checks),'worlds':len(reconstructed),'sensitivities':len(sensitivities)}))

if __name__=='__main__':main()
