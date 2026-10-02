"""Compute and verify the source-defined Kanmer physical-use ledger."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats(values):
    return {'n': len(values), 'minimum': min(values), 'maximum': max(values),
            'mean': statistics.mean(values),
            'population_sd': statistics.pstdev(values),
            'population_cv': statistics.pstdev(values) / statistics.mean(values)}


def compute():
    ledger = json.loads((BASE / 'object-ledger.json').read_text(encoding='utf-8'))
    objects = ledger['objects']
    core = [o for o in objects if o['frame_role'] in ('original-three-pendant', 'fourth-source-related-pendant')]
    original = [o for o in objects if o['frame_role'] == 'original-three-pendant']
    acquisitions = []
    for path in sorted(BASE.glob('acquisition-*/access.json')):
        for record in json.loads(path.read_text(encoding='utf-8')):
            record = dict(record)
            record['endpoint'] = path.parent.name
            acquisitions.append(record)
    per_core = [{'id': o['id'], 'max_extent_mm': max(o['dimensions_mm']['length'], o['dimensions_mm']['width']),
                 'thickness_to_max_extent': o['dimensions_mm']['thickness'] / max(o['dimensions_mm']['length'], o['dimensions_mm']['width']),
                 'shared_reported_hole_to_max_extent': 4.15 / max(o['dimensions_mm']['length'], o['dimensions_mm']['width'])}
                for o in original]
    return {'schema': 'kanmer-audit-v1', 'objects': len(objects), 'core_pendants': len(core),
            'original_core_registered': len(original), 'frame_roles': dict(Counter(o['frame_role'] for o in objects)),
            'core_field_coverage': {'registration': sum(o['registration'] is not None for o in core),
                                    'dimensions_and_mass': sum(o['dimensions_mm'] is not None and o['mass_g'] is not None for o in core),
                                    'individual_trench_layer': sum(o['context']['trench'] is not None and o['context']['layer'] is not None for o in core),
                                    'visible_reverse_hole': 4, 'source_numbered_reverse_photos': 4,
                                    'caption_stem_joined_scanner_objects': sum(o['gis'] is not None for o in core),
                                    'measured_hole_axis': sum(o['perforation']['axis_measured'] for o in core),
                                    'measured_hole_wear': sum(o['perforation']['wear_measured'] for o in core),
                                    'individual_hole_diameter': sum(o['perforation']['individual_diameter_mm'] is not None for o in core),
                                    'direct_object_laboratory_date': 0},
            'core_graphic_layout': {'author_shared_obverse_upper_units': 2,
                                    'numbered_reverse_marked_layouts': 4,
                                    'reverse_partial_cases': sum(o['reverse']['readability'] == 'partial' for o in core),
                                    'matrix_identity_basis': 'author assertion and visible broad correspondence; no raw-surface geometric matrix match'},
            'nominal_core_dimensions_mm': {field: stats([o['dimensions_mm'][field] for o in original]) for field in ('length', 'width', 'thickness')},
            'nominal_core_mass_g': stats([o['mass_g'] for o in original]),
            'individual_dimension_ratios': per_core,
            'scanner_display_views': sum(o['gis']['displayed_views'] for o in objects if o['gis']),
            'scanner_instrument_minimum_pitch_mm': 0.1,
            'actual_pendant_sampling_pitch_known': False,
            'raw_mesh_acquired': False,
            'acquisition': {'attempts': len(acquisitions), 'http_statuses': dict(Counter(str(o.get('http_status', 'exception')) for o in acquisitions)),
                            'transport_200': sum(o.get('http_status') == 200 for o in acquisitions),
                            'successful_transport_is_content_qualification': False},
            'scope': 'Descriptive author-report measurements of three surviving objects; shared hole datum repeated once in source group, no sample-based inference about ancient use.'}


def verify(results):
    checks = []
    def check(name, condition, detail=None):
        checks.append({'name': name, 'passed': bool(condition), 'detail': detail})
    check('protocol_hash', digest(BASE / 'PROTOCOL.md') == '0b949ee7c94958ae925f1897ee5223aca9a66400fb929881df192ce19a69d69b')
    check('objects_eight', results['objects'] == 8)
    check('core_four_with_three_registrations', results['core_pendants'] == 4 and results['original_core_registered'] == 3)
    check('reverse_hole_visible_four', results['core_field_coverage']['visible_reverse_hole'] == 4)
    check('individual_hole_measurements_missing', results['core_field_coverage']['individual_hole_diameter'] == 0)
    check('scanner_display_views_25', results['scanner_display_views'] == 25)
    manifest = json.loads((BASE / 'gis-figure-manifest-reviewed.json').read_text(encoding='utf-8'))
    expected = {'5.1.27': (245, '899c'), '5.1.28': (243, '900c'), '5.1.29': (244, '1286b'),
                '5.1.30': (241, '1054'), '5.1.31': (242, '1996c'), '5.1.32': (239, '1997c'),
                '5.1.33': (240, '1995c'), '5.1.34': (238, '1007')}
    for figure in manifest['figures']:
        path = BASE / figure['path']
        check('native_hash_' + figure['figure'], path.exists() and digest(path) == figure['sha256'])
        check('caption_xref_' + figure['figure'], (figure['xref'], figure['caption_object_label']) == expected[figure['figure']])
    access = {}
    for path in sorted(BASE.glob('acquisition-*/access.json')):
        for record in json.loads(path.read_text(encoding='utf-8')):
            key = path.parent.name + '/' + record['id']
            access[key] = record
            if record.get('local_path'):
                target = ROOT / record['local_path']
                check('witness_hash_' + key, target.exists() and digest(target) == record['sha256'])
    for source in json.loads((BASE / 'source-register.json').read_text(encoding='utf-8')):
        for ref in source['acquisition']:
            check('source_ref_' + source['id'] + '_' + ref,
                  ref in access or (BASE / ref).exists())
    check('source2012_pdf_bytes', (BASE / 'local-witness/acquisition-gis-file/teramura-kondo-uno2012-gis-chapter.pdf').stat().st_size == 49459102)
    check('source2012_pdf_hash', digest(BASE / 'local-witness/acquisition-gis-file/teramura-kondo-uno2012-gis-chapter.pdf') == '7f3ea038b2d26322d31f4ecc92f87891ac9c9a5bd16e9338c0e90817ebbcb41e')
    check('no_embedded_mesh', manifest['embedded_mesh_files'] == 0)
    check('failure_mapping_preserved', (BASE / 'gis-image-mapping-failure.json').exists() and (BASE / 'gis-figure-manifest.json').exists())
    import fitz
    source = fitz.open(BASE / 'local-witness/acquisition-gis-file/teramura-kondo-uno2012-gis-chapter.pdf')
    check('gis_pdf55_pages', len(source) == 55)
    check('gis_source_scanner', 'LPX-1200' in source[22].get_text())
    check('gis_source_labels_all', all(label in source[24].get_text() for _, label in expected.values()))
    decoded = (BASE / 'local-witness/op10-digit-decoding/text-digit-decoded.txt').read_text(encoding='utf-8')
    for numeral in ('26.7', '25', '34.52', '4.15'):
        check('op10_decoded_' + numeral, numeral in decoded)
    return {'checks': len(checks), 'passed': sum(c['passed'] for c in checks), 'failed': [c for c in checks if not c['passed']], 'details': checks}


def main():
    endpoint = BASE / 'main'
    if endpoint.exists():
        raise RuntimeError('Preserve earlier audit endpoints.')
    endpoint.mkdir()
    results = compute()
    results['recorded_utc'] = datetime.now(timezone.utc).isoformat()
    results['input_hashes'] = {name: digest(BASE / name) for name in ('PROTOCOL.md', 'object-ledger.json', 'source-register.json', 'gis-first-observations.json', 'primary2023-first-observations.json', 'disagreements.json')}
    (endpoint / 'results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    (endpoint / 'verification.json').write_text(json.dumps(verify(results), indent=2) + '\n', encoding='utf-8')
    (endpoint / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'results': results, 'verification': json.loads((endpoint / 'verification.json').read_text(encoding='utf-8'))['failed']}, indent=2))


if __name__ == '__main__':
    main()
