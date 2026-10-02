"""Reweight saved gap-count posteriors by their artificial masking law.

The fitted glyph/length models and every held-out query stay unchanged.
For survivors of total length m, candidate full length is L=m+k; the
internal-start factor 1/(m-1) cancels. Only 1/min(3,L-2) remains.
This is a benchmark-design sensitivity, not a historical erosion prior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

from conditional_structure import digest, group_records, load_records, make_folds

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from gap_restoration import summary
from restoration import paired_ci


def reweight(record):
    survivors = len(record["left"]) + len(record["right"])
    if not record["left"] or not record["right"]:
        raise ValueError("Benchmark law requires an internal gap with both sides surviving.")
    old = record["posterior"]
    if [p["count"] for p in old] != [1, 2, 3]:
        raise ValueError("This sensitivity is declared for candidate counts 1, 2, 3.")
    raw = np.asarray([p["model_mass"] / min(3, survivors + p["count"] - 2) for p in old])
    probs = raw / raw.sum()
    posterior = [{"count": p["count"], "model_mass": float(q)} for p, q in zip(old, probs)]
    best = max(posterior, key=lambda p: (p["model_mass"], -p["count"]))
    return dict(record, predicted=best["count"], top1=best["count"] == record["actual"],
                top_mass=best["model_mass"], posterior=posterior)


def main(args):
    source_dir = Path(args.prior)
    prior_path = source_dir / "gap_benchmark.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    inp = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
    if digest(inp) != prior["input_sha256"]:
        raise ValueError("The observational corpus changed since the original gap benchmark.")
    if digest(ROOT / "src/gap_restoration.py") != prior["source_sha256"]:
        raise ValueError("The gap source changed; use the original source snapshot before reweighting.")
    if prior["count_candidates"] != [1, 2, 3] or prior["alpha"] != 20:
        raise ValueError("Unexpected original candidate counts or frozen model smoothing.")
    rows, _ = load_records(inp, min_length=3, unique=True)
    groups = group_records(rows)
    folds, loads = make_folds(rows, groups, 5, prior["fold_seed"])
    lookup = {rows[i]["record_id"]: g for g, indices in enumerate(groups) for i in indices}
    records = {r["record_id"]: r for r in rows}
    expected = {}
    rng = np.random.default_rng(prior["query_seed"])
    for index, row in enumerate(rows):
        k = int(rng.integers(1, min(3, len(row["seq"]) - 2) + 1))
        start = int(rng.integers(1, len(row["seq"]) - k))
        expected[row["record_id"]] = (k, start, row["seq"][:start], row["seq"][start+k:], folds[index])
    original, corrected, paths = {}, {}, [prior_path]
    for name in ["baseline", "local"]:
        path = source_dir / f"{name}_count_audit.jsonl"
        paths.append(path)
        original[name] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if len(original[name]) != len(rows) or {r["record_id"] for r in original[name]} != set(records):
            raise ValueError("Saved posterior queries do not cover every original unique text exactly once.")
        for r in original[name]:
            observed = (r["actual"], r["slot"], tuple(r["left"]), tuple(r["right"]), r["fold"])
            if observed != expected[r["record_id"]]:
                raise ValueError(f"Query/fold mismatch for {r['record_id']}.")
            if abs(sum(p["model_mass"] for p in r["posterior"]) - 1) > 1e-10:
                raise ValueError("Saved count posterior is not normalized.")
        corrected[name] = [reweight(r) for r in original[name]]
    constant_one = [dict(r, top1=r["actual"] == 1) for r in corrected["local"]]
    result = {
        "design": "Post-audit artificial-gap-sampling-law sensitivity; unchanged fitted models and held-out queries.",
        "parameters": vars(args), "source_sha256": digest(__file__),
        "prior_result_sha256": digest(prior_path),
        "input_sha256": digest(inp),
        "dependency_sha256": {str(p.relative_to(ROOT)): digest(p) for p in [
            ROOT / "src/gap_restoration.py", ROOT / "src/restoration.py",
            ROOT / "src/methods/conditional_structure.py"]},
        "source_output_hashes": {str(p): digest(p) for p in paths},
        "count_candidates": [1, 2, 3], "alpha": prior["alpha"],
        "query_seed": prior["query_seed"], "fold_seed": prior["fold_seed"],
        "bootstrap_seed": 142, "bootstrap_draws": 10000,
        "unique_texts": len(rows), "physical_text_components": len(groups), "fold_token_loads": loads,
        "posterior_adjustment": "p_design(k|survivors) proportional to p_original(k|survivors) / min(3,m+k-2)",
        "start_factor": "1/(m-1), identical across count candidates and therefore canceled",
        "original_models": {name: summary(values) for name, values in original.items()},
        "design_matched_models": {name: summary(values) for name, values in corrected.items()},
        "design_matched_local_minus_independent": paired_ci(corrected["baseline"], corrected["local"], lookup),
        "design_matched_local_minus_constant_one": paired_ci(constant_one, corrected["local"], lookup),
        "design_matched_minus_original": {name: paired_ci(original[name], corrected[name], lookup)
                                          for name in corrected},
        "limitations": [
            "This law belongs to the artificial masking benchmark, not physical erosion.",
            "Model/count masses remain uncalibrated, and finite counts 1..3 omit other historical possibilities.",
            "Bootstrap conditions on unchanged fitted cross-validation models and sampled queries.",
            "Source glyph uncertainty, unknown sign count, separators and UNKNOWN pooling remain unresolved.",
        ],
    }
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "gap_design_matched.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    for name, values in corrected.items():
        (output / f"{name}_count_audit.jsonl").write_text("\n".join(json.dumps(r) for r in values), encoding="utf-8")
    print(json.dumps({"output": str(output), "design_matched_models": result["design_matched_models"],
                      "local_minus_independent": result["design_matched_local_minus_independent"],
                      "local_minus_constant_one": result["design_matched_local_minus_constant_one"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", default="results/gap_restoration")
    parser.add_argument("--output", default="research/methods/results/gap_design_matched")
    main(parser.parse_args())
