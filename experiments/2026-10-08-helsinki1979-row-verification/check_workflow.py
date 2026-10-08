"""Synthetic contract tests and packet integrity audit; never reads corpus rows."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import workflow as W
import score_pilot as S
import adjudicate as A
import merge as G


def check(run, raw_out, summary_out):
    raw_out = W.owned(raw_out)
    if not raw_out.is_relative_to(W.RAW) or raw_out.exists():
        raise ValueError('Use a fresh local raw synthetic-check directory')
    raw_out.mkdir(parents=True)
    tests = []
    def expect(name, condition):
        tests.append(dict(name=name, passed=bool(condition)))
        if not condition:
            raise AssertionError(name)
    manifest = W.read(Path(run) / 'coordinator/private-manifest.json')
    E = W.evaluator()
    codes = W.code_universe()
    return_root = raw_out / 'synthetic-returns'
    for bidx, batch in enumerate(manifest['batches']):
        packets = {}
        for role in ('reader-1', 'reader-2'):
            path = W.ROOT / batch['packets'][role]['path']
            p = W.check_packet(path)
            packets[role] = p
            expect(f'{role}/{batch["batch_id"]}: hash verified', p['packet_sha256'] == batch['packets'][role]['sha256'])
            expect(f'{role}/{batch["batch_id"]}: controls unlabelled', all('control' not in json.dumps(r).lower() for r in p['items']))
            expect(f'{role}/{batch["batch_id"]}: proposal isolation', (path.parent / 'proposals.json').exists() == (role == 'reader-1'))
            if role == 'reader-2':
                expect(f'{batch["batch_id"]}: blind packet has no codes/field values', all(
                    not any(k in r for k in ('units', 'inscription_number', 'printed_inscription_id', 'classification_literal', 'strict_candidate_codes')) for r in p['items']))
            form = W.template(p)
            form.update(evidence_status='Synthetic', reader=dict(provider='Synthetic fixture', model='synthetic-fixture', model_version='1',
                                    run_id=f'synthetic-{role}-{batch["batch_id"]}', independence_attestation='Synthetic software test; no source reading'),
                        started_utc='2026-10-08T00:00:00Z', finished_utc='2026-10-08T00:01:00Z', elapsed_seconds=60,
                        usage=dict(input_tokens=3900, cached_input_tokens=100, output_tokens=390,
                                   billed_usd=.01, unavailable_reason=None))
            form['columns'][0].update(numbered_occurrences=len(batch['target_keys']), continuation_lines=0,
                                       observed_page_columns=batch.get('detected_page_columns', 2), unassigned_columns=[],
                                       coverage_complete=True, source_observations='Synthetic inventory')
            locs = {r['item_id']: r for r in p['items']}
            for row in form['rows']:
                iid = row['item_id']
                loc = locs[iid]
                if iid in batch['controls']:
                    ref = batch['controls'][iid]
                    row.update({k: copy.deepcopy(ref[k]) for k in ('printed_inscription_id', 'classification_literal', 'drawn_unit_count', 'crop_correct', 'units')})
                    ordinal = 1
                else:
                    ordinal = int(batch['target_keys'][iid].rsplit(':r', 1)[1]) + 1
                    row.update(printed_inscription_id=str(100 + ordinal), classification_literal='11 40', drawn_unit_count=1,
                               crop_correct=True, units=[dict(strict_candidate_codes=[144], unit_kind='sign', underline_dashes=False)])
                row.update(source_row_ordinal=ordinal, source_y_pdf=loc['target_y_pdf'], source_observations='Synthetic fixture, not a source reading',
                           blank_gaps=[], continuation_y_pdf=[], continuation_rows=[], unresolved_fields=[], unresolved_boundary=None)
            expect(f'{role}/{batch["batch_id"]}: valid synthetic envelope', not W.validate_return(form, p, codes))
            if bidx == 0:
                base = copy.deepcopy(form)
                # Validation mutation coverage goes beyond matching the implementation's happy path.
                mutations = {
                    'wrong packet hash': lambda d: d.update(packet_sha256='0' * 64),
                    'missing row': lambda d: d['rows'].pop(),
                    'duplicate row': lambda d: d['rows'].append(copy.deepcopy(d['rows'][0])),
                    'unknown item': lambda d: d['rows'][0].update(item_id='unknown'),
                    'count mismatch': lambda d: d['rows'][0].update(drawn_unit_count=999),
                    'invalid classification': lambda d: d['rows'][0].update(classification_literal='1140'),
                    'lost string suffix type': lambda d: d['rows'][0].update(printed_inscription_id=101),
                    'wrong page': lambda d: d['rows'][0].update(pdf_page=999),
                    'impossible coordinate': lambda d: d['rows'][0].update(source_y_pdf=-1),
                    'missing identity': lambda d: d['reader'].update(model=None),
                    'negative tokens': lambda d: d['usage'].update(input_tokens=-1),
                    'fractional tokens': lambda d: d['usage'].update(input_tokens=3.5),
                    'cache exceeds input': lambda d: d['usage'].update(cached_input_tokens=999999),
                    'missing timing': lambda d: d.update(elapsed_seconds=None),
                    'reversed timing': lambda d: d.update(finished_utc='2026-10-07T00:00:00Z'),
                    'invalid strict code': lambda d: d['rows'][0]['units'][0].update(strict_candidate_codes=[999999]),
                    'missing underline': lambda d: d['rows'][0]['units'][0].pop('underline_dashes'),
                    'missing continuation payload': lambda d: d['rows'][0].update(continuation_y_pdf=[20]),
                }
                for name, mutate in mutations.items():
                    d = copy.deepcopy(base)
                    mutate(d)
                    expect(f'{role}: reject {name}', bool(W.validate_return(d, p, codes)))
                target_id = next(iter(batch['target_keys']))
                rr = next(r for r in form['rows'] if r['item_id'] == target_id)
                if role == 'reader-2':
                    rr['printed_inscription_id'] = '999'
            W.write(return_root / role / (batch['batch_id'] + '.json'), form)
        expect(f'{batch["batch_id"]}: same source items across roles', packets['reader-1']['items'] == packets['reader-2']['items'])
    sample = dict(printed_inscription_id='1', classification_literal='11 40', drawn_unit_count=1, crop_correct=True,
                  valid_printed_target=True, source_row_ordinal=1, source_y_pdf=100, units=[dict(strict_candidate_codes=[9, 765], unit_kind='sign', underline_dashes=False)],
                  blank_gaps=[], continuation_y_pdf=[], continuation_rows=[], unresolved_fields=[], unresolved_boundary=None)
    expect('matching ambiguous sets are unresolved', not W.resolved(sample) and not W.differences(sample, copy.deepcopy(sample)))
    changed = copy.deepcopy(sample)
    changed['units'][0]['strict_candidate_codes'] = [9]
    expect('intersection is not exact agreement', bool(W.differences(sample, changed)))
    for field, value in [('printed_inscription_id', '2'), ('classification_literal', '11 41'), ('drawn_unit_count', 2), ('crop_correct', False), ('source_row_ordinal', 2)]:
        changed = copy.deepcopy(sample)
        changed[field] = value
        expect('route disagreement: ' + field, field in W.differences(sample, changed))
    expect('anonymous reading excludes role metadata', 'reader' not in A.anonymous(sample) and 'proposal_confidence' not in json.dumps(A.anonymous(sample)))
    # Reconcile all-field disagreement into an anonymous packet, then supply a synthetic adjudication.
    adjud_out = raw_out / 'synthetic-adjudication'
    A.prepare(run, return_root, adjud_out)
    apaths = sorted((adjud_out / 'adjudicator').glob('*/packet.json'))
    expect('one constructed disagreement creates one adjudication packet', len(apaths) == 1)
    ap = W.check_packet(apaths[0])
    af = W.template(ap)
    bid = ap['batch_id']
    original = W.read(return_root / 'reader-1' / (bid + '.json'))
    arows = {r['item_id']: r for r in original['rows']}
    af.update(evidence_status='Synthetic', reader=dict(provider='Synthetic fixture', model='synthetic-fixture', model_version='1', run_id='synthetic-adjudicator',
                          independence_attestation='Synthetic software test'), started_utc=original['started_utc'], finished_utc=original['finished_utc'],
              elapsed_seconds=10, usage=dict(input_tokens=1000, cached_input_tokens=0, output_tokens=100, billed_usd=.001, unavailable_reason=None))
    af['rows'] = [dict(copy.deepcopy(arows[loc['item_id']]), adjudication_basis='Synthetic choice, not a source reading') for loc in ap['items']]
    af['columns'] = []
    expect('synthetic adjudication validates', not W.validate_return(af, ap, codes))
    W.write(return_root / 'adjudicator' / (bid + '.json'), af)
    rates = dict(status='Synthetic', models={'synthetic-fixture': dict(input_usd_per_million=1, cached_input_usd_per_million=.1, output_usd_per_million=2)})
    result = S.score(run, return_root, raw_out / 'synthetic-score', adjud_out, rates=rates)
    expect('all 18 controls scored per role', all(r['evaluated_controls'] == 18 for r in result['control_accuracy'].values()))
    expect('constructed disagreement count', result['adjudication_load']['success'] == 1 and result['adjudication_load']['total'] == 216)
    expect('complete timing and billing project total', result['cost']['full_run']['total_summed_task_hours'] is not None and result['cost']['monetary_cost_known'])
    expect('planning interval computed', result['cost']['full_run']['projection_metrics']['elapsed_seconds']['total_planning_interval95'] is not None)
    merged = G.merge(run, return_root, raw_out / 'synthetic-merge', raw_out / 'synthetic-merge-summary.json', adjud_out)
    expect('controls excluded from merge', merged['merged_records'] == 216 and merged['control_items_excluded'] == 18)
    expect('synthetic resolved records staged only', merged['ledger_staging_rows'] == 216 and merged['real_ledger_imports'] == 0)
    expect('provenance retained', merged['dispositions'] == {'adjudicated': 1, 'agreed': 215})
    import jsonschema
    schema_path = W.ROOT / 'experiments/2026-10-07-object-ledger/verification-2026-10-07-v3/interface-schema-v2.json'
    schema = W.read(schema_path)
    validator = jsonschema.Draft202012Validator({'$ref': '#/$defs/digitized_row', '$defs': schema['$defs']})
    ledger = [json.loads(line) for line in (raw_out / 'synthetic-merge/ledger-staging.jsonl').read_text().splitlines()]
    expect('all staged fixtures pass L row schema', all(not list(validator.iter_errors(r)) for r in ledger))
    tasks = result['cost']['roles']
    expect('per-row timing includes controls', tasks['reader-1']['metrics']['elapsed_seconds']['per_assigned_row'] == 360 / 234)
    nulltasks = copy.deepcopy(S.collect(run, return_root)['tasks'])
    for t in nulltasks:
        t['usage'] = dict(input_tokens=None, cached_input_tokens=None, output_tokens=None, billed_usd=None, unavailable_reason='Synthetic missing usage')
    nullcost = S.costs(nulltasks, [53, 83, 170], 11369, 1, E.wilson(1, 216), None)
    expect('unknown billing stays null', nullcost['full_run']['projection_metrics']['billed_usd']['initial_passes'] is None)
    expect('unmeasured adjudicator leaves total null', nullcost['full_run']['total_summed_task_hours'] is None)
    first = W.read(return_root / 'reader-1' / (manifest['batches'][0]['batch_id'] + '.json'))
    missing_column = copy.deepcopy(first)
    missing_column['columns'][0]['observed_page_columns'] = 3
    missing_column['columns'][0]['unassigned_columns'] = [dict(pdf_column=2, x_extent_pdf=[400, 500])]
    expect('missed whole column blocks coverage', not W.inventory_complete(missing_column, manifest['batches'][0]))
    duplicate_ordinal = copy.deepcopy(first)
    tids = set(manifest['batches'][0]['target_keys'])
    trs = [r for r in duplicate_ordinal['rows'] if r['item_id'] in tids]
    trs[1]['source_row_ordinal'] = trs[0]['source_row_ordinal']
    expect('duplicate source ordinal blocks coverage', not W.inventory_complete(duplicate_ordinal, manifest['batches'][0]))
    expect('all ledger fixtures explicitly marked Synthetic', all(r['synthetic'] is True and r['review_status'] == 'synthetic_fixture' for r in ledger))
    # A candidate ambiguity in one completely inventoried row leaves other rows eligible.
    ambiguous_returns = raw_out / 'synthetic-ambiguous-returns'
    uncertain_id = list(manifest['batches'][0]['target_keys'])[1]
    for batch in manifest['batches']:
        for role in ('reader-1', 'reader-2'):
            data = W.read(return_root / role / (batch['batch_id'] + '.json'))
            if batch == manifest['batches'][0]:
                first_rows = {r['item_id']: r for r in first['rows']}
                for row in data['rows']:
                    if row['item_id'] in batch['target_keys']:
                        row['printed_inscription_id'] = first_rows[row['item_id']]['printed_inscription_id']
                    if row['item_id'] == uncertain_id:
                        row['units'][0]['strict_candidate_codes'] = [9, 765]
            W.write(ambiguous_returns / role / (batch['batch_id'] + '.json'), data)
    uncertain_merge = G.merge(run, ambiguous_returns, raw_out / 'synthetic-ambiguous-merge', raw_out / 'synthetic-ambiguous-summary.json')
    expect('candidate ambiguity retains one unresolved record', uncertain_merge['dispositions'] == {'agreed': 215, 'unresolved': 1})
    expect('other resolved rows remain staged with complete source coverage', uncertain_merge['ledger_staging_rows'] == 215)
    expect('all source inventories remain covered despite ambiguous content', all(c['source_coverage_complete'] for c in uncertain_merge['columns']))
    checks = dict(status='Verified computation', fixture_status='Synthetic', created_utc=W.now(),
                  tests=tests, passed=sum(t['passed'] for t in tests), total=len(tests),
                  source_readings_performed=0, packets_audited=12,
                  local_fixture_directory=W.relative(raw_out), script_sha256=W.sha(__file__),
                  workflow_sha256=W.sha(W.HERE / 'workflow.py'), L_schema_sha256=W.sha(schema_path),
                  note='Fixture rows and costs are constructed; counts validate software behavior and do not measure pilot reader accuracy.')
    W.write(summary_out, checks)
    print(f'{checks["passed"]}/{checks["total"]} checks passed; zero source readings')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--raw-out', type=Path, required=True)
    p.add_argument('--summary-out', type=Path, required=True)
    args = p.parse_args()
    check(args.run, args.raw_out, args.summary_out)
