"""Score real returned readings; absence of readings produces pending metrics."""
from __future__ import annotations
import argparse
import copy
import json
import math
import random
from collections import defaultdict
from pathlib import Path
import workflow as W
import usage_ledger as U


def collect(run, returns, adjudications=None, usage_ledger=None):
    manifest = W.read(Path(run) / 'coordinator/private-manifest.json')
    result = dict(manifest=manifest, batches=[], errors=[], tasks=[])
    for batch in manifest['batches']:
        state = dict(batch=batch, readings={}, packet={}, hashes={}, adjudication=None)
        for role in ('reader-1', 'reader-2'):
            packetpath = W.ROOT / batch['packets'][role]['path']
            packet = W.check_packet(packetpath)
            if packet['packet_sha256'] != batch['packets'][role]['sha256']:
                raise ValueError('Coordinator packet pin differs')
            state['packet'][role] = packet
            path = Path(returns) / role / (batch['batch_id'] + '.json')
            if not path.exists():
                continue
            try:
                data = W.read(path)
                errors = W.validate_return(data, packet, W.code_universe(packet))
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                errors = [f'malformed return: {type(e).__name__}: {e}']
            if errors:
                result['errors'].append(dict(role=role, batch_id=batch['batch_id'], path=W.relative(path), errors=errors))
                continue
            state['readings'][role] = data
            state['hashes'][role] = dict(path=W.relative(path), sha256=W.sha(path))
            result['tasks'].append(task_record(data, batch, path))
        if adjudications:
            packetpath = Path(adjudications) / 'adjudicator' / batch['batch_id'] / 'packet.json'
            path = Path(returns) / 'adjudicator' / (batch['batch_id'] + '.json')
            if path.exists() and not packetpath.exists():
                result['errors'].append(dict(role='adjudicator', batch_id=batch['batch_id'], errors=['Adjudication packet absent']))
            elif path.exists():
                packet = W.check_packet(packetpath)
                try:
                    data = W.read(path)
                    errors = W.validate_return(data, packet, W.code_universe(packet))
                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    errors = [f'malformed adjudication: {e}']
                # Prevent applying an adjudication to different or changed initial readings.
                current = {role: state['hashes'].get(role, {}).get('sha256') for role in ('reader-1', 'reader-2')}
                privatepath = Path(adjudications) / 'coordinator' / (batch['batch_id'] + '.json')
                if not privatepath.exists() or W.read(privatepath)['initial_reading_hashes'] != current:
                    errors.append('Adjudication initial-reading pins differ')
                if errors:
                    result['errors'].append(dict(role='adjudicator', batch_id=batch['batch_id'], errors=errors))
                else:
                    state['adjudication'] = data
                    state['hashes']['adjudicator'] = dict(path=W.relative(path), sha256=W.sha(path))
                    state['packet']['adjudicator'] = packet
                    result['tasks'].append(task_record(data, batch, path))
        result['batches'].append(state)
    result['usage_ledger'] = U.attach(result['tasks'], usage_ledger)
    return result


def task_record(data, batch, path):
    return dict(batch_id=batch['batch_id'], page=batch['pdf_page'], role=data['role'], reader=data['reader'],
                evidence_status=data['evidence_status'],
                packet_sha256=data['packet_sha256'], return_sha256=W.sha(path), return_path=W.relative(path),
                started_utc=data['started_utc'], finished_utc=data['finished_utc'], elapsed_seconds=data['elapsed_seconds'],
                submitted_rows=len(data['rows']), target_rows=sum(r['item_id'] not in batch['controls'] for r in data['rows']),
                control_rows=sum(r['item_id'] in batch['controls'] for r in data['rows']), usage=data['usage'])


