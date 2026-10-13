"""Logical countercases to six route overclaims; no historical probabilities."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE / 'counterexamples-v1')
    out = parser.parse_args().out.resolve()
    if not out.is_relative_to(HERE):
        raise SystemExit('Output must be within the owned review directory')
    if out.exists():
        raise SystemExit(f'Refusing existing output directory: {out}')
    out.mkdir()
    cases = [
        {
            'id': 'IC01',
            'overclaim': 'Successive local practice implies descent of a later textual institution',
            'assignments': {'successive_local_practice': True, 'later_textual_institution': True,
                            'same_feature_at_both_domains': False, 'literary_descent': False},
            'antecedent': True, 'conclusion': False,
            'construction': 'A locally maintained drainage operation and an independently composed hymn both exist. No matching technical feature links the hymn to that operation.',
        },
        {
            'id': 'IC02',
            'overclaim': 'Population admixture implies transmission of a specified practice',
            'assignments': {'population_admixture': True, 'feature_transmitted': False,
                            'feature_specific_carrier_observed': None},
            'antecedent': True, 'conclusion': False,
            'construction': 'People mix, while the particular lost tool-making recipe is not taught or reacquired. Population mixing and recipe loss are consistent assignments.',
        },
        {
            'id': 'IC03',
            'overclaim': 'A borrowed term identifies a named Harappan donor practice',
            'assignments': {'borrowed_term': True, 'donor': 'other regional community',
                            'named_harappan_donor': False},
            'antecedent': True, 'conclusion': False,
            'construction': 'A later speaker borrows a crop name from a neighboring community whose recipe history is unobserved. Contact vocabulary exists without the named donor attribution.',
        },
        {
            'id': 'IC04',
            'overclaim': 'An inherited ritual comparison excludes every local contribution',
            'assignments': {'inherited_ritual_role': True, 'local_operation_acquired': True,
                            'all_local_contributions_excluded': False},
            'antecedent': True, 'conclusion': False,
            'construction': 'A specialist inherits an office and its verbal formulae, then learns a local water-lifting technique. The role and operation have different route histories.',
        },
        {
            'id': 'IC05',
            'overclaim': 'Later synthesis implies that all components were invented late',
            'assignments': {'later_synthesis': True, 'older_component_reused': True,
                            'all_components_invented_at_synthesis': False},
            'antecedent': True, 'conclusion': False,
            'construction': 'A compiler arranges an older song and an older procedure under a new explanation. The organization is new while both components predate it.',
        },
        {
            'id': 'IC06',
            'overclaim': 'Several agreeing versions increase the independent observation count',
            'assignments': {'agreeing_versions': ['print', 'digital edition', 'translation'],
                            'parent_lineage': {'print': 'L1', 'digital edition': 'L1', 'translation': 'L1'},
                            'more_than_one_independent_observation': False},
            'antecedent': True, 'conclusion': False,
            'construction': 'A printed edition, its electronic transcription and a translation all preserve the same underlying observation. The lineage set contains one member.',
        },
    ]
    assertions = []

    def check(name, condition):
        assertions.append({'check': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    try:
        check('all six distinct controls', [c['id'] for c in cases] == [f'IC{i:02d}' for i in range(1, 7)])
        for c in cases:
            check(f"{c['id']} true antecedent and false conclusion", c['antecedent'] is True and c['conclusion'] is False)
        check('admixture control retains unknown carrier rather than absence',
              cases[1]['assignments']['feature_specific_carrier_observed'] is None)
        lineages = set(cases[5]['assignments']['parent_lineage'].values())
        check('three agreeing versions have one lineage', len(lineages) == 1 and
              len(cases[5]['assignments']['agreeing_versions']) == 3)
        check('inherited role and local operation coexist', cases[3]['assignments']['inherited_ritual_role'] and
              cases[3]['assignments']['local_operation_acquired'])
        result = {'created_utc': datetime.now(timezone.utc).isoformat(),
                  'scope': 'Invented logical countercases; no historical probabilities or additional empirical sample',
                  'protocol_sha256': digest(HERE / 'COUNTEREXAMPLES-PROTOCOL.md'),
                  'coordinator_protocol_sha256': digest(ROOT / 'coordinator/AUDIT-PROTOCOL.md'),
                  'code_sha256': digest(Path(__file__)), 'cases': cases,
                  'checks_passed': len(assertions), 'checks': assertions}
        (out / 'results.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps({'countercases': len(cases), 'checks_passed': len(assertions), 'endpoint': str(out / 'results.json')}))
    except Exception as exc:
        (out / 'failure.json').write_text(json.dumps({'status': 'failed; preserved', 'error': repr(exc),
                                                    'checks': assertions}, indent=2) + '\n', encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
