"""Study R: role coherence of the anchor-expansion family map against its own rearrangements.

Null: family labels permuted among the 673 assigned codes within sign-frequency strata.
Bounds: exact linear assignment for additive statistics (R2, R3), swap annealing for R1 and R5.
Transfer: exact R3 fit on one half of closure components, scored on the other half.
"""
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import math
import time

import numpy as np
from scipy import sparse
from scipy.optimize import linear_sum_assignment

import common as C

OUT = C.HERE / 'roles'
LOCAL = C.LOCAL / 'roles'
N_NULL = 1000
ANNEAL_STEPS = 1_000_000
RESTARTS = 4
FAMILY_SPAWN, ANNEAL_SPAWN, ROLEFIT_SPAWN = 1, 2, 3


# --------------------------------------------------------------------------- tables

class Tables:
    """Per-code, per-string token, match and expectation tables for the five roles."""

    def __init__(self):
        fam = C.read_json('experiments/2026-10-12-anchor-expansion/visual/families.json')
        self.families = [{'id': f['family_id'], 'codes': sorted(f['codes']), 'role': f['role_predictions']}
                         for f in fam['rows']]
        self.fid = [f['id'] for f in self.families]
        self.frole = [f['role'] for f in self.families]
        self.constrained = [i for i, r in enumerate(self.frole) if r != 'unconstrained']
        prior = C.read_json('experiments/2026-10-11-bonta-adversarial/run-v6/catalogue-data.json')
        self.codes = sorted(r['code'] for r in prior['rows'])
        assert len(self.codes) == 713
        self.ci = {c: i for i, c in enumerate(self.codes)}
        self.strings = C.load_strings()
        self.seqs = [s['seq'] for s in self.strings]
        nC, nS = len(self.codes), len(self.seqs)
        N = np.zeros((nC, nS))
        M = {r: np.zeros((nC, nS)) for r in C.ROLES}
        E = {r: np.zeros((nC, nS)) for r in C.ROLES}
        for j, seq in enumerate(self.seqs):
            for slot, code in enumerate(seq):
                i = self.ci[code]
                N[i, j] += 1
                for r, ok in C.role_flags(seq, slot).items():
                    M[r][i, j] += ok
            for code in set(seq):
                for r, e in C.code_role_expectation(seq, code).items():
                    E[r][self.ci[code], j] = e
        self.N, self.M, self.E = N, M, E
        self.Ns = sparse.csr_matrix(N)
        self.B = sparse.csr_matrix((N > 0).astype(float))
        self.Fail = {r: sparse.csr_matrix(N - M[r]) for r in C.ROLES}
        self.strata, self.count = C.strata_of(self.strings, self.codes)
        self.label0 = np.full(nC, -1)
        for k, f in enumerate(self.families):
            for c in f['codes']:
                assert self.label0[self.ci[c]] == -1
                self.label0[self.ci[c]] = k
        self.assigned = np.flatnonzero(self.label0 >= 0)
        assert len(self.assigned) == 673
        groups = defaultdict(list)
        for i in self.assigned:
            groups[self.strata[self.codes[i]]].append(int(i))
        self.groups = {b: np.array(v) for b, v in sorted(groups.items())}
        self.masks = {'all': np.ones(nS, bool)}
        for key, values in [('split', ['discovery', 'transfer']), ('half', ['H1', 'H2'])]:
            for v in values:
                self.masks[v] = np.array([s[key] == v for s in self.strings])
        h1 = [self.seqs[j] for j in np.flatnonzero(self.masks['H1'])]
        h2 = [self.seqs[j] for j in np.flatnonzero(self.masks['H2'])]
        self.novel_info = {}
        for name, fit, ev, evmask in [('H2_novel', h1, h2, 'H2'), ('H1_novel', h2, h1, 'H1')]:
            keep, info = C.novel_against(fit, ev)
            idx = np.flatnonzero(self.masks[evmask])[keep]
            m = np.zeros(nS, bool)
            m[idx] = True
            self.masks[name] = m
            self.novel_info[name] = info
        self.code_frame = {name: self.frame_tables(mask) for name, mask in self.masks.items()}

    def frame_tables(self, mask):
        w = mask.astype(float)
        t = {'n': self.N @ w, 's': (self.N > 0).astype(float) @ w}
        for r in C.ROLES:
            t['m_' + r] = self.M[r] @ w
            t['e_' + r] = self.E[r] @ w
            t['x_' + r] = t['m_' + r] - t['e_' + r]
        return t

    def role_index(self, labels, froles=None):
        froles = froles or self.frole
        out = np.full(len(self.codes), -1)
        ok = labels >= 0
        out[ok] = [C.ROLES.index(froles[k]) if froles[k] != 'unconstrained' else -1 for k in labels[ok]]
        return out

    def code_value(self, frame, key):
        """Matrix codes x roles of a per-code frame quantity, e.g. 'x' excess or 'm' matches."""
        t = self.code_frame[frame]
        return np.stack([t[f'{key}_{r}'] for r in C.ROLES], axis=1)

    def code_pass(self):
        if getattr(self, '_pass', None) is not None:
            return self._pass
        a, d, t = self.code_frame['all'], self.code_frame['discovery'], self.code_frame['transfer']
        P = np.zeros((len(self.codes), len(C.ROLES)), bool)
        for k, r in enumerate(C.ROLES):
            P[:, k] = ((a['s'] >= 5) & (d['n'] > 0) & (t['n'] > 0)
                       & (d['x_' + r] > C.TOL) & (t['x_' + r] > C.TOL))
        self._pass = P
        return P


