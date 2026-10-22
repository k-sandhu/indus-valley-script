"""Blind template test of Parpola's rebus identifications (C-0014, prediction P1).

Each frozen template is an ordered pair of Indus signs (reading order) with Parpola's
Dravidian word for each sign. A template holds when the two words form an attested
two-member compound of the Madras Tamil Lexicon (shape C), or, for the gapped
templates, when compounds W1-X and X-W2 share a member (shape S). The same templates
are then scored with random replacement words matched on compounding productivity and
Sangam frequency, with the code and tables of REBUS-BASE-RATE-2026-10-21.

    python -I experiments/2026-10-22-rebus-blind-templates/code/run_templates.py TEMPLATES.json OUTDIR

The compound index, tolerances, candidate filter and matched pools are imported
unchanged from experiments/2026-10-21-rebus-base-rate/code (rebus.py, run_interlocks.py).
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / "2026-10-21-rebus-base-rate" / "code"
sys.path.insert(0, str(BASE))
import rebus  # noqa: E402
import run_interlocks as ri  # noqa: E402

PKG = HERE.parent
LOCAL = rebus.ROOT / "data" / "raw" / "2026-10-22-rebus-blind-templates"
SEED = 20261022
K_MAIN = 50
K_SENS = (25, 100)
EXACT_LIMIT = 2500      # enumerate every replacement pair when one form fills each slot
MC_DRAWS = 5000         # otherwise estimate the template's random rate from this many draws
JOINT_DRAWS = 10000     # random keys replacing every word at once
BOOT = 2000
TOLS = ("T0s", "T1s")


# ---------------------------------------------------------------- words

def resolve(word, entries_by_translit, entries_by_t0):
    """The one-member Tamil Lexicon headword that supplies a word's Sangam frequency."""
    e = entries_by_translit.get(word)
    if e is None:
        e = entries_by_t0.get(rebus.tl_norm(word, "T0s"))
    return e


def features(word, comp, tokens, index):
    e = resolve(word, *index)
    head = e["head"] if e else ""
    return {"word": word, "stem": "".join(comp.anchor(word)), "lexicon_headword": e["translit"] if e else None,
            "prod_first": comp.prod_first(word), "prod_last": comp.prod_last(word),
            "freq": ri.prefix_count(tokens, ri.tamil_prefix(head)) if head else 0}


# ---------------------------------------------------------------- template searches

class Searcher:
    def __init__(self, comp):
        self.comp = comp
        self.cache = {}

    def compound(self, w1, w2, tol, direction="both"):
        """Attested compounds that read the pair W1 W2: a compound anchored on W2 whose first
        member coincides with W1 (direction a), or one anchored on W1 whose second member
        coincides with W2 (direction b)."""
        key = ("C", w1, w2, tol, direction)
        if key not in self.cache:
            hits = []
            if direction in ("both", "a"):
                hits += ri.picture_hits([w1], self.comp.B(w2), 0, tol)
            if direction in ("both", "b"):
                hits += ri.picture_hits([w2], self.comp.A(w1), 1, tol)
            self.cache[key] = sorted(set(hits))
        return self.cache[key]

    def shared(self, w1, w2, tol):
        key = ("S", w1, w2, tol)
        if key not in self.cache:
            self.cache[key] = ri.i1(self.comp, w1, w2, tol)
        return self.cache[key]

    def _firsts(self, w2, tol):
        """Forms (with sandhi bases) of the first members of compounds anchored on W2."""
        key = ("F", w2, tol)
        if key not in self.cache:
            self.cache[key] = {rebus.tl_norm(b, tol) for e in self.comp.B(w2) for b in rebus.sandhi_bases(e["members"][0])}
        return self.cache[key]

    def _seconds(self, w1, tol):
        """Forms of the second members of compounds anchored on W1."""
        key = ("L", w1, tol)
        if key not in self.cache:
            self.cache[key] = {rebus.tl_norm(e["members"][1], tol) for e in self.comp.A(w1)}
        return self.cache[key]

    def compound_holds(self, w1, w2, tol, direction="both"):
        """Boolean form of compound(), from cached member sets; same result as picture_hits."""
        if direction in ("both", "a") and rebus.tl_norm(w1, tol) in self._firsts(w2, tol):
            return True
        if direction in ("both", "b") and rebus.tl_norm(w2, tol) in self._seconds(w1, tol):
            return True
        return False

    def holds(self, shape, f1, f2, tol, direction="both"):
        for a in f1:
            for b in f2:
                found = self.compound_holds(a, b, tol, direction) if shape == "C" else bool(self.shared(a, b, tol))
                if found:
                    return True
        return False


# ---------------------------------------------------------------- statistics

