"""Measurement 2: Parpola's interlock searches rerun with random replacement words.

The veḷ search (I1): collect the compounds W1-X (W1 = muruku, the god's name) and
X-W2 (W2 = mīṉ, the head noun) in the Tamil Lexicon and look for a shared member X.
We then replace W1 and W2 by random native nouns matched on compounding
productivity and Sangam frequency and record how often a shared member appears.

The other searches use the same machinery:
  I2  a word for the banyan has a homophone Y with Y-mīṉ attested      (vaṭa-mīṉ)
  I3  a word for the squirrel is the second member of a muruku compound (Muruka-p-piḷḷai)
  I4  the numerals three, six and seven form attested compounds with mīṉ (aṟu-mīṉ, eḻu-mīṉ)
  I5  a word for the spindle has a homophone Y with Y-kaṭavuḷ attested (katir-k-kaṭavuḷ)

    python -I experiments/2026-10-21-rebus-base-rate/code/run_interlocks.py OUTDIR [--synthetic]
"""

import bisect
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebus  # noqa: E402

PKG = rebus.ROOT / "experiments" / "2026-10-21-rebus-base-rate"
SEED = 20261021
K_MAIN = 50
K_SENS = (25, 100)
DRAWS = 10000
BOOT = 2000
TOLS = ("T0s", "T1s")
W1, W2, W3 = "muruku", "mīṉ", "kaṭavuḷ"
PICTURE_KEYS = {"I2": "banyan", "I3": "squirrel", "I5": "spindle"}
PARPOLA_PICTURE_WORDS = {"I2": ["vaṭam"], "I3": ["piḷḷai", "aṇil"], "I5": ["katir"]}   # named in Parpola (2010)
NUMERALS = {"three": ["mū", "mūṉṟu", "mu"], "six": ["āṟu", "aṟu"], "seven": ["ēḻu", "eḻu"]}
MURUKAN_RE = re.compile(r"Skanda|Muruk|Kumara|Subrahma|Subramaṇ|Kārttikēya|war-god|god of war", re.I)
ASTRAL_FISH_RE = re.compile(r"\bstar|planet|constellation|asterism|nakṣatra|Venus|Jupiter|Mars\b|Mercury|Saturn|"
                            r"Pleiades|comet|\bfish|Ursa|Arcturus|Canopus|Sirius|Orion|Alcor|pole-star|lunar mansion", re.I)
TAMIL_SIGNS = set(chr(c) for c in range(0x0BBE, 0x0BCE)) | {"ௗ"}


# ---------------------------------------------------------------- inputs

def sangam_tokens():
    toks = []
    files = sorted((rebus.SRC / "sangam").glob("pmuni*.html"))
    for p in files:
        text = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
        toks.extend(re.findall(r"[஀-௿]+", text))
    toks.sort()
    return toks, {p.name: rebus.sha256(p) for p in files}


def tamil_prefix(head):
    h = re.sub(r"-.*$", "", head)
    while h and h[-1] in TAMIL_SIGNS:
        h = h[:-1]
    return h


def prefix_count(sorted_tokens, prefix):
    if not prefix:
        return 0
    lo = bisect.bisect_left(sorted_tokens, prefix)
    hi = bisect.bisect_left(sorted_tokens, prefix + "\U0010ffff")
    return hi - lo


# ---------------------------------------------------------------- searches

def i1(comp, w1, w2, tol, A=None, B=None):
    A = comp.A(w1) if A is None else A
    B = comp.B(w2) if B is None else B
    excl = {rebus.tl_norm(b, tol) for w in (w1, w2) for b in rebus.sandhi_bases(w)}
    return rebus.shared_members(A, B, tol, excl)