# --------------------------------------------------------------------------- statistics

def membership(T, labels):
    rows = labels[labels >= 0]
    cols = np.flatnonzero(labels >= 0)
    return sparse.csr_matrix((np.ones(len(cols)), (rows, cols)), shape=(len(T.families), len(T.codes)))


def evaluate(T, labels, froles=None, frames=('all', 'discovery', 'transfer', 'H1', 'H2', 'H1_novel', 'H2_novel')):
    froles = froles or T.frole
    ridx = T.role_index(labels, froles)
    A = membership(T, labels)
    out = {'families': {}}
    constrained = [k for k, r in enumerate(froles) if r != 'unconstrained']
    for frame in frames:
        t = T.code_frame[frame]
        m = np.zeros(len(T.families))
        e = np.zeros(len(T.families))
        for k in constrained:
            members = np.flatnonzero(labels == k)
            r = froles[k]
            m[k] = t['m_' + r][members].sum()
            e[k] = t['e_' + r][members].sum()
        n = A @ t['n']
        out['families'][frame] = {'m': m, 'e': e, 'n': n}
        out[f'R3_{frame}'] = float((m - e)[constrained].sum())
        out[f'positive_families_{frame}'] = int(sum((n[k] > 0) and (m[k] - e[k] > C.TOL) for k in constrained))
    contain = np.asarray(((A @ T.B) > 0).sum(axis=1)).ravel()
    out['containing'] = contain
    if 'discovery' in out['families'] and 'transfer' in out['families']:
        fd, ft = out['families']['discovery'], out['families']['transfer']
        passes = [k for k in constrained if contain[k] >= 5 and fd['n'][k] > 0 and ft['n'][k] > 0
                  and fd['m'][k] - fd['e'][k] > C.TOL and ft['m'][k] - ft['e'][k] > C.TOL]
        out['R1'] = len(passes)
        out['R1_families'] = [T.fid[k] for k in passes]
    P = T.code_pass()
    ok = ridx >= 0
    code_pass = np.zeros(len(T.codes), bool)
    code_pass[ok] = P[np.flatnonzero(ok), ridx[ok]]
    out['R2'] = int(code_pass.sum())
    fails = np.zeros(len(T.seqs))
    ctok = np.zeros(len(T.seqs))
    for k, r in enumerate(C.ROLES):
        sel = np.flatnonzero(ridx == k)
        if len(sel):
            fails += np.asarray(T.Fail[r][sel].sum(axis=0)).ravel()
            ctok += np.asarray(T.Ns[sel].sum(axis=0)).ravel()
    out['R5_compatible'] = int(((ctok > 0) & (fails == 0)).sum())
    out['R5_any_contradiction'] = int((fails > 0).sum())
    out['R5_with_constrained_token'] = int((ctok > 0).sum())
    n_all = T.code_frame['all']['n']
    out['R6_constrained_tokens'] = float(n_all[ok].sum())
    out['R6_rule_passing_tokens'] = float(n_all[code_pass].sum())
    out['R6_assigned_tokens'] = float(n_all[labels >= 0].sum())
    out['total_tokens'] = float(n_all.sum())
    return out


