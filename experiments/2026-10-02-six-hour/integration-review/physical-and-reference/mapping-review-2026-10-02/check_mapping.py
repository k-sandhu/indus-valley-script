"""Reaggregate saved mapping results and audit counts without fitting."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "experiments/2026-10-02-six-hour/latent-forms"
OUT = Path(__file__).resolve().parent
pins = {}
checks = Counter()


def load(path):
    raw = path.read_bytes()
    pins[path.relative_to(ROOT).as_posix()] = {
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()
    }
    return json.loads(raw.decode("utf-8"))


def equal(a, b, label):
    assert a == b, (label, a, b)
    checks[label] += 1


def near(a, b, label, tol=1e-10):
    assert math.isclose(a, b, abs_tol=tol, rel_tol=tol), (label, a, b)
    checks[label] += 1


rows = load(BASE / "review-v1/reviewed-rows.json")
audit = load(BASE / "review-v1/verification.json")
objective = load(BASE / "review-v1/objective-diagnostics.json")
collapsed = load(BASE / "collapsed-v1/rows.json")
collapsed_audit = load(BASE / "collapsed-v1/verification.json")
choices = load(BASE / "collapsed-v1/reference-choices.json")
paired = load(BASE / "review-v1/paired-comparisons.json")
main = load(BASE / "main-v1/results.json")

equal(len(rows), 864, "reviewed_row_count")
equal(len(collapsed), 288, "collapsed_row_count")
equal(len({r["seed"] for r in rows}), 12, "independent_systems")
equal(len({(r["seed"], r["variant"], r["reference_records"], r["shift"]) for r in rows}), 144, "reused_conditions")

groups = defaultdict(list)
for r in rows + collapsed:
    groups[(r["variant"], r["reference_records"], r["algorithm"])].append(r)
for source in [audit, collapsed_audit]:
    for aggregate in source["aggregates"]:
        key = (aggregate["variant"], aggregate["reference_records"], aggregate["algorithm"])
        selected = groups[key]
        equal(len(selected), aggregate["conditions"], "aggregate_denominator")
        equal(sum(r["exact_recovery"] for r in selected), aggregate["complete_recovery"], "aggregate_recovery")

table = []
expected = {
    (40, "same_length_0"): [8, 12, 12, 8],
    (40, "same_length_35"): [2, 4, 3, 1],
    (40, "same_length_70"): [0, 0, 0, 0],
    (400, "same_length_0"): [22, 24, 24, 21],
    (400, "same_length_35"): [22, 24, 24, 22],
    (400, "same_length_70"): [16, 18, 16, 17],
}
algorithms = ["reference_selected", "latent_mixture", "reference_selected_three", "collapsed_profile"]
for (ref, variant), want in expected.items():
    actual = []
    for algorithm in algorithms:
        selected = groups[(variant, ref, algorithm)]
        equal(len(selected), 24, "paper_table_denominator")
        actual.append(sum(r["exact_recovery"] for r in selected))
    equal(actual, want, "paper_six_row_table")
    table.append({"reference_records": ref, "variant": variant, "counts": dict(zip(algorithms, actual)), "conditions": 24})

totals = {}
for algorithm, count in [("latent_mixture", 82), ("reference_selected_three", 79), ("reference_selected", 70), ("form_observed_slot", 85)]:
    selected = [r for r in rows if r["algorithm"] == algorithm]
    equal(len(selected), 144, "total_denominator")
    totals[algorithm] = sum(r["exact_recovery"] for r in selected)
    equal(totals[algorithm], count, "paper_recovery_totals")

indexed = {(r["seed"], r["variant"], r["reference_records"], r["shift"], r["algorithm"]): r for r in rows}
for r in collapsed:
    if r["algorithm"] != "reference_selected_four":
        continue
    old = indexed[(r["seed"], r["variant"], r["reference_records"], r["shift"], "reference_selected_three")]
    equal(r["exact_recovery"], old["exact_recovery"], "four_model_point_recovery_unchanged")

medians = {}
for variant, value in [("same_length_0", 1669.37), ("same_length_35", 530.80), ("same_length_70", -36.48)]:
    selected = [r for r in choices if r["variant"] == variant and r["reference_records"] == 400]
    equal(len(selected), 12, "cv_median_system_count")
    for r in selected:
        near(r["scores"]["latent_mixture"] - r["scores"]["collapsed_profile"], r["mixture_minus_collapsed_CV_bits"], "cv_score_subtraction")
    medians[variant] = median(r["mixture_minus_collapsed_CV_bits"] for r in selected)
    equal(round(medians[variant], 2), value, "paper_cv_median_rounding")

for variant, mean, interval in [("same_length_0", .125, [0, .25]), ("same_length_35", .0625, [0, .125]), ("same_length_70", 0, [0, 0])]:
    entry = next(r for r in paired if r["variant"] == variant and r["algorithm"] == "reference_selected_three" and r["comparator"] == "reference_selected" and r["metric"] == "exact_recovery")
    near(entry["mean_difference"], mean, "selected_paired_gain")
    equal(entry["percentile_95_interval"], interval, "saved_paired_interval")
    equal(entry["systems"], 12, "paired_independent_systems")
    equal(entry["conditions_per_system"], 4, "paired_repeated_conditions")
    equal(entry["bootstrap_draws"], 20000, "saved_bootstrap_draws")

equal(main["component_count_prior"], 3, "component_prior")
equal(len(main["models"]), 288, "reference_fit_count")
equal(sum(m["stage"] == "full_reference" for m in main["models"]), 72, "full_reference_fit_count")
starts = [s for m in main["models"] for s in m["starts"]]
equal(len(starts), 2304, "individual_reference_starts")
for model in main["models"]:
    equal(len(model["starts"]), 8, "starts_per_fit")
equal(max(s["iterations"] for s in starts), 150, "maximum_reference_iterations")
equal(sum(s["iterations"] == 150 for s in starts), 178, "iteration_limit_starts")
equal(audit["reference_iteration_budget_stops"], 178, "audit_iteration_limit_count")
updates = sum(len(s.get("trace", [])) for run in main["mapping_runs"] for s in run["starts"])
equal(updates, 4433, "saved_assignment_update_count")
equal(audit["mapping_assignments_checked"], updates, "assignment_audit_coverage")
for run in main["mapping_runs"]:
    for start in run["starts"]:
        assert len(start.get("trace", [])) <= 25
        checks["mapping_update_budget"] += 1
    for candidate in run["candidate_ties"]:
        equal(candidate["mapping"], run["mapping"], "no_distinct_retained_candidate_tie")

failed = [r for r in objective if not r["recovered"]]
equal(len(failed), 62, "failed_mixture_maps")
equal(sum(r["returned_minus_truth_nats"] > 1e-8 for r in failed), 56, "wrong_map_objective_preferred")
equal(sum(r["returned_minus_truth_nats"] < -1e-8 for r in failed), 6, "search_misses")
equal(audit["checks_total"], 68014, "saved_primary_audit_total")
equal(audit["checks_passed"], 68014, "saved_primary_audit_passed")
equal(audit["failures"], [], "saved_primary_audit_failures")
near(audit["max_scalar_errors"]["selected assignment Q"], 1.46e-11, "assignment_disagreement_rounding", 1e-13)

# Verify the contributor's source pins, including protocols and code, without
# executing any fitting helper or changing any source file.
for record in [main, audit, collapsed_audit]:
    for name, want in record["source_hashes"].items():
        raw = (ROOT / name).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        equal(actual, want, "contributor_source_hash")
        pins[name] = {"bytes": len(raw), "sha256": actual}
for name in ["PROTOCOL.md", "METHODS.md", "RETROSPECTIVE.md", "COLLAPSED_PROTOCOL.md"]:
    raw = (BASE / name).read_bytes()
    pins[(BASE / name).relative_to(ROOT).as_posix()] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
equal(pins[(BASE / "PROTOCOL.md").relative_to(ROOT).as_posix()]["sha256"], main["protocol_sha256"], "main_protocol_pin")
equal(pins[(BASE / "COLLAPSED_PROTOCOL.md").relative_to(ROOT).as_posix()]["sha256"], collapsed_audit["protocol_sha256"], "collapsed_protocol_pin")

result = {
    "status": "pass", "checked_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Read-only reaggregation of saved rows, reference scores, starts, trajectories and contributor audit pins. No fits or bootstrap were rerun.",
    "assertions": sum(checks.values()), "check_counts": dict(checks),
    "table": table, "totals": totals, "large_reference_cv_medians_bits": medians,
    "reference_fits": 288, "reference_starts": 2304, "iteration_limit_starts": 178,
    "mapping_updates": updates, "failed_map_objective_counts": {"above_truth": 56, "below_truth": 6},
    "source_files": pins,
}
(OUT / "numerical-checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ["status", "assertions", "large_reference_cv_medians_bits", "mapping_updates"]}, indent=2))
