"""Reviewer check: compare scores recomputed by the staged scorer with Package M's original metrics files.

Inputs (all read-only):
  staged v1/v2 score files produced by release/code/score_benchmark.py (in the raw directory)
  Package M frozen v1 metrics and repaired v2 adjudicated metrics
  release/benchmark/expected-metrics.json (the package's own copy of the targets)
Writes review/score-comparison.json.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
M = ROOT / "experiments/2026-10-07-helsinki1979-digitization"
RAWS = ROOT / "data/raw/2026-10-08-hf-public-release/review-scores"
REL = ROOT / "experiments/2026-10-08-hf-public-release/release"
TOL = 1e-12


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def walk(a, b, path, out, stats):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out["only_in_reference"].append(f"{path}/{k}")
            elif k not in b:
                out["only_in_staged"].append(f"{path}/{k}")
            else:
                walk(a[k], b[k], f"{path}/{k}", out, stats)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out["mismatch"].append(f"{path}: list length {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out, stats)
    elif isinstance(a, bool) or isinstance(b, bool) or isinstance(a, str) or isinstance(b, str) or a is None or b is None:
        stats["discrete"] += 1
        if a != b:
            out["mismatch"].append(f"{path}: {a!r} vs {b!r}")
    else:
        stats["numeric"] += 1
        if isinstance(a, float) or isinstance(b, float):
            if (a is None) != (b is None) or not (math.isclose(a, b, rel_tol=TOL, abs_tol=TOL) or (math.isnan(a) and math.isnan(b))):
                out["mismatch"].append(f"{path}: {a!r} vs {b!r}")
        elif a != b:
            out["mismatch"].append(f"{path}: {a!r} vs {b!r}")


def compare(ref, staged, keys):
    out = {"mismatch": [], "only_in_reference": [], "only_in_staged": []}
    stats = {"numeric": 0, "discrete": 0}
    for k in keys:
        if k in ref and k in staged:
            walk(ref[k], staged[k], k, out, stats)
        else:
            out["only_in_reference" if k in ref else "only_in_staged"].append(k)
    out["stats"] = stats
    return out


result = {}
pairs = {
    "v1": (M / "evaluation/2026-10-07-frozen-v1/metrics.json", RAWS / "staged-v1.json",
           ["summary", "rows", "row_bootstrap_95", "negative_result_criteria", "exploratory_sensitivities", "pipeline_status"]),
    "v2": (M / "repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json", RAWS / "staged-v2.json",
           ["summary", "rows", "row_bootstrap_95", "negative_result_criteria", "source_row_recall", "pipeline_status"]),
}
expected = load(REL / "benchmark/expected-metrics.json")
for v, (mp, sp, keys) in pairs.items():
    ref, staged = load(mp), load(sp)
    r = compare(ref, staged, keys)
    e = compare(expected[v], staged, [k for k in keys if k in expected[v]])
    h = {
        "strict_top5_whole_rows": staged["summary"]["strict_top5"]["whole_rows_all_sample"],
        "strict_top1_whole_rows": staged["summary"]["strict_top1"]["whole_rows_all_sample"],
        "crop": staged["summary"]["row_crop_correctness"],
        "count": staged["summary"]["drawn_unit_count_agreement"],
        "number": staged["summary"]["inscription_number_accuracy"],
        "classification": staged["summary"]["classification_exact_accuracy"],
        "criteria": staged["negative_result_criteria"],
        "pipeline_status": staged["pipeline_status"],
        "frozen_status_in_M": ref.get("status"),
        "M_pipeline_status": ref.get("pipeline_status"),
    }
    if v == "v2":
        h["random_recall"] = staged["source_row_recall"]["random"]["recall"]
        h["stress_recall"] = staged["source_row_recall"]["stress"]["recall"]
        h["strict_top5_aligned_recall"] = staged["summary"]["strict_top5"]["aligned_recall"]
    result[v] = {"vs_package_M": {k: (len(x) if isinstance(x, list) else x) for k, x in r.items()},
                 "vs_package_M_mismatch_paths": r["mismatch"][:40],
                 "vs_package_M_only_in_ref": r["only_in_reference"][:40],
                 "vs_expected_metrics_copy": {k: (len(x) if isinstance(x, list) else x) for k, x in e.items()},
                 "headline": h}
(ROOT / "experiments/2026-10-08-hf-public-release/review/score-comparison.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
print(json.dumps(result, indent=1)[:6000])
