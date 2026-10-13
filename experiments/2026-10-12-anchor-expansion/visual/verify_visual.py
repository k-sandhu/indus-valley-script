"""Independently check inventory, image provenance and corrected dispositions."""
from pathlib import Path
from collections import Counter
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = HERE / 'verification.json'
    if output.exists():
        raise FileExistsError(output)
    checks = []

    def check(name, condition, detail=None):
        checks.append(dict(name=name, pass_check=bool(condition), detail=detail))

    inventory = read(HERE.parent / 'candidate-starting-pool.json')['rows']
    by_code = {row['code']: row for row in inventory}
    families = read(HERE / 'families.json')
    freeze = read(HERE / 'freeze-manifest.json')
    images = read(HERE / 'image-review-manifest.json')
    paired = read(HERE / 'crosswalk-image-review-manifest.json')
    crosswalk = read(HERE / 'chart-crosswalk-audit.json')
    supplement = read(HERE / 'integration-supplement-v1.json')

    check('713 unique starting codes', len(inventory) == len(by_code) == 713)
    check('Starting inventory hash', sha(HERE.parent / 'candidate-starting-pool.json') == freeze['input_sha256'])
    for row in freeze['outputs']:
        check('Frozen output hash: ' + row['path'], sha(ROOT / row['path']) == row['sha256'])
    check('Corrected integration leaves the original family map unchanged', supplement['family_map_sha256'] == sha(HERE / 'families.json'))
    check('Membership and roles remain frozen', supplement['membership_and_roles_unchanged'] is True)

    assigned = [code for row in families['rows'] for code in row['codes']]
    check('One primary family for each assigned code', len(assigned) == len(set(assigned)) == 673)
    check('Seventy unique primary families', len({row['family_id'] for row in families['rows']}) == len(families['rows']) == 70)
    check('Assigned and unresolved form the full inventory', set(assigned).isdisjoint(families['uncovered_codes']) and set(assigned) | set(families['uncovered_codes']) == set(by_code))
    check('Forty explicitly unresolved codes', len(families['uncovered_codes']) == 40)
    actual_layers = dict(Counter(by_code[code]['tier_before'] for code in assigned))
    check('Coverage and inherited layers counted independently', actual_layers == families['counts']['assigned_prior_layers'] and actual_layers['unreviewed'] == 533)
    valid_roles = {'closing', 'counted_entity', 'nonfinal_entity', 'internal_connector', 'opening', 'unconstrained'}
    check('Every role is one declared scalar prediction', all(row['role_predictions'] in valid_roles for row in families['rows']))
    check('Every family retains an observation, meaning and rival', all(row['picture_observation'] and row['working_meaning'] and row['graphic_rivals'] for row in families['rows']))

    exact = images['exact_font']
    check('Font witness hash', sha(ROOT / exact['font_path']) == exact['font_sha256'])
    seen_codes = [code for sheet in exact['rows'] for code in sheet['codes']]
    check('Fifteen seen sheets cover every code once', len(exact['rows']) == 15 and len(seen_codes) == len(set(seen_codes)) == 713 and set(seen_codes) == set(by_code) and all(sheet['seen'] for sheet in exact['rows']))
    for sheet in exact['rows']:
        check('Exact sheet hash: ' + sheet['path'], sha(ROOT / sheet['path']) == sheet['sha256'])
    check('Exact sheets remain in the ignored local companion', all(sheet['path'].startswith('data/raw/2026-10-12-anchor-expansion/visual/') for sheet in exact['rows']))
    for sheet in images['licensed_class_sheets']['rows']:
        check('Initial licensed representative sheet hash: ' + sheet['path'], sha(ROOT / sheet['path']) == sheet['sha256'] and sheet['seen'])

    mapped = {row['code'] for row in inventory if row['drawings']}
    paired_codes = [witness['code'] for sheet in paired['rows'] for witness in sheet['witnesses']]
    check('Fourteen paired sheets cover all 498 mapped codes', len(paired['rows']) == 14 and len(paired_codes) == len(set(paired_codes)) == 498 and set(paired_codes) == mapped)
    for sheet in paired['rows']:
        check('Paired sheet hash: ' + sheet['path'], sha(ROOT / sheet['path']) == sheet['sha256'] and sheet['seen'])
        for witness in sheet['witnesses']:
            if sha(ROOT / witness['source']) != witness['source_sha256']:
                check('Class parent source hash: ' + witness['source'], False)
    dispositions = {row['code']: row for row in supplement['glyph_dispositions']}
    check('Every paired code has one public-chart disposition', len(dispositions) == len(supplement['glyph_dispositions']) == 498 and set(dispositions) == mapped)
    suppressed = sorted([code for code, row in dispositions.items() if row['suppress_public_glyph']], key=int)
    check('Eleven public exact-glyph suppressions', suppressed == crosswalk['suppressed_codes'] and len(suppressed) == 11)
    check('W353 and W940 initial suppression flags withdrawn', all(not dispositions[code]['suppress_public_glyph'] for code in ['353', '940']) and supplement['withdrawn_initial_suppression_codes'] == ['353', '940'])
    check('W354 carries the corrected class mismatch', dispositions['354']['suppress_public_glyph'])
    check('W700 is corrected to one U-shaped outline', supplement['withdrawn_initial_ambiguity_codes'] == ['700'] and 'one U-shaped' in dispositions['700']['observation'])
    mixed = next(row for row in supplement['family_corrections'] if row['family_id'] == 'enclosed_fish_group')
    check('Bounded creature picture retains the arthropod rival', 'arthropod' in mixed['picture_observation'] and 'mixed-creature' in mixed['working_meaning'])
    check('No chart class is promoted to exact identity', all(not row['exact_identity_confirmed'] for row in crosswalk['rows']))
    check('Image corrections did not use new contextual outcomes', supplement['new_context_outputs_read'] is False)
    public_files = [path for path in HERE.iterdir() if path.is_file()]
    check('Public visual directory excludes font and image payloads', all(path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.ttf', '.woff', '.woff2', '.pdf'} for path in public_files))
    summary = dict(status='pass' if all(row['pass_check'] for row in checks) else 'fail',
                   checks=len(checks), failures=sum(not row['pass_check'] for row in checks),
                   families=70, assigned_codes=673, newly_reviewed_codes=533,
                   exact_code_images_seen=713, mapped_code_pairs_seen=498,
                   public_glyph_suppressions=11, rows=checks)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key != 'rows'}))
    if summary['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
