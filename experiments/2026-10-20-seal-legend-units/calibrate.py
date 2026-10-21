"""Expected values, predictive bounds and power for the prospective predictions (PROTOCOL section 7).

Usage: python -P experiments/2026-10-20-seal-legend-units/calibrate.py --version v1 --out <json>

Every statistic is computed on the held set H with the frozen inventory and rules, with the
known corpus for recurrence lookups taken as the build corpus B (H's own components never enter
it). The same functions score the fresh pools in score_prospective.py.
"""
import argparse
import random
import sys
from math import comb
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legend_units as U  # noqa: E402

SIZES = [10, 20, 30, 50, 80, 100, 150]
EXPECTED = {"cisi31_seals": 50, "post_catalogue": 30, "combined": 80}
SIMS = 20000


class Known:
    """Lookup tables over the known corpus: final pairs, initial pairs and contiguous stretches."""

    def __init__(self, texts):
        self.texts = [tuple(t) for t in texts]
        self.end2, self.start2, self.sub = {}, {}, {}
        for t in self.texts:
            if len(t) >= 2:
                self.end2.setdefault(t[-2:], set()).add(t)
                self.start2.setdefault(t[:2], set()).add(t)
            for i in range(len(t)):
                for j in range(i + 2, min(len(t), i + 12) + 1):
                    self.sub.setdefault(t[i:j], set()).add(t)

    def _hit(self, table, key, own):
        return any(x != own for x in table.get(key, ()))

    def legend_stats(self, t, inv, stock):
        t = tuple(t)
        s = U.segment_by_rules(t, inv, stock)
        close = s["closing"]
        opening = t[:len(t) - len(close)] if close else None
        return {"closing": close is not None,
                "end_pair_known": self._hit(self.end2, t[-2:], t),
                "start_pair_known": self._hit(self.start2, t[:2], t),
                "opening_len": len(opening) if opening is not None else None,
                "opening_known": (self._hit(self.sub, opening, t) if opening is not None and len(opening) >= 2 else None),
                "closing_formula": list(close) if close else None,
                "cuts": s["cuts"]}


def mcnemar_one_sided(b, c):
    """P(at least b of b+c discordant pairs favour ends) under equal odds."""
    n = b + c
    if n == 0:
        return 1.0
    return sum(comb(n, k) for k in range(b, n + 1)) / 2 ** n


