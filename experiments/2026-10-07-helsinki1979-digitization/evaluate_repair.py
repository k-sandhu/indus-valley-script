"""Evaluate the repaired freeze against two readers and source-only adjudication."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import random
import numpy as np
import evaluate as E

HERE=Path(__file__).resolve().parent
RUN=HERE/'repair/2026-10-07-v2'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def recall_page(predicted,reference):
    matched=detected=true=0;columns=[]
    for column in reference['columns']:
        left,right=column['x_extent_pdf'];actual=column['row_centers_pdf']
        assert len(actual)==column['row_count']
        guesses=[r['row_anchor_y_2x']/2 for r in predicted if left<=(r['margin_xyxy_2x'][0]+r['margin_xyxy_2x'][2])/4<=right]
        pairs=sorted((abs(a-b),i,j) for i,a in enumerate(guesses) for j,b in enumerate(actual) if abs(a-b)<=9)
        used_guess=set();used_true=set()
        for distance,i,j in pairs:
            if i in used_guess or j in used_true:continue
            used_guess.add(i);used_true.add(j)
        count=len(used_true);matched+=count;true+=len(actual);detected+=len(guesses)
        columns.append(dict(reference_rows=len(actual),detected_rows=len(guesses),matched_rows=count))
    # Predictions outside every source-column extent are false positives.
    detected=len(predicted)
    return dict(pdf_page=reference['pdf_page'],matched=matched,true=true,detected=detected,columns=columns)


def page_summary(pages):
    m=sum(p['matched'] for p in pages);t=sum(p['true'] for p in pages);d=sum(p['detected'] for p in pages)
    return dict(pages=len(pages),matched=m,true_rows=t,detected_rows=d,recall=E.wilson(m,t),precision=E.wilson(m,d))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned evaluation directory')
    freeze=read(RUN/'freeze-manifest.json');pfreeze=read(RUN/'prediction-freeze.json')
    assert E.sha(RUN/'predictions.json')==pfreeze['prediction_sha256']
    assert E.sha(HERE/'evaluate_repair.py')==freeze['code_hashes']['evaluate_repair.py']
    selection=read(RUN/'blind/selection.json');pred=read(RUN/'predictions.json')['rows']
    reference=read(RUN/'blind/adjudicated-reference.json')['rows']
    assert sorted(r['sample_index'] for r in reference)==list(range(80))
    refs={r['sample_index']:r for r in reference};rows=[]
    for p in pred:
        ref=refs[p['sample_index']];r=E.score_row(p,ref)
        if ref.get('valid_printed_target') is False:
            r.update(crop_correct=False,count_agrees=False,number_correct=False,classification_correct=False,uniquely_resolved_exact_sequence=False)
            for key in ('strict_top1','strict_top5','shape_only_top1','shape_only_top5'):r[key]['whole_row_compatible']=False
        rows.append(r)
    summary=E.aggregate(rows);rng=np.random.default_rng(2026100781);boot=[]
    # Resample within the frozen section quotas.
    section_indices={s:[i for i,p in enumerate(pred) if p['section']==s] for s in selection['denominators']}
    for _ in range(2000):
        sampled=[rows[j] for indices in section_indices.values() for j in rng.choice(indices,len(indices))]
        a=E.aggregate(sampled)
        boot.append([a['strict_top1']['aligned_recall']['rate'],a['strict_top5']['aligned_recall']['rate'],
                     a['strict_top1']['same_position_equal_count']['rate'],a['strict_top5']['same_position_equal_count']['rate'],
                     a['calibration']['brier'],a['calibration']['ece10']])
    names=['strict_top1_aligned_recall','strict_top5_aligned_recall','strict_top1_same_position_equal_count',
           'strict_top5_same_position_equal_count','calibration_brier','calibration_ece10']
    intervals={name:np.nanquantile(np.array(boot,dtype=float)[:,i],[.025,.975]).tolist() for i,name in enumerate(names)}
    counts=read(RUN/'blind/adjudicated-counts.json')['pages'];frame=read(RUN/'frame.json')
    by_page={p['layout']['orientation']['rotation']:None for p in frame['pages']}
    # Frame rows exclude development; count matching needs the complete unfiltered page detections.
    detection=read(RUN/'count-page-detections.json')['pages']
    pages=[recall_page(next(p['rows'] for p in detection if p['pdf_page']==r['pdf_page']),r) for r in counts]
    original_rng=random.Random(2026100791);random_pages=[]
    for lo,hi in [(22,78),(79,130),(131,180)]:random_pages.extend(original_rng.sample(list(range(lo,hi+1)),6))
    random_set=set(random_pages);random_results=[p for p in pages if p['pdf_page'] in random_set]
    stress=[p for p in pages if p['pdf_page'] in {62,129,130}]
    count_boot=[]
    for _ in range(2000):
        sampled=[random_results[i] for i in rng.integers(0,len(random_results),len(random_results))]
        a=page_summary(sampled);count_boot.append([a['recall']['rate'],a['precision']['rate']])
    recall=page_summary(random_results)
    criteria=dict(crop_90=summary['row_crop_correctness']['success']>=72,
                  number_90=summary['inscription_number_accuracy']['success']>=72,
                  count_95=summary['drawn_unit_count_agreement']['success']>=76,
                  top5_rows_80=summary['strict_top5']['whole_rows_all_sample']['success']>=64,
                  random_page_recall_95=recall['recall']['rate'] is not None and recall['recall']['rate']>=.95)
    result=dict(status='Frozen evaluation',pipeline_status='Verified computation' if all(criteria.values()) else 'Failed',
       summary=summary,row_bootstrap_95=intervals,bootstrap=dict(seed=2026100781,replicates=2000,unit='row within section'),
       source_row_recall=dict(random=recall,stress=page_summary(stress),pages=pages,
          random_page_bootstrap_ci95=dict(recall=np.quantile(np.array(count_boot)[:,0],[.025,.975]).tolist(),precision=np.quantile(np.array(count_boot)[:,1],[.025,.975]).tolist()),
          matching_tolerance_pdf_points=9,random_pages=random_pages),negative_result_criteria=criteria,
       frame=dict(rows=80,section_quotas=dict(number_order=28,end_sorted=26,beginning_sorted=26),denominators=selection['denominators'],
                  development_pages_excluded=freeze['development_pages'],previous_60_targets_excluded=True),
       freeze_sha256=E.sha(RUN/'freeze-manifest.json'),prediction_sha256=E.sha(RUN/'predictions.json'),
       reference_sha256=E.sha(RUN/'blind/adjudicated-reference.json'),count_reference_sha256=E.sha(RUN/'blind/adjudicated-counts.json'),
       evaluator_sha256=E.sha(__file__),rows=rows)
    out.mkdir(parents=True);(out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(summary=summary,criteria=criteria,row_recall=recall),indent=2))


if __name__=='__main__':main()
