"""Independent count, inversion, likelihood and constrained-optimizer audit."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "noisy-faces/main"
MAIN = HERE / "main"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scalar_objective(counts, probabilities, epsilon, fixed=False):
    likelihood = 0.
    categories = probabilities.shape[1]
    for cell, a, b in zip(*np.nonzero(counts)):
        probability = sum(probabilities[cell, x] * ((1 - epsilon) if x == a else epsilon / (categories - 1))
                          * ((1 - epsilon) if x == b else epsilon / (categories - 1)) for x in range(categories))
        likelihood += counts[cell, a, b] * math.log(probability)
    penalty = .5 * sum(math.log(value) for row in probabilities for value in row)
    if not fixed:
        penalty += .5 * math.log(epsilon) + .5 * math.log1p(-epsilon)
    return likelihood + penalty, likelihood, penalty


def independent_counts(trial):
    counts = np.zeros((6, 8, 8), dtype=int)
    for index in range(0, len(trial["rows"]), 2):
        a, b = trial["rows"][index:index + 2]
        assert a["artifact"] == b["artifact"] and a["record_id"] < b["record_id"]
        site = int(a["site"][-1])
        for slot in range(3):
            counts[3 * site + slot, int(a["seq"][slot]) - 1, int(b["seq"][slot]) - 1] += 1
    return counts


def projection_conditions(raw, projected):
    for a, b in zip(raw, projected):
        assert np.all(b >= -1e-12) and abs(b.sum() - 1) < 1e-12
        active = b > 1e-12
        threshold = (a[active] - b[active]).mean()
        assert np.max(np.abs(a[active] - b[active] - threshold)) < 1e-12
        assert np.all(a[~active] <= threshold + 1e-12)


def numerical_check(counts, fit):
    cells, categories = fit["p"].__len__(), 8
    start = np.r_[np.array(fit["p"]).ravel(), fit["epsilon"]]

    def loss_gradient(values):
        p, epsilon = values[:-1].reshape(cells, categories), values[-1]
        transition = np.full((categories, categories), epsilon / 7)
        np.fill_diagonal(transition, 1 - epsilon)
        derivative = np.full_like(transition, 1 / 7)
        np.fill_diagonal(derivative, -1)
        emission = transition[:, :, None] * transition[:, None, :]
        emission_derivative = derivative[:, :, None] * transition[:, None, :] + transition[:, :, None] * derivative[:, None, :]
        probability = np.einsum("cx,xab->cab", p, emission)
        weight = counts / probability
        value = np.sum(counts * np.log(probability)) + .5 * np.log(p).sum() + .5 * np.log(epsilon) + .5 * np.log1p(-epsilon)
        dp = np.einsum("cab,xab->cx", weight, emission) + .5 / p
        de = np.sum(weight * np.einsum("cx,xab->cab", p, emission_derivative)) + .5 / epsilon - .5 / (1 - epsilon)
        return -value, -np.r_[dp.ravel(), de]

    constraint_gradient = np.zeros((cells, cells * categories + 1))
    for cell in range(cells):
        constraint_gradient[cell, cell * categories:(cell + 1) * categories] = 1
    constraints = {"type": "eq", "fun": lambda z: z[:-1].reshape(cells, categories).sum(axis=1) - 1,
                   "jac": lambda z: constraint_gradient}
    result = minimize(loss_gradient, start, jac=True, method="SLSQP",
                      bounds=[(1e-10, 1.)] * (cells * categories) + [(1e-10, 7 / 8 - 1e-10)],
                      constraints=constraints, options={"ftol": 1e-10, "maxiter": 500})
    gain = -float(result.fun) - fit["objective"]
    assert result.success and gain < 1e-7
    return {"success": bool(result.success), "iterations": result.nit, "objective_gain": gain,
            "epsilon": float(result.x[-1]), "max_parameter_difference": float(np.max(np.abs(result.x - start)))}


def run():
    endpoint = MAIN / "verification.json"
    if endpoint.exists():
        raise FileExistsError("Refusing an existing recovery verification")
    results = json.loads((MAIN / "results.json").read_text())
    assert results["status"] == "complete" and results["populations"] == 1000
    assert results["source_sha256"] == digest(MAIN / "code_snapshot.py")
    hashes = json.loads((MAIN / "input_hashes.json").read_text())
    assert results["input_hashes_sha256"] == digest(MAIN / "input_hashes.json")
    spec = importlib.util.spec_from_file_location("channel_snapshot", MAIN / "code_snapshot.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    base = np.array([.2, .16, .14, .12, .11, .1, .09, .08])
    truth = np.array([np.roll(base, site + 2 * slot) for site in range(2) for slot in range(3)])
    pooled = np.zeros((6, 8, 8), dtype=int)
    negatives = {name: {"populations": 0, "cells": 0, "components": 0, "undefined": 0} for name in ["agreement", "known_channel"]}
    records, optimizations = [], []
    traces, objectives, replayed = 0, 0, 0
    for index in range(1000):
        path = SOURCE / f"dataset_{index:04d}.json"
        assert digest(path) == hashes[path.name]
        original = json.loads(path.read_text())
        record = json.loads((MAIN / path.name).read_text())
        assert record["input_sha256"] == hashes[path.name] and record["trial_index"] == index
        counts = independent_counts(original)
        assert np.array_equal(counts, record["counts"])
        pooled += counts
        agreement = sum(counts[c, x, x] for c in range(6) for x in range(8)) / 60
        assert agreement == record["agreement"]["agreement"]
        epsilon = 7 / 8 - math.sqrt(max(0, 7 * (8 * agreement - 1))) / 8
        assert abs(epsilon - record["agreement"]["epsilon"]) < 1e-14
        marginal = np.array([[sum(counts[c, x, b] + counts[c, b, x] for b in range(8)) / 20 for x in range(8)] for c in range(6)])
        for name, rate, key in [("agreement", epsilon, "raw_inverse"), ("known_channel", .1, "known_channel_raw_inverse")]:
            attenuation = 1 - 8 * rate / 7
            values = (marginal - rate / 7) / attenuation
            assert np.allclose(values, record[key], atol=1e-14)
            component_count, cell_count = int((values < -1e-12).sum()), int((values < -1e-12).any(axis=1).sum())
            assert record["negative_inversions"][name]["negative_components"] == component_count
            assert record["negative_inversions"][name]["affected_cells"] == cell_count
            negatives[name]["components"] += component_count
            negatives[name]["cells"] += cell_count
            negatives[name]["populations"] += cell_count > 0
            if name == "agreement":
                projection_conditions(values, np.array(record["estimates"]["agreement_projected"]))
        assert np.allclose(marginal, record["estimates"]["observed_marginal"])
        assert np.allclose((marginal * 10 + .5) / 14, record["estimates"]["smoothed_marginal"])
        for name, values in record["estimates"].items():
            p = np.array(values)
            assert np.all(p >= -1e-12) and np.allclose(p.sum(axis=1), 1)
            assert math.isclose(np.abs(p - truth).sum(axis=1).mean() / 2, record["frequency_metrics"][name]["total_variation"], abs_tol=1e-14)
            assert math.isclose(np.square(p - truth).mean(), record["frequency_metrics"][name]["component_mse"], abs_tol=1e-14)
        for name, fixed in [("joint_unknown", False), ("joint_known", True)]:
            fitted = record[name]
            assert fitted["selected_start"] == max(range(len(fitted["starts"])), key=lambda s: fitted["starts"][s]["objective"])
            assert fitted["fit"] == fitted["starts"][fitted["selected_start"]]
            for start in fitted["starts"]:
                assert 0 < start["epsilon"] < 7 / 8
                assert len(start["trace"]) == start["iterations"] + 1 and np.min(np.diff(start["trace"])) >= -1e-8
                values = scalar_objective(counts, np.array(start["p"]), start["epsilon"], fixed)
                assert np.allclose(values, [start["objective"], start["log_likelihood"], start["penalty"]], atol=1e-10, rtol=0)
                assert abs(start["trace"][-1] - start["objective"]) < 1e-12
                traces += 1
                objectives += 1
            if index in [0, 499, 999]:
                replay = module.joint_fit(counts, .1 if fixed else None)
                assert replay == fitted
                replayed += 1
        if index in [0, 499, 999]:
            optimizations.append({"trial_index": index, **numerical_check(counts, record["joint_unknown"]["fit"])})
        records.append(record)
    assert negatives == results["negative_inversions"]
    stored_pooled = json.loads((MAIN / "pooled.json").read_text())
    assert np.array_equal(pooled, stored_pooled["counts"])
    assert module.analyze(pooled) == stored_pooled
    assert module.bootstrap_summary(records) == results["summary"]
    report = {"status": "passed", "populations": 1000, "pairs": 60000, "independent_count_reconstructions": 1000,
              "independent_objective_checks": objectives, "trace_checks": traces, "fit_replays": replayed + 2,
              "bootstrap_replays": 20000, "simplex_kkt_checks": 6000, "separate_constrained_optimizer": optimizations,
              "input_results_sha256": digest(MAIN / "results.json"), "verification_source_sha256": digest(__file__)}
    endpoint.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    run()
