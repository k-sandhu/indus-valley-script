"""Reviewer analysis of the full-export links between benchmark components.

Independent of the package's own union-find: builds a key graph (object keys and
string keys) with typed edges, then reports (1) what the bridging faces are,
(2) how many benchmark test queries each outer fold touches through them, and
(3) how those links split across folds.  Aggregates only are written to review/;
record-level detail goes to the local raw review-tmp directory.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
from data import Corpus, ROOT, RAW  # noqa: E402

TMP = RAW / 'review-tmp'
TMP.mkdir(exist_ok=True)


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


def main():
    c = Corpus()
    rows = c.rows
    n_bench = len(rows)
    bench_ids = {r['record_id'] for r in rows}
    # Raw faces that are not themselves benchmark representatives.
    raw = []
    for r in c.raw:
        seq = tuple(map(str, r.get('signs_reading_rtl', [])))
        fam = str(r.get('object_family_id', r.get('artifact_id', r['record_id'])))
        raw.append({'id': r['record_id'], 'seq': seq, 'family': fam, 'raw': r})
    raw_ids = {x['id'] for x in raw}
    benchmark_in_raw = len(bench_ids & raw_ids)
    # Nodes: benchmark rows [0, n_bench), raw faces [n_bench, n_bench+len(raw)).
    # Benchmark representatives are also present as raw faces (same record_id); keep both,
    # because the package's graph does too, and they join through the shared keys.
    nodes = n_bench + len(raw)
    dsu = DSU(nodes)
    obj_first, str_first = {}, {}
    edges_by_type = Counter()

    def attach(i, key, table, label):
        if key in table:
            if dsu.find(i) != dsu.find(table[key]):
                edges_by_type[label] += 1
            dsu.union(i, table[key])
        else:
            table[key] = i

    for i, r in enumerate(rows):
        for a in r['artifact_aliases']:
            attach(i, a, obj_first, 'object')
        attach(i, r['seq'], str_first, 'string')
    for j, x in enumerate(raw):
        i = n_bench + j
        attach(i, x['family'], obj_first, 'object')
        if x['seq']:
            attach(i, x['seq'], str_first, 'string')

    # Benchmark-only components (the saved ones) from the package's own groups.
    comp_of_row = {}
    for g, members in enumerate(c.groups):
        for i in members:
            comp_of_row[i] = g
    fold_of_row = {i: c.assignment[i] for i in range(n_bench)}
    # Full-graph component for each benchmark row.
    root_of_row = [dsu.find(i) for i in range(n_bench)]
    members_by_root = defaultdict(list)
    for i, rt in enumerate(root_of_row):
        members_by_root[rt].append(i)
    # Sets in which more than one saved benchmark component meets.
    bridged = {}
    for rt, mem in members_by_root.items():
        comps = {comp_of_row[i] for i in mem}
        if len(comps) > 1:
            bridged[rt] = {'rows': mem, 'components': comps}
    summary = {
        'benchmark_rows': n_bench, 'saved_components': len(c.groups),
        'raw_faces': len(raw), 'benchmark_rows_present_as_raw_faces': benchmark_in_raw,
        'bridged_full_graph_sets': len(bridged),
        'bridged_sets_component_counts': sorted([len(v['components']) for v in bridged.values()], reverse=True),
        'bridged_sets_row_counts': sorted([len(v['rows']) for v in bridged.values()], reverse=True),
        'bridged_components_total': sum(len(v['components']) for v in bridged.values()),
        'bridged_rows_total': sum(len(v['rows']) for v in bridged.values()),
        'bridged_queries_total': sum(len(rows[i]['seq']) for v in bridged.values() for i in v['rows']),
    }
    # Per-fold exposure: for fold f, test rows in a bridged set that also holds a training row.
    per_fold = []
    touched_rows_all = set()
    for f in range(5):
        train_linked, test_touched = set(), set()
        for rt, v in bridged.items():
            tests = [i for i in v['rows'] if fold_of_row[i] == f]
            trains = [i for i in v['rows'] if fold_of_row[i] != f]
            if tests and trains:
                train_linked.update(trains)
                test_touched.update(tests)
        touched_rows_all |= test_touched
        per_fold.append({
            'fold': f,
            'test_rows': sum(1 for i in range(n_bench) if fold_of_row[i] == f),
            'test_queries': sum(len(rows[i]['seq']) for i in range(n_bench) if fold_of_row[i] == f),
            'linked_training_rows': len(train_linked),
            'linked_training_tokens': sum(len(rows[i]['seq']) for i in train_linked),
            'test_rows_touched': len(test_touched),
            'test_queries_touched': sum(len(rows[i]['seq']) for i in test_touched),
            'training_rows': sum(1 for i in range(n_bench) if fold_of_row[i] != f),
        })
    summary['per_fold'] = per_fold
    summary['test_queries_touched_total'] = sum(p['test_queries_touched'] for p in per_fold)
    summary['test_rows_touched_total'] = sum(p['test_rows_touched'] for p in per_fold)
    summary['test_queries_total'] = sum(p['test_queries'] for p in per_fold)
    # Sizes of a giant set: folds it spans.
    giant = max(bridged.values(), key=lambda v: len(v['components']))
    summary['largest_set'] = {
        'components': len(giant['components']), 'rows': len(giant['rows']),
        'queries': sum(len(rows[i]['seq']) for i in giant['rows']),
        'rows_per_fold': dict(Counter(fold_of_row[i] for i in giant['rows'])),
        'row_length_distribution': dict(sorted(Counter(len(rows[i]['seq']) for i in giant['rows']).items())),
    }
    # What are the non-benchmark faces inside bridged sets?
    bridged_roots = set(bridged)
    kinds = Counter()
    reasons = Counter()
    length_hist = Counter()
    sets_with_faces = defaultdict(int)
    detail = []
    for j, x in enumerate(raw):
        i = n_bench + j
        rt = dsu.find(i)
        if rt not in bridged_roots:
            continue
        r = x['raw']
        is_bench = x['id'] in bench_ids
        if is_bench:
            kinds['benchmark_row_copy'] += 1
            continue
        sets_with_faces[rt] += 1
        seq = x['seq']
        if not seq:
            why = 'empty'
        elif len(seq) < 3:
            why = 'too_short(<3)'
        elif r.get('complete_observed') is not True:
            why = 'incomplete'
        elif r.get('single_line') is False:
            why = 'multiline'
        elif r.get('has_unknown_sign') or r.get('has_blank_space') or any(s in {'000', '999', 'P000', '?'} for s in seq):
            why = 'unknown_or_blank'
        elif r.get('max_damage', 0) or r.get('max_uncertainty', 0):
            why = 'damaged_or_uncertain'
        elif tuple(seq) in {rr['seq'] for rr in rows}:
            why = 'duplicate_of_benchmark_string'
        else:
            why = 'other_eligible'
        reasons[why] += 1
        length_hist[min(len(seq), 6)] += 1
        kinds['non_benchmark_face'] += 1
        detail.append({'id': x['id'], 'why': why, 'length': len(seq), 'family': x['family'], 'root': rt})
    summary['faces_in_bridged_sets'] = dict(kinds)
    summary['non_benchmark_face_reasons'] = dict(reasons)
    summary['non_benchmark_face_length_hist(6=6+)'] = dict(sorted(length_hist.items()))

    # How do two saved components end up in one set?  Count mechanisms by examining, for every
    # non-benchmark face in a bridged set, the saved components touched by its object key
    # and by its string key (via benchmark rows only).
    obj_to_comps, str_to_comps = defaultdict(set), defaultdict(set)
    for i, r in enumerate(rows):
        for a in r['artifact_aliases']:
            obj_to_comps[a].add(comp_of_row[i])
        str_to_comps[r['seq']].add(comp_of_row[i])
    direct = Counter()
    by_id = {x['id']: x for x in raw}
    for d in detail:
        x = by_id[d['id']]
        oc = obj_to_comps.get(x['family'], set())
        sc = str_to_comps.get(x['seq'], set()) if x['seq'] else set()
        both = oc | sc
        if len(both) >= 2:
            if oc and sc and not (oc & sc):
                direct['object_key_and_string_key_reach_different_saved_components'] += 1
            elif len(oc) >= 2:
                direct['object_key_reaches_two_or_more_saved_components'] += 1
            elif len(sc) >= 2:
                direct['string_key_reaches_two_or_more_saved_components'] += 1
            else:
                direct['other_two_component_link'] += 1
        elif len(both) == 1:
            direct['face_touches_exactly_one_saved_component'] += 1
        else:
            direct['face_touches_no_saved_component_directly'] += 1
    summary['direct_bridge_mechanism_counts_for_non_benchmark_faces'] = dict(direct)

    # How many distinct families / strings hold the giant set together?
    giant_root = root_of_row[giant['rows'][0]]
    summary['largest_set_non_benchmark_faces'] = sum(1 for d in detail if d['root'] == giant_root)
    summary['largest_set_non_benchmark_faces_by_reason'] = dict(Counter(d['why'] for d in detail if d['root'] == giant_root))

    # Sign-level overlap: do linked training strings resemble the test strings?
    def ngrams(seq, k):
        return {tuple(seq[i:i + k]) for i in range(len(seq) - k + 1)}
    train_by_fold = {f: [i for i in range(n_bench) if fold_of_row[i] != f] for f in range(5)}
    linked_by_fold = {}
    for f in range(5):
        linked = set()
        for rt, v in bridged.items():
            tests = [i for i in v['rows'] if fold_of_row[i] == f]
            trains = [i for i in v['rows'] if fold_of_row[i] != f]
            if tests and trains:
                linked.update(trains)
        linked_by_fold[f] = linked
    max_bi_linked, max_bi_unlinked = [], []
    for f in range(5):
        for t in range(n_bench):
            if fold_of_row[t] != f or t not in touched_rows_all:
                continue
            tb = ngrams(rows[t]['seq'], 2)
            # Linked training rows in the same full-graph set.
            same = [i for i in members_by_root[root_of_row[t]] if fold_of_row[i] != f]
            best_linked = max((len(tb & ngrams(rows[i]['seq'], 2)) / max(1, len(tb)) for i in same), default=0.0)
            others = [i for i in train_by_fold[f] if i not in linked_by_fold[f]]
            best_other = max((len(tb & ngrams(rows[i]['seq'], 2)) / max(1, len(tb)) for i in others), default=0.0)
            max_bi_linked.append(best_linked)
            max_bi_unlinked.append(best_other)
    import statistics
    summary['bigram_overlap_of_touched_test_strings'] = {
        'touched_test_rows': len(max_bi_linked),
        'mean_best_bigram_coverage_by_linked_training_row': statistics.mean(max_bi_linked) if max_bi_linked else None,
        'mean_best_bigram_coverage_by_any_unlinked_training_row': statistics.mean(max_bi_unlinked) if max_bi_unlinked else None,
        'share_with_full_bigram_coverage_by_one_linked_row': sum(x >= 1.0 for x in max_bi_linked) / max(1, len(max_bi_linked)),
        'share_with_full_bigram_coverage_by_one_unlinked_row': sum(x >= 1.0 for x in max_bi_unlinked) / max(1, len(max_bi_unlinked)),
    }
    (PKG / 'review' / 'graph-links-summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    (TMP / 'graph-links-detail.json').write_text(json.dumps({'faces': detail, 'touched_rows': sorted(touched_rows_all)}, indent=1), encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'per_fold'}, indent=1))
    print(json.dumps(per_fold, indent=1))


if __name__ == '__main__':
    main()
