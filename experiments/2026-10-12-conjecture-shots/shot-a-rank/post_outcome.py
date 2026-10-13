"""Exploratory, post-outcome: descriptive breakdowns of the frozen confirmation result.

Written on 13 October 2026 after confirmation/results.json existed. Nothing here changes
a frozen verdict. Output: confirmation/post-outcome-exploratory.json, described in
AMENDMENT-2026-10-13-post-outcome.md.
"""
from pathlib import Path
import collections
import json
import math
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from shots_common import load_half  # noqa: E402
from seal_table import seal_table  # noqa: E402
import rank_lib as L  # noqa: E402


def main():
    lex = json.loads((HERE / "discovery" / "lexicon.json").read_text(encoding="utf-8"))
    table = seal_table(load_half("confirmation", HERE))
    pop = L.representative(L.size_text_population(table))
    res, _ = L.residualize(pop)
    sd = float(res.std())
    out = {"status": "Exploratory, post-outcome", "residual_sd": sd}

    def unit_rows(key, scores):
        g = L.unit_groups([t[key] for t in pop], res)
        rows = []
        for u, v in g.items():
            if len(v) >= 3:
                rows.append({"unit": u, "n": len(v), "mean_residual": float(np.mean(v)),
                             "z": float(np.mean(v) / (sd / math.sqrt(len(v)))),
                             "share_of_between_ss": None,
                             "discovery_score": scores.get(u, {}).get("score") if scores else None})
        tot = sum(r["n"] * r["mean_residual"] ** 2 for r in rows)
        for r in rows:
            r["share_of_between_ss"] = float(r["n"] * r["mean_residual"] ** 2 / tot)
        return sorted(rows, key=lambda r: -r["share_of_between_ss"])

    out["last_sign_units"] = unit_rows("last", lex["closing_scores_last"])
    out["first_sign_units"] = unit_rows("first", lex["opening_scores_first"])
    low = {u for u, v in lex["closing_scores_last"].items() if v["score"] <= -0.10}
    lv = [r for t, r in zip(pop, res) if t["last"] in low]
    out["discovery_low_scored_last_signs"] = {"signs": sorted(low), "n": len(lv), "mean_residual": float(np.mean(lv))}

    p3pop = L.representative([t for t in table if t["type"] in L.SEAL_TYPES and t["text_ok"] and t["length"] >= 2
                              and t["site"] != "Unknown"])
    sites = collections.Counter(t["site"] for t in p3pop)
    n = len(p3pop)
    by = collections.defaultdict(collections.Counter)
    for t in p3pop:
        by[t["formula"]][t["site"]] += 1
    rows = []
    for u, c in by.items():
        m = sum(c.values())
        if m >= 5:
            contrib = sum(k / n * math.log(k * n / (m * sites[s])) for s, k in c.items())
            rows.append({"formula": u, "n": m, "sites": dict(c.most_common(4)), "mi_contribution": float(contrib)})
    out["closing_formula_site_profiles"] = sorted(rows, key=lambda r: -r["mi_contribution"])[:15]
    out["site_totals"] = dict(sites.most_common(8))
    (HERE / "confirmation" / "post-outcome-exploratory.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("discovery_low_scored_last_signs",)}, indent=1))
    for r in out["last_sign_units"][:8]:
        print("last", r)
    for r in out["first_sign_units"][:8]:
        print("first", r)
    for r in out["closing_formula_site_profiles"][:8]:
        print("formula", r)
    print(out["site_totals"])


if __name__ == "__main__":
    main()
