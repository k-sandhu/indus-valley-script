"""Assemble southern town records from preserved independent picks and fits."""
import sys,json,subprocess,hashlib,datetime,shutil
from pathlib import Path
owned=Path(__file__).resolve().parent
root=owned.parents[2]
tools=owned.parent/'tools'
raw=root/'data/raw/2026-10-21-town-orientations-verification/measure-A'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def rel(p):
    p=Path(p)
    return p.resolve().relative_to(root).as_posix()
def source_record(source):
    p=Path(source.get('source_path',source.get('local_source_path','')))
    if p.is_file():source.update(source_path=rel(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    acq=source.get('acquisition_record')
    if acq:source['acquisition']=read(acq)
    return source
config=read(owned/'decisions-S-v1.json')
all_sources=[];all_renders=[];observed=[]
for decision in config['towns']:
    slug=decision['slug'];pickdir=owned/'picks'/slug
    snap=read(pickdir/'source-snapshot-v1.json');site=snap['site'];im=snap['imagery']
    sources=[dict(id='imagery',kind='imagery',scene_ids=im.get('composite_scene_ids',[]),scene_datetimes=[s['datetime'] for s in im.get('scenes',[]) if s.get('used_in_composite')],manifest_path=rel(owned.parent/'infra-v1/imagery-manifest-v1.json'),source_snapshot=rel(pickdir/'source-snapshot-v1.json'),composite=im.get('composite'),scenes=[{k:s[k] for k in ['item_id','datetime','file'] if k in s} for s in im.get('scenes',[]) if s.get('used_in_composite')],measurement_status='No securely identified architectural imagery line accepted')]
    for p in snap['plans'].get('plans',[]):
        sources.append(source_record(dict(id=p['id'],kind='plan',citation=p['citation'],pdf_page=p['pdf_page'],printed_page=p.get('printed_page'),figure=p.get('figure_or_plate'),north_class=p.get('north_class'),north_evidence=p.get('north_words_exact') or p.get('north_evidence_location'),survey_year=p.get('survey_year'),local_source_path=p['local_source_path'],acquisition=p.get('source'),measurement_status='Inspected locator or architectural source; selected measured source recorded separately below')))
    lines=[];measurement_records=[]
    for spec in decision['measurements']:
        resultpath=pickdir/spec['result'];pickspath=pickdir/spec['picks'];m=read(resultpath)
        source=spec.get('source')
        if source is None:
            lib=next(p for p in sources if p['id']==spec['library_id'])
            source=dict(lib)
        else:source=dict(source)
        source.update(id=m['source_id'],kind='plan',north_class=m['north']['class'],north_evidence=m['north']['evidence'],survey_year=m['north'].get('survey_year'),north=m['north'],measured_arrow=m['arrow'],metres_per_render_pixel=m['metres_per_render_pixel'],measurement_result=rel(resultpath),picks_path=rel(pickspath),render_sidecar=m['render_sidecar'],measurement_status='Measured; true reference unresolved' if m['north']['class']=='unspecified' else 'Measured; magnetic correction retained')
        source_record(source)
        sources.append(source)
        group=read(pickdir/spec['grouping']) if spec.get('grouping') else None
        for row in m['lines']:
            row=dict(row,source_id=m['source_id'],picks_path=rel(pickspath),measurement_result=rel(resultpath),render_sidecar=m['render_sidecar'],source_locator={k:source.get(k) for k in ['citation','pdf_page','printed_page','figure','source_path']})
            if group:row['system']=group['assignments'][row['id']];row['grouping_record']=rel(pickdir/spec['grouping'])
            lines.append(row)
        measurement_records.append(dict(source_id=m['source_id'],picks_path=rel(pickspath),measurement_result=rel(resultpath),render_sidecar=m['render_sidecar'],grouping_record=rel(pickdir/spec['grouping']) if group else None))
    point=decision.get('located_point_override',site['coordinate_used'])
    town=dict(schema_version=1,slug=slug,measurer='A',regional_share='Sindh, Baluchistan and Pakistani Punjab',authors=config['authors'],located_point=dict(latitude=point[0],longitude=point[1],method=decision['location_status']+'; see LOG-S.md and retained source snapshot'),location_status=decision['location_status'],sources=sources,lines=lines,registrations=[],registration_status='No securely matching archaeological controls in the 10m imagery',notes=decision['notes'],unmeasurable_reason=decision.get('unmeasurable_reason'),imagery_status='not measurable',status='measured from plans' if lines else 'not measurable',measurements=measurement_records,calibration_record='experiments/2026-10-21-town-orientations-verification/infra-v1/validation-v1/summary.json',error_scope='Tool sigma preserved. Unspecified plan arrows leave true north unresolved. Shared north-arrow error, survey and paper distortion are outside an independence interpretation of the system SE.')
    if decision.get('coordinate_candidates'):town['coordinate_candidates']=decision['coordinate_candidates']
    inputpath=pickdir/'town-input-v1.json';write(inputpath,town)
    out=owned/'towns'/f'{slug}.json'
    subprocess.run([sys.executable,'-I',str(tools/'systems.py'),str(inputpath),str(out),'--summary',str(owned/'summary-S.csv')],check=True)
    town=read(out)
    all_sources.append(dict(town=slug,sources=sources))
    for sc in sorted((raw/slug).rglob('*.png.json')):
        side=read(sc)
        if side.get('source'):
            observed.append(dict(town=slug,source=side['source'],sha256=side.get('source_sha256',side.get('sha256')),pdf_page=side.get('page'),role=side.get('role','render'),sidecar=rel(sc)))
        all_renders.append(dict(town=slug,path=rel(Path(str(sc)[:-5])),sidecar=rel(sc),settings=side))
    print(slug,[(s['source_id'],round(s['theta_deg'],5),round(s['se_deg'],5),s['n'],round(s['total_length_m'],3),s['conditions_pass']) for s in town['systems'] if town['main_system_by_source'].get(s['source_id'])==s['id']])
acquisitions=[]
for decision in config['towns']:
    for p in sorted((raw/decision['slug']).rglob('acquisition.json')):acquisitions.append(dict(record=rel(p),**read(p)))
source_index=dict(schema_version=1,measurer='A',regional_share='S',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),authors=config['authors'],town_sources=all_sources,acquisitions=acquisitions,render_observations=observed,render_inventory=all_renders,additional_rights_observations=[dict(source='Durham Cork thesis PDF page1',notice='Personal research/study, educational and not-for-profit use permitted with full bibliographic reference, repository metadata link, and unchanged full text. No sale without permission. See preserved page1 render.')],failed_acquisitions=[dict(url='https://easaa.org/wp-content/uploads/2023/01/Sidra-Gulzar-3.pdf',attempt_date_utc='2026-10-21',status='HTTP403',directory=rel(raw/'ganweriwala/gulzar-survey-v1'),bytes_received=0,sha256=None,rights_notice='No file acquired; rights not assessed')],redistribution='All acquired and held third-party sources and renders remain local; no publication performed.',imagery_plan_disagreements_over_2_deg=None,comparison_status='No accepted imagery lines; imagery-plan comparison unavailable',free_bytes_at_end=shutil.disk_usage('C:/').free)
write(owned/'sources-S.json',source_index)
write(owned/'created-paths-S-v1.json',dict(paths=sorted(set([rel(p) for d in config['towns'] for p in (raw/d['slug']).rglob('*') if p.is_file()]+[rel(p) for d in config['towns'] for p in (owned/'picks'/d['slug']).rglob('*') if p.is_file()]+[rel(owned/'towns'/f'{d["slug"]}.json') for d in config['towns']]+[rel(owned/p) for p in ['LOG-S.md','summary-S.csv','sources-S.json','decisions-S-v1.json']]))))
