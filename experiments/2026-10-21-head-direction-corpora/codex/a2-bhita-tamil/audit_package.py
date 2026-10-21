"""Write A2 source inventory, source-text leak audit and complete file inventory.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a2-bhita-tamil/audit_package.py --root .
Reads only A2 source records and local transcriptions. Leak patterns stay local;
tracked reports contain field names, identifiers, counts and paths.
"""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

PACKAGE = Path('experiments/2026-10-21-head-direction-corpora')
RAW = Path('data/raw/2026-10-21-head-direction-corpora')
SOURCES = ['asi-ar-1909-10', 'asi-ar-1911-12', 'mahadevan-2003']
EXISTING = {'CODEX-PROMPT.md', 'TASK.md', 'launch-codex.sh'}


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def owned_tracked(root):
    result = [p for p in (root / PACKAGE / 'codex/a2-bhita-tamil').iterdir() if p.is_file() and p.name not in EXISTING]
    for source in SOURCES:
        result.extend((root / PACKAGE / 'acquisition').glob(source + '-*.json'))
    return sorted(result)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    args = ap.parse_args()
    root = args.root.resolve()
    out = root / PACKAGE / 'codex/a2-bhita-tamil'
    scratch = root / RAW / 'codex-a2'
    counts = json.loads((out / 'transcription-counts.json').read_text(encoding='utf-8'))
    read_ranges = {
        'asi-ar-1909-10': ('40–42; navigation 31, 36–38', '1, 60, 69–71, 73–75'),
        'asi-ar-1911-12': ('29–63; contents; plates XI–XXI', 'primary: 1, 8, 70–123; alternate: 1, 7, 60, 70'),
        'mahadevan-2003': ('31, 46, 49–67, 154, 200, 208 (figure crop), 235–237', '1, 75, 90, 93–111, 198, 244, 252 (figure crop), 279–281'),
    }
    text = ['# A2 source inventory', '', 'We acquired six pinned source files and four item metadata witnesses on 21 October 2026 UTC. Every pinned byte count and SHA-1 matches. Acquisition JSON records retain URLs, retrieval times, SHA-1, SHA-256 and rights notes. Each file occupies a separate local directory. Page numbers below are one-based.', '']
    acquisitions = []
    for source in SOURCES:
        text += ['## ' + source, '', '| Item | File | Bytes | SHA-256 | PDF pages |', '|---|---|---:|---|---:|']
        for path in sorted((root / PACKAGE / 'acquisition').glob(source + '-*.json')):
            rec = json.loads(path.read_text(encoding='utf-8'))
            acquisitions.append(path)
            parts = urlsplit(rec['url']).path.split('/')
            item = unquote(parts[2])
            filename = Path(rec['local_path']).name
            text += [f"| `{item}` | `{filename}` | {rec['bytes']} | `{rec['sha256']}` | {rec.get('pdf_pages', 'not applicable')} |"]
        text += ['', 'Rights status: `rights-unverified`. ' + rec['rights_note'] + '.', '', 'Printed pages read: ' + read_ranges[source][0] + '. PDF pages inspected: ' + read_ranges[source][1] + '.', '']
    text += ['The 1909–10 summary supplies no catalogue row or seal legend. The 1911–12 primary scan supplies entries 1–120 and a 25-row findspot index. Tables 1.6, 1.7 and 1.8 supply 13, five and 14 rows. Their printed pages are 62–63, 64 and 65–67; PDF pages are 106–107, 108 and 109–111. Figure locators include 1.23–1.24, 4.4, 5.9 and 5.14. Section 6.13 is on printed p. 236, PDF p. 280. The local notes record exceptions and the source differences.', '', 'Local render manifests list every image and its 300 dpi setting. PDF p. 252 was read through crops. A crop extended into the following symbol panel; no sign identification, legend reading or comparison was made there. The local notes preserve that exposure.', '']
    (out / 'SOURCES.md').write_text('\n'.join(text), encoding='utf-8')
    for source in SOURCES[1:]:
        notes_path = root / RAW / 'transcriptions' / (source + '.notes.md')
        rows = [json.loads(s) for s in (root / RAW / 'transcriptions' / (source + '.jsonl')).read_text(encoding='utf-8').splitlines()]
        marker = '\n## Field uncertainties\n'
        notes = notes_path.read_text(encoding='utf-8').split(marker)[0]
        paragraphs = []
        for row in rows:
            for item in row['uncertain_fields']:
                locator = ('Table ' + row['table'] + ', row ' + str(row['entry'])) if row.get('table') else ('Entry ' + str(row['entry']))
                paragraphs.append(locator + ', `' + item['field'] + '`: ' + item['reason'])
        notes_path.write_text(notes.rstrip() + marker + '\n' + '\n\n'.join(paragraphs) + '\n', encoding='utf-8')
    local_rows = [json.loads(s) for s in (root / RAW / 'transcriptions/mahadevan-2003.jsonl').read_text(encoding='utf-8').splitlines()]
    fields = ['legend_as_printed', 'literal_rendering', 'table_legend_as_printed', 'translation_as_printed', 'device', 'object_text']
    patterns = set()
    for row in local_rows:
        for field in fields:
            value = row.get(field)
            if not value:
                continue
            for line in value.splitlines():
                line = line.strip()
                if len(line) >= 5:
                    patterns.add(line)
                words = line.split()
                patterns.update(' '.join(words[i:i + 6]) for i in range(max(0, len(words) - 5)))
        for note in row.get('orthography_notes', []):
            for field in ['literal_rendering', 'reading', 'translation']:
                if len(note.get(field, '')) >= 5:
                    patterns.add(note[field])
    pattern_file = scratch / 'mahadevan-leak-patterns.txt'
    pattern_file.write_text('\n'.join(sorted(patterns)) + '\n', encoding='utf-8')
    targets = owned_tracked(root)
    # Reports already present are included when this script is rerun at the end.
    command = ['rg', '--fixed-strings', '--ignore-case', '--count-matches', '--file', str(pattern_file)] + [str(p) for p in targets]
    check = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8')
    if check.returncode not in (0, 1):
        raise RuntimeError(check.stderr)
    matches = []
    for line in check.stdout.splitlines():
        path, n = line.rsplit(':', 1)
        matches.append({'path': Path(path).relative_to(root).as_posix(), 'matching_lines': int(n)})
    dump(out / 'leak-check.json', {'tool': 'rg --fixed-strings --ignore-case --count-matches --file LOCAL_PATTERN_FILE OWNED_TRACKED_FILES',
        'patterns': len(patterns), 'pattern_fields': fields, 'tracked_files_checked': len(targets),
        'matches': matches, 'passed': check.returncode == 1,
        'scope': 'All A2-created tracked files and acquisition records; source literals and six-word sequences remain local.'})
    status = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', 'status', '--porcelain', '--untracked-files=all'], cwd=root, check=True, capture_output=True, text=True, encoding='utf-8').stdout
    (scratch / 'git-status-end.txt').write_text(status, encoding='utf-8')
    baseline = (scratch / 'git-status-start.txt').read_text(encoding='utf-8')
    own_paths = {p.relative_to(root).as_posix() for p in owned_tracked(root)}
    before = set(baseline.splitlines())
    after = set(status.splitlines())
    other_delta = [line for line in sorted(after - before) if line[3:].strip('"') not in own_paths]
    dump(out / 'status-check.json', {'a2_created_tracked_paths': sorted(own_paths),
        'repository_status_exclusively_a2': not any(line[3:].strip('"') not in own_paths for line in after),
        'preexisting_status_lines': len(before), 'current_status_lines': len(after),
        'other_new_or_changed_status_lines': len(other_delta),
        'note': 'Other sessions have pre-existing and concurrent changes. Local start/end snapshots retain the full read-only status. A2 scripts write only the assigned paths.'})
    files = owned_tracked(root)
    for source in SOURCES:
        stem = source.replace('asi-ar-', 'asi-')
        for folder in (root / RAW).glob('src-' + stem + '-*'):
            files.extend(p for p in folder.rglob('*') if p.is_file())
        folder = root / RAW / ('pages-' + stem)
        files.extend(p for p in folder.rglob('*') if p.is_file())
    for source in SOURCES[1:]:
        files.extend((root / RAW / 'transcriptions').glob(source + '.*'))
    files.extend(p for p in scratch.rglob('*') if p.is_file() and p.name not in {'codex.log', 'launches.txt'})
    inventory = out / 'created-paths.json'
    if inventory not in files:
        files.append(inventory)
    raw_paths = sorted({p.relative_to(root).as_posix() for p in files if p.is_relative_to(root / RAW)})
    ignored = subprocess.run(['git', '-c', f'safe.directory={root.as_posix()}', 'check-ignore', '-z', '--stdin'],
                             cwd=root, input=('\0'.join(raw_paths) + '\0').encode('utf-8'), capture_output=True, check=True)
    ignored_paths = set(ignored.stdout.decode('utf-8').strip('\0').split('\0'))
    missing = [p for p in raw_paths if p not in ignored_paths]
    dump(out / 'local-only-check.json', {'raw_files_checked': len(raw_paths), 'raw_files_not_ignored': missing, 'passed': not missing,
        'method': 'git check-ignore -z --stdin with binary NUL-separated paths'})
    dump(inventory, {'paths': sorted({p.relative_to(root).as_posix() for p in files}),
                     'note': 'Complete created file list. Supplied launch/prompt files and launcher logs are excluded.'})
    print(json.dumps({'acquisitions': len(acquisitions), 'leak_patterns': len(patterns), 'leak_matches': matches, 'created_files': len(set(files)), 'concurrent_status_delta': len(other_delta)}))


if __name__ == '__main__':
    main()