def picture_hits(words, compounds, position, tol):
    """Compounds whose member at `position` (0 first, 1 second) is a homophone of a picture word."""
    targets = {rebus.tl_norm(w, tol) for w in words}
    hits = []
    for e in compounds:
        m = e["members"][position]
        bases = rebus.sandhi_bases(m) if position == 0 else {m}
        if targets & {rebus.tl_norm(b, tol) for b in bases}:
            hits.append(e["translit"])
    return hits


def numeral_count(comp, w2):
    B = comp.B(w2)
    stems = {e_k: {rebus.tl_norm(b, "T1s") for b in rebus.sandhi_bases(e["members"][0])} for e_k, e in enumerate(B)}
    found = {}
    for name, forms in NUMERALS.items():
        ns = {rebus.tl_norm(f, "T1s") for f in forms}
        found[name] = sorted(B[k]["translit"] for k, st in stems.items() if st & ns)
    return sum(1 for v in found.values() if v), found


# ---------------------------------------------------------------- pools of replacement words

def candidates(entries, comp, dedr_t0, tokens):
    seen = {}
    for e in entries:
        if len(e["members"]) != 1 or e["star"] or (e["pos"] or "") != "n" or e["verb"]:
            continue
        t0 = rebus.tl_norm(e["translit"], "T0s")
        if t0 not in dedr_t0:
            continue
        st = comp.anchor(e["translit"])
        if st in seen:
            continue
        seen[st] = {"word": e["translit"], "head": e["head"], "stem": "".join(st),
                    "prod_first": comp.prod_first(e["translit"]), "prod_last": comp.prod_last(e["translit"]),
                    "freq": prefix_count(tokens, tamil_prefix(e["head"]))}
    return list(seen.values())


def nearest(cands, real, prod_key, k):
    pool = [c for c in cands if c["stem"] != real["stem"]]
    lp = np.array([math.log1p(c[prod_key]) for c in pool])
    lf = np.array([math.log1p(c["freq"]) for c in pool])
    sp, sf = lp.std() or 1.0, lf.std() or 1.0
    d = np.sqrt(((lp - math.log1p(real[prod_key])) / sp) ** 2 + ((lf - math.log1p(real["freq"])) / sf) ** 2)
    order = sorted(range(len(pool)), key=lambda i: (d[i], pool[i]["word"]))
    return [dict(pool[i], distance=float(d[i])) for i in order[:k]]


def real_features(word, entries, comp, tokens):
    e = next((x for x in entries if x["translit"] == word and len(x["members"]) == 1), None)
    head = e["head"] if e else ""
    return {"word": word, "head": head, "stem": "".join(comp.anchor(word)), "found_in_lexicon": e is not None,
            "prod_first": comp.prod_first(word), "prod_last": comp.prod_last(word),
            "freq": prefix_count(tokens, tamil_prefix(head)) if head else 0}


def picture_words(dedr, key):
    words = set()
    for e in dedr:
        if e["attested"] and rebus.matches(key, e["items"]):
            words |= set(e["tamil_forms"]) if e["tamil_forms"] else set()
    return sorted(words)


# ---------------------------------------------------------------- main

