"""Independent rank, residual, random-expectation and family checks."""
from __future__ import annotations
import ast
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import itertools
import json
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'experiments/2026-10-02-six-hour/khipu-control/validation-design'
RUN=BASE/'main-v1';SOURCE=BASE.parent/'conservation-check/main-v1'


def scalar(row,vector):return sum(Q(x)*Q(y) for x,y in zip(row,vector))


def minor_rank(rows):
    for size in (3,2,1):
        for picked in itertools.combinations(rows,size):
            for cols in itertools.combinations(range(3),size):
                value=Q(0)
                for perm in itertools.permutations(range(size)):
                    sign=(-1)**sum(perm[i]>perm[j] for i in range(size) for j in range(i+1,size))
                    term=Q(sign)
                    for i in range(size):term*=Q(picked[i][cols[perm[i]]])
                    value+=term
                if value:return size
    return 0


def reduce_equalities(equations):
    rows=[list(map(Q,row)) for row in equations];pivot_cols=[]
    for col in range(3):
        position=next((i for i in range(len(pivot_cols),len(rows)) if rows[i][col]),None)
        if position is None:continue
        k=len(pivot_cols);rows[k],rows[position]=rows[position],rows[k]
        divisor=rows[k][col];rows[k]=[x/divisor for x in rows[k]]
        for i in range(len(rows)):
            if i!=k:
                factor=rows[i][col];rows[i]=[a-factor*b for a,b in zip(rows[i],rows[k])]
        pivot_cols.append(col)
    if any(not any(row[:3]) and row[3] for row in rows):return None
    free=[j for j in range(3) if j not in pivot_cols];origin=[Q(0)]*3
    directions=[]
    for i,j in enumerate(pivot_cols):origin[j]=rows[i][3]
    for j in free:
        direction=[Q(int(i==j)) for i in range(3)]
        for i,c in enumerate(pivot_cols):direction[c]=-rows[i][j]
        directions.append(direction)
    return origin,directions


def inequalities_feasible(rows,dimension):
    """Independent elimination of >= bounds with strictness propagation."""
    for variable in range(dimension-1,-1,-1):
        up=[];down=[];unchanged=[]
        for coefficients,bound,strict in rows:
            multiplier=coefficients[variable]
            trimmed=coefficients[:variable]+coefficients[variable+1:]
            if multiplier>0:up.append((trimmed,bound,strict,multiplier))
            elif multiplier<0:down.append((trimmed,bound,strict,multiplier))
            else:unchanged.append((trimmed,bound,strict))
        for a,b,s,m in up:
            for c,d,t,n in down:
                unchanged.append(([x/m-y/n for x,y in zip(a,c)],b/m-d/n,s or t))
        rows=unchanged
    return all(Q(0)>bound if strict else Q(0)>=bound for _,bound,strict in rows)


def expected_classification(equations,halfspace):
    space=reduce_equalities(equations)
    if space is None:return 'empty',None
    origin,directions=space
    inequalities=[([direction[j] for direction in directions],-origin[j],True) for j in range(3)]
    if halfspace is not None:inequalities.append(([scalar(halfspace,d) for d in directions],-scalar(halfspace,origin),False))
    if not inequalities_feasible(inequalities,len(directions)):return 'empty',None
    return ('family' if directions else 'point'),len(directions)


def ray_answer(values,checks,rhs,selected,unit):
    vector=list(map(Q,values));scales=[]
    if unit is not None:scales.append(Q(unit))
    for i in selected:
        predicted=scalar(checks[i]['row'],vector);target=Q(rhs[i])
        if predicted==0:
            if target!=0:return 'empty',None
        else:scales.append(target/predicted)
    if any(x<=0 for x in scales) or len(set(scales))>1:return 'empty',None
    return ('point',[str(scales[0]*x) for x in vector]) if scales else ('family',None)


def choose(n,k):return comb(n,k) if n>=k>=0 else 0


def random_ray_counts(values,checks,rhs,budget,unit):
    vector=list(map(Q,values));universal=0;groups=defaultdict(int)
    if unit is not None:
        good=sum(scalar(check['row'],[Q(unit)*x for x in vector])==Q(target) for check,target in zip(checks,rhs))
        return choose(good,budget),choose(good,budget)
    for check,target in zip(checks,rhs):
        predicted=scalar(check['row'],vector)
        if not predicted:
            universal+=int(target==0)
        elif Q(target)/predicted>0:
            groups[Q(target)/predicted]+=1
    free=choose(universal,budget)
    scaled=sum(choose(universal+size,budget)-free for size in groups.values())
    return free+scaled,scaled


