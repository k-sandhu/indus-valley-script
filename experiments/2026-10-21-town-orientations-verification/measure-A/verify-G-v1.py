"""Reproduce Gujarat town systems from original picks and audit provenance."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,subprocess,csv,math,shutil,datetime,hashlib
root=Path.cwd();pkg=root/'experiments/2026-10-21-town-orientations-verification'
own=pkg/'measure-A';raw=root/'data/raw/2026-10-21-town-orientations-verification/measure-A'
sys.path.insert(0,str(pkg/'tools'))
from common import read_json,write_json,sha256
from measure_lines import measure
slugs='lothal dholavira surkotada kanmer shikarpur juni-kuran gola-dhoro desalpur khirsara kuntasi rojdi rangpur kotada-bhadli pabumath navinal'.split()
checks=[];source_towns=[];total_lines=0;comparisons=[]
summary=own/'summary-G-reproduced-v1.csv'
if summary.exists():raise FileExistsError(summary)
for slug in slugs:
    directory=own/'picks'/slug
    original=read_json(own/'towns'/f'{slug}.json')
    inp=read_json(directory/'town-input-G-v1.json')
    snap=read_json(directory/'source-index-G-v1.json')
    linked=sorted(set(x['measurement_record'] for x in inp['lines']))
    fresh={};line_checks=[]
    for resultpath in linked:
        held=read_json(resultpath)
        pp=Path(resultpath.replace('-refined.json','.json'))
        repeated=measure(read_json(pp),held['render_sidecar'])
        out=Path(resultpath.replace('-refined.json','-reproduced-G-v1.json'))
        write_json(out,repeated)
        assert repeated['lines']==held['lines'],f'line reproduction failed: {resultpath}'
        assert repeated['arrow']==held['arrow'],f'arrow reproduction failed: {resultpath}'
        for line in repeated['lines']:fresh[(held['source_id'],line['id'])]=line
    for line in inp['lines']:
        assert line['identification'] and line['measurement_record']
        assert math.isfinite(line['sigma_deg']) and line['sigma_deg']>0
        assert line['source_id'] in [s['id'] for s in inp['sources']]
        assert any(k in line for k in ['endpoints_plan_m','endpoints_utm'])
        if line.get('north_class'):
            source=next(s for s in inp['sources'] if s['id']==line['source_id'])
            assert source['north_class'] and source['north_evidence'] and source['arrow']
            assert 'survey_year' in source
        line_checks.append(dict(id=line['id'],source_id=line['source_id'],locator_present=True,error_present=True,metric_endpoints_present=True))
        new=fresh[(line['source_id'],line['id'])]
        assert line['theta_deg']==new['theta_deg'] and line['sigma_deg']==new['sigma_deg']
    newinput=directory/'town-input-reproduced-G-v1.json'
    # Input retains exact metadata and source locator. Numeric fields have just
    # been checked against a new tool run from the original picks.
    write_json(newinput,inp)
    destination=directory/'town-reproduced-G-v1.json'
    subprocess.run([sys.executable,'-I',str(pkg/'tools/systems.py'),str(newinput),str(destination),'--summary',str(summary)],check=True,capture_output=True,text=True)
    repeated_town=read_json(destination)
    assert repeated_town['systems']==original['systems']
    assert repeated_town['main_system_by_source']==original['main_system_by_source']
    if not inp['lines']:assert inp['unmeasurable_reason']
    checks.append(dict(slug=slug,line_count=len(inp['lines']),picks_reproduced=True,systems_reproduced=True,line_audit=line_checks,system_warnings=[w for s in original['systems'] for w in s['warnings']]))
    total_lines+=len(inp['lines'])
    im=snap['imagery']
    source_towns.append(dict(slug=slug,index_snapshot=str(directory/'source-index-G-v1.json'),imagery_status=im.get('status') if im else 'missing',composite=im.get('composite') if im else None,scenes=[dict(item_id=s['item_id'],datetime=s['datetime'],used_in_composite=s.get('used_in_composite'),file=s.get('file'),scl=s.get('scl')) for s in (im or {}).get('scenes',[])],plans=(snap['plans'] or {}).get('plans',[])))
    mains={s['source_id']:s for s in original['systems'] if s['id']==original['main_system_by_source'].get(s['source_id'])}
    if 'imagery' in mains:
        for key,s in mains.items():
            if key!='imagery':
                delta=abs((s['theta_deg']-mains['imagery']['theta_deg']+45)%90-45)
                comparisons.append(dict(slug=slug,plan_source=key,difference_deg=delta,above_2_deg=delta>2,north_class=next(p['north_class'] for p in inp['sources'] if p['id']==key)))
with (own/'summary-G.csv').open(encoding='utf-8',newline='') as f:first=list(csv.DictReader(f))
with summary.open(encoding='utf-8',newline='') as f:second=list(csv.DictReader(f))
assert first==second
acquired=[]
for slug in slugs:
    if (raw/slug).exists():
        for path in sorted((raw/slug).rglob('source-record.json')):
            r=read_json(path);r.pop('final_url',None)
            r['acquisition_record_path']=str(path)
            if 's1-figure' in str(path):
                r.update(rights_status='explicit-license',licence_evidence='Pokharia et al.2017 PDF page1: Creative Commons Attribution License',decoded_copy=str(path.with_name('source.tif')),decoded_copy_transformation='byte-identical copy; original download had .pdf suffix; MIME is image/tiff')
                assert sha256(path.with_name('source.tif'))==r['sha256']
            if 'asi-brochure' in str(path):r.update(source_identity_correction='Kendriya Vidyalaya Gujarat school booklet, 83 pages; not an ASI report. Excluded.',used_for_measurement=False)
            acquired.append(r)
extra=[]
specs=[('data/raw/2026-10-21-town-orientations-verification/infra/plans/khirsara/pokharia2017/source.pdf','Pokharia et al.2017, Altered cropping pattern and cultural continuation with declined prosperity following abrupt and extreme arid event at ~4,200 yrs BP: Evidence from an Indus archaeological site Khirsara, Gujarat, western India','https://doi.org/10.1371/journal.pone.0185684','Creative Commons Attribution License, PDF p.1','PDF pp.1,4,15; S1 Fig link'),('data/raw/2026-10-21-town-orientations-verification/infra/plans/kuntasi/dhavalikar/source.pdf','M.K.Dhavalikar, Kuntasi: A Harappan port-settlement on the Western Coast, in Recent Advances in Marine Archaeology (1991)','https://ignca.gov.in/Asi_data/80451.pdf','No explicit reuse licence verified','PDF p.52, printed p.37')]
for path,title,url,rights,locator in specs:
    p=root/path;extra.append(dict(path=path,citation=title,url=url,bytes=p.stat().st_size,sha256=sha256(p),rights_notice=rights,locator=locator,acquisition='Previously held infrastructure source; retrieval record remains with infrastructure, not reacquired'))
review=read_json(pkg/'infra-v1/coordinate-source-review-resume-v2.json')
extra.append(dict(citation=review['citation'],source=review['source'],locator='PDF pp.1-3 read for Shikarpur site description; p.9 coordinate cited from infrastructure review'))
write_json(own/'sources-G.json',dict(schema_version=1,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),measurer='A',share='Gujarat',towns=source_towns,additional_held_sources=extra,acquired_sources=acquired,download_block=dict(url='https://www.ancientportsantiques.com/wp-content/uploads/Documents/PLACES/IndOc-Gulf/Gujarat-Rawat2015.pdf',status='not attempted: automatic approval rejected combined command as blocked by policy',town='pabumath'),rights_handling='All acquired scans and renders retained locally. Stable public URLs only; transient signed redirect omitted.'))
report=dict(schema_version=1,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),town_count=len(checks),town_files_complete=True,line_count=total_lines,system_count=sum(len(read_json(own/'towns'/f'{s}.json')['systems']) for s in slugs),summary_reproduces=True,checks=checks,imagery_plan_comparisons=comparisons,free_bytes=shutil.disk_usage(root).free,invariants=dict(git_mutations=False,output_paths='Within both owned roots; Gujarat names only',forbidden_measurement_directories_opened=False,commercial_strip='Shikarpur initial upper-figure render inadvertently included narrow panelD strip. No measurement used it. Retained and disclosed.',tool_edits=False,overwrites=False))
write_json(own/'verification-G-v1.json',report)
paths=[]
for slug in slugs:
    for base in [own/'picks'/slug,raw/slug]:
        if base.exists():paths.extend(str(p.relative_to(root)).replace('\\','/') for p in base.rglob('*') if p.is_file())
    paths.append(str((own/'towns'/f'{slug}.json').relative_to(root)).replace('\\','/'))
for name in ['helper-G.py','runner-G-v1.py','relocate-G-v1.py','acquire-plan-G-v1.py','verify-G-v1.py','LOG-G.md','summary-G.csv','summary-G-reproduced-v1.csv','sources-G.json','verification-G-v1.json','created-paths-G-v1.json']:
    paths.append(str((own/name).relative_to(root)).replace('\\','/'))
assert all((root/p).resolve().is_relative_to(own) or (root/p).resolve().is_relative_to(raw) for p in paths)
write_json(own/'created-paths-G-v1.json',dict(schema_version=1,paths=sorted(set(paths)),note='Only this Gujarat run; sibling measurer-A regional files are not inventoried.'))
print(json.dumps({k:report[k] for k in ['town_count','line_count','system_count','summary_reproduces','imagery_plan_comparisons','free_bytes']}))
