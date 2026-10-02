"""Blind synthetic quantity inference from independently observed membership.

Run manually. The finite permutation assay and unrestricted rational assay are
reported separately. This program contains no Indus transcription or semantics.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement, permutations
from math import gcd, lcm, log2
from pathlib import Path
import json
import shutil

import numpy as np


VALUES = (1, 2, 3, 4, 6, 8)
N = len(VALUES)
PREFIXES = (0, 1, 2, 3, 5, 8, 12)
SCENARIOS = (
    "complete_membership",
    "scrambled_membership",
    "incomplete_assumed_complete",
    "incomplete_recorded",
    "ownership_labels",
)


def rref(matrix):
    """Exact reduced row-echelon form and a witness minor's original row IDs."""
    if not matrix:
        return [], [], []
    rows = [[Fraction(x) for x in row] for row in matrix]
    row_ids = list(range(len(rows)))
    columns = len(rows[0])
    if any(len(row) != columns for row in rows):
        raise ValueError("Ragged matrix")
    pivot_columns, pivot_row_ids = [], []
    cursor = 0
    for column in range(columns):
        target = next((i for i in range(cursor, len(rows)) if rows[i][column]), None)
        if target is None:
            continue
        rows[cursor], rows[target] = rows[target], rows[cursor]
        row_ids[cursor], row_ids[target] = row_ids[target], row_ids[cursor]
        pivot = rows[cursor][column]
        rows[cursor] = [x / pivot for x in rows[cursor]]
        for i in range(len(rows)):
            if i != cursor and rows[i][column]:
                multiple = rows[i][column]
                rows[i] = [x - multiple * y for x, y in zip(rows[i], rows[cursor])]
        pivot_columns.append(column)
        pivot_row_ids.append(row_ids[cursor])
        cursor += 1
        if cursor == len(rows):
            break
    return rows, pivot_columns, pivot_row_ids


