"""Exhibit two positive rational assignments for every retained relative ambiguity."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json

from verify_run import independent_model, dot


def valid(vector, eq, rhs, ub, limits):
    return (all(v > 0 for v in vector)
            and all(dot(row, vector) == F(b) for row, b in zip(eq, rhs))
            and all(dot(row, vector) <= F(b) for row, b in zip(ub, limits)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    worlds = {(w["condition"], w["seed"]): w for w in json.loads((args.run / "worlds.json").read_text())}
    records = []
    for path in sorted(args.run.glob("*.json")):
        if not any(path.name.endswith("-" + p + ".json") for p in ("information_rank", "random", "cost_availability", "information_overlap")):
            continue
        record = json.loads(path.read_text())
        state = record["final_state"]
        if state["classification"] != "positive_ambiguity":
            continue
        world = worlds[(record["condition"], record["seed"])]
        observations = list(world["initial_observations"]) + [t["response_after_selection"] for t in record["trace"]]
        eq, rhs, ub, limits = independent_model(observations)
        first = [F(v) for v in state["positive_point"]]
        assert valid(first, eq, rhs, ub, limits)
        normalized = [v / sum(first) for v in first]
        second = None
        sources = list(state["range_certificates"]) + list(state.get("relative_tests", []))
        for source in sources:
            for side in ("lower", "upper"):
                certificate = source[side]
                other = [F(v) for v in certificate["primal"]]
                if len(certificate["ub"]) == len(ub) + 1 and all(F(v) == 0 for v in certificate["rhs"]):
                    candidate = [a + b for a, b in zip(first, other)]
                else:
                    candidate = [(a + b) / 2 for a, b in zip(first, other)]
                if valid(candidate, eq, rhs, ub, limits) and [v / sum(candidate) for v in candidate] != normalized:
                    second = candidate
                    break
            if second is not None:
                break
        assert second is not None, path.name
        records.append({"record": path.name, "record_sha256": sha256(path.read_bytes()).hexdigest(),
                        "condition": record["condition"], "policy": record["policy"], "seed": record["seed"],
                        "first_positive_vector": [str(v) for v in first],
                        "second_positive_vector": [str(v) for v in second],
                        "first_ratios": [str(v / sum(first)) for v in first],
                        "second_ratios": [str(v / sum(second)) for v in second],
                        "equalities": eq, "right_hand_sides": rhs, "inequalities": ub, "upper_limits": limits,
                        "all_acquired_constraints_satisfied_exactly": True,
                        "relative_assignments_differ": True})
    report = {"status": "positive-rational-ambiguity-certified", "run": args.run.as_posix(),
              "retained_relative_ambiguities": len(records), "records": records,
              "code_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "retained_relative_ambiguities": len(records)}, indent=2))


if __name__ == "__main__":
    main()