def comparison(state):
    a, b = state['readings'].get('reader-1'), state['readings'].get('reader-2')
    ar = {r['item_id']: r for r in a['rows']} if a else {}
    br = {r['item_id']: r for r in b['rows']} if b else {}
    items = set(state['batch']['target_keys']) | set(state['batch']['controls']) | set(ar) | set(br)
    inventory_agrees = bool(a and b and a['columns'][0]['numbered_occurrences'] == b['columns'][0]['numbered_occurrences']
                             and a['columns'][0]['continuation_lines'] == b['columns'][0]['continuation_lines'])
    coverage = (inventory_agrees and W.inventory_complete(a, state['batch']) and W.inventory_complete(b, state['batch']))
    rows = []
    for item in sorted(items):
        ra, rb = ar.get(item), br.get(item)
        paired = ra is not None and rb is not None
        diffs = W.differences(ra, rb) if paired else ['missing_reading']
        is_control = item in state['batch']['controls']
        if paired and not is_control and not coverage:
            diffs.append('column_coverage')
        rows.append(dict(item_id=item, control=is_control, a=ra, b=rb, paired=paired,
                         differences=diffs, agrees=paired and not diffs,
                         requires_adjudication=bool(a and b and diffs)))
    return rows, coverage


def control_fields(row, ref):
    fields = dict(number=row.get('printed_inscription_id') == ref['printed_inscription_id'],
                  classification=row.get('classification_literal') == ref['classification_literal'],
                  count=row.get('drawn_unit_count') == ref['drawn_unit_count'],
                  crop=row.get('crop_correct') == ref['crop_correct'])
    units, truth = row['units'], ref['units']
    fields['strict_sequence'] = len(units) == len(truth) and all(
        set(a['strict_candidate_codes']) == set(b['strict_candidate_codes']) for a, b in zip(units, truth))
    fields['unit_kind_and_underline'] = len(units) == len(truth) and all(
        a['unit_kind'] == b['unit_kind'] and a['underline_dashes'] == b['underline_dashes'] for a, b in zip(units, truth))
    fields['all_required_fields'] = all(fields.values()) and row.get('valid_printed_target') is True
    return fields


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    point = (len(values) - 1) * p
    lo, hi = math.floor(point), math.ceil(point)
    return values[lo] + (values[hi] - values[lo]) * (point - lo)


def cluster_interval(page_pairs, E):
    if not page_pairs:
        return None
    rng = random.Random(2026100802)
    values = []
    for _ in range(2000):
        selected = [rng.choice(page_pairs) for __ in page_pairs]
        denom = sum(p[1] for p in selected)
        if denom:
            values.append(sum(p[0] for p in selected) / denom)
    return [percentile(values, .025), percentile(values, .975)]


def priced(task, rates):
    if not rates:
        return None
    rate = rates.get('models', {}).get(task['reader']['model'])
    if not rate:
        return None
    usage = task['usage']
    values = [usage.get(k) for k in ('input_tokens', 'cached_input_tokens', 'output_tokens')]
    if any(v is None for v in values):
        return None
    total, cached, output = values
    return ((total - cached) * rate['input_usd_per_million'] + cached * rate['cached_input_usd_per_million']
            + output * rate['output_usd_per_million']) / 1000000


