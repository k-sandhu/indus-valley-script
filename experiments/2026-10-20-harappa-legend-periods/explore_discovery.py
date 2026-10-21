"""Discovery stage: Harappa seals with a period or stratum label outside Vats's Mound F.

Reads the discovery file and, for parameters that need no date, the legends of every
Harappa seal outside the confirmation population (discovery, undated and the held-out
Mound F seals without a stratum). The confirmation file is not read.

    python -P experiments/2026-10-20-harappa-legend-periods/explore_discovery.py OUT_DIR
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import period_stats as P  # noqa: E402
from period_stats import S  # noqa: E402
import build_inputs as B  # noqa: E402

ROOT = PACKAGE.parents[1]
DISCOVERY = ROOT / "data/raw/2026-10-20-harappa-legend-periods/discovery-harappa-labelled.jsonl"
DKG = ROOT / "experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2/frozen-parameters.json"
DRAWS = 9999


def harappa_pool():
    """Every Harappa seal family outside the confirmation population, one legend each,
    without dates. Used for the closing-stock definition and the power simulation."""
    faces = P.read_rows(B.FACES)
    fam = defaultdict(list)
    for f in faces:
        if f["site"] == "Harappa" and f["object_type"].startswith("SEAL"):
            fam[f["object_family_id"]].append(f)
    pool = []
    for k, members in fam.items():
        face = B.legend_face(members)
        chron = B.chronology(face)
        if chron["chron_mound"] == "F" and chron["chron_source"] == "vats_stratum":
            continue
        row = dict(face)
        row["metadata"] = dict(face["metadata"], **chron)
        row["text"] = P.edge_text_fields(face)
        pool.append(row)
    return pool


def closing_stock(rows, min_final=5, min_share=0.5):
    """Signs closing at least min_final legends with at least min_share of their
    occurrences (in legends whose closing is read) in final position."""
    occ, fin = Counter(), Counter()
    for r in rows:
        t = r["text"]
        if t["closing"] is None or (t["length"] is not None and t["length"] < 2):
            continue
        for s in t["signs"]:
            if s != "000":
                occ[s] += 1
        fin[t["closing"]] += 1
    stock = [s for s in fin if fin[s] >= min_final and fin[s] / occ[s] >= min_share]
    return sorted(stock, key=lambda s: (-fin[s], s)), {s: {"final": fin[s], "occurrences": occ[s]} for s in stock}, fin


def share(rows, members):
    vals = [r["text"]["closing"] in members for r in rows
            if r["text"]["closing"] is not None and not (r["text"]["length"] is not None and r["text"]["length"] < 2)]
    return {"legends": len(vals), "share": float(np.mean(vals)) if vals else None}


def by_third(units, fn):
    out = []
    for t in range(3):
        sel = [r for r in units if P.third(r["u"]) == t]
        out.append({"third": t, "units": len(sel), "value": fn(sel) if sel else None})
    return out


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=False)
    rows = P.read_rows(DISCOVERY)
    objects, frames = P.prepare(rows, "discovery")
    pool = harappa_pool()
    dkg = json.loads(DKG.read_text(encoding="utf-8"))
    record = {"population": {"discovery_families": len(rows), "in_frames": len(objects), "frames": frames,
                             "pool_families": len(pool),
                             "pool_by_source": dict(Counter(str(r["metadata"]["chron_source"]) for r in pool)),
                             "periods_by_frame": {f: dict(Counter(o["metadata"]["chron_period_label"] or f"stratum {o['metadata']['chron_stratum']}" for o in objects if o["stratum"] == f)) for f in frames}}}

    # closing stock: Mohenjo-daro DK-G stock against Harappa legends, and a Harappa stock
    stock_h, counts_h, finals = closing_stock(pool)
    dk = set(dkg["closing_stock"])
    record["closing"] = {
        "dkg_stock": dkg["closing_stock"],
        "dkg_stock_share_pool": share(pool, dk),
        "dkg_stock_share_discovery": share(objects, dk),
        "dkg_stock_share_pool_by_type": {t: share([r for r in pool if r["object_type"] == t], dk) for t in ("SEAL:S", "SEAL:R")},
        "harappa_stock_rule": "signs closing at least 5 pool legends with at least half their occurrences final",
        "harappa_stock": stock_h, "harappa_stock_counts": counts_h,
        "harappa_stock_share_pool": share(pool, set(stock_h)),
        "union_share_pool": share(pool, dk | set(stock_h)),
        "top_pool_closings": dict(finals.most_common(25)),
        "sign_740_share_pool": share(pool, {"740"}),
    }
    pairs = Counter(r["text"]["closing_pair"] for r in pool if r["text"]["closing_pair"])
    record["closing"]["pool_closing_pairs_top"] = dict(pairs.most_common(20))
    record["closing"]["dkg_formulae_share_pool"] = float(np.mean([r["text"]["closing_pair"] in set(dkg["closing_formulae"]) for r in pool if r["text"]["closing_pair"]]))

    # usable legends
    record["usable"] = {name: {"pool": sum(r["text"][f] is not None for r in pool),
                               "discovery": sum(o["text"][f] is not None for o in objects)}
                        for name, f in (("closing", "closing"), ("opening", "opening"), ("length", "length"), ("closing_pair", "closing_pair"))}
    record["usable"]["complete_ordered_closing_pool"] = sum(r["text"]["ordered"] and r["text"]["closing"] is not None for r in pool)

    # discovery trends, permutations within frames
    close = P.position_units(objects, "closing")
    opening = P.position_units(objects, "opening")
    legends = P.length_units(objects)
    trends = {}
    for name, members in (("dkg_stock", dk), ("harappa_stock", set(stock_h)), ("sign_740", {"740"})):
        ind = np.array([r["value"] in members for r in close], float)
        trends[f"{name}_share_by_third"] = by_third([dict(r, flag=f) for r, f in zip(close, ind)], lambda sel: float(np.mean([x["flag"] for x in sel])))
        trends[f"{name}_late_minus_early"] = S.permutation_test(close, S.share_difference_factory(ind), DRAWS, 3, alternative="two-sided")
    for m in (3, 5):
        codes, names = S.category_codes(opening, m)
        trends[f"opening_min{m}"] = dict(S.permutation_test(opening, S.between_ratio_factory(codes), DRAWS, 4 + m), categories=len(names))
        codes, names = S.category_codes(close, m)
        trends[f"closing_min{m}"] = dict(S.permutation_test(close, S.between_ratio_factory(codes), DRAWS, 14 + m), categories=len(names))
    trends["length"] = S.permutation_test(legends, S.stratified_spearman_factory([r["value"] for r in legends], legends), DRAWS, 7, alternative="two-sided")
    trends["mean_length_by_third"] = by_third(legends, lambda sel: float(np.mean([x["value"] for x in sel])))
    inv, keep = P.inventory_factory(legends)
    trends["inventory"] = dict(S.permutation_test(legends, inv, DRAWS, 8), signs=len(keep))
    variants = S.variant_tokens([{"stratum": r["stratum"], "u": r["u"], "object_family_id": r["families"][0],
                                  "text": {"signs": r["signs"]}} for r in S.all_legends(objects)], S.load_variant_classes())
    vstat, used = S.variant_statistic_factory(variants)
    trends["variants"] = dict(S.permutation_test(variants, vstat, DRAWS, 9), classes=used)
    rect = P.indicator_units(objects, lambda o: o["object_type"] == "SEAL:R")
    trends["rectangular_by_third"] = by_third(rect, lambda sel: float(np.mean([x["value"] for x in sel])))
    trends["rectangular"] = S.permutation_test(rect, S.pearson_factory([r["value"] for r in rect]), DRAWS, 10)
    script_only = P.indicator_units(objects, lambda o: o["symbol"] == "None")
    trends["script_only_by_third"] = by_third(script_only, lambda sel: float(np.mean([x["value"] for x in sel])))
    trends["script_only"] = S.permutation_test(script_only, S.pearson_factory([r["value"] for r in script_only]), DRAWS, 11)
    trends["units"] = {"closing": len(close), "opening": len(opening), "length": len(legends), "variant_rows": len(variants), "seals": len(objects)}
    record["discovery_trends"] = trends

    # per frame: rectangular seals and stock share by early and late half of the frame
    per_frame = {}
    for f in frames:
        sel = [o for o in objects if o["stratum"] == f]
        if not sel:
            continue
        early = [o for o in sel if o["u"] < 0.5]
        late = [o for o in sel if o["u"] >= 0.5]
        per_frame[f] = {"seals": len(sel),
                        "rect_early_late": [sum(o["object_type"] == "SEAL:R" for o in early), len(early), sum(o["object_type"] == "SEAL:R" for o in late), len(late)],
                        "dkg_stock_early_late": [share(early, dk), share(late, dk)]}
    record["per_frame"] = per_frame
    (out_dir / "exploration.json").write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    brief = {k: (v.get("observed"), v.get("z"), v.get("p")) if isinstance(v, dict) and "p" in v else v for k, v in trends.items()}
    print(json.dumps(P.jsonable({"population": record["population"], "closing": record["closing"], "usable": record["usable"], "trends": brief, "per_frame": per_frame}), indent=1))


if __name__ == "__main__":
    main()
