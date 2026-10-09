"""PDF-review field corrections; reuse the frozen three operational mappings."""
import argparse, collections, functools, random
from pathlib import Path
from pdf_followup import ROOT, OWN, RAW, read, write, sha
from second_coder_sensitivity import Grammar, summary

BASE = OWN / 'pdf-review-response-2026-10-09-v1'
LOCAL = RAW / BASE.name
MAPPINGS = OWN / 'two-coder-2026-10-09-v1'


class TerminalGrammar(Grammar):
    """Same necessary grammar, admitting one final or penultimate terminal."""
    def classify(self, seq, units):
        reasons = []
        terminal = [i for i, code in enumerate(seq) if code in self.terminal]
        junctures = []
        i = 0
        while i < len(seq):
            matching = [p for p in self.junctures if tuple(seq[i:i + len(p)]) == p]
            if matching:
                pattern = max(matching, key=len)
                junctures.append((i, i + len(pattern)))
                i += len(pattern)
            else:
                i += 1
        m = [unit for unit in units if unit[0] in {'O', 'F', 'MS'}]
        anchor = any(u[0] in {'O', 'MS'} for u in units) or any(
            a[0] == b[0] == 'F' for a, b in zip(units, units[1:]))
        if not terminal and not junctures and not anchor:
            return 'indeterminate', ['no discriminating field anchor'], []
        if terminal and not (len(terminal) == 1 and terminal[0] in {len(seq) - 1, len(seq) - 2}):
            reasons.append('terminal outside final or penultimate slot')
        if len(junctures) > 1:
            reasons.append('multiple P-exclusive junctures')
        if anchor and m:
            left, right = m[0][2], m[-1][3]
            if junctures and junctures[-1][0] >= left:
                reasons.append('P-exclusive juncture after M anchor')
            span = [u for u in units if u[2] >= left and u[3] <= right]
            if any(u[0] == 'X' for u in span):
                reasons.append('interrupted canonical M span')
            types = [u[0] for u in span if u[0] != 'A']
            ranks = {'O': 0, 'F': 1, 'MS': 2, 'X': 3}
            if any(ranks[a] > ranks[b] for a, b in zip(types, types[1:])):
                reasons.append('M order differs from O-F-MS')
            f = [u[1] for u in span if u[0] == 'F']
            o = [u[1] for u in span if u[0] == 'O']
            if len(f) > 3:
                reasons.append('more than three F units')
            if len(f) != len(set(f)):
                reasons.append('repeated F unit')
            if len(o) > 2:
                reasons.append('more than two O units')
            if len(o) != len(set(o)):
                reasons.append('repeated O unit')
            if types.count('MS') > 1:
                reasons.append('multiple MS pairs')
        elif m:
            return 'indeterminate', ['fish lexical/measurement role unresolved'], []
        if reasons:
            return 'conflict', sorted(set(reasons)), []
        if any(u[0] == 'A' for u in units):
            return 'indeterminate', ['mapping categories or oval role ambiguous'], []
        fields = []
        boundary = junctures[0][1] if junctures else 0
        if not boundary and anchor and m:
            singles = [i for i, code in enumerate(seq[:m[0][2]]) if code in self.single]
            if len(singles) == 1:
                boundary = singles[0] + 1
        if boundary:
            fields.append({'field': 'P', 'start': 0, 'end': boundary})
        if anchor and m:
            if m[0][2] > boundary:
                return 'indeterminate', ['prefix before M has no certain P boundary'], []
            fields.append({'field': 'M', 'start': m[0][2], 'end': m[-1][3]})
            boundary = m[-1][3]
        end = terminal[0] if terminal else len(seq)
        if end > boundary:
            fields.append({'field': 'C', 'start': boundary, 'end': end})
        if terminal:
            fields.append({'field': 'T', 'start': end, 'end': len(seq)})
        return 'clean', [], fields


def population():
    grouped = collections.defaultdict(list)
    path = ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl'
    for line in path.read_text(encoding='utf-8').splitlines():
        row = __import__('json').loads(line)
        grouped[row['object_family_id']].append(row)
    chosen = [sorted(v, key=lambda r: (-len(r['signs_reading_rtl']), r['record_id']))[0]
              for v in grouped.values()]
    assert len(chosen) == 2469
    return path, chosen


