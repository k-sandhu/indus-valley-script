"""Aggregate the immutable first-pilot readings, merge and coordinator ledger."""
import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
import workflow as W
import score_pilot as S


def record(out):
    run=W.RAW/'pilot-2026-10-08-v2';returns=W.RAW/'returns-v2';adj=W.RAW/'adjudication-pilot-v1'
    state=S.collect(run,returns,adj,W.HERE/'pilot/coordinator-task-ledger-v1.jsonl')
    if state['errors']:raise ValueError(state['errors'])
    inputs=[W.HERE/'pilot/scored-initial-v1/metrics.json',W.HERE/'pilot/scored-final-v1/metrics.json',
            W.HERE/'pilot/merge-summary-v1.json',W.HERE/'pilot/PILOT-RESULTS.md',W.HERE/'pilot/coordinator-task-ledger-v1.jsonl',
            W.HERE/'pilot/coordinator-cost-projection-v1.json',W.RAW/'pilot-merge-v1/merged-records.json']
    merged=W.read(inputs[-1])['rows']
    candidate_sets=Counter();open_rows=[]
    for row in merged:
        if row['disposition']!='unresolved':continue
        final=row['final_row']
        if not final:raise ValueError('Unexpected unresolved source assignment')
        if final.get('unresolved_fields') or final.get('unresolved_boundary'):
            raise ValueError('Non-code unresolved content must be reported separately')
        for field in ('printed_inscription_id','classification_literal','drawn_unit_count','crop_correct','source_row_ordinal','source_y_pdf'):
            if final.get(field) is None:raise ValueError('Unresolved required field')
        sets=[tuple(sorted(u['strict_candidate_codes'])) for u in final['units'] if len(u['strict_candidate_codes'])>1]
        if not sets or any(not u['strict_candidate_codes'] or u['unit_kind']=='unresolved' for u in final['units']):
            raise ValueError('Unexpected unresolved unit')
        candidate_sets.update(sets);open_rows.append(row)
    groups=Counter();column_disputes=Counter();fields=Counter()
    for b in state['batches']:
        for item in S.comparison(b)[0]:
            if item['control'] or not item['requires_adjudication']:continue
            column_disputes[b['batch']['batch_id']]+=1;fields.update(item['differences'])
            found=set()
            for a,z in zip(item['a']['units'],item['b']['units']):
                ac,bc=set(a['strict_candidate_codes']),set(z['strict_candidate_codes'])
                if ac!=bc:
                    union=ac|bc
                    if any(union==pair for pair in ({8,764},{9,765},{10,766},{543,769},{501,768})):found.add('coincident_stroke_pair')
                    if union <= {597,598}:found.add('597_598_spacing')
                    if union <= {205,206,208} or union <= {465,485,486}:found.add('U_or_comb_chart_labels')
                    if union <= {58,68}:found.add('58_68_rectangle')
                    if union <= {235,593}:found.add('235_593_bow_tie')
                    if union <= {126,443}:found.add('126_443_Y')
                if a['unit_kind']!=z['unit_kind'] and (ac|bc)&{596,454}:found.add('596_454_unit_kind')
            if 'source_y_pdf' in item['differences']:found.add('source_y_pdf')
            groups.update(found)
    roles={}
    for role in ('reader-1','reader-2','adjudicator'):
        tasks=[t for t in state['tasks'] if t['role']==role];seconds=[t['elapsed_seconds'] for t in tasks];tokens=[t['combined_tokens'] for t in tasks]
        roles[role]=dict(tasks=len(tasks),assigned_rows=sum(t['submitted_rows'] for t in tasks),target_rows=sum(t['target_rows'] for t in tasks),
                        combined_tokens=sum(tokens),elapsed_seconds=sum(seconds),mean_task_seconds=statistics.mean(seconds),median_task_seconds=statistics.median(seconds),
                        mean_task_tokens=statistics.mean(tokens),tokens_range=[min(tokens),max(tokens)],seconds_range=[min(seconds),max(seconds)])
    result=dict(status='Verified computation',reading_status='Frozen evaluation',screening_status='Failed',
                targets=len(merged),dispositions=dict(Counter(r['disposition'] for r in merged)),candidate_only_open_rows=len(open_rows),
                candidate_sets_total=sum(candidate_sets.values()),candidate_sets=[dict(codes=list(k),units=v) for k,v in sorted(candidate_sets.items())],
                dispute_patterns=dict(groups),pattern_method='Overlapping row counts from initial unequal strict sets/unit kinds; no source re-reading',
                target_disputes_by_column=dict(column_disputes),target_dispute_fields=dict(fields),tasks=roles,
                measured_combined_tokens=sum(t['combined_tokens'] for t in state['tasks']),measured_agent_seconds=sum(t['elapsed_seconds'] for t in state['tasks']),
                tokens_per_target=sum(t['combined_tokens'] for t in state['tasks'])/len(merged),
                coordinator_projection=W.read(W.HERE/'pilot/coordinator-cost-projection-v1.json')['full_run'],
                inputs={W.relative(p):W.sha(p) for p in inputs},raw_manifest_sha256=W.sha(run/'coordinator/private-manifest.json'))
    W.write(out,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','coordinator_projection')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();record(a.out)
