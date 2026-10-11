"""Post-outcome context audit; reuse observed strings without new permutations.

The protocol in context-diagnostics-v1 must exist before this script runs.
Public results contain aggregates and source IDs, not corpus strings/templates.
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math
import shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'context-diagnostics-v1'
TARGETS = ['151', '154', '156', '158', '161', '400', '527', '617', '130', '142']
CONTEXT_TARGETS = ['151', '154', '156', '158', '161', '130']
STROKES_ALL = {f'{i:03d}' for i in range(1, 6)}
STROKES_TWO_PLUS = {f'{i:03d}' for i in range(2, 6)}
FORMULA_FIRST = {f'{i:03d}' for i in range(465, 476)}
CLOSERS = {'400', '740'}
POSITIONS = ['initial', 'medial', 'final']
START = '<START>'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def write_json(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def record_key(row):
    return tuple(int(x) if x.isdigit() else x for x in row['record_id'].split('.'))


def closing_member(seq, slot):
    return slot == len(seq) - 1 or (
        slot == len(seq) - 2 and seq[-1] in CLOSERS
    )


def position_stats(frame, codes):
    result = {
        code: {
            'tokens': 0,
            'distinct_strings': 0,
            'positions': {
                p: {'observed': 0, 'expectation': 0.0, 'variance': 0.0}
                for p in POSITIONS
            },
        }
        for code in codes
    }
    for seq in frame:
        length = len(seq)
        if length < 2:
            continue
        counts = Counter(seq)
        for code in codes:
            number = counts[code]
            if not number:
                continue
            row = result[code]
            row['tokens'] += number
            row['distinct_strings'] += 1
            chance = number / length
            expectations = [chance, (length - 2) * chance, chance]
            variances = [
                chance * (1 - chance),
                2 * (length - 2) * chance * (1 - chance) / (length - 1),
                chance * (1 - chance),
            ]
            for p, expected, variance in zip(POSITIONS, expectations, variances):
                row['positions'][p]['expectation'] += expected
                row['positions'][p]['variance'] += variance
        for slot, code in enumerate(seq):
            if code in result:
                p = 'initial' if slot == 0 else 'final' if slot == length - 1 else 'medial'
                result[code]['positions'][p]['observed'] += 1
    for row in result.values():
        assert sum(v['observed'] for v in row['positions'].values()) == row['tokens']
        for cell in row['positions'].values():
            variance = cell['variance']
            if variance > 0:
                cell['z'] = (cell['observed'] - cell['expectation']) / math.sqrt(variance)
            else:
                assert math.isclose(cell['observed'], cell['expectation'], abs_tol=1e-10)
                cell['z'] = None
    return result


def fisher_descriptive(table):
    a, b = table[0]
    c, d = table[1]
    total, row_total, final_total = a + b + c + d, a + b, a + c
    denominator = math.comb(total, row_total)

    def probability(k):
        return math.comb(final_total, k) * math.comb(total - final_total, row_total - k) / denominator

    observed = probability(a)
    lower = max(0, row_total - (total - final_total))
    upper = min(row_total, final_total)
    p = sum(probability(k) for k in range(lower, upper + 1)
            if probability(k) <= observed * (1 + 1e-12))
    odds = a * d / (b * c) if b * c else None
    return {'table': table, 'two_sided_fisher_p': min(1.0, p), 'odds_ratio': odds,
            'scope': 'Descriptive after selection; text/formula and production dependence remain unresolved.'}


def conditional_class(code):
    if code == START:
        return 'START'
    if code in STROKES_ALL:
        return 'narrow_stroke_W001_W005'
    if code == '740':
        return 'jar_W740'
    if code in {'151', '154', '156', '158', '161'}:
        return 'selected_carrier_graphics'
    if code in {'130', '142'}:
        return 'other_selected_person_composites'
    if code in {'400', '527', '617'}:
        return 'other_selected_closing_candidates'
    if code == '806':
        return 'formula_token_W806'
    if code in FORMULA_FIRST:
        return 'formula_first_W465_W475'
    if code == '035':
        return 'W035_separately_reported_not_in_stroke_sets'
    return 'other_or_unclassified'


def context_stats(unique):
    result = {}
    for code in TARGETS:
        events = [(seq, slot) for seq in unique for slot, token in enumerate(seq) if token == code]
        record_rows = [r for seq, rows in unique.items() if code in seq for r in rows]
        following400 = sum(slot + 1 < len(seq) and seq[slot + 1] == '400' for seq, slot in events)
        following740 = sum(slot + 1 < len(seq) and seq[slot + 1] == '740' for seq, slot in events)
        before_terminal400 = sum(slot == len(seq) - 2 and seq[-1] == '400' for seq, slot in events)
        before_terminal740 = sum(slot == len(seq) - 2 and seq[-1] == '740' for seq, slot in events)
        terminal = sum(slot == len(seq) - 1 for seq, slot in events)
        closing = sum(closing_member(seq, slot) for seq, slot in events)
        assert closing == terminal + before_terminal400 + before_terminal740
        formula = [(seq, slot) for seq, slot in events
                   if slot >= 2 and seq[slot - 1] == '806' and seq[slot - 2] in FORMULA_FIRST]
        numeral = {}
        for name, signs in [('W001_W005', STROKES_ALL), ('W002_W005', STROKES_TWO_PLUS)]:
            hits = [(seq, slot) for seq, slot in events if slot > 0 and seq[slot - 1] in signs]
            numeral[name] = {
                'tokens_with_immediate_predecessor': len(hits),
                'all_target_tokens_denominator': len(events),
                'rate': len(hits) / len(events) if events else None,
                'distinct_strings': len({seq for seq, _ in hits}),
                'object_families': len({r['object_family_id'] for seq, _ in hits for r in unique[seq]}),
                'length_distribution': dict(sorted(Counter(str(len(seq)) for seq, _ in hits).items())),
            }
        result[code] = {
            'tokens': len(events),
            'distinct_strings': len({seq for seq, _ in events}),
            'complete_faces': len(record_rows),
            'object_families': len({r['object_family_id'] for r in record_rows}),
            'terminal_only': terminal,
            'before_terminal_W400': before_terminal400,
            'before_terminal_W740': before_terminal740,
            'closing_block': closing,
            'closing_block_rate': closing / len(events) if events else None,
            'directly_before_W400_any_slot': following400,
            'directly_before_W740_any_slot': following740,
            'immediate_W806_predecessor': sum(slot > 0 and seq[slot - 1] == '806' for seq, slot in events),
            'immediate_W035_predecessor': sum(slot > 0 and seq[slot - 1] == '035' for seq, slot in events),
            'W465_W475_then_W806_formula': {
                'tokens': len(formula),
                'distinct_strings': len({seq for seq, _ in formula}),
                'terminal_only': sum(slot == len(seq) - 1 for seq, slot in formula),
                'before_terminal_W400': sum(slot == len(seq) - 2 and seq[-1] == '400' for seq, slot in formula),
                'closing_block': sum(closing_member(seq, slot) for seq, slot in formula),
            },
            'immediate_stroke_predecessor': numeral,
        }
    return result


def formula_clusters(unique):
    groups = defaultdict(list)
    for seq in unique:
        for slot, code in enumerate(seq):
            if code not in CONTEXT_TARGETS:
                continue
            prefix = ((START, START) if slot == 0 else (START, seq[0]) if slot == 1
                      else seq[slot - 2:slot])
            groups[prefix].append((seq, slot, code))
    rows = []
    for number, (prefix, events) in enumerate(sorted(groups.items()), 1):
        category = {}
        for code in CONTEXT_TARGETS:
            selected = [(seq, slot) for seq, slot, token in events if token == code]
            if not selected:
                continue
            closing = sum(closing_member(seq, slot) for seq, slot in selected)
            category[code] = {
                'tokens': len(selected),
                'distinct_strings': len({seq for seq, _ in selected}),
                'object_families': len({r['object_family_id'] for seq, _ in selected for r in unique[seq]}),
                'terminal_only': sum(slot == len(seq) - 1 for seq, slot in selected),
                'closing_block': closing,
                'closing_rate': closing / len(selected),
            }
        rows.append({
            'cluster_id': f'C{number:03d}',
            'preceding_pair_classes': [conditional_class(x) for x in prefix],
            'last_predecessor_is_W806': prefix[-1] == '806',
            'first_is_W465_W475_and_last_is_W806': prefix[0] in FORMULA_FIRST and prefix[1] == '806',
            'last_predecessor_in_W001_W005': prefix[-1] in STROKES_ALL,
            'last_predecessor_in_W002_W005': prefix[-1] in STROKES_TWO_PLUS,
            'tokens': len(events),
            'distinct_strings': len({seq for seq, _, _ in events}),
            'categories': category,
        })
    per_code = {}
    for code in CONTEXT_TARGETS:
        support = [row for row in rows if code in row['categories']]
        per_code[code] = {
            'clusters': len(support),
            'tokens': sum(row['categories'][code]['tokens'] for row in support),
            'largest_cluster_tokens': max((row['categories'][code]['tokens'] for row in support), default=0),
            'closing_supporting_clusters': sum(row['categories'][code]['closing_block'] > 0 for row in support),
            'W806_clusters': sum(row['last_predecessor_is_W806'] for row in support),
            'stroke_W001_W005_clusters': sum(row['last_predecessor_in_W001_W005'] for row in support),
            'stroke_W002_W005_clusters': sum(row['last_predecessor_in_W002_W005'] for row in support),
        }
    return {
        'unit': 'Exact two immediately preceding codes, padded with START; category events are tokens in distinct strings.',
        'denominator': 'A cluster is a descriptive formula group, not an established independent archaeological sample. One string can contribute to several clusters.',
        'identity': 'IDs follow lexicographic sorting of the hidden exact preceding pairs. Only class flags are public; reproduce against the pinned local input to recover pairs.',
        'clusters': len(rows), 'per_code': per_code, 'rows': rows,
    }


def substitutions(unique):
    holes = defaultdict(set)
    for seq in unique:
        for slot, code in enumerate(seq):
            holes[seq[:slot] + ('?',) + seq[slot + 1:]].add(code)
    result = {}
    for code in TARGETS:
        selected = [(hole, alternatives) for hole, alternatives in holes.items()
                    if code in alternatives and len(alternatives) > 1]
        alternative_counts = Counter(x for _, alternatives in selected for x in alternatives if x != code)
        lengths = Counter(str(len(hole)) for hole, _ in selected)
        class_relations = Counter(conditional_class(x) for _, alternatives in selected for x in alternatives if x != code)
        class_templates = Counter()
        for _, alternatives in selected:
            class_templates.update({conditional_class(x) for x in alternatives if x != code})
        pair_details = {}
        for alternative in sorted(alternative_counts):
            pair_holes = [hole for hole, alternatives in selected if alternative in alternatives]
            pair_details[alternative] = {
                'templates': len(pair_holes),
                'length_distribution': dict(sorted(Counter(str(len(hole)) for hole in pair_holes).items())),
                'target_slot_distribution': dict(sorted(Counter(
                    'initial' if hole.index('?') == 0 else 'final' if hole.index('?') == len(hole) - 1 else 'medial'
                    for hole in pair_holes).items())),
            }
        result[code] = {
            'templates': len(selected),
            'length_distribution': dict(sorted(lengths.items())),
            'alternative_counts': dict(sorted(alternative_counts.items())),
            'alternative_class_relations': dict(sorted(class_relations.items())),
            'templates_containing_alternative_class': dict(sorted(class_templates.items())),
            'per_alternative': pair_details,
        }
    for left in TARGETS:
        for right in TARGETS:
            assert result[left]['alternative_counts'].get(right, 0) == result[right]['alternative_counts'].get(left, 0)
    return {'definition': 'Whole remaining string, length and target slot held fixed. Aggregate exact templates; no residual template strings are public.',
            'class_scope': 'Classes are the explicitly declared conditional graphic groups; unassigned codes remain other_or_unclassified.',
            'rows': result}


def orientation_and_medial_examples(unique, rows):
    tool_strings = [(seq, rr) for seq, rr in unique.items() if '130' in seq]
    tool_records = []
    for seq, records in sorted(tool_strings, key=lambda x: record_key(min(x[1], key=record_key))):
        representative = min(records, key=record_key)
        slots = [slot for slot, code in enumerate(seq) if code == '130']
        tool_records.append({
            'record_id': representative['record_id'], 'source_cisi': representative['source_cisi'],
            'length': len(seq), 'source_direction': representative['direction'],
            'W035_immediately_before_W130': any(slot > 0 and seq[slot - 1] == '035' for slot in slots),
            'W171_initial': seq[0] == '171', 'W171_terminal': seq[-1] == '171',
        })
    candidates = []
    used_families = set()
    medial = [(seq, rr) for seq, rr in unique.items()
              if any(code == '142' and 0 < slot < len(seq) - 1 for slot, code in enumerate(seq))]
    medial.sort(key=lambda x: (len(x[0]), record_key(min(x[1], key=record_key))))
    for _, rr in medial:
        for row in sorted(rr, key=record_key):
            if row['source_cisi'] in {'-', '', None} or row['object_family_id'] in used_families:
                continue
            candidates.append({'record_id': row['record_id'], 'source_cisi': row['source_cisi']})
            used_families.add(row['object_family_id'])
            break
        if len(candidates) == 3:
            break
    reversals = sum(r['signs_reading_rtl'] == list(reversed(r['signs_visual_ltr'])) for r in rows)
    carrier_candidates = []
    before_comb = [(seq, rr) for seq, rr in unique.items()
                   if len(seq) >= 2 and seq[-2:] == ('158', '400')]
    before_comb.sort(key=lambda x: (len(x[0]), record_key(min(x[1], key=record_key))))
    for _, rr in before_comb:
        eligible = [row for row in rr if row['source_cisi'] not in {'-', '', None}]
        if eligible:
            row = min(eligible, key=record_key)
            carrier_candidates.append({'record_id': row['record_id'], 'source_cisi': row['source_cisi']})
        if len(carrier_candidates) == 3:
            break
    return {
        'source_basis': dict(Counter(r['orientation_basis'] for r in rows)),
        'directions': dict(Counter(r['direction'] for r in rows)),
        'reading_field_equals_reversed_visual_field_faces': reversals,
        'all_faces': len(rows),
        'W130_distinct_strings': len(tool_strings),
        'W130_W035_before_count': sum(r['W035_immediately_before_W130'] for r in tool_records),
        'W130_W035_before_and_terminal_W171_count': sum(r['W035_immediately_before_W130'] and r['W171_terminal'] for r in tool_records),
        'W130_W035_before_and_initial_W171_count': sum(r['W035_immediately_before_W130'] and r['W171_initial'] for r in tool_records),
        'W130_records': tool_records,
        'W142_medial_example_selection': 'Shortest distinct strings with a genuinely medial W142, then source record ID; separate object families, IDs/CISI only.',
        'W142_medial_example_candidates': candidates,
        'W158_before_terminal_W400_example_candidates': carrier_candidates,
    }


def recoding_sensitivity(unique):
    recoded = {tuple(x for code in seq for x in (('G617a', 'G617b') if code == '617' else (code,))) for seq in unique}
    codes = [code for code in TARGETS if code != '617'] + ['G617a', 'G617b']
    pair_rows = [(seq, slot) for seq in recoded for slot in range(len(seq) - 1)
                 if seq[slot:slot + 2] == ('G617a', 'G617b')]
    return {
        'status': 'Constructed encoding sensitivity with two new abstract labels; no new archaeological observations.',
        'original_strings': len(unique), 'recoded_distinct_strings': len(recoded),
        'length_distribution': dict(sorted(Counter(str(len(seq)) for seq in recoded).items())),
        'individual_token_reference': 'Uniform arrangements of the recoded multiset allow the ordered grid pair to separate. The individual-token z scores therefore depend on the constructed tokenization.',
        'position_stats': position_stats(recoded, codes),
        'ordered_pair': {
            'occurrences': len(pair_rows),
            'terminal_pair': sum(slot + 1 == len(seq) - 1 for seq, slot in pair_rows),
            'pair_before_terminal_W400': sum(slot + 1 == len(seq) - 2 and seq[-1] == '400' for seq, slot in pair_rows),
            'pair_before_terminal_W740': sum(slot + 1 == len(seq) - 2 and seq[-1] == '740' for seq, slot in pair_rows),
            'pair_in_closing_block': sum(closing_member(seq, slot + 1) for seq, slot in pair_rows),
            'reference_note': 'An inseparable ordered-pair reference restores the original W617 block lengths and expectations; it is not the independent-token reference above.',
        },
    }


def report(context, positions, clusters, subs, orientation, recoded, contrasts):
    text = ['# Context and encoding audit after the external review', '',
            'This post-outcome audit reuses 1,859 distinct complete reading-order strings from 2,930 faces. It calculates conditional analytic moments and context aggregates; it generates no new permutations. The frozen [protocol](PROTOCOL.json) keeps the two stroke definitions, closing-block rule and formula clusters together. A formula cluster is a descriptive grouping, not a proven independent archaeological observation.', '',
            'The context counts are:', '',
            '| Code | Last token | Closing block | Immediately after W001–W005 | Immediately after W002–W005 | After W806 | W465–W475/W806 formula |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for code in CONTEXT_TARGETS:
        row = context[code]
        n = row['tokens']
        text.append(f"| W{code} | {row['terminal_only']}/{n} | {row['closing_block']}/{n} | {row['immediate_stroke_predecessor']['W001_W005']['tokens_with_immediate_predecessor']}/{n} | {row['immediate_stroke_predecessor']['W002_W005']['tokens_with_immediate_predecessor']}/{n} | {row['immediate_W806_predecessor']}/{n} | {row['W465_W475_then_W806_formula']['tokens']}/{n} |")
    terminal = contrasts['W154_W158_terminal_only']['two_sided_fisher_p']
    block = contrasts['W154_W158_closing_block']['two_sided_fisher_p']
    text += ['', f"W154/W158's terminal-only descriptive Fisher value is {terminal:.9f}; using the declared closing block changes it to {block:.9f}. The difference in attached terminal signs should therefore accompany the earlier terminal-only contrast. W154 and W158 share a W806 formula; W156 has a different profile. Both stroke definitions remain displayed, including any W001 cases.", '',
             '| Code | Final tokens, length 2 | Final tokens, length ≥3 | Expected final, length ≥3 | Analytic final z, length ≥3 |',
             '|---|---:|---:|---:|---:|']
    for code in TARGETS:
        short = positions['length_2']['rows'][code]
        long = positions['length_ge_3']['rows'][code]
        cell = long['positions']['final']
        z = f"{cell['z']:.3f}" if cell['z'] is not None else 'deterministic'
        text.append(f"| W{code} | {short['positions']['final']['observed']}/{short['tokens']} | {cell['observed']}/{long['tokens']} | {cell['expectation']:.3f} | {z} |")
    text += ['', 'These z scores separate two-sign records from longer strings under the same length/multiset reference. They do not supply a partner-controlled ordering model. No new Monte Carlo p values accompany them.', '',
             f"The six carrier/tool categories occupy {clusters['clusters']} distinct preceding-pair clusters. Each cluster's support and closing rate are in [formula-clusters.json](formula-clusters.json), with opaque identities and public class flags. Repeated strings were removed before clustering; shared formulas, moulds and production traditions can still make the category counts dependent.", '',
             '| Code | Exact substitution templates | Length distribution |', '|---|---:|---|']
    for code in TARGETS:
        row = subs['rows'][code]
        lengths = ', '.join(f"{length}: {count}" for length, count in row['length_distribution'].items()) or 'none'
        text.append(f"| W{code} | {row['templates']} | {lengths} |")
    jar = subs['rows']['151']['per_alternative'].get('740', {})
    text += ['', f"The jar W740 substitutes for W151 in {jar.get('templates', 0)} of its {subs['rows']['151']['templates']} exact templates. [Substitution aggregates](substitution-aggregates.json) give every alternative and pairwise length distribution, including W527 and W617. Residual templates are retained only in the local source input.", '',
             f"The W130 orientation check finds {orientation['W130_W035_before_count']} strings with W035 immediately before W130. Of these, {orientation['W130_W035_before_and_terminal_W171_count']} end in W171 and {orientation['W130_W035_before_and_initial_W171_count']} begin with W171. Source IDs and the orientation metadata are in [orientation-and-examples.json](orientation-and-examples.json). The reading-order field is used as supplied; no extra reversal is applied."]
    w142 = positions['all']['rows']['142']['positions']['final']
    candidates = ', '.join(f"{r['record_id']} ({r['source_cisi']})" for r in orientation['W142_medial_example_candidates'])
    text += ['', f"W142 is final in {w142['observed']}/39 tokens, with expectation {w142['expectation']:.3f} and analytic z {w142['z']:.3f}. Genuinely medial candidate records are {candidates}. This output supplies their IDs/CISI only, for later bounded example selection.", '',
             f"Splitting W617 into G617a followed by G617b leaves {recoded['recoded_distinct_strings']} distinct recoded strings. The ordered pair is terminal {recoded['ordered_pair']['terminal_pair']} times and belongs to the declared closing block {recoded['ordered_pair']['pair_in_closing_block']} times. [Encoding sensitivity](W617-recoding.json) reports each abstract token's analytic positions. G617a cannot be last and G617b cannot be first by construction. A tokenwise reference breaks their adjacency; an inseparable-pair reference restores the original block. The grid construction therefore changes the apparent position evidence without adding source observations.", '',
             'The pooled counts and expectations match frozen run-v2, exact substitution counts are symmetric, and the retained terminal Fisher table reproduces. [Verification and hashes](manifest.json) identify every input, calculation file and output.']
    return '\n'.join(text) + '\n'


def main():
    protocol_path = OUT / 'PROTOCOL.json'
    if not protocol_path.exists():
        raise SystemExit('Write the post-outcome protocol before calculating outputs.')
    if any(p.name != 'PROTOCOL.json' for p in OUT.iterdir()):
        raise SystemExit('Refusing to overwrite a populated endpoint.')
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    source = ROOT / protocol['source']['path']
    source_hash = sha(source)
    assert source_hash == protocol['source']['sha256'], 'Pinned source hash differs'
    rows = [json.loads(line) for line in source.read_text(encoding='utf-8').splitlines() if line]
    assert len(rows) == protocol['source']['expected_faces']
    unique = defaultdict(list)
    for row in rows:
        unique[tuple(row['signs_reading_rtl'])].append(row)
    assert len(unique) == protocol['source']['expected_distinct_strings']
    assert TARGETS == protocol['targets'] and CONTEXT_TARGETS == protocol['carrier_and_tool_context_targets']
    assert all(len(seq) >= 2 for seq in unique)
    original_path = HERE / 'run-v2/position-audit.json'
    old = json.loads(original_path.read_text(encoding='utf-8'))
    old_by = {row['code']: row for row in old['rows']}
    observed_codes = {code for seq in unique for code in seq}
    assert observed_codes.issubset(old_by), 'Observed code absent from the frozen inventory'
    all_stats = position_stats(unique, list(old_by))
    for code, row in all_stats.items():
        assert row['tokens'] == old_by[code]['non_singleton_tokens']
        for p in POSITIONS:
            assert row['positions'][p]['observed'] == old_by[code]['positions'][p]['observed']
            assert abs(row['positions'][p]['expectation'] - old_by[code]['positions'][p]['shuffle_expected']) <= 0.000501
    positions = {}
    for name, frame in [('all', list(unique)), ('length_2', [seq for seq in unique if len(seq) == 2]),
                        ('length_ge_3', [seq for seq in unique if len(seq) >= 3])]:
        positions[name] = {'frame_strings': len(frame), 'rows': position_stats(frame, TARGETS)}
    context = context_stats(unique)
    clusters = formula_clusters(unique)
    subs = substitutions(unique)
    orientation = orientation_and_medial_examples(unique, rows)
    recoded = recoding_sensitivity(unique)
    contrasts = {}
    for basis in ['terminal_only', 'closing_block']:
        for left, right in [('154', '158'), ('154', '156'), ('151', '161')]:
            table = [[context[code][basis], context[code]['tokens'] - context[code][basis]] for code in [left, right]]
            contrasts[f'W{left}_W{right}_{basis}'] = fisher_descriptive(table)
    old_robustness_path = HERE / 'run-v2/robustness.json'
    old_robustness = json.loads(old_robustness_path.read_text(encoding='utf-8'))
    old_contrast = next(row for row in old_robustness['variant_contrasts'] if row['left'] == '154' and row['right'] == '158')
    assert contrasts['W154_W158_terminal_only']['table'] == old_contrast['final_nonfinal_table']
    assert math.isclose(contrasts['W154_W158_terminal_only']['two_sided_fisher_p'], old_contrast['two_sided_fisher_p'], abs_tol=1e-12)
    outputs = {
        'context-counts.json': {'unit': 'Target-code tokens in distinct strings; face/family support is separate.', 'rows': context},
        'position-by-length.json': {'reference': 'Analytic within-string multiset moments; no new Monte Carlo p values.', 'frames': positions},
        'formula-clusters.json': clusters,
        'substitution-aggregates.json': subs,
        'orientation-and-examples.json': orientation,
        'W617-recoding.json': recoded,
        'descriptive-contrasts.json': contrasts,
    }
    catalogue_rows = []
    for code in TARGETS:
        row = context[code]
        longer = positions['length_ge_3']['rows'][code]
        final = longer['positions']['final']
        catalogue_rows.append({
            'code': code, 'tokens': row['tokens'],
            'terminal_count': row['terminal_only'],
            'closing_block_count': row['closing_block'],
            'before_terminal_W400_count': row['before_terminal_W400'],
            'before_terminal_W740_count': row['before_terminal_W740'],
            'predecessor_strokes_W001_W005_count': row['immediate_stroke_predecessor']['W001_W005']['tokens_with_immediate_predecessor'],
            'predecessor_strokes_W002_W005_count': row['immediate_stroke_predecessor']['W002_W005']['tokens_with_immediate_predecessor'],
            'predecessor_W806_count': row['immediate_W806_predecessor'],
            'formula_W465_W475_W806_count': row['W465_W475_then_W806_formula']['tokens'],
            'position_length_ge3': {'tokens': longer['tokens'], 'final_count': final['observed'],
                                   'final_expectation': final['expectation'], 'final_z': final['z']},
            'all_position_analytic': positions['all']['rows'][code]['positions'],
            'formula_clusters': clusters['per_code'].get(code),
            'substitutions': subs['rows'][code],
        })
    outputs['catalogue-summary.json'] = {
        'status': 'Post-outcome aggregates; code-token and formula denominators are descriptive.',
        'rows': catalogue_rows,
    }
    report_text = report(context, positions, clusters, subs, orientation, recoded, contrasts)
    for name, value in outputs.items():
        write_json(name, value)
    (OUT / 'REPORT.md').write_text(report_text, encoding='utf-8')
    shutil.copyfile(__file__, OUT / 'context_review.py')
    manifest = {
        'status': 'Verified post-outcome context arithmetic; no new permutations or independent semantic validation.',
        'code': {'path': relative(Path(__file__)), 'sha256': sha(Path(__file__))},
        'inputs': [{'path': relative(path), 'sha256': sha(path)} for path in
                   [source, protocol_path, original_path, old_robustness_path]],
        'frame': {'clean_faces': len(rows), 'object_families': len({r['object_family_id'] for r in rows}),
                  'distinct_strings': len(unique), 'inventory_codes': len(old_by),
                  'codes_present_in_clean_frame': len(observed_codes)},
        'development_note': 'An initial pre-output assertion incorrectly required every inventory code to occur in the clean frame. It was corrected to require every observed code to belong to that inventory; no results had been written and no analytic assumptions changed.',
        'verification': {'pooled_counts_match_run_v2_all_713_codes': True,
                         'pooled_analytic_expectations_match_run_v2': True,
                         'position_token_conservation': True, 'substitution_pair_symmetry': True,
                         'W154_W158_terminal_fisher_matches_run_v2': True},
        'outputs': [{'path': relative(path), 'sha256': sha(path)} for path in sorted(OUT.iterdir()) if path.is_file()],
    }
    write_json('manifest.json', manifest)
    print(json.dumps({'directory': relative(OUT), 'context_counts': [
        {key: row[key] for key in ['code', 'tokens', 'terminal_count', 'closing_block_count',
                                  'predecessor_strokes_W001_W005_count', 'predecessor_strokes_W002_W005_count',
                                  'predecessor_W806_count', 'formula_W465_W475_W806_count']}
        for row in catalogue_rows if row['code'] in CONTEXT_TARGETS],
                      'W154_W158_closing_fisher': contrasts['W154_W158_closing_block'],
                      'orientation_claim': {k: v for k, v in orientation.items() if k.startswith('W130_W035')},
                      'medial_examples': orientation['W142_medial_example_candidates'],
                      'carrier_examples': orientation['W158_before_terminal_W400_example_candidates']}, indent=2))


if __name__ == '__main__':
    main()
