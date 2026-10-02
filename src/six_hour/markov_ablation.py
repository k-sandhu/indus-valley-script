"""Post-outcome boundary and training-order study using frozen comparator code."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil
import sys
import time

import numpy as np

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / "src/methods/conditional_structure.py").exists() and (parent / "knowledge").is_dir())
PRIOR = ROOT / "experiments/2026-10-02-six-hour/markov-baseline/main"
VARIANTS = {
    "no_end_factor": {"use_end": False},
    "glyph_only_fit": {"use_end": False, "glyph_only": True},
    "unigram_start": {"unigram_start": True},
    "unigram_start_no_end_factor": {"unigram_start": True, "use_end": False},
    "unigram_start_glyph_only_fit": {"unigram_start": True, "use_end": False, "glyph_only": True},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Populate the import name used inside the frozen comparator with its frozen helper.
sys.path.insert(0, str(ROOT / "src"))
helper = load_module("methods.conditional_structure", PRIOR / "conditional_structure_snapshot.py")
base = load_module("frozen_markov_comparator", PRIOR / "code_snapshot.py")


class AblatedRestorer(base.MarkovRestorer):
    def __init__(self, rows, alpha, use_end=True, unigram_start=False, glyph_only=False):
        super().__init__(rows, alpha)
        self.use_end = use_end
        if unigram_start:
            self.start = self.unigram.copy()
        if glyph_only:
            counts = np.zeros((len(self.signs), len(self.signs)))
            for row in rows:
                for left, right in zip(row["seq"][:-1], row["seq"][1:]):
                    counts[self.index[left], self.index[right]] += 1
            self.transition = (counts + alpha * self.unigram) / (counts.sum(axis=1)[:, None] + alpha)
            assert not use_end
            assert np.allclose(self.transition.sum(axis=1), 1.0)

    def distribution(self, row, slot):
        sequence = row["seq"]
        if slot:
            previous = self.index.get(sequence[slot - 1], self.index[helper.UNKNOWN])
            score = self.transition[previous, :self.end_index].copy()
        else:
            score = self.start.copy()
        if slot + 1 < len(sequence):
            successor = self.index.get(sequence[slot + 1], self.index[helper.UNKNOWN])
            score *= self.transition[:, successor]
        elif self.use_end:
            score *= self.transition[:, self.end_index]
        return score / score.sum()


def permute_training(rows, seed, interior=False):
    rng = random.Random(seed)
    transformed = []
    changed_rows = changed_slots = movable_rows = movable_slots = 0
    for row in rows:
        original = row["seq"]
        sequence = list(original)
        start, stop = (1, len(sequence) - 1) if interior else (0, len(sequence))
        part = sequence[start:stop]
        if len(set(part)) > 1:
            movable_rows += 1
            movable_slots += len(part)
        rng.shuffle(part)
        sequence[start:stop] = part
        sequence = tuple(sequence)
        assert Counter(sequence) == Counter(original)
        if interior:
            assert sequence[0] == original[0] and sequence[-1] == original[-1]
        changed_rows += sequence != original
        changed_slots += sum(a != b for a, b in zip(sequence, original))
        transformed.append(dict(row, seq=sequence))
    return transformed, {"training_rows": len(rows), "training_slots": sum(len(row["seq"]) for row in rows),
                         "movable_rows": movable_rows, "movable_slots": movable_slots,
                         "changed_rows": changed_rows, "changed_slots": changed_slots}


def subset_metrics(scores):
    result = {"slots": len(scores), **{metric: float(np.mean([score[metric] for score in scores])) for metric in ["top1", "top5", "top10", "bucket_loss_bits"]},
              "unknown_true_rate": float(np.mean([not score["known_in_training"] for score in scores]))}
    bins = []
    for lower, upper in base.BINS:
        part = [score for score in scores if lower <= score["model_top_mass"] < upper]
        bins.append({"mass_interval": [lower, min(upper, 1.0)], "slots": len(part),
                     "mean_model_mass": float(np.mean([score["model_top_mass"] for score in part])) if part else None,
                     "exact_accuracy": float(np.mean([score["top1"] for score in part])) if part else None})
    result["confidence_audit"] = bins
    result["expected_calibration_error"] = sum(item["slots"] / len(scores) * abs(item["mean_model_mass"] - item["exact_accuracy"]) for item in bins if item["slots"])
    return result


def breakdowns(scores, frequencies):
    masks = {position: [score for score in scores if score["position"] == position] for position in ["initial", "internal", "final"]}
    masks.update({label: [score for score in scores if lower <= frequencies[score["actual"]] <= upper] for label, lower, upper in [("frequency_1", 1, 1), ("frequency_2-4", 2, 4), ("frequency_5-19", 5, 19), ("frequency_20+", 20, len(scores))]})
    return {name: subset_metrics(part) for name, part in masks.items()}


def compare_subset(original, changed, repeats, seed=142):
    metrics = ["top1", "top5", "bucket_loss_bits"]
    grouped = defaultdict(lambda: np.zeros(4))
    for a, b in zip(original, changed):
        assert (a["record_id"], a["slot"], a["group"]) == (b["record_id"], b["slot"], b["group"])
        grouped[a["group"]] += [float(b[metric]) - float(a[metric]) for metric in metrics] + [1.0]
    array = np.asarray([grouped[group] for group in sorted(grouped)])
    point = array.sum(axis=0)
    rng = np.random.default_rng(seed)
    samples = []
    for offset in range(0, repeats, 250):
        indices = rng.integers(0, len(array), size=(min(250, repeats - offset), len(array)))
        totals = array[indices].sum(axis=1)
        samples.append(totals[:, :3] / totals[:, 3, None])
    draws = np.concatenate(samples)
    return {"groups": len(array), "slots": int(point[3]), "bootstrap_repeats": repeats, "seed": seed,
            "direction": "changed minus frozen full model",
            "metrics": {metric: {"difference": float(point[index] / point[3]), "cluster_bootstrap_95_ci": np.quantile(draws[:, index], [.025, .975]).tolist()} for index, metric in enumerate(metrics)}}


def compare_breakdowns(original, changed, frequencies, repeats):
    filters = {position: lambda score, value=position: score["position"] == value for position in ["initial", "internal", "final"]}
    for label, lower, upper in [("frequency_1", 1, 1), ("frequency_2-4", 2, 4), ("frequency_5-19", 5, 19), ("frequency_20+", 20, len(original))]:
        filters[label] = lambda score, low=lower, high=upper: low <= frequencies[score["actual"]] <= high
    return {name: compare_subset([score for score in original if keep(score)], [score for score in changed if keep(score)], repeats) for name, keep in filters.items()}


def self_test():
    rows = [{"seq": sequence, "record_id": str(i), "stratum": ("s", "t"), "artifact": str(i), "artifact_aliases": [str(i)]} for i, sequence in enumerate([("A", "B", "C", "D"), ("A", "B", "C", "D"), ("B", "C", "A", "D"), ("C", "A", "D", "B"), ("A", "D", "B", "C")])]
    query = {"seq": ("A", "B", "C", "D")}
    full = base.MarkovRestorer(rows, 2)
    checks = []
    for name, options in VARIANTS.items():
        model = AblatedRestorer(rows, 2, **options)
        for slot in range(4):
            likelihoods = []
            for candidate in model.signs:
                sequence = list(query["seq"])
                sequence[slot] = candidate
                indices = [model.index[sign] for sign in sequence]
                product = model.start[indices[0]]
                for left, right in zip(indices[:-1], indices[1:]):
                    product *= model.transition[left, right]
                if model.use_end:
                    product *= model.transition[indices[-1], model.end_index]
                likelihoods.append(product)
            expected = np.asarray(likelihoods) / sum(likelihoods)
            assert np.allclose(model.distribution(query, slot), expected, rtol=1e-12, atol=1e-14)
            hidden = list(query["seq"])
            hidden[slot] = "HIDDEN"
            assert np.array_equal(model.distribution({"seq": hidden}, slot), model.distribution(query, slot))
        unseen = model.distribution({"seq": ("UNSEEN_LEFT", "?", "UNSEEN_RIGHT")}, 1)
        assert np.isfinite(unseen).all() and np.all(unseen > 0) and abs(unseen.sum() - 1) < 1e-12
        checks.append(name + "_likelihood_target_independence_unknowns")
    no_end = AblatedRestorer(rows, 2, use_end=False)
    no_start = AblatedRestorer(rows, 2, unigram_start=True)
    for slot in range(3):
        assert np.array_equal(full.distribution(query, slot), no_end.distribution(query, slot))
    for slot in range(1, 4):
        assert np.array_equal(full.distribution(query, slot), no_start.distribution(query, slot))
    checks.append("locality_of_direct_boundary_ablation")
    glyph_only = AblatedRestorer(rows, 2, use_end=False, glyph_only=True)
    assert glyph_only.transition.shape == (len(glyph_only.signs), len(glyph_only.signs))
    assert np.allclose(glyph_only.transition.sum(axis=1), 1)
    assert not np.allclose(no_end.distribution(query, 1), glyph_only.distribution(query, 1))
    checks.append("glyph_only_refit_has_distinct_internal_normalization")
    for interior in [False, True]:
        shuffled, mobility = permute_training(rows, 13, interior)
        assert all(a["stratum"] == b["stratum"] and a["artifact_aliases"] == b["artifact_aliases"] for a, b in zip(rows, shuffled))
        assert np.array_equal(full.unigram, base.MarkovRestorer(shuffled, 2).unigram)
        if interior:
            assert np.array_equal(full.start, base.MarkovRestorer(shuffled, 2).start)
        assert mobility["changed_rows"] > 0
        checks.append("interior_shuffle_preservation" if interior else "full_shuffle_preservation")
    return {"passed": True, "checks": checks, "count": len(checks), "explicit_likelihood_comparisons": 20}


def save_scores(path, scores):
    path.write_text("\n".join(json.dumps(score) for score in scores) + "\n", encoding="utf-8")


def run(args):
    started = time.monotonic()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"Refusing existing endpoint: {output}")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    prior_result = json.loads((PRIOR / "results.json").read_text(encoding="utf-8"))
    try:
        assert digest(PRIOR / "code_snapshot.py") == prior_result["source_sha256"]
        assert digest(PRIOR / "conditional_structure_snapshot.py") == prior_result["helper_sha256"]
        input_path = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
        assert digest(input_path) == prior_result["input_sha256"]
        tests = self_test()
        rows, _ = helper.load_records(input_path, min_length=3, unique=True)
        groups = helper.group_records(rows)
        assignments, loads = helper.make_folds(rows, groups, 5, 20261006)
        group_lookup = {rows[i]["record_id"]: group for group, indices in enumerate(groups) for i in indices}
        full = base.read_jsonl(PRIOR / "markov_slot_audit.jsonl")
        original = ROOT / "results/restoration"
        old_benchmark = json.loads((original / "benchmark.json").read_text(encoding="utf-8"))
        base.verify_saved(rows, groups, assignments, loads, old_benchmark, base.read_jsonl(original / "baseline_slot_audit.jsonl"), base.read_jsonl(original / "local_slot_audit.jsonl"))
        frequencies = Counter(score["actual"] for score in full)
        scored = {name: [] for name in VARIANTS}
        folds = []
        for fold in range(5):
            train = [row for i, row in enumerate(rows) if assignments[i] != fold]
            test = [row for i, row in enumerate(rows) if assignments[i] == fold]
            assert not {alias for row in train for alias in row["artifact_aliases"]}.intersection({alias for row in test for alias in row["artifact_aliases"]})
            assert not {row["seq"] for row in train}.intersection({row["seq"] for row in test})
            alpha = prior_result["folds"][fold]["chosen_alpha"]
            replay = base.MarkovRestorer(train, alpha).score_rows(test, details=True)
            saved = [score for score in full if score["fold"] == fold]
            for a, b in zip(replay, saved):
                for key in a:
                    assert a[key] == b[key], (fold, key)
            for name, options in VARIANTS.items():
                model = AblatedRestorer(train, alpha, **options)
                assert model.signs == base.MarkovRestorer(train, alpha).signs
                predictions = model.score_rows(test, details=True)
                for score in predictions:
                    score["fold"] = fold
                    score["group"] = group_lookup[score["record_id"]]
                scored[name].extend(predictions)
            folds.append({"fold": fold, "train_texts": len(train), "test_texts": len(test), "fixed_alpha": alpha})
        results = {"design": "Post-outcome Markov boundary and training-order mechanism study", "parameters": vars(args),
                   "source_sha256": digest(__file__), "protocol_sha256": digest(output.parent / "PROTOCOL.md"),
                   "input_sha256": digest(input_path), "prior_result_sha256": digest(PRIOR / "results.json"),
                   "prior_code_sha256": digest(PRIOR / "code_snapshot.py"), "prior_helper_sha256": digest(PRIOR / "conditional_structure_snapshot.py"),
                   "self_tests": tests, "reference_replayed_exactly": True, "folds": folds,
                   "query_count": len(full), "text_count": len(rows), "component_count": len(groups),
                   "reference": {"summary": base.summarize(full), "breakdowns": breakdowns(full, frequencies)},
                   "variants": {}, "order_controls": {}}
        for name, scores in scored.items():
            for a, b in zip(full, scores):
                assert (a["record_id"], a["slot"], a["actual"], a["fold"], a["group"], a["known_in_training"]) == (b["record_id"], b["slot"], b["actual"], b["fold"], b["group"], b["known_in_training"])
            save_scores(output / (name + "_slot_audit.jsonl"), scores)
            results["variants"][name] = {"options": VARIANTS[name], "summary": base.summarize(scores), "breakdowns": breakdowns(scores, frequencies),
                                          "paired_against_full": base.paired(full, scores, args.bootstrap),
                                          "paired_breakdowns": compare_breakdowns(full, scores, frequencies, args.bootstrap)}
            print(json.dumps({"stage": "ablation", "name": name, "top1": results["variants"][name]["summary"]["top1"], "seconds": time.monotonic() - started}), flush=True)
        for family, interior in [("all_slot_shuffle", False), ("interior_shuffle", True)]:
            family_dir = output / family
            family_dir.mkdir()
            replicates = []
            mean_slots = np.zeros((len(full), 4))
            confidence_totals = np.zeros((len(base.BINS), 3))
            for replicate in range(args.shuffle_replicates):
                scores = []
                training_audits = []
                for fold in range(5):
                    train = [row for i, row in enumerate(rows) if assignments[i] != fold]
                    test = [row for i, row in enumerate(rows) if assignments[i] == fold]
                    seed = 20261020 + 100 * replicate + fold + (100000 if interior else 0)
                    shuffled, mobility = permute_training(train, seed, interior)
                    original_model = base.MarkovRestorer(train, prior_result["folds"][fold]["chosen_alpha"])
                    model = base.MarkovRestorer(shuffled, prior_result["folds"][fold]["chosen_alpha"])
                    assert model.signs == original_model.signs and np.array_equal(model.unigram, original_model.unigram)
                    if interior:
                        assert np.array_equal(model.start, original_model.start)
                        assert np.array_equal(model.transition[:, model.end_index], original_model.transition[:, original_model.end_index])
                    assert all(a["stratum"] == b["stratum"] and a["artifact_aliases"] == b["artifact_aliases"] for a, b in zip(train, shuffled))
                    test_sequences = {row["seq"] for row in test}
                    mobility["accidental_shuffled_training_matches_to_test_strings"] = sum(row["seq"] in test_sequences for row in shuffled)
                    mobility["seed"] = seed
                    mobility["fold"] = fold
                    training_audits.append(mobility)
                    predictions = model.score_rows(test, details=False)
                    for score in predictions:
                        score["fold"] = fold
                        score["group"] = group_lookup[score["record_id"]]
                    scores.extend(predictions)
                for index, (a, b) in enumerate(zip(full, scores)):
                    assert (a["record_id"], a["slot"], a["actual"], a["fold"], a["group"]) == (b["record_id"], b["slot"], b["actual"], b["fold"], b["group"])
                    mean_slots[index] += [b["top1"], b["top5"], b["top10"], b["bucket_loss_bits"]]
                    bin_index = min(int(b["model_top_mass"] / 0.2), 4)
                    confidence_totals[bin_index] += [1, b["model_top_mass"], b["top1"]]
                save_scores(family_dir / f"replicate_{replicate:02d}.jsonl", scores)
                replicates.append({"replicate": replicate, "summary": base.summarize(scores), "breakdowns": breakdowns(scores, frequencies), "training_audits": training_audits})
                print(json.dumps({"stage": "order_control", "family": family, "replicate": replicate, "top1": replicates[-1]["summary"]["top1"], "seconds": time.monotonic() - started}), flush=True)
            mean_slots /= args.shuffle_replicates
            mean_predictions = []
            for index, item in enumerate(full):
                changed = dict(item)
                changed.update({metric: float(mean_slots[index, column]) for column, metric in enumerate(["top1", "top5", "top10", "bucket_loss_bits"])})
                mean_predictions.append(changed)
            means = {metric: float(np.mean([record["summary"][metric] for record in replicates])) for metric in ["top1", "top5", "top10", "bucket_cross_entropy_bits", "expected_calibration_error"]}
            spread = {metric: [min(record["summary"][metric] for record in replicates), max(record["summary"][metric] for record in replicates)] for metric in means}
            pooled_confidence = [{"mass_interval": [lower, min(upper, 1)], "slots_across_replicates": int(values[0]), "mean_model_mass": float(values[1] / values[0]) if values[0] else None, "exact_accuracy": float(values[2] / values[0]) if values[0] else None} for (lower, upper), values in zip(base.BINS, confidence_totals)]
            results["order_controls"][family] = {"replicates": replicates, "mean_metrics": means, "replicate_min_max": spread,
                                                "pooled_confidence_audit": pooled_confidence,
                                                "mean_control_paired_against_full": compare_subset(full, mean_predictions, args.bootstrap),
                                                "mean_control_paired_breakdowns": compare_breakdowns(full, mean_predictions, frequencies, args.bootstrap),
                                                "interval_scope": "Component resampling of per-mask means over the declared twenty training orders; seed spread reported separately."}
        results["runtime_seconds"] = time.monotonic() - started
        (output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"stage": "ablation_complete", "seconds": results["runtime_seconds"]}), flush=True)
    except Exception as error:
        (output / "failure.json").write_text(json.dumps({"exception": type(error).__name__, "message": str(error), "source_sha256": digest(__file__), "elapsed_seconds": time.monotonic() - started}, indent=2), encoding="utf-8")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="experiments/2026-10-02-six-hour/markov-ablation/main")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--shuffle-replicates", type=int, default=20)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))
    else:
        run(args)
