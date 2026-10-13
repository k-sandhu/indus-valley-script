"""Pin the manually reviewed argument and independently verify claim joins."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[1]
CORE = [
    'README.md', 'PROTOCOL.md', 'THEORY.md', 'EMPIRICAL-TESTS.md',
    'MANUSCRIPT.md', 'REPORT.md', 'REVIEW-RESPONSE.md', 'RETROSPECTIVE.md',
    'CLAIM-EVIDENCE.json', 'coordinator/comparisons-v1.json',
    'coordinator/source-summary-v1.json',
]
MANUAL_CLAIMS = {
    'P01': 'Component-history hypothesis with stated precedents; no measured ancestry.',
    'P02': 'Selected catalogue pages confirm working stage and one accession collision; local production remains attributed.',
    'P03': 'Actual collection description supports mixed manufacture histories; deposition is not manufacture time.',
    'P04': 'Contributor forming-trace audit and independently read neighboring-maker proposal retain their different scopes.',
    'P05': 'Original supplement confirms specimen ranges and probability scope, with missing individual layer joins.',
    'P06': 'Complete paired hymn retains ritual and figurative context; a matching material sequence remains unobserved.',
    'P07': 'Bounded role comparison challenges narrow uniqueness while preserving local contributions.',
    'P08': 'Competence depiction and attributed inherited-role comparisons remain separate evidential types.',
    'P09': 'Represented sifting/speech comparison is directly supported; refinement and untraced donor are explicit.',
    'P10': 'Selected paired DN 1 paragraphs support own-stage livelihood organization, without an earlier rewrite claim.',
    'P11': 'Independent selected demographic reading supports opportunity-versus-feature-transfer distinction.',
    'P12': 'All seven comparisons and 35 rival declarations assert no traced local literary descent.',
    'P13': 'Actual software fixture passes declarations with an expressly invented and unsupported interpretation.',
    'P14': 'Exploratory mechanism has prospective tests; current observations do not authenticate its ancestry.',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def pointer(doc, path):
    if path == '':
        return doc
    if not path.startswith('/'):
        raise ValueError('Invalid JSON pointer')
    for part in path[1:].split('/'):
        key = part.replace('~1', '/').replace('~0', '~')
        doc = doc[int(key)] if isinstance(doc, list) else doc[key]
    return doc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE / 'reviewer-final-v1')
    out = parser.parse_args().out.resolve()
    if not out.is_relative_to(HERE):
        raise SystemExit('Output must be within the owned review directory')
    if out.exists():
        raise SystemExit('Refusing existing output directory')
    out.mkdir()
    checks, cache, ledgers = [], {}, {}

    def check(name, passed):
        checks.append({'check': name, 'passed': bool(passed)})
        if not passed:
            raise AssertionError(name)

    def document(name):
        if name not in cache:
            cache[name] = read(REPO / name)
        return cache[name]

    def validate_pin(name, digest, relative_to=REPO):
        check(f'current pin {name}', sha(relative_to / name) == digest)

    try:
        reviewed = {}
        for name in CORE:
            path = BASE / name
            check(f'reviewed core exists {name}', path.is_file())
            reviewed[path.relative_to(REPO).as_posix()] = sha(path)
        claims = read(BASE / 'CLAIM-EVIDENCE.json')['claims']
        check('14 distinct synthesis claim IDs', {r['id'] for r in claims} == set(MANUAL_CLAIMS) and len(claims) == 14)
        reference_count, pointer_count = 0, 0
        for row in claims:
            cid = row['id']
            check(f'{cid} statement and evidential status explicit', bool(row['statement']) and bool(row['status']))
            for ref in row['observations']:
                name = ref['file']
                if name not in ledgers:
                    doc = document(name)
                    rows = doc['observations'] if isinstance(doc, dict) else doc
                    ids = [r.get('observation_id', r.get('id')) for r in rows]
                    check(f'actual distinct IDs {name}', None not in ids and len(ids) == len(set(ids)))
                    ledgers[name] = dict(zip(ids, rows))
                for oid in ref['ids']:
                    check(f'{cid} actual reference {oid}', oid in ledgers[name])
                    reference_count += 1
            for item in row['outputs']:
                actual = pointer(document(item['file']), item['pointer'])
                check(f'{cid} exact pointer {item["pointer"]}',
                      type(actual) is type(item['equals']) and actual == item['equals'])
                pointer_count += 1
            for field in ['discussion', 'test', 'independent_check']:
                check(f'{cid} linked {field}', (REPO / row[field]).is_file())
        check('15 exact output pointers', pointer_count == 15)

        summary = read(BASE / 'coordinator/source-summary-v1.json')
        for name, digest in summary['input_sha256'].items():
            validate_pin(name, digest, BASE)
        ms = read(BASE / 'material/sources.json')['sources']
        mo = read(BASE / 'material/observations.json')['observations']
        ts = read(BASE / 'texts/SOURCES-v2.json')['sources']
        to = read(BASE / 'texts/OBSERVATIONS.json')['observations']
        tl = read(BASE / 'texts/LEXICAL-SOURCE-OBSERVATIONS.json')['observations']
        rs = read(HERE / 'sources-v2.json')['sources']
        ro = read(HERE / 'observations-v2.json')['observations']
        cs = read(BASE / 'coordinator/sources-v2.json')['sources']
        co = read(BASE / 'coordinator/observations-v2.json')['observations']
        comparisons = read(BASE / 'coordinator/comparisons-v1.json')['comparisons']
        result_rows = read(BASE / 'coordinator/run-v1/audit.json')['comparisons']
        main_rows = [r for r in to if r['observation_id'].startswith(('TX-RV9.112.', 'TX-RV10.71.', 'TX-RV10.101.'))]
        frame_values = {
            'material': {'source_records': len(ms), 'observations': len(mo),
                         'observed_teaching_relationships': sum(r['teaching_relationship_observed'] is True for r in mo),
                         'diagnostic_cross_domain_joins': sum(r['diagnostic_cross_domain_join'] is True for r in mo)},
            'texts': {'source_records': len(ts), 'main_stanzas': len(main_rows),
                      'control_observation_summaries': len(to) - len(main_rows),
                      'lexical_source_observations': len(tl),
                      'authored_observation_records': len(to) + len(tl)},
            'independent_review': {'target_records': len(rs),
                                   'scoped_primary_works': sum(r['selected_primary_work'] is True for r in rs),
                                   'unavailable_target_records': sum(r['selected_primary_work'] is False for r in rs),
                                   'observations': len(ro)},
            'coordinator_controls': {'source_records': len(cs), 'observations': len(co)},
            'comparisons': {'cases': len(comparisons),
                            'rival_records': sum(len(r['rivals']) for r in comparisons),
                            'asserted_traced_local_literary_descent': sum(r['claims_traced_local_literary_descent'] is True for r in comparisons),
                            'declared_record_completeness': sum(r['declared_local_descent_record_completeness'] is True for r in result_rows)},
        }
        for frame, fields in frame_values.items():
            for field, value in fields.items():
                check(f'separate census {frame}/{field}', summary[frame][field] == value)

        capsules = [
            ('source-checks-v2/checks.json', 174, HERE, 'audit_sources_v2.py'),
            ('comparison-checks-v1/checks.json', 260, BASE, None),
        ]
        for name, expected, input_base, code in capsules:
            capsule = read(HERE / name)
            check(f'preserved scoped check total {name}', capsule['checks_passed'] == expected and
                  len(capsule['checks']) == expected and all(r['passed'] for r in capsule['checks']))
            for input_name, digest in capsule['input_sha256'].items():
                validate_pin(input_name, digest, input_base)
            if code:
                check(f'preserved checker code {name}', sha(HERE / code) == capsule['code_sha256'])
            else:
                check(f'preserved checker code {name}', sha(HERE / 'check_comparisons.py') == capsule['code_sha256'])
                for input_name, digest in capsule['source_ledger_sha256'].items():
                    validate_pin(input_name, digest)

        anchors = read(HERE / 'additional-anchor-review-v2.json')
        for name, digest in anchors['branch_observation_pins'].items():
            validate_pin(name, digest, BASE)
        anchor_pins = []
        for row in anchors['records']:
            for field in ['witness', 'render', 'paired_derivative']:
                if field in row:
                    anchor_pins.append(row[field])
            for field in ['witnesses', 'renders']:
                anchor_pins.extend(row.get(field, []))
        for item in anchor_pins:
            path = REPO / item['path']
            check(f'additional witness hash {item["path"]}', sha(path) == item['sha256'])
            check(f'additional witness bytes {item["path"]}', path.stat().st_size == item['bytes'])
        edit = anchors['editorial_successor']
        check('additional anchor predecessor retained', sha(HERE / edit['original_endpoint']) == edit['original_sha256'])
        check('additional anchor editorial code retained', sha(HERE / 'edit_anchor_review_v2.py') == edit['editorial_code_sha256'])
        check('literal-anchor failure retained', (HERE / 'source-checks-v1/failure.json').is_file())
        check('validator-wrapper failure retained', (HERE / 'validator-scope-v1/failure.json').is_file())
        fixture = read(HERE / 'validator-scope-v2/interpretation.json')
        check('unsupported semantic fixture result retained', fixture['expected_limitation_observed'] is True)

        result = {
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'scope': 'Final substantive assessment plus independent documentary claim/count/preservation checks; no historical likelihood or authenticated ancestry.',
            'no_unresolved_blockers': True,
            'manual_substantive_assessment': {
                'status': 'Acceptable at the declared component and source scopes.',
                'review': 'REVIEW.md',
                'claims': [{'id': cid, 'assessment': text, 'status': 'acceptable_at_declared_scope'} for cid, text in MANUAL_CLAIMS.items()],
                'requirements_retained': ['TC04 narrow uniqueness challenge', 'TC05 attributed comparative inheritance with premises',
                                          'TC06 directly represented analogy and post-reading refinement',
                                          'R5 own-stage organization distinct from demonstrated redaction',
                                          'No asserted traced local Harappan literary descent'],
                'remaining_research_questions': ['Specific carrier histories', 'Distinctive operation-to-textual joins',
                                                'Measured comparative rarity', 'Earlier verbal history of the sifting analogy'],
            },
            'reviewed_file_sha256': reviewed,
            'source_verification': {
                'control_target_records': 7, 'scoped_primary_works': 6, 'observations': 19,
                'preserved_documentary_checks': 174, 'visually_checked_control_page_renders': 8,
                'additional_material_works_at_selected_loci': 4, 'additional_material_pdf_pages_viewed': 5,
                'additional_anchor_pin_records': len(anchor_pins),
                'paired_derivative_reading': 'All 27 main Rigvedic stanzas and DN 1.1.21–27; actual parent HTML independently checked at RV 10.71.2.',
                'limit': 'Contributor scopes cover other integrated source loci. No whole-report reading, manuscript collation or genetic reanalysis is asserted.',
            },
            'comparison_verification': {'independent_documentary_checks': 260, 'comparisons': 7, 'rival_records': 35,
                                        'scope': 'Reference/declaration reconstruction; semantic decisions separately read.'},
            'final_documentary_verification': {'checks_passed': len(checks), 'claims': len(claims),
                                               'exact_output_pointers': pointer_count,
                                               'observation_reference_occurrences': reference_count,
                                               'separate_frame_counts': frame_values},
            'checks': checks,
            'input_sha256': {p.relative_to(REPO).as_posix(): sha(p) for p in [
                HERE / 'REVIEW.md', HERE / 'sources-v2.json', HERE / 'observations-v2.json',
                HERE / 'source-checks-v2/checks.json', HERE / 'comparison-checks-v1/checks.json',
                HERE / 'additional-anchor-review-v2.json', HERE / 'validator-scope-v2/interpretation.json']},
            'protocol_sha256': sha(HERE / 'FINAL-REVIEW-PROTOCOL.md'),
            'code_sha256': sha(Path(__file__)),
            'excluded_from_substantive_review_pins': 'Coordinator finalizers, navigation edits and final manifest tooling.',
        }
        with (out / 'checks.json').open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps({'no_unresolved_blockers': True, 'checks_passed': len(checks),
                          'claims': len(claims), 'exact_output_pointers': pointer_count,
                          'pinned_core_files': len(reviewed)}))
    except Exception as exc:
        with (out / 'failure.json').open('x', encoding='utf-8') as stream:
            json.dump({'status': 'failed; preserved', 'error': repr(exc), 'checks': checks}, stream, indent=2)
            stream.write('\n')
        raise


if __name__ == '__main__':
    main()
