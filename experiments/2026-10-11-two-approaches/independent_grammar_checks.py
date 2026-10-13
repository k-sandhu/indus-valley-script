"""Coordinator checks using explicit state paths and frozen fitted weights.

This checks numerical scoring and split/selection accounting. It does not refit
the empirical grammar or supply independent archaeological observations.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "grammar/run-v1"
RAW = ROOT / "data/raw/2026-10-11-two-approaches/grammar/run-v1"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def explicit_probability(model, sequence):
    length = len(sequence)
    total = 0.0
    for states in itertools.product(range(model.states), repeat=length):
        value = model._initial(length)[states[0]] * model.emission[states[0], sequence[0]]
        for slot in range(1, length):
            value *= model._transition(length, slot)[states[slot - 1], states[slot]]
            value *= model.emission[states[slot], sequence[slot]]
        total += value
    return total


def independent_scores(model, sequence):
    """Unscaled probability recursion, separate from the author's score function."""
    vector = model._initial(len(sequence)) * model.emission[:, sequence[0]]
    previous = 1.0
    scores = []
    for slot in range(len(sequence)):
        if slot:
            vector = (vector @ model._transition(len(sequence), slot)) * model.emission[:, sequence[slot]]
        likelihood = float(vector.sum())
        scores.append(math.log2(likelihood / previous))
        previous = likelihood
    return np.array(scores)


