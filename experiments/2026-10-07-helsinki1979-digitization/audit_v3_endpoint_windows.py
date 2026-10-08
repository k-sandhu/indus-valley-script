"""Preserve post-prediction visual observations; never edit source references."""
from pathlib import Path
import argparse
import json
import record_repaired_endpoint as R

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-endpoint-inspection-v1'
DEFAULT = HERE / 'repair/2026-10-08-endpoint-record-v1/unit-window-audit.json'
OBSERVATIONS = {
    14: 'The first proposed window encloses the isolated ring/speck left of the two-column hatch. Both source readers treat that mark as a speck and the paired hatch as one unit 762; the proposal adds a spurious unit.',
    32: 'The eight windows cover seven drawings. The second window cuts the right end of the ruled compound; the last narrow window encloses only a detached underline dash to the right of the last fish. Underline association and cell bounds split the line incorrectly.',
    41: 'The final eight-tick group, one reference unit 492, is divided across three narrow proposed windows. The other five drawings have one window each, giving eight proposals instead of six.',
    60: 'The first window encloses a tiny isolated mark far left of the nine drawings. The reference excludes it; the proposal emits ten units.',
    65: 'The first window encloses two tiny isolated marks far left of the two three-stroke groups and three following drawings. The reference excludes the marks; the proposal emits six units instead of five.',
    68: 'A single proposed window contains both the curved unit 220 and the adjacent ruled compound 275. Their merger yields ten proposals for eleven reference drawings.',
    31: 'There are seven windows and seven reference drawings, but window 3 cuts the right arm and cell underline of the U. Window 4 starts inside that U and cuts the following fish; window 5 starts inside the preceding fish and cuts the next fish; window 6 starts inside that fish and extends through the final oval. Underline slots overlap drawing boundaries. The four resolved strict top-five misses at units 3–6 therefore begin at unit windows, despite equal counts.',
    3: 'The oval and slashed inner oval lie in a single complete window without an underline. The strict reference is empty because no card matches that drawing and underline state together. This is source/chart coverage uncertainty, not an observed unit-window failure.',
    35: 'The isolated high tick is in one window without an underline. Its strict set was emptied by adjudication after both readers chose 23. The empty strict set cannot score a compatible candidate.',
    70: 'The isolated high tick is in one window without an underline. Its strict set is empty because the chart does not match height, stroke continuity and underline state together.',
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, default=DEFAULT)
    ap.add_argument('--images', type=Path, default=RAW)
    ap.add_argument('--diagnosis', type=Path, default=HERE / 'repair/2026-10-08-endpoint-record-v1/diagnosis.json')
    args = ap.parse_args(); out = args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError('Use a fresh owned audit output')
    images = args.images.resolve()
    if not images.is_relative_to(ROOT / 'data/raw/2026-10-07-helsinki1979-digitization'):
        raise ValueError('Source overlays must be inside Package M local raw')
    d = R.read(args.diagnosis)
    p = d['incompatible_whole_row_partitions']['strict_top5']['sample_indices']
    assert p['unit_count'] == [14, 32, 41, 60, 65, 68]
    assert p['unit_candidates_count_consistent_proxy'] == [3, 31, 35, 70]
    cases = [dict(sample_index=i, observation=note,
                  source_overlay=(images / f'row_{i:03}.png').relative_to(ROOT).as_posix(),
                  overlay_sha256=R.sha(images / f'row_{i:03}.png')) for i, note in OBSERVATIONS.items()]
    result = dict(status='Exploratory', source='Post-outcome inspection by Package M of original-PDF raster overlays; predictions and references visible.',
                  source_pdf_sha256=R.sha(ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'),
                  code='inspect_v3_endpoint.py', observations=cases,
                  refined_top5_failed_rows=dict(crop=p['crop'],
                      segmentation_or_underline_association=p['unit_count']+[31],
                      unresolved_strict_reference=[3, 35, 70],
                      resolved_graphic_candidate_miss_on_an_inspected_correct_window=[]),
                  refined_top5_counts=dict(crop=8, segmentation_or_underline_association=7,
                                          unresolved_strict_reference=3, resolved_graphic_candidate_miss=0),
                  equal_count_resolved_top5_miss_units=[dict(sample_index=31, unit_index=i) for i in [3, 4, 5, 6]],
                  crop_tag_families=dict(neighbour_ink=[21, 44, 48, 55, 58, 66],
                                         drawing_cut=[30, 76, 77],
                                         own_underline_cut=[77], field_overlap=[76, 77]),
                  limitation='Visual review targets the failed top-five rows; it does not independently validate all boundaries of other equal-count rows or estimate an edition-wide error distribution.')
    assert sum(result['refined_top5_counts'].values()) == 18
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result['refined_top5_counts']))


if __name__ == '__main__':
    main()
