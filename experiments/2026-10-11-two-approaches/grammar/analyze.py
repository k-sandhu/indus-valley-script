"""Manual, immutable run entry point for latent-field grammar induction."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import itertools
import json
import math
from pathlib import Path
import shutil
import sys
import time

from grammar import (UNKNOWN, POSITION_GRID, MARKOV_GRID, GRAMMAR_GRID, Alphabet, Grammar, Markov,
                     Position, SignCounts, audit_split, digest, folds, load_corpus, self_tests, write_json)
import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]


def key(configuration):
    return json.dumps(list(configuration) if isinstance(configuration, tuple) else configuration, separators=(",", ":"))


def sum_scores(model, rows):
    return sum(float(model.score(row).sum()) for row in rows)


def select(rows, splits, seed, outpath):
    scores = {"POSITION": Counter(), "MARKOV": Counter(), "GRAMMAR": Counter()}
    details = []
    validation_tokens = 0
    for inner, (train, validation) in enumerate(splits):
        assert audit_split(train, validation)
        counts = SignCounts(train)
        validation_tokens += sum(len(row["seq"]) for row in validation)
        for alpha in POSITION_GRID:
            scores["POSITION"][alpha] += sum_scores(Position(counts, alpha), validation)
        for configuration in MARKOV_GRID:
            scores["MARKOV"][configuration] += sum_scores(Markov(counts, *configuration), validation)
        for configuration in GRAMMAR_GRID:
            start = time.monotonic()
            model = Grammar(train, *configuration, seed=seed + inner * 1009)
            score = sum_scores(model, validation)
            scores["GRAMMAR"][configuration] += score
            details.append({"inner": inner, "configuration": list(configuration),
                            "train_texts": len(train), "validation_texts": len(validation),
                            "validation_score_bits": score, "iterations": model.iterations,
                            "restart_summaries": model.restart_summaries,
                            "elapsed_seconds": time.monotonic() - start})
        print(json.dumps({"stage": "inner_complete", "inner": inner, "training_texts": len(train),
                          "validation_texts": len(validation)}), flush=True)
    chosen = {name: max(grid, key=lambda candidate: scores[name][candidate])
              for name, grid in (("POSITION", POSITION_GRID), ("MARKOV", MARKOV_GRID), ("GRAMMAR", GRAMMAR_GRID))}
    result = {"selected": {name: list(config) if isinstance(config, tuple) else config for name, config in chosen.items()},
              "validation_tokens": validation_tokens,
              "inner_cross_entropy_bits": {name: {key(config): -score / validation_tokens for config, score in values.items()}
                                           for name, values in scores.items()},
              "grammar_fit_summaries": details}
    write_json(outpath, result)
    return chosen, result


def fit_models(train, chosen, seed):
    counts = SignCounts(train)
    models = {"POSITION": Position(counts, chosen["POSITION"]),
              "MARKOV": Markov(counts, *chosen["MARKOV"]),
              "GRAMMAR": Grammar(train, *chosen["GRAMMAR"], seed=seed)}
    alphabets = {tuple(model.alphabet.signs) for model in models.values()}
    assert len(alphabets) == 1
    return models, counts


def predictions(models, counts, test, fold):
    result = []
    for row in test:
        scores = {name: model.score(row).tolist() for name, model in models.items()}
        result.append({"record_id": row["record_id"], "group": row["group"], "fold": fold,
                       "sequence": list(row["seq"]), "artifact_aliases": row["artifact_aliases"],
                       "log2_probabilities": scores,
                       "in_training_alphabet": [sign in counts.alphabet.index for sign in row["seq"]],
                       "unseen_bigram": [False] + [(left, right) not in counts.bigram_seen
                                                    for left, right in zip(row["seq"][:-1], row["seq"][1:])]})
    return result


def describe_grammar(model, rows):
    occupancy = np.zeros(model.states)
    positions = np.zeros((model.states, 3))
    normalized_position = np.zeros(model.states)
    paths = Counter()
    state_pair = np.zeros((model.states, model.states))
    for row in rows:
        gamma, _ = model.posterior(row)
        length = len(row["seq"])
        occupancy += gamma.sum(axis=0)
        positions[:, 0] += gamma[0]
        positions[:, 2] += gamma[-1]
        positions[:, 1] += gamma[1:-1].sum(axis=0)
        normalized_position += ((np.arange(length) / (length - 1))[:, None] * gamma).sum(axis=0)
        path = model.viterbi(row)
        paths[path] += 1
        for left, right in zip(path[:-1], path[1:]):
            state_pair[left, right] += 1
    ordering = np.argsort(normalized_position / occupancy, kind="stable")
    label = {int(state): f"C{rank + 1:02d}" for rank, state in enumerate(ordering)}
    classes = []
    for state in ordering:
        top = np.argsort(-model.emission[state], kind="stable")[:6]
        classes.append({"class": label[int(state)], "raw_state": int(state),
                        "expected_tokens": float(occupancy[state]), "token_share": float(occupancy[state] / occupancy.sum()),
                        "initial_internal_final_share": (positions[state] / occupancy[state]).tolist(),
                        "mean_normalized_position": float(normalized_position[state] / occupancy[state]),
                        "top_emissions": [{"code": model.alphabet.signs[int(code)],
                                           "probability": float(model.emission[state, code])} for code in top],
                        "top_six_emission_mass": float(model.emission[state, top].sum())})
    transitions = [{"left": label[left], "right": label[right], "viterbi_edges": int(state_pair[left, right]),
                    "global_transition_probability": float(model.transition[left, right])}
                   for left, right in itertools.product(range(model.states), repeat=2) if state_pair[left, right] >= 10]
    transitions.sort(key=lambda r: (-r["viterbi_edges"], r["left"], r["right"]))
    return {"configuration": [model.states, model.emission_strength, model.contextual],
            "state_labels_ordered_by_mean_position": True, "descriptive_training_population": len(rows),
            "classes": classes, "top_class_transitions": transitions[:24],
            "top_viterbi_productions": [{"production": " ".join(label[state] for state in path), "texts": count}
                                       for path, count in paths.most_common(16)],
            "training_iterations": model.iterations, "restart_summaries": model.restart_summaries,
            "scope": "Aggregate latent classes, bounded high-probability emissions and coarse state paths. No code meanings assigned."}


def save_model(model, path):
    payload = {"emission": model.emission, "initial": model.initial, "transition": model.transition,
               "signs": np.array(model.alphabet.signs), "configuration": np.array([model.states, model.emission_strength, int(model.contextual)])}
    payload.update({f"initial_L{length}": value for length, value in model.context_initial.items()})
    payload.update({f"transition_L{length}_j{slot}": value for (length, slot), value in model.context_transition.items()})
    np.savez_compressed(path, **payload)


def summarize(records, seed, bootstrap=5000):
    sums = Counter()
    group_deltas = defaultdict(lambda: np.zeros(3))
    strata = defaultdict(lambda: {"tokens": 0, "score_bits": Counter()})
    noninitial = Counter()
    oov = 0
    for row in records:
        length = len(row["sequence"])
        sums["tokens"] += length
        sums["texts"] += 1
        for name, scores in row["log2_probabilities"].items():
            sums[name] += sum(scores)
            sums[f"text_{name}"] += sum(scores) / length
            noninitial[name] += sum(scores[1:])
        noninitial["tokens"] += length - 1
        group_deltas[row["group"]] += [sum(row["log2_probabilities"]["GRAMMAR"]) - sum(row["log2_probabilities"]["MARKOV"]),
                                     sum(row["log2_probabilities"]["GRAMMAR"]) - sum(row["log2_probabilities"]["POSITION"]), length]
        for j in range(length):
            known = row["in_training_alphabet"][j]
            oov += not known
            names = ["known_target" if known else "OOV_target", "initial" if j == 0 else "final" if j + 1 == length else "internal"]
            if j and known:
                names.append("unseen_bigram_known_target" if row["unseen_bigram"][j] else "seen_bigram_known_target")
            for name in names:
                strata[name]["tokens"] += 1
                for model, scores in row["log2_probabilities"].items():
                    strata[name]["score_bits"][model] += scores[j]
    rng = np.random.default_rng(seed)
    values = np.stack(list(group_deltas.values()))
    draws = []
    for offset in range(0, bootstrap, 100):
        selected = rng.integers(0, len(values), size=(min(100, bootstrap - offset), len(values)))
        totals = values[selected].sum(axis=1)
        draws.append(totals[:, :2] / totals[:, 2, None])
    draws = np.concatenate(draws)
    contrast = {}
    for j, rival in enumerate(("MARKOV", "POSITION")):
        point = float(values[:, j].sum() / values[:, 2].sum())
        contrast[f"GRAMMAR_minus_{rival}"] = {"bits_per_token": point,
                                                "conditional_component_bootstrap_95_ci": np.quantile(draws[:, j], [0.025, 0.975]).tolist(),
                                                "equal_text_weight_bits_per_token": (sums["text_GRAMMAR"] - sums[f"text_{rival}"]) / sums["texts"],
                                                "noninitial_bits_per_token": (noninitial["GRAMMAR"] - noninitial[rival]) / noninitial["tokens"]}
    return {"texts": int(sums["texts"]), "tokens": int(sums["tokens"]), "components": len(values),
            "cross_entropy_bits_per_token": {name: -sums[name] / sums["tokens"] for name in ("POSITION", "MARKOV", "GRAMMAR")},
            "contrasts": contrast, "OOV_tokens": int(oov), "OOV_rate": oov / sums["tokens"],
            "strata": {name: {"tokens": item["tokens"],
                              "cross_entropy_bits_per_token": {model: -score / item["tokens"] for model, score in item["score_bits"].items()},
                              "GRAMMAR_minus_MARKOV_bits_per_token": (item["score_bits"]["GRAMMAR"] - item["score_bits"]["MARKOV"]) / item["tokens"]}
                       for name, item in sorted(strata.items())},
            "bootstrap_draws": bootstrap, "bootstrap_seed": seed,
            "bootstrap_scope": "Conditional on fitted models and observed fold design; component resampling with fixed benchmark weights."}


def align_states(reference, models):
    from scipy.optimize import linear_sum_assignment
    comparisons = []
    for fold, model in enumerate(models):
        common = sorted(set(reference.alphabet.signs) & set(model.alphabet.signs) - {UNKNOWN})
        a = reference.emission[:, [reference.alphabet.index[sign] for sign in common]]
        b = model.emission[:, [model.alphabet.index[sign] for sign in common]]
        a = np.column_stack([a, 1 - a.sum(axis=1)])
        b = np.column_stack([b, 1 - b.sum(axis=1)])
        cost = np.empty((len(a), len(b)))
        for i, p in enumerate(a):
            for j, q in enumerate(b):
                mean = (p + q) / 2
                cost[i, j] = (np.sum(p * np.log2(p / mean)) + np.sum(q * np.log2(q / mean))) / 2
        left, right = linear_sum_assignment(cost)
        pairs = []
        for i, j in zip(left, right):
            top_a = {reference.alphabet.signs[int(code)] for code in np.argsort(-reference.emission[i])[:6]}
            top_b = {model.alphabet.signs[int(code)] for code in np.argsort(-model.emission[j])[:6]}
            pairs.append({"full_state": int(i), "outer_state": int(j), "JS_divergence_bits": float(cost[i, j]),
                          "top_six_overlap": len(top_a & top_b), "shared_top_codes": sorted(top_a & top_b)})
        comparisons.append({"fold": fold, "outer_states": model.states, "full_states": reference.states,
                            "matched_states": len(left), "mean_JS_divergence_bits": float(cost[left, right].mean()),
                            "pairs": pairs})
    return {"scope": "Descriptive emission alignment after evaluation; rectangular assignment if selected state counts differ. Missing/UNKNOWN emissions pooled into one remainder bin.",
            "folds": comparisons}


def synthetic_rows(seed, count=1600):
    rng = np.random.default_rng(seed)
    members = [np.arange(0, 12), np.arange(12, 28), np.arange(28, 40), np.arange(40, 64), np.arange(64, 76), np.arange(76, 80)]
    emissions = [1 / np.arange(1, len(items) + 1) ** 0.65 for items in members]
    emissions = [weights / weights.sum() for weights in emissions]
    rows, seen = [], set()
    while len(rows) < count:
        path = ([0] if rng.random() < 0.65 else []) + [1]
        if rng.random() < 0.55:
            path.append(2)
        path += [3] * int(rng.choice([1, 2, 3, 4, 5], p=[0.55, 0.25, 0.10, 0.06, 0.04]))
        if rng.random() < 0.45:
            path.append(4)
        path += [5]
        seq = tuple(f"S{int(rng.choice(members[state], p=emissions[state])):03d}" for state in path)
        if seq in seen:
            continue
        seen.add(seq)
        i = len(rows)
        rows.append({"record_id": f"synthetic-{seed}-{i}", "seq": seq, "group": i,
                     "artifact_aliases": [f"synthetic-object-{seed}-{i}"]})
    return rows


def run_controls(out, local, seed):
    results = []
    for replicate in range(3):
        for mechanism in ("administrative_fields", "compositional_clause"):
            control_seed = seed + 50000 + replicate * 1000 + (0 if mechanism == "administrative_fields" else 271)
            rows = synthetic_rows(control_seed)
            assignment, loads = folds(rows, 20, control_seed)
            train = [row for i, row in enumerate(rows) if assignment[i] < 14]
            validation = [row for i, row in enumerate(rows) if 14 <= assignment[i] < 17]
            test = [row for i, row in enumerate(rows) if assignment[i] >= 17]
            audit_split(train, validation)
            audit_split(train + validation, test)
            label = f"{mechanism}-r{replicate}"
            chosen, selection = select(rows, [(train, validation)], control_seed, out / f"control-{label}-selection.json")
            models, counts = fit_models(train + validation, chosen, control_seed + 199)
            scored = predictions(models, counts, test, 0)
            with (local / f"control-{label}-predictions.jsonl").open("w", encoding="utf-8") as handle:
                for row in scored:
                    handle.write(json.dumps(row) + "\n")
            summary = summarize(scored, control_seed, bootstrap=2000)
            result = {"replicate": replicate, "mechanism": mechanism, "seed": control_seed,
                      "generated_texts": len(rows), "fit_texts": len(train + validation), "test_texts": len(test),
                      "selected": selection["selected"], "summary": summary}
            results.append(result)
            write_json(out / f"control-{label}.json", result)
            print(json.dumps({"stage": "control_complete", "label": label,
                              "grammar_minus_markov": summary["contrasts"]["GRAMMAR_minus_MARKOV"]["bits_per_token"]}), flush=True)
    graph = {"production": "[C0] C1 [C2] C3{1,2,3,4,5} [C4] C5",
             "C0_present_probability": 0.65, "C2_present_probability": 0.55, "C4_present_probability": 0.45,
             "C3_count_probabilities": {"1": 0.55, "2": 0.25, "3": 0.10, "4": 0.06, "5": 0.04},
             "emissions": "Disjoint code groups of sizes 12,16,12,24,12,4; rank probability proportional to rank^-0.65",
             "administrative_labels": ["opening_marker", "issuer", "quantity_class", "item", "qualifier", "authorization"],
             "compositional_labels": ["opening_particle", "head", "case_class", "modifier", "aspect", "inflection"],
             "labels_change_no_sequence_probability": True}
    result = {"status": "synthetic", "shared_generator": graph, "independent_realizations": results,
              "semantic_twin_witness": {"construction": "The same generated code rows, with either class-label interpretation.",
                                        "probability_equality": "Both interpretations assign exactly the same product of field-selection and emission factors to every sequence.",
                                        "likelihood_ratio_every_sequence": 1.0}}
    write_json(out / "structured-controls.json", result)
    return result


def main(args):
    out = PACKAGE / args.run
    local = ROOT / "data/raw/2026-10-11-two-approaches/grammar" / args.run
    if out.exists() or local.exists():
        raise FileExistsError("A run directory already exists; preserve it and select a fresh --run name.")
    out.mkdir(parents=True)
    local.mkdir(parents=True)
    for path in (PACKAGE / "PROTOCOL.md", PACKAGE / "grammar.py", Path(__file__)):
        shutil.copyfile(path, out / path.name)
    started = time.monotonic()
    write_json(out / "self-tests.json", self_tests())
    rows, census = load_corpus(ROOT / "data/normalized/lipi_observed_faces.jsonl")
    assignment, loads = folds(rows, 5, args.seed)
    manifest = {"run": args.run, "seed": args.seed, "input": "data/normalized/lipi_observed_faces.jsonl",
                "input_sha256": census["raw_input_sha256"], "code_sha256": digest(PACKAGE / "grammar.py"),
                "runner_sha256": digest(__file__), "protocol_sha256": digest(PACKAGE / "PROTOCOL.md"),
                "census": census, "outer_fold_token_loads": loads,
                "local_only_output": str(local.relative_to(ROOT)).replace("\\", "/")}
    write_json(out / "manifest.json", manifest)
    with (local / "fold-assignment.jsonl").open("w", encoding="utf-8") as handle:
        for i, row in enumerate(rows):
            handle.write(json.dumps({**row, "seq": list(row["seq"]), "fold": assignment[i]}) + "\n")
    scored, outer_grammars, selections = [], [], []
    fold_results = []
    for fold in range(5):
        train = [row for i, row in enumerate(rows) if assignment[i] != fold]
        test = [row for i, row in enumerate(rows) if assignment[i] == fold]
        audit_split(train, test)
        inner_assignment, inner_loads = folds(train, 3, args.seed + fold)
        splits = [([row for i, row in enumerate(train) if inner_assignment[i] != inner],
                   [row for i, row in enumerate(train) if inner_assignment[i] == inner]) for inner in range(3)]
        chosen, selection = select(train, splits, args.seed + fold, out / f"fold-{fold}-selection.json")
        models, counts = fit_models(train, chosen, args.seed + fold + 100000)
        fold_scored = predictions(models, counts, test, fold)
        scored += fold_scored
        outer_grammars.append(models["GRAMMAR"])
        selections.append(selection)
        save_model(models["GRAMMAR"], local / f"fold-{fold}-model.npz")
        write_json(out / f"fold-{fold}-grammar.json", describe_grammar(models["GRAMMAR"], train))
        summary = summarize(fold_scored, args.seed + fold, bootstrap=2000)
        fold_result = {"fold": fold, "train_texts": len(train), "test_texts": len(test),
                       "inner_fold_token_loads": inner_loads, "selected": selection["selected"],
                       "summary": summary, "elapsed_seconds": time.monotonic() - started}
        fold_results.append(fold_result)
        write_json(out / f"fold-{fold}-results.json", fold_result)
        with (local / f"fold-{fold}-predictions.jsonl").open("w", encoding="utf-8") as handle:
            for row in fold_scored:
                handle.write(json.dumps(row) + "\n")
        print(json.dumps({"stage": "outer_complete", "fold": fold, "selected": selection["selected"],
                          "summary": summary["cross_entropy_bits_per_token"], "seconds": time.monotonic() - started}), flush=True)
    summary = summarize(scored, args.seed)
    pooled = Counter()
    for selection in selections:
        for configuration, loss in selection["inner_cross_entropy_bits"]["GRAMMAR"].items():
            pooled[configuration] -= loss * selection["validation_tokens"]
    chosen_full = tuple(json.loads(max(pooled, key=pooled.get)))
    full = Grammar(rows, *chosen_full, seed=args.seed + 999999)
    save_model(full, local / "full-descriptive-model.npz")
    write_json(out / "learned-grammar.json", describe_grammar(full, rows))
    write_json(out / "classes-stability.json", align_states(full, outer_grammars))
    result = {"status": "exploratory-completed", "manifest": manifest, "summary": summary, "folds": fold_results,
              "full_descriptive_configuration": list(chosen_full),
              "full_configuration_selection": "Maximum pooled inner validation likelihood across outer training sets; outer scores unused.",
              "elapsed_seconds": time.monotonic() - started}
    write_json(out / "results.json", result)
    controls = run_controls(out, local, args.seed)
    result["controls_file"] = "structured-controls.json"
    result["elapsed_seconds"] = time.monotonic() - started
    write_json(out / "results.json", result)
    write_json(out / "completion.json", {"complete": True, "outer_folds": 5, "synthetic_controls": len(controls["independent_realizations"]),
                                        "elapsed_seconds": time.monotonic() - started,
                                        "tracked_output_sha256": {str(path.relative_to(out)): digest(path) for path in sorted(out.glob("*.json"))},
                                        "local_only_output_sha256": {str(path.relative_to(local)): digest(path) for path in sorted(local.glob("*"))}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--seed", type=int, default=20261011)
    main(parser.parse_args())