def permute(T, labels, rng):
    new = labels.copy()
    for idx in T.groups.values():
        new[idx] = labels[idx][rng.permutation(len(idx))]
    return new


def scalar_view(ev):
    keys = [k for k in ['R1'] if k in ev] + ['R2', 'R5_compatible', 'R5_any_contradiction', 'R6_constrained_tokens', 'R6_rule_passing_tokens',
            'R6_assigned_tokens']
    keys += [k for k in ev if k.startswith('R3_') or k.startswith('positive_families_')]
    return {k: ev[k] for k in keys}


# --------------------------------------------------------------------------- exact bounds

def assign_exact(T, weight, labels):
    """Maximize sum_c weight[c, role of label] by linear assignment of labels within strata.

    weight: codes x roles; unconstrained labels have weight 0.
    """
    ridx = T.role_index(labels)
    new = labels.copy()
    total = 0.0
    for idx in T.groups.values():
        slots = labels[idx]
        sr = ridx[idx]
        W = np.zeros((len(idx), len(idx)))
        for col, r in enumerate(sr):
            if r >= 0:
                W[:, col] = weight[idx, r]
        rows, cols = linear_sum_assignment(W, maximize=True)
        new[idx[rows]] = slots[cols]
        total += W[rows, cols].sum()
    return new, total


def family_bound(T, k, frame='all'):
    """Largest excess family k can reach alone, keeping its member count per stratum."""
    r = T.frole[k]
    x = T.code_frame[frame]['x_' + r]
    total = 0.0
    for idx in T.groups.values():
        need = int((T.label0[idx] == k).sum())
        if need:
            total += np.sort(x[idx])[::-1][:need].sum()
    return float(total)


# --------------------------------------------------------------------------- annealing

