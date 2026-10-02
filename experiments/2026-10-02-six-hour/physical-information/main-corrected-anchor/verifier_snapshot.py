"""Review a preserved run using modular ranks and direct map enumeration."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import argparse
import json


def rank_modulo(matrix, prime):
    if not matrix:
        return 0
    rows = [[int(x) % prime for x in row] for row in matrix]
    cursor = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(cursor, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[cursor], rows[pivot] = rows[pivot], rows[cursor]
        inverse = pow(rows[cursor][column], -1, prime)
        rows[cursor] = [x * inverse % prime for x in rows[cursor]]
        for i in range(cursor + 1, len(rows)):
            factor = rows[i][column]
            rows[i] = [(x - factor * y) % prime for x, y in zip(rows[i], rows[cursor])]
        cursor += 1
        if cursor == len(rows):
            break
    return cursor


def dot(row, values):
    return sum(a * v for a, v in zip(row, values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result_path, world_path = args.run / "results.json", args.run / "worlds.json"
    result = json.loads(result_path.read_text())
    worlds = {w["seed"]: w for w in json.loads(world_path.read_text())}
    assert sha256((args.run / "code_snapshot.py").read_bytes()).hexdigest() == result["code_sha256"]
    assert sha256((args.run / "protocol_snapshot.md").read_bytes()).hexdigest() == result["protocol_sha256"]
    if "correction_sha256" in result:
        assert sha256((args.run / "correction_snapshot.md").read_bytes()).hexdigest() == result["correction_sha256"]
    maps = list(permutations(result["concealed_semantic_values"]))
    assert len(maps) == 720
    reviewed = 0
    for record in result["records"]:
        equations, inequalities, withheld = (
            record["training_equality_matrix"],
            record["training_inequality_matrix"],
            record["withheld_equality_matrix"],
        )
        rational, finite = record["rational"], record["finite"]
        for prime in (1000003, 1000033):
            assert rank_modulo(equations, prime) == rational["rank"]
        assert all(all(dot(row, [Fraction(x) for x in vector]) == 0 for row in equations)
                   for vector in rational["rational_nullspace_basis"])
        truth = worlds[record["seed"]]["concealed_values_by_code"]
        world = worlds[record["seed"]]
        measurements = world.get("independent_measurements", {}).get(record["scenario"])
        measured_values = measurements["values_by_code"] if measurements else truth
        candidates = [mapping for mapping in maps
                      if all(dot(row, mapping) == 0 for row in equations)
                      and all(dot(row, mapping) >= 0 for row in inequalities)]
        assert len(candidates) == finite["training_compatible_maps"]
        assert (tuple(truth) in candidates) == finite["true_map_survives"]
        assert sum(all(dot(row, mapping) == 0 for row in withheld) for mapping in candidates) == finite["maps_also_compatible_with_all_withheld_relations"]
        if candidates:
            exact_expectations = []
            actual_counts = []
            for code in range(6):
                counts = Counter(mapping[code] for mapping in candidates)
                exact_expectations.append(Fraction(sum(c * c for c in counts.values()), len(candidates)))
                actual_counts.append(counts[measured_values[code]])
            exact_choice = min(range(6), key=lambda j: (exact_expectations[j], j))
            assert exact_choice == finite["active_measurement"]["code_selected_before_count"]
            assert actual_counts == finite["candidate_counts_after_actual_measurement_by_code"]
        anchored = rational["anchor"]["unique_values"]
        if anchored:
            vector = [Fraction(x) for x in anchored]
            assert all(dot(row, vector) == 0 for row in equations)
            assert vector[rational["anchor"]["code"]] == rational["anchor"]["measured_count"]
        reviewed += 1
    for world in worlds.values():
        observed_counts = Counter(obj["code"] for obj in world["objects"])
        assert len(set(observed_counts.values())) == 1
        assert Counter(world["ownership_label_by_object"].values()) == observed_counts
        objects = {obj["id"]: obj for obj in world["objects"]}
        for scenario, measurements in world.get("independent_measurements", {}).items():
            for code, identifier in enumerate(measurements["object_ids_by_code"]):
                obj = objects[identifier]
                observed_label = world["ownership_label_by_object"][identifier] if scenario == "ownership_labels" else obj["code"]
                assert observed_label == code
                assert measurements["values_by_code"][code] == world["concealed_values_by_code"][obj["code"]]
        seen = set()
        for relation in world["complete_membership"]:
            identifiers = [relation["parent_object"]] + relation["child_objects"]
            assert not seen.intersection(identifiers)
            seen.update(identifiers)
    report = {
        "status": "passed",
        "records_reviewed": reviewed,
        "worlds_reviewed": len(worlds),
        "checks": ["snapshot hashes", "rank over two prime fields", "exact nullspace residuals", "independent direct enumeration of 720 maps", "withheld map counts", "active measurement selected with exact fractions", "anchor residuals", "balanced quantity and ownership labels", "disjoint physical object IDs", "actual measured object and its observed label where object measurements are recorded"],
        "results_sha256": sha256(result_path.read_bytes()).hexdigest(),
        "worlds_sha256": sha256(world_path.read_bytes()).hexdigest(),
        "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
