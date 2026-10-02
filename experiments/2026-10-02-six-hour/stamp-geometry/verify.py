"""Check contact-model artifacts and independently replay saved probabilities."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.six_hour import stamp_geometry as model
import numpy as np


def read(relative):
    return json.loads((BASE / relative).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(relative):
    with (BASE / relative).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def load_snapshot(relative):
    path = BASE / relative
    # Use the original location for dependency resolution; do not execute its CLI.
    namespace = {'__name__': 'snapshot_review', '__file__': str(ROOT / 'src/six_hour/stamp_geometry.py')}
    sys.modules['snapshot_review'] = type(sys)('snapshot_review')
    exec(compile(path.read_bytes(), str(path), 'exec'), namespace)
    return namespace


def main():
    checks = []

    def check(name, passed, detail=None):
        checks.append({'check': name, 'passed': bool(passed), 'detail': detail})

    main_result = read('main/results.json')
    analytic = read('analytic-refinement/results.json')
    reviewed = read('reviewed/results.json')
    check('frozen_initial_protocol_hash', digest(BASE / 'PROTOCOL.md') == main_result['protocol_sha256'])
    check('main_csv_preserved', digest(BASE / 'main/primary-configurations.csv') == analytic['main_csv_sha256'])
    for endpoint in ('main', 'sampling-refinement', 'length-selection', 'analytic-refinement'):
        result = read(endpoint + '/results.json')
        check(endpoint + '_code_snapshot_hash', digest(BASE / endpoint / 'code_snapshot.py') == result['code_sha256'])
    check('refinement_protocol_hash', digest(BASE / 'ANALYTIC-REFINEMENT.md') == analytic['refinement_protocol_sha256'])
    check('selection_protocol_hash', digest(BASE / 'LENGTH-SELECTION-PROTOCOL.md') == read('length-selection/results.json')['extension_protocol_sha256'])
    check('review_parent_hash', digest(BASE / 'analytic-refinement/results.json') == read('reviewed/record.json')['parent_results_sha256'])
    check('illustration_parent_hash', digest(BASE / 'reviewed/results.json') == read('illustrations/record.json')['parent_results_sha256'])
    check('illustration_code_hash', digest(BASE / 'illustrations/code_snapshot.py') == read('illustrations/record.json')['code_sha256'])

    for endpoint, filename, count in (('main', 'verification.json', 9),
                                    ('length-selection', 'selection-verification.json', 5),
                                    ('analytic-refinement', 'analytic-verification.json', 5)):
        saved = read(endpoint + '/' + filename)
        check(endpoint + '_saved_checks', len(saved) == count and all(row['passed'] for row in saved))
    frozen = load_snapshot('main/code_snapshot.py')
    independent = frozen['verify_model']()
    check('frozen_main_limiting_and_independent_checks_replay', len(independent) == 9 and all(row['passed'] for row in independent), independent)

    primary = rows('main/primary-configurations.csv')
    nuisance = rows('main/nuisance-configurations.csv')
    exact = rows('analytic-refinement/primary-configurations.csv')
    check('primary_configuration_count', len(primary) == 4320)
    check('nuisance_configuration_count', len(nuisance) == 8748)
    check('exact_configuration_count', len(exact) == 4320)
    check('nuisance_empty_count', sum(float(row['row_retention']) == 0 for row in nuisance) == 4086)
    check('nuisance_depth_retention_threshold_count', sum(float(row['depth']) * float(row['retention']) < 0.08 for row in nuisance) == 2916)
    check('profile_sensitivity_count', len(read('main/profile-sensitivity.json')) == 72 and main_result['profile_changed_visibility_comparisons'] == 14)
    changed_cells = sum(sum(a != b for a, b in zip(old['visibility_by_slot'], new['visibility_by_slot'])) for old, new in zip(primary, exact))
    changed_rows = sum(old['visibility_by_slot'] != new['visibility_by_slot'] for old, new in zip(primary, exact))
    check('exact_refinement_changes_preserved', changed_rows == 3 and changed_cells == 6, {'rows': changed_rows, 'cells': changed_cells})
    check('quadrature_changes_preserved', read('sampling-refinement/results.json')['changed_visibility_cells'] == 6)

    records = []
    max_probability_error = 0.0
    for row in exact:
        visible = np.asarray([[int(value) for value in slot] for slot in row['visibility_by_slot'].split('|')])
        expectation = model.selected_endpoint_expectations(visible, 1)
        for side in ('first', 'last'):
            stored = np.asarray([float(row[side + '_' + label]) for label in model.CLASSES])
            max_probability_error = max(max_probability_error, float(abs(stored - expectation[side]).max()))
        records.append({'geometry': {key: int(row[key]) if key == 'slots' else float(row[key]) for key in model.Geometry.__dataclass_fields__},
                        'imprint': {'damage': row['damage']}, 'visible': visible.tolist()})
    check('exact_csv_endpoint_probabilities_replay', max_probability_error < 1e-12, {'maximum_error': max_probability_error})
    spec = importlib.util.spec_from_file_location('review_statistics', BASE / 'reviewed/review_statistics.py')
    review_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(review_module)
    reproduced, changes = review_module.review(analytic)
    for key in ('parent_results_path', 'parent_results_sha256', 'reviewed_status'):
        reproduced[key] = reviewed[key]
    check('reviewed_statistics_reproduced', reproduced == reviewed and len(changes) == 2)
    replayed = dict(analytic)
    replayed['minimum_visible_graphics_pools'] = {str(minimum): model.selected_pools(records, minimum) for minimum in (1, 3)}
    replayed, _ = review_module.review(replayed)
    check('all_reviewed_pools_reproduced_from_exact_csv', replayed['minimum_visible_graphics_pools'] == reviewed['minimum_visible_graphics_pools'])
    groups = reviewed['minimum_visible_graphics_pools']['3']['8']
    check('selected_positive_tilt_endpoint_tv', abs(groups['positive_tilt_no_damage']['left_right_endpoint_tv'] - 0.03084657801) < 1e-10)
    check('selected_balanced_tilt_endpoint_tv', groups['balanced_tilt_no_damage']['left_right_endpoint_tv'] == 0)
    check('selected_balanced_break_sides_endpoint_tv', groups['balanced_tilt_both_break_sides']['left_right_endpoint_tv'] == 0)
    empty = reviewed['minimum_visible_graphics_pools']['3']['3']
    check('empty_pools_use_undefined_statistics', all(empty[name]['left_right_endpoint_tv'] is None and not empty[name]['endpoint_distribution_defined'] for name in ('balanced_tilt_left_break', 'balanced_tilt_both_break_sides')))

    for source in read('acquisition.json'):
        path = ROOT / source['local_path']
        check('local_source_' + path.name, path.exists() and digest(path) == source['sha256'])
    crop = read('H1714-crop-manifest.json')
    check('H1714_parent_image_hash', digest(ROOT / crop['parent_path']) == crop['parent_sha256'])
    check('H1714_crop_hash', digest(ROOT / crop['crop_path']) == crop['crop_sha256'])
    measurement = read('H1714-drawing-measurement.json')
    scale_pixels = measurement['crop_scale_x_endpoints'][1] - measurement['crop_scale_x_endpoints'][0]
    calculated = [value * measurement['scale_mm'] / scale_pixels for value in measurement['pixel_dimensions']]
    check('H1714_scale_calculation', np.allclose(calculated, measurement['estimated_face_dimensions_mm'], rtol=0, atol=1e-12))
    for filename in ('contact-and-visibility', 'synthetic-graphics-and-endpoints'):
        for suffix in ('png', 'svg'):
            path = BASE / 'illustrations' / (filename + '.' + suffix)
            check('illustration_' + filename + '_' + suffix, path.exists() and path.stat().st_size > 1000)

    broken = []
    pattern = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
    for path in BASE.glob('*.md'):
        for target in pattern.findall(path.read_text(encoding='utf-8')):
            if not target.startswith(('https://', 'http://', '#')) and not (path.parent / target.split('#')[0]).exists():
                broken.append({'file': path.name, 'target': target})
    check('documentation_local_links', not broken, broken)
    result = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'model snapshots, saved grid probabilities, post-outcome refinements, local source hashes and navigation',
              'checks': len(checks), 'passed': sum(row['passed'] for row in checks), 'details': checks}
    output = BASE / 'verification.json'
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checks': result['checks'], 'passed': result['passed'], 'failed': [row for row in checks if not row['passed']]}, indent=2))
    if result['checks'] != result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
