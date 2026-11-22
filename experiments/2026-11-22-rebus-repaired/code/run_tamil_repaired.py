"""Experiment A: Repaired Tamil blind-template rerun and re-extracted Winslow sensitivity.

Reuses the exact frozen 38 blind pairs, 24 gapped pairs, and 12 published pairs from
experiments/2026-10-22-rebus-blind-templates/templates-v1.json, replacing the defective
Sangam prefix-count proxy and silent phonological fallback with exact written-form token
counting and strict lookup from experiments/2026-10-22-reading-eval-readiness/code/lexical_inputs.py.

Also evaluates the re-extracted Winslow table (data/raw/2026-10-24-lexical-extraction-extension/
run-v1/winslow-entries.jsonl), keeping raw Winslow guarded boundaries strictly separate from
Tamil Lexicon-assisted boundaries.

Run from repository root:
    python experiments/2026-11-22-rebus-repaired/code/run_tamil_repaired.py
"""

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE_CODE = ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "code"
READINESS_CODE = ROOT / "experiments" / "2026-10-22-reading-eval-readiness" / "code"
sys.path.insert(0, str(BASE_CODE))
sys.path.insert(0, str(READINESS_CODE))

import lexical_inputs as li  # noqa: E402
import rebus  # noqa: E402
import run_interlocks as ri  # noqa: E402

PKG = Path(__file__).resolve().parents[1]
TEMPLATES_PATH = ROOT / "experiments" / "2026-10-22-rebus-blind-templates" / "templates-v1.json"
POOLS_BASE_PATH = ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "pools-v1.json"
WINSLOW_EXT_PATH = ROOT / "data" / "raw" / "2026-10-24-lexical-extraction-extension" / "run-v1" / "winslow-entries.jsonl"
LOCAL_OUT = ROOT / "data" / "raw" / "2026-11-22-rebus-repaired" / "results-v1"
REPO_OUT = PKG / "results-v1"

SEED = 20261122
K_MAIN = 50
K_SENS = (25, 100)
EXACT_LIMIT = 2500
MC_DRAWS = 5000
JOINT_DRAWS = 10000
BOOT = 2000


# ---------------------------------------------------------------- exact Sangam counts & lookup

def load_exact_sangam_counts():
    files = sorted((rebus.SRC / "sangam").glob("pmuni*.html"))
    tokens = []
    hashes = {}
    for p in files:
        text = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
        tokens.extend(li.tamil_tokens(text))
        hashes[p.name] = rebus.sha256(p)
    return li.FormCounts(tokens), len(tokens), hashes


def resolve_exact_freq(word, lex, counts):
    """Exact written-form frequency via lexical_inputs.Lexicon with zero phonological fallback."""
    res = lex.resolve(word, counts)
    status = res["status"]
    form_counts = res.get("form_counts", {})
    if status in ("exact", "ambiguous"):
        freq = sum(form_counts.values())
    else:
        freq = None
    return {
        "status": status,
        "exact_candidate_count": len(res["candidates"]),
        "distinct_heads": sorted(form_counts.keys()),
        "form_counts": form_counts,
        "freq": freq,
    }


def build_candidates(entries, comp, dedr_t0, counts):
    """Native one-member nouns attested in DEDR (T0s), with exact written-form Sangam frequency."""
    seen = {}
    for e in entries:
        m = e["members"]
        if len(m) != 1 or e.get("star") or (e.get("pos") or "") != "n" or e.get("verb"):
            continue
        tr = e["translit"]
        if rebus.tl_norm(tr, "T0s") not in dedr_t0:
            continue
        st = comp.anchor(tr)
        if st in seen:
            continue
        head = e.get("head") or ""
        freq = counts.exact(head) if head.strip() else 0
        seen[st] = {
            "word": tr,
            "head": head,
            "stem": "".join(st),
            "prod_first": comp.prod_first(tr),
            "prod_last": comp.prod_last(tr),
            "freq": freq,
        }
    return list(seen.values())


