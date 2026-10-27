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
# Exact, reviewed feature names determine this reference index. They are not a
# classifier for planning, a completeness score, or inferred absence.
DOMAIN_FEATURES = {
 'location_setting': 'location;location and printed coordinate;location conflict;location extent',
 'occupation_chronology': 'occupation interval;chronology model;chronology disagreement;chronology proposal;source chronology;dating convention;chronological extent;AMS method;dated charcoal;residual context problem;early occupation;new sequence;relative occupation;occupation duration missing;occupation interval missing;later settlement',
 'settlement_extent': 'area;area conflict;area scope conflict;settlement extent;site extent;town extent;extent;mound area;location extent;surface extent and destruction;citadel extent;citadel dimensions;lower city dimensions;enclosed dimensions;enclosure dimensions;fortification scale;interior area conflict;annexe dimensions',
 'excavation_coverage': 'excavated area;excavated area update;excavation exposure;preservation and exposure;room exposure;house exposure;partial house exposure;house count missing;sample count conflict;residence sample count',
 'layout_and_access': 'layout;layout maintenance;layout persistence;layout regularization;street continuity;street form;street form contrast;street count;arterial street count;street width;street widths;lane width;lanes and drainage;gate and street width;gate width;gate street convergence;entrance relocation;passage closure;local alignment adjustment;radial form;settlement form;fortification;fortification addition;fortification change;fortification rebuild;fortification reuse;fortification sequence;fortification rebuilding;fortification missing;wall extent;wall line retention;retained plan;plan retention;open-space dimensions;open-space occupation;interruption and replanning;replanning;clearance and replanning;unresolved boundary;source direction conflict',
 'building_inventory': 'house form change;house material and amenities;house exposure;partial house exposure;housing block count;block count;storage cell count;house workshop association;room and hearth counts;room exposure;burning features;bathing platform count;bathing platform;reservoir count;well count;well count estimate;kiln;early dwelling;complex enlargement;platform count;platform dimensions;platform height;rectangular block count;residence definition;median residence area;dam count;craft zoning;reuse structures',
 'construction_materials': 'construction material;building material;building materials;house material;house material and amenities;fortification material;founding enclosure material;stone construction;waterproofing material;early house material;fired brick adoption;brick dimensions;construction change;retaining wall;architecture material;architecture material change;annexe enclosure',
 'water_and_sanitation': 'well count;well exposure;well missing;well catchment estimate;well count estimate;well dimensions;reservoir area;reservoir count;dam count;drainage;drain dimensions;drain maintenance;drain rebuilding;gate drain rebuilding;lane drainage;lanes and drainage;sanitation;sanitation layout;sanitation maintenance;hydraulic rebuilding;water structure dimensions;bathing platform;bathing platform count;waterproofing material;basin construction;flood protection',
 'incremental_alteration': 'extra mural growth;residential expansion;street encroachment;named street encroachment;street side platforms;open-space occupation;lane occupation;complex enlargement;encroachment record;passage closure;urban contraction',
 'replanning_and_retention': 'replanning;clearance and replanning;interruption and replanning;layout regularization;layout maintenance;layout persistence;plan retention;retained plan;wall line retention;rebuilding sequence;structural sequence;structural phases in sections;fortification rebuilding;fortification rebuild;fortification reuse;fortification sequence;gate drain rebuilding;hydraulic rebuilding;drain rebuilding;drain maintenance;maintenance count;rebuilding count;urban expansion;urban expansion after damage;enclosure growth;fortification addition',
 'documentary_context': 'writing carriers;inscribed carriers;inscribed object context;inscription context;seal form change',
}

def feature_key(value):
    return re.sub(r'\s+',' ',value.replace('_',' ').strip()).casefold()

DOMAINS={key:{feature_key(v) for v in values.split(';')} for key,values in DOMAIN_FEATURES.items()}
DOMAINS['quantities_and_scope']=set()
DOMAINS['phase_information']=set()

READINESS_GAPS={
 'contemporary_building_census':'No phase-contemporary inventory of all buildings and its surveyed excavation denominator assembled in this bounded pass; reported blocks, rooms and estimates retain their own scope.',
 'construction_boundary':'No new independently modelled construction boundary joins a named measured wall, its construction deposit and an identified short-lived sample.',
 'phase_specific_street_graph':'No complete phase-keyed, north-referenced street and entrance graph with restoration and exposure masks assembled in this pass.',
 'comparable_documentary_density':'No matched primary-use context population with excavation volume, recovery, preservation and physical-object identity denominators assembled for cross-town frequencies.',
 'component_material_provenance':'No comparable component-level inventory of material volumes and independently established quarry or clay provenance assembled across the twelve cases.',
}

