"""Check measured-ledger joins, preservation and pilot-2 delivery integrity."""
import argparse
import copy
import json
from pathlib import Path
from PIL import Image
import workflow as W
import usage_ledger as U
import score_pilot as S
import prepare_pilot2 as P
import adjudicate as A


def check(raw_out,out):
    raw_out=W.owned(raw_out)
    if not raw_out.is_relative_to(W.RAW) or raw_out.exists():raise ValueError('Use a fresh local raw check directory')
    raw_out.mkdir(parents=True);checks=[]
    def test(name,value):checks.append(dict(name=name,passed=bool(value)))
    follow=W.HERE/'follow-up/2026-10-08-pilot2-v1'
    pins=W.read(follow/'preservation-before.json')['files']
    test('all first-pilot frozen witnesses preserved',all(W.sha(W.ROOT/r['path'])==r['sha256'] for r in pins))
    state=S.collect(W.RAW/'pilot-2026-10-08-v2',W.RAW/'returns-v2',W.RAW/'adjudication-pilot-v1',W.HERE/'pilot/coordinator-task-ledger-v1.jsonl')
    test('all 17 first-pilot returns validate',len(state['tasks'])==17 and not state['errors'])
    test('all coordinator rows matched',len(state['usage_ledger']['matched'])==17 and not state['usage_ledger']['unmatched'])
    test('measured combined total',U.measurement(state['tasks'])['combined_tokens']['total']==6218955)
    test('measured coordinator duration',abs(U.measurement(state['tasks'])['elapsed_seconds']['total']-23373.822)<1e-8)
    test('unknown token categories remain null',all(t['usage'][k] is None for t in state['tasks'] for k in ('input_tokens','cached_input_tokens','output_tokens')))
    timing=next(t for t in state['tasks'] if t['role']=='reader-2' and t['batch_id']=='pdf170-c1')
    test('coordinator timing precedence and original witness retained',timing['elapsed_seconds']==4503.897 and timing['returned_elapsed_seconds']==1566)
    initial=S.collect(W.RAW/'pilot-2026-10-08-v2',W.RAW/'returns-v2',usage_ledger=W.HERE/'pilot/coordinator-task-ledger-v1.jsonl')
    test('initial join reports five unmatched later adjudicator entries',len(initial['usage_ledger']['unmatched'])==5 and len(initial['usage_ledger']['matched'])==12)
    final=W.read(follow/'scored-final/metrics.json')
    test('original accuracy and agreement unchanged',final['control_accuracy']==W.read(W.HERE/'pilot/scored-final-v1/metrics.json')['control_accuracy'] and final['target_agreement']['success']==185 and final['adjudication_load']['success']==31)
    test('final control score explicitly 18 of 18',final['final_control_accuracy']['fields']['all_required_fields']['success']==18)
    oldmerge=W.read(W.HERE/'pilot/merge-summary-v1.json');newmerge=W.read(follow/'merge-summary.json')
    test('merge rows and staging byte-identical',all(oldmerge[k]==newmerge[k] for k in ('merged_sha256','ledger_staging_sha256','merged_records','dispositions','ledger_staging_rows')))
    test('merge receives same measured tokens',newmerge['cost']['measured_totals']['combined_tokens']['total']==6218955)
    proj=U.column_projection(state['tasks'],state['batches'],328,11702,12)
    test('column projection deterministic',proj==U.column_projection(state['tasks'],state['batches'],328,11702,12))
    test('column projection includes measured combined tokens and unknown bills',proj['metrics']['combined_tokens']['ci95_median'] is not None and proj['metrics']['billed_usd']['ci95_median'] is None)
    test('projection denominator and disputed-column count',proj['reader_tasks']==656 and proj['pilot_disputed_columns']==5)
    # Invalid ledger inputs must fail instead of silently changing a measurement.
    first=json.loads((W.HERE/'pilot/coordinator-task-ledger-v1.jsonl').read_text().splitlines()[0])
    one=[copy.deepcopy(next(t for t in state['tasks'] if t['role']==first['role'] and t['batch_id']==first['batch_id']))]
    cases={}
    for name,field,value in [('negative tokens','subagent_total_tokens',-1),('fractional tokens','subagent_total_tokens',1.5),
                             ('boolean tokens','subagent_total_tokens',True),('negative duration','duration_ms',-1),
                             ('stale run','run_id','another-run'),('wrong provider','provider','another-provider'),
                             ('wrong model','model','another-model'),('wrong packet pin','packet_sha256','wrong'),
                             ('wrong return pin','return_sha256','wrong'),('missing source','source','')]:
        row=copy.deepcopy(first);row[field]=value;cases[name]=[row]
    cases['duplicate ledger key']=[first,first]
    conflict=copy.deepcopy(first);conflict['combined_tokens']=first['subagent_total_tokens']+1;cases['conflicting totals']=[conflict]
    conflict=copy.deepcopy(first);conflict['elapsed_seconds']=1;cases['conflicting durations']=[conflict]
    for i,(name,rows) in enumerate(cases.items()):
        path=raw_out/f'bad-ledger-{i}.jsonl';W.write_text(path,''.join(json.dumps(r)+'\n' for r in rows))
        try:U.attach(copy.deepcopy(one),path);failed=False
        except ValueError:failed=True
        test('reject '+name,failed)
    good=copy.deepcopy(first);good['combined_tokens']=0;good.pop('subagent_total_tokens');good.pop('duration_ms');good['elapsed_seconds']=0
    path=raw_out/'zero-ledger.jsonl';W.write_text(path,json.dumps(good)+'\n');zero=copy.deepcopy(one);U.attach(zero,path)
    test('zero measured usage remains measured',zero[0]['combined_tokens']==0 and zero[0]['elapsed_seconds']==0)
    run=W.RAW/'pilot2-2026-10-08-v1';manifest=W.read(run/'coordinator/private-manifest.json');summary=W.read(W.HERE/'pilot-2/2026-10-08-v1/preparation.json')
    selection=P.select()
    test('seeded selection reproduces',selection==manifest['selection'] and selection['selected_pages']==[152,162])
    test('both fresh pages excluded from every known use',not set(selection['selected_pages'])&{int(k) for k in selection['excluded_pages']})
    test('v3 proposal/source/chart dependencies remain pinned',all(W.sha(W.ROOT/k)==v for k,v in manifest['dependencies'].items()))
    test('pilot 2 remains unrun',not (W.RAW/'pilot2-returns-2026-10-08-v1').exists())
    test('second pilot dimensions',summary['target_detected_rows']==144 and summary['columns']==4 and summary['controls_per_role']==12)
    oldrefs={r['sample_index']:r for r in W.read(W.V2/'blind/adjudicated-reference.json')['rows']}
    test('new controls preserve complete v2 answers without remapping',all(r==oldrefs[r['sample_index']] for b in manifest['batches'] for r in b['controls'].values()))
    test('controls distinct within second pilot',len({r['sample_index'] for b in manifest['batches'] for r in b['controls'].values()})==12)
    packets=[]
    for b in manifest['batches']:
        for role in ('reader-1','reader-2'):
            packet=W.check_packet(W.ROOT/b['packets'][role]['path']);packets.append(packet)
            test('packet and asset pins '+role+' '+b['batch_id'],packet['packet_sha256']==b['packets'][role]['sha256'])
            test('blind delivery '+role+' '+b['batch_id'],packet['proposals'] is None and packet['reader_mode']=='blind' and not list((run/role).rglob('proposals*')))
    test('both roles receive identical image/chart assets',all({a['path']:a['sha256'] for a in packets[i]['assets'] if a['path']!='../INSTRUCTIONS.md'}==
        {a['path']:a['sha256'] for a in packets[i+1]['assets'] if a['path']!='../INSTRUCTIONS.md'} for i in range(0,len(packets),2)))
    labels=W.read(run/'reader-1/charts/chart-labels-v2.1.json')['rows']
    test('all new labels match P v2.1',labels==W.read(P.CHART)['rows'] and len(labels)==687)
    panels_equal=True
    for start in range(0,len(labels),60):
        old=Image.open(W.V2/'blind/position-chart'/f'chart_{start:03d}.png').convert('RGB')
        new=Image.open(run/'reader-1/charts'/f'chart_{start:03d}.png').convert('RGB')
        for i in range(min(60,len(labels)-start)):
            x,y=(i%10)*120,(i//10)*200;xx,yy=(i%10)*160,(i//10)*220
            panels_equal &= old.crop((x+8,y+8,x+110,y+86)).tobytes()==new.crop((xx+20,yy+8,xx+122,yy+86)).tobytes()
    test('all 687 original glyph panels preserved',panels_equal)
    test('confidence notice and 33 medium labels included',sum(r['numeric_confidence']=='medium' for r in labels)==33 and (run/'reader-1/charts/CHART-NOTICE.md').exists())
    # Constructed rows exercise the new adjudication route; they are not source readings.
    returns=raw_out/'synthetic-returns';b=manifest['batches'][0]
    for role in ('reader-1','reader-2'):
        packet=W.check_packet(W.ROOT/b['packets'][role]['path']);data=W.template(packet)
        data.update(evidence_status='Synthetic',reader=dict(provider='software fixture',model='synthetic',model_version=None,run_id=role+'-fixture',independence_attestation='Constructed software rows; no source reading'),
                    started_utc='2026-10-08T00:00:00Z',finished_utc='2026-10-08T00:00:00Z',elapsed_seconds=0)
        target_items=sorted([i for i in packet['items'] if i['item_id'] in b['target_keys']],key=lambda i:i['target_y_pdf'])
        ordinals={i['item_id']:j+1 for j,i in enumerate(target_items)}
        for row in data['rows']:
            loc=next(i for i in packet['items'] if i['item_id']==row['item_id'])
            row.update(source_row_ordinal=ordinals.get(row['item_id'],1),source_y_pdf=loc['target_y_pdf'],printed_inscription_id='1',classification_literal='11 40',drawn_unit_count=1,
                       crop_correct=True,units=[dict(strict_candidate_codes=[143 if role=='reader-2' and row['item_id']==target_items[0]['item_id'] else 144],unit_kind='sign',underline_dashes=False)],
                       source_observations='Synthetic fixture; values do not transcribe this source')
        data['columns'][0].update(numbered_occurrences=36,continuation_lines=0,coverage_complete=True,observed_page_columns=2,source_observations='Synthetic complete inventory')
        test('constructed new-format return validates '+role,not W.validate_return(data,packet,W.code_universe(packet)))
        W.write(returns/role/(b['batch_id']+'.json'),data)
    adjud=raw_out/'synthetic-adjudication';A.prepare(run,returns,adjud)
    packet=W.check_packet(adjud/'adjudicator'/b['batch_id']/'packet.json')
    test('adjudicator receives revised instructions',(adjud/'adjudicator/INSTRUCTIONS.md').read_text(encoding='utf-8')==(P.GUIDANCE/'adjudication/INSTRUCTIONS.md').read_text(encoding='utf-8'))
    test('adjudicator receives pinned v2.1 vocabulary and confidence notice',packet['chart_reference']==packets[0]['chart_reference'] and packet['chart_code_universe']==packets[0]['chart_code_universe'] and
         any(a['path'].endswith('CHART-NOTICE.md') for a in packet['assets']))
    reading=W.read(adjud/'adjudicator'/b['batch_id']/'readings.json')
    test('anonymous readings omit identity and usage',all('reader' not in x and 'usage' not in x for r in reading['rows'].values() for x in (r['A'],r['B'])))
    fixture_score=S.score(run,returns,raw_out/'synthetic-score',full_rows=11702)
    test('new pilot screening preserves synthetic status',fixture_score['reader_evaluation_status']=='Synthetic' and fixture_score['revised_screening']['status']=='Synthetic')
    result=dict(status='Verified computation' if all(c['passed'] for c in checks) else 'Failed',checks=checks,passed=sum(c['passed'] for c in checks),total=len(checks),
                evidence_status='Synthetic for constructed adjudication fixtures; Verified computation for hash and measured-usage checks',source_readings_performed=0,
                preserved_files=len(pins),glyph_panels_compared=687,raw_directory=W.relative(raw_out),script_sha256=W.sha(__file__))
    W.write(out,result);print(f"{result['passed']}/{result['total']} checks passed")
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw-out',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=check(a.raw_out,a.out);raise SystemExit(0 if result['status']=='Verified computation' else 1)
