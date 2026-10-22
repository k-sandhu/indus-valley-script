"""Rerun every accepted pick and every town system to fresh southern outputs."""
import json,sys,subprocess,math,datetime,shutil
from pathlib import Path
owned=Path(__file__).resolve().parent;root=owned.parents[2];tool=owned.parent/'tools'
verify=owned/'verification-S-v1';verify.mkdir(exist_ok=False)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def rel(p):return Path(p).resolve().relative_to(root).as_posix()
config=read(owned/'decisions-S-v1.json');checks=[]
for decision in config['towns']:
    slug=decision['slug'];town=read(owned/'towns'/f'{slug}.json');rebuilt=dict(town)
    for key in ['created_utc','systems','main_system_by_source']:rebuilt.pop(key,None)
    rebuilt['lines']=[];source_checks=[]
    for record in town['measurements']:
        old=read(record['measurement_result']);out=verify/slug/f'{record["source_id"]}-refinement-rerun.json'
        subprocess.run([sys.executable,'-I',str(tool/'measure_lines.py'),record['picks_path'],record['render_sidecar'],str(out)],check=True)
        fresh=read(out)
        assert old['lines']==fresh['lines'],(slug,record['source_id'],'refined lines differ')
        assert old['arrow']==fresh['arrow'],(slug,'north arrow differs')
        assert old['north']==fresh['north'] and old['source_sha256']==fresh['source_sha256']
        group=read(record['grouping_record'])['assignments'] if record.get('grouping_record') else None
        for row in fresh['lines']:
            original=next(r for r in town['lines'] if r['source_id']==record['source_id'] and r['id']==row['id'])
            r=dict(original,**row)
            if group:r['system']=group[r['id']]
            assert r==original,(slug,r['id'],'town geometry does not follow picks and grouping')
            assert r['source_locator'] and r['identification'] and r['render_sidecar']
            assert math.isfinite(r['sigma_deg']) and r['sigma_deg']>0 and r['length_m']>0
            assert r.get('endpoints_plan_m') or r.get('endpoints_utm')
            rebuilt['lines'].append(r)
        src=next(s for s in town['sources'] if s['id']==record['source_id'])
        assert src['north_class'] in ['true','magnetic','grid','unspecified'] and src['north_evidence']
        assert src['measured_arrow']==fresh['arrow'] and src['survey_year']==fresh['north'].get('survey_year')
        source_checks.append(dict(source_id=record['source_id'],picks_reproduce=True,arrow_reproduces=True,source_sha256=fresh['source_sha256'],fresh_result=rel(out)))
    tin=verify/slug/'town-input-rerun.json';tout=verify/slug/'town-rerun.json';write(tin,rebuilt)
    subprocess.run([sys.executable,'-I',str(tool/'systems.py'),str(tin),str(tout),'--summary',str(verify/'summary-rerun.csv')],check=True)
    current=read(tout);baseline=dict(town)
    current.pop('created_utc',None);baseline.pop('created_utc',None)
    assert current==baseline,(slug,'town output differs')
    warnings=[dict(source_id=s['source_id'],system=s['id'],warnings=s['warnings']) for s in town['systems'] if s['warnings']]
    checks.append(dict(town=slug,town_exists=True,line_count=len(town['lines']),line_locators_and_errors_complete=True,plan_north_records_complete=True,refinements=source_checks,systems_reproduce=True,warnings=warnings))
allpaths=[]
for d in config['towns']:
    slug=d['slug']
    for folder in [owned/'picks'/slug,root/'data/raw/2026-10-21-town-orientations-verification/measure-A'/slug]:allpaths += [p.resolve() for p in folder.rglob('*') if p.is_file()]
    allpaths.append((owned/'towns'/f'{slug}.json').resolve())
allpaths += [p.resolve() for p in verify.rglob('*') if p.is_file()]
allpaths += [p.resolve() for p in owned.iterdir() if p.is_file() and ('-S' in p.name or p.name=='revise-nausharo-S.py')]
allowed=[owned.resolve(),(root/'data/raw/2026-10-21-town-orientations-verification/measure-A').resolve()]
assert all(any(p.is_relative_to(a) for a in allowed) for p in allpaths)
report=dict(schema_version=1,measurer='A',regional_share='S',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),town_count=len(checks),line_count=sum(c['line_count'] for c in checks),all_picks_and_systems_reproduce=True,all_output_paths_owned=True,checks=checks,known_method_condition_failures='Sutkagen-dor northern wall main system is a singleton and fails the 200m neighbour rule; retained visibly under the fixed main-selection rule.',imagery_plan_disagreements_over_2_deg=None,comparison_status='Unavailable: no accepted imagery lines',free_bytes=shutil.disk_usage('C:/').free,paths=sorted(set(rel(p) for p in allpaths)))
write(verify/'verification-report.json',report)
print(json.dumps({k:report[k] for k in ['town_count','line_count','all_picks_and_systems_reproduce','all_output_paths_owned','free_bytes']}))
