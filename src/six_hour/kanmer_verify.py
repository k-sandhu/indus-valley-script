"""Independently check frozen Kanmer counts, input preservation and report links."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/kanmer-physical-use'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = BASE / 'reviewed-verification/verification.json'
    if target.exists():
        raise RuntimeError('Preserve prior reviews.')
    target.parent.mkdir(exist_ok=True)
    checks = []
    def check(name, value, detail=None):
        checks.append({'name': name, 'passed': bool(value), 'detail': detail})
    results = json.loads((BASE / 'main/results.json').read_text(encoding='utf-8'))
    objects = json.loads((BASE / 'object-ledger.json').read_text(encoding='utf-8'))['objects']
    photo = json.loads((BASE / 'primary2023-first-observations.json').read_text(encoding='utf-8'))
    rev = [o for o in photo['observations'] if o['face'] == 'reverse']
    front = [o for o in photo['observations'] if o['face'] == 'obverse']
    check('independent_four_numbered_reverses', sorted(o['source_number'] for o in rev) == [1, 2, 3, 4])
    check('independent_four_visible_hole_mouths', len([o for o in rev if o['opening'] == 'clear']) == results['core_field_coverage']['visible_reverse_hole'])
    check('independent_four_front_views', len(front) == results['core_pendants'])
    check('photo_pixel_bounds', all(0 <= o['bbox'][0] < o['bbox'][2] <= 1801 and 0 <= o['bbox'][1] < o['bbox'][3] <= 1035 for o in photo['observations']))
    check('object_ids_unique', len({o['id'] for o in objects}) == 8)
    check('fourth_registration_missing', next(o for o in objects if o['id'] == 'SK2023-No4')['registration'] is None)
    check('fourth_outside_context_unassigned', next(o for o in objects if o['id'] == 'SK2023-No4')['context']['trench'] is None)
    check('direct_hole_measurements_zero', all(o['perforation']['individual_diameter_mm'] is None for o in objects))
    check('eight_object_seven_registered', sum(o['registration'] is not None for o in objects) == 7)
    original = {o['registration']: o for o in objects if o['frame_role'] == 'original-three-pendant'}
    values = {'08-1286': (34.1, 34.5, 16.1, 15.0), '09-900': (32.5, 35.3, 15.7, 15.0), '09-899': (33.2, 35.4, 16.6, 15.7)}
    for registration, dims in values.items():
        obj = original[registration]
        check('manually_reread_measurement_' + registration,
              tuple(obj['dimensions_mm'][f] for f in ('length', 'width', 'thickness')) + (obj['mass_g'],) == dims,
              'Source CH8 draft pages 4–5: cm converted to mm; source entries reread before this comparison.')
    widths = [34.5, 35.3, 35.4]
    mean = sum(widths) / 3
    variance = sum((v - mean) ** 2 for v in widths) / 3
    check('independent_width_cv_formula', abs(variance ** 0.5 / mean - results['nominal_core_dimensions_mm']['width']['population_cv']) < 1e-12)
    obs = json.loads((BASE / 'gis-first-observations.json').read_text(encoding='utf-8'))
    check('independent_25_displayed_scanner_regions', sum(len(o['regions']) for o in obs['views']) == 25 == results['scanner_display_views'])
    check('unique_scanner_caption_stems', len({o['caption'] for o in obs['views']}) == 7)
    for name, value in results['input_hashes'].items():
        check('frozen_input_' + name, sha(BASE / name) == value)
    ignored = (BASE / '.gitignore').read_text(encoding='utf-8').splitlines()
    for name in ('local-witness/', 'object-ledger.json', 'antiquity-first-observations.json', 'primary2023-first-observations.json', 'gis-first-observations.json'):
        check('local_only_' + name, name in ignored)
    broken = []
    for doc in BASE.glob('*.md'):
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if link.startswith(('http://', 'https://', '#')):
                continue
            path = link.split('#')[0]
            if not (doc.parent / path).resolve().exists():
                broken.append({'doc': doc.name, 'target': link})
    check('document_links_resolve_locally', not broken, broken)
    editor = json.loads((BASE / 'editorial-review.json').read_text(encoding='utf-8'))
    check('editorial_flags_reviewed_zero', len(editor['flags']) == 0)
    check('main_verification_129', json.loads((BASE / 'main/verification.json').read_text(encoding='utf-8'))['passed'] == 129)
    output = {'checks': len(checks), 'passed': sum(o['passed'] for o in checks),
              'failed': [o for o in checks if not o['passed']], 'details': checks,
              'code_sha256': sha(Path(__file__)),
              'scope': 'Independent observation counts, explicit source-value reread, alternate CV calculation, input hashes, local-only rules and local document navigation.'}
    target.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checks': output['checks'], 'passed': output['passed'], 'failed': output['failed']}, indent=2))


if __name__ == '__main__':
    main()
