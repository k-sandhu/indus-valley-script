"""Review-response lexical power and derivation-object sensitivities.

Reuse the reviewer's independent matcher read-only. Manuscript role IDs and
value bundles are the inputs; external sign mappings are never read.
"""
import argparse, collections, copy, itertools, json, math, sys
from pathlib import Path
from pdf_followup import ROOT, OWN, RAW, WORK, OUT, read, write, sha

BASE = OWN / 'pdf-review-response-2026-10-09-v1'
LOCAL = RAW / BASE.name
sys.path.insert(0, str(OWN / 'review-pdf'))
import lexical_recheck as MATCH

ANCHORS = {6, 17, 18, 19, 29, 31, 36, 50, 51, 52}
NUMERAL_SENSITIVITY = ANCHORS | {12, 15}
EARLY = {5, 47, 6, 17, 18, 19, 36, 29, 50, 51, 52}
REVIEW_NO_DICT = EARLY - {5, 47}
FROZEN_CLEAR = {6, 17, 18, 19, 36, 48, 49}


def score(rows, roles, bundles, initial, local, name):
    population = [r for r in rows if set(r['roles']) <= roles]
    seqs = sorted({tuple(r['roles']) for r in population})
    result = {'occurrences': len(population), 'types': len(seqs), 'allowed_roles': sorted(roles)}
    predictions = {'rows': population, 'sequence_list': [list(s) for s in seqs], 'endpoints': {}}
    for endpoint in ['exact', 'normalized']:
        detail = MATCH.run(seqs, bundles, initial, endpoint, seed=1) if seqs else None
        predictions['endpoints'][endpoint] = detail
        result[endpoint] = ({k: v for k, v in detail.items() if k not in ['matched_sequences']} if detail else None)
    write(local / 'lexical-panels' / f'{name}.json', predictions)
    return result, predictions


