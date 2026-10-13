"""Freeze the reviewed family map and distinguish exact and class witnesses."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    spec = importlib.util.spec_from_file_location('definition_ledger', HERE / 'build_family_ledger.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prior = read(HERE.parent / 'candidate-starting-pool.json')['rows']
    by_code = {row['code']: row for row in prior}
    exact_sheets = read(HERE / 'sheet-manifest-initial.json')
    class_sheets = read(HERE / 'licensed-sheet-manifest-initial.json')
    code_sheet = {code: row['path'] for row in exact_sheets['rows'] for code in row['codes']}
    seen_class = {rep['family_id']: dict(rep, contact_sheet=row['path'])
                  for row in class_sheets['rows'] for rep in row['representatives']}
    staff_source = 'output/chart_atlas/cells/p20_c1_r18.png'
    seen_class['staff_bearer'] = dict(family_id='staff_bearer', code='142', source=staff_source,
                                     source_sha256=sha(ROOT / staff_source), graphic_class='P031',
                                     contact_sheet=None)
    conflicts = [
        dict(code='850', family_id='diamond_enclosure',
             font_observation='A plain closed diamond formed by four angled sides.',
             mapped_class_observation='P355 is a plain closed oval with no diamond corners.',
             path='output/chart_atlas/cells/p21_c7_r13.png',
             disposition='Suppress as this code\'s public glyph. It may be shown separately as the conflicting mapped class.',
             suppress_public_glyph=True),
        dict(code='930', family_id='arch_canopy',
             font_observation='A peaked covering over a divided arched lower frame with two short lower marks.',
             mapped_class_observation='P339 is a radial divided oval on several short lower strokes.',
             path='output/chart_atlas/cells/p21_c6_r24.png',
             disposition='Suppress as this code\'s public glyph; keep the class conflict discoverable.',
             suppress_public_glyph=True),
        dict(code='940', family_id='enclosed_fish_group',
             font_observation='Two oval-and-tail fish-like bodies lie between curved side boundaries.',
             mapped_class_observation='P054 has one fish-like body beside a multi-appendage arthropod-like body between curves.',
             path='output/chart_atlas/cells/p20_c2_r22.png',
             disposition='Suppress as an exact two-fish illustration; the mapped class is a mixed-creature witness.',
             suppress_public_glyph=True),
        dict(code='353', family_id='rail_tally',
             font_observation='Parallel uprights cross a straight rail; lower ends remain separate strokes.',
             mapped_class_observation='P091 has upper prongs and a single joined U-shaped lower loop.',
             path='output/chart_atlas/cells/p20_c4_r0.png',
             disposition='Suppress as this code\'s exact glyph; retain the shared prong/rail comparison separately.',
             suppress_public_glyph=True),
        dict(code='309', family_id='many_legged_outline',
             font_observation='A rounded upper loop joins several spreading lower strokes and two small side hooks.',
             mapped_class_observation='P206 is mostly parallel bent strips with a rounded side attachment.',
             path='output/chart_atlas/cells/p20_c8_r8.png',
             disposition='Suppress as an exact-code illustration because the rounded part and bent-strip arrangement differ.',
             suppress_public_glyph=True),
    ]
    # Use the actual source pointers for each declared conflict; the observation
    # was made from that source cell in the licensed contact sheet.
    for conflict in conflicts:
        conflict['path'] = by_code[conflict['code']]['drawings'][0]['path']
        conflict['source_sha256'] = sha(ROOT / conflict['path'])
    source_ambiguities = [
        dict(code='272', family_id='multi_appendage_creature',
             font_observation='Segmented central form with forked lower/left strokes and two rounded right-side extensions.',
             mapped_class_observation='P070 has a segmented body, several lateral strokes and a long upward curved tail-like appendage.',
             path=by_code['272']['drawings'][0]['path'],
             implication='Insect/scorpion is a direct rival to the earlier bird/messenger wording; no precise species is selected.',
             suppress_public_glyph=False),
        dict(code='700', family_id='cup_vessels',
             font_observation='The local font repeats the U-shaped vessel outline.',
             mapped_class_observation='P310 depicts a single U-shaped outline.',
             path=by_code['700']['drawings'][0]['path'],
             implication='The shared cup class illustrates shape only; it cannot show exact repetition count.',
             suppress_public_glyph=False),
    ]
    conflict_by_code = {row['code']: row for row in conflicts}
    rows, assignments = [], {}
    for family_id, code_string, observation, meaning, words, role, rivals in module.DEFINITIONS:
        codes = code_string.split()
        for code in codes:
            if code not in by_code or code in assignments:
                raise ValueError((family_id, code, assignments.get(code)))
            assignments[code] = family_id
        representative = seen_class.get(family_id)
        seen = sorted({code_sheet[code] for code in codes})
        if representative:
            seen.append(representative['contact_sheet'] or representative['source'])
        source_drawings = sorted({drawing['path'] for code in codes for drawing in by_code[code]['drawings']})
        confidence = 'The declared common component was seen in every listed exact-code font witness. Material meanings and positional roles are candidate tests.'
        if representative:
            if representative['code'] in conflict_by_code:
                confidence += ' The representative mapped chart class conflicts with the exact-font outline; it is not an exact-code illustration.'
            else:
                confidence += f" A licensed class witness at W{representative['code']} supplies a shared-component comparison, with the recorded variant limitations."
        rows.append(dict(family_id=family_id, codes=codes, picture_observation=observation,
                         working_meaning=meaning, Sanskrit_comparison_words=words.split(),
                         role_predictions=role, graphic_rivals=[rivals],
                         source_drawing_paths=source_drawings, visual_support='private-font-only',
                         seen_images=seen, confidence_reason=confidence,
                         licensed_representative_seen=representative,
                         prior_layer={code: by_code[code]['tier_before'] for code in codes},
                         code_source_support={code: dict(exact_witness=code_sheet[code],
                             exact_witness_kind='Lipi font; local-only drawing, not source artifact photograph',
                             class_images=by_code[code]['drawings'],
                             public_glyph_suppressed=code in conflict_by_code,
                             class_identity_limit='The chart pointer represents a graphic class. Exact Wells variant strokes, repetition and segmentation are separate observations.')
                             for code in codes}))
    uncovered = sorted(set(by_code) - set(assignments), key=int)
    freeze_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    counts = dict(families=len(rows), assigned_codes=len(assignments), uncovered_codes=len(uncovered),
                  new_unreviewed_codes=sum(by_code[code]['tier_before'] == 'unreviewed' for code in assignments),
                  assigned_prior_layers=dict(Counter(by_code[code]['tier_before'] for code in assignments)))
    write(HERE / 'families.json', dict(date='2026-10-12', frozen_at_utc=freeze_time,
          construction='Image-derived primary family map frozen before any new complete-context result tables were read. Earlier project outcomes were exposed.',
          scope='One primary family per assigned code. Membership records a shared visual component and a working semantic comparison. It does not assign distinct meanings to every qualifier or replace the inherited layer.',
          counts=counts, rows=rows, uncovered_codes=uncovered, chart_conflicts=conflicts,
          source_ambiguities=source_ambiguities))
    for row in exact_sheets['rows']:
        row['seen'] = True
        row['seen_by'] = 'Codex visual-language image inspection, 2026-10-12'
        if sha(ROOT / row['path']) != row['sha256']:
            raise ValueError(row['path'])
    for row in class_sheets['rows']:
        row['seen'] = True
        row['seen_by'] = 'Codex visual-language image inspection, 2026-10-12'
        if sha(ROOT / row['path']) != row['sha256']:
            raise ValueError(row['path'])
    write(HERE / 'image-review-manifest.json', dict(date='2026-10-12', frozen_at_utc=freeze_time,
          exact_font=exact_sheets, licensed_class_sheets=class_sheets,
          separately_seen_cells=[dict(path=staff_source, sha256=sha(ROOT / staff_source)),
                                 dict(path=by_code['272']['drawings'][0]['path'], sha256=sha(ROOT / by_code['272']['drawings'][0]['path']))],
          source_attribution='Koskenniemi and Parpola, Corpus of Texts in the Indus Script (1979), University of Helsinki edition, CC BY 4.0; original project atlas cells.',
          source_url='https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/',
          source_note='Contact sheets containing the exact font are local-only. The manifest records pointers, hashes and authored observations, without copies of that font or source inscription strings.'))
    write(HERE / 'freeze-manifest.json', dict(frozen_at_utc=freeze_time, counts=counts,
          input_sha256=sha(HERE.parent / 'candidate-starting-pool.json'),
          outputs=[dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path))
                   for path in [HERE / 'families.json', HERE / 'image-review-manifest.json']],
          no_new_context_outputs_read=True,
          unresolved_prior_layers=dict(Counter(by_code[code]['tier_before'] for code in uncovered))))
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
