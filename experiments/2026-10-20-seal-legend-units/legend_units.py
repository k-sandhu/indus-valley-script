"""Shared code for the seal-legend unit study of 20 October 2026.

Texts are tuples of sign labels in reading order. Position i (1 <= i < len(t)) is a cut
between t[i-1] and t[i]. Corpus statistics are always computed with the scored text's own
component removed, so a text never informs its own segmentation through identical copies,
aliases or other faces of its object. See PROTOCOL.md.
"""
import collections
import hashlib
import json
import math
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "experiments/2026-10-20-seal-legend-units"
RAW = ROOT / "data/raw/2026-10-20-seal-legend-units"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
CLEAN = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
BRONZE = ROOT / "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl"
AUDIT = RAW / "plate-audit"
SEED = "2026-10-20-seal-legend-units"
START, END = "<s>", "</s>"
FEATURES = ["be_forward", "be_backward", "pmi", "left_ends_text", "right_starts_text",
            "left_pair_ends_text", "right_pair_starts_text", "pair_count", "crossing_triple_count",
            "left_window_drop", "right_window_drop"]
LAMBDA = 1.0
FOLDS = 5


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path, obj, exist_ok=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not exist_ok:
        raise FileExistsError(path)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


class UnionFind:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


# ------------------------------------------------------------------ Indus inputs
def lines_of(face):
    """Return (lines in reading order within each line, exclusion reason)."""
    code = face["text_code_visual_ltr"].strip("+")
    if face["direction"] == "BUS":
        return None, "boustrophedon"
    if any(ch in code for ch in "[]") or "000" in code.split("/") or any(
            s == "000" for seg in code.split("/") for s in seg.replace("+", "-").split("-")):
        return None, "unknown_or_damaged_sign"
    if any(s == "999" for seg in code.split("/") for s in seg.replace("+", "-").split("-")):
        return None, "blank_space_marker"
    lines = []
    for seg in code.split("/"):
        signs = [s for s in seg.replace("+", "-").split("-") if s]
        if not signs:
            return None, "empty_line"
        if face["direction"] != "L/R":
            signs = signs[::-1]
        lines.append(tuple(signs))
    if len(lines) < 2:
        return None, "single_line"
    return lines, None


def join(lines, order):
    seq = lines if order == "forward" else lines[::-1]
    text, cuts = [], []
    for line in seq:
        text.extend(line)
        cuts.append(len(text))
    return tuple(text), cuts[:-1]


def load_audit():
    """Plate-audit verdicts keyed by record id (empty if the audit files are absent)."""
    out = {}
    for path in sorted(AUDIT.glob("verdicts-*.tsv")):
        with open(path, encoding="utf-8") as f:
            header = f.readline().rstrip("\n").split("\t")
            for line in f:
                if not line.strip():
                    continue
                vals = line.rstrip("\n").split("\t")
                row = dict(zip(header, vals + [""] * (len(header) - len(vals))))
                out[row["record_id"].strip()] = {k: v.strip() for k, v in row.items()}
    return out


def audit_order(verdict):
    """Plate-determined reading order (top line first), or None."""
    if not verdict:
        return None
    if verdict.get("division_confirmed") != "yes" or verdict.get("confidence") not in ("high", "medium"):
        return None
    pos = verdict.get("first_segment_is")
    return {"top": "forward", "bottom": "reverse"}.get(pos)