def nearest_slot(cands, feat, prod_key, k, use_freq=True):
    pool = [c for c in cands if c["stem"] != feat["stem"]]
    lp = np.array([math.log1p(c[prod_key]) for c in pool], dtype=float)
    sp = lp.std() or 1.0
    dp = ((lp - math.log1p(feat[prod_key])) / sp) ** 2
    if use_freq and feat["freq"] is not None:
        lf = np.array([math.log1p(c["freq"]) for c in pool], dtype=float)
        sf = lf.std() or 1.0
        df = ((lf - math.log1p(feat["freq"])) / sf) ** 2
        d = np.sqrt(dp + df)
    else:
        d = np.sqrt(dp)
    order = sorted(range(len(pool)), key=lambda i: (d[i], pool[i]["word"]))
    return [dict(pool[i], distance=float(d[i])) for i in order[:k]]


def nearest_sign(cands, feat, k, use_freq=True):
    """Unified sign-level matching on both first- and second-member productivity (and optional freq)."""
    pool = [c for c in cands if c["stem"] != feat["stem"]]
    lp1 = np.array([math.log1p(c["prod_first"]) for c in pool], dtype=float)
    lp2 = np.array([math.log1p(c["prod_last"]) for c in pool], dtype=float)
    sp1 = lp1.std() or 1.0
    sp2 = lp2.std() or 1.0
    dist_sq = ((lp1 - math.log1p(feat["prod_first"])) / sp1) ** 2 + ((lp2 - math.log1p(feat["prod_last"])) / sp2) ** 2
    if use_freq and feat["freq"] is not None:
        lf = np.array([math.log1p(c["freq"]) for c in pool], dtype=float)
        sf = lf.std() or 1.0
        dist_sq = dist_sq + ((lf - math.log1p(feat["freq"])) / sf) ** 2
    d = np.sqrt(dist_sq)
    order = sorted(range(len(pool)), key=lambda i: (d[i], pool[i]["word"]))
    return [dict(pool[i], distance=float(d[i])) for i in order[:k]]


# ---------------------------------------------------------------- fast cached searcher

class Searcher:
    def __init__(self, comp):
        self.comp = comp
        self.cache = {}

    def _firsts(self, w2, tol):
        key = ("F", w2, tol)
        if key not in self.cache:
            self.cache[key] = {rebus.tl_norm(b, tol) for e in self.comp.B(w2) for b in rebus.sandhi_bases(e["members"][0])}
        return self.cache[key]

    def _seconds(self, w1, tol):
        key = ("L", w1, tol)
        if key not in self.cache:
            self.cache[key] = {rebus.tl_norm(e["members"][1], tol) for e in self.comp.A(w1)}
        return self.cache[key]

    def compound_holds(self, w1, w2, tol, direction="both"):
        if direction in ("both", "a") and rebus.tl_norm(w1, tol) in self._firsts(w2, tol):
            return True
        if direction in ("both", "b") and rebus.tl_norm(w2, tol) in self._seconds(w1, tol):
            return True
        return False

    def shared_holds(self, w1, w2, tol):
        key = ("SB", w1, w2, tol)
        if key not in self.cache:
            a_secs = self._seconds(w1, tol)
            b_firsts = self._firsts(w2, tol)
            if not a_secs or not b_firsts:
                self.cache[key] = False
            else:
                excl = {rebus.tl_norm(b, tol) for w in (w1, w2) for b in rebus.sandhi_bases(w)}
                self.cache[key] = bool((a_secs & b_firsts) - excl)
        return self.cache[key]

    def compound(self, w1, w2, tol, direction="both"):
        hits = []
        if direction in ("both", "a"):
            hits += ri.picture_hits([w1], self.comp.B(w2), 0, tol)
        if direction in ("both", "b"):
            hits += ri.picture_hits([w2], self.comp.A(w1), 1, tol)
        return sorted(set(hits))

    def shared(self, w1, w2, tol):
        return ri.i1(self.comp, w1, w2, tol)

    def holds(self, shape, f1, f2, tol, direction="both"):
        for a in f1:
            for b in f2:
                ok = self.compound_holds(a, b, tol, direction) if shape == "C" else self.shared_holds(a, b, tol)
                if ok:
                    return True
        return False


