"""Reviewer: attribute each failed row to pipeline stages (Exploratory, post-outcome).

Inputs: diagnosis.json (count-mismatch causes from alignment), unit-adjudication.json (reviewer verdicts on the 46 top-1
mismatches), boundary-cut-sample60.json (native-resolution edge test), metrics.json (frozen outcomes).
Stage order for the exclusive assignment: orientation, crop or field geometry (margin fragment, edge clipping,
neighbouring-row ink, underline excluded from the box), unit segmentation (merge or split), glyph classification.
A row can carry several causes; the 'any_cause' counts keep them.
"""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1]
diag = {r['sample_index']: r for r in json.loads((OUT / 'diagnosis/diagnosis.json').read_text())['rows']}
units = json.loads((OUT / 'unit-adjudication.json').read_text())['units']
cut = {r['sample_index']: r for r in json.loads((OUT / 'diagnosis/boundary-cut-sample60.json').read_text())['results']}
metrics = {r['sample_index']: r for r in json.loads((HERE / 'evaluation/2026-10-07-frozen-v1/metrics.json').read_text())['rows']}

GEOMETRY = {'underline_omitted', 'right_edge_clipped', 'margin_leakage', 'neighbor_row_ink'}
SEGMENTATION = {'merged_units', 'split_unit'}
CLASSIFICATION = {'position_twin', 'fine_variant', 'hatched_sign'}
unit_mech = collections.defaultdict(set)
for u in units:
    unit_mech[u['sample_index']].add(u['mechanism'])

rows = []
for i, m in sorted(metrics.items()):
    d = diag[i]
    causes = set()
    if d['rotated_page']:
        causes.add('orientation')
    kinds = [x['kind'] for x in d['inserted']]
    if 'margin_edge_fragment' in kinds or (not d['count_ok'] and any(x['pred_unit'] == d['pred_count'] - 1 and x['width'] <= 28 for x in d['inserted'])):
        causes.add('margin_field_fragment')
    if 'neighbor_row_ink_at_strip_edge' in kinds and not d['rotated_page']:
        causes.add('neighbor_row_ink')
    if d['deleted_ref_units'] and not d['inserted']:
        causes.add('right_edge_clipped_or_merged_unit_lost')
    for mech in unit_mech[i]:
        if mech in GEOMETRY:
            causes.add(mech)
        elif mech in SEGMENTATION:
            causes.add('segmentation:' + mech)
        elif mech in CLASSIFICATION:
            causes.add('classification:' + mech)
        elif mech == 'reference_error':
            causes.add('reference_error')
    rows.append(dict(sample_index=i, top5_whole_row=m['strict_top5']['whole_row_compatible'], count_ok=bool(m['count_agrees']),
                     number_ok=bool(m['number_correct']), causes=sorted(causes)))

fail5 = [r for r in rows if not r['top5_whole_row']]
order = [('orientation', lambda c: c == 'orientation'),
         ('crop_or_field_geometry', lambda c: c in {'margin_field_fragment', 'neighbor_row_ink', 'right_edge_clipped_or_merged_unit_lost', 'underline_omitted', 'right_edge_clipped', 'margin_leakage', 'neighbor_row_ink'}),
         ('unit_segmentation', lambda c: c.startswith('segmentation:')),
         ('glyph_classification_or_convention', lambda c: c.startswith('classification:') or c == 'reference_error')]
exclusive = collections.Counter()
any_cause = collections.Counter()
for r in fail5:
    first = None
    for name, test in order:
        if any(test(c) for c in r['causes']):
            if first is None:
                first = name
            any_cause[name] += 1
    exclusive[first or 'no_cause_found'] += 1
summary = dict(rows_failing_strict_top5=len(fail5), exclusive_first_stage=dict(exclusive), rows_with_any_cause=dict(any_cause),
               rows_without_cause=[r['sample_index'] for r in fail5 if not r['causes']])
num_fail = [r for r in rows if not r['number_ok']]
(OUT / 'diagnosis/stage-attribution.json').write_text(json.dumps(dict(summary=summary, rows=rows), indent=1), encoding='utf-8')
print(json.dumps(summary, indent=1))
for r in fail5:
    print(r['sample_index'], r['count_ok'], r['causes'])
