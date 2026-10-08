"""Read-only checks of frozen witnesses and the small completed-v3 record."""
from pathlib import Path
import argparse
import json
import math
import re
import record_repaired_endpoint as R

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REC = HERE / 'repair/2026-10-08-endpoint-record-v1'
RUN = HERE / 'repair/2026-10-08-v3'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=REC / 'verification-final.json')
    args = ap.parse_args(); out = args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError('Use a fresh owned verification path')
    checks = {}; details = {}
    pin = R.read(REC / 'preservation-check.json')
    failed = [p for p, h in pin['hashes'].items() if R.sha(HERE / p) != h]
    checks['all_520_frozen_witnesses_unchanged'] = len(pin['hashes']) == 520 and not failed
    details['changed_frozen_paths'] = failed
    import hashlib
    snapshot = R.read(REC / 'documentation-snapshot.json')['files']
    checks['all_seven_portable_document_snapshots_match_hashes'] = len(snapshot) == 7 and all(hashlib.sha256(x['text'].encode('utf-8')).hexdigest() == x['sha256'] for x in snapshot.values())
    f = R.read(RUN / 'freeze-manifest.json')
    checks['all_twelve_v3_frozen_implementation_inputs_match'] = all(R.sha(HERE / p) == h for p, h in f['code_hashes'].items()) and len(f['code_hashes']) == 12
    checks['source_pdf_matches_freeze'] = R.sha(ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf') == f['source_sha256']
    original = RUN / 'evaluation-2026-10-08-adjudicated/metrics.json'
    replay = REC / 'evaluator-replay/metrics.json'
    checks['unchanged_evaluator_replay_byte_identical'] = original.read_bytes() == replay.read_bytes()
    details['metrics_sha256'] = R.sha(original)
    m = R.read(original); d = R.read(REC / 'diagnosis.json'); a = R.read(REC / 'unit-window-audit.json')
    cost = R.read(REC / 'reader-process-cost.json')
    checks['diagnosis_reuses_exact_frozen_summary_and_intervals'] = d['summary'] == m['summary'] and d['row_bootstrap_95'] == m['row_bootstrap_95']
    checks['frame_old140_excluded_with_28_26_26_quotas'] = m['frame']['old140_targets_excluded'] and list(m['frame']['section_quotas'].values()) == [28, 26, 26]
    checks['all_four_failed_criterion_gaps_match_thresholds'] = [d['criterion_row_gaps'][k]['additional_rows_needed'] for k in ['crop_90','number_90','count_95','top5_rows_80']] == [1,1,4,2]
    checks['four_failures_one_recall_pass'] = list(m['negative_result_criteria'].values()) == [False,False,False,False,True]
    checks['stage_partitions_cover_every_failed_row'] = all(sum(x['counts'].values()) == x['incompatible_rows'] and len(set(i for ids in x['sample_indices'].values() for i in ids)) == x['incompatible_rows'] for x in d['incompatible_whole_row_partitions'].values())
    checks['refined_top5_partition_8_7_3_0'] = list(a['refined_top5_counts'].values()) == [8,7,3,0] and sum(a['refined_top5_counts'].values()) == 18
    checks['four_resolved_equal_count_misses_all_in_row31'] = [(x['sample_index'],x['unit_index']) for x in d['accepted_crop_equal_count_top5_misses'] if not x['unresolved_reference']] == [(31,3),(31,4),(31,5),(31,6)]
    checks['empty_reference_units_separate_from_classifier_defects'] = [(x['sample_index'],x['unit_index']) for x in d['unresolved_strict_units']] == [(3,5),(35,2),(70,4)]
    checks['reader_agreement_357_of_369_and_79_of_80_crops'] = d['readers']['strict_unit_sets_agreed'] == 357 and d['readers']['strict_unit_sets_total'] == 369 and d['readers']['row_field_agreement']['crop_correct'] == 79
    checks['all_320_number_class_count_membership_fields_agree'] = sum(d['readers']['row_field_agreement'][k] for k in ['printed_inscription_id','classification_literal','drawn_unit_count','physical_line_membership']) == 320
    ledger = [json.loads(s) for s in (RUN / 'blind/coordinator-task-ledger.jsonl').read_text().splitlines() if s.strip()]
    checks['task_ledger_totals_2486666_tokens_11108273_ms'] = sum(x['subagent_total_tokens'] for x in ledger) == cost['groups']['all']['tokens'] == 2486666 and sum(x['duration_ms'] for x in ledger) == round(cost['groups']['all']['summed_duration_seconds']*1000) == 11108273
    chart = d['chart_label_audit']
    checks['chart_cell_uses_3_2_0_0_and_top5_3_6_0_1'] = [x['reference_units'] for x in chart.values()] == [3,2,0,0] and [x['top5_prediction_units'] for x in chart.values()] == [3,6,0,1]
    checks['row58_conflicting_locator_preserved'] = d['chart_location_witness_disagreement']['reference_chart_locations'] == ['21:7:5'] and d['chart_location_witness_disagreement']['adjudication_notes_location'] == '20:4:1'
    locator = R.read(REC / 'chart-locator-inspection.json')
    checks['all_three_row58_locator_inspection_source_hashes_match'] = len(locator['source_hashes']) == 3 and all(R.sha(ROOT / p) == h for p,h in locator['source_hashes'].items())
    checks['all_ten_source_overlay_hashes_match'] = all(R.sha(ROOT / x['source_overlay']) == x['overlay_sha256'] for x in a['observations']) and len(a['observations']) == 10
    full = R.read(RUN / 'full-summary.json'); payload = ROOT / full['path']
    checks['large_proposal_payload_hash_and_size_unchanged'] = R.sha(payload) == full['sha256'] and payload.stat().st_size == full['bytes'] == 106190599
    n = units = continuations = numbered = released = unresolved = 0
    pages = set(); quarantined = True
    with payload.open(encoding='utf-8') as stream:
        for s in stream:
            r = json.loads(s); n += 1; units += len(r['units']); pages.add(r['pdf_page'])
            continuations += r['line_kind'] == 'continuation'; numbered += r['line_kind'] == 'numbered'
            released += bool(r['released']); quarantined &= r['quarantined'] and r['review_status'] == 'unreviewed'
            unresolved += sum(not u['alternatives'] and u['confidence'] is None for u in r['units'])
    checks['full_inventory_11769_rows_54384_units_159_pages'] = (n,units,len(pages),numbered,continuations,unresolved) == (11769,54384,159,11702,67,5)
    checks['every_full_occurrence_quarantined_zero_releases'] = quarantined and released == 0
    entry = R.read(HERE / 'registry-entry.json')
    checks['registry_required_fields_and_failed_status'] = all(k in entry for k in ['id','theme','status','question','outcome','challenge','remedy','evidence','retry_when']) and entry['status'] == 'Failed'
    checks['registry_evidence_paths_exist'] = all((ROOT / p).exists() or (ROOT / p).resolve() == out for p in entry['evidence'])
    broken = []
    for name in ['README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','OPTION-B-INTERFACE.md']:
        p = HERE / name
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if target.startswith(('http:', 'https:', '#')):
                continue
            q = target.strip('<>').split('#')[0]
            expected = [REC/'verification-final.json', REC/'changed-paths.json', out]
            path = (p.parent / q).resolve()
            if not path.exists() and path not in expected:
                broken.append(dict(file=name,target=target))
    checks['all_living_document_links_resolve'] = not broken
    details['broken_links'] = broken
    details.update(frozen_files=len(pin['hashes']), full_rows=n, full_units=units, released=released)
    # Code hashes belong to this aggregate check, not the frozen pipeline.
    details['record_code_hashes'] = {p.name:R.sha(p) for p in [HERE/'record_v3_endpoint.py',HERE/'inspect_v3_endpoint.py',HERE/'audit_v3_endpoint_windows.py',HERE/'write_v3_endpoint_docs.py',Path(__file__)]}
    result = dict(status='Verified computation' if all(checks.values()) else 'Failed',
                  passed=sum(checks.values()),total=len(checks),checks=checks,details=details)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],total=result['total'],failed=[k for k,v in checks.items() if not v])))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
