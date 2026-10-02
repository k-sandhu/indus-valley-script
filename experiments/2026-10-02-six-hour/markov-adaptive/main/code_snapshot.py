"""Extra training-count shrinkage on preserved second-order restoration factors."""
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/markov-adaptive"
SOURCES = {
    "conditional_structure.py": ROOT / "experiments/2026-10-02-six-hour/markov-baseline/main/conditional_structure_snapshot.py",
    "markov_baseline.py": ROOT / "experiments/2026-10-02-six-hour/markov-baseline/main/code_snapshot.py",
    "markov_order2.py": ROOT / "experiments/2026-10-02-six-hour/markov-order2/main/code_snapshot.py",
    "direct_review.py": ROOT / "experiments/2026-10-02-six-hour/markov-order2/review-ties/code_snapshot.py"}
EXPECTED = {"conditional_structure.py": "ed150239452339a04ef35f04b5814a236d9bd3ad0b64702e66a0230760de0ca8",
            "markov_baseline.py": "5bdfb4e9629712418001ce362fc4ac08bdce59f3e9f575d2c2ff09b9d6240a3f",
            "markov_order2.py": "900191ff7d498f09be7495c2547ea2c7827aa8c389f60ae963c628544333801a"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def freeze():
    folder = FOLDER / "sources"
    folder.mkdir(exist_ok=True)
    hashes = {}
    for name, path in SOURCES.items():
        hashes[name] = sha(path)
        if name in EXPECTED:
            assert hashes[name] == EXPECTED[name]
        destination = folder / name
        if destination.exists():
            assert sha(destination) == hashes[name]
        else:
            shutil.copyfile(path, destination)
    sys.path.insert(0, str(ROOT / "src"))
    import methods
    load(folder / "conditional_structure.py", "methods.conditional_structure")
    baseline = load(folder / "markov_baseline.py", "markov_baseline")
    baseline.ROOT = ROOT
    second = load(folder / "markov_order2.py", "adaptive_second_snapshot")
    return baseline, second, hashes


BASE, SECOND, HASHES = freeze()
PARAMS, SEEN = [], set()
for a in [5, 20, 100, 500, 2000]:
    for k in [0, 20, 100, 500]:
        key = tuple(sorted([a, k]))
        if key not in SEEN:
            PARAMS.append((a, k))
            SEEN.add(key)
PARAMS.append((None, None))
assert len(PARAMS) == 18


def label(pair):
    return "backoff_only" if pair[0] is None else f"alpha={pair[0]},kappa={pair[1]}"


class Restorer(SECOND.Restorer):
    def __init__(self, rows, alpha, kappa):
        super().__init__(rows, None if kappa is None else alpha)
        self.kappa = kappa
        self.history_counts = Counter()
        for row in rows:
            chain = [self.start_index, self.start_index] + [self.index[s] for s in row["seq"]] + [self.end_index]
            self.history_counts.update(zip(chain[:-2], chain[1:-1]))
        if kappa is not None:
            for history, q2 in list(self.observed.items()):
                n = self.history_counts[history]
                w = n / (n + kappa)
                self.observed[history] = w * q2 + (1 - w) * self.prior(history[1])
            assert all(abs(values.sum() - 1) < 1e-12 for values in self.observed.values())


def tests():
    rows = [{"seq": tuple(s)} for s in ["ABC", "ABC", "ACB", "BAC", "CAC", "BBB", "CAB"]]
    query = {"seq": ("A", "B", "C")}
    findings = []
    for alpha, kappa in [(5, 0), (20, 100), (500, 20), (None, None)]:
        model = Restorer(rows, alpha, kappa)
        for slot in range(3):
            full = []
            for candidate in model.signs:
                values = [model.index[s] for s in query["seq"]]
                values[slot] = model.index[candidate]
                chain = [model.start_index, model.start_index] + values + [model.end_index]
                probability = 1.0
                for a, b, target in zip(chain, chain[1:], chain[2:]):
                    probability *= model.probability(a, b)[target]
                full.append(probability)
            full = np.asarray(full) / sum(full)
            assert np.allclose(full, model.distribution(query, slot), rtol=1e-12, atol=1e-14)
            hidden = list(query["seq"])
            hidden[slot] = "HIDDEN"
            assert np.array_equal(model.distribution(query, slot), model.distribution({"seq": hidden}, slot))
        if kappa == 0:
            original = SECOND.Restorer(rows, alpha)
            assert all(np.array_equal(model.distribution(query, s), original.distribution(query, s)) for s in range(3))
        if kappa is None:
            assert all(np.array_equal(model.distribution(query, s), model.base.distribution(query, s)) for s in range(3))
        findings.append(label((alpha, kappa)))
    identities = 0
    for n in [1, 2, 7, 100, 1000]:
        for alpha, kappa in PARAMS[:-1]:
            prior, c = F(1, 7), n // 2
            mixture = F(n, n + kappa) * F(c + alpha * prior, n + alpha) + F(kappa, n + kappa) * prior
            effective = alpha + kappa + F(alpha * kappa, n)
            assert mixture == F(c + effective * prior, n + effective)
            identities += 1
    return {"status": "pass", "toy_models": findings, "complete_likelihood_and_mask_slots": 12,
            "effective_strength_rational_identities": identities, "normalized_rows": True,
            "exact_second_order_zero_kappa": True, "exact_first_order_infinite_kappa": True}


def tune(rows, seed):
    groups = BASE.group_records(rows)
    assignments, loads = BASE.make_folds(rows, groups, 3, seed)
    losses = Counter()
    successes = {pair: Counter() for pair in PARAMS}
    fold_rows = []
    for part in range(3):
        train = [row for i, row in enumerate(rows) if assignments[i] != part]
        test = [row for i, row in enumerate(rows) if assignments[i] == part]
        for pair in PARAMS:
            current = Restorer(train, *pair).score_rows(test)
            losses[pair] += sum(row["bucket_loss_bits"] for row in current)
            for metric in ["top1", "top5", "top10"]:
                successes[pair][metric] += sum(row[metric] for row in current)
        fold_rows.append({"inner_fold": part, "train_strings": len(train), "test_strings": len(test), "test_slots": sum(len(r["seq"]) for r in test)})
    slots = sum(len(row["seq"]) for row in rows)
    chosen = min(PARAMS, key=lambda pair: (losses[pair], -float("inf") if pair[1] is None else -pair[1], -float("inf") if pair[0] is None else -pair[0]))
    return chosen, {"fold_token_loads": loads, "split_sizes": fold_rows,
                    "candidates": {label(pair): {"bucket_loss_bits": losses[pair] / slots,
                                                   **{metric: successes[pair][metric] / slots for metric in ["top1", "top5", "top10"]}} for pair in PARAMS}}


def run():
    output = FOLDER / "main"
    if output.exists():
        raise FileExistsError("Refusing an existing adaptive endpoint")
    output.mkdir()
    shutil.copyfile(__file__, output / "code_snapshot.py")
    started = time.monotonic()
    state = {"status": "running", "post_outcome": True, "source_sha256": sha(__file__), "source_hashes": HASHES,
             "protocol_sha256": sha(FOLDER / "PROTOCOL.md"), "self_tests": tests(), "first_order_strength": 20,
             "candidate_pairs": PARAMS, "selection_criterion": "inner_bucket_loss", "completed_folds": 0, "folds": []}
    try:
        original = ROOT / "results/restoration"
        input_path = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
        benchmark = json.loads((original / "benchmark.json").read_text())
        assert sha(input_path) == benchmark["input_sha256"]
        rows, exclusions = BASE.load_records(input_path, min_length=3, unique=True)
        groups = BASE.group_records(rows)
        assignment, loads = BASE.make_folds(rows, groups, 5, 20261006)
        pm = BASE.read_jsonl(original / "baseline_slot_audit.jsonl")
        pmb = BASE.read_jsonl(original / "local_slot_audit.jsonl")
        lookup, correspondence = BASE.verify_saved(rows, groups, assignment, loads, benchmark, pm, pmb)
        scores = []
        for fold in range(5):
            train = [row for i, row in enumerate(rows) if assignment[i] != fold]
            test = [row for i, row in enumerate(rows) if assignment[i] == fold]
            chosen, inner = tune(train, 20261006 + fold)
            model = Restorer(train, *chosen)
            current = model.score_rows(test, details=True)
            for row in current:
                row["fold"] = fold
                row["group"] = lookup[row["record_id"]]
            scores.extend(current)
            state["folds"].append({"fold": fold, "chosen_alpha": chosen[0], "chosen_kappa": chosen[1], "chosen_label": label(chosen),
                                   "train_strings": len(train), "test_strings": len(test), "vocabulary": len(model.signs),
                                   "positive_contexts": len(model.history_counts), "context_count_range": [min(model.history_counts.values()), max(model.history_counts.values())],
                                   "inner": inner})
            state["completed_folds"] = fold + 1
            state["elapsed_seconds"] = time.monotonic() - started
            (output / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"stage": "adaptive_fold", "fold": fold, "chosen": label(chosen), "elapsed_seconds": state["elapsed_seconds"]}), flush=True)
        comparators = {"M1": BASE.read_jsonl(ROOT / "experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl"),
                       "M2_top1_selected": BASE.read_jsonl(ROOT / "experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl"), "PMB": pmb}
        for comparator in comparators.values():
            assert len(comparator) == len(scores) == 8009
            for a, b in zip(scores, comparator):
                assert tuple(a[k] for k in ["record_id", "slot", "actual", "fold", "group"]) == tuple(b[k] for k in ["record_id", "slot", "actual", "fold", "group"])
        state.update({"status": "complete", "input_sha256": sha(input_path), "correspondence": correspondence, "exclusions": exclusions,
                      "models": {"adaptive": BASE.summarize(scores), **{name: BASE.summarize(old) for name, old in comparators.items()}},
                      "paired": {name: BASE.paired(old, scores, 10000, seed=23102) for name, old in comparators.items()},
                      "elapsed_seconds": time.monotonic() - started})
        (output / "adaptive_slot_audit.jsonl").write_text("\n".join(json.dumps(row) for row in scores) + "\n", encoding="utf-8")
        (output / "results.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"stage": "adaptive_complete", "top1": state["models"]["adaptive"]["top1"],
                          "loss": state["models"]["adaptive"]["bucket_cross_entropy_bits"], "elapsed_seconds": state["elapsed_seconds"]}), flush=True)
    except Exception as error:
        state["status"] = "failed"
        state["failure"] = {"exception": type(error).__name__, "message": str(error)}
        (output / "failure.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    run()
