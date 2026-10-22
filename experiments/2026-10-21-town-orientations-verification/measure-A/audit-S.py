"""Record read-only Git status and the southern run's explicitly owned paths."""
import json,subprocess,sys,datetime,hashlib,shutil
from pathlib import Path
owned=Path(__file__).resolve().parent;root=owned.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rel(p):return Path(p).resolve().relative_to(root).as_posix()
verification=read(owned/'verification-S-v1/verification-report.json')
status=subprocess.run(['git','-c','safe.directory='+root.as_posix(),'status','--porcelain','--untracked-files=normal'],cwd=root,text=True,encoding='utf-8',capture_output=True,check=True)
out=owned/'invariant-audit-S-v1.json'
report=dict(schema_version=1,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),git_command='git -c safe.directory=<repository> status --porcelain --untracked-files=normal',git_status=status.stdout.splitlines(),git_mutations_performed=False,output_paths_owned=verification['all_output_paths_owned'],town_count=verification['town_count'],line_count=verification['line_count'],measurement_tools_modified=False,forbidden_study_or_other_measurer_contents_consulted=False,stated_orientation_exposures='Logged in LOG-S.md; excluded from picks and measurements',commercial_imagery_or_osm_geometry_used=False,network_scope='Plan-scan discovery and acquisition only; no imagery acquired',source_reads='Infra venv Python in isolated mode; UTF8 option used when needed',overwrite_policy='Fresh renders, picks, refinements, town outputs and verification files. LOG-S.md appended as the work progressed; summary-S.csv appended once per town by systems.py.',free_bytes=shutil.disk_usage('C:/').free,known_measurement_condition_failure='Sutkagen-dor main system singleton, visible in town JSON and summary',verification_report=rel(owned/'verification-S-v1/verification-report.json'),scripts=[rel(p) for p in owned.glob('*S.py')])
with out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
# Local-only bibliography supplement to the render records already in sources-S.json.
index=read(owned/'sources-S.json');resources={}
for r in index['render_observations']:
    p=Path(r['source']);key=p.resolve().as_posix()
    resources.setdefault(key,dict(source_path=rel(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pdf_pages=set(),render_sidecars=[]))
    if r['pdf_page'] is not None:resources[key]['pdf_pages'].add(r['pdf_page'])
    resources[key]['render_sidecars'].append(r['sidecar'])
for r in resources.values():
    r['pdf_pages']=sorted(r['pdf_pages']);r['rights_notice']='See source/acquisition record in sources-S.json. Locally held reports without a verified licence remain local-only.'
    name=Path(r['source_path']).name
    if name=='jansen_urban1987_interim2_govscan_77275.pdf':r['citation']='Michael Jansen and Günter Urban (eds), Interim Reports, vol.2, Aachen1987; inspected chapters and figures listed in LOG-S.md. Forbidden orientation chapter was not rendered.'
    elif name=='marshall_1931_govscan_14985.pdf':r['citation']='John Marshall (ed.), Mohenjo-daro and the Indus Civilization,1931, held scan; preface and contents pages inspected only.'
    elif name=='vats_1940_govscan_9842.pdf':r['citation']='Madho Sarup Vats (1940), Excavations at Harappa, II: Plates, Delhi.'
    elif name=='mackay_1943_chandaro.pdf':r['citation']='Ernest J.H. Mackay (1943), Chanhu-daro Excavations1935-36, American Oriental Series20.'
with (owned/'source-resource-audit-S-v1.json').open('x',encoding='utf-8') as f:json.dump(dict(schema_version=1,resources=list(resources.values())),f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:report[k] for k in ['town_count','line_count','output_paths_owned','git_mutations_performed','free_bytes']}))
