"""Reviewer: compare each rerun output with the package's saved output (hash and deep equality).
Run from the repository root. Writes review/rerun-comparison.json (aggregates only)."""
import hashlib, json
from pathlib import Path
PKG = Path('experiments/2026-10-06-sign-context-and-seals')
REV = PKG / 'review'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
pairs = []
for name in ['site-frequencies', 'sign-analysis', 'motif-concentration', 'motif-association', 'dimensions']:
    pairs.append(('primary', PKG / 'run-2026-10-07-01' / f'{name}.json', REV / 'rerun-primary' / f'{name}.json'))
pairs.append(('supplement', PKG / 'supplement-2026-10-07-01' / 'dimension-coverage.json', REV / 'rerun-supplement' / 'dimension-coverage.json'))
for name in ['richness', 'concentration', 'terminal740', 'period-stability', 'external-motifs']:
    pairs.append(('post-launch', PKG / 'post-launch-2026-10-07-02' / f'{name}.json', REV / 'rerun-postlaunch' / f'{name}.json'))
out = []
for stage, a, b in pairs:
    ja, jb = json.loads(a.read_text(encoding='utf-8')), json.loads(b.read_text(encoding='utf-8'))
    identical_bytes = sha(a) == sha(b)
    if not identical_bytes and name == 'external-motifs':
        pass
    out.append({'stage': stage, 'file': a.name, 'byte_identical': identical_bytes, 'json_equal': ja == jb,
                'sha256_original': sha(a), 'sha256_rerun': sha(b)})
# exploratory: results.json differs in runtime only
ea = json.loads((PKG / 'exploratory-2026-10-07-01/results.json').read_text(encoding='utf-8'))
eb = json.loads((REV / 'rerun-exploratory/results.json').read_text(encoding='utf-8'))
ea.pop('runtime_seconds'); eb.pop('runtime_seconds')
out.append({'stage': 'exploratory', 'file': 'results.json', 'byte_identical': None,
            'json_equal_ignoring_runtime_seconds': ea == eb})
# external-motifs with local path normalization
a = json.loads((PKG / 'post-launch-2026-10-07-02/external-motifs.json').read_text(encoding='utf-8'))
b = json.loads((REV / 'rerun-postlaunch/external-motifs.json').read_text(encoding='utf-8'))
paths_a, paths_b = a.pop('external_object_list_local'), b.pop('external_object_list_local')
out.append({'stage': 'post-launch', 'file': 'external-motifs.json (path field removed)', 'json_equal': a == b,
            'path_original': paths_a, 'path_rerun': paths_b})
(REV / 'rerun-comparison.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
for r in out:
    print({k: v for k, v in r.items() if k not in ('sha256_original', 'sha256_rerun', 'path_original', 'path_rerun')})
