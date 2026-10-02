"""Latent independent-slot templates as a stronger nonphonetic baseline."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from conditional_structure import Model, digest, group_records, load_records, make_folds
from nested_conditional import fixed_groups, tune


class Templates:
    def __init__(self, rows, max_components, alpha, seed=20261001, starts=2, iterations=40, min_per_component=10):
        self.base = Model(rows, 100)
        self.alpha = alpha
        self.components = {}
        self.log_likelihood = 0.0
        by_length = defaultdict(list)
        for row in rows:
            by_length[len(row["seq"])].append(row)
        for length, items in sorted(by_length.items()):
            matrix = np.array([[self.base.index[s] for s in row["seq"]] for row in items], dtype=int)
            zvalues = sorted({row["stratum"] for row in items})
            zindex = {z: n for n, z in enumerate(zvalues)}
            z = np.array([zindex[row["stratum"]] for row in items], dtype=int)
            k = max(1, min(max_components, len(items) // min_per_component))
            prior = np.stack([self.base.distributions(length, j, ("NEVER", "NEVER"), None)[0] for j in range(length)])
            best = None
            for start in range(starts if k > 1 else 1):
                rng = np.random.default_rng(seed + length * 1000 + start)
                theta = np.broadcast_to(prior, (k, length, len(self.base.signs))).copy()
                if k > 1:
                    selected = rng.choice(len(items), k, replace=False)
                    theta *= 0.5
                    for component, row_index in enumerate(selected):
                        theta[component, np.arange(length), matrix[row_index]] += 0.5
                pi = np.full(k, 1 / k)
                piz = np.tile(pi, (len(zvalues), 1))
                previous_ll = -float("inf")
                for iteration in range(iterations):
                    logp = np.log(piz[z])
                    for j in range(length):
                        logp += np.log(theta[:, j, matrix[:, j]].T)
                    shift = logp.max(axis=1)
                    exp = np.exp(logp - shift[:, None])
                    norm = exp.sum(axis=1)
                    responsibilities = exp / norm[:, None]
                    ll = float((shift + np.log(norm)).sum())
                    if iteration > 2 and abs(ll - previous_ll) < 1e-7 * (1 + abs(previous_ll)):
                        break
                    previous_ll = ll
                    totals = responsibilities.sum(axis=0)
                    pi = (totals + 0.5) / (len(items) + k * 0.5)
                    for stratum in range(len(zvalues)):
                        selected_z = z == stratum
                        counts = responsibilities[selected_z].sum(axis=0)
                        piz[stratum] = (counts + 20 * pi) / (selected_z.sum() + 20)
                    for component in range(k):
                        for j in range(length):
                            counts = np.bincount(matrix[:, j], weights=responsibilities[:, component], minlength=len(self.base.signs))
                            theta[component, j] = (counts + alpha * prior[j]) / (totals[component] + alpha)
                # Score the final update too, so start selection compares fitted models.
                logp = np.log(piz[z])
                for j in range(length):
                    logp += np.log(theta[:, j, matrix[:, j]].T)
                shift = logp.max(axis=1)
                ll = float((shift + np.log(np.exp(logp - shift[:, None]).sum(axis=1))).sum())
                fitted = {"theta": theta, "pi": pi, "piz": {value: piz[n].copy() for value, n in zindex.items()}, "k": k, "training_ll": ll, "iterations": iteration + 1}
                if best is None or ll > best["training_ll"]:
                    best = fitted
            self.components[length] = best
            self.log_likelihood += best["training_ll"]

    def score(self, row):
        seq = row["seq"]
        fitted = self.components.get(len(seq))
        if fitted is None:
            return [math.log2(float(self.base.unigram[self.base.index.get(s, self.base.index["__UNKNOWN__"])])) for s in seq]
        theta = fitted["theta"]
        weights = fitted["piz"].get(row["stratum"], fitted["pi"]).copy()
        result = []
        for j, sign in enumerate(seq):
            c = self.base.index.get(sign, self.base.index["__UNKNOWN__"])
            likelihood = theta[:, j, c]
            prob = float(weights @ likelihood)
            result.append(math.log2(prob))
            weights *= likelihood
            weights /= weights.sum()
        return result


def tune_templates(rows, seed, component_grid=(1, 2, 4, 8, 16), min_per_component=10):
    assignment, _ = make_folds(rows, fixed_groups(rows), 3, seed)
    totals = Counter()
    count = 0
    for fold in range(3):
        train = [r for i, r in enumerate(rows) if assignment[i] != fold]
        test = [r for i, r in enumerate(rows) if assignment[i] == fold]
        count += sum(len(r["seq"]) - 1 for r in test)
        for k in component_grid:
            for alpha in [5, 20, 100]:
                model = Templates(train, k, alpha, seed + fold, min_per_component=min_per_component)
                totals[(k, alpha)] += sum(sum(model.score(r)[1:]) for r in test)
    chosen = max(totals, key=totals.get)
    return chosen, {f"K{k}@{alpha}": -score / count for (k, alpha), score in sorted(totals.items())}


def main(args):
    start = time.monotonic()
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, excluded = load_records(args.input, 3, args.unique, False, collapse)
    groups = group_records(rows)
    assignment, loads = make_folds(rows, groups, 5, args.seed)
    for group, indices in enumerate(groups):
        for i in indices:
            rows[i]["analysis_group"] = group
    result = {"design": "Declared latent independent-slot template robustness; no phonetic values", "input_sha256": digest(args.input), "source_sha256": digest(__file__), "parameters": vars(args), "exclusions": excluded, "records": len(rows), "groups": len(groups), "fold_loads": loads, "folds": []}
    totals = Counter()
    per_group = defaultdict(lambda: {"PMB_minus_TEMPLATE": [0.0, 0], "TEMPLATE_minus_BASELINE": [0.0, 0]})
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    for fold in range(5):
        train = [r for i, r in enumerate(rows) if assignment[i] != fold]
        test = [r for i, r in enumerate(rows) if assignment[i] == fold]
        baseline, dependent, scores = tune(train, args.seed + fold)
        component_grid = tuple(map(int, args.component_grid.split(",")))
        template, template_scores = tune_templates(train, args.seed + fold, component_grid, args.min_per_component)
        print(json.dumps({"stage": "selected", "fold": fold, "template": template, "baseline": baseline, "dependent": dependent}), flush=True)
        models = {alpha: Model(train, alpha) for alpha in {baseline[1], dependent[1]}}
        templ = Templates(train, *template, args.seed + fold, min_per_component=args.min_per_component)
        fold_totals = Counter()
        count = 0
        for row in test:
            bs, _ = models[baseline[1]].score(row)
            ds, _ = models[dependent[1]].score(row)
            b, d = sum(bs[baseline[0]][1:]), sum(ds[dependent[0]][1:])
            t = sum(templ.score(row)[1:])
            n = len(row["seq"]) - 1
            for name, score in [("BASELINE", b), ("PMB", d), ("TEMPLATE", t)]:
                fold_totals[name] += score
                totals[name] += score
            count += n
            totals["tokens"] += n
            for name, delta in [("PMB_minus_TEMPLATE", d - t), ("TEMPLATE_minus_BASELINE", t - b)]:
                per_group[row["analysis_group"]][name][0] += delta
                per_group[row["analysis_group"]][name][1] += n
        result["folds"].append({"fold": fold, "noninitial_tokens": count, "baseline": baseline, "dependent": dependent, "template": template, "template_components_per_length": {str(length): {"k": fitted["k"], "iterations": fitted["iterations"]} for length, fitted in templ.components.items()}, "inner_template_cross_entropy_bits": template_scores, "inner_other_cross_entropy_bits": scores, "outer_cross_entropy_bits": {name: -score / count for name, score in fold_totals.items()}, "PMB_minus_TEMPLATE_gain_bits": (fold_totals["PMB"] - fold_totals["TEMPLATE"]) / count})
        result["elapsed_seconds"] = time.monotonic() - start
        (out / "template_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps({"stage": "fold_complete", "fold": fold, "gain": result["folds"][-1]["PMB_minus_TEMPLATE_gain_bits"], "seconds": result["elapsed_seconds"]}), flush=True)
    result["noninitial_tokens"] = totals["tokens"]
    result["outer_cross_entropy_bits"] = {name: -totals[name] / totals["tokens"] for name in ["BASELINE", "PMB", "TEMPLATE"]}
    result["contrasts"] = {}
    rng = np.random.default_rng(args.seed)
    for name in ["PMB_minus_TEMPLATE", "TEMPLATE_minus_BASELINE"]:
        values = np.array([data[name] for data in per_group.values()], dtype=float)
        draws = []
        for i in range(args.bootstrap):
            sample = values[rng.integers(0, len(values), len(values))]
            draws.append(sample[:, 0].sum() / sample[:, 1].sum())
        result["contrasts"][name] = {"gain_bits_per_noninitial_sign": float(values[:, 0].sum() / values[:, 1].sum()), "95pct_group_bootstrap_ci": [float(x) for x in np.quantile(draws, [0.025, 0.975])]}
    result["elapsed_seconds"] = time.monotonic() - start
    (out / "template_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"stage": "complete", "output": str(out), "contrasts": result["contrasts"], "seconds": result["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--unique", action="store_true")
    parser.add_argument("--collapse")
    parser.add_argument("--component-grid", default="1,2,4,8,16")
    parser.add_argument("--min-per-component", type=int, default=10)
    main(parser.parse_args())
