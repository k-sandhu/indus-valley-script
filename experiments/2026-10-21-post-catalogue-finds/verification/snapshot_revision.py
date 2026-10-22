"""Preserve results and freeze the externally revised audit input."""
import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import BASE,OUT,ROOT,csvrows,save,safe,norm
from safe_read import RESTRICTED,UNIT

prior=OUT/'initial-results-2026-10-21'
prior.mkdir(exist_ok=True)
for name in ['sampling.json','blind-sample.csv','blind-summary.json','count-check.json','coordinator-join-check.json','dholavira-grid-check.json','locator-check.json','resume-integrity.json','content-check.json','omission-sample.csv','omission-summary.json']:
    if (OUT/name).exists() and not (prior/name).exists():shutil.copyfile(OUT/name,prior/name)
dest=OUT/'revised-input-2026-10-21'
dest.mkdir(exist_ok=True)
initial=json.loads((OUT/'sampling.json').read_text(encoding='utf-8'))['inputs']
records=[]
for name in ['objects.csv','sites.csv','join-decisions.csv','local-unnamed.csv']:
    p=BASE/name;b=p.read_bytes();s=b.decode('utf-8-sig')
    if RESTRICTED.search(s) or UNIT.search(s):raise SystemExit('Snapshot rejected by content guard; input not copied.')
    target=dest/name
    if target.exists():raise SystemExit('Revision snapshot already exists; refusing to replace it.')
    target.write_bytes(b)
    sha=hashlib.sha256(b).hexdigest()
    records.append({'input':str(p.relative_to(ROOT)),'snapshot':str(target.relative_to(ROOT)),'sha256':sha,'initial_sha256':initial.get(str(p.relative_to(ROOT))),'changed_from_initial':initial.get(str(p.relative_to(ROOT))) not in (sha,None)})
current={r['row_id']:r for r in csvrows(dest/'objects.csv')}
drift=[]
for r in csvrows(OUT/'blind-sample.csv'):
    if r['field']=='registration_present':continue
    if r['table_value']!=current[r['row_id']][r['field']]:drift.append({'row_id':r['row_id'],'field':r['field'],'initial_table_value':safe(r['table_value']),'revised_table_value':safe(current[r['row_id']][r['field']])})
save('input-revision.json',{'captured_utc':datetime.now(timezone.utc).isoformat(),'cause':'External edits occurred while verification was in progress. Run 4 wrote no source-list file.','inputs':records,'sampled_field_changes':drift,'initial_result_directory':str(prior.relative_to(ROOT)),'interpretation':'The original blind observations and comparisons remain the initial endpoint. Structural checks of the revised input are reported separately.'})
print('SNAPSHOT captured',len(records),'inputs; sampled field changes',len(drift))
for r in records:print(r['input'],r['sha256'])
