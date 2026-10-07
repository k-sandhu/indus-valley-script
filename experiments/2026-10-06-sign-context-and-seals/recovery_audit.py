"""Read-only artifact checks after the reported disk-full interruption."""
import argparse
import hashlib
import json
import os
import re
import shutil
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'


def sha256(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', default='FILE-MANIFEST-FOLLOWUP-2026-10-07.json')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    manifest_path = (OWN / args.manifest).resolve()
    destination = (OWN / args.output).resolve()
    if manifest_path.parent != OWN or destination.parent != OWN or destination.exists():
        raise ValueError('Use an existing owned manifest and a fresh owned output name.')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    issues = []
    hashed = 0
    for item in manifest['files']:
        path = ROOT / item['path']
        if not path.is_file():
            issues.append({'path': item['path'], 'issue': 'missing'})
        elif item['sha256'] is not None:
            hashed += 1
            if path.stat().st_size != item['bytes'] or sha256(path) != item['sha256']:
                issues.append({'path': item['path'], 'issue': 'size/hash mismatch'})
    actual = [p for folder in (OWN, RAW) for p in folder.rglob('*') if p.is_file()]
    known = {item['path'] for item in manifest['files']}
    new_paths = sorted(p.relative_to(ROOT).as_posix() for p in actual
                       if p.relative_to(ROOT).as_posix() not in known)
    formats = Counter()
    format_errors = []
    arrays = []
    import numpy as np
    for path in actual:
        relative = path.relative_to(ROOT).as_posix()
        try:
            if path.suffix == '.json':
                json.loads(path.read_text(encoding='utf-8'))
                formats['json'] += 1
            elif path.suffix == '.py' and OWN in path.parents:
                compile(path.read_text(encoding='utf-8'), str(path), 'exec')
                formats['owned_python'] += 1
            elif path.suffix == '.svg' and OWN in path.parents:
                ElementTree.parse(path)
                formats['owned_svg'] += 1
            elif path.suffix == '.npz':
                with zipfile.ZipFile(path) as archive:
                    bad_member = archive.testzip()
                    if bad_member:
                        raise ValueError(f'CRC failure: {bad_member}')
                formats['npz_crc'] += 1
            elif path.suffix == '.npy':
                array = np.load(path, mmap_mode='r', allow_pickle=False)
                arrays.append({'path': relative, 'shape': list(array.shape),
                               'dtype': str(array.dtype), 'payload_bytes': array.nbytes})
                del array
                formats['npy_header_and_mapping'] += 1
        except Exception as error:
            format_errors.append({'path': relative, 'error': str(error)})
    link_errors = []
    local_links = 0
    for path in OWN.rglob('*.md'):
        # Archived living documents retain their original link context byte for byte.
        base = OWN if path.parent.name == 'pre-followup-2026-10-07' else path.parent
        body = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^\s)]+)\)', body):
            target = target.strip('<>')
            if re.match(r'^(?:https?://|app://|mailto:|#)', target):
                continue
            target = target.split('#', 1)[0]
            if not target:
                continue
            local_links += 1
            if not (base / target).exists():
                link_errors.append({'path': path.relative_to(ROOT).as_posix(), 'target': target})
    registry = json.loads((OWN / 'registry-entry.json').read_text(encoding='utf-8'))
    expected_fields = {'id', 'theme', 'status', 'question', 'outcome', 'challenge',
                       'remedy', 'evidence', 'retry_when'}
    registry_errors = []
    if set(registry) != expected_fields:
        registry_errors.append('Registry fields differ from the required vocabulary.')
    for target in registry['evidence']:
        if not (ROOT / target).is_file():
            registry_errors.append(f'Missing evidence: {target}')
    result = {
        'status': 'Verified computation' if not any((issues, format_errors, link_errors,
                                                   registry_errors)) else 'Failed',
        'stage': 'post-launch amendment',
        'purpose': 'Artifact integrity after the user-reported Windows error 112 interruption; no new statistical outcome.',
        'prepared_utc': datetime.now(timezone.utc).isoformat(),
        'manifest': manifest_path.name, 'manifest_sha256': sha256(manifest_path),
        'manifest_entries': len(manifest['files']), 'hashed_files': hashed,
        'manifest_self_entry_excluded_from_hash': True,
        'missing_or_changed_manifest_files': issues,
        'files_added_since_manifest': new_paths,
        'formats_checked': dict(formats), 'format_errors': format_errors,
        'local_markdown_links_checked': local_links, 'link_errors': link_errors,
        'registry_evidence_paths_checked': len(registry['evidence']),
        'registry_errors': registry_errors, 'arrays_checked_without_copying': arrays,
        'owned_bytes': sum(p.stat().st_size for p in actual if OWN in p.parents),
        'local_raw_bytes': sum(p.stat().st_size for p in actual if RAW in p.parents),
        'disk_free_bytes_observed': shutil.disk_usage(ROOT).free,
        'interruption_attribution': 'The user reported disk exhaustion; this audit found no damaged recorded artifact and does not attribute the machine-wide error to this package.',
    }
    temporary = RAW / 'tmp' / (destination.name + '.partial')
    temporary.parent.mkdir(parents=True, exist_ok=True)
    try:
        with temporary.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps({key: result[key] for key in (
        'status', 'manifest_entries', 'hashed_files', 'formats_checked',
        'missing_or_changed_manifest_files', 'format_errors', 'link_errors',
        'registry_errors', 'owned_bytes', 'local_raw_bytes')}, indent=2))


if __name__ == '__main__':
    run()
