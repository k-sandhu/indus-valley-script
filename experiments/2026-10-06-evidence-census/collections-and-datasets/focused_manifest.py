"""List all focused-pass writes within the two authorized directories."""
import hashlib,json
from focused_analysis import OWN,ROOT,RAW,dump

updated={'PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','collection-register.json','collection-register.csv','dataset-register.json','metadata-field-matrix.csv','paired-sample-audit.csv','sources.json','registry-entry.json'}
untouched={'build_registers.py','apply_depth_pass.py','depth_queries.py','museum-api-query-counts.csv'}
rows=[]
for path in sorted(OWN.rglob('*')):
    if not path.is_file() or path.name in untouched or path.name=='CHANGES.json':continue
    rows.append(dict(path=path.relative_to(ROOT).as_posix(),action='updated' if path.parent==OWN and path.name in updated else 'created',bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
for path in sorted(RAW.rglob('*')):
    if path.is_file():rows.append(dict(path=path.relative_to(ROOT).as_posix(),action='created_local_raw',bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
rows.append(dict(path=(OWN/'CHANGES.json').relative_to(ROOT).as_posix(),action='created',bytes=None,sha256=None))
dump(OWN/'CHANGES.json',dict(date='2026-10-07',scope='Focused pass only; earlier depth raw and shared files were not edited',paths=rows,counts={action:sum(r['action']==action for r in rows) for action in ['updated','created','created_local_raw']},created_directories=[(OWN/'history/2026-10-07-depth-pass').relative_to(ROOT).as_posix(),RAW.relative_to(ROOT).as_posix(),(RAW/'tmp').relative_to(ROOT).as_posix()],self_hash_note='The manifest lists itself without a recursive self-hash.'))
print('Manifest paths',len(rows))
