"""Descriptive source-count and value-dependence checks registered in PR-R/PR-H."""
import json, itertools, re, sys
from pdf_followup import OWN, RAW, WORK, read, write, sha
sys.path.insert(0, str(OWN / 'review-pdf'))
import lexical_recheck as L

OUT = OWN / 'pdf-review-response-2026-10-09-v1'
LOCAL = RAW / OUT.name


def main():
    endpoint = OUT / 'source-diagnostics.json'
    if endpoint.exists():
        raise SystemExit('Diagnostic endpoint exists')
    inv = read(WORK / 'reading-inventory-v4.json')
    attempts = [r for r in inv if r['is_reading_attempt']]
    matched = [r for r in attempts if re.search(r'doubtful|questionable|\?', r.get('source_text', ''), re.I)]
    newly = [r for r in matched if not r['unclear_or_unattested_flag']]
    kw = {'fields_searched': ['source_text'], 'case_insensitive_pattern': r'doubtful|questionable|\?',
          'attempt_rows_searched': len(attempts), 'matching_attempts': len(matched),
          'newly_flagged_attempts': len(newly), 'review_report_matching_attempts': 94,
          'review_report_newly_unflagged': 60,
          'reconciliation': 'The review’s 94/60 does not reproduce on the retained row-local source_text fields. The registered correction flags 57 new attempts; direct row inspection is reproducible.'}
    selection = read(WORK / 'lexical-selection-v2.json')
    bundles = {int(k): v for k, v in selection['table18_role_variants_slp1'].items()}
    initial = selection['initial_only_slp1']
    scored = read(LOCAL / 'lexical-panels/early_values_outside_derivation_labels.json')
    details = []
    for seq in scored['endpoints']['exact']['matched_sequences']:
        opts = [bundles[r] if i == 0 else [v for v in bundles[r] if v not in initial.get(str(r), [])]
                for i, r in enumerate(seq)]
        combinations = [list(c) for c in itertools.product(*opts) if ''.join(c) in L.HEADS]
        independent = [c for c in combinations if not any(
            role in {5, 47} or (role == 6 and value in {'maha', 'mahA'})
            for role, value in zip(seq, c))]
        details.append({'roles': seq, 'matching_combinations': combinations,
                        'matching_combination_without_PU_PATI_or_maha': bool(independent)})
    dependence = {'exact_hit_types': len(details),
                  'requiring_PU_PATI_or_maha': sum(not r['matching_combination_without_PU_PATI_or_maha'] for r in details)}
    assert dependence['requiring_PU_PATI_or_maha'] == 5
    write(LOCAL / 'source-diagnostic-rows.json', {
        'keyword_match_reading_ids': [r['reading_id'] for r in matched],
        'newly_flagged_reading_ids': [r['reading_id'] for r in newly],
        'hit_dependence': details})
    write(endpoint, {'status': 'Exploratory', 'uncertainty_flag_reconciliation': kw,
                     'partial_split_hit_dependence': dependence,
                     'code_sha256': sha(__import__('pathlib').Path(__file__))})
    print(kw); print(dependence)


if __name__ == '__main__':
    main()