class R1Annealer:
    """Within-stratum label swaps maximizing the number of families meeting the two-split rule."""

    def __init__(self, T, labels, rng):
        self.T, self.lab, self.rng = T, labels.copy(), rng
        nF = len(T.families)
        self.frames = ['discovery', 'transfer']
        self.role = T.frole
        self.cons = np.array([r != 'unconstrained' for r in self.role])
        self.m = np.zeros((nF, 2))
        self.e = np.zeros((nF, 2))
        self.n = np.zeros((nF, 2))
        self.cnt = np.zeros((nF, len(T.seqs)), dtype=np.int32)
        self.where = [np.flatnonzero(T.N[i] > 0) for i in range(len(T.codes))]
        for i in T.assigned:
            self.add(int(i), int(self.lab[i]), +1)
            # Version 1 omitted this line, so containing-string counts started at zero
            # (see AMENDMENT-1.md); history/roles-v1.py is the code behind roles/summary.json.
            self.cnt[int(self.lab[i]), self.where[int(i)]] += 1
        self.contain = (self.cnt > 0).sum(axis=1)
        self.sizes = np.array([len(g) for g in T.groups.values()], float)
        self.glist = list(T.groups.values())
        self.p = self.sizes / self.sizes.sum()

    def add(self, i, k, sign):
        r = self.role[k]
        for f, frame in enumerate(self.frames):
            t = self.T.code_frame[frame]
            self.n[k, f] += sign * t['n'][i]
            if r != 'unconstrained':
                self.m[k, f] += sign * t['m_' + r][i]
                self.e[k, f] += sign * t['e_' + r][i]

    def move_strings(self, i, k, sign):
        idx = self.where[i]
        before = (self.cnt[k, idx] > 0).sum()
        self.cnt[k, idx] += sign
        after = (self.cnt[k, idx] > 0).sum()
        self.contain[k] += after - before

    def fam_score(self, k):
        if not self.cons[k]:
            return 0, 0.0
        if self.contain[k] < 5 or self.n[k, 0] <= 0 or self.n[k, 1] <= 0:
            return 0, 0.0
        margin = min(self.m[k, 0] - self.e[k, 0], self.m[k, 1] - self.e[k, 1])
        return int(margin > C.TOL), (math.tanh(margin) + 1) / 2

    def objective(self):
        s = [self.fam_score(k) for k in range(len(self.T.families))]
        return sum(a for a, _ in s) + 0.9 * sum(b for _, b in s) / len(s), sum(a for a, _ in s)

    def swap(self, a, b):
        ka, kb = int(self.lab[a]), int(self.lab[b])
        self.add(a, ka, -1); self.move_strings(a, ka, -1)
        self.add(b, kb, -1); self.move_strings(b, kb, -1)
        self.add(b, ka, +1); self.move_strings(b, ka, +1)
        self.add(a, kb, +1); self.move_strings(a, kb, +1)
        self.lab[a], self.lab[b] = kb, ka
        return ka, kb

    def run(self, steps, t0=1.0, t1=0.01):
        nF = len(self.T.families)
        scores = [self.fam_score(k) for k in range(nF)]
        obj = lambda: sum(a for a, _ in scores) + 0.9 * sum(b for _, b in scores) / nF
        cur = obj()
        best = sum(a for a, _ in scores)
        best_lab = self.lab.copy()
        lr = math.log(t1 / t0)
        for step in range(steps):
            temp = t0 * math.exp(lr * step / steps)
            g = self.glist[self.rng.choice(len(self.glist), p=self.p)]
            a, b = g[self.rng.integers(len(g))], g[self.rng.integers(len(g))]
            if self.lab[a] == self.lab[b]:
                continue
            ka, kb = self.swap(a, b)
            old = scores[ka], scores[kb]
            scores[ka], scores[kb] = self.fam_score(ka), self.fam_score(kb)
            new = obj()
            if new >= cur or self.rng.random() < math.exp((new - cur) / temp):
                cur = new
                r1 = sum(x for x, _ in scores)
                if r1 > best:
                    best, best_lab = r1, self.lab.copy()
            else:
                self.swap(a, b)
                scores[ka], scores[kb] = old
        return best, best_lab


