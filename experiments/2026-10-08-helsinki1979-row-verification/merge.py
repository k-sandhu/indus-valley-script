"""Merge source records with preserved candidate sets and ledger staging rows."""
from __future__ import annotations
import argparse
import copy
from collections import Counter, defaultdict
from pathlib import Path
import workflow as W
import score_pilot as S
import usage_ledger as U


def merge(run, returns, out, summary_out, adjudications=None, usage_ledger=None):
    out = W.owned(out)
    if not out.is_relative_to(W.RAW) or out.exists():
        raise ValueError('Use a fresh local raw merge directory')
    state = S.collect(run, returns, adjudications, usage_ledger)
    records, false_targets, batch_progress = [], [], []
    for b in state['batches']:
        rows, initial_coverage = S.comparison(b)
        aj = {r['item_id']: r for r in b['adjudication']['rows']} if b['adjudication'] else {}
        decisions = []
        for item in rows:
            if item['control']:
                continue
            iid = item['item_id']
            row = aj.get(iid) or (item['a'] if item['agrees'] else None)
            status = 'adjudicated' if iid in aj and W.resolved(row) else 'agreed' if item['agrees'] and W.resolved(row) else 'unresolved'
            candidates = [copy.deepcopy(r) for r in (item['a'], item['b'], aj.get(iid)) if r]
            provenance = dict(disposition=status, batch_id=b['batch']['batch_id'], item_id=iid,
                              evidence_status='Synthetic' if any(d['evidence_status'] == 'Synthetic' for d in b['readings'].values()) else 'Frozen evaluation',
                              proposal_occurrence_key=b['batch']['target_keys'].get(iid),
                              packet_hashes={role: p['packet_sha256'] for role, p in b['packet'].items()},
                              reading_hashes=b['hashes'], differences=item['differences'])
            if b['packet']['reader-2'].get('chart_reference'):
                provenance['chart_reference'] = b['packet']['reader-2']['chart_reference']
            if row and row.get('valid_printed_target') is False:
                false_targets.append(dict(provenance=provenance, final_row=row, candidate_readings=candidates))
                continue
            # An unresolved assignment keeps the original locator identity until adjudicated.
            ordinals = {r.get('source_row_ordinal') for r in candidates if r.get('valid_printed_target')}
            ordinal = row.get('source_row_ordinal') if row else next(iter(ordinals)) if len(ordinals) == 1 else None
            key = (f'helsinki1979:pdf{b["batch"]["pdf_page"]}:c{b["batch"]["pdf_column"]}:source-r{ordinal}'
                   if ordinal is not None else f'pending-source-assignment:{b["batch"]["batch_id"]}:{iid}')
            decisions.append(dict(source_occurrence_id=key, disposition=status, final_row=row,
                                  candidate_readings=candidates, provenance=provenance))
        grouped = defaultdict(list)
        for d in decisions:
            grouped[d['source_occurrence_id']].append(d)
        combined = []
        for key, ds in grouped.items():
            if len(ds) == 1:
                combined.append(ds[0])
            else:
                combined.append(dict(source_occurrence_id=key, disposition='unresolved', final_row=None,
                                     candidate_readings=[r for d in ds for r in d['candidate_readings']],
                                     provenance=dict(disposition='unresolved', collision='multiple locators claim same printed occurrence',
                                                     contributing_records=[d['provenance'] for d in ds])))
        # A reconciled inventory can come from adjudication after it read all queued targets.
        inventory = b['adjudication'] if b['adjudication'] and b['adjudication'].get('columns') else None
        covered = initial_coverage or bool(inventory and W.inventory_complete(inventory, b['batch']))
        expected = inventory['columns'][0]['numbered_occurrences'] if inventory else (
            b['readings'].get('reader-1', {}).get('columns', [{}])[0].get('numbered_occurrences'))
        # Source coverage and unresolved code/field content are separate checks.
        # One ambiguous code set must not invalidate other resolved source rows.
        assigned_ordinals = sorted(int(d['source_occurrence_id'].rsplit('source-r', 1)[1])
                                   for d in combined if ':source-r' in d['source_occurrence_id'])
        source_coverage = bool(covered and expected is not None and assigned_ordinals == list(range(1, expected + 1))
                               and not any(d['provenance'].get('collision') for d in combined)
                               and not any(d['disposition'] != 'adjudicated' and
                                   {'source_row_ordinal', 'source_y_pdf'}.intersection(d['provenance'].get('differences', [])) for d in combined))
        complete = source_coverage and all(d['disposition'] != 'unresolved' for d in combined)
        if not source_coverage:
            # Preserve resolved row status, but block column-level completeness and accepted ledger output.
            for d in combined:
                d['provenance']['column_complete'] = False
        else:
            for d in combined:
                d['provenance']['column_complete'] = True
        records.extend(combined)
        batch_progress.append(dict(batch_id=b['batch']['batch_id'], source_inventory_reconciled=covered,
                                    source_coverage_complete=source_coverage,
                                    expected_occurrences=expected, merged_records=len(combined), complete=complete))
    evidence_status = 'Synthetic' if any(t['evidence_status'] == 'Synthetic' for t in state['tasks']) else 'Proposed' if not state['tasks'] else 'Frozen evaluation'
    W.write(out / 'merged-records.json', dict(status='Verified computation', reader_status=evidence_status,
                                            source_sha256=state['manifest']['source_sha256'], rows=records))
    W.write(out / 'false-locators.json', dict(rows=false_targets))
    ledger = [W.ledger_row(d['final_row'], d['provenance']) for d in records
              if d['disposition'] in ('agreed', 'adjudicated') and d['provenance'].get('column_complete')]
    W.write_text(out / 'ledger-staging.jsonl', ''.join(__import__('json').dumps(row, ensure_ascii=False) + '\n' for row in ledger))
    summary = dict(status='Verified computation', reader_status=evidence_status,
                   merged_records=len(records), dispositions=dict(Counter(r['disposition'] for r in records)),
                   false_locators=len(false_targets), ledger_staging_rows=len(ledger), real_ledger_imports=0,
                   control_items_excluded=sum(len(b['batch']['controls']) for b in state['batches']),
                   columns=batch_progress, invalid_returns=state['errors'], raw_output=W.relative(out),
                   merged_sha256=W.sha(out / 'merged-records.json'), ledger_staging_sha256=W.sha(out / 'ledger-staging.jsonl'),
                   script_sha256=W.sha(__file__), note='Staging requires reviewed object/surface concordance before Package L import.')
    summary['cost'] = dict(measured_totals=U.measurement(state['tasks']), coordinator_ledger=state['usage_ledger'])
    W.write(out / 'task-cost-ledger.json', dict(tasks=state['tasks'], aggregate=summary['cost']))
    W.write(summary_out, summary)
    print(f'Merged {len(records)} records; staged {len(ledger)} rows; imported 0')
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--returns', type=Path, required=True)
    p.add_argument('--adjudications', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--summary-out', type=Path, required=True)
    p.add_argument('--usage-ledger', type=Path)
    args = p.parse_args()
    merge(args.run, args.returns, args.out, args.summary_out, args.adjudications, args.usage_ledger)
