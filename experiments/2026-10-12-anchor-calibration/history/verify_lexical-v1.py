"""Check the cached lexical search against the frozen Bonta lexical_search on several assignments."""
from collections import defaultdict
import time

import numpy as np

import common as C
import lexical as L

OUT = C.HERE / 'lexical/engine-verification.json'


def original(values_by_code, unique, entries):
    """Run the frozen function with seed records carrying the given values."""
    seeds = {s: [{'slp1': list(v)}] for s, v in values_by_code.items()}
    lex, witnesses, _ = L.A.lexical_search({seq: [{'record_id': '', 'object_family_id': ''}] for seq in unique},
                                           seeds, entries)
    return lex, witnesses


def compare(mine, theirs):
    diffs = []
    if set(mine) != set(theirs):
        diffs.append(('codes', len(set(mine) ^ set(theirs))))
    for u in set(mine) & set(theirs):
        a, b = mine[u], theirs[u]
        for k in ['pattern_count', 'candidate_classes', 'full_intersection_classes']:
            if a[k] != b[k]:
                diffs.append((u, k, a[k], b[k]))
        ta = [(t['normalized_slot'], t['context_count'], t['exact_context_count'], t['score'], t['support_fraction'])
              for t in a['top']]
        tb = [(t['normalized_slot'], t['context_count'], t['exact_context_count'], t['score'], t['support_fraction'])
              for t in b['top']]
        if ta != tb:
            diffs.append((u, 'top'))
    return diffs


def main():
    if OUT.exists():
        raise SystemExit('Refusing to overwrite')
    entries, unique, pairs, anchors = L.load_inputs()
    search = L.Search(unique, L.Lexicon(entries))
    bin_of, count = L.strata_for(unique)
    rng = np.random.default_rng(np.random.SeedSequence(C.SEED, spawn_key=(99,)))
    cases = [('published', pairs, set(anchors))]
    for i in range(2):
        new, _ = L.permute_L1(pairs, bin_of, rng)
        anchor_pairs = {pairs[a] for a in anchors}
        cases.append((f'L1-check-{i}', new, {s for s, p in new.items() if p in anchor_pairs}))
    new, holders = L.permute_L2(pairs, anchors, bin_of, count, rng)
    cases.append(('L2-check-0', new, holders))
    rows = []
    for name, assignment, holders in cases:
        vp, va = L.split_values(assignment)
        t0 = time.time()
        mine_p, mine_a = search.run(vp), search.run(va)
        t1 = time.time()
        theirs_p, wit_p = original(vp, unique, entries)
        theirs_a, _ = original(va, unique, entries)
        t2 = time.time()
        # Window lists for the anchor statistics, rebuilt from the original witnesses.
        for u, w in wit_p.items():
            theirs_p[u]['windows'] = [tuple(p['window']) for p in w['patterns']]
            theirs_p[u]['literal_sets'] = [set() for _ in w['patterns']]
        mine_stats = L.statistics(mine_p, mine_a, holders)
        theirs_stats = L.statistics(theirs_p, theirs_a, holders)
        keys = [k for k in mine_stats if not k.endswith('_support') or 'literal' not in k]
        rows.append({'case': name,
                     'preferred_differences': len(compare(mine_p, theirs_p)),
                     'alternative_differences': len(compare(mine_a, theirs_a)),
                     'statistics_equal': all(mine_stats[k] == theirs_stats[k] for k in keys if 'literal' not in k),
                     'statistics': mine_stats, 'cached_seconds': t1 - t0, 'original_seconds': t2 - t1})
        print(rows[-1]['case'], rows[-1]['preferred_differences'], rows[-1]['alternative_differences'],
              rows[-1]['statistics_equal'], round(t1 - t0, 1), round(t2 - t1, 1), flush=True)
    assert all(r['preferred_differences'] == 0 and r['alternative_differences'] == 0 and r['statistics_equal'] for r in rows)
    C.write_json(OUT, {'scope': 'Cached search against the frozen lexical_search: per-code pattern counts, candidate classes, '
                                'full intersections and top-five rankings, and every summary statistic except literal residual support, '
                                'which the original function does not return.',
                       'code_sha256': C.sha(__file__), 'lexical_code_sha256': C.sha(C.HERE / 'lexical.py'),
                       'cases': rows, 'all_equal': True})


if __name__ == '__main__':
    main()
