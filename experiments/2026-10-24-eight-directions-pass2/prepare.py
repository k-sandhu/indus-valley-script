"""Create a preserved starting record for the second eight-direction pass."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw')
SLUGS = ['object-identity-pass2','unit-source-pass2','harappa-context-pass2','office-seal-pass2',
         'tablet-use-pass2','lexical-evidence-pass2','readable-seal-pass2','town-phase-pass2']

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def save(name, data):
    with (PACKAGE/name).open('x',encoding='utf-8') as f:
        json.dump(data,f,indent=2,ensure_ascii=False)
        f.write('\n')

if __name__=='__main__':
    assert (ROOT/'data/raw').resolve()==RAW.resolve()
    assert shutil.disk_usage(RAW).free>10*1024**3
    previous=ROOT/'experiments/2026-10-24-eight-directions'
    rows=json.loads((previous/'dispatch-v7.json').read_text(encoding='utf-8'))
    for row,slug in zip(rows,SLUGS):
        row['prior_package']=row['package']
        row['package']='experiments/2026-10-24-'+slug
        row['physical_raw']=str(RAW/('2026-10-24-'+slug))
        row['attempt']=slug.upper()+'-2026-10-24'
        row['status']='pending'
        row.pop('claim_body',None)
        assert not (ROOT/row['package']).exists(),row['package']
        assert not Path(row['physical_raw']).exists(),row['physical_raw']
    protected=json.loads((previous/'protected-files.json').read_text())
    protected={p:digest(ROOT/p) for p in protected}
    prior_packages=[ROOT/r['prior_package'] for r in rows]+[previous,ROOT/'experiments/2026-10-24-office-source-verification']
    for folder in prior_packages:
        for p in folder.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                protected[p.relative_to(ROOT).as_posix()]=digest(p)
    save('protected-files.json',protected)
    save('dispatch-v1.json',rows)
    save('storage-check.json',{'raw_root':str(RAW.resolve()),'junction_target':str((ROOT/'data/raw').resolve()),'free_bytes':shutil.disk_usage(RAW).free})
    raw=RAW/'2026-10-24-eight-directions-pass2'
    raw.mkdir(exist_ok=False)
    result=subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',check=True)
    with (PACKAGE/'baseline-status.txt').open('x',encoding='utf-8') as f:f.write(result.stdout)
    print(json.dumps({'directions':len(rows),'protected_files':len(protected),'raw_root':str(raw)}))
