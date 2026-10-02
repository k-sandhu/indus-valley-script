"""Quantity-free grouping from recorded khipu cluster intervals."""
from __future__ import annotations
import argparse
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
OUT=ROOT/"experiments/2026-10-02-six-hour/khipu-control"
RAW=ROOT/"data/six-hour/khipu/puruchuco-2026-10-02"
SPECS=(("UR063",1,111,6,[20,38,56,76,96]),("UR068",14,73,3,[33,53]))
RADII=tuple(map(Fraction,("0","1/20","1/10","1/5","1/4","3/10","1/2","1")))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,obj):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")

def prepare():
    db=sqlite3.connect(RAW/"khipu.db");db.row_factory=sqlite3.Row
    inputs=[];keys=[]
    for name,start,end,groups,reference in SPECS:
        main=db.execute("select KHIPU_ID,OKR_NUM from khipu_main where INVESTIGATOR_NUM=?",(name,)).fetchone()
        clusters=[]
        for row in db.execute("select CLUSTER_ID,ORDINAL,BEG_INV_CORD,END_INV_CORD,START_POSITION,END_POSITION,SPACING,NUM_CORDS from cord_cluster where KHIPU_ID=? and CLUSTER_LEVEL=1 order by ORDINAL",(main['KHIPU_ID'],)):
            if row['BEG_INV_CORD']>=start and row['END_INV_CORD']<=end:
                item=dict(row)
                for field in ('START_POSITION','END_POSITION','SPACING'):
                    if item[field] is not None:
                        item[field]=str(Fraction(str(item[field])))
                clusters.append(item)
        assert clusters and clusters[0]['BEG_INV_CORD']==start and clusters[-1]['END_INV_CORD']==end
        assert all(a['END_INV_CORD']+1==b['BEG_INV_CORD'] for a,b in zip(clusters,clusters[1:]))
        for cluster in clusters:
            assert cluster['NUM_CORDS']==cluster['END_INV_CORD']-cluster['BEG_INV_CORD']+1
            assert cluster['START_POSITION'] is not None and cluster['END_POSITION'] is not None
            assert Fraction(cluster['START_POSITION'])<=Fraction(cluster['END_POSITION'])
        boundaries=[x['END_INV_CORD'] for x in clusters[:-1]]
        assert all(x in boundaries for x in reference)
        gaps=[Fraction(b['START_POSITION'])-Fraction(a['END_POSITION']) for a,b in zip(clusters,clusters[1:])]
        assert all(x>=0 for x in gaps)
        inputs.append({'id':name,'okr_id':main['OKR_NUM'],'range':[start,end],'group_count_prior':groups,
                       'clusters':clusters,'eligible_boundaries':boundaries,'gaps':list(map(str,gaps))})
        keys.append({'id':name,'reference_boundaries':reference,'reference_group_count':groups})
    save(RAW/'interval-component-input.json',{'database_sha256':sha(RAW/'khipu.db'),'cases':inputs})
    save(RAW/'interval-evaluator-key.json',{'cases':keys,'source':'KFG published source partitions; recorded in protocol before scoring'})
    save(OUT/'interval-input-manifest.json',{
        'created_utc':datetime.now(timezone.utc).isoformat(),'database_sha256':sha(RAW/'khipu.db'),
        'input_path':(RAW/'interval-component-input.json').relative_to(ROOT).as_posix(),'input_sha256':sha(RAW/'interval-component-input.json'),
        'key_path':(RAW/'interval-evaluator-key.json').relative_to(ROOT).as_posix(),'key_sha256':sha(RAW/'interval-evaluator-key.json'),
        'tested_input_fields':['stable cluster IDs','cord spans','start/end intervals','computed gaps','optional group count'],
        'quantity_fields_in_input':False,'reference_partitions_in_input':False,'redistribution':'local-only source derivatives'})
    print('Prepared quantity-free interval input and separate reference key.')

