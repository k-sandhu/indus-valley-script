"""Reviewer measurement: how many benchmark test strings have a training string one sign edit away,
and how much more accurately are their slots restored?

A one-edit neighbor is a training string of the same outer fold that differs from the test string by one
substitution, insertion or deletion.  Identical strings and shared objects are already excluded by the
benchmark's components, so this measures near-variants the split does not treat as dependent.
Saved per-query top-one outcomes are read from the three saved Markov/MKN prediction files.
Aggregates only are written.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import Corpus, ROOT, RAW, old  # noqa: E402
from graph_rules import build  # noqa: E402


def one_edit(a, b):
    la, lb = len(a), len(b)
    if abs(la - lb) > 1 or a == b:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def main():
    c = Corpus()
    rows = c.rows
    n = len(rows)
    fold = [c.assignment[i] for i in range(n)]
    dsu, _ = build(c, min_string_len=1)
    comp_of = {}
    for g, mem in enumerate(c.groups):
        for i in mem:
            comp_of[i] = g
    members = defaultdict(list)
    for i in range(n):
        members[dsu.find(i)].append(i)
    touched = set()
    for m in members.values():
        if len({comp_of[i] for i in m}) > 1:
            for i in m:
                touched.add(i)
    has = np.zeros(n, dtype=bool)
    for f in range(5):
        train = [rows[i]['seq'] for i in range(n) if fold[i] != f]
        for i in range(n):
            if fold[i] == f:
                s = rows[i]['seq']
                has[i] = any(one_edit(s, t) for t in train)
    saved = {}
    for name, path in [('Markov1', ROOT / 'experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl'),
                       ('Markov2', ROOT / 'experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl')]:
        saved[name] = {(s['record_id'], s['slot']): s['top1'] for s in old.read_jsonl(path)}
    mk = {}
    for f in range(5):
        for s in old.read_jsonl(RAW / 'main' / f'classical-f{f}-extra0-outer-c3-queries.jsonl'):
            mk[(s['record_id'], s['slot'])] = s['top1']
    saved['MKN'] = mk
    idx = {r['record_id']: i for i, r in enumerate(rows)}
    out = {'status': 'Exploratory reviewer measurement',
           'strings': n, 'strings_with_a_one_edit_training_neighbor': int(has.sum()),
           'share_of_strings_with_a_one_edit_training_neighbor': float(has.mean()),
           'share_among_touched_strings': float(np.mean([has[i] for i in touched])),
           'share_among_untouched_strings': float(np.mean([has[i] for i in range(n) if i not in touched])),
           'queries_by_neighbor_status': {}}
    for name, table in saved.items():
        a = [v for (rid, slot), v in table.items() if has[idx[rid]]]
        b = [v for (rid, slot), v in table.items() if not has[idx[rid]]]
        out['queries_by_neighbor_status'][name] = {
            'queries_with_neighbor': len(a), 'top1_with_neighbor': float(np.mean(a)),
            'queries_without_neighbor': len(b), 'top1_without_neighbor': float(np.mean(b))}
    (PKG / 'review' / 'neighbor-exposure.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