# ---------------------------------------------------------------- scoring & summary

def summarise(h, r, rng, joint_sign_counts=None, joint_slot_counts=None):
    h_arr, r_arr = np.asarray(h, float), np.asarray(r, float)
    n, H, R = len(h_arr), float(h_arr.sum()), float(r_arr.sum())
    ratio = H / R if R > 0 else None
    idx = rng.integers(0, n, (BOOT, n))
    rs, hs = r_arr[idx].sum(1), h_arr[idx].sum(1)
    ok = rs > 0
    boots = hs[ok] / rs[ok]
    ci = [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))] if ok.any() else [None, None]
    loo = [(H - h_arr[i]) / (R - r_arr[i]) if R - r_arr[i] > 0 else None for i in range(n)]
    loo_vals = [x for x in loo if x is not None]
    out = {
        "templates": n,
        "parpola_hits": int(H),
        "parpola_rate": H / n if n else None,
        "parpola_rate_ci95_wilson": rebus.wilson(int(H), n),
        "expected_random_hits_marginal": R,
        "random_rate_marginal": R / n if n else None,
        "ratio_marginal": ratio,
        "ratio_ci95_bootstrap_over_templates": ci,
        "leave_one_out_min": min(loo_vals) if loo_vals else None,
        "leave_one_out_max": max(loo_vals) if loo_vals else None,
    }
    if joint_sign_counts is not None:
        jc = np.asarray(joint_sign_counts, dtype=float)
        jm = float(jc.mean())
        out["joint_sign_level"] = {
            "draws": int(len(jc)),
            "expected_random_hits": jm,
            "random_rate": jm / n if n else None,
            "ratio": (H / jm) if jm > 0 else None,
            "sd_hits": float(jc.std(ddof=0)),
            "p_random_key_at_least_parpola_hits": float((jc >= H).mean()),
            "hits_distribution": {str(int(v)): int((jc == v).sum()) for v in sorted(set(jc.tolist()))},
        }
    if joint_slot_counts is not None:
        jc = np.asarray(joint_slot_counts, dtype=float)
        jm = float(jc.mean())
        out["joint_slot_level"] = {
            "draws": int(len(jc)),
            "expected_random_hits": jm,
            "random_rate": jm / n if n else None,
            "ratio": (H / jm) if jm > 0 else None,
            "sd_hits": float(jc.std(ddof=0)),
            "p_random_key_at_least_parpola_hits": float((jc >= H).mean()),
            "hits_distribution": {str(int(v)): int((jc == v).sum()) for v in sorted(set(jc.tolist()))},
        }
    return out


def score_set(templates, idents, shape, srch, slot_pools, sign_pools, tol, k, rng,
              run_joint=True, direction="both", marginal_mode="sign"):
    """Score a template set with marginal rates and optional sign-level + slot-level joint draws."""
    real, rates, rows = [], [], []
    for t in templates:
        f1 = idents[t["first"]]["words"]
        f2 = idents[t["second"]]["words"]
        h = srch.holds(shape, f1, f2, tol, direction)
        if marginal_mode == "sign":
            p1 = [[c["word"] for c in sign_pools[w][k]] for w in f1]
            p2 = [[c["word"] for c in sign_pools[w][k]] for w in f2]
        else:
            p1 = [[c["word"] for c in slot_pools["first"][w][k]] for w in f1]
            p2 = [[c["word"] for c in slot_pools["second"][w][k]] for w in f2]
        if len(p1) == 1 and len(p2) == 1 and len(p1[0]) * len(p2[0]) <= EXACT_LIMIT:
            hits = sum(srch.holds(shape, [a], [b], tol, direction) for a in p1[0] for b in p2[0])
            r, method = hits / (len(p1[0]) * len(p2[0])), "exact"
        else:
            hits = 0
            for _ in range(MC_DRAWS):
                a = [p[rng.integers(len(p))] for p in p1]
                b = [p[rng.integers(len(p))] for p in p2]
                hits += srch.holds(shape, a, b, tol, direction)
            r, method = hits / MC_DRAWS, f"monte-carlo-{MC_DRAWS}"
        real.append(int(h))
        rates.append(r)
        rows.append({
            "id": t["id"], "first": t["first"], "second": t["second"], "shape": shape,
            "parpola_holds": bool(h), "random_rate": r, "random_rate_method": method,
        })

    joint_sign = None
    joint_slot = None
    if run_joint:
        signs = sorted({t["first"] for t in templates} | {t["second"] for t in templates})
        sign_word_pools = {s: [[c["word"] for c in sign_pools[w][k]] for w in idents[s]["words"]] for s in signs}
        joint_sign = []
        for _ in range(JOINT_DRAWS):
            key = {s: [p[rng.integers(len(p))] for p in sign_word_pools[s]] for s in signs}
            joint_sign.append(sum(srch.holds(shape, key[t["first"]], key[t["second"]], tol, direction) for t in templates))

        slots = sorted({(t["first"], "first") for t in templates} | {(t["second"], "second") for t in templates})
        slot_word_pools = {(s, sl): [[c["word"] for c in slot_pools[sl][w][k]] for w in idents[s]["words"]] for s, sl in slots}
        joint_slot = []
        for _ in range(JOINT_DRAWS):
            key = {(s, sl): [p[rng.integers(len(p))] for p in slot_word_pools[(s, sl)]] for s, sl in slots}
            joint_slot.append(sum(srch.holds(shape, key[(t["first"], "first")], key[(t["second"], "second")], tol, direction) for t in templates))

    return real, rates, rows, joint_sign, joint_slot


