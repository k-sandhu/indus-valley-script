"""Study L: lexical windows of the Bonta extension against rearrangements of its own seed values.

The search reimplements experiments/2026-10-08-bonta-extension/analyze.py lexical_search with
cached dictionary queries and cached per-window residual sets; verify_lexical.py checks it
against the original function. Stages run separately and each refuses to overwrite its output:

    python lexical.py nulls     # L1 and L2 permutation draws
    python lexical.py anneal    # achievable-fit bound by within-stratum swaps
    python lexical.py summary   # combine into lexical/summary.json
"""
from bisect import bisect_left
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import argparse
import heapq
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
PUBLISHED = {'searched_unknown_codes': 362, 'unknown_codes_in_new_anchor_windows': 111,
             'distinct_new_anchor_windows': 256, 'multiple_context_codes': 274,
             'nonempty_full_intersections_preferred': 164, 'nonempty_full_intersections_alternative': 158}


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
        """Residuals x (1-6 letters, with a vowel) such that pre + x + suf is a headword."""
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
        raw = frozenset(found)
        # The frozen normalization is not idempotent (w->t, t->d); the original normalizes
        # every residual, including residuals cut from normalized headwords.
        out = (raw, frozenset(normalize(x) for x in raw))
        self.cache[key] = out
        return out


class Search:
    """Per-assignment lexical search over fixed corpus windows."""

    def __init__(self, unique, lexicon):
        self.unique = unique
        self.lex = lexicon
        self.pcache = {}

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
        """(exact canonical, normalized canonical, literal raw) residual sets of one window."""
        key = (window, slot, tuple(tuple(values[s]) if i != slot else None for i, s in enumerate(window)))
        hit = self.pcache.get(key)
        if hit is not None:
            return hit
        choices = [['?'] if i == slot else values[s] for i, s in enumerate(window)]
        exact, norm, literal = set(), set(), set()
        for parts in itertools.product(*choices):
            pre, suf = ''.join(parts[:slot]), ''.join(parts[slot + 1:])
            raw, canon = self.lex.query(pre, suf, False)
            literal |= raw
            exact |= canon
            norm |= self.lex.query(normalize(pre), normalize(suf), True)[1]
        out = (frozenset(exact), frozenset(norm), frozenset(literal))
        if len(self.pcache) > 600_000:
            self.pcache.clear()
        self.pcache[key] = out
        return out

    def summarize(self, ps, values):
        cand_any, cand_exact = Counter(), Counter()
        inter = None
        literal = []
        for window, slot in ps.items():
            exact, norm, lit = self.pattern_sets(window, slot, values)
            cand_any.update(exact | norm)
            cand_exact.update(exact)
            inter = set(norm) if inter is None else inter & norm
            literal.append(lit)
        return finish(len(ps), cand_any, cand_exact, len(inter or ())) | {'literal_sets': literal}

    def run(self, values):
        patterns = self.windows(values)
        return {u: self.summarize(ps, values) | {'windows': list(ps)} for u, ps in patterns.items()}


def top_five(n, cand_any, cand_exact):
    # Incremental counters can hold zero entries between cleanups; they are not candidates.
    live = [x for x, v in cand_any.items() if v > 0]
    best = heapq.nsmallest(5, live, key=lambda x: (-(cand_any[x] + 0.5 * cand_exact[x]), len(x), x))
    return [{'normalized_slot': x, 'context_count': cand_any[x], 'exact_context_count': cand_exact[x],
             'score': cand_any[x] + 0.5 * cand_exact[x], 'support_fraction': round(cand_any[x] / n, 4)} for x in best]


def finish(n, cand_any, cand_exact, inter_size):
    return {'pattern_count': n, 'candidate_classes': len(cand_any), 'full_intersection_classes': inter_size,
            'top': top_five(n, cand_any, cand_exact)}


def repeated(pref_top, alt_top):
    by = {t['normalized_slot']: t for t in alt_top}
    return any(t['normalized_slot'] in by and min(t['exact_context_count'],
               by[t['normalized_slot']]['exact_context_count']) >= 2 for t in pref_top)