class R5Annealer:
    """Within-stratum label swaps maximizing whole-string role compatibility."""

    def __init__(self, T, labels, rng):
        self.T, self.lab, self.rng = T, labels.copy(), rng
        self.ridx = T.role_index(self.lab)
        nS = len(T.seqs)
        self.fail = np.zeros(nS)
        self.ctok = np.zeros(nS)
        self.where = [np.flatnonzero(T.N[i] > 0) for i in range(len(T.codes))]
        self.Fd = {r: T.N - T.M[r] for r in C.ROLES}
        for i in T.assigned:
            self.apply(int(i), self.ridx[i], +1)
        self.glist = list(T.groups.values())
        sizes = np.array([len(g) for g in self.glist], float)
        self.p = sizes / sizes.sum()

    def apply(self, i, r, sign):
        if r < 0:
            return
        idx = self.where[i]
        self.fail[idx] += sign * self.Fd[C.ROLES[r]][i, idx]
        self.ctok[idx] += sign * self.T.N[i, idx]

    def compatible(self):
        return int(((self.ctok > 0) & (self.fail == 0)).sum())

    def run(self, steps, t0=3.0, t1=0.03, lam=0.02):
        cur_c = self.compatible()
        cur = cur_c - lam * self.fail.sum()
        best, best_lab = cur_c, self.lab.copy()
        lr = math.log(t1 / t0)
        for step in range(steps):
            temp = t0 * math.exp(lr * step / steps)
            g = self.glist[self.rng.choice(len(self.glist), p=self.p)]
            a, b = g[self.rng.integers(len(g))], g[self.rng.integers(len(g))]
            ra, rb = self.ridx[a], self.ridx[b]
            if ra == rb:
                continue
            idx = np.union1d(self.where[a], self.where[b])
            before = int(((self.ctok[idx] > 0) & (self.fail[idx] == 0)).sum())
            fb = self.fail[idx].sum()
            self.apply(a, ra, -1); self.apply(b, rb, -1)
            self.apply(a, rb, +1); self.apply(b, ra, +1)
            after = int(((self.ctok[idx] > 0) & (self.fail[idx] == 0)).sum())
            fa = self.fail[idx].sum()
            new_c = cur_c + after - before
            new = cur + (after - before) - lam * (fa - fb)
            if new >= cur or self.rng.random() < math.exp((new - cur) / temp):
                cur, cur_c = new, new_c
                self.lab[a], self.lab[b] = self.lab[b], self.lab[a]
                self.ridx[a], self.ridx[b] = rb, ra
                if cur_c > best:
                    best, best_lab = cur_c, self.lab.copy()
            else:
                self.apply(a, rb, -1); self.apply(b, ra, -1)
                self.apply(a, ra, +1); self.apply(b, rb, +1)
        return best, best_lab


_T = None


def _init():
    global _T
    _T = Tables()


def anneal_job(args):
    kind, restart, seed = args
    rng = np.random.default_rng(seed)
    start = permute(_T, _T.label0, rng)
    t0 = time.time()
    if kind == 'R1':
        ann = R1Annealer(_T, start, rng)
        best, lab = ann.run(ANNEAL_STEPS)
    else:
        ann = R5Annealer(_T, start, rng)
        best, lab = ann.run(ANNEAL_STEPS)
    ev = evaluate(_T, lab)
    assert (kind == 'R1' and ev['R1'] == best) or (kind == 'R5' and ev['R5_compatible'] == best)
    return {'statistic': kind, 'restart': restart, 'seed': seed, 'best': best,
            'start_value': evaluate(_T, start)[kind if kind == 'R1' else 'R5_compatible'],
            'seconds': time.time() - t0, 'labels': lab.tolist(), 'evaluation': scalar_view(ev)}


# --------------------------------------------------------------------------- main

def labels_to_map(T, labels):
    return {T.fid[k]: sorted(T.codes[i] for i in np.flatnonzero(labels == k)) for k in range(len(T.families))}


def family_rows(T, ev_pub, null_evs, bound_by_family):
    rows = []
    pvals = []
    for k in T.constrained:
        x_pub = ev_pub['families']['all']['m'][k] - ev_pub['families']['all']['e'][k]
        draws = [ev['families']['all']['m'][k] - ev['families']['all']['e'][k] for ev in null_evs]
        s = C.null_summary(float(x_pub), draws, bound_by_family[k])
        pvals.append(s['p_at_or_above'])
        rows.append({'family_id': T.fid[k], 'role': T.frole[k], 'members': int((T.label0 == k).sum()),
                     'tokens': float(ev_pub['families']['all']['n'][k]),
                     'matching': float(ev_pub['families']['all']['m'][k]),
                     'expected': float(ev_pub['families']['all']['e'][k]),
                     'containing_strings': int(ev_pub['containing'][k]),
                     'meets_two_split_rule': T.fid[k] in ev_pub['R1_families'],
                     'excess': s,
                     'h2_excess_published': float(ev_pub['families']['H2']['m'][k] - ev_pub['families']['H2']['e'][k])})
    for row, q in zip(rows, C.bh(pvals)):
        row['excess']['bh_q'] = q
    return rows


