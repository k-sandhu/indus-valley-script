"""Post-outcome analyses of the blind template results. Nothing here was frozen.

E1  Published against blind templates: hit rates, Fisher's exact test, and the ratio of the
    two hit-rate ratios with a bootstrap interval over templates.
E2  The primary ratio without the 'bull's head' templates, whose words (ā, āṉ, āvu) are the
    shortest and whose identification is the least direct.
E3  How many blind templates Parpola would have needed to try to collect the seven successes
    of his published set, at the blind hit rate of his own words.

    python experiments/2026-10-22-rebus-blind-templates/code/exploratory.py RESULTS_DIR OUTDIR
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SEED = 20261023
BOOT = 5000


def fisher_greater(a, n1, c, n2):
    """P(X >= a) for the hypergeometric count of hits in group 1 (one-sided Fisher test)."""
    k, n = a + c, n1 + n2
    total = math.comb(n, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / total


def rows(res, name):
    r = res["results"][name]["per_template"]
    return np.array([x["parpola_holds"] for x in r], float), np.array([x["random_rate"] for x in r], float), r


def main(results_dir, outdir):
    outdir = Path(outdir)
    target = outdir / "exploratory.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    res = json.loads((Path(results_dir) / "templates.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(SEED)
    hb, rb, _ = rows(res, "primary")
    hp, rp, _ = rows(res, "published_shape_C")
    out = {"schema_version": "1.0", "task": "rebus-blind-templates/exploratory", "synthetic": False,
           "created_utc": datetime.now(timezone.utc).isoformat(), "status": "post-outcome, not frozen",
           "source": {"results": str(Path(results_dir) / "templates.json")}}

    # E1
    rr = []
    for _ in range(BOOT):
        ib = rng.integers(0, len(hb), len(hb))
        ip = rng.integers(0, len(hp), len(hp))
        if rb[ib].sum() > 0 and rp[ip].sum() > 0 and hb[ib].sum() > 0:
            rr.append((hp[ip].sum() / rp[ip].sum()) / (hb[ib].sum() / rb[ib].sum()))
    out["E1_published_vs_blind"] = {
        "published": {"templates": len(hp), "hits": int(hp.sum()), "hit_rate": hp.mean(), "random_rate": rp.mean(),
                      "ratio": hp.sum() / rp.sum()},
        "blind": {"templates": len(hb), "hits": int(hb.sum()), "hit_rate": hb.mean(), "random_rate": rb.mean(),
                  "ratio": hb.sum() / rb.sum()},
        "hit_rate_ratio_published_over_blind": hp.mean() / hb.mean(),
        "fisher_one_sided_p_published_hit_rate_higher": fisher_greater(int(hp.sum()), len(hp), int(hb.sum()), len(hb)),
        "ratio_of_ratios": (hp.sum() / rp.sum()) / (hb.sum() / rb.sum()),
        "ratio_of_ratios_ci95_bootstrap": [float(np.quantile(rr, 0.025)), float(np.quantile(rr, 0.975))],
        "bootstrap_draws_used": len(rr)}

    # E2
    _, _, per = rows(res, "primary")
    keep = [i for i, x in enumerate(per) if "BULLHEAD" not in (x["first"], x["second"])]
    h2, r2 = hb[keep], rb[keep]
    boots = []
    for _ in range(BOOT):
        i = rng.integers(0, len(keep), len(keep))
        if r2[i].sum() > 0:
            boots.append(h2[i].sum() / r2[i].sum())
    out["E2_without_bull_head"] = {"templates": len(keep), "hits": int(h2.sum()), "expected_random_hits": float(r2.sum()),
                                   "ratio": float(h2.sum() / r2.sum()),
                                   "ratio_ci95_bootstrap": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]}

    # E3: number of templates m at which seven or more successes become likely, at the blind rate of his words
    p = hb.mean()
    def p_at_least(k, m):
        return sum(math.comb(m, j) * p ** j * (1 - p) ** (m - j) for j in range(k, m + 1))
    out["E3_templates_needed"] = {"blind_hit_rate": p, "successes": int(hp.sum()),
                                  "p_at_least_7_of_12": p_at_least(int(hp.sum()), len(hp)),
                                  "m_with_p_half": next(m for m in range(7, 200) if p_at_least(int(hp.sum()), m) >= 0.5),
                                  "expected_templates_per_7_successes": hp.sum() / p}
    outdir.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k.startswith("E")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