def costs(tasks, pages, full_rows, concurrency, adjud_rate, rates, expected_batches=None):
    roles = {}
    metric_names = ('elapsed_seconds', 'input_tokens', 'cached_input_tokens', 'output_tokens', 'billed_usd', 'priced_usd', 'combined_tokens')
    rng = random.Random(2026100803)
    for role in ('reader-1', 'reader-2', 'adjudicator'):
        selected = [t for t in tasks if t['role'] == role]
        nassigned = sum(t['submitted_rows'] for t in selected)
        ntarget = sum(t['target_rows'] for t in selected)
        per_metric = {}
        for metric in metric_names:
            def value(t):
                return t['elapsed_seconds'] if metric == 'elapsed_seconds' else t.get('combined_tokens') if metric == 'combined_tokens' else priced(t, rates) if metric == 'priced_usd' else t['usage'].get(metric)
            values = [value(t) for t in selected]
            complete = bool(values) and all(v is not None for v in values)
            total = sum(values) if complete else None
            per_metric[metric] = dict(total=total, measured_tasks=sum(v is not None for v in values), tasks=len(values),
                                      per_assigned_row=total / nassigned if total is not None and nassigned else None,
                                      per_target_row_including_controls=total / ntarget if total is not None and ntarget else None)
        roles[role] = dict(tasks=len(selected), assigned_rows=nassigned, target_rows=ntarget, metrics=per_metric)
    # No full projection until every initial column task has valid timing/identity.
    expected_batches = len(pages) * 2 if expected_batches is None else expected_batches
    initial_complete = all(roles[r]['tasks'] == expected_batches for r in ('reader-1', 'reader-2'))
    projections = {}
    for metric in metric_names:
        initial = None
        interval = None
        initial_draws = []
        parallel_draws = []
        if initial_complete and all(roles[r]['metrics'][metric]['total'] is not None for r in ('reader-1', 'reader-2')):
            initial = full_rows * sum(roles[r]['metrics'][metric]['per_target_row_including_controls'] for r in ('reader-1', 'reader-2'))
            for _ in range(2000):
                sampled = [rng.choice(pages) for __ in pages]
                rate_sum = 0
                role_rates = []
                for role in ('reader-1', 'reader-2'):
                    ts = [t for p in sampled for t in tasks if t['role'] == role and t['page'] == p]
                    def value(t):
                        return t['elapsed_seconds'] if metric == 'elapsed_seconds' else t.get('combined_tokens') if metric == 'combined_tokens' else priced(t, rates) if metric == 'priced_usd' else t['usage'][metric]
                    rate = sum(value(t) for t in ts) / sum(t['target_rows'] for t in ts)
                    role_rates.append(rate)
                    rate_sum += rate
                initial_draws.append(full_rows * rate_sum)
                if metric == 'elapsed_seconds':
                    parallel_draws.append(full_rows * max(role_rates) / concurrency / 3600)
            interval = [percentile(initial_draws, .025), percentile(initial_draws, .975)]
        adjmetric = roles['adjudicator']['metrics'][metric]
        arate = adjmetric['per_target_row_including_controls']
        adj = full_rows * adjud_rate['rate'] * arate if adjud_rate['rate'] is not None and arate is not None else None
        adjinterval = [full_rows * p * arate for p in adjud_rate['ci95']] if adj is not None else None
        total_draws = []
        total_parallel_draws = []
        adjtasks = [t for t in tasks if t['role'] == 'adjudicator' and t['target_rows']]
        if initial_draws and adj is not None and adjtasks:
            # Page-resampled initial workload plus adjudicator-task resampling and
            # Wilson adjudication-rate endpoints. This is a planning sensitivity band.
            for i, initial_value in enumerate(initial_draws):
                ats = [rng.choice(adjtasks) for __ in adjtasks]
                def avalue(t):
                    return t['elapsed_seconds'] if metric == 'elapsed_seconds' else t.get('combined_tokens') if metric == 'combined_tokens' else priced(t, rates) if metric == 'priced_usd' else t['usage'].get(metric)
                if any(avalue(t) is None for t in ats):
                    continue
                adjrate_draw = sum(avalue(t) for t in ats) / sum(t['target_rows'] for t in ats)
                # Sample q from observed paired target outcomes for point uncertainty.
                n, k = adjud_rate['total'], adjud_rate['success']
                qdraw = rng.betavariate(k + .5, n - k + .5)
                adjunct = full_rows * qdraw * adjrate_draw
                total_draws.append(initial_value + adjunct)
                if metric == 'elapsed_seconds':
                    total_parallel_draws.append(parallel_draws[i] + adjunct / concurrency / 3600)
        projections[metric] = dict(initial_passes=initial, initial_page_bootstrap_ci95=interval,
                                   adjudication=adj, adjudication_wilson_sensitivity95=adjinterval,
                                   total=initial + adj if initial is not None and adj is not None else None,
                                   total_planning_interval95=[percentile(total_draws, .025), percentile(total_draws, .975)] if total_draws else None,
                                   initial_parallel_hours_ci95=[percentile(parallel_draws, .025), percentile(parallel_draws, .975)] if parallel_draws else None,
                                   sequential_phase_parallel_hours_interval95=[percentile(total_parallel_draws, .025), percentile(total_parallel_draws, .975)] if total_parallel_draws else None)
    seconds = projections['elapsed_seconds']
    initial_parallel = None
    if seconds['initial_passes'] is not None:
        initial_parallel = full_rows * max(roles[r]['metrics']['elapsed_seconds']['per_target_row_including_controls'] for r in ('reader-1', 'reader-2')) / concurrency / 3600
    return dict(roles=roles, full_run=dict(status='Exploratory', provisional_rows=full_rows, workers_per_reader_role=concurrency,
                projection_metrics=projections, initial_summed_task_hours=seconds['initial_passes'] / 3600 if seconds['initial_passes'] is not None else None,
                initial_parallel_hours=initial_parallel,
                total_summed_task_hours=seconds['total'] / 3600 if seconds['total'] is not None else None,
                sequential_phase_parallel_hours=(initial_parallel + seconds['adjudication'] / concurrency / 3600)
                    if initial_parallel is not None and seconds['adjudication'] is not None else None,
                note='Includes observed setup/controls. Total requires measured adjudicator effort. Equal workers per role; no scaling efficiency guarantee. Provisional denominator omits unknown missing rows.'),
                bootstrap=dict(seed=2026100803, replicates=2000, unit='page', pages=pages,
                               total_interval='Page bootstrap + adjudicator task bootstrap + Jeffreys beta disagreement-rate draws; planning interval, not a population guarantee'),
                rates_assumption=rates, monetary_cost_known=projections['billed_usd']['total'] is not None)