def summarise(h, r, rng, joint_counts=None):
    h, r = np.asarray(h, float), np.asarray(r, float)
    n, H, R = len(h), float(h.sum()), float(r.sum())
    ratio = H / R if R > 0 else None
    idx = rng.integers(0, n, (BOOT, n))
    rs, hs = r[idx].sum(1), h[idx].sum(1)
    ok = rs > 0
    boots = hs[ok] / rs[ok]
    ci = [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))] if ok.any() else [None, None]
    loo = [(H - h[i]) / (R - r[i]) if R - r[i] > 0 else None for i in range(n)]
    loo_vals = [x for x in loo if x is not None]
    out = {"templates": n, "parpola_hits": int(H), "parpola_rate": H / n if n else None,
           "parpola_rate_ci95_wilson": rebus.wilson(int(H), n), "expected_random_hits": R,
           "random_rate": R / n if n else None, "ratio": ratio, "ratio_ci95_bootstrap_over_templates": ci,
           "leave_one_out_min": min(loo_vals) if loo_vals else None,
           "leave_one_out_max": max(loo_vals) if loo_vals else None}
    if joint_counts is not None:
        jc = np.asarray(joint_counts)
        out["joint_draws"] = int(len(jc))
        out["p_random_key_at_least_parpola_hits"] = float((jc >= H).mean())
        out["random_key_hits_distribution"] = {str(v): int((jc == v).sum()) for v in sorted(set(jc.tolist()))}
    return out


def decide(s):
    ratio, lo = s["ratio"], s["ratio_ci95_bootstrap_over_templates"][0]
    if ratio is None:
        return {"verdict": "not computable"}
    passed = ratio < 2 and (s["leave_one_out_max"] is None or s["leave_one_out_max"] < 3)
    killed = ratio >= 3 and lo is not None and lo > 1.5 and (s["leave_one_out_min"] is not None and s["leave_one_out_min"] >= 2)
    return {"pass_rule": "ratio of hit rates below 2, and below 3 after removing any one template",
            "kill_rule": "ratio at least 3, bootstrap 2.5% bound above 1.5, and at least 2 after removing any one template",
            "passed": bool(passed), "killed": bool(killed),
            "verdict": "pass" if passed else ("kill" if killed else "neither")}


# ---------------------------------------------------------------- scoring one template set

def score(templates, idents, shape_of, srch, pools, tol, k, rng, joint=True, direction="both"):
    """Parpola hits, per-template random rates and (optionally) random-key draws."""
    real, rates, rows = [], [], []
    for t in templates:
        f1 = idents[t["first"]]["words"]
        f2 = idents[t["second"]]["words"]
        shape = shape_of(t)
        h = srch.holds(shape, f1, f2, tol, direction)
        p1 = [[c["word"] for c in pools["first"][w][k]] for w in f1]
        p2 = [[c["word"] for c in pools["second"][w][k]] for w in f2]
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
        rows.append({"id": t["id"], "first": t["first"], "second": t["second"], "shape": shape,
                     "parpola_holds": bool(h), "random_rate": r, "random_rate_method": method})
    counts = None
    if joint:
        counts = []
        slots = sorted({(t["first"], "first") for t in templates} | {(t["second"], "second") for t in templates})
        for _ in range(JOINT_DRAWS):
            key = {}
            for ident, slot in slots:
                key[(ident, slot)] = [pools[slot][w][k][rng.integers(len(pools[slot][w][k]))]["word"]
                                      for w in idents[ident]["words"]]
            counts.append(sum(srch.holds(shape_of(t), key[(t["first"], "first")], key[(t["second"], "second")], tol, direction)
                              for t in templates))
    return real, rates, rows, counts


# ---------------------------------------------------------------- main run

