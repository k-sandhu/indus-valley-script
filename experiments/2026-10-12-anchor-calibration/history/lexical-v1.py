"""Study L: lexical windows of the Bonta extension against rearrangements of its own seed values.

The search reimplements experiments/2026-10-08-bonta-extension/analyze.py lexical_search with
cached dictionary queries; verify.py checks it against the original function.
"""
from bisect import bisect_left
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import argparse
import importlib.util
import itertools
import json
import math
import sys
import time

import numpy as np

import common as C

OUT = C.HERE / 'lexical'
LOCAL = C.LOCAL / 'lexical'
BONTA = C.ROOT / 'experiments/2026-10-08-bonta-extension'
N_NULL = 1000
L1_SPAWN, L2_SPAWN, ANNEAL_SPAWN = 11, 12, 13
ANNEAL_STEPS = 6000
RESTARTS = 2
TRACKED = {'233': 'ati', '231': 'sam', '204': 'sa'}


def bonta_modules():
    sys.path.insert(0, str(BONTA))
    import analyze  # noqa: E402  (frozen Bonta extension code)
    import new_anchors  # noqa: E402
    return analyze, new_anchors


A, NA = bonta_modules()
VOWELS, EXCLUDE, normalize = A.VOWELS, A.EXCLUDE, A.normalize


class Lexicon:
    """Monier-Williams headwords indexed by length, for prefix/suffix residual queries."""

    def __init__(self, entries):
        self.modes = {}
        for relaxed, words in [(False, list(entries)), (True, sorted({normalize(w) for w in entries}))]:
            by_len = defaultdict(list)
            for w in words:
                by_len[len(w)].append(w)
            self.modes[relaxed] = {L: (sorted(ws), sorted(w[::-1] for w in ws)) for L, ws in by_len.items()}
        self.cache = {}

    def query(self, pre, suf, relaxed):
        key = (pre, suf, relaxed)
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        lp, ls = len(pre), len(suf)
        found = set()
        for L in range(lp + ls + 1, lp + ls + 7):
            if L not in self.modes[relaxed]:
                continue
            fwd, rev = self.modes[relaxed][L]
            choices = []
            if pre:
                lo, hi = bisect_left(fwd, pre), bisect_left(fwd, pre + '￿')
                choices.append((hi - lo, 'f', lo, hi))
            if suf:
                r = suf[::-1]
                lo, hi = bisect_left(rev, r), bisect_left(rev, r + '￿')
                choices.append((hi - lo, 'r', lo, hi))
            _, side, lo, hi = min(choices)
            pool = fwd[lo:hi] if side == 'f' else [w[::-1] for w in rev[lo:hi]]
            for w in pool:
                if (not pre or w.startswith(pre)) and (not suf or w.endswith(suf)):
                    x = w[lp:L - ls]
                    if set(x) & VOWELS:
                        found.add(x)
        out = frozenset(found)
        self.cache[key] = out
        return out


