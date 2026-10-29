"""Prepare an isolated filtered mirror, retaining a private recovery bundle.

This utility never pushes or changes the original checkout's refs or files.
The calling task must separately inspect the mirror and verify a fresh clone.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-11-public-release'

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd).decode('utf-8').strip()

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expected-head', required=True)
    args = parser.parse_args()
    if git('rev-parse', 'HEAD') != args.expected_head or git('branch', '--show-current') != 'main':
        raise SystemExit('Prepared main head changed; reassess before filtering')
    if git('diff', '--cached', '--name-only'):
        raise SystemExit('Index has uncommitted changes')
    # A new directory inside the named ignored backup root is the only target.
    mirror = (RAW / 'clean-mirror.git').resolve()
    mirror.relative_to(RAW.resolve())
    bundle = RAW / 'private-history-pre-filter.bundle'
    record = HERE / 'history-preparation.json'
    runtime = RAW / 'filter-repo-runtime/git_filter_repo.py'
    if any(p.exists() for p in [mirror, bundle, record]):
        raise SystemExit('Preserve existing preparation; do not replace its outputs')
    if not runtime.is_file():
        raise SystemExit('Missing reviewed git-filter-repo runtime')
    before = {ref: git('rev-parse', ref) for ref in ['refs/heads/main', 'refs/heads/research/2026-10-06-program']}
    subprocess.run(['git', 'bundle', 'create', str(bundle), '--all'], cwd=ROOT, check=True)
    print('Private recovery bundle saved', flush=True)
    subprocess.run(['git', 'clone', '--mirror', '--no-local', str(ROOT), str(mirror)], cwd=ROOT, check=True)
    exclusions = json.loads((HERE / 'publication-manifest.json').read_text(encoding='utf-8'))['excluded_from_public_history']
    command = ['python', '-B', str(runtime), '--invert-paths']
    for item in exclusions:
        command += ['--path', item['path']]
    # --no-local above creates a fresh clone; no --force or filesystem deletion.
    subprocess.run(command, cwd=mirror, check=True)
    after = {ref: git('rev-parse', ref, cwd=mirror) for ref in before}
    before_tree = git('rev-parse', args.expected_head + '^{tree}')
    after_tree = git('rev-parse', after['refs/heads/main'] + '^{tree}', cwd=mirror)
    if before_tree != after_tree:
        raise SystemExit('Unexpected public tree change: exclusions should already be absent from index')
    data = dict(status='prepared-for-audit', original_refs=before, filtered_refs=after,
        main_tree=before_tree, tree_unchanged=True, excluded_paths=[x['path'] for x in exclusions],
        recovery_bundle=dict(path=bundle.relative_to(ROOT).as_posix(), bytes=bundle.stat().st_size, sha256=digest(bundle)),
        filter_runtime_sha256=digest(runtime), commit_map_sha256=digest(mirror/'filter-repo/commit-map'),
        scope='Isolated mirror preparation only. Visibility and remote refs have not been changed by this utility.')
    record.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:data[k] for k in ['status','filtered_refs','tree_unchanged']}), flush=True)

if __name__ == '__main__':
    main()
