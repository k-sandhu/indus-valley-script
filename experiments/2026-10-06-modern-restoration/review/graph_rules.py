"""Reviewer sensitivity of the full-export link count to the string-identity rule.

Rebuilds the object/string graph over the observed export plus the saved benchmark
rows under different minimum lengths for identical-string links, and reports how
many saved components are bridged, how many training strings per outer fold are
linked to the test fold, and which hub strings carry the largest set.  Aggregates
only are written to review/.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from data import Corpus, RAW  # noqa: E402


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, i):
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, i, j):
        a, b = self.find(i), self.find(j)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def build(c, min_string_len, use_objects=True, complete_only=False):
    rows = c.rows
    n_bench = len(rows)
    raw = []
    for r in c.raw:
        seq = tuple(map(str, r.get('signs_reading_rtl', [])))
        fam = str(r.get('object_family_id', r.get('artifact_id', r['record_id'])))
        raw.append((seq, fam, r))
    dsu = DSU(n_bench + len(raw))
    objs, strs = {}, {}

    def attach(i, key, table):
        if key in table:
            dsu.union(i, table[key])
        else:
            table[key] = i

    for i, r in enumerate(rows):
        if use_objects:
            for a in r['artifact_aliases']:
                attach(i, a, objs)
        attach(i, r['seq'], strs)          # benchmark strings are >= 3 signs by construction
    for j, (seq, fam, r) in enumerate(raw):
        i = n_bench + j
        if use_objects:
            attach(i, fam, objs)
        if seq and len(seq) >= min_string_len and (not complete_only or r.get('complete_observed') is True):
            attach(i, seq, strs)
    return dsu, n_bench


def exposure(c, dsu, n_bench):
    rows = c.rows
    fold = [c.assignment[i] for i in range(n_bench)]
    members = defaultdict(list)
    for i in range(n_bench):
        members[dsu.find(i)].append(i)
    comp_of = {}
    for g, mem in enumerate(c.groups):
        for i in mem:
            comp_of[i] = g
    bridged = {rt: m for rt, m in members.items() if len({comp_of[i] for i in m}) > 1}
    out = {'bridged_sets': len(bridged), 'bridged_components': sum(len({comp_of[i] for i in m}) for m in bridged.values()),
           'largest_set_components': max((len({comp_of[i] for i in m}) for m in bridged.values()), default=0),
           'per_fold_linked_training_rows': [], 'per_fold_test_queries_touched': []}
    for f in range(5):
        linked, touched = set(), set()
        for m in bridged.values():
            t = [i for i in m if fold[i] == f]
            tr = [i for i in m if fold[i] != f]
            if t and tr:
                linked.update(tr)
                touched.update(t)
        out['per_fold_linked_training_rows'].append(len(linked))
        out['per_fold_test_queries_touched'].append(sum(len(rows[i]['seq']) for i in touched))
    out['test_queries_touched_total'] = sum(out['per_fold_test_queries_touched'])
    return out


def main():
    c = Corpus()
    result = {'rules': {}}
    for label, kw in [
            ('package rule: objects + identical strings of any length', dict(min_string_len=1)),
            ('objects + identical strings of at least 2 signs', dict(min_string_len=2)),
            ('objects + identical strings of at least 3 signs', dict(min_string_len=3)),
            ('objects + identical strings of at least 4 signs', dict(min_string_len=4)),
            ('objects + identical strings of at least 3 signs, complete faces only', dict(min_string_len=3, complete_only=True)),
            ('identical strings of any length only (no object keys beyond the saved aliases)', dict(min_string_len=1, use_objects=False)),
            ('objects only (no identical strings from non-benchmark faces)', dict(min_string_len=10 ** 6)),
    ]:
        dsu, n = build(c, **kw)
        result['rules'][label] = exposure(c, dsu, n)
    # Hub strings: string keys (from non-benchmark faces) whose faces sit on objects in several saved components.
    rows = c.rows
    comp_of = {}
    for g, mem in enumerate(c.groups):
        for i in mem:
            comp_of[i] = g
    obj_comps = defaultdict(set)
    for i, r in enumerate(rows):
        for a in r['artifact_aliases']:
            obj_comps[a].add(comp_of[i])
    by_string = defaultdict(list)
    for r in c.raw:
        seq = tuple(map(str, r.get('signs_reading_rtl', [])))
        if seq:
            by_string[seq].append(str(r.get('object_family_id', r.get('artifact_id', r['record_id']))))
    hubs = []
    for seq, fams in by_string.items():
        comps = set()
        for fam in fams:
            comps |= obj_comps.get(fam, set())
        if len(comps) >= 2:
            hubs.append({'length': len(seq), 'faces': len(fams), 'saved_components_reached_through_object_keys': len(comps)})
    hubs.sort(key=lambda h: -h['saved_components_reached_through_object_keys'])
    result['strings_whose_faces_reach_two_or_more_saved_components'] = {
        'count': len(hubs), 'by_length': dict(sorted(Counter(min(h['length'], 6) for h in hubs).items())),
        'top_10_by_components_reached': hubs[:10]}
    (PKG / 'review' / 'graph-rule-sensitivity.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
