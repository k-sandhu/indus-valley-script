"""First-order restoration comparator on the preserved artifact-held-out masks."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from methods.conditional_structure import UNKNOWN, Model, group_records, load_records, make_folds

GRID = [20, 100, 500, 2000]
END = "__END_OF_TEXT__"
BINS = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.000001)]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


class MarkovRestorer:
    """Time-homogeneous transitions, with an empirical initial distribution."""

    def __init__(self, rows, alpha):
        self.signs = sorted({s for row in rows for s in row["seq"]}) + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        n = len(self.signs)
        self.end_index = n
        unigram = np.full(n, 0.5)
        starts = np.zeros(n)
        counts = np.zeros((n, n + 1))
        for row in rows:
            sequence = [self.index[s] for s in row["seq"]]
            starts[sequence[0]] += 1
            for i, current in enumerate(sequence):
                unigram[current] += 1
                successor = sequence[i + 1] if i + 1 < len(sequence) else n
                counts[current, successor] += 1
        self.unigram = unigram / unigram.sum()
        destination = np.append(unigram, len(rows) + 0.5)
        self.destination_prior = destination / destination.sum()
        self.start = (starts + alpha * self.unigram) / (len(rows) + alpha)
        self.transition = (counts + alpha * self.destination_prior) / (counts.sum(axis=1)[:, None] + alpha)
        self.alpha = float(alpha)
        assert np.allclose(self.start.sum(), 1.0)
        assert np.allclose(self.transition.sum(axis=1), 1.0)

    def distribution(self, row, slot):
        sequence = row["seq"]
        if slot:
            previous = self.index.get(sequence[slot - 1], self.index[UNKNOWN])
            score = self.transition[previous, :self.end_index].copy()
        else:
            score = self.start.copy()
        following = (self.index.get(sequence[slot + 1], self.index[UNKNOWN])
                     if slot + 1 < len(sequence) else self.end_index)
        score *= self.transition[:, following]
        return score / score.sum()

    def score_rows(self, rows, details=False):
        scores = []
        for row in rows:
            for slot, actual in enumerate(row["seq"]):
                distribution = self.distribution(row, slot)
                order = np.argsort(-distribution, kind="stable")
                predictions = [self.signs[i] for i in order]
                actual_index = self.index.get(actual, self.index[UNKNOWN])
                score = {"record_id": row["record_id"], "artifact": row["artifact"],
                         "slot": slot, "length": len(row["seq"]), "actual": actual,
                         "position": "initial" if slot == 0 else "final" if slot + 1 == len(row["seq"]) else "internal",
                         "known_in_training": actual in self.index,
                         "top1": predictions[0] == actual,
                         "top5": actual in predictions[:5], "top10": actual in predictions[:10],
                         "model_top_mass": float(distribution[order[0]]),
                         "top_is_unknown": predictions[0] == UNKNOWN,
                         "bucket_loss_bits": -math.log2(float(distribution[actual_index]))}
                if details:
                    score["suggestions"] = [{"code": self.signs[i], "model_mass": float(distribution[i])} for i in order[:10]]
                    score["site"] = row.get("site")
                    score["object_type"] = row.get("object_type")
                scores.append(score)
        return scores


def tune(train, seed):
    groups = group_records(train)
    assignments, _ = make_folds(train, groups, 3, seed)
    totals = Counter()
    slot_count = sum(len(row["seq"]) for row in train)
    for fold in range(3):
        fit = [row for i, row in enumerate(train) if assignments[i] != fold]
        test = [row for i, row in enumerate(train) if assignments[i] == fold]
        for alpha in GRID:
            scores = MarkovRestorer(fit, alpha).score_rows(test)
            totals[alpha] += sum(score["top1"] for score in scores)
    chosen = max(GRID, key=lambda alpha: (totals[alpha], alpha))
    return chosen, {str(alpha): totals[alpha] / slot_count for alpha in GRID}


def summarize(scores):
    by_text, by_code = defaultdict(list), defaultdict(list)
    for score in scores:
        by_text[score["record_id"]].append(score)
        by_code[score["actual"]].append(score)
    result = {"slots": len(scores), "texts": len(by_text), "glyph_types": len(by_code)}
    for metric in ["top1", "top5", "top10"]:
        result[metric] = float(np.mean([score[metric] for score in scores]))
    result["equal_text_weight"] = {metric: float(np.mean([np.mean([score[metric] for score in group]) for group in by_text.values()])) for metric in ["top1", "top5", "top10"]}
    result["macro_type"] = {metric: float(np.mean([np.mean([score[metric] for score in group]) for group in by_code.values()])) for metric in ["top1", "top5", "top10"]}
    result["unknown_true_rate"] = float(np.mean([not score["known_in_training"] for score in scores]))
    result["unknown_prediction_rate"] = float(np.mean([score["top_is_unknown"] for score in scores]))
    result["bucket_cross_entropy_bits"] = float(np.mean([score["bucket_loss_bits"] for score in scores]))
    result["positions"] = {position: {"slots": len(part), **{metric: float(np.mean([score[metric] for score in part])) for metric in ["top1", "top5", "top10"]}} for position in ["initial", "internal", "final"] for part in [[score for score in scores if score["position"] == position]]}
    result["confidence_audit"] = []
    ece = 0.0
    for lower, upper in BINS:
        part = [score for score in scores if lower <= score["model_top_mass"] < upper]
        mean_mass = float(np.mean([score["model_top_mass"] for score in part])) if part else None
        accuracy = float(np.mean([score["top1"] for score in part])) if part else None
        if part:
            ece += len(part) / len(scores) * abs(mean_mass - accuracy)
        result["confidence_audit"].append({"mass_interval": [lower, min(upper, 1.0)], "slots": len(part), "mean_model_mass": mean_mass, "exact_accuracy": accuracy})
    result["expected_calibration_error"] = ece
    result["top_label_brier"] = float(np.mean([(score["model_top_mass"] - int(score["top1"])) ** 2 for score in scores]))
    result["frequency_strata"] = {}
    for label, lower, upper in [("1", 1, 1), ("2-4", 2, 4), ("5-19", 5, 19), ("20+", 20, len(scores))]:
        codes = {code for code, part in by_code.items() if lower <= len(part) <= upper}
        part = [score for score in scores if score["actual"] in codes]
        result["frequency_strata"][label] = {"slots": len(part), "types": len(codes), **{metric: float(np.mean([score[metric] for score in part])) for metric in ["top1", "top5", "top10"]}, "unknown_in_training_rate": float(np.mean([not score["known_in_training"] for score in part]))}
    return result


def paired(first, second, repeats=10000, seed=142):
    """Second minus first; cluster resampling with fixed evaluation weights."""
    frequencies = Counter(score["actual"] for score in first)
    columns = [(metric, "slot") for metric in ["top1", "top5", "top10", "bucket_loss_bits", "top_label_brier"]]
    columns += [("top1", "text"), ("top1", "type"), ("top5", "type")]
    sums = defaultdict(lambda: np.zeros((len(columns), 2)))
    for a, b in zip(first, second):
        assert (a["record_id"], a["slot"], a["group"]) == (b["record_id"], b["slot"], b["group"])
        for index, (metric, weighting) in enumerate(columns):
            weight = 1 / a["length"] if weighting == "text" else 1 / frequencies[a["actual"]] if weighting == "type" else 1.0
            if metric == "top_label_brier":
                delta = (b["model_top_mass"] - int(b["top1"])) ** 2 - (a["model_top_mass"] - int(a["top1"])) ** 2
            else:
                delta = float(b[metric]) - float(a[metric])
            sums[a["group"]][index] += weight * np.array([delta, 1.0])
    array = np.asarray([sums[group] for group in sorted(sums)])
    point = array.sum(axis=0)
    rng = np.random.default_rng(seed)
    draws = []
    for offset in range(0, repeats, 200):
        indices = rng.integers(0, len(array), size=(min(200, repeats - offset), len(array)))
        totals = array[indices].sum(axis=1)
        draws.append(totals[:, :, 0] / totals[:, :, 1])
    samples = np.concatenate(draws)
    return {"groups": len(array), "bootstrap_repeats": repeats, "seed": seed,
            "direction": "second minus first", "type_interval_weights": "Inverse true-code counts fixed from the complete benchmark; resampled weighted-slot ratio.",
            "metrics": {f"{metric}_{weighting}": {"difference": float(point[i, 0] / point[i, 1]), "cluster_bootstrap_95_ci": np.quantile(samples[:, i], [.025, .975]).tolist()} for i, (metric, weighting) in enumerate(columns)}}


def verify_saved(rows, groups, assignments, loads, benchmark, pm, pmb):
    assert len(rows) == 1596 and len(groups) == 1526
    assert sum(len(row["seq"]) for row in rows) == 8009
    assert loads == benchmark["fold_token_loads"]
    lookup = {row["record_id"]: (i, row) for i, row in enumerate(rows)}
    group_lookup = {rows[i]["record_id"]: g for g, group in enumerate(groups) for i in group}
    expected = {(row["record_id"], slot) for row in rows for slot in range(len(row["seq"]))}
    for label, scores in [("PM", pm), ("PMB", pmb)]:
        keys = [(score["record_id"], score["slot"]) for score in scores]
        assert len(keys) == len(set(keys)) == 8009, f"Duplicate or missing queries in {label}"
        assert set(keys) == expected
        for score in scores:
            i, row = lookup[score["record_id"]]
            assert score["actual"] == row["seq"][score["slot"]]
            assert score["length"] == len(row["seq"])
            assert score["artifact"] == row["artifact"]
            assert score["fold"] == assignments[i]
            assert score["group"] == group_lookup[score["record_id"]]
        original = benchmark["models"]["baseline" if label == "PM" else "local"]
        current = summarize(scores)
        for metric in ["top1", "top5", "top10", "unknown_true_rate", "unknown_prediction_rate", "bucket_cross_entropy_bits"]:
            assert abs(current[metric] - original[metric]) < 1e-12, (label, metric)
    for a, b in zip(pm, pmb):
        assert (a["record_id"], a["slot"], a["actual"], a["fold"], a["group"]) == (b["record_id"], b["slot"], b["actual"], b["fold"], b["group"])
    return group_lookup, {"verified_queries_per_model": 8009, "texts": len(rows), "components": len(groups), "fold_token_loads": loads, "matched_fields": ["record_id", "slot", "actual", "length", "artifact", "group", "fold"], "saved_metrics_reproduced": True}


def self_test():
    rows = [{"seq": sequence, "stratum": ("site", "type")} for sequence in [("A", "B", "C"), ("A", "B", "C"), ("B", "C", "A"), ("C", "A", "C"), ("A", "C", "B")]]
    model = MarkovRestorer(rows, 2.0)
    reference = Model(rows, 2.0)
    tests = []
    assert model.signs == reference.signs and np.array_equal(model.unigram, reference.unigram)
    tests.append("alphabet_and_unigram_match_existing_model")
    query = {"seq": ("A", "B", "C")}
    for slot in range(3):
        brute = []
        for candidate in model.signs:
            sequence = list(query["seq"])
            sequence[slot] = candidate
            indices = [model.index[s] for s in sequence]
            likelihood = model.start[indices[0]]
            for left, right in zip(indices[:-1], indices[1:]):
                likelihood *= model.transition[left, right]
            likelihood *= model.transition[indices[-1], model.end_index]
            brute.append(likelihood)
        brute = np.asarray(brute) / sum(brute)
        assert np.allclose(model.distribution(query, slot), brute, rtol=1e-12, atol=1e-14)
        tests.append(f"complete_string_likelihood_slot_{slot}")
        hidden = list(query["seq"])
        hidden[slot] = "ERASED"
        assert np.array_equal(model.distribution({"seq": hidden}, slot), model.distribution(query, slot))
    tests.append("hidden_target_independence_all_positions")
    assert not np.allclose(model.distribution({"seq": ("A", "?", "B")}, 1), model.distribution({"seq": ("A", "?", "C")}, 1))
    tests.append("successor_transition_changes_predictions")
    assert not np.allclose(model.distribution(query, 2), model.transition[model.index["B"], :model.end_index] / model.transition[model.index["B"], :model.end_index].sum())
    tests.append("end_transition_changes_final_predictions")
    unknown = model.distribution({"seq": ("UNSEEN_LEFT", "?", "UNSEEN_RIGHT")}, 1)
    assert np.isfinite(unknown).all() and np.all(unknown > 0) and abs(unknown.sum() - 1) < 1e-12
    assert END not in model.signs and len(unknown) == len(model.signs)
    tests.append("unknown_neighbors_and_end_exclusion")
    return {"passed": True, "checks": tests, "count": len(tests)}


def run(args):
    started = time.monotonic()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"Refusing existing run: {output}")
    output.mkdir(parents=True)
    try:
        tests = self_test()
        original = ROOT / "results/restoration"
        input_path = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
        helper_path = ROOT / "src/methods/conditional_structure.py"
        benchmark = json.loads((original / "benchmark.json").read_text(encoding="utf-8"))
        assert digest(input_path) == benchmark["input_sha256"], "Input hash differs from the saved benchmark"
        assert digest(helper_path) == benchmark["model_dependency_sha256"], "Grouping helper differs from the saved benchmark"
        assert benchmark["parameters"]["seed"] == args.seed and benchmark["collapse_mapping"] is None
        pm = read_jsonl(original / "baseline_slot_audit.jsonl")
        pmb = read_jsonl(original / "local_slot_audit.jsonl")
        rows, exclusions = load_records(input_path, min_length=3, unique=True)
        groups = group_records(rows)
        assignments, loads = make_folds(rows, groups, 5, args.seed)
        group_lookup, correspondence = verify_saved(rows, groups, assignments, loads, benchmark, pm, pmb)
        scores, folds = [], []
        for fold in range(5):
            train = [row for i, row in enumerate(rows) if assignments[i] != fold]
            test = [row for i, row in enumerate(rows) if assignments[i] == fold]
            chosen, inner = tune(train, args.seed + fold)
            model = MarkovRestorer(train, chosen)
            assert model.signs == Model(train, chosen).signs
            fold_scores = model.score_rows(test, details=True)
            for score in fold_scores:
                score["fold"] = fold
                score["group"] = group_lookup[score["record_id"]]
            scores.extend(fold_scores)
            folds.append({"fold": fold, "train_texts": len(train), "test_texts": len(test), "chosen_alpha": chosen, "inner_top1": inner, "vocabulary_size_including_unknown": len(model.signs)})
            print(json.dumps({"stage": "markov_fold", "fold": fold, "alpha": chosen, "seconds": time.monotonic() - started}), flush=True)
        for baseline in [pm, pmb]:
            for a, b in zip(scores, baseline):
                assert (a["record_id"], a["slot"], a["actual"], a["fold"], a["group"], a["known_in_training"]) == (b["record_id"], b["slot"], b["actual"], b["fold"], b["group"], b["known_in_training"])
        result = {"design": "New conventional time-homogeneous first-order Markov comparator; exact saved outer queries",
                  "parameters": vars(args), "source_sha256": digest(__file__), "input_sha256": digest(input_path), "helper_sha256": digest(helper_path),
                  "saved_sources": {name: digest(original / name) for name in ["benchmark.json", "baseline_slot_audit.jsonl", "local_slot_audit.jsonl"]},
                  "protocol_sha256": digest(output.parent / "PROTOCOL.md"), "self_tests": tests, "correspondence": correspondence,
                  "smoothing_grid": GRID, "folds": folds, "exclusions": exclusions,
                  "models": {"PM": summarize(pm), "Markov": summarize(scores), "PMB": summarize(pmb)},
                  "paired": {"Markov_minus_PM": paired(pm, scores, args.bootstrap), "PMB_minus_Markov": paired(scores, pmb, args.bootstrap)},
                  "runtime_seconds": time.monotonic() - started}
        (output / "markov_slot_audit.jsonl").write_text("\n".join(json.dumps(score) for score in scores) + "\n", encoding="utf-8")
        (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        shutil.copyfile(__file__, output / "code_snapshot.py")
        shutil.copyfile(helper_path, output / "conditional_structure_snapshot.py")
        print(json.dumps({"stage": "markov_complete", "models": {name: {key: summary[key] for key in ["top1", "top5", "expected_calibration_error", "macro_type"]} for name, summary in result["models"].items()}, "seconds": result["runtime_seconds"]}), flush=True)
    except Exception as error:
        (output / "failure.json").write_text(json.dumps({"exception": type(error).__name__, "message": str(error), "source_sha256": digest(__file__), "elapsed_seconds": time.monotonic() - started}, indent=2), encoding="utf-8")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="experiments/2026-10-02-six-hour/markov-baseline/main")
    parser.add_argument("--seed", type=int, default=20261006)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        print(json.dumps(self_test(), indent=2))
    else:
        run(arguments)
