"""Reviewer probe: are the linked training strings near-variants of the touched test strings?

For each touched test string (a test string in a bridged full-graph set that also holds a
training string), compare its closest linked training string with the closest string in
random, equally sized samples of unlinked training strings from the same outer fold.
Similarity measures: Levenshtein distance over sign sequences and shared contiguous
trigrams.  Aggregates only are written.
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
from data import Corpus  # noqa: E402
from graph_rules import build  # noqa: E402


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def trigrams(s):
    return {s[i:i + 3] for i in range(len(s) - 2)}


def main(draws=30):
    c = Corpus()
    rows = c.rows
    n = len(rows)
    dsu, _ = build(c, min_string_len=1)
    fold = [c.assignment[i] for i in range(n)]
    comp_of = {}
    for g, mem in enumerate(c.groups):
        for i in mem:
            comp_of[i] = g
    members = defaultdict(list)
    for i in range(n):
        members[dsu.find(i)].append(i)
    bridged = [m for m in members.values() if len({comp_of[i] for i in m}) > 1]
    rng = np.random.default_rng(20261006)
    out = {'status': 'Exploratory reviewer analysis', 'random_draws': draws, 'touched_rows': 0}
    linked_d, linked_tri, linked_best_norm = [], [], []
    ctrl_d = [[] for _ in range(draws)]
    ctrl_tri = [[] for _ in range(draws)]
    ctrl_norm = [[] for _ in range(draws)]
    for f in range(5):
        train = [i for i in range(n) if fold[i] != f]
        linked, touched = set(), set()
        for m in bridged:
            t = [i for i in m if fold[i] == f]
            tr = [i for i in m if fold[i] != f]
            if t and tr:
                linked.update(tr)
                touched.update(t)
        unlinked = [i for i in train if i not in linked]
        samples = [list(rng.choice(unlinked, size=len(linked), replace=False)) for _ in range(draws)]
        for t in sorted(touched):
            s = rows[t]['seq']
            ts = trigrams(s)
            # Only training strings of its own full-graph set count as "linked" for this test string.
            own = [i for i in members[dsu.find(t)] if fold[i] != f]
            dmin = min(lev(s, rows[i]['seq']) for i in own)
            linked_d.append(dmin)
            linked_best_norm.append(max(1 - lev(s, rows[i]['seq']) / max(len(s), len(rows[i]['seq'])) for i in own))
            linked_tri.append(int(any(ts & trigrams(rows[i]['seq']) for i in own)))
            for k, sample in enumerate(samples):
                pool = [i for i in sample]
                ctrl_d[k].append(min(lev(s, rows[i]['seq']) for i in pool))
                ctrl_norm[k].append(max(1 - lev(s, rows[i]['seq']) / max(len(s), len(rows[i]['seq'])) for i in pool))
                ctrl_tri[k].append(int(any(ts & trigrams(rows[i]['seq']) for i in pool)))
    out['touched_rows'] = len(linked_d)
    summary = lambda v: float(np.mean(v))
    out['linked_training_strings_of_the_same_set'] = {
        'share_with_a_string_at_edit_distance_1_or_less': summary([d <= 1 for d in linked_d]),
        'share_with_a_string_at_edit_distance_2_or_less': summary([d <= 2 for d in linked_d]),
        'share_sharing_a_contiguous_trigram': summary(linked_tri),
        'mean_best_normalized_similarity': summary(linked_best_norm),
    }
    ctrl = lambda arrs, fn: [fn(a) for a in arrs]
    out['equal_size_random_unlinked_samples_same_fold'] = {
        'share_with_a_string_at_edit_distance_1_or_less_mean_and_sd': [float(np.mean([np.mean([d <= 1 for d in a]) for a in ctrl_d])), float(np.std([np.mean([d <= 1 for d in a]) for a in ctrl_d], ddof=1))],
        'share_with_a_string_at_edit_distance_2_or_less_mean_and_sd': [float(np.mean([np.mean([d <= 2 for d in a]) for a in ctrl_d])), float(np.std([np.mean([d <= 2 for d in a]) for a in ctrl_d], ddof=1))],
        'share_sharing_a_contiguous_trigram_mean_and_sd': [float(np.mean([np.mean(a) for a in ctrl_tri])), float(np.std([np.mean(a) for a in ctrl_tri], ddof=1))],
        'mean_best_normalized_similarity_mean_and_sd': [float(np.mean([np.mean(a) for a in ctrl_norm])), float(np.std([np.mean(a) for a in ctrl_norm], ddof=1))],
    }
    (PKG / 'review' / 'neighbor-probe.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