def beta_binomial_quantiles(x, n_obs, n_new, rng, sims=SIMS):
    p = rng.beta(1 + x, 1 + n_obs - x, size=sims)
    k = rng.binomial(n_new, p)
    return np.quantile(k / n_new, [0.025, 0.975]).tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    raw = U.RAW / f"frozen-{args.version}"
    inv = {tuple(r["unit"]) for r in U.json.loads((raw / "inventory.json").read_text(encoding="utf-8"))["units"]}
    stock_rows = U.json.loads((raw / "closing-stock.json").read_text(encoding="utf-8"))["units"]
    stock = {tuple(r["unit"]) for r in stock_rows}
    held = U.read_jsonl(raw / "held-legends.jsonl")
    texts, faces, _, _ = U.load_inputs()
    H = U.held_components(texts)
    known = Known(d["text"] for d in texts if d["component"] not in H)
    rows = [known.legend_stats(h["text"], inv, stock) for h in held]
    n = len(rows)
    rng = np.random.default_rng(20261020)

    # S1 closing coverage and its within-legend shuffle null
    x1 = sum(r["closing"] for r in rows)
    prng = random.Random(f"{U.SEED}:shuffle")
    null_cov = []
    for _ in range(2000):
        cov = 0
        for h in held:
            t = list(h["text"])
            prng.shuffle(t)
            cov += U.closing_formula(tuple(t), stock) is not None
        null_cov.append(cov / n)
    p_null = float(np.mean(null_cov))

    # S2 end-pair versus start-pair recurrence
    e = [r["end_pair_known"] for r in rows]
    s = [r["start_pair_known"] for r in rows]
    b = sum(a and not c for a, c in zip(e, s))
    c = sum(c and not a for a, c in zip(e, s))

    # S3 openings found elsewhere, among stock-closed legends with an opening of 2+ signs
    o = [r["opening_known"] for r in rows if r["closing"] and r["opening_len"] and r["opening_len"] >= 2]
    x3 = sum(o)

    # S4 descriptive: line divisions of the known divided faces at the opening/closing junction
    junction, chance, scorable = 0, 0.0, 0
    for f in faces:
        if not f["order"]:
            continue
        t, cuts = f[f["order"]]["text"], f[f["order"]]["cuts"]
        close = U.closing_formula(t, stock)
        if close is None or len(t) < 3:
            continue
        scorable += 1
        junction += (len(t) - len(close)) in cuts
        chance += len(cuts) / (len(t) - 1)

    stock_top = sorted(stock_rows, key=lambda r: -r["final_components"])[:10]
    top10 = {tuple(r["unit"]) for r in stock_top}
    closed = [r for r in rows if r["closing"]]
    x5 = sum(tuple(r["closing_formula"]) in top10 for r in closed)

    def power_s1(nn):
        lo = beta_binomial_quantiles(x1, n, nn, rng)[0]
        out = {"lower_bound": lo}
        for label, p in (("conjecture_rate", x1 / n), ("rate_minus_0.15", x1 / n - 0.15),
                         ("rate_minus_0.25", x1 / n - 0.25), ("shuffle_null", p_null)):
            p = max(p, 0.0)
            k = rng.binomial(nn, p, size=SIMS)
            out[f"p_pass_if_{label}"] = float(np.mean(k / nn >= lo - 1e-12))
        null_hi = float(np.quantile(rng.binomial(nn, p_null, size=SIMS) / nn, 0.975))
        out["kill_bound_shuffle_null_97.5"] = null_hi
        return out

    pairs = list(zip(e, s))

    def power_s2(nn, sims=5000):
        hits_c = hits_n = 0
        pe, ps = np.mean(e), np.mean(s)
        pm = (pe + ps) / 2
        for _ in range(sims):
            draw = [pairs[i] for i in rng.integers(0, n, nn)]
            bb = sum(a and not cc for a, cc in draw)
            c2 = sum(cc and not a for a, cc in draw)
            hits_c += (bb - c2) / nn >= 0.10 and mcnemar_one_sided(bb, c2) < 0.05
            # null: ends and starts recur equally, keeping H's discordance rate
            disc = (b + c) / n
            dn = rng.binomial(nn, disc)
            bn = rng.binomial(dn, 0.5)
            hits_n += (bn - (dn - bn)) / nn >= 0.10 and mcnemar_one_sided(bn, dn - bn) < 0.05
        return {"p_pass_if_conjecture": hits_c / sims, "p_pass_if_no_asymmetry": hits_n / sims,
                "mean_end_known": float(pe), "mean_start_known": float(ps), "pooled": float(pm)}

    def power_s3(nn_legends):
        share = len(o) / n
        nn = max(1, int(round(nn_legends * share)))
        hi = beta_binomial_quantiles(x3, len(o), nn, rng)[1]
        out = {"expected_openings_scored": nn, "upper_bound": hi}
        for label, p in (("conjecture_rate", x3 / len(o)), ("rate_plus_0.20", x3 / len(o) + 0.20),
                         ("formulaic_openings_0.9", 0.9)):
            k = rng.binomial(nn, min(p, 1.0), size=SIMS)
            out[f"p_pass_if_{label}"] = float(np.mean(k / nn <= hi + 1e-12))
        return out

    result = {"version": args.version, "held_legends": n, "frozen_files": {p.name: U.sha256(p) for p in sorted(raw.glob("*.json*"))},
              "S1_closing_coverage": {"held": x1 / n, "count": x1, "shuffle_null_mean": p_null,
                                      "shuffle_null_q975": float(np.quantile(null_cov, 0.975)),
                                      "by_size": {str(k): power_s1(k) for k in SIZES},
                                      "expected": {name: power_s1(k) for name, k in EXPECTED.items()}},
              "S2_end_start_asymmetry": {"held_end_known": float(np.mean(e)), "held_start_known": float(np.mean(s)),
                                         "held_difference": float(np.mean(e) - np.mean(s)), "discordant_end": b,
                                         "discordant_start": c, "held_mcnemar_one_sided_p": mcnemar_one_sided(b, c),
                                         "by_size": {str(k): power_s2(k) for k in SIZES},
                                         "expected": {name: power_s2(k) for name, k in EXPECTED.items()}},
              "S3_opening_known_elsewhere": {"held_scored": len(o), "held_known": x3,
                                             "held_share": x3 / len(o) if o else None,
                                             "share_of_legends_scored": len(o) / n,
                                             "by_size": {str(k): power_s3(k) for k in SIZES},
                                             "expected": {name: power_s3(k) for name, k in EXPECTED.items()}},
              "S4_division_at_junction_known_faces": {"scorable_faces": scorable, "at_junction": junction,
                                                      "chance_expected": chance,
                                                      "note": "in-sample: these divisions trained the model"},
              "S5_top10_share_of_stock_closings": {"held_closed": len(closed), "in_top10": x5,
                                                   "share": x5 / len(closed) if closed else None,
                                                   "lower_bound_by_size": {str(k): beta_binomial_quantiles(x5, len(closed), max(1, int(round(k * len(closed) / n))), rng)[0] for k in SIZES}}}
    U.write_json(args.out, result)
    print(U.json.dumps({k: v for k, v in result.items() if k.startswith("S")}, indent=1)[:6000])


if __name__ == "__main__":
    main()
