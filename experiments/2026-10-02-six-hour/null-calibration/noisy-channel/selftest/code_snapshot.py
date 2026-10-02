"""Recover a declared symmetric channel from frozen synthetic paired-face counts."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import shutil
import sys
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
FOLDER = ROOT / "experiments/2026-10-02-six-hour/null-calibration/noisy-channel"
SOURCE = FOLDER.parent / "noisy-faces/main"
TRUE_EPSILON = .1
BASE_P = np.array([.20, .16, .14, .12, .11, .10, .09, .08])
TRUE_P = np.array([np.roll(BASE_P, site + 2 * slot) for site in range(2) for slot in range(3)])
BOOTSTRAP_SEED = 6026100207


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def kernel(epsilon, categories=8):
    matrix = np.full((categories, categories), epsilon / (categories - 1))
    np.fill_diagonal(matrix, 1 - epsilon)
    return matrix


def joint_probability(p, epsilon):
    transition = kernel(epsilon, p.shape[1])
    return np.einsum("cx,xa,xb->cab", p, transition, transition)


def mean_marginal(counts):
    totals = counts.sum(axis=(1, 2))
    return (counts.sum(axis=1) + counts.sum(axis=2)) / (2 * totals[:, None])


def agreement_inversion(counts):
    categories = counts.shape[1]
    agreement = float(np.trace(counts, axis1=1, axis2=2).sum() / counts.sum())
    domain = agreement >= 1 / categories
    epsilon = (categories - 1) / categories * (1 - math.sqrt(max(0., (categories * agreement - 1) / (categories - 1))))
    return {"agreement": agreement, "epsilon": epsilon, "in_domain": domain}


def raw_inverse(marginal, epsilon):
    categories = marginal.shape[1]
    attenuation = 1 - categories * epsilon / (categories - 1)
    if attenuation <= 1e-12:
        return None
    return (marginal - epsilon / (categories - 1)) / attenuation


def simplex_projection(values):
    result = []
    for vector in values:
        ordered = np.sort(vector)[::-1]
        offsets = (np.cumsum(ordered) - 1) / np.arange(1, len(vector) + 1)
        active = np.flatnonzero(ordered > offsets)
        threshold = offsets[active[-1]]
        result.append(np.maximum(vector - threshold, 0))
    return np.array(result)


def objective(counts, p, epsilon, fixed_epsilon=False):
    probability = joint_probability(p, epsilon)
    positive = counts > 0
    likelihood = float(np.sum(counts[positive] * np.log(probability[positive])))
    penalty = float(.5 * np.log(p).sum())
    if not fixed_epsilon:
        penalty += .5 * math.log(epsilon) + .5 * math.log1p(-epsilon)
    return likelihood + penalty, likelihood, penalty


def em_one(counts, start, fixed_epsilon=None):
    categories = counts.shape[1]
    cells, left, right = np.nonzero(counts)
    weights = counts[cells, left, right]
    totals = counts.sum(axis=(1, 2))
    p = (mean_marginal(counts) * totals[:, None] + .5) / (totals[:, None] + categories * .5)
    epsilon = float(start if fixed_epsilon is None else fixed_epsilon)
    upper = (categories - 1) / categories - 1e-10
    trace = [objective(counts, p, epsilon, fixed_epsilon is not None)[0]]
    converged = False
    changes = []
    for iteration in range(500):
        transition = kernel(epsilon, categories)
        emission = transition[:, left].T * transition[:, right].T
        posterior = p[cells] * emission
        posterior /= posterior.sum(axis=1, keepdims=True)
        expected = np.zeros_like(p)
        np.add.at(expected, cells, posterior * weights[:, None])
        next_p = (expected + .5) / (totals[:, None] + categories * .5)
        expected_replacements = float(np.sum(weights * (2 - posterior[np.arange(len(weights)), left] - posterior[np.arange(len(weights)), right])))
        next_epsilon = float(np.clip((expected_replacements + .5) / (2 * counts.sum() + 1), 1e-10, upper)) if fixed_epsilon is None else epsilon
        change = max(float(np.max(np.abs(next_p - p))), abs(next_epsilon - epsilon))
        p, epsilon = next_p, next_epsilon
        current = objective(counts, p, epsilon, fixed_epsilon is not None)[0]
        if current < trace[-1] - 1e-8:
            raise ArithmeticError(f"Penalized objective decreased: {trace[-1]} to {current}")
        increment = current - trace[-1]
        trace.append(current)
        changes.append(change)
        if change <= 1e-8 and increment <= 1e-9 * max(1, counts.sum()):
            converged = True
            break
    value, likelihood, penalty = objective(counts, p, epsilon, fixed_epsilon is not None)
    return {"epsilon": epsilon, "p": p.tolist(), "objective": value, "log_likelihood": likelihood,
            "penalty": penalty, "converged": converged, "iterations": len(changes),
            "last_parameter_change": changes[-1], "start_epsilon": start,
            "trace": trace, "minimum_objective_increment": min(np.diff(trace))}


def joint_fit(counts, fixed_epsilon=None):
    starts = [.02, .1, .3] if fixed_epsilon is None else [fixed_epsilon]
    fits = [em_one(counts, start, fixed_epsilon) for start in starts]
    selected = max(range(len(fits)), key=lambda index: fits[index]["objective"])
    return {"selected_start": selected, "fit": fits[selected], "starts": fits}


def count_pairs(trial):
    by_object = {}
    for row in trial["rows"]:
        by_object.setdefault(row["artifact"], []).append(row)
    counts = np.zeros((6, 8, 8), dtype=int)
    for artifact, faces in sorted(by_object.items()):
        faces.sort(key=lambda row: row["record_id"])
        assert len(faces) == 2 and faces[0]["site"] == faces[1]["site"]
        site = int(faces[0]["site"].split("_")[-1])
        for slot in range(3):
            left, right = [int(row["seq"][slot]) - 1 for row in faces]
            counts[site * 3 + slot, left, right] += 1
    assert np.all(counts.sum(axis=(1, 2)) == 10)
    return counts


def frequency_metrics(p, truth=TRUE_P):
    return {"total_variation": float(np.abs(p - truth).sum(axis=1).mean() / 2),
            "component_mse": float(np.square(p - truth).mean())}


def analyze(counts):
    marginal = mean_marginal(counts)
    agreement = agreement_inversion(counts)
    raw = raw_inverse(marginal, agreement["epsilon"])
    projected = simplex_projection(raw) if raw is not None else np.full_like(marginal, 1 / marginal.shape[1])
    known_raw = raw_inverse(marginal, TRUE_EPSILON)
    unknown, known = joint_fit(counts), joint_fit(counts, TRUE_EPSILON)
    estimates = {"observed_marginal": marginal, "agreement_projected": projected,
                 "joint_unknown_channel": np.array(unknown["fit"]["p"]),
                 "joint_known_channel": np.array(known["fit"]["p"])}
    negatives = {}
    for name, values in [("agreement", raw), ("known_channel", known_raw)]:
        negatives[name] = {"undefined": values is None,
                           "negative_components": int((values < -1e-12).sum()) if values is not None else 0,
                           "affected_cells": int((values < -1e-12).any(axis=1).sum()) if values is not None else 0}
    return {"counts": counts.tolist(), "agreement": agreement, "raw_inverse": raw.tolist() if raw is not None else None,
            "known_channel_raw_inverse": known_raw.tolist(), "negative_inversions": negatives,
            "estimates": {name: value.tolist() for name, value in estimates.items()},
            "frequency_metrics": {name: frequency_metrics(value) for name, value in estimates.items()},
            "joint_unknown": unknown, "joint_known": known}


def bootstrap_summary(records):
    measurements = {}
    for name in ["agreement", "joint_unknown"]:
        values = np.array([r["agreement"]["epsilon"] if name == "agreement" else r["joint_unknown"]["fit"]["epsilon"] for r in records])
        measurements[f"{name}_bias"] = values - TRUE_EPSILON
        measurements[f"{name}_absolute_error"] = np.abs(values - TRUE_EPSILON)
        measurements[f"{name}_squared_error"] = np.square(values - TRUE_EPSILON)
    for name in records[0]["frequency_metrics"]:
        for metric in ["total_variation", "component_mse"]:
            measurements[f"{name}_{metric}"] = np.array([r["frequency_metrics"][name][metric] for r in records])
    measurements["joint_minus_agreement_total_variation"] = measurements["joint_unknown_channel_total_variation"] - measurements["agreement_projected_total_variation"]
    matrix = np.column_stack(list(measurements.values()))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    replicates = np.empty((20000, matrix.shape[1]))
    for first in range(0, 20000, 200):
        indices = rng.integers(0, len(records), size=(200, len(records)))
        replicates[first:first + 200] = matrix[indices].mean(axis=1)
    return {name: {"mean": float(matrix[:, index].mean()), "ci95": np.quantile(replicates[:, index], [.025, .975]).tolist()}
            for index, name in enumerate(measurements)}


def selftest(output):
    if output.exists():
        raise FileExistsError("Refusing an existing channel test endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    epsilon = Fraction(1, 10)
    agreement = (1 - epsilon) ** 2 + epsilon ** 2 / 7
    assert agreement == Fraction(142, 175)
    attenuation = 1 - 8 * epsilon / 7
    assert agreement == Fraction(1, 8) + Fraction(7, 8) * attenuation ** 2
    rational_p = [Fraction(int(round(value * 100)), 100) for value in BASE_P]
    for x, p in enumerate(rational_p):
        marginal = sum(rational_p[z] * ((1 - epsilon) if z == x else epsilon / 7) for z in range(8))
        assert (marginal - epsilon / 7) / attenuation == p
    assert np.allclose(joint_probability(TRUE_P, 0), np.array([np.diag(p) for p in TRUE_P]))
    assert np.allclose(joint_probability(TRUE_P, 7 / 8), np.full((6, 8, 8), 1 / 64))
    for rate in [0, .1, .875, 1]:
        assert np.allclose(joint_probability(TRUE_P, rate).sum(axis=(1, 2)), 1)
    p = np.array([[.2, .3, .5]])
    small_epsilon = Fraction(1, 5)
    pairs = [(0, 1), (1, 1), (2, 0)]
    rational_small_p = [Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)]
    oracle = sum(math.prod(rational_small_p[x] * ((1 - small_epsilon) if a == x else small_epsilon / 2) * ((1 - small_epsilon) if b == x else small_epsilon / 2)
                           for x, (a, b) in zip(latent, pairs)) for latent in itertools.product(range(3), repeat=3))
    probabilities = joint_probability(p, float(small_epsilon))[0]
    assert math.isclose(float(oracle), math.prod(probabilities[a, b] for a, b in pairs), abs_tol=1e-15)
    projected = simplex_projection(np.array([[-.2, .4, .8], [.2, .3, .5]]))
    assert np.allclose(projected, [[0, .3, .7], [.2, .3, .5]])
    counts = np.array([[[7, 2, 1], [1, 5, 1], [2, 1, 10]]])
    fitted = joint_fit(counts)
    assert fitted["fit"]["converged"]
    assert min(fitted["fit"]["trace"][i + 1] - fitted["fit"]["trace"][i] for i in range(len(fitted["fit"]["trace"]) - 1)) >= -1e-8
    # Independently form posterior and the first update with scalar loops.
    totals = counts.sum(axis=(1, 2))
    start_p = (mean_marginal(counts) * totals[:, None] + .5) / (totals[:, None] + 1.5)
    expected = np.zeros(3)
    replacements = 0.
    for a in range(3):
        for b in range(3):
            mass = [start_p[0, x] * (.9 if a == x else .05) * (.9 if b == x else .05) for x in range(3)]
            for x in range(3):
                posterior = mass[x] / sum(mass)
                expected[x] += counts[0, a, b] * posterior
                replacements += counts[0, a, b] * posterior * ((a != x) + (b != x))
    next_p = ((expected + .5) / (totals[0] + 1.5))[None]
    next_epsilon = (replacements + .5) / (2 * totals.sum() + 1)
    one = em_one(counts, .1)
    assert math.isclose(objective(counts, next_p, next_epsilon)[0], one["trace"][1], abs_tol=1e-12)
    write_json(output / "results.json", {"status": "passed", "source_sha256": digest(__file__),
                                         "protocol_sha256": digest(FOLDER / "PROTOCOL.md"),
                                         "agreement_exact": str(agreement), "small_assignment_likelihood": str(oracle),
                                         "small_assignment_terms": 27, "checks": 9,
                                         "test_joint_fit": fitted})
    print(json.dumps({"selftest": "passed", "checks": 9}), flush=True)


def main(output):
    source_results = json.loads((SOURCE / "results.json").read_text(encoding="utf-8"))
    assert source_results["status"] == "complete" and source_results["completed_datasets"] == 1000
    if output.exists():
        raise FileExistsError("Refusing an existing channel recovery endpoint")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    started = time.monotonic()
    records = []
    pooled = np.zeros((6, 8, 8), dtype=int)
    hashes = {}
    for index in range(1000):
        path = SOURCE / f"dataset_{index:04d}.json"
        trial = json.loads(path.read_text(encoding="utf-8"))
        assert trial["complete"] and trial["trial_index"] == index and trial["generation"]["error_probability"] == TRUE_EPSILON
        counts = count_pairs(trial)
        record = analyze(counts)
        record["trial_index"] = index
        record["input_sha256"] = digest(path)
        hashes[path.name] = record["input_sha256"]
        write_json(output / f"dataset_{index:04d}.json", record)
        records.append(record)
        pooled += counts
        if (index + 1) % 100 == 0:
            print(json.dumps({"stage": "channel_recovery", "done": index + 1, "total": 1000,
                              "elapsed_seconds": time.monotonic() - started}), flush=True)
    pooled_record = analyze(pooled)
    write_json(output / "pooled.json", pooled_record)
    summary = bootstrap_summary(records)
    negatives = {name: {"populations": sum(r["negative_inversions"][name]["affected_cells"] > 0 for r in records),
                        "cells": sum(r["negative_inversions"][name]["affected_cells"] for r in records),
                        "components": sum(r["negative_inversions"][name]["negative_components"] for r in records),
                        "undefined": sum(r["negative_inversions"][name]["undefined"] for r in records)}
                 for name in ["agreement", "known_channel"]}
    convergence = {name: {"selected_nonconverged": sum(not r[name]["fit"]["converged"] for r in records),
                          "all_start_nonconverged": sum(not start["converged"] for r in records for start in r[name]["starts"]),
                          "maximum_iterations": max(start["iterations"] for r in records for start in r[name]["starts"]),
                          "maximum_start_objective_spread": max(max(s["objective"] for s in r[name]["starts"]) - min(s["objective"] for s in r[name]["starts"]) for r in records)}
                   for name in ["joint_unknown", "joint_known"]}
    write_json(output / "input_hashes.json", hashes)
    result = {"status": "complete", "simulation": True, "populations": 1000, "pairs_per_population": 60,
              "source_sha256": digest(__file__), "protocol_sha256": digest(FOLDER / "PROTOCOL.md"),
              "input_results_sha256": digest(SOURCE / "results.json"), "input_hashes_sha256": digest(output / "input_hashes.json"),
              "numpy_version": np.__version__, "python_version": sys.version, "bootstrap_seed": BOOTSTRAP_SEED,
              "bootstrap_draws": 20000, "true_epsilon": TRUE_EPSILON, "true_p": TRUE_P.tolist(),
              "summary": summary, "negative_inversions": negatives, "convergence": convergence,
              "agreement_inversion_outside_domain": sum(not r["agreement"]["in_domain"] for r in records),
              "pooled_epsilon": {"agreement": pooled_record["agreement"]["epsilon"], "joint": pooled_record["joint_unknown"]["fit"]["epsilon"]},
              "pooled_frequency_metrics": pooled_record["frequency_metrics"], "elapsed_seconds": time.monotonic() - started}
    write_json(output / "results.json", result)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["selftest", "main"])
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    (selftest if arguments.mode == "selftest" else main)(arguments.output)
