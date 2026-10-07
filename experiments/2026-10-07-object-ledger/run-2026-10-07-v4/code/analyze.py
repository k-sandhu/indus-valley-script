"""Measure same-carrier coverage, join dispositions, source differences and lookup cost."""
import argparse
import collections
import json
import statistics
from pathlib import Path
from common import OWN, RAW, ROOT, PATHS, coarse, digest, fresh, missing, write
from validate import validate

FIELDS = ['catalogue_identifier', 'excavation_identifier', 'field_identifier', 'museum_accession', 'site', 'region', 'object_type', 'material', 'holding', 'area', 'room_grid', 'stratum_phase', 'period_label', 'calendar_interval', 'dating_basis', 'dating_sample', 'excavation_unit', 'excavation_item', 'measurement', 'image_pointer', 'rights_pointer']

def analyze(ledger, selection, comparisons, lookups):
    errors = validate(ledger)
    if errors:
        raise ValueError('Invalid ledger: ' + '; '.join(errors[:5]))
    objects = {o['id']: o for o in ledger['objects']}
    chosen = {o['object_id']: o for o in selection['objects']}
    matched = {o['object_id'] for o in selection['objects'] if o['family'] is not None}
    have = collections.defaultdict(set)
    baseline = collections.defaultdict(set)
    grouped = collections.defaultdict(list)
    for a in ledger['assertions']:
        if a['confidence'] == 'candidate':
            continue
        have[a['field']].add(a['object_id'])
        if a['source_id'] == 'lipi':
            baseline[a['field']].add(a['object_id'])
        grouped[(a['object_id'], a['field'])].append(a)
    completeness = []
    for f in FIELDS:
        completeness.append({'field': f, 'pilot_denominator': 200, 'corpus_present_on_pilot': len(baseline[f]), 'ledger_present_on_pilot': len(have[f]), 'gain_on_pilot': len(have[f]) - len(baseline[f]), 'matched_denominator': len(matched), 'corpus_present_on_matched': len(baseline[f] & matched), 'ledger_present_on_matched': len(have[f] & matched), 'gain_on_matched': len((have[f] - baseline[f]) & matched), 'catalogue_only_present': len(have[f] - matched), 'definition': 'at least one nonplaceholder noncandidate source-located assertion; image pointers include unverified catalogue section pointers'})

    rels = ledger['relationships']
    museum_confirmed = [r for r in rels if r['status'] == 'confirmed' and r['source_id'].startswith('museum-')]
    candidate = [r for r in rels if r['status'] == 'candidate']
    jsummary = {'confirmed_relationships': len([r for r in rels if r['status'] == 'confirmed']), 'confirmed_relationships_by_method': dict(collections.Counter(r['method'] for r in rels if r['status'] == 'confirmed')), 'confirmed_museum_records': len(museum_confirmed), 'confirmed_museum_objects': len({r['object_id'] for r in museum_confirmed}), 'candidate_relationships': len(candidate), 'candidate_museum_records': len({r['external_record'] for r in candidate}), 'candidate_objects': len({r['object_id'] for r in candidate}), 'candidate_rule': 'site and coarse carrier type; at most five selected carriers; no merges or metadata transfers', 'candidate_review_scope': 'search buckets, not identity evidence', 'museum_field_adjudications': sum(p['adjudication'] is not None for p in comparisons), 'museum_unadjudicated_pairs': sum(p['adjudication'] is None for p in comparisons), 'independent_expert_reviewed_joins': 0}

    museum_fields = ['site_comparison', 'type_comparison', 'material_comparison', 'dimensions_comparison', 'inscription_comparison']
    inherited = {f: dict(collections.Counter(p['adjudication'][f] for p in comparisons if p['adjudication'] is not None)) for f in museum_fields}
    distinct = []
    for (oid, field), assertions in grouped.items():
        if field not in {'site', 'region', 'object_type', 'material', 'period_label', 'excavation_identifier', 'area', 'room_grid', 'stratum_phase', 'calendar_interval', 'impression_count'}:
            continue
        vals = {json.dumps(a['value'], sort_keys=True, ensure_ascii=True) for a in assertions}
        if len(vals) > 1:
            normalized = {coarse(a['value']) for a in assertions} if field == 'object_type' else None
            classification = 'same_coarse_type_different_source_labels' if normalized and len(normalized) == 1 else 'distinct_attributed_values_requiring_field_specific_review'
            distinct.append({'object_id': oid, 'field': field, 'values': [json.loads(v) for v in sorted(vals)], 'assertion_ids': [a['id'] for a in assertions], 'classification': classification, 'source_count': len({a['source_id'] for a in assertions})})
    differences = {'museum_adjudication_denominator': jsummary['museum_field_adjudications'], 'museum_inherited_categories': inherited, 'museum_unadjudicated_pairs': jsummary['museum_unadjudicated_pairs'], 'distinct_assertion_groups_by_field': dict(collections.Counter(d['field'] for d in distinct)), 'distinct_assertion_groups': distinct, 'definition': 'Distinct values can be compatible specificity, material terminology or different depositional/source labels. Only the inherited museum categories assert adjudicated disagreement.'}

    counts = [r['lookup_count'] for r in lookups]
    cost = {'definition': 'unique source file and recorded input-record locator used per carrier, including source-specific rights rule rows; generated assertions are not separate lookups', 'objects': len(counts), 'total_lookups': sum(counts), 'mean_per_object': statistics.mean(counts), 'median_per_object': statistics.median(counts), 'minimum_per_object': min(counts), 'maximum_per_object': max(counts), 'distribution': dict(sorted(collections.Counter(counts).items())), 'new_primary_pages_read_for_population': 0, 'human_minutes_per_object': None, 'human_minutes_missing_reason': 'automated_reuse; no_timed_human_source_review'}

    queue = []
    def q(oid, reason, role, field, question, evidence):
        queue.append({'id': f'Q-{len(queue) + 1:05d}', 'object_id': oid, 'catalogue_key': chosen[oid]['key'], 'reason': reason, 'reviewer_role': role, 'field': field, 'question': question, 'evidence': evidence})
    contexts = {c['object_id']: c for c in ledger['contexts']}
    for oid, r in chosen.items():
        if r['family'] is None:
            q(oid, 'catalogue_only', 'epigrapher and catalogue specialist', 'identity_and_inscription_eligibility', f'Does {r["key"]} show an Indus inscription, and which catalogue views belong to this carrier? Explain its absent export key.', PATHS['lothal'] + '#object_id=' + r['key'] + ';' + PATHS['absent'])
        elif r['catalogue_key'] is None:
            q(oid, 'export_only_identity', 'archaeologist or curator', 'published_identifier', f'Which registered or published object is pinned Lipi family {r["family"]} at {r["site"]}? Supply its concordance and carrier boundary.', PATHS['lipi'] + '#object_family_id=' + r['family'])
        if r['primary_selection'] == 'Harappa_22_tablets':
            q(oid, 'face_alignment', 'epigrapher', 'surfaces', f'For {r["key"]}, how do Figure 4 top/middle/bottom faces align to the three export records? Use the corrected author/PDF pagination.', PATHS['harappa'] + '#target_id=' + r['key'])
        ctx = contexts[oid]['fields']
        if ctx['context_code']['value'] == 'W1':
            q(oid, 'stamp_based_context', 'archaeologist', 'context_code', f'Is {r["key"]} independently documented in the warehouse, or does its W1 assignment rely on a repeated stamp?', PATHS['lothal'] + '#object_id=' + r['key'] + ';Frenez-Tosi2005-pp70-71')
        if r['primary_selection'] == 'Harappa_3A':
            q(oid, 'one_3A_record', 'archaeologist', 'period_label', f'What primary context supports the sole selected Period 3A label for {r["key"]}? Check residuality and the excavation registration before chronological use.', PATHS['lipi'] + '#object_family_id=' + r['family'])
        if r['key'] == 'BM-123208':
            q(oid, 'findspot_production_roles', 'curator and archaeologist', 'findspot_site', 'Does the export family carrying BM-123208 match Gadd no.16 and the museum object? Confirm Ur as findspot and retain Dilmun as an attributed production label.', PATHS['corrections'] + '#id=B3-V6-050;' + PATHS['external'] + '#site=Dilmun')
    for r in candidate:
        q(r['object_id'], 'candidate_museum_join', 'curator or catalogue specialist', 'museum_accession', f'Can {r["external_record"]} be joined to {chosen[r["object_id"]]["key"]} by an accession/excavation concordance? Shared site and type currently define only a search bucket.', r['assertion_id'])
    for p in comparisons:
        if p['adjudication'] is None:
            q(p['object_id'], 'unadjudicated_museum_pair', 'curator', 'source_comparison', f'Compare site, material, dimensions and sign-count fields for {p["museum_key"]}; the v6 identity supplement did not adjudicate these fields.', p['evidence'])
            continue
        for field, value in p['adjudication'].items():
            if isinstance(value, str) and value in {'disagreement', 'outside_tolerance', 'count_disagreement'}:
                q(p['object_id'], 'museum_field_disagreement', 'curator or epigrapher', field, f'Resolve the inherited {value} in {field} for {p["museum_key"]}; check original labelled axes and source count conventions before choosing a value.', p['evidence'])
    for d in distinct:
        if d['field'] in {'calendar_interval', 'period_label'}:
            q(d['object_id'], 'dating_assertions', 'archaeologist', d['field'], f'Do the attributed {d["field"]} values for {chosen[d["object_id"]]["key"]} describe compatible date scopes or conflicting deposits?', ';'.join(d['assertion_ids']))
        elif d['field'] == 'impression_count':
            q(d['object_id'], 'impression_count_conflict', 'archaeologist or epigrapher', d['field'], f'How many impressions belong to {chosen[d["object_id"]]["key"]}? Reconcile the table and prose counts against the complete carrier and its published views.', ';'.join(d['assertion_ids']))

    image_types = collections.Counter(v['kind'] for v in ledger['images'])
    summary = {'status': 'Verified computation', 'annotation_status': 'Exploratory; no independent expert review', 'objects': 200, 'corpus_matched_objects': len(matched), 'catalogue_only_objects': 200 - len(matched), 'regions': dict(collections.Counter(r['region'] for r in chosen.values())), 'sites': dict(collections.Counter(r['site'] for r in chosen.values())), 'site_count': len({r['site'] for r in chosen.values()}), 'coarse_object_types': dict(collections.Counter(r['type'] for r in chosen.values())), 'length_bins': dict(collections.Counter(r['length_bin'] for r in chosen.values())), 'damage_status': dict(collections.Counter(str(r['damaged']) for r in chosen.values())), 'multi_face_objects_from_corpus': sum(r['multi_face'] is True for r in chosen.values()), 'normalized_lipi_faces': sum(t['source_id'] == 'lipi' for t in ledger['transcriptions']), 'mayig_transcriptions': sum(t['source_id'] == 'mayig' for t in ledger['transcriptions']), 'transcriptions': len(ledger['transcriptions']), 'source_specific_surfaces': len(ledger['surfaces']), 'image_pointers_by_kind': dict(image_types), 'new_image_inspections': 0, 'independent_dating_sample_links': len(have['dating_sample']), 'assertions': len(ledger['assertions']), 'measurement_assertions': len(ledger['measurements']), 'asset_rights_records': len(ledger['rights']), 'sources': len(ledger['sources']), 'correction_overlays': len(ledger['correction_overlays']), 'review_questions': len(queue), 'review_objects': len({q['object_id'] for q in queue}), 'primary_selection': selection['primary_counts'], 'joins': jsummary, 'source_lookup_cost': cost}
    return summary, completeness, differences, queue

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger-dir', required=True)
    ap.add_argument('--selection', required=True)
    ap.add_argument('--output-dir', required=True)
    a = ap.parse_args()
    d = Path(a.ledger_dir)
    load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    ledger, selection = load(d / 'ledger-public.json'), load(a.selection)
    summary, completeness, differences, queue = analyze(ledger, selection, load(d / 'museum-comparisons.json'), load(d / 'source-lookups.json'))
    out = fresh(a.output_dir, OWN)
    write(out / 'summary.json', summary)
    write(out / 'completeness.json', completeness)
    write(out / 'join-report.json', summary['joins'])
    write(out / 'disagreements.json', differences)
    write(out / 'review-queue.json', queue)
    write(out / 'analysis-manifest.json', {'ledger_sha256': digest(d / 'ledger-public.json'), 'selection_sha256': digest(a.selection), 'code_sha256': digest(__file__), 'input_hashes': {p.name: digest(p) for p in d.glob('*.json')}})
    import csv
    with (out / 'completeness.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(completeness[0]))
        w.writeheader(); w.writerows(completeness)
    print(json.dumps(summary, ensure_ascii=True))

if __name__ == '__main__':
    main()
