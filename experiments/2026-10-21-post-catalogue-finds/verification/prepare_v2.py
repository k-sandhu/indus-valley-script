"""Freeze the second follow-up audit without changing earlier endpoints."""
import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,csvrows,save
from safe_read import RESTRICTED,UNIT

def main():
    target=OUT/'input-v2-2026-10-21'
    target.mkdir(exist_ok=True)
    first={}
    for name in ['count-check.json','coordinator-join-check.json','locator-check.json','content-check.json','blind-freeze.json','blind-observations-frozen.csv','blind-sample.csv','blind-summary.json','omission-assignments.csv']:
        p=OUT/name;first[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':json.loads(p.read_text(encoding='utf-8-sig'))
        elif p.suffix=='.csv':
            with p.open(encoding='utf-8-sig',newline='') as f:rs=list(csv.reader(f,strict=True))
            assert rs and all(len(r)==len(rs[0]) for r in rs)
    backups=OUT/'pre-v2-reports-2026-10-21';backups.mkdir(exist_ok=True)
    for name in ['VERIFICATION.md','final.md','RETROSPECTIVE.md','omission-sample.csv','omission-summary.json']:
        if not (backups/name).exists():shutil.copyfile(OUT/name,backups/name)
    records=[]
    for name in ['objects.csv','sites.csv','join-decisions.csv','local-unnamed.csv']:
        p=BASE/name;b=p.read_bytes();s=b.decode('utf-8-sig')
        if RESTRICTED.search(s) or UNIT.search(s):raise SystemExit('Snapshot content guard rejected an input; no unsafe content copied.')
        dest=target/name
        if dest.exists():raise SystemExit('The v2 snapshot already exists; refusing replacement.')
        dest.write_bytes(b)
        rs=csvrows(dest)
        with dest.open(encoding='utf-8-sig',newline='') as f:raw=list(csv.reader(f,strict=True))
        assert raw and all(len(r)==len(raw[0]) for r in raw)
        records.append({'input':str(p.relative_to(ROOT)),'snapshot':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'rows':len(rs),'columns':list(rs[0]) if rs else []})
    save('input-manifest-v2.json',{'captured_utc':datetime.now(timezone.utc).isoformat(),'inputs':records,'preserved_first_versions':first,'authors':'Codex / GPT-6 / API tool harness','scope':'Second follow-up audit. The original blind observations and check outputs are preserved.'})
    for r in records:print(Path(r['input']).name,'rows',r['rows'],'headers',r['columns'])
    print('SNAPSHOT v2 complete; first-version hashes recorded.')

if __name__=='__main__':
    try:main()
    except OSError as e:
        try:save('WRITE-FAILURE-v2.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