def main():
    inputs={x['world_id']:x for x in map(json.loads,(RUN/'selector-inputs.jsonl').read_text(encoding='utf-8').splitlines())}
    targets={x['world_id']:x for x in map(json.loads,(RUN/'targets.jsonl').read_text(encoding='utf-8').splitlines())}
    final={}
    with (SOURCE/'inferences.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            x=json.loads(line)
            if x['prefix']==8:final[x['world_id']]=x
    assert len(inputs)==len(targets)==len(final)==1400
    with (SOURCE/'evaluator-key.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            source=json.loads(line);identifier=source['id'];key=source['key']
            assert [c['row'] for c in inputs[identifier]['checks']]==key['heldout_equations']+key['count_features']
            assert targets[identifier]['rhs']==[0]*8+key['count_values']
            assert targets[identifier]['true_absolute_values']==key['true_weights']
            assert set(inputs[identifier])=={'world_id','checks','anchor_rows'}
            assert all(set(c)=={'id','kind','row'} for c in inputs[identifier]['checks'])
    random_subsets=json.loads((RUN/'random-subsets.json').read_text(encoding='utf-8'))
    assert all(random_subsets[str(k)]==[list(s) for s in itertools.combinations(range(11),k)] for k in range(4))
    rank_cache={};selection_records=0;greedy_steps=0
    with (RUN/'selections.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            record=json.loads(line);world=inputs[record['world_id']];checks=world['checks'];budget=record['budget'];anchor=world['anchor_rows'][record['view']]
            for policy,selected in record['policies'].items():
                order=list(range(11)) if policy!='count_first' else list(range(8,11))+list(range(8))
                if policy=='greedy_rank':
                    taken=[]
                    for step in range(budget):
                        prior=anchor+[checks[i]['row'] for i in taken];prior_rank=minor_rank(prior)
                        gains={i:minor_rank(prior+[checks[i]['row']])-prior_rank for i in range(11) if i not in taken}
                        chosen=min(i for i,gain in gains.items() if gain==max(gains.values()));taken.append(chosen);greedy_steps+=1
                    order=taken
                assert selected['indices']==order[:budget]
                assert selected['rank']==minor_rank(anchor+[checks[i]['row'] for i in selected['indices']])
            selection_records+=1
    deterministic=0;residuals=0;family_parts=0;metrics_total=defaultdict(lambda:defaultdict(Q));rankone=[]
    with (RUN/'evaluated.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            record=json.loads(line);identifier=record['world_id'];view=record['view'];budget=record['budget'];policy=record['selection_policy'];world=inputs[identifier];key=targets[identifier];inferred=final[identifier];selected=record['selected_indices'];checks=world['checks'];unit=inferred['scale_observations']['counted']['count'] if view=='counted' else None
            equations=[checks[i]['row']+[key['rhs'][i]] for i in selected]
            assert record['rank']==minor_rank(world['anchor_rows'][view]+[checks[i]['row'] for i in selected])
            for model,survivor in record['validated_models'].items():
                fitted=inferred[model]
                if survivor['status']=='gate_rejected':continue
                if fitted['status']=='unique_positive':
                    status,point=ray_answer(fitted['optimal_points'][0]['values'],checks,key['rhs'],selected,unit)
                    assert survivor['status']=={'empty':'empty','family':'ambiguous','point':'one_absolute_point'}[status]
                    if point is not None:assert survivor['points']==[point]
                    residuals+=len(selected)
                else:
                    originals=[('point',p) for p in fitted['optimal_points']]+[('family',f) for f in fitted['optimal_families']]
                    assert len(originals)==len(survivor['parts'])
                    for (kind,original),part in zip(originals,survivor['parts']):
                        restrictions=list(equations);halfspace=None
                        if unit is not None:restrictions.append([1,0,0,unit])
                        if model=='collective':
                            if inferred['kind']=='equality':restrictions.append(inferred['aggregate']+[0])
                            else:halfspace=inferred['aggregate']
                        if kind=='point':
                            _,t,h=map(Q,original['values']);restrictions.extend([[-t,1,0,0],[-h,0,1,0]])
                        elif 'line' in original:restrictions.append(original['line']+[0])
                        status,dimension=expected_classification(restrictions,halfspace)
                        assert part['status']==status,(identifier,record['view'],selected,part,status)
                        if status!='empty':
                            assert part['dimension']==dimension
                            witness=list(map(Q,part['witness']));assert all(x>0 for x in witness)
                            assert all(scalar(row[:3],witness)==Q(row[3]) for row in restrictions)
                            assert halfspace is None or scalar(halfspace,witness)>=0
                            origin=list(map(Q,part['base']));directions=[list(map(Q,s)) for s in part['slopes']]
                            assert all(scalar(row[:3],origin)==Q(row[3]) for row in restrictions)
                            assert all(scalar(row[:3],d)==0 for row in restrictions for d in directions)
                            residuals+=len(restrictions)*(2+len(directions))
                        family_parts+=1
            for fitter_policy,values in record['policy_metrics'].items():
                bucket=metrics_total[(identifier.split('-',1)[1],view,policy,budget,fitter_policy)]
                for name,value in values.items():bucket[name]+=value
                bucket['rank_sum']+=record['rank'];bucket[f"rank_{record['rank']}"]+=1
                decision=inferred['policies'][fitter_policy]
                if decision['status']=='accepted_unique_ray':
                    status,_=ray_answer(decision['normalized_values'],checks,key['rhs'],selected,unit)
                    truth=key['true_absolute_values'];correct=tuple(map(Q,decision['normalized_values']))==tuple(Q(x)/Q(truth[0]) for x in truth)
                    expected_name='original_correct_preserved' if correct and status!='empty' else 'original_correct_rejected' if correct else 'original_wrong_rejected' if status=='empty' else 'original_wrong_compatible'
                    assert values.get(expected_name)==1
            if identifier=='20261020124-four_swapped':rankone.append(record)
            deterministic+=1
    random_records=0;random_point_checks=0;random_rank_states=0
    with (RUN/'random-world-scores.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            record=json.loads(line);identifier=record['world_id'];world=inputs[identifier];key=targets[identifier];inferred=final[identifier];view=record['view'];budget=record['budget'];anchor=world['anchor_rows'][view];checks=world['checks'];denominator=comb(11,budget);assert record['subsets']==denominator
            cache_key=(tuple(tuple(c['row']) for c in checks),bool(anchor),budget)
            if cache_key not in rank_cache:
                counts=defaultdict(int)
                for selected in random_subsets[str(budget)]:
                    value=minor_rank(anchor+[checks[i]['row'] for i in selected]);counts[value]+=1;random_rank_states+=1
                rank_cache[cache_key]=counts
            counts=rank_cache[cache_key]
            for fitter_policy,values in record['policy_expected_metrics'].items():
                for value,number in counts.items():assert Q(values.get(f'rank_{value}',0))==Q(number,denominator)
                assert Q(values['rank_sum'])==sum(Q(value*number,denominator) for value,number in counts.items())
                decision=inferred['policies'][fitter_policy]
                if decision['status']=='accepted_unique_ray':
                    unit=inferred['scale_observations']['counted']['count'] if view=='counted' else None
                    passed,scaled=random_ray_counts(decision['normalized_values'],checks,key['rhs'],budget,unit)
                    truth=key['true_absolute_values'];correct=tuple(map(Q,decision['normalized_values']))==tuple(Q(x)/Q(truth[0]) for x in truth)
                    assert Q(values.get('original_correct_preserved' if correct else 'original_wrong_compatible',0))==Q(passed,denominator)
                    assert Q(values.get('original_correct_rejected' if correct else 'original_wrong_rejected',0))==1-Q(passed,denominator)
                    assert Q(values.get('one_correct_absolute' if correct else 'one_wrong_absolute',0))==Q(scaled,denominator)
                    random_point_checks+=1
                bucket=metrics_total[(identifier.split('-',1)[1],view,'uniform_random',budget,fitter_policy)]
                for name,value in values.items():bucket[name]+=Q(value)
            random_records+=1
    aggregate=json.loads((RUN/'aggregate.json').read_text(encoding='utf-8'))
    for row in aggregate['rows']:
        key=tuple(row[name] for name in ('condition','view','selection_policy','budget','fitter_policy'))
        assert {k:Q(v) for k,v in row['metrics'].items()}==dict(metrics_total[key])
    tree=ast.parse((ROOT/'src/six_hour/khipu_validation.py').read_text(encoding='utf-8'));function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='select')
    assert [x.arg for x in function.args.args]==['checks','anchor_rows','budget','policy']
    assert not any(isinstance(n,ast.Name) and n.id in {'targets','truth','SOURCE','RUN','inferred','key','open'} for n in ast.walk(function))
    manifest=json.loads((RUN/'selection-manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((RUN/'selections.jsonl').read_bytes()).hexdigest()==manifest['selections_sha256']
    for pin in json.loads((RUN/'source-pins.json').read_text(encoding='utf-8'))['sources']:
        assert hashlib.sha256((BASE/pin['source']).read_bytes()).hexdigest()==pin['sha256']
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'passed':True,'source_projection_worlds':1400,'sealed_selection_records':selection_records,'greedy_steps':greedy_steps,'deterministic_validation_records':deterministic,'family_parts_independently_classified':family_parts,'selected_residual_checks':residuals,'random_world_records':random_records,'random_subset_ranks_checked_with_reuse':random_rank_states,'analytic_random_ray_metric_checks':random_point_checks,'aggregate_rows_rebuilt':len(aggregate['rows']),'rank_one_deterministic_records':len(rankone),'selector_interface_has_no_targets_or_decoders':True,'selections_remain_sealed':True,'source_hashes_match':True,'random_family_metrics_scope':'Aggregates rebuilt from saved per-world expectations; independently classified families and witnesses cover deterministic selected sets','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    p=RUN/'verification.json'
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