def infer_partitions(bounds,groups):
    """Enumerate every rank-compatible cut set using only observed intervals."""
    dimension=len(bounds)
    assert 1<=groups<=dimension+1
    parsed=[(Fraction(lo),None if hi is None else Fraction(hi)) for lo,hi in bounds]
    assert all(lo>=0 and (hi is None or lo<=hi) for lo,hi in parsed)
    accepted=[];rejected=[]
    for selected in itertools.combinations(range(dimension),groups-1):
        selected_set=set(selected);remaining=[i for i in range(dimension) if i not in selected_set]
        finite_uppers=[(parsed[i][1],i) for i in selected if parsed[i][1] is not None]
        minimum=min(finite_uppers) if finite_uppers else None
        maximum=max((parsed[i][0],i) for i in remaining) if remaining else None
        if minimum is not None and maximum is not None and minimum[0]<maximum[0]:
            rejected.append({'cuts':list(selected),'selected_boundary':minimum[1],'selected_upper':str(minimum[0]),
                             'unselected_boundary':maximum[1],'unselected_lower':str(maximum[0])})
            continue
        finite=[value for pair in parsed for value in pair if value is not None]
        infinite_replacement=max(finite,default=Fraction(0))+1
        witness=[(hi if hi is not None else infinite_replacement) if i in selected_set else lo for i,(lo,hi) in enumerate(parsed)]
        assert all(witness[i]>=witness[j] for i in selected for j in remaining)
        accepted.append({'cuts':list(selected),'ranking_witness':list(map(str,witness))})
    return {'admissible':accepted,'excluded':rejected,'admissible_count':len(accepted),
            'all_cut_sets_count':math.comb(dimension,groups-1),'groups_prior':groups}

def count_free(point_gaps):
    gaps=list(map(Fraction,point_gaps))
    distinct=sorted(set(gaps))
    if len(distinct)<2 or any(x<=0 for x in gaps):
        return {'status':'abstain','reason':'no_distinct_positive_gap_levels','possible_counts':[1,len(gaps)+1]}
    ratios=[high/low for low,high in zip(distinct,distinct[1:])]
    largest=max(ratios)
    candidates=[]
    for index,ratio in enumerate(ratios):
        if ratio==largest:
            low,high=distinct[index:index+2]
            cuts=[i for i,gap in enumerate(gaps) if gap>=high]
            candidates.append({'cuts':cuts,'group_count':len(cuts)+1,'threshold_interval':[str(low),str(high)],'ratio':str(ratio)})
    return {'status':'unique' if len(candidates)==1 else 'ambiguous_threshold','candidates':candidates}

def distinct_permutations(items):
    counts=collections.Counter(items);keys=sorted(counts);size=len(items)
    def walk(prefix):
        if len(prefix)==size:
            yield list(prefix);return
        for key in keys:
            if counts[key]:
                counts[key]-=1;prefix.append(key)
                yield from walk(prefix)
                prefix.pop();counts[key]+=1
    yield from walk([])

def balanced_partitions(case):
    clusters=case['clusters'];groups=case['group_count_prior']
    ideal=Fraction(sum(x['NUM_CORDS'] for x in clusters),groups)
    choices=[];best=None
    for cuts in itertools.combinations(range(len(clusters)-1),groups-1):
        ends=list(cuts)+[len(clusters)-1];start=0;lengths=[]
        for end in ends:
            lengths.append(sum(x['NUM_CORDS'] for x in clusters[start:end+1]));start=end+1
        error=sum(abs(Fraction(x)-ideal) for x in lengths)
        if best is None or error<best:
            choices=[];best=error
        if error==best:
            choices.append({'cuts':list(cuts),'group_sizes':lengths})
    return {'minimum_absolute_size_deviation':str(best),'ideal_group_size':str(ideal),'candidates':choices}