def transfer(T, fit_half, eval_half, null_labels, label_start, froles=None, tag=''):
    """Exact R3 fit on fit_half; score on eval_half against permutations scored there."""
    froles = froles or T.frole
    weight = T.code_value(fit_half, 'x')
    fitted, _ = assign_exact_roles(T, weight, label_start, froles)
    ev_fit = evaluate(T, fitted, froles, frames=('all', 'discovery', 'transfer', fit_half, eval_half, eval_half + '_novel'))
    out = {'fit_half': fit_half, 'evaluation_half': eval_half, 'variant': tag}
    for frame in [eval_half, eval_half + '_novel']:
        draws_r3 = [n[f'R3_{frame}'] for n in null_labels]
        draws_pos = [n[f'positive_families_{frame}'] for n in null_labels]
        out[frame] = {'R3_fit': C.null_summary(ev_fit[f'R3_{frame}'], draws_r3),
                      'positive_families_fit': C.null_summary(ev_fit[f'positive_families_{frame}'], draws_pos)}
    out['R3_in_sample_fit'] = ev_fit[f'R3_{fit_half}']
    out['fitted_map'] = labels_to_map(T, fitted)
    out['fitted_roles'] = dict(zip(T.fid, froles))
    return out, fitted


def assign_exact_roles(T, weight, labels, froles):
    ridx = np.full(len(T.codes), -1)
    ok = labels >= 0
    ridx[ok] = [C.ROLES.index(froles[k]) if froles[k] != 'unconstrained' else -1 for k in labels[ok]]
    new = labels.copy()
    total = 0.0
    for idx in T.groups.values():
        slots, sr = labels[idx], ridx[idx]
        W = np.zeros((len(idx), len(idx)))
        for col, r in enumerate(sr):
            if r >= 0:
                W[:, col] = weight[idx, r]
        rows, cols = linear_sum_assignment(W, maximize=True)
        new[idx[rows]] = slots[cols]
        total += W[rows, cols].sum()
    return new, total