class Search:
    """Per-assignment lexical search over fixed corpus windows."""

    def __init__(self, unique, lexicon):
        self.unique = unique
        self.lex = lexicon

    def windows(self, values):
        patterns = defaultdict(dict)
        for seq in self.unique:
            for length in (2, 3):
                for start in range(len(seq) - length + 1):
                    window = seq[start:start + length]
                    unknown = [i for i, s in enumerate(window) if s not in values and s not in EXCLUDE]
                    if len(unknown) != 1 or any(s in EXCLUDE for s in window):
                        continue
                    slot = unknown[0]
                    if math.prod(len(values[s]) for i, s in enumerate(window) if i != slot) > 80:
                        continue
                    patterns[window[slot]].setdefault(window, slot)
        return patterns

    def pattern_sets(self, window, slot, values):
        choices = [['?'] if i == slot else values[s] for i, s in enumerate(window)]
        exact, norm, literal = set(), set(), set()
        for parts in itertools.product(*choices):
            pre, suf = ''.join(parts[:slot]), ''.join(parts[slot + 1:])
            raw = self.lex.query(pre, suf, False)
            literal |= raw
            exact |= {normalize(x) for x in raw}
            # The frozen normalization is not idempotent (w->t, t->d), and the original
            # re-normalizes residuals cut from normalized headwords.
            norm |= {normalize(x) for x in self.lex.query(normalize(pre), normalize(suf), True)}
        return exact, norm, literal

    def summarize(self, ps, values):
        cand_any, cand_exact = Counter(), Counter()
        inter = None
        literal = []
        for window, slot in ps.items():
            exact, norm, lit = self.pattern_sets(window, slot, values)
            for x in exact | norm:
                cand_any[x] += 1
            for x in exact:
                cand_exact[x] += 1
            inter = set(norm) if inter is None else inter & norm
            literal.append(lit)
        n = len(ps)
        ranked = sorted(((x, cand_any[x], cand_exact[x], cand_any[x] + 0.5 * cand_exact[x]) for x in cand_any),
                        key=lambda t: (-t[3], len(t[0]), t[0]))
        top = [{'normalized_slot': x, 'context_count': a, 'exact_context_count': e, 'score': s,
                'support_fraction': round(a / n, 4)} for x, a, e, s in ranked[:5]]
        return {'pattern_count': n, 'candidate_classes': len(ranked),
                'full_intersection_classes': len(inter or ()), 'top': top, 'literal_sets': literal}

    def run(self, values):
        patterns = self.windows(values)
        return {u: self.summarize(ps, values) | {'windows': list(ps)} for u, ps in patterns.items()}


def statistics(pref, alt, anchor_holders):
    out = {'searched_unknown_codes': len(pref),
           'multiple_context_codes': sum(r['pattern_count'] >= 2 for r in pref.values()),
           'nonempty_full_intersections_preferred': sum(r['full_intersection_classes'] > 0 for r in pref.values()),
           'nonempty_full_intersections_alternative': sum(r['full_intersection_classes'] > 0 for r in alt.values())}
    added = {u: sum(bool(set(w) & anchor_holders) for w in r['windows']) for u, r in pref.items()}
    out['unknown_codes_in_new_anchor_windows'] = sum(v > 0 for v in added.values())
    out['distinct_new_anchor_windows'] = sum(added.values())
    repeated = 0
    for u, r in pref.items():
        by = {t['normalized_slot']: t for t in alt.get(u, {}).get('top', [])}
        repeated += any(t['normalized_slot'] in by and min(t['exact_context_count'],
                        by[t['normalized_slot']]['exact_context_count']) >= 2 for t in r['top'])
    out['codes_with_repeated_exact_residual_both_scenarios'] = repeated
    out['mean_top_support_fraction'] = float(np.mean([r['top'][0]['support_fraction'] if r['top'] else 0.0
                                                      for r in pref.values()]))
    for code, residual in TRACKED.items():
        r = pref.get(code)
        out[f'W{code}_patterns'] = r['pattern_count'] if r else 0
        out[f'W{code}_top_support'] = r['top'][0]['context_count'] if r and r['top'] else 0
        out[f'W{code}_top_support_fraction'] = r['top'][0]['support_fraction'] if r and r['top'] else 0.0
        out[f'W{code}_literal_{residual}_support'] = sum(residual in s for s in r['literal_sets']) if r else 0
    return out


# --------------------------------------------------------------------------- assignments

def load_inputs():
    inherited, _ = A.import_seeds()
    entries = json.loads((C.ROOT / 'data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json')
                         .read_text(encoding='utf-8'))
    unique = {}
    for line in (C.ROOT / A.INPUTS[1]).read_text(encoding='utf-8').splitlines():
        if line:
            r = json.loads(line)
            unique.setdefault(tuple(r['signs_reading_rtl']), []).append(r)
    pref = NA.seeds_for_scenario(inherited, False)
    alt = NA.seeds_for_scenario(inherited, True)
    vp = {s: sorted({v for r in rs for v in r['slp1']}) for s, rs in pref.items()}
    va = {s: sorted({v for r in rs for v in r['slp1']}) for s, rs in alt.items()}
    seeded = sorted(s for s in vp if vp[s])
    assert seeded == sorted(s for s in va if va[s]) and len(seeded) == 134
    pairs = {s: (tuple(vp[s]), tuple(va[s])) for s in seeded}
    anchors = sorted({c for a in NA.ANCHORS for c in a['codes']})
    assert len(anchors) == 17 and set(anchors) <= set(seeded)
    return entries, list(unique), pairs, anchors


