"""Complete-string context summaries and fixed-role stability diagnostics.

Full records, templates and occurrence indices are written only to LOCAL.
Each run refuses existing destinations; family integration is a new run.
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent
LOCAL = ROOT / 'data/raw/2026-10-12-anchor-expansion/context'
REGISTER = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
CLEAN = ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl'
CATALOGUE = ROOT / 'experiments/2026-10-11-bonta-adversarial/run-v6/catalogue-data.json'
REGISTER_SHA = '1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db'
CLEAN_SHA = '9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8'
CATALOGUE_SHA = '1e8589c5c6ac1d446a760cd9cc73c091a2e8c3f43a949aad4e78963c3c8b5b16'
SALT = 'indus-anchor-expansion-2026-10-12-context-v1'
STROKES = {f'{x:03d}' for x in range(1, 6)}
OTHER_STROKES = {f'{x:03d}' for x in range(31, 36)}
CLOSERS = {'400', '740'}
ROLES = ['closing', 'counted_entity', 'nonfinal_entity', 'internal_connector', 'opening', 'unconstrained']
FRAMES = ['all_texts', 'length_ge3', 'discovery', 'transfer', 'one_face_per_physical_object']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def write(path, obj):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def load_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]


def record_key(row):
    return tuple((0, int(x)) if x.isdigit() else (1, x)
                 for x in re.split(r'(\d+)', str(row['record_id'])) if x)


class UnionFind:
    def __init__(self, n, parents=None):
        self.parents = list(range(n)) if parents is None else parents.copy()

    def find(self, i):
        while self.parents[i] != i:
            self.parents[i] = self.parents[self.parents[i]]
            i = self.parents[i]
        return i

    def union(self, i, j):
        a, b = self.find(i), self.find(j)
        self.parents[max(a, b)] = min(a, b)


def cisi_base(value):
    found = re.fullmatch(r'([A-Za-z][A-Za-z0-9]*-\d+)[A-Za-z]?', value.strip())
    return found[1] if found else None


def group_ids(uf, rows):
    groups = defaultdict(list)
    for i in range(len(rows)):
        groups[uf.find(i)].append(i)
    ids = {}
    for indices in groups.values():
        source_ids = sorted(str(rows[i]['record_id']) for i in indices)
        identifier = hashlib.sha256(json.dumps(source_ids, separators=(',', ':')).encode()).hexdigest()
        for i in indices:
            ids[i] = identifier
    return ids, groups


def identity_closure(rows):
    physical, seen, unresolved = UnionFind(len(rows)), {}, []
    for i, row in enumerate(rows):
        aliases = set(map(str, row.get('artifact_aliases', []))) | {str(row['object_family_id'])}
        keys = [('family', alias) for alias in aliases]
        base = cisi_base(row.get('source_cisi', ''))
        if base:
            keys.append(('cisi', base))
        elif row.get('source_cisi', '').strip() not in {'', '-', '--'}:
            unresolved.append({'record_id': row['record_id'], 'source_cisi': row['source_cisi']})
        for key in keys:
            if key in seen:
                physical.union(i, seen[key])
            else:
                seen[key] = i
    physical_ids, physical_groups = group_ids(physical, rows)
    closures = {}
    for name, placeholders in [('primary', True), ('without_placeholder_text_edges', False)]:
        graph, string_seen = UnionFind(len(rows), physical.parents), {}
        for i, row in enumerate(rows):
            seq = tuple(map(str, row['signs_reading_rtl']))
            placeholder = row.get('has_unknown_sign', False) or row.get('has_blank_space', False) or any(
                code in {'000', '999', '?', '__UNKNOWN__'} for code in seq)
            if not seq or (placeholder and not placeholders):
                continue
            if seq in string_seen:
                graph.union(i, string_seen[seq])
            else:
                string_seen[seq] = i
        ids, groups = group_ids(graph, rows)
        closures[name] = {'ids': ids, 'groups': groups}
    return physical_ids, physical_groups, closures, unresolved


def split_for(identifier):
    value = int.from_bytes(hashlib.sha256(f'{SALT}|{identifier}'.encode('utf-8')).digest(), 'big')
    return 'discovery' if value < (7 * (1 << 256)) // 10 else 'transfer'


def eligibility(row):
    if not row.get('clean_rtl_singleline', False):
        return 'not_clean_reading_order_singleline'
    if (not row.get('complete_observed', False) or not row.get('single_line', False)
            or row.get('has_unknown_sign', False) or row.get('has_blank_space', False)
            or row.get('max_damage', 0) or row.get('max_uncertainty', 0)
            or any(code in {'000', '999', '?', '__UNKNOWN__'} for code in row['signs_reading_rtl'])):
        return 'incomplete_unknown_blank_damage_uncertainty'
    return 'length_below_two' if len(row['signs_reading_rtl']) < 2 else None


def role_flags(seq, slot):
    length = len(seq)
    return {
        'closing': slot == length - 1 or (slot == length - 2 and seq[-1] in CLOSERS),
        'counted_entity': slot > 0 and seq[slot - 1] in STROKES,
        'nonfinal_entity': slot < length - 1,
        'internal_connector': 0 < slot < length - 1,
        'opening': slot == 0,
    }


def expected_roles(seq, members):
    counts, length = Counter(seq), len(seq)
    number = sum(counts[c] for c in members)
    stroke_count = sum(counts[c] for c in STROKES)
    closer_count = sum(counts[c] for c in CLOSERS)
    own_strokes = sum(counts[c] for c in members & STROKES)
    own_closers = sum(counts[c] for c in members & CLOSERS)
    return {
        'opening': number / length,
        'nonfinal_entity': number * (length - 1) / length,
        'internal_connector': number * (length - 2) / length,
        'counted_entity': (number * stroke_count - own_strokes) / length,
        'closing': number / length + (number * closer_count - own_closers) / (length * (length - 1)),
    }


def aggregate(frame, members, anchor_codes):
    positions = Counter()
    expected_pos = Counter()
    variance_pos = Counter()
    predecessor = Counter()
    anchor_support = Counter()
    role_rows = {role: {'matching_tokens': 0, 'expected_matching_tokens': 0.0,
                        'all_occurrences_matching_inscriptions': 0,
                        'any_contradiction_inscriptions': 0, 'mixed_inscriptions': 0}
                 for role in ROLES if role != 'unconstrained'}
    containing = [record for record in frame if members & set(record['seq'])]
    physical_support = set()
    closure_support = set()
    token_total = 0
    for record in containing:
        seq = record['seq']
        length = len(seq)
        slots = [slot for slot, code in enumerate(seq) if code in members]
        token_total += len(slots)
        physical_support.update(record['physical_ids'])
        closure_support.add(record['component_id'])
        p = len(slots) / length
        for name, exp, var in zip(['initial', 'medial', 'final'],
                                   [p, (length - 2) * p, p],
                                   [p * (1 - p), 2 * (length - 2) * p * (1 - p) / (length - 1), p * (1 - p)]):
            expected_pos[name] += exp
            variance_pos[name] += var
        expected = expected_roles(seq, members)
        flags = [role_flags(seq, slot) for slot in slots]
        for role, target in role_rows.items():
            matched = sum(f[role] for f in flags)
            target['matching_tokens'] += matched
            target['expected_matching_tokens'] += expected[role]
            target['all_occurrences_matching_inscriptions'] += matched == len(slots)
            target['any_contradiction_inscriptions'] += matched < len(slots)
            target['mixed_inscriptions'] += 0 < matched < len(slots)
        for slot in slots:
            position = 'initial' if slot == 0 else 'final' if slot == length - 1 else 'medial'
            positions[position] += 1
            if slot > 0:
                prior = seq[slot - 1]
                predecessor['W001_W005'] += prior in STROKES
                predecessor['W031_W035'] += prior in OTHER_STROKES
                predecessor['W060'] += prior == '060'
        anchor_support.update((set(seq) & anchor_codes) - members)
    position_output = {}
    for name in ['initial', 'medial', 'final']:
        variance = variance_pos[name]
        position_output[name] = {'observed': positions[name], 'expectation': expected_pos[name],
                                 'variance': variance,
                                 'z': (positions[name] - expected_pos[name]) / math.sqrt(variance) if variance else None}
    assert sum(positions.values()) == token_total
    for role, row in role_rows.items():
        matched = row['matching_tokens']
        row.update({'tokens': token_total, 'contradicting_tokens': token_total - matched,
                    'matching_fraction': matched / token_total if token_total else None,
                    'observed_minus_expected': matched - row['expected_matching_tokens'],
                    'supporting_direction': matched > row['expected_matching_tokens'] + 1e-12 if token_total else None,
                    'empty_sample': token_total == 0,
                    'observed_zero_matches': token_total > 0 and matched == 0,
                    'status': 'empty_sample' if token_total == 0 else 'zero_matches' if matched == 0 else
                              'all_matching' if matched == token_total else 'mixed',
                    'containing_inscriptions': len(containing)})
    role_rows['unconstrained'] = {'tokens': token_total, 'containing_inscriptions': len(containing),
                                  'matching_tokens': None, 'contradicting_tokens': None,
                                  'expected_matching_tokens': None, 'supporting_direction': None,
                                  'status': 'unconstrained', 'empty_sample': token_total == 0,
                                  'score': None}
    return {'frame_inscriptions': len(frame), 'containing_inscriptions': len(containing),
            'tokens': token_total, 'physical_object_support': len(physical_support),
            'closure_component_support': len(closure_support),
            'length_distribution': dict(sorted(Counter(str(len(r['seq'])) for r in containing).items())),
            'positions': position_output, 'role_scores': role_rows,
            'predecessor_graphic_groups': {name: predecessor[name] for name in ['W001_W005', 'W031_W035', 'W060']},
            'fixed_run_v6_anchor_cooccurrence_strings': dict(sorted(anchor_support.items()))}


def make_templates(unique, inventory):
    holes = defaultdict(dict)
    for record in unique:
        seq = record['seq']
        for slot, code in enumerate(seq):
            hole = seq[:slot] + ('?',) + seq[slot + 1:]
            holes[hole][code] = record
    per_code, private = {}, []
    for code in inventory:
        selected = [(hole, variants) for hole, variants in holes.items()
                    if code in variants and len(variants) > 1]
        alternatives = Counter(other for _, variants in selected for other in variants if other != code)
        lengths = Counter(str(len(hole)) for hole, _ in selected)
        per_code[code] = {
            'templates': len(selected), 'length_distribution': dict(sorted(lengths.items())),
            'two_sign_templates': sum(len(hole) == 2 for hole, _ in selected),
            'length_ge3_templates': sum(len(hole) >= 3 for hole, _ in selected),
            'alternative_counts': dict(sorted(alternatives.items())),
        }
    for hole, variants in holes.items():
        if len(variants) < 2:
            continue
        private.append({'template': list(hole), 'slot_one_based': hole.index('?') + 1,
                        'variants': [{'code': code, 'source_record_id': record['record_id'],
                                      'source_cisi': record['source_cisi'], 'component_id': record['component_id'],
                                      'split': record['split'], 'complete_codes_reading_rtl': list(record['seq'])}
                                     for code, record in sorted(variants.items())]})
    return per_code, private


def family_members(family):
    raw = family.get('codes', family.get('members', []))
    return sorted({str(item.get('code') if isinstance(item, dict) else item).removeprefix('W').zfill(3)
                   for item in raw})


def declared_roles(family):
    raw = family.get('roles', family.get('role_predictions', family.get('role', [])))
    if isinstance(raw, str):
        raw = [raw]
    answer = {item.get('role') if isinstance(item, dict) else item for item in raw}
    for key in ['primary_role', 'alternative_roles']:
        more = family.get(key, [])
        if isinstance(more, str):
            more = [more]
        answer.update(item.get('role') if isinstance(item, dict) else item for item in more)
    answer.discard(None)
    if not answer:
        raise ValueError(f'No declared role for {family.get("id", family.get("family_id"))}')
    if answer - set(ROLES):
        raise ValueError(f'Unknown roles: {answer - set(ROLES)}')
    return [role for role in ROLES if role in answer]


def evaluate_family(family, frames, anchor_codes, code_rows, templates):
    members = family_members(family)
    assert members and set(members).issubset(code_rows), 'Family codes absent from inventory'
    roles = declared_roles(family)
    row = {'family_id': family.get('family_id', family.get('id')),
           'name': family.get('name', family.get('label', family.get('working_meaning'))), 'codes': members,
           'declared_roles': roles,
           'frames': {name: aggregate(frame, set(members), anchor_codes) for name, frame in frames.items()},
           'member_rows': [{'code': code, **code_rows[code]['frames']} for code in members]}
    for name, pooled in row['frames'].items():
        children = [code_rows[code]['frames'][name] for code in members]
        assert pooled['tokens'] == sum(child['tokens'] for child in children)
        for position in ['initial', 'medial', 'final']:
            assert pooled['positions'][position]['observed'] == sum(child['positions'][position]['observed'] for child in children)
            assert math.isclose(pooled['positions'][position]['expectation'],
                                sum(child['positions'][position]['expectation'] for child in children),
                                abs_tol=1e-9)
        for role in ROLES:
            if role == 'unconstrained':
                continue
            aggregate_role = pooled['role_scores'][role]
            assert aggregate_role['matching_tokens'] == sum(child['role_scores'][role]['matching_tokens'] for child in children)
            assert aggregate_role['contradicting_tokens'] == sum(child['role_scores'][role]['contradicting_tokens'] for child in children)
            assert math.isclose(aggregate_role['expected_matching_tokens'],
                                sum(child['role_scores'][role]['expected_matching_tokens'] for child in children),
                                abs_tol=1e-9)
    row['pooled_member_arithmetic'] = {
        'token_counts_and_role_expectations_match_sum_of_codes': True,
        'frames_checked': FRAMES,
        'inscription_scope': 'Containing and all-occurrences-passing inscriptions are unions of complete records, rather than sums of overlapping member-code counts.'}
    stability = {}
    for role in roles:
        discovery = row['frames']['discovery']['role_scores'][role]
        transfer = row['frames']['transfer']['role_scores'][role]
        all_text = row['frames']['all_texts']
        stability[role] = {
            'all_distinct_strings': all_text['containing_inscriptions'],
            'at_least_five_distinct_strings': all_text['containing_inscriptions'] >= 5,
            'discovery_nonempty': not discovery['empty_sample'],
            'transfer_nonempty': not transfer['empty_sample'],
            'discovery_supporting_direction': discovery['supporting_direction'],
            'transfer_supporting_direction': transfer['supporting_direction'],
            'both_nonempty_frames_above_expectation': None if role == 'unconstrained' else
                discovery['supporting_direction'] is True and transfer['supporting_direction'] is True,
            'scope': 'Structural prioritization criterion; picture and selected anchor are reviewed by the integration owner.',
        }
    row['declared_role_stability'] = stability
    selected = [item for item in templates if set(members) & {v['code'] for v in item['variants']}]
    row['exact_substitutions'] = {
        'templates_involving_any_member': len(selected),
        'length_distribution': dict(sorted(Counter(str(len(item['template'])) for item in selected).items())),
        'two_sign_templates': sum(len(item['template']) == 2 for item in selected),
        'length_ge3_templates': sum(len(item['template']) >= 3 for item in selected),
        'alternative_code_counts': dict(sorted(Counter(v['code'] for item in selected for v in item['variants']
                                                      if v['code'] not in members).items())),
        'member_substitution_counts': {code: code_rows[code]['substitutions'] for code in members},
    }
    return row


def complete_record(row, physical_id, component_id):
    return {'record_id': str(row['record_id']), 'source_id': str(row.get('source_record_id', row['record_id'])),
            'object_family_id': str(row['object_family_id']), 'physical_component_id': physical_id,
            'component_id': component_id, 'split': split_for(component_id),
            'source_cisi': row.get('source_cisi'), 'site': row.get('site'), 'region': row.get('region'),
            'object_type': row.get('object_type'), 'source_direction': row.get('direction'),
            'orientation_basis': row.get('orientation_basis'), 'length': len(row['signs_reading_rtl']),
            'complete_codes_reading_rtl': list(row['signs_reading_rtl'])}


def independent_checks(raw, eligible, unique, code_rows, templates, split_map, closure_ids, physical_ids):
    prior_path = ROOT / 'experiments/2026-10-11-bonta-adversarial/run-v2/position-audit.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    positions_match = all(code_rows[row['code']]['frames']['all_texts']['tokens'] == row['non_singleton_tokens']
        and all(code_rows[row['code']]['frames']['all_texts']['positions'][position]['observed'] == row['positions'][position]['observed']
                for position in ['initial', 'medial', 'final']) for row in prior['rows'])
    assert positions_match
    physical_splits = defaultdict(set)
    string_splits = defaultdict(set)
    for i, row in enumerate(raw):
        physical_splits[physical_ids[i]].add(split_map[closure_ids[i]])
        if row['signs_reading_rtl']:
            string_splits[tuple(row['signs_reading_rtl'])].add(split_map[closure_ids[i]])
    assert all(len(v) == 1 for v in physical_splits.values())
    assert all(len(v) == 1 for v in string_splits.values())
    witness_rows = []
    for item in templates:
        for left, right in combinations(item['variants'], 2):
            if {left['code'], right['code']} not in [{'154', '156'}, {'154', '158'}, {'151', '740'}]:
                continue
            a, b = left['complete_codes_reading_rtl'], right['complete_codes_reading_rtl']
            differences = [i for i, pair in enumerate(zip(a, b)) if pair[0] != pair[1]]
            assert len(a) == len(b) and differences == [item['slot_one_based'] - 1]
            witness_rows.append({'left_id': left['source_record_id'], 'right_id': right['source_record_id'],
                                 'length': len(a), 'single_difference_one_based': differences[0] + 1,
                                 'left_code': left['code'], 'right_code': right['code'],
                                 'verified': True})
    selected = {row['record_id']: row for row in eligible}
    medial = selected['2162.1']['signs_reading_rtl']
    variant = selected['834.2']['signs_reading_rtl']
    assert medial[1] == '142' and len(medial) == 3
    assert variant[-2:] == ['158', '400']
    assert code_rows['151']['substitutions']['alternative_counts']['740'] == 8
    assert code_rows['154']['substitutions']['alternative_counts']['156'] == 4
    assert code_rows['154']['substitutions']['alternative_counts']['158'] == 2
    return {'eligible_frame_matches_prior_complete_frame': True,
            'all_713_pooled_position_counts_match_frozen_run_v2': positions_match,
            'full_register_physical_split_overlap': 0, 'full_register_identical_string_split_overlap': 0,
            'actual_record_medial_W142_M2063': True, 'actual_record_W158_before_comb_H2185': True,
            'real_exact_template_witnesses_checked': len(witness_rows),
            'witness_metadata': witness_rows,
            'scope': 'Pinned empirical counts and actual whole-record one-difference witnesses; no simulated unit fixtures.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    parser.add_argument('--families', type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'run-v\d+', args.run):
        raise SystemExit('Run name must be run-vN')
    public, local = HERE / args.run, LOCAL / args.run
    if public.exists() or local.exists():
        raise SystemExit('Refusing to overwrite an existing endpoint')
    assert sha(REGISTER) == REGISTER_SHA and sha(CLEAN) == CLEAN_SHA and sha(CATALOGUE) == CATALOGUE_SHA
    if args.families is not None and not args.families.is_absolute():
        args.families = ROOT / args.families
    if args.families is not None and not args.families.is_file():
        raise SystemExit('Frozen family map is missing')
    public.mkdir(parents=True)
    local.mkdir(parents=True)
    inputs = [REGISTER, CLEAN, CATALOGUE, HERE / 'PROTOCOL.md', BASE / 'PROTOCOL.md']
    if args.families is not None:
        inputs.append(args.families)
    write(public / 'input-manifest.json', {
        'status': 'Exploratory complete-context diagnostic; stability on previously exposed data',
        'run': args.run, 'code': {'path': rel(Path(__file__)), 'sha256': sha(Path(__file__))},
        'inputs': [{'path': rel(path), 'sha256': sha(path)} for path in inputs],
        'split': {'salt': SALT, 'hash': 'SHA256', 'discovery_component_fraction': 0.7,
                  'transfer_component_fraction': 0.3}, 'new_random_draws': 0})
    raw, pinned_clean = load_rows(REGISTER), load_rows(CLEAN)
    assert len(raw) == 5680 and len({r['record_id'] for r in raw}) == len(raw)
    physical_ids, physical_groups, closures, unresolved = identity_closure(raw)
    primary = closures['primary']
    closure_ids = primary['ids']
    split_map = {identifier: split_for(identifier) for identifier in set(closure_ids.values())}
    eligible_indices = [i for i, row in enumerate(raw) if eligibility(row) is None]
    eligible = [raw[i] for i in eligible_indices]
    clean_by = {str(row['record_id']): row for row in pinned_clean}
    assert len(eligible) == len(pinned_clean) == 2930
    assert {str(row['record_id']) for row in eligible} == set(clean_by)
    assert all(row['signs_reading_rtl'] == clean_by[str(row['record_id'])]['signs_reading_rtl'] for row in eligible)
    grouped = defaultdict(list)
    for i in eligible_indices:
        grouped[tuple(raw[i]['signs_reading_rtl'])].append(i)
    unique = []
    for seq, indices in grouped.items():
        assert len({closure_ids[i] for i in indices}) == 1
        chosen = min(indices, key=lambda i: record_key(raw[i]))
        row = raw[chosen]
        unique.append({'seq': seq, 'record_id': row['record_id'], 'source_cisi': row['source_cisi'],
                       'component_id': closure_ids[chosen], 'split': split_map[closure_ids[chosen]],
                       'physical_ids': {physical_ids[i] for i in indices}, 'raw_indices': indices})
    unique.sort(key=lambda r: record_key(r))
    assert len(unique) == 1859
    by_physical = defaultdict(list)
    for i in eligible_indices:
        by_physical[physical_ids[i]].append(i)
    representatives = []
    for identifier, indices in by_physical.items():
        chosen = min(indices, key=lambda i: (-len(raw[i]['signs_reading_rtl']), record_key(raw[i])))
        representatives.append({'seq': tuple(raw[chosen]['signs_reading_rtl']), 'record_id': raw[chosen]['record_id'],
                                'source_cisi': raw[chosen]['source_cisi'], 'physical_ids': {identifier},
                                'component_id': closure_ids[chosen], 'split': split_map[closure_ids[chosen]],
                                'raw_indices': [chosen]})
    frames = {'all_texts': unique, 'length_ge3': [r for r in unique if len(r['seq']) >= 3],
              'discovery': [r for r in unique if r['split'] == 'discovery'],
              'transfer': [r for r in unique if r['split'] == 'transfer'],
              'one_face_per_physical_object': representatives}
    prior = json.loads(CATALOGUE.read_text(encoding='utf-8'))
    prior_by = {row['code']: row for row in prior['rows']}
    inventory = sorted(prior_by)
    anchor_codes = {code for code, row in prior_by.items() if row['anchors']}
    substitutions, full_templates = make_templates(unique, inventory)
    code_rows = {}
    for code in inventory:
        code_rows[code] = {'code': code, 'starting_tier': prior_by[code]['tier'],
                           'starting_meaning': prior_by[code]['meaning'],
                           'frames': {name: aggregate(frame, {code}, anchor_codes) for name, frame in frames.items()},
                           'substitutions': substitutions[code]}
    family_rows = []
    declared_families = []
    if args.families is not None:
        family_file = json.loads(args.families.read_text(encoding='utf-8'))
        declared_families = family_file if isinstance(family_file, list) else family_file.get('families', family_file.get('rows'))
        if not isinstance(declared_families, list):
            raise ValueError('Family map must have a families list')
        family_rows = [evaluate_family(f, frames, anchor_codes, code_rows, full_templates) for f in declared_families]
    component_load = Counter(r['component_id'] for r in unique)
    token_load = Counter()
    for r in unique:
        token_load[r['component_id']] += len(r['seq'])
    largest_id = max(component_load, key=lambda identifier: (component_load[identifier], identifier))
    accounting = {
        'input_register_records': len(raw), 'physical_components_before_filter': len(physical_groups),
        'full_object_text_closure_components': len(primary['groups']),
        'largest_full_register_component_records': max(map(len, primary['groups'].values())),
        'unresolved_nonblank_CISI_references': len(unresolved),
        'eligibility_exclusions': dict(Counter(eligibility(row) for row in raw if eligibility(row) is not None)),
        'eligible_faces': len(eligible), 'eligible_physical_objects': len(by_physical),
        'distinct_complete_strings': len(unique), 'complete_string_tokens': sum(len(r['seq']) for r in unique),
        'codes_present': len({code for r in unique for code in r['seq']}), 'inventory_codes': len(inventory),
        'eligible_closure_components': len(component_load),
        'largest_eligible_component_strings': max(component_load.values()),
        'largest_eligible_component_tokens': max(token_load.values()),
        'largest_eligible_string_component_split': split_map[largest_id],
        'largest_eligible_string_component_token_load': token_load[largest_id],
        'length_distribution': dict(sorted(Counter(str(len(r['seq'])) for r in unique).items())),
        'split': {'salt': SALT, 'discovery_component_fraction_rule': 0.7,
                  'closure_components_all_register': dict(Counter(split_map.values())),
                  'frames': {name: {'strings': len(frame), 'tokens': sum(len(r['seq']) for r in frame),
                                    'components': len({r['component_id'] for r in frame})}
                             for name, frame in frames.items()}},
        'without_placeholder_text_links': {
            'full_register_components': len(closures['without_placeholder_text_edges']['groups']),
            'eligible_components': len({closures['without_placeholder_text_edges']['ids'][i] for i in eligible_indices}),
        },
        'fixed_run_v6_anchor_codes': [{'code': code, 'tier': prior_by[code]['tier'],
                                      'comparisons': [a['word'] for a in prior_by[code]['anchors']]}
                                     for code in sorted(anchor_codes)],
    }
    local_records = [complete_record(raw[i], physical_ids[i], closure_ids[i]) for i in eligible_indices]
    record_lookup = {row['record_id']: row for row in local_records}
    occurrences = defaultdict(list)
    for row in local_records:
        seq = row['complete_codes_reading_rtl']
        for slot, code in enumerate(seq):
            occurrences[code].append({'record_id': row['record_id'], 'source_id': row['source_id'],
                                      'source_cisi': row['source_cisi'], 'component_id': row['component_id'],
                                      'physical_component_id': row['physical_component_id'], 'split': row['split'],
                                      'index_one_based': slot + 1, 'whole_record_length': len(seq),
                                      'role_matches': role_flags(seq, slot)})
    example_candidates = []
    for record in unique:
        local_row = record_lookup[record['record_id']]
        seq = record['seq']
        family_support = []
        for family in declared_families:
            members = set(family_members(family))
            slots = [slot for slot, code in enumerate(seq) if code in members]
            if not slots:
                continue
            roles = declared_roles(family)
            family_support.append({'family_id': family.get('family_id', family.get('id')),
                                   'indices_one_based': [slot + 1 for slot in slots],
                                   'declared_role_contradictions': {
                                       role: None if role == 'unconstrained' else sum(not role_flags(seq, slot)[role] for slot in slots)
                                       for role in roles}})
        example_candidates.append({**local_row, 'all_source_record_ids': [raw[i]['record_id'] for i in record['raw_indices']],
                                   'family_support': family_support})
    checks = independent_checks(raw, eligible, unique, code_rows, full_templates, split_map, closure_ids, physical_ids)
    write(public / 'input-accounting.json', accounting)
    write(public / 'summary.json', {
        'status': 'Exploratory full-inscription stability; generic frame' if not family_rows else 'Exploratory fixed-family context compatibility',
        'run': args.run, 'role_definitions': {role: role for role in ROLES},
        'role_score_scope': 'Counts and analytic bag-shuffle expectations. Structural compatibility does not prove vocabulary. All role alternatives retained.',
        'family_map': {'path': rel(args.families), 'sha256': sha(args.families)} if args.families else None,
        'input_accounting': accounting, 'code_rows': list(code_rows.values()), 'family_rows': family_rows})
    write(public / 'verification.json', checks)
    write(local / 'complete-records.json', {'status': 'Local-only complete source-derived records', 'run': args.run, 'records': local_records})
    write(local / 'code-occurrences.json', {'scope': 'All eligible faces, including duplicate strings; primary public code summaries deduplicate strings.',
                                           'rows': [{'code': code, 'occurrences': occurrences[code]} for code in inventory]})
    write(local / 'complete-templates.json', {'templates': full_templates})
    write(local / 'complete-example-candidates.json', {'status': 'Local-only; complete strings retained and contradictions included',
                                                       'records': example_candidates})
    write(local / 'closure-register.json', {
        'records': [{'record_id': row['record_id'], 'physical_component_id': physical_ids[i],
                     'component_id': closure_ids[i], 'split': split_map[closure_ids[i]],
                     'eligible': eligibility(row) is None, 'exclusion': eligibility(row)}
                    for i, row in enumerate(raw)], 'unresolved_source_references': unresolved})
    shutil.copyfile(__file__, public / 'analyze_complete.py')
    shutil.copyfile(HERE / 'PROTOCOL.md', public / 'PROTOCOL.md')
    write(public / 'output-manifest.json', {
        'status': 'Complete', 'public': [{'path': rel(path), 'sha256': sha(path)} for path in sorted(public.iterdir())],
        'local_only': [{'path': rel(path), 'sha256': sha(path)} for path in sorted(local.iterdir())],
        'scope': 'Local files contain complete corpus derivatives; they require the ignored local workspace.'})
    print(json.dumps({'run': args.run, 'public': rel(public), 'local': rel(local),
                      'faces': len(eligible), 'strings': len(unique),
                      'physical_objects': len(by_physical), 'closure_components': len(component_load),
                      'discovery_strings': len(frames['discovery']), 'transfer_strings': len(frames['transfer']),
                      'family_rows': len(family_rows), 'verification': 'pass'}, indent=2))


if __name__ == '__main__':
    main()
