"""Record the coordinator's unchanged v3 endpoint; no inference or references."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
import shutil

import record_repaired_endpoint as R

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = HERE / 'repair/2026-10-08-v3'
DEFAULT = HERE / 'repair/2026-10-08-endpoint-record-v1'
CELL_DIFFERENCES = {'20:4:1': (506, 508), '21:6:1': (206, 208),
                    '20:4:13': (360, 350), '21:6:31': (285, 286)}


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False) + '\n', encoding='utf-8')


def frozen_paths():
    paths = []
    for p, h in R.read(RUN / 'freeze-manifest.json')['code_hashes'].items():
        assert R.sha(HERE / p) == h, p
        paths.append(HERE / p)
    for directory in [RUN / 'blind', RUN / 'evaluation-2026-10-08-adjudicated',
                      HERE / 'repair/2026-10-07-v2', HERE / 'blind',
                      HERE / 'evaluation/2026-10-07-frozen-v1']:
        paths.extend(p for p in directory.rglob('*') if p.is_file())
    for name in ['freeze-manifest.json', 'prediction-freeze.json', 'predictions.json',
                 'frame.json', 'count-page-detections.json', 'full-summary.json',
                 'full-transport-manifest.json']:
        paths.append(RUN / name)
    old = R.read(HERE / 'follow-up/2026-10-07/endpoint-record-v1/preservation-check.json')
    paths.extend(HERE / p for p in old['hashes'])
    paths.append(HERE / 'freeze-manifest.json')
    return sorted(set(p for p in paths if p.is_file()))


def canonical_lines(row):
    # Readers use line_index=0 or line=1 for the same source-first line.
    return [(x.get('kind', x.get('line_kind')),
             x['unit_count'] if 'unit_count' in x else len(x['unit_orders']))
            for x in row['physical_lines']]


def chart_locator_observation():
    paths = [RUN / 'blind/exact_058.png',
             ROOT / 'output/chart_atlas/cells/p20_c4_r1.png',
             ROOT / 'output/chart_atlas/cells/p21_c7_r5.png']
    return dict(status='Exploratory', sample_index=58, unit_index=0,
                method='Post-outcome visual comparison of the frozen exact crop and existing original-PDF atlas crops, with predictions/reference visible.',
                observation='The first drawing in exact_058 is two overlapping circles with corner ticks, matching cell21:7:5. Cell20:4:1 is a branched stem. The source comparison supports the reference locator21:7:5 and identifies the prose-notes locator20:4:1 as inconsistent with this drawing.',
                source_hashes={p.relative_to(ROOT).as_posix(): R.sha(p) for p in paths},
                action='Preserve both frozen witnesses and scored code506. Package N should independently confirm the cell identity before applying a future mapping; no chart or reference edited.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=DEFAULT)
    args = ap.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError('Use a fresh output directory inside Package M')
    before = {p.relative_to(HERE).as_posix(): R.sha(p) for p in frozen_paths()}
    m = R.read(RUN / 'evaluation-2026-10-08-adjudicated/metrics.json')
    sel = R.read(RUN / 'blind/selection.json')
    refs = {r['sample_index']: r for r in R.read(RUN / 'blind/adjudicated-reference.json')['rows']}
    ps = {r['sample_index']: r for r in R.read(RUN / 'predictions.json')['rows']}
    rows = m['rows']
    assert len(rows) == 80 and sorted(refs) == list(range(80))
    for field, path in [('freeze_sha256', RUN / 'freeze-manifest.json'),
                        ('prediction_sha256', RUN / 'predictions.json'),
                        ('reference_sha256', RUN / 'blind/adjudicated-reference.json'),
                        ('count_reference_sha256', RUN / 'blind/adjudicated-counts.json'),
                        ('evaluator_sha256', HERE / 'evaluate_crop_v3.py')]:
        assert m[field] == R.sha(path), field
    pf = R.read(RUN / 'prediction-freeze.json')
    for file, key in [('predictions.json', 'prediction_sha256'),
                      ('blind/selection.json', 'selection_sha256'),
                      ('count-page-detections.json', 'count_detections_sha256')]:
        assert R.sha(RUN / file) == pf[key]
    assert R.sha(RUN / 'freeze-manifest.json') == pf['freeze_sha256']
    for p, h in pf['packet_hashes'].items():
        assert R.sha(RUN / 'blind' / p) == h, p

    predicates = {
        'crop_rejected': lambda r: not r['crop_correct'],
        'count_wrong_after_accepted_crop': lambda r: r['crop_correct'] and not r['count_agrees'],
        'count_consistent_accepted_crop': lambda r: r['crop_correct'] and r['count_agrees'],
        'number_wrong': lambda r: not r['number_correct'],
        'classification_field_wrong': lambda r: not r['classification_correct'],
        'either_field_wrong': lambda r: not (r['number_correct'] and r['classification_correct']),
        'number_wrong_after_crop_and_count': lambda r: r['crop_correct'] and r['count_agrees'] and not r['number_correct'],
        'classification_field_wrong_after_crop_and_count': lambda r: r['crop_correct'] and r['count_agrees'] and not r['classification_correct'],
        'empty_strict_reference': lambda r: r['reference_unresolved_units'] > 0,
    }
    subsets = {k: dict(count=len(ids := R.indices(rows, p)), sample_indices=ids)
               for k, p in predicates.items()}
    partitions = {}
    for name in ['strict_top1', 'strict_top5']:
        failed = [r for r in rows if not r[name]['whole_row_compatible']]
        parts = {
            'crop': R.indices(failed, lambda r: not r['crop_correct']),
            'unit_count': R.indices(failed, lambda r: r['crop_correct'] and not r['count_agrees']),
            'unit_candidates_count_consistent_proxy': R.indices(failed, lambda r: r['crop_correct'] and r['count_agrees']),
        }
        assert sum(map(len, parts.values())) == len(failed)
        partitions[name] = dict(incompatible_rows=len(failed),
                               counts={k: len(v) for k, v in parts.items()}, sample_indices=parts)
    proxy = [r for r in rows if r['crop_correct'] and r['count_agrees']]
    proxy_details = {}
    for name in ['strict_top1', 'strict_top5', 'shape_only_top1', 'shape_only_top5']:
        correct = sum(r[name]['equal_count_position_correct'] for r in proxy)
        total = sum(r[name]['equal_count_position_total'] for r in proxy)
        proxy_details[name] = dict(correct=correct, total=total, incorrect=total-correct,
                                   compatible_rows=sum(r[name]['whole_row_compatible'] for r in proxy),
                                   row_total=len(proxy))
    unresolved = []
    misses = []
    tags = {}
    source_rows = []
    for r in rows:
        i = r['sample_index']
        ref = refs[i]
        for tag in set(ref['crop_issues']):
            tags.setdefault(tag, []).append(i)
        for j, u in enumerate(ref['units']):
            if not u['strict_candidate_codes']:
                unresolved.append(dict(sample_index=i, unit_index=j, source=u))
        if r['crop_correct'] and r['count_agrees']:
            for j, (u, v) in enumerate(zip(ref['units'], ps[i]['units'])):
                if not set(u['strict_candidate_codes']) & {c for a in v['alternatives'][:5] for c in a['codes']}:
                    misses.append(dict(sample_index=i, unit_index=j,
                                       unresolved_reference=not bool(u['strict_candidate_codes']),
                                       reference=u, prediction=v))
        source_rows.append(dict(sample_index=i, pdf_page=r['pdf_page'],
                                section=ps[i]['section'], margin_side=ps[i]['margin_side'],
                                metric_fields=r, adjudicated_crop_issues=ref['crop_issues'],
                                adjudicated_crop_observations=ref.get('crop_observations', [])))

    by_section = {s: R.row_summary([r for r in rows if ps[r['sample_index']]['section'] == s])
                  for s in sel['denominators']}
    by_side = {s: R.row_summary([r for r in rows if ps[r['sample_index']]['margin_side'] == s])
               for s in ['left', 'right']}
    by_parity = {s: R.row_summary([r for r in rows if ('even' if r['pdf_page'] % 2 == 0 else 'odd') == s])
                 for s in ['even', 'odd']}
    by_page = {str(p): R.row_summary([r for r in rows if r['pdf_page'] == p])
               for p in sorted({r['pdf_page'] for r in rows})}
    criteria = {}
    for name, key, threshold in [('crop_90', 'row_crop_correctness', .90),
                                 ('number_90', 'inscription_number_accuracy', .90),
                                 ('count_95', 'drawn_unit_count_agreement', .95),
                                 ('top5_rows_80', 'strict_top5', .80)]:
        x = m['summary'][key]
        if key == 'strict_top5':
            x = x['whole_rows_all_sample']
        needed = math.ceil(threshold * x['total'])
        criteria[name] = dict(observed=x['success'], total=x['total'], threshold=threshold,
                              required_successes=needed, additional_rows_needed=max(0, needed-x['success']),
                              passes=m['negative_result_criteria'][name])
    x = m['source_row_recall']['random']['recall']
    needed = math.ceil(.95 * x['total'])
    criteria['random_page_recall_95'] = dict(observed=x['success'], total=x['total'], threshold=.95,
        required_successes=needed, additional_rows_needed=max(0, needed-x['success']),
        surplus_rows=x['success']-needed, passes=m['negative_result_criteria']['random_page_recall_95'])

    readers = {a: {r['sample_index']: r for part in (1, 2)
                   for r in R.read(RUN / f'blind/reader-{a}/rows-part{part}.json')['rows']}
               for a in 'ab'}
    agreement = {k: sum(readers['a'][i][k] == readers['b'][i][k] for i in range(80))
                 for k in ['printed_inscription_id', 'classification_literal', 'drawn_unit_count', 'crop_correct']}
    agreement['physical_line_membership'] = sum(canonical_lines(readers['a'][i]) == canonical_lines(readers['b'][i]) for i in range(80))
    differences = []
    for i in range(80):
        assert len(readers['a'][i]['units']) == len(readers['b'][i]['units'])
        for j, (a, b) in enumerate(zip(readers['a'][i]['units'], readers['b'][i]['units'])):
            if set(a['strict_candidate_codes']) != set(b['strict_candidate_codes']):
                differences.append(dict(sample_index=i, unit_index=j,
                                        reader_a=a['strict_candidate_codes'], reader_b=b['strict_candidate_codes']))
    notes = R.read(RUN / 'blind/adjudication-notes.json')
    assert agreement == dict(printed_inscription_id=80, classification_literal=80,
                              drawn_unit_count=80, crop_correct=79, physical_line_membership=80)
    assert len(differences) == 12 and sum(len(r['units']) for r in refs.values()) == 369
    ledger = [json.loads(s) for s in (RUN / 'blind/coordinator-task-ledger.jsonl').read_text().splitlines() if s.strip()]
    reader_notes = []
    for a in 'ab':
        for file in ['rows-part1.json', 'rows-part2.json', 'counts.json']:
            p = RUN / f'blind/reader-{a}' / file
            j = R.read(p)
            reader_notes.append(dict(source=p.relative_to(HERE).as_posix(), notes=j['notes'],
                                      started_utc=j.get('started_utc'), finished_utc=j.get('finished_utc')))
    task_groups = {}
    for k, tasks in [('rows', [x for x in ledger if x['part'] in [1, 2]]),
                     ('counts', [x for x in ledger if x['part'] == 3]),
                     ('adjudication', [x for x in ledger if x['part'] == 'adjudication']),
                     ('all', ledger)]:
        task_groups[k] = dict(tasks=len(tasks), tokens=sum(x['subagent_total_tokens'] for x in tasks),
                              tool_uses=sum(x['tool_uses'] for x in tasks),
                              summed_duration_seconds=sum(x['duration_ms'] for x in tasks)/1000)
    cost = dict(status='Verified computation', ledger_path=(RUN / 'blind/coordinator-task-ledger.jsonl').relative_to(HERE).as_posix(),
                ledger=ledger, groups=task_groups, row_readings=160,
                row_tokens_per_reading=task_groups['rows']['tokens']/160,
                row_seconds_per_reading=task_groups['rows']['summed_duration_seconds']/160,
                tokens_including_counts_and_adjudication_per_target=task_groups['all']['tokens']/80,
                billed_dollars=None,
                cost_scope='Task tokens include input/cached-context/output; summed task duration is not wall time or human effort.',
                reader_notes=reader_notes, adjudication_exposure=notes['exposure'],
                package_n_pilot=R.read(ROOT / 'experiments/2026-10-08-helsinki1979-row-verification/pilot/coordinator-cost-projection-v1.json'))

    chart = {}
    for cell, (card, printed) in CELL_DIFFERENCES.items():
        ref_uses = []; proposed = []
        for i in range(80):
            for j, u in enumerate(refs[i]['units']):
                if cell in u.get('chart_locations', []):
                    ref_uses.append(dict(sample_index=i, unit_index=j, strict_codes=u['strict_candidate_codes']))
            for j, u in enumerate(ps[i]['units']):
                for k, alt in enumerate(u['alternatives'][:5]):
                    if alt['template_key'] == cell:
                        proposed.append(dict(sample_index=i, unit_index=j, alternative_rank=k+1, codes=alt['codes']))
        chart[cell] = dict(card_label=card, printed_code=printed, reference_units=len(ref_uses),
                           reference_uses=ref_uses, top1_prediction_units=sum(x['alternative_rank']==1 for x in proposed),
                           top5_prediction_units=len(proposed), prediction_uses=proposed)
    # Exact reference location keys outrank prose locators for this tally.
    # Adjudication notes additionally name 58:0 at 20:4:1, but the reference
    # records 21:7:5 (another card labelled 506); retain that disagreement.
    assert sum(x['reference_units'] for x in chart.values()) == 5

    result = dict(status='Exploratory', endpoint_status=m['status'], pipeline_status=m['pipeline_status'],
                  frame=m['frame'], summary=m['summary'], row_bootstrap_95=m['row_bootstrap_95'],
                  numbered_recall=m['source_row_recall'], physical_recall=m['physical_line_recall'],
                  criterion_row_gaps=criteria, subsets=subsets,
                  incompatible_whole_row_partitions=partitions,
                  count_consistent_accepted_crop_proxy=proxy_details,
                  proxy_limitation='Accepted crop and equal counts do not establish one-to-one unit boundaries.',
                  unresolved_strict_units=unresolved, accepted_crop_equal_count_top5_misses=misses,
                  crop_issues={k: dict(count=len(v), sample_indices=v) for k, v in sorted(tags.items())},
                  by_section=by_section, by_margin_side=by_side, by_page_parity=by_parity, by_page=by_page,
                  readers=dict(row_field_agreement=agreement, strict_unit_sets_agreed=357, strict_unit_sets_total=369,
                               disagreement_units=differences, disagreement_rows=sorted({x['sample_index'] for x in differences}),
                               adjudication_summary=notes['agreement_summary'], adjudication_decisions=notes['disagreement_summary']),
                  chart_label_audit=chart,
                  chart_location_witness_disagreement=dict(sample_index=58, unit_index=0,
                      reference_chart_locations=refs[58]['units'][0]['chart_locations'],
                      adjudication_notes_location='20:4:1', strict_codes=refs[58]['units'][0]['strict_candidate_codes'],
                      action='Keep both frozen witnesses; do not infer a cell-specific remap from code 506 alone.'),
                  chart_scoring_note='Frozen scored codes remain card labels. Printed-code remapping requires a separate cell-specific snapshot and future pipeline.',
                  v2_comparator=R.read(HERE / 'follow-up/2026-10-07/endpoint-record-v1/diagnosis.json'),
                  input_hashes=before, rows=source_rows)
    out.mkdir(parents=True)
    snapshots = {}
    for name in ['README.md', 'REPORT.md', 'RETROSPECTIVE.md', 'PROTOCOL.md',
                 'registry-entry.json', 'sources.json', 'OPTION-B-INTERFACE.md']:
        shutil.copyfile(HERE / name, out / (name + '.before-record.txt'))
        snapshots[name] = dict(text=(HERE / name).read_bytes().decode('utf-8'), sha256=R.sha(HERE / name))
    dump(out / 'documentation-snapshot.json', dict(status='Verified computation', files=snapshots))
    dump(out / 'diagnosis.json', result)
    dump(out / 'reader-process-cost.json', cost)
    dump(out / 'chart-locator-inspection.json', chart_locator_observation())
    assert all(R.sha(HERE / p) == h for p, h in before.items())
    dump(out / 'preservation-check.json', dict(status='Verified computation', all_unchanged=True,
                                               frozen_file_count=len(before), hashes=before))
    print(json.dumps(dict(output=out.relative_to(HERE).as_posix(), subsets=subsets, partitions=partitions,
                          sections={s: {k: len(v) if isinstance(v, list) else v for k, v in x.items()} for s, x in by_section.items()},
                          chart={k: {f: v[f] for f in ['reference_units', 'top1_prediction_units', 'top5_prediction_units']} for k, v in chart.items()},
                          costs=task_groups, frozen_files=len(before)), indent=2))


if __name__ == '__main__':
    main()
