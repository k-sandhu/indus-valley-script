"""Check explicit file/hash bindings in a parent review specification."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys

from prepare import ROOT, digest

def walk(value):
    if isinstance(value,dict):
        if 'sha256' in value and any(k in value for k in ('physical_path','logical_path','path')):
            yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)

def bindings(spec):
    rows=list(spec.get('bindings',[]))
    for source in spec.get('manifests',[]):
        file=Path(source['path'])
        if not file.is_absolute():file=ROOT/file
        data=json.loads(file.read_text(encoding='utf-8-sig'))
        base=Path(source.get('relative_base',str(ROOT)))
        for row in walk(data):
            key=next(k for k in ('physical_path','logical_path','path') if k in row)
            target=Path(row[key])
            if not target.is_absolute():target=(ROOT if key=='logical_path' else base)/target
            rows.append({'path':str(target),'sha256':row['sha256'],'manifest':str(file)})
    return rows

def verify(row):
    path=Path(row['path'])
    if not path.is_absolute():path=ROOT/path
    try:
        actual=digest(path)
        return dict(row,actual_sha256=actual,matches=actual==row['sha256'],physical_path=str(path.resolve()))
    except OSError as exc:
        return dict(row,matches=False,error=str(exc))

if __name__=='__main__':
    spec_path=Path(sys.argv[1]);out=Path(sys.argv[2])
    if out.exists():raise SystemExit('Refusing to overwrite an earlier byte review.')
    spec=json.loads(spec_path.read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=8) as pool:
        checks=list(pool.map(verify,bindings(spec)))
    errors=[r for r in checks if not r['matches']]
    result={'status':'pass' if not errors else 'fail','scope':spec['scope'],
            'specification':str(spec_path),'check_count':len(checks),'checks':checks,'errors':errors}
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'checks':len(checks),'errors':errors},indent=2))
    raise SystemExit(bool(errors))
