"""Post-outcome check (exploratory): did Mound F's legends grow more like Mohenjo-daro's?

Each readable sign of a Mound F legend gets a log ratio of its smoothed frequency in
Mohenjo-daro seal legends to its smoothed frequency in Harappa seal legends outside
Mound F's stratified seals (the pool, no dates). A legend's score is the mean log ratio
over its readable signs, computed once with every sign and once with the interior signs
only (neither first nor last). The score is correlated with u within trenches, as in
the frozen tests. A positive correlation means later legends draw more on signs that are
commoner at Mohenjo-daro than at Harappa. Nothing here is confirmation.

    python -P experiments/2026-10-20-harappa-legend-periods/post_outcome_convergence.py OUT_JSON
"""
from collections import Counter
import json
import math
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import period_stats as P  # noqa: E402
from period_stats import S  # noqa: E402
import explore_discovery as E  # noqa: E402
import build_inputs as B  # noqa: E402

ROOT = PACKAGE.parents[1]
CONFIRMATION = ROOT / "data/raw/2026-10-20-harappa-legend-periods/confirmation-mound-f-vats.jsonl"


def frequencies(rows):
    c = Counter(s for r in rows for s in r["signs_reading_rtl"] if s != "000")
    return c, sum(c.values())


def main():
    out_path = Path(sys.argv[1])
    if out_path.exists():
        raise SystemExit("output exists")
    faces = P.read_rows(B.FACES)
    md = [f for f in faces if f["site"] == "Mohenjo-daro" and f["object_type"].startswith("SEAL")]
    pool = E.harappa_pool()
    cm, nm = frequencies(md)
    ch, nh = frequencies(pool)
    vocab = set(cm) | set(ch)
    v = len(vocab)

    def ratio(s):
        return math.log((cm[s] + 0.5) / (nm + 0.5 * v)) - math.log((ch[s] + 0.5) / (nh + 0.5 * v))

    objects, _ = P.prepare(P.read_rows(CONFIRMATION), "confirmation")
    rows = S.all_legends(objects)
    record = {"status": "exploratory, computed after the frozen read",
              "mohenjo_daro_seal_faces": len(md), "harappa_pool_families": len(pool)}
    for name, pick in (("all_signs", lambda signs: signs), ("interior_signs", lambda signs: signs[1:-1])):
        units = []
        for r in rows:
            signs = [s for s in pick(r["signs"]) if s != "000"]
            if signs:
                units.append(dict(r, value=float(np.mean([ratio(s) for s in signs]))))
        res = S.permutation_test(units, S.pearson_factory([x["value"] for x in units]), 9999, 600 if name == "all_signs" else 601, "two-sided")
        record[name] = {"units": len(units), "r": res["observed"], "z": res["z"], "p_two_sided": res["p"],
                        "mean_score_by_third": [float(np.mean([x["value"] for x in units if P.third(x["u"]) == t])) for t in range(3)]}
    out_path.write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(P.jsonable(record), indent=1))


if __name__ == "__main__":
    main()
