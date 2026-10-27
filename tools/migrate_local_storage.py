"""Plan and byte-verify local-only storage relocation; mutation uses PowerShell."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('D:/projects/indus_valley_script')
if os.name == 'nt':
    ROOT = Path('\\\\?\\' + str(ROOT))
    DEST = Path('\\\\?\\' + str(DEST))
WALK_ERRORS = []

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def walk(root):
    stack = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = os.scandir(directory)
        except OSError as exc:
            WALK_ERRORS.append(dict(path=str(directory), error=str(exc)))
            continue
        with entries:
            for e in entries:
                if e.is_symlink() or e.is_junction():
                    continue
                if e.is_dir(follow_symlinks=False):
                    stack.append(Path(e.path))
                else:
                    yield Path(e.path), e.stat().st_size

def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['plan', 'verify'])
    p.add_argument('--manifest', required=True)
    a = p.parse_args()
    manifest = Path(a.manifest)
    if a.action == 'plan':
        tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
        files = []
        for path, size in walk(ROOT):
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith('.git/') or rel in tracked:
                continue
            files.append((rel, size))
        # Whole acquired-source trees retain their nested repositories and notices.
        directories = [f'data/{n}' for n in ['raw', 'lipi', 'mayig', 'indus_website', 'normalized', 'six-hour']]
        directories += ['tmp', '.playwright-cli', 'research/literature/sources', 'research/literature/primary']
        directories = [d for d in directories if (ROOT/d).is_dir()]
        for d in directories:
            if any(t.startswith(d + '/') for t in tracked if t):
                raise SystemExit('Refusing whole-tree move with tracked files: ' + d)
        def in_tree(rel):
            return any(rel.startswith(d + '/') for d in directories)
        candidates = [rel for rel, size in files if not in_tree(rel) and size >= 1_000_000]
        payload = ''.join(rel + '\0' for rel in candidates).encode()
        ignored = set(subprocess.run(['git', 'check-ignore', '--stdin', '-z'], input=payload,
                                     stdout=subprocess.PIPE, cwd=ROOT, check=False).stdout.decode().split('\0')) if candidates else set()
        rows = [{'relative_path': rel, 'bytes': size} for rel, size in files
                if in_tree(rel) or rel in ignored]
        print(json.dumps(dict(stage='hashing', files=len(rows), bytes=sum(r['bytes'] for r in rows), inaccessible_directories=WALK_ERRORS)), flush=True)
        def hash_source(row):
            try:
                row['sha256'] = digest(ROOT/row['relative_path'])
            except OSError as exc:
                row['access_error'] = str(exc)
            return row
        with ThreadPoolExecutor(max_workers=32) as pool:
            with manifest.with_suffix('.hash-progress.jsonl').open('x', encoding='utf-8') as progress:
                hashed = []
                for row in pool.map(hash_source, rows):
                    progress.write(json.dumps(row) + '\n')
                    hashed.append(row)
                    if len(hashed) % 20000 == 0:
                        print(f'Hashed {len(hashed)} files', flush=True)
                rows = hashed
        inaccessible_files = [r for r in rows if 'access_error' in r]
        rows = [r for r in rows if 'sha256' in r]
        preserve = {Path(e['path']).parent.relative_to(ROOT).as_posix() for e in WALK_ERRORS}
        preserve.update(Path(e['relative_path']).parent.as_posix() for e in inaccessible_files)
        preserve = sorted(d for d in preserve if not any(d.startswith(other+'/') for other in preserve if d != other))
        individual = [r['relative_path'] for r in rows if not any(r['relative_path'].startswith(d+'/') for d in directories)]
        out = dict(source_root=str(ROOT).removeprefix('\\\\?\\'), destination_root=str(DEST).removeprefix('\\\\?\\'), directories=directories,
                   individual_files=individual, files=rows, total_bytes=sum(r['bytes'] for r in rows), inaccessible_directories=WALK_ERRORS,
                   inaccessible_files=inaccessible_files, preserve_trees=preserve)
        with manifest.open('x', encoding='utf-8') as f:
            json.dump(out, f, indent=2)
        print(json.dumps(dict(files=len(rows), directories=directories, individual_files=len(individual), bytes=out['total_bytes'])), flush=True)
    else:
        data = json.loads(manifest.read_text(encoding='utf-8'))
        def verify(row):
            target = DEST/row['relative_path']
            return None if target.is_file() and target.stat().st_size == row['bytes'] and digest(target) == row['sha256'] else row['relative_path']
        failures = []
        with ThreadPoolExecutor(max_workers=32) as pool:
            for i, failure in enumerate(pool.map(verify, data['files']), 1):
                if failure:
                    failures.append(failure)
                if i % 20000 == 0:
                    print(f'Verified {i} destination files', flush=True)
        result = dict(verified_files=len(data['files']), verified_bytes=data['total_bytes'], failures=failures)
        with manifest.with_suffix('.verification.json').open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(json.dumps(result), flush=True)
        if failures:
            raise SystemExit(1)

if __name__ == '__main__':
    main()
