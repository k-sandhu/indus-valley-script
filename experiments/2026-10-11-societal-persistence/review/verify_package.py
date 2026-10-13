"""Verify completed reviewer inputs, outputs, guards and rights handling."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f'Refusing existing output: {args.output}')
    checks = []

    def check(label, value):
        checks.append({'check': label, 'passed': bool(value)})
        if not value:
            raise AssertionError(label)

    model = read('model-checks-v1/checks.json')
    counter = read('counterexamples-v1/counterexamples.json')
    source = read('source-checks-v3/checks.json')
    check('all 5218 model checks pass', len(model['checks']) == 5218 and all(t['passed'] for t in model['checks']))
    check('all six counterexample assertions pass', len(counter['assertions']) == 6 and all(counter['assertions'].values()))
    check('all 90 source checks pass', len(source['checks']) == 90 and all(t['passed'] for t in source['checks']))
    check('root result pin unchanged', model['root_results_sha256'] == sha(HERE.parent / 'coordinator/run-v1/results.json'))
    check('checker code unchanged', model['checker_sha256'] == sha(HERE / 'check_model.py'))
    check('checker protocol unchanged', model['review_protocol_sha256'] == sha(HERE / 'CHECKER-PROTOCOL.md'))
    for name, value in counter['input_hashes'].items():
        check('counterexample input ' + name, value == sha(HERE / name))
    for name, key in [('sources.json', 'source_ledger_sha256'), ('claims.json', 'claims_sha256'),
                      ('falsifiers.json', 'falsifiers_sha256'), ('source_audit_v3.py', 'code_sha256')]:
        check('source-audit input ' + name, source[key] == sha(HERE / name))
    summary = []
    for variant in model['sensitivities']:
        rows = variant['world_modes']
        summary.append({
            'variant': variant['variant'],
            'changed_world_modes': sum(bool(r['removed_from_baseline'] or r['added_to_baseline']) for r in rows),
            'removed_state_memberships': sum(len(r['removed_from_baseline']) for r in rows),
            'added_state_memberships': sum(len(r['added_to_baseline']) for r in rows),
        })
    check('severity variant 10 modes and 118 removed', (summary[0]['changed_world_modes'], summary[0]['removed_state_memberships'], summary[0]['added_state_memberships']) == (10, 118, 0))
    check('eligibility variant 14 modes and 56 removed', (summary[1]['changed_world_modes'], summary[1]['removed_state_memberships'], summary[1]['added_state_memberships']) == (14, 56, 0))
    check('severity variant nonzero supports have empty robust kernels', all(r['infinite_count'] == 0 for r in model['sensitivities'][0]['world_modes'] if r['mode'] == 'robust' and r['shock_support'] != 'none'))
    check('severity variant possible kernels unchanged', all(not r['removed_from_baseline'] and not r['added_to_baseline'] for r in model['sensitivities'][0]['world_modes'] if r['mode'] == 'possible'))
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
        check('AST parses ' + path.name, True)
    for claim in read('claims.json')['claims']:
        for output in claim['outputs']:
            name, *fragment = output.split('#', 1)
            data = read(name)
            if fragment:
                for part in fragment[0].strip('/').split('/'):
                    part = part.replace('~1', '/').replace('~0', '~')
                    data = data[int(part)] if isinstance(data, list) else data[part]
            check('claim output pointer ' + claim['id'] + ' ' + output, data is not None)
    guards = []
    for code, folder, name in [('counterexamples.py', 'counterexamples-v1', 'counterexamples.json'),
                               ('check_model.py', 'model-checks-v1', 'checks.json'),
                               ('source_audit_v3.py', 'source-checks-v3', 'checks.json')]:
        path = HERE / folder / name
        old = sha(path)
        proc = subprocess.run([sys.executable, str(HERE / code), '--output', str(HERE / folder)], capture_output=True, text=True, encoding='utf-8')
        okay = proc.returncode != 0 and 'Refusing existing output' in proc.stderr and sha(path) == old
        check('overwrite refusal ' + code, okay)
        guards.append({'code': code, 'returncode': proc.returncode, 'refused_existing_output': okay, 'endpoint_sha256_before_after': old})
    check('prose scan no stock flags', read('prose-review-v2.json')['flags'] == [])
    ledger = read('sources.json')
    paths = [w['path'] for w in ledger['witnesses']] + [d['path'] for d in ledger['derivatives']]
    # Explicit path arguments avoid Windows text-mode CRLF altering stdin names.
    proc = subprocess.run(['git', 'check-ignore', '--'] + paths, text=True, capture_output=True, encoding='utf-8', cwd=ROOT)
    check('all raw witnesses and derivatives ignored', set(paths) <= set(proc.stdout.splitlines()))
    args.output.mkdir(parents=True)
    result = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'passed',
        'checks_passed': len(checks),
        'checks': checks,
        'independent_model_checks': 5218,
        'counterexample_assertions': 6,
        'source_checks': 90,
        'sensitivity_summary': summary,
        'overwrite_guard_checks': guards,
        'root_model_result_sha256': model['root_results_sha256'],
        'code_sha256': sha(Path(__file__)),
        'own_input_sha256': {name: sha(HERE / name) for name in ['model-checks-v1/checks.json', 'counterexamples-v1/counterexamples.json', 'source-checks-v3/checks.json', 'prose-review-v2.json']},
        'rights_handling': 'All 14 raw witnesses/derivatives checked against exact ignore paths; own code/prose/metadata/aggregate outputs remain separate.',
        'preserved_attempts': ['source-checks-v1/failure.json', 'source-checks-v2/failure.json', 'integrity-checks-v1/failure.json'],
    }
    (args.output / 'checks.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checks_passed': len(checks)}))


if __name__ == '__main__':
    main()