def run(outdir, entries, dedr, tokens, sangam_hashes, pools, synthetic=False):
    rng = np.random.default_rng(SEED)
    comp = rebus.Compounds(entries)
    dedr_t0 = {rebus.tl_norm(f, "T0s") for e in dedr if e["attested"] for f in e["tamil_forms"]}
    cands = candidates(entries, comp, dedr_t0, tokens)
    real = {w: real_features(w, entries, comp, tokens) for w in (W1, W2, W3)}
    pools_w = {
        W1: {k: nearest(cands, real[W1], "prod_first", k) for k in (K_MAIN,) + K_SENS},
        W2: {k: nearest(cands, real[W2], "prod_last", k) for k in (K_MAIN,) + K_SENS},
        W3: {k: nearest(cands, real[W3], "prod_last", k) for k in (K_MAIN,) + K_SENS},
    }
    pic_concepts = []
    for c in pools["picture"]:
        ws = picture_words(dedr, c["key"])
        if ws:
            pic_concepts.append({"id": c["id"], "key": c["key"], "words": ws})
    real_pics = {k: sorted(set(picture_words(dedr, key)) | set(PARPOLA_PICTURE_WORDS[k])) for k, key in PICTURE_KEYS.items()}

    out = {"schema_version": "1.0", "task": "rebus-base-rate/interlocks", "synthetic": synthetic,
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "parameters": {"seed": SEED, "k_main": K_MAIN, "k_sensitivity": list(K_SENS), "draws": DRAWS,
                          "bootstrap": BOOT, "tolerances": list(TOLS), "W1": W1, "W2": W2, "W3": W3,
                          "picture_keys": PICTURE_KEYS, "parpola_picture_words": PARPOLA_PICTURE_WORDS,
                          "numerals": NUMERALS},
           "lexicon": {"tamil_lexicon_entries": len(entries), "two_member_compounds": len(comp.c2),
                       "replacement_candidates": len(cands), "picture_concepts_with_tamil_words": len(pic_concepts)},
           "real_features": real, "real_picture_words": real_pics,
           "replacement_pools": {w: [{k: v for k, v in c.items() if k in ("word", "prod_first", "prod_last", "freq", "distance")}
                                     for c in pools_w[w][K_MAIN]] for w in pools_w},
           "real": {}, "null": {}}
    if not synthetic:
        out["provenance"] = {
            "code": {p.name: rebus.sha256(p) for p in sorted((PKG / "code").glob("*.py"))},
            "inputs": {str(p.relative_to(rebus.ROOT)).replace("\\", "/"): rebus.sha256(p) for p in [
                rebus.DER / "tamil-lex-entries.jsonl", rebus.DER / "dedr-entries.jsonl", PKG / "pools-v1.json"]},
            "sangam_files": sangam_hashes, "sangam_tokens": len(tokens)}

    # ---- real searches
    A, B = comp.A(W1), comp.B(W2)
    A_r = [e for e in A if MURUKAN_RE.search(e["gloss"] or "")]
    B_r = [e for e in B if ASTRAL_FISH_RE.search(e["gloss"] or "")]
    real_res = {"A_size": len(A), "B_size": len(B), "A_restricted_size": len(A_r), "B_restricted_size": len(B_r),
                "A_compounds": [e["translit"] for e in A], "B_compounds_sample": [e["translit"] for e in B][:400],
                "A_restricted": [e["translit"] for e in A_r], "B_restricted": [e["translit"] for e in B_r]}
    for tol in TOLS:
        sh = i1(comp, W1, W2, tol)
        shr = i1(comp, W1, W2, tol, A_r, B_r)
        real_res[f"I1_{tol}"] = {"holds": bool(sh), "n_shared": len(sh), "shared": sh,
                                 "restricted_holds": bool(shr), "restricted_shared": shr}
        real_res[f"I2_{tol}"] = picture_hits(real_pics["I2"], B, 0, tol)
        real_res[f"I3_{tol}"] = picture_hits(real_pics["I3"], A, 1, tol)
        real_res[f"I5_{tol}"] = picture_hits(real_pics["I5"], comp.B(W3), 0, tol)
    n4, found4 = numeral_count(comp, W2)
    real_res["I4"] = {"numerals_with_compound": n4, "compounds": found4}
    out["real"] = real_res

    # ---- I1 null, exact enumeration over replacement pools
    for tol in TOLS:
        res = {}
        for k in (K_MAIN,) + K_SENS:
            p1, p2 = pools_w[W1][k], pools_w[W2][k]
            M = np.zeros((len(p1), len(p2)), dtype=bool)
            nshared = np.zeros((len(p1), len(p2)), dtype=int)
            for i, a in enumerate(p1):
                Aa = comp.A(a["word"])
                for j, b in enumerate(p2):
                    sh = i1(comp, a["word"], b["word"], tol, Aa, None)
                    M[i, j] = bool(sh)
                    nshared[i, j] = len(sh)
            only_w1 = [bool(i1(comp, a["word"], W2, tol)) for a in p1]
            only_w2 = [bool(i1(comp, W1, b["word"], tol)) for b in p2]
            entry = {"pairs": int(M.size), "pairs_with_shared": int(M.sum()), "rate": float(M.mean()),
                     "mean_shared_members": float(nshared.mean()),
                     "rate_only_W1_replaced": float(np.mean(only_w1)), "rate_only_W2_replaced": float(np.mean(only_w2))}
            if k == K_MAIN:
                boots = []
                for _ in range(BOOT):
                    ii = rng.integers(0, M.shape[0], M.shape[0])
                    jj = rng.integers(0, M.shape[1], M.shape[1])
                    boots.append(M[np.ix_(ii, jj)].mean())
                entry["rate_ci95_bootstrap_over_pool_words"] = [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]
                entry["rate_ci95_wilson_pairs"] = rebus.wilson(int(M.sum()), int(M.size))
                entry["share_of_pairs_with_at_least_as_many_shared_as_real"] = float(
                    (nshared >= real_res[f"I1_{tol}"]["n_shared"]).mean()) if real_res[f"I1_{tol}"]["n_shared"] else None
            res[f"K{k}"] = entry
        out["null"][f"I1_{tol}"] = res

    # ---- I1 null with Parpola's semantic restriction emulated by subset size
    for tol in TOLS:
        hits = 0
        p1, p2 = pools_w[W1][K_MAIN], pools_w[W2][K_MAIN]
        nA, nB = len(A_r), len(B_r)
        for _ in range(DRAWS):
            a = p1[rng.integers(len(p1))]["word"]
            b = p2[rng.integers(len(p2))]["word"]
            Aa, Bb = comp.A(a), comp.B(b)
            if nA < len(Aa):
                Aa = [Aa[i] for i in rng.choice(len(Aa), nA, replace=False)]
            if nB < len(Bb):
                Bb = [Bb[i] for i in rng.choice(len(Bb), nB, replace=False)]
            hits += bool(i1(comp, a, b, tol, Aa, Bb))
        out["null"][f"I1_restricted_size_{tol}"] = {"draws": DRAWS, "A_size": nA, "B_size": nB, "hits": hits,
                                                    "rate": hits / DRAWS, "ci95_wilson": rebus.wilson(hits, DRAWS)}

    # ---- picture interlocks (I2, I3, I5) and numerals (I4)
    for tol in TOLS:
        def rate_pics(compounds, position):
            ok = [bool(picture_hits(c["words"], compounds, position, tol)) for c in pic_concepts]
            return float(np.mean(ok)) if ok else None
        res = {"I2_real_W2": rate_pics(B, 0), "I3_real_W1": rate_pics(A, 1), "I5_real_W3": rate_pics(comp.B(W3), 0)}
        res["I2_random_W2"] = float(np.mean([rate_pics(comp.B(b["word"]), 0) for b in pools_w[W2][K_MAIN]]))
        res["I3_random_W1"] = float(np.mean([rate_pics(comp.A(a["word"]), 1) for a in pools_w[W1][K_MAIN]]))
        res["I5_random_W3"] = float(np.mean([rate_pics(comp.B(c["word"]), 0) for c in pools_w[W3][K_MAIN]]))
        out["null"][f"pictures_{tol}"] = res
    n4s = [numeral_count(comp, b["word"])[0] for b in pools_w[W2][K_MAIN]]
    out["null"]["I4"] = {"distribution": {str(v): n4s.count(v) for v in sorted(set(n4s))},
                         "rate_at_least_real": float(np.mean([v >= n4 for v in n4s])) if n4 else None}

    # ---- network null: all components replaced at once
    for tol in TOLS:
        held = {"I1": real_res[f"I1_{tol}"]["holds"], "I2": bool(real_res[f"I2_{tol}"]),
                "I3": bool(real_res[f"I3_{tol}"]), "I4": n4 >= 1, "I5": bool(real_res[f"I5_{tol}"])}
        required = [k for k, v in held.items() if v]
        counts = np.zeros(6, dtype=int)
        all_hits = 0
        cache_A, cache_B = {}, {}
        p1, p2, p3 = pools_w[W1][K_MAIN], pools_w[W2][K_MAIN], pools_w[W3][K_MAIN]
        for _ in range(DRAWS):
            a = p1[rng.integers(len(p1))]["word"]
            b = p2[rng.integers(len(p2))]["word"]
            c = p3[rng.integers(len(p3))]["word"]
            pics = rng.choice(len(pic_concepts), 3, replace=False)
            Aa = cache_A.setdefault(a, comp.A(a))
            Bb = cache_B.setdefault(b, comp.B(b))
            Bc = cache_B.setdefault(c, comp.B(c))
            got = {"I1": bool(i1(comp, a, b, tol, Aa, Bb)),
                   "I2": bool(picture_hits(pic_concepts[pics[0]]["words"], Bb, 0, tol)),
                   "I3": bool(picture_hits(pic_concepts[pics[1]]["words"], Aa, 1, tol)),
                   "I4": numeral_count(comp, b)[0] >= 1,
                   "I5": bool(picture_hits(pic_concepts[pics[2]]["words"], Bc, 0, tol))}
            counts[sum(got.values())] += 1
            all_hits += all(got[k] for k in required) if required else 0
        out["null"][f"network_{tol}"] = {
            "real_holds": held, "required": required, "draws": DRAWS,
            "draws_matching_all_required": int(all_hits), "rate": all_hits / DRAWS,
            "ci95_wilson": rebus.wilson(int(all_hits), DRAWS),
            "distribution_of_interlocks_held": {str(i): int(v) for i, v in enumerate(counts)},
            "rate_at_least_real_count": float(counts[sum(held.values()):].sum() / DRAWS)}

    # ---- decision rules from PROTOCOL.md
    k_rate = out["null"]["I1_T0s"][f"K{K_MAIN}"]["rate"]
    net = out["null"]["network_T0s"]
    out["decision"] = {
        "kill_rule": "the veḷ interlock is dead as evidence if random replacements reproduce a shared member in more than 20% of draws (I1, both words replaced, T0s, K=50)",
        "I1_null_rate": k_rate, "killed": k_rate > 0.20,
        "network_rule": "Parpola's network passes if all interlocks that hold for his words hold together in fewer than 1% of random replacements (T0s)",
        "network_rate": net["rate"], "network_pass": (net["rate"] < 0.01) if net["required"] else None,
    }
    target = Path(outdir) / ("interlocks-synthetic.json" if synthetic else "interlocks.json")
    if not synthetic:
        # compound lists derived from the Tamil Lexicon stay local; the tracked file keeps counts
        detail = {k: real_res.pop(k) for k in ("A_compounds", "B_compounds_sample", "A_restricted", "B_restricted")}
        local = rebus.RAW / "results-v1" / (Path(outdir).name + "-interlocks-detail.json")
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text(json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8")
        out["local_detail"] = {"path": str(local.relative_to(rebus.ROOT)).replace("\\", "/"), "sha256": rebus.sha256(local)}
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def main(outdir, synthetic=False):
    outdir = Path(outdir)
    target = outdir / ("interlocks-synthetic.json" if synthetic else "interlocks.json")
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    pools = json.loads((PKG / "pools-v1.json").read_text(encoding="utf-8"))
    entries = [json.loads(l) for l in (rebus.DER / "tamil-lex-entries.jsonl").open(encoding="utf-8")]
    dedr = rebus.load_dedr()
    tokens, hashes = sangam_tokens()
    out = run(outdir, entries, dedr, tokens, hashes, pools)
    print(json.dumps(out["decision"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