def h(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def records(path, key):
    obj=json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(obj,list): return obj
    if key in obj: return obj[key]
    if key=='sources' and 'source_records' in obj: return obj['source_records']
    raise ValueError('Unsupported record wrapper in '+str(path))

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
                    row['town_raw']=row['town']
                    if row['id']=='INS-029':
                        row['town']='multi-site'
                        row['towns']=['harappa','lahoma-lal-tibba']
                    else:
                        row['town']=normal_town(row['town'])
                        row['towns']=[row['town']]
                    if not row.get('phase'):
                        row['phase_raw']=row.get('phase')
                        row['phase']='unknown'
                        row['phase_missing_reason']=row.get('field_missing_reasons',{}).get('phase','No named construction phase joined in the inspected assertion')
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
        rows=[r for r in observations if town in r['towns']]
        if not rows: errors.append('No observations for '+town)
        domains={}
        for domain,features in DOMAINS.items():
            matched=[r for r in rows if feature_key(r['feature']) in features or
                     (domain=='documentary_context' and r['module']=='inscriptions') or
                     (domain=='quantities_and_scope' and any(k in r for k in ['quantity','value','count'])) or
                     (domain=='phase_information' and r['phase']!='unknown')]
            explicit_gaps=[r for r in matched if r.get('missing_reason') or r.get('field_missing_reasons') or re.search(r'gap|missing|unresolved',r['feature'],re.I)]
            conflicts=[r for r in matched if re.search(r'conflict|disagreement|inconsisten',r['feature']+' '+r.get('evidence_status',''),re.I)]
            status='mixed-assertions-and-limits' if matched and (explicit_gaps or conflicts) else 'indexed-assertions' if matched else 'not-indexed'
            reason='No assertion tagged to this domain in this bounded pass; this is not an archaeological absence' if not matched else None
            domains[domain]=dict(status=status,observation_ids=[r['id'] for r in matched],
                                 explicit_gap_ids=[r['id'] for r in explicit_gaps],conflict_ids=[r['id'] for r in conflicts],
                                 negative_observation_ids=[],negative_observation_status='Not adjudicated by this index',missing_reason=reason,
                                 completeness='not-assessed',scope='Reviewed feature-name reference index; chronology labels do not establish a dated architectural join')
        old=next((r for r in inherited_rows if r['town']==town),None)
        north = dict(status='inherited',source_path=logical(inherited),source_sha256=h(inherited),json_pointer=f'/towns/{inherited_rows.index(old)}',
                     latitude=old.get('latitude'),longitude=old.get('longitude'),coordinate_basis=old.get('coordinate_datum'),
                     north_readings=old.get('true_north_readings',[]),missing=old.get('missing',{})) if old else dict(status='missing',reason='No inherited town row')
        town_cards.append(dict(town=town,observation_count=len(rows),source_ids=sorted(set(r['source_id'] for r in rows)),domains=domains,
                               axis_horizon_register=north,observation_ids=[r['id'] for r in rows],research_readiness_gaps=READINESS_GAPS))
        gaps.extend(dict(town=town,domain=key,status='not-assembled-in-this-study',reason=reason,observation_ids=';'.join(r['id'] for r in rows)) for key,reason in READINESS_GAPS.items())
    durations=[]
    for row in observations:
        start=row.get('start_bce'); end=row.get('end_bce')
        if isinstance(start,(int,float)) and isinstance(end,(int,float)) and start>=end:
            start_op=row.get('start_operator','='); end_op=row.get('end_operator','=')
            durations.append(dict(observation_id=row['id'],town=row['town'],phase=row['phase'],start_bce=start,end_bce=end,
                                  start_operator=start_op,end_operator=end_op,
                                  nominal_span_years=start-end if start_op=='=' and end_op=='=' else None,
                                  continuous_occupation_years=None,source_id=row['source_id'],locator=row['locator'],dating_basis=row.get('dating_basis'),uncertainty=row.get('uncertainty'),
                                  source_chronology=row.get('chronology_numeric'),scope='Arithmetic span of closed source-model bounds only; open bounds suppress subtraction; no continuity or construction-date inference'))
        if row.get('chronology_numeric'):
            durations.append(dict(observation_id=row['id'],town=row['town'],phase=row['phase'],source_id=row['source_id'],locator=row['locator'],
                                  source_chronology=row['chronology_numeric'],nominal_span_years=None,continuous_occupation_years=None,
                                  dating_basis=row.get('dating_basis'),uncertainty=row.get('uncertainty'),scope='Original numerical chronology and conventions retained; no derived duration for historical BC or contested dates'))
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
                 core_town_assertion_links={town:sum(town in r['towns'] for r in observations) for town in TOWNS},
                 multi_site_assertions=sum(len(r['towns'])>1 for r in observations),outside_core_towns=sorted({t for r in observations for t in r['towns'] if t not in TOWNS}),
                 observations_by_module=dict(Counter(r['module'] for r in observations)),
                 required_domains=len(DOMAINS),town_domain_status_counts=dict(Counter(d['status'] for t in town_cards for d in t['domains'].values())),
                 nominal_interval_rows=len(durations),missing_or_conflicting_domain_rows=len(gaps),
                 notes=['Source-use records are not a publication count','Assertions are not independent archaeological observations','Exact reviewed feature tags form a reference index; completeness is not assessed','One multi-site assertion links Harappa and Lahoma Lal Tibba; the latter is a hinterland comparison outside the twelve-town case frame','No new town-level seal frequency, continuous occupation duration, true-north bearing or script meaning measured'])
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