def run(spec, entries, dedr, tokens, sangam_hashes=None, synthetic=False):
    rng = np.random.default_rng(SEED)
    comp = rebus.Compounds(entries)
    dedr_t0 = {rebus.tl_norm(f, "T0s") for e in dedr if e["attested"] for f in e["tamil_forms"]}
    cands = ri.candidates(entries, comp, dedr_t0, tokens)
    one = [e for e in entries if len(e["members"]) == 1]
    by_tr, by_t0 = {}, {}
    for e in one:
        by_tr.setdefault(e["translit"], e)
        by_t0.setdefault(rebus.tl_norm(e["translit"], "T0s"), e)
    index = (by_tr, by_t0)
    idents = spec["identifications"]
    groups = {"primary": spec["templates"], "gapped": spec.get("gapped_templates", []),
              "published": spec.get("published_templates", [])}
    used = {"first": set(), "second": set()}
    for ts in groups.values():
        for t in ts:
            used["first"] |= set(idents[t["first"]]["words"])
            used["second"] |= set(idents[t["second"]]["words"])
    feats = {w: features(w, comp, tokens, index) for w in sorted(used["first"] | used["second"])}
    pools = {"first": {}, "second": {}}
    for slot, key in (("first", "prod_first"), ("second", "prod_last")):
        for w in sorted(used[slot]):
            pools[slot][w] = {kk: ri.nearest(cands, feats[w], key, kk) for kk in (K_MAIN,) + K_SENS}
    srch = Searcher(comp)

    out = {"schema_version": "1.0", "task": "rebus-blind-templates/templates", "synthetic": synthetic,
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "parameters": {"seed": SEED, "k_main": K_MAIN, "k_sensitivity": list(K_SENS), "exact_limit": EXACT_LIMIT,
                          "monte_carlo_draws": MC_DRAWS, "joint_draws": JOINT_DRAWS, "bootstrap": BOOT,
                          "tolerances": list(TOLS)},
           "lexicon": {"tamil_lexicon_entries": len(entries), "two_member_compounds": len(comp.c2),
                       "replacement_candidates": len(cands)},
           "word_features": feats,
           "replacement_pools": {slot: {w: [{k: v for k, v in c.items() if k in ("word", "prod_first", "prod_last", "freq", "distance")}
                                             for c in pools[slot][w][K_MAIN]] for w in pools[slot]} for slot in pools},
           "results": {}}
    if not synthetic:
        out["provenance"] = {
            "templates": {"path": spec["_path"], "sha256": rebus.sha256(spec["_path"])},
            "code": {p.relative_to(rebus.ROOT).as_posix(): rebus.sha256(p)
                     for p in [HERE / "run_templates.py", BASE / "rebus.py", BASE / "run_interlocks.py"]},
            "inputs": {p.relative_to(rebus.ROOT).as_posix(): rebus.sha256(p)
                       for p in [rebus.DER / "tamil-lex-entries.jsonl", rebus.DER / "dedr-entries.jsonl"]},
            "sangam_files": sangam_hashes, "sangam_tokens": len(tokens)}

    detail = {}
    shape_primary = lambda t: "C"  # noqa: E731
    shape_gapped = lambda t: "S"  # noqa: E731
    # primary: adjacent pairs, shape C, T0s, K50, with random keys
    plan = [("primary", groups["primary"], shape_primary, "T0s", K_MAIN, True, "both")]
    # sensitivities of the primary set
    plan += [("primary_T1s", groups["primary"], shape_primary, "T1s", K_MAIN, True, "both"),
             ("primary_K25", groups["primary"], shape_primary, "T0s", 25, False, "both"),
             ("primary_K100", groups["primary"], shape_primary, "T0s", 100, False, "both"),
             ("primary_picture_first_member_only", groups["primary"], shape_primary, "T0s", K_MAIN, False, "a")]
    exposed = set(spec.get("exposed_second_words", []))
    unexposed = [t for t in groups["primary"] if not (set(idents[t["second"]]["words"]) & exposed)
                 and not (set(idents[t["first"]]["words"]) & exposed)]
    plan += [("primary_without_words_searched_on_2026_10_21", unexposed, shape_primary, "T0s", K_MAIN, False, "both")]
    if groups["gapped"]:
        plan += [("gapped_shape_S", groups["gapped"], shape_gapped, "T0s", K_MAIN, True, "both")]
    if groups["published"]:
        plan += [("published_shape_C", groups["published"], shape_primary, "T0s", K_MAIN, False, "both")]
    for name, ts, shape_of, tol, k, joint, direction in plan:
        if not ts:
            out["results"][name] = {"templates": 0}
            continue
        real, rates, rows, counts = score(ts, idents, shape_of, srch, pools, tol, k, rng, joint, direction)
        s = summarise(real, rates, rng, counts)
        s.update({"tolerance": tol, "pool_size": k, "direction": direction, "per_template": rows})
        if name in ("primary", "gapped_shape_S", "published_shape_C") or name == "primary_T1s":
            s["decision"] = decide(s)
        out["results"][name] = s
        detail[name] = {r["id"]: _found(r, idents, srch, tol, direction) for r in rows if r["parpola_holds"]}
    out["decision"] = dict(out["results"]["primary"]["decision"],
                           statistic="ratio of the share of primary templates holding for Parpola's words to the "
                                     "expected share for matched random words (T0s, pools of 50)")
    return out, detail


def _found(row, idents, srch, tol, direction):
    """Every word pair of a holding template with the compounds or shared members that make it hold."""
    found = {}
    for a in idents[row["first"]]["words"]:
        for b in idents[row["second"]]["words"]:
            x = srch.compound(a, b, tol, direction) if row["shape"] == "C" else srch.shared(a, b, tol)
            if x:
                found[f"{a} | {b}"] = x
    return found


def main(spec_path, outdir):
    outdir = Path(outdir)
    target = outdir / "templates.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    spec["_path"] = str(Path(spec_path).resolve())
    entries = [json.loads(l) for l in (rebus.DER / "tamil-lex-entries.jsonl").open(encoding="utf-8")]
    dedr = rebus.load_dedr()
    tokens, hashes = ri.sangam_tokens()
    out, detail = run(spec, entries, dedr, tokens, hashes)
    spec_rel = Path(spec["_path"]).relative_to(rebus.ROOT).as_posix()
    out["provenance"]["templates"]["path"] = spec_rel
    local = LOCAL / outdir.name / "templates-detail.json"
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists():
        print("refusing to overwrite", local)
        return 1
    local.write_text(json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8")
    out["local_detail"] = {"path": local.relative_to(rebus.ROOT).as_posix(), "sha256": rebus.sha256(local)}
    outdir.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["decision"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
