"""Freeze final navigation, source preservation and lossless-package checks."""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from latent_forms_package import reconstruction

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/latent-forms'
LOCAL_ORIGINAL = BASE / 'main-v1/results.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    if (BASE / 'verification.json').exists() or (BASE / 'artifact-manifest.json').exists():
        raise RuntimeError('Preserve previous final endpoints.')
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(check=name, passed=bool(passed), detail=detail))

    main_result = read(LOCAL_ORIGINAL)
    pilot = read(BASE / 'pilot-v1/results.json')
    review = read(BASE / 'review-v1/verification.json')
    collapsed = read(BASE / 'collapsed-v1/verification.json')
    check('independent scalar review', review['checks_total'] == review['checks_passed'] == 68014 and not review['failures'])
    check('collapsed profile independent checks', collapsed['checks_total'] == collapsed['checks_passed'] == 289)
    check('primary protocol unchanged', main_result['protocol_sha256'] == digest(BASE / 'PROTOCOL.md'))
    check('review protocol unchanged', review['protocol_sha256'] == digest(BASE / 'REVIEW_PROTOCOL.md'))
    check('control protocol unchanged', collapsed['protocol_sha256'] == digest(BASE / 'COLLAPSED_PROTOCOL.md'))
    for payload in (main_result, review, collapsed, pilot):
        for relative, sha in payload['source_hashes'].items():
            check('preserved frozen input ' + relative, digest(ROOT / relative) == sha)
    check('main source unchanged', main_result['code_sha256'] == digest(BASE / 'main-v1/code_snapshot.py') == digest(ROOT / 'src/six_hour/latent_forms.py'))
    check('main scope', len(main_result['mapping_runs']) == 144 and len(main_result['rows']) == 864 and len(main_result['models']) == 288)
    check('supplied component count recorded', main_result['component_count_prior'] == 3)
    check('main and pilot system sets disjoint', {r['seed'] for r in main_result['rows']}.isdisjoint({r['seed'] for r in pilot['rows']}))
    check('all mapping assignment duals audited', review['mapping_assignments_checked'] == sum(len(start['trace']) for run in main_result['mapping_runs'] for start in run['starts']) == 4433)
    counts = Counter(r['algorithm'] for r in main_result['rows'] if r['exact_recovery'])
    expected = dict(latent_mixture=82, reference_selected_three=79, reference_selected=70, form_observed_slot=85)
    check('reported aggregate recovery counts', all(counts[name] == value for name, value in expected.items()), dict(counts))
    check('retained mapping near ties', all(len(run['candidate_ties']) == 1 for run in main_result['mapping_runs']))
    tree = ast.parse((BASE / 'main-v1/code_snapshot.py').read_text(encoding='utf-8'))
    calls = {name: [[ast.unparse(arg) for arg in node.args] for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name] for name in ('fit_reference', 'map_records')}
    check('reference fit call inputs', calls['fit_reference'] == [['reference', 'fit_seed'], ['train', 'fit_seed + 100000 + 100 * fold']], calls['fit_reference'])
    check('mapping call inputs', calls['map_records'] == [["case['training']", 'reference', 'fitted', "base['length_slot']['mapping']", "base['graph_multistart']['mapping']", 'map_seed']], calls['map_records'])
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in ('fit_reference', 'map_records'):
            accesses = [n for n in ast.walk(node) if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and n.slice.value in ('truth', 'forms', 'pools', 'training_labels', 'reference_labels')]
            check('no generated latent fields read in ' + node.name, not accesses)
    for path in sorted((ROOT / 'src/six_hour').glob('latent_forms*.py')):
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
        check('Python syntax ' + path.name, True)
    manifest_path = BASE / 'git-package/main-results-v1/manifest.json'
    package = read(manifest_path)
    rebuilt = reconstruction(manifest_path)
    check('streamed package matches original', rebuilt['reconstructed_sha256'] == digest(LOCAL_ORIGINAL) == package['original_sha256'] and rebuilt['reconstructed_bytes'] == LOCAL_ORIGINAL.stat().st_size, rebuilt)
    check('eight package chunks remain below GitHub limit', len(package['chunks']) == 8 and all(c['compressed_bytes'] < 100_000_000 for c in package['chunks']))
    check('executed packaging version in prose', package['python_version'] == '3.13.5' and 'Python 3.13.5' in (manifest_path.parent / 'RECONSTRUCT.md').read_text(encoding='utf-8'))
    editorial = read(BASE / 'editorial-review.json')
    check('eight owned prose files scanned', editorial['files_scanned'] == 8 and not editorial['flags'])
    # Supply the self-link destination while navigation is checked; replace it once.
    write(BASE / 'verification.json', {})
    for path in sorted(BASE.rglob('*.md')):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                check('navigation ' + path.relative_to(BASE).as_posix() + ': ' + target, (path.parent / target.split('#')[0]).exists())
    eligible = [p for p in BASE.rglob('*') if p.is_file() and p != LOCAL_ORIGINAL and p.name != 'artifact-manifest.json' and '__pycache__' not in p.parts]
    eligible += sorted((ROOT / 'src/six_hour').glob('latent_forms*.py'))
    check('every tracked-eligible own file below GitHub limit', all(p.stat().st_size < 100_000_000 for p in eligible))
    summary = dict(completed_utc=datetime.now(timezone.utc).isoformat(), checks_total=len(checks), checks_passed=sum(c['passed'] for c in checks), checks=checks)
    write(BASE / 'verification.json', summary)
    write(BASE / 'artifact-manifest.json', dict(scope='Own synthetic numerical outputs, source snapshots, prose and deterministic package; original oversized endpoint stays local', local_only_original=dict(path=LOCAL_ORIGINAL.relative_to(ROOT).as_posix(), bytes=LOCAL_ORIGINAL.stat().st_size, sha256=digest(LOCAL_ORIGINAL)), files=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(eligible)]))
    print(json.dumps(dict(checks=summary['checks_total'], passed=summary['checks_passed'], failures=[c for c in checks if not c['passed']], artifacts=len(eligible))))


if __name__ == '__main__':
    main()