def load_inputs():
    """Clean texts, line-division faces and their shared components and folds."""
    clean_rows = [r for r in read_jsonl(CLEAN) if r["clean_rtl_singleline"] and not r["has_unknown_sign"]]
    face_rows = [r for r in read_jsonl(FACES) if "/" in r["text_code_visual_ltr"]]
    all_faces = read_jsonl(FACES)
    audit = load_audit()
    uf = UnionFind()
    for r in all_faces:
        fam = "F:" + r["object_family_id"]
        uf.find(fam)
        if r["source_cisi"] not in ("-", ""):
            uf.union(fam, "C:" + r["source_cisi"])
    texts = collections.OrderedDict()
    for r in clean_rows:
        t = tuple(r["signs_reading_rtl"])
        uf.union("F:" + r["object_family_id"], "T:" + "-".join(t))
        d = texts.setdefault(t, {"text": t, "records": [], "families": set(), "types": set(), "sites": set()})
        d["records"].append(r["record_id"])
        d["families"].add(r["object_family_id"])
        d["types"].add(r["object_type"])
        d["sites"].add(r["site"])
    faces, excluded = [], collections.Counter()
    for r in face_rows:
        lines, why = lines_of(r)
        if lines is None:
            excluded[why] += 1
            continue
        verdict = audit.get(r["record_id"])
        if verdict and verdict.get("division_confirmed") == "no":
            excluded["plate_audit_division_not_confirmed"] += 1
            continue
        f = {"record_id": r["record_id"], "family": r["object_family_id"], "cisi": r["source_cisi"],
             "site": r["site"], "type": r["object_type"], "lines": lines, "audit": verdict,
             "order": audit_order(verdict)}
        for o in ("forward", "reverse"):
            t, cuts = join(lines, o)
            f[o] = {"text": t, "cuts": cuts}
            uf.union("F:" + r["object_family_id"], "T:" + "-".join(t))
        faces.append(f)
    comp_members = collections.defaultdict(set)
    for d in texts.values():
        d["component"] = uf.find("T:" + "-".join(d["text"]))
    for f in faces:
        f["component"] = uf.find("F:" + f["family"])
    for d in texts.values():
        comp_members[d["component"]].update(d["families"])
    for f in faces:
        comp_members[f["component"]].add(f["family"])
    fold = {}
    for c, fams in comp_members.items():
        key = min(fams, key=lambda s: (len(s), s))
        fold[c] = int(hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest(), 16) % FOLDS
    for d in texts.values():
        d["fold"] = fold[d["component"]]
    for f in faces:
        f["fold"] = fold[f["component"]]
    return list(texts.values()), faces, dict(excluded), uf


def is_seal(d):
    return any(t.startswith("SEAL") for t in d["types"])


def held_components(texts):
    """Components holding the calibration-and-agreement set H (PROTOCOL section 5)."""
    comps = {d["component"] for d in texts if is_seal(d) and len(d["text"]) >= 3}
    return {c for c in comps if int(hashlib.sha256(f"{SEED}:H:{c}".encode()).hexdigest(), 16) % 100 < 15}


# ------------------------------------------------------------------ corpus statistics
def _entropy(counter):
    n = sum(counter.values())
    if not n:
        return 0.0
    return -sum(v / n * math.log2(v / n) for v in counter.values() if v > 0)


class Stats:
    """Counts over distinct texts that can remove one component at a time."""

    MAXSUB = 12

    def __init__(self, items):
        """items: iterable of (text tuple, component key)."""
        self.uni, self.bi, self.tri = collections.Counter(), collections.Counter(), collections.Counter()
        self.start, self.end = collections.Counter(), collections.Counter()
        self.prefix, self.suffix = collections.Counter(), collections.Counter()
        self.sub = collections.Counter()
        self.nxt = collections.defaultdict(collections.Counter)
        self.prv = collections.defaultdict(collections.Counter)
        self.by_comp = collections.defaultdict(list)
        self.n1 = self.n2 = 0
        for t, c in items:
            self.by_comp[c].append(tuple(t))
            self._add(tuple(t), 1)

    def _add(self, t, s):
        L = len(t)
        for x in t:
            self.uni[x] += s
        self.n1 += s * L
        for i in range(L - 1):
            self.bi[t[i:i + 2]] += s
        self.n2 += s * max(L - 1, 0)
        for i in range(L - 2):
            self.tri[t[i:i + 3]] += s
        self.start[t[0]] += s
        self.end[t[-1]] += s
        for k in (1, 2, 3):
            if L >= k:
                self.prefix[t[:k]] += s
                self.suffix[t[-k:]] += s
        subs = {t[i:j] for i in range(L) for j in range(i + 1, min(L, i + self.MAXSUB) + 1)}
        for w in subs:
            self.sub[w] += s
        f = (START,) + t + (END,)
        for i in range(1, len(f)):
            self.nxt[(f[i - 1],)][f[i]] += s
            if i >= 2:
                self.nxt[(f[i - 2], f[i - 1])][f[i]] += s
        r = (END,) + t[::-1] + (START,)
        for i in range(1, len(r)):
            self.prv[(r[i - 1],)][r[i]] += s
            if i >= 2:
                self.prv[(r[i - 2], r[i - 1])][r[i]] += s

    @contextmanager
    def without(self, component):
        texts = self.by_comp.get(component, [])
        for t in texts:
            self._add(t, -1)
        try:
            yield self
        finally:
            for t in texts:
                self._add(t, 1)

    def _be(self, table, s, j):
        rises = [_entropy(table[(s[j - 1],)]) - _entropy(table[(s[j - 2],)])]
        if j >= 3:
            rises.append(_entropy(table[(s[j - 2], s[j - 1])]) - _entropy(table[(s[j - 3], s[j - 2])]))
        return sum(rises) / len(rises)

    def features(self, t, i):
        t = tuple(t)
        L = len(t)
        a, b = t[i - 1], t[i]
        s = (START,) + t
        fwd = self._be(self.nxt, s, i + 1)
        r = (END,) + t[::-1]
        bwd = self._be(self.prv, r, (L - i) + 1)
        n1, n2 = max(self.n1, 1), max(self.n2, 1)
        pmi = (math.log((self.bi[(a, b)] + 0.5) / n2) - math.log((self.uni[a] + 0.5) / n1)
               - math.log((self.uni[b] + 0.5) / n1))
        left_end = math.log((self.end[a] + 0.5) / (self.uni[a] + 1))
        right_start = math.log((self.start[b] + 0.5) / (self.uni[b] + 1))
        left_pair = math.log1p(self.suffix[t[max(0, i - 2):i]])
        right_pair = math.log1p(self.prefix[t[i:min(L, i + 2)]])
        pair = math.log1p(self.bi[(a, b)])
        crossing = [self.tri[t[i - 2:i + 1]]] if i >= 2 else []
        if i + 1 < L:
            crossing.append(self.tri[t[i - 1:i + 2]])
        cross = math.log1p(max(crossing)) if crossing else 0.0
        k = min(i, 2)
        ldrop = math.log1p(self.sub[t[i - k:i]]) - math.log1p(self.sub[t[i - k:i + 1]])
        k = min(L - i, 2)
        rdrop = math.log1p(self.sub[t[i:i + k]]) - math.log1p(self.sub[t[i - 1:i + k]])
        return [fwd, bwd, pmi, left_end, right_start, left_pair, right_pair, pair, cross, ldrop, rdrop]

    def text_features(self, t):
        return [self.features(t, i) for i in range(1, len(t))]