def cases_for_input(case):
    gaps=list(map(Fraction,case['gaps']));groups=case['group_count_prior']
    point=lambda values:[[str(x),str(x)] for x in values]
    yield {'condition':'recorded_point','replicate':0,'bounds':point(gaps),'inferred':infer_partitions(point(gaps),groups),'count_free':count_free(gaps)}
    for index,permutation in enumerate(distinct_permutations(gaps)):
        bounds=point(permutation)
        yield {'condition':'gap_multiset_permutation','replicate':index,'bounds':bounds,'inferred':infer_partitions(bounds,groups)}
    for missing in range(len(gaps)):
        bounds=point(gaps);bounds[missing]=['0',None]
        yield {'condition':'one_missing_gap','replicate':missing,'bounds':bounds,'inferred':infer_partitions(bounds,groups),
               'count_free':{'status':'abstain','reason':'missing_measurement','possible_counts':[1,len(gaps)+1]}}
    for label,bounds in [('all_missing_gaps',[['0',None] for _ in gaps]),('forced_equal_gaps',[['1','1'] for _ in gaps])]:
        yield {'condition':label,'replicate':0,'bounds':bounds,'inferred':infer_partitions(bounds,groups)}
    for radius in RADII:
        bounds=[[str(max(Fraction(0),gap-radius)),str(gap+radius)] for gap in gaps]
        yield {'condition':'gap_radius','replicate':str(radius),'bounds':bounds,'inferred':infer_partitions(bounds,groups)}
    # Unit, origin and orientation transformations are quantity-free invariances.
    translated=[{**x,'START_POSITION':str(Fraction(x['START_POSITION'])+100),'END_POSITION':str(Fraction(x['END_POSITION'])+100)} for x in case['clusters']]
    translated_gaps=[Fraction(b['START_POSITION'])-Fraction(a['END_POSITION']) for a,b in zip(translated,translated[1:])]
    yield {'condition':'translate_intervals','replicate':100,'bounds':point(translated_gaps),'inferred':infer_partitions(point(translated_gaps),groups)}
    for scale in (Fraction(1,10),Fraction(10)):
        bounds=point([x*scale for x in gaps])
        yield {'condition':'scale_intervals','replicate':str(scale),'bounds':bounds,'inferred':infer_partitions(bounds,groups)}
    extent=max(Fraction(x['END_POSITION']) for x in case['clusters'])+1
    mirrored=[(extent-Fraction(x['END_POSITION']),extent-Fraction(x['START_POSITION'])) for x in reversed(case['clusters'])]
    mirrored_gaps=[b[0]-a[1] for a,b in zip(mirrored,mirrored[1:])]
    yield {'condition':'reverse_orientation','replicate':0,'bounds':point(mirrored_gaps),'inferred':infer_partitions(point(mirrored_gaps),groups)}

def run():
    endpoint=OUT/'endpoints/intervals-v1'
    if endpoint.exists():
        raise FileExistsError(endpoint)
    endpoint.mkdir(parents=True)
    source=RAW/'interval-component-input.json';inp=json.loads(source.read_text(encoding='utf-8'))
    output=RAW/'interval-inferences.jsonl'
    if output.exists():
        raise FileExistsError(output)
    count=0
    with output.open('w',encoding='utf-8') as f:
        for case in inp['cases']:
            for record in cases_for_input(case):
                record['case_id']=case['id']
                f.write(json.dumps(record,separators=(',',':'))+'\n');count+=1
    save(endpoint/'inference-manifest.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'input_sha256':sha(source),
          'inference_path':output.relative_to(ROOT).as_posix(),'inference_sha256':sha(output),'records':count,
          'code_sha256':sha(Path(__file__)),'quantities_received':False,'reference_partition_received':False})
    for name in ['PROTOCOL_INTERVALS.md','interval-protocol-freeze.json','interval-input-manifest.json']:
        shutil.copyfile(OUT/name,endpoint/name)
    shutil.copyfile(Path(__file__),endpoint/Path(__file__).name)
    print('Saved '+str(count)+' quantity-free interval inferences.')

