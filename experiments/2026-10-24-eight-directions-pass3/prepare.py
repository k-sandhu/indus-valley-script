"""Preserve starting state for the third eight-direction evidence pass."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def save(name, data):
    with (PACKAGE / name).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write('\n')

if __name__ == '__main__':
    assert (ROOT / 'data/raw').resolve() == RAW.resolve()
    assert shutil.disk_usage(RAW).free > 10*1024**3
    previous = ROOT / 'experiments/2026-10-24-eight-directions-pass2'
    rows = json.loads((previous / 'dispatch-v6.json').read_text(encoding='utf-8'))
    protected = json.loads((previous / 'protected-files.json').read_text(encoding='utf-8'))
    for row in rows:
        for field in ['package', 'prior_package']:
            folder = ROOT / row[field]
            for path in folder.rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts:
                    protected[path.relative_to(ROOT).as_posix()] = digest(path)
        attempt = ROOT / 'knowledge/registry/attempts' / (row['attempt'] + '.json')
        protected[attempt.relative_to(ROOT).as_posix()] = digest(attempt)
        row['prior_package'] = row['package']
        row['package'] = row['package'].replace('-pass2', '-pass3')
        row['physical_raw'] = row['physical_raw'].replace('-pass2', '-pass3')
        row['attempt'] = row['attempt'].replace('-PASS2-', '-PASS3-')
        row['status'] = 'pending'
        row.pop('agent', None)
        assert not (ROOT / row['package']).exists()
        assert not Path(row['physical_raw']).exists()
    for folder in [previous, ROOT / 'experiments/2026-10-24-harappa-context-pass2-review']:
        for path in folder.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                protected[path.relative_to(ROOT).as_posix()] = digest(path)
    for name in ['EIGHT-DIRECTIONS-PASS2-2026-10-24', 'HARAPPA-CONTEXT-PASS2-REVIEW-2026-10-24']:
        path = ROOT / 'knowledge/registry/attempts' / (name + '.json')
        protected[path.relative_to(ROOT).as_posix()] = digest(path)
    protected = {path: digest(ROOT / path) for path in protected}
    save('protected-files.json', protected)
    save('dispatch-v1.json', rows)
    save('storage-check.json', {'raw_root': str(RAW.resolve()),
         'junction_target': str((ROOT / 'data/raw').resolve()), 'free_bytes': shutil.disk_usage(RAW).free})
    (RAW / PACKAGE.name).mkdir(exist_ok=False)
    status = subprocess.run(['git','status','--short'], cwd=ROOT, capture_output=True,
                            text=True, encoding='utf-8', check=True)
    with (PACKAGE / 'baseline-status.txt').open('x',encoding='utf-8') as stream:
        stream.write(status.stdout)
    print(json.dumps({'directions':len(rows),'protected_files':len(protected),'physical_raw':str(RAW/PACKAGE.name)}))
