"""Save stable preview, deterministic rebuild and final verification records."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RECORD = Path(__file__).resolve().parent
ENV = os.environ.copy()
ENV['PYTHONIOENCODING'] = 'utf-8'


def command(args, output):
    result = subprocess.run(args, cwd=ROOT, env=ENV, capture_output=True)
    (RECORD / output).write_bytes(result.stdout)
    if result.stderr:
        (RECORD / (output + '.stderr')).write_bytes(result.stderr)
    if result.returncode:
        raise ValueError(f'{args}: exit {result.returncode}: {result.stderr.decode("utf-8", "replace")}')
    return json.loads(result.stdout)


def hashes(out):
    return {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob('*')) if p.is_file()}


def save(name, value):
    (RECORD / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def run():
    for name in ['build-final.json', 'check-final.json', 'rebuild-final.json', 'determinism-final.json',
                 'page-sizes.json', 'accessibility-final.json', 'filters-final.json',
                 'prose-site-final.json', 'prose-record-final.json', 'CHANGES.json', 'environment.json']:
        if not (RECORD / name).exists():
            (RECORD / name).write_text('{}\n', encoding='utf-8')
    save('environment.json', {'python': sys.version, 'dependencies': {p: importlib.metadata.version(p) for p in ('Markdown', 'Jinja2')}})
    build = command(['python', 'tools/build_site.py', '--worktree', '--out', '_site'], 'build-final.json')
    checked = command(['python', 'tools/build_site.py', '--check', '_site'], 'check-final.json')
    first = hashes(ROOT / '_site')
    with tempfile.TemporaryDirectory(prefix='indus-site-repeat-') as tmp:
        out = Path(tmp) / 'site'
        second_build = command(['python', 'tools/build_site.py', '--worktree', '--out', str(out)], 'rebuild-final.json')
        second = hashes(out)
    difference = sorted(p for p in set(first) | set(second) if first.get(p) != second.get(p))
    save('determinism-final.json', {'ok': not difference, 'files': len(first), 'different_files': difference,
          'hashes': first, 'source_commit': build['source_commit']})
    assert not difference
    files = [{'path': p.relative_to(ROOT / '_site').as_posix(), 'bytes': p.stat().st_size}
             for p in sorted((ROOT / '_site').rglob('*')) if p.is_file()]
    save('page-sizes.json', {'bytes': sum(p['bytes'] for p in files), 'pages': sum(p['path'].endswith('.html') for p in files), 'files': files})
    command(['python', str(RECORD / 'accessibility.py'), '_site'], 'accessibility-final.json')
    command(['node', str(RECORD / 'test_filters.js'), '_site'], 'filters-final.json')
    command(['python', 'tools/review_prose.py', '--path', 'site', '--no-write'], 'prose-site-final.json')
    command(['python', 'tools/review_prose.py', '--path', str(RECORD.relative_to(ROOT)), '--no-write'], 'prose-record-final.json')
    owned = [ROOT / 'tools/build_site.py', ROOT / '.gitignore']
    owned += [p for p in (ROOT / 'site').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    owned += [p for p in RECORD.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('CODEX-PROMPT.md', 'launch.sh')]
    save('CHANGES.json', {'scope': 'Owned source and verification paths; supplied prompt and launcher unchanged',
         'files': [{'path': p.relative_to(ROOT).as_posix(), 'change': 'modified; one added /_site/ line' if p.name == '.gitignore' else 'created',
                    'sha256': hashlib.sha256(p.read_bytes()).hexdigest() if p.name != 'CHANGES.json' else None}
                   for p in sorted(owned)],
         'generated_output': {'directory': '_site', 'tracked': False, 'inventory': 'page-sizes.json', 'pages': checked['pages'], 'bytes': checked['bytes']}})
    print(json.dumps({'ok': True, 'build': build, 'check': checked, 'deterministic_files': len(first)}, indent=2))


if __name__ == '__main__':
    run()
