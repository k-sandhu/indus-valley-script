"""Reviewer leakage audit of the training sets actually fitted in each outer fold.

Independent re-derivation of the extra-text selection from the protocol (candidate rule,
full-graph closure of the held-out strings, one face per string), compared with the
package's own selection, followed by direct tests of every fitted training row:
  * no training row or extra face shares an object key or an identical string with a test row;
  * no extra face lies in the full-graph closure of a test row;
  * secondary probes: other identifier fields, contiguous-substring relations between
    extra strings and test strings.
Aggregates only are written.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import Corpus, UNKNOWN  # noqa: E402
from graph_rules import build  # noqa: E402


def contains(long, short):
    n, m = len(long), len(short)
    return m <= n and any(long[i:i + m] == short for i in range(n - m + 1))


def main():
    c = Corpus()
    rows = c.rows
    n = len(rows)
    dsu, _ = build(c, min_string_len=1)
    raw = c.raw
    bench_strings = {r['seq'] for r in rows}
    # Independent candidate rule, written from PROTOCOL.md "Extra text and exclusions".
    def seq_of(r):
        return tuple(map(str, r.get('signs_reading_rtl', [])))
    candidates = []
    for j, r in enumerate(raw):
        seq = seq_of(r)
        if not seq:
            continue
        if r.get('complete_observed') is not True or r.get('has_blank_space') or r.get('has_unknown_sign'):
            continue
        if any(s in {'000', '999', 'P000', '?', UNKNOWN} for s in seq):
            continue
        if r.get('max_damage', 0) or r.get('max_uncertainty', 0):
            continue
        if seq in bench_strings:
            continue
        candidates.append(j)
    result = {'status': 'Exploratory reviewer analysis', 'independent_candidate_faces': len(candidates),
              'package_candidate_faces': len(c.candidates), 'folds': []}
    result['candidate_sets_match_package'] = {r['record_id'] for r in c.candidates} == {raw[j]['record_id'] for j in candidates}
    for f in range(5):
        train, test, extra, detail = c.outer(f)
        test_idx = [i for i in range(n) if c.assignment[i] == f]
        test_roots = {dsu.find(i) for i in test_idx}
        # Independent selection of extra faces.
        retained = [j for j in candidates if dsu.find(n + j) not in test_roots]
        retained.sort(key=lambda j: str(raw[j]['record_id']))
        chosen = {}
        for j in retained:
            chosen.setdefault(seq_of(raw[j]), j)
        mine = {raw[j]['record_id'] for j in chosen.values()}
        theirs = {r['record_id'] for r in extra}
        # Test-side keys.
        test_alias = {a for i in test_idx for a in rows[i]['artifact_aliases']}
        test_strings = {rows[i]['seq'] for i in test_idx}
        # Benchmark training rows.
        train_alias_hits = sum(1 for r in train if set(r['artifact_aliases']) & test_alias)
        train_string_hits = sum(1 for r in train if r['seq'] in test_strings)
        # Extra faces actually fitted.
        extra_family_hits = sum(1 for r in extra if str(r.get('object_family_id', r.get('artifact_id', r['record_id']))) in test_alias)
        extra_string_hits = sum(1 for r in extra if r['seq'] in test_strings)
        extra_root_hits = 0
        by_id = {r['record_id']: j for j, r in enumerate(raw)}
        for r in extra:
            if dsu.find(n + by_id[r['record_id']]) in test_roots:
                extra_root_hits += 1
        # Contiguous-substring relations (length >= 3 on the shorter side).
        contained_in_test = contains_test = 0
        for r in extra:
            if len(r['seq']) >= 3:
                if any(contains(t, r['seq']) for t in test_strings):
                    contained_in_test += 1
                if any(contains(r['seq'], t) for t in test_strings):
                    contains_test += 1
        # Baseline: the same relations for benchmark training strings.
        train_contained_in_test = sum(1 for r in train if any(contains(t, r['seq']) for t in test_strings))
        train_contains_test = sum(1 for r in train if any(contains(r['seq'], t) for t in test_strings))
        # Test rows whose exact string occurs inside some extra string (any length >= 3 test string).
        extra_seqs = [r['seq'] for r in extra]
        test_inside_extra = sum(1 for t in test_strings if any(contains(e, t) for e in extra_seqs))
        result['folds'].append({
            'fold': f, 'test_rows': len(test_idx), 'training_rows': len(train), 'extra_faces_fitted': len(extra),
            'independent_selection_equals_package_selection': mine == theirs,
            'training_rows_sharing_an_alias_with_a_test_row': train_alias_hits,
            'training_rows_with_an_identical_string_to_a_test_row': train_string_hits,
            'extra_faces_with_object_key_of_a_test_row': extra_family_hits,
            'extra_faces_with_identical_string_to_a_test_row': extra_string_hits,
            'extra_faces_in_full_graph_closure_of_test_rows': extra_root_hits,
            'extra_strings_len3plus_contained_in_a_test_string': contained_in_test,
            'extra_strings_len3plus_containing_a_test_string': contains_test,
            'benchmark_training_strings_contained_in_a_test_string': train_contained_in_test,
            'benchmark_training_strings_containing_a_test_string': train_contains_test,
            'test_strings_contained_in_an_extra_string': test_inside_extra,
        })
    # Inner allocations: fitted rows and extra faces versus validation + test rows.
    inner_checks = []
    for f in range(5):
        test_idx = [i for i in range(n) if c.assignment[i] == f]
        test_ids = {rows[i]['record_id'] for i in test_idx}
        by_id = {r['record_id']: j for j, r in enumerate(raw)}
        for k, (fit, val, more, detail) in enumerate(c.inner(f)):
            held = [r for r in rows if r['record_id'] in test_ids] + val
            held_alias = {a for r in held for a in r['artifact_aliases']}
            held_strings = {r['seq'] for r in held}
            held_ids = {r['record_id'] for r in held}
            held_roots = {dsu.find(i) for i, r in enumerate(rows) if r['record_id'] in held_ids}
            inner_checks.append({
                'outer': f, 'inner': k, 'fit_rows': len(fit), 'validation_rows': len(val), 'extra_faces': len(more),
                'fit_rows_sharing_alias_or_string_with_validation_or_test': sum(1 for r in fit if (set(r['artifact_aliases']) & held_alias) or r['seq'] in held_strings),
                'extra_faces_with_alias_or_string_of_validation_or_test': sum(1 for r in more if str(r.get('object_family_id', r.get('artifact_id', r['record_id']))) in held_alias or r['seq'] in held_strings),
                'extra_faces_in_full_graph_closure_of_validation_or_test': sum(1 for r in more if dsu.find(n + by_id[r['record_id']]) in held_roots)})
    result['inner_allocations'] = {
        'allocations_checked': len(inner_checks),
        'total_fit_rows_sharing_alias_or_string_with_held_rows': sum(x['fit_rows_sharing_alias_or_string_with_validation_or_test'] for x in inner_checks),
        'total_extra_faces_with_alias_or_string_of_held_rows': sum(x['extra_faces_with_alias_or_string_of_validation_or_test'] for x in inner_checks),
        'total_extra_faces_in_closure_of_held_rows': sum(x['extra_faces_in_full_graph_closure_of_validation_or_test'] for x in inner_checks),
        'fit_rows_range': [min(x['fit_rows'] for x in inner_checks), max(x['fit_rows'] for x in inner_checks)],
        'extra_faces_range': [min(x['extra_faces'] for x in inner_checks), max(x['extra_faces'] for x in inner_checks)]}
    # Other identifier fields: do any object identifiers outside object_family_id join faces?
    ident = defaultdict(set)
    for r in raw:
        md = r.get('metadata', {})
        for key in ['excavation-idno']:
            v = md.get(key)
            if v not in (None, '', '-', '--'):
                ident[(md.get('site'), key, v)].add(str(r.get('object_family_id')))
    multi = [k for k, v in ident.items() if len(v) > 1]
    result['same_site_and_excavation_idno_under_different_object_families'] = {
        'identifiers_checked': len(ident), 'identifiers_with_two_or_more_object_families': len(multi)}
    # Do those identifiers cross a fold boundary between a test row and a training/extra row?
    fam_fold = defaultdict(set)
    for i, r in enumerate(rows):
        for a in r['artifact_aliases']:
            fam_fold[a].add(c.assignment[i])
    crossing = 0
    for k in multi:
        folds = set()
        for fam in ident[k]:
            folds |= fam_fold.get(fam, set())
        if len(folds) > 1:
            crossing += 1
    result['same_site_and_excavation_idno_under_different_object_families']['of_which_benchmark_strings_fall_in_different_folds'] = crossing
    (PKG / 'review' / 'leak-audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=1))


if __name__ == '__main__':
    main()
