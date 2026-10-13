"""Post-review quantity-family predecessor sensitivity; primary results stay fixed."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'quantity-sensitivity-v1'
LOCAL = ROOT / 'data/raw/2026-10-12-anchor-expansion/context/quantity-sensitivity-v1'
PREVIOUS_LOCAL = ROOT / 'data/raw/2026-10-12-anchor-expansion/context/run-v2'
VISUAL = HERE.parent / 'visual/families.json'
VISUAL_SHA = '022db17e93741edb3bba098cbba286a6723c544d64d2bbc19e99c43a4908f6a3'
NARROW = {f'{x:03d}' for x in range(1, 6)}
FRAME_NAMES = ['all_texts', 'length_ge3', 'discovery', 'transfer', 'one_face_per_physical_object']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def proxy_score(frame, members, quantity):
    support = 0
    tokens = 0
    expected = 0.0
    inscriptions = 0
    all_match = 0
    any_exception = 0
    mixed = 0
    for record in frame:
        seq = record['complete_codes_reading_rtl']
        slots = [i for i, code in enumerate(seq) if code in members]
        if not slots:
            continue
        counts = Counter(seq)
        n = len(slots)
        q = sum(counts[code] for code in quantity)
        overlap = sum(counts[code] for code in members & quantity)
        expected += (n * q - overlap) / len(seq)
        matches = sum(i > 0 and seq[i - 1] in quantity for i in slots)
        tokens += n
        support += matches
        inscriptions += 1
        all_match += matches == n
        any_exception += matches != n
        mixed += 0 < matches < n
    return {'tokens': tokens, 'matching_tokens': support, 'contradicting_tokens': tokens - support,
            'expected_matching_tokens': expected, 'matching_fraction': support / tokens if tokens else None,
            'observed_minus_expected': support - expected,
            'supporting_direction': support > expected + 1e-12 if tokens else None,
            'containing_inscriptions': inscriptions, 'all_occurrences_matching_inscriptions': all_match,
            'any_contradiction_inscriptions': any_exception, 'mixed_inscriptions': mixed,
            'empty_sample': tokens == 0, 'observed_zero_matches': tokens > 0 and support == 0,
            'status': 'empty_sample' if tokens == 0 else 'zero_matches' if support == 0 else
                      'all_matching' if support == tokens else 'mixed'}


def score_comparison(frame, members, quantity, primary):
    narrow = proxy_score(frame, members, NARROW)
    expanded = proxy_score(frame, members, quantity)
    for key in ['tokens', 'matching_tokens', 'contradicting_tokens', 'containing_inscriptions',
                'all_occurrences_matching_inscriptions', 'any_contradiction_inscriptions', 'mixed_inscriptions']:
        assert narrow[key] == primary[key], (key, narrow[key], primary[key])
    assert math.isclose(narrow['expected_matching_tokens'], primary['expected_matching_tokens'], abs_tol=1e-9)
    assert narrow['supporting_direction'] == primary['supporting_direction']
    assert expanded['matching_tokens'] >= narrow['matching_tokens']
    return {'narrow_W001_W005': narrow, 'expanded_quantity_family': expanded,
            'supporting_direction_differs': narrow['supporting_direction'] != expanded['supporting_direction'],
            'additional_matching_tokens': expanded['matching_tokens'] - narrow['matching_tokens']}


def stability(row):
    result = {}
    for proxy in ['narrow_W001_W005', 'expanded_quantity_family']:
        discovery = row['frames']['discovery'][proxy]
        transfer = row['frames']['transfer'][proxy]
        all_text = row['frames']['all_texts'][proxy]
        both = not discovery['empty_sample'] and not transfer['empty_sample']
        direction = (discovery['supporting_direction'] is True and transfer['supporting_direction'] is True) if both else None
        result[proxy] = {'both_split_frames_nonempty': both, 'both_split_frames_above_expectation': direction,
                         'at_least_five_distinct_strings': all_text['containing_inscriptions'] >= 5,
                         'proxy_directional_criterion_met': bool(direction) and all_text['containing_inscriptions'] >= 5,
                         'scope': 'Diagnostic side-by-side flag; the primary grade remains unchanged.'}
    result['two_split_direction_differs'] = result['narrow_W001_W005']['both_split_frames_above_expectation'] != result['expanded_quantity_family']['both_split_frames_above_expectation']
    result['five_string_proxy_criterion_differs'] = result['narrow_W001_W005']['proxy_directional_criterion_met'] != result['expanded_quantity_family']['proxy_directional_criterion_met']
    return result


def main():
    if OUT.exists() or LOCAL.exists():
        raise SystemExit('Refusing to overwrite a sensitivity endpoint')
    assert sha(VISUAL) == VISUAL_SHA
    assert (HERE / 'AMENDMENT-QUANTITY-FAMILY.md').is_file()
    spec = importlib.util.spec_from_file_location('context_definition', HERE / 'run-v2/analyze_complete.py')
    prior_code = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior_code)
    primary = load(HERE / 'run-v2/summary.json')
    visual = load(VISUAL)
    families = visual['rows']
    quantity = set(next(family['codes'] for family in families if family['family_id'] == 'quantity_strokes'))
    assert len(quantity) == 32 and NARROW.issubset(quantity)
    records = load(PREVIOUS_LOCAL / 'complete-records.json')['records']
    unique = load(PREVIOUS_LOCAL / 'complete-example-candidates.json')['records']
    by_physical = defaultdict(list)
    for record in records:
        by_physical[record['physical_component_id']].append(record)
    representatives = [min(rows, key=lambda row: (-row['length'], prior_code.record_key(row)))
                       for rows in by_physical.values()]
    frames = {'all_texts': unique, 'length_ge3': [row for row in unique if row['length'] >= 3],
              'discovery': [row for row in unique if row['split'] == 'discovery'],
              'transfer': [row for row in unique if row['split'] == 'transfer'],
              'one_face_per_physical_object': representatives}
    for name, frame in frames.items():
        prior_size = primary['input_accounting']['split']['frames'][name]
        assert len(frame) == prior_size['strings']
        assert sum(row['length'] for row in frame) == prior_size['tokens']
    OUT.mkdir()
    LOCAL.mkdir(parents=True)
    inputs = [VISUAL, HERE / 'AMENDMENT-QUANTITY-FAMILY.md', HERE / 'run-v2/summary.json',
              HERE / 'run-v2/analyze_complete.py', PREVIOUS_LOCAL / 'complete-records.json',
              PREVIOUS_LOCAL / 'complete-example-candidates.json']
    write(OUT / 'input-manifest.json', {
        'status': 'Post-outcome sensitivity; fixed primary results and grades preserved',
        'code': {'path': rel(Path(__file__)), 'sha256': sha(Path(__file__))},
        'inputs': [{'path': rel(path), 'sha256': sha(path)} for path in inputs],
        'narrow_codes': sorted(NARROW), 'expanded_codes': sorted(quantity), 'new_random_draws': 0})
    code_rows = []
    for prior in primary['code_rows']:
        code = prior['code']
        row = {'code': code, 'starting_tier': prior['starting_tier'],
               'frames': {name: score_comparison(frame, {code}, quantity,
                                                 prior['frames'][name]['role_scores']['counted_entity'])
                          for name, frame in frames.items()}}
        row['diagnostic_stability'] = stability(row)
        code_rows.append(row)
    by_code = {row['code']: row for row in code_rows}
    prior_families = {family['family_id']: family for family in primary['family_rows']}
    family_rows = []
    for family in families:
        identifier = family['family_id']
        members = set(family['codes'])
        prior = prior_families[identifier]
        row = {'family_id': identifier, 'codes': family['codes'],
               'primary_declared_role': family['role_predictions'],
               'frames': {name: score_comparison(frame, members, quantity,
                                                 prior['frames'][name]['role_scores']['counted_entity'])
                          for name, frame in frames.items()}}
        for name in FRAME_NAMES:
            for proxy in ['narrow_W001_W005', 'expanded_quantity_family']:
                pooled = row['frames'][name][proxy]
                children = [by_code[code]['frames'][name][proxy] for code in members]
                assert pooled['matching_tokens'] == sum(child['matching_tokens'] for child in children)
                assert pooled['contradicting_tokens'] == sum(child['contradicting_tokens'] for child in children)
                assert math.isclose(pooled['expected_matching_tokens'],
                                    sum(child['expected_matching_tokens'] for child in children), abs_tol=1e-9)
        row['diagnostic_stability'] = stability(row)
        row['pooled_member_arithmetic_verified'] = True
        family_rows.append(row)
    selected = []
    for cisi, code, predecessor in [('M-16', '130', '035'), ('M-389', '383', '031')]:
        witnesses = [row for row in records if row['source_cisi'] == cisi]
        matches = []
        for record in witnesses:
            seq = record['complete_codes_reading_rtl']
            for slot, token in enumerate(seq):
                if token == code and slot > 0 and seq[slot - 1] == predecessor:
                    assert predecessor in quantity and predecessor not in NARROW
                    matches.append({'record_id': record['record_id'], 'source_id': record['source_id'],
                                    'source_cisi': cisi, 'target_code': code,
                                    'predecessor_code': predecessor, 'index_one_based': slot + 1,
                                    'whole_record_length': len(seq), 'split': record['split'],
                                    'narrow_match': False, 'expanded_match': True})
        assert matches, f'Selected {cisi}/{code}/{predecessor} relationship absent'
        selected.extend(matches)
    occurrence_rows = []
    record_rows = []
    member_map = {family['family_id']: set(family['codes']) for family in families}
    for record in records:
        seq = record['complete_codes_reading_rtl']
        per_code = defaultdict(list)
        per_family = defaultdict(list)
        for slot, code in enumerate(seq):
            narrow = slot > 0 and seq[slot - 1] in NARROW
            expanded = slot > 0 and seq[slot - 1] in quantity
            occurrence = {'record_id': record['record_id'], 'source_id': record['source_id'],
                          'source_cisi': record['source_cisi'], 'component_id': record['component_id'],
                          'physical_component_id': record['physical_component_id'], 'split': record['split'],
                          'code': code, 'index_one_based': slot + 1, 'whole_record_length': len(seq),
                          'narrow_match': narrow, 'expanded_match': expanded,
                          'predecessor_code': seq[slot - 1] if slot > 0 else None}
            occurrence_rows.append(occurrence)
            per_code[code].append((narrow, expanded))
            for identifier, members in member_map.items():
                if code in members:
                    per_family[identifier].append((narrow, expanded))
        def record_comparison(flags):
            return {'occurrences': len(flags),
                    'narrow_matching': sum(x[0] for x in flags), 'expanded_matching': sum(x[1] for x in flags),
                    'narrow_all_matching': all(x[0] for x in flags), 'expanded_all_matching': all(x[1] for x in flags),
                    'narrow_any_exception': any(not x[0] for x in flags),
                    'expanded_any_exception': any(not x[1] for x in flags)}
        record_rows.append({**record, 'code_proxy_comparisons': {code: record_comparison(flags) for code, flags in per_code.items()},
                            'family_proxy_comparisons': {identifier: record_comparison(flags) for identifier, flags in per_family.items()}})
    changes = {'code_rows': [{'code': row['code'], 'frames_with_different_direction':
                             [name for name in FRAME_NAMES if row['frames'][name]['supporting_direction_differs']],
                             'diagnostic_stability': row['diagnostic_stability']}
                            for row in code_rows if any(row['frames'][name]['supporting_direction_differs'] for name in FRAME_NAMES)
                            or row['diagnostic_stability']['five_string_proxy_criterion_differs']],
               'family_rows': [{'family_id': row['family_id'], 'primary_declared_role': row['primary_declared_role'],
                               'frames_with_different_direction':
                               [name for name in FRAME_NAMES if row['frames'][name]['supporting_direction_differs']],
                               'diagnostic_stability': row['diagnostic_stability']}
                              for row in family_rows if any(row['frames'][name]['supporting_direction_differs'] for name in FRAME_NAMES)
                              or row['diagnostic_stability']['five_string_proxy_criterion_differs']]}
    write(OUT / 'summary.json', {
        'status': 'Post-review quantity-family sensitivity; primary grades unchanged',
        'narrow_codes': sorted(NARROW), 'expanded_codes': sorted(quantity),
        'proxy_scope': 'Quantity-like graphics with unverified count/tier meanings; immediate predecessor proxy only.',
        'frames': {name: {'inscriptions': len(frame), 'tokens': sum(row['length'] for row in frame)} for name, frame in frames.items()},
        'code_rows': code_rows, 'family_rows': family_rows,
        'grade_scope': 'Side-by-side diagnostic flags are not retrospective replacements for the fixed primary grade.'})
    write(OUT / 'direction-changes.json', changes)
    write(OUT / 'verification.json', {
        'status': 'pass', 'all_713_narrow_results_match_fixed_primary': True,
        'all_70_family_narrow_results_match_fixed_primary': True,
        'all_five_frames_unchanged': True, 'pooled_member_matching_expectations_equal': True,
        'expanded_matching_counts_never_below_narrow': True,
        'selected_source_relationships': selected,
        'primary_summary_sha256': sha(HERE / 'run-v2/summary.json'), 'new_draws': 0,
        'scope': 'Arithmetic, original primary reproduction and named source assertions; no semantic authentication.'})
    write(LOCAL / 'quantity-occurrences.json', {'scope': 'All eligible faces including duplicate strings; full primary summaries deduplicate strings.',
                                              'occurrences': occurrence_rows})
    write(LOCAL / 'complete-record-comparisons.json', {'scope': 'Local-only complete strings and per-record exceptions', 'records': record_rows})
    write(LOCAL / 'selected-complete-witnesses.json', {'records': [record for record in record_rows if record['record_id'] in {s['record_id'] for s in selected}]})
    text = ['# Quantity-family sensitivity after source review', '',
            'The expanded predecessor proxy uses all 32 codes from the frozen quantity-strokes family. The original W001–W005 calculation and grades remain unchanged. Every code and family has side-by-side results in all five original frames, including whole-inscription all-occurrence matches and exceptions.', '',
            '| Code | Narrow matches / tokens | Expanded matches / tokens | Expanded expectation | Narrow two-split direction | Expanded two-split direction |',
            '|---|---:|---:|---:|---|---|']
    for code in ['130', '383', '151', '154', '156', '158', '142']:
        row = by_code[code]
        narrow = row['frames']['all_texts']['narrow_W001_W005']
        expanded = row['frames']['all_texts']['expanded_quantity_family']
        st = row['diagnostic_stability']
        text.append(f"| W{code} | {narrow['matching_tokens']}/{narrow['tokens']} | {expanded['matching_tokens']}/{expanded['tokens']} | {expanded['expected_matching_tokens']:.3f} | {st['narrow_W001_W005']['both_split_frames_above_expectation']} | {st['expanded_quantity_family']['both_split_frames_above_expectation']} |")
    text += ['', f"Direction differs in at least one frame for {len(changes['code_rows'])} code rows and {len(changes['family_rows'])} family rows. [All changes](direction-changes.json) retain the unaffected and opposing split directions; [complete results](summary.json) retain zero matches and empty frames.", '',
             'The source assertions confirm that M-16 contains W035 immediately before W130 and M-389 contains W031 immediately before W383. Both predecessors belong to the frozen expanded family. Public verification gives IDs and bounded predecessor relationships; the complete witnesses remain local.', '',
             'A failure under W001–W005 describes absence of the selected short-stroke proxy. It does not describe absence of all counting or quantity-like graphics. Expansion also raises the bag-shuffle expectation, so increased matching counts alone do not establish stronger directional support. These post-review results remain a sensitivity beside the unchanged primary classification.', '',
             'Both proxies reproduce the original five frame populations. All 713 narrow code results and all 70 narrow family results match the primary endpoint, and pooled matching/expectation sums agree with member codes. No new draws or probability tails were computed.']
    (OUT / 'REPORT.md').write_text('\n'.join(text) + '\n', encoding='utf-8')
    import shutil
    shutil.copyfile(__file__, OUT / 'quantity_sensitivity.py')
    shutil.copyfile(HERE / 'AMENDMENT-QUANTITY-FAMILY.md', OUT / 'AMENDMENT-QUANTITY-FAMILY.md')
    write(OUT / 'output-manifest.json', {
        'status': 'complete',
        'public': [{'path': rel(path), 'sha256': sha(path)} for path in sorted(OUT.iterdir())],
        'local_only': [{'path': rel(path), 'sha256': sha(path)} for path in sorted(LOCAL.iterdir())]})
    print(json.dumps({'endpoint': rel(OUT), 'code_rows': len(code_rows), 'family_rows': len(family_rows),
                      'code_direction_change_rows': len(changes['code_rows']),
                      'family_direction_change_rows': len(changes['family_rows']),
                      'selected_relationships': selected, 'status': 'pass'}, indent=2))


if __name__ == '__main__':
    main()
