#!/usr/bin/env python3
"""Study C: test the allograph and homophone structure of Yajnadevam's key against
substitution, neighbour and positional evidence internal to the Lipi corpus.

Implements PROTOCOL.md in this directory. Writes tracked aggregates to
run-YYYY-MM-DD/ and local-only example lists (with inscription sequences) to
data/raw/2026-10-12-decipherment-claim-tests/allographs/.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KEY = ROOT / "data/lipi/src/assets/data/xlits.csv"
CORPUS = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
MAYIG = ROOT / "data/normalized/mayig_wells_class_crosswalk.json"
PROTOCOL = HERE / "PROTOCOL.md"
LOCAL = ROOT / "data/raw/2026-10-12-decipherment-claim-tests/allographs"

NONSIGNS = {"000", "999"}
VOWELS = set("aAiIuUeEoO")
R_NULL = 2000
B_BOOT = 2000
SEED_NULL = 20261012
SEED_BOOT = 20261013
MIN_STRATUM = 5
JAR_STROKES = {"740": 0, "741": 1, "742": 2, "743": 2, "744": 2,
               "745": 3, "746": 3, "747": 3, "748": 4}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- key table

class Key:
    def __init__(self, path: Path):
        with path.open(encoding="utf-8", newline="") as handle:
            self.rows = list(csv.DictReader(handle))
        self.order = [r["sign"] for r in self.rows]
        self.xlit = {r["sign"]: r["xlit"] for r in self.rows}
        self.canonical = {r["sign"]: r["canonical"] for r in self.rows}
        self.signs = [s for s in self.order if s not in NONSIGNS]

    def kind(self, s: str) -> str:
        c = self.canonical[s]
        if "-" in c:
            return "ligature"
        return "base" if c == s else "variant"

    def root(self, s: str) -> str:
        seen = set()
        while self.kind(s) == "variant":
            if s in seen:
                raise ValueError(f"canonical cycle at {s}")
            seen.add(s)
            s = self.canonical[s]
        return s

    def components(self, s: str, written_order: bool = False) -> list[str]:
        parts = self.canonical[s].split("-")
        return parts if written_order else list(reversed(parts))

    def value(self, s: str, depth: int = 0) -> str:
        """resolveXlit in glyphs.vue: own xlit, else root/canonical, else components."""
        if depth > 8:
            return ""
        own = self.xlit[s]
        if own:
            return own
        c = self.canonical[s]
        if c == s:
            return ""
        if "-" in c:
            return "".join(self.value(x, depth + 1) for x in self.components(s))
        return self.value(c, depth + 1)

    def index_vue_values(self) -> dict[str, str]:
        """Emulate index.vue mkregex in CSV order with json-2-csv number parsing."""
        def parsed_is_number(text: str) -> bool:
            try:
                return isinstance(json.loads(text), (int, float))
            except (ValueError, json.JSONDecodeError):
                return False
        state = dict(self.xlit)
        for s in self.order:
            c = self.canonical[s]
            if not c or parsed_is_number(c):
                if c in state:
                    state[s] = state[c]
                continue
            lit = "".join(state.get(item, "") for item in reversed(c.split("-")))
            state[s] = state[s] or lit
        return state


def pooled(value: str) -> str:
    skeleton = "".join("s" if ch == "h" else ch for ch in value if ch not in VOWELS)
    if skeleton:
        return skeleton
    vowel = value.replace("A", "a")
    return "V:" + vowel


# ---------------------------------------------------------------- corpus

def load_corpus(path: Path):
    records = [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]
    seqs = [tuple(r["signs_reading_rtl"]) for r in records]
    mult = collections.Counter(seqs)
    unique = sorted(mult)
    return records, unique, mult


def minimal_pairs(texts, weights, min_len):
    """Count text pairs of equal length differing at exactly one position, by sign pair."""
    groups = collections.defaultdict(collections.Counter)
    for text, w in zip(texts, weights):
        n = len(text)
        if n < min_len:
            continue
        for i in range(n):
            groups[(n, i, text[:i] + text[i + 1:])][text[i]] += w
    mp = collections.Counter()
    for group in groups.values():
        if len(group) < 2:
            continue
        items = sorted(group.items())
        for (a, wa), (b, wb) in itertools.combinations(items, 2):
            mp[(a, b)] += wa * wb
    return mp, groups


def jsd_matrix(P: np.ndarray) -> np.ndarray:
    """Pairwise base-2 Jensen-Shannon divergence between the rows of P."""
    with np.errstate(divide="ignore", invalid="ignore"):
        H = -np.where(P > 0, P * np.log2(P), 0.0).sum(1)
    out = np.empty((P.shape[0], P.shape[0]))
    for i in range(P.shape[0]):
        M = 0.5 * (P[i][None, :] + P)
        with np.errstate(divide="ignore", invalid="ignore"):
            HM = -np.where(M > 0, M * np.log2(M), 0.0).sum(1)
        out[i] = HM - 0.5 * (H[i] + H)
    np.clip(out, 0.0, None, out=out)
    return out


def smooth(counts: np.ndarray, beta: float) -> np.ndarray:
    q = counts.sum(0) / counts.sum()
    totals = counts.sum(1, keepdims=True)
    return (counts + beta * q[None, :]) / (totals + beta)


class Profiles:
    """Count-based statistics for every attested code in one analysis population."""

    def __init__(self, texts, weights, codes, ctx_map=None):
        self.codes = codes
        self.idx = {c: i for i, c in enumerate(codes)}
        ctx_map = ctx_map or {}
        ctx_codes = sorted({ctx_map.get(c, c) for c in codes})
        cidx = {c: i for i, c in enumerate(ctx_codes)}
        n, d = len(codes), len(ctx_codes) + 1
        self.left = np.zeros((n, d))
        self.right = np.zeros((n, d))
        self.pos = np.zeros((n, 4))  # initial, medial, final, sole
        for text, w in zip(texts, weights):
            L = len(text)
            for i, s in enumerate(text):
                a = self.idx[s]
                self.left[a, cidx[ctx_map.get(text[i - 1], text[i - 1])] if i > 0 else d - 1] += w
                self.right[a, cidx[ctx_map.get(text[i + 1], text[i + 1])] if i < L - 1 else d - 1] += w
                cat = 3 if L == 1 else (0 if i == 0 else (2 if i == L - 1 else 1))
                self.pos[a, cat] += w

    def matrices(self, beta):
        jl = jsd_matrix(smooth(self.left, beta))
        jr = jsd_matrix(smooth(self.right, beta))
        jp = jsd_matrix(smooth(self.pos, beta))
        return {"neighbour": 0.5 * (jl + jr), "left": jl, "right": jr, "position": jp}


# ---------------------------------------------------------------- null machinery

def strata_for(codes, counts, k):
    universe = [c for c in codes if counts[c] >= k]
    by = collections.defaultdict(list)
    for c in universe:
        by[int(math.floor(math.log2(counts[c])))].append(c)
    levels = sorted(by, reverse=True)
    merged, carry = [], []
    for lv in levels:
        carry = carry + by[lv]
        if len(carry) >= MIN_STRATUM:
            merged.append(sorted(carry))
            carry = []
    if carry:
        if merged:
            merged[-1] = sorted(merged[-1] + carry)
        else:
            merged.append(sorted(carry))
    return universe, merged


def permutations(rng, n_codes, idx, strata, R):
    """R stratified permutations as an R x n_codes index array (identity outside the universe)."""
    sigma = np.tile(np.arange(n_codes), (R, 1))
    for stratum in strata:
        ids = np.array([idx[c] for c in stratum])
        draws = np.argsort(rng.random((R, len(ids))), axis=1)
        sigma[:, ids] = ids[draws]
    return sigma


def cluster_boot(values, clusters, rng, B):
    labels = sorted(set(clusters))
    members = collections.defaultdict(list)
    for v, c in zip(values, clusters):
        members[c].append(v)
    sums = np.array([sum(members[c]) for c in labels])
    sizes = np.array([len(members[c]) for c in labels])
    picks = rng.integers(0, len(labels), size=(B, len(labels)))
    boot = sums[picks].sum(1) / sizes[picks].sum(1)
    return boot


def pair_boot(values, rng, B):
    values = np.asarray(values)
    picks = rng.integers(0, len(values), size=(B, len(values)))
    return values[picks].mean(1)


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running = {}, 0.0
    for rank, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - rank) * p))
        adjusted[name] = running
    return adjusted


def poisson_binomial_upper(probs, observed):
    dist = np.zeros(len(probs) + 1)
    dist[0] = 1.0
    for p in probs:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return float(dist[observed:].sum()), float(np.dot(np.arange(len(dist)), dist))


# ---------------------------------------------------------------- pair sets

def build_pairsets(key: Key, mayig: dict):
    nonlig = [s for s in key.signs if key.kind(s) != "ligature"]
    roots = collections.defaultdict(list)
    for s in nonlig:
        roots[key.root(s)].append(s)
    P1 = {}
    for r, members in roots.items():
        for a, b in itertools.combinations(sorted(members), 2):
            P1[(a, b)] = r
    bases = [s for s in key.signs if key.kind(s) == "base"]
    by_value = collections.defaultdict(list)
    for s in bases:
        by_value[pooled(key.value(s))].append(s)
    P2 = {}
    for v, members in by_value.items():
        for a, b in itertools.combinations(sorted(members), 2):
            P2[(a, b)] = v
    by_strict = collections.defaultdict(list)
    for s in bases:
        by_strict[key.value(s)].append(s)
    P2_strict = {}
    for v, members in by_strict.items():
        for a, b in itertools.combinations(sorted(members), 2):
            P2_strict[(a, b)] = v
    by_value_all = collections.defaultdict(list)
    for s in nonlig:
        by_value_all[pooled(key.value(s))].append(s)
    P2_all = {}
    for v, members in by_value_all.items():
        for a, b in itertools.combinations(sorted(members), 2):
            if key.root(a) != key.root(b):
                P2_all[(a, b)] = v
    classes = mayig["by_wells_id"]
    P3 = {}
    for a, b in itertools.combinations(sorted(classes), 2):
        shared = sorted(set(classes[a]) & set(classes[b]))
        if shared:
            P3[(a, b)] = shared[0]
    sets = {"P1": P1, "P2": P2, "P3": P3,
            "P1_in": {p: c for p, c in P1.items() if p in P3},
            "P1_out": {p: c for p, c in P1.items()
                       if p[0] in classes and p[1] in classes and p not in P3},
            "P1_unmapped": {p: c for p, c in P1.items()
                            if not (p[0] in classes and p[1] in classes)},
            "P3_only": {p: c for p, c in P3.items() if p not in P1},
            "P2_strict": P2_strict, "P2_all": P2_all}
    return sets, roots, by_value, by_value_all


# ---------------------------------------------------------------- set tests

def test_sets(pairsets, counts, codes, mp, mats, k, rng_null, rng_boot, exclude=None,
              set_names=None, keep_pairs=False):
    idx = {c: i for i, c in enumerate(codes)}
    pool = [c for c in codes if not exclude or c not in exclude]
    universe, strata = strata_for(pool, counts, k)
    sigma = permutations(rng_null, len(codes), idx, strata, R_NULL)
    n = len(codes)
    mpm = np.zeros((n, n))
    for (a, b), v in mp.items():
        if a in idx and b in idx:
            mpm[idx[a], idx[b]] = mpm[idx[b], idx[a]] = v
    measures = {"mp": mpm, "mp_any": (mpm > 0).astype(float),
                "neighbour": mats["neighbour"], "left": mats["left"],
                "right": mats["right"], "position": mats["position"]}
    uset = set(universe)
    out = {"k": k, "universe_codes": len(universe),
           "strata": [{"min_count": min(counts[c] for c in s), "max_count": max(counts[c] for c in s),
                       "codes": len(s)} for s in strata], "sets": {}}
    pair_rows = {}
    for name in set_names or pairsets:
        pairs = sorted(p for p in pairsets[name] if p[0] in uset and p[1] in uset)
        clusters = [pairsets[name][p] for p in pairs]
        entry = {"pairs": len(pairs), "clusters": len(set(clusters)), "measures": {}}
        if not pairs:
            out["sets"][name] = entry
            continue
        ia = np.array([idx[a] for a, _ in pairs])
        ib = np.array([idx[b] for _, b in pairs])
        sa, sb = sigma[:, ia], sigma[:, ib]
        for mname, M in measures.items():
            obs = M[ia, ib]
            null = M[sa, sb]
            null_means = null.mean(1)
            expected = null.mean(0)
            excess = obs - expected
            m = float(obs.mean())
            p_high = (1 + int((null_means >= m - 1e-12).sum())) / (R_NULL + 1)
            p_low = (1 + int((null_means <= m + 1e-12).sum())) / (R_NULL + 1)
            cb = cluster_boot(excess.tolist(), clusters, rng_boot, B_BOOT)
            pb = pair_boot(excess, rng_boot, B_BOOT)
            res = {"observed_mean": m, "null_mean": float(null_means.mean()),
                   "null_q025": float(np.quantile(null_means, 0.025)),
                   "null_q975": float(np.quantile(null_means, 0.975)),
                   "p_high": p_high, "p_low": p_low,
                   "p_two_sided": min(1.0, 2 * min(p_high, p_low)),
                   "percentile": float((null_means < m).mean() * 100),
                   "mean_excess": float(excess.mean()),
                   "excess_ci_cluster": [float(np.quantile(cb, 0.025)), float(np.quantile(cb, 0.975))],
                   "excess_ci_pair": [float(np.quantile(pb, 0.025)), float(np.quantile(pb, 0.975))]}
            if mname == "mp":
                res["ratio_to_null"] = m / float(null_means.mean()) if null_means.mean() > 0 else None
                res["pairs_with_mp"] = int((obs > 0).sum())
                res["total_mp"] = int(obs.sum())
            entry["measures"][mname] = res
            if keep_pairs:
                for j, p in enumerate(pairs):
                    pair_rows.setdefault((name, p), {})[mname] = (float(obs[j]), float(expected[j]))
            entry.setdefault("_excess", {})[mname] = (excess, clusters)
        out["sets"][name] = entry
    return out, pair_rows


def compare(entry_a, entry_b, measure, rng):
    ea, ca = entry_a["_excess"][measure]
    eb, cb = entry_b["_excess"][measure]
    ba = cluster_boot(list(ea), ca, rng, B_BOOT)
    bb = cluster_boot(list(eb), cb, rng, B_BOOT)
    diff = ba - bb
    return {"difference_in_mean_excess": float(ea.mean() - eb.mean()),
            "ci_cluster": [float(np.quantile(diff, 0.025)), float(np.quantile(diff, 0.975))]}


def strip(result):
    for entry in result["sets"].values():
        entry.pop("_excess", None)
    return result


# ---------------------------------------------------------------- secondary tests

def jar_test(unique):
    probs_order, probs_final, conform_order, conform_final = [], [], 0, 0
    rel = {"stroked": [], "unstroked": []}
    n_texts = 0
    for text in unique:
        L = len(text)
        jars = [(i, JAR_STROKES[s]) for i, s in enumerate(text) if s in JAR_STROKES]
        for i, st in jars:
            rel["stroked" if st else "unstroked"].append(i / (L - 1))
        if len(jars) < 2 or not any(st for _, st in jars):
            continue
        n_texts += 1
        strokes = [st for _, st in jars]
        mult = collections.Counter(strokes)
        prob = math.prod(math.factorial(v) for v in mult.values()) / math.factorial(len(strokes))
        probs_order.append(prob)
        conform_order += all(x >= y for x, y in zip(strokes, strokes[1:]))
        probs_final.append(mult[0] / len(strokes))
        conform_final += strokes[-1] == 0
    p_order, e_order = poisson_binomial_upper(probs_order, conform_order)
    p_final, e_final = poisson_binomial_upper(probs_final, conform_final)
    return {"texts": n_texts,
            "non_increasing": {"observed": conform_order, "expected": e_order, "p_upper": p_order},
            "final_unstroked": {"observed": conform_final, "expected": e_final, "p_upper": p_final},
            "relative_position": {k: {"tokens": len(v), "mean": float(np.mean(v)) if v else None,
                                      "initial_share": float(np.mean([x == 0 for x in v])) if v else None,
                                      "final_share": float(np.mean([x == 1 for x in v])) if v else None}
                                  for k, v in rel.items()}}


def consistency_test(unique, key, rng, include_jar):
    per_root = collections.defaultdict(lambda: ([], []))
    for t, text in enumerate(unique):
        for s in text:
            if key.kind(s) == "ligature":
                continue
            r = key.root(s)
            per_root[r][0].append(t)
            per_root[r][1].append(s)
    observed, null_total, eligible_texts, roots_used = 0, np.zeros(R_NULL), 0, 0
    for r, (tids, codes) in sorted(per_root.items()):
        if r == "740" and not include_jar:
            continue
        if len(set(codes)) < 2:
            continue
        tids = np.array(tids)
        order = np.argsort(tids, kind="stable")
        tids = tids[order]
        code_ids = np.unique(np.array(codes)[order], return_inverse=True)[1]
        starts = np.flatnonzero(np.r_[True, tids[1:] != tids[:-1]])
        sizes = np.diff(np.r_[starts, len(tids)])
        multi = sizes >= 2
        if not multi.any():
            continue
        roots_used += 1
        eligible_texts += int(multi.sum())
        mn = np.minimum.reduceat(code_ids, starts)
        mx = np.maximum.reduceat(code_ids, starts)
        observed += int(((mn != mx) & multi).sum())
        perm = np.argsort(rng.random((R_NULL, len(code_ids))), axis=1)
        pc = code_ids[perm]
        mnp = np.minimum.reduceat(pc, starts, axis=1)
        mxp = np.maximum.reduceat(pc, starts, axis=1)
        null_total += ((mnp != mxp) & multi[None, :]).sum(1)
    p_low = (1 + int((null_total <= observed).sum())) / (R_NULL + 1)
    return {"include_jar_root": include_jar, "roots": roots_used, "texts_with_repeat": eligible_texts,
            "mixed_observed": observed, "mixed_null_mean": float(null_total.mean()),
            "mixed_null_q025": float(np.quantile(null_total, 0.025)),
            "mixed_null_q975": float(np.quantile(null_total, 0.975)), "p_low": p_low}


def ligature_test(unique, key, counts, codes, rng, written_order):
    textset = set(unique)
    idx = {c: i for i, c in enumerate(codes)}
    universe, strata = strata_for(codes, counts, 1)
    sigma = permutations(rng, len(codes), idx, strata, R_NULL)
    occurrences, matches, types_with_match, examples = [], 0, set(), []
    for text in unique:
        for i, s in enumerate(text):
            if s in key.canonical and key.kind(s) == "ligature":
                comps = key.components(s, written_order)
                occurrences.append((text, i, s, comps))
                new = text[:i] + tuple(comps) + text[i + 1:]
                if new in textset:
                    matches += 1
                    types_with_match.add(s)
                    examples.append({"ligature": s, "components": comps, "text": list(text),
                                     "decomposed": list(new)})
    null = np.zeros(R_NULL, dtype=int)
    for text, i, s, comps in occurrences:
        comp_idx = [idx.get(c) for c in comps]
        for r in range(R_NULL):
            mapped = tuple(codes[sigma[r, j]] if j is not None else c for j, c in zip(comp_idx, comps))
            if text[:i] + mapped + text[i + 1:] in textset:
                null[r] += 1
    p_high = (1 + int((null >= matches).sum())) / (R_NULL + 1)
    return ({"written_order": written_order, "ligature_types": len({o[2] for o in occurrences}),
             "occurrences": len(occurrences), "matching_occurrences": matches,
             "ligature_types_with_match": len(types_with_match),
             "null_mean": float(null.mean()), "null_q975": float(np.quantile(null, 0.975)),
             "p_high": p_high}, examples)


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="run-2026-10-12")
    args = parser.parse_args()
    outdir = HERE / args.run
    outdir.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)

    key = Key(KEY)
    mayig = json.loads(MAYIG.read_text(encoding="utf-8"))
    records, unique, mult = load_corpus(CORPUS)
    dup_texts = unique
    dup_weights = [mult[t] for t in unique]
    uni_weights = [1] * len(unique)
    counts = collections.Counter(s for t in unique for s in t)
    counts_dup = collections.Counter()
    for t in unique:
        for s in t:
            counts_dup[s] += mult[t]
    codes = sorted(counts)
    sets, roots, by_value, by_value_all = build_pairsets(key, mayig)
    classes = mayig["by_wells_id"]

    # ---------------- inventory
    kinds = collections.Counter(key.kind(s) for s in key.signs)
    chained = [s for s in key.signs if key.kind(s) == "variant" and key.kind(key.canonical[s]) == "variant"]
    value_diff = [{"sign": s, "own": key.xlit[s], "root": key.root(s), "root_value": key.value(key.root(s))}
                  for s in key.signs if key.kind(s) == "variant" and key.xlit[s]
                  and pooled(key.xlit[s]) != pooled(key.value(key.root(s)))]
    vue = key.index_vue_values()
    vue_diff = [{"sign": s, "glyphs_vue": key.value(s), "index_vue": vue[s]}
                for s in key.signs if vue[s] != key.value(s)]
    group_rows = []
    nonlig_codes = [s for s in key.signs if key.kind(s) != "ligature"]
    tokens_total = sum(counts.values())
    tokens_total_dup = sum(counts_dup.values())
    lig_tokens = sum(v for s, v in counts.items() if key.kind(s) == "ligature")
    for v, members in sorted(by_value_all.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        group_rows.append({"pooled_value": v, "codes": len(members),
                           "roots": len({key.root(s) for s in members}),
                           "root_codes": " ".join(sorted({key.root(s) for s in members})),
                           "attested_codes": sum(1 for s in members if counts[s] > 0),
                           "tokens_unique_texts": sum(counts[s] for s in members),
                           "tokens_all_records": sum(counts_dup[s] for s in members)})
    big = {r["pooled_value"] for r in group_rows if r["codes"] >= 10}
    big_tokens = sum(counts[s] for s in nonlig_codes if pooled(key.value(s)) in big)
    big_tokens_dup = sum(counts_dup[s] for s in nonlig_codes if pooled(key.value(s)) in big)
    p1_mapped = [p for p in sets["P1"] if p[0] in classes and p[1] in classes]
    inventory = {
        "key_rows": len(key.rows), "sign_rows": len(key.signs),
        "base_signs": kinds["base"], "variants": kinds["variant"], "ligatures": kinds["ligature"],
        "chained_variants": chained,
        "roots_with_variants": sum(1 for r, m in roots.items() if len(m) > 1),
        "roots_attested": sum(1 for r, m in roots.items() if any(counts[s] for s in m)),
        "root_group_sizes": {r: len(m) for r, m in sorted(roots.items())},
        "distinct_pooled_values_of_bases": len(by_value),
        "bases_per_pooled_value": {v: len(m) for v, m in sorted(by_value.items(), key=lambda kv: -len(kv[1]))},
        "distinct_pooled_values_nonligature_codes": len(by_value_all),
        "values_shared_by_10plus_codes": sorted(big),
        "token_share_values_shared_by_10plus_codes_unique_texts": big_tokens / tokens_total,
        "token_share_values_shared_by_10plus_codes_all_records": big_tokens_dup / tokens_total_dup,
        "tokens_unique_texts": tokens_total, "tokens_all_records": tokens_total_dup,
        "ligature_token_share_unique_texts": lig_tokens / tokens_total,
        "variants_with_own_value_differing_from_root": value_diff,
        "index_vue_value_differences": vue_diff,
        "p1_pairs_both_mayig_mapped": len(p1_mapped),
        "p1_mapped_share_sharing_mayig_class": sum(1 for p in p1_mapped if p in sets["P3"]) / len(p1_mapped),
        "corpus_records": len(records), "unique_texts": len(unique), "attested_codes": len(codes),
    }

    rng_null = np.random.default_rng(SEED_NULL)
    rng_boot = np.random.default_rng(SEED_BOOT)

    # ---------------- primary population: unique texts
    mp3, groups3 = minimal_pairs(unique, uni_weights, 3)
    prof = Profiles(unique, uni_weights, codes)
    mats = prof.matrices(1.0)
    primary_sets = ["P1", "P1_in", "P1_out", "P1_unmapped", "P2", "P3", "P3_only", "P2_strict", "P2_all"]
    analyses = {}
    pair_tables = {}
    for k in (1, 3, 5):
        res, rows = test_sets(sets, counts, codes, mp3, mats, k, rng_null, rng_boot,
                              set_names=primary_sets, keep_pairs=True)
        if k == 3:
            res["comparisons"] = {
                f"{a}_minus_{b}:{m}": compare(res["sets"][a], res["sets"][b], m, rng_boot)
                for a, b in (("P1", "P3"), ("P1_out", "P1_in"))
                for m in ("mp", "neighbour", "position")}
            pvals = {f"{s}:{m}": res["sets"][s]["measures"][m]["p_high" if m == "mp" else "p_low"]
                     for s in ("P1", "P1_out", "P2", "P3") for m in ("mp", "neighbour")}
            res["primary_family_holm"] = {name: {"p": pvals[name], "p_holm": adj, "pass": adj < 0.05}
                                          for name, adj in holm(pvals).items()}
            ppos = {s: res["sets"][s]["measures"]["position"]["p_two_sided"]
                    for s in ("P1", "P1_out", "P2", "P3")}
            res["position_family_holm"] = {
                s: {"p_two_sided": ppos[s], "p_holm": adj,
                    "direction": "lower (shared positions)"
                    if res["sets"][s]["measures"]["position"]["observed_mean"]
                    < res["sets"][s]["measures"]["position"]["null_mean"] else "higher (complementary)"}
                for s, adj in holm(ppos).items()}
        analyses[f"primary_k{k}"] = strip(res)
        pair_tables[k] = rows

    # ---------------- sensitivities at k = 3
    sens_sets = ["P1", "P1_out", "P1_in", "P2", "P3"]
    # with duplicates
    mp_dup, _ = minimal_pairs(dup_texts, dup_weights, 3)
    prof_dup = Profiles(dup_texts, dup_weights, codes)
    res, _ = test_sets(sets, counts_dup, codes, mp_dup, prof_dup.matrices(1.0), 3, rng_null, rng_boot,
                       set_names=sens_sets)
    analyses["sens_with_duplicates_k3"] = strip(res)
    # frames of length >= 2
    mp2, _ = minimal_pairs(unique, uni_weights, 2)
    res, _ = test_sets(sets, counts, codes, mp2, mats, 3, rng_null, rng_boot, set_names=sens_sets)
    analyses["sens_frames_len2_k3"] = strip(res)
    # beta = 0
    res, _ = test_sets(sets, counts, codes, mp3, prof.matrices(0.0), 3, rng_null, rng_boot,
                       set_names=sens_sets)
    analyses["sens_beta0_k3"] = strip(res)
    # contexts collapsed to key roots
    ctx = {s: key.root(s) for s in codes if key.kind(s) != "ligature"}
    prof_root = Profiles(unique, uni_weights, codes, ctx_map=ctx)
    res, _ = test_sets(sets, counts, codes, mp3, prof_root.matrices(1.0), 3, rng_null, rng_boot,
                       set_names=sens_sets)
    analyses["sens_root_collapsed_contexts_k3"] = strip(res)
    # null universe without ligature codes
    ligs = {s for s in codes if key.kind(s) == "ligature"}
    res, _ = test_sets(sets, counts, codes, mp3, mats, 3, rng_null, rng_boot, exclude=ligs,
                       set_names=sens_sets)
    analyses["sens_null_without_ligatures_k3"] = strip(res)

    # ---------------- secondary predictions
    secondary = {
        "S1_jar_direction": jar_test(unique),
        "S2_variant_consistency": consistency_test(unique, key, np.random.default_rng(SEED_NULL + 2), False),
        "S2_variant_consistency_with_jar": consistency_test(unique, key, np.random.default_rng(SEED_NULL + 3), True),
    }
    s3, s3_examples = ligature_test(unique, key, counts, codes, np.random.default_rng(SEED_NULL + 4), False)
    s3w, s3w_examples = ligature_test(unique, key, counts, codes, np.random.default_rng(SEED_NULL + 5), True)
    secondary["S3_conjunct_decomposition"] = s3
    secondary["S3_conjunct_decomposition_written_order"] = s3w

    # ---------------- outputs
    summary = {
        "study": "Study C: allographs and homophones in Yajnadevam's key",
        "protocol": {"path": "PROTOCOL.md", "sha256": sha256(PROTOCOL)},
        "inputs": {p.relative_to(ROOT).as_posix(): sha256(p) for p in (KEY, CORPUS, MAYIG)},
        "parameters": {"R_null": R_NULL, "B_boot": B_BOOT, "seed_null": SEED_NULL, "seed_boot": SEED_BOOT,
                       "min_stratum_codes": MIN_STRATUM, "primary_k": 3, "mp_min_length": 3, "beta": 1.0},
        "inventory": inventory, "analyses": analyses, "secondary": secondary,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with (outdir / "value_groups.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(group_rows[0]))
        writer.writeheader()
        writer.writerows(group_rows)

    for k, rows in pair_tables.items():
        fields = ["set", "a", "b", "cluster", "root_a", "root_b", "value_a", "value_b",
                  "mayig_a", "mayig_b", "count_a", "count_b"]
        mnames = ["mp", "neighbour", "position"]
        for m in mnames:
            fields += [m, m + "_null_expected"]
        with (outdir / f"pairs_k{k}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(fields)
            for (name, (a, b)), stats in sorted(rows.items()):
                if name in ("P2_strict", "P2_all", "P3_only", "P1_in", "P1_out", "P1_unmapped"):
                    continue
                def root_or(s):
                    return key.root(s) if s in key.canonical and key.kind(s) != "ligature" else ""
                def val_or(s):
                    return pooled(key.value(s)) if s in key.canonical else ""
                row = [name, a, b, sets[name][(a, b)], root_or(a), root_or(b), val_or(a), val_or(b),
                       "|".join(classes.get(a, [])), "|".join(classes.get(b, [])), counts[a], counts[b]]
                for m in mnames:
                    o, e = stats[m]
                    row += [f"{o:.6g}", f"{e:.6g}"]
                writer.writerow(row)

    # local-only examples with inscription sequences
    examples = collections.defaultdict(list)
    for (n, i, frame), group in groups3.items():
        if len(group) < 2:
            continue
        for a, b in itertools.combinations(sorted(group), 2):
            for name in ("P1", "P2", "P3"):
                if (a, b) in sets[name] and counts[a] >= 3 and counts[b] >= 3:
                    examples[name].append({"a": a, "b": b, "length": n, "slot": i, "frame": list(frame)})
    (LOCAL / "minimal_pair_examples_k3.json").write_text(
        json.dumps(examples, indent=1) + "\n", encoding="utf-8")
    (LOCAL / "ligature_decomposition_matches.json").write_text(
        json.dumps({"reading_order": s3_examples, "written_order": s3w_examples}, indent=1) + "\n",
        encoding="utf-8")
    print(json.dumps({"primary_family_holm": analyses["primary_k3"]["primary_family_holm"],
                      "position_family_holm": analyses["primary_k3"]["position_family_holm"]}, indent=1))


if __name__ == "__main__":
    main()
