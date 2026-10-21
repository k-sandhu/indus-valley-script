"""Single confirmation read: Marshall 1931 seals, scored by the frozen predictions.

Both halves of this package's bench shots split hold confirmation material: the split
exists so that every read of the Marshall population passes the loader's freeze check
and is logged. The confirmation half is read first (the loader refuses it before the
freeze), then the discovery half; the two are pooled and scored once.

    python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/confirm.py OUT_DIR
"""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))
from bench import shots  # noqa: E402
import score  # noqa: E402
import strat_stats as S  # noqa: E402

SPLIT = PACKAGE / "shots/round.json"
LEDGER = PACKAGE / "shots/spent-ledger.json"
SHOT = "stratigraphy"
FROZEN = PACKAGE / "discovery-v2/frozen-parameters.json"
START_CREDENCE = 0.20
DRAWS = 9999
SEED = 20261020


def jsonable(value):
    import numpy as np
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.bool_):
        return bool(value)
    return value


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

    objects, strata = score.prepare(copy.deepcopy(rows))
    results = score.score_predictions(objects, frozen, draws=args.draws, boot=args.draws, seed=SEED, influence=True)
    decision = score.credence(results, START_CREDENCE)

    # Pre-declared sensitivity analyses; they do not change any outcome.
    sensitivity = {}
    area_objects = S.add_height_rank(copy.deepcopy(objects), stratum_key="strat_area")
    sensitivity["area_ranked"] = {k: {"outcome": v.get("outcome"), "observed": v.get("observed"), "p": v.get("p"),
                                      "interval90": v.get("interval90")}
                                  for k, v in score.score_predictions(area_objects, frozen, draws=1999, boot=1999,
                                                                      seed=SEED + 1, influence=False,
                                                                      only={"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"}).items()}
    for name, half in (("loader_confirmation_half", confirmation), ("loader_discovery_half", discovery)):
        members = {r["object_family_id"] for r in half}
        objs = S.add_height_rank(copy.deepcopy([o for o in objects if o["object_family_id"] in members]),
                                 stratum_key="strat_stratum")
        sensitivity[name] = {k: {"outcome": v.get("outcome"), "observed": v.get("observed"), "p": v.get("p"),
                                 "interval90": v.get("interval90")}
                             for k, v in score.score_predictions(objs, frozen, draws=1999, boot=1999, seed=SEED + 2,
                                                                 influence=False,
                                                                 only={"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"}).items()}

    record = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
              "access": [event_c, event_d],
              "population": {"rows_read": len(rows), "confirmation_half_rows": len(confirmation),
                             "discovery_half_rows": len(discovery), "seals_with_depth_in_strata": len(objects),
                             "strata": strata},
              "frozen_parameters": str(FROZEN.relative_to(ROOT)).replace("\\", "/"), "split": str(args.split), "draws": args.draws,
              "start_credence": START_CREDENCE, "results": results, "credence": decision,
              "sensitivity": sensitivity}
    (out_dir / "results.json").write_text(json.dumps(jsonable(record), indent=2) + "\n", encoding="utf-8")
    brief = {k: {"outcome": v.get("outcome"), "observed": v.get("observed"), "p": v.get("p"),
                 "interval90": v.get("interval90"), "bottom_share": v.get("bottom_share"), "holm_p": v.get("holm_p")}
             for k, v in results.items()}
    print(json.dumps(jsonable({"results": brief, "credence": decision, "population": record["population"]}), indent=1))


if __name__ == "__main__":
    main()
