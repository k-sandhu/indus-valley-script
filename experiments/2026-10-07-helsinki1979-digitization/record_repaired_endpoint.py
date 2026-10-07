"""Record the supplied frozen endpoint; diagnose checks without new inference."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RUN=HERE/'repair/2026-10-07-v2'
DEFAULT=HERE/'follow-up/2026-10-07/endpoint-record-v1'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as s:
        for block in iter(lambda:s.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def wilson(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n
    mid=(p+z*z/(2*n))/d;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return dict(success=k,total=n,rate=p,ci95=[max(0,mid-half),min(1,mid+half)])


def indices(rows,predicate):return [r['sample_index'] for r in rows if predicate(r)]


def row_summary(rows):
    return dict(rows=len(rows),crop_failures=indices(rows,lambda r:not r['crop_correct']),
        count_failures=indices(rows,lambda r:not r['count_agrees']),
        number_failures=indices(rows,lambda r:not r['number_correct']),
        classification_field_failures=indices(rows,lambda r:not r['classification_correct']),
        top1_failures=indices(rows,lambda r:not r['strict_top1']['whole_row_compatible']),
        top5_failures=indices(rows,lambda r:not r['strict_top5']['whole_row_compatible']))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=DEFAULT);args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned output directory')
    frozen=[HERE/'pipeline.py',HERE/'evaluate.py',HERE/'evaluate_repair.py',HERE/'layout_v2.py',HERE/'layout_v3.py',
            HERE/'freeze_repair.py',HERE/'freeze_repair_v2.py',HERE/'freeze-manifest.json']
    frozen+=list((HERE/'evaluation/2026-10-07-frozen-v1').rglob('*'))
    frozen+=list((HERE/'blind').rglob('*.json'))
    frozen+=list((RUN/'blind').rglob('*'))
    frozen+=list((RUN/'evaluation-2026-10-07-adjudicated').rglob('*'))
    frozen += [RUN/p for p in ('freeze-manifest.json','prediction-freeze.json','predictions.json','count-page-detections.json','frame.json')]
    frozen=list(dict.fromkeys(p for p in frozen if p.is_file()))
    before={str(p.relative_to(HERE)).replace('\\','/'):sha(p) for p in frozen}
    m=read(RUN/'evaluation-2026-10-07-adjudicated/metrics.json')
    old=read(HERE/'evaluation/2026-10-07-frozen-v1/metrics.json')
    sel=read(RUN/'blind/selection.json');refs={r['sample_index']:r for r in read(RUN/'blind/adjudicated-reference.json')['rows']}
    ps={r['sample_index']:r for r in read(RUN/'predictions.json')['rows']}
    sections={r['sample_index']:r['section'] for r in sel['rows']};rows=m['rows']
    assert len(rows)==80 and sorted(r['sample_index'] for r in rows)==list(range(80))
    f=read(RUN/'freeze-manifest.json');pf=read(RUN/'prediction-freeze.json')
    assert all(sha(HERE/p)==h for p,h in f['code_hashes'].items())
    for field,path in [('freeze_sha256',RUN/'freeze-manifest.json'),('prediction_sha256',RUN/'predictions.json'),
        ('reference_sha256',RUN/'blind/adjudicated-reference.json'),('count_reference_sha256',RUN/'blind/adjudicated-counts.json'),
        ('evaluator_sha256',HERE/'evaluate_repair.py')]:assert m[field]==sha(path)
    assert sha(RUN/'predictions.json')==pf['prediction_sha256']
    predicates={
        'crop_rejected':lambda r:not r['crop_correct'],
        'count_wrong_after_accepted_crop':lambda r:r['crop_correct'] and not r['count_agrees'],
        'count_consistent_accepted_crop':lambda r:r['crop_correct'] and r['count_agrees'],
        'number_wrong':lambda r:not r['number_correct'],
        'classification_field_wrong':lambda r:not r['classification_correct'],
        'either_field_wrong':lambda r:not (r['number_correct'] and r['classification_correct']),
        'number_wrong_after_crop_and_count':lambda r:r['crop_correct'] and r['count_agrees'] and not r['number_correct'],
        'classification_field_wrong_after_crop_and_count':lambda r:r['crop_correct'] and r['count_agrees'] and not r['classification_correct'],
    }
    subsets={k:dict(count=len(ids:=indices(rows,p)),sample_indices=ids) for k,p in predicates.items()}
    partitions={};quality={}
    for name in ('strict_top1','strict_top5'):
        incompatible=[r for r in rows if not r[name]['whole_row_compatible']]
        parts=dict(crop=indices(incompatible,lambda r:not r['crop_correct']),
            unit_count=indices(incompatible,lambda r:r['crop_correct'] and not r['count_agrees']),
            unit_candidates_count_consistent_proxy=indices(incompatible,lambda r:r['crop_correct'] and r['count_agrees']))
        assert sum(map(len,parts.values()))==len(incompatible)
        partitions[name]=dict(incompatible_rows=len(incompatible),counts={k:len(v) for k,v in parts.items()},sample_indices=parts)
        quality[name]={k:dict(count=len(v),sample_indices=v) for k,v in dict(
            crop=indices(rows,lambda r:not r['crop_correct']),
            unit_count=indices(rows,lambda r:r['crop_correct'] and not r['count_agrees']),
            unit_candidates_count_consistent_proxy=indices(rows,lambda r:r['crop_correct'] and r['count_agrees'] and not r[name]['whole_row_compatible']),
            passes_geometry_count_candidates=indices(rows,lambda r:r['crop_correct'] and r['count_agrees'] and r[name]['whole_row_compatible'])).items()}
        assert sum(v['count'] for v in quality[name].values())==80
    proxy=[r for r in rows if r['crop_correct'] and r['count_agrees']]
    proxy_details={}
    for name in ('strict_top1','strict_top5','shape_only_top1','shape_only_top5'):
        matched=sum(r[name]['equal_count_position_correct'] for r in proxy)
        units=sum(r['reference_count'] for r in proxy)
        proxy_details[name]=dict(correct=matched,total=units,incorrect=units-matched,
            compatible_rows=sum(r[name]['whole_row_compatible'] for r in proxy),row_total=len(proxy))
    reader_files=[RUN/f'blind/reader-{a}/{name}' for a in ('a','b') for name in ('rows-part1.json','rows-part2.json','counts.json')]
    readers={a:{r['sample_index']:r for part in (1,2) for r in read(RUN/f'blind/reader-{a}/rows-part{part}.json')['rows']} for a in ('a','b')}
    agreement_fields=('printed_inscription_id','classification_literal','drawn_unit_count','crop_correct')
    row_agreement={field:sum(readers['a'][i][field]==readers['b'][i][field] for i in range(80)) for field in agreement_fields}
    unit_agreement=unit_total=0;disagreement_rows=[];unit_differences=[]
    for i in range(80):
        a=readers['a'][i]['units'];b=readers['b'][i]['units'];assert len(a)==len(b)
        disagree=False
        for j,(u,v) in enumerate(zip(a,b)):
            unit_total+=1
            if set(u['strict_candidate_codes'])==set(v['strict_candidate_codes']):unit_agreement+=1
            else:
                disagree=True;unit_differences.append(dict(sample_index=i,unit_index=j,reader_a=u['strict_candidate_codes'],reader_b=v['strict_candidate_codes']))
        if disagree:disagreement_rows.append(i)
    tags={};source_rows=[]
    for r in rows:
        i=r['sample_index'];ref=refs[i]
        for tag in set(ref.get('crop_issues',[])):tags.setdefault(tag,[]).append(i)
        source_rows.append(dict(sample_index=i,pdf_page=r['pdf_page'],section=sections[i],
            margin_side=ps[i]['margin_side'],parity='even' if r['pdf_page']%2==0 else 'odd',
            metric_fields=r,adjudicated_crop_issues=ref.get('crop_issues',[]),adjudicated_crop_note=ref.get('crop_note'),
            reader_a_crop_issues=readers['a'][i].get('crop_issues',[]),reader_a_crop_observations=readers['a'][i].get('crop_observations'),
            reader_b_crop_issues=readers['b'][i].get('crop_issues',[]),reader_b_crop_observations=readers['b'][i].get('crop_observations'),
            blank_gaps=ref.get('blank_gaps',[]),unresolved_boundary=ref.get('unresolved_boundary')))
    by_section={s:row_summary([r for r in rows if sections[r['sample_index']]==s]) for s in sel['denominators']}
    by_side={s:row_summary([r for r in rows if ps[r['sample_index']]['margin_side']==s]) for s in ('left','right')}
    by_parity={s:row_summary([r for r in rows if ('even' if r['pdf_page']%2==0 else 'odd')==s]) for s in ('even','odd')}
    by_page={str(p):row_summary([r for r in rows if r['pdf_page']==p]) for p in sorted({r['pdf_page'] for r in rows})}
    pages=m['source_row_recall']['pages']
    count_failures=[dict(missing=p['true']-p['matched'],**p) for p in pages if p['true']!=p['matched']]
    notes=read(RUN/'blind/adjudication-notes.json')
    timings=[]
    for path in reader_files:
        j=read(path);duration=(datetime.fromisoformat(j['finished_utc'].replace('Z','+00:00'))-datetime.fromisoformat(j['started_utc'].replace('Z','+00:00'))).total_seconds()
        timings.append(dict(path=str(path.relative_to(HERE)).replace('\\','/'),reader=j['reader'],part=j['part'],
            started_utc=j['started_utc'],finished_utc=j['finished_utc'],elapsed_seconds=duration,
            items=len(j.get('rows',j.get('pages',[]))),notes=j['notes']))
    row_timings=[x for x in timings if x['part']!=3];count_timings=[x for x in timings if x['part']==3]
    # Summed task time is throughput bookkeeping, not human effort or billed tokens.
    wall=(max(datetime.fromisoformat(x['finished_utc'].replace('Z','+00:00')) for x in timings)-min(datetime.fromisoformat(x['started_utc'].replace('Z','+00:00')) for x in timings)).total_seconds()
    n=11369;projections={}
    for name,pred in [('crop_correction',lambda r:not r['crop_correct']),('unit_count_correction',lambda r:not r['count_agrees']),
        ('top1_sequence_correction',lambda r:not r['strict_top1']['whole_row_compatible']),('top5_proposal_miss',lambda r:not r['strict_top5']['whole_row_compatible']),
        ('number_correction',lambda r:not r['number_correct']),('classification_field_correction',lambda r:not r['classification_correct']),
        ('either_field_correction',lambda r:not (r['number_correct'] and r['classification_correct']))]:
        measure=wilson(len(indices(rows,pred)),80)
        projections[name]=dict(**measure,expected_occurrences=n*measure['rate'],projected_ci95=[n*x for x in measure['ci95']])
    da=wilson(len(disagreement_rows),80)
    projections['strict_reader_disagreement']=dict(**da,expected_occurrences=n*da['rate'],projected_ci95=[n*x for x in da['ci95']])
    cost=dict(status='Exploratory',population_occurrences=n,population_scope='original provisional extraction; incomplete row recall, not a true edition census',
        sample_frame=m['frame'],required_human_row_readings=n,required_second_ai_row_readings=n,minimum_row_readings=2*n,
        projections=projections,correction_categories_overlap=True,
        observed_reader_task_timing=timings,reader_summed_elapsed_seconds=sum(x['elapsed_seconds'] for x in timings),
        row_reader_summed_elapsed_seconds=sum(x['elapsed_seconds'] for x in row_timings),
        count_reader_summed_elapsed_seconds=sum(x['elapsed_seconds'] for x in count_timings),
        reader_wall_span_seconds=wall,reader_row_readings=sum(x['items'] for x in row_timings),
        ai_elapsed_seconds_per_row_reading=sum(x['elapsed_seconds'] for x in row_timings)/160,
        ai_one_pass_projected_task_hours=n*sum(x['elapsed_seconds'] for x in row_timings)/160/3600,
        human_scenarios=[dict(assumed_minutes_per_row=k,hours=n*k/60,eight_hour_days=n*k/480) for k in (1,2,5)],
        adjudicator_time_seconds=None,billed_usd=None,billed_tokens=None,
        monetary_cost_note='No billing witness supplied; reader wall/task times do not establish monetary cost or human throughput.',
        extrapolation_note='Unweighted 28/26/26 sample rates used for planning; new all-section frame differs from old output. No population accuracy claim. Human/AI disagreement rate and missing-row recovery costs remain unmeasured.')
    result=dict(status='Exploratory',frozen_endpoint_status=m['status'],pipeline_status=m['pipeline_status'],frames=dict(first='60 numbered-section rows, PDF31–79; detected frame3460/11369; no sorted target',second=m['frame']),
        comparison=dict(first_summary=old['summary'],first_bootstrap=old['row_bootstrap_95'],second_summary=m['summary'],second_bootstrap=m['row_bootstrap_95'],source_row_recall=m['source_row_recall']),
        criteria=m['negative_result_criteria'],subsets=subsets,incompatible_whole_row_partitions=partitions,
        earliest_quality_check_partitions=quality,count_consistent_accepted_crop_proxy=proxy_details,
        proxy_limitation='Accepted crop and equal unit counts do not independently validate one-to-one glyph boundaries.',
        crop_issues={tag:dict(count=len(v),sample_indices=v) for tag,v in sorted(tags.items())},
        by_section=by_section,by_margin_side=by_side,by_page_parity=by_parity,by_page=by_page,count_page_failures=count_failures,
        compact_stress_page_scope='129/130 are excluded from row-recognition evaluation as development pages; evaluated only for row recall',
        readers=dict(row_field_agreement=row_agreement,row_fields_total=320,strict_unit_set_agreement=unit_agreement,strict_units_total=unit_total,
            strict_disagreement_rows=disagreement_rows,strict_disagreement_units=unit_differences,
            adjudication_notes=len(notes),adjudication_scope_counts=dict(Counter(x['scope'] for x in notes)),adjudication_field_counts=dict(Counter(x['field'] for x in notes))),
        quarantine=dict(all_original_occurrences=11369,released_occurrences=0,global_rule_passes=all(m['negative_result_criteria'].values())),
        input_hashes=before,rows=source_rows)
    assert row_agreement=={k:80 for k in agreement_fields} and (unit_agreement,unit_total)==(333,352)
    out.mkdir(parents=True)
    for name,payload in [('diagnosis.json',result),('review-workload.json',cost)]:
        (out/name).write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    for name in ('README.md','REPORT.md','RETROSPECTIVE.md','registry-entry.json','IMPORT_INTERFACE.md','sources.json'):
        shutil.copyfile(HERE/name,out/(name+'.before-record.txt'))
    assert all(sha(HERE/p)==h for p,h in before.items())
    (out/'preservation-check.json').write_text(json.dumps(dict(status='Verified computation',all_unchanged=True,frozen_file_count=len(before),hashes=before),indent=2),encoding='utf-8')
    print(json.dumps(dict(subsets=subsets,partitions=partitions,proxy=proxy_details,
        crop_tags={k:v['count'] for k,v in result['crop_issues'].items()},
        sections={k:{x:len(v[x]) if isinstance(v[x],list) else v[x] for x in v} for k,v in by_section.items()},
        reader_disagreement_rows=disagreement_rows,timing={k:v for k,v in cost.items() if 'seconds' in k or k in ['ai_one_pass_projected_task_hours','human_scenarios']},
        frozen_files=len(before)),indent=2))


if __name__=='__main__':main()