def statistics(pref, alt, anchor_holders):
    out = {'searched_unknown_codes': len(pref),
           'multiple_context_codes': sum(r['pattern_count'] >= 2 for r in pref.values()),
           'nonempty_full_intersections_preferred': sum(r['full_intersection_classes'] > 0 for r in pref.values()),
           'nonempty_full_intersections_alternative': sum(r['full_intersection_classes'] > 0 for r in alt.values())}
    added = {u: sum(bool(set(w) & anchor_holders) for w in r['windows']) for u, r in pref.items()}
    out['unknown_codes_in_new_anchor_windows'] = sum(v > 0 for v in added.values())
    out['distinct_new_anchor_windows'] = sum(added.values())
    out['codes_with_repeated_exact_residual_both_scenarios'] = sum(
        repeated(r['top'], alt.get(u, {}).get('top', [])) for u, r in pref.items())
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


def anchor_holders(pairs, assignment, anchors):
    # Anchor pairs differ from every inherited pair, so holders follow the values.
    anchor_pairs = {pairs[a] for a in anchors}
    return {s for s, p in assignment.items() if p in anchor_pairs}


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
        holders = anchor_holders(_CTX['pairs'], new, _CTX['anchors'])
    else:
        new, holders = permute_L2(_CTX['pairs'], _CTX['anchors'], _CTX['bin_of'], _CTX['count'], rng)
    return {'kind': kind, 'index': index, 'seed': seed, **evaluate_pairs(new, holders)}


class Scenario:
    """Incremental per-code counters for one scenario's values, over a fixed window frame."""

    def __init__(self, frame, values):
        self.frame, self.values = frame, values
        self.inc = {u: {} for u in frame}
        self.any = {u: Counter() for u in frame}
        self.exact = {u: Counter() for u in frame}
        self.normc = {u: Counter() for u in frame}
        for u, ws in frame.items():
            for w, slot in ws.items():
                self.refresh(u, w, slot)

    def refresh(self, u, w, slot):
        old = self.inc[u].pop(w, None)
        if old is not None:
            self.any[u].subtract(old[0] | old[1])
            self.exact[u].subtract(old[0])
            self.normc[u].subtract(old[1])
        if math.prod(len(self.values[s]) for i, s in enumerate(w) if i != slot) <= 80:
            exact, norm, _ = _S.pattern_sets(w, slot, self.values)
            self.inc[u][w] = (exact, norm)
            self.any[u].update(exact | norm)
            self.exact[u].update(exact)
            self.normc[u].update(norm)

    def clean(self, u):
        for c in (self.any[u], self.exact[u], self.normc[u]):
            for x in [x for x, v in c.items() if v == 0]:
                del c[x]

    def has_intersection(self, u):
        n = len(self.inc[u])
        return n > 0 and any(v == n for v in self.normc[u].values())

    def top(self, u):
        n = len(self.inc[u])
        return top_five(n, self.any[u], self.exact[u]) if n else []


class LexAnnealer:
    """Within-stratum swaps of value pairs among seeded codes, with incremental re-search."""

    def __init__(self, objective, rng, start_pairs):
        self.obj_name, self.rng = objective, rng
        self.pairs = dict(start_pairs)
        groups = defaultdict(list)
        for s in sorted(self.pairs):
            groups[_CTX['bin_of'](s)].append(s)
        self.groups = [g for b, g in groups.items() if b >= 0 and len(g) > 1]
        sizes = np.array([len(g) for g in self.groups], float)
        self.p = sizes / sizes.sum()
        # The seeded set is fixed, so candidate windows are fixed; the value-count filter is not.
        frame = defaultdict(dict)
        for seq in _S.unique:
            for length in (2, 3):
                for start in range(len(seq) - length + 1):
                    window = seq[start:start + length]
                    unknown = [i for i, s in enumerate(window) if s not in self.pairs and s not in EXCLUDE]
                    if len(unknown) != 1 or any(s in EXCLUDE for s in window):
                        continue
                    frame[window[unknown[0]]].setdefault(window, unknown[0])
        self.frame = frame
        self.windows_of = defaultdict(set)
        for u, ws in frame.items():
            for w, slot in ws.items():
                for s in w:
                    if s in self.pairs:
                        self.windows_of[s].add((u, w, slot))
        self.vp, self.va = split_values(self.pairs)
        self.sc = {'pref': Scenario(frame, self.vp)}
        if objective == 'repeated_residual':
            self.sc['alt'] = Scenario(frame, self.va)

    def code_score(self, u):
        p = self.sc['pref']
        if self.obj_name == 'full_intersection':
            return int(p.has_intersection(u))
        if not p.inc[u]:
            return 0
        return int(repeated(p.top(u), self.sc['alt'].top(u)))

    def set_pair(self, s, pair):
        self.pairs[s] = pair
        self.vp[s][:] = pair[0]
        self.va[s][:] = pair[1]

    def apply_swap(self, a, b):
        pa, pb = self.pairs[a], self.pairs[b]
        self.set_pair(a, pb)
        self.set_pair(b, pa)
        touched = self.windows_of[a] | self.windows_of[b]
        for sc in self.sc.values():
            for u, w, slot in touched:
                sc.refresh(u, w, slot)
        return {u for u, _, _ in touched}

    def total(self):
        return sum(self.code_score(u) for u in self.frame)

    def run(self, steps):
        score = {u: self.code_score(u) for u in self.frame}
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
            us = self.apply_swap(a, b)
            new = {u: self.code_score(u) for u in us}
            delta = sum(new.values()) - sum(score[u] for u in us)
            if delta >= 0 or self.rng.random() < math.exp(delta / temp):
                cur += delta
                accepted += 1
                score.update(new)
                if cur > best:
                    best, best_pairs = cur, dict(self.pairs)
            else:
                self.apply_swap(a, b)
            if step % 500 == 0:
                for sc in self.sc.values():
                    for u in self.frame:
                        sc.clean(u)
        return {'start': start, 'best': best, 'accepted': accepted, 'final': cur}, best_pairs