def main(output=BASE, local=LOCAL):
    endpoint = output / 'lexical-corrections.json'
    if endpoint.exists():
        raise SystemExit('Lexical correction endpoint exists')
    selection = read(WORK / 'lexical-selection-v2.json')
    inventory = read(WORK / 'reading-inventory-v4.json')
    byid = {r['reading_id']: r for r in inventory}
    population = [r for r in selection['readings'] if r['basis'].startswith('explicit caption') and len(r['roles']) >= 2]
    bundles = {int(k): v for k, v in selection['table18_role_variants_slp1'].items()}
    initial = selection['initial_only_slp1']
    correction_bundles = {**bundles, 6: ['ma', 'mA'], 17: ['pala'], 29: ['mIna'], 31: ['caru']}
    review_clean_bundles = {**bundles, 6: ['ma', 'mA'], 17: ['pala', 'pAla']}
    derivation_labels = {r['primary_label'] for r in inventory if 39 <= r['source_page'] <= 77}
    # The closure uses literal same-manuscript labels and explicit CISI joins only.
    labelled_derivation_rows = [r for r in inventory if
        ({r['primary_label']} | set(r.get('mh_aliases', [])) | set(r.get('icit_aliases', []))) & derivation_labels]
    derivation_families = set().union(*(set(r['joined_object_family_ids']) for r in labelled_derivation_rows))
    label_outside = [r for r in population if r['primary_label'] not in derivation_labels]
    object_outside = [r for r in label_outside if not (
        set(byid[r['reading_id']]['joined_object_family_ids']) & derivation_families)]
    write(output / 'lexical-registration.json', {
        'protocol_sha256': sha(OWN / 'PROTOCOL.md'), 'code_sha256': sha(Path(__file__)),
        'reviewer_matcher_sha256': sha(OWN / 'review-pdf/lexical_recheck.py'),
        'selection_sha256': sha(WORK / 'lexical-selection-v2.json'),
        'inventory_sha256': sha(WORK / 'reading-inventory-v4.json'),
        'dictionary_sha256': sha(MATCH.MW), 'external_mapping_used': False,
        'anchor_roles': sorted(ANCHORS), 'numeral_sensitivity_roles': sorted(NUMERAL_SENSITIVITY),
        'anchor_bundle_restrictions': {str(k): correction_bundles[k] for k in [6, 17, 29, 31]}})
    panels = {}; raw_panels = {}
    configurations = [
        ('corrected_anchor_all', population, ANCHORS, correction_bundles),
        ('corrected_anchor_outside_derivation_labels', label_outside, ANCHORS, correction_bundles),
        ('corrected_anchor_outside_derivation_objects', object_outside, ANCHORS, correction_bundles),
        ('numeral_motivation_all', population, NUMERAL_SENSITIVITY, correction_bundles),
        ('numeral_motivation_outside_derivation_labels', label_outside, NUMERAL_SENSITIVITY, correction_bundles),
        ('early_values_all', population, EARLY, bundles),
        ('early_values_outside_derivation_labels', label_outside, EARLY, bundles),
        ('early_values_outside_derivation_objects', object_outside, EARLY, bundles),
        ('review_without_PU_PATI_maha_bala', label_outside, REVIEW_NO_DICT, review_clean_bundles)]
    for name, rows, allowed, values in configurations:
        panels[name], raw_panels[name] = score(rows, allowed, values, initial, local, name)
    # Attainability audit of the old panel: fixed own bundles block three ma- types.
    fixed = [r for r in population if set(r['roles']) <= FROZEN_CLEAR]
    own_bundles = {**bundles, 6: [v for v in bundles[6] if v not in ['maha', 'mahA']],
                   17: [v for v in bundles[17] if v != 'bala']}
    seqs = sorted({tuple(r['roles']) for r in fixed})
    matching = MATCH.run(seqs, own_bundles, initial, 'exact', seed=1)
    checks = []
    for sequence in seqs:
        options = [own_bundles[r] if pos == 0 else [v for v in own_bundles[r] if v not in initial.get(str(r), [])]
                   for pos, r in enumerate(sequence)]
        words = [''.join(c) for c in itertools.product(*options)]
        hits = [w for w in words if w in MATCH.HEADS]
        checks.append({'roles': list(sequence), 'own_bundle_matches': bool(hits), 'matches': hits,
                       'maha_reading_blocked': 6 in sequence and not hits})
    hist = {int(k): v for k, v in matching['null_histogram'].items()}
    attainable = sum(r['own_bundle_matches'] for r in checks)
    rejection_scores = [score for score in range(len(seqs) + 1)
                        if sum(n for k, n in hist.items() if k >= score) / matching['null_n'] <= .05]
    power = {'status': 'Exploratory', 'types': len(seqs), 'observed': matching['observed'],
             'best_attainable_with_own_restricted_bundles': attainable,
             'blocked_maha_types': sum(r['maha_reading_blocked'] for r in checks),
             'permutation_histogram': matching['null_histogram'], 'null_assignments': matching['null_n'],
             'exact_tail': matching['tail'], 'minimum_rejection_score_at_05': min(rejection_scores),
             'can_reach_rejection_with_own_bundles': attainable >= min(rejection_scores),
             'interpretation': 'The constructed panel cannot attain rejection; its two hits depend on dictionary-derived pāla, and one on reading-supported ASHVA.'}
    write(local / 'clear-origin-attainability.json', {'type_checks': checks, 'full_permutation_result': matching})
    hit_detail = raw_panels['early_values_outside_derivation_labels']['endpoints']['exact']['matched_sequences']
    dictionary_dependent_hits = sum(bool(set(s) & {5, 47, 6}) for s in hit_detail)
    assert dictionary_dependent_hits == len(hit_detail)
    write(local / 'derivation-split-membership.json', {
        'labels': sorted(derivation_labels), 'joined_families': sorted(derivation_families),
        'label_outside_reading_ids': [r['reading_id'] for r in label_outside],
        'object_outside_reading_ids': [r['reading_id'] for r in object_outside]})
    result = {'status': 'Exploratory; post-outcome source/provenance sensitivity',
              'external_mapping_used': False, 'agreed_only_effect': 'Target exclusions only; no alternate lexical values.',
              'clear_origin_attainability': power, 'panels': panels,
              'partial_split': {'derivation_labels': len(derivation_labels),
                               'counting_unit': 'Primary manuscript MH/ICIT labels on pp. 39–77, not deduplicated excavation objects.',
                               'explicitly_joined_derivation_families': len(derivation_families),
                               'outside_label_hit_types': len(hit_detail),
                               'hit_types_using_PU_PATI_or_maha': dictionary_dependent_hits,
                               'sealed_historical_batch_identified': False},
              'review_reused': ['review-pdf/lexical-recheck.json', 'review-pdf/heldout-sensitivity.json'],
              'independent_test_limit': 'No larger non-circular sealed test is reconstructible: later-extension discovery histories and reserved failures/examples are absent; early assignments followed repeated confirmation.',
              'dictionary_sha256': sha(MATCH.MW)}
    write(endpoint, result)
    print('Power', power)
    for name, panel in panels.items():
        r = panel['exact']; print(name, panel['occurrences'], panel['types'], None if r is None else (r['observed'], r['null_mean'], r['tail']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output-dir', default=BASE.name)
    args = parser.parse_args()
    output = (OWN / args.output_dir).resolve(); local = (RAW / args.output_dir).resolve()
    if not output.is_relative_to(OWN) or not local.is_relative_to(RAW):
        raise SystemExit('Output outside package')
    main(output, local)
