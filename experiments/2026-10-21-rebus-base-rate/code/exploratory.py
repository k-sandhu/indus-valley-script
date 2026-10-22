"""Post-outcome exploration, written after results-v2 were read. Nothing here was frozen.

E1  The restricted veḷ search failed for Parpola's own words because the Tamil
    Lexicon glosses muruka-vēḷ by cross-reference, so the frozen regular expression
    did not count it as a name of Murukan. We add it by hand and rerun the
    size-matched null.
E2  Which numerals from one to ten form an attested compound with mīṉ, and how
    often each numeral forms a compound with the replacement head nouns.
E3  How the network's chance rate depends on the number of templates tried: the
    probability that at least four of m templates succeed when each succeeds at
    the mean per-template rate measured with random words.
E4  The largest factor by which each interlock can raise the odds of the reading.

    python experiments/2026-10-21-rebus-base-rate/code/exploratory.py RESULTS_DIR OUTDIR
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebus  # noqa: E402
import run_interlocks as ri  # noqa: E402

PKG = rebus.ROOT / "experiments" / "2026-10-21-rebus-base-rate"
NUMERALS_1_10 = {1: ["oru", "ōr", "or"], 2: ["iru", "īr", "iraṇṭu"], 3: ["mū", "mu", "mūṉṟu"], 4: ["nāl", "nāṉku", "nāṟ"],
                 5: ["ai", "aim", "aintu"], 6: ["aṟu", "āṟu"], 7: ["eḻu", "ēḻu"], 8: ["eṇ", "eṭṭu"],
                 9: ["oṉpatu", "toṇ"], 10: ["pattu", "pat", "paḵtu"]}


def numeral_hits(comp, w2):
    B = comp.B(w2)
    out = {}
    for n, forms in NUMERALS_1_10.items():
        stems = {rebus.tl_norm(f, "T1s") for f in forms}
        out[n] = sorted(e["translit"] for e in B
                        if {rebus.tl_norm(b, "T1s") for b in rebus.sandhi_bases(e["members"][0])} & stems)
    return out


def main(results_dir, outdir):
    results_dir, outdir = Path(results_dir).resolve(), Path(outdir).resolve()
    target = outdir / "exploratory.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    inter = json.loads((results_dir / "interlocks.json").read_text(encoding="utf-8"))
    entries = [json.loads(l) for l in (rebus.DER / "tamil-lex-entries.jsonl").open(encoding="utf-8")]
    comp = rebus.Compounds(entries)
    rng = np.random.default_rng(ri.SEED + 1)
    out = {"schema_version": "1.0", "task": "rebus-base-rate/exploratory", "post_outcome": True,
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "results_dir": str(results_dir.relative_to(rebus.ROOT)).replace("\\", "/"),
           "provenance": {"code": {p.name: rebus.sha256(p) for p in sorted((PKG / "code").glob("*.py"))},
                          "results": rebus.sha256(results_dir / "interlocks.json")}}

    # E1
    A, B = comp.A(ri.W1), comp.B(ri.W2)
    A_r = [e for e in A if ri.MURUKAN_RE.search(e["gloss"] or "")]
    added = [e for e in A if e["translit"] == "muruka-vēḷ" and e not in A_r]
    A_r2 = A_r + added
    B_r = [e for e in B if ri.ASTRAL_FISH_RE.search(e["gloss"] or "")]
    e1 = {"muruka_vel_gloss": [e["gloss"] for e in added], "A_restricted": [e["translit"] for e in A_r2],
          "B_restricted_size": len(B_r)}
    pools = {w: [x["word"] for x in inter["replacement_pools"][w]] for w in (ri.W1, ri.W2)}
    for tol in ri.TOLS:
        real = ri.i1(comp, ri.W1, ri.W2, tol, A_r2, B_r)
        hits = 0
        for _ in range(ri.DRAWS):
            a = pools[ri.W1][rng.integers(50)]
            b = pools[ri.W2][rng.integers(50)]
            Aa, Bb = comp.A(a), comp.B(b)
            if len(A_r2) < len(Aa):
                Aa = [Aa[i] for i in rng.choice(len(Aa), len(A_r2), replace=False)]
            if len(B_r) < len(Bb):
                Bb = [Bb[i] for i in rng.choice(len(Bb), len(B_r), replace=False)]
            hits += bool(ri.i1(comp, a, b, tol, Aa, Bb))
        e1[tol] = {"real_shared": real, "draws": ri.DRAWS, "hits": hits, "rate": hits / ri.DRAWS,
                   "ci95_wilson": rebus.wilson(hits, ri.DRAWS)}
    out["E1_restricted_with_muruka_vel"] = e1

    # E2
    real_num = numeral_hits(comp, ri.W2)
    pool_num = [numeral_hits(comp, w) for w in pools[ri.W2]]
    out["E2_numerals_with_min"] = {
        "real": {str(n): v for n, v in real_num.items()},
        "numerals_with_compound": sorted(n for n, v in real_num.items() if v),
        "pool_share_with_compound": {str(n): sum(1 for p in pool_num if p[n]) / len(pool_num) for n in NUMERALS_1_10},
        "pool_numerals_per_word": [sum(1 for v in p.values() if v) for p in pool_num],
    }

    # E3
    pics = inter["null"]["pictures_T0s"]
    i4_any = sum(v for k, v in inter["null"]["I4"]["distribution"].items() if int(k) >= 1) / 50
    rates = {"I1": inter["null"]["I1_T0s"]["K50"]["rate"], "I2": pics["I2_random_W2"], "I3": pics["I3_random_W1"],
             "I4_at_least_one": i4_any, "I5": pics["I5_random_W3"]}
    p = float(np.mean(list(rates.values())))

    def at_least(k, m, p):
        return sum(math.comb(m, j) * p ** j * (1 - p) ** (m - j) for j in range(k, m + 1))
    out["E3_template_multiplicity"] = {
        "per_template_rates_T0s": rates, "mean_rate": p,
        "p_at_least_4_of_m": {str(m): at_least(4, m, p) for m in (5, 6, 8, 10, 12, 15, 20, 30)},
        "templates_for_p_above_0_05": next(m for m in range(4, 200) if at_least(4, m, p) > 0.05),
        "templates_for_p_above_0_5": next(m for m in range(4, 200) if at_least(4, m, p) > 0.5),
    }

    # E4
    out["E4_largest_odds_factor"] = {k: (1 / v if v else None) for k, v in rates.items()}
    out["E4_largest_odds_factor"]["network_T0s"] = 1 / inter["null"]["network_T0s"]["rate"]
    out["E4_largest_odds_factor"]["network_T1s"] = 1 / inter["null"]["network_T1s"]["rate"]
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1)[:6000])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
