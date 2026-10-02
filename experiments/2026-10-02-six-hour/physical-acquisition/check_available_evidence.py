"""Post-run diagnostic: acquire every available observation without a cost cap."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

from verify_run import check_state, check_certificate, walk_certificates
from verify_classification import check_uniqueness


def main():
    root = Path(__file__).resolve().parent
    output = root / "main-all-available-review.json"
    if output.exists():
        raise FileExistsError(output)
    source = root / "main/code_snapshot.py"
    spec = importlib.util.spec_from_file_location("available_evidence", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    worlds_path = root / "main/worlds.json"
    records, counts = [], Counter()
    lp = module.CertifiedLP()
    for world in json.loads(worlds_path.read_text()):
        if world["condition"] not in ("complete_exact", "incomplete", "valid_intervals"):
            continue
        available = [a for a in world["public_actions"] if a["available"]]
        observations = list(world["initial_observations"]) + [world["oracle_responses"][a["id"]] for a in available]
        state, _ = module.analyze(lp, observations)
        check_state(state, observations)
        check_uniqueness(state, observations)
        for certificate in walk_certificates(state):
            check_certificate(certificate)
        counts[(world["condition"], state["classification"])] += 1
        actual = json.loads((root / "main" / f"{world['condition']}-{world['seed']}-information_rank.json").read_text())
        records.append({"condition": world["condition"], "seed": world["seed"],
                        "all_available_cost": sum(a["cost"] for a in available),
                        "available_counts": sum(a["kind"] == "count" for a in available),
                        "actual_budget_classification": actual["final_state"]["classification"],
                        "all_available_state": state})
    result = {"status": "post-run-all-available-diagnostic", "worlds": len(records),
              "scope": "All available responses opened after the frozen acquisition run, with no budget cap. This is a collection-limit diagnostic, not a selection policy or a result at budget 24.",
              "summary": [{"condition": condition, "classification": classification, "worlds": count} for (condition, classification), count in sorted(counts.items())],
              "records": records, "worlds_sha256": sha256(worlds_path.read_bytes()).hexdigest(),
              "analysis_source_sha256": sha256(source.read_bytes()).hexdigest(),
              "diagnostic_code_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
