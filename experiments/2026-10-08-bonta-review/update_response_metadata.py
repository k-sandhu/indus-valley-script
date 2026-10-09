"""Rebuild response source/registry/completion metadata from the preserved baseline."""
from pathlib import Path
import json

OWN = Path(__file__).resolve().parent
BASE = OWN / 'history/2026-10-08-before-review-response'

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def write(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    sources = read(BASE / 'sources.json')
    ledger = [json.loads(l) for l in (OWN / 'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    for source in sources['sources']:
        quotes = [r for r in ledger if r['source_id'] == source['id'] and r['quotation']]
        source['short_quotation'] = quotes[0]['quotation'] if quotes else None
        if quotes:
            source['quotation_location'] = quotes[0]['source_location']
        if source['id'] == 'K24':
            source.update({'opened': False, 'year': None, 'reported_year_unverified': 2024,
                'venue': 'Requested author-posted item; date and substantive content unverified',
                'access': 'Direct request returned HTTP 403. Previous claim of opened substantive text is withdrawn; requested bibliographic identification and search snippets are insufficient to describe its position.',
                'location': 'Requested Academia identifier 113408961; no verified substantive passage',
                'verification_status': 'Unverified', 'short_quotation': None})
        elif source['id'] == 'K03':
            source.update({'print_year': 2003, 'online_publication_year': 2009,
                'location': 'Chapter 6 summary: noun-headed compounds with noun/adjective/verb modifier; no quantitative productivity estimate in the opened summary'})
        elif source['id'] == 'B-letter':
            source['access'] = 'Opened PDF text including page 5 and rendered pages 1–4; pages 2 and 4 preserve six provisional graphic roles'
        elif source['id'] == 'B10':
            source['response_recheck'] = 'The previous public-page identification is retained. No full early witness is available locally; response chronology uses the 2024 author retrospective, segment 3.'
    sources['policy'] = 'Downloaded payloads, lexical/per-object outputs and long excerpts remain local. Seven source-checked quotations, each at most 15 words, preserve consequential wording; all other claim descriptions are project paraphrases.'
    sources['review_response'] = {'date': '2026-10-08', 'review': 'REVIEW.md',
        'source_audit': 'claim-source-audit-2026-10-08-v2.json',
        'corrections': ['K24 substantive interpretation withdrawn after HTTP 403', 'Krishnamurti print/online dates distinguished',
                       'Letter and categorical-caption quotations source-checked']}
    write(OWN / 'sources.json', sources)

    registry = read(BASE / 'registry-entry.json')
    registry['outcome'] = (
        'On 2469 selected objects jar 740 is final 838/1196 (70.07%) with 358 non-final tokens (29.93%), '
        '241 followed by 400/090; arrow 520 is final 192/225 (85.33%) with 33 non-final (14.67%). '
        'Strong final tendencies reproduce; categorical sequence-final use fails, with T-field boundaries unresolved. '
        'Exploratory fish adjacency is 135 pairs against shuffle mean 54.5505, 95% range 44–65, 2000 draws; '
        'zero repeats/maximum-three runs are withdrawn as structural support. The selected lexical panel gives 9/10 exact matches. '
        'Global normalization is broader than Table 18 role lists. All 13 normalized assignments reaching at least 9 keep PU; '
        'none of the 600 moving it reaches 9. Eight of ten strings contain PU or PATI, which he derived by searching this dictionary '
        'against those same contexts, so the 13/720 tail is close to circular for these signs. Holding PU/PATI fixed gives '
        'normalized 8/24 and exact 2/24 tails; dropping their eight strings leaves 2/2, with tails 8/24 and 4/24. '
        'The corrected source-history audit has three repeated objects, zero conflicting labels among six candidates and three '
        'parser false overlaps: only ICIT3656 is an ICIT-first reading, ICIT3084 is an MH-first alias and ICIT2816 an iconography remark. '
        'Eight same-entry MH references remain, one uncertain. Validation membership, attempt/failure denominators and full field '
        'boundaries remain unknown; physical quantity joins are zero. All 126 original ledger rows were checked, including 74 '
        'outside the review sample, all 74 of which changed, mainly table/evidence clarifications; four additions give 130 rows. Kalyanaraman substantive content is unverified after HTTP 403.')
    registry['challenge'] = ('Dictionary-derived roles and development-selected examples make the original lexical tail dependent on construction. '
        'Full manuscript figures, a complete historical ICIT attempt list, fine sign/field mappings and physical quantity joins are missing. '
        'Parser excerpts can attach adjacent aliases incorrectly. Machine captions remain unchecked against audio; Kalyanaraman access failed HTTP 403.')
    registry['remedy'] = ('Preserved frozen runs, protocol/selection hashes, original audit and reviewer files; registered Exploratory response sensitivities; '
        'held dictionary-derived roles fixed and removed their strings; counted terminal exceptions and fish adjacency; issued a dated selection erratum '
        'and source-qualified validation successor; checked all existing ledger rows and recorded every change; corrected source access and evidence ranking.')
    registry['evidence'] = [
        'experiments/2026-10-08-bonta-review/' + p for p in [
            'REPORT.md', 'PROTOCOL.md', 'PROTOCOL-registered.md', 'REVIEW.md',
            'run-2026-10-08-v1/distributions.json', 'run-2026-10-08-v1/lexical.json',
            'response-2026-10-08-v2/lexical-sensitivities.json', 'response-2026-10-08-v2/terminal-exceptions.json',
            'response-2026-10-08-v2/fish-adjacency.json', 'response-2026-10-08-v2/validation-audit-v2.json',
            'response-2026-10-08-v2/selection-errata.json', 'review/role-pair-census.json',
            'claims.jsonl', 'claim-source-audit-2026-10-08-v2.json', 'ledger-coverage.json', 'sources.json',
            'response-checks-2026-10-08-v4.json']]
    registry['retry_when'] = ('Obtain full manuscript figures, source-qualified fine identities/field boundaries, the historical ICIT attempted/rejected '
        'list and values fixed before consultation, or independent inscription-to-quantity joins. Use externally reserved objects and finite acceptance '
        'rules for a lexical test that models value/panel selection. Complete the full reading inventory and edition collation when witnesses are available.')
    write(OWN / 'registry-entry.json', registry)

    completion = read(BASE / 'completion.json')
    completion['package_verification'] = {'scope': 'Historical initial package checks; current response checked separately',
                                         **completion['package_verification']}
    completion['main_outputs'].update({'claim_records': 130, 'confirmed_ICIT_first_reading_entries': 1,
        'confirmed_MH_first_alias_entries': 1, 'confirmed_iconography_mentions': 1, 'conflicting_overlap_labels': 0,
        'parser_false_overlaps': 3, 'jar_nonfinal': 358, 'arrow_nonfinal': 33, 'fish_adjacent_pairs': 135,
        'fish_shuffle_mean': 54.5505, 'fish_max_repeat_structural_interpretation': 'Withdrawn',
        'lexical_dictionary_derived_role_strings': 8, 'lexical_PU_fixed_all_high_normalized_assignments': 13,
        'lexical_PU_moved_high_assignments': '0/600', 'lexical_PU_PATI_fixed_normalized_tail': '8/24',
        'lexical_PU_PATI_fixed_exact_tail': '2/24', 'lexical_dropped_PU_PATI_strings_normalized_tail': '8/24',
        'lexical_dropped_PU_PATI_strings_exact_tail': '4/24'})
    completion['review_response'] = {'date': '2026-10-08', 'status': 'Exploratory',
        'checks': 'response-checks-2026-10-08-v4.json', 'ledger_original_rows_checked': 126,
        'outside_sample_rows_checked': 74, 'outside_sample_rows_changed': 74,
        'frozen_outputs_and_review_preserved': True}
    completion['preservation'] = 'Original numerical runs, registered protocol, selection, code, Failed verifier output and reviewer files retained; pre-response annotations snapshotted. Shared registry, indexes and first-pass directory unchanged.'
    completion['reviewer_instructions'] = 'Repeat README response commands and source samples; verify PU/PATI conditioning, non-final exceptions, adjacency, entry types, short quotations and protected hashes.'
    write(OWN / 'completion.json', completion)

if __name__ == '__main__':
    main()