def found_detail(rows, idents, srch, tol, direction="both"):
    detail = {}
    for r in rows:
        if not r["parpola_holds"]:
            continue
        found = {}
        for a in idents[r["first"]]["words"]:
            for b in idents[r["second"]]["words"]:
                x = srch.compound(a, b, tol, direction) if r["shape"] == "C" else srch.shared(a, b, tol)
                if x:
                    found[f"{a} | {b}"] = x
        detail[r["id"]] = found
    return detail


# ---------------------------------------------------------------- base-rate I1 & network check

def run_i1_and_network(entries, comp, dedr, cands, counts, pools_base, lex, rng, use_freq=True):
    """Recompute Parpola's I1 (veḷ) and 5-link network under exact written-form counts."""
    W1, W2, W3 = ri.W1, ri.W2, ri.W3
    real_feats = {}
    for w in (W1, W2, W3):
        info = resolve_exact_freq(w, lex, counts)
        real_feats[w] = {
            "word": w, "stem": "".join(comp.anchor(w)),
            "prod_first": comp.prod_first(w), "prod_last": comp.prod_last(w),
            "freq": info["freq"], "lookup_status": info["status"],
        }
    pools_w = {
        W1: nearest_slot(cands, real_feats[W1], "prod_first", K_MAIN, use_freq=use_freq),
        W2: nearest_slot(cands, real_feats[W2], "prod_last", K_MAIN, use_freq=use_freq),
        W3: nearest_slot(cands, real_feats[W3], "prod_last", K_MAIN, use_freq=use_freq),
    }
    pic_concepts = []
    for c in pools_base["picture"]:
        ws = ri.picture_words(dedr, c["key"])
        if ws:
            pic_concepts.append({"id": c["id"], "key": c["key"], "words": ws})
    real_pics = {k: sorted(set(ri.picture_words(dedr, key)) | set(ri.PARPOLA_PICTURE_WORDS[k]))
                 for k, key in ri.PICTURE_KEYS.items()}

    A, B = comp.A(W1), comp.B(W2)
    n4, found4 = ri.numeral_count(comp, W2)
    out = {
        "anchor_features": real_feats,
        "A_size": len(A), "B_size": len(B), "B_katavul_size": len(comp.B(W3)),
        "I4_numerals_with_compound": n4,
        "tolerances": {},
    }
    for tol in ("T0s", "T1s"):
        sh = ri.i1(comp, W1, W2, tol)
        i2_hits = ri.picture_hits(real_pics["I2"], B, 0, tol)
        i3_hits = ri.picture_hits(real_pics["I3"], A, 1, tol)
        i5_hits = ri.picture_hits(real_pics["I5"], comp.B(W3), 0, tol)
        held = {"I1": bool(sh), "I2": bool(i2_hits), "I3": bool(i3_hits), "I4": n4 >= 1, "I5": bool(i5_hits)}
        required = [k for k, v in held.items() if v]

        p1, p2, p3 = pools_w[W1], pools_w[W2], pools_w[W3]
        M = np.zeros((len(p1), len(p2)), dtype=bool)
        for i, a in enumerate(p1):
            Aa = comp.A(a["word"])
            for j, b in enumerate(p2):
                M[i, j] = bool(ri.i1(comp, a["word"], b["word"], tol, Aa, None))
        boots = []
        for _ in range(BOOT):
            ii = rng.integers(0, M.shape[0], M.shape[0])
            jj = rng.integers(0, M.shape[1], M.shape[1])
            boots.append(M[np.ix_(ii, jj)].mean())

        all_hits = 0
        cache_A, cache_B = {}, {}
        for _ in range(JOINT_DRAWS):
            a = p1[rng.integers(len(p1))]["word"]
            b = p2[rng.integers(len(p2))]["word"]
            c = p3[rng.integers(len(p3))]["word"]
            pics = rng.choice(len(pic_concepts), 3, replace=False)
            Aa = cache_A.setdefault(a, comp.A(a))
            Bb = cache_B.setdefault(b, comp.B(b))
            Bc = cache_B.setdefault(c, comp.B(c))
            got = {
                "I1": bool(ri.i1(comp, a, b, tol, Aa, Bb)),
                "I2": bool(ri.picture_hits(pic_concepts[pics[0]]["words"], Bb, 0, tol)),
                "I3": bool(ri.picture_hits(pic_concepts[pics[1]]["words"], Aa, 1, tol)),
                "I4": ri.numeral_count(comp, b)[0] >= 1,
                "I5": bool(ri.picture_hits(pic_concepts[pics[2]]["words"], Bc, 0, tol)),
            }
            if required and all(got[k] for k in required):
                all_hits += 1

        out["tolerances"][tol] = {
            "real_holds": held,
            "required": required,
            "I1_shared_keys": sorted(sh.keys()),
            "I1_null_rate": float(M.mean()),
            "I1_null_pairs_with_shared": int(M.sum()),
            "I1_null_ci95_bootstrap": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
            "network_draws": JOINT_DRAWS,
            "network_hits": int(all_hits),
            "network_rate": all_hits / JOINT_DRAWS,
            "network_ci95_wilson": rebus.wilson(int(all_hits), JOINT_DRAWS),
        }
    return out


