"""Score frozen predictions against independent visual candidate-set references."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-07-helsinki1979-digitization'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wilson(success,total):
    if not total:return dict(success=success,total=total,rate=None,ci95=None)
    z=1.959963984540054;p=success/total;denom=1+z*z/total
    center=(p+z*z/(2*total))/denom
    delta=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/denom
    return dict(success=success,total=total,rate=p,ci95=[center-delta,center+delta])


def align(guess,truth):
    """Minimum candidate-set edits, maximize matches among minimum-edit paths."""
    n,m=len(guess),len(truth)
    dp=[[None]*(m+1) for _ in range(n+1)];dp[0][0]=(0,0,[])
    for i in range(n+1):
        for j in range(m+1):
            if i==j==0:continue
            options=[]
            if i:
                e,c,path=dp[i-1][j];options.append((e+1,c,path+[(i-1,None)]))
            if j:
                e,c,path=dp[i][j-1];options.append((e+1,c,path+[(None,j-1)]))
            if i and j:
                match=bool(guess[i-1]&truth[j-1]);e,c,path=dp[i-1][j-1]
                options.append((e+(not match),c+int(match),path+[(i-1,j-1)]))
            dp[i][j]=min(options,key=lambda z:(z[0],-z[1]))
    e,c,path=dp[n][m]
    return dict(edits=e,matches=c,alignment=path)


def calibration(items):
    if not items:return dict(n=0,brier=None,ece10=None,bins=[])
    a=np.array(items);p=a[:,0];y=a[:,1];bins=[];ece=0.
    for b in range(10):
        selected=(p>=b/10)&(p<(b+1)/10 if b<9 else p<=1)
        n=int(selected.sum())
        if n:
            confidence=float(p[selected].mean());accuracy=float(y[selected].mean())
            ece+=n/len(p)*abs(confidence-accuracy)
            bins.append(dict(lower=b/10,upper=(b+1)/10,n=n,mean_confidence=confidence,accuracy=accuracy))
        else:bins.append(dict(lower=b/10,upper=(b+1)/10,n=0,mean_confidence=None,accuracy=None))
    return dict(n=len(p),brier=float(np.mean((p-y)**2)),ece10=float(ece),bins=bins)


def score_row(pred,ref):
    units=ref.get('units',[])
    declared=ref.get('drawn_unit_count')
    if declared is not None:assert declared==len(units),f"Reference count inconsistent at {ref['sample_index']}"
    record=dict(sample_index=pred['sample_index'],occurrence_key=pred['occurrence_key'],pdf_page=pred['pdf_page'],
                reference_count=declared,predicted_count=len(pred['units']),
                count_agrees=declared==len(pred['units']) if declared is not None else None,
                crop_correct=ref.get('crop_correct'),reference_inscription_number=ref.get('printed_inscription_id'),
                predicted_inscription_number=pred.get('inscription_number'),reference_classification=ref.get('classification_literal'),
                predicted_classification=pred.get('classification_code'))
    record['number_correct']=None if ref.get('printed_inscription_id') is None else pred.get('inscription_number')==str(ref['printed_inscription_id'])
    record['classification_correct']=None if ref.get('classification_literal') is None else pred.get('classification_code')==ref['classification_literal']
    strict=[set(int(c) for c in u.get('strict_candidate_codes',[])) for u in units]
    shape=[set(int(c) for c in u.get('shape_only_candidate_codes',u.get('strict_candidate_codes',[]))) for u in units]
    record['reference_unresolved_units']=sum(not s for s in strict)
    record['reference_ambiguous_units']=sum(len(s)>1 for s in strict)
    record['reference_fully_resolved']=declared is not None and all(strict)
    record['reference_unique_sequence']=declared is not None and all(len(s)==1 for s in strict)
    record['calibration_items']=[]
    for kind,truth in [('strict',strict),('shape_only',shape)]:
        for k in (1,5):
            guesses=[{int(c) for a in u['alternatives'][:k] for c in a['codes']} for u in pred['units']]
            outcome=align(guesses,truth)
            prefix=f'{kind}_top{k}'
            record[prefix]=dict(edits=outcome['edits'],aligned_matches=outcome['matches'],
                 resolved_reference_units=sum(bool(t) for t in truth),
                 whole_row_compatible=declared is not None and all(truth) and outcome['edits']==0,
                 candidate_widths=[len(s) for s in guesses],
                 equal_count_position_correct=sum(bool(a&b) for a,b in zip(guesses,truth) if b) if record['count_agrees'] else None,
                 equal_count_position_total=sum(bool(t) for t in truth) if record['count_agrees'] else 0)
            if kind=='strict' and k==1:
                record['uniquely_resolved_exact_sequence']=record['reference_unique_sequence'] and all(len(s)==1 for s in guesses) and outcome['edits']==0
                if record['count_agrees']:
                    for u,a,b in zip(pred['units'],guesses,truth):
                        if not b or u.get('confidence') is None:continue
                        record['calibration_items'].append([u['confidence'],int(bool(a&b))])
    return record


def aggregate(rows):
    result=dict(rows=len(rows),reference_drawn_units=sum(r['reference_count'] or 0 for r in rows),
        predicted_drawn_units=sum(r['predicted_count'] for r in rows),
        reference_unresolved_units=sum(r['reference_unresolved_units'] for r in rows),
        reference_ambiguous_units=sum(r['reference_ambiguous_units'] for r in rows),
        reference_fully_resolved_rows=sum(r['reference_fully_resolved'] for r in rows),
        reference_unique_sequence_rows=sum(r['reference_unique_sequence'] for r in rows))
    for name,field in [('row_crop_correctness','crop_correct'),('drawn_unit_count_agreement','count_agrees'),
                       ('inscription_number_accuracy','number_correct'),('classification_exact_accuracy','classification_correct')]:
        scored=[r for r in rows if r[field] is not None]
        result[name]=wilson(sum(bool(r[field]) for r in scored),len(scored))
        result[name]['unscorable_rows']=len(rows)-len(scored)
    for kind in ('strict','shape_only'):
        for k in (1,5):
            key=f'{kind}_top{k}';outcomes=[r[key] for r in rows]
            resolved=sum(o['resolved_reference_units'] for o in outcomes);matches=sum(o['aligned_matches'] for o in outcomes)
            equal_total=sum(o['equal_count_position_total'] for o in outcomes)
            equal_correct=sum(o['equal_count_position_correct'] or 0 for o in outcomes)
            whole=sum(o['whole_row_compatible'] for o in outcomes);fully=[r for r in rows if r['reference_fully_resolved']]
            widths=[n for o in outcomes for n in o['candidate_widths']]
            result[key]=dict(whole_rows_all_sample=wilson(whole,len(rows)),
                whole_rows_fully_resolved_reference=wilson(sum(r[key]['whole_row_compatible'] for r in fully),len(fully)),
                summed_candidate_set_edits=sum(o['edits'] for o in outcomes),
                aligned_recall=dict(correct=matches,total=resolved,rate=matches/resolved if resolved else None),
                same_position_equal_count=dict(correct=equal_correct,total=equal_total,rate=equal_correct/equal_total if equal_total else None),
                candidate_width_mean=float(np.mean(widths)) if widths else None,candidate_width_max=max(widths,default=None))
    eligible=[r for r in rows if r['reference_unique_sequence']]
    result['uniquely_resolved_exact_sequence']=wilson(sum(r['uniquely_resolved_exact_sequence'] for r in eligible),len(eligible))
    result['calibration']=calibration([x for r in rows for x in r['calibration_items']])
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(HERE/'evaluation/2026-10-07-frozen-v1'));args=ap.parse_args()
    out=Path(args.out)
    if out.exists():raise FileExistsError('Choose a new evaluation directory')
    pred_freeze=json.loads((HERE/'prediction-freeze.json').read_text())
    pred_path=ROOT/pred_freeze['predictions_path'];assert sha(pred_path)==pred_freeze['predictions_sha256']
    pred=json.loads(pred_path.read_text(encoding='utf-8'))
    references=[];hashes={}
    for name in ('reference-a.json','reference-b.json','reference-c.json'):
        path=HERE/'blind'/name;d=json.loads(path.read_text(encoding='utf-8'))
        references.extend(d['rows'] if isinstance(d,dict) else d);hashes[name]=sha(path)
    selection=json.loads((HERE/'blind/selection.json').read_text())
    selected={r['sample_index'] for r in selection['rows']}
    ids=[r['sample_index'] for r in references];assert len(ids)==len(set(ids))==60 and set(ids)==selected
    pids=[r['sample_index'] for r in pred['rows']];assert len(pids)==len(set(pids))==60 and set(pids)==selected
    refs={r['sample_index']:r for r in references}
    rows=[score_row(r,refs[r['sample_index']]) for r in pred['rows']]
    summary=aggregate(rows)
    original_ocr_rows={r['sample_index'] for r in selection['rows'] if r.get('ocr_number_witnesses')}
    sensitivities={
        'excluding_original_ocr_locator_witness_rows':aggregate([r for r in rows if r['sample_index'] not in original_ocr_rows]),
        'excluding_annotator_A':aggregate([r for r in rows if r['sample_index']>=20]),
        'source_confirmed_correct_crops_only':aggregate([r for r in rows if r['crop_correct'] is True]),
    }
    rng=np.random.default_rng(20261008);bootstrap=[]
    for _ in range(2000):
        picked=[rows[i] for i in rng.integers(0,len(rows),len(rows))]
        a=aggregate(picked)
        bootstrap.append([a['strict_top1']['aligned_recall']['rate'],a['strict_top5']['aligned_recall']['rate'],
                          a['strict_top1']['same_position_equal_count']['rate'],a['strict_top5']['same_position_equal_count']['rate'],
                          a['calibration']['brier'],a['calibration']['ece10']])
    names=['strict_top1_aligned_recall','strict_top5_aligned_recall','strict_top1_same_position_equal_count',
           'strict_top5_same_position_equal_count','calibration_brier','calibration_ece10']
    intervals={name:np.quantile(np.array(bootstrap,dtype=float)[:,i],[.025,.975]).tolist() for i,name in enumerate(names)}
    criteria=dict(crop_90=summary['row_crop_correctness']['rate'] is not None and summary['row_crop_correctness']['rate']>=.90,
                  number_90=summary['inscription_number_accuracy']['rate'] is not None and summary['inscription_number_accuracy']['rate']>=.90,
                  count_95=summary['drawn_unit_count_agreement']['rate'] is not None and summary['drawn_unit_count_agreement']['rate']>=.95,
                  top5_rows_80=summary['strict_top5']['whole_rows_all_sample']['rate']>=.80)
    out.mkdir(parents=True)
    result=dict(status='Frozen evaluation',pipeline_status='Verified computation' if all(criteria.values()) else 'Failed',
        reference_scope='Independent AI visual annotation, disjoint rows per annotator; no duplicate-annotator disagreement estimate',
        prediction_sha256=sha(pred_path),prediction_freeze_sha256=sha(HERE/'prediction-freeze.json'),
        freeze_manifest_sha256=sha(HERE/'freeze-manifest.json'),reference_sha256=hashes,evaluator_sha256=sha(__file__),
        reference_release='Predictions completed and hashed before GO messages to independent annotators',
        label_blinding=dict(original_ocr_locator_nonempty_rows=len(original_ocr_rows),
             exposed_locator_indices=sorted(original_ocr_rows),
             scope='Original PDF OCR fields were present in locator read by all three annotators; classifiers and glyph candidates withheld. See annotator notes.'),
        exploratory_sensitivities=sensitivities,
        summary=summary,row_bootstrap_95=intervals,bootstrap=dict(seed=20261008,replicates=2000,unit='printed_row'),
        negative_result_criteria=criteria,
        metric_definitions=dict(top_k='k image templates, each retaining chart numeric candidates',
          whole_row='same drawn count and each ordered candidate set intersects; unresolved reference prevents a pass',
          unique_sequence='all reference and top-one code sets singleton and equal; denominator unique-reference rows',
          aligned_recall='maximum compatible matches among minimum candidate-edit alignments divided by resolved reference units',
          same_position='compatible positions on equal-count rows only',
          calibration='candidate-set correctness on resolved same-position units in equal-count rows'),rows=rows)
    (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(summary=summary,criteria=criteria),indent=2))


if __name__=='__main__':main()
