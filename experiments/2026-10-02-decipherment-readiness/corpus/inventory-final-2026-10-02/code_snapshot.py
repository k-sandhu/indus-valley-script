"""Read preserved corpus/source records and compute bounded readiness aggregates."""
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    output = BASE / 'inventory-final-2026-10-02'
    if output.exists():
        raise RuntimeError('Preserve preceding readiness endpoints.')
    output.mkdir()
    relative_inputs = [
        'knowledge/experiments/registry.json',
        'data/lipi/src/assets/data/inscriptions.csv',
        'data/lipi/src/assets/data/seal_id_and_image_mapping.json',
        'data/normalized/lipi_observed_faces.jsonl',
        'data/normalized/lipi_clean_rtl_singleline.jsonl',
        'data/normalized/mayig_faces.jsonl',
        'data/normalized/indus_website_observed.jsonl',
        'experiments/2026-10-02-six-hour/context-audit/main/results.json',
        'experiments/2026-10-02-six-hour/context-audit/source-cohorts/results.json',
        'experiments/2026-10-02-six-hour/harappa-object-frame/annotated/results.json',
        'experiments/2026-10-02-six-hour/harappa-object-frame/figure4-native-reinspection.json',
        'experiments/2026-10-02-six-hour/lothal-physical-use/join-refined/results.json',
        'experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json',
        'experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/selected-trace-observations.json',
        'experiments/2026-10-02-six-hour/kanmer-physical-use/main/results.json',
        'research/corpus/normalize_lipi.py', 'research/corpus/normalize_mayig.py', 'research/corpus/normalize_indus_website.py',
    ]
    input_hashes = {name: digest(ROOT / name) for name in relative_inputs}
    registry = read(ROOT / relative_inputs[0])
    ids = [r['id'] for r in registry['experiments']]
    write(output / 'coverage.json', dict(registry_path=relative_inputs[0], registry_sha256=input_hashes[relative_inputs[0]], registry_entries=len(ids), registry_ids_read=ids, direct_corpus_source_ids=[r['id'] for r in registry['experiments'] if r['id'].startswith(('ROOT-', 'ARCH-', 'GEOM-')) or r['theme'] == 'corpus'], mode='All entries parsed and reviewed for scope/status/evidence; direct record inspection concentrates on corpus and archaeological source frames.'))
    lipi = rows(ROOT / 'data/normalized/lipi_observed_faces.jsonl')
    clean = rows(ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl')
    mayig = rows(ROOT / 'data/normalized/mayig_faces.jsonl')
    older = rows(ROOT / 'data/normalized/indus_website_observed.jsonl')
    raw = list(csv.DictReader((ROOT / 'data/lipi/src/assets/data/inscriptions.csv').open(encoding='utf-8-sig', newline='')))
    semantic_presence = {key: dict(nonempty_strings=sum(bool((row.get(key) or '').strip()) for row in raw), absent_cells=sum(row.get(key) is None for row in raw), empty_strings=sum(row.get(key) == '' for row in raw), whitespace_only_strings=sum(row.get(key) is not None and row.get(key) != '' and not row[key].strip() for row in raw)) for key in ('sanskrit', 'translation', 'notes')}
    normalized_schema = {label: dict(rows=len(data), families=len({row['object_family_id'] for row in data}), top_level_keys=sorted(set().union(*(set(row) for row in data))), metadata_keys=sorted(set().union(*(set(row.get('metadata', {})) for row in data))), supplied_interpretive_keys_found=sorted({key for row in data for key in ('sanskrit', 'translation', 'notes', 'phonetic_value', 'personal_name', 'commodity_quantity') if key in row or key in row.get('metadata', {})})) for label, data in [('lipi', lipi), ('mayig', mayig), ('earlier_export', older)]}
    image_index = read(ROOT / 'data/lipi/src/assets/data/seal_id_and_image_mapping.json')
    directory = ROOT / 'data/lipi/public/seal_images'
    assets = sorted(p for p in directory.iterdir() if p.is_file())
    names = {p.name for p in assets}
    referenced = [name for values in image_index.values() for name in values]
    referenced_set = set(referenced)
    image_hashes = Counter(digest(path) for path in assets)
    source_keys = {row['source_cisi'] for row in lipi if row['source_cisi'] in image_index}
    mapped_rows = [row for row in lipi if row['source_cisi'] in image_index and any((directory / name).is_file() for name in image_index[row['source_cisi']])]
    image_summary = dict(asset_directory=directory.relative_to(ROOT).as_posix(), index_path='data/lipi/src/assets/data/seal_id_and_image_mapping.json', assets=len(assets), asset_extensions=dict(Counter(p.suffix.lower() for p in assets)), indexed_catalogue_keys=len(image_index), index_references=len(referenced), unique_indexed_files=len(referenced_set), missing_indexed_files=len(referenced_set - names), unindexed_assets=len(names - referenced_set), unique_asset_byte_hashes=len(image_hashes), duplicate_asset_byte_excess=sum(count-1 for count in image_hashes.values()), byte_duplicate_group_size_distribution=dict(Counter(count for count in image_hashes.values() if count > 1)), lipi_exact_key_matched_catalogue_keys=len(source_keys), lipi_rows_with_existing_indexed_asset=len(mapped_rows), lipi_families_with_existing_indexed_asset=len({row['object_family_id'] for row in mapped_rows}), principal_rows_with_existing_indexed_asset=sum(row['length'] >= 3 and row['clean_rtl_singleline'] for row in mapped_rows), mayig_faces_with_existing_indexed_asset=sum(row['object_family_id'] in image_index and any((directory / name).is_file() for name in image_index[row['object_family_id']]) for row in mayig), missingness_scope='Exact raw CISI key through the upstream image index; no fuzzy key or physical side/polarity match. Counts identify available assets and export links, not independent artifact photographs.', hash_scope='SHA-256 of every file in the asset directory; byte differences can still depict the same object/side.')
    context = read(ROOT / 'experiments/2026-10-02-six-hour/context-audit/main/results.json')
    availability = {key: dict(reported_rows=value['reported_rows'], families_any_value=value['families_any_value'], families_distinct_face_values=value['families_distinct_face_values'], row_statuses=value['row_statuses']) for key, value in context['field_availability'].items()}
    harp = read(ROOT / 'experiments/2026-10-02-six-hour/harappa-object-frame/annotated/results.json')
    harp_summary = {key: value for key, value in harp['summary'].items() if key not in ('target_objects_without_image_observation', 'reported_object_without_image')}
    native = read(ROOT / 'experiments/2026-10-02-six-hour/harappa-object-frame/figure4-native-reinspection.json')
    cohort_source = read(ROOT / 'experiments/2026-10-02-six-hour/context-audit/source-cohorts/results.json')
    # Keep counts, not raw catalogue strings, from the existing frozen cohorts.
    cohorts = []
    for name, row in cohort_source['cohorts'].items():
        cohorts.append(dict(cohort=name, **{key: value for key, value in row.items() if isinstance(value, (str, int, float, bool))}))
    lothal = read(ROOT / 'experiments/2026-10-02-six-hour/lothal-physical-use/join-refined/results.json')
    graphic = read(ROOT / 'experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json')
    traces = read(ROOT / 'experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/selected-trace-observations.json')
    trace_ids = {row['object_id'] for row in traces['observations'] if 'object_id' in row}
    groups = [dict(group_id=row['group_id'], objects=row['objects'], length=row['length'], source_categories=row['physical_types'], selected_trace_objects=sum(target in trace_ids for target in row['object_ids']), selected_trace_ids=[target for target in row['object_ids'] if target in trace_ids]) for row in graphic['groups']]
    kanmer = read(ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use/main/results.json')
    inventory = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), scope='Actual Indus corpus and source frames; generated mapping/numerical systems excluded from observation counts.', protocol_sha256=digest(BASE / 'PROTOCOL.md'), code_sha256=digest(Path(__file__)), input_hashes=input_hashes, corpus_schemas=normalized_schema, raw_interpretive_column_presence=semantic_presence, raw_schema_fields=list(raw[0]), export_image_index=image_summary, derivative_metadata_availability=availability, joint_metadata_availability=context['joint_availability'], metadata_evidence_basis=context['evidence_basis'], main_filter=dict(clean_rows=len(clean), principal_rows=sum(row['length'] >= 3 for row in clean), source_cohorts=cohorts), harappa=harp_summary, direct_tablet_stroke_counts=dict(faces=len(native['stroke_count_observations']), histogram=dict(Counter(row['separate_upright_strokes'] for row in native['stroke_count_observations'])), basis=native['basis'], source_geometry_convention=harp['summary']['display_convention']), lothal=dict(source_objects=lothal['objects'], table_impressions=lothal['source_impressions'], joined_objects=lothal['joined_objects'], joined_faces=lothal['joined_faces'], principal_objects=lothal['principal_objects'], distinct_principal_strings=graphic['distinct_complete_strings'], photographed_labelled_objects=traces['distinct_labelled_figure_objects'], selected_trace_objects=traces['selected_objects'], recurring_groups=groups, context_basis_record='experiments/2026-10-02-six-hour/lothal-physical-use/README.md'), kanmer={key:kanmer[key] for key in ('objects','core_pendants','original_core_registered','core_field_coverage','core_graphic_layout','raw_mesh_acquired')})
    checks = []

    def check(name, passed):
        checks.append(dict(check=name, passed=bool(passed)))

    check('registry IDs unique', len(ids) == len(set(ids)))
    check('Lipi source accounting', len(raw) == len(lipi) == 5680 and normalized_schema['lipi']['families'] == 4695)
    check('main filtered rows match frozen audit', len(clean) == 2930 and inventory['main_filter']['principal_rows'] == 2107)
    check('semantic columns omitted from analytical schemas', all(not row['supplied_interpretive_keys_found'] for row in normalized_schema.values()))
    check('raw semantic-column cell accounting', all(row['nonempty_strings'] + row['absent_cells'] + row['empty_strings'] + row['whitespace_only_strings'] == len(raw) for row in semantic_presence.values()))
    check('all image references resolve', image_summary['missing_indexed_files'] == 0)
    check('image hash accounting', image_summary['unique_asset_byte_hashes'] + image_summary['duplicate_asset_byte_excess'] == image_summary['assets'])
    check('seven direct stroke observations retained', inventory['direct_tablet_stroke_counts']['faces'] == 7 and inventory['direct_tablet_stroke_counts']['histogram'] == {3:5,4:2})
    check('Lothal recurrence accounting', len(groups) == 9 and sum(row['objects'] for row in groups) == 29)
    check('all frozen inputs preserved', all(digest(ROOT / name) == sha for name, sha in input_hashes.items()))
    write(output / 'evidence-inventory.json', inventory)
    write(output / 'verification.json', dict(checks_total=len(checks), checks_passed=sum(row['passed'] for row in checks), checks=checks))
    (output / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(checks=len(checks), passed=sum(row['passed'] for row in checks), registry_ids=len(ids), image_index=image_summary, semantic_column_presence=semantic_presence, trace_group_intersections=[(row['group_id'], row['selected_trace_ids']) for row in groups]), ensure_ascii=False))


if __name__ == '__main__':
    main()