# ---------------------------------------------------------------- full suite on a dictionary table

def evaluate_lexicon(label, entries, spec, dedr, dedr_t0, counts, pools_base, namespace,
                     aru_direct_sensitivity=False):
    rng = np.random.default_rng(SEED)
    comp = rebus.Compounds(entries)
    lex = li.Lexicon(entries, namespace=namespace)
    cands = build_candidates(entries, comp, dedr_t0, counts)
    idents = spec["identifications"]

    groups = {
        "primary": spec["templates"],
        "gapped": spec["gapped_templates"],
        "published": spec["published_templates"],
    }
    used_words = sorted({w for d in idents.values() for w in d["words"]})

    feats = {}
    for w in used_words:
        info = resolve_exact_freq(w, lex, counts)
        feats[w] = {
            "word": w,
            "stem": "".join(comp.anchor(w)),
            "prod_first": comp.prod_first(w),
            "prod_last": comp.prod_last(w),
            "freq": info["freq"],
            "lookup_status": info["status"],
            "exact_candidate_count": info["exact_candidate_count"],
            "distinct_heads": info["distinct_heads"],
        }

    srch = Searcher(comp)
    exposed = set(spec.get("exposed_second_words", []))
    unexposed = [t for t in groups["primary"]
                 if not (set(idents[t["second"]]["words"]) & exposed)
                 and not (set(idents[t["first"]]["words"]) & exposed)]
    no_bullhead = [t for t in groups["primary"] if t["first"] != "BULLHEAD" and t["second"] != "BULLHEAD"]

    modes = [
        ("exact_freq_prod", True, feats),
        ("prod_only", False, feats),
    ]
    if aru_direct_sensitivity:
        feats_aru = {w: dict(f) for w, f in feats.items()}
        if feats_aru["aṟu"]["freq"] is None:
            feats_aru["aṟu"]["freq"] = counts.exact("அறு")
            feats_aru["aṟu"]["note"] = "direct exact Sangam token count of அறு; still unresolved in one-member Lexicon"
        modes.append(("exact_freq_prod_aru_direct", True, feats_aru))

    out = {
        "label": label,
        "lexicon_summary": {
            "entries": len(entries),
            "two_member_compounds": len(comp.c2),
            "replacement_candidates": len(cands),
        },
        "word_features": feats,
        "modes": {},
        "base_rate_check": {},
    }
    detail = {}

    for mode_name, use_freq, mode_feats in modes:
        slot_pools = {"first": {}, "second": {}}
        sign_pools = {}
        for w in used_words:
            slot_pools["first"][w] = {kk: nearest_slot(cands, mode_feats[w], "prod_first", kk, use_freq=use_freq)
                                      for kk in (K_MAIN,) + K_SENS}
            slot_pools["second"][w] = {kk: nearest_slot(cands, mode_feats[w], "prod_last", kk, use_freq=use_freq)
                                       for kk in (K_MAIN,) + K_SENS}
            sign_pools[w] = {kk: nearest_sign(cands, mode_feats[w], kk, use_freq=use_freq)
                             for kk in (K_MAIN,) + K_SENS}

        plan = [
            ("primary_sign_marginal", groups["primary"], "C", "T0s", K_MAIN, True, "both", "sign"),
            ("primary_slot_marginal", groups["primary"], "C", "T0s", K_MAIN, False, "both", "slot"),
            ("primary_T1s", groups["primary"], "C", "T1s", K_MAIN, True, "both", "sign"),
            ("primary_K25", groups["primary"], "C", "T0s", 25, True, "both", "sign"),
            ("primary_K100", groups["primary"], "C", "T0s", 100, True, "both", "sign"),
            ("primary_direction_a", groups["primary"], "C", "T0s", K_MAIN, True, "a", "sign"),
            ("primary_unexposed_26", unexposed, "C", "T0s", K_MAIN, True, "both", "sign"),
            ("primary_no_bullhead_26", no_bullhead, "C", "T0s", K_MAIN, True, "both", "sign"),
            ("gapped_shape_S", groups["gapped"], "S", "T0s", K_MAIN, True, "both", "sign"),
            ("published_shape_C", groups["published"], "C", "T0s", K_MAIN, True, "both", "sign"),
        ]
        mode_res = {}
        for name, ts, shape, tol, k, run_joint, direction, marg_mode in plan:
            real, rates, rows, j_sign, j_slot = score_set(
                ts, idents, shape, srch, slot_pools, sign_pools, tol, k, rng,
                run_joint=run_joint, direction=direction, marginal_mode=marg_mode,
            )
            s = summarise(real, rates, rng, j_sign, j_slot)
            s.update({"tolerance": tol, "pool_size": k, "direction": direction, "marginal_pool_type": marg_mode})
            if name in ("primary_sign_marginal", "published_shape_C"):
                s["per_template"] = rows
            mode_res[name] = s
            if mode_name == "exact_freq_prod" and name in ("primary_sign_marginal", "primary_T1s", "published_shape_C", "gapped_shape_S"):
                detail[name] = found_detail(rows, idents, srch, tol, direction)
        out["modes"][mode_name] = mode_res

    out["base_rate_check"]["exact_freq_prod"] = run_i1_and_network(
        entries, comp, dedr, cands, counts, pools_base, lex, rng, use_freq=True
    )
    out["base_rate_check"]["prod_only"] = run_i1_and_network(
        entries, comp, dedr, cands, counts, pools_base, lex, rng, use_freq=False
    )
    return out, detail


