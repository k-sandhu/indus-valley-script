"""Shared population, strata, splits and role arithmetic for the anchor calibration.

Inputs are read from the repository that holds the tested packages. When this
directory sits in a git worktree without those uncommitted packages, the main
checkout is used (override with IVS_INPUT_ROOT). Outputs go next to this file
and to the ignored local directory of the repository that contains it.
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LOCAL = REPO / 'data/raw/2026-10-12-anchor-calibration'
PROBE = 'experiments/2026-10-12-anchor-expansion/visual/families.json'


def _input_root():
    if os.environ.get('IVS_INPUT_ROOT'):
        return Path(os.environ['IVS_INPUT_ROOT']).resolve()
    if (REPO / PROBE).is_file() and (REPO / 'data/normalized/lipi_clean_rtl_singleline.jsonl').is_file():
        return REPO
    common = subprocess.run(['git', 'rev-parse', '--git-common-dir'], cwd=REPO,
                            capture_output=True, text=True, check=True).stdout.strip()
    root = (REPO / common).resolve().parent
    assert (root / PROBE).is_file(), 'Tested packages not found; set IVS_INPUT_ROOT'
    return root


ROOT = _input_root()

PINNED = {
    'data/normalized/lipi_clean_rtl_singleline.jsonl': '9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8',
    'data/raw/2026-10-12-anchor-expansion/context/run-v2/complete-records.json': '63bfb74e149cf402fd86d5086c4c01199a6591864c13d96d81760c3499ea962f',
    'experiments/2026-10-12-anchor-expansion/visual/families.json': '022db17e93741edb3bba098cbba286a6723c544d64d2bbc19e99c43a4908f6a3',
    'experiments/2026-10-12-anchor-expansion/context/run-v2/summary.json': 'a5eed1c2ee4f73cb4f3bd2e213ff647224c88ff5ad905b4d56ace49f362da4d6',
    'data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json': 'f6c42b48dd7fff724f785572ea66db078fee51f587bde09facda88237e13546a',
    'experiments/2026-10-08-bonta-extension/new_anchors.py': '4c04957f10ba3d902b08d2c708fd3ed21078bf93fe70d4d8808c789acf766a95',
    'experiments/2026-10-08-bonta-extension/analyze.py': '99e660aa91a89c7c6b0e1918d3533372f037c45f56ec7e45331b1f72799fd3ac',
    'experiments/2026-10-08-bonta-review/pdf-2026-10-09-v1/mapping-v1-frozen.json': '500764e176d7ae0e00f635e1ae38f1e3f62b0df55fd115c3100f3a41dbf441b8',
    'data/raw/2026-10-08-bonta-review/pdf-2026-10-09-v1/sign-catalogue-v2.json': 'f5c14d375dda47697392c348eeb2820d56c6611021b618bedcfbb1f794b957d6',
    'experiments/2026-10-11-bonta-adversarial/diagnostics-v3/robustness.json': 'c13010d53d7e6802b2d34e0909fae411e46718132e604caed2141d8f64d01435',
}

SEED = 20261012
# Token-count bins of the published-claim tests (common.py FREQ_BINS).
FREQ_BINS = [(1, 1), (2, 3), (4, 7), (8, 15), (16, 31), (32, 63), (64, 127), (128, 10 ** 9)]
STROKES = frozenset(f'{x:03d}' for x in range(1, 6))
CLOSERS = frozenset({'400', '740'})
ROLES = ['closing', 'counted_entity', 'nonfinal_entity', 'internal_connector', 'opening']
HALF_SALT = 'indus-anchor-calibration-2026-10-12-half-v1'
TOL = 1e-12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_pins():
    bad = {p: sha(ROOT / p) for p, h in PINNED.items() if sha(ROOT / p) != h}
    assert not bad, f'Pinned inputs changed: {bad}'
    return [{'path': p, 'sha256': h} for p, h in PINNED.items()]


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def write_json(path, obj, overwrite=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = 'w' if overwrite else 'x'
    with path.open(mode, encoding='utf-8') as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def record_key(record_id):
    return tuple((0, int(x)) if x.isdigit() else (1, x) for x in re.split(r'(\d+)', str(record_id)) if x)


def half_for(component_id):
    return 'H1' if hashlib.sha256(f'{HALF_SALT}|{component_id}'.encode()).digest()[0] < 128 else 'H2'


def load_strings():
    """Distinct complete strings with closure component, published split and new half."""
    records = read_json('data/raw/2026-10-12-anchor-expansion/context/run-v2/complete-records.json')['records']
    assert len(records) == 2930
    groups = defaultdict(list)
    for r in records:
        groups[tuple(r['complete_codes_reading_rtl'])].append(r)
    strings = []
    for seq, rs in groups.items():
        assert len({r['component_id'] for r in rs}) == 1 and len({r['split'] for r in rs}) == 1
        first = min(rs, key=lambda r: record_key(r['record_id']))
        strings.append({'seq': seq, 'record_id': first['record_id'], 'component_id': first['component_id'],
                        'split': first['split'], 'half': half_for(first['component_id']),
                        'faces': len(rs)})
    strings.sort(key=lambda s: record_key(s['record_id']))
    clean = [json.loads(x) for x in (ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl')
             .read_text(encoding='utf-8').splitlines() if x]
    clean_set = {tuple(r['signs_reading_rtl']) for r in clean if len(r['signs_reading_rtl']) >= 2}
    assert {s['seq'] for s in strings} == clean_set and len(strings) == 1859
    return strings


def strata_of(strings, codes):
    count = Counter(c for s in strings for c in s['seq'])
    out = {}
    for c in codes:
        n = count[c]
        out[c] = -1 if n == 0 else next(b for b, (lo, hi) in enumerate(FREQ_BINS) if lo <= n <= hi)
    return out, count


def role_flags(seq, slot):
    length = len(seq)
    return {
        'closing': slot == length - 1 or (slot == length - 2 and seq[-1] in CLOSERS),
        'counted_entity': slot > 0 and seq[slot - 1] in STROKES,
        'nonfinal_entity': slot < length - 1,
        'internal_connector': 0 < slot < length - 1,
        'opening': slot == 0,
    }


def code_role_expectation(seq, code):
    """Analytic bag-shuffle expectation of matching tokens for one code in one string."""
    counts, length = Counter(seq), len(seq)
    n = counts[code]
    s = sum(counts[c] for c in STROKES)
    k = sum(counts[c] for c in CLOSERS)
    return {
        'opening': n / length,
        'nonfinal_entity': n * (length - 1) / length,
        'internal_connector': n * (length - 2) / length,
        'counted_entity': (n * s - (n if code in STROKES else 0)) / length,
        'closing': n / length + (n * k - (n if code in CLOSERS else 0)) / (length * (length - 1)),
    }


def deletion_keys(t):
    keys = {t}
    for i in range(len(t)):
        keys.add(t[:i] + t[i + 1:])
    return keys


def novel_against(fit, evaluation):
    """Evaluation strings with no fitting string within one edit and not contained in one.

    Same rule as stage3h_novel_transfer.novel_B of the published-claim tests.
    """
    index = defaultdict(set)
    for i, t in enumerate(fit):
        for k in deletion_keys(t):
            index[k].add(i)
    joined = ['|' + '|'.join(t) + '|' for t in fit]
    keep, near, sub = [], 0, 0
    for j, t in enumerate(evaluation):
        close = any(index.get(k) for k in deletion_keys(t))
        s = '|' + '|'.join(t) + '|'
        contained = any(s in x for x in joined)
        near += close
        sub += contained
        if not close and not contained:
            keep.append(j)
    return keep, {'evaluation_strings': len(evaluation), 'within_one_edit': near,
                  'contained_in_fitting_string': sub, 'novel': len(keep)}


def null_summary(observed, draws, bound=None):
    draws = np.asarray(draws, dtype=float)
    mean, sd = float(draws.mean()), float(draws.std(ddof=1))
    out = {'published': observed, 'null_mean': mean, 'null_sd': sd,
           'null_min': float(draws.min()), 'null_max': float(draws.max()),
           'null_q01': float(np.quantile(draws, 0.01)), 'null_q99': float(np.quantile(draws, 0.99)),
           'p_at_or_above': (1 + int((draws >= observed - TOL).sum())) / (1 + len(draws)),
           'share_at_or_above': float((draws >= observed - TOL).mean()),
           'z': (observed - mean) / sd if sd > 0 else None}
    if bound is not None:
        out['bound'] = bound
        out['share_of_achievable_gain'] = (observed - mean) / (bound - mean) if bound > mean else None
    return out


def bh(pvalues):
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty_like(q)
    out[order] = np.minimum(q, 1.0)
    return out.tolist()
