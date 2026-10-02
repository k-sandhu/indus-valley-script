"""Independent count construction and read-only correspondence audit."""
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def count_model(rows, alpha, options, unknown):
    signs = sorted({sign for row in rows for sign in row["seq"]}) + [unknown]
    index = {sign: i for i, sign in enumerate(signs)}
    glyph_counts = Counter(sign for row in rows for sign in row["seq"])
    starts = Counter(row["seq"][0] for row in rows)
    pairs = Counter()
    for row in rows:
        pairs.update(zip(row["seq"][:-1], row["seq"][1:]))
        if not options.get("glyph_only", False):
            pairs[(row["seq"][-1], "END")] += 1
    total = sum(glyph_counts.values()) + 0.5 * len(signs)
    unigram = np.array([(glyph_counts[sign] + 0.5) / total for sign in signs])
    initial = unigram.copy() if options.get("unigram_start", False) else np.array([(starts[sign] + alpha * unigram[index[sign]]) / (len(rows) + alpha) for sign in signs])
    destinations = signs if options.get("glyph_only", False) else signs + ["END"]
    destination_counts = np.array([glyph_counts[sign] + 0.5 for sign in signs] + ([] if options.get("glyph_only", False) else [len(rows) + 0.5]))
    prior = destination_counts / destination_counts.sum()
    counts = np.zeros((len(signs), len(destinations)))
    for (left, right), count in pairs.items():
        counts[index[left], len(signs) if right == "END" else index[right]] = count
    outgoing = Counter()
    for (left, right), count in pairs.items():
        outgoing[left] += count
    transition = np.array([[(pairs[(left, right)] + alpha * prior[j]) / (outgoing[left] + alpha) for j, right in enumerate(destinations)] for left in signs])
    return signs, index, initial, transition


def independent_prediction(row, slot, fitted, options, unknown):
    signs, index, initial, transition = fitted
    if slot:
        left = index.get(row["seq"][slot - 1], index[unknown])
        weights = transition[left, :len(signs)].copy()
    else:
        weights = initial.copy()
    if slot + 1 < len(row["seq"]):
        right = index.get(row["seq"][slot + 1], index[unknown])
        weights *= transition[:, right]
    elif options.get("use_end", True):
        weights *= transition[:, len(signs)]
    probabilities = weights / weights.sum()
    ranking = np.argsort(-probabilities, kind="stable")
    actual = row["seq"][slot]
    actual_index = index.get(actual, index[unknown])
    return {"codes": [signs[i] for i in ranking[:10]], "masses": probabilities[ranking[:10]],
            "top1": signs[ranking[0]] == actual, "top5": actual in [signs[i] for i in ranking[:5]],
            "top10": actual in [signs[i] for i in ranking[:10]], "model_top_mass": probabilities[ranking[0]],
            "bucket_loss_bits": -math.log2(probabilities[actual_index]), "known_in_training": actual in index}


