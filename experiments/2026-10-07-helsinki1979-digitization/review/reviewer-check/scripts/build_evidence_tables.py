"""Reviewer: record my independent source readings and unit-level adjudications as machine-readable tables.

The readings in READS and the verdicts in UNIT_VERDICTS were made by looking at renders of the unchanged PDF
(5x for rows, 6x for unit galleries, 14x for single digits) and at the chart atlas cells. They are the reviewer's own
visual judgments, recorded after the pipeline predictions and the reference were available; they are an audit of the
reference, not a second blind reference.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[3]
ROOT = HERE.parents[1]
OUT = Path(__file__).resolve().parents[1]

# sample_index: (units counted, printed number, classification string as read; note)
READS = {
    0: (6, '1097', '11 40', ''), 4: (3, '1238', '11 40', 'third unit is a hatched patch with dashed underline'),
    5: (5, '1251', '11 40', 'leading 1 of the number sits inside the pipeline glyph box'),
    13: (1, '1517', '43 77', 'horizontal-bar stack; pipeline box ends about 2 pt before its right end'),
    14: (4, '1582', '62 99', 'page 37 is upright in the PDF; pipeline rotated it'),
    15: (8, '1562', '69 98', 'page 37'), 16: (6, '1541', '11 40', 'page 37'),
    20: (6, '2247', '11 40', 'first unit carries a dashed underline'),
    24: (9, '2429', '11 40', 'ninth drawing lies beyond the pipeline box edge'),
    25: (4, '2559', '11 54', 'ticks at the top of the line; last hatched patch clipped by box'),
    29: (4, '2892', '11 90', 'fourth (hatched, underlined) drawing lies beyond the pipeline box edge'),
    30: (6, '3067', '11 40', 'ticks at the top of the line; second arrow and ticks merged by pipeline'),
    31: (6, '3100', '11 40', 'ticks at the top of the line'),
    33: (5, '3564', '79699', 'three-tick cluster lies beyond the pipeline box edge'),
    34: (5, '3601', '52647', 'read 62647 at 5x; 14x zoom shows 52647'),
    35: (9, '3671', '67671', 'first and last hatched patches are narrow'),
    36: (5, '3716', '91 99', 'third tick of the last drawing lies beyond the pipeline box edge'),
    37: (5, '3859', '75 90', 'all units editorial hatched patches; last patch clipped'),
    39: (5, '3878', '75699', ''), 40: (6, '3915', '67671', ''),
    41: (1, '3949', '11 96', 'double narrow hatched patch is one chart sign (code 762)'),
    42: (2, '4112', '11 40', 'leading 4 of the number sits inside the pipeline glyph box'),
    43: (5, '4149', '23 99', 'a tiny dot between units is not counted; last two drawings merged and clipped by pipeline'),
    44: (1, '4301', '11 91', ''), 49: (3, '6054', '11 40', 'previous row underline enters top of box; last drawing cut by box edge'),
    50: (1, '6079A', '51 90', 'previous row underline enters top of box'),
    51: (3, '6134', '23 99', 'a 0.4 pt sliver of the leading 6 lies inside the pipeline glyph box'),
    52: (7, '6153', '51 90', 'ticks at the top of the line'), 57: (3, '9102', '11 40', 'last drawing cut in half by pipeline box edge'),
    59: (8, '9905', '11 40', 'ticks at the top of the line'),
}

# (sample_index, pipeline unit) -> (verdict, mechanism, note)
R, P, N, I = 'reference_right', 'pipeline_right', 'neither_right', 'indeterminate'
UNIT_VERDICTS = {
    (0, 3): (R, 'position_twin', 'two ticks at line top = chart code 25; pipeline top-1 was 2, top-2 was 25'),
    (0, 5): (I, 'position_twin', 'single long stroke; codes 8 and 764 have the same tight shape'),
    (1, 3): (R, 'fine_variant', 'plain fish (177); pipeline chose 179 (fish with inner band)'),
    (2, 3): (R, 'fine_variant', 'fish with horizontal band (179); pipeline chose 178 (vertical inner line)'),
    (4, 2): (R, 'underline_omitted', 'hatched patch with dashed underline (106); pipeline box excludes the underline'),
    (5, 4): (R, 'fine_variant', 'fish with horizontal band (179); pipeline chose 178'),
    (6, 1): (R, 'underline_omitted', 'three ticks with dashed underline (199); pipeline box excludes the underline'),
    (7, 3): (I, 'position_twin', 'single long stroke; codes 8 and 764'),
    (7, 4): (I, 'fine_variant', 'U with outward ticks; 204 and 205 differ by a short centre mark; reference plausible'),
    (10, 4): (P, 'reference_error', 'four ticks over three = chart code 19; reference has 17 (three over two)'),
    (13, 0): (R, 'right_edge_clipped', 'bar stack clipped at the right end; pipeline top-1 was a grid'),
    (17, 2): (R, 'fine_variant', 'triangle with horizontal bars only (104); pipeline chose 103 (bars plus centre line)'),
    (18, 3): (R, 'position_twin', 'two ticks at line top = chart code 25'),
    (19, 0): (I, 'fine_variant', 'figure with two circles; 144 and 586 are neighbouring variants; reference plausible'),
    (20, 0): (R, 'underline_omitted', 'U with dashed underline (526); pipeline box excludes the underline'),
    (21, 6): (R, 'underline_omitted', 'hatched square with dashed underline (106)'),
    (23, 1): (I, 'position_twin', 'standing figure; codes 133 and 394 look identical in the chart cells'),
    (24, 3): (R, 'fine_variant', 'plain fish (177); pipeline chose 179'),
    (25, 0): (P, 'reference_error', 'two ticks at line top = chart code 25 (pipeline top-1); reference has 2'),
    (25, 3): (R, 'right_edge_clipped', 'narrow hatched patch cut by the box edge'),
    (27, 2): (R, 'underline_omitted', 'fish with inner vertical line and dashed underline (461); pipeline chose 179'),
    (27, 5): (I, 'fine_variant', 'narrow hatched patch; 597 versus 598'),
    (28, 1): (R, 'margin_leakage', 'four ticks (code 4) merged with leading digits of the printed number inside the box'),
    (29, 0): (R, 'underline_omitted', 'U with dashed underline (526)'),
    (30, 2): (R, 'merged_units', 'second arrow merged with the tick pair; reference 82 is the arrow'),
    (30, 4): (R, 'merged_units', 'trident-U with crossbar and underline (523); pipeline unit covers part of it'),
    (34, 1): (R, 'neighbor_row_ink', 'plain U (246); ticks from the row above enter the box top'),
    (35, 2): (P, 'reference_error', 'narrow hatched patch (597); reference has wide patch 599'),
    (35, 5): (R, 'underline_omitted', 'hooked stroke with underline (306)'),
    (35, 6): (R, 'underline_omitted', 'creature with underline (460)'),
    (35, 8): (N, 'reference_error', 'narrow hatched patch with underline = 13; reference has 106 (wide), pipeline 597 (no underline)'),
    (36, 3): (R, 'fine_variant', 'plain fish (177); pipeline chose 179'),
    (36, 4): (R, 'right_edge_clipped', 'three ticks, third lies beyond the box'),
    (37, 4): (R, 'right_edge_clipped', 'narrow hatched patch cut by the box edge'),
    (41, 0): (R, 'split_unit', 'double narrow hatched patch is chart code 762; pipeline split it in two'),
    (43, 3): (R, 'merged_units', 'ladder box merged with the small square and clipped'),
    (47, 0): (I, 'position_twin', 'standing figure; codes 133 and 394'),
    (48, 0): (I, 'fine_variant', 'figure with circles and triangular top; reference 244 plausible'),
    (49, 3): (R, 'right_edge_clipped', 'fish cut in half by the box edge'),
    (52, 1): (R, 'fine_variant', 'plain fish (177); pipeline chose 178'),
    (53, 3): (R, 'underline_omitted', 'hooked stroke with underline (469)'),
    (53, 4): (R, 'underline_omitted', 'X with underline (507)'),
    (55, 0): (R, 'right_edge_clipped', 'bar stack clipped; pipeline chose hatched'),
    (56, 0): (R, 'hatched_sign', 'hatched patch with a question-mark sign inside (596); pipeline chose plain hatched 599'),
    (56, 1): (I, 'fine_variant', 'tick cluster; reference 16 plausible'),
    (57, 2): (R, 'right_edge_clipped', 'creature cut in half by the box edge'),
}

metrics = {r['sample_index']: r for r in json.loads((HERE / 'evaluation/2026-10-07-frozen-v1/metrics.json').read_text())['rows']}
reads = []
for i, (n, num, cls, note) in sorted(READS.items()):
    m = metrics[i]
    reads.append(dict(sample_index=i, pdf_page=m['pdf_page'], my_units=n, my_number=num, my_classification=cls,
                      reference_units=m['reference_count'], reference_number=m['reference_inscription_number'], reference_classification=m['reference_classification'],
                      pipeline_units=m['predicted_count'], pipeline_number=m['predicted_inscription_number'], pipeline_classification=m['predicted_classification'],
                      reference_agrees_units=n == m['reference_count'], reference_agrees_number=num == m['reference_inscription_number'],
                      reference_agrees_classification=cls == m['reference_classification'],
                      pipeline_agrees_units=n == m['predicted_count'], pipeline_agrees_number=num == m['predicted_inscription_number'],
                      note=note))
summary = dict(rows_read=len(reads), units_reference_agrees=sum(r['reference_agrees_units'] for r in reads),
               number_reference_agrees=sum(r['reference_agrees_number'] for r in reads),
               classification_reference_agrees=sum(r['reference_agrees_classification'] for r in reads),
               units_pipeline_agrees=sum(r['pipeline_agrees_units'] for r in reads), number_pipeline_agrees=sum(r['pipeline_agrees_number'] for r in reads))
(OUT / 'independent-rereads.json').write_text(json.dumps(dict(summary=summary, rows=reads), indent=1), encoding='utf-8')
print(json.dumps(summary))

units = []
pairs = json.loads((OUT / 'diagnosis/gallery-top1-index.json').read_text())  # written by gallery.py --mode top1
tally = {}
for p in pairs:
    key = (p['sample_index'], p['pred_unit'])
    verdict, mech, note = UNIT_VERDICTS[key]
    units.append(dict(sample_index=p['sample_index'], pipeline_unit=p['pred_unit'], reference_unit=p['ref_unit'], reference_codes=p['ref_codes'],
                      pipeline_top2=p['pred_top2'], verdict=verdict, mechanism=mech, note=note))
    tally[verdict] = tally.get(verdict, 0) + 1
assert len(units) == len(UNIT_VERDICTS) == 46
mech = {}
for u in units:
    mech[u['mechanism']] = mech.get(u['mechanism'], 0) + 1
(OUT / 'unit-adjudication.json').write_text(json.dumps(dict(
    scope='46 aligned (pipeline unit, reference unit) pairs, page-37 rows excluded, where the pipeline top-1 candidate set does not intersect the strict reference set',
    verdict_counts=tally, mechanism_counts=mech, units=units), indent=1), encoding='utf-8')
print(tally)
print(mech)