def role_refit(T, fit_half, rounds=5):
    """Alternate per-family best role on fit_half with exact membership refits."""
    froles = list(T.frole)
    labels = T.label0.copy()
    weight = T.code_value(fit_half, 'x')
    history = []
    for rnd in range(rounds):
        labels, total = assign_exact_roles(T, weight, labels, froles)
        changed = 0
        for k in T.constrained:
            members = np.flatnonzero(labels == k)
            best = max(C.ROLES, key=lambda r: (weight[members, C.ROLES.index(r)].sum(), r == froles[k]))
            changed += best != froles[k]
            froles[k] = best
        history.append({'round': rnd + 1, 'objective_before_role_change': float(total), 'roles_changed': changed})
    labels, total = assign_exact_roles(T, weight, labels, froles)
    history.append({'final_objective': float(total)})
    return labels, froles, history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    if OUT.exists() or LOCAL.exists():
        raise SystemExit('Refusing to overwrite an existing endpoint')
    inputs = C.check_pins()
    t0 = time.time()
    T = Tables()
    null_ss, anneal_ss, rolefit_ss = [np.random.SeedSequence(C.SEED, spawn_key=(k,))
                                      for k in (FAMILY_SPAWN, ANNEAL_SPAWN, ROLEFIT_SPAWN)]
    ev_pub = evaluate(T, T.label0)
    print('published', scalar_view(ev_pub), flush=True)

    rng = np.random.default_rng(null_ss)
    null_labels, null_evs = [], []
    for i in range(N_NULL):
        lab = permute(T, T.label0, rng)
        null_labels.append(lab)
        null_evs.append(evaluate(T, lab))
    print('null done', time.time() - t0, flush=True)

    # Exact bounds for additive statistics.
    X = T.code_value('all', 'x')
    P = T.code_pass().astype(float)
    lab_r3, r3_bound = assign_exact(T, X, T.label0)
    lab_r2, r2_bound = assign_exact(T, P + 1e-6 * np.tanh(X), T.label0)
    ev_r3, ev_r2 = evaluate(T, lab_r3), evaluate(T, lab_r2)
    assert abs(ev_r3['R3_all'] - r3_bound) < 1e-6
    bound_by_family = {k: family_bound(T, k) for k in T.constrained}

    anneal_args = []
    seeds = anneal_ss.generate_state(2 * RESTARTS)
    for n, kind in enumerate(['R1', 'R5']):
        for r in range(RESTARTS):
            anneal_args.append((kind, r, int(seeds[n * RESTARTS + r])))
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as pool:
        anneal = list(pool.map(anneal_job, anneal_args))
    print('anneal done', time.time() - t0, flush=True)
    r1_bound = max(a['best'] for a in anneal if a['statistic'] == 'R1')
    r5_bound = max(a['best'] for a in anneal if a['statistic'] == 'R5')

    # Upper bounds for R1 and R5 also include the exact-assignment maps and the published map.
    r1_bound = max(r1_bound, ev_r3['R1'], ev_r2['R1'], ev_pub['R1'])
    r5_bound = max(r5_bound, ev_r3['R5_compatible'], ev_r2['R5_compatible'], ev_pub['R5_compatible'])

    stats = {}
    for key, bound in [('R1', r1_bound), ('R2', float(ev_r2['R2'])), ('R3_all', float(r3_bound)),
                       ('R5_compatible', r5_bound), ('R5_any_contradiction', None),
                       ('R6_constrained_tokens', None), ('R6_rule_passing_tokens', None),
                       ('R6_assigned_tokens', None)]:
        stats[key] = C.null_summary(ev_pub[key], [e[key] for e in null_evs], bound)
    # Coverage achievable within the same stratum counts (min and max of constrained-token coverage).
    n_all = T.code_frame['all']['n']
    cov_min = cov_max = 0.0
    for idx in T.groups.values():
        k = int((T.role_index(T.label0)[idx] >= 0).sum())
        v = np.sort(n_all[idx])
        cov_min += v[:k].sum()
        cov_max += v[::-1][:k].sum()
    stats['R6_constrained_tokens']['achievable_range'] = [float(cov_min), float(cov_max)]

    # Transfer between halves.
    transfers = []
    fitted_maps = {}
    for fit_half, eval_half in [('H1', 'H2'), ('H2', 'H1')]:
        res, fitted = transfer(T, fit_half, eval_half, null_evs, T.label0, tag='membership fit, published roles')
        pub = {}
        for frame in [eval_half, eval_half + '_novel']:
            pub[frame] = {'R3_published': C.null_summary(ev_pub[f'R3_{frame}'], [n[f'R3_{frame}'] for n in null_evs]),
                          'positive_families_published': C.null_summary(
                              ev_pub[f'positive_families_{frame}'], [n[f'positive_families_{frame}'] for n in null_evs])}
        res['published_map'] = pub
        fitted_maps[f'membership_fit_{fit_half}'] = res.pop('fitted_map')
        transfers.append(res)
        # Role-refit sensitivity with its own null.
        lab_rf, froles, history = role_refit(T, fit_half)
        rng_rf = np.random.default_rng(np.random.SeedSequence(C.SEED, spawn_key=(ROLEFIT_SPAWN, 1 if fit_half == 'H1' else 2)))
        null_rf = [evaluate(T, permute(T, lab_rf, rng_rf), froles, frames=(eval_half, eval_half + '_novel'))
                   for _ in range(N_NULL)]
        ev_rf = evaluate(T, lab_rf, froles, frames=(fit_half, eval_half, eval_half + '_novel'))
        rf = {'fit_half': fit_half, 'evaluation_half': eval_half, 'variant': 'membership and role refit',
              'history': history, 'roles_changed_from_published': sum(a != b for a, b in zip(froles, T.frole)),
              'role_counts': dict(Counter(froles)), 'R3_in_sample_fit': ev_rf[f'R3_{fit_half}']}
        for frame in [eval_half, eval_half + '_novel']:
            rf[frame] = {'R3_fit': C.null_summary(ev_rf[f'R3_{frame}'], [n[f'R3_{frame}'] for n in null_rf]),
                         'positive_families_fit': C.null_summary(ev_rf[f'positive_families_{frame}'],
                                                                 [n[f'positive_families_{frame}'] for n in null_rf])}
        fitted_maps[f'role_refit_{fit_half}'] = {'map': labels_to_map(T, lab_rf), 'roles': dict(zip(T.fid, froles))}
        transfers.append(rf)
    print('transfer done', time.time() - t0, flush=True)

    fam = family_rows(T, ev_pub, null_evs, bound_by_family)
    strata = {str(b): {'assigned_codes': len(idx), 'tokens': float(n_all[idx].sum())} for b, idx in T.groups.items()}
    summary = {
        'status': 'Calibration of a frozen exploratory map; outcomes computed after PROTOCOL.md was frozen',
        'protocol_sha256': C.sha(C.HERE / 'PROTOCOL.md'), 'code_sha256': C.sha(__file__),
        'common_sha256': C.sha(C.HERE / 'common.py'), 'inputs': inputs,
        'population': {'strings': len(T.seqs), 'tokens': float(n_all.sum()),
                       'half_strings': {h: int(T.masks[h].sum()) for h in ['H1', 'H2']},
                       'half_tokens': {h: float(T.code_frame[h]['n'].sum()) for h in ['H1', 'H2']},
                       'published_split_strings': {h: int(T.masks[h].sum()) for h in ['discovery', 'transfer']},
                       'near_duplicate_control': T.novel_info},
        'strata': strata,
        'null': {'draws': N_NULL, 'seed_entropy': C.SEED, 'spawn_key': [FAMILY_SPAWN],
                 'rule': 'family labels permuted among the 673 assigned codes within token-count strata'},
        'published': scalar_view(ev_pub), 'published_R1_families': ev_pub['R1_families'],
        'statistics': stats,
        'bounds': {'R2_R3_method': 'exact linear assignment within strata',
                   'R1_R5_method': f'swap annealing, {RESTARTS} restarts x {ANNEAL_STEPS} proposals; reported bound is the best value found',
                   'anneal_runs': [{k: v for k, v in a.items() if k != 'labels'} for a in anneal],
                   'R3_exact_map_evaluation': scalar_view(ev_r3), 'R2_exact_map_evaluation': scalar_view(ev_r2)},
        'families': fam,
        'transfer': transfers,
        'seconds': time.time() - t0,
    }
    C.write_json(OUT / 'summary.json', summary)
    best_r1 = max((a for a in anneal if a['statistic'] == 'R1'), key=lambda a: a['best'])
    best_r5 = max((a for a in anneal if a['statistic'] == 'R5'), key=lambda a: a['best'])
    C.write_json(OUT / 'fitted-maps.json', {
        'scope': 'Project-generated code-to-family maps. Each keeps the published family roles and per-stratum member counts unless stated.',
        'R3_exact_all_strings': labels_to_map(T, lab_r3), 'R2_exact_all_strings': labels_to_map(T, lab_r2),
        'R1_annealed_best': labels_to_map(T, np.array(best_r1['labels'])),
        'R5_annealed_best': labels_to_map(T, np.array(best_r5['labels'])), **fitted_maps})
    LOCAL.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(LOCAL / 'null-draws.npz',
                        labels=np.array(null_labels),
                        family_excess_all=np.array([[e['families']['all']['m'][k] - e['families']['all']['e'][k]
                                                     for k in T.constrained] for e in null_evs]))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ('published', 'null_mean', 'null_sd', 'p_at_or_above', 'bound', 'z')}
                      for k, v in stats.items()}, indent=1), flush=True)


if __name__ == '__main__':
    main()