def score(run, returns, out, adjudications=None, full_rows=11369, concurrency=1, rates=None, usage_ledger=None, printed_columns=328, total_concurrency=12):
    out = W.owned(out)
    if out.exists():
        raise FileExistsError('Use a fresh aggregate output directory')
    if full_rows < 1 or concurrency < 1:
        raise ValueError('Full rows and concurrency must be positive')
    E = W.evaluator()
    state = collect(run, returns, adjudications, usage_ledger)
    all_rows, page_disputes, coverage_rows, wrong_agreed_controls = [], defaultdict(lambda: [0, 0]), [], []
    roles, details = {}, []
    for role in ('reader-1', 'reader-2'):
        values = []
        mrows = []
        batch_accuracy = []
        strata = defaultdict(list)
        for b in state['batches']:
            data = b['readings'].get(role)
            if not data:
                continue
            rows = {r['item_id']: r for r in data['rows']}
            batch_values = []
            for item, ref in b['batch']['controls'].items():
                row = rows[item]
                fields = control_fields(row, ref)
                values.append(fields)
                batch_values.append(fields)
                truth = copy.deepcopy(ref)
                truth.update(sample_index=row['sample_index'])
                mrows.append(E.score_row(W.as_prediction(row), truth))
                key = 'ambiguous' if any(len(u['strict_candidate_codes']) > 1 for u in ref['units']) else 'singleton'
                strata[key].append(fields)
                details.append(dict(role=role, batch_id=b['batch']['batch_id'], item_id=item, reference_sample_index=ref['sample_index'], fields=fields))
            batch_accuracy.append(dict(batch_id=b['batch']['batch_id'], controls=len(batch_values),
                                       fields={k: E.wilson(sum(v[k] for v in batch_values), len(batch_values)) for k in batch_values[0]}))
        roles[role] = dict(assigned_controls=sum(len(b['batch']['controls']) for b in state['batches']), evaluated_controls=len(values),
                           fields={k: E.wilson(sum(v[k] for v in values), len(values)) for k in ('number', 'classification', 'count', 'crop', 'strict_sequence', 'unit_kind_and_underline', 'all_required_fields')},
                           by_batch=batch_accuracy,
                           ambiguity_strata={k: E.wilson(sum(v['all_required_fields'] for v in vs), len(vs)) for k, vs in strata.items()},
                           package_m_compatibility=E.aggregate(mrows) if mrows else None)
    for b in state['batches']:
        rows, coverage = comparison(b)
        all_rows.extend(rows)
        coverage_rows.append(dict(batch_id=b['batch']['batch_id'], both_valid_returns=len(b['readings']) == 2,
                                  source_column_complete=coverage,
                                  inventories={role: data['columns'] for role, data in b['readings'].items()}))
        for r in rows:
            if r['control'] and r['agrees']:
                ref = b['batch']['controls'][r['item_id']]
                if not control_fields(r['a'], ref)['all_required_fields']:
                    wrong_agreed_controls.append(dict(batch_id=b['batch']['batch_id'], item_id=r['item_id']))
            if not r['control'] and r['paired']:
                page_disputes[b['batch']['pdf_page']][0] += int(r['requires_adjudication'])
                page_disputes[b['batch']['pdf_page']][1] += 1
    targets = [r for r in all_rows if not r['control']]
    paired = [r for r in targets if r['paired']]
    disputed = [r for r in paired if r['requires_adjudication']]
    agreement = E.wilson(sum(r['agrees'] for r in paired), len(paired))
    load = E.wilson(len(disputed), len(paired))
    load['page_bootstrap_ci95'] = cluster_interval(list(page_disputes.values()), E)
    progress = dict(planned_batches=len(state['batches']), valid_reader_tasks=len([t for t in state['tasks'] if t['role'] != 'adjudicator']),
                    expected_reader_tasks=2 * len(state['batches']), planned_target_locators=sum(len(b['batch']['target_keys']) for b in state['batches']),
                    paired_targets=len(paired), missing_pair_targets=len(targets) - len(paired),
                    agreed_targets=sum(r['agrees'] for r in paired),
                    agreed_resolved_targets=sum(r['agrees'] and W.resolved(r['a']) for r in paired),
                    agreed_unresolved_targets=sum(r['agrees'] and not W.resolved(r['a']) for r in paired),
                    target_adjudication_queue=len(disputed), completed_column_inventories=sum(c['source_column_complete'] for c in coverage_rows),
                    invalid_returns=state['errors'], column_inventory=coverage_rows)
    screening = dict(status='Proposed', criteria={}, reason='Await complete valid pilot readings and costs')
    if len(paired) and progress['valid_reader_tasks'] == progress['expected_reader_tasks']:
        criteria = dict(no_control_number_classification_count_error=all(
            roles[r]['fields'][k]['success'] == roles[r]['fields'][k]['total'] for r in roles for k in ('number', 'classification', 'count')),
                        role_control_all_fields_at_least_95=all(roles[r]['fields']['all_required_fields']['rate'] >= .95 for r in roles),
                        no_wrong_agreed_control=not wrong_agreed_controls,
                        all_columns_complete=all(c['source_column_complete'] for c in coverage_rows))
        screening = dict(status='Verified computation' if all(criteria.values()) else 'Failed', criteria=criteria,
                         reason='Screening only; small reference controls and target agreement do not certify corpus accuracy')
    cost = costs(state['tasks'], sorted(set(b['batch']['pdf_page'] for b in state['batches'])), full_rows, concurrency, load, rates, len(state['batches']))
    cost['measured_totals'] = U.measurement(state['tasks'])
    cost['coordinator_ledger'] = state['usage_ledger']
    cost['column_task_projection'] = U.column_projection(state['tasks'], state['batches'], printed_columns, full_rows, total_concurrency)
    final_controls = []
    dispute_fields = defaultdict(int)
    for b in state['batches']:
        aj = {r['item_id']: r for r in b['adjudication']['rows']} if b['adjudication'] else {}
        for item in comparison(b)[0]:
            if item['control']:
                row = aj.get(item['item_id']) or (item['a'] if item['agrees'] else None)
                if row:
                    final_controls.append(control_fields(row, b['batch']['controls'][item['item_id']]))
            elif item['requires_adjudication']:
                for field in item['differences']:
                    dispute_fields[field] += 1
    summary = dict(status='Verified computation', reader_evaluation_status='Proposed' if not paired else 'Frozen evaluation',
                   control_accuracy=roles, target_agreement=agreement, adjudication_load=load,
                   final_control_accuracy=dict(evaluated_controls=len(final_controls), assigned_controls=sum(len(b['batch']['controls']) for b in state['batches']),
                       fields={k: E.wilson(sum(v[k] for v in final_controls), len(final_controls)) for k in ('number','classification','count','crop','strict_sequence','unit_kind_and_underline','all_required_fields')}),
                   target_dispute_fields=dict(dispute_fields),
                   wrong_agreed_controls=wrong_agreed_controls, screening=screening,
                   progress=progress, cost=cost, score_code_sha256=W.sha(__file__), workflow_sha256=W.sha(W.HERE / 'workflow.py'),
                   private_manifest_sha256=W.sha(Path(run) / 'coordinator/private-manifest.json'),
                   input_reading_hashes=[b['hashes'] for b in state['batches']],
                   estimand_note='Unseen-target agreement is measured only after paired readings; target accuracy requires independent source adjudication.')
    if state['manifest'].get('pilot_version') == 2:
        checks = dict(screening['criteria'])
        checks['all_assigned_returns_validate'] = not state['errors'] and progress['valid_reader_tasks'] == progress['expected_reader_tasks']
        checks['target_adjudication_at_most_10_percent'] = load['rate'] is not None and load['rate'] <= .10
        checks['final_controls_all_correct'] = (len(final_controls) == summary['final_control_accuracy']['assigned_controls']
                                              and bool(final_controls) and all(v['all_required_fields'] for v in final_controls))
        summary['revised_screening'] = dict(status='Proposed' if not paired else 'Verified computation' if all(checks.values()) else 'Failed', criteria=checks,
            note='Post-pilot-1 revised workflow screen; final control criterion stays false until every control has an accepted final row.')
    if any(t['evidence_status'] == 'Synthetic' for t in state['tasks']):
        summary['reader_evaluation_status'] = 'Synthetic'
        summary['screening']['status'] = 'Synthetic'
        if 'revised_screening' in summary:
            summary['revised_screening']['status'] = 'Synthetic'
    W.write(out / 'metrics.json', summary)
    W.write(out / 'progress.json', progress)
    W.write(out / 'cost-ledger.json', dict(status='Verified computation', evidence_status=summary['reader_evaluation_status'], tasks=state['tasks'], aggregate=cost))
    # Control answer indexes are sensitive; keep per-control diagnostics beside local raw inputs.
    raw_details = W.owned(Path(run) / 'coordinator' / ('control-scores-' + W.digest(W.relative(out))[:12] + '.json'))
    W.write(raw_details, dict(status='Verified computation', controls=details))
    print(json.dumps(dict(progress={k: v for k, v in progress.items() if k not in ('column_inventory', 'invalid_returns')},
                          target_agreement=agreement, adjudication_load=load, screening=screening), indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--returns', type=Path, required=True)
    parser.add_argument('--adjudications', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--full-rows', type=int, default=11369)
    parser.add_argument('--workers-per-role', type=int, default=1)
    parser.add_argument('--rates', type=Path)
    parser.add_argument('--usage-ledger', type=Path)
    parser.add_argument('--printed-columns', type=int, default=328)
    parser.add_argument('--total-concurrency', type=int, default=12)
    args = parser.parse_args()
    rates = W.read(args.rates) if args.rates else None
    if rates:
        for rate in rates['models'].values():
            for key in ('input_usd_per_million', 'cached_input_usd_per_million', 'output_usd_per_million'):
                if not W.finite_nonnegative(rate.get(key)):
                    raise ValueError('Rate card requires all three finite nonnegative rates per model')
    if args.printed_columns < 1 or args.total_concurrency < 1:
        raise ValueError('Printed columns and total concurrency must be positive')
    score(args.run, args.returns, args.out, args.adjudications, args.full_rows, args.workers_per_role, rates, args.usage_ledger, args.printed_columns, args.total_concurrency)
