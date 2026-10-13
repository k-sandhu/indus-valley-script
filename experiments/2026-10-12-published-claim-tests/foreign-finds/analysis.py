"""Study B main analysis: matched predictability of texts found outside South Asia.

Implements PROTOCOL.md (frozen 2026-10-12). Usage:
    python analysis.py            # writes run-2026-10-12/ and the local raw outputs
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import ffcore as C

RUN = "run-2026-10-12"
OUT = C.HERE / RUN
RAW_OUT = C.RAW / RUN
NULL_DRAWS = 20000
BOOT_DRAWS = 10000
NULL_SEED = 20261012
BOOT_SEED = 20261013
TOP_INITIAL = {"817", "820", "861"}
RARE_MAX = 2
SECONDARY = ["unseen", "rare", "unsupported", "terminal_absent"]
PERIPHERAL = ["gujarat_kutch", "eastern_headwaters", "kalibangan", "chanhudaro_control",
              "baluchistan_makran", "upper_indus", "south_asian_round"]
QUALIFYING = ["gujarat_kutch", "eastern_headwaters", "kalibangan", "chanhudaro_control"]


# ====================================================================== models
class Model:
    """Bigram/trigram sign model with training-set statistics for secondary measures."""

    def __init__(self, texts: list[dict], vocab_size: int, kind: str = "kn2"):
        self.kind, self.V = kind, vocab_size
        c2, c3 = Counter(), Counter()
        for t in texts:
            for h, w in C.events(t, 3):
                c2[(h[-1], w)] += 1
                if len(h) == 2:
                    c3[(h[0], h[1], w)] += 1
        self.c2 = c2
        self.cu, self.nu = Counter(), Counter()
        for (u, w), c in c2.items():
            self.cu[u] += c
            self.nu[u] += 1
        # Kneser-Ney bigram pieces
        cc = Counter(c2.values())
        self.D2 = cc[1] / (cc[1] + 2 * cc[2])
        cont = Counter(w for (u, w) in c2)
        self.cont, self.cont_total, self.cont_types = cont, len(c2), len(cont)
        ccc = Counter(cont.values())
        self.D1 = ccc[1] / (ccc[1] + 2 * ccc[2])
        # Witten-Bell pieces
        uni = Counter()
        for (u, w), c in c2.items():
            uni[w] += c
        self.uni, self.uni_total, self.uni_types = uni, sum(uni.values()), len(uni)
        # trigram pieces
        self.c3 = c3
        self.cuv, self.nuv = Counter(), Counter()
        for (u, v, w), c in c3.items():
            self.cuv[(u, v)] += c
            self.nuv[(u, v)] += 1
        cc3 = Counter(c3.values())
        self.D3 = cc3[1] / (cc3[1] + 2 * cc3[2]) if c3 else 0.0
        # secondary statistics
        self.tokens = Counter(s for t in texts for s in C.known_signs(t))
        subs = set()
        for t in texts:
            for run, _, _ in C.spans(t):
                n = len(run)
                for i in range(n):
                    for j in range(i + 1, n + 1):
                        subs.add(tuple(run[i:j]))
        self.subs = subs
        self._cache = {}

    def p_cont(self, w):
        return (max(self.cont.get(w, 0) - self.D1, 0.0) / self.cont_total
                + self.D1 * self.cont_types / self.cont_total / self.V)

    def p_kn2(self, u, w):
        cu = self.cu.get(u, 0)
        if cu == 0:
            return self.p_cont(w)
        return (max(self.c2.get((u, w), 0) - self.D2, 0.0) / cu
                + self.D2 * self.nu[u] / cu * self.p_cont(w))

    def p_wb2(self, u, w):
        p1 = (self.uni.get(w, 0) + self.uni_types / self.V) / (self.uni_total + self.uni_types)
        cu = self.cu.get(u, 0)
        if cu == 0:
            return p1
        return (self.c2.get((u, w), 0) + self.nu[u] * p1) / (cu + self.nu[u])

    def p_kn3(self, h, w):
        if len(h) < 2:
            return self.p_kn2(h[-1], w)
        cuv = self.cuv.get((h[0], h[1]), 0)
        lower = self.p_kn2(h[1], w)
        if cuv == 0:
            return lower
        return (max(self.c3.get((h[0], h[1], w), 0) - self.D3, 0.0) / cuv
                + self.D3 * self.nuv[(h[0], h[1])] / cuv * lower)

    def surprisal(self, text: dict) -> float | None:
        bits = []
        if self.kind == "kn3":
            for h, w in C.events(text, 3):
                bits.append(-math.log2(self.p_kn3(h, w)))
        else:
            f = self.p_kn2 if self.kind == "kn2" else self.p_wb2
            for h, w in C.events(text, 2):
                bits.append(-math.log2(f(h[-1], w)))
        return sum(bits) / len(bits) if bits else None

    def secondary(self, text: dict) -> dict:
        ev = list(C.events(text, 2))
        unseen = (sum(1 for h, w in ev if self.c2.get((h[-1], w), 0) == 0) / len(ev)) if ev else None
        ks = C.known_signs(text)
        rare = (sum(1 for s in ks if self.tokens.get(s, 0) <= RARE_MAX) / len(ks)) if ks else None
        runs = [r for r, _, _ in C.spans(text)]
        if runs:
            longest = max(len(r) for r in runs)
            best = 0
            for r in runs:
                n = len(r)
                for i in range(n):
                    for j in range(n, i + best, -1):
                        if tuple(r[i:j]) in self.subs:
                            best = max(best, j - i)
                            break
            unsupported = 1.0 - best / longest
        else:
            unsupported = None
        return {"unseen": unseen, "rare": rare, "unsupported": unsupported}


def reversed_text(text: dict) -> dict:
    return {"lines": [list(reversed(l)) for l in reversed(text["lines"])],
            "single_line": text["single_line"], "start_known": text["end_known"],
            "end_known": text["start_known"], "length": text["length"]}


def descriptive(text: dict) -> dict:
    """Model-free positional measures."""
    out = {"terminal_absent": None, "has740": None, "initial_top3": None,
           "initial_091": None, "adj740": None}
    ks = C.known_signs(text)
    out["has740"] = int("740" in ks) if ks else None
    adj = 0
    for run, _, _ in C.spans(text):
        adj += sum(1 for a, b in zip(run, run[1:]) if a == "740" and b == "740")
    out["adj740"] = int(adj > 0) if ks else None
    if text["single_line"]:
        line = text["lines"][0]
        if text["end_known"] and line[-1] not in (C.UNKNOWN, C.BLANK):
            out["terminal_absent"] = int(line[-1] != "740")
        if text["start_known"] and line[0] not in (C.UNKNOWN, C.BLANK):
            out["initial_top3"] = int(line[0] in TOP_INITIAL)
            out["initial_091"] = int(line[0] == "091")
    return out


# ====================================================================== pools
class Pool:
    def __init__(self, name, faces, vocab_size, kinds=("kn2",)):
        self.name, self.faces, self.V = name, faces, vocab_size
        self.folds = C.assign_folds(faces)
        self.kinds = kinds
        self._models = {}
        self._train_codes = {}
        self.code_count = Counter(f["face"]["text_code_visual_ltr"] for f in faces)
        fam_by_code = defaultdict(set)
        for f in faces:
            fam_by_code[f["face"]["text_code_visual_ltr"]].add(f["face"]["object_family_id"])
        self.fam_by_code = fam_by_code
        self._comp_cache = {}
        self._ex_models = {}

    def training(self, k):
        if k not in self._train_codes:
            seen = {}
            for f, fk in zip(self.faces, self.folds):
                if fk != k:
                    seen.setdefault(f["face"]["text_code_visual_ltr"], f["text"])
            self._train_codes[k] = seen
        return self._train_codes[k]

    def model(self, k, kind="kn2", exclude_code=None):
        """Base fold models are cached; a model that excludes a test text's
        identical code string is refitted and kept only until the next test."""
        tr = self.training(k)
        if exclude_code not in tr:
            exclude_code = None
        key = (k, kind, exclude_code)
        cache = self._models if exclude_code is None else self._ex_models
        if key not in cache:
            texts = [t for c, t in tr.items() if c != exclude_code]
            cache[key] = Model(texts, self.V, kind)
        return cache[key]

    def clear_exclusions(self):
        self._ex_models = {}


def text_stats(model: Model, text: dict, orientation: bool = False) -> dict:
    s = model.surprisal(text)
    if orientation and s is not None:
        r = model.surprisal(reversed_text(text))
        s = min(s, r)
    out = {"surprisal": s}
    out.update(model.secondary(text))
    out.update(descriptive(text))
    return out


def mask_key(text):
    return (text["length"], text["start_known"], text["end_known"], tuple(text["lines"][0]))


def comparator_stats(pool: Pool, j: int, test_text: dict, kind: str, orientation: bool):
    mask = tuple(t if t in (C.UNKNOWN, C.BLANK) else "X" for t in test_text["lines"][0])
    key = (j, test_text["length"], test_text["start_known"], test_text["end_known"], mask, kind,
           orientation)
    if key not in pool._comp_cache:
        w = C.comparator_window(test_text, pool.faces[j]["text"]["lines"][0])
        m = pool.model(pool.folds[j], kind)
        pool._comp_cache[key] = text_stats(m, w, orientation)
    return pool._comp_cache[key]


# ====================================================================== matched scoring
STATS = ["surprisal"] + SECONDARY  # u-framework statistics
DESC = ["has740", "initial_top3", "initial_091", "adj740"]


def r12(x):
    return None if x is None else round(x, 12)


def score_tests(tests, pool: Pool, ladder="primary", kind="kn2", orientation=False):
    results = []
    for f in tests:
        t = f["text"]
        n_ev = sum(1 for _ in C.events(t, 2))
        row = {"record_id": f["record_id"], "family": f["face"]["object_family_id"],
               "site": f["face"]["site"], "region": f["face"]["region"], "group": f["group"],
               "object_type": f["face"]["object_type"], "medium": f["medium"],
               "length": t["length"], "structure": C.structure_string(t),
               "single_line": t["single_line"], "clean": f["clean"], "events": n_ev,
               "subregion": C.west_subregion(f["face"]) if f["group"] == "west_asia" else None}
        if not t["single_line"] or n_ev == 0:
            row["scorable"] = False
            results.append(row)
            continue
        level, idx, tried = C.choose_cell(f["face"], t, pool.faces, ladder)
        row.update({"scorable": level is not None, "level": level, "n_comp": len(idx),
                    "tried": tried})
        if level is None:
            results.append(row)
            continue
        code = f["face"]["text_code_visual_ltr"]
        pool.clear_exclusions()
        test_by_fold = {}
        for k in range(C.K_FOLDS):
            test_by_fold[k] = text_stats(pool.model(k, kind, exclude_code=code), t, orientation)
        comp = [comparator_stats(pool, j, t, kind, orientation) for j in idx]
        comp_folds = [pool.folds[j] for j in idx]
        # Fold-averaged test values (reported) and matched u / delta.
        for s in STATS:
            vals = [test_by_fold[k][s] for k in range(C.K_FOLDS)]
            if any(v is None for v in vals):
                row[s] = None
                row[f"u_{s}"] = None
                continue
            row[s] = float(np.mean(vals))
            xs = np.array([c[s] for c in comp], dtype=float)
            xt = np.array([test_by_fold[k][s] for k in comp_folds], dtype=float)
            xs_r, xt_r = np.round(xs, 12), np.round(xt, 12)
            u = float(np.mean((xt_r > xs_r) + 0.5 * (xt_r == xs_r)))
            row[f"u_{s}"] = u
            row[f"delta_{s}"] = float(np.mean(xt - xs))
            row[f"comp_mean_{s}"] = float(np.mean(xs))
            # leave-one-out u/delta of each comparator, for the null distribution
            n = len(xs_r)
            order = np.sort(xs_r)
            less = np.searchsorted(order, xs_r, side="left")
            leq = np.searchsorted(order, xs_r, side="right")
            eq = leq - less - 1
            row[f"_loo_u_{s}"] = ((less + 0.5 * eq) / (n - 1)).tolist()
            tot = xs.sum()
            row[f"_loo_d_{s}"] = (xs - (tot - xs) / (n - 1)).tolist()
        for s in DESC:
            v = test_by_fold[0][s]
            row[s] = v
            cv = [c[s] for c in comp if c[s] is not None]
            row[f"comp_rate_{s}"] = float(np.mean(cv)) if cv and v is not None else None
        row["terminal740_test"] = test_by_fold[0]["terminal_absent"]
        # whole-text duplication (complete texts only)
        if f["full"]:
            row["whole_text_in_pool"] = int(pool.code_count.get(code, 0) > 0)
            dup = [int(len(pool.fam_by_code[pool.faces[j]["face"]["text_code_visual_ltr"]]) > 1)
                   for j in idx]
            row["comp_rate_duplicated"] = float(np.mean(dup))
        row["_comp_ids"] = [pool.faces[j]["record_id"] for j in idx]
        row["_comp_surprisal"] = [c["surprisal"] for c in comp]
        results.append(row)
    return results


# ====================================================================== statistics
def scorable(rows, stat="surprisal"):
    return [r for r in rows if r.get("scorable") and r.get(f"u_{stat}") is not None]


def group_stat(rows, stat="surprisal", seed_offset=0, null=True):
    rs = scorable(rows, stat)
    n = len(rs)
    if n == 0:
        return {"n": 0}
    u = np.array([r[f"u_{stat}"] for r in rs])
    d = np.array([r[f"delta_{stat}"] for r in rs])
    out = {"n": n, "U": float(u.mean()), "delta": float(d.mean()),
           "objects_above_half": int((u > 0.5).sum()),
           "families": len({r["family"] for r in rs})}
    # bootstrap over families
    fam = defaultdict(list)
    for i, r in enumerate(rs):
        fam[(r["site"], r["family"])].append(i)
    keys = list(fam)
    rng = np.random.default_rng(BOOT_SEED + seed_offset)
    bu, bd = np.empty(BOOT_DRAWS), np.empty(BOOT_DRAWS)
    for b in range(BOOT_DRAWS):
        pick = rng.integers(0, len(keys), len(keys))
        ids = [i for p in pick for i in fam[keys[p]]]
        bu[b], bd[b] = u[ids].mean(), d[ids].mean()
    out["U_ci95"] = [float(np.percentile(bu, 2.5)), float(np.percentile(bu, 97.5))]
    out["delta_ci95"] = [float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))]
    out["_boot_U"] = bu
    if null:
        rng = np.random.default_rng(NULL_SEED + seed_offset)
        nu = np.zeros(NULL_DRAWS)
        nd = np.zeros(NULL_DRAWS)
        for r in rs:
            lu = np.array(r[f"_loo_u_{stat}"])
            ld = np.array(r[f"_loo_d_{stat}"])
            pick = rng.integers(0, len(lu), NULL_DRAWS)
            nu += lu[pick]
            nd += ld[pick]
        nu /= n
        nd /= n
        out["null_U_mean"] = float(nu.mean())
        out["null_U_q025_q975"] = [float(np.quantile(nu, 0.025)), float(np.quantile(nu, 0.975))]
        out["null_U_q95"] = float(np.quantile(nu, 0.95))
        out["p_one_sided_U"] = float((1 + np.sum(nu >= out["U"] - 1e-12)) / (1 + NULL_DRAWS))
        out["p_two_sided_U"] = float((1 + np.sum(np.abs(nu - 0.5) >= abs(out["U"] - 0.5) - 1e-12))
                                     / (1 + NULL_DRAWS))
        out["p_one_sided_delta"] = float((1 + np.sum(nd >= out["delta"] - 1e-12)) / (1 + NULL_DRAWS))
    return out


def diff_ci(a, b):
    """Percentile interval for difference of two independent bootstrap vectors."""
    d = a["_boot_U"] - b["_boot_U"]
    return {"difference": a["U"] - b["U"],
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)
        out[k] = running
    return out


def clean(o):
    if isinstance(o, dict):
        return {(k if isinstance(k, str) else str(k)): clean(v) for k, v in o.items()
                if not str(k).startswith("_")}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


def desc_rates(rows, s):
    rs = [r for r in rows if r.get("scorable") and r.get(s) is not None
          and r.get(f"comp_rate_{s}") is not None]
    if not rs:
        return {"n": 0}
    return {"n": len(rs), "test_count": int(sum(r[s] for r in rs)),
            "test_rate": float(np.mean([r[s] for r in rs])),
            "matched_comparator_rate": float(np.mean([r[f"comp_rate_{s}"] for r in rs]))}


# ====================================================================== main
def main():
    OUT.mkdir(exist_ok=True)
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    faces = C.load_faces()
    V = len(C.vocabulary(faces))
    sa = [f for f in faces if f["group"] == "south_asia"]
    west_all = [f for f in faces if f["group"] == "west_asia"]
    west = [f for f in west_all if f["record_id"] not in C.DUPLICATE_WITNESS]
    central = [f for f in faces if f["group"] == "central_asia"]
    unprov = [f for f in faces if f["group"] == "unprovenanced" and f["medium"] == "round"]

    summary = {"protocol": "PROTOCOL.md (frozen 2026-10-12; see FREEZE-2026-10-12.json)",
               "input_sha256": C.sha256_file(C.FACES), "vocabulary_size_including_end": V,
               "folds": C.K_FOLDS, "null_draws": NULL_DRAWS, "bootstrap_draws": BOOT_DRAWS}

    pool = Pool("south_asia", sa, V)
    summary["pool"] = {"faces": len(sa), "unique_codes": len(pool.code_count),
                       "fold_sizes": dict(sorted(Counter(pool.folds).items()))}

    # ------------------------------------------------ primary scoring
    rows_w = score_tests(west, pool)
    rows_c = score_tests(central, pool)
    rows_u = score_tests(unprov, pool)
    rows_dup = score_tests([f for f in west_all if f["record_id"] in C.DUPLICATE_WITNESS], pool)

    h1_rows = rows_w
    h2_rows = [r for r in rows_w if r["medium"] == "round"]
    nonround_rows = [r for r in rows_w if r["medium"] != "round"]
    H = {}
    H["H1_west_all"] = group_stat(h1_rows, "surprisal", 1)
    H["H2_west_round"] = group_stat(h2_rows, "surprisal", 2)
    hp = holm({"H1": H["H1_west_all"]["p_one_sided_U"], "H2": H["H2_west_round"]["p_one_sided_U"]})
    H["H1_west_all"]["p_holm"] = hp["H1"]
    H["H2_west_round"]["p_holm"] = hp["H2"]
    for key in ("H1_west_all", "H2_west_round"):
        g = H[key]
        g["decision_deviation"] = bool(g["p_holm"] < 0.05 and g["U_ci95"][0] > 0.5)

    # secondary measures with Holm within each hypothesis
    secondary = {}
    for hk, rows, off in (("H1_west_all", h1_rows, 10), ("H2_west_round", h2_rows, 20)):
        sec = {s: group_stat(rows, s, off + i) for i, s in enumerate(SECONDARY)}
        ps = {s: sec[s]["p_one_sided_U"] for s in SECONDARY if sec[s].get("n")}
        adj = holm(ps)
        for s in SECONDARY:
            if s in adj:
                sec[s]["p_holm_within"] = adj[s]
        secondary[hk] = sec

    # ------------------------------------------------ subgroups (descriptive)
    sub = {}
    sub["west_nonround"] = group_stat(nonround_rows, "surprisal", 30)
    sub["west_square"] = group_stat([r for r in rows_w if r["medium"] == "square"], "surprisal", 31)
    sub["west_other_media"] = group_stat([r for r in rows_w if r["medium"] not in ("square", "round")],
                                         "surprisal", 32)
    for i, sr in enumerate(("Gulf", "Mesopotamia", "Iran")):
        sub[f"west_{sr}"] = group_stat([r for r in rows_w if r["subregion"] == sr], "surprisal", 33 + i)
    sub["west_round_gulf_mesopotamia"] = group_stat(
        [r for r in h2_rows if r["subregion"] in ("Gulf", "Mesopotamia")], "surprisal", 40)
    sub["west_round_iran"] = group_stat([r for r in h2_rows if r["subregion"] == "Iran"], "surprisal", 41)
    sub["central_asia"] = group_stat(rows_c, "surprisal", 42)
    sub["unprovenanced_round"] = group_stat(rows_u, "surprisal", 43)
    sub["west_seals_only"] = group_stat([r for r in rows_w if r["medium"] in C.SEAL_MEDIA],
                                        "surprisal", 44)
    sub["round_minus_nonround"] = diff_ci(H["H2_west_round"], sub["west_nonround"])

    # ------------------------------------------------ peripheral / regional groups
    periph, periph_rows = {}, {}
    for i, label in enumerate(PERIPHERAL):
        if label == "south_asian_round":
            gfaces = [f for f in sa if f["medium"] == "round"]
        else:
            gfaces = [f for f in sa if f["peripheral"] == label]
        gids = {f["record_id"] for f in gfaces}
        gpool = Pool(label, [f for f in sa if f["record_id"] not in gids], V)
        tests = C.dedupe_test_faces(gfaces)
        rows = score_tests(tests, gpool)
        periph_rows[label] = rows
        g = {"all_media": group_stat(rows, "surprisal", 100 + 10 * i),
             "seals_only": group_stat([r for r in rows if r["medium"] in C.SEAL_MEDIA],
                                      "surprisal", 101 + 10 * i)}
        for j, s in enumerate(SECONDARY):
            g[f"secondary_{s}"] = group_stat(rows, s, 102 + 10 * i + j, null=False)
        periph[label] = g
    comparisons = {}
    for label in QUALIFYING:
        comparisons[f"H1_minus_{label}"] = diff_ci(H["H1_west_all"], periph[label]["all_media"])
        comparisons[f"H1_seals_minus_{label}_seals"] = diff_ci(sub["west_seals_only"],
                                                                periph[label]["seals_only"])
    comparisons["H2_minus_south_asian_round"] = diff_ci(H["H2_west_round"],
                                                         periph["south_asian_round"]["all_media"])
    if H["H1_west_all"]["decision_deviation"]:
        beyond = all(comparisons[f"H1_minus_{l}"]["ci95"][0] > 0 for l in QUALIFYING)
    else:
        beyond = None
    round_specific = bool(H["H2_west_round"]["U_ci95"][0] > 0.5
                          and sub["round_minus_nonround"]["ci95"][0] > 0)

    # ------------------------------------------------ sensitivities
    sens = {}
    for code, kw in (("S2_trigram", {"kind": "kn3"}), ("S3_witten_bell", {"kind": "wb2"}),
                     ("S4_square_comparators", {"ladder": "square_only"}),
                     ("S5_any_object_comparators", {"ladder": "any_object"}),
                     ("S6_orientation_favourable", {"orientation": True})):
        rows = score_tests(west, pool, **kw)
        sens[code] = {"H1": group_stat(rows, "surprisal", 200),
                      "H2": group_stat([r for r in rows if r["medium"] == "round"], "surprisal", 201)}
    # S1 clean-only
    sa_clean = [f for f in sa if f["clean"]]
    cpool = Pool("south_asia_clean", sa_clean, V)
    rows = score_tests([f for f in west if f["clean"]], cpool)
    sens["S1_clean_only"] = {"H1": group_stat(rows, "surprisal", 210),
                             "H2": group_stat([r for r in rows if r["medium"] == "round"],
                                              "surprisal", 211),
                             "pool_faces": len(sa_clean)}
    # S7 witness swap
    swap = [r for r in rows_w if r["record_id"] != C.DUPLICATE_WITNESS["6000.1"]] + rows_dup
    sens["S7_dilmun_witness"] = {"H1": group_stat(swap, "surprisal", 220),
                                 "H2": group_stat([r for r in swap if r["medium"] == "round"],
                                                  "surprisal", 221)}
    # S8 leave one site out
    loso = {}
    for site in sorted({r["site"] for r in scorable(h1_rows)}):
        rr = [r for r in scorable(h1_rows) if r["site"] != site]
        loso[site] = float(np.mean([r["u_surprisal"] for r in rr]))
    sens["S8_leave_one_site_out_H1_U"] = {"min": min(loso.values()), "max": max(loso.values()),
                                          "by_site_removed": loso}
    loso2 = {}
    for site in sorted({r["site"] for r in scorable(h2_rows)}):
        rr = [r for r in scorable(h2_rows) if r["site"] != site]
        loso2[site] = float(np.mean([r["u_surprisal"] for r in rr]))
    sens["S8_leave_one_site_out_H2_U"] = {"min": min(loso2.values()), "max": max(loso2.values()),
                                          "by_site_removed": loso2}

    # ------------------------------------------------ descriptive positional measures
    desc = {}
    for name, rows in (("H1_west_all", h1_rows), ("H2_west_round", h2_rows),
                       ("west_nonround", nonround_rows), ("central_asia", rows_c)):
        desc[name] = {s: desc_rates(rows, s) for s in DESC}
        tr = [r for r in rows if r.get("scorable") and r.get("u_terminal_absent") is not None]
        desc[name]["terminal_740"] = {
            "n": len(tr), "test_count": int(sum(1 - r["terminal740_test"] for r in tr)),
            "test_rate": float(np.mean([1 - r["terminal740_test"] for r in tr])) if tr else None,
            "matched_comparator_rate": float(np.mean([1 - r["comp_mean_terminal_absent"] for r in tr]))
            if tr else None}
    # whole-text duplication
    dup_rows = [r for r in h1_rows if r.get("whole_text_in_pool") is not None]
    desc["whole_text_duplication"] = {
        "complete_west_texts": len(dup_rows),
        "with_identical_south_asian_code": int(sum(r["whole_text_in_pool"] for r in dup_rows)),
        "matched_comparator_duplication_rate": float(np.mean([r["comp_rate_duplicated"] for r in dup_rows]))
        if dup_rows else None}
    # 740-740 adjacency in South Asia (all faces and unique complete codes)
    adj_faces = sum(1 for f in sa if descriptive(f["text"])["adj740"])
    seen, adj_unique = set(), 0
    for f in sa:
        c = f["face"]["text_code_visual_ltr"]
        if f["full"] and c not in seen:
            seen.add(c)
            adj_unique += descriptive(f["text"])["adj740"] or 0
    west_adj = [f["record_id"] for f in west_all if descriptive(f["text"])["adj740"]]
    unprov_adj = [f["record_id"] for f in unprov if descriptive(f["text"])["adj740"]]
    desc["adjacent_740_740"] = {"south_asian_faces": adj_faces,
                                "south_asian_unique_complete_codes": adj_unique,
                                "west_asian_faces": west_adj, "unprovenanced_round_faces": unprov_adj}
    # initial 091 counts
    sa_unique_full = {}
    for f in sa:
        if f["full"]:
            sa_unique_full.setdefault(f["face"]["text_code_visual_ltr"], f)
    desc["initial_091"] = {
        "south_asian_unique_complete": sum(1 for f in sa_unique_full.values()
                                           if f["text"]["lines"][0][0] == "091"),
        "south_asian_unique_complete_total": len(sa_unique_full),
        "west_asian_start_known": [f["record_id"] for f in west_all
                                   if descriptive(f["text"])["initial_091"]],
        "west_asian_start_known_total": sum(1 for f in west_all
                                            if descriptive(f["text"])["initial_091"] is not None)}

    summary.update({"primary": H, "secondary": secondary, "subgroups": sub,
                    "peripheral": periph, "comparisons": comparisons,
                    "decisions": {"H1_deviation": H["H1_west_all"]["decision_deviation"],
                                  "H2_deviation": H["H2_west_round"]["decision_deviation"],
                                  "H1_beyond_regional_variation": beyond,
                                  "round_specificity": round_specific},
                    "sensitivity": sens, "descriptive": desc,
                    "unscorable_west": [r["record_id"] for r in rows_w if not r.get("scorable")],
                    "levels_west": dict(Counter(r.get("level") for r in rows_w if r.get("scorable")))})

    (OUT / "summary.json").write_text(json.dumps(clean(summary), indent=2) + "\n", encoding="utf-8")

    # ------------------------------------------------ per-object table (no sequences)
    cols = ["record_id", "family", "group", "subregion", "site", "region", "object_type", "medium",
            "length", "structure", "single_line", "clean", "events", "scorable", "level", "n_comp",
            "surprisal", "comp_mean_surprisal", "delta_surprisal", "u_surprisal",
            "unseen", "u_unseen", "rare", "u_rare", "unsupported", "u_unsupported",
            "terminal740_test", "u_terminal_absent", "comp_rate_has740", "has740",
            "initial_top3", "comp_rate_initial_top3", "initial_091", "adj740",
            "whole_text_in_pool", "comp_rate_duplicated"]
    all_rows = ([dict(r, analysis="primary") for r in rows_w + rows_dup + rows_c + rows_u])
    with (OUT / "objects.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols + ["note"])
        for r in all_rows:
            note = "duplicate witness of 3898.1; used only in S7" if r["record_id"] in C.DUPLICATE_WITNESS else ""
            w.writerow([("" if r.get(c) is None else (f"{r[c]:.6f}" if isinstance(r.get(c), float) else r.get(c)))
                        for c in cols] + [note])
    with (OUT / "groups.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "subset", "n", "U", "U_lo", "U_hi", "delta_bits", "delta_lo", "delta_hi",
                    "null_q025", "null_q975", "p_one_sided"])

        def put(name, subset, g):
            if not g.get("n"):
                w.writerow([name, subset, 0] + [""] * 9)
                return
            w.writerow([name, subset, g["n"], f"{g['U']:.4f}", f"{g['U_ci95'][0]:.4f}", f"{g['U_ci95'][1]:.4f}",
                        f"{g['delta']:.4f}", f"{g['delta_ci95'][0]:.4f}", f"{g['delta_ci95'][1]:.4f}",
                        f"{g['null_U_q025_q975'][0]:.4f}" if "null_U_q025_q975" in g else "",
                        f"{g['null_U_q025_q975'][1]:.4f}" if "null_U_q025_q975" in g else "",
                        f"{g['p_one_sided_U']:.5f}" if "p_one_sided_U" in g else ""])
        put("west_asia", "all (H1)", H["H1_west_all"])
        put("west_asia", "round (H2)", H["H2_west_round"])
        for k, g in sub.items():
            if k != "round_minus_nonround":
                put(k, "descriptive", g)
        for k, g in periph.items():
            put(k, "all media", g["all_media"])
            put(k, "seals only", g["seals_only"])

    # ------------------------------------------------ local raw outputs (sequences)
    with (RAW_OUT / "test_texts.jsonl").open("w", encoding="utf-8") as fh:
        for f in west_all + central + unprov:
            fh.write(json.dumps({"record_id": f["record_id"], "site": f["face"]["site"],
                                 "lines_reading_order": f["text"]["lines"],
                                 "start_known": f["text"]["start_known"],
                                 "end_known": f["text"]["end_known"],
                                 "code_visual_ltr": f["face"]["text_code_visual_ltr"]}) + "\n")
    with (RAW_OUT / "comparators.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows_w + rows_dup + rows_c + rows_u:
            if r.get("scorable"):
                fh.write(json.dumps({"record_id": r["record_id"], "comparator_ids": r["_comp_ids"],
                                     "comparator_surprisal": r["_comp_surprisal"]}) + "\n")
    with (RAW_OUT / "peripheral_rows.jsonl").open("w", encoding="utf-8") as fh:
        for label, rows in periph_rows.items():
            for r in rows:
                fh.write(json.dumps(clean(dict(r, peripheral_group=label))) + "\n")

    s = clean(summary)
    print(json.dumps({"primary": s["primary"], "decisions": s["decisions"]}, indent=1))


if __name__ == "__main__":
    main()
