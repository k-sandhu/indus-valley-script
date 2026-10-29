"""Freeze the list of untracked and modified tracked files for the publication screen."""
from pathlib import Path
import hashlib, json, subprocess, sys, datetime

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/2026-10-13-publication-screen'
SELF = 'experiments/2026-10-13-publication-screen/'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    out = RAW / (sys.argv[1] if len(sys.argv) > 1 else 'inventory.json')
    if out.exists():
        raise SystemExit(f'Refusing to overwrite {out}')
    untracked = sorted(set(git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')) - {''})
    modified = []
    for line in git('status', '--porcelain=v1', '-z').decode().split('\0'):
        if line and not line.startswith('??') and len(line) > 3:
            modified.append(line[3:])
    files = []
    for kind, names in (('untracked', untracked), ('modified-tracked', sorted(modified))):
        for name in names:
            if name.startswith(SELF):
                continue
            p = ROOT / name
            if not p.is_file():
                files.append({'path': name, 'kind': kind, 'bytes': None, 'sha256': None})
                continue
            b = p.read_bytes()
            files.append({'path': name, 'kind': kind, 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()})
    RAW.mkdir(parents=True, exist_ok=True)
    rec = {'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
           'head': git('rev-parse', 'HEAD').decode().strip(),
           'untracked_files': sum(f['kind'] == 'untracked' for f in files),
           'modified_tracked_files': sum(f['kind'] == 'modified-tracked' for f in files),
           'bytes': sum(f['bytes'] or 0 for f in files), 'files': files}
    out.write_text(json.dumps(rec, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in rec.items() if k != 'files'}, indent=1))


if __name__ == '__main__':
    main()
