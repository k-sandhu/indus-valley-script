"""Reconcile town-axis observations without refitting a scientific hypothesis."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / 'experiments/2026-10-24-q1032-town-axis-register'
OLD = ROOT / 'experiments/2026-10-21-town-axes'
VERIFY = ROOT / 'experiments/2026-10-21-town-orientations-verification'
REG = ROOT / 'experiments/2026-10-21-plan-registration'
INPUTS = {}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    p = Path(p)
    INPUTS[p.relative_to(ROOT).as_posix()] = digest(p)
    return json.loads(p.read_text(encoding='utf-8-sig'))

def ref(p, pointer=''):
    return dict(path=Path(p).relative_to(ROOT).as_posix(), json_pointer=pointer,
                sha256=INPUTS.get(Path(p).relative_to(ROOT).as_posix()) or digest(p))

def num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) else None

def fold(x):
    return (x + 45) % 90 - 45

def distance(a, b):
    p, q = map(math.radians, (a[0], b[0]))
    dlat, dlon = q-p, math.radians(b[1]-a[1])
    return 6371000 * 2 * math.asin(min(1, math.sqrt(math.sin(dlat/2)**2 + math.cos(p)*math.cos(q)*math.sin(dlon/2)**2)))

def write(p, x):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(x, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')

def jsonl(p, rows):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')

def csvfile(p, rows, fields):
    with p.open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k,v in row.items() if k in fields})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit('Preserve the existing output; choose a new --out.')
    sources, measurements, parts, dates, absences, horizons = [], [], [], [], [], []
    locations = defaultdict(list)
    towns = set()
    source_index = {}
    errors = []

    def add_source(row, namespace, p, pointer):
        key = str(row.get('id', row.get('source_key', len(sources))))
        sid = namespace + ':' + key
        if sid not in source_index:
            # Source metadata and original references preserve all locators without
            # republishing downloaded text or image payloads.
            keep = {k:v for k,v in row.items() if k not in ['notes','source_words','quotation']}
            source = dict(source_id=sid, metadata=keep, record=ref(p,pointer),
                          review_scope='inherited source record; see source-checks.json for pages inspected in this run')
            source_index[sid] = source
            sources.append(source)
        return sid

    oldlist = read(OLD/'towns-v1.json')
    required = {r['slug'] for r in oldlist['required']}
    for r in oldlist['required'] + oldlist['optional']:
        towns.add(r['slug'])

    cohorts = [('axes', OLD/'measure-img-A/towns'), ('axes', OLD/'measure-img-B/towns'),
               ('axes', OLD/'measure-plan-A/towns'), ('axes', OLD/'measure-plan-B/towns'),
               ('verify', VERIFY/'measure-A/towns'), ('verify', VERIFY/'measure-B/towns'),
               ('registration-search', REG/'measure-S/towns')]
    for cohort, directory in cohorts:
        for p in sorted(directory.glob('*.json')):
            x = read(p)
            town = x.get('town', x.get('slug'))
            if not isinstance(town, str):
                errors.append('Missing town: ' + str(p)); continue
            towns.add(town)
            observer = x.get('role', x.get('measurer', directory.parent.name))
            namespace = ':'.join([cohort, directory.parent.name, p.stem])
            current = not (p.with_name(p.stem+'-v2.json').exists())
            if '-v2' in p.stem:
                current = True
            loc = x.get('location', x.get('located_point', {})) or {}
            lat, lon = loc.get('lat', loc.get('latitude')), loc.get('lon', loc.get('longitude'))
            if num(lat) is not None and num(lon) is not None:
                locations[town].append(dict(lat=lat, lon=lon, basis=loc.get('basis',loc.get('method')), record=ref(p,'/location' if 'location' in x else '/located_point'), is_current_input=current))
            smap = {}
            slist = x.get('sources', [])
            if isinstance(slist, dict):
                slist = [dict(v,id=k) for k,v in slist.items()]
            for i,s in enumerate(slist):
                smap[str(s.get('id', i))] = add_source(s,namespace,p,f'/sources/{i}')
            absences.append(dict(town=town, observer=str(observer), cohort=cohort, record=ref(p),
                                 measurable=x.get('measurable'), reason=x.get('unmeasurable_reason', x.get('main_system_reason', x.get('notes'))),
                                 imagery_assessment=x.get('imagery_assessment'), plan_assessment=x.get('plan_assessment'), is_current_input=current))
            for field,level in [('structures','line'),('lines','line'),('systems','system')]:
                for i,r in enumerate(x.get(field, [])):
                    source_key = str(r.get('source',r.get('source_id','')))
                    sid = smap.get(source_key)
                    s = source_index.get(sid,{}).get('metadata',{})
                    kind = s.get('kind','unknown')
                    north = s.get('north_reference',s.get('north_class', 'true' if kind=='imagery' else 'unspecified'))
                    theta = num(r.get('deviation_deg',r.get('theta_deg')))
                    bearing = num(r.get('bearing_deg'))
                    sigma = num(r.get('sigma_deg',r.get('se_deg')))
                    mid = namespace + ':' + field + ':' + str(i) + ':' + str(r.get('id',i))
                    measurements.append(dict(measurement_id=mid,town=town,observer=str(observer),cohort=cohort,
                        level=level,source_id=sid,source_kind=kind,north_reference=north,
                        part=r.get('part',r.get('description')),kind=r.get('kind'),description=r.get('description',r.get('identification')),
                        endpoints=r.get('endpoints',r.get('endpoints_lonlat',r.get('endpoints_px'))),
                        endpoint_reference='original record defines units and render; preserve all coordinate forms through record',
                        length_m=num(r.get('length_m',r.get('total_length_m'))),bearing_deg=None if bearing is None else bearing%180,
                        deviation_deg=theta,sigma_reported_deg=sigma,uncertainty_status='reported' if sigma is not None else 'unknown',
                        uncertainty_reason='Inherited error; provider orientation accuracy is not independently established.' if sigma is not None else 'No finite one-sigma error in this record.',
                        phase=r.get('phase'),phase_missing_reason=None if r.get('phase') else 'This measurement does not assign the exposed line to a dated building phase.',
                        n_lines=r.get('n_lines',r.get('n',1 if level=='line' else None)),
                        structure_ids=r.get('structures',r.get('line_ids',[])),warnings=r.get('warnings',[]),
                        empirical_error_warning='Runway validation found length-dependent errors and underestimation; retain the reported value with that warning.' if cohort=='verify' and kind=='imagery' else None,
                        independence_group='Sentinel-2' if cohort=='verify' and kind=='imagery' else 'Esri World Imagery' if kind=='imagery' else sid,
                        conditions_pass=r.get('conditions_pass'),is_current_input=current,record=ref(p,f'/{field}/{i}')))

    # Dating source keys belong to their original compilation namespaces.
    for prefix,p in [('axes-dating',OLD/'dating-v1/sources.json'),('verify-dating',VERIFY/'dating-v1/sources.json')]:
        x = read(p)
        for i,s in enumerate(x['sources']):
            add_source(s,prefix,p,f'/sources/{i}')
    for prefix,directory in [('axes-dating',OLD/'dating-v1/towns'),('verify-dating',VERIFY/'dating-v1/evidence')]:
        for p in sorted(directory.glob('*.json')):
            x = read(p); town = x.get('slug',x.get('town'))
            if not isinstance(town,str): continue
            towns.add(town)
            for i,r in enumerate(x.get('parts',[])):
                lp = r.get('layout_phase')
                label = lp.get('label') if isinstance(lp,dict) else lp
                parts.append(dict(part_record_id=f'{prefix}:{town}:{i}',town=town,part=r.get('part'),
                    layout_phase=label,excavator_range_bce=r.get('excavator_range_bce'),excavator_basis=r.get('excavator_basis'),
                    locator=r.get('locator',lp.get('support',{}).get('locators') if isinstance(lp,dict) else None),
                    phases=[dict(label=q.get('label'),architecture=q.get('architecture'),locators=q.get('locators')) for q in r.get('phases',[])],
                    candidates_by_level=r.get('candidates_by_level'),proposed_candidate=r.get('proposed_candidate'),
                    syntheses=r.get('syntheses'),bayesian_start=r.get('bayesian_start'),
                    uncertainty_reason='A phase range or candidate is not an identified construction boundary for every measured line.',
                    record=ref(p,f'/parts/{i}')))
                for j,radiocarbon in enumerate(r.get('radiocarbon',[])):
                    sk=radiocarbon.get('source')
                    dates.append(dict(town=town,compilation=prefix,part=r.get('part'),
                                      source_id=prefix+':'+str(sk) if sk else None,
                                      values=radiocarbon,record=ref(p,f'/parts/{i}/radiocarbon/{j}')))
            for j,radiocarbon in enumerate(x.get('radiocarbon_determinations',[])):
                sk=radiocarbon.get('locator',{}).get('source_key')
                dates.append(dict(town=town,compilation=prefix,part=None,source_id=prefix+':'+str(sk) if sk else None,
                                  values=radiocarbon,record=ref(p,f'/radiocarbon_determinations/{j}')))

    # Keep registrations, including their failed validation, distinct from direct imagery.
    p = REG/'registration-v1/results.json'; registered = read(p)
    for i,r in enumerate(registered['systems']):
        source_key=r.get('plan','').split(':',1)[-1]
        sid=next((s for s in source_index if s.startswith('axes:measure-plan-B:'+r['town']+':') and s.endswith(':'+source_key)),None)
        sm=source_index.get(sid,{}).get('metadata',{})
        measurements.append(dict(measurement_id=f'registration:{i}',town=r['town'],observer='prior registrars',cohort='registration',level='system',
            source_id=sid,source_kind='registered-plan',north_reference='true',original_plan_north_reference=sm.get('north_reference'),part=r.get('part'),description=r.get('description'),
            length_m=r.get('total_length_m'),bearing_deg=None,deviation_deg=r.get('theta_true_deg'),sigma_reported_deg=r.get('sigma_true_deg'),
            uncertainty_status='reported',uncertainty_reason='Exploratory registration; the package failed its frozen validation.',
            phase=None,phase_missing_reason='Registration does not establish the construction phase.',n_lines=r.get('n_lines'),
            is_current_input=True,validation_passes=registered['validation_passes'],plan=r.get('plan'),variant=r.get('variant'),
            record=ref(p,f'/systems/{i}')))

    # New, explicitly unblinded picks, on one archived image.
    p = PACKAGE/'new-observations.json'; x = read(p); src = x['sources'][0]
    sid = add_source(src,'new-surkotada',p,'/sources/0')
    gp=PACKAGE/'geodesic-check.json'; geo=read(gp); georows={r['id']:(j,r) for j,r in enumerate(geo['rows'])}
    for i,r in enumerate(x['structures']):
        (a,b),(c,d) = r['endpoints_px']; dx,dy=c-a,d-b
        length_px=math.hypot(dx,dy); bearing=math.degrees(math.atan2(dx,-dy))%180
        scale=math.cos(math.radians(x['location']['lat']))*2*math.pi*6378137/(256*2**src['zoom'])
        sigma=math.degrees(math.sqrt(2)*x['digitizing_sigma_px']/length_px)
        gi,gr=georows[r['id']]
        true_bearing=gr['geodesic'][0]%180
        measurements.append(dict(measurement_id='new-surkotada:'+r['id'],town='surkotada',observer=x['role'],cohort='new',level='line',
            source_id=sid,source_kind='imagery',north_reference='true',part=r['part'],kind=r['kind'],description=r['description'],
            endpoints=r['endpoints_px'],endpoint_reference='native mosaic pixels, x right and y down; source has global origin and zoom',
            length_m=gr['geodesic'][2],bearing_deg=true_bearing,deviation_deg=fold(true_bearing),sigma_reported_deg=None,
            pixel_grid_bearing_deg=bearing,geodesic_reference=ref(gp,f'/rows/{gi}'),
            sigma_digitizing_deg=sigma,uncertainty_status='partial',uncertainty_reason=x['systematic_missing_reason'],
            phase=r['phase'],phase_missing_reason=None,n_lines=1,is_current_input=True,
            independence_group='Esri World Imagery',record=ref(p,f'/structures/{i}')))
    locations['surkotada'].insert(0,dict(**x['location'],record=ref(p,'/location'),is_current_input=True))

    # Source-reported angles are facts about publications, not new image measurements.
    p = PACKAGE/'source-checks.json'; checked = read(p)
    for r in checked['rows']:
        g=r['reported_deviation_gon']
        r['deviation_deg']=g*.9 if isinstance(g,(int,float)) else None
        r['deviation_interval_deg']=[v*.9 for v in g] if isinstance(g,list) else None
        r['error_bound_deg']=r.get('reported_error_bound_gon',0)*.9 or None

    # Horizon summaries point to the full, hash-preserved profiles and tile manifests.
    p = OLD/'horizon-v1/horizons.json'; x=read(p)
    for i,h in enumerate(x['towns']):
        horizons.append(dict(town=h['town'],lat=h['lat'],lon=h['lon'],
            east_deg=h['altitude_at_90_deg'],west_deg=h['altitude_at_270_deg'],
            max_east_deg=h['max_altitude_east_deg'],max_west_deg=h['max_altitude_west_deg'],
            datum='Copernicus DSM surface; observer 1.6 m above DEM at the recorded point',
            model='GLO-30 at 2-20 km, GLO-90 at 20-250 km; 0.1 degree rays; effective curvature k=0.13',
            sigma_deg=None,uncertainty_reason='No numerical vertical-datum, observer-position or palaeohorizon uncertainty was propagated.',
            usable_at_corrected_site=h['town'] not in ['surkotada','farmana','gola-dhoro'],
            exclusion_reason='Inherited coordinates were corrected or the site identity remains unresolved.' if h['town'] in ['surkotada','farmana','gola-dhoro'] else None,
            profile=ref(p,f'/towns/{i}/profile'),dem_sources=ref(p,'/dem_tiles')))
    for p in sorted((VERIFY/'astro-v1/horizon').glob('*.json')):
        if p.stem.startswith('coords-'): continue
        h=read(p); town=p.stem
        if 'azimuth_deg' not in h: continue
        az=h['azimuth_deg']; alt=h['apparent_altitude_deg']
        east=[v for a,v in zip(az,alt) if 45<=a%360<=135]
        west=[v for a,v in zip(az,alt) if 225<=a%360<=315]
        get=lambda a: alt[min(range(len(az)),key=lambda i:abs((az[i]-a+180)%360-180))]
        horizons.append(dict(town=town,lat=h['lat'],lon=h['lon'],east_deg=get(90),west_deg=get(270),
            max_east_deg=max(east) if east else None,max_west_deg=max(west) if west else None,
            datum='See exact DEM and observer heights in the source profile',model='independent verification profile; original model and tile records retained',
            sigma_deg=None,uncertainty_reason='No complete one-sigma horizon error is supplied.',
            usable_at_corrected_site=town not in ['surkotada','farmana','gola-dhoro'],
            exclusion_reason='Inherited coordinates were corrected or the site identity remains unresolved.' if town in ['surkotada','farmana','gola-dhoro'] else None,
            profile=ref(p),dem_sources=ref(p,'/dem_tiles')))

    repair=PACKAGE/'horizon-repair-v1/horizons.json'
    if repair.exists():
        x=read(repair)
        for i,h in enumerate(x['towns']):
            horizons.append(dict(town=h['town'],lat=h['lat'],lon=h['lon'],east_deg=h['altitude_at_90_deg'],west_deg=h['altitude_at_270_deg'],
                max_east_deg=h['max_altitude_east_deg'],max_west_deg=h['max_altitude_west_deg'],
                datum='Modern Copernicus DSM surface; observer 1.6 m above local surface',model=x['model'],
                sigma_deg=None,uncertainty_reason=x['uncertainty'],usable_at_corrected_site=True,
                coordinate_precision_reason=h['coordinate_basis'],profile=ref(repair,f'/towns/{i}/profile'),dem_sources=ref(repair,'/dem_tiles')))
        for i,tile in enumerate(x['dem_tiles']):
            add_source(dict(tile,id=str(i),kind='elevation-model-tile',licence_source=x['licence_source'],attribution=x['attribution']),
                       'new-copernicus',repair,f'/dem_tiles/{i}')

    # A town is an index into part-level observations, not a pooled axis or date.
    summaries=[]; gaps=[]
    for town in sorted(towns):
        ms=[m for m in measurements if m['town']==town and m.get('is_current_input')]
        ps=[q for q in parts if q['town']==town]
        hs=[q for q in horizons if q['town']==town]
        locs=locations[town]
        chosen=next((q for q in locs if q.get('is_current_input')),None)
        if town=='farmana':
            chosen=dict(lat=29.040,lon=76.306,basis='Corrected approximate report coordinate in plan-registration REPORT.md; precision is not a surveyed architectural point.',record=ref(REG/'REPORT.md'))
        if town=='gola-dhoro':
            chosen=None
        image=[m for m in ms if m['source_kind']=='imagery']
        plans=[m for m in ms if m['source_kind']=='plan']
        systems=[m for m in image if m['level']=='system']
        absence_indices=[i for i,q in enumerate(absences) if q['town']==town]
        why={
            'coordinates':None if chosen else 'No verified measured-architecture location; retain candidate locations separately.',
            'two_independent_imagery_sources':('No direct image lines in the retained records; consult this town\'s absence records for the source-specific search and visibility reasons. ' if not image else '')+'Multiple observers can share a raster. Different imagery products need agreement or a recorded discordance on the same architectural part, with validated errors; this register does not certify that condition.',
            'plan_true_north':None if any(m['north_reference']=='true' for m in plans) else 'No measured plan with an explicitly established true-north reference in these records.',
            'horizon':None if any(h['usable_at_corrected_site'] for h in hs) else 'No usable profile at the retained location; superseded-location profiles remain available.' if hs else 'No inherited profile for this town; DEM profile has not been acquired.',
            'horizon_sigma':'Terrain, observer and palaeohorizon uncertainty have not been propagated.',
            'layout_boundary':'Phase and sample assertions require a wall-by-wall stratigraphic join; no single pooled founding year is assigned.',
            'bayesian_start':'No accepted Bayesian construction-boundary output is supplied for the measured part in this register.'}
        for field,reason in why.items():
            if reason:gaps.append(dict(town=town,field=field,value_status='unknown',reason=reason))
        summaries.append(dict(town=town,required=town in required,latitude=chosen['lat'] if chosen else None,
            longitude=chosen['lon'] if chosen else None,coordinate=chosen,coordinate_candidates=locs,
            axes=[m['measurement_id'] for m in ms],imagery_lines=sum(m['level']=='line' for m in image),
            imagery_systems=len(systems),plan_lines=sum(m['level']=='line' for m in plans),
            registered_systems=sum(m['source_kind']=='registered-plan' for m in ms),
            true_north_readings=[dict(id=m['measurement_id'],part=m['part'],deviation_deg=m['deviation_deg'],sigma_reported_deg=m.get('sigma_reported_deg'),source_id=m.get('source_id')) for m in image if m['level']=='system' or m['cohort']=='new'],
            dated_part_assertions=[q['part_record_id'] for q in ps],radiocarbon_assertions=sum(q['town']==town for q in dates),
            horizon_records=[i for i,q in enumerate(horizons) if q['town']==town],
            source_absence_records=absence_indices,missing=why))

    ids=[m['measurement_id'] for m in measurements]
    if len(ids)!=len(set(ids)):errors.append('Duplicate measurement IDs')
    if not required.issubset(towns):errors.append('Missing required towns')
    for m in measurements:
        if m.get('source_id') and m['source_id'] not in source_index:errors.append('Missing source: '+m['measurement_id'])
        if m.get('bearing_deg') is not None and not 0<=m['bearing_deg']<180:errors.append('Invalid bearing: '+m['measurement_id'])
        if m.get('deviation_deg') is not None and not -45.000001<=m['deviation_deg']<=45.000001:errors.append('Invalid deviation: '+m['measurement_id'])
        if m.get('source_kind')=='plan' and m.get('north_reference') not in ['true','magnetic','grid','unspecified','unknown']:
            errors.append('Unknown north class: '+m['measurement_id']+': '+str(m['north_reference']))
    field_gaps=[]
    for m in measurements:
        for field in ['part','source_id','length_m','bearing_deg','phase','sigma_reported_deg']:
            if m.get(field) is not None:continue
            reason={'part':'No named architectural part in this system; original line records remain available.',
                    'source_id':'Registration source join is unresolved; its original plan identifier and result record are retained.',
                    'length_m':'No metric length is reported for this measurement.',
                    'bearing_deg':'Orthogonal system is represented by its folded deviation; a unique directed bearing is not applicable.' if m['level']=='system' else 'Source gives no directed bearing.',
                    'phase':m.get('phase_missing_reason','No dated building-phase assignment.'),
                    'sigma_reported_deg':m.get('uncertainty_reason','No complete one-sigma measurement error.')}[field]
            field_gaps.append(dict(measurement_id=m['measurement_id'],field=field,
                                   value_status='not-applicable' if field=='bearing_deg' and m['level']=='system' else 'unknown',reason=reason))
    # Exact coordinates and lengths of all new picks are reproducible independently.
    coverage=dict(towns=len(towns),required_towns=len(required),measurement_rows=len(measurements),
        source_records=len(sources),dated_part_assertions=len(parts),radiocarbon_assertions=len(dates),
        towns_with_imagery_lines=sum(s['imagery_lines']>0 for s in summaries),
        towns_with_plan_lines=sum(s['plan_lines']>0 for s in summaries),
        towns_with_any_horizon=len({h['town'] for h in horizons}),
        towns_with_usable_horizon=len({h['town'] for h in horizons if h['usable_at_corrected_site']}),
        missing_field_rows=len(gaps),new_digitized_lines=2,new_wanzke_rows=len(checked['rows']),
        new_radiocarbon_determinations=0,new_objects=0,source_files_newly_downloaded=len({s['metadata'].get('physical_path') for s in sources if s['source_id'].startswith('new-copernicus:') and s['metadata'].get('status')==200}),
        note='Counts are assertions, including repeated source uses. No new independent sample, source image or radiocarbon measurement is claimed.')
    out.mkdir(parents=True)
    write(out/'town-axis-table.json',dict(schema_version='1.0',status_class='source-review',scientific_confirmation=False,towns=summaries))
    jsonl(out/'measurements.jsonl',measurements);jsonl(out/'sources.jsonl',sources)
    jsonl(out/'chronology-parts.jsonl',parts);jsonl(out/'radiocarbon.jsonl',dates)
    jsonl(out/'horizons.jsonl',horizons);jsonl(out/'absence-records.jsonl',absences)
    write(out/'published-wanzke.json',checked)
    csvfile(out/'town-axis-table.csv',summaries,['town','required','latitude','longitude','imagery_lines','imagery_systems','plan_lines','registered_systems','radiocarbon_assertions','true_north_readings','missing'])
    csvfile(out/'measurements.csv',measurements,['measurement_id','town','observer','source_kind','level','part','north_reference','bearing_deg','deviation_deg','sigma_reported_deg','sigma_digitizing_deg','length_m','phase','source_id','uncertainty_reason','record'])
    csvfile(out/'missing-fields.csv',gaps,['town','field','value_status','reason'])
    csvfile(out/'measurement-field-gaps.csv',field_gaps,['measurement_id','field','value_status','reason'])
    write(out/'coverage.json',coverage)
    write(out/'input-manifest.json',dict(inputs=INPUTS,code_sha256=digest(Path(__file__)),protocol_sha256=digest(PACKAGE/'PROTOCOL.md')))
    write(out/'validation.json',dict(status='pass' if not errors else 'fail',errors=errors,
        checks=['required towns','unique measurement IDs','source references','bearing range','deviation range','north class vocabulary'],
        scope='Structural validation of a source register; no independent verification of all inherited observations.'))
    print(json.dumps(dict(coverage=coverage,errors=errors),indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':
    main()
