"""Join separately coded, frozen modules without inventing missing observations."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
MODULES = ('plans-east', 'plans-west', 'contexts', 'mohenjo-control')
PRIMARY = ('farmana', 'kanmer', 'banawali', 'harappa', 'dholavira', 'lothal')

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))

def rows(value, key):
    return value if isinstance(value, list) else value[key]

def common_measurement(module, row):
    out = {'id': f'{module}::{row["id"]}', 'module':module,
           'town':row['town'].lower(), 'source_record':row,
           'source_ref':f'{module}::{row["source_id"]}',
           'eligible_persistence_episode':False}
    if module == 'plans-east':
        out.update(value=row['value'], unit=row['unit'], reading_bound=row['reading_bound'],
                   feature=row['description'],phase=row['phase'],north_reference=row['north_reference'])
    elif module == 'plans-west':
        out.update(value=row['metres'],unit='m',reading_bound=row['digitization_sensitivity_metres'],
                   feature=row['feature'],phase=row['phase'],north_reference=row['north_reference'])
    else:
        out.update(value=row['estimate_m'],unit='m',
                   reading_bound=[row.get('combined_reading_lower_m',row['reading_lower_m']),
                                  row.get('combined_reading_upper_m',row['reading_upper_m'])],
                   feature=row['feature'],phase=row['phase_raw'],north_reference=row['north_reference'])
    return out

def main(tag):
    out=P/f'run-{tag}.json'
    if out.exists(): raise FileExistsError('Preserve existing run; use a new tag.')
    inputs = [P/x for x in ('PROTOCOL.md','PROTOCOL.sha256.json','AMENDMENT-01.md',
                            'AMENDMENT-01.sha256.json','EXPOSURE.json','MEASUREMENT-RULES.md',
                            'measurement-controls-v1.json','bench-shots-synthetic-v1.json',
                            'lothal-recount-v1.json')]
    sources=[]
    source_checks=[]
    cached_hashes={}
    for module in MODULES:
        f=P/'modules'/module/'sources.json';inputs.append(f)
        for item in rows(read(f),'sources'):
            sid=item.get('id', item.get('source_id'))
            assert sid is not None
            record={'source_ref':f'{module}::{sid}','module':module,**item}
            sources.append(record)
            physical=item.get('physical_path')
            expected=item.get('sha256')
            if physical and expected:
                path=Path(physical)
                if physical not in cached_hashes:
                    cached_hashes[physical]=sha(path) if path.is_file() else None
                actual=cached_hashes[physical]
                source_checks.append({'source_ref':record['source_ref'],'physical_path':physical,
                                      'expected_sha256':expected,'actual_sha256':actual,
                                      'passed':actual==expected})
    measured=[]
    unmeasured=[]
    east=read(P/'modules/plans-east/measurements.json')
    west=read(P/'modules/plans-west/measurements.json')
    md=read(P/'modules/mohenjo-control/measurements.json')
    for module, data, key in [('plans-east',east,'measured'),('plans-west',west,'measurements'),
                              ('mohenjo-control',md,'rows')]:
        inputs.append(P/'modules'/module/'measurements.json')
        for row in data[key]:
            if module == 'mohenjo-control' and row.get('estimate_m') is None:
                unmeasured.append({'module':module,'source_record':row})
            else: measured.append(common_measurement(module,row))
    for key in ('unmeasured_candidates','withdrawn_after_visual_review'):
        unmeasured.extend({'module':'plans-east','category':key,'source_record':r} for r in east[key])
    episodes=[]
    for module in ('plans-east','plans-west'):
        f=P/'modules'/module/'episodes.json';inputs.append(f)
        for row in rows(read(f),'episodes'):
            episodes.append({'module':module,'source_record':row})
    contexts=read(P/'modules/contexts/context-joins.json')
    dates=read(P/'modules/contexts/date-evidence.json')
    eligibility=read(P/'modules/contexts/eligibility-summary.json')
    dhol=read(P/'modules/contexts/dholavira225-summary.json')
    loth=read(P/'modules/contexts/lothal-denominators.json')
    for name in ('context-joins.json','date-evidence.json','eligibility-summary.json',
                 'dholavira225-summary.json','lothal-denominators.json','context-freeze.json'):
        inputs.append(P/'modules/contexts'/name)
    clar=P/'modules/contexts/CLARIFICATION-01.json'
    if clar.exists():inputs.append(clar)
    for module in MODULES:
        for name in ('inventory-freeze.json','INVENTORY-v1.json','module-freeze.json','plan-panels.json','visual-assets.json'):
            f=P/'modules'/module/name
            if f.exists():inputs.append(f)
    source_refs={s['source_ref'] for s in sources}
    assert len(source_refs)==len(sources), 'Source IDs collide within module'
    assert all(m['source_ref'] in source_refs for m in measured)
    assert all(m['reading_bound'][0] <= m['value'] <= m['reading_bound'][1] for m in measured)
    assert eligibility['C0018_qualified_matched_pairs']==0
    assert eligibility['C0019_qualified_work_allocation_pairs']==0
    assert west['decision']['C0017_P1_eligible_episodes']==0
    assert md['independent_episodes_for_p1']==0
    assert all(not e.get('eligible_independent_episode_for_P1',False) for e in rows(read(P/'modules/plans-east/episodes.json'),'episodes'))
    counted_determinations=sum(bool(r.get('determination_as_reported')) for r in dates['records'])
    assert counted_determinations == 76
    # Specific field semantics differ for TL; use the independently authored module's
    # explicit76/2 classification, and retain all original date fields for audit.
    decisions=[
      {'claim':'C-0017 P1','required':'12 independent episodes / 4 towns, complete common windows, preservation controls and power; route-minus-partition persistence >=0.25',
       'eligible':0,'effect':None,'status':'not estimable','reason':'No source pair supplies comparable complete route and partition inventories, despite one grid-registered descriptive pair.'},
      {'claim':'C-0017 P2','required':'6 directly joined repair episodes / 3 towns, with >=4 usable local component connections',
       'eligible':0,'effect':None,'status':'entry gate unmet','reason':'Local additions and service continuities lack the complete matched component/repair design; a visible addition is not a qualified P2 unit.'},
      {'claim':'C-0017 P3','required':'Independent construction/repair dates; frozen network prediction compared with distance and engineering',
       'eligible':0,'effect':None,'status':'not estimable','reason':'No jointly assembled dated repair-network panel. Reported sample determinations remain separate from event dates.'},
      {'claim':'C-0018','required':'20 matched primary-use/custody-change pairs /4 towns, adequate sensitivity; OR >=2 and interval above1',
       'eligible':0,'effect':None,'status':'entry gate unmet','reason':eligibility['decisive_missing_join']},
      {'claim':'C-0019','required':'Matched episodes plus independent physical distinction of shared work from ordinary goods allocation',
       'eligible':0,'effect':None,'status':'entry gate unmet','reason':'No qualified work-allocation pair; text contents and labour meanings are unassigned.'}]
    result={'schema_version':'1.0','experiment_id':'SHARED-INFRASTRUCTURE-PLAN-TEST-2026-10-24',
            'status_class':'exploratory','created_utc':datetime.now(timezone.utc).isoformat(),
            'authors':[{'model':'GPT-6 family; exact serving variant unavailable','harness':'Codex desktop collaboration','role':'coordinator plus three delegated agents'}],
            'primary_towns':list(PRIMARY),'supplementary_control_town':'mohenjo-daro',
            'protocol_sha256':sha(P/'PROTOCOL.md'),'amendment_sha256':sha(P/'AMENDMENT-01.md'),
            'context_prejoin_freeze':read(P/'modules/contexts/context-freeze.json'),
            'inputs':[{'path':str(f.relative_to(ROOT)).replace('\\','/'),'sha256':sha(f)} for f in dict.fromkeys(inputs)],
            'counts':{'source_use_records':len(sources),'distinct_source_payload_hashes':len({s['sha256'] for s in sources if s.get('sha256')}),
                      'measured_quantities':len(measured),'measurement_units':dict(Counter(m['unit'] for m in measured)),
                      'architectural_source_cases':len(episodes),'context_assessments':len(contexts['joins']),
                      'date_evidence_entries':len(dates['records']),'entries_with_determination_or_TL_result':76,
                      'calibrated_paragraph_entries_without_raw_BP':2,'Dholavira_rows_gated':dhol['source_rows'],
                      'Lothal_provenance_rows_recounted':loth['table_rows'],'grid_registered_descriptive_pairs':1,
                      'qualified_persistence_episodes':0,'qualified_C0018_pairs':0,'qualified_C0019_pairs':0},
            'source_use_records':sources,'source_hash_checks':source_checks,
            'measurements':measured,'unmeasured_or_withdrawn':unmeasured,
            'architectural_source_cases':episodes,'grid_registration':west['registration'],
            'context_assessments':contexts['joins'],'date_evidence':dates['records'],
            'context_eligibility':eligibility,'Dholavira_coverage':dhol,'Lothal_denominators':loth,
            'Lothal_independent_recount':read(P/'lothal-recount-v1.json'),'decisions':decisions,
            'interpretation_limits':['Quantities, source cases, catalogue rows and independent episodes are separate denominators.',
                                     'Reading bounds are conditional sensitivity bounds; source survey and compilation errors remain unknown.',
                                     'No p-value, odds ratio, wall-survival fraction or new posterior credence is calculated from ineligible units.',
                                     'Zero eligible joins is a result about the held source frame, not archaeological absence.'],
            'passed':all(x['passed'] for x in source_checks)}
    assert result['passed'], 'Source hash check failed'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(out),'sha256':sha(out),'counts':result['counts'],'passed':result['passed']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True)
    main(parser.parse_args().tag)
