"""Shot A confirmation analysis. Scores every prediction in PREDICTIONS.md.

Usage
  python confirm.py                     the confirmation run (once PREDICTIONS.md and
                                        PREDICTIONS.sha256 are frozen); reads the
                                        confirmation half through shots_common.load_half
                                        and writes confirmation/results.json
  python confirm.py --dry-run-discovery code test on the discovery half only; writes
                                        discovery/confirm-dry-run.json. Its numbers are
                                        in-sample and carry no evidential weight.

The script runs unchanged after freezing. It checks that discovery/lexicon.json still has
the SHA-256 recorded in PREDICTIONS.md before using it.
"""
from pathlib import Path
import argparse
import datetime
import json
import re
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from shots_common import load_half, sha256  # noqa: E402
from seal_table import seal_table  # noqa: E402
import rank_lib as L  # noqa: E402

NPERM = 9999
SEED = 20261013
ALPHA = 0.05
MIN_HIGH = 5          # prediction 4 is untestable with fewer high-set seals
MIN_PAIRS = 10        # prediction 2 is untestable with fewer usable identical pairs


def frozen_lexicon_hash():
    text = (HERE / "PREDICTIONS.md").read_text(encoding="utf-8")
    m = re.search(r"lexicon\.json SHA-256:\s*`?([0-9a-f]{64})", text)
    if not m:
        raise SystemExit("PREDICTIONS.md does not record the lexicon hash")
    return m.group(1)


def verdict(p, ok=True):
    if p is None or not ok:
        return "untestable"
    return "pass" if p < ALPHA else "fail"


def run(half):
    lex_path = HERE / "discovery" / "lexicon.json"
    recorded = frozen_lexicon_hash()
    if sha256(lex_path) != recorded:
        raise SystemExit("discovery/lexicon.json differs from the hash frozen in PREDICTIONS.md")
    lex = json.loads(lex_path.read_text(encoding="utf-8"))
    rows = load_half("confirmation", HERE) if half == "confirmation" else load_half("discovery")
    table = seal_table(rows)
    rng = np.random.default_rng(SEED)

    pop_all = L.size_text_population(table)
    pop = L.representative(pop_all)
    res, r2 = L.residualize(pop)
    strata = L.strata_of(pop)
    last = [t["last"] for t in pop]
    first = [t["first"] for t in pop]
    out = {"half": half, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "predictions_sha256": sha256(HERE / "PREDICTIONS.md"), "lexicon_sha256": recorded,
           "permutations": NPERM, "seed": SEED,
           "population": {"seals": len(pop_all), "components": len(pop), "base_model_r2": r2,
                          "residual_sd": float(res.std()), "movable": L.StratPerm(strata).movable}}

    # P1a: closing units carry size beyond type, site and length
    p1a = L.between_ratio_test(last, res, strata, 3, NPERM, rng)
    p1a["verdict"] = verdict(p1a["p_one_sided"])
    out["P1a"] = p1a

    # P1b: grade order of the frozen closing scores reappears (calibration against rearrangements)
    sc = lex["closing_scores_last"]
    p1b = L.rearrangement_test(last, res, sc, lex["score_bins"], NPERM, rng)
    p1b["seal_permutation"] = L.score_correlation_test(last, res, strata, sc, NPERM, rng)
    p1b["verdict"] = "pass" if (p1b["r"] > 0 and p1b["p_one_sided"] < ALPHA) else "fail"
    out["P1b"] = p1b

    # P1c: closing explains more size variation than opening (matched between-unit ratios)
    sp = L.StratPerm(strata)
    A, F = np.array(last, dtype=object), np.array(first, dtype=object)
    na, nf = [], []
    for _ in range(NPERM):
        idx = sp.draw(rng)
        na.append(L.between_ss(list(A[idx]), res, 3))
        nf.append(L.between_ss(list(F[idx]), res, 3))
    na, nf = np.array(na), np.array(nf)
    ra, rf = L.between_ss(last, res, 3) / na.mean(), L.between_ss(first, res, 3) / nf.mean()
    dn = na / na.mean() - nf / nf.mean()
    p1c = {"closing_ratio": float(ra), "opening_ratio": float(rf), "difference": float(ra - rf),
           "p_one_sided": float((1 + (dn >= ra - rf).sum()) / (1 + NPERM)), "permutations": NPERM}
    p1c["verdict"] = verdict(p1c["p_one_sided"])
    out["P1c"] = p1c

    # P2: identical legends are closer in size than matched seals
    p2 = L.identical_legend_test(pop_all, NPERM, rng)
    p2["verdict"] = verdict(p2["p_one_sided_smaller"], p2["usable_pairs"] >= MIN_PAIRS)
    out["P2"] = p2

    # P3: opening signs more site-specific than closing formulae
    p3pop = L.representative([t for t in table if t["type"] in L.SEAL_TYPES and t["text_ok"] and t["length"] >= 2
                              and t["site"] != "Unknown"])
    p3 = L.site_specificity_test(p3pop, "first", "formula", NPERM, rng)
    p3["verdict"] = verdict(p3["p_one_sided"])
    out["P3"] = p3

    # P4: the high closing set marks larger seals
    H = set(lex["high_set"])
    p4 = L.contrast_test(["H" if l in H else "O" for l in last], res, strata, {"H"}, {"O"}, NPERM, rng)
    p4["verdict"] = verdict(p4["p_one_sided"], p4["n_high"] >= MIN_HIGH)
    p4["seals"] = [{"cisi": t["cisi"], "site": t["site"], "type": t["type"], "length": t["length"], "last": t["last"],
                    "size_mm": round(t["size"], 2), "residual": round(float(r), 3)} for t, r in zip(pop, res) if t["last"] in H]
    out["P4"] = p4

    # P5 (auxiliary): unicorn W variant on larger seals
    p5 = L.ornament_test(pop, res, NPERM, rng)
    p5["verdict"] = verdict(p5["p_one_sided"], p5["n_high"] >= MIN_HIGH and p5["n_low"] >= MIN_HIGH)
    out["P5"] = p5

    # Reported, not scored
    out["reported"] = {
        "last_sign_without_high_set": L.between_ratio_test([l if l not in H else None for l in last], res, strata, 3, 1999, rng),
        "formula_between_unit": L.between_ratio_test([t["formula"] for t in pop], res, strata, 3, 1999, rng),
        "first_between_unit": L.between_ratio_test(first, res, strata, 3, 1999, rng),
        "site_specificity_first_vs_last": L.site_specificity_test(p3pop, "first", "last", 1999, rng),
        "opening_score_correlation": L.score_correlation_test(first, res, strata, lex["opening_scores_first"], 1999, rng),
    }

    # Kill condition
    dead = out["P4"]["verdict"] != "pass" and out["P1a"]["verdict"] != "pass"
    out["kill_condition_met"] = bool(dead)
    out["verdicts"] = {k: out[k]["verdict"] for k in ("P1a", "P1b", "P1c", "P2", "P3", "P4", "P5")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run-discovery", action="store_true")
    a = ap.parse_args()
    if a.dry_run_discovery:
        out = run("discovery")
        out["note"] = "dry run on the discovery half: in-sample code test, no evidential weight"
        dest = HERE / "discovery" / "confirm-dry-run.json"
    else:
        dest = HERE / "confirmation" / "results.json"
        if dest.exists():
            raise SystemExit("confirmation/results.json exists; the confirmation outcome is frozen")
        out = run("confirmation")
        (HERE / "confirmation").mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out["verdicts"], indent=1), "kill:", out["kill_condition_met"])


if __name__ == "__main__":
    main()
