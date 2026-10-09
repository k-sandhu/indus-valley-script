"""Reviewer sensitivity: admit a jar/arrow in penultimate position (PDF p. 15: final or penultimate).

Copies the package classifier's logic read-only (imports pdf_fields.tokenize) and changes one condition.
From the repository root:
    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/field_penultimate.py
"""
import collections, json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/2026-10-08-bonta-review'))
import pdf_fields as F

def classify(seq, allow_penultimate):
    u = F.tokenize(seq); reasons = []
    terminal = [i for i, x in enumerate(seq) if x in F.T]
    juncture = [i for i, x in enumerate(seq) if x in {'002', '060'}]
    m = [x for x in u if x[0] in {'O', 'F', 'MS'}]
    anchor = any(x[0] in {'O', 'MS'} for x in u) or any(a[0] == b[0] == 'F' for a, b in zip(u, u[1:]))
    if not terminal and not juncture and not anchor: return 'indeterminate'
    ok = [len(seq) - 1] + ([len(seq) - 2] if allow_penultimate else [])
    if terminal and not (len(terminal) == 1 and terminal[0] in ok): reasons.append('terminal')
    if len(juncture) > 1: reasons.append('multi-J')
    if anchor and m:
        left, right = m[0][2], m[-1][3]
        if juncture and juncture[-1] >= left: reasons.append('J after M')
        span = [x for x in u if x[2] >= left and x[3] <= right]
        if any(x[0] == 'X' for x in span): reasons.append('interrupted')
        types = [x[0] for x in span if x[0] != 'A']
        ranks = {'O': 0, 'F': 1, 'MS': 2, 'X': 3}
        if any(ranks[a] > ranks[b] for a, b in zip(types, types[1:])): reasons.append('order')
        f = [x[1] for x in span if x[0] == 'F']; o = [x[1] for x in span if x[0] == 'O']
        if len(f) > 3: reasons.append('F>3')
        if len(f) != len(set(f)): reasons.append('F repeat')
        if len(o) > 2: reasons.append('O>2')
        if len(o) != len(set(o)): reasons.append('O repeat')
        if types.count('MS') > 1: reasons.append('MS>1')
    elif m: return 'indeterminate'
    if reasons: return 'conflict'
    if any(x[0] == 'A' for x in u): return 'indeterminate'
    boundary = juncture[0] + 1 if juncture else 0
    if not boundary and anchor and m:
        singles = [i for i, c in enumerate(seq[:m[0][2]]) if c == '001']
        if len(singles) == 1: boundary = singles[0] + 1
    if anchor and m and m[0][2] > boundary: return 'indeterminate'
    return 'clean'

rows = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
grouped = collections.defaultdict(list)
for r in rows: grouped[r['object_family_id']].append(r)
chosen = [sorted(v, key=lambda r: (-len(r['signs_reading_rtl']), r['record_id']))[0] for v in grouped.values()]
out = {'status': 'Exploratory (reviewer sensitivity)', 'objects': len(chosen)}
for name, allow in (('package_rule_reimplemented', False), ('penultimate_admitted', True)):
    c = collections.Counter(classify(r['signs_reading_rtl'], allow) for r in chosen)
    rng = random.Random(20261009); null = []
    for _ in range(1999):
        n = 0
        for r in chosen:
            s = r['signs_reading_rtl'].copy(); rng.shuffle(s); n += classify(s, allow) == 'clean'
        null.append(n)
    ss = sorted(null)
    out[name] = {'classification': dict(c), 'null_mean_clean': sum(null) / len(null), 'null_range_95': [ss[int(.025 * len(ss))], ss[int(.975 * len(ss))]],
                 'add_one_tail': (1 + sum(x >= c['clean'] for x in null)) / (1 + len(null))}
(Path(__file__).resolve().parent / 'field-penultimate.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out, indent=1))
