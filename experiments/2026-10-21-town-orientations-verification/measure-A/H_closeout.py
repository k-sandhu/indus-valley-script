import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,subprocess,shutil,datetime
own=Path(sys.argv[1]);raw=Path(sys.argv[2]);root=Path.cwd();slugs=['kalibangan','banawali','rakhigarhi','farmana','bhirrana','kunal','mitathal','karanpura']
audit=json.loads((own/'verification-H-v1.json').read_text())
assert audit['reproduction_pass'] and len(audit['towns'])==8
status=subprocess.run(['git','--no-optional-locks','-c','safe.directory='+str(root).replace('\\','/'),'status','--porcelain'],capture_output=True,text=True,check=True)
with (own/'git-status-H-v1.txt').open('x',encoding='utf-8') as f:f.write(status.stdout)
free=shutil.disk_usage(root).free
assert free>=1_000_000_000
with (own/'LOG-H.md').open('a',encoding='utf-8') as f:
 f.write('\nFinal checks passed for all eight towns and 42 accepted lines. All admitted line refinements, arrow measurements and system calculations reproduce. The final CSV is summary-H-v2.csv, and FINAL-H.json gives the active town paths. Banawali\'s main singleton warning is retained. No imagery–plan difference can be calculated. The final read-only git status used --no-optional-locks and a per-command ownership exception; it is retained in git-status-H-v1.txt. Other contributors\' changes remain present. The owned-file inventory checks every path from this share against the two allowed roots. No commits, branch changes, stash, reset, Git configuration edits, supplied-tool edits, writes outside the owned roots, commercial imagery, OSM geometry, forbidden source accesses or overwrites of prior output files were performed. Logs and the tool-generated CSV were appended as required. Free space at closeout was '+str(free)+' bytes.\n')
files=list(own.glob('H_*.py'))
for name in ['LOG-H.md','sources-H.json','summary-H.csv','summary-H-v2.csv','summary-mitathal-revision-H-v2.csv','selection-H-v1.json','selection-H-v2.json','FINAL-H.json','verification-H-v1.json','git-status-H-v1.txt']:files.append(own/name)
for slug in slugs:
 files.extend((own/'picks'/slug).rglob('*'));files.extend((own/'towns').glob(slug+'*.json'));files.extend((raw/slug).rglob('*'))
for name in ['audit-H-v1','audit-H-v2']:files.extend((own/name).rglob('*'))
rows=[]
for p in sorted(set(p.resolve() for p in files if p.is_file())):
 assert p.is_relative_to(own.resolve()) or p.is_relative_to(raw.resolve()),str(p)
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 rows.append(dict(path=str(p.relative_to(root)).replace('\\','/'),bytes=p.stat().st_size,sha256=digest))
out=own/'owned-files-H-v1.json'
with out.open('x',encoding='utf-8') as f:json.dump(dict(schema_version=1,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),paths_within_owned_roots=True,file_count=len(rows),free_bytes=free,git_status_record=str(own/'git-status-H-v1.txt').replace('\\','/'),files=rows),f,indent=2)
print(json.dumps(dict(towns=8,accepted_lines=42,reproduction_pass=True,owned_file_count=len(rows),paths_within_owned_roots=True,free_bytes=free,git_status_lines=len(status.stdout.splitlines()))))
