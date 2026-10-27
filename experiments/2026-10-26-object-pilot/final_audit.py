"""Check preservation, owned artifacts and the scoped shared inventory update."""
import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot')
PACKAGES = [PKG] + [ROOT / 'experiments' / ('2026-10-26-' + s) for s in ('object-pilot-register', 'image-recovery', 'source-conflicts', 'object-pilot-review')]

def read_json(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    checks = []
    def check(name, passed, detail=None):
        checks.append({'check':name, 'passed':bool(passed), 'detail':detail})
    protected = read_json(PKG / 'protected-files.json')
    changed = [x['path'] for x in protected if not (ROOT / x['path']).exists() or sha(ROOT / x['path']) != x['sha256']]
    check('frozen inputs unchanged', not changed, {'count':len(protected), 'changed':changed})
    check('data junction resolves to D', (ROOT/'data/raw').resolve() == RAW.parent.resolve())
    parsed = 0
    py_count = 0
    bad = []
    forbidden = []
    for package in PACKAGES:
        for f in package.rglob('*'):
            if not f.is_file():
                continue
            if '__pycache__' in f.parts or f.suffix.lower() in {'.png','.jpg','.jpeg','.pdf','.html','.sqlite','.db','.pyc'}:
                forbidden.append(str(f.relative_to(ROOT)))
            try:
                if f.suffix == '.json':
                    read_json(f)
                    parsed += 1
                elif f.suffix == '.py':
                    ast.parse(f.read_text(encoding='utf-8-sig'), filename=str(f))
                    py_count += 1
            except (ValueError, SyntaxError) as e:
                bad.append({'path':str(f), 'error':str(e)})
    check('owned JSON and Python parse', not bad, {'json_files':parsed, 'python_files':py_count, 'errors':bad})
    check('source payloads and runtime caches absent from owned checkout packages', not forbidden, forbidden)
    before = read_json(RAW / 'MANIFEST.json.before')
    current = read_json(ROOT / 'data/MANIFEST.json')
    old_by_id = {x['id']:x for x in before['sources']}
    now_by_id = {x['id']:x for x in current['sources']}
    changed_sources = [key for key,value in old_by_id.items() if now_by_id.get(key) != value]
    check('all earlier manifest entries preserved', not changed_sources, changed_sources)
    new_entries = [x for x in current['sources'] if x['id'] not in old_by_id]
    expected = {'object-pilot-reviewed-2026-10-26', 'image-recovery-index-2026-10-26', 'object-source-conflicts-2026-10-26'}
    check('only three scoped manifest entries added', {x['id'] for x in new_entries} == expected, [x['id'] for x in new_entries])
    check('manifest status counts agree', dict(Counter(x['status'] for x in current['sources'])) == current['counts'], current['counts'])
    new_bindings = []
    for source in new_entries:
        for path, digest in source.get('hashes', {}).items():
            f = ROOT / path
            new_bindings.append({'path':path, 'passed':f.exists() and sha(f) == digest})
    check('new inventory hash bindings match', bool(new_bindings) and all(x['passed'] for x in new_bindings), new_bindings)
    data = (ROOT/'knowledge/DATA.md').read_text(encoding='utf-8-sig')
    check('scoped inventory section exists', 'Twenty-target object pilot, 26 October 2026' in data)
    check('shared manifest timestamp updated', current['updated'] == '2026-10-26')
    result = {'passed':all(x['passed'] for x in checks), 'checks':checks}
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({'passed':result['passed'], 'checks':len(checks), 'failed':[x['check'] for x in checks if not x['passed']]}))

if __name__ == '__main__':
    main()
