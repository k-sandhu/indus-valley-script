"""Compare scores recomputed by the staged scorer (release/code/score_benchmark.py) with package M's frozen metrics files
for v1, v2 and v3, leaf by leaf, and with release/benchmark/expected-metrics.json.

Usage (repository root): python -B experiments/2026-10-08-hf-public-release/review-0.3.0/compare_scores_v3.py --scores <dir with staged-v1.json, staged-v2.json, staged-v3.json>
Adapted from the 0.2.0 review's compare_scores.py (unchanged), with v3 added. Writes review-0.3.0/score-comparison.json.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
M = ROOT / "experiments/2026-10-07-helsinki1979-digitization"
REL = ROOT / "experiments/2026-10-08-hf-public-release/release"
TOL = 1e-12


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def walk(a, b, path, out, stats):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out["only_in_staged"].append(f"{path}/{k}")
            elif k not in b:
                out["only_in_reference"].append(f"{path}/{k}")
            else:
                walk(a[k], b[k], f"{path}/{k}", out, stats)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out["mismatch"].append(f"{path}: list length {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out, stats)
    elif isinstance(a, (bool, str)) or isinstance(b, (bool, str)) or a is None or b is None:
        stats["discrete"] += 1
        if a != b:
            out["mismatch"].append(f"{path}: {a!r} vs {b!r}")
    else:
        stats["numeric"] += 1
        if not (math.isclose(a, b, rel_tol=TOL, abs_tol=TOL) or (isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b))):
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


ap = argparse.ArgumentParser()
ap.add_argument("--scores", required=True)
a = ap.parse_args()
RAWS = Path(a.scores)
common = ["summary", "rows", "row_bootstrap_95", "negative_result_criteria", "pipeline_status"]
pairs = {
    "v1": (M / "evaluation/2026-10-07-frozen-v1/metrics.json", common + ["exploratory_sensitivities"]),
    "v2": (M / "repair/2026-10-07-v2/evaluation-2026-10-07-adjudicated/metrics.json", common + ["source_row_recall"]),
    "v3": (M / "repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json", common + ["source_row_recall", "physical_line_recall"]),
}
expected = load(REL / "benchmark/expected-metrics.json")
result = {}
for v, (mp, keys) in pairs.items():
    ref, staged = load(mp), load(RAWS / f"staged-{v}.json")
    r = compare(ref, staged, keys)
    exp = expected.get(v, {})
    e = compare(exp, staged, [k for k in keys if k in exp])
    s = staged["summary"]
    h = {
        "strict_top5_whole_rows": s["strict_top5"]["whole_rows_all_sample"],
        "strict_top1_whole_rows": s["strict_top1"]["whole_rows_all_sample"],
        "crop": s["row_crop_correctness"], "count": s["drawn_unit_count_agreement"],
        "number": s["inscription_number_accuracy"], "classification": s["classification_exact_accuracy"],
        "criteria": staged["negative_result_criteria"], "pipeline_status": staged["pipeline_status"],
        "M_pipeline_status": ref.get("pipeline_status"), "M_status": ref.get("status"),
        "strict_top5_aligned_recall": s["strict_top5"]["aligned_recall"],
    }
    if v in ("v2", "v3"):
        h["random_recall"] = staged["source_row_recall"]["random"]["recall"]
        h["stress_recall"] = staged["source_row_recall"]["stress"]["recall"]
    if v == "v3":
        h["physical_random_recall"] = staged["physical_line_recall"]["random"]["recall"]
        h["physical_stress_recall"] = staged["physical_line_recall"]["stress"]["recall"]
    result[v] = {
        "vs_package_M": {k: (len(x) if isinstance(x, list) else x) for k, x in r.items()},
        "vs_package_M_mismatch_paths": r["mismatch"][:40],
        "vs_package_M_only_in_reference": r["only_in_reference"][:40],
        "vs_package_M_only_in_staged": r["only_in_staged"][:40],
        "vs_expected_metrics_copy": {k: (len(x) if isinstance(x, list) else x) for k, x in e.items()},
        "vs_expected_mismatch_paths": e["mismatch"][:20],
        "headline": h,
    }
Path(__file__).with_name("score-comparison.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
print(json.dumps({v: {"M": x["vs_package_M"], "expected": x["vs_expected_metrics_copy"]} for v, x in result.items()}, indent=1))
for v in result:
    print(v, json.dumps(result[v]["headline"], default=str)[:1500])
