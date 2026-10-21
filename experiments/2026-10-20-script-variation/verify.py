"""Separate arithmetic implementation; no import of the fitted scorer."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / "data/raw/2026-10-20-script-variation"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = {}
    rnd = read(HERE / "round.json")
    frozen = rnd["shots"]["variant-choice"]["frozen"]
    checks["frozen_artifacts_unchanged"] = all(sha(Path(p)) == h for p, h in frozen["artifacts"].items())
    checks["predictions_unchanged"] = sha(HERE / "PREDICTIONS.json") == frozen["predictions_sha256"]
    events = rows(HERE / "round.access.jsonl")
    checks["one_confirmation_read"] = sum(e["half"] == "confirmation" and e["allowed"] for e in events) == 1
    checks["exposure_disclosed"] = all(not e.get("fresh_claim_allowed", False) for e in events if e["half"] == "confirmation")
    tr = rows(LOCAL / "discovery-v1/component-observations.jsonl")
    te = rows(LOCAL / "run-v1/component-observations.jsonl")
    checks["discovery_components_unique"] = len(tr) == len({r["component"] for r in tr})
    checks["confirmation_components_unique"] = len(te) == len({r["component"] for r in te})
    checks["components_do_not_cross_halves"] = not ({r["component"] for r in te} & {r["component"] for r in tr})
    checks["families_do_not_cross_halves"] = not ({r["family"] for r in te} & {r["family"] for r in tr})
    per_class = defaultdict(Counter)
    for r in tr:
        per_class[r["class"]][r["code"]] += 1
    eligible = {cl for cl, cs in per_class.items() if len([n for n in cs.values() if n >= 3]) >= 2}
    tr = [r for r in tr if r["class"] in eligible]
    te = [r for r in te if r["class"] in eligible]
    details = rows(LOCAL / "run-v1/primary-details.jsonl")
    checks["scored_population"] = len(te) == len(details) == 306 and len(eligible) == 9

    # The count filters below independently reconstruct every conditional distribution.
    def prob(target, local=False):
        same_class = [r for r in tr if r["class"] == target["class"]]
        p = (sum(r["code"] == target["code"] for r in same_class) + 1) / (len(same_class) + len(target["candidate_codes"]))
        conditions = []
        if local:
            conditions.append(["site"])
        conditions.append(["carrier", "material", "motif", "preservation", "volume"] + (["site"] if local else []))
        conditions.append(["carrier", "material", "motif", "preservation", "volume", "length", "position", "previous", "next"] + (["site"] if local else []))
        for fields in conditions:
            rr = [r for r in same_class if all(r[f] == target[f] for f in fields)]
            p = (sum(r["code"] == target["code"] for r in rr) + 20 * p) / (len(rr) + 20)
        return p

    independently_computed = []
    max_error = 0
    for target, recorded in zip(te, details):
        assert target["record"] == recorded["record"] and target["position"] == recorded["position"]
        a, b = prob(target, True), prob(target, False)
        max_error = max(max_error, abs(a - recorded["p_added"]), abs(b - recorded["p_baseline"]))
        independently_computed.append(math.log2(a / b))
    checks["all_probabilities_agree"] = max_error < 1e-14
    summary = read(HERE / "run-v1/summary.json")
    primary = summary["variant_prediction"]["primary"]
    checks["primary_mean_agrees"] = abs(sum(independently_computed) / len(te) - primary["mean_gain_bits"]) < 1e-14
    rng = np.random.default_rng(2671020)
    arr = np.array(independently_computed)
    samples = [float(arr[rng.integers(0, len(arr), size=len(arr))].mean()) for _ in range(4999)]
    interval = [float(x) for x in np.quantile(samples, [0.025, 0.975])]
    checks["primary_interval_agrees"] = max(abs(a - b) for a, b in zip(interval, primary["component_bootstrap_95_interval"])) < 1e-13
    checks["prediction_did_not_pass"] = primary["passes_primary_rule"] is False
    for mode, field in (("fine", "fine_frame"), ("graphic", "graphic_frame")):
        groups = defaultdict(list)
        for r in rows(LOCAL / "run-v1/component-observations.jsonl"):
            key = tuple(r[field]) + tuple(r[k] for k in ["position", "carrier", "motif", "preservation", "volume"])
            groups[key].append(r)
        count = sum(len({r["site"] for r in rs}) > 1 and len({r["code"] for r in rs}) > 1 for rs in groups.values())
        checks[f"{mode}_frames_recount"] = count == summary["exact_frames"][mode]["informative_cells"] == 0
    coverage = read(HERE / "source-v1/coverage.json")
    sr = rows(LOCAL / "source-v1/objects.jsonl")
    checks["source_locator_counts"] = sum(bool(r["cisi_sources"]) for r in sr) == coverage["objects_with_cisi_table_locator"] == 2602
    checks["source_qualification_count"] = sum(r["qualified_cisi"] for r in sr) == coverage["objects_with_unbracketed_excavation_source"] == 1897
    checks["source_artifact_hash"] = sha(LOCAL / "source-v1/objects.jsonl") == coverage["local_objects_sha256"]
    result = {"verification_tier": "submitted", "independent_contributor": False,
              "description": "Separately written arithmetic and identity checks by the study author; no scorer import.",
              "checks": checks, "pass": all(checks.values()), "maximum_probability_difference": max_error,
              "recomputed_primary_interval": interval, "verification_code_sha256": sha(Path(__file__))}
    out = HERE / "verification-v1.json"
    with out.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(result, indent=2))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
