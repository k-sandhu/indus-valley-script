"""Evaluate sealed row choices on unchanged KHI-04 candidate sets."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
import json
from pathlib import Path
from khipu_validation import BASE,RUN,SOURCE,VIEWS,BUDGETS,POLICIES,rank,digest,save
from khipu_validation_geometry import validated_set,dot

FITTER_POLICIES=("baseline_three_quarter","baseline_half","collective_three_quarter","collective_half")


def ray_intersection(values,equations,unit_count):
    vector=list(map(F,values)); scale=F(unit_count) if unit_count is not None else None
    for row in equations:
        predicted=dot(row[:3],vector); target=F(row[3])
        if not predicted:
            if target:
                return {"status":"empty","points":[],"families":[],"surviving_dimension":None}
        else:
            proposed=target/predicted
            if proposed<=0 or scale is not None and proposed!=scale:
                return {"status":"empty","points":[],"families":[],"surviving_dimension":None}
            scale=proposed
    if scale is None:
        family={"status":"family","dimension":1,"base":["0","0","0"],"slopes":[[str(x) for x in vector]],"witness":[str(x) for x in vector]}
        return {"status":"ambiguous","points":[],"families":[family],"surviving_dimension":1}
    return {"status":"one_absolute_point","points":[[str(scale*x) for x in vector]],"families":[],"surviving_dimension":0}


def filter_model(inferred,model,equations,unit_count):
    fitted=inferred[model]
    if fitted['status']=='unique_positive':
        return ray_intersection(fitted['optimal_points'][0]['values'],equations,unit_count)
    return validated_set(fitted,model,inferred['aggregate'],inferred['kind'],equations,unit_count)


def relative_identification(survivor):
    ratios={tuple(str(F(x)/F(point[0])) for x in point) for point in survivor['points']}
    for family in survivor['families']:
        if family['dimension']!=1:
            return None
        base=list(map(F,family['base'])); slope=list(map(F,family['slopes'][0]))
        if rank([base,slope])>1:
            return None
        point=family['witness'];ratios.add(tuple(str(F(x)/F(point[0])) for x in point))
    return next(iter(ratios)) if len(ratios)==1 else None


def metrics(decision,survivor,truth):
    out={'records':1}
    if decision['status'].startswith('rejected'):
        return out|{'gate_rejected':1}
    is_empty=survivor['status']=='empty'
    if decision['status']=='accepted_unique_ray':
        correct=tuple(map(F,decision['normalized_values']))==tuple(F(x)/F(truth[0]) for x in truth)
        out['original_correct_preserved' if correct and not is_empty else 'original_correct_rejected' if correct else 'original_wrong_rejected' if is_empty else 'original_wrong_compatible']=1
        out['original_correct' if correct else 'original_wrong']=1
    else:
        out['original_ambiguous']=1
    if is_empty:
        out['validation_rejected']=1
    elif survivor['status']=='one_absolute_point':
        correct=tuple(map(F,survivor['points'][0]))==tuple(map(F,truth))
        out['one_correct_absolute' if correct else 'one_wrong_absolute']=1
    else:
        out['surviving_ambiguous']=1
        out[f"surviving_dimension_{survivor['surviving_dimension']}"]=1
    relative=relative_identification(survivor)
    if relative is not None:
        correct=tuple(map(F,relative))==tuple(F(x)/F(truth[0]) for x in truth)
        out['one_correct_relative_ray' if correct else 'one_wrong_relative_ray']=1
    return out


def main():
    manifest=json.loads((RUN/'selection-manifest.json').read_text(encoding='utf-8'))
    assert digest(RUN/'selections.jsonl')==manifest['selections_sha256']
    inputs={x['world_id']:x for x in map(json.loads,(RUN/'selector-inputs.jsonl').read_text(encoding='utf-8').splitlines())}
    targets={x['world_id']:x for x in map(json.loads,(RUN/'targets.jsonl').read_text(encoding='utf-8').splitlines())}
    choices={(x['world_id'],x['view'],x['budget']):x for x in map(json.loads,(RUN/'selections.jsonl').read_text(encoding='utf-8').splitlines())}
    subsets=json.loads((RUN/'random-subsets.json').read_text(encoding='utf-8'))
    aggregate=defaultdict(lambda:defaultdict(F)); detailed=0; random_records=0; intersections=0;examples=[]
    with (SOURCE/'inferences.jsonl').open(encoding='utf-8') as stream,(RUN/'evaluated.jsonl').open('x',encoding='utf-8') as output,(RUN/'random-world-scores.jsonl').open('x',encoding='utf-8') as random_out:
        for line in stream:
            inferred=json.loads(line)
            if inferred['prefix']!=8:continue
            identifier=inferred['world_id'];condition=identifier.split('-',1)[1]
            projected=inputs[identifier]; target=targets[identifier]; checks=projected['checks']
            for view in VIEWS:
                unit=inferred['scale_observations']['counted']['count'] if view=='counted' else None
                cache={}
                def run_subset(indices):
                    nonlocal intersections
                    key=tuple(sorted(indices))
                    if key not in cache:
                        equations=[checks[i]['row']+[target['rhs'][i]] for i in key]
                        survivors={}
                        for model in ('baseline','collective'):
                            relevant=[p for p in FITTER_POLICIES if p.startswith(model)]
                            if any(not inferred['policies'][p]['status'].startswith('rejected') for p in relevant):
                                survivors[model]=filter_model(inferred,model,equations,unit);intersections+=1
                            else:
                                survivors[model]={'status':'gate_rejected','points':[],'families':[],'surviving_dimension':None}
                        rank_value=rank(projected['anchor_rows'][view]+[checks[i]['row'] for i in key])
                        results={p:metrics(inferred['policies'][p],survivors[p.split('_',1)[0]],target['true_absolute_values']) for p in FITTER_POLICIES}
                        cache[key]=(rank_value,survivors,results)
                    return cache[key]
                for budget in BUDGETS:
                    sealed=choices[(identifier,view,budget)]
                    for policy in POLICIES:
                        selected=sealed['policies'][policy]; rank_value,survivors,results=run_subset(selected['indices'])
                        assert rank_value==selected['rank']
                        output.write(json.dumps({'world_id':identifier,'view':view,'budget':budget,'selection_policy':policy,'selected_indices':selected['indices'],'selected_ids':selected['ids'],'rank':rank_value,'validated_models':survivors,'policy_metrics':results},separators=(',',':'))+'\n');detailed+=1
                        for p,values in results.items():
                            bucket=aggregate[(condition,view,policy,budget,p)]
                            for k,v in values.items():bucket[k]+=v
                            bucket['rank_sum']+=rank_value;bucket[f'rank_{rank_value}']+=1
                        if identifier=='20261020124-four_swapped':
                            examples.append({'view':view,'budget':budget,'selection_policy':policy,'selected_ids':selected['ids'],'rank':rank_value,'validated_models':survivors,'policy_metrics':results})
                    random_totals=defaultdict(lambda:defaultdict(F));denominator=len(subsets[str(budget)])
                    for indices in subsets[str(budget)]:
                        rank_value,_,results=run_subset(indices)
                        for p,values in results.items():
                            for k,v in values.items():random_totals[p][k]+=F(v,denominator)
                            random_totals[p]['rank_sum']+=F(rank_value,denominator);random_totals[p][f'rank_{rank_value}']+=F(1,denominator)
                    random_out.write(json.dumps({'world_id':identifier,'view':view,'budget':budget,'subsets':denominator,'policy_expected_metrics':{p:{k:str(v) for k,v in values.items()} for p,values in random_totals.items()}},separators=(',',':'))+'\n');random_records+=1
                    for p,values in random_totals.items():
                        bucket=aggregate[(condition,view,'uniform_random',budget,p)]
                        for k,v in values.items():bucket[k]+=v
    rows=[{'condition':c,'view':v,'selection_policy':s,'budget':b,'fitter_policy':p,'metrics':{k:str(value) for k,value in values.items()}} for (c,v,s,b,p),values in sorted(aggregate.items())]
    save(RUN/'aggregate.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Post-outcome validation allocation on frozen KHI-04; exact random-subset expected counts','worlds':1400,'independent_base_seeds':200,'deterministic_records':detailed,'random_world_records':random_records,'unique_model_intersections':intersections,'rows':rows,'input_pins':manifest,'code_sha256':digest(Path(__file__))})
    save(RUN/'rank-one-failure-trajectories.json',{'world_id':'20261020124-four_swapped','scope':'Previously seen witness; trajectories of fixed policies','rows':examples})
    print(json.dumps({'deterministic_records':detailed,'random_world_records':random_records,'intersections':intersections,'aggregate_rows':len(rows)}))


if __name__=='__main__':main()
