"""Check preserved inputs and the completed second-pass package boundaries."""
from pathlib import Path
import json
import sys

from prepare import ROOT, PACKAGE, RAW, digest

def check():
    errors = []
    protected = json.loads((PACKAGE/'protected-files.json').read_text(encoding='utf-8'))
    changed = [p for p,h in protected.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
    if changed:
        errors.append({'protected_files_changed':changed})
    if (ROOT/'data/raw').resolve()!=RAW.resolve():
        errors.append('Raw-data junction does not resolve to the D: root.')
    dispatch = max(PACKAGE.glob('dispatch-v*.json'),key=lambda p:int(p.stem.split('-v')[-1]))
    rows = json.loads(dispatch.read_text(encoding='utf-8'))
    results = []
    for row in rows:
        folder=ROOT/row['package']
        raw=Path(row['physical_raw'])
        registry=ROOT/'knowledge/registry/attempts'/f"{row['attempt']}.json"
        required=['PROTOCOL.md','REPORT.md','RETROSPECTIVE.md','DATA-UPDATE.md','changed-paths.json']
        missing=[name for name in required if not (folder/name).is_file()]
        if not raw.is_dir():missing.append('D: raw directory')
        if not registry.is_file():missing.append('attempt registry entry')
        if missing:errors.append({'direction':row['direction'],'missing':missing})
        broken=[]
        if registry.is_file():
            entry=json.loads(registry.read_text(encoding='utf-8-sig'))
            for ref in entry.get('evidence',[]):
                target=ref.split('#',1)[0]
                if target and not (ROOT/target).exists():broken.append(ref)
        if broken:errors.append({'direction':row['direction'],'broken_evidence':broken})
        hashes={}
        misplaced=[]
        invalid=[]
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:continue
            rel=path.relative_to(ROOT).as_posix()
            hashes[rel]=digest(path)
            if path.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.tif','.tiff','.webp','.zip','.sqlite','.db','.parquet'}:
                misplaced.append(rel)
            if path.suffix=='.json':
                try:json.loads(path.read_text(encoding='utf-8-sig'))
                except (ValueError,UnicodeError) as exc:invalid.append({'path':rel,'error':str(exc)})
        if misplaced:errors.append({'direction':row['direction'],'research_binaries_in_checkout':misplaced})
        if invalid:errors.append({'direction':row['direction'],'invalid_json':invalid})
        raw_files=[p for p in raw.rglob('*') if p.is_file()] if raw.is_dir() else []
        results.append({'direction':row['direction'],'package':row['package'],'physical_raw':str(raw.resolve()),
                        'raw_files':len(raw_files),'raw_bytes':sum(p.stat().st_size for p in raw_files),
                        'missing':missing,'broken_evidence':broken,'package_sha256':hashes})
    return {'status':'pass' if not errors else 'fail','scope':'Preserved inputs, package completeness and D: storage; interpretation review recorded separately.',
            'protected_file_count':len(protected),'protected_changed':changed,'dispatch':dispatch.name,
            'raw_root':str(RAW.resolve()),'directions':results,'errors':errors}

if __name__=='__main__':
    target=Path(sys.argv[1])
    if target.exists():raise SystemExit('Refusing to overwrite a prior audit.')
    result=check()
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'directions':len(result['directions']),'errors':result['errors']},indent=2))
    raise SystemExit(result['status']!='pass')
