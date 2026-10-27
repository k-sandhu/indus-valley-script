"""Record final scope, syntax, repository and prose checks without changing shared files."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import ast
import json
import subprocess
import sys

from prepare import ROOT, PACKAGE, RAW, digest


def save(name, value):
    with (PACKAGE / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def run(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    return {'command': args, 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}


if __name__ == '__main__':
    if (PACKAGE / 'knowledge-check-v1.json').exists():
        raise SystemExit('Use a new version for a later check; earlier outputs are preserved.')
    latest = max(PACKAGE.glob('dispatch-v*.json'), key=lambda p: int(p.stem.split('-v')[-1]))
    rows = json.loads(latest.read_text(encoding='utf-8'))
    review = ROOT / 'experiments/2026-10-24-source-review-pass3'
    folders = [ROOT / row['package'] for row in rows] + [review, PACKAGE]
    registries = [ROOT / 'knowledge/registry/attempts' / (row['attempt'] + '.json') for row in rows]
    registries += [ROOT / 'knowledge/registry/attempts' / (name + '-2026-10-24.json')
                   for name in ['SOURCE-REVIEW-PASS3', 'EIGHT-DIRECTIONS-PASS3']]

    syntax_errors = []
    syntax_files = []
    for folder in folders:
        for path in sorted(folder.rglob('*.py')):
            if '__pycache__' in path.parts:
                continue
            syntax_files.append(path.relative_to(ROOT).as_posix())
            try:
                ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
            except (SyntaxError, UnicodeError) as exc:
                syntax_errors.append({'file': syntax_files[-1], 'error': str(exc)})
    save('syntax-check-v1.json', {'status': 'fail' if syntax_errors else 'pass',
                                'files': syntax_files, 'errors': syntax_errors})

    review_errors = []
    for name in ['PROTOCOL.md', 'REPORT.md', 'RETROSPECTIVE.md', 'changed-paths.json',
                 'source-manifest-v1.json', 'validation-v1.json', 'verification-v1.json']:
        if not (review / name).is_file():
            review_errors.append('Missing ' + name)
    review_raw = RAW / review.name
    if not review_raw.is_dir() or review_raw.resolve().drive.lower() != 'd:':
        review_errors.append('Review raw data are not at the required D: directory.')
    for path in review.rglob('*.json'):
        try:
            json.loads(path.read_text(encoding='utf-8-sig'))
        except (ValueError, UnicodeError) as exc:
            review_errors.append(str(path) + ': ' + str(exc))
    review_registry = json.loads(registries[-2].read_text(encoding='utf-8'))
    for path in review_registry['evidence']:
        if not (ROOT / path).is_file():
            review_errors.append('Missing evidence ' + path)
    save('separate-review-audit-v1.json', {'status': 'fail' if review_errors else 'pass',
         'physical_raw': str(review_raw.resolve()), 'errors': review_errors,
         'files': {path.relative_to(ROOT).as_posix(): digest(path)
                   for path in sorted(review.rglob('*'))
                   if path.is_file() and '__pycache__' not in path.parts}})

    base = [sys.executable, '-X', 'utf8']
    prose_args = base + ['tools/review_prose.py', '--no-write']
    for folder in folders:
        prose_args += ['--path', folder.relative_to(ROOT).as_posix()]
    repo_output = PACKAGE / 'repository-check-v1.json'
    commands = [base + ['tools/kb.py', 'check'], prose_args,
                base + ['tools/verify_knowledge_repo.py', '--output',
                        repo_output.relative_to(ROOT).as_posix()]]
    with ThreadPoolExecutor(max_workers=3) as pool:
        knowledge, prose, repository = list(pool.map(run, commands))
    save('knowledge-check-v1.json', knowledge)
    if prose['exit_code'] == 0:
        save('prose-review-v1.json', json.loads(prose['stdout']))
    else:
        save('prose-review-v1.json', prose)
    if not repo_output.exists():
        save('repository-command-failure-v1.json', repository)
        raise SystemExit('Repository verifier did not create its result.')
    baseline = json.loads((PACKAGE / 'baseline-repository-check.json').read_text(encoding='utf-8'))
    final = json.loads(repo_output.read_text(encoding='utf-8'))
    before, after = set(baseline['errors']), set(final['errors'])
    prefixes = [folder.relative_to(ROOT).as_posix() for folder in folders]
    prefixes += [path.relative_to(ROOT).as_posix() for path in registries]
    added = sorted(after - before)
    save('repository-comparison-v1.json', {
        'baseline_errors': len(baseline['errors']), 'final_errors': len(final['errors']),
        'added_errors': added, 'removed_errors': sorted(before - after),
        'added_errors_in_owned_paths': [error for error in added if any(p in error for p in prefixes)],
        'scope': 'Compare error text with the pre-dispatch baseline; shared and concurrent work is not repaired here.'})

    status = run(['git', 'status', '--short'])
    if status['exit_code']:
        raise SystemExit(status['stderr'])
    old_lines = set((PACKAGE / 'baseline-status.txt').read_text(encoding='utf-8').splitlines())
    new_lines = set(status['stdout'].splitlines())
    delta = sorted(new_lines - old_lines)
    save('worktree-review-v1.json', {'new_status_lines': delta,
         'removed_status_lines': sorted(old_lines - new_lines),
         'new_lines_outside_owned_prefixes': [line for line in delta
            if not any(line[3:].startswith(prefix) for prefix in prefixes)],
         'scope': 'Status difference records concurrent work; protected-content hashes are checked separately.'})
    save('changed-paths.json', {
        'tracked_candidates': sorted([p.relative_to(ROOT).as_posix() for p in PACKAGE.rglob('*')
                                      if p.is_file() and '__pycache__' not in p.parts]
                                     + [PACKAGE.relative_to(ROOT).as_posix() + '/changed-paths.json',
                                        registries[-1].relative_to(ROOT).as_posix()]),
        'contribution_manifests': [(folder / 'changed-paths.json').relative_to(ROOT).as_posix()
                                   for folder in folders if folder != PACKAGE],
        'local_only_root': str(RAW / PACKAGE.name)})
    print(json.dumps({'syntax_files': len(syntax_files), 'syntax_errors': syntax_errors,
                     'review_errors': review_errors, 'knowledge': knowledge['stdout'].strip(),
                     'prose_exit_code': prose['exit_code'], 'repository_errors': len(final['errors']),
                     'repository_added': added}, ensure_ascii=False, indent=2))
