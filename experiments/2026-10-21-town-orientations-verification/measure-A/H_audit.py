import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,subprocess,copy,datetime,shutil
OWN=Path(sys.argv[1]);RAW=Path(sys.argv[2]);TOOLS=Path(sys.argv[3]);AUDIT=OWN/'audit-H-v1'
AUDIT.mkdir(exist_ok=False)
SLUGS=['kalibangan','banawali','rakhigarhi','farmana','bhirrana','kunal','mitathal','karanpura']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(exist_ok=True,parents=True)
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')
def command(args):
 r=subprocess.run([sys.executable,'-I',*map(str,args)],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout
# Preserve the first endpoint and split the identified >6 degree group in v2.
mit=read(OWN/'picks/mitathal/town-input-v1.json')
for row in mit['lines']:
 if row['source_id']=='mitathal-01' and row['id']=='40-west':
  row['system_from_picks']=row['system'];row['system']='IIA-3-wall40'
for admission in mit['measurement_selection']:
 if admission['source_id']=='mitathal-01':admission['system_overrides']['40-west']='IIA-3-wall40'
mit['notes']+=' Revision v2 splits wall 40 from the two Structure 39 faces: their combined span was 6.719466 degrees, outside the allowed six-degree window. The two Structure 39 faces remain correlated.'
write(OWN/'picks/mitathal/town-input-v2.json',mit)
command([TOOLS/'systems.py',OWN/'picks/mitathal/town-input-v2.json',OWN/'towns/mitathal-v2.json','--summary',OWN/'summary-mitathal-revision-H-v2.csv'])
checks=[];final_paths={};full_selection=[]
for slug in SLUGS:
 version=2 if slug=='mitathal' else 1
 inputpath=OWN/f'picks/{slug}/town-input-v{version}.json'
 townpath=OWN/f'towns/{slug}{"-v2" if slug=="mitathal" else ""}.json'
 final_paths[slug]=str(townpath).replace('\\','/')
 town=read(inputpath);expected=read(townpath);fresh=copy.deepcopy(town);rows={}
 for admission in town['measurement_selection']:
  dest=AUDIT/f'{slug}-{admission["source_id"]}-lines.json'
  command([TOOLS/'measure_lines.py',admission['picks'],admission['sidecar'],dest])
  actual=read(dest);prior=read(admission['measurement_result'])
  assert actual==prior, f'line refinement mismatch: {slug} {admission["source_id"]}'
  for row in actual['lines']:
   if row['id'] in admission['accepted_ids']:rows[(admission['source_id'],row['id'])]=row
  full_selection.append(dict(town=slug,**admission))
 for i,row in enumerate(fresh['lines']):
  key=(row['source_id'],row['id']);raw=rows[key]
  rebuilt={**row,**raw};rebuilt['source_id']=row['source_id'];rebuilt['system']=row['system']
  if 'system_from_picks' in row:rebuilt['system_from_picks']=row['system_from_picks']
  assert rebuilt==row,f'accepted line mismatch {slug} {key}'
  fresh['lines'][i]=rebuilt
  assert row.get('source_locator') and row['sigma_deg']>0 and row['length_m']>0
 for source in fresh['sources']:
  if source['kind']=='plan':
   assert source['north_class'] in ['true','magnetic','grid','unspecified']
   assert source['north_evidence'] and source['measured_arrow']['sigma_deg']>0
 write(AUDIT/f'{slug}-input.json',fresh)
 stdout=command([TOOLS/'systems.py',AUDIT/f'{slug}-input.json',AUDIT/f'{slug}-town.json','--summary',OWN/'summary-H-v2.csv'])
 rerun=read(AUDIT/f'{slug}-town.json')
 for val in [rerun,expected]:val.pop('created_utc',None)
 assert rerun==expected,f'town reconstruction mismatch: {slug}'
 assert all(s['deviation_window_deg']<=6+1e-10 for s in rerun['systems'])
 checks.append(dict(town=slug,record=final_paths[slug],refinement_reproduced=True,systems_reproduced=True,accepted_line_count=len(fresh['lines']),source_and_error_fields_complete=True,all_system_windows_within_six_degrees=True,warnings=[dict(source_id=s['source_id'],system=s['id'],warnings=s['warnings']) for s in rerun['systems'] if s['warnings']]))
 print(slug,'PASS',len(fresh['lines']),'accepted lines',flush=True)
 # A final accepted-only view records the rejected Figure 4 candidates explicitly.
 if slug=='mitathal':
  original=read(OWN/'picks/mitathal/plan-02-lines-v1.json');original['lines']=[r for r in original['lines'] if r['id'] not in ['11-west','11-east']]
  path=OWN/'picks/mitathal/plan-02-accepted-lines-v2.json';write(path,original)
  command([OWN/'H_work.py','overlay',RAW/'mitathal/plan-02-100-v2.png',path,RAW/'mitathal/plan-02-accepted-check-v2.png'])
assert set(final_paths)==set(SLUGS)
write(OWN/'selection-H-v2.json',dict(schema_version=1,measurement_selection=full_selection))
write(OWN/'FINAL-H.json',dict(schema_version=1,measurer='A',share='Haryana, Rajasthan and Indian Punjab',towns=final_paths,summary=str(OWN/'summary-H-v2.csv').replace('\\','/'),sources=str(OWN/'sources-H.json').replace('\\','/'),log=str(OWN/'LOG-H.md').replace('\\','/'),superseded=['summary-H.csv','towns/mitathal.json','selection-H-v1.json'],reason='Mitathal wall 40 is separated to satisfy the six-degree grouping rule; all first outputs are preserved.'))
write(OWN/'verification-H-v1.json',dict(schema_version=1,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),towns=checks,coverage_pass=True,reproduction_pass=True,imagery_lines=0,imagery_plan_comparison='not assessable: no admitted imagery bearings',free_bytes=shutil.disk_usage(OWN).free,tool_mutations=False,git_mutations=False))
