"""Reviewer exploratory checks computed from the package's primary rows (coder-a.json). Status: Exploratory.

None of these quantities appears in the package. They use the package's own matching rules and its
primary coding, and answer five questions raised during review:
  1. How many distinct (segments, loops) classes do the 42 Tamil Nadu drawings occupy, and which
     classes does each inventory cover?
  2. What do pooled unrelated inventories (Ogham + Tifinagh) cover?
  3. How do matches change when references are restricted to at most six segments and drawn at a
     common size?
  4. Are the differences between inventories resolved by the 42 paired queries (exact McNemar test)?
  5. How many descriptor classes does each inventory contain under each rule?

Seeds are fixed. Writes review/exploratory.json.
"""
import json
import math
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-06-resemblance-baseline'
HERE = Path(__file__).resolve().parent

INT = 'segments curved loops L T X Y other terminals components dots'.split()
RULES = {'R1': ['segments', 'loops'], 'R2': INT, 'R3': INT + ['symmetry', 'orientation']}

rows = [r for r in json.loads((RAW / 'coder-a.json').read_text(encoding='utf-8')) if r.get('readable', True)]
tam = [r for r in rows if r['inventory'] == 'tamil']
inv = {k: [r for r in rows if r['inventory'] == k] for k in ('indus', 'ogham', 'tifinagh')}


def sig(r, rule):
    return tuple(r[f] for f in RULES[rule])


def covered(refs, rule):
    s = {sig(r, rule) for r in refs}
    return [q['id'] for q in tam if sig(q, rule) in s]


out = {'status': 'Exploratory (reviewer computation from primary rows; not part of the package endpoint)'}

# 1. R1 classes
cls = Counter(sig(q, 'R1') for q in tam)
sup = {k: {sig(r, 'R1') for r in v} for k, v in inv.items()}
out['R1_classes'] = {
    'distinct_classes_among_42_queries': len(cls),
    'rows': [{'segments_loops': list(c), 'queries': n,
              'covered_by': [k for k in sup if c in sup[k]]} for c, n in sorted(cls.items(), key=lambda kv: (-kv[1], kv[0]))],
    'top5_classes_queries': sum(sorted(cls.values(), reverse=True)[:5]),
}

# 2. pooled inventories
pools = {'indus_36': inv['indus'], 'ogham_tifinagh_52': inv['ogham'] + inv['tifinagh'],
         'all_three_88': inv['indus'] + inv['ogham'] + inv['tifinagh']}
out['pooled_coverage'] = {name: {rule: len(covered(refs, rule)) for rule in RULES} for name, refs in pools.items()}
out['pooled_uncovered_R1_queries'] = [q for q in [x['id'] for x in tam] if q not in covered(pools['all_three_88'], 'R1')]

# 3. size-matched draws, 2000 replicates, seed 20261008
rng = random.Random(20261008)


def draws(refs, n, rule):
    v = sorted(len(covered(rng.sample(refs, n), rule)) for _ in range(2000))
    return {'mean': sum(v) / len(v), 'q025': v[49], 'q975': v[1949]}


pool = inv['ogham'] + inv['tifinagh']
out['pooled_unrelated_subsets'] = {str(n): {rule: draws(pool, n, rule) for rule in RULES} for n in (20, 36)}
restricted = {k: [r for r in v if r['segments'] <= 6] for k, v in inv.items()}
out['references_restricted_to_at_most_6_segments'] = {
    'reference_counts': {k: len(v) for k, v in restricted.items()},
    'full_coverage': {k: {rule: len(covered(v, rule)) for rule in RULES} for k, v in restricted.items()},
    'unrestricted_coverage': {k: {rule: len(covered(v, rule)) for rule in RULES} for k, v in inv.items()},
    'size_matched_16': {k: {rule: draws(v, 16, rule) for rule in RULES} for k, v in restricted.items()},
}

# 4. paired exact McNemar tests on the 42 queries
def mcnemar(a, b):
    a, b = set(a), set(b)
    oa, ob = len(a - b), len(b - a)
    n = oa + ob
    k = min(oa, ob)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    return {'only_first': oa, 'only_second': ob, 'exact_two_sided_p': round(p, 4)}


out['paired_tests'] = {}
for rule in RULES:
    h = {k: covered(v, rule) for k, v in inv.items()}
    out['paired_tests'][rule] = {
        'indus_vs_tifinagh': mcnemar(h['indus'], h['tifinagh']),
        'indus_vs_ogham': mcnemar(h['indus'], h['ogham']),
        'tifinagh_vs_ogham': mcnemar(h['tifinagh'], h['ogham']),
    }

# 5. descriptor classes per inventory and rule
out['descriptor_classes'] = {k: {rule: len({sig(r, rule) for r in v}) for rule in RULES} | {'references': len(v)} for k, v in inv.items()}

(HERE / 'exploratory.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps({k: out[k] for k in ('pooled_coverage', 'pooled_uncovered_R1_queries', 'paired_tests', 'descriptor_classes')}, indent=1))
print(json.dumps(out['pooled_unrelated_subsets'], indent=1))
print(json.dumps(out['references_restricted_to_at_most_6_segments'], indent=1))
