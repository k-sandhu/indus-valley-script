"""Independent exact certificates for the recorded-interval grouping endpoint."""
from __future__ import annotations
import argparse
import ast
import collections
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import shutil
import sqlite3

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/2026-10-02-six-hour/khipu-control'
RAW=ROOT/'data/six-hour/khipu/puruchuco-2026-10-02'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,obj):
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

def verify():
    endpoint=OUT/'endpoints/intervals-v1'
    inputs=json.loads((RAW/'interval-component-input.json').read_text(encoding='utf-8'))
    keys={x['id']:x for x in json.loads((RAW/'interval-evaluator-key.json').read_text(encoding='utf-8'))['cases']}
    by_id={x['id']:x for x in inputs['cases']}
    db=sqlite3.connect(RAW/'khipu.db');db.row_factory=sqlite3.Row
    for case in inputs['cases']:
        assert 'reference_boundaries' not in case
        assert all('TOTAL_VALUE' not in x and 'knot_value_type' not in x for x in case['clusters'])
        for source in case['clusters']:
            row=db.execute('select * from cord_cluster where CLUSTER_ID=?',(source['CLUSTER_ID'],)).fetchone()
            assert source['BEG_INV_CORD']==row['BEG_INV_CORD'] and source['END_INV_CORD']==row['END_INV_CORD']
            assert Fraction(source['START_POSITION'])==Fraction(str(row['START_POSITION']))
            assert Fraction(source['END_POSITION'])==Fraction(str(row['END_POSITION']))
        computed=[]
        for i in range(len(case['clusters'])-1):
            next_start=Fraction(case['clusters'][i+1]['START_POSITION'])
            previous_end=Fraction(case['clusters'][i]['END_POSITION'])
            computed.append(next_start-previous_end)
        assert computed==list(map(Fraction,case['gaps']))
    counts=collections.Counter();positive=0;negative=0;perm_counts=collections.Counter();perm_sets=collections.defaultdict(set)
    original_cuts={};score_lines=(RAW/'interval-scores.jsonl').open(encoding='utf-8')
    summaries=collections.defaultdict(collections.Counter)
    with (RAW/'interval-inferences.jsonl').open(encoding='utf-8') as f:
        for line in f:
            record=json.loads(line);case=by_id[record['case_id']];inferred=record['inferred']
            bounds=[(Fraction(a),None if b is None else Fraction(b)) for a,b in record['bounds']]
            accepted=inferred['admissible'];excluded=inferred['excluded'];groups=case['group_count_prior']
            cuts=set()
            for candidate in accepted:
                subset=tuple(candidate['cuts']);assert subset not in cuts;cuts.add(subset)
                assert len(subset)==groups-1 and len(set(subset))==len(subset)
                witness=list(map(Fraction,candidate['ranking_witness']))
                assert len(witness)==len(bounds)
                for value,(low,high) in zip(witness,bounds):
                    assert value>=low and (high is None or value<=high)
                not_selected=set(range(len(bounds)))-set(subset)
                for selected in subset:
                    for unselected in not_selected:
                        assert witness[selected]>=witness[unselected]
                positive+=1
            for certificate in excluded:
                subset=tuple(certificate['cuts']);assert subset not in cuts;cuts.add(subset)
                i=certificate['selected_boundary'];j=certificate['unselected_boundary']
                assert i in subset and j not in subset
                assert bounds[i][1] is not None
                assert bounds[i][1]==Fraction(certificate['selected_upper'])
                assert bounds[j][0]==Fraction(certificate['unselected_lower'])
                assert bounds[i][1]<bounds[j][0]
                negative+=1
            expected=set(itertools.combinations(range(len(bounds)),groups-1))
            assert cuts==expected and len(cuts)==math.comb(len(bounds),groups-1)
            assert len(accepted)==inferred['admissible_count']
            accepted_cuts=[x['cuts'] for x in accepted]
            reference=[case['eligible_boundaries'].index(x) for x in keys[case['id']]['reference_boundaries']]
            if record['condition']=='reverse_orientation':
                reference=sorted(len(bounds)-1-x for x in reference)
            correct=reference in accepted_cuts
            score=json.loads(next(score_lines));evaluation=score['evaluation']
            assert score['case_id']==case['id'] and score['condition']==record['condition'] and score['replicate']==record['replicate']
            assert evaluation['reference_survives']==correct
            assert evaluation['unique_correct']==(correct and len(accepted)==1)
            assert evaluation['admissible_count']==len(accepted)
            group=summaries[(case['id'],record['condition'])]
            group['records']+=1;group['reference_survives']+=int(correct);group['unique_correct']+=int(correct and len(accepted)==1)
            group['admissible_count_'+str(len(accepted))]+=1
            counts[record['condition']]+=1
            if record['condition']=='recorded_point':
                original_cuts[case['id']]=accepted_cuts
                # Independently form every distinct-level threshold and maximize its ratio.
                values=sorted(set(Fraction(x) for x in case['gaps']))
                ratios={ (a,b):b/a for a,b in zip(values,values[1:])}
                maximum=max(ratios.values())
                expected_thresholds=[(a,b) for (a,b),ratio in ratios.items() if ratio==maximum]
                given=record['count_free']['candidates']
                assert {tuple(map(Fraction,x['threshold_interval'])) for x in given}==set(expected_thresholds)
                for candidate in given:
                    high=Fraction(candidate['threshold_interval'][1])
                    assert candidate['cuts']==[i for i,value in enumerate(map(Fraction,case['gaps'])) if value>=high]
            if record['condition'] in ('translate_intervals','scale_intervals'):
                assert accepted_cuts==original_cuts[case['id']]
            if record['condition']=='reverse_orientation':
                mirrored=[sorted(len(bounds)-1-x for x in cut) for cut in original_cuts[case['id']]]
                assert accepted_cuts==mirrored
            if record['condition']=='gap_multiset_permutation':
                perm_counts[case['id']]+=1
                permutation=tuple(a for a,b in bounds)
                assert collections.Counter(permutation)==collections.Counter(map(Fraction,case['gaps']))
                assert permutation not in perm_sets[case['id']];perm_sets[case['id']].add(permutation)
    assert next(score_lines,None) is None
    aggregate=json.loads((endpoint/'aggregate.json').read_text(encoding='utf-8'))
    for row in aggregate['summaries']:
        assert dict(summaries[(row['case_id'],row['condition'])])=={k:v for k,v in row.items() if k not in ('case_id','condition')}
    for case in inputs['cases']:
        multiplicities=collections.Counter(case['gaps']).values()
        number=math.factorial(len(case['gaps']))//math.prod(math.factorial(x) for x in multiplicities)
        assert perm_counts[case['id']]==number
        loss=next(x for x in aggregate['information_loss'] if x['case_id']==case['id'])
        assert loss['known_count_order_only_partitions']==math.comb(len(case['gaps']),case['group_count_prior']-1)
        assert loss['unknown_count_order_only_partitions']==sum(math.comb(len(case['gaps']),k) for k in range(len(case['gaps'])+1))
        sizes=[x['NUM_CORDS'] for x in case['clusters']];ideal=Fraction(sum(sizes),case['group_count_prior'])
        errors={}
        for cut in itertools.combinations(range(len(sizes)-1),case['group_count_prior']-1):
            chunk_sizes=[];begin=0
            for end in list(cut)+[len(sizes)-1]:
                chunk_sizes.append(sum(sizes[begin:end+1]));begin=end+1
            errors[cut]=sum(abs(Fraction(x)-ideal) for x in chunk_sizes)
        best=min(errors.values());optimal={cut for cut,value in errors.items() if value==best}
        ref=tuple(case['eligible_boundaries'].index(x) for x in keys[case['id']]['reference_boundaries'])
        assert best==Fraction(loss['equal_cord_count_minimum_deviation'])
        assert len(optimal)==loss['equal_cord_count_candidates']
        assert (ref in optimal)==loss['equal_cord_count_reference_survives']
    tree=ast.parse((ROOT/'src/six_hour/khipu_intervals.py').read_text(encoding='utf-8'))
    selected=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('infer_partitions','count_free','cases_for_input','balanced_partitions')]
    for function in selected:
        for node in ast.walk(function):
            if isinstance(node,ast.Name):assert node.id not in ('keys','reference','SPECS')
            if isinstance(node,ast.Attribute):assert node.attr not in ('read_text','read_bytes','open')
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'passed':True,'records_checked':sum(counts.values()),
            'condition_counts':dict(counts),'exact_ranking_witnesses_checked':positive,'exact_exclusion_certificates_checked':negative,
            'permutation_counts':dict(perm_counts),'permutation_count_method':'factorial divided by value multiplicity factorials',
            'all_cut_sets_covered':True,'source_interval_reconstruction':True,'orientation_origin_scale_invariance':True,
            'equal_cord_count_baseline_independently_checked':True,'count_free_estimator_independently_checked':True,
            'tested_functions_have_no_quantity_or_reference_access':True,'input_sha256':sha(RAW/'interval-component-input.json'),
            'inferences_sha256':sha(RAW/'interval-inferences.jsonl'),'scores_sha256':sha(RAW/'interval-scores.jsonl')}
    save(endpoint/'verification.json',report)
    print(json.dumps(report,indent=2))

def freeze():
    endpoint=OUT/'endpoints/intervals-v1'
    assert (endpoint/'verification.json').exists()
    for name in ('khipu_intervals.py','khipu_intervals_verify.py'):
        original=ROOT/'src/six_hour'/name;target=endpoint/name
        if target.exists():assert sha(target)==sha(original)
        else:shutil.copyfile(original,target)
    paths=sorted(x for x in endpoint.rglob('*') if x.is_file())
    records=[{'path':x.relative_to(endpoint).as_posix(),'bytes':x.stat().st_size,'sha256':sha(x)} for x in paths]
    save(endpoint/'freeze-manifest.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'files':records,
         'files_count':len(records),'total_bytes':sum(x['bytes'] for x in records),'protocol_snapshot_links':'original khipu-control directory context'})
    print('Frozen '+str(len(records))+' files; '+str(sum(x['bytes'] for x in records))+' bytes.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','freeze']);a=p.parse_args()
    (verify if a.command=='verify' else freeze)()