def anneal_job(args):
    objective, restart, seed, steps = args
    rng = np.random.default_rng(seed)
    t0 = time.time()
    # Start from a within-stratum rearrangement, as in the published-claim tests.
    start_pairs, _ = permute_L1(_CTX['pairs'], _CTX['bin_of'], rng)
    ann = LexAnnealer(objective, rng, start_pairs)
    res, best_pairs = ann.run(steps)
    stats = evaluate_pairs(best_pairs, anchor_holders(_CTX['pairs'], best_pairs, _CTX['anchors']))
    key = ('nonempty_full_intersections_preferred' if objective == 'full_intersection'
           else 'codes_with_repeated_exact_residual_both_scenarios')
    assert stats[key] == res['best'], (stats[key], res['best'])
    moved = sum(best_pairs[s] != _CTX['pairs'][s] for s in best_pairs)
    return {'objective': objective, 'restart': restart, 'seed': seed, 'steps': steps, **res,
            'seeded_codes_moved_from_published': moved, 'seconds': time.time() - t0,
            'statistics': stats, 'pairs': {s: [list(p[0]), list(p[1])] for s, p in sorted(best_pairs.items())}}


# --------------------------------------------------------------------------- stages

def stage_nulls(workers):
    target = LOCAL / 'null-draws.json'
    if target.exists() or (OUT / 'null-manifest.json').exists():
        raise SystemExit('Refusing to overwrite an existing endpoint')
    inputs = C.check_pins()
    t0 = time.time()
    _init()
    published = evaluate_pairs(_CTX['pairs'], set(_CTX['anchors']))
    assert all(published[k] == v for k, v in PUBLISHED.items()), published
    jobs = []
    for kind, spawn in [('L1', L1_SPAWN), ('L2', L2_SPAWN)]:
        seeds = np.random.SeedSequence(C.SEED, spawn_key=(spawn,)).generate_state(N_NULL)
        jobs += [(kind, i, int(s)) for i, s in enumerate(seeds)]
    with ProcessPoolExecutor(max_workers=workers, initializer=_init) as pool:
        draws = list(pool.map(null_job, jobs, chunksize=10))
    C.write_json(target, {'draws': draws})
    C.write_json(OUT / 'null-manifest.json', {
        'status': 'Null draws complete; values are local', 'code_sha256': C.sha(__file__),
        'protocol_sha256': C.sha(C.HERE / 'PROTOCOL.md'), 'inputs': inputs, 'published': published,
        'draws_per_null': N_NULL, 'seed_entropy': C.SEED, 'spawn_keys': {'L1': L1_SPAWN, 'L2': L2_SPAWN},
        'local_sha256': C.sha(target), 'seconds': time.time() - t0})
    print('nulls done', time.time() - t0, flush=True)