def determinant_bareiss(matrix):
    """Independent integer determinant with fraction-free elimination."""
    if not matrix:
        return 1
    rows = [list(map(int, row)) for row in matrix]
    n = len(rows)
    assert all(len(row) == n for row in rows)
    sign, previous = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if rows[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            rows[k], rows[pivot_row] = rows[pivot_row], rows[k]
            sign *= -1
        pivot = rows[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = rows[i][j] * pivot - rows[i][k] * rows[k][j]
                assert numerator % previous == 0
                rows[i][j] = numerator // previous
            rows[i][k] = 0
        previous = pivot
    return sign * rows[-1][-1]


def rank_review(matrix):
    rows, pivots, witness_rows = rref(matrix)
    rank = len(pivots)
    minor = [[matrix[i][j] for j in pivots] for i in witness_rows]
    determinant = determinant_bareiss(minor)
    assert determinant != 0
    return rows, pivots, {
        "rank": rank,
        "witness_rows": witness_rows,
        "witness_columns": pivots,
        "witness_minor_determinant": determinant,
    }


def primitive_vector(vector):
    denominator = lcm(*(v.denominator for v in vector))
    integers = [int(v * denominator) for v in vector]
    divisor = gcd(*integers)
    if divisor:
        integers = [v // divisor for v in integers]
    nonzero = next((v for v in integers if v), 0)
    if nonzero < 0:
        integers = [-v for v in integers]
    return integers


def rational_summary(equalities, inequalities, heldout, truth, anchor_code, anchor_value):
    rows, pivots, review = rank_review(equalities)
    free = [j for j in range(N) if j not in pivots]
    basis = []
    for j in free:
        vector = [Fraction(0)] * N
        vector[j] = Fraction(1)
        for i, pivot in enumerate(pivots):
            vector[pivot] = -rows[i][j]
        basis.append([str(v) for v in vector])
    positive_ray = None
    if len(free) == 1:
        primitive = primitive_vector([Fraction(v) for v in basis[0]])
        if all(v > 0 for v in primitive):
            positive_ray = primitive
    inequality_ok = positive_ray is not None and all(
        sum(a * v for a, v in zip(row, positive_ray)) >= 0 for row in inequalities
    )
    heldout_ok = positive_ray is not None and all(
        sum(a * v for a, v in zip(row, positive_ray)) == 0 for row in heldout
    )
    truth_primitive = primitive_vector([Fraction(v) for v in truth])

    augmented = [row + [0] for row in equalities]
    anchor_row = [0] * N
    anchor_row[anchor_code] = 1
    augmented.append(anchor_row + [anchor_value])
    augmented_rows, augmented_pivots, augmented_review = rank_review(augmented)
    coefficient_rank = len([j for j in augmented_pivots if j < N])
    inconsistent = N in augmented_pivots
    anchored_values = None
    if coefficient_rank == N and not inconsistent:
        anchored_values = [Fraction(0)] * N
        for i, pivot in enumerate(augmented_pivots):
            anchored_values[pivot] = augmented_rows[i][-1]
    anchored_inequalities_ok = anchored_values is not None and all(
        sum(Fraction(a) * v for a, v in zip(row, anchored_values)) >= 0
        for row in inequalities
    )
    return {
        **review,
        "nullity": N - len(pivots),
        "rational_nullspace_basis": basis,
        "positive_primitive_ray": positive_ray,
        "ray_satisfies_inequalities": inequality_ok,
        "ray_matches_answer_up_to_scale": positive_ray == truth_primitive,
        "ray_satisfies_all_withheld_relations": heldout_ok,
        "unrestricted_unique_ray_accepted": bool(inequality_ok and heldout_ok),
        "absolute_scale_before_measurement": "unfixed" if positive_ray else "underidentified_or_rejected",
        "anchor": {
            "code": anchor_code,
            "measured_count": anchor_value,
            "coefficient_rank": coefficient_rank,
            "augmented_rank": augmented_review["rank"],
            "inconsistent_equalities": inconsistent,
            "unique_values": [str(v) for v in anchored_values] if anchored_values else None,
            "positive_values": bool(anchored_values and all(v > 0 for v in anchored_values)),
            "satisfies_inequalities": anchored_inequalities_ok,
            "matches_answer_exactly": anchored_values == list(map(Fraction, truth)),
            "determinant_review": augmented_review,
        },
    }


def rows_for(relations):
    rows = []
    for relation in relations:
        row = [0] * N
        row[relation["parent_code"]] += 1
        for code in relation["child_codes"]:
            row[code] -= 1
        rows.append(row)
    return rows


def finite_summary(equalities, inequalities, heldout, truth, maps, anchor_code):
    feasible = np.ones(len(maps), dtype=bool)
    if equalities:
        feasible &= np.all(maps @ np.asarray(equalities).T == 0, axis=1)
    if inequalities:
        feasible &= np.all(maps @ np.asarray(inequalities).T >= 0, axis=1)
    candidates = maps[feasible]
    truth_array = np.asarray(truth)
    truth_survives = bool(np.any(np.all(candidates == truth_array, axis=1)))
    heldout_compatible = np.ones(len(candidates), dtype=bool)
    if heldout:
        heldout_compatible &= np.all(candidates @ np.asarray(heldout).T == 0, axis=1)
    measured_survivors = []
    expected_survivors = []
    if len(candidates):
        for j in range(N):
            _, counts = np.unique(candidates[:, j], return_counts=True)
            expected_survivors.append(float(np.sum(counts.astype(float) ** 2) / len(candidates)))
            measured_survivors.append(int(np.sum(candidates[:, j] == truth[j])))
        active_code = min(range(N), key=lambda j: (expected_survivors[j], j))
        ranges = [[int(candidates[:, j].min()), int(candidates[:, j].max())] for j in range(N)]
    else:
        active_code, ranges = None, None
    return {
        "prior": "all_720_permutations_of_known_value_bag",
        "training_compatible_maps": int(len(candidates)),
        "true_map_survives": truth_survives,
        "maps_also_compatible_with_all_withheld_relations": int(heldout_compatible.sum()),
        "uniform_candidate_withheld_success_fraction": float(heldout_compatible.mean()) if len(candidates) else None,
        "finite_prior_joint_feasibility": bool(heldout_compatible.any()),
        "remaining_map_information_bits": log2(len(candidates)) if len(candidates) else None,
        "value_ranges_by_code": ranges,
        "random_anchor_compatible_maps": measured_survivors[anchor_code] if measured_survivors else 0,
        "candidate_counts_after_actual_measurement_by_code": measured_survivors,
        "random_code_mean_actual_survivors": float(np.mean(measured_survivors)) if measured_survivors else None,
        "active_measurement": {
            "code_selected_before_count": active_code,
            "uniform_prior_expected_survivors_by_code": expected_survivors,
            "actual_survivors": measured_survivors[active_code] if active_code is not None else 0,
        },
    }


def valid_semantic_relations():
    relations = []
    for size in (2, 3, 4):
        for children in combinations_with_replacement(range(N), size):
            total = sum(VALUES[j] for j in children)
            if total in VALUES:
                relations.append((VALUES.index(total), list(children)))
    assert relations
    return relations


def generate_world(seed, semantic_relations):
    rng = np.random.default_rng(seed)
    semantic_to_code = rng.permutation(N).tolist()
    truth = [0] * N
    for semantic, code in enumerate(semantic_to_code):
        truth[code] = VALUES[semantic]
    relations = []
    objects = []
    for i in range(20):
        parent, children = semantic_relations[int(rng.integers(len(semantic_relations)))]
        identifier = f"S{seed}-A{i:02d}"
        parent_id = identifier + "-P"
        child_ids = [identifier + f"-C{j}" for j in range(len(children))]
        record = {
            "assembly_id": identifier,
            "partition": "train" if i < 12 else "withheld",
            "parent_object": parent_id,
            "parent_code": semantic_to_code[parent],
            "child_objects": child_ids,
            "child_codes": [semantic_to_code[j] for j in children],
            "contents_complete": True,
        }
        relations.append(record)
        objects.append({"id": parent_id, "code": record["parent_code"]})
        objects.extend({"id": obj, "code": code} for obj, code in zip(child_ids, record["child_codes"]))
    before_balance = Counter(obj["code"] for obj in objects)
    target_count = max(before_balance.values())
    for code in range(N):
        for j in range(target_count - before_balance[code]):
            objects.append({"id": f"S{seed}-U{code}-{j}", "code": code})
    counts = Counter(obj["code"] for obj in objects)
    assert len({obj["id"] for obj in objects}) == len(objects)
    assert [counts[j] for j in range(N)] == [target_count] * N
    assert all(sum(a * v for a, v in zip(row, truth)) == 0 for row in rows_for(relations))

    # Reassign entire child groups. Preserve original observations and a record
    # of the changed physical memberships rather than editing the true world.
    scrambled = []
    changed_groups = 0
    for start, end in ((0, 12), (12, 20)):
        order = rng.permutation(end - start)
        subset = relations[start:end]
        for i, relation in enumerate(subset):
            donor = subset[int(order[i])]
            copy = dict(relation)
            copy["child_objects"] = donor["child_objects"]
            copy["child_codes"] = donor["child_codes"]
            copy["child_group_source"] = donor["assembly_id"]
            scrambled.append(copy)
            changed_groups += donor["assembly_id"] != relation["assembly_id"]
        assert sorted(tuple(x["child_codes"]) for x in subset) == sorted(
            tuple(x["child_codes"]) for x in scrambled[start:end]
        )
        assert Counter(x["parent_code"] for x in subset) == Counter(
            x["parent_code"] for x in scrambled[start:end]
        )

    missing_indices = sorted(rng.choice(12, size=6, replace=False).tolist())
    incomplete = []
    for i, relation in enumerate(relations):
        copy = dict(relation)
        if i in missing_indices:
            removed = int(rng.integers(len(relation["child_codes"])))
            copy["child_codes"] = [c for j, c in enumerate(relation["child_codes"]) if j != removed]
            copy["child_objects"] = [c for j, c in enumerate(relation["child_objects"]) if j != removed]
            copy["contents_complete"] = False
            copy["concealed_removed_child"] = relation["child_objects"][removed]
        incomplete.append(copy)
    incomplete_rows = rows_for(incomplete)
    assert all(sum(a * v for a, v in zip(row, truth)) >= 0 for row in incomplete_rows)
    assert all(sum(a * v for a, v in zip(incomplete_rows[i], truth)) > 0 for i in missing_indices)

    # Global relabelling across slots, including fillers, gives categorical
    # badges with exactly the same single-label pool frequencies.
    badge_labels = rng.permutation([obj["code"] for obj in objects]).tolist()
    badge_by_object = {obj["id"]: label for obj, label in zip(objects, badge_labels)}
    assert Counter(badge_labels) == counts
    badges = []
    for relation in relations:
        copy = dict(relation)
        copy["parent_code"] = badge_by_object[relation["parent_object"]]
        copy["child_codes"] = [badge_by_object[identifier] for identifier in relation["child_objects"]]
        badges.append(copy)
    anchor_code = int(rng.integers(N))
    return {
        "seed": seed,
        "concealed_values_by_code": truth,
        "objects": objects,
        "text_only_count_per_code": target_count,
        "complete_membership": relations,
        "scrambled_membership": scrambled,
        "scrambled_changed_groups": int(changed_groups),
        "incomplete_membership": incomplete,
        "missing_training_indices": missing_indices,
        "ownership_labels": badges,
        "ownership_label_by_object": badge_by_object,
        "random_anchor_code": anchor_code,
    }


def matrices_for(world, scenario, prefix):
    if scenario.startswith("incomplete"):
        relations = world["incomplete_membership"]
    else:
        relations = world[scenario]
    training, withheld = relations[:prefix], relations[12:]
    if scenario == "incomplete_recorded":
        equalities = rows_for([r for r in training if r["contents_complete"]])
        inequalities = rows_for([r for r in training if not r["contents_complete"]])
    else:
        equalities, inequalities = rows_for(training), []
    return equalities, inequalities, rows_for(withheld)


def aggregate(records):
    summary = []
    for scenario in SCENARIOS:
        for prefix in PREFIXES:
            rows = [r for r in records if r["scenario"] == scenario and r["training_relations"] == prefix]
            counts = [r["finite"]["training_compatible_maps"] for r in rows]
            active = [r["finite"]["active_measurement"]["actual_survivors"] for r in rows if r["finite"]["training_compatible_maps"]]
            random = [r["finite"]["random_code_mean_actual_survivors"] for r in rows if r["finite"]["training_compatible_maps"]]
            summary.append({
                "scenario": scenario,
                "training_relations": prefix,
                "worlds": len(rows),
                "equality_rank_distribution": dict(sorted(Counter(str(r["rational"]["rank"]) for r in rows).items())),
                "finite_compatible_maps_min_median_max": [min(counts), float(np.median(counts)), max(counts)],
                "finite_unique_worlds": sum(c == 1 for c in counts),
                "finite_empty_worlds": sum(c == 0 for c in counts),
                "finite_true_map_survives_worlds": sum(r["finite"]["true_map_survives"] for r in rows),
                "finite_joint_train_withheld_feasible_worlds": sum(r["finite"]["finite_prior_joint_feasibility"] for r in rows),
                "positive_rank_five_ray_worlds": sum(r["rational"]["positive_primitive_ray"] is not None for r in rows),
                "true_relative_values_recovered_worlds": sum(r["rational"]["ray_matches_answer_up_to_scale"] for r in rows),
                "unrestricted_unique_ray_withheld_accepted_worlds": sum(r["rational"]["unrestricted_unique_ray_accepted"] for r in rows),
                "absolute_values_recovered_with_one_count_worlds": sum(r["rational"]["anchor"]["matches_answer_exactly"] for r in rows),
                "active_anchor_actual_survivors_mean_given_nonempty": float(np.mean(active)) if active else None,
                "random_anchor_actual_survivors_mean_given_nonempty": float(np.mean(random)) if random else None,
            })
    return summary


def run(output, seeds):
    if output.exists():
        raise FileExistsError(f"Preserved output already exists: {output}")
    output.mkdir(parents=True)
    source = Path(__file__).resolve()
    protocol = Path("experiments/2026-10-02-six-hour/physical-information/PROTOCOL.md")
    code_hash = sha256(source.read_bytes()).hexdigest()
    protocol_hash = sha256(protocol.read_bytes()).hexdigest()
    shutil.copy2(source, output / "code_snapshot.py")
    shutil.copy2(protocol, output / "protocol_snapshot.md")
    maps = np.asarray(list(permutations(VALUES)), dtype=np.int64)
    assert maps.shape == (720, N)
    semantic_relations = valid_semantic_relations()
    worlds, records = [], []
    for seed in seeds:
        world = generate_world(seed, semantic_relations)
        worlds.append(world)
        truth = world["concealed_values_by_code"]
        anchor_code = world["random_anchor_code"]
        for scenario in SCENARIOS:
            for prefix in PREFIXES:
                equalities, inequalities, withheld = matrices_for(world, scenario, prefix)
                rational = rational_summary(equalities, inequalities, withheld, truth, anchor_code, truth[anchor_code])
                finite = finite_summary(equalities, inequalities, withheld, truth, maps, anchor_code)
                if scenario in ("complete_membership", "incomplete_recorded"):
                    assert finite["true_map_survives"]
                if scenario == "complete_membership" and rational["rank"] == N - 1:
                    assert rational["ray_matches_answer_up_to_scale"]
                    assert rational["anchor"]["matches_answer_exactly"]
                if prefix == 0:
                    assert finite["training_compatible_maps"] == 720
                    assert finite["random_anchor_compatible_maps"] == 120
                    assert rational["rank"] == 0
                records.append({
                    "seed": seed,
                    "scenario": scenario,
                    "training_relations": prefix,
                    "training_equality_matrix": equalities,
                    "training_inequality_matrix": inequalities,
                    "withheld_equality_matrix": withheld,
                    "rational": rational,
                    "finite": finite,
                })
    result = {
        "status": "synthetic-completed",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "code_sha256": code_hash,
        "protocol_sha256": protocol_hash,
        "seeds": seeds,
        "symbols": N,
        "concealed_semantic_values": list(VALUES),
        "possible_semantic_relation_multisets": len(semantic_relations),
        "training_assemblies_per_world": 12,
        "withheld_assemblies_per_world": 8,
        "worlds_are_independent_units": True,
        "prefixes_and_controls_share_worlds": True,
        "checks": {
            "balanced_single_label_pools": "passed",
            "object_ids_unique": "passed",
            "complete_conservation_exact": "passed",
            "scrambled_marginals_preserved": "passed",
            "badge_marginals_preserved": "passed",
            "incomplete_inequality_direction": "passed",
            "permutation_count_720": "passed",
            "rational_rank_witness_determinants": "passed",
            "rank_five_relative_and_anchored_answer_recovery": "passed",
            "correct_missingness_true_map_retention": "passed",
        },
        "summary": aggregate(records),
        "records": records,
    }
    (output / "worlds.json").write_text(json.dumps(worlds, indent=2) + "\n", encoding="utf-8")
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "worlds": len(worlds), "records": len(records), "checks": result["checks"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/2026-10-02-six-hour/physical-information/main"))
    parser.add_argument("--worlds", type=int, default=24)
    args = parser.parse_args()
    if args.worlds < 1:
        parser.error("--worlds must be positive")
    run(args.output, list(range(20261002, 20261002 + args.worlds)))


if __name__ == "__main__":
    main()
