"""Reconstruct source joins and declared completeness without coordinator imports."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[1]
EXPECTED_DECISIONS = {'TC01': 'unresolved_join', 'TC02': 'supported_intermediate',
                      'TC03': 'unresolved_join', 'TC04': 'rival_comparison',
                      'TC05': 'rival_comparison', 'TC06': 'supported_endpoint',
                      'TC07': 'supported_endpoint'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE / 'comparison-checks-v1')
    out = parser.parse_args().out.resolve()
    if not out.is_relative_to(HERE):
        raise SystemExit('Output must be within the owned review directory')
    if out.exists():
        raise SystemExit('Refusing existing output directory')
    out.mkdir()
    checks, ledgers = [], {}

    def check(name, passed):
        checks.append({'check': name, 'passed': bool(passed)})
        if not passed:
            raise AssertionError(name)

    def refs(records, label):
        count = 0
        for ref in records:
            name = ref['file']
            if name not in ledgers:
                doc = read(REPO / name)
                rows = doc['observations'] if isinstance(doc, dict) else doc
                ids = [row.get('observation_id', row.get('id')) for row in rows]
                check(f'distinct actual IDs in {name}', None not in ids and len(ids) == len(set(ids)))
                ledgers[name] = dict(zip(ids, rows))
            for oid in ref['ids']:
                check(f'{label} actual observation {oid}', oid in ledgers[name])
                count += 1
        return count

    try:
        input_path = BASE / 'coordinator/comparisons-v1.json'
        output_path = BASE / 'coordinator/run-v1/audit.json'
        comparisons = read(input_path)['comparisons']
        root = read(output_path)
        output_by_id = {r['id']: r for r in root['comparisons']}
        check('seven selected comparison IDs', {r['id'] for r in comparisons} == set(EXPECTED_DECISIONS))
        check('output comparison IDs equal inputs', set(output_by_id) == set(EXPECTED_DECISIONS))
        rival_count, joined_count = 0, 0
        reconstructed = []
        for row in comparisons:
            cid = row['id']
            joined_count += refs(row['observations'], cid)
            check(f'{cid} declared decision', row['decision'] == EXPECTED_DECISIONS[cid])
            check(f'{cid} no asserted traced literary descent', row['claims_traced_local_literary_descent'] is False)
            check(f'{cid} all five rivals', set(row['rivals']) == {f'R{i}' for i in range(1, 6)})
            for rid, rival in row['rivals'].items():
                joined_count += refs(rival['observations'], f'{cid}/{rid}')
                rival_count += 1
                if rival['relation'] == 'counter_observation_under_stated_assumption':
                    check(f'{cid}/{rid} counterclaim assumption explicit', bool(rival['assumption']))
            unresolved, unsupported, opportunity = [], [], []
            for n, edge in enumerate(row['transitions'], start=1):
                cited = refs(edge['observations'], f'{cid}/edge{n}')
                joined_count += cited
                if edge['state'] == 'unresolved':
                    unresolved.append(n)
                elif cited == 0:
                    unsupported.append(n)
                if edge['type'] == 'population_opportunity':
                    opportunity.append(n)
                if edge['state'] == 'attributed_inference':
                    check(f'{cid}/edge{n} attributed premises explicit', bool(edge['premises']))
            complete = bool(row['transitions']) and not unresolved and not unsupported and not opportunity and\
                       all(edge['feature_specific'] for edge in row['transitions']) and bool(row['rival_discrimination_basis'])
            values = {'id': cid, 'family': row['family'], 'decision': row['decision'],
                      'unresolved_transition_indices': unresolved,
                      'opportunity_only_indices': opportunity,
                      'unsupported_resolved_transition_indices': unsupported,
                      'declared_local_descent_record_completeness': complete,
                      'claims_traced_local_literary_descent': False,
                      'rival_relations': {key: val['relation'] for key, val in row['rivals'].items()}}
            for key, val in values.items():
                check(f'{cid} reconstructed output {key}', output_by_id[cid][key] == val)
            reconstructed.append(values)
        check('35 rival records', rival_count == 35)
        check('all selected local-descent declarations incomplete', not any(
            r['declared_local_descent_record_completeness'] for r in reconstructed))
        check('root reports297passed declaration checks', root['checks_passed'] == 297 and root['checks_failed'] == 0)
        check('all root declaration assertions pass', len(root['checks']) == 297 and all(r['passed'] for r in root['checks']))
        for name, digest in root['input_sha256'].items():
            check(f'root input pin {name}', sha(REPO / name) == digest)
        check('root result code pin', sha(BASE / 'coordinator/audit_comparisons.py') == root['code_sha256'])
        result = {'created_utc': datetime.now(timezone.utc).isoformat(),
                  'scope': 'Independent reconstruction of reference IDs and declared completeness; semantic decisions require separate source review',
                  'checks_passed': len(checks), 'checks': checks,
                  'comparisons': reconstructed, 'rival_records': rival_count,
                  'reference_occurrences_resolved': joined_count,
                  'input_sha256': {name: sha(BASE / name) for name in ['coordinator/comparisons-v1.json',
                                     'coordinator/run-v1/audit.json', 'coordinator/AUDIT-PROTOCOL.md',
                                     'coordinator/AUDIT-AMENDMENT.md']},
                  'protocol_sha256': sha(HERE / 'COMPARISON-CHECK-PROTOCOL.md'),
                  'code_sha256': sha(Path(__file__)),
                  'source_ledger_sha256': {name: sha(REPO / name) for name in ledgers},
                  'manual_review': 'REVIEW.md; narrow uniqueness, attributed comparative inheritance, represented analogy and organization/redaction limits read directly'}
        (out / 'checks.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps({'checks_passed': len(checks), 'comparisons': 7,
                          'rival_records': rival_count, 'resolved_reference_occurrences': joined_count}))
    except Exception as exc:
        (out / 'failure.json').write_text(json.dumps({'status': 'failed; preserved', 'error': repr(exc),
                                                    'checks': checks}, indent=2) + '\n', encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
