"""Rehearsal of the frozen scorer on the discovery seals (in sample).

The discovery frames use their own clocks (Vats strata in Mounds AB, D, H and J, HARP
period labels in Mounds E and F), ranked within each frame, so the rehearsal checks the
code path and shows what the statistics give on the material that shaped them. It is
not evidence for the conjecture.

    python -P experiments/2026-10-20-harappa-legend-periods/rehearse_discovery.py OUT_DIR
"""
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import period_stats as P  # noqa: E402
import period_score as Q  # noqa: E402

ROOT = PACKAGE.parents[1]
DISCOVERY = ROOT / "data/raw/2026-10-20-harappa-legend-periods/discovery-harappa-labelled.jsonl"
FROZEN = PACKAGE / "discovery-v2/frozen-parameters.json"


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=False)
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    objects, frames = P.prepare(P.read_rows(DISCOVERY), "discovery")
    results = Q.score_predictions(objects, frozen, draws=9999, boot=9999, seed=7, influence=True)
    decision = Q.credence(results, frozen, 0.40)
    record = {"frames": frames, "seals": len(objects), "results": results, "credence_if_this_were_the_read": decision}
    (out_dir / "rehearsal.json").write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    brief = {k: {"outcome": v.get("outcome"), "observed": v.get("observed"), "p": v.get("p") or v.get("perm_p"),
                 "interval90": v.get("interval90"), "early_share": v.get("early_share"), "holm_p": v.get("holm_p"),
                 "units": v.get("units") or v.get("early_units")} for k, v in results.items()}
    print(json.dumps(P.jsonable({"frames": frames, "results": brief, "credence": decision}), indent=1))


if __name__ == "__main__":
    main()
