"""Discovery stage: Mackay 1938 seals from the DK area, levels against the DK datum.

Writes the exploration record and the frozen parameters derived from Mackay's seals.
Marshall's rows are not read here.

    python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/explore_mackay.py OUT_DIR
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import strat_stats as S  # noqa: E402
import score  # noqa: E402

ROOT = PACKAGE.parents[1]
DISCOVERY = ROOT / "data/raw/2026-10-20-mohenjo-daro-stratigraphy/discovery-mackay1938.jsonl"
DRAWS = 9999


def third(u):
    return 0 if u < 1 / 3 else (1 if u < 2 / 3 else 2)


def closing_stock(units, min_final=5, min_share=0.5):
    occ, fin = Counter(), Counter()
    for r in units:
        for s in r["signs"]:
            occ[s] += 1
        fin[r["value"]] += 1
    stock = [s for s in fin if fin[s] >= min_final and fin[s] / occ[s] >= min_share]
    return sorted(stock, key=lambda s: (-fin[s], s)), {s: {"final": fin[s], "occurrences": occ[s]} for s in stock}


def nonfinal_scores(units, k=10, min_units=3):
    """Shrunken mean height of each sign over legends where it stands before the last
    position: (sum of u + k * 0.5) / (n + k), for signs in at least min_units legends."""
    acc = defaultdict(list)
    for r in units:
        for s in set(r["signs"][:-1]):
            if s != "000":
                acc[s].append(r["u"])
    return {s: (sum(v) + k * 0.5) / (len(v) + k) for s, v in sorted(acc.items()) if len(v) >= min_units}


def split_half(units, kind, rng, rounds=200):
    """Per-sign mean heights in two random halves of units: correlation across signs with
    at least four units in both halves, and transfer of one half's shrunken scores to the
    other half's heights."""
    def means(rows):
        acc = defaultdict(list)
        for r in rows:
            keys = {s for s in r["signs"] if s != "000"} if kind == "any" else {r["value"]}
            for s in keys:
                acc[s].append(r["u"])
        return {s: (np.mean(v), len(v), (sum(v) + 5) / (len(v) + 10)) for s, v in acc.items()}
    rel, transfer = [], []
    for _ in range(rounds):
        idx = rng.permutation(len(units))
        a = [units[i] for i in idx[: len(units) // 2]]
        b = [units[i] for i in idx[len(units) // 2:]]
        ma, mb = means(a), means(b)
        common = [s for s in ma if s in mb and ma[s][1] >= 4 and mb[s][1] >= 4]
        if len(common) > 5:
            rel.append(np.corrcoef([ma[s][0] for s in common], [mb[s][0] for s in common])[0, 1])
        pairs = []
        for r in b:
            keys = {s for s in r["signs"] if s != "000"} if kind == "any" else {r["value"]}
            v = [ma[s][2] for s in keys if s in ma]
            if v:
                pairs.append((np.mean(v), r["u"]))
        x, y = np.array(pairs).T
        transfer.append(np.corrcoef(x, y)[0, 1])
    rel, transfer = np.array(rel), np.array(transfer)
    return {"per_sign_split_half_r": float(rel.mean()), "spearman_brown": float(2 * rel.mean() / (1 + rel.mean())),
            "transfer_r_mean": float(transfer.mean()), "transfer_r_sd": float(transfer.std()),
            "transfer_share_positive": float((transfer > 0).mean()), "rounds": rounds}


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=False)
    rows = [json.loads(line) for line in DISCOVERY.read_text(encoding="utf-8").splitlines() if line.strip()]
    objects, sizes = score.prepare(rows, areas={"DK"})
    record = {"population": {"seals_with_level": len(objects), "strata": sizes,
                             "level_range_ft": [min(o["metadata"]["strat_height_ft"] for o in objects),
                                                max(o["metadata"]["strat_height_ft"] for o in objects)],
                             "third_cuts_ft": [float(np.quantile([o["metadata"]["strat_height_ft"] for o in objects], q)) for q in (1 / 3, 2 / 3)],
                             "below_minus_18_ft": sum(o["metadata"]["strat_height_ft"] < -18 for o in objects),
                             "below_minus_24_ft": sum(o["metadata"]["strat_height_ft"] < -24 for o in objects)}}

    # frozen parameters
    close = S.units(objects, "closing")
    stock, stock_counts = closing_stock(close)
    pairs = S.units(objects, "closing_pair")
    pair_counts = Counter(r["value"] for r in pairs)
    formulae = sorted(p for p, n in pair_counts.items() if n >= 4)
    nonfinal = nonfinal_scores(S.units(objects, "length", min_length=2))
    frozen = {"closing_stock": stock, "closing_stock_counts": stock_counts,
              "closing_formulae": formulae, "closing_formula_counts": {p: pair_counts[p] for p in formulae},
              "nonfinal_scores": nonfinal,
              "rules": {"closing_stock": "signs closing at least 5 Mackay DK legends of two or more signs, with at least half of their occurrences in those legends in final position",
                        "closing_formulae": "final sign pairs closing at least 4 Mackay DK legends",
                        "nonfinal_scores": "shrunken mean height rank (k = 10 toward 0.5) of each sign over Mackay DK legends where it stands before the last position; signs in at least 3 legends"}}

    # exploration: slot association with height, several category thresholds
    slots = {}
    for field in ("opening", "closing", "closing_pair"):
        U = S.units(objects, field)
        slots[field] = {}
        for m in (3, 5, 8):
            codes, names = S.category_codes(U, m)
            slots[field][f"min_count_{m}"] = dict(S.permutation_test(U, S.between_ratio_factory(codes), DRAWS, 11 + m), categories=len(names))
    record["slot_height_association"] = slots

    # distributions by third
    by_third = {}
    for name, members in (("closing_stock", set(stock)), ("sign_740", {"740"})):
        c = Counter((third(r["u"]), r["value"] in members) for r in close)
        by_third[name] = [{"third": t, "units": c[(t, True)] + c[(t, False)], "share": c[(t, True)] / (c[(t, True)] + c[(t, False)])} for t in range(3)]
    c = Counter((third(r["u"]), r["value"] in set(formulae)) for r in pairs)
    by_third["closing_formulae"] = [{"third": t, "units": c[(t, True)] + c[(t, False)], "share": c[(t, True)] / (c[(t, True)] + c[(t, False)])} for t in range(3)]
    by_third["formula_760_740"] = dict(Counter(third(r["u"]) for r in pairs if r["value"] == "760-740"))
    by_third["formula_740_090"] = dict(Counter(third(r["u"]) for r in pairs if r["value"] == "740-090"))
    legends = S.units(objects, "length", min_length=1)
    by_third["mean_length"] = [float(np.mean([r["value"] for r in legends if third(r["u"]) == t])) for t in range(3)]
    by_third["rectangular_share"] = [float(np.mean([o["object_type"] == "SEAL:R" for o in objects if third(o["u"]) == t])) for t in range(3)]
    rng = np.random.default_rng(3)
    opening = S.units(objects, "opening")
    groups = [[r["value"] for r in opening if third(r["u"]) == t] for t in range(3)]
    n = min(len(g) for g in groups)
    by_third["opening_richness_rarefied"] = {"size": n, "values": [float(np.mean([len(set(rng.choice(g, n, replace=False))) for _ in range(500)])) for g in groups]}
    deep = [o for o in objects if o["metadata"]["strat_height_ft"] < -18 and o["text"]["closing"]]
    by_third["below_minus_18_ft_closings"] = dict(Counter(o["text"]["closing"] for o in deep).most_common(10))
    by_third["below_minus_18_ft_stock_share"] = float(np.mean([o["text"]["closing"] in set(stock) for o in deep]))
    record["by_third"] = by_third

    # per-sign mean heights (signs in at least 6 units) for the record
    per_sign = {}
    for field in ("opening", "closing"):
        acc = defaultdict(list)
        for r in S.units(objects, field):
            acc[r["value"]].append(r["u"])
        per_sign[field] = {s: {"units": len(v), "mean_u": float(np.mean(v))} for s, v in sorted(acc.items()) if len(v) >= 6}
    acc = defaultdict(list)
    for r in legends:
        for s in set(r["signs"]) - {"000"}:
            acc[s].append(r["u"])
    per_sign["any_position"] = {s: {"units": len(v), "mean_u": float(np.mean(v))} for s, v in sorted(acc.items()) if len(v) >= 8}
    record["per_sign_mean_height"] = per_sign

    # any-position sign inventory against height
    keep = [s for s, v in per_sign["any_position"].items()]
    M = np.array([[1.0 if s in set(r["signs"]) else 0.0 for s in keep] for r in legends])

    def inventory(u):
        n = M.sum(0)
        mu = (M * u[:, None]).sum(0) / n
        return float(np.sum(n * (mu - u.mean()) ** 2) / u.var())
    record["any_position_inventory"] = dict(S.permutation_test(legends, inventory, DRAWS, 21), signs=len(keep))

    # reliability and transfer within Mackay
    rng = np.random.default_rng(11)
    record["split_half"] = {"any_position": split_half(legends, "any", rng),
                            "opening": split_half(opening, "slot", rng),
                            "closing": split_half(close, "slot", rng)}

    # section ranking (DK-G north and south) as a sensitivity check
    sec_objects = S.add_height_rank([dict(o) for o in objects], stratum_key="strat_section")
    record["section_ranked"] = {}
    for field in ("opening", "closing"):
        U = S.units(sec_objects, field)
        codes, _ = S.category_codes(U, 5)
        record["section_ranked"][field] = S.permutation_test(U, S.between_ratio_factory(codes), DRAWS, 31)
    U = S.units(sec_objects, "length", min_length=1)
    record["section_ranked"]["length"] = S.permutation_test(U, S.stratified_spearman_factory([r["value"] for r in U], U), DRAWS, 32)
    S.add_height_rank(objects, stratum_key="strat_stratum")

    # rehearsal of the frozen scorer on Mackay itself; P8 cross-fitted on two halves
    rehearsal = score.score_predictions(objects, frozen, draws=DRAWS, boot=DRAWS, seed=7, influence=True)
    halves = np.random.default_rng(5).permutation(len(objects))
    a = [objects[i] for i in halves[: len(objects) // 2]]
    b = [objects[i] for i in halves[len(objects) // 2:]]
    cross = []
    for train, test in ((a, b), (b, a)):
        scores_train = nonfinal_scores(S.units(train, "length", min_length=2))
        res = score.score_predictions(test, dict(frozen, nonfinal_scores=scores_train), draws=1999, boot=999, seed=9, influence=False)
        cross.append({"r": res["P8"]["observed"], "p": res["P8"]["p"], "units": res["P8"]["units"]})
    rehearsal["P8_cross_fitted"] = cross
    record["rehearsal_in_sample"] = rehearsal

    (out_dir / "frozen-parameters.json").write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
    (out_dir / "exploration.json").write_text(json.dumps(S_json(record), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(S_json({k: record[k] for k in ("population", "by_third", "any_position_inventory", "split_half")}), indent=1))
    print(json.dumps(S_json({k: {kk: (vv.get("outcome"), vv.get("observed"), vv.get("p"), vv.get("interval90")) for kk, vv in rehearsal.items() if isinstance(vv, dict)} for k in ["r"]}), indent=1))


def S_json(value):
    if isinstance(value, dict):
        return {str(k): S_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [S_json(v) for v in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


if __name__ == "__main__":
    main()