def stage_anneal(workers, steps):
    target = OUT / 'anneal.json'
    if target.exists():
        raise SystemExit('Refusing to overwrite an existing endpoint')
    t0 = time.time()
    aseeds = np.random.SeedSequence(C.SEED, spawn_key=(ANNEAL_SPAWN,)).generate_state(2 * RESTARTS)
    jobs = [(obj, r, int(aseeds[n * RESTARTS + r]), steps)
            for n, obj in enumerate(['full_intersection', 'repeated_residual']) for r in range(RESTARTS)]
    with ProcessPoolExecutor(max_workers=workers, initializer=_init) as pool:
        runs = list(pool.map(anneal_job, jobs))
    C.write_json(target, {'status': 'Achievable-fit bound by within-stratum swaps of seed value pairs',
                          'code_sha256': C.sha(__file__), 'seed_entropy': C.SEED, 'spawn_key': ANNEAL_SPAWN,
                          'runs': runs, 'seconds': time.time() - t0})
    print('anneal done', time.time() - t0, [(r['objective'], r['start'], r['best']) for r in runs], flush=True)


def stage_summary():
    if (OUT / 'summary.json').exists():
        raise SystemExit('Refusing to overwrite an existing endpoint')
    manifest = json.loads((OUT / 'null-manifest.json').read_text(encoding='utf-8'))
    draws = json.loads((LOCAL / 'null-draws.json').read_text(encoding='utf-8'))['draws']
    anneal = json.loads((OUT / 'anneal.json').read_text(encoding='utf-8'))['runs']
    published = manifest['published']
    keys = [k for k in published if isinstance(published[k], (int, float))]
    bounds = {'nonempty_full_intersections_preferred': 'full_intersection',
              'codes_with_repeated_exact_residual_both_scenarios': 'repeated_residual'}
    out = {}
    for kind in ['L1', 'L2']:
        ds = [d for d in draws if d['kind'] == kind]
        assert len(ds) == N_NULL
        out[kind] = {}
        for k in keys:
            bound = None
            if kind == 'L1' and k in bounds:
                bound = max([a['best'] for a in anneal if a['objective'] == bounds[k]] + [published[k]])
            out[kind][k] = C.null_summary(published[k], [d[k] for d in ds], bound)
    C.write_json(OUT / 'summary.json', {
        'status': 'Calibration of the frozen October 9 lexical search; outcomes computed after PROTOCOL.md was frozen',
        'protocol_sha256': C.sha(C.HERE / 'PROTOCOL.md'), 'code_sha256': C.sha(__file__),
        'inputs': manifest['inputs'], 'seeded_codes': 134,
        'anchor_codes': ['W' + a for a in sorted({c for a in NA.ANCHORS for c in a['codes']})],
        'published': published,
        'nulls': {'L1': 'value pairs permuted among the 134 seeded codes within token-count strata',
                  'L2': '17 new-anchor value pairs moved to random non-inherited codes of the same stratum'},
        'draws_per_null': N_NULL, 'seed_entropy': C.SEED,
        'spawn_keys': {'L1': L1_SPAWN, 'L2': L2_SPAWN, 'anneal': ANNEAL_SPAWN},
        'statistics': out,
        'anneal': [{k: v for k, v in a.items() if k != 'pairs'} for a in anneal]})
    C.write_json(OUT / 'annealed-seed-maps.json', {
        'scope': 'Project-generated rearrangements of the published seed values; each code keeps a value pair from its own stratum.',
        'maps': [{'objective': a['objective'], 'restart': a['restart'], 'best': a['best'],
                  'pairs': {'W' + s: p for s, p in a['pairs'].items()}} for a in anneal]})
    print(json.dumps({k: {kk: (vv['published'], round(vv['null_mean'], 3), round(vv['null_sd'], 3),
                               vv['p_at_or_above'], vv.get('bound')) for kk, vv in v.items()} for k, v in out.items()},
                     indent=1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['nulls', 'anneal', 'summary'])
    parser.add_argument('--workers', type=int, default=12)
    parser.add_argument('--steps', type=int, default=ANNEAL_STEPS)
    args = parser.parse_args()
    if args.stage == 'nulls':
        stage_nulls(args.workers)
    elif args.stage == 'anneal':
        stage_anneal(args.workers, args.steps)
    else:
        stage_summary()


if __name__ == '__main__':
    main()