def split_values(pairs):
    return ({s: list(p[0]) for s, p in pairs.items()}, {s: list(p[1]) for s, p in pairs.items()})


def strata_for(unique):
    count = Counter(c for seq in unique for c in seq)
    def bin_of(c):
        n = count[c]
        return -1 if n == 0 else next(b for b, (lo, hi) in enumerate(C.FREQ_BINS) if lo <= n <= hi)
    return bin_of, count


def permute_L1(pairs, bin_of, rng):
    groups = defaultdict(list)
    for s in sorted(pairs):
        groups[bin_of(s)].append(s)
    new = {}
    for members in groups.values():
        perm = rng.permutation(len(members))
        for s, k in zip(members, perm):
            new[s] = pairs[members[k]]
    return new, None


def permute_L2(pairs, anchors, bin_of, count, rng):
    inherited = {s: p for s, p in pairs.items() if s not in anchors}
    pool = defaultdict(list)
    for c in sorted(count):
        if c not in inherited and c not in EXCLUDE:
            pool[bin_of(c)].append(c)
    new = dict(inherited)
    holders = set()
    by_bin = defaultdict(list)
    for a in anchors:
        by_bin[bin_of(a)].append(a)
    for b, members in by_bin.items():
        targets = rng.choice(pool[b], size=len(members), replace=False)
        for a, t in zip(members, targets):
            new[str(t)] = pairs[a]
            holders.add(str(t))
    return new, holders


# --------------------------------------------------------------------------- workers

_S = None
_CTX = None


def _init():
    global _S, _CTX
    entries, unique, pairs, anchors = load_inputs()
    _S = Search(unique, Lexicon(entries))
    bin_of, count = strata_for(unique)
    _CTX = {'pairs': pairs, 'anchors': anchors, 'bin_of': bin_of, 'count': count}


def evaluate_pairs(new_pairs, holders):
    vp, va = split_values(new_pairs)
    pref, alt = _S.run(vp), _S.run(va)
    return statistics(pref, alt, holders)


def null_job(args):
    kind, index, seed = args
    rng = np.random.default_rng(seed)
    if kind == 'L1':
        new, _ = permute_L1(_CTX['pairs'], _CTX['bin_of'], rng)
        anchor_pairs = {_CTX['pairs'][a] for a in _CTX['anchors']}
        # Anchor pairs are distinct from inherited pairs, so holders follow the values.
        holders = {s for s, p in new.items() if p in anchor_pairs}
    else:
        new, holders = permute_L2(_CTX['pairs'], _CTX['anchors'], _CTX['bin_of'], _CTX['count'], rng)
    return {'kind': kind, 'index': index, 'seed': seed, **evaluate_pairs(new, holders)}


