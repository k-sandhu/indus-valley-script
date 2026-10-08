"""Independent recomputation of the v3 headline numbers (reviewer script, read-only).

Reads the frozen packet, predictions, adjudicated reference/counts, reader files and the
per-row metrics; recomputes the counts quoted in README.md and REPORT.md without
importing the package's own scoring or diagnosis code (Wilson intervals are re-derived
here). Also computes sensitivity checks that the package does not report.
Writes JSON to the path given by --out (new file only).
"""
import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[1]
RUN = PKG / 'repair/2026-10-08-v3'
BL = RUN / 'blind'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit('output exists')
    m = read(RUN / 'evaluation-2026-10-08-adjudicated/metrics.json')
    rows = m['rows']
    sel = read(BL / 'selection.json')
    ref = read(BL / 'adjudicated-reference.json')['rows']
    pred = read(RUN / 'predictions.json')['rows']
    out = {}

    # 1. headline counts from per-row records
    crop = sum(r['crop_correct'] for r in rows)
    cnt = sum(r['count_agrees'] for r in rows)
    num = sum(r['number_correct'] for r in rows)
    cls = sum(r['classification_correct'] for r in rows)
    t1 = sum(r['strict_top1']['whole_row_compatible'] for r in rows)
    t5 = sum(r['strict_top5']['whole_row_compatible'] for r in rows)
    s1 = sum(r['shape_only_top1']['whole_row_compatible'] for r in rows)
    s5 = sum(r['shape_only_top5']['whole_row_compatible'] for r in rows)
    ex = [r for r in rows if r['reference_unique_sequence']]
    exact = sum(r['uniquely_resolved_exact_sequence'] for r in ex)
    resolved = [r for r in rows if r['reference_fully_resolved']]
    t5r = sum(r['strict_top5']['whole_row_compatible'] for r in resolved)
    out['headline'] = {k: dict(k=v[0], n=v[1], wilson95=wilson(*v)) for k, v in dict(
        crop=(crop, 80), count=(cnt, 80), number=(num, 80), classification=(cls, 80),
        strict_top1=(t1, 80), strict_top5=(t5, 80), shape_only_top1=(s1, 80), shape_only_top5=(s5, 80),
        exact_singleton=(exact, len(ex)), strict_top5_fully_resolved_reference=(t5r, len(resolved))).items()}
    out['criterion_thresholds_min_numerator'] = dict(crop=math.ceil(.9 * 80), number=math.ceil(.9 * 80),
                                                     count=math.ceil(.95 * 80), top5=math.ceil(.8 * 80))
    out['criterion_gaps'] = dict(crop=72 - crop, number=72 - num, count=76 - cnt, top5=64 - t5)
    # aligned unit recall
    a1 = sum(r['strict_top1']['aligned_matches'] for r in rows)
    a5 = sum(r['strict_top5']['aligned_matches'] for r in rows)
    den = sum(r['strict_top5']['resolved_reference_units'] for r in rows)
    out['aligned_unit_recall'] = dict(top1=[a1, den], top5=[a5, den])
    p1 = sum((r['strict_top1']['equal_count_position_correct'] or 0) for r in rows)
    p5 = sum((r['strict_top5']['equal_count_position_correct'] or 0) for r in rows)
    pd = sum((r['strict_top5']['equal_count_position_total'] or 0) for r in rows)
    out['equal_count_positional'] = dict(top1=[p1, pd], top5=[p5, pd])

    # 2. partitions
    def partition(key):
        fail = [r for r in rows if not r[key]['whole_row_compatible']]
        parts = defaultdict(list)
        for r in fail:
            if not r['crop_correct']:
                parts['crop'].append(r['sample_index'])
            elif not r['count_agrees']:
                parts['count'].append(r['sample_index'])
            else:
                parts['count_consistent'].append(r['sample_index'])
        return dict(total=len(fail), **{k: [len(v), v] for k, v in parts.items()})
    out['partition_top5'] = partition('strict_top5')
    out['partition_top1'] = partition('strict_top1')
    acc = [r for r in rows if r['crop_correct'] and r['count_agrees']]
    out['accepted_crop_equal_count'] = dict(
        rows=len(acc),
        top1=[sum((r['strict_top1']['equal_count_position_correct'] or 0) for r in acc), sum((r['strict_top1']['equal_count_position_total'] or 0) for r in acc)],
        top5=[sum((r['strict_top5']['equal_count_position_correct'] or 0) for r in acc), sum((r['strict_top5']['equal_count_position_total'] or 0) for r in acc)],
        top5_unit_miss_rows=sorted({r['sample_index'] for r in acc if (r['strict_top5']['equal_count_position_correct'] or 0) < (r['strict_top5']['equal_count_position_total'] or 0)}))
    out['wrong_fields'] = dict(
        number=[r['sample_index'] for r in rows if not r['number_correct']],
        classification=[r['sample_index'] for r in rows if not r['classification_correct']],
        crop_rejected=[r['sample_index'] for r in rows if not r['crop_correct']],
        count_wrong=[r['sample_index'] for r in rows if not r['count_agrees']])
    sec = {r['sample_index']: r['section'] for r in pred}
    pg = {r['sample_index']: r['pdf_page'] for r in pred}
    bysec = {}
    for s in ['number_order', 'end_sorted', 'beginning_sorted']:
        rr = [r for r in rows if sec[r['sample_index']] == s]
        bysec[s] = dict(n=len(rr), crop_fail=sum(not r['crop_correct'] for r in rr), count_fail=sum(not r['count_agrees'] for r in rr),
                        top5_fail=sum(not r['strict_top5']['whole_row_compatible'] for r in rr),
                        number_fail=sum(not r['number_correct'] for r in rr), cls_fail=sum(not r['classification_correct'] for r in rr))
    out['by_section'] = bysec
    out['crop_rejected_pages'] = {i: pg[i] for i in out['wrong_fields']['crop_rejected']}
    side = {r['sample_index']: r['margin_side'] for r in pred}
    out['margin_side_crop_rejected'] = dict(Counter(side[i] for i in out['wrong_fields']['crop_rejected']))
    out['margin_side_rows'] = dict(Counter(side.values()))
    out['parity_crop_rejected'] = dict(Counter('even' if pg[i] % 2 == 0 else 'odd' for i in out['wrong_fields']['crop_rejected']))
    out['parity_rows'] = dict(Counter('even' if p % 2 == 0 else 'odd' for p in pg.values()))

    # 3. calibration bin >= 0.9
    items = [x for r in rows for x in r['calibration_items']]
    hi = [x for x in items if x[0] >= 0.9]
    out['calibration_ge_0_9'] = dict(n=len(hi), top1_correct=sum(x[1] for x in hi), all_items=len(items))

    # 4. sample page structure
    pages_by_sec = defaultdict(list)
    for r in sel['rows']:
        pages_by_sec[r['section']].append(r['pdf_page'])
    out['sample_pages'] = {s: dict(rows=len(v), distinct_pages=len(set(v)), eligible_pages=len(sel['eligible_pages'][s]),
                                   max_rows_per_page=max(Counter(v).values())) for s, v in pages_by_sec.items()}
    out['eligible_pages_number_order'] = sel['eligible_pages']['number_order']

    # 5. overlap of the fresh count pages with development / earlier target pages
    first = read(PKG / 'blind/selection.json')['rows']
    v2 = read(PKG / 'repair/2026-10-07-v2/blind/selection.json')
    earlier_pages = {r['pdf_page'] for r in first} | {r['pdf_page'] for r in v2['rows']}
    dev_pages = {22, 25, 30, 37, 62, 78, 100, 129, 130, 145}
    old_count = set(v2['count_pages'])
    rc = set(sel['random_count_pages'])
    out['count_page_overlap'] = dict(random_count_pages=sorted(rc),
                                     overlap_with_earlier_recognition_target_pages=sorted(rc & earlier_pages),
                                     overlap_with_original_development_pages=sorted(rc & dev_pages),
                                     overlap_with_previous_count_pages=sorted(rc & old_count),
                                     overlap_with_v3_recognition_target_pages=sorted(rc & {r['pdf_page'] for r in sel['rows']}))

    # 6. reader agreement recomputed from raw files
    def reader_rows(r):
        d = {}
        for f in ['rows-part1', 'rows-part2']:
            for x in read(BL / f'reader-{r}/{f}.json')['rows']:
                d[x['sample_index']] = x
        return d
    A, B = reader_rows('a'), reader_rows('b')
    agree = dict(number=sum(A[i]['printed_inscription_id'] == B[i]['printed_inscription_id'] for i in range(80)),
                 classification=sum(A[i]['classification_literal'] == B[i]['classification_literal'] for i in range(80)),
                 unit_count=sum(A[i]['drawn_unit_count'] == B[i]['drawn_unit_count'] for i in range(80)),
                 crop=sum(A[i]['crop_correct'] == B[i]['crop_correct'] for i in range(80)))
    same = tot = 0
    dis = []
    for i in range(80):
        ua, ub = A[i]['units'], B[i]['units']
        for k, (x, y) in enumerate(zip(ua, ub)):
            tot += 1
            if sorted(x['strict_candidate_codes']) == sorted(y['strict_candidate_codes']):
                same += 1
            else:
                dis.append([i, k, x['strict_candidate_codes'], y['strict_candidate_codes']])
    out['reader_agreement'] = dict(agree, strict_sets=[same, tot], strict_disagreements=dis,
                                   crop_disagreement_rows=[i for i in range(80) if A[i]['crop_correct'] != B[i]['crop_correct']])
    # changes the adjudicator made to unit sets or crops relative to the agreed reader values
    changed = []
    for i in range(80):
        for k, u in enumerate(ref[i]['units']):
            a, b = sorted(A[i]['units'][k]['strict_candidate_codes']), sorted(B[i]['units'][k]['strict_candidate_codes'])
            c = sorted(u['strict_candidate_codes'])
            if a == b and c != a:
                changed.append([i, k, 'adjudicated differs from both agreeing readers', a, c])
    out['adjudicator_overrides_of_agreeing_readers'] = changed
    out['row_crop_adjudication'] = {i: dict(A=A[i]['crop_correct'], B=B[i]['crop_correct'], adjudicated=ref[i]['crop_correct'])
                                    for i in range(80) if not ref[i]['crop_correct'] or A[i]['crop_correct'] != B[i]['crop_correct']}

    # 7. sensitivity checks (post-outcome, not a rescoring)
    def codes(alts, n):
        s = set()
        for a in alts[:n]:
            s.update(a['codes'])
        return s
    sens = {}
    # (a) rows whose strict top-five failure is caused solely by an empty strict set
    only_empty = []
    for i, r in enumerate(rows):
        if r['strict_top5']['whole_row_compatible'] or not r['crop_correct'] or not r['count_agrees']:
            continue
        miss = []
        for k, (u, pu) in enumerate(zip(ref[i]['units'], pred[i]['units'])):
            s = set(u['strict_candidate_codes'])
            if not s:
                miss.append((k, 'empty', sorted(set(u['shape_only_candidate_codes']) & codes(pu['alternatives'], 5))))
            elif not (s & codes(pu['alternatives'], 5)):
                miss.append((k, 'resolved_miss', None))
        only_empty.append((i, miss))
    sens['accepted_crop_equal_count_top5_failures_unit_detail'] = only_empty
    sens['strict_top5_if_35_2_and_70_4_were_23'] = t5 + 2
    sens['crop_if_row21_accepted'] = crop + 1
    out['sensitivity'] = sens

    # 8. chart cells
    cells = ['20:4:1', '21:6:1', '20:4:13', '21:6:31']
    ch = {}
    union_units = set()
    for c in cells:
        refu = [(i, u['unit_index']) for i in range(80) for u in ref[i]['units'] if c in (u.get('chart_locations') or [])]
        t1u = [(i, k) for i, p in enumerate(pred) for k, u in enumerate(p['units']) if u['alternatives'] and u['alternatives'][0]['template_key'] == c]
        t5u = [(i, k) for i, p in enumerate(pred) for k, u in enumerate(p['units']) if any(a['template_key'] == c for a in u['alternatives'][:5])]
        union_units |= set(t5u)
        ch[c] = dict(reference_units=len(refu), reference=refu, top1_units=len(t1u), top5_units=len(t5u), top5=t5u)
    out['chart_cells'] = ch
    out['chart_top5_unique_units_across_cells'] = len(union_units)
    # reference units on those cells that are also top-5 matched (scored) -- all scored by shared label
    # notes search
    notes = json.dumps(read(BL / 'adjudication-notes.json'))
    out['notes_mentions'] = {c: len(re.findall(re.escape(c), notes)) for c in cells}
    # row 58 locator
    out['row58_unit0_reference_locations'] = ref[58]['units'][0]['chart_locations']
    out['row58_unit0_note'] = ref[58]['units'][0]['note'][:400]

    # 9. count pages
    cnt_ref = read(BL / 'adjudicated-counts.json')['pages']
    numbered = sum(c['row_count'] for p in cnt_ref for c in p['columns'])
    physical = sum(c['physical_line_count'] for p in cnt_ref for c in p['columns'])
    cols = sum(len(p['columns']) for p in cnt_ref)
    cont = {p['pdf_page']: sum(len(c['continuation_lines']) for c in p['columns']) for p in cnt_ref if any(c['continuation_lines'] for c in p['columns'])}
    rand = [p for p in cnt_ref if p['pdf_page'] in sel['random_count_pages']]
    out['count_reference'] = dict(pages=len(cnt_ref), columns=cols, numbered=numbered, physical=physical, continuation_pages=cont,
                                  random_numbered=sum(c['row_count'] for p in rand for c in p['columns']),
                                  random_physical=sum(c['physical_line_count'] for p in rand for c in p['columns']))
    # reader agreement on counts
    def cnt_pages(r):
        return {p['pdf_page']: [(c['row_count'], c['physical_line_count']) for c in p['columns']] for p in read(BL / f'reader-{r}/counts.json')['pages']}
    ca, cb = cnt_pages('a'), cnt_pages('b')
    out['count_reader_agreement'] = dict(pages_equal=sum(ca[p] == cb[p] for p in ca), pages=len(ca),
                                         numbered_a=sum(x for v in ca.values() for x, _ in v), numbered_b=sum(x for v in cb.values() for x, _ in v),
                                         physical_a=sum(y for v in ca.values() for _, y in v), physical_b=sum(y for v in cb.values() for _, y in v))

    # 10. full inventory (streams the local JSONL)
    full = read(RUN / 'full-summary.json')
    path = ROOT / full['path']
    n = units = numbered = cont_lines = quarantined = released = unresolved = 0
    pages = set()
    keys = set()
    dup = 0
    with path.open(encoding='utf-8') as fh:
        for line in fh:
            r = json.loads(line)
            n += 1
            units += len(r['units'])
            pages.add(r['pdf_page'])
            numbered += r['line_kind'] == 'numbered'
            cont_lines += r['line_kind'] == 'continuation'
            quarantined += bool(r['quarantined'])
            released += bool(r.get('released'))
            unresolved += sum(u['confidence'] is None for u in r['units'])
            if r['occurrence_key'] in keys:
                dup += 1
            keys.add(r['occurrence_key'])
    out['full_inventory_recomputed'] = dict(records=n, numbered=numbered, continuation=cont_lines, units=units, pages=len(pages),
                                            page_min=min(pages), page_max=max(pages), quarantined=quarantined, released=released,
                                            unresolved_units=unresolved, duplicate_keys=dup, bytes=path.stat().st_size)
    out['full_summary_fields'] = {k: full.get(k) for k in ['rows', 'numbered_occurrences', 'continuation_lines', 'units', 'pages',
                                                         'nonfinite_units_unresolved', 'released_rows', 'bytes', 'sha256']}
    args.out.write_text(json.dumps(out, indent=1, default=str), encoding='utf-8')
    print(json.dumps(out, indent=1, default=str))


if __name__ == '__main__':
    main()