def layout(t_len, i):
    r = i / t_len
    return [r, r * r]


# ------------------------------------------------------------------ conditional-logit line-break model
class BreakModel:
    """Where a scribe breaks a line: softmax over positions of unit score plus a layout term.

    Only the unit part (weights on FEATURES) is used to segment; the layout part absorbs the
    preference for balanced or top-heavy lines.
    """

    def __init__(self, lam=LAMBDA):
        self.lam = lam

    def fit(self, observations):
        """observations: list of (X unit features [n_pos x k], Z layout [n_pos x 2], chosen index, weight)."""
        allx = np.vstack([np.asarray(x, float) for x, z, c, w in observations])
        self.mu = allx.mean(axis=0)
        self.sd = allx.std(axis=0)
        self.sd[self.sd == 0] = 1.0
        obs = [((np.asarray(x, float) - self.mu) / self.sd, np.asarray(z, float), c, w) for x, z, c, w in observations]
        k = obs[0][0].shape[1] + obs[0][1].shape[1]

        def loss(theta):
            total, grad = 0.0, np.zeros(k)
            for x, z, c, w in obs:
                d = np.hstack([x, z])
                s = d @ theta
                m = s.max()
                p = np.exp(s - m)
                zsum = p.sum()
                p /= zsum
                total -= w * (s[c] - m - math.log(zsum))
                grad -= w * (d[c] - p @ d)
            total += 0.5 * self.lam * theta @ theta
            grad += self.lam * theta
            return total, grad

        res = minimize(loss, np.zeros(k), jac=True, method="L-BFGS-B")
        self.theta = res.x
        self.w_unit = res.x[:len(self.mu)]
        self.w_layout = res.x[len(self.mu):]
        self.converged = bool(res.success)
        return self

    def unit_scores(self, X):
        X = (np.asarray(X, float) - self.mu) / self.sd
        return X @ self.w_unit

    def choose_threshold(self, labelled):
        """labelled: list of (scores array, set of labelled positions as 0-based indices, weight).

        Returns the cut-off maximizing recall at labelled positions minus the cut rate at the
        other positions (Youden J), pooled with the given weights; ties go to the higher cut-off.
        """
        pos, neg = [], []
        for scores, chosen, w in labelled:
            for j, s in enumerate(scores):
                (pos if j in chosen else neg).append((float(s), w))
        cands = sorted({s for s, _ in pos + neg})
        mids = [cands[0] - 1.0] + [(a + b) / 2 for a, b in zip(cands, cands[1:])] + [cands[-1] + 1.0]
        wp = sum(w for _, w in pos)
        wn = sum(w for _, w in neg)
        best = None
        for tau in mids:
            rec = sum(w for s, w in pos if s > tau) / wp
            rate = sum(w for s, w in neg if s > tau) / wn
            j = rec - rate
            if best is None or j > best[0] + 1e-12 or (abs(j - best[0]) <= 1e-12 and tau > best[1]):
                best = (j, tau)
        self.tau = best[1]
        self.train_j = best[0]
        return self.tau

    def cuts(self, X):
        if not len(X):
            return []
        s = self.unit_scores(X)
        return [j + 1 for j, v in enumerate(s) if v > self.tau]

    def to_json(self):
        return {"features": FEATURES, "lambda": self.lam, "mu": self.mu.tolist(), "sd": self.sd.tolist(),
                "w_unit": self.w_unit.tolist(), "w_layout": self.w_layout.tolist(), "tau": self.tau,
                "train_j": self.train_j, "converged": self.converged}

    @classmethod
    def from_json(cls, obj):
        m = cls(obj["lambda"])
        m.mu, m.sd = np.array(obj["mu"]), np.array(obj["sd"])
        m.w_unit, m.w_layout = np.array(obj["w_unit"]), np.array(obj["w_layout"])
        m.tau, m.train_j, m.converged = obj["tau"], obj["train_j"], obj["converged"]
        return m


