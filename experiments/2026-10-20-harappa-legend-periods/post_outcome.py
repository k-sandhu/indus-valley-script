"""Post-outcome description of the Mound F result (exploratory, written after the read).

The frozen read found drift in variant choice, legend length and sign inventory, with
the closing stock, the closing signs and the opening signs unchanged, and rectangular
seals rising. This script asks where the drift sits:

1. whether it survives when seal format is held fixed (permutations within trench and
   format, and square seals alone);
2. which signs and which variant classes carry the inventory and variant statistics;
3. whether the added length sits inside the legend, between an opening and a closing
   that do not change.

It reads the confirmation file directly; the population was opened by the frozen read.

    python -P experiments/2026-10-20-harappa-legend-periods/post_outcome.py OUT_DIR
"""
from collections import Counter, defaultdict
import copy
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import period_stats as P  # noqa: E402
from period_stats import S  # noqa: E402
import period_score as Q  # noqa: E402

ROOT = PACKAGE.parents[1]
CONFIRMATION = ROOT / "data/raw/2026-10-20-harappa-legend-periods/confirmation-mound-f-vats.jsonl"
FROZEN = PACKAGE / "discovery-v2/frozen-parameters.json"
DRAWS = 9999


def drift_tests(objects, frozen, seed, keys=("P4", "P5", "P6")):
    res = Q.score_predictions(objects, frozen, draws=DRAWS, boot=1999, seed=seed, influence=False, only=set(keys))
    return {k: {"observed": v.get("observed"), "z": v.get("z"), "p": v.get("p"), "units": v.get("units"), "outcome": v.get("outcome")}
            for k, v in res.items()}


def by_third(rows, fn):
    out = []
    for t in range(3):
        sel = [r for r in rows if P.third(r["u"]) == t]
        out.append({"third": t, "units": len(sel), "value": fn(sel) if sel else None})
    return out


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=False)
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    objects, frames = P.prepare(P.read_rows(CONFIRMATION), "confirmation")
    record = {"status": "exploratory, computed after the frozen read", "seals": len(objects)}

    # 1. format held fixed
    fmt = copy.deepcopy(objects)
    for o in fmt:
        o["stratum"] = f"{o['stratum']}|{'R' if o['object_type'] == 'SEAL:R' else 'S'}"
    record["within_trench_and_format"] = drift_tests(fmt, frozen, 101)
    square = [copy.deepcopy(o) for o in objects if o["object_type"] != "SEAL:R"]
    record["square_seals_only"] = dict(drift_tests(square, frozen, 102), seals=len(square))
    rect = [copy.deepcopy(o) for o in objects if o["object_type"] == "SEAL:R"]
    record["rectangular_seals_only"] = dict(drift_tests(rect, frozen, 103), seals=len(rect))

    legends = P.length_units(objects)
    record["length_by_third_and_format"] = {
        name: by_third([r for r in legends if (r["object_type"] == "SEAL:R") == (name == "rectangular")],
                       lambda sel: float(np.mean([x["value"] for x in sel])))
        for name in ("square", "rectangular")}
    record["length_by_third"] = by_third(legends, lambda sel: float(np.mean([x["value"] for x in sel])))
    record["length_distribution_by_third"] = by_third(legends, lambda sel: dict(sorted(Counter(x["value"] for x in sel).items())))

    # 2. inventory: per-sign contributions on all legends
    rows = S.all_legends(objects)
    u = np.array([r["u"] for r in rows])
    counts = Counter(s for r in rows for s in set(r["signs"]) - {"000"})
    contrib = []
    for s, n in counts.items():
        if n < frozen["inventory_min_units"]:
            continue
        mask = np.array([s in set(r["signs"]) for r in rows])
        mu = u[mask].mean()
        thirds = Counter(P.third(x) for x in u[mask])
        contrib.append({"sign": s, "legends": int(n), "mean_u": float(mu),
                        "contribution": float(n * (mu - u.mean()) ** 2 / u.var()),
                        "early_middle_late": [thirds[0], thirds[1], thirds[2]]})
    record["inventory_contributions"] = sorted(contrib, key=lambda x: -x["contribution"])
    record["legends_by_third"] = [int(np.sum([P.third(x) == t for x in u])) for t in range(3)]

    # 3. variant classes: per-class statistic and code counts by third
    variants = S.variant_tokens([{"stratum": r["stratum"], "u": r["u"], "object_family_id": r["families"][0],
                                  "text": {"signs": r["signs"]}} for r in rows], S.load_variant_classes())
    _, used = S.variant_statistic_factory(variants)
    per_class = []
    for item in used:
        sub = [r for r in variants if r["class"] == item["class"] and r["value"] in item["codes"]]
        codes = sorted(item["codes"])
        lookup = {c: i for i, c in enumerate(codes)}
        code_index = np.array([lookup[r["value"]] for r in sub])
        uu = np.array([r["u"] for r in sub])
        stat = S.between_ratio_factory(code_index)(uu) - (len(codes) - 1)
        table = {c: [sum(1 for r in sub if r["value"] == c and P.third(r["u"]) == t) for t in range(3)] for c in codes}
        mean_u = {c: float(np.mean([r["u"] for r in sub if r["value"] == c])) for c in codes}
        test = S.permutation_test(sub, lambda v, ci=code_index, k=len(codes): S.between_ratio_factory(ci)(v) - (k - 1), DRAWS, 200 + len(per_class))
        per_class.append({"class": item["class"], "rows": len(sub), "statistic": float(stat), "p_within_trench": test["p"],
                          "codes_early_middle_late": table, "mean_u": mean_u})
    record["variant_classes"] = per_class

    # 4. where the added length sits
    complete = [r for r in legends if r["text"]["ordered"] and r["value"] >= 2]
    record["interior_signs_by_third"] = by_third(complete, lambda sel: float(np.mean([x["value"] - 2 for x in sel])))
    record["openings_and_closings_of_complete_legends_by_third"] = by_third(
        complete, lambda sel: {"stock_closing_share": float(np.mean([x["signs"][-1] in set(frozen["closing_stock"]) for x in sel])),
                               "top_openings": dict(Counter(x["signs"][0] for x in sel).most_common(5))})
    pairs = P.position_units(objects, "closing_pair")
    record["closing_pairs_by_third"] = by_third(pairs, lambda sel: dict(Counter(x["value"] for x in sel).most_common(8)))

    (out_dir / "summary.json").write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(P.jsonable({k: record[k] for k in ("within_trench_and_format", "square_seals_only", "rectangular_seals_only",
                                                        "length_by_third_and_format", "interior_signs_by_third")}), indent=1))
    print(json.dumps(P.jsonable(record["inventory_contributions"][:12]), indent=0))
    print(json.dumps(P.jsonable(record["variant_classes"]), indent=0))


if __name__ == "__main__":
    main()