def main():
    REPO_OUT.mkdir(parents=True, exist_ok=True)
    LOCAL_OUT.mkdir(parents=True, exist_ok=True)

    spec = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))
    pools_base = json.loads(POOLS_BASE_PATH.read_text(encoding="utf-8"))
    dedr = rebus.load_dedr()
    dedr_t0 = {rebus.tl_norm(f, "T0s") for e in dedr if e["attested"] for f in e["tamil_forms"]}
    counts, total_tokens, sangam_hashes = load_exact_sangam_counts()

    print(f"Exact Sangam tokens: {total_tokens}, ka={counts.exact('கா')}, aa={counts.exact('ஆ')}, aru={counts.exact('அறு')}")

    # ---- A1: Repaired Madras Tamil Lexicon
    tl_path = rebus.DER / "tamil-lex-entries.jsonl"
    tl_entries = [json.loads(line) for line in tl_path.open(encoding="utf-8")]
    tl_out, tl_detail = evaluate_lexicon(
        "Madras Tamil Lexicon (repaired exact written-form counts, no phonological fallback)",
        tl_entries, spec, dedr, dedr_t0, counts, pools_base, namespace="tamil-lexicon",
        aru_direct_sensitivity=True,
    )
    tl_out["schema_version"] = "1.0"
    tl_out["task"] = "rebus-repaired/tamil-lexicon"
    tl_out["created_utc"] = datetime.now(timezone.utc).isoformat()
    tl_out["parameters"] = {
        "seed": SEED, "k_main": K_MAIN, "k_sensitivity": list(K_SENS),
        "exact_limit": EXACT_LIMIT, "mc_draws": MC_DRAWS, "joint_draws": JOINT_DRAWS, "bootstrap": BOOT,
    }
    tl_out["sangam_summary"] = {
        "total_tokens": total_tokens,
        "exact_ka": counts.exact("கா"),
        "exact_aa": counts.exact("ஆ"),
        "exact_aru_written": counts.exact("அறு"),
        "exact_arru_written": counts.exact("அற்று"),
        "files": sangam_hashes,
    }
    tl_out["provenance"] = {
        "templates": {"path": TEMPLATES_PATH.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(TEMPLATES_PATH)},
        "tamil_lexicon": {"path": tl_path.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(tl_path)},
        "dedr": {"path": (rebus.DER / "dedr-entries.jsonl").relative_to(ROOT).as_posix(),
                 "sha256": rebus.sha256(rebus.DER / "dedr-entries.jsonl")},
        "lexical_inputs_code": {"path": (READINESS_CODE / "lexical_inputs.py").relative_to(ROOT).as_posix(),
                                "sha256": rebus.sha256(READINESS_CODE / "lexical_inputs.py")},
    }
    tl_detail_path = LOCAL_OUT / "tamil-repaired-detail.json"
    tl_detail_path.write_text(json.dumps(tl_detail, ensure_ascii=False, indent=1), encoding="utf-8")
    tl_out["local_detail"] = {"path": tl_detail_path.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(tl_detail_path)}
    (REPO_OUT / "tamil_repaired.json").write_text(json.dumps(tl_out, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- A2: Re-extracted Winslow (raw guarded vs Lexicon-assisted)
    w_raw_records = [json.loads(line) for line in WINSLOW_EXT_PATH.open(encoding="utf-8")]
    w_guarded_entries = [dict(r, members=r["winslow_guarded_members"]) for r in w_raw_records]
    w_assisted_entries = [dict(r, members=r["members"]) for r in w_raw_records]

    w_raw_out, w_raw_detail = evaluate_lexicon(
        "Winslow 1862 re-extracted — raw guarded boundaries only (independent of Tamil Lexicon)",
        w_guarded_entries, spec, dedr, dedr_t0, counts, pools_base, namespace="winslow-raw-guarded",
    )
    w_ass_out, w_ass_detail = evaluate_lexicon(
        "Winslow 1862 re-extracted — Tamil Lexicon-assisted boundaries (cross-dictionary dependent sensitivity)",
        w_assisted_entries, spec, dedr, dedr_t0, counts, pools_base, namespace="winslow-lexicon-assisted",
    )
    w_combined = {
        "schema_version": "1.0",
        "task": "rebus-repaired/winslow-reextracted",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "independence_note": "raw_guarded uses strictly Winslow-internal parsing after the grammatical guard; lexicon_assisted incorporates Tamil Lexicon boundaries and must not be treated as independent cross-dictionary agreement.",
        "provenance": {
            "templates": {"path": TEMPLATES_PATH.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(TEMPLATES_PATH)},
            "winslow_reextracted": {"path": WINSLOW_EXT_PATH.relative_to(ROOT).as_posix(),
                                    "sha256": rebus.sha256(WINSLOW_EXT_PATH)},
        },
        "raw_guarded": w_raw_out,
        "lexicon_assisted": w_ass_out,
    }
    w_detail_path = LOCAL_OUT / "winslow-reextracted-detail.json"
    w_detail_path.write_text(json.dumps({"raw_guarded": w_raw_detail, "lexicon_assisted": w_ass_detail},
                                        ensure_ascii=False, indent=1), encoding="utf-8")
    w_combined["local_detail"] = {"path": w_detail_path.relative_to(ROOT).as_posix(), "sha256": rebus.sha256(w_detail_path)}
    (REPO_OUT / "winslow_reextracted.json").write_text(json.dumps(w_combined, ensure_ascii=False, indent=1), encoding="utf-8")

    # Print concise summary
    print("\n=== TAMIL LEXICON REPAIRED ===")
    for m in ("exact_freq_prod", "exact_freq_prod_aru_direct", "prod_only"):
        p = tl_out["modes"][m]["primary_sign_marginal"]
        ps = tl_out["modes"][m]["primary_slot_marginal"]
        pub = tl_out["modes"][m]["published_shape_C"]
        print(f"  [{m}] blind={p['parpola_hits']}/38 | sign-joint exp={p['joint_sign_level']['expected_random_hits']:.2f} "
              f"ratio={p['joint_sign_level']['ratio']:.2f} p={p['joint_sign_level']['p_random_key_at_least_parpola_hits']:.4f} | "
              f"slot-joint exp={p['joint_slot_level']['expected_random_hits']:.2f} ratio={p['joint_slot_level']['ratio']:.2f} "
              f"p={p['joint_slot_level']['p_random_key_at_least_parpola_hits']:.4f} | "
              f"slot-marg exp={ps['expected_random_hits_marginal']:.2f} ratio={ps['ratio_marginal']:.2f} | "
              f"pub={pub['parpola_hits']}/12 ratio={pub['joint_sign_level']['ratio']:.2f}")
    br_e = tl_out["base_rate_check"]["exact_freq_prod"]["tolerances"]["T0s"]
    br_p = tl_out["base_rate_check"]["prod_only"]["tolerances"]["T0s"]
    print(f"  [Base-rate T0s] exact_freq_prod: I1={br_e['I1_null_rate']:.3f}, net={br_e['network_rate']:.4f} | "
          f"prod_only: I1={br_p['I1_null_rate']:.3f}, net={br_p['network_rate']:.4f}")

    print("\n=== WINSLOW RE-EXTRACTED ===")
    for layer_name, layer in (("raw_guarded", w_raw_out), ("lexicon_assisted", w_ass_out)):
        print(f"  Layer: {layer_name} (2-mem compounds={layer['lexicon_summary']['two_member_compounds']})")
        for m in ("exact_freq_prod", "prod_only"):
            p = layer["modes"][m]["primary_sign_marginal"]
            pub = layer["modes"][m]["published_shape_C"]
            print(f"    [{m}] blind={p['parpola_hits']}/38 exp={p['joint_sign_level']['expected_random_hits']:.2f} "
                  f"ratio={p['joint_sign_level']['ratio']:.2f} p={p['joint_sign_level']['p_random_key_at_least_parpola_hits']:.4f} | "
                  f"pub={pub['parpola_hits']}/12 exp={pub['joint_sign_level']['expected_random_hits']:.2f}")
        br = layer["base_rate_check"]["exact_freq_prod"]["tolerances"]["T0s"]
        print(f"    [Base-rate T0s] required={br['required']}, I1={br['I1_null_rate']:.3f}, net={br['network_rate']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
