"""Read saved outputs and independently check finite arithmetic; never refit."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from math import comb, isclose, sqrt
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/2026-10-02-six-hour/null-calibration/shared-quality"
sources = {}
checks = Counter()


def read(path):
    raw = path.read_bytes()
    sources[path.relative_to(ROOT).as_posix()] = {
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()
    }
    return json.loads(raw.decode("utf-8"))


def equal(actual, expected, label):
    assert actual == expected, (label, actual, expected)
    checks[label] += 1


def near(actual, expected, label, tolerance=1e-12):
    assert isclose(actual, expected, abs_tol=tolerance, rel_tol=tolerance), (
        label, actual, expected
    )
    checks[label] += 1


def overlap_counts(n, middle, outer):
    return {
        k: comb(middle, k) * comb(n - middle, outer - k)
        for k in range(max(0, outer - (n - middle)), min(middle, outer) + 1)
    }


def convolve(left, right):
    result = Counter()
    for i, a in left.items():
        for j, b in right.items():
            result[i + j] += a * b
    return dict(result)


def distribution(n, a0, a1, a2):
    # Fix the middle-column arrangement, count independent outer overlaps,
    # then multiply by the number of possible middle arrangements.
    counts = convolve(overlap_counts(n, a1, a0), overlap_counts(n, a1, a2))
    return {score: weight * comb(n, a1) for score, weight in counts.items()}


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    radius = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return [center - radius, center + radius]


main = read(BASE / "main/results.json")
main_audit = read(BASE / "verification_main.json")
diagnostic = read(BASE / "agreement-diagnostic/main/results.json")
audit = read(BASE / "agreement-diagnostic/verification.json")
tables = read(BASE / "agreement-diagnostic/main/binary_dp.json")
equal(main["datasets"], 300, "nested_population_count")
equal(diagnostic["datasets"], 1000, "diagnostic_population_count")
equal(diagnostic["post_outcome"], True, "diagnostic_post_outcome")
for filename, obj, audit_obj in [
    ("main/results.json", main, main_audit),
    ("agreement-diagnostic/main/results.json", diagnostic, audit),
]:
    equal(
        sources[(BASE / filename).relative_to(ROOT).as_posix()]["sha256"],
        audit_obj["input_results_sha256"], "audit_input_hash"
    )
equal(main_audit["status"], "pass", "saved_audit_status")
equal(audit["status"], "pass", "saved_audit_status")

dist = {}
for n_text, entries in tables.items():
    n = int(n_text)
    equal(len(entries), (n + 1) ** 3, "cell_count_triple_coverage")
    for entry in entries:
        a0, a1, a2 = entry["agreement_counts"]
        independent = distribution(n, a0, a1, a2)
        saved = {int(k): v for k, v in entry["score_counts"].items()}
        equal(independent, saved, "hypergeometric_distribution")
        total = comb(n, a0) * comb(n, a1) * comb(n, a2)
        equal(sum(independent.values()), total, "cell_integer_total")
        equal(
            Fraction(sum(k * v for k, v in independent.items()), total),
            Fraction(a0 * a1 + a1 * a2, n), "cell_exact_mean"
        )
        dist[(n, a0, a1, a2)] = independent
equal(len(dist), 1547, "all_cell_distributions")

thresholds = ["0.01", "0.05", "0.1"]
methods = ["broad_vectors", "quality_vectors"]
mc = {m: Counter() for m in methods}
ex = {m: Counter() for m in methods}
means = {m: Fraction(0) for m in methods}
paired = {mode: {t: Counter() for t in thresholds} for mode in ["monte_carlo", "exact"]}
support_sizes = {m: Counter() for m in methods}
observed_sum = 0
diagnostic_seeds = set()

for index in range(1000):
    item = read(BASE / f"agreement-diagnostic/main/dataset_{index:04d}.json")
    diagnostic_seeds.add(item["generation"]["seed"])
    pairs = defaultdict(list)
    for row in item["rows"]:
        pairs[row["artifact"]].append(row)
    equal(len(pairs), 20, "diagnostic_object_count")
    observed = 0
    count_cells = {m: defaultdict(lambda: [0, 0, 0, 0]) for m in methods}
    for rows in pairs.values():
        equal(len(rows), 2, "observed_pair_size")
        agreement = [int(a == b) for a, b in zip(rows[0]["seq"], rows[1]["seq"])]
        observed += agreement[0] * agreement[1] + agreement[1] * agreement[2]
        for method in methods:
            key = (rows[0]["site"], rows[0]["object_type"])
            if method == "quality_vectors":
                key += (rows[0]["quality"],)
            values = count_cells[method][key]
            values[0] += 1
            for slot in range(3):
                values[slot + 1] += agreement[slot]
    equal(observed, item["observed_score"], "observed_integer_score")
    observed_sum += observed
    values_by_mode = {mode: {} for mode in paired}
    for method in methods:
        ref = item["references"][method]
        expected_cells = sorted(tuple(v) for v in count_cells[method].values())
        saved_cells = sorted((c["objects"], *c["agreement_counts"]) for c in ref["cells"])
        equal(saved_cells, expected_cells, "observed_cell_agreement_counts")
        full = {0: 1}
        mean = Fraction(0)
        for n, a0, a1, a2 in expected_cells:
            full = convolve(full, dist[(n, a0, a1, a2)])
            mean += Fraction(a0 * a1 + a1 * a2, n)
        denominator = sum(full.values())
        tail = Fraction(sum(v for k, v in full.items() if k >= observed), denominator)
        equal(tail, Fraction(ref["exact_tail"]), "exact_population_tail")
        equal(denominator, ref["conditional_table_count"], "population_integer_total")
        equal(mean, Fraction(ref["conditional_mean"]), "population_conditional_mean")
        means[method] += mean
        support_sizes[method][len(full)] += 1
        equal(len(ref["null_scores"]), 99, "saved_reference_score_count")
        exceed = sum(s >= observed for s in ref["null_scores"])
        equal(exceed, ref["exceedances"], "saved_score_exceedances")
        p = Fraction(1 + exceed, 100)
        near(float(p), ref["p_value"], "inclusive_mc_tail")
        values_by_mode["monte_carlo"][method] = p
        values_by_mode["exact"][method] = tail
        for t in thresholds:
            mc[method][t] += p <= Fraction(t)
            ex[method][t] += tail <= Fraction(t)
    for mode, values in values_by_mode.items():
        for t in thresholds:
            left = values["broad_vectors"] <= Fraction(t)
            right = values["quality_vectors"] <= Fraction(t)
            label = "both" if left and right else "broad_only" if left else "quality_only" if right else "neither"
            paired[mode][t][label] += 1

equal(len(diagnostic_seeds), 1000, "distinct_diagnostic_generator_seeds")
near(observed_sum / 1000, diagnostic["observed_score_mean"], "observed_score_mean")
for method in methods:
    near(float(means[method] / 1000), diagnostic["conditional_mean_average"][method], "conditional_mean_average")
    for section, counts in [("aggregate", mc), ("exact_aggregate", ex)]:
        for t in thresholds:
            saved = diagnostic[section][f"agreement_diagnostic/{method}"]["rejections"][t]
            equal(saved["count"], counts[method][t], "diagnostic_rejection_count")
            near(saved["rate"], counts[method][t] / 1000, "diagnostic_rejection_rate")
            for actual, expected in zip(saved["wilson_95_ci"], wilson(counts[method][t], 1000)):
                near(actual, expected, "diagnostic_wilson_interval", 1e-8)
for mode in paired:
    for t in thresholds:
        saved = audit["paired_rejection"][mode][t]
        for name in ["both", "broad_only", "quality_only", "neither"]:
            equal(saved[name], paired[mode][t][name], "diagnostic_paired_counts")
        near(saved["broad_minus_quality_rate"], (paired[mode][t]["broad_only"] - paired[mode][t]["quality_only"]) / 1000, "diagnostic_paired_difference")
equal(audit["bootstrap_replicates"], 20000, "saved_bootstrap_replicates")
equal(audit["paired_rejection"]["monte_carlo"]["0.05"]["paired_95_interval"], [0.916, 0.947], "saved_paired_interval")

nested_rejections = {m: Counter() for m in methods}
nested_seeds = set()
for index in range(300):
    item = read(BASE / f"main/dataset_{index:04d}.json")
    nested_seeds.add(item["generation"]["seed"])
    for method in methods:
        ref = item["references"][method]
        observed_gain = item["observed"]["gain"]
        exceed = sum(v["gain"] >= observed_gain for v in ref["null"])
        equal(exceed, ref["exceedances"], "nested_saved_gain_exceedances")
        p = Fraction(1 + exceed, 100)
        near(float(p), ref["p_value"], "nested_inclusive_tail")
        for t in thresholds:
            nested_rejections[method][t] += p <= Fraction(t)
for method in methods:
    for t in thresholds:
        saved = main["aggregate"][f"shared_quality/{method}"]["rejections"][t]
        equal(saved["count"], nested_rejections[method][t], "nested_rejection_count")
        near(saved["rate"], nested_rejections[method][t] / 300, "nested_rejection_rate")
        for actual, expected in zip(saved["wilson_95_ci"], wilson(nested_rejections[method][t], 300)):
            near(actual, expected, "nested_wilson_interval", 1e-8)
equal(len(nested_seeds), 300, "distinct_nested_generator_seeds")
equal(len(nested_seeds & diagnostic_seeds), 0, "fresh_generator_namespaces")

H_low = Fraction(39, 40) ** 2 + Fraction(1, 40) ** 2 / 7
H_high = Fraction(2, 5) ** 2 + Fraction(3, 5) ** 2 / 7
expected_score = 20 * (H_low ** 2 + H_high ** 2)
expected_broad = 40 * ((H_low + H_high) / 2) ** 2
equal(expected_score, Fraction(diagnostic["generator_expected_score"]), "analytic_generator_mean")
equal(expected_broad, Fraction(diagnostic["broad_reference_expected_conditional_mean"]), "analytic_broad_mean")
equal(expected_score - expected_broad, Fraction(diagnostic["expected_mean_difference"]), "analytic_mean_gap")
equal(expected_score - expected_broad, 10 * (H_low - H_high) ** 2, "analytic_gap_identity")

small = read(BASE / "exact/results.json")
small_audit = read(BASE / "verification_exact.json")
moments = read(BASE / "analytic-moments/results.json")
equal(small["broad_columns"], 6, "small_broad_columns")
equal(small["broad_tables"], 6 ** 3, "small_broad_tables")
equal(small["quality_columns"], 4, "small_quality_columns")
equal(small["quality_tables"], 4 ** 3, "small_quality_tables")
equal(Fraction(small["quality_table_probability"]), Fraction(1, 64), "small_uniform_probability")
equal(small_audit["status"], "pass", "saved_small_space_audit")
equal(small_audit["independent_sampler_draws_replayed"], 20000, "saved_small_sampler_replay")
equal(moments["status"], "pass", "saved_moment_audit")
equal([Fraction(v) for v in moments["class_agreement"]], [H_low, H_high], "moment_class_agreement")
near(float(Fraction(moments["single_face_maximum_absolute_covariance"])), .0006072704, "single_face_covariance_rounding", 1e-10)
for witness in moments["vector_maximum"]:
    near(float(Fraction(witness["largest_absolute_covariance"])), .0057955982, "vector_covariance_rounding", 1e-10)

record = {
    "status": "pass", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Read-only finite arithmetic and saved-score checks. No generator, sampler, fitting routine or bootstrap was rerun; paired intervals are checked against the independently audited endpoint.",
    "check_counts": dict(checks), "total_assertions": sum(checks.values()),
    "cell_distributions": len(dist), "exact_population_tails": 2000,
    "observed_integer_scores": 1000, "saved_mc_score_tails": 2000,
    "nested_saved_gain_tails": 600,
    "conditional_support_size_histogram": {m: dict(v) for m, v in support_sizes.items()},
    "source_files": sources,
}
(OUT / "numerical-checks.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: record[k] for k in ["status", "total_assertions", "cell_distributions", "exact_population_tails", "conditional_support_size_histogram"]}, indent=2))
