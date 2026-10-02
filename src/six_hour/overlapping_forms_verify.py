"""Final input, source-interface, navigation and own-artifact checks."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/overlapping-forms'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    if (BASE / 'verification.json').exists() or (BASE / 'artifact-manifest.json').exists():
        raise RuntimeError('Preserve prior final endpoints.')
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(check=name, passed=bool(passed), detail=detail))

    result = read(BASE / 'main-v1/results.json')
    pilot = read(BASE / 'pilot-v1/results.json')
    audit = read(BASE / 'review-v1/verification.json')
    extra = read(BASE / 'additional-v1/summary.json')
    check('main audit all 9202 checks pass', audit['checks_total'] == audit['checks_passed'] == 9202 and not audit['failures'])
    check('main protocol unchanged', result['protocol_sha256'] == digest(BASE / 'PROTOCOL.md'))
    check('review protocol unchanged', audit['review_protocol_sha256'] == digest(BASE / 'REVIEW_PROTOCOL.md'))
    check('additional protocol unchanged', extra['additional_protocol_sha256'] == digest(BASE / 'ADDITIONAL_PROTOCOL.md'))
    for source in (audit['source_hashes'], extra['input_hashes']):
        for path, sha in source.items():
            check('frozen input ' + path, digest(ROOT / path) == sha)
    check('pilot and main system seeds separate', {r['seed'] for r in pilot['rows']}.isdisjoint({r['seed'] for r in result['rows']}))
    check('pilot completed four conditions', len(pilot['cases']) == 4 and len(pilot['rows']) == 16)
    tree = ast.parse((BASE / 'main-v1/code_snapshot.py').read_text(encoding='utf-8'))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'selector' and node.func.attr == 'select_reference']
    observed = [[ast.unparse(arg) for arg in node.args] for node in calls]
    check('primary selector call exposes only declared reference inputs', observed == [['reference[:size]', 'K', 'seed + 50']], observed)
    for name in ('overlapping_forms.py', 'overlapping_forms_review.py', 'overlapping_forms_additional.py', 'overlapping_forms_verify.py'):
        path = ROOT / 'src/six_hour' / name
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
        check('Python syntax ' + name, True)
    ties = read(BASE / 'review-v1/linear-alternatives.json')
    check('exact equality witness accounting', len(ties) == 384 and sum(bool(t['witnesses']) for t in ties) == 30 and sum(len(t['witnesses']) for t in ties) == 60 and all(w['exact_likelihood_ratio'] == '1' for t in ties for w in t['witnesses']))
    wrong = read(BASE / 'additional-v1/wrong-linear-truth-equalities.json')
    check('every failed linear map scores above truth', len(wrong) == 161 and all(r['returned_minus_truth_bits'] > 1e-7 and not r['exact_truth_likelihood_equal'] for r in wrong))
    check('every failed graph map scores above truth', sum(r['graph_failures'] for r in extra['graph_objective_diagnostics']) == 105 and all(r['graph_failures'] == r['returned_scores_above_truth'] for r in extra['graph_objective_diagnostics']))
    image = (BASE / 'additional-v1/recovery.png').read_bytes()
    width, height = struct.unpack('>II', image[16:24])
    check('rendered plot extent', width == 2160 and height == 864, [width, height])
    editorial = read(BASE / 'editorial-review.json')
    check('seven owned prose files scanned', editorial['files_scanned'] == 7 and not editorial['flags'])
    write(BASE / 'verification.json', {})
    for path in BASE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                check('navigation ' + path.name + ': ' + target, (path.parent / target.split('#')[0]).exists())
    summary = dict(completed_utc=datetime.now(timezone.utc).isoformat(), checks_total=len(checks), checks_passed=sum(c['passed'] for c in checks), checks=checks)
    write(BASE / 'verification.json', summary)
    files = [p for p in BASE.rglob('*') if p.is_file() and p.name != 'artifact-manifest.json']
    files += sorted((ROOT / 'src/six_hour').glob('overlapping_forms*.py'))
    write(BASE / 'artifact-manifest.json', dict(scope='Own generated records, source snapshots, computations, prose and plots; no third-party corpus', files=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(files)]))
    print(json.dumps(dict(checks=summary['checks_total'], passed=summary['checks_passed'], failures=[c for c in checks if not c['passed']], artifacts=len(files))))


if __name__ == '__main__':
    main()