def tests():
    spec = importlib.util.spec_from_file_location("frozen_grammar_for_coordinator", PACKAGE / "grammar.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []
    def record(name, passed, **details):
        checks.append({"check": name, "pass": bool(passed), **details})

    # Fixed, hand-specified probabilities make this an independent state-path
    # calculation rather than another call to the fitting implementation.
    for contextual in (False, True):
        toy = module.Grammar.__new__(module.Grammar)
        toy.alphabet = module.Alphabet([{"seq": ("a", "b", "a")}])
        toy.states, toy.contextual = 2, contextual
        toy.emission = np.array([[0.6, 0.3, 0.1], [0.15, 0.75, 0.1]])
        toy.initial = np.array([0.8, 0.2])
        toy.transition = np.array([[0.25, 0.75], [0.65, 0.35]])
        toy.context_initial = {3: np.array([0.35, 0.65])}
        toy.context_transition = {(3, 1): np.array([[0.1, 0.9], [0.8, 0.2]]),
                                  (3, 2): np.array([[0.7, 0.3], [0.4, 0.6]])}
        max_score_error, max_filter_error, max_posterior_error = 0.0, 0.0, 0.0
        sums = []
        for length in range(1, 5):
            total = 0.0
            for seq in itertools.product(range(3), repeat=length):
                p = explicit_probability(toy, seq)
                total += p
                row = {"seq": tuple(toy.alphabet.signs[s] for s in seq)}
                max_score_error = max(max_score_error, abs(sum(toy.score(row)) - math.log2(p)))
                max_filter_error = max(max_filter_error, float(np.max(np.abs(toy.score(row) - independent_scores(toy, seq)))))
                if length == 3:
                    gamma = np.zeros((length, 2))
                    for states in itertools.product(range(2), repeat=length):
                        v = toy._initial(length)[states[0]] * toy.emission[states[0], seq[0]]
                        for slot in range(1, length):
                            v *= toy._transition(length, slot)[states[slot - 1], states[slot]] * toy.emission[states[slot], seq[slot]]
                        for slot, state in enumerate(states):
                            gamma[slot, state] += v / p
                    max_posterior_error = max(max_posterior_error, float(np.max(np.abs(gamma - toy.posterior(row)[0]))))
            sums.append(total)
        record("explicit_state_path_normalization", all(abs(p - 1) < 1e-12 for p in sums), contextual=contextual, totals=sums)
        record("explicit_state_path_likelihood", max_score_error < 1e-12, contextual=contextual, max_error=max_score_error)
        record("independent_prefix_recursion", max_filter_error < 1e-12, contextual=contextual, max_error=max_filter_error)
        record("explicit_state_path_posterior", max_posterior_error < 1e-12, contextual=contextual, max_error=max_posterior_error)

    assignment = lines(RAW / "fold-assignment.jsonl")
    corpus = lines(ROOT / "data/normalized/lipi_observed_faces.jsonl")
    parent = list(range(len(corpus)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def unite(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[b] = a
    seen_family, seen_text = {}, {}
    simple_cisi = defaultdict(set)
    for i, row in enumerate(corpus):
        family, seq = row["object_family_id"], tuple(row["signs_reading_rtl"])
        if family in seen_family:
            unite(i, seen_family[family])
        seen_family[family] = i
        if seq:
            if seq in seen_text:
                unite(i, seen_text[seq])
            seen_text[seq] = i
        match = re.fullmatch(r"([A-Za-z]+)-?(\d+)(?:[A-Za-z])?", str(row["source_cisi"]).strip())
        if match:
            simple_cisi[(match[1].upper(), int(match[2]))].add(family)
    by_id = {row["record_id"]: i for i, row in enumerate(corpus)}
    component_folds = defaultdict(set)
    for row in assignment:
        component_folds[find(by_id[row["record_id"]])].add(row["fold"])
    record("independent_full_register_closure_respected", all(len(v) == 1 for v in component_folds.values()), components=len(component_folds))
    record("simple_cisi_bases_covered_by_export_families", all(len(v) == 1 for v in simple_cisi.values()), bases=len(simple_cisi))

    predictions = []
    max_fitted_error = 0.0
    for fold in range(5):
        test = lines(RAW / f"fold-{fold}-predictions.jsonl")
        predictions.extend(test)
        train = [r for r in assignment if r["fold"] != fold]
        train_aliases = {a for r in train for a in r["artifact_aliases"]}
        test_aliases = {a for r in test for a in r["artifact_aliases"]}
        record("outer_physical_alias_disjointness", not train_aliases.intersection(test_aliases), fold=fold)
        selection = read(PACKAGE / f"fold-{fold}-selection.json")
        for name, scores in selection["inner_cross_entropy_bits"].items():
            selected = selection["selected"][name]
            selected_key = next(key for key in scores if json.loads(key) == selected)
            record("train_only_grid_minimum", abs(scores[selected_key] - min(scores.values())) < 1e-12, fold=fold, model=name)
        with np.load(RAW / f"fold-{fold}-model.npz", allow_pickle=False) as fitted:
            model = module.Grammar.__new__(module.Grammar)
            model.alphabet = module.Alphabet(train)
            record("saved_model_training_alphabet", model.alphabet.signs == fitted["signs"].tolist(), fold=fold)
            model.states, _, context = fitted["configuration"].tolist()
            model.contextual = bool(context)
            model.emission, model.initial, model.transition = (fitted[k] for k in ("emission", "initial", "transition"))
            model.context_initial, model.context_transition = {}, {}
            for name in fitted.files:
                if m := re.fullmatch(r"initial_L(\d+)", name):
                    model.context_initial[int(m[1])] = fitted[name]
                if m := re.fullmatch(r"transition_L(\d+)_j(\d+)", name):
                    model.context_transition[(int(m[1]), int(m[2]))] = fitted[name]
            for row in test:
                encoded = model.alphabet.encode(row["sequence"])
                predicted = independent_scores(model, encoded)
                max_fitted_error = max(max_fitted_error, float(np.max(np.abs(predicted - row["log2_probabilities"]["GRAMMAR"]))))
    record("all_empirical_grammar_tokens_rescored", max_fitted_error < 1e-11, tokens=sum(len(r["sequence"]) for r in predictions), max_error=max_fitted_error)
    n = sum(len(r["sequence"]) for r in predictions)
    losses = {name: -sum(sum(r["log2_probabilities"][name]) for r in predictions) / n for name in ("POSITION", "MARKOV", "GRAMMAR")}
    result = read(PACKAGE / "results.json")["summary"]
    record("pooled_losses_recounted", all(abs(losses[k] - result["cross_entropy_bits_per_token"][k]) < 1e-12 for k in losses), losses=losses)
    record("one_prediction_per_distinct_text", len({tuple(r["sequence"]) for r in predictions}) == len(predictions) == len(assignment), texts=len(predictions))
    return {"status": "coordinator-independent-numeric-and-design-audit", "checks": checks,
            "passed": sum(c["pass"] for c in checks), "failed": sum(not c["pass"] for c in checks),
            "scope": "Exact toy enumeration, independent empirical rescoring from frozen weights, selection and grouping accounting. No training refit or semantic validation."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="coordinator-checks/grammar-v1.json")
    args = parser.parse_args()
    output = HERE / args.out
    if output.exists():
        raise SystemExit("Output exists; preserve it and select a new path.")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = tests()
    result["code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"], "output": str(output)}))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
