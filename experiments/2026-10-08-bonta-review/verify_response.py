"""Verify response calculations, source annotations, replay and protected hashes.

Run from the repository root. This checks computational/source-record consistency;
manual caption/audio and manuscript-glyph adjudication remains separate.
"""
from pathlib import Path
import argparse, ast, collections, hashlib, json, math, re

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
BASE = OWN / 'response-2026-10-08-v2'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', default='response-replay-2026-10-08-01')
    parser.add_argument('--output', default='response-checks-2026-10-08-v4.json')
    args = parser.parse_args()
    replay = (OWN / args.replay).resolve()
    target = (OWN / args.output).resolve()
    if not replay.is_relative_to(OWN) or not target.is_relative_to(OWN):
        parser.error('paths must remain inside owned directory')
    if target.is_relative_to(OWN / 'review') or target.is_relative_to(OWN / 'history'):
        parser.error('reviewer files and historical snapshots are read-only')
    if target.exists():
        parser.error('refusing to replace an existing verification')
    checks = []
    def check(name, condition, evidence):
        checks.append({'name': name, 'passed': bool(condition), 'evidence': evidence})
    manifest = read(BASE / 'manifest.json')
    for row in manifest['protected_files']:
        check('preserved ' + row['path'], digest(ROOT / row['path']) == row['sha256'], 'response manifest protected_files')
    for row in manifest['inputs']:
        check('input pin ' + row['path'], digest(ROOT / row['path']) == row['sha256'], 'response manifest inputs')
    for p in sorted(BASE.glob('*.json')):
        if p.name != 'manifest.json':
            check('replay aggregate ' + p.name, read(p) == read(replay / p.name), str(p.relative_to(ROOT)))
    rawbase = ROOT / manifest['raw_output_root']
    rawreplay = ROOT / read(replay / 'manifest.json')['raw_output_root']
    for p in sorted(rawbase.glob('*.json')):
        check('replay derivative ' + p.name, digest(p) == digest(rawreplay / p.name), 'local-only derivative equality')

    review = read(OWN / 'review/review-checks.json')
    lex = read(BASE / 'lexical-sensitivities.json')
    frozen = read(OWN / 'run-2026-10-08-v1/lexical.json')
    for endpoint, reviewerkey in [('exact', 'exact'), ('normalized', 'package_normalization')]:
        actual = lex['endpoints'][endpoint]
        ref = review['lexical_independent'][reviewerkey]
        check(endpoint + ' observed nine', actual['whole_panel']['observed'] == ref['observed'] == 9, 'lexical-sensitivities endpoints and review lexical_independent')
        check(endpoint + ' histogram matches independent review', actual['whole_panel']['histogram'] == ref['histogram'], 'lexical-sensitivities endpoints and review lexical_independent')
        check(endpoint + ' PU moved tail zero', actual['PU_moved']['assignments_at_least_observed'] == 0 and actual['PU_moved']['assignments'] == 600, 'endpoints.' + endpoint + '.PU_moved')
        expected = 3 if endpoint == 'exact' else 13
        check(endpoint + ' PU retained tail', actual['PU_held_fixed']['assignments_at_least_observed'] == expected and actual['PU_held_fixed']['assignments'] == 120, 'endpoints.' + endpoint + '.PU_held_fixed')
        fixed = actual['PU_and_PATI_held_fixed']
        check(endpoint + ' PU/PATI fixed agrees with review', f"{fixed['assignments_at_least_observed']}/{fixed['assignments']}" == ref['tail_permuting_only_MA_TRA_PALA_DHANA'], 'endpoints fixed roles and review')
        dropped = actual['PU_and_PATI_strings_dropped_four_roles_permuted']
        expected_drop = 4 if endpoint == 'exact' else 8
        check(endpoint + ' dropped roles endpoint', (dropped['observed'], dropped['assignments'], dropped['assignments_at_least_observed']) == (2, 24, expected_drop), 'endpoints.' + endpoint + '.PU_and_PATI_strings_dropped_four_roles_permuted')
    check('eight developmental strings', lex['strings_containing_PU_or_PATI'] == 8 and lex['drop_dictionary_derived_strings_retained_ids'] == ['A01', 'A02'], 'lexical-sensitivities selection fields')
    check('normalization explicitly broader', lex['normalization_broader_than_Table18_role_lists'], 'lexical-sensitivities normalization field')

    fish = read(BASE / 'fish-adjacency.json')
    oldfish = review['fish_proxy_power']
    check('fish adjacency agrees with review', fish['observed_adjacent_pairs'] == oldfish['observed_adjacent_fish_pairs'] == 135 and fish['shuffle_mean_adjacent_pairs'] == oldfish['shuffle_adjacent_pairs_mean'] == 54.5505, 'fish-adjacency and review fish_proxy_power')
    check('fish reference range', fish['shuffle_reference_range_95'] == [44.0, 65.0] and fish['shuffle_maximum'] == 74, 'fish-adjacency reference fields')
    check('fish old endpoint lacks discriminatory support', fish['maximum_fish_tokens_any_observed_face'] == 3 and fish['selected_texts_with_repeated_fish_code'] == 3 and fish['shuffle_probability_zero_repeating_runs'] == 0.3915, 'fish-adjacency composition fields')
    check('fish add-one tail', math.isclose(fish['add_one_tail_fraction'], 1 / 2001), 'fish-adjacency add_one_tail_fraction')
    dist = read(BASE / 'terminal-exceptions.json')
    check('population preserved', (dist['objects'], dist['tokens']) == (2469, 10835), 'terminal-exceptions population')
    for code, counts in [('740', (1196, 838, 358, 355)), ('520', (225, 192, 33, 33))]:
        x = dist['signs'][code]
        check(code + ' terminal and exception counts', tuple(x[k] for k in ['tokens', 'final_tokens', 'nonfinal_tokens', 'objects_with_nonfinal']) == counts, 'terminal-exceptions signs.' + code)
        check(code + ' exception fraction', math.isclose(x['nonfinal_fraction'], (counts[0] - counts[1]) / counts[0]), 'terminal-exceptions signs.' + code)
    check('jar next 400/090 census', dist['signs']['740']['following_sign_counts']['400'] == 146 and dist['signs']['740']['following_sign_counts']['090'] == 95 and dist['signs']['740']['nonfinal_followed_by_400_or_090'] == 241, 'terminal-exceptions signs.740')
    check('jar sites', all(dist['signs']['740']['objects_with_nonfinal_by_site'][s] == n for s, n in [('Harappa',189),('Mohenjo-daro',129),('Lothal',15)]), 'terminal-exceptions signs.740 objects_with_nonfinal_by_site')

    audit = read(BASE / 'validation-audit-v2.json')
    check('validation classifications', tuple(audit[k] for k in ['confirmed_catalogue_object_overlaps','conflicting_label_overlaps','parser_false_overlaps']) == (3,0,3), 'validation-audit-v2 count fields')
    obs = {x['ICIT']: x for x in audit['observations']}
    check('entry types distinguished', obs['3084']['entry_type'] == 'MH_first_entry_with_ICIT_alias' and obs['3656']['entry_type'] == 'ICIT_first_reading_entry' and obs['2816']['entry_type'] == 'iconography_only_mention', 'validation-audit-v2 observations')
    check('ICIT2717 parser error', obs['2717']['classification'] == 'parser_false_overlap_multiple_aliases' and obs['2717']['correct_CISI'] == 'M-192' and obs['2717']['correct_ICIT_for_M1714'] == '2346', 'validation-audit-v2 observations ICIT2717')
    check('unknown validation denominators', not any(audit[k] for k in ['validation_membership_known','attempt_denominator_known','failure_denominator_known']), 'validation-audit-v2 unknown gates')
    check('eight explicit references', len(audit['explicit_references']) == 8 and sum(x['qualifier'] is None for x in audit['explicit_references']) == 7, 'validation-audit-v2 explicit_references')
    errata = read(BASE / 'selection-errata.json')
    check('selection hash unchanged', errata['unchanged_selection_sha256'] == digest(OWN / 'selection.json') == 'ca1c57de2895a89a0aa966139ea6e1ead7051b50f4f681dfe7ef6b5e330800b5', 'selection-errata unchanged_selection_sha256')
    check('selection object correction', [x['correct_CISI'] for x in errata['corrections']] == ['M-1688','M-958'], 'selection-errata corrections')
    check('PU tall and short cases', [x['PU_followed_by_full_height_033'] for x in errata['objects']] == [1,0,0] and [x['PU_followed_by_short_stroke_003'] for x in errata['objects']] == [0,1,1], 'selection-errata objects')

    ledger = [json.loads(l) for l in (OWN / 'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    byid = {r['id']: r for r in ledger}
    ca = read(OWN / 'claim-source-audit-2026-10-08-v2.json')
    original = {r['id']: r for r in [json.loads(l) for l in (ROOT / ca['baseline']).read_text(encoding='utf-8').splitlines()]}
    check('all original rows audited', len(ca['records']) == 126 and len(ledger) == 130 and set(original) == {x['id'] for x in ca['records']}, 'claim-source-audit records and claims.jsonl')
    outside = [r for r in ca['records'] if not r['reviewer_sample']]
    check('74 unsampled checked; 74 changed', len(outside) == 74 and sum(r['changed'] for r in outside) == 74, 'claim-source-audit counts and records')
    check('unsampled change categories', [ca['counts'][k] for k in ['outside_sample_table_rows_changed','outside_sample_reading_rows_changed','outside_sample_other_rows_changed']] == [53,10,11], 'claim-source-audit counts')
    check('every change log agrees with ledger', all(all(original[r['id']].get(k) == v['before'] and byid[r['id']].get(k) == v['after'] for k, v in r['changed_fields'].items()) and (original[r['id']] != byid[r['id']]) == r['changed'] for r in ca['records']), 'claim-source-audit changed_fields')
    types = dict(collections.Counter(r['type'] for r in ledger))
    coverage = read(OWN / 'ledger-coverage.json')
    check('ledger type counts current', coverage['by_type'] == types and sum(types.values()) == 130, 'ledger-coverage by_type')
    check('existing scope remains explicit', not coverage['complete_substantive_claim_inventory'], 'ledger-coverage complete_substantive_claim_inventory')
    test_ids = {'D1','D2','D3','L1','L2','V1','M1','D1-R','D2-R','L1-R','V1-R','C1-R'}
    check('no undefined test IDs', all(set(r['test_ids']).issubset(test_ids) for r in ledger), 'claims.jsonl test_ids and protocol')
    sources = read(OWN / 'sources.json')
    source_ids = {s['id'] for s in sources['sources']}
    check('all ledger sources resolve', all(r['source_id'] in source_ids for r in ledger), 'claims.jsonl source_id and sources.json')
    def squash(s):
        return ' '.join(s.split())
    quote_rows = [r for r in ledger if r['quotation']]
    check('short quotation limits', len(quote_rows) == 7 and all(len(r['quotation'].split()) <= 15 for r in quote_rows), 'claims.jsonl quotation fields')
    for r in quote_rows:
        if r['source_id'].startswith('L'):
            path = next((RAW / 'captions').glob(r['source_id'][1:] + '-*.txt'))
        else:
            path = RAW / 'acquisition-2026-10-08-v1/bonta-letter.txt'
        check('exact source quotation ' + r['id'], squash(r['quotation']) in squash(path.read_text(encoding='utf-8')), 'local witness at ' + r['source_location'])
    sr = {r['id']: r for r in sources['sources']}
    check('Kalyanaraman marked unverified', sr['K24']['opened'] is False and sr['K24']['verification_status'] == 'Unverified', 'sources K24')
    check('source quotation metadata agrees', all(sr[r['source_id']]['short_quotation'] == r['quotation'] for r in quote_rows), 'sources quotation metadata')
    for name in ('review_response.py', 'revise_claims.py', 'update_response_metadata.py', 'verify_response.py', 'inventory.py'):
        ast.parse((OWN / name).read_text(encoding='utf-8-sig'))
        check('Python syntax ' + name, True, name)
    broken = []
    for name in ('README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','claims.md'):
        text = (OWN / name).read_text(encoding='utf-8-sig')
        for link in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', text):
            if re.match(r'^[a-zA-Z]+://', link) or link.startswith('#'):
                continue
            path = link.split('#')[0].strip('<>')
            if path and (OWN / path).resolve() == target:
                continue
            if path and not (OWN / path).exists():
                broken.append({'file': name, 'target': path})
    check('current Markdown local links', not broken, broken or 'all relative file links resolve')
    result = {'status': 'Verified computation' if all(c['passed'] for c in checks) else 'Failed',
              'passed': sum(c['passed'] for c in checks), 'total': len(checks), 'replay': args.replay,
              'scope': 'Computational/source-record consistency and preservation; no audio or missing-glyph authentication.', 'checks': checks}
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'checks'}, indent=2))
    for c in checks:
        if not c['passed']:
            print(json.dumps(c, ensure_ascii=False))
    if result['status'] == 'Failed':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