class LexAnnealer:
    """Within-stratum swaps of value pairs among seeded codes, with incremental re-search."""

    def __init__(self, objective, rng):
        self.obj_name, self.rng = objective, rng
        self.pairs = dict(_CTX['pairs'])
        groups = defaultdict(list)
        for s in sorted(self.pairs):
            groups[_CTX['bin_of'](s)].append(s)
        self.groups = [g for b, g in groups.items() if b >= 0 and len(g) > 1]
        sizes = np.array([len(g) for g in self.groups], float)
        self.p = sizes / sizes.sum()
        # Candidate windows per unknown code ignore the value-count filter; the seeded set is fixed.
        allvals = {s: ['x'] for s in self.pairs}
        frame = defaultdict(dict)
        for seq in _S.unique:
            for length in (2, 3):
                for start in range(len(seq) - length + 1):
                    window = seq[start:start + length]
                    unknown = [i for i, s in enumerate(window) if s not in allvals and s not in EXCLUDE]
                    if len(unknown) != 1 or any(s in EXCLUDE for s in window):
                        continue
                    frame[window[unknown[0]]].setdefault(window, unknown[0])
        self.frame = frame
        self.affects = defaultdict(set)
        for u, ws in frame.items():
            for w in ws:
                for s in w:
                    if s in self.pairs:
                        self.affects[s].add(u)
        self.vp, self.va = split_values(self.pairs)
        self.state = {u: self.code_state(u) for u in frame}

    def code_state(self, u):
        out = {}
        for name, values in [('pref', self.vp), ('alt', self.va)]:
            ps = {w: slot for w, slot in self.frame[u].items()
                  if math.prod(len(values[s]) for i, s in enumerate(w) if i != slot) <= 80}
            out[name] = _S.summarize(ps, values) if ps else None
        return out

    def code_score(self, st):
        p, a = st['pref'], st['alt']
        if p is None:
            return 0
        if self.obj_name == 'full_intersection':
            return int(p['full_intersection_classes'] > 0)
        by = {t['normalized_slot']: t for t in (a['top'] if a else [])}
        return int(any(t['normalized_slot'] in by and min(t['exact_context_count'],
                       by[t['normalized_slot']]['exact_context_count']) >= 2 for t in p['top']))

    def set_pair(self, s, pair):
        self.pairs[s] = pair
        self.vp[s], self.va[s] = list(pair[0]), list(pair[1])

    def run(self, steps):
        score = {u: self.code_score(st) for u, st in self.state.items()}
        cur = sum(score.values())
        start, best = cur, cur
        best_pairs = dict(self.pairs)
        t0, t1 = 2.0, 0.02
        lr = math.log(t1 / t0)
        accepted = 0
        for step in range(steps):
            temp = t0 * math.exp(lr * step / steps)
            g = self.groups[self.rng.choice(len(self.groups), p=self.p)]
            a, b = g[self.rng.integers(len(g))], g[self.rng.integers(len(g))]
            if a == b or self.pairs[a] == self.pairs[b]:
                continue
            pa, pb = self.pairs[a], self.pairs[b]
            self.set_pair(a, pb); self.set_pair(b, pa)
            touched = self.affects[a] | self.affects[b]
            new_state = {u: self.code_state(u) for u in touched}
            new_score = {u: self.code_score(st) for u, st in new_state.items()}
            delta = sum(new_score.values()) - sum(score[u] for u in touched)
            if delta >= 0 or self.rng.random() < math.exp(delta / temp):
                cur += delta
                accepted += 1
                self.state.update(new_state)
                score.update(new_score)
                if cur > best:
                    best, best_pairs = cur, dict(self.pairs)
            else:
                self.set_pair(a, pa); self.set_pair(b, pb)
        return {'start': start, 'best': best, 'accepted': accepted}, best_pairs


