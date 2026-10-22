"""Recount outputs independently and check run 3 invariants."""
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from identity_io import (ROOT, PACKAGE, OUT, LOCAL, CORPUS, TOP, META,
                         read_csv, corpus_rows, sha, compact, id_rule,
                         normalise, projected_json, blocked_patterns, write_json)


def run():
    summary = json.loads((OUT / 'match-summary.json').read_text(encoding='utf-8'))
    _, rows = read_csv(OUT / 'objects-merged.csv')
    _, count_rows = read_csv(OUT / 'site-counts.csv')
    _, sources = read_csv(OUT / 'source-register.csv')
    checks, errors = {}, []

    def check(name, passed, detail=None):
        checks[name] = {'passed': bool(passed)}
        if detail is not None:
            checks[name]['detail'] = detail
        if not passed:
            errors.append(name)

    extracted = []
    for part in ('N', 'G', 'D', 'P', 'E', 'F'):
        extracted.extend(read_csv(PACKAGE / f'extraction/{part}/objects-{part}.csv')[1])
    check('each_extraction_row_once',
          Counter(r['row_id'] for r in extracted) == Counter(r['provisional_row_id'] for r in rows)
          and len(rows) == summary['rows_merged'], {'input_rows': len(extracted), 'output_rows': len(rows)})
    by_old = {r['row_id']: r for r in extracted}
    changed_cells = []
    for row in rows:
        before = by_old[row['provisional_row_id']]
        for key in before:
            if key not in {'row_id', 'catalogue_status', 'possible_duplicate_of'} and row[key] != before[key]:
                changed_cells.append({'row_id': row['row_id'], 'field': key})
    check('extraction_values_preserved', not changed_cells, changed_cells)
    check('final_row_ids_unique', len({r['row_id'] for r in rows}) == len(rows))

    _, seeds = read_csv(PACKAGE / 'selection/sites-seed.csv')
    aliases = {}
    for row in seeds:
        for alias in [row['site'], *row['aliases'].split('|')]:
            if alias:
                aliases[compact(alias)] = row['site']
    for row in count_rows:
        if row['site'] != 'TOTAL':
            aliases.setdefault(compact(row['site']), row['site'])
    fams = {}
    allowed_projection = True
    for face in corpus_rows():
        allowed_projection &= set(face) <= set(TOP) | {'metadata'}
        allowed_projection &= set(face.get('metadata', {})) <= set(META)
        site = aliases.get(compact(face['site']))
        if site is None:
            continue
        fid = str(face['object_family_id'])
        if fid in fams and fams[fid] != site:
            allowed_projection = False
        fams[fid] = site
    check('corpus_projection_allowlist', allowed_projection)
    wrong_refs = []
    for row in rows:
        for fid in filter(None, row['local_family_ids'].split('|')):
            if fams.get(fid) != row['site']:
                wrong_refs.append({'row_id': row['row_id'], 'family': fid})
    check('family_references_exist_at_site', not wrong_refs, wrong_refs)
    check('matched_has_one_family', all(len(list(filter(None, r['local_family_ids'].split('|')))) == 1
                                          for r in rows if r['local_match'] == 'matched'))
    check('candidate_has_families', all(r['local_family_ids'] for r in rows if r['local_match'] == 'candidate'))
    check('absent_has_no_families', all(not r['local_family_ids'] for r in rows if r['local_match'] == 'absent'))
    pairs = set()
    for name in ('cross-part-duplicates.csv', 'same-part-duplicates.csv'):
        for row in read_csv(OUT / name)[1]:
            pairs.add(tuple(sorted((row['row_id_a'], row['row_id_b']))))
    for row in rows:
        for other in re.findall(r'PCF-[A-Z]+-\d+', row['possible_duplicate_of']):
            pairs.add(tuple(sorted((row['row_id'], other))))
    uses = defaultdict(set)
    for row in rows:
        if row['local_match'] == 'matched':
            uses[row['local_family_ids']].add(row['row_id'])
    double_joins = [list(pair) for rids in uses.values() for pair in itertools.combinations(sorted(rids), 2)
                    if tuple(pair) not in pairs]
    check('no_double_match_without_duplicate_flag', not double_joins, double_joins)
    assigned = defaultdict(set)
    for row in rows:
        if row['local_match'] in {'matched', 'in-baseline-catalogue'}:
            for fid in filter(None, row['local_family_ids'].split('|')):
                assigned[fid].add(row['row_id'])
    bad_candidates = []
    for row in rows:
        if row['local_match'] == 'candidate':
            for fid in filter(None, row['local_family_ids'].split('|')):
                if any(tuple(sorted((row['row_id'], other))) not in pairs for other in assigned.get(fid, set())):
                    bad_candidates.append({'row_id': row['row_id'], 'family': fid})
    check('candidates_obey_family_reservations', not bad_candidates, bad_candidates)

    assigned_ids = {fid for fid, users in assigned.items() if users}
    numeric = [k for k in count_rows[0] if k not in {'site_code', 'site', 'best_publication', 'publication_basis'}]
    recomputed, differences = [], []
    for count_row in count_rows:
        site = count_row['site']
        if site == 'TOTAL':
            continue
        site_rows = [r for r in rows if r['site'] == site]
        eligible = [r for r in site_rows if r['catalogue_status'] == 'post-catalogue' and r['inscription_status'] == 'stated']
        states = Counter(r['local_match'] for r in eligible)
        matched_ids = {f for r in eligible if r['local_match'] == 'matched' for f in r['local_family_ids'].split('|') if f}
        candidate_ids = {f for r in eligible if r['local_match'] == 'candidate' for f in r['local_family_ids'].split('|') if f} - assigned_ids
        expected = {'rows_total': len(eligible),
                    'rows_individual': sum(r['row_basis'] == 'individual' for r in eligible),
                    'rows_enumerated': sum(r['row_basis'] == 'enumerated-count' for r in eligible),
                    'rows_uncertain_status': sum(r['inscription_status'] != 'stated' for r in site_rows),
                    'rows_possibly_in_cisi3': sum(r['catalogue_status'] == 'possibly-in-cisi3' for r in site_rows),
                    'rows_in_baseline_catalogue': sum(r['catalogue_status'] == 'in-baseline-catalogue' for r in site_rows),
                    'rows_post_catalogue': len(eligible), 'matched': states['matched'],
                    'candidate': states['candidate'], 'absent': states['absent'],
                    'local_families_at_site': sum(s == site for s in fams.values()),
                    'local_families_matched': len(matched_ids),
                    'local_candidate_families_unassigned': len(candidate_ids),
                    'absent_lower_bound': states['absent'] + max(0, states['candidate'] - len(candidate_ids)),
                    'absent_upper_bound': len(eligible) - states['matched']}
        for key, value in expected.items():
            if int(count_row[key]) != value:
                differences.append({'site': site, 'field': key})
        recomputed.append(expected)
    total = next(r for r in count_rows if r['site'] == 'TOTAL')
    for key in numeric:
        if int(total[key]) != sum(r[key] for r in recomputed):
            differences.append({'site': 'TOTAL', 'field': key})
    check('site_counts_recompute', not differences, differences)
    check('status_counts_partition_eligible_rows', all(int(r['rows_total']) == sum(int(r[k]) for k in ('matched', 'candidate', 'absent')) for r in count_rows))
    check('bounds_ordered', all(0 <= int(r['absent_lower_bound']) <= int(r['absent_upper_bound']) <= int(r['rows_total']) for r in count_rows))

    named = {f for r in rows for f in r['local_family_ids'].split('|') if f}
    _, unlisted = read_csv(OUT / 'local-unlisted.csv')
    check('local_unlisted_is_exact_complement',
          Counter(r['object_family_id'] for r in unlisted) == Counter({f: 1 for f in fams.keys() - named}))
    check('local_unlisted_counts_by_site', all(summary['local_unlisted_by_site'][s] == sum(r['site'] == s for r in unlisted)
                                               for s in summary['local_unlisted_by_site']))

    current_hash = sha(CORPUS)
    check('corpus_hash_matches_record', current_hash == summary['corpus_sha256'] and current_hash.startswith('1220f559'), current_hash)
    changed_inputs = [name for name, digest in summary['input_hashes'].items() if sha(ROOT / name) != digest]
    check('all_recorded_input_hashes_match', not changed_inputs, changed_inputs)
    script_changes = [name for name, digest in summary.get('script_hashes', {}).items() if sha(ROOT / name) != digest]
    # Script hashes are written by finish_3.py after the initial validation.
    check('recorded_script_hashes_match', not script_changes, script_changes)
    source_ids = [r['source_id'] for r in sources]
    expected_sources = set()
    for path in [PACKAGE / 'acquisition/source-register-1a.csv', PACKAGE / 'acquisition-web/source-candidates-1b.csv',
                 *sorted(PACKAGE.glob('extraction/*/source-register*.csv'))]:
        expected_sources.update(r['source_id'] for r in read_csv(path)[1])
    expected_sources.update(r['id'] for r in json.loads((PACKAGE / 'acquisition-coordinator/manifest-proposals-coordinator.json').read_text(encoding='utf-8'))['sources'])
    check('combined_source_register_complete_unique', len(source_ids) == len(set(source_ids)) and set(source_ids) == expected_sources,
          {'source_rows': len(source_ids)})
    check('primary_sources_registered', all(r['primary_publication'] in expected_sources for r in rows))
    locator_rows = read_csv(OUT / 'locator-checks.csv')[1]
    check('locators_use_combined_register', all(r['source_id'] in expected_sources for r in locator_rows))
    check('numeric_pdf_locators_in_registered_extents', not any(r['check'] == 'outside registered extent' for r in locator_rows))
    check('baseline_rows_have_catalogue_numbers', all(r['cisi_in_baseline'] for r in rows if r['catalogue_status'] == 'in-baseline-catalogue'))
    check('museum_absence_witness_respected', all(r['local_match'] == 'absent' for r in rows
                                                 if r['site'] == 'Dholavira' and r['registration'] == '22198'))
    check('registration_rule_examples', all([
        normalise('RGR-00051.007', {'RGR'}) == '517',
        id_rule('5123', '-DHR 5123', {'DHR'}) == 'registration-normalised',
        id_rule('5123', 'DHR512309', {'DHR'}) == 'registration-contained',
        id_rule('06-9074', 'RIHN-Indus project06-9074', {'KNM'}) == 'registration-contained',
        id_rule('9074', 'DK9074', {'DHR'}) is None,
        id_rule('9074', '190741', {'DHR'}) is None]))
    sample = '{"record_id":"x","skip":{"nested":[1,"\\\"",{}]},"metadata":{"type":"TAG","skip":[9]}}'
    check('projection_skips_unselected_nested_values', projected_json(sample, {'record_id': None, 'metadata': {'type': None}})
          == {'record_id': 'x', 'metadata': {'type': 'TAG'}})

    findings, scanned = [], []
    for directory in (OUT, LOCAL):
        for path in sorted(directory.rglob('*')):
            if not path.is_file() or path.suffix not in {'.py', '.csv', '.json', '.md'}:
                continue
            scanned.append(path.relative_to(ROOT).as_posix())
            body = path.read_text(encoding='utf-8')
            for i, pattern in enumerate(blocked_patterns()):
                for hit in pattern.finditer(body):
                    findings.append({'path': path.relative_to(ROOT).as_posix(), 'check_group': i, 'offset': hit.start()})
    check('all_owned_text_files_pass_content_scan', not findings, {'files_scanned': scanned, 'findings': findings})
    result = {'passed': not errors, 'checks_passed': sum(r['passed'] for r in checks.values()),
              'checks_total': len(checks), 'errors': errors, 'checks': checks,
              'corpus_sha256': current_hash,
              'warnings': ['PDF page extent unavailable for some registered sources; see locator-checks.csv',
                           'All proposals remain subject to coordinator review'],
              'selftest_scope': 'Independent count arithmetic and identity invariants; no source-page re-extraction'}
    assert not any(pattern.search(json.dumps(result, ensure_ascii=False)) for pattern in blocked_patterns()), 'Prospective check output failed content scan'
    write_json(OUT / 'selftest-3.json', result)
    print(json.dumps({'passed': result['passed'], 'checks_passed': result['checks_passed'],
                      'checks_total': result['checks_total'], 'errors': errors}))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    run()
