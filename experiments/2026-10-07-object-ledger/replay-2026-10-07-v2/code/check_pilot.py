"""Independent source recounts, frozen-input checks and negative validator/import tests."""
import argparse
import collections
import copy
import gzip
import json
from pathlib import Path
from common import OWN, RAW, ROOT, PATHS, cisi, digest, fresh, read, write
from validate import validate, sequence_errors
from import_helsinki1979 import import_rows, EDITION, LICENSE

def checks(ledger_dir, analysis_dir, raw_dir, selection_path):
    load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    ledger = load(ledger_dir / 'ledger-public.json')
    selection = load(selection_path)
    summary = load(analysis_dir / 'summary.json')
    comp = {r['field']: r for r in load(analysis_dir / 'completeness.json')}
    results = []
    def check(name, ok, detail=None):
        results.append({'check': name, 'passed': bool(ok), 'detail': detail})
    check('public_schema_and_relations', not validate(ledger))
    for path, meta in selection['input_manifest'].items():
        check('input_hash:' + path, digest(ROOT / path) == meta['sha256'])
    check('protocol_preserved', digest(OWN / 'PROTOCOL.md') == selection['protocol_sha256'])
    check('exact_200_unique_carriers', len({o['id'] for o in ledger['objects']}) == len(ledger['objects']) == 200)
    check('selected_id_order', [o['id'] for o in ledger['objects']] == [o['object_id'] for o in selection['objects']])
    lookup = {o['object_id']: o for o in selection['objects']}
    families = {o['family'] for o in selection['objects'] if o['family'] is not None}
    corpus = read(PATHS['lipi'])
    faces = [f for f in corpus if f['object_family_id'] in families]
    check('independent_lipi_face_count', len(faces) == summary['normalized_lipi_faces'], len(faces))
    check('independent_matched_carriers', len(families) == summary['corpus_matched_objects'] == 180)
    check('all_22_short_tablets', {f'H-{n}' for n in range(2218, 2240)}.issubset({o['key'] for o in selection['objects']}))
    absent_keys = {cisi(k) for row in read(PATHS['absent']) if row['edition'].startswith('CISI1') for k in row['absent_base_identifiers']}
    cat = [o for o in selection['objects'] if o['family'] is None]
    check('20_absent_CISI1_keys', len(cat) == 20 and all(o['key'] in absent_keys for o in cat))
    check('no_selected_H356_duplicate_caption', 'H-356' not in {o['key'] for o in cat})
    check('external_four_groups', all(sum(o['region'] == r for o in selection['objects']) >= n for r, n in [('Persian Gulf', 5), ('Mesopotamia', 5), ('Iranian Plateau', 5), ('Central Asia', 3)]))
    # Independently compute raw export completeness. Empty and zero dimensions
    # are handled here rather than by the builder's assertion extraction.
    def present(v):
        return v is not None and str(v).strip().casefold() not in {'', '-', '--', '- -', 'none', 'unknown', 'others', '?'}
    mapping = {'catalogue_identifier': 'cisi', 'excavation_identifier': 'excavation-idno', 'site': 'site', 'region': 'region', 'object_type': 'type', 'material': 'material', 'area': 'area-section', 'room_grid': 'room-grid', 'period_label': 'time'}
    for field, src in mapping.items():
        count = len({f['object_family_id'] for f in faces if present(f['metadata'].get(src))})
        check('baseline_completeness:' + field, count == comp[field]['corpus_present_on_pilot'], count)
    phase = len({f['object_family_id'] for f in faces if present(f['metadata'].get('phase')) or present(f['metadata'].get('period'))})
    check('baseline_completeness:stratum_phase', phase == comp['stratum_phase']['corpus_present_on_pilot'], phase)
    dims = set()
    for f in faces:
        for k in ['horizontal(mm)', 'vertical(mm)', 'thickness(mm)']:
            try:
                if float(f['metadata'].get(k, 0)) > 0:
                    dims.add(f['object_family_id'])
            except (ValueError, TypeError):
                pass
    check('baseline_measurement_completeness', len(dims) == comp['measurement']['corpus_present_on_pilot'], len(dims))
    for field in ['museum_accession', 'calendar_interval', 'dating_sample', 'image_pointer', 'rights_pointer']:
        check('structural_export_absence:' + field, comp[field]['corpus_present_on_pilot'] == 0)
    accepted = [a for a in ledger['assertions'] if a['confidence'] != 'candidate']
    for field, row in comp.items():
        n = len({a['object_id'] for a in accepted if a['field'] == field})
        check('ledger_completeness:' + field, n == row['ledger_present_on_pilot'], n)
    joins = [j for j in read(PATHS['joins']) if j['family'] in families]
    check('museum_join_recount', len(joins) == summary['joins']['confirmed_museum_records'] == 26)
    check('at_least_20_museum_joins', len(joins) >= 20)
    for a in accepted:
        if a['field'] == 'field_identifier':
            check('field_identifier_alias:' + a['object_id'], any(i['object_id'] == a['object_id'] and i['value'] == a['value'] and i['status'] == 'confirmed' and i['assertion_id'] == a['id'] for i in ledger['identifiers']))
    candidates = [r for r in ledger['relationships'] if r['status'] == 'candidate']
    check('candidate_aliases_separate', len([i for i in ledger['identifiers'] if i['status'] == 'candidate']) == len(candidates) and all(any(i['status'] == 'candidate' and i['object_id'] == r['object_id'] and i['assertion_id'] == r['assertion_id'] for i in ledger['identifiers']) for r in candidates))
    tables = read(PATHS['lothal'])
    contexts = {c['object_id']: c['fields'] for c in ledger['contexts']}
    for oid, s in lookup.items():
        row = next((l for l in tables if l['object_id'] == s['key']), None)
        if row:
            check('Lothal_table:' + s['key'], contexts[oid]['impression_count']['value'] == int(row['impressions']) and (contexts[oid]['context_code']['value'] == row['context_code'] or row['context_code'] == '?'))
    sample_links = [a for a in accepted if a['field'] == 'dating_sample']
    check('no_period_mapping_as_sample_link', not sample_links)
    check('HARP_mapping_only_Harappa', all(lookup[a['object_id']]['site'] == 'Harappa' for a in accepted if a['source_id'] == 'harappa2010'))
    check('candidate_links_not_accepted_fields', all(a['confidence'] != 'candidate' for o in ledger['objects'] + ledger['contexts'] for v in o['fields'].values() for aid in v['assertion_ids'] for a in ledger['assertions'] if a['id'] == aid))

    costs = load(ledger_dir / 'source-lookups.json')
    expected = collections.defaultdict(set)
    for a in ledger['assertions']:
        expected[a['object_id']].add((a['locator']['path'], a['locator']['record']))
    check('source_lookup_recount', all(r['lookup_count'] == len(expected[r['object_id']]) for r in costs))
    check('source_lookup_total', sum(map(len, expected.values())) == summary['source_lookup_cost']['total_lookups'])
    manifest = load(ledger_dir / 'build-manifest.json')
    with gzip.open(ROOT / manifest['local_full_register'], 'rt', encoding='utf-8') as f:
        full = json.load(f)
    check('raw_public_layer_exact', full['public_layer'] == ledger)
    check('raw_transcription_payload_count', len(full['local_transcription_payloads']) == len(ledger['transcriptions']))
    check('raw_sequence_presence', any(r['source_record'].get('signs_visual_ltr') for r in full['local_transcription_payloads']))
    check('public_sequence_absence', not sequence_errors(ledger))

    def mutation(name, fn):
        altered = copy.deepcopy(ledger)
        fn(altered)
        check('negative_validator:' + name, bool(validate(altered)))
    mutation('broken_object_key', lambda d: d['contexts'][0].update(object_id='NONEXISTENT'))
    mutation('negative_measurement', lambda d: d['measurements'][0].update(value=-1))
    mutation('nonfinite_measurement', lambda d: d['measurements'][0].update(value=float('inf')))
    mutation('wrong_dimension_unit', lambda d: d['measurements'][0].update(unit='kg'))
    mutation('rights_asset_mismatch', lambda d: d['rights'][0].update(asset_ref='NO-ASSET'))
    mutation('missing_reason', lambda d: d['objects'][0]['fields']['authenticity'].update(missing_reason=None))
    mutation('restricted_payload_key', lambda d: d['objects'][0].update(signs_reading_rtl=['SIM-A']))
    mutation('glyph_payload_key', lambda d: d['objects'][0].update(glyph_tokens=['SIM-A']))
    def cross_object(d):
        other = next(a for a in d['assertions'] if a['object_id'] != d['objects'][0]['id'] and a['field'] == 'material')
        d['objects'][0]['fields']['material'] = {'value': other['value'], 'assertion_ids': [other['id']], 'missing_reason': None}
    mutation('cross_object_cell_provenance', cross_object)
    def reverse(d):
        a = next(a for a in d['assertions'] if a['field'] == 'calendar_interval')
        a['value'] = {'bce_oldest': 1, 'bce_youngest': 2}
    mutation('reversed_BCE_interval', reverse)

    # Entire fixture ledger is invented. It contains no real pilot object or text number.
    simulated_ledger = {'objects': [{'id': 'SIM-OBJECT'}], 'identifiers': [{'status': 'confirmed', 'scheme': 'SIM-CATALOGUE', 'value': 'SIM-ALIAS', 'object_id': 'SIM-OBJECT'}], 'surfaces': [{'id': 'SIM-SURFACE', 'object_id': 'SIM-OBJECT'}]}
    row = {'synthetic': True, 'edition_id': EDITION, 'text_number': '999999', 'inventory': 'SIMULATED', 'inventory_version': 'fixture-v1', 'source_page': 1, 'glyph_tokens': ['SIM-A', 'SIM-B'], 'auxiliary_markers': [{'synthetic': True, 'position': 1, 'kind': 'uncertainty'}], 'order': 'synthetic visual order', 'boundary_status': 'synthetic single surface', 'rights': {'license': LICENSE, 'source_url': 'http://hdl.handle.net/10138/342677', 'attribution': 'Synthetic interface fixture; no source transcription', 'modifications': 'Invented symbols for software checks'}, 'digitization_version': 'synthetic-fixture-v1', 'review_status': 'synthetic_only'}
    cross = {'edition_id': EDITION, 'text_number': '999999', 'concordance_source': 'SIM-CONCORDANCE', 'concordance_page': 'SIM-PAGE-1', 'source_access': 'opened_primary_concordance', 'target_identifier': {'scheme': 'SIM-CATALOGUE', 'value': 'SIM-ALIAS'}, 'surface_id': 'SIM-SURFACE', 'surface_review_status': 'reviewed_source_surface_alignment', 'relation': 'same_physical_object', 'status': 'confirmed', 'review_status': 'reviewed_object_identity'}
    good, bad = import_rows([row], [cross], simulated_ledger, allow_synthetic=True)
    check('synthetic_import_preserves_payload', len(good) == 1 and not bad and good[0]['status'] == 'Synthetic' and good[0]['auxiliary_markers'] == row['auxiliary_markers'])
    _, bad = import_rows([row], [cross], simulated_ledger)
    check('production_rejects_synthetic_fixture', bool(bad))
    for name, change in [('candidate', {'status': 'candidate'}), ('unopened', {'source_access': 'snippet_only'}), ('duplicate_text_relation', {'relation': 'same_text'}), ('unknown_surface', {'surface_id': 'NO-SURFACE'}), ('unknown_target', {'target_identifier': {'scheme': 'CISI', 'value': '999999'}})]:
        trial = dict(cross, **change)
        good, bad = import_rows([row], [trial], simulated_ledger, allow_synthetic=True)
        check('negative_import:' + name, not good and len(bad) == 1)
    good, bad = import_rows([row], [cross, cross], simulated_ledger, allow_synthetic=True)
    check('negative_import:concordance_collision', not good and len(bad) == 1)
    wrong_license = copy.deepcopy(row); wrong_license['rights']['license'] = 'unverified'
    good, bad = import_rows([wrong_license], [cross], simulated_ledger, allow_synthetic=True)
    check('negative_import:unlicensed_payload', not good and len(bad) == 1)
    write(raw_dir / 'synthetic-interface-fixtures.json', {'status': 'Synthetic', 'rows': [row], 'crosswalk': [cross], 'ledger': simulated_ledger})
    # The archaeological builder must reject even interface-accepted fixtures.
    good, _ = import_rows([row], [cross], simulated_ledger, allow_synthetic=True)
    write(raw_dir / 'synthetic-accepted-layer.json', good)
    from build import Builder
    try:
        Builder.__new__(Builder).attach_helsinki_layer(raw_dir / 'synthetic-accepted-layer.json')
        blocked = False
    except ValueError as exc:
        blocked = 'Synthetic fixtures' in str(exc)
    check('builder_rejects_synthetic_layer', blocked)
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger-dir', required=True)
    ap.add_argument('--analysis-dir', required=True)
    ap.add_argument('--selection', required=True)
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--raw-dir', required=True)
    a = ap.parse_args()
    out, raw = fresh(a.output_dir, OWN), fresh(a.raw_dir, RAW)
    r = checks(Path(a.ledger_dir), Path(a.analysis_dir), raw, Path(a.selection))
    result = {'status': 'Verified computation' if all(x['passed'] for x in r) else 'Failed', 'checks': len(r), 'passed': sum(x['passed'] for x in r), 'failed': sum(not x['passed'] for x in r), 'results': r}
    write(out / 'checks.json', result)
    print({k: v for k, v in result.items() if k != 'results'})
    if result['failed']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
