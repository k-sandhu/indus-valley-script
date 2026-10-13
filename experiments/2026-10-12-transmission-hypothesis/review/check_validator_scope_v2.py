"""Exercise a declaration gate with an explicitly unsupported semantic claim."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    out = HERE / 'validator-scope-v2'
    if out.exists():
        raise SystemExit('Refusing existing output directory')
    out.mkdir()
    source_name = (ROOT / 'coordinator/observations-v2.json').relative_to(REPO).as_posix()
    references = [{'file': source_name, 'ids': ['C-O01']}]
    rivals = {
        f'R{i}': {'prediction': 'An alternative route could produce the same endpoint.',
                  'relation': 'compatible_only', 'observations': [],
                  'missing_discriminator': 'No feature-specific route evidence is supplied.'}
        for i in range(1, 6)
    }
    fixture = {'scope': 'Deliberately invalid semantic fixture, not a historical comparison',
               'comparisons': [{
                   'id': 'ADVERSARIAL-DECLARATION', 'family': 'invented practice',
                   'feature': 'invented recipe', 'proposition': 'A population observation teaches a recipe',
                   'chronology': 'Undated invented teaching claim',
                   'dependencies': 'One actual scientific observation is intentionally misused',
                   'observations': references, 'decision': 'supported_endpoint',
                   'conclusion': 'Unsupported by its cited population observation',
                   'rivals': rivals,
                   'transitions': [{'from': 'invented donor', 'to': 'invented teaching recipient',
                                    'feature': 'invented recipe', 'type': 'learning_relation',
                                    'state': 'observed', 'feature_specific': True,
                                    'observations': references}],
                   'rival_discrimination_basis': 'This deliberately inadequate string excludes no rival.',
                   'claims_traced_local_literary_descent': True,
               }]}
    input_path = out / 'fixture.json'
    input_path.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
    code = ROOT / 'coordinator/audit_comparisons.py'
    before = sha(code)
    run = subprocess.run([sys.executable, str(code), '--input', str(input_path),
                          '--output', str(out / 'validator-output')], capture_output=True,
                         text=True, encoding='utf-8')
    result_path = out / 'validator-output/audit.json'
    result = json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else None
    interpretation = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Negative semantic fixture applied to declaration/reference validator; not historical evidence',
        'protocol_sha256': sha(HERE / 'VALIDATOR-CONTROL-PROTOCOL.md'),
        'reviewer_code_sha256': sha(Path(__file__)),
        'output_schema_amendment_sha256': sha(HERE / 'AMENDMENT-validator-output.md'),
        'coordinator_code_sha256_before': before,
        'coordinator_code_sha256_after': sha(code),
        'fixture_sha256': sha(input_path), 'returncode': run.returncode,
        'stdout': run.stdout, 'stderr': run.stderr,
        'validator_result_sha256': sha(result_path) if result_path.exists() else None,
        'expected_limitation_observed': bool(result and run.returncode == 0 and
                                             result['comparisons'][0]['declared_local_descent_record_completeness']),
        'interpretation': 'A pass confirms the documented semantic limit: cited ID and declared edge tags do not establish teaching or rival exclusion. Source support must be reviewed manually.',
    }
    (out / 'interpretation.json').write_text(json.dumps(interpretation, indent=2) + '\n', encoding='utf-8')
    if interpretation['coordinator_code_sha256_before'] != interpretation['coordinator_code_sha256_after']:
        raise RuntimeError('Coordinator code changed during control')
    if not interpretation['expected_limitation_observed']:
        raise RuntimeError('Declared expected validator behavior did not occur; preserve this endpoint')
    print(json.dumps({'expected_limitation_observed': True, 'checks_passed_by_validator': result['checks_passed'],
                      'result': str(out / 'interpretation.json')}))
