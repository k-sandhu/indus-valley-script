"""Acquire A2 sources with the frozen downloader.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/acquire.py --root .
Each file has its own directory. Existing acquisition records are checked and skipped.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

FILES = [
    ('asi-ar-1909-10', 'in.ernet.dli.2015.35501', '2015.35501.Archaeological-Survey-Of-India-Annual-Report-1909-10.pdf', 15007114, 'f243690ee494f2a70d1bd22dc97662c3c7ed22f0', 'primary-pdf'),
    ('asi-ar-1911-12', 'in.ernet.dli.2015.207521', '2015.207521.Annual-Report.pdf', 33076046, '41dc237f927bd59036c96e8141d7974c5104dd5c', 'primary-pdf'),
    ('asi-ar-1911-12', 'in.ernet.dli.2015.207521', '2015.207521.Annual-Report_djvu.txt', 725708, '8c78308cf1c462de3b2e282393360d95ca09256c', 'primary-ocr'),
    ('asi-ar-1911-12', 'in.ernet.dli.2015.35495', '2015.35495.Archaeological-Survey-Of-India--Annual-Report-1911-12.pdf', 18393279, '38ea23a44a42ec76bb2900029514a066875e34a0', 'alternate-pdf'),
    ('mahadevan-2003', 'iravatham-mahadevan-early-tamil-epigraphy-from-the-earliest-times-to-the-sixth-century-a.-d.', 'Iravatham Mahadevan - Early Tamil Epigraphy - From the Earliest Times to the Sixth Century A.D..pdf', 233674839, '38db2ae4be16ee3272a9e9824328365096dc6b1c', 'primary-pdf'),
    ('mahadevan-2003', 'iravatham-mahadevan-early-tamil-epigraphy-from-the-earliest-times-to-the-sixth-century-a.-d.', 'Iravatham Mahadevan - Early Tamil Epigraphy - From the Earliest Times to the Sixth Century A.D._djvu.txt', 1286552, 'b92c6dc82a4dfa3a6003764d02cce656dddee30a', 'primary-ocr'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    args = ap.parse_args()
    root = args.root.resolve()
    package = root / 'experiments/2026-10-21-head-direction-corpora'
    raw = root / 'data/raw/2026-10-21-head-direction-corpora'
    scratch = raw / 'codex-a2'
    scratch.mkdir(parents=True, exist_ok=True)
    baseline = scratch / 'git-status-start.txt'
    if not baseline.exists():
        result = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', 'status', '--porcelain', '--untracked-files=all'], cwd=root, capture_output=True, check=True)
        baseline.write_bytes(result.stdout)
    seen = set()
    jobs = []
    for source, item, name, size, sha1, label in FILES:
        if item not in seen:
            seen.add(item)
            jobs.append((source, item, 'metadata.json', None, None, 'metadata-' + item, 'https://archive.org/metadata/' + quote(item, safe='')))
        url = 'https://archive.org/download/' + quote(item, safe='') + '/' + quote(name, safe='')
        jobs.append((source, item, name, size, sha1, label, url))
    for source, item, name, size, sha1, label, url in jobs:
        stem = source.replace('asi-ar-', 'asi-')
        dest = raw / ('src-' + stem + '-' + label)
        record = package / 'acquisition' / (source + '-' + label + '.json')
        if record.exists():
            rec = json.loads(record.read_text(encoding='utf-8'))
            target = root / rec['local_path']
            if target.stat().st_size != rec['bytes'] or hashlib.sha256(target.read_bytes()).hexdigest() != rec['sha256']:
                raise ValueError('Existing acquisition differs: ' + str(record))
            print('verified existing ' + record.name, flush=True)
            continue
        year = 1914 if source == 'asi-ar-1909-10' else 1915
        rights = ('Copyright 2003, Cre-A and Harvard University; third-party upload with no licence; local-only, aggregates only in tracked files' if source == 'mahadevan-2003' else f'Government of India publication of {year}; public domain by age in India and the United States (our assessment); Internet Archive item states no licence')
        title = 'Early Tamil Epigraphy (2003)' if source == 'mahadevan-2003' else 'Archaeological Survey of India Annual Report ' + source.removeprefix('asi-ar-')
        command = [sys.executable, '-I', str(package / 'fetch_source.py'), '--url', url, '--dest', str(dest.relative_to(root)), '--name', name, '--record', str(record.relative_to(root)), '--source-id', source, '--title', title, '--rights-status', 'rights-unverified', '--rights-note', rights, '--note', 'Internet Archive item ' + item + '; A2 ' + label]
        if sha1:
            command.extend(['--expect-sha1', sha1, '--expect-bytes', str(size)])
        print('acquiring ' + source + ' ' + label, flush=True)
        subprocess.run(command, cwd=root, check=True)


if __name__ == '__main__':
    main()