def j_counts(gold, pred, length):
    g, p = set(gold), set(pred)
    return {"hits": len(g & p), "required": len(g), "other_cuts": len(p - g), "other_slots": length - 1 - len(g)}


def pooled_j(rows, weights=None):
    weights = weights or [1.0] * len(rows)
    h = sum(w * r["hits"] for r, w in zip(rows, weights))
    q = sum(w * r["required"] for r, w in zip(rows, weights))
    o = sum(w * r["other_cuts"] for r, w in zip(rows, weights))
    s = sum(w * r["other_slots"] for r, w in zip(rows, weights))
    rec = h / q if q else float("nan")
    rate = o / s if s else float("nan")
    return {"recall": rec, "rate_elsewhere": rate, "j": rec - rate}


def auc_within(scores, gold_idx):
    """Share of (division, other position) pairs in one face where the division scores higher; ties count half."""
    others = [s for j, s in enumerate(scores) if j not in gold_idx]
    if not others:
        return None
    tot = 0.0
    for g in gold_idx:
        for s in others:
            tot += 1.0 if scores[g] > s else 0.5 if scores[g] == s else 0.0
    return tot / (len(gold_idx) * len(others))


# ------------------------------------------------------------------ lexicon segmentation (RULES.md)
def closing_formula(t, stock, max_len=4):
    """Longest final stretch of t, shorter than t, that is in the closing stock."""
    for k in range(min(max_len, len(t) - 1), 0, -1):
        if tuple(t[-k:]) in stock:
            return tuple(t[-k:])
    return None


def min_units(t, lexicon, max_len=6):
    """Fewest-unit cover of t by lexicon units (single signs always allowed).

    Ties: prefer the segmentation whose unit lengths, read from the end of the text, are larger
    at the first place they differ.
    """
    t = tuple(t)
    L = len(t)
    best = [None] * (L + 1)  # best[j] = (n_units, lengths from the end as negative tuple) for suffix t[j:]
    best[L] = (0, ())
    choice = [None] * (L + 1)
    for j in range(L - 1, -1, -1):
        for k in range(1, min(max_len, L - j) + 1):
            u = t[j:j + k]
            if k > 1 and u not in lexicon:
                continue
            rest = best[j + k]
            if rest is None:
                continue
            cand = (rest[0] + 1, rest[1] + (-k,))
            if best[j] is None or cand < best[j]:
                best[j], choice[j] = cand, k
    # the tuple stores lengths from the END backwards, since suffixes are built first
    cuts, j = [], 0
    while j < L:
        j += choice[j]
        if j < L:
            cuts.append(j)
    return cuts


def segment_by_rules(t, lexicon, stock):
    t = tuple(t)
    close = closing_formula(t, stock)
    if close is None:
        return {"closing": None, "cuts": min_units(t, lexicon)}
    opening = t[:len(t) - len(close)]
    cuts = min_units(opening, lexicon) + [len(opening)]
    return {"closing": close, "cuts": cuts}
