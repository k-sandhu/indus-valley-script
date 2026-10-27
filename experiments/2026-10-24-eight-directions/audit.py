"""Check package boundaries, storage roots and preserved shared inputs."""
from pathlib import Path
import hashlib
import json
import sys

from coordinate import ROOT, PACKAGE, TRACKS

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def audit():
    errors = []
    rows = []
    protected = json.loads((PACKAGE / 'protected-files.json').read_text(encoding='utf-8'))
    changed = [p for p, expected in protected.items() if digest(ROOT / p) != expected]
    if changed:
        errors.append({'protected_inputs_changed': changed})
    raw_root = Path('D:/projects/indus_valley_script/data/raw').resolve()
    junction_root = (ROOT / 'data/raw').resolve()
    if raw_root != junction_root:
        errors.append('Checkout raw junction no longer resolves to the intended D: root.')
    for number, qid, issue, title, slug, attempt_id in TRACKS:
        package = ROOT / 'experiments' / f'2026-10-24-{slug}'
        raw = raw_root / f'2026-10-24-{slug}'
        entry_path = ROOT / 'knowledge/registry/attempts' / f'{attempt_id}.json'
        required = ['PROTOCOL.md', 'REPORT.md', 'RETROSPECTIVE.md', 'DATA-UPDATE.md', 'changed-paths.json']
        missing = [name for name in required if not (package / name).is_file()]
        if not raw.is_dir():
            missing.append('D: raw directory')
        if not entry_path.is_file():
            missing.append('attempt registry entry')
            entry = {}
        else:
            entry = json.loads(entry_path.read_text(encoding='utf-8-sig'))
        if missing:
            errors.append({'direction': number, 'missing': missing})
        broken = []
        for reference in entry.get('evidence', []):
            path = reference.split('#', 1)[0]
            if path and not (ROOT / path).exists():
                broken.append(reference)
        if broken:
            errors.append({'direction': number, 'broken_evidence': broken})
        binary_suffixes = {'.pdf','.png','.jpg','.jpeg','.tif','.tiff','.webp','.zip','.parquet','.sqlite','.db'}
        misplaced = []
        hashes = {}
        invalid_json = []
        for path in sorted(package.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            rel = path.relative_to(ROOT).as_posix()
            hashes[rel] = digest(path)
            if path.suffix.lower() in binary_suffixes:
                misplaced.append(rel)
            if path.suffix == '.json':
                try:
                    json.loads(path.read_text(encoding='utf-8-sig'))
                except (ValueError, UnicodeError) as exc:
                    invalid_json.append({'path':rel,'error':str(exc)})
        if misplaced:
            errors.append({'direction':number,'research_binaries_in_checkout':misplaced})
        if invalid_json:
            errors.append({'direction':number,'invalid_json':invalid_json})
        raw_files = list(raw.rglob('*')) if raw.is_dir() else []
        raw_files = [p for p in raw_files if p.is_file()]
        rows.append({'direction':number, 'question':qid, 'title':title,
                     'package':package.relative_to(ROOT).as_posix(),
                     'raw_physical':str(raw.resolve()), 'raw_file_count':len(raw_files),
                     'raw_bytes':sum(p.stat().st_size for p in raw_files),
                     'missing':missing, 'broken_evidence':broken,
                     'registry_id':entry.get('id'), 'registry_authors':entry.get('authors'),
                     'package_sha256':hashes})
    return {'status':'pass' if not errors else 'fail', 'scope':'Package integrity, D: storage and preserved inputs; scientific review recorded separately.',
            'protected_file_count':len(protected), 'protected_changed':changed,
            'raw_root':str(raw_root), 'junction_root':str(junction_root),
            'directions':rows, 'errors':errors}

if __name__ == '__main__':
    target = Path(sys.argv[1])
    if target.exists():
        raise SystemExit('Refusing to overwrite a prior audit.')
    result = audit()
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'directions':len(result['directions']),'errors':result['errors']},indent=2))
    raise SystemExit(0 if result['status']=='pass' else 1)
