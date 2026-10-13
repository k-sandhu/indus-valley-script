"""Isolated publication and public-boundary checks; no real branch updates."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RECORD = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'tools/build_site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def digest_tree(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file()}


def tree(entries, root):
    nodes = {}
    for path, oid in entries.items():
        node = nodes
        parts = path.split('/')
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = oid
    def write(node):
        rows = []
        for name, value in sorted(node.items(), key=lambda x: x[0] + ('/' if isinstance(x[1], dict) else '')):
            mode, kind, oid = ('040000', 'tree', write(value)) if isinstance(value, dict) else ('100644', 'blob', value)
            rows.append(f'{mode} {kind} {oid}\t{name}'.encode() + b'\0')
        return site.git('mktree', '-z', root=root, payload=b''.join(rows)).decode().strip()
    return write(nodes)


def run():
    real_before = {name: site.git(*args).decode().strip() for name, args in {
        'head': ('rev-parse', 'HEAD'), 'branch': ('symbolic-ref', 'HEAD'),
        'index': ('ls-files', '--stage'), 'refs': ('show-ref',)}.items()}
    source = site.GitSource(True)
    result = {}
    with tempfile.TemporaryDirectory(prefix='indus-site-test-') as tmp:
        tmp = Path(tmp)
        clone = tmp / 'clone'
        # A local bundle avoids upload-pack's separate ownership check under the
        # sandbox account. It reads the repository and writes only in this tempdir.
        bundle = tmp / 'repository.bundle'
        site.git('bundle', 'create', bundle.as_posix(), '--all')
        cloned = subprocess.run(['git', 'clone', '--no-checkout', bundle.as_posix(), clone.as_posix()], capture_output=True)
        if cloned.returncode:
            raise ValueError(cloned.stderr.decode('utf-8', 'replace'))
        entries = site.tree_inventory(source.commit, clone)
        changed = {p.decode() for p in site.git('diff', '--name-only', '-z', 'HEAD').split(b'\0') if p}
        changed = sorted((changed | (source.files - set(entries))) & source.files)
        # Batch hashing writes objects in the clone, reading only gated public paths.
        absolute = '\n'.join((ROOT / p).as_posix() for p in changed) + '\n'
        oids = site.git('hash-object', '-w', '--no-filters', '--stdin-paths', root=clone,
                        payload=absolute.encode('utf-8')).decode().splitlines()
        assert len(oids) == len(changed)
        entries.update(zip(changed, oids))
        fixtures = {
            'data/private.json': b'PRIVATE_FIXTURE_BYTES',
            'private-source/blocked.md': b'OMITTED_FIXTURE_BYTES',
            'data/MANIFEST.json': site.dumps({'sources': [{'id': 'fixture', 'title': 'Synthetic metadata',
                'status': 'held', 'location': 'tracked', 'rights': {'status': 'own-work', 'licence': None}, 'size': {'rows': 1}}]}).encode(),
            'llms.txt': b'# Fixture\n\n[README](README.md)\n[Data](knowledge/DATA.md)\n',
            'README.md': (source.text('README.md') + '\n[Excluded data](data/private.json)\n[Omitted source](private-source/blocked.md)\n').encode(),
            site.OMISSIONS: site.dumps({'targets': source.omissions + ['private-source/blocked.md']}).encode(),
        }
        for path, payload in fixtures.items():
            entries[path] = site.git('hash-object', '-w', '--stdin', root=clone, payload=payload).decode().strip()
        snapshot_tree = tree(entries, clone)
        env = os.environ.copy()
        env.update(GIT_AUTHOR_NAME='Website fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
                   GIT_COMMITTER_NAME='Website fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid',
                   GIT_AUTHOR_DATE=source.date, GIT_COMMITTER_DATE=source.date)
        snapshot = site.git('commit-tree', snapshot_tree, '-p', source.commit, root=clone,
                            payload=b'Isolated site test snapshot\n', env=env).decode().strip()
        site.git('update-ref', 'HEAD', snapshot, root=clone)
        # Put only the executable in the clone's worktree. Its templates and kb
        # dependency must be read from the committed snapshot, not these files.
        (clone / 'tools').mkdir()
        (clone / 'tools/build_site.py').write_bytes(source.bytes('tools/build_site.py'))
        (clone / 'README.md').write_text('UNCOMMITTED_FIXTURE_BYTES', encoding='utf-8')
        (clone / 'untracked.md').write_text('UNTRACKED_FIXTURE_BYTES', encoding='utf-8')
        committed_source = site.GitSource(root=clone)
        first, second = tmp / 'first', tmp / 'second'
        result['head_build'] = site.build_to(committed_source, first)
        result['second_head_build'] = site.build_to(site.GitSource(root=clone), second)
        result['byte_identical'] = digest_tree(first) == digest_tree(second)
        assert result['head_build']['ok'] and result['second_head_build']['ok'] and result['byte_identical']
        assert not (first / 'data').exists() and not (first / 'private-source').exists()
        assert 'Synthetic metadata' in (first / 'data.html').read_text(encoding='utf-8')
        assert site.SITE + 'index.html' in (first / 'llms.txt').read_text(encoding='utf-8')
        prohibited = [b'PRIVATE_FIXTURE_BYTES', b'OMITTED_FIXTURE_BYTES', b'UNCOMMITTED_FIXTURE_BYTES', b'UNTRACKED_FIXTURE_BYTES']
        assert all(not any(marker in p.read_bytes() for marker in prohibited) for p in first.rglob('*') if p.is_file())
        result['boundary_fixtures'] = 'excluded data and omissions, tracked metadata, llms rewrite, HEAD isolation passed'
        def state():
            return {key: site.git(*args, root=clone).decode() for key, args in {
                'head': ('rev-parse', 'HEAD'), 'branch': ('symbolic-ref', 'HEAD'),
                'index': ('ls-files', '--stage'), 'status': ('status', '--porcelain=v1', '-uall')}.items()}
        before = state()
        command = ['python', str(clone / 'tools/build_site.py'), '--publish']
        cli = subprocess.run(command, cwd=clone, capture_output=True, text=True)
        result['publish_exit_code'] = cli.returncode
        result['publish'] = json.loads(cli.stdout)
        assert cli.returncode == 0 and result['publish']['ok']
        assert state() == before
        first_commit = result['publish']['published_local_commit']
        publication = site.tree_inventory(first_commit, clone)
        assert set(publication) == set(digest_tree(first))
        published_tree = site.git('rev-parse', f'{first_commit}^{{tree}}', root=clone).decode().strip()
        cli2 = subprocess.run(command, cwd=clone, capture_output=True, text=True)
        result['second_publish_exit_code'] = cli2.returncode
        result['second_publish'] = json.loads(cli2.stdout)
        assert cli2.returncode == 0 and state() == before
        second_commit = result['second_publish']['published_local_commit']
        assert site.git('rev-parse', f'{second_commit}^', root=clone).decode().strip() == first_commit
        assert site.git('rev-parse', f'{second_commit}^{{tree}}', root=clone).decode().strip() == published_tree
        result['source_branch_index_worktree_preserved'] = True
        result['publication_parent_and_tree_verified'] = True
        # Mutate only the temporary output. Each failure must be detected.
        home = first / 'index.html'
        original = home.read_text(encoding='utf-8')
        failures = {}
        for name, injected in {
            'missing_internal_link': '<a href="missing.html">Missing</a>',
            'external_stylesheet': '<link rel="stylesheet" href="https://example.invalid/style.css">',
            'external_script': '<script src="https://example.invalid/code.js"></script>',
            'external_inline_css': '<p style="background:url(https://example.invalid/x.png)">CSS</p>',
            'external_script_fetch': '<script>fetch("https://example.invalid/data")</script>',
            'unpinned_github_link': f'<a href="{site.REPO}/blob/main/README.md">Source</a>',
            'missing_github_path': f'<a href="{site.REPO}/blob/{snapshot}/absent.md">Source</a>',
            'image_alt': '<img src="assets/site.css">',
        }.items():
            home.write_text(original + injected, encoding='utf-8')
            checked = site.check(first, clone)
            assert not checked['ok'], name
            failures[name] = checked['errors']
        home.write_text(original, encoding='utf-8')
        (first / 'data').mkdir()
        (first / 'data/private.json').write_text('fixture', encoding='utf-8')
        checked = site.check(first, clone)
        assert not checked['ok']
        failures['excluded_output'] = checked['errors']
        result['negative_checks'] = failures
        result['snapshot_commit'] = snapshot
    after = {name: site.git(*args).decode().strip() for name, args in {
        'head': ('rev-parse', 'HEAD'), 'branch': ('symbolic-ref', 'HEAD'),
        'index': ('ls-files', '--stage'), 'refs': ('show-ref',)}.items()}
    assert after == real_before
    result['real_repository_refs_and_index_preserved'] = True
    result['ok'] = True
    return result


if __name__ == '__main__':
    print(site.dumps(run()), end='')
