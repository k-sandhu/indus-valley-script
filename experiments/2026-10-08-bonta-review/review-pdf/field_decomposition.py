"""Reviewer decomposition of the canonical field test, using the package's tokenizer and classifier read-only.

Run from the repository root:
    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/field_decomposition.py
Writes field-decomposition.json beside this script. Uses the first frozen mapping's operational code sets
(as hard-coded in pdf_fields.py) and the pinned Lipi clean RTL single-line export (local data/normalized).
"""
import collections, json, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/2026-10-08-bonta-review'))
import pdf_fields as F

rows = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
grouped = collections.defaultdict(list)
for r in rows:
    grouped[r['object_family_id']].append(r)
chosen = [sorted(v, key=lambda r: (-len(r['signs_reading_rtl']), r['record_id']))[0] for v in grouped.values()]
assert len(chosen) == 2469
RANK = {'O': 0, 'F': 1, 'MS': 2}

def m_units(seq_units):
    return [u for u in seq_units if u[0] in RANK]

def canonical_order(units):
    t = [u[0] for u in units]
    return all(RANK[a] <= RANK[b] for a, b in zip(t, t[1:]))

out = {'status': 'Exploratory (reviewer decomposition)'}
# 1. composition of the 942 clean texts
comp = collections.Counter()
for r in chosen:
    seq = r['signs_reading_rtl']
    status, why, fields = F.classify(seq)
    if status == 'clean':
        fs = {f['field'] for f in fields}
        comp['with M field' if 'M' in fs else 'no M field']+=1
        comp['T only (C+T, no M, no P)' if fs <= {'C', 'T'} and 'M' not in fs else 'other'] += 0
out['clean_composition'] = dict(comp)
out['clean_C_T_only_no_M_no_P'] = sum(1 for r in chosen if F.classify(r['signs_reading_rtl'])[0] == 'clean' and {f['field'] for f in F.classify(r['signs_reading_rtl'])[2]} <= {'C', 'T'})

# 2. terminal in penultimate position (admitted by the paper, p. 15) among texts flagged only for terminal position
pen = only = tot = 0
for r in chosen:
    seq = r['signs_reading_rtl']
    status, why, _ = F.classify(seq)
    if 'terminal outside final canonical slot' in why:
        tot += 1
        ti = [i for i, x in enumerate(seq) if x in F.T]
        pen += ti == [len(seq) - 2]
        only += why == ['terminal outside final canonical slot']
out['terminal_outside_final'] = {'texts': tot, 'terminal_penultimate': pen, 'only_reason': only}

# 3. ordering test conditional on content: texts with >= 2 M-field units; fraction in O-F-MS order
def stat(seqs_units):
    n = c = 0
    for units in seqs_units:
        mu = m_units(units)
        if len(mu) >= 2:
            n += 1
            c += canonical_order(mu)
    return n, c

obs_units = [F.tokenize(r['signs_reading_rtl']) for r in chosen]
n_obs, c_obs = stat(obs_units)
rng = random.Random(4242)
fr = []
for _ in range(1999):
    shuffled = []
    for u in obs_units:
        v = u[:]
        rng.shuffle(v)
        shuffled.append(v)
    n, c = stat(shuffled)
    fr.append(c / n if n else 0)
fr_sorted = sorted(fr)
out['ordering_conditional_on_content'] = {'texts_with_two_or_more_M_units': n_obs, 'canonical_O_F_MS_order': c_obs,
    'fraction': c_obs / n_obs, 'unit_shuffle_null_mean_fraction': sum(fr) / len(fr),
    'null_range_95': [fr_sorted[int(.025 * len(fr))], fr_sorted[int(.975 * len(fr))]],
    'add_one_tail': (1 + sum(x >= c_obs / n_obs for x in fr)) / (1 + len(fr)), 'draws': 1999, 'seed': 4242,
    'shuffle_unit': 'tokenized units (fish compounds and MA+033 pairs stay whole) permuted within each text'}

# 4. Jar/arrow position test: share of texts ending in 740/520 observed vs token shuffle
obs_end = sum(r['signs_reading_rtl'][-1] in F.T for r in chosen)
out['texts_ending_in_jar_or_arrow'] = obs_end
(Path(__file__).resolve().parent / 'field-decomposition.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out, indent=1))
