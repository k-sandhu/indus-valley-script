"""Run the 0.3.0 card's Python examples against the private Hub repository, then test the documented prediction format.

1. Extract the card's ```python blocks from release/README.md and run the first two (hosted loading, snapshot_download) unchanged,
   with the Hugging Face caches redirected to a short path (Windows lock-file limit).
2. Build prediction files for v1, v2 and v3 from the documented fields only, once with the card's required-field names
   (printed_inscription_id, classification_literal) and once with the names the scorer reads (inscription_number, classification_code),
   score them with the snapshot's code/score_benchmark.py, and compare summary, rows and bootstrap with the baseline run.
3. Failing cases: missing unit confidence, confidence out of range or NaN, missing/invalid section for v2 and v3, units not a list.
Writes review-0.3.0/readme-snippets.json.
Usage: python -B readme_snippets_v3.py --work <dir under review-030-tmp>
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--cache", default="C:/hfc030/hubcache")
a = ap.parse_args()
work = Path(a.work)
work.mkdir(parents=True, exist_ok=True)
os.environ["HF_HUB_CACHE"] = a.cache
os.environ["HF_DATASETS_CACHE"] = "C:/hfc030/ds"
card = (PKG / "release/README.md").read_text(encoding="utf-8")
blocks = re.findall(r"```python\n(.*?)```", card, re.S)
out = {"python_blocks": len(blocks), "run": []}
ns = {}
for i, code in enumerate(blocks[:2]):
    try:
        exec(compile(code, f"card-block-{i}", "exec"), ns)
        out["run"].append({"block": i, "ok": True})
    except Exception as e:  # noqa: BLE001
        out["run"].append({"block": i, "ok": False, "error": repr(e)[:400]})
if "chart" in ns:
    out["chart_image_size"] = list(ns["chart"][0]["image"].size)
    out["rows_context_image_size"] = list(ns["rows"][0]["context_image"].size)
    out["sites_row0_keys"] = list(ns["sites"][0].keys())[:6]
    out["n_configs_listed"] = len(ns["tables"])
if "cards" in ns:
    out["card_image_size"] = list(ns["Image"].open(ns["snapshot"] / ns["cards"][0]["image_path"]).size)
    out["snapshot_has_scorer"] = (ns["snapshot"] / "code/score_benchmark.py").exists()
snapshot = ns.get("snapshot")
if snapshot is None:
    Path(__file__).with_name("readme-snippets.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    sys.exit(1)

import pyarrow.parquet as pq

DOC_ROW = ["sample_index", "occurrence_key", "pdf_page", "printed_inscription_id", "classification_literal"]


def minimal(v, names="scorer"):
    """Prediction rows from documented fields only. names="card": number and classification stored under the card's
    required-field names (printed_inscription_id, classification_literal); names="scorer": under the names the scorer reads
    (inscription_number, classification_code). Values come from the frozen predictions in both cases."""
    rows = pq.read_table(snapshot / f"data/benchmark_rows_{v}.parquet", columns=["prediction_json"]).to_pylist()
    res = []
    for r in rows:
        p = json.loads(r["prediction_json"])
        m = {k: p.get(k) for k in ("sample_index", "occurrence_key", "pdf_page")}
        if names == "card":
            m["printed_inscription_id"] = p.get("inscription_number")
            m["classification_literal"] = p.get("classification_code")
        else:
            m["inscription_number"] = p.get("inscription_number")
            m["classification_code"] = p.get("classification_code")
        m["section"] = p.get("section")
        m["units"] = [{"confidence": u["confidence"], "alternatives": [{"codes": x["codes"]} for x in u["alternatives"]]} for u in p["units"]]
        res.append(m)
    return res


def run(v, preds, tag):
    path = work / f"{tag}.jsonl"
    path.write_text("\n".join(json.dumps(p) for p in preds), encoding="utf-8")
    outp = work / f"score-{tag}.json"
    if outp.exists():
        outp.unlink()
    r = subprocess.run([sys.executable, "-B", str(snapshot / "code/score_benchmark.py"), "--release", str(snapshot), "--benchmark", v,
                        "--predictions", str(path), "--out", str(outp)], capture_output=True, text=True)
    return r, outp


def walk_eq(x, y, tol=1e-12):
    if isinstance(x, dict) and isinstance(y, dict):
        return set(x) == set(y) and all(walk_eq(x[k], y[k]) for k in x)
    if isinstance(x, list) and isinstance(y, list):
        return len(x) == len(y) and all(walk_eq(p, q) for p, q in zip(x, y))
    if isinstance(x, float) and isinstance(y, float):
        return math.isclose(x, y, rel_tol=tol, abs_tol=tol) or (math.isnan(x) and math.isnan(y))
    return x == y


base = ROOT / "data/raw/2026-10-08-hf-public-release/review-030-tmp/scores"
out["minimal_format"] = {}
for v in ("v1", "v2", "v3"):
    for names in ("card", "scorer"):
        r, outp = run(v, minimal(v, names), f"minimal-{v}-{names}")
        rec = {"returncode": r.returncode, "stderr_tail": r.stderr[-300:]}
        if r.returncode == 0:
            got = json.loads(outp.read_text())
            ref = json.loads((base / f"staged-{v}.json").read_text())
            rec["number_correct"] = got["summary"]["inscription_number_accuracy"]["success"]
            rec["classification_correct"] = got["summary"]["classification_exact_accuracy"]["success"]
            rec["baseline_number_correct"] = ref["summary"]["inscription_number_accuracy"]["success"]
            rec["baseline_classification_correct"] = ref["summary"]["classification_exact_accuracy"]["success"]
            rec["summary_equal_baseline"] = walk_eq(ref["summary"], got["summary"])
            rec["rows_equal_baseline"] = walk_eq(ref["rows"], got["rows"])
            rec["bootstrap_equal_baseline"] = walk_eq(ref["row_bootstrap_95"], got["row_bootstrap_95"])
            rec["calibration_n"] = got["summary"]["calibration"]["n"]
        out["minimal_format"][f"{v}:{names}_names"] = rec


def mutate(v, fn):
    p = minimal(v)
    fn(p)
    return p


def drop_conf(p):
    del p[3]["units"][0]["confidence"]


def conf_big(p):
    p[3]["units"][0]["confidence"] = 1.5


def conf_nan(p):
    p[3]["units"][0]["confidence"] = float("nan")


def conf_bool(p):
    p[3]["units"][0]["confidence"] = True


def drop_section(p):
    del p[5]["section"]


def bad_section(p):
    p[5]["section"] = "random_order"


def units_none(p):
    p[2]["units"] = None


def alt_conf_only(p):
    for u in p[0]["units"]:
        c = u.pop("confidence", 0.5)
        for x in u["alternatives"]:
            x["confidence"] = c


cases = {}
for v in ("v2", "v3"):
    for name, fn in [("missing_unit_confidence", drop_conf), ("confidence_above_1", conf_big), ("confidence_nan", conf_nan), ("confidence_bool", conf_bool),
                     ("missing_section", drop_section), ("invalid_section", bad_section), ("units_not_list", units_none), ("confidence_only_inside_alternatives", alt_conf_only)]:
        r, outp = run(v, mutate(v, fn), f"fail-{v}-{name}")
        cases[f"{v}:{name}"] = {"returncode": r.returncode, "message": (r.stderr.strip().splitlines() or [""])[-1][:160]}
r, outp = run("v1", mutate("v1", drop_conf), "fail-v1-missing_unit_confidence")
cases["v1:missing_unit_confidence"] = {"returncode": r.returncode, "message": (r.stderr.strip().splitlines() or [""])[-1][:160]}
r, outp = run("v3", minimal("v3")[:-1], "fail-v3-one-row-short")
cases["v3:one_row_short"] = {"returncode": r.returncode, "message": (r.stderr.strip().splitlines() or [""])[-1][:160]}
out["failing_cases"] = cases
Path(__file__).with_name("readme-snippets.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
