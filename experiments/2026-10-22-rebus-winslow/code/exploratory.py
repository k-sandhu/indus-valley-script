"""Post-outcome analyses of the Winslow rerun. Not frozen; chosen after results-v1 was read.

In Winslow no two-member compound begins with muruku, so the frozen pools for
muruku hold words without compounds and the frozen null rate is zero by
construction. These analyses ask what the same search gives once the first word
has compounds, using the functions of the frozen code:

  X1  Winslow, the muruku pool matched to the Tamil Lexicon's productivity of
      muruku (7 first-member compounds) and its Sangam frequency; the mīṉ pool as
      frozen (Winslow's 29 second-member compounds)
  X2  Winslow, the muruku pool matched to one first-member compound, the most a
      complete parse could give (the parser misses murukkam-pū)
  X3  both dictionaries with the same target sizes, 7 first-member compounds for
      the first word and 29 second-member compounds for the second, so that the
      chance of a shared member at equal set sizes can be compared
  X4  the Tamil forms in Winslow's text that end in மீன், and how many of them are
      entries, compounds of mīṉ by our parse, or only words inside definitions

    python experiments/2026-10-22-rebus-winslow/code/exploratory.py OUTDIR
"""

import glob
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_winslow  # noqa: E402
from run_winslow import rebus, run_interlocks  # noqa: E402

SEED = 20261022
K = 50
BOOT = 2000


def rate(comp, p1, p2, tol, rng):
    M = np.zeros((len(p1), len(p2)), dtype=bool)
    for i, a in enumerate(p1):
        Aa = comp.A(a["word"])
        for j, b in enumerate(p2):
            M[i, j] = bool(run_interlocks.i1(comp, a["word"], b["word"], tol, Aa, None))
    boots = []
    for _ in range(BOOT):
        ii = rng.integers(0, M.shape[0], M.shape[0])
        jj = rng.integers(0, M.shape[1], M.shape[1])
        boots.append(M[np.ix_(ii, jj)].mean())
    return {"pairs": int(M.size), "pairs_with_shared": int(M.sum()), "rate": float(M.mean()),
            "ci95_bootstrap_over_pool_words": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]}


def pool_summary(pool, key):
    return {"mean_" + key: float(np.mean([p[key] for p in pool])), "median_freq": float(np.median([p["freq"] for p in pool])),
            "max_distance": float(max(p["distance"] for p in pool))}


def setup(entries, dedr, tokens):
    comp = rebus.Compounds(entries)
    dedr_t0 = {rebus.tl_norm(f, "T0s") for e in dedr if e["attested"] for f in e["tamil_forms"]}
    cands = run_interlocks.candidates(entries, comp, dedr_t0, tokens)
    real = {w: run_interlocks.real_features(w, entries, comp, tokens) for w in ("muruku", "mīṉ")}
    return comp, cands, real


def target(real, **override):
    t = dict(real)
    t.update(override)
    return t


