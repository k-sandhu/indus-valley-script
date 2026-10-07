"""Preserve a post-outcome visual inspection of residual unit windows."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
RUN=HERE/'repair/2026-10-07-v2'


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=HERE/'follow-up/2026-10-07/endpoint-record-v1/unit-window-audit.json')
    args=ap.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned audit file')
    refs={r['sample_index']:r for r in read(RUN/'blind/adjudicated-reference.json')['rows']}
    pred={r['sample_index']:r for r in read(RUN/'predictions.json')['rows']}
    metrics={r['sample_index']:r for r in read(RUN/'evaluation-2026-10-07-adjudicated/metrics.json')['rows']}
    unit_records=[]
    for i,j in ((25,1),(25,2),(25,3),(58,5),(72,1)):
        u=pred[i]['units'][j];r=refs[i]['units'][j]
        guesses={c for a in u['alternatives'][:5] for c in a['codes']}
        assert metrics[i]['crop_correct'] and metrics[i]['count_agrees']
        assert not guesses.intersection(r['strict_candidate_codes'])
        shape_match=bool(guesses.intersection(r['shape_only_candidate_codes']))
        record=dict(sample_index=i,unit_index=j,pdf_page=pred[i]['pdf_page'],
            exact_source=f'repair/2026-10-07-v2/blind/exact_{i:03d}.png',
            strict_reference=r['strict_candidate_codes'],shape_reference=r['shape_only_candidate_codes'],
            candidate_top5=sorted(guesses),bare_shape_compatible=shape_match,
            predicted_unit_x_bounds_2x=u['x_bounds'],predicted_unit_y_bounds_2x=u['y_bounds'],
            predicted_unit_width_pdf_points=(u['x_bounds'][1]-u['x_bounds'][0])/2,
            source_underline_observed=r['underline_dashes'],
            inspection='unit window truncates the full-width dashed underline' if shape_match else 'graphic proposal mismatch with a visibly complete figure',
            inspection_basis='Source exact image retains the full dashed sign slot. Frozen x window is narrower than the approximately 14-point underline; plain graphic appears among the proposals.' if shape_match else 'Source figure with pointed top and two circles is contained in the unit window; top-five candidates have no intersection with strict or shape-only reference.')
        record['source_sha256']=sha(HERE/record['exact_source']);unit_records.append(record)
    count_records=[]
    for i,observation in [(3,'Loss rectangle left vertical border is a separate proposed stroke; two units replace one rectangle.'),
        (50,'A left underline fragment below the single long stroke becomes an extra proposed short tick; eight units replace seven.'),
        (52,'The high single/pair tick is absorbed into the following diamond unit window; four units replace five.')]:
        r=metrics[i];assert r['crop_correct'] and not r['count_agrees']
        path=f'repair/2026-10-07-v2/blind/exact_{i:03d}.png'
        count_records.append(dict(sample_index=i,reference_count=r['reference_count'],predicted_count=r['predicted_count'],
            observation=observation,source=path,source_sha256=sha(HERE/path),
            predicted_unit_x_bounds_2x=[u['x_bounds'] for u in pred[i]['units']]))
    result=dict(status='Exploratory',date='2026-10-07',reader='Package M recording agent; predictions were visible',
        selection_rule='All five strict top-five same-position misses in accepted crops with matching counts, and all three accepted-crop count failures.',
        units=unit_records,count_failure_rows=count_records,
        refined_top5_incompatible_rows=dict(total=40,crop=34,unit_count_segmentation=3,
            unit_underline_window_association=2,graphic_proposal_classification=1),
        refined_top5_sample_indices=dict(unit_count_segmentation=[3,50,52],unit_underline_window_association=[25,58],graphic_proposal_classification=[72]),
        underlined_unit_misses=4,underlined_miss_rows=2,graphic_unit_misses=1,
        limitations='Post-outcome source/window inspection identifies repair targets. Other count-consistent units were not independently audited for complete geometry; no repaired accuracy was computed.',
        source_underline_width_witness='repair/2026-10-07-v2/blind/reader-b/rows-part1.json: notes, paragraph on 14.3-point dashed sign slots; exact source images independently viewed for these rows',
        code_sha256=sha(Path(__file__)))
    assert sum(result['refined_top5_incompatible_rows'][k] for k in ['crop','unit_count_segmentation','unit_underline_window_association','graphic_proposal_classification'])==40
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(result['refined_top5_incompatible_rows']))


if __name__=='__main__':main()