def run(label, output=BASE, local=LOCAL):
    target = output / label / 'field-corrections.json'
    if target.exists():
        raise SystemExit('Field endpoint exists')
    mapping_path = MAPPINGS / f'mapping-{label}.json'
    mapping = read(mapping_path)
    final = Grammar(mapping)
    widened = TerminalGrammar(mapping)
    path, rows = population()
    seqs = [tuple(r['signs_reading_rtl']) for r in rows]
    canonical = collections.Counter()
    updated = collections.Counter()
    composition = collections.Counter()
    transitions = collections.Counter()
    reason_counts = collections.Counter()
    annotations = []
    pen = outside = only_terminal = 0
    for row, seq in zip(rows, seqs):
        status, reasons, fields, _ = final.assess(seq)
        newstatus, newreasons, newfields, _ = widened.assess(seq)
        canonical[status] += 1
        updated[newstatus] += 1
        transitions[f'{status} -> {newstatus}'] += 1
        reason_counts.update(newreasons)
        if 'terminal outside final canonical slot' in reasons:
            outside += 1
            positions = [i for i, code in enumerate(seq) if code in final.terminal]
            pen += positions == [len(seq) - 2]
            only_terminal += reasons == ('terminal outside final canonical slot',)
        if status == 'clean':
            kinds = {f[0] for f in fields}
            composition['with_M' if 'M' in kinds else 'without_M'] += 1
            if kinds <= {'C', 'T'}:
                composition['C_T_without_P_or_M'] += 1
        annotations.append({'record_id': row['record_id'], 'object_family_id': row['object_family_id'],
                            'final_only_status': status, 'widened_status': newstatus,
                            'widened_reasons': list(newreasons), 'widened_fields': list(newfields)})
    # This null follows the review's sign-shuffle sequence exactly.
    rng = random.Random(20261009)
    clean_null = []
    for _ in range(1999):
        count = 0
        for seq in seqs:
            v = list(seq); rng.shuffle(v)
            count += widened.assess(tuple(v))[0] == 'clean'
        clean_null.append(count)
    # M order is measured independently of full canonical classification.
    ranks = {'O': 0, 'F': 1, 'MS': 2}
    def ordered(units):
        m = [u for u in units if u[0] in ranks]
        return len(m) >= 2, all(ranks[a[0]] <= ranks[b[0]] for a, b in zip(m, m[1:]))
    unit_rows = [final.units(seq) for seq in seqs]
    eligible = sum(ordered(u)[0] for u in unit_rows)
    n_ordered = sum(ordered(u)[0] and ordered(u)[1] for u in unit_rows)
    rng = random.Random(4242)
    order_null = []
    for _ in range(1999):
        count = 0
        for units in unit_rows:
            v = units.copy(); rng.shuffle(v)
            ok, in_order = ordered(v)
            count += ok and in_order
        order_null.append(count / eligible)
    payload = {'status': 'Exploratory', 'mapping': label, 'objects': len(rows),
               'source': 'Second-edition manuscript p. 15; terminal environment also p. 57',
               'final_only_frozen_recipe_recount': dict(canonical),
               'widened_terminal': {'classification': dict(updated),
                                    'clean_null': summary(clean_null, updated['clean'])},
               'canonical_clean_composition': dict(composition),
               'final_only_terminal_exclusions': {'texts': outside, 'penultimate': pen,
                                                  'only_terminal_reason': only_terminal},
               'classification_transitions': dict(transitions), 'widened_reason_counts': dict(reason_counts),
               'M_order': {'ordered': n_ordered, 'eligible': eligible,
                           'fraction': n_ordered / eligible,
                           **summary(order_null, n_ordered / eligible),
                           'seed': 4242, 'unit': 'Tokenized units, preserving compounds/pairs'},
               'rules_unchanged': ['P boundary', 'M count/repetition/order', 'ambiguous classes', 'canonical anchor'],
               'repeated_oval_prohibition': 'Operational assumption; manuscript does not explicitly state it.',
               'population_sha256': sha(path), 'mapping_sha256': sha(mapping_path),
               'protocol_sha256': read(BASE / 'registration.json')['protocol_sha256'],
               'reuse': ['second_coder_sensitivity.Grammar', 'review-pdf/field_decomposition.py unit null',
                         'review-pdf/field_penultimate.py one-condition sensitivity']}
    write(target, payload)
    write(local / label / 'field-correction-rows.json', annotations)
    write(local / label / 'field-correction-nulls.json', {'clean': clean_null, 'M_order_fraction': order_null})
    print(label, payload['widened_terminal']['classification'], payload['M_order'])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--mapping', choices=['first', 'second', 'agreed_only'], required=True)
    p.add_argument('--output-dir', default=BASE.name)
    args = p.parse_args()
    output = (OWN / args.output_dir).resolve(); local = (RAW / args.output_dir).resolve()
    if not output.is_relative_to(OWN) or not local.is_relative_to(RAW):
        raise SystemExit('Output outside package')
    run(args.mapping, output, local)