def main(outdir):
    outdir = Path(outdir)
    out_path = outdir / "exploratory.json"
    if out_path.exists():
        print("refusing to overwrite", out_path)
        return 1
    rng = np.random.default_rng(SEED)
    dedr = rebus.load_dedr()
    tokens, _ = run_interlocks.sangam_tokens()
    win = run_winslow.load_entries()
    lex = [json.loads(l) for l in (rebus.DER / "tamil-lex-entries.jsonl").open(encoding="utf-8")]
    cw, cand_w, real_w = setup(win, dedr, tokens)
    cl, cand_l, real_l = setup(lex, dedr, tokens)
    res = {"schema_version": "1.0", "task": "rebus-winslow/exploratory", "synthetic": False, "post_outcome": True,
           "created_utc": datetime.now(timezone.utc).isoformat(), "seed": SEED, "k": K,
           "real_features": {"winslow": real_w, "tamil_lexicon": real_l},
           "provenance": {"code": {p.name: run_winslow.sha(p) for p in sorted((run_winslow.PKG / "code").glob("*.py"))},
                          "inputs": {run_winslow.rel(p): run_winslow.sha(p) for p in
                                     (run_winslow.TABLE, rebus.DER / "tamil-lex-entries.jsonl", rebus.DER / "dedr-entries.jsonl")}}}

    w2_frozen = run_interlocks.nearest(cand_w, real_w["mīṉ"], "prod_last", K)
    # X1: muruku pool at the Lexicon's productivity
    p1 = run_interlocks.nearest(cand_w, target(real_w["muruku"], prod_first=real_l["muruku"]["prod_first"]), "prod_first", K)
    res["X1_winslow_muruku_at_lexicon_productivity"] = {
        "target_prod_first": real_l["muruku"]["prod_first"], "pool_W1": pool_summary(p1, "prod_first"),
        "pool_W2": pool_summary(w2_frozen, "prod_last"),
        "T0s": rate(cw, p1, w2_frozen, "T0s", rng), "T1s": rate(cw, p1, w2_frozen, "T1s", rng)}
    # X2: muruku pool at one first-member compound
    p1b = run_interlocks.nearest(cand_w, target(real_w["muruku"], prod_first=1), "prod_first", K)
    res["X2_winslow_muruku_at_one_compound"] = {
        "target_prod_first": 1, "pool_W1": pool_summary(p1b, "prod_first"),
        "T0s": rate(cw, p1b, w2_frozen, "T0s", rng), "T1s": rate(cw, p1b, w2_frozen, "T1s", rng)}
    # X3: equal target sizes in both dictionaries
    x3 = {"target_prod_first_W1": real_l["muruku"]["prod_first"], "target_prod_last_W2": real_w["mīṉ"]["prod_last"]}
    for name, comp, cands, real in (("winslow", cw, cand_w, real_w), ("tamil_lexicon", cl, cand_l, real_l)):
        q1 = run_interlocks.nearest(cands, target(real["muruku"], prod_first=x3["target_prod_first_W1"]), "prod_first", K)
        q2 = run_interlocks.nearest(cands, target(real["mīṉ"], prod_last=x3["target_prod_last_W2"]), "prod_last", K)
        x3[name] = {"pool_W1": pool_summary(q1, "prod_first"), "pool_W2": pool_summary(q2, "prod_last"),
                    "T0s": rate(comp, q1, q2, "T0s", rng)}
    res["X3_equal_set_sizes"] = x3

    # X4: Tamil forms ending in மீன் in Winslow's text
    by_head = {}
    for r in win:
        by_head.setdefault(r["head"], []).append(r)
    forms = set()
    for f in sorted(glob.glob(str(run_winslow.RAW / "sources-v1" / "winslow" / "page-*.html"))):
        t = Path(f).read_text(encoding="utf-8")
        forms |= {m.strip() for m in re.findall(r"<(?:tam|b)>([^<]*?மீன்)</(?:tam|b)>", t)}
    forms = {w for w in forms if w != "மீன்" and " " not in w}
    entries_ = [w for w in forms if w in by_head]
    split_mīṉ = [w for w in entries_ if any(len(r["members"]) == 2 and rebus.tl_norm(r["members"][1], "T1s") == ("m", "i", "ṉ")
                                            for r in by_head[w])]
    res["X4_forms_ending_in_min"] = {
        "distinct_forms": len(forms), "entries": len(entries_), "split_as_X_min": len(split_mīṉ),
        "only_in_definitions": len(forms) - len(entries_),
        "parpola_compounds_as_entries": {w: w in by_head for w in ("முருகவேள்", "வெண்மீன்", "வெள்ளிமீன்", "முருகக்கடவுள்")},
        "parpola_compounds_in_text": {w: w in forms or any(w in Path(f).read_text(encoding="utf-8") for f in
                                                          glob.glob(str(run_winslow.RAW / "sources-v1" / "winslow" / "page-*.html")))
                                      for w in ("முருகவேள்", "வெண்மீன்", "வெள்ளிமீன்")}}
    outdir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v.get("T0s", v) if isinstance(v, dict) else v) for k, v in res.items()
                      if k.startswith("X")}, ensure_ascii=False, indent=1)[:3000])
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
