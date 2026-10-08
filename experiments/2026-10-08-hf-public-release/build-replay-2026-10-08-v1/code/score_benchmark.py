"""Score a staged benchmark or new predictions. Outputs go only to --out."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import random
import sys
import numpy as np
import pyarrow.parquet as pq

def setup(release):
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(release/'code'))
    import score_core, score_recall
    return score_core, score_recall

def load_rows(release,version,predictions=None):
    rows=pq.read_table(release/'data'/f'benchmark_rows_{version}.parquet').to_pylist()
    preds=[json.loads(r['prediction_json']) for r in rows]
    if predictions:
        path=Path(predictions)
        if path.suffix=='.jsonl':preds=[json.loads(line) for line in path.read_text(encoding='utf8').splitlines() if line.strip()]
        else:
            obj=json.loads(path.read_text(encoding='utf-8-sig'));preds=obj['rows'] if isinstance(obj,dict) else obj
    indices=[p['sample_index'] for p in preds]
    assert len(indices)==len(set(indices))==len(rows),'Supply exactly one prediction for every benchmark sample.'
    byid={p['sample_index']:p for p in preds}
    assert set(byid)=={r['sample_index'] for r in rows},'Prediction indices differ from the reference.'
    return rows,[byid[r['sample_index']] for r in rows]

def compute(release,version,predictions=None,bootstrap=True):
    E,R=setup(release)
    data,preds=load_rows(release,version,predictions)
    rows=[]
    for p,datum in zip(preds,data):
        ref=json.loads(datum['reference_json']);r=E.score_row(p,ref)
        if version=='v2' and ref.get('valid_printed_target') is False:
            r.update(crop_correct=False,count_agrees=False,number_correct=False,classification_correct=False,uniquely_resolved_exact_sequence=False)
            for key in ('strict_top1','strict_top5','shape_only_top1','shape_only_top5'):r[key]['whole_row_compatible']=False
        rows.append(r)
    summary=E.aggregate(rows)
    result=dict(summary=summary,rows=rows)
    if version=='v1':
        exposed={r['sample_index'] for r in data if r['original_ocr_locator_exposed']}
        result['exploratory_sensitivities']={
            'excluding_original_ocr_locator_witness_rows':E.aggregate([r for r in rows if r['sample_index'] not in exposed]),
            'excluding_annotator_A':E.aggregate([r for r in rows if r['sample_index']>=20]),
            'source_confirmed_correct_crops_only':E.aggregate([r for r in rows if r['crop_correct'] is True])}
        criteria=dict(crop_90=summary['row_crop_correctness']['rate'] is not None and summary['row_crop_correctness']['rate']>=.90,
            number_90=summary['inscription_number_accuracy']['rate'] is not None and summary['inscription_number_accuracy']['rate']>=.90,
            count_95=summary['drawn_unit_count_agreement']['rate'] is not None and summary['drawn_unit_count_agreement']['rate']>=.95,
            top5_rows_80=summary['strict_top5']['whole_rows_all_sample']['rate']>=.80)
    else:
        countdata=pq.read_table(release/'data/benchmark_count_pages.parquet').to_pylist()
        pages=[R.recall_page(json.loads(d['detections_json']),json.loads(d['reference_json'])) for d in countdata]
        original_rng=random.Random(2026100791);random_pages=[]
        for lo,hi in [(22,78),(79,130),(131,180)]:random_pages.extend(original_rng.sample(list(range(lo,hi+1)),6))
        random_results=[p for p in pages if p['pdf_page'] in set(random_pages)]
        stress=[p for p in pages if p['pdf_page'] in {62,129,130}]
        recall=R.page_summary(random_results)
        result['source_row_recall']=dict(random=recall,stress=R.page_summary(stress),pages=pages,
            matching_tolerance_pdf_points=9,random_pages=random_pages)
        criteria=dict(crop_90=summary['row_crop_correctness']['success']>=72,
            number_90=summary['inscription_number_accuracy']['success']>=72,
            count_95=summary['drawn_unit_count_agreement']['success']>=76,
            top5_rows_80=summary['strict_top5']['whole_rows_all_sample']['success']>=64,
            random_page_recall_95=recall['recall']['rate'] is not None and recall['recall']['rate']>=.95)
    result['negative_result_criteria']=criteria
    result['pipeline_status']='Verified computation' if all(criteria.values()) else 'Failed'
    if bootstrap:
        rng=np.random.default_rng(20261008 if version=='v1' else 2026100781)
        sections={s:[i for i,p in enumerate(preds) if p.get('section')==s] for s in ['number_order','end_sorted','beginning_sorted']}
        boot=[]
        for _ in range(2000):
            sampled=[rows[i] for i in rng.integers(0,len(rows),len(rows))] if version=='v1' else [rows[j] for indices in sections.values() for j in rng.choice(indices,len(indices))]
            a=E.aggregate(sampled)
            boot.append([a['strict_top1']['aligned_recall']['rate'],a['strict_top5']['aligned_recall']['rate'],
                a['strict_top1']['same_position_equal_count']['rate'],a['strict_top5']['same_position_equal_count']['rate'],a['calibration']['brier'],a['calibration']['ece10']])
        names=['strict_top1_aligned_recall','strict_top5_aligned_recall','strict_top1_same_position_equal_count','strict_top5_same_position_equal_count','calibration_brier','calibration_ece10']
        quantile=np.quantile if version=='v1' else np.nanquantile
        result['row_bootstrap_95']={name:quantile(np.array(boot,dtype=float)[:,i],[.025,.975]).tolist() for i,name in enumerate(names)}
        if version=='v2':
            count_boot=[]
            for _ in range(2000):
                sampled=[random_results[i] for i in rng.integers(0,len(random_results),len(random_results))]
                a=R.page_summary(sampled);count_boot.append([a['recall']['rate'],a['precision']['rate']])
            result['source_row_recall']['random_page_bootstrap_ci95']=dict(recall=np.quantile(np.array(count_boot)[:,0],[.025,.975]).tolist(),precision=np.quantile(np.array(count_boot)[:,1],[.025,.975]).tolist())
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    base=Path(__file__).resolve().parent
    parser.add_argument('--release',type=Path,default=base.parent if base.name=='code' else base/'release')
    parser.add_argument('--benchmark',choices=['v1','v2'],required=True)
    parser.add_argument('--predictions',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--no-bootstrap',action='store_true')
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('Choose a new output file.')
    result=compute(args.release.resolve(),args.benchmark,args.predictions,not args.no_bootstrap)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(rows=result['summary']['rows'],pipeline_status=result['pipeline_status'],out=str(args.out))))

if __name__=='__main__':main()