def main():
    folder = HERE / "main"
    result = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    assert digest(folder / "code_snapshot.py") == result["source_sha256"]
    assert digest(HERE / "PROTOCOL.md") == result["protocol_sha256"]
    assert digest(ROOT / "experiments/2026-10-02-six-hour/markov-baseline/main/results.json") == result["prior_result_sha256"]
    spec = importlib.util.spec_from_file_location("frozen_ablation", folder / "code_snapshot.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    rows, _ = module.helper.load_records(ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl", min_length=3, unique=True)
    groups = module.helper.group_records(rows)
    assignments, _ = module.helper.make_folds(rows, groups, 5, 20261006)
    row_lookup = {row["record_id"]: row for row in rows}
    fold_lookup = {row["record_id"]: assignments[i] for i, row in enumerate(rows)}
    group_lookup = {rows[i]["record_id"]: group for group, indices in enumerate(groups) for i in indices}
    prior_scores = module.base.read_jsonl(module.PRIOR / "markov_slot_audit.jsonl")
    expected_keys = [(score["record_id"], score["slot"]) for score in prior_scores]
    maximum_mass_error = maximum_loss_error = 0.0
    fixed_queries = control_queries = independent_control_queries = 0

    def check_prediction(saved, expected):
        nonlocal maximum_mass_error, maximum_loss_error
        for name in ["top1", "top5", "top10", "known_in_training"]:
            assert saved[name] == expected[name]
        maximum_mass_error = max(maximum_mass_error, abs(saved["model_top_mass"] - expected["model_top_mass"]))
        maximum_loss_error = max(maximum_loss_error, abs(saved["bucket_loss_bits"] - expected["bucket_loss_bits"]))
        if "suggestions" in saved:
            assert [item["code"] for item in saved["suggestions"]] == expected["codes"]
            maximum_mass_error = max(maximum_mass_error, max(abs(item["model_mass"] - mass) for item, mass in zip(saved["suggestions"], expected["masses"])))

    def check_correspondence(scores):
        assert [(score["record_id"], score["slot"]) for score in scores] == expected_keys
        for score in scores:
            row = row_lookup[score["record_id"]]
            assert score["actual"] == row["seq"][score["slot"]]
            assert score["fold"] == fold_lookup[score["record_id"]]
            assert score["group"] == group_lookup[score["record_id"]]
            assert score["length"] == len(row["seq"])

    for name, record in result["variants"].items():
        scores = module.base.read_jsonl(folder / (name + "_slot_audit.jsonl"))
        check_correspondence(scores)
        assert module.base.summarize(scores) == record["summary"]
        for fold in range(5):
            train = [row for i, row in enumerate(rows) if assignments[i] != fold]
            fitted = count_model(train, result["folds"][fold]["fixed_alpha"], record["options"], module.helper.UNKNOWN)
            for saved in scores:
                if saved["fold"] == fold:
                    expected = independent_prediction(row_lookup[saved["record_id"]], saved["slot"], fitted, record["options"], module.helper.UNKNOWN)
                    check_prediction(saved, expected)
                    fixed_queries += 1
        if name == "no_end_factor":
            assert all(a["suggestions"] == b["suggestions"] for a, b in zip(prior_scores, scores) if a["position"] != "final")
        if name == "unigram_start":
            assert all(a["suggestions"] == b["suggestions"] for a, b in zip(prior_scores, scores) if a["position"] != "initial")
    for family, record in result["order_controls"].items():
        interior = family == "interior_shuffle"
        pooled_bins = np.zeros((5, 3))
        for replicate in record["replicates"]:
            scores = module.base.read_jsonl(folder / family / f"replicate_{replicate['replicate']:02d}.jsonl")
            check_correspondence(scores)
            assert module.base.summarize(scores) == replicate["summary"]
            control_queries += len(scores)
            for score in scores:
                bin_index = next(i for i, (lower, upper) in enumerate(module.base.BINS) if lower <= score["model_top_mass"] < upper)
                pooled_bins[bin_index] += [1, score["model_top_mass"], score["top1"]]
            for audit in replicate["training_audits"]:
                fold = audit["fold"]
                train = [row for i, row in enumerate(rows) if assignments[i] != fold]
                shuffled, mobility = module.permute_training(train, audit["seed"], interior)
                for field, value in mobility.items():
                    assert audit[field] == value
                assert Counter(sign for row in train for sign in row["seq"]) == Counter(sign for row in shuffled for sign in row["seq"])
                if interior:
                    assert Counter(row["seq"][0] for row in train) == Counter(row["seq"][0] for row in shuffled)
                    assert Counter(row["seq"][-1] for row in train) == Counter(row["seq"][-1] for row in shuffled)
                fitted = count_model(shuffled, result["folds"][fold]["fixed_alpha"], {}, module.helper.UNKNOWN)
                fold_scores = [score for score in scores if score["fold"] == fold]
                sample = []
                for position in ["initial", "internal", "final"]:
                    sample.extend([score for score in fold_scores if score["position"] == position][:2])
                sample.extend([score for score in fold_scores if not score["known_in_training"]][:2])
                for saved in sample:
                    expected = independent_prediction(row_lookup[saved["record_id"]], saved["slot"], fitted, {}, module.helper.UNKNOWN)
                    check_prediction(saved, expected)
                    independent_control_queries += 1
        for saved_bin, actual_bin in zip(record["pooled_confidence_audit"], pooled_bins):
            assert saved_bin["slots_across_replicates"] == int(actual_bin[0])
            if actual_bin[0]:
                assert abs(saved_bin["mean_model_mass"] - actual_bin[1] / actual_bin[0]) < 1e-12
                assert abs(saved_bin["exact_accuracy"] - actual_bin[2] / actual_bin[0]) < 1e-12
    assert maximum_mass_error < 1e-12 and maximum_loss_error < 1e-10
    report = {"passed": True, "fixed_variant_queries_checked_independently": fixed_queries,
              "control_queries_with_correspondence_and_summary_checks": control_queries,
              "control_queries_checked_by_independent_counts": independent_control_queries,
              "maximum_probability_error": maximum_mass_error, "maximum_bucket_loss_error": maximum_loss_error,
              "checks": ["protocol_prior_and_code_hashes", "all_fixed_variant_rankings_and_losses", "all_query_fold_group_correspondence", "direct_boundary_locality", "all_twenty_replicate_summaries", "all_shuffle_count_and_endpoint_invariants", "stratified_control_prediction_samples", "pooled_calibration_bins"],
              "audit_source_sha256": digest(__file__)}
    output = HERE / "verification.json"
    if output.exists():
        raise FileExistsError("Refusing existing audit record")
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