def anneal_job(args):
    objective, restart, seed, steps = args
    rng = np.random.default_rng(seed)
    t0 = time.time()
    ann = LexAnnealer(objective, rng)
    # Start from a within-stratum rearrangement, as in the published-claim tests.
    start_pairs, _ = permute_L1(_CTX['pairs'], _CTX['bin_of'], rng)
    for s, p in start_pairs.items():
        ann.set_pair(s, p)
    ann.state = {u: ann.code_state(u) for u in ann.frame}
    res, best_pairs = ann.run(steps)
    anchor_pairs = {_CTX['pairs'][a] for a in _CTX['anchors']}
    holders = {s for s, p in best_pairs.items() if p in anchor_pairs}
    stats = evaluate_pairs(best_pairs, holders)
    key = ('nonempty_full_intersections_preferred' if objective == 'full_intersection'
           else 'codes_with_repeated_exact_residual_both_scenarios')
    assert stats[key] == res['best'], (stats[key], res['best'])
    moved = sum(best_pairs[s] != _CTX['pairs'][s] for s in best_pairs)
    return {'objective': objective, 'restart': restart, 'seed': seed, 'steps': steps, **res,
            'seeded_codes_moved_from_published': moved, 'seconds': time.time() - t0,
            'statistics': stats, 'pairs': {s: [list(p[0]), list(p[1])] for s, p in sorted(best_pairs.items())}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--anneal-steps', type=int, default=ANNEAL_STEPS)
    args = parser.parse_args()
    if (OUT / 'summary.json').exists() or LOCAL.exists():
        raise SystemExit('Refusing to overwrite an existing endpoint')
    inputs = C.check_pins()
    t0 = time.time()
    _init()
    published = evaluate_pairs(_CTX['pairs'], set(_CTX['anchors']))
    expected = {'searched_unknown_codes': 362, 'unknown_codes_in_new_anchor_windows': 111,
                'distinct_new_anchor_windows': 256, 'multiple_context_codes': 274,
                'nonempty_full_intersections_preferred': 164, 'nonempty_full_intersections_alternative': 158}
    assert all(published[k] == v for k, v in expected.items()), published
    print('published', published, time.time() - t0, flush=True)
    jobs = []
    for kind, spawn in [('L1', L1_SPAWN), ('L2', L2_SPAWN)]:
        seeds = np.random.SeedSequence(C.SEED, spawn_key=(spawn,)).generate_state(N_NULL)
        jobs += [(kind, i, int(s)) for i, s in enumerate(seeds)]
    aseeds = np.random.SeedSequence(C.SEED, spawn_key=(ANNEAL_SPAWN,)).generate_state(2 * RESTARTS)
    anneal_args = [(obj, r, int(aseeds[n * RESTARTS + r]), args.anneal_steps)
                   for n, obj in enumerate(['full_intersection', 'repeated_residual']) for r in range(RESTARTS)]
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as pool:
        anneal_futures = [pool.submit(anneal_job, a) for a in anneal_args]
        draws = list(pool.map(null_job, jobs, chunksize=8))
        anneal = [f.result() for f in anneal_futures]
    print('done', time.time() - t0, flush=True)
    keys = [k for k in published if isinstance(published[k], (int, float))]
    out = {}
    for kind in ['L1', 'L2']:
        ds = [d for d in draws if d['kind'] == kind]
        out[kind] = {}
        for k in keys:
            bound = None
            if kind == 'L1' and k == 'nonempty_full_intersections_preferred':
                bound = max([a['best'] for a in anneal if a['objective'] == 'full_intersection'] + [published[k]])
            if kind == 'L1' and k == 'codes_with_repeated_exact_residual_both_scenarios':
                bound = max([a['best'] for a in anneal if a['objective'] == 'repeated_residual'] + [published[k]])
            out[kind][k] = C.null_summary(published[k], [d[k] for d in ds], bound)
    C.write_json(OUT / 'summary.json', {
        'status': 'Calibration of the frozen October 9 lexical search; outcomes computed after PROTOCOL.md was frozen',
        'protocol_sha256': C.sha(C.HERE / 'PROTOCOL.md'), 'code_sha256': C.sha(__file__), 'inputs': inputs,
        'seeded_codes': len(_CTX['pairs']), 'anchor_codes': ['W' + a for a in _CTX['anchors']],
        'published': published,
        'nulls': {'L1': 'value pairs permuted among the 134 seeded codes within token-count strata',
                  'L2': '17 new-anchor value pairs moved to random non-inherited codes of the same stratum'},
        'draws_per_null': N_NULL, 'seed_entropy': C.SEED, 'spawn_keys': {'L1': L1_SPAWN, 'L2': L2_SPAWN,
                                                                         'anneal': ANNEAL_SPAWN},
        'statistics': out,
        'anneal': [{k: v for k, v in a.items() if k != 'pairs'} for a in anneal],
        'seconds': time.time() - t0})
    C.write_json(OUT / 'annealed-seed-maps.json', {
        'scope': 'Project-generated rearrangements of the published seed values; each code keeps a value pair from its own stratum.',
        'maps': [{'objective': a['objective'], 'restart': a['restart'], 'best': a['best'],
                  'pairs': {'W' + s: p for s, p in a['pairs'].items()}} for a in anneal]})
    LOCAL.mkdir(parents=True, exist_ok=False)
    C.write_json(LOCAL / 'null-draws.json', {'draws': draws})
    print(json.dumps({k: {kk: (vv['published'], round(vv['null_mean'], 3), round(vv['null_sd'], 3), vv['p_at_or_above'])
                          for kk, vv in v.items()} for k, v in out.items()}, indent=1))


if __name__ == '__main__':
    main()
