"""Merge source-qualified assertions without collapsing phases or source conflicts."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import json
import re

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
TOWNS = ['mohenjo-daro','harappa','dholavira','lothal','chanhu-daro','kalibangan',
         'banawali','rakhigarhi','surkotada','kanmer','shikarpur','farmana']
DOMAINS = {
 'location_setting': r'location|setting|geograph|environment|palaeo',
 'occupation_chronology': r'occupation|chronolog|dating|radiocarbon|duration|sequence',
 'settlement_extent': r'area$|extent|enclosure_dimensions|settlement_size',
 'excavation_coverage': r'excavat.*area|coverage|sample_count|exposure',
 'layout_and_access': r'layout|street|lane|gate|access|enclosure|fortification|wall_extent|drain',
 'building_inventory': r'building|house|residen|block|room|storage|workshop|bathing|reservoir|well|drain|kiln|platform',
 'count_and_denominator': r'count|census|inventory|sample',
 'construction_materials': r'material|brick|masonry|construction_change|fired_brick',
 'water_and_sanitation': r'water|well|reservoir|drain|sanitation|hydraulic|bathing|dam_|flood',
 'incremental_change': r'encroach|subdiv|infill|growth|incremental|construction_change|urban_contraction',
 'replanning_and_retention': r'replan|rebuild|retention|maintenance|persist|regulariz|enclos|fortification|clearance',
 'documentary_context': r'inscription|seal|tablet|document|writing|production|manufactur|panel|lintel|accession',
 'phase_context_join': r'context|phase|stratigr|dating|chronolog|sequence|occupation|depos|rebuild',
}

def h(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def records(path, key):
    obj=json.loads(path.read_text(encoding='utf-8-sig'))
    return obj if isinstance(obj,list) else obj[key]

def normal_town(value):
    value=value.lower().strip().replace(' ','-')
    return {'mohenjodaro':'mohenjo-daro','chanhudaro':'chanhu-daro','chanhu-daro':'chanhu-daro'}.get(value,value)

def logical(path):
    try: return Path(path).relative_to(REPO).as_posix()
    except ValueError: return str(path)

def build(out):
    out.mkdir()
    observations=[]; sources=[]; inputs=[]; errors=[]
    for module in ['western','eastern','inscriptions']:
        for filename,key in [('observations.json','observations'),('sources.json','sources')]:
            path=PACKAGE/'modules'/module/filename
            inputs.append(dict(path=logical(path),sha256=h(path)))
            for row in records(path,key):
                row=dict(row,module=module)
                if key=='sources':
                    row['source_id']=row.get('source_id',row.get('id'))
                    sources.append(row)
                else:
                    row['town']=normal_town(row['town'])
                    observations.append(row)
    for name in ['methods-sources-v1.json','methods-sources-supplement-v1.json']:
        path=PACKAGE/name
        inputs.append(dict(path=logical(path),sha256=h(path)))
        sources.extend(dict(r,module='methods') for r in records(path,'sources'))
    source_by_id={s['source_id']:s for s in sources}
    if len(source_by_id)!=len(sources): errors.append('Duplicate source-use ID')
    ids=[o['id'] for o in observations]
    if len(ids)!=len(set(ids)): errors.append('Duplicate observation ID')
    for row in observations:
        if row.get('source_id') not in source_by_id: errors.append('Unresolved source: '+row['id'])
        for key in ['id','town','feature','assertion','source_id','locator','phase','evidence_status']:
            if not row.get(key): errors.append('Empty '+key+': '+row['id'])
    inherited=REPO/'experiments/2026-10-24-q1032-town-axis-register/run-v5/town-axis-table.json'
    inherited_rows=json.loads(inherited.read_text(encoding='utf-8'))['towns']
    inputs.append(dict(path=logical(inherited),sha256=h(inherited)))
    town_cards=[]
    gaps=[]
    for town in TOWNS:
        rows=[r for r in observations if r['town']==town]
        if not rows: errors.append('No observations for '+town)
        domains={}
        for domain,pattern in DOMAINS.items():
            matched=[r for r in rows if re.search(pattern,r['feature'],re.I)]
            positive=[r for r in matched if not r.get('missing_reason') and not any(w in r['feature'] for w in ['gap','conflict','unresolved'])]
            conflicts=[r for r in matched if 'conflict' in r['feature'] or 'conflict' in r.get('evidence_status','')]
            status='conflicting-assertions' if conflicts else 'reported-assertions' if positive else 'explicit-gap' if matched else 'not-recovered'
            reason=None if positive else '; '.join(dict.fromkeys(str(r.get('missing_reason') or r['assertion']) for r in matched)) if matched else 'No checked assertion recovered for this domain in this bounded source pass'
            domains[domain]=dict(status=status,observation_ids=[r['id'] for r in matched],missing_reason=reason,
                                 completeness='Source presence only; does not establish a complete inventory or comparable denominator')
            if status!='reported-assertions': gaps.append(dict(town=town,domain=domain,status=status,reason=reason or 'Conflicting source statements retained',observation_ids=';'.join(r['id'] for r in matched)))
        old=next((r for r in inherited_rows if r['town']==town),None)
        north = dict(status='inherited',source_path=logical(inherited),source_sha256=h(inherited),json_pointer=f'/towns/{inherited_rows.index(old)}',
                     latitude=old.get('latitude'),longitude=old.get('longitude'),coordinate_basis=old.get('coordinate_datum'),
                     north_readings=old.get('true_north_readings',[]),missing=old.get('missing',{})) if old else dict(status='missing',reason='No inherited town row')
        town_cards.append(dict(town=town,observation_count=len(rows),source_ids=sorted(set(r['source_id'] for r in rows)),domains=domains,
                               axis_horizon_register=north,observation_ids=[r['id'] for r in rows]))
    durations=[]
    for row in observations:
        start=row.get('start_bce'); end=row.get('end_bce')
        if isinstance(start,(int,float)) and isinstance(end,(int,float)) and start>=end:
            durations.append(dict(observation_id=row['id'],town=row['town'],phase=row['phase'],start_bce=start,end_bce=end,
                                  nominal_span_years=start-end,source_id=row['source_id'],locator=row['locator'],dating_basis=row.get('dating_basis'),
                                  scope='Arithmetic span of source bounds; no continuity or construction-date inference'))
    source_checks=[]
    for source in sources:
        raw=source.get('physical_path')
        expected=source.get('sha256')
        if raw and expected:
            path=Path(raw.replace('\\\\','\\'))
            check=dict(source_id=source['source_id'],physical_path=str(path),exists=path.is_file(),expected_sha256=expected)
            if path.is_file():
                check['actual_sha256']=h(path)
                check['matches']=check['actual_sha256'].lower()==expected.lower()
                if not check['matches']: errors.append('Source hash mismatch: '+source['source_id'])
            else: errors.append('Source missing: '+source['source_id'])
            source_checks.append(check)
    summary=dict(status_class='source-review',scientific_confirmation=False,created_utc=datetime.now(timezone.utc).isoformat(),
                 towns=len(town_cards),observation_assertions=len(observations),source_use_records=len(sources),
                 distinct_held_file_hashes=len({s.get('sha256') for s in sources if s.get('sha256')}),
                 source_files_checked=len(source_checks),observations_by_town=dict(Counter(r['town'] for r in observations)),
                 observations_by_module=dict(Counter(r['module'] for r in observations)),
                 required_domains=len(DOMAINS),town_domain_status_counts=dict(Counter(d['status'] for t in town_cards for d in t['domains'].values())),
                 nominal_interval_rows=len(durations),missing_or_conflicting_domain_rows=len(gaps),
                 notes=['Source-use records are not a publication count','Assertions are not independent archaeological observations','Field matching is a documented feature-name index; reported-assertions does not mean field complete','No new town-level seal frequency, continuous occupation duration, true-north bearing or script meaning measured'])
    for name,data in [('observations.json',observations),('sources.json',sources),('towns.json',town_cards),('duration-spans.json',durations),('summary.json',summary),('input-manifest.json',inputs),('source-integrity.json',source_checks),('validation.json',dict(status='pass' if not errors else 'fail',errors=errors))]:
        (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (out/'observations.csv').open('w',newline='',encoding='utf-8-sig') as f:
        fields=['id','town','phase','feature','assertion','source_id','locator','evidence_status','dating_basis','uncertainty','missing_reason']
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); writer.writeheader(); writer.writerows(observations)
    with (out/'missing-fields.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=['town','domain','status','reason','observation_ids']); writer.writeheader(); writer.writerows(gaps)
    print(json.dumps(dict(summary=summary,validation=errors),indent=2))
    return 0 if not errors else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',required=True,type=Path)
    raise SystemExit(build(parser.parse_args().out))
