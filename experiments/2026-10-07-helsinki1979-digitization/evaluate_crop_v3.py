"""Frozen v3 scorer; consumes coordinator-provided adjudication, never creates it."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import evaluate as E
import evaluate_repair as ER

HERE=Path(__file__).resolve().parent
DEFAULT=HERE/'repair/2026-10-08-v3'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def recall_page(predicted,reference,physical=False):
    matched=detected=true=0;columns=[]
    for column in reference['columns']:
        left,right=column['x_extent_pdf']
        actual=column['physical_line_centers_pdf'] if physical else column['row_centers_pdf']
        assert len(actual)==column['physical_line_count' if physical else 'row_count']
        guesses=[]
        for r in predicted:
            if not physical and r['line_kind']!='numbered':continue
            field=r.get('margin_pdf_box');box=r['glyph_pdf_box']
            x=(field[0]+field[2])/2 if field else (box[0]+box[2])/2
            if left<=x<=right:guesses.append((box[1]+box[3])/2 if physical else r['row_anchor_y_2x']/2)
        pairs=sorted((abs(a-b),i,j) for i,a in enumerate(guesses) for j,b in enumerate(actual) if abs(a-b)<=9)
        used_guess=set();used_true=set()
        for distance,i,j in pairs:
            if i not in used_guess and j not in used_true:used_guess.add(i);used_true.add(j)
        matched+=len(used_true);true+=len(actual);detected+=len(guesses)
        columns.append(dict(reference_rows=len(actual),detected_rows=len(guesses),matched_rows=len(used_true)))
    detected=sum(physical or r['line_kind']=='numbered' for r in predicted)
    return dict(pdf_page=reference['pdf_page'],matched=matched,true=true,detected=detected,columns=columns)

def count_summary(pages,selection,rng):
    random=[p for p in pages if p['pdf_page'] in selection['random_count_pages']]
    stress=[p for p in pages if p['pdf_page'] in selection['stress_pages']];boot=[]
    for _ in range(2000):
        a=ER.page_summary([random[i] for i in rng.integers(0,len(random),len(random))])
        boot.append([a['recall']['rate'],a['precision']['rate']])
    return dict(random=ER.page_summary(random),stress=ER.page_summary(stress),pages=pages,
        random_page_bootstrap_ci95=dict(recall=np.quantile(np.array(boot)[:,0],[.025,.975]).tolist(),
            precision=np.quantile(np.array(boot)[:,1],[.025,.975]).tolist()),matching_tolerance_pdf_points=9)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,default=DEFAULT);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    run=args.run.resolve();out=args.out.resolve()
    if not run.is_relative_to(HERE) or not out.is_relative_to(HERE) or out.exists():raise ValueError('Use owned inputs and a new owned output')
    freeze=read(run/'freeze-manifest.json');pf=read(run/'prediction-freeze.json')
    assert E.sha(HERE/'evaluate_crop_v3.py')==freeze['code_hashes']['evaluate_crop_v3.py']
    assert E.sha(HERE/'evaluate.py')==freeze['code_hashes']['evaluate.py']
    assert E.sha(HERE/'evaluate_repair.py')==freeze['code_hashes']['evaluate_repair.py']
    for p,k in [('predictions.json','prediction_sha256'),('blind/selection.json','selection_sha256'),('count-page-detections.json','count_detections_sha256')]:
        assert E.sha(run/p)==pf[k]
    assert E.sha(run/'freeze-manifest.json')==pf['freeze_sha256']
    selection=read(run/'blind/selection.json');pred=read(run/'predictions.json')['rows'];reference=read(run/'blind/adjudicated-reference.json')['rows']
    assert sorted(r['sample_index'] for r in reference)==list(range(80))
    assert sorted(r['sample_index'] for r in pred)==list(range(80))
    refs={r['sample_index']:r for r in reference};rows=[]
    for p in pred:
        ref=refs[p['sample_index']];r=E.score_row(p,ref)
        if ref.get('valid_printed_target') is False:
            r.update(crop_correct=False,count_agrees=False,number_correct=False,classification_correct=False,uniquely_resolved_exact_sequence=False)
            for key in ('strict_top1','strict_top5','shape_only_top1','shape_only_top5'):r[key]['whole_row_compatible']=False
        rows.append(r)
    summary=E.aggregate(rows);rng=np.random.default_rng(2026100881);boot=[]
    strata={s:[i for i,p in enumerate(pred) if p['section']==s] for s in selection['denominators']}
    for _ in range(2000):
        a=E.aggregate([rows[j] for indices in strata.values() for j in rng.choice(indices,len(indices))])
        boot.append([a['strict_top1']['aligned_recall']['rate'],a['strict_top5']['aligned_recall']['rate'],
            a['strict_top1']['same_position_equal_count']['rate'],a['strict_top5']['same_position_equal_count']['rate'],
            a['calibration']['brier'],a['calibration']['ece10']])
    names=['strict_top1_aligned_recall','strict_top5_aligned_recall','strict_top1_same_position_equal_count',
        'strict_top5_same_position_equal_count','calibration_brier','calibration_ece10']
    intervals={name:np.nanquantile(np.array(boot,dtype=float)[:,i],[.025,.975]).tolist() for i,name in enumerate(names)}
    counts=read(run/'blind/adjudicated-counts.json')['pages'];detections=read(run/'count-page-detections.json')['pages']
    assert sorted(p['pdf_page'] for p in counts)==selection['count_pages']
    by_page={p['pdf_page']:p['rows'] for p in detections}
    numbered=count_summary([recall_page(by_page[r['pdf_page']],r) for r in counts],selection,rng)
    physical=count_summary([recall_page(by_page[r['pdf_page']],r,True) for r in counts],selection,rng)
    criteria={name:summary[key]['total']==80 and summary[key]['rate']>=threshold for name,key,threshold in [
        ('crop_90','row_crop_correctness',.90),('number_90','inscription_number_accuracy',.90),('count_95','drawn_unit_count_agreement',.95)]}
    criteria['top5_rows_80']=summary['strict_top5']['whole_rows_all_sample']['success']>=64
    criteria['random_page_recall_95']=numbered['random']['recall']['rate'] is not None and numbered['random']['recall']['rate']>=.95
    result=dict(status='Frozen evaluation',pipeline_status='Verified computation' if all(criteria.values()) else 'Failed',
        summary=summary,row_bootstrap_95=intervals,bootstrap=dict(seed=2026100881,replicates=2000,unit='row within section'),
        source_row_recall=numbered,physical_line_recall=physical,negative_result_criteria=criteria,
        physical_line_recall_note='Separate completeness measure; original five global criteria retained. Quarantine remains pending option-B verification.',
        frame=dict(rows=80,section_quotas=dict(number_order=28,end_sorted=26,beginning_sorted=26),denominators=selection['denominators'],
            eligible_pages=selection['eligible_pages'],excluded_pages=selection['excluded_pages'],old140_targets_excluded=True),
        freeze_sha256=E.sha(run/'freeze-manifest.json'),prediction_sha256=E.sha(run/'predictions.json'),
        reference_sha256=E.sha(run/'blind/adjudicated-reference.json'),count_reference_sha256=E.sha(run/'blind/adjudicated-counts.json'),
        evaluator_sha256=E.sha(__file__),rows=rows)
    out.mkdir(parents=True);(out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(summary=summary,criteria=criteria,numbered_recall=numbered['random'],physical_recall=physical['random']),indent=2))
if __name__=='__main__':main()
