"""Single confirmation read: Vats's Mound F seals, scored by the frozen predictions.

Both halves of this package's bench shots split hold confirmation material: the split
exists so that every read of the Mound F population passes the loader's freeze check
and is logged. The confirmation half is read first (the loader refuses it before the
freeze), then the other half; the two are pooled and scored once.

    python -P experiments/2026-10-20-harappa-legend-periods/confirm.py OUT_DIR
"""
from collections import Counter
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
sys.path.insert(1, str(ROOT))
from bench import shots  # noqa: E402
import period_stats as P  # noqa: E402
from period_stats import S  # noqa: E402
import period_score as Q  # noqa: E402

SPLIT = PACKAGE / "shots/round.json"
LEDGER = PACKAGE / "shots/spent-ledger.json"
SHOT = "harappa-periods"
FROZEN = PACKAGE / "discovery-v2/frozen-parameters.json"
DKG = ROOT / "experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2/frozen-parameters.json"
START_CREDENCE = 0.40
DRAWS = 9999
SEED = 20261021
ALL = {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "PC"}


def brief(results):
    return {k: {"outcome": v.get("outcome"), "observed": v.get("observed"), "p": v.get("p", v.get("perm_p")),
                "interval90": v.get("interval90"), "early_share": v.get("early_share"),
                "late_share": v.get("late_share"), "units": v.get("units") or v.get("early_units")}
            for k, v in results.items()}


def depth_clock(objects):
    """Sensitivity clock: Vats's printed depth ranked within each frame (deeper is older).
    Seals without a parsed depth are dropped."""
    kept = [o for o in objects if o["metadata"]["chron_depth_ft"] is not None]
    groups = {}
    for o in kept:
        groups.setdefault(o["stratum"], []).append(o)
    for members in groups.values():
        ranks = S.average_ranks([-o["metadata"]["chron_depth_ft"] for o in members])
        for o, r in zip(members, ranks):
            o["u"] = (r - 0.5) / len(members)
    return kept


def describe(objects, frozen):
    """Descriptive table by third of the sequence, recorded with the frozen read."""
    stock = set(frozen["closing_stock"])
    closing = P.position_units(objects, "closing")
    opening = P.position_units(objects, "opening")
    legends = P.length_units(objects)
    out = []
    for t in range(3):
        c = [r for r in closing if P.third(r["u"]) == t]
        o = [r for r in opening if P.third(r["u"]) == t]
        lg = [r for r in legends if P.third(r["u"]) == t]
        seals = [x for x in objects if P.third(x["u"]) == t]
        out.append({"third": t,
                    "strata": sorted({x["metadata"]["chron_stratum"] for x in seals}, reverse=True),
                    "seals": len(seals),
                    "rectangular_share": float(np.mean([x["object_type"] == "SEAL:R" for x in seals])) if seals else None,
                    "closing_units": len(c),
                    "stock_share": float(np.mean([r["value"] in stock for r in c])) if c else None,
                    "sign_740_share": float(np.mean([r["value"] == "740" for r in c])) if c else None,
                    "closing_counts": dict(Counter(r["value"] for r in c).most_common(10)),
                    "opening_units": len(o),
                    "opening_counts": dict(Counter(r["value"] for r in o).most_common(10)),
                    "length_units": len(lg),
                    "mean_length": float(np.mean([r["value"] for r in lg])) if lg else None})
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--split", type=Path, default=SPLIT, help="dry runs only; the confirmation uses the default")
    ap.add_argument("--ledger", type=Path, default=LEDGER, help="dry runs only")
    ap.add_argument("--draws", type=int, default=DRAWS, help="dry runs only")
    args = ap.parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    confirmation, event_c = shots.load_half(args.split, "confirmation", SHOT, args.ledger)
    discovery, event_d = shots.load_half(args.split, "discovery", SHOT, args.ledger)
    rows = confirmation + discovery
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))

    objects, frames = P.prepare(copy.deepcopy(rows), "confirmation")
    results = Q.score_predictions(objects, frozen, draws=args.draws, boot=args.draws, seed=SEED, influence=True)
    decision = Q.credence(results, frozen, START_CREDENCE)

    # Pre-declared sensitivity analyses; none changes an outcome.
    small = min(args.draws, 1999)
    sensitivity = {}
    mound = copy.deepcopy(objects)
    for o in mound:
        o["stratum"] = "F"
    sensitivity["mound_wide_permutation"] = brief(Q.score_predictions(mound, frozen, draws=small, boot=small, seed=SEED + 1, influence=False))
    sensitivity["depth_within_frame"] = brief(Q.score_predictions(depth_clock(copy.deepcopy(objects)), frozen, draws=small, boot=small, seed=SEED + 2, influence=False))
    dkg = json.loads(DKG.read_text(encoding="utf-8"))
    sensitivity["dkg_stock_only"] = brief(Q.score_predictions(objects, dict(frozen, closing_stock=dkg["closing_stock"]), draws=small, boot=small, seed=SEED + 3, influence=False, only={"P1", "P2"}))
    strict = copy.deepcopy(objects)
    for o in strict:
        t = o["text"]
        if not t["ordered"] or not t["clean"]:
            t["opening"] = t["closing"] = t["closing_pair"] = None
    sensitivity["complete_legends_only"] = brief(Q.score_predictions(strict, frozen, draws=small, boot=small, seed=SEED + 4, influence=False, only={"P1", "P2", "P3", "P7"}))
    for name, half in (("loader_confirmation_half", confirmation), ("loader_discovery_half", discovery)):
        members = {r["object_family_id"] for r in half}
        sub = copy.deepcopy([o for o in objects if o["object_family_id"] in members])
        P.add_clock(sub, "mound")
        sensitivity[name] = brief(Q.score_predictions(sub, frozen, draws=small, boot=small, seed=SEED + 5, influence=False))

    record = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
              "access": [event_c, event_d],
              "population": {"rows_read": len(rows), "confirmation_half_rows": len(confirmation),
                             "discovery_half_rows": len(discovery), "seals_in_frames": len(objects), "frames": frames,
                             "strata": dict(sorted(Counter(o["metadata"]["chron_stratum"] for o in objects).items()))},
              "frozen_parameters": str(FROZEN.relative_to(ROOT)).replace("\\", "/"), "split": str(args.split),
              "draws": args.draws, "start_credence": START_CREDENCE, "results": results, "credence": decision,
              "by_third": describe(objects, frozen), "sensitivity": sensitivity}
    (out_dir / "results.json").write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(P.jsonable({"results": brief(results), "credence": decision, "population": record["population"]}), indent=1))


if __name__ == "__main__":
    main()
