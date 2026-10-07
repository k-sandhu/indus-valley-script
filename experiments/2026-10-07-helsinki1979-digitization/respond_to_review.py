"""Compact coordinator corrections; preserve every first-endpoint file."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import evaluate as E

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-07-helsinki1979-digitization'
REVIEW=HERE/'review/reviewer-check'
PORTABLE=HERE/'portable-inputs'


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):digest.update(part)
    return digest.hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=HERE/'follow-up/2026-10-07/analysis-v1')
    args=parser.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Choose a new owned output directory')
    out.mkdir(parents=True)
    frozen_paths=['pipeline.py','evaluate.py','freeze-manifest.json','prediction-freeze.json',
                  'chart-snapshot.json','development/digits.npz','development/classifier.pt',
                  'development/calibration.json','blind/selection.json',
                  'evaluation/2026-10-07-frozen-v1/metrics.json','evaluation/annotation-comparison-v1.json',
                  'runs/2026-10-07-full-v1/occurrences.jsonl','runs/2026-10-07-full-v1/coverage.json',
                  'runs/2026-10-07-full-v1/review-queue.jsonl',
                  'integration/2026-10-07-v1/ledger-import.jsonl',
                  'review/2026-10-07-v1/priority-queue.jsonl']
    frozen_paths += [f'blind/reference-{c}{suffix}.json' for c in 'abc' for suffix in ('','-repeat')]
    before={p:sha(HERE/p) for p in frozen_paths}
    freeze=read(HERE/'prediction-freeze.json');original=ROOT/freeze['predictions_path']
    assert sha(original)==freeze['predictions_sha256']
    destination=PORTABLE/freeze['predictions_path']
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():assert sha(destination)==sha(original)
    else:shutil.copyfile(original,destination)
    selection=read(HERE/'blind/selection.json')
    assets=[HERE/'development/digits.npz',destination]
    assets += [HERE/'blind'/r['source_crop'] for r in selection['rows']]
    assets += sorted((HERE/'blind/chart_sheets').glob('*.png'))
    assert len(selection['rows'])==60 and len(list((HERE/'blind/chart_sheets').glob('*.png')))==9
    asset_manifest=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)) for p in assets]
    write(out/'portable-input-manifest.json',dict(status='Verified computation',assets=asset_manifest,
         attribution='Kimmo Koskenniemi and Asko Parpola (1979), Corpus of Texts in the Indus Script, University of Helsinki',
         source_url='http://hdl.handle.net/10138/342677',license='CC-BY-4.0',
         modifications='source cropping, chart sheets, numerical recognition and independent source annotation',
         tracking_status='Prepared; coordinator must add the TRACK-EXCEPTIONS.txt paths before a clean checkout contains the ignored assets'))
    exceptions=[a['path'] for a in asset_manifest]
    exceptions += [str((HERE/'TRACK-EXCEPTIONS.txt').relative_to(ROOT)).replace('\\','/')]
    track=HERE/'TRACK-EXCEPTIONS.txt'
    existing=track.read_text(encoding='utf-8').splitlines() if track.exists() else []
    track.write_text('\n'.join(sorted(set(existing+exceptions)))+'\n',encoding='utf-8')
    write(out/'freeze-supplement.json',dict(status='Exploratory',recorded_utc=datetime.now(timezone.utc).isoformat(),
         original_freeze_sha256=sha(HERE/'freeze-manifest.json'),prediction_freeze_sha256=sha(HERE/'prediction-freeze.json'),
         evaluator_sha256=sha(HERE/'evaluate.py'),recorded_after_outcome=True,
         chronology_source='REVIEW.md: evaluator last written 2026-10-07 10:27:44 America/Toronto, before first reference at 10:31:48',
         chronology_limit='Retrospective hash supplement; no claim that this hash was in the original freeze',
         portable_prediction_path=str(destination.relative_to(ROOT)),predictions_sha256=sha(destination)))

    primary=[r for c in 'abc' for r in read(HERE/f'blind/reference-{c}.json')['rows']]
    refs={r['sample_index']:r for r in primary}
    metrics=read(HERE/'evaluation/2026-10-07-frozen-v1/metrics.json')
    cover=read(HERE/'runs/2026-10-07-full-v1/coverage.json')
    crop=read(REVIEW/'diagnosis/crop-audit-summary.json')
    full_review=read(REVIEW/'diagnosis/full-run-summary.json')
    rotated=set(full_review['rotated_pages'])
    frame=dict(sample_rows=60,pdf_pages=[31,79],detected_frame_rows=3460,
               full_detected_rows=11369,selected_sorted_section_rows=sum(r['pdf_page']>=79 for r in selection['rows']),
               scope='Numbered-section detected rows only; sorted-section accuracy and overall row recall were not measured')
    assert frame['selected_sorted_section_rows']==0
    per_annotator={c:dict(accepted=sum(r['crop_correct'] is True for r in primary if i<=r['sample_index']<i+20),rows=20)
                   for c,i in [('A',0),('B',20),('C',40)]}
    write(out/'crop-and-frame.json',dict(status='Exploratory',frame=frame,
        original_crop=E.wilson(23,60),per_annotator=per_annotator,
        objective_no_tolerance=E.wilson(crop['variants']['no_tolerance']['n_clean'],60),
        objective_one_point_tolerance=E.wilson(crop['variants']['ignore_crossings_under_1pt']['n_clean'],60),
        annotator_C_accepted_boxes_with_defects=dict(no_tolerance=11,one_point_tolerance=9),
        source='review/reviewer-check/diagnosis/crop-audit-summary.json: variants',
        audit_scope='Post-outcome edge and unmatched-fragment tests, with reference losses and known incorrect orientation'))
    changes=[dict(sample_index=10,unit_index_zero_based=4,old=[17],adjudicated=[19],reason='four ticks over three'),
             dict(sample_index=35,unit_index_zero_based=2,old=[599],adjudicated=[597],reason='narrow unmarked hatched patch'),
             dict(sample_index=35,unit_index_zero_based=8,old=[106],adjudicated=[13],reason='narrow underlined hatched patch')]
    for index in [24,25,30,31,34,51,52,59]:
        found=[i for i,u in enumerate(refs[index]['units']) if u['strict_candidate_codes']==[2]]
        assert len(found)==1
        changes.append(dict(sample_index=index,unit_index_zero_based=found[0],old=[2],adjudicated=[25],
                            reason='pair of short ticks at the top of the source line; chart position distinguishes code 25 from code 2'))
    for row in changes:
        assert refs[row['sample_index']]['units'][row['unit_index_zero_based']]['strict_candidate_codes']==row['old']
    write(out/'adjudication-overlay.json',dict(status='Exploratory',changes=changes,
        applied_to_frozen_reference=False,source='REVIEW.md: Independent readings of the disputed rows; unit-adjudication.json; diagnosis/tick-position-check.json',
        convention='Preserve vertical position in the chart sign box. Code 25 is the high tick pair; code 2 is centered. Tight crops alone cannot distinguish them.',
        repeat_selection=dict(indices=[5,13,30,35,42,51],rule='Fixed convenience indices, two from each 20-row primary group; no RNG or probability-sampling rule recorded',
          timing='Original protocol calls them prespecified before annotation; independent paragraph-level timing is unavailable',
          inferential_scope='Agreement estimates apply only to these six rows')))
    kept=[r for r in metrics['rows'] if r['pdf_page'] not in rotated]
    cal=E.calibration([p for r in kept for p in r['calibration_items']])
    rng=np.random.default_rng(2026100707);boot=[]
    for _ in range(2000):
        sampled=[kept[i] for i in rng.integers(0,len(kept),len(kept))]
        c=E.calibration([p for r in sampled for p in r['calibration_items']])
        boot.append([c['brier'],c['ece10']])
    write(out/'calibration-upright-only.json',dict(status='Exploratory',frame=frame,
        excluded_sample_indices=[r['sample_index'] for r in metrics['rows'] if r['pdf_page'] in rotated],
        included_rows=len(kept),calibration=cal,model_refitted=False,reference_adjudications_applied=False,
        bootstrap=dict(seed=2026100707,replicates=2000,unit='printed_row'),
        ci95=dict(brier=np.quantile(np.array(boot)[:,0],[.025,.975]).tolist(),ece10=np.quantile(np.array(boot)[:,1],[.025,.975]).tolist()),
        source_metric_sha256=sha(HERE/'evaluation/2026-10-07-frozen-v1/metrics.json')))

    short=[dict(pdf_page=p['pdf_page'],detected_rows=p['rows']) for p in cover['pages'] if p['rows']<72]
    write(out/'row-recall-evidence.json',dict(status='Exploratory',short_pages=short,
       source_count_coverage_page62_column0=E.wilson(21,36),
       page62_note='The review counted 36 printed rows and 21 detected rows. Count coverage is not a corpus-wide matched-row recall estimate.',
       complex_column_pages=[129,130],source_column_counts='five to eight columns, according to REVIEW.md',
       full_edition_row_recall=None,missing_true_row_denominator=True,
       source='REVIEW.md: Checked claims and row-recall diagnosis; original coverage.json',
       limit='Fewer than 72 detected rows identifies pages to inspect; it does not establish that every page should print 72 rows.'))
    cuts={r['key']:r for r in read(REVIEW/'diagnosis/boundary-cut-full.json')['results']}
    order=read(HERE/'review/2026-10-07-v1/number-order-check.json')['violations']
    order_keys={p[k] for p in order for k in ('previous','following')}
    rows=[];groups=defaultdict(list)
    with (HERE/'runs/2026-10-07-full-v1/occurrences.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line);rows.append(r)
            if r['inscription_number'] is not None:
                sequence=tuple(tuple(u['alternatives'][0]['codes']) if u['alternatives'] else () for u in r['units'])
                groups[r['inscription_number']].append((r['occurrence_key'],sequence))
    differing={key for group in groups.values() if len(group)>1 and len({seq for _,seq in group})>1 for key,_ in group}
    queue=[];orientation=[];reason_counts=Counter();priorities=Counter()
    for r in rows:
        key=r['occurrence_key'];page=r['pdf_page'];reasons=[]
        if page in rotated:
            reasons.append('orientation_unreliable')
            orientation.append(dict(occurrence_key=key,pdf_page=page,original_rotation=180,verified_source_orientation=0,flags=['orientation_unreliable']))
        if page in (129,130):reasons.append('column_layout_incomplete')
        if page==62:reasons.append('page_row_recall_incomplete')
        edge=('left' if r['margin_side']=='right' else 'right') if r['page_rotation']==180 else r['margin_side']
        if cuts[key][edge][0] and cuts[key][edge][1]>=1:reasons.append('margin_edge_ink_crossing_at_least_one_point')
        if any(cuts[key][side][0] and cuts[key][side][1]>=1 for side in ('top','bottom')):reasons.append('vertical_edge_ink_crossing_at_least_one_point')
        if r['units']:
            u=r['units'][-1] if r['margin_side']=='right' else r['units'][0]
            xb=u['x_bounds'];yb=u.get('y_bounds') or [0,0];width=r['glyph_xyxy_2x'][2]-r['glyph_xyxy_2x'][0]
            near=xb[1]>=width-8 if r['margin_side']=='right' else xb[0]<=8
            if near and xb[1]-xb[0]<=28 and yb[0]>=10:reasons.append('narrow_number_edge_unit')
        if any(not u['alternatives'] for u in r['units']):reasons.append('unmatched_ink')
        if r['inscription_number'] is None:reasons.append('number_unresolved')
        if r['classification_code'] is None:reasons.append('classification_unresolved')
        if key in order_keys:reasons.append('number_order_violation')
        if key in differing:reasons.append('unverified_repeat_candidate_disagreement')
        if not reasons:continue
        priority=0 if any(s in reasons for s in ('orientation_unreliable','column_layout_incomplete','page_row_recall_incomplete')) else (
            1 if any('edge' in s or s=='unmatched_ink' for s in reasons) else
            2 if any(s in reasons for s in ('number_unresolved','classification_unresolved','number_order_violation')) else 3)
        queue.append(dict(occurrence_key=key,pdf_page=page,inscription_number=r['inscription_number'],priority=priority,
                          reasons=reasons,review_crop_local=r['review_crop_local'],disposition='quarantine'))
        reason_counts.update(reasons);priorities[priority]+=1
    assert len(orientation)==1223 and len(queue)<11369
    queue.sort(key=lambda r:(r['priority'],r['pdf_page'],r['occurrence_key']))
    with (out/'triage-queue.jsonl').open('w',encoding='utf-8') as stream:
        for r in queue:stream.write(json.dumps(r)+'\n')
    write(out/'orientation-overlay.json',dict(status='Exploratory',source='REVIEW.md and diagnosis/full-run-summary.json: all 17 pages are upright',
        pages=sorted(rotated),affected_rows=len(orientation),rows=orientation,original_payload_modified=False))
    write(out/'triage-summary.json',dict(status='Exploratory',total_occurrences=11369,queued_rows=len(queue),
        not_in_triage=11369-len(queue),priorities=dict(priorities),reason_counts=dict(reason_counts),
        quarantined_rows=11369,eligible_for_release=0,
        queue_sha256=sha(out/'triage-queue.jsonl'),
        scope='Objective repair priority subset. Omission from triage does not validate a row or release it from quarantine. Repeat groups use unverified numbers.'))
    free=shutil.disk_usage('C:\\').free
    write(out/'storage-gate.json',dict(status='Verified computation',drive='C:',free_bytes=free,
        threshold_bytes=1_000_000_000,write_threshold_bytes=50_000_000,
        repair_status='Proposed; new freeze, blind sample, reference, evaluation and full rerun remain pending',
        stop_condition_active=free<1_000_000_000,
        reason='The planned new full payload exceeds 50 MB; compare recorded free_bytes with the threshold. No source witness was deleted.'))
    after={p:sha(HERE/p) for p in frozen_paths}
    write(out/'preservation-check.json',dict(status='Verified computation' if before==after else 'Failed',
        frozen_hashes=after,checks=dict(frozen_endpoint_bytes_unchanged=before==after,
        portable_prediction_bytes_exact=sha(destination)==freeze['predictions_sha256'],
        all_source_crop_hashes=all(sha(HERE/'blind'/r['source_crop'])==r['source_crop_sha256'] for r in selection['rows']),
        queue_is_subset=len(queue)<11369,all_rotated_occurrences_flagged=len(orientation)==1223)))
    print(json.dumps(dict(output=str(out.relative_to(ROOT)),triage_rows=len(queue),orientation_rows=len(orientation),
                         calibration_n=cal['n'],brier=cal['brier'],ece10=cal['ece10'],frozen_unchanged=before==after),indent=2))


if __name__=='__main__':main()
