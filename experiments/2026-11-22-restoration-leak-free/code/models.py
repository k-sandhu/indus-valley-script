"""Exact-probability classical, Kneser-Ney, graphic-family, and skip-bigram models.

All models use NumPy and standard library only, share identical training-fold
vocabularies (observed training codes sorted ascending plus UNKNOWN), and never
inspect the hidden target slot.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/six_hour"))
from methods.conditional_structure import UNKNOWN
import restoration as paper001_restoration
import markov_baseline as m1_module
import markov_order2 as m2_module

PM_GRID = [20, 100, 500, 2000]
M1_GRID = [20, 100, 500, 2000]
M2_GRID = [5, 20, 100, 500, 2000, None]
MKN_GRID = [{"order": k, "discount_scale": d} for k in [2, 3, 4, 5] for d in [0.75, 1.0]]
GF_ALPHA_GRID = [5.0, 20.0]
GF_WEIGHT_GRID = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30]
ENS_GF_WEIGHT_GRID = [0.0, 0.05, 0.10, 0.15, 0.20]
ENS_SB_WEIGHT_GRID = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25]


class PMRestorer:
    """Paper 001 independent length, slot, site, and object-type baseline."""

    def __init__(self, rows: list[dict], alpha: float):
        self.inner = paper001_restoration.Restorer(rows, alpha)
        self.signs = self.inner.model.signs
        self.index = self.inner.model.index
        self.alpha = float(alpha)

    def distribution(self, row: dict, slot: int) -> np.ndarray:
        return self.inner.distribution(row, slot, bidirectional=False)

    def predict(self, rows: list[dict]) -> np.ndarray:
        return np.asarray([self.distribution(r, i) for r in rows for i in range(len(r["seq"]))], dtype=np.float64)


class M1Restorer:
    """Conventional time-homogeneous first-order Markov restorer (MARKOV-01)."""

    def __init__(self, rows: list[dict], alpha: float):
        self.inner = m1_module.MarkovRestorer(rows, alpha)
        self.signs = self.inner.signs
        self.index = self.inner.index
        self.alpha = float(alpha)

    def distribution(self, row: dict, slot: int) -> np.ndarray:
        return self.inner.distribution(row, slot)

    def predict(self, rows: list[dict]) -> np.ndarray:
        return np.asarray([self.distribution(r, i) for r in rows for i in range(len(r["seq"]))], dtype=np.float64)


class M2Restorer:
    """Exact vectorized second-order Markov restorer with M1(alpha=20) backoff (MARKOV-03)."""

    def __init__(self, rows: list[dict], alpha: float | None):
        self.base = m1_module.MarkovRestorer(rows, 20)
        self.signs = self.base.signs
        self.index = self.base.index
        self.end_index = self.base.end_index
        self.start_index = self.end_index + 1
        self.alpha = alpha
        self.observed: dict[tuple[int, int], np.ndarray] = {}
        self.by_first: dict[int, list[tuple[int, np.ndarray]]] = defaultdict(list)
        self.by_second: dict[int, list[tuple[int, np.ndarray]]] = defaultdict(list)
        if alpha is not None:
            counts: dict[tuple[int, int], Counter] = defaultdict(Counter)
            for row in rows:
                sequence = [self.index[s] for s in row["seq"]] + [self.end_index]
                a = b = self.start_index
                for target in sequence:
                    counts[(a, b)][target] += 1
                    a, b = b, target
            for history, targets in counts.items():
                prior = self.prior(history[1])
                values = alpha * prior.copy()
                for target, number in targets.items():
                    values[target] += number
                probs = values / (sum(targets.values()) + alpha)
                self.observed[history] = probs
                if history[1] < self.end_index:
                    self.by_first[history[0]].append((history[1], probs))
                if history[0] < self.end_index:
                    self.by_second[history[1]].append((history[0], probs))

    def prior(self, latest: int) -> np.ndarray:
        return np.r_[self.base.start, 0.0] if latest == self.start_index else self.base.transition[latest]

    def probability(self, first: int, latest: int) -> np.ndarray:
        values = self.observed.get((first, latest))
        return values if values is not None else self.prior(latest)

    def distribution(self, row: dict, slot: int) -> np.ndarray:
        if self.alpha is None:
            return self.base.distribution(row, slot)
        n = self.end_index
        unk = self.index[UNKNOWN]
        sequence = [self.index.get(v, unk) for v in row["seq"]] + [n]
        score = np.ones(n, dtype=np.float64)
        for position in range(slot, min(len(sequence), slot + 3)):
            a = self.start_index if position < 2 else sequence[position - 2]
            b = self.start_index if position < 1 else sequence[position - 1]
            if position == slot:
                score *= self.probability(a, b)[:n]
            elif position == slot + 1:
                target = sequence[position]
                col = self.base.transition[:, target].copy()
                for cand, probs in self.by_first.get(a, ()):
                    col[cand] = probs[target]
                score *= col
            else:
                target = sequence[position]
                col = np.full(n, float(self.prior(b)[target]), dtype=np.float64)
                for cand, probs in self.by_second.get(b, ()):
                    col[cand] = probs[target]
                score *= col
        return score / score.sum()

    def predict(self, rows: list[dict]) -> np.ndarray:
        return np.asarray([self.distribution(r, i) for r in rows for i in range(len(r["seq"]))], dtype=np.float64)


class MKNRestorer:
    """Finite-vocabulary interpolated modified Kneser-Ney (exact 6 October specification)."""

    def __init__(self, rows: list[dict], order: int = 3, discount_scale: float = 1.0):
        self.order = order
        self.scale = float(discount_scale)
        self.signs = sorted({s for r in rows for s in r["seq"]}) + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        self.n = len(self.signs)
        self.end = self.n
        self.start = self.n + 1
        raw = [Counter() for _ in range(order + 1)]
        for r in rows:
            sequence = [self.start] * (order - 1) + [self.index[s] for s in r["seq"]] + [self.end]
            for pos in range(order - 1, len(sequence)):
                for k in range(1, order + 1):
                    raw[k][tuple(sequence[pos - k + 1:pos + 1])] += 1
        self.counts = [Counter() for _ in range(order + 1)]
        self.counts[order] = raw[order]
        for k in range(1, order):
            for gram in raw[k + 1]:
                self.counts[k][gram[1:]] += 1
        bottom = np.full(self.n + 1, 0.5, dtype=np.float64)
        for (token,), count in self.counts[1].items():
            bottom[token] += count
        self.bottom = bottom / bottom.sum()
        self.discounts, self.rows, self.patterns = {}, {}, {}
        for k in range(2, order + 1):
            coc = Counter(self.counts[k].values())
            n1, n2, n3, n4 = [coc[j] for j in [1, 2, 3, 4]]
            y = n1 / (n1 + 2 * n2) if n1 + 2 * n2 else 0.5
            estimates = [
                1 - 2 * y * n2 / n1 if n1 else 0.5,
                2 - 3 * y * n3 / n2 if n2 else 1.0,
                3 - 4 * y * n4 / n3 if n3 else 1.5,
            ]
            ds = np.array([np.clip(d * discount_scale, 0.05, j - 0.05) for j, d in enumerate(estimates, 1)])
            self.discounts[k] = {"count_of_counts": dict(coc), "discounts": ds.tolist()}
            counts = defaultdict(Counter)
            for gram, count in self.counts[k].items():
                counts[gram[:-1]][gram[-1]] = count
            self.rows[k] = {}
            self.patterns[k] = [defaultdict(list) for _ in range(k - 1)]
            for hist, values in counts.items():
                total = sum(values.values())
                sparse = {token: (count - ds[min(count, 3) - 1]) / total for token, count in values.items()}
                gamma = sum(ds[min(count, 3) - 1] for count in values.values()) / total
                self.rows[k][hist] = (sparse, gamma)
                for pos in range(k - 1):
                    key = hist[:pos] + hist[pos + 1:]
                    self.patterns[k][pos][key].append((hist[pos], sparse, gamma))
        self._vector_cache: dict[tuple[int, ...], np.ndarray] = {}

    def vector(self, hist: tuple[int, ...]) -> np.ndarray:
        hist = tuple(hist[-(self.order - 1):])
        if not hist:
            return self.bottom
        if hist in self._vector_cache:
            return self._vector_cache[hist]
        low = self.vector(hist[1:])
        sparse_row = self.rows[len(hist) + 1].get(hist)
        if sparse_row is None:
            return low
        sparse, gamma = sparse_row
        p = gamma * low.copy()
        for token, value in sparse.items():
            p[token] += value
        self._vector_cache[hist] = p
        return p

    def wildcard(self, hist: list[int], pos: int, target: int) -> np.ndarray:
        if not hist:
            return np.full(self.n, self.bottom[target])
        if pos == 0:
            p = np.full(self.n, self.vector(tuple(hist[1:]))[target])
        else:
            p = self.wildcard(hist[1:], pos - 1, target)
        key = tuple(hist[:pos] + hist[pos + 1:])
        for candidate, sparse, gamma in self.patterns[len(hist) + 1][pos].get(key, []):
            if candidate < self.n:
                p[candidate] = sparse.get(target, 0.0) + gamma * p[candidate]
        return p

    def distribution(self, row: dict, slot: int) -> np.ndarray:
        seq = [self.index.get(s, self.index[UNKNOWN]) for s in row["seq"]] + [self.end]
        padded = [self.start] * (self.order - 1) + seq
        offset = self.order - 1
        score = self.vector(tuple(padded[slot:slot + offset]))[:self.n].copy()
        for j in range(slot + 1, min(len(seq), slot + self.order)):
            hist = padded[j:j + offset]
            pos = slot + offset - j
            score *= self.wildcard(hist, pos, seq[j])
        return score / score.sum()

    def predict(self, rows: list[dict]) -> np.ndarray:
        return np.asarray([self.distribution(r, i) for r in rows for i in range(len(r["seq"]))], dtype=np.float64)

    def likelihood(self, sequence: list[str]) -> float:
        padded = [self.start] * (self.order - 1) + [self.index.get(s, self.index[UNKNOWN]) for s in sequence] + [self.end]
        value = 1.0
        for j in range(self.order - 1, len(padded)):
            value *= float(self.vector(tuple(padded[j - self.order + 1:j]))[padded[j]])
        return value


class GraphicFamilyMarkov:
    """Exact generative first-order class Markov restorer using F-0010 base shapes."""

    def __init__(self, rows: list[dict], base_map: dict[str, str], alpha: float = 5.0):
        self.alpha = float(alpha)
        self.signs = sorted({s for r in rows for s in r["seq"]}) + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        self.n = len(self.signs)
        self.unk_idx = self.index[UNKNOWN]

        cls_names = [base_map.get(s, s) for s in self.signs[:-1]] + ["__UNKNOWN_CLASS__"]
        self.classes = sorted(set(cls_names))
        self.cls_index = {c: i for i, c in enumerate(self.classes)}
        self.n_cls = len(self.classes)
        self.end_cls = self.n_cls
        self.cls_of = np.array([self.cls_index[c] for c in cls_names], dtype=np.int64)

        unigram_raw = np.full(self.n, 0.5, dtype=np.float64)
        c_start = np.zeros(self.n_cls, dtype=np.float64)
        c_trans = np.zeros((self.n_cls, self.n_cls + 1), dtype=np.float64)
        for row in rows:
            seq = [self.index[s] for s in row["seq"]]
            c_start[self.cls_of[seq[0]]] += 1.0
            for pos, cur in enumerate(seq):
                unigram_raw[cur] += 1.0
                nxt_cls = self.cls_of[seq[pos + 1]] if pos + 1 < len(seq) else self.end_cls
                c_trans[self.cls_of[cur], nxt_cls] += 1.0

        self.unigram = unigram_raw / unigram_raw.sum()
        cls_raw = np.bincount(self.cls_of, weights=unigram_raw, minlength=self.n_cls).astype(np.float64)
        self.p0 = cls_raw / cls_raw.sum()
        self.emit = self.unigram / self.p0[self.cls_of]

        dest_raw = np.append(cls_raw, len(rows) + 0.5)
        self.dest_prior = dest_raw / dest_raw.sum()
        self.start = (c_start + self.alpha * self.p0) / (len(rows) + self.alpha)
        self.trans = (c_trans + self.alpha * self.dest_prior[None, :]) / (c_trans.sum(axis=1, keepdims=True) + self.alpha)

    def distribution(self, row: dict, slot: int) -> np.ndarray:
        seq = row["seq"]
        if slot > 0:
            prev_cls = self.cls_of[self.index.get(seq[slot - 1], self.unk_idx)]
            cls_score = self.trans[prev_cls, :self.end_cls].copy()
        else:
            cls_score = self.start.copy()
        next_cls = (
            self.cls_of[self.index.get(seq[slot + 1], self.unk_idx)]
            if slot + 1 < len(seq)
            else self.end_cls
        )
        cls_score *= self.trans[:, next_cls]
        score = cls_score[self.cls_of] * self.emit
        return score / score.sum()

    def predict(self, rows: list[dict]) -> np.ndarray:
        return np.asarray([self.distribution(r, i) for r in rows for i in range(len(r["seq"]))], dtype=np.float64)

    def likelihood(self, sequence: list[str]) -> float:
        idxs = [self.index.get(s, self.unk_idx) for s in sequence]
        g = [self.cls_of[i] for i in idxs]
        val = float(self.start[g[0]] * self.emit[idxs[0]])
        for t in range(1, len(idxs)):
            val *= float(self.trans[g[t - 1], g[t]] * self.emit[idxs[t]])
        val *= float(self.trans[g[-1], self.end_cls])
        return val


class SkipBigramPosModel:
    """Length-and-slot prior combined with distance-2 skip-bigram lift ratios."""

    def __init__(self, rows: list[dict], alpha_pos: float = 20.0, alpha_skip: float = 20.0):
        self.alpha_pos = float(alpha_pos)
        self.alpha_skip = float(alpha_skip)
        self.signs = sorted({s for r in rows for s in r["seq"]}) + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        self.n = len(self.signs)
        self.unk_idx = self.index[UNKNOWN]

        unigram = np.full(self.n, 0.5, dtype=np.float64)
        pos_counts: dict[tuple[int, int], Counter] = defaultdict(Counter)
        skip_counts = np.zeros((self.n, self.n), dtype=np.float64)
        for row in rows:
            seq = [self.index[s] for s in row["seq"]]
            length = len(seq)
            for i, c in enumerate(seq):
                unigram[c] += 1.0
                pos_counts[(length, i)][c] += 1
                if i >= 2:
                    skip_counts[seq[i - 2], c] += 1.0
        self.unigram = unigram / unigram.sum()
        self.pos_counts = pos_counts
        self._pos_cache: dict[tuple[int, int], np.ndarray] = {}

        row_sums = skip_counts.sum(axis=1, keepdims=True)
        p_skip = (skip_counts + self.alpha_skip * self.unigram[None, :]) / (row_sums + self.alpha_skip)
        self.skip_ratio = p_skip / self.unigram[None, :]

    def pos_prior(self, length: int, slot: int) -> np.ndarray:
        key = (length, slot)
        if key not in self._pos_cache:
            counts = self.pos_counts.get(key)
            if not counts:
                self._pos_cache[key] = self.unigram
            else:
                total = sum(counts.values())
                vec = self.alpha_pos * self.unigram.copy()
                for c, cnt in counts.items():
                    vec[c] += cnt
                self._pos_cache[key] = vec / (total + self.alpha_pos)
        return self._pos_cache[key]

    def distribution(self, row: dict, slot: int) -> np.ndarray:
        seq = row["seq"]
        length = len(seq)
        score = self.pos_prior(length, slot).copy()
        if slot >= 2:
            prev2 = self.index.get(seq[slot - 2], self.unk_idx)
            score *= self.skip_ratio[prev2, :]
        if slot + 2 < length:
            next2 = self.index.get(seq[slot + 2], self.unk_idx)
            score *= self.skip_ratio[:, next2]
        return score / score.sum()

    def predict(self, rows: list[dict]) -> np.ndarray:
        return np.asarray([self.distribution(r, i) for r in rows for i in range(len(r["seq"]))], dtype=np.float64)


def log_linear_pool(probs_list: list[np.ndarray], weights: list[float]) -> np.ndarray:
    """Exact log-linear (geometric) probability pool over aligned (N, V) arrays."""
    acc = np.zeros_like(probs_list[0], dtype=np.float64)
    for arr, w in zip(probs_list, weights):
        if w != 0.0:
            acc += w * np.log(np.clip(arr, 1e-300, 1.0))
    acc -= acc.max(axis=1, keepdims=True)
    exp_acc = np.exp(acc)
    return exp_acc / exp_acc.sum(axis=1, keepdims=True)


def probability_metrics(rows: list[dict], probs: np.ndarray, signs: list[str]) -> dict:
    index = {s: i for i, s in enumerate(signs)}
    unk = index[UNKNOWN]
    actual = [s for r in rows for s in r["seq"]]
    targets = np.array([index.get(s, unk) for s in actual], dtype=np.int64)
    order = np.argsort(-probs, axis=1, kind="stable")
    correct = np.array([signs[j] == s for j, s in zip(order[:, 0], actual)], dtype=np.float64)
    loss = -np.log2(np.clip(probs[np.arange(len(actual)), targets], 1e-300, 1.0))
    return {"slots": len(actual), "top1": float(correct.mean()), "bucket_loss_bits": float(loss.mean())}


def self_test() -> dict:
    rows = [
        {"seq": tuple(s), "stratum": ("S1", "T1")}
        for s in ["ABCD", "ABCD", "ACBD", "BACD", "CACB", "BBBD", "CABA", "DCBA"]
    ]
    base_map = {"A": "G1", "B": "G1", "C": "G2", "D": "G3"}
    query = {"seq": tuple("ABCD"), "stratum": ("S1", "T1")}
    checks = {}

    # 1. PM hidden independence & normalization
    pm = PMRestorer(rows, 20.0)
    for slot in range(4):
        p = pm.distribution(query, slot)
        assert abs(float(p.sum()) - 1.0) < 1e-12
        hidden = list(query["seq"]); hidden[slot] = "ERASED"
        assert np.array_equal(p, pm.distribution({"seq": tuple(hidden), "stratum": ("S1", "T1")}, slot))
    checks["PM"] = {"normalized": True, "hidden_invariance": True}

    # 2. M1 brute-force likelihood & hidden independence
    m1 = M1Restorer(rows, 2.0)
    for slot in range(4):
        brute = []
        for cand in m1.signs:
            s = list(query["seq"]); s[slot] = cand
            ix = [m1.index[c] for c in s]
            val = m1.inner.start[ix[0]]
            for a, b in zip(ix[:-1], ix[1:]):
                val *= m1.inner.transition[a, b]
            val *= m1.inner.transition[ix[-1], m1.inner.end_index]
            brute.append(val)
        brute = np.asarray(brute) / sum(brute)
        p = m1.distribution(query, slot)
        assert np.allclose(p, brute, atol=1e-14, rtol=1e-12)
        hidden = list(query["seq"]); hidden[slot] = "ERASED"
        assert np.array_equal(p, m1.distribution({"seq": tuple(hidden)}, slot))
    checks["M1"] = {"brute_force_exact": True, "hidden_invariance": True}

    # 3. M2 exact match with reference markov_order2.Restorer & brute force
    for alpha in [2.0, None]:
        m2 = M2Restorer(rows, alpha)
        ref = m2_module.Restorer(rows, alpha)
        for slot in range(4):
            p = m2.distribution(query, slot)
            q = ref.distribution(query, slot)
            assert np.allclose(p, q, atol=1e-15, rtol=1e-14)
            hidden = list(query["seq"]); hidden[slot] = "ERASED"
            assert np.array_equal(p, m2.distribution({"seq": tuple(hidden)}, slot))
    checks["M2"] = {"matches_reference_exact": True, "hidden_invariance": True}

    # 4. MKN brute-force complete sequence likelihood & hidden independence
    for cfg in MKN_GRID:
        mkn = MKNRestorer(rows, **cfg)
        for slot in range(4):
            brute = []
            for cand in mkn.signs:
                s = list(query["seq"]); s[slot] = cand
                brute.append(mkn.likelihood(s))
            brute = np.asarray(brute) / sum(brute)
            p = mkn.distribution(query, slot)
            assert np.allclose(p, brute, atol=1e-14, rtol=1e-11)
            hidden = list(query["seq"]); hidden[slot] = "ERASED"
            assert np.array_equal(p, mkn.distribution({"seq": tuple(hidden)}, slot))
    checks["MKN"] = {"brute_force_all_grid_configs": True, "hidden_invariance": True}

    # 5. GF-M1 brute-force complete sequence likelihood & hidden independence
    gf = GraphicFamilyMarkov(rows, base_map, alpha=5.0)
    for slot in range(4):
        brute = []
        for cand in gf.signs:
            s = list(query["seq"]); s[slot] = cand
            brute.append(gf.likelihood(s))
        brute = np.asarray(brute) / sum(brute)
        p = gf.distribution(query, slot)
        assert np.allclose(p, brute, atol=1e-14, rtol=1e-12)
        hidden = list(query["seq"]); hidden[slot] = "ERASED"
        assert np.array_equal(p, gf.distribution({"seq": tuple(hidden)}, slot))
    checks["GF_M1"] = {"brute_force_exact": True, "hidden_invariance": True}

    # 6. SB-Pos normalization, hidden independence, and skip-2 sensitivity
    sb = SkipBigramPosModel(rows, alpha_pos=20.0, alpha_skip=20.0)
    for slot in range(4):
        p = sb.distribution(query, slot)
        assert abs(float(p.sum()) - 1.0) < 1e-12 and np.all(p > 0)
        hidden = list(query["seq"]); hidden[slot] = "ERASED"
        assert np.array_equal(p, sb.distribution({"seq": tuple(hidden)}, slot))
    assert not np.allclose(sb.distribution({"seq": ("A", "X", "C", "D")}, 2), sb.distribution({"seq": ("B", "X", "C", "D")}, 2))
    checks["SB_Pos"] = {"normalized": True, "hidden_invariance": True, "skip2_sensitive": True}

    # 7. Log-linear pooling exact fallback when weight=0
    p_mkn = mkn.predict([query])
    p_gf = gf.predict([query])
    p_sb = sb.predict([query])
    assert np.allclose(log_linear_pool([p_mkn, p_gf, p_sb], [1.0, 0.0, 0.0]), p_mkn, atol=1e-14)
    pooled = log_linear_pool([p_mkn, p_gf, p_sb], [0.7, 0.15, 0.15])
    assert np.allclose(pooled.sum(axis=1), 1.0, atol=1e-14)
    checks["log_linear_pool"] = {"exact_fallback": True, "normalized": True}

    return {"passed": True, "checks": checks}
