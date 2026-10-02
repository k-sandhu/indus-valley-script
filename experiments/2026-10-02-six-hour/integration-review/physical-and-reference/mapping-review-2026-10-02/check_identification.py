"""Check saved rational rank certificates and identification audit sizes."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/2026-10-02-six-hour/latent-generator-identification"
pins = {}
checks = Counter()


def load(name):
    raw = (BASE / name).read_bytes()
    pins[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return json.loads(raw.decode("utf-8"))


def equal(a, b, label):
    assert a == b, (label, a, b)
    checks[label] += 1


def rational(pair):
    return Fraction(int(pair[0]), int(pair[1]))


def determinant(matrix):
    n = len(matrix)
    value = Fraction(0)
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n))
        term = Fraction((-1) ** inversions)
        for i, j in enumerate(order):
            term *= matrix[i][j]
        value += term
    return value


main = load("main/results.json")
collapsed = load("collapsed-control/results.json")
audit = load("review-v2/verification.json")
equal(main["main_generator_profiles"], 36, "main_profiles")
equal(len(main["profiles"]), 72, "main_convention_profiles")
equal(len(collapsed["profiles"]), 24, "collapsed_convention_profiles")
equal({p["alpha"] for p in main["profiles"]}, {0, .35, .70}, "main_shared_mass_levels")
equal({p["convention"] for p in main["profiles"]}, {"normalized_binary64", "rounded_thresholds_continuous_uniform"}, "probability_conventions")
matrix_count = 0
mixing_count = 0
support_counts = Counter()
for label, record, expected_rank in [("main", main, 3), ("collapsed", collapsed, 1)]:
    for profile in record["profiles"]:
        equal([m["slots"] for m in profile["grouped_matrices"]], [[0, 1], [2, 3], [4, 5]], "fixed_pair_grouping")
        for grouped in profile["grouped_matrices"]:
            matrix = [[rational(v) for v in row] for row in grouped["minor"]]
            det = determinant(matrix)
            equal(det, rational(grouped["determinant"]), "exact_minor_determinant")
            assert det != 0
            checks["nonzero_minor"] += 1
            equal(grouped["rank"], expected_rank, "reported_rank")
            equal(grouped["kruskal_rank"], expected_rank, "reported_kruskal_rank")
            matrix_count += 1
        equal(profile["rank_sum"], 3 * expected_rank, "rank_sum")
        equal(profile["threshold"], 2 * 3 + 2, "fixed_component_threshold")
        equal(profile["corollary2_condition"], label == "main", "identification_condition")
        if label == "main":
            for shift, values in profile["mixing_weights_by_shift"].items():
                weights = [rational(v) for v in values]
                equal(sum(weights), 1, "mixing_weight_normalization")
                assert all(v > 0 for v in weights)
                checks["positive_mixing_weights"] += 1
                mixing_count += 1
            for row in profile["slot_support_counts"]:
                support_counts.update(row)
        else:
            equal(profile["alpha"], 1, "constructed_collapse_alpha")
            alternatives = [[rational(v) for v in row] for row in profile["alternative_positive_weights"]]
            equal(alternatives, [[Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)], [Fraction(3, 10), Fraction(3, 10), Fraction(2, 5)]], "collapsed_weight_vectors")
            for weights in alternatives:
                equal(sum(weights), 1, "collapsed_weight_sum")
                assert all(v > 0 for v in weights)
                checks["collapsed_weight_positivity"] += 1
            assert sorted(alternatives[0]) != sorted(alternatives[1])
            checks["weight_ambiguity_beyond_label_swap"] += 1
            equal(profile["identical_component_products"], True, "identical_collapsed_components")
            equal(profile["same_population_law"], True, "collapsed_equal_law_certificate")

equal(matrix_count, 288, "all_minor_certificates")
equal(mixing_count, 144, "all_mixing_vectors")
equal(audit["status"], "pass", "saved_audit_status")
equal(audit["exact_grouped_entries_reconstructed"], 96 * 3 * 3 * 400, "audit_pair_entry_count")
equal(audit["exact_slot_marginals_checked"], 96 * 3 * 6 * 20, "audit_slot_marginal_count")
equal(audit["positive_normalized_mixing_vectors_checked"], 144, "audit_positive_mixture_count")
equal(audit["independently_eliminated_minor_certificates"], 288, "audit_minor_count")
equal(audit["main_results_sha256"], pins["main/results.json"]["sha256"], "main_audit_hash")
equal(audit["collapsed_results_sha256"], pins["collapsed-control/results.json"]["sha256"], "collapsed_audit_hash")
for name, want in main["input_hashes"].items():
    raw = (BASE / name).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    equal(actual, want, "input_source_hash")
    pins[name] = {"bytes": len(raw), "sha256": actual}
result = {
    "status": "pass", "checked_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Independent Leibniz determinant check of saved minors, positive mixing weights, equal-law control parameters and audit-size arithmetic; no full pair-matrix reconstruction or fitting replay.",
    "assertions": sum(checks.values()), "check_counts": dict(checks),
    "minor_certificates_checked": matrix_count, "positive_mixing_vectors_checked": mixing_count,
    "main_slot_support_histogram": dict(support_counts), "source_files": pins,
    "primary_theorem_access": {
        "url": "https://arxiv.org/pdf/0809.5032v2", "access_date": "2026-10-02",
        "location": "Corollary 2, PDF page index11 (reprint page12); marginal recovery Lemma14, page index23",
        "observed_condition": "Positive weights and row Kruskal ranks summing to at least2r+2 identify fixed-r model parameters up to common component labels.",
        "application": "r=3; three independent 400-state slot pairs; nonzero three-row minors give ranks3/3/3."
    }
}
(OUT / "identification-checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: result[k] for k in ["status", "assertions", "minor_certificates_checked", "positive_mixing_vectors_checked", "main_slot_support_histogram"]}, indent=2))
