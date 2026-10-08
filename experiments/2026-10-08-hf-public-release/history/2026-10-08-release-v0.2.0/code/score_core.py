"""Score frozen predictions against independent visual candidate-set references."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np




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


