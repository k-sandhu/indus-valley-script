"""Capture the pre-run state without altering existing research records."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot')

def write_json(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def digest(p):
    return hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()

def main():
    assert (ROOT / 'data/raw').resolve() == RAW.parent.resolve()
    RAW.mkdir(exist_ok=False)
    paths = [ROOT / 'bench/spent.json', ROOT / 'knowledge/experiments/registry.json', ROOT / 'knowledge/MAP.md']
    slugs = ('eight-directions', 'object-identity', 'harappa-context', 'office-seal', 'unit-source', 'source-review')
    for p in sorted((ROOT / 'experiments').glob('2026-10-24-*')):
        if any(p.name.startswith('2026-10-24-' + slug) for slug in slugs):
            paths.extend(f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
    frozen = [{'path':p.relative_to(ROOT).as_posix(), 'sha256':digest(p), 'bytes':p.stat().st_size} for p in paths if p.exists()]
    write_json(PKG / 'protected-files.json', frozen)
    shared = []
    for rel in ('knowledge/DATA.md', 'data/MANIFEST.json'):
        src = ROOT / rel
        dest = RAW / (src.name + '.before')
        shutil.copyfile(src, dest)
        shared.append({'path':rel, 'sha256':digest(src), 'snapshot':dest.as_posix()})
    write_json(PKG / 'shared-before.json', shared)
    write_json(PKG / 'storage-check.json', {'utc':datetime.now(timezone.utc).isoformat(), 'logical':'data/raw/2026-10-26-object-pilot', 'physical':RAW.as_posix(), 'free_bytes':shutil.disk_usage(RAW).free})
    (PKG / 'baseline-status.txt').write_text(subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True,check=True).stdout,encoding='utf-8')
    print(json.dumps({'protected_files':len(frozen),'raw':str(RAW)}))

if __name__ == '__main__':
    main()
