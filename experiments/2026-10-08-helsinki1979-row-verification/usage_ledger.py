"""Join coordinator measurements without inventing input/output token splits."""
from __future__ import annotations
import copy
import json
import random
from pathlib import Path
import workflow as W


def attach(tasks, path):
    if path is None:
        return None
    entries = []
    seen = set()
    for line_number, line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        key = tuple(row.get(k) for k in ('role', 'batch_id', 'run_id'))
        if any(not isinstance(k, str) or not k for k in key) or key[0] not in ('reader-1', 'reader-2', 'adjudicator'):
            raise ValueError(f'Ledger line {line_number}: role/batch/run required')
        if key in seen:
            raise ValueError(f'Duplicate coordinator ledger key: {key}')
        seen.add(key)
        total = row.get('combined_tokens', row.get('subagent_total_tokens'))
        if type(total) is not int or total < 0:
            raise ValueError(f'Ledger line {line_number}: nonnegative integer combined token total required')
        if 'combined_tokens' in row and 'subagent_total_tokens' in row and row['combined_tokens'] != row['subagent_total_tokens']:
            raise ValueError('Conflicting combined token totals')
        for field in ('duration_ms', 'elapsed_seconds', 'billed_usd'):
            if row.get(field) is not None and not W.finite_nonnegative(row[field]):
                raise ValueError(f'Invalid coordinator {field}')
        if row.get('duration_ms') is not None and row.get('elapsed_seconds') is not None and abs(row['duration_ms']/1000-row['elapsed_seconds']) > .001:
            raise ValueError('Conflicting coordinator durations')
        if not isinstance(row.get('source'), str) or not row['source'].strip():
            raise ValueError('Coordinator ledger must name its measurement source')
        entries.append((key, row, total, line_number))
    by_key = {(t['role'], t['batch_id'], t['reader']['run_id']): t for t in tasks}
    matched, unmatched = [], []
    for key, row, total, line in entries:
        task = by_key.get(key)
        if task is None:
            # A matching batch/role with another run is a dangerous stale ledger.
            if any(t['role'] == key[0] and t['batch_id'] == key[1] for t in tasks):
                raise ValueError(f'Coordinator run identity differs for {key[:2]}')
            unmatched.append(dict(role=key[0], batch_id=key[1], run_id=key[2], line=line))
            continue
        for field in ('provider', 'model_version'):
            if row.get(field) is not None and row[field] != task['reader'].get(field):
                raise ValueError(f'Coordinator {field} differs for {key}')
        if row.get('model'):
            model, version = task['reader']['model'], task['reader'].get('model_version')
            if row['model'] != model and not (version and (row['model'] == version or row['model'].startswith(version+' '))):
                raise ValueError(f'Coordinator model differs for {key}')
        for field in ('packet_sha256', 'return_sha256'):
            if row.get(field) is not None and row[field] != task[field]:
                raise ValueError(f'Coordinator {field} differs for {key}')
        task['returned_elapsed_seconds'] = task['elapsed_seconds']
        task['returned_usage'] = copy.deepcopy(task['usage'])
        duration = row.get('elapsed_seconds', row.get('duration_ms', None))
        if row.get('elapsed_seconds') is None and row.get('duration_ms') is not None:
            duration = row['duration_ms']/1000
        if duration is not None:
            task['elapsed_seconds'] = duration
            task['timing_source'] = 'coordinator ledger'
        task['combined_tokens'] = total
        if row.get('billed_usd') is not None:
            if task['usage'].get('billed_usd') is not None and task['usage']['billed_usd'] != row['billed_usd']:
                raise ValueError(f'Coordinator bill differs for {key}')
            task['usage'] = copy.deepcopy(task['usage'])
            task['usage']['billed_usd'] = row['billed_usd']
        task['coordinator_measurement'] = dict(ledger_path=W.relative(path), ledger_sha256=W.sha(path),
                                              line=line, source=row['source'], record=row)
        matched.append(dict(role=key[0], batch_id=key[1], run_id=key[2], line=line))
    return dict(path=W.relative(path), sha256=W.sha(path), entries=len(entries), matched=matched,
                unmatched=unmatched, tasks_without_measurement=[dict(role=t['role'], batch_id=t['batch_id'], run_id=t['reader']['run_id'])
                    for t in tasks if 'coordinator_measurement' not in t],
                token_definition='Measured combined task totals; input/cached/output categories remain as returned; not a price')


def measurement(tasks):
    result = {}
    for field in ('combined_tokens', 'elapsed_seconds', 'billed_usd'):
        values = [t.get(field) if field != 'billed_usd' else t['usage'].get(field) for t in tasks]
        known = [v for v in values if v is not None]
        result[field] = dict(measured_total=sum(known) if known else None, measured_tasks=len(known), tasks=len(tasks),
                             complete=bool(tasks) and len(known) == len(tasks),
                             total=sum(known) if known and len(known) == len(tasks) else None)
    return result


def column_projection(tasks, batches, printed_columns, numbered_rows, concurrency=12):
    """Task bootstrap and disputed-column uncertainty. No token pricing inference."""
    from score_pilot import percentile, comparison
    rng = random.Random(2026100807)
    readers = [t for t in tasks if t['role'] != 'adjudicator']
    adjudicators = [t for t in tasks if t['role'] == 'adjudicator']
    complete = len(readers) == 2*len(batches) and bool(batches)
    # Controls also create adjudication tasks, so include their disputes.
    disputed = sum(any(r['requires_adjudication'] for r in comparison(b)[0]) for b in batches)
    n = len(batches)
    metrics = {}
    for field in ('combined_tokens', 'elapsed_seconds', 'billed_usd'):
        def value(t):
            return t['usage'].get(field) if field == 'billed_usd' else t.get(field)
        draws = []
        if complete and adjudicators and all(value(t) is not None for t in tasks):
            for _ in range(4000):
                initial = sum(sum(value(rng.choice([t for t in readers if t['role']==role])) for __ in range(len(batches)))/len(batches)
                              for role in ('reader-1', 'reader-2')) * printed_columns
                amean = sum(value(rng.choice(adjudicators)) for __ in adjudicators)/len(adjudicators)
                draws.append(initial + printed_columns*rng.betavariate(disputed+.5,n-disputed+.5)*amean)
        interval = [percentile(draws,.025),percentile(draws,.5),percentile(draws,.975)] if draws else None
        metrics[field] = dict(ci95_median=interval, measured_metric=measurement(tasks)[field])
    seconds = metrics['elapsed_seconds']['ci95_median']
    return dict(status='Exploratory', seed=2026100807, replicates=4000,
                numbered_occurrences=numbered_rows, printed_columns=printed_columns, reader_tasks=2*printed_columns,
                pilot_columns=n, pilot_disputed_columns=disputed, concurrency=concurrency,
                metrics=metrics, agent_hours_ci95_median=[v/3600 for v in seconds] if seconds else None,
                ideal_wall_hours_ci95_median=[v/3600/concurrency for v in seconds] if seconds else None,
                assumptions='One task per column per blind/assisted role, one adjudication task per disputed column including controls. Role-stratified reader task bootstrap, adjudicator task bootstrap, Jeffreys disputed-column share. Observed setup/controls included; column lengths and continuation effort assumed exchangeable with sampled tasks. Ideal wall time divides summed effort by concurrency; excludes rate limits, scheduling and phase dependencies. Combined tokens cannot determine dollars.')
