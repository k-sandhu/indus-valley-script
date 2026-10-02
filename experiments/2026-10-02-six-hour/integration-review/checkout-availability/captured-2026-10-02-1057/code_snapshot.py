"""Inventory core Markdown navigation against the captured intended Git payload."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'experiments/2026-10-02-six-hour/integration-review/checkout-availability'
LATENT = ROOT / 'experiments/2026-10-02-six-hour/latent-forms/git-package/main-results-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def destinations(content):
    """Line-based balanced inline destinations and explicit reference definitions."""
    fenced = False
    for number, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            fenced = not fenced
            continue
        if fenced:
            continue
        definition = re.match(r'^\s*\[([^\]]+)\]:\s*(<[^>]+>|\S+)', line)
        if definition:
            yield number, 'reference-definition', definition.group(2).strip('<>')
        for match in re.finditer(r'!?\[[^\]]*\]\(', line):
            start = match.end()
            level, escaped, angle = 1, False, False
            end = start
            while end < len(line):
                char = line[end]
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == '<':
                    angle = True
                elif char == '>':
                    angle = False
                elif not angle and char == '(':
                    level += 1
                elif not angle and char == ')':
                    level -= 1
                    if level == 0:
                        break
                end += 1
            if level:
                continue
            value = line[start:end].strip()
            if value.startswith('<') and '>' in value:
                value = value[1:value.index('>')]
            else:
                value = re.split(r'\s+[\"\']', value, maxsplit=1)[0]
            yield number, 'image' if match.group(0).startswith('!') else 'inline', value


def classify(doc, destination, selected):
    target = unquote(destination.split('#', 1)[0].split('?', 1)[0])
    if not target:
        return dict(category='local-fragment', target=destination)
    if re.match(r'^[a-zA-Z][\w+.-]*:', target) and not re.match(r'^[A-Za-z]:[/\\]', target):
        return dict(category='network-or-scheme', target=destination)
    path = (doc.parent / target).resolve()
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        return dict(category='outside-repository', target=target, workspace_exists=path.exists())
    children = [p for p in selected if p.startswith(relative.rstrip('/') + '/')]
    exact = relative in selected
    if exact or children:
        category = 'selected'
    elif path.exists():
        category = 'local-only'
    else:
        category = 'missing'
    return dict(category=category, target=relative, workspace_exists=path.exists(), target_kind='directory' if children or path.is_dir() else 'file', selected_descendants=len(children), exact_file_selected=exact)


def credential_chunk_check():
    patterns = {
        'github_token': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})',
        'openai_style_token': rb'sk-(?:proj-)?[A-Za-z0-9_-]{35,}',
        'private_key_header': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    }
    metadata = json.loads((LATENT / 'manifest.json').read_text(encoding='utf-8'))
    previous = b''
    reports = []
    total = 0
    for entry in metadata['chunks']:
        payload = gzip.decompress((LATENT / entry['file']).read_bytes())
        combined = previous + payload
        counts = {}
        for name, pattern in patterns.items():
            counts[name] = sum(match.end() > len(previous) for match in re.finditer(pattern, combined))
        reports.append(dict(chunk=entry['file'], decompressed_bytes=len(payload), known_pattern_counts=counts))
        total += len(payload)
        previous = combined[-512:]
    return dict(scope='Known token formats and private-key headers in authored decompressed result only; no matched values are written', decompressed_bytes=total, boundary_overlap_bytes=512, chunks=reports, total_known_matches=sum(sum(r['known_pattern_counts'].values()) for r in reports))


def main(args):
    output = BASE / args.endpoint
    if output.exists():
        raise RuntimeError('Preserve earlier checkout-review endpoints.')
    output.mkdir(parents=True)
    command = ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z']
    raw = subprocess.run(command, cwd=ROOT, capture_output=True, check=True).stdout
    selected = sorted(set(name.decode('utf-8') for name in raw.split(b'\0') if name))
    # Do not alter the payload, index, rights exclusions or linked targets.
    documents = [ROOT / name for name in ('README.md', 'REPRODUCING.md', 'CONTRIBUTING.md')]
    documents += sorted((ROOT / 'knowledge').rglob('*.md')) + sorted((ROOT / 'papers').rglob('*.md'))
    documents = sorted(set(p for p in documents if p.is_file()))
    links = []
    document_hashes = {}
    document_snapshots = {}
    for doc in documents:
        relative = doc.relative_to(ROOT).as_posix()
        payload = doc.read_bytes()
        document_hashes[relative] = hashlib.sha256(payload).hexdigest()
        snapshot = output / 'documents' / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(payload)
        document_snapshots[relative] = snapshot.relative_to(ROOT).as_posix()
        for line, kind, destination in destinations(payload.decode('utf-8')):
            links.append(dict(document=doc.relative_to(ROOT).as_posix(), line=line, link_kind=kind, written_destination=destination, **classify(doc, destination, selected)))
    local = [r for r in links if r['category'] not in ('network-or-scheme', 'local-fragment')]
    totals = dict(Counter(r['category'] for r in links))
    unique = {category: sorted({r['target'] for r in local if r['category'] == category}) for category in ('selected', 'local-only', 'missing', 'outside-repository')}
    evidence_candidates = [name for name in selected if re.search(r'(?:source|acquisition|provenance|manifest|reconstruct|corpus_report|redistribution)', name, re.I) and Path(name).suffix.lower() in ('.md', '.json', '.py')]
    credentials = credential_chunk_check()
    write(output / 'selected-payload.json', dict(command=command, selected_paths=selected, path_list_sha256=hashlib.sha256('\n'.join(selected).encode('utf-8')).hexdigest()))
    write(output / 'links.json', links)
    write(output / 'source-record-candidates.json', evidence_candidates)
    write(output / 'credential-chunk-check.json', credentials)
    summary = dict(captured_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=digest(BASE / 'PROTOCOL.md'), code_sha256=digest(Path(__file__)), scope='README, REPRODUCING, CONTRIBUTING and Markdown under knowledge/ and papers/; inline/image/reference-definition links outside fences', documents=len(documents), selected_files=len(selected), occurrences_by_category=totals, local_link_occurrences=len(local), unique_local_targets={k: len(v) for k, v in unique.items()}, targets=unique, document_hashes=document_hashes, document_snapshots=document_snapshots, selected_path_list_sha256=hashlib.sha256('\n'.join(selected).encode('utf-8')).hexdigest(), credential_chunk_known_matches=credentials['total_known_matches'])
    write(output / 'summary.json', summary)
    (output / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({key: summary[key] for key in ('captured_utc', 'documents', 'selected_files', 'occurrences_by_category', 'local_link_occurrences', 'unique_local_targets', 'credential_chunk_known_matches')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required=True)
    main(parser.parse_args())
