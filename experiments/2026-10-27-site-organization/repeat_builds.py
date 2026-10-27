"""Build twice from one cached Git-selected worktree snapshot and compare bytes."""
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import build_site as site

source = site.GitSource(True)
generator = source.bytes('tools/build_site.py')
outputs = [ROOT / '_site/site-preview-repeat-a', ROOT / '_site/site-preview-repeat-b']
results = [site.build_to(source, out) for out in outputs]


def hashes(out):
    return {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob('*')) if p.is_file()}


left, right = map(hashes, outputs)
missing = sorted(set(left) - set(right))
added = sorted(set(right) - set(left))
changed = sorted(p for p in set(left) & set(right) if left[p] != right[p])
snapshot = {'source_commit': source.commit, 'mode': 'worktree', 'public_files': sorted(source.files),
            'inputs': dict(sorted(source.inputs.items()))}
(PACKAGE / 'snapshot-inputs.json').write_bytes(site.dumps(snapshot).encode())
result = {'ok': all(r['ok'] for r in results) and not (missing or added or changed),
          'snapshot': 'One Git-selected inventory and the exact bytes cached by the first build; no live file rereads in the second build.',
          'source_commit': source.commit, 'generator_sha256': hashlib.sha256(generator).hexdigest(),
          'snapshot_sha256': hashlib.sha256(site.dumps(snapshot).encode()).hexdigest(),
          'python': platform.python_version(), 'Markdown': site.markdown.__version__, 'Jinja2': site.jinja2.__version__,
          'outputs': [p.relative_to(ROOT).as_posix() for p in outputs], 'files_per_build': [len(left), len(right)],
          'tree_sha256': hashlib.sha256(site.dumps(left).encode()).hexdigest(),
          'missing': missing, 'added': added, 'changed': changed, 'checks': results}
(PACKAGE / 'determinism.json').write_bytes(site.dumps(result).encode())
print(site.dumps({k: result[k] for k in ('ok', 'files_per_build', 'missing', 'added', 'changed', 'tree_sha256')}))
raise SystemExit(0 if result['ok'] else 1)
