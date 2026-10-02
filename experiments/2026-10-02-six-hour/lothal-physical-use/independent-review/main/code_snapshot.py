"""Verify an independent table reading and the Lothal inscription groups.

Full table rows and inscription strings remain in the ignored local data tree.
The frozen endpoint contains aggregates, object identifiers and source hashes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/lothal-physical-use/independent-review'
LOCAL = ROOT / 'data/six-hour/lothal/independent-review'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    endpoint = BASE / 'main'
    details = LOCAL / 'comparison-and-joins'
    if endpoint.exists() or details.exists():
        raise RuntimeError('Preserve the existing run; select a new endpoint before rerunning.')

    first_path = LOCAL / 'independent-first-pass.csv'
    comparison_path = ROOT / 'data/six-hour/lothal/table-coding/reviewed-pass.csv'
    corpus_path = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
    source_path = ROOT / 'data/six-hour/lothal/frenez-tosi2005.pdf'
    with first_path.open(encoding='utf-8', newline='') as stream:
        first_rows = list(csv.DictReader(stream))
    with comparison_path.open(encoding='utf-8', newline='') as stream:
        other_rows = list(csv.DictReader(stream))
    objects = {row['source_cisi']: row for row in first_rows}
    other = {row['object_id']: row for row in other_rows}
    expected_ids = {f'L-{number}' for number in range(124, 217)}
    if len(first_rows) != 93 or len(objects) != 93 or set(objects) != expected_ids:
        raise ValueError('The independent frame must contain each L124–L216 object once.')
    if set(other) != expected_ids or len(other_rows) != 93:
        raise ValueError('The comparison frame differs from the source-defined frame.')

    field_pairs = [('impressions', 'impressions'), ('physical_type', 'physical_type'),
                   ('context', 'context_code'), ('pdf_page_one_based', 'pdf_page'),
                   ('printed_page', 'printed_page')]
    differences = []
    for object_id, row in objects.items():
        for own_field, other_field in field_pairs:
            if row[own_field] != other[object_id][other_field]:
                differences.append({'object_id': object_id, 'field': own_field,
                                    'independent_value': row[own_field],
                                    'comparison_value': other[object_id][other_field],
                                    'pdf_page_one_based': int(row['pdf_page_one_based']),
                                    'printed_page': int(row['printed_page']),
                                    'table_row': int(row['table_row'])})

    faces = defaultdict(list)
    family_sets = defaultdict(set)
    for line in corpus_path.open(encoding='utf-8'):
        face = json.loads(line)
        label = face['source_cisi']
        match = re.fullmatch(r'L-(\d+)(?:[A-Za-z].*|\..*)?', label)
        if not match:
            continue
        object_id = f'L-{int(match.group(1))}'
        if object_id in objects:
            faces[object_id].append(face)
            family_sets[object_id].add(face['object_family_id'])

    grouped = defaultdict(list)
    detailed_objects = []
    eligible_object_ids = set()
    for object_id, row in objects.items():
        observed = faces[object_id]
        eligible = [face for face in observed if face['clean_rtl_singleline'] and face['length'] >= 3]
        if eligible:
            eligible_object_ids.add(object_id)
        for face in eligible:
            grouped[tuple(face['signs_reading_rtl'])].append((object_id, face))
        detailed_objects.append({'source_table': row, 'observed_faces': observed,
                                 'eligible_face_ids': [face['record_id'] for face in eligible]})

    groups = []
    detailed_groups = []
    for index, (signs, members) in enumerate(sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])), 1):
        ids = sorted({object_id for object_id, _ in members})
        group = {'group_id': f'G{index:02d}', 'objects': len(ids), 'faces': len(members),
                 'object_ids': ids, 'length': len(signs),
                 'physical_types': dict(Counter(objects[key]['physical_type'] for key in ids)),
                 'context_codes': dict(Counter(objects[key]['context'] for key in ids)),
                 'motif_assertions': dict(Counter(face['symbol'] for _, face in members)),
                 'text_digest': hashlib.sha256('|'.join(signs).encode()).hexdigest()}
        groups.append(group)
        detailed_groups.append({**group, 'signs_reading_rtl': signs,
                                'eligible_record_ids': [face['record_id'] for _, face in members]})

    root_graphic_path = BASE.parent / 'graphic-coverage/results.json'
    root_join_path = BASE.parent / 'join-refined/results.json'
    root_graphic = json.loads(root_graphic_path.read_text(encoding='utf-8'))
    root_join = json.loads(root_join_path.read_text(encoding='utf-8'))
    counts = Counter(int(row['impressions']) for row in first_rows)
    aggregate = {'objects': len(objects), 'source_impressions': sum(k * v for k, v in counts.items()),
                 'impression_count_distribution': {str(k): v for k, v in sorted(counts.items())},
                 'context_counts': dict(Counter(row['context'] for row in first_rows)),
                 'physical_type_counts': dict(Counter(row['physical_type'] for row in first_rows)),
                 'joined_objects': len(faces), 'joined_faces': sum(map(len, faces.values())),
                 'principal_objects': len(eligible_object_ids),
                 'principal_faces': sum(group['faces'] for group in groups)}
    checks = []

    def check(name: str, passed: bool, value: object = None) -> None:
        checks.append({'check': name, 'passed': passed, 'value': value})

    check('all_93_source_objects_once', set(objects) == expected_ids and len(first_rows) == 93)
    check('all_465_compared_cells_agree', len(differences) == 0, {'cells': 93 * 5, 'differences': len(differences)})
    check('source_table_row_and_page_coordinates', all(
        int(row['pdf_page_one_based']) == (31 if number <= 170 else 32)
        and int(row['printed_page']) == (93 if number <= 170 else 94)
        and int(row['table_row']) == (number - 123 if number <= 170 else number - 170)
        for number in range(124, 217) for row in [objects[f'L-{number}']]))
    check('single_family_per_source_object', all(len(value) == 1 for value in family_sets.values()))
    check('one_eligible_face_per_eligible_object', aggregate['principal_faces'] == aggregate['principal_objects'])
    check('exact_group_membership_matches_root', groups == root_graphic['groups'])
    check('all_table_and_coverage_aggregates_match_root', all(root_join[key] == value for key, value in aggregate.items()))
    check('nine_groups_cover_29_eligible_objects', len(groups) == 9 and sum(group['objects'] for group in groups) == 29)
    check('largest_group_spans_seven_categories', groups[0]['objects'] == 11 and len(groups[0]['physical_types']) == 7)
    check('second_group_is_ten_elephant_wooden_box_objects', groups[1]['objects'] == 10
          and groups[1]['physical_types'] == {'wooden_box': 10}
          and groups[1]['motif_assertions'] == {'Elep': 10})
    expected_hashes = {'source_pdf': 'b0694314c9b91321dc85e90a9c66c1cf410fe46387efd0e2dffeb747fa7ddcd3',
                       'independent_first_pass': '21c4c72f56657b82670cefbb4668df280cbaada32027899799ff30accd9f3666',
                       'comparison_table': 'b2970efd5d21d633a20e7c0edf8e843304697b5dc0c2418a4ff8c3f7a6c03b38',
                       'corpus': '1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db'}
    paths = {'source_pdf': source_path, 'independent_first_pass': first_path,
             'comparison_table': comparison_path, 'corpus': corpus_path}
    inputs = {name: {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)} for name, path in paths.items()}
    for name, expected in expected_hashes.items():
        check(f'{name}_hash_preserved', inputs[name]['sha256'] == expected)

    result = {'status': 'independent-source-table-and-recurrence-review',
              'created_utc': datetime.now(timezone.utc).isoformat(),
              'independent_row_coding': 'Saved before reading the comparison CSV; aggregate targets were known.',
              'comparison': {'objects': 93, 'fields_per_object': 5, 'cells': 465,
                             'agreements': 465 - len(differences), 'disagreements': len(differences)},
              **aggregate, 'distinct_complete_strings': len(groups),
              'string_group_size_distribution': dict(Counter(group['objects'] for group in groups)),
              'top_two_objects': sum(group['objects'] for group in groups[:2]),
              'top_two_object_share': sum(group['objects'] for group in groups[:2]) / len(eligible_object_ids),
              'groups_spanning_physical_types': sum(len(group['physical_types']) > 1 for group in groups),
              'groups': groups, 'inputs': inputs,
              'root_endpoint_hashes': {'join_refined': digest(root_join_path), 'graphic_coverage': digest(root_graphic_path)},
              'protocol_sha256': digest(BASE / 'PROTOCOL.md'), 'code_sha256': digest(Path(__file__)),
              'verification': {'checks': len(checks), 'passed': sum(item['passed'] for item in checks),
                               'failed': sum(not item['passed'] for item in checks)}}
    endpoint.mkdir(parents=True)
    details.mkdir(parents=True)
    write_json(details / 'cell-disagreements.json', differences)
    write_json(details / 'object-joins.json', detailed_objects)
    write_json(details / 'graphic-groups.json', detailed_groups)
    write_json(endpoint / 'results.json', result)
    write_json(endpoint / 'verification.json', checks)
    (endpoint / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({key: value for key, value in result.items() if key not in ['groups', 'inputs', 'root_endpoint_hashes']}, indent=2))
    if result['verification']['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
