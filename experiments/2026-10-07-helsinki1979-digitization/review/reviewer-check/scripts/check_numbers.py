"""Reviewer: compare every headline number in README.md and REPORT.md with the saved outputs.

Each check recomputes the value from primary inputs where possible (references, predictions, coverage, queues),
not from the package's own summary fields. Output: review/reviewer-check/numbers-check.json
"""
import json
import math
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[3]
ROOT = HERE.parents[1]
OUT = Path(__file__).resolve().parents[1]
metrics = json.loads((HERE / 'evaluation/2026-10-07-frozen-v1/metrics.json').read_text())
S = metrics['summary']
rows = metrics['rows']
cov = json.loads((HERE / 'runs/2026-10-07-full-v1/coverage.json').read_text())
refs = {}
for n in 'abc':
    for r in json.loads((HERE / f'blind/reference-{n}.json').read_text(encoding='utf-8'))['rows']:
        refs[r['sample_index']] = r
pred = {r['sample_index']: r for r in json.loads((ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json').read_text(encoding='utf-8'))['rows']}
sel = json.loads((HERE / 'blind/selection.json').read_text())
comp = json.loads((HERE / 'evaluation/annotation-comparison-v1.json').read_text())
rsum = json.loads((HERE / 'review/2026-10-07-v1/summary.json').read_text())
cal = json.loads((HERE / 'development/calibration.json').read_text())
dev = json.loads((HERE / 'development/page30_evaluation.json').read_text())
isum = json.loads((HERE / 'integration/2026-10-07-v1/summary.json').read_text())
ichk = json.loads((HERE / 'integration/l-interface-check-v1.json').read_text())


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


checks = []


def chk(claim, claimed, recomputed, source):
    ok = claimed == recomputed
    checks.append(dict(claim=claim, claimed=claimed, recomputed=recomputed, result='confirmed' if ok else 'discrepancy', source=source))


# independent recomputation from references and predictions
crop_true = sum(1 for r in refs.values() if r['crop_correct'])
count_ok = sum(1 for i, r in refs.items() if len(pred[i]['units']) == len(r['units']))
num_ok = sum(1 for i, r in refs.items() if pred[i].get('inscription_number') == str(r['printed_inscription_id']))
cls_ok = sum(1 for i, r in refs.items() if pred[i].get('classification_code') == r['classification_literal'])
chk('clean crops 23/60 (README, REPORT)', [23, 60], [crop_true, 60], 'blind/reference-*.json crop_correct')
chk('matching unit counts 33/60', [33, 60], [count_ok, 60], 'predictions vs references')
chk('exact inscription numbers 23/60', [23, 60], [num_ok, 60], 'predictions vs references')
chk('exact classification 19/60', [19, 60], [cls_ok, 60], 'predictions vs references')
chk('strict top-1 whole rows 13/60', [13, 60], [S['strict_top1']['whole_rows_all_sample']['success'], 60], 'metrics.json summary (evaluate.py recomputed byte-identical)')
chk('strict top-5 whole rows 24/60', [24, 60], [S['strict_top5']['whole_rows_all_sample']['success'], 60], 'metrics.json summary')
chk('unique exact sequence 10/52', [10, 52], [S['uniquely_resolved_exact_sequence']['success'], S['uniquely_resolved_exact_sequence']['total']], 'metrics.json summary')
chk('288 predicted vs 267 reference units', [288, 267], [sum(len(p['units']) for p in pred.values()), sum(len(r['units']) for r in refs.values())], 'predictions, references')
kinds = collections.Counter('glyph' if u.get('unit_kind') == 'glyph' else 'editorial' for r in refs.values() for u in r['units'])
chk('229 glyph + 38 editorial reference units', [229, 38], [kinds['glyph'], kinds['editorial']], 'reference unit_kind')
chk('eight reference units with two candidates', 8, sum(1 for r in refs.values() for u in r['units'] if len(u['strict_candidate_codes']) > 1), 'reference strict_candidate_codes')
chk('52 rows with singleton codes throughout', 52, sum(1 for r in refs.values() if all(len(u['strict_candidate_codes']) == 1 for u in r['units'])), 'reference strict_candidate_codes')
for name, k, n, claimed in [('crop 23/60 CI 27.1-51.0', 23, 60, [27.1, 51.0]), ('count 33/60 CI 42.5-66.9', 33, 60, [42.5, 66.9]),
                            ('classification 19/60 CI 21.3-44.2', 19, 60, [21.3, 44.2]), ('top-1 13/60 CI 13.1-33.6', 13, 60, [13.1, 33.6]),
                            ('top-5 24/60 CI 28.6-52.6', 24, 60, [28.6, 52.6]), ('unique 10/52 CI 10.8-31.9', 10, 52, [10.8, 31.9]),
                            ('13/38 number CI 21.2-50.1', 13, 38, [21.2, 50.1])]:
    chk('Wilson interval ' + name, claimed, wilson(k, n), 'closed-form Wilson 95%')
ra = S['strict_top1']['aligned_recall']
chk('aligned recall top-1 199/267, top-5 224/267', [199, 224, 267], [ra['correct'], S['strict_top5']['aligned_recall']['correct'], ra['total']], 'metrics.json summary')
chk('summed edits 95 and 71', [95, 71], [S['strict_top1']['summed_candidate_set_edits'], S['strict_top5']['summed_candidate_set_edits']], 'metrics.json summary')
chk('same-position 103/140 and 118/140', [103, 118, 140], [S['strict_top1']['same_position_equal_count']['correct'], S['strict_top5']['same_position_equal_count']['correct'], S['strict_top1']['same_position_equal_count']['total']], 'metrics.json summary')
chk('relaxed shape-only whole rows 15/60 and 25/60', [15, 25], [S['shape_only_top1']['whole_rows_all_sample']['success'], S['shape_only_top5']['whole_rows_all_sample']['success']], 'metrics.json summary')
chk('top-5 mean width 5.208, max 8', [5.208, 8], [round(S['strict_top5']['candidate_width_mean'], 3), S['strict_top5']['candidate_width_max']], 'metrics.json summary')
b = metrics['row_bootstrap_95']
chk('bootstrap CI aligned recall 66.3-81.7 and 76.0-90.6', [[66.3, 81.7], [76.0, 90.6]],
    [[round(100 * x, 1) for x in b['strict_top1_aligned_recall']], [round(100 * x, 1) for x in b['strict_top5_aligned_recall']]], 'metrics.json row_bootstrap_95')
chk('same-position CI 58.4-85.3 and 68.7-95.7', [[58.4, 85.3], [68.7, 95.7]],
    [[round(100 * x, 1) for x in b['strict_top1_same_position_equal_count']], [round(100 * x, 1) for x in b['strict_top5_same_position_equal_count']]], 'metrics.json row_bootstrap_95')
chk('Brier 0.1488 CI 0.107-0.197; ECE10 0.1056 CI 0.080-0.185', [0.1488, [0.107, 0.197], 0.1056, [0.08, 0.185]],
    [round(S['calibration']['brier'], 4), [round(x, 3) for x in b['calibration_brier']], round(S['calibration']['ece10'], 4), [round(x, 3) for x in b['calibration_ece10']]], 'metrics.json')
chk('calibration on 140 resolved same-position units', 140, S['calibration']['n'], 'metrics.json')
ex = metrics['exploratory_sensitivities']['excluding_original_ocr_locator_witness_rows']
chk('number accuracy excluding 22 OCR-exposed rows: 13/38', [13, 38], [ex['inscription_number_accuracy']['success'], ex['inscription_number_accuracy']['total']], 'metrics.json exploratory_sensitivities')
chk('22 rows with original OCR witnesses', 22, sum(1 for r in sel['rows'] if r.get('ocr_number_witnesses')), 'blind/selection.json')
chk('3,460 frame rows; 60 rows from 33 pages', [3460, 33], [sel['frame_rows'], len({r['pdf_page'] for r in sel['rows']})], 'blind/selection.json')
chk('repeat readings: 6 counts, 6 numbers, 6 classes, 4 identical sets, 4 crop disagreements',
    [6, 6, 6, 4, 4], [comp['matching_counts'], comp['matching_numbers'], comp['matching_classifications'], comp['identical_candidate_set_rows'],
                      sum(1 for r in comp['rows'] if r['primary_crop_correct'] != r['repeat_crop_correct'])], 'annotation-comparison-v1.json')
c = cov['counts']
chk('full run 11,369 rows, 57,426 units, 159 pages, 10,425 numbers read, 3 unmatched', [11369, 57426, 159, 10425, 3],
    [c['printed_rows'], c['drawn_unit_candidates'], len(cov['pages']), c['numbers_read'], c['unmatched_units']], 'coverage.json')
secs = collections.Counter()
for p in cov['pages']:
    secs['number_order' if p['pdf_page'] <= 78 else ('end_sorted' if p['pdf_page'] <= 130 else 'beginning_sorted')] += p['rows']
chk('section totals 4,036 / 3,743 / 3,590', [4036, 3743, 3590], [secs['number_order'], secs['end_sorted'], secs['beginning_sorted']], 'coverage.json pages')
chk('17 pages rotated 180 degrees', 17, sum(1 for p in cov['pages'] if p['layout']['rotation'] == 180), 'coverage.json pages')
chk('full run 52.1 minutes', 52.1, round(cov['seconds'] / 60, 1), 'coverage.json seconds')
chk('priority queue 946 / 9,712 / 711', [946, 9712, 711], [rsum['counts']['priority_0'], rsum['counts']['priority_1'], rsum['counts']['priority_2']], 'review/2026-10-07-v1/summary.json')
chk('490 nonincreasing within-column number pairs', 490, rsum['number_order_nonincreasing_pairs'], 'review summary')
chk('calibration fit: 81 development positions, 61 correct', [81, 61], [cal['examples'], cal['correct']], 'development/calibration.json')
chk('page-30 development: 17/20 counts, 6/20 top-1, 12/20 top-5', [17, 6, 12], [dev['correct_counts'], dev['top1_rows'], dev['top5_rows']], 'development/page30_evaluation.json')
chk('import staging: 11,369 quarantined, 944 unresolved numbers', [11369, 944], [isum['counts']['quarantine'], isum['counts']['printed_number_unresolved']], 'integration summary')
chk('interface exercise: 0 accepted, 60 quarantined', [0, 60], [ichk['accepted'], ichk['quarantined']], 'l-interface-check-v1.json')

# live recount of the large payloads
n_rows = n_units = n_num = n_unmatched = 0
pages = set()
sections = collections.Counter()
quar = collections.Counter()
with (HERE / 'runs/2026-10-07-full-v1/occurrences.jsonl').open(encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        n_rows += 1
        n_units += len(r['units'])
        n_num += r['inscription_number'] is not None
        n_unmatched += sum(not u['alternatives'] for u in r['units'])
        pages.add(r['pdf_page'])
        quar[r.get('status')] += 1
chk('occurrences.jsonl recount: rows, units, numbers read, unmatched, pages', [11369, 57426, 10425, 3, 159], [n_rows, n_units, n_num, n_unmatched, len(pages)], 'runs/2026-10-07-full-v1/occurrences.jsonl')
n_staged = 0
disp = collections.Counter()
review_status = collections.Counter()
rights = collections.Counter()
with (HERE / 'integration/2026-10-07-v1/ledger-import.jsonl').open(encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        n_staged += 1
        disp[r['disposition']] += 1
        review_status[r['review_status']] += 1
        rights[json.dumps(r['rights'], sort_keys=True)] += 1
chk('ledger-import.jsonl: 11,369 rows, all quarantine', [11369, {'quarantine': 11369}], [n_staged, dict(disp)], 'integration/2026-10-07-v1/ledger-import.jsonl')
res = dict(n_checks=len(checks), n_confirmed=sum(1 for c in checks if c['result'] == 'confirmed'), n_discrepancy=sum(1 for c in checks if c['result'] != 'confirmed'),
           review_status_values=dict(review_status), rights_variants=len(rights), rights_example=json.loads(next(iter(rights))), checks=checks)
(OUT / 'numbers-check.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(json.dumps({k: v for k, v in res.items() if k != 'checks'}, indent=1))
for ch in checks:
    if ch['result'] != 'confirmed':
        print('DISCREPANCY', ch)
