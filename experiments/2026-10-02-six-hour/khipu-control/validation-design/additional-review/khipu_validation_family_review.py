"""Additional independent review of random-subset ambiguous-set metrics."""
from collections import defaultdict
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path
from khipu_validation_verify import BASE,RUN,SOURCE,scalar,minor_rank,reduce_equalities,expected_classification,ray_answer


def classify(fitted,model,aggregate,kind,equations,unit):
    common=list(equations);halfspace=None
    if unit is not None:common.append([1,0,0,unit])
    if model=='collective':
        if kind=='equality':common.append(aggregate+[0])
        else:halfspace=aggregate
    pieces=[];points=set();families=[];ratios=set();relative_possible=True
    originals=[('point',p) for p in fitted['optimal_points']]+[('family',f) for f in fitted['optimal_families']]
    for category,original in originals:
        restrictions=list(common)
        if category=='point':
            _,t,h=map(Q,original['values']);restrictions.extend([[-t,1,0,0],[-h,0,1,0]])
        elif 'line' in original:restrictions.append(original['line']+[0])
        status,dimension=expected_classification(restrictions,halfspace)
        if status=='empty':continue
        origin,directions=reduce_equalities(restrictions)
        if not directions:
            point=tuple(origin);points.add(point);ratios.add(tuple(x/point[0] for x in point))
        else:
            families.append(dimension)
            if dimension!=1 or minor_rank([origin,directions[0]])!=1:
                relative_possible=False
            else:
                direction=directions[0];ratios.add(tuple(x/direction[0] for x in direction))
        pieces.append(dimension)
    status='empty' if not pieces else 'point' if len(points)==1 and not families else 'ambiguous'
    relative=next(iter(ratios)) if relative_possible and len(ratios)==1 else None
    return status,max(pieces,default=None),points,relative,len(originals)


def main():
    folder=BASE/'additional-review';folder.mkdir(exist_ok=False)
    worlds={x['world_id']:x for x in map(json.loads,(RUN/'selector-inputs.jsonl').read_text(encoding='utf-8').splitlines())}
    targets={x['world_id']:x for x in map(json.loads,(RUN/'targets.jsonl').read_text(encoding='utf-8').splitlines())}
    finals={}
    with (SOURCE/'inferences.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            x=json.loads(line)
            if x['prefix']==8:finals[x['world_id']]=x
    subsets=json.loads((RUN/'random-subsets.json').read_text(encoding='utf-8'))
    checked=0;parts=0;wrong_witnesses=0;ambiguous_world_records=0
    with (RUN/'random-world-scores.jsonl').open(encoding='utf-8') as stream,(folder/'wrong-compatible-random-witnesses.jsonl').open('x',encoding='utf-8') as wrong:
        for line in stream:
            record=json.loads(line);identifier=record['world_id'];inferred=finals[identifier];world=worlds[identifier];key=targets[identifier];view=record['view'];budget=record['budget'];unit=inferred['scale_observations']['counted']['count'] if view=='counted' else None;denominator=comb(11,budget);truth=tuple(map(Q,key['true_absolute_values']));checks=world['checks'];cache={}
            for model in ('baseline','collective'):
                fitted=inferred[model];relevant=[p for p in inferred['policies'] if p.startswith(model+'_')]
                accepted=[p for p in relevant if inferred['policies'][p]['status']=='accepted_unique_ray']
                if accepted:
                    vector=inferred['policies'][accepted[0]]['normalized_values'];correct=tuple(map(Q,vector))==tuple(x/truth[0] for x in truth)
                    if not correct:
                        for selected in subsets[str(budget)]:
                            status,point=ray_answer(vector,checks,key['rhs'],selected,unit)
                            if status!='empty':
                                wrong.write(json.dumps({'world_id':identifier,'view':view,'budget':budget,'selected_indices':selected,'original_policy_ids':accepted,'normalized_values':vector,'absolute_point':point,'remaining_scale':'all positive multiples' if status=='family' else 'fixed by the available/selected observation','selection_probability':f'1/{denominator}','scope':'Compatible wrong candidate in exact uniform-random validation'},separators=(',',':'))+'\n');wrong_witnesses+=1
                ambiguities=[p for p in relevant if inferred['policies'][p]['status']=='abstained_ambiguity']
                if not ambiguities:continue
                totals=defaultdict(int)
                for selected in subsets[str(budget)]:
                    equations=[checks[i]['row']+[key['rhs'][i]] for i in selected]
                    status,dimension,points,relative,partcount=classify(fitted,model,inferred['aggregate'],inferred['kind'],equations,unit);parts+=partcount;checked+=1
                    if status=='empty':totals['validation_rejected']+=1
                    elif status=='point':totals['one_correct_absolute' if next(iter(points))==truth else 'one_wrong_absolute']+=1
                    else:totals['surviving_ambiguous']+=1;totals[f'surviving_dimension_{dimension}']+=1
                    if relative is not None:totals['one_correct_relative_ray' if relative==tuple(x/truth[0] for x in truth) else 'one_wrong_relative_ray']+=1
                for policy in ambiguities:
                    saved=record['policy_expected_metrics'][policy]
                    names={'validation_rejected','one_correct_absolute','one_wrong_absolute','surviving_ambiguous','surviving_dimension_1','surviving_dimension_2','surviving_dimension_3','one_correct_relative_ray','one_wrong_relative_ray'}
                    for name in names:assert Q(saved.get(name,0))==Q(totals[name],denominator),(identifier,view,budget,policy,name,saved,totals)
                    ambiguous_world_records+=1
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'passed':True,'scope':'Independent random-subset classification of original gate-passing ambiguous optima, extending main verification','ambiguous_model_subset_intersections':checked,'original_optimum_parts_checked':parts,'random_ambiguous_policy_world_records':ambiguous_world_records,'wrong_compatible_random_witnesses_preserved':wrong_witnesses,'geometry_uses_independent_rref_and_inequality_elimination':True,'main_outputs_unchanged':True,'aggregate_sha256':hashlib.sha256((RUN/'aggregate.json').read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (folder/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