def score():
    endpoint=OUT/'endpoints/intervals-v1'
    cases={x['id']:x for x in json.loads((RAW/'interval-component-input.json').read_text(encoding='utf-8'))['cases']}
    keys={x['id']:x for x in json.loads((RAW/'interval-evaluator-key.json').read_text(encoding='utf-8'))['cases']}
    summaries=collections.defaultdict(lambda:collections.Counter())
    detailed=RAW/'interval-scores.jsonl'
    if detailed.exists():
        raise FileExistsError(detailed)
    sensitivity=[];missing=[];baseline=[];count_free_scores=[]
    with detailed.open('w',encoding='utf-8') as f:
        for line in (RAW/'interval-inferences.jsonl').open(encoding='utf-8'):
            record=json.loads(line);case=cases[record['case_id']]
            reference=[case['eligible_boundaries'].index(x) for x in keys[case['id']]['reference_boundaries']]
            if record['condition']=='reverse_orientation':
                reference=sorted(len(case['gaps'])-1-x for x in reference)
            candidates=[x['cuts'] for x in record['inferred']['admissible']]
            survives=reference in candidates;unique_correct=len(candidates)==1 and survives
            evaluation={'reference_survives':survives,'unique_correct':unique_correct,'admissible_count':len(candidates)}
            if len(candidates)==1:
                intersection=len(set(reference)&set(candidates[0]))
                evaluation['boundary_precision']=str(Fraction(intersection,len(candidates[0])))
                evaluation['boundary_recall']=str(Fraction(intersection,len(reference)))
            out={'case_id':case['id'],'condition':record['condition'],'replicate':record['replicate'],'evaluation':evaluation}
            f.write(json.dumps(out,separators=(',',':'))+'\n')
            aggregate=summaries[(case['id'],record['condition'])]
            aggregate['records']+=1;aggregate['reference_survives']+=int(survives);aggregate['unique_correct']+=int(unique_correct)
            aggregate['admissible_count_'+str(len(candidates))]+=1
            if record['condition']=='recorded_point':
                count_free_scores.append({'case_id':case['id'],'output':record['count_free'],'reference_group_count':case['group_count_prior']})
            if record['condition']=='gap_radius':
                sensitivity.append(out)
            if record['condition']=='one_missing_gap':
                missing.append(out)
    for case in cases.values():
        reference=[case['eligible_boundaries'].index(x) for x in keys[case['id']]['reference_boundaries']]
        balanced=balanced_partitions(case)
        baseline.append({'case_id':case['id'],'clusters':len(case['clusters']),'eligible_boundaries':len(case['gaps']),
                         'known_count_order_only_partitions':math.comb(len(case['gaps']),case['group_count_prior']-1),
                         'unknown_count_order_only_partitions':2**len(case['gaps']),
                         'equal_cord_count_candidates':len(balanced['candidates']),
                         'equal_cord_count_reference_survives':reference in [x['cuts'] for x in balanced['candidates']],
                         'equal_cord_count_unique_correct':len(balanced['candidates'])==1 and balanced['candidates'][0]['cuts']==reference,
                         'equal_cord_count_minimum_deviation':balanced['minimum_absolute_size_deviation']})
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'source-reference-controlled grouping; quantities absent from grouping inputs',
            'summaries':[{'case_id':name,'condition':condition,**dict(counts)} for (name,condition),counts in sorted(summaries.items())],
            'information_loss':baseline,'sensitivity':sensitivity,'missing_gap_cases':missing,'count_free_estimator':count_free_scores,
            'scores_path':detailed.relative_to(ROOT).as_posix(),'scores_sha256':sha(detailed),
            'evaluator_key_sha256':sha(RAW/'interval-evaluator-key.json'),'inference_sha256':sha(RAW/'interval-inferences.jsonl')}
    save(endpoint/'aggregate.json',result)
    print(json.dumps({'information_loss':baseline,'point':[x for x in result['summaries'] if x['condition']=='recorded_point'],
                      'permutation':[x for x in result['summaries'] if x['condition']=='gap_multiset_permutation'],'sensitivity':sensitivity},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run','score']);a=p.parse_args()
    {'prepare':prepare,'run':run,'score':score}[a.command]()
