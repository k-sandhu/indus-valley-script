"""Check source corrections, frozen witnesses, exact replays and revised records."""
import argparse, collections, json, re
from pathlib import Path
from pdf_followup import ROOT, OWN, RAW, WORK, OUT, read, write, sha

RESPONSE = OWN / 'pdf-review-response-2026-10-09-v1'
LOCAL = RAW / RESPONSE.name
HISTORY = OWN / 'history/2026-10-09-before-pdf-review'
EDITABLE = {'README.md', 'REPORT.md', 'RETROSPECTIVE.md', 'PROTOCOL.md', 'sources.json',
            'registry-entry.json', 'claims.jsonl', 'claims.md', 'ledger-coverage.json', 'COMPLETION.md', 'FILES.json'}


def main(replay_name, output_name):
    replay = (OWN / replay_name).resolve(); raw_replay = (RAW / replay_name).resolve()
    endpoint = (OWN / output_name).resolve()
    if not replay.is_relative_to(OWN) or not raw_replay.is_relative_to(RAW) or not endpoint.is_relative_to(OWN):
        raise SystemExit('Paths must stay within package trees')
    if endpoint.exists():
        raise SystemExit('Check endpoint exists')
    checks = []
    def eq(label, actual, expected):
        checks.append({'check': label, 'passed': actual == expected, 'actual': actual, 'expected': expected})
    def yes(label, condition):
        eq(label, bool(condition), True)
    baseline = read(HISTORY / 'baseline-files.json')
    protected = 0
    for row in baseline:
        path = ROOT / row['path']
        if path.parent == OWN and path.name in EDITABLE:
            snapshot = HISTORY / path.name
            eq('snapshot ' + path.name, sha(snapshot), row['sha256'])
        else:
            eq('preserved ' + row['path'], sha(path) if path.is_file() else None, row['sha256'])
            protected += 1
    registration = read(RESPONSE / 'registration.json')
    eq('registered protocol hash', sha(RESPONSE / 'PROTOCOL-registered.md'), registration['protocol_sha256'])
    yes('registered protocol prefix preserved', (OWN / 'PROTOCOL.md').read_bytes().startswith(
        (RESPONSE / 'PROTOCOL-registered.md').read_bytes()))
    for row in registration['inputs']:
        eq('registered input ' + row['path'], sha(ROOT / row['path']), row['sha256'])
    field_reg = read(RESPONSE / 'field-registration.json')
    eq('field operational protocol hash', sha(RESPONSE / 'PROTOCOL-operational.md'), field_reg['protocol_sha256'])
    eq('field code preserved', sha(OWN / 'pdf_review_fields.py'), field_reg['code_sha256'])
    for mapping, digest in field_reg['mappings'].items():
        eq('field mapping ' + mapping, sha(OWN / f'two-coder-2026-10-09-v1/mapping-{mapping}.json'), digest)
    for label in ['first', 'second', 'agreed_only']:
        original = read(RESPONSE / label / 'field-corrections.json')
        eq('field replay ' + label, read(replay / label / 'field-corrections.json'), original)
        frozen = read(OWN / f'two-coder-2026-10-09-v1/{label}/field-test.json')
        eq('final-only recount ' + label, original['final_only_frozen_recipe_recount'], frozen['classification'])
        eq('field population sum ' + label, sum(original['widened_terminal']['classification'].values()), 2469)
        for name in ['field-correction-rows.json', 'field-correction-nulls.json']:
            eq('raw field replay ' + label + '/' + name, sha(raw_replay / label / name), sha(LOCAL / label / name))
    first = read(RESPONSE / 'first/field-corrections.json')
    reviewed = read(OWN / 'review-pdf/field-penultimate.json')['penultimate_admitted']
    eq('review widened classification', first['widened_terminal']['classification'], reviewed['classification'])
    eq('review widened null mean', first['widened_terminal']['clean_null']['null_mean'], reviewed['null_mean_clean'])
    reviewed = read(OWN / 'review-pdf/field-decomposition.json')
    eq('review clean without M', first['canonical_clean_composition']['without_M'], reviewed['clean_composition']['no M field'])
    eq('review clean with M', first['canonical_clean_composition']['with_M'], 259)
    eq('review C+T only', first['canonical_clean_composition']['C_T_without_P_or_M'], 323)
    eq('review M-order numerator', first['M_order']['ordered'], reviewed['ordering_conditional_on_content']['canonical_O_F_MS_order'])
    eq('review M-order denominator', first['M_order']['eligible'], 331)
    eq('review M-order null mean', first['M_order']['null_mean'], reviewed['ordering_conditional_on_content']['unit_shuffle_null_mean_fraction'])
    for name in ['value-derivations-v3.json', 'derivation-changes.json', 'reading-corrections.json',
                 'join-corrections.json', 'reading-index-v5.json', 'lexical-corrections.json']:
        eq('aggregate replay ' + name, read(replay / name), read(RESPONSE / name))
    for path in sorted((LOCAL / 'lexical-panels').glob('*.json')):
        eq('raw lexical replay ' + path.name, sha(raw_replay / 'lexical-panels' / path.name), sha(path))
    for name in ['reading-inventory-v5.json', 'reading-correction-details.json', 'clear-origin-attainability.json',
                 'derivation-split-membership.json']:
        eq('raw source replay ' + name, sha(raw_replay / name), sha(LOCAL / name))
    source_reg = read(RESPONSE / 'source-registration.json')
    eq('source code pin', sha(OWN / 'pdf_review_sources.py'), source_reg['code_sha256'])
    lex_reg = read(RESPONSE / 'lexical-registration.json')
    eq('lexical code pin', sha(OWN / 'pdf_review_lexical.py'), lex_reg['code_sha256'])
    eq('review matcher pin', sha(OWN / 'review-pdf/lexical_recheck.py'), lex_reg['reviewer_matcher_sha256'])
    eq('dictionary pin', sha(RAW / 'acquisition-2026-10-08-v1/mw.txt'), lex_reg['dictionary_sha256'])
    eq('external lexical mapping input', lex_reg['external_mapping_used'], False)
    lex = read(RESPONSE / 'lexical-corrections.json')
    power = lex['clear_origin_attainability']
    eq('clear-origin unattainable', power['can_reach_rejection_with_own_bundles'], False)
    eq('clear-origin ceiling', power['best_attainable_with_own_restricted_bundles'], 2)
    eq('clear-origin rejection score', power['minimum_rejection_score_at_05'], 3)
    eq('clear-origin histogram', power['permutation_histogram'], {'0': 60, '1': 36, '2': 18, '3': 6})
    held = lex['panels']['early_values_outside_derivation_labels']
    review_held = read(OWN / 'review-pdf/heldout-sensitivity.json')['early values incl. PU and PATI, exact bundles']['outside derivation objects']['exact']
    for key in ['observed', 'sequences', 'null_mean', 'tail', 'null_n']:
        eq('review partial split ' + key, held['exact'][key], review_held[key])
    eq('partial split labels', lex['partial_split']['derivation_labels'], 129)
    eq('partial split object closure', lex['panels']['early_values_outside_derivation_objects']['exact'], held['exact'])
    diagnostics = read(RESPONSE / 'source-diagnostics.json')
    eq('dictionary-derived dependence count', diagnostics['partial_split_hit_dependence']['requiring_PU_PATI_or_maha'], 5)
    original_rows = read(WORK / 'reading-inventory-v4.json')
    corrected_rows = read(LOCAL / 'reading-inventory-v5.json')
    eq('source row count preserved', len(corrected_rows), len(original_rows))
    eq('source row IDs preserved', [r['reading_id'] for r in corrected_rows], [r['reading_id'] for r in original_rows])
    original_byid = {r['reading_id']: r for r in original_rows}
    corrected_byid = {r['reading_id']: r for r in corrected_rows}
    independently_added = [r['reading_id'] for r in original_rows if r['is_reading_attempt']
        and not r['unclear_or_unattested_flag'] and re.search(r'doubtful|questionable|\?', r['source_text'], re.I)]
    correction = read(RESPONSE / 'reading-corrections.json')
    eq('independent uncertainty addition count', correction['attempts_newly_flagged'], len(independently_added))
    eq('uncertainty before/after', [correction['unclear_before'], correction['unclear_after']], [103, 160])
    eq('transcription before/after', [correction['transcriptions_before'], correction['transcriptions_after']], [718, 726])
    yes('R0146 caption recovered', corrected_byid['R0146']['proposed_reading'] == 'SA-DEVA')
    yes('R1097 alias transcription removed', corrected_byid['R1097']['proposed_reading'] is None)
    bad_codes = {'R1094', 'R1097', 'R1100', 'R1112'}
    yes('four alias-only captions removed', all(corrected_byid[r]['proposed_reading'] is None for r in bad_codes))
    for a, b in zip(original_rows, corrected_rows):
        if b['reading_id'] in independently_added:
            yes('new flag ' + b['reading_id'], b['unclear_or_unattested_flag'])
        eq('source drawing unchanged ' + b['reading_id'], b['sign_sequence_assumed_rtl'], a['sign_sequence_assumed_rtl'])
        eq('source join unchanged ' + b['reading_id'], b['joined_object_family_ids'], a['joined_object_family_ids'])
    joins = read(RESPONSE / 'join-corrections.json')
    eq('conservative join attempts', joins['excluding_four_probable_misjoined_objects']['attempts'], 707)
    eq('conservative join families', joins['excluding_four_probable_misjoined_objects']['families'], 334)
    eq('suspect reading count', len(joins['probable_misjoin_rows']), 6)
    deriv = {r['table18_entry']: r for r in read(RESPONSE / 'value-derivations-v3.json')['rows']}
    eq('derivation entries', len(deriv), 58)
    for entry in [29, 31, 50, 51, 52]:
        yes('restored origin ' + str(entry), deriv[entry]['dictionary_context_search_excluded_with_confidence'])
    for entry in [17, 48, 49]:
        eq('mixed derivation excluded ' + str(entry), deriv[entry]['dictionary_context_search_excluded_with_confidence'], False)
    eq('pala variants distinguished', deriv[17]['value_origins']['pAla'], 'dictionary search against contexts')
    current = [json.loads(line) for line in (OWN / 'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    old_ledger = [json.loads(line) for line in (HISTORY / 'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    eq('ledger IDs preserved', [r['id'] for r in current], [r['id'] for r in old_ledger])
    for a, b in zip(old_ledger, current):
        eq('quotation preserved ' + b['id'], b.get('quotation'), a.get('quotation'))
    byid = {r['id']: r for r in current}
    yes('letter page disambiguated', byid['Q053']['source_location'].startswith('Introductory letter'))
    yes('Q134 oval assumption corrected', 'nonrepeating units' not in byid['Q134']['paraphrase'].split('and F')[0])
    for name in ['REPORT.md', 'README.md']:
        text = (OWN / name).read_text(encoding='utf-8')
        eq('qualifier once ' + name, text.count('two AI coding rounds without specialist review'), 1)
        eq('uninformative interpretation corrected ' + name, 'no detectable excess' in text, False)
        eq('lexical mapping-survival wording removed ' + name, 'lexical excess also survives' in text, False)
    source = read(OWN / 'sources.json')
    yes('Language Log reader attribution', '7 March 2025' in next(r for r in source['sources'] if r['id'] == 'LL25')['claim_attribution'])
    yes('first Table exposure recorded', '17 caption forms' in source['independent_second_coding']['first_coder_exposure_note'])
    registry = read(OWN / 'registry-entry.json')
    eq('registry schema', sorted(registry), sorted(['id', 'theme', 'status', 'question', 'outcome', 'challenge', 'remedy', 'evidence', 'retry_when']))
    eq('registry interpretation', 'no clear-origin excess' in registry['outcome'], False)
    yes('registry spacing repaired', all(s not in registry['outcome'] for s in ['means55', 'lexical84', 'ICIT68first']))
    payload = {'status': 'Verified computation' if all(r['passed'] for r in checks) else 'Failed',
               'checks': len(checks), 'passed': sum(r['passed'] for r in checks),
               'protected_existing_files': protected, 'replay': replay.relative_to(ROOT).as_posix(),
               'results_status': 'Exploratory; source corrections and post-outcome sensitivities', 'records': checks}
    write(endpoint, payload)
    print({k: payload[k] for k in ['status', 'checks', 'passed', 'protected_existing_files']})
    for row in checks:
        if not row['passed']:
            print(row)
    if not all(r['passed'] for r in checks):
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--replay', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args(); main(args.replay, args.output)
