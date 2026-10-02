"""Read frozen aggregates and check this review's links; do not fit any model."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
inputs: dict[str, dict] = {}


def read(relative: str):
    path = ROOT / relative
    raw = path.read_bytes()
    inputs[relative] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return json.loads(raw)


def recoveries(rows):
    return {
        a: {"conditions": sum(x["algorithm"] == a for x in rows),
            "complete_maps": sum(x["algorithm"] == a and x["exact_recovery"] for x in rows)}
        for a in sorted({x["algorithm"] for x in rows})
    }


unique = read("research/methods/results/nested_unique_preserved_aliases/nested_results.json")["observed"]
unique = {k: unique[k] for k in ("records", "groups", "noninitial_tokens", "gain_bits_per_noninitial_sign", "gain_95pct_group_bootstrap_ci")}
annotation = read("results/independent_annotator/candidate_event_test.json")["all_clear_weighting"]
copies = read("experiments/2026-10-02-six-hour/null-calibration/main/results.json")["aggregate"]
copy_rates = {k: v["rejections"]["0.05"] for k, v in copies.items()}
selected = read("experiments/2026-10-02-six-hour/null-calibration/dedup-selection/results.json")["endpoints"]["nested_full_procedure"]
selected_rates = {k: v["rates"]["0.05"] for k, v in selected.items()}
lothal = read("experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json")
lothal_summary = {k: lothal[k] for k in ("eligible_objects", "distinct_complete_strings", "groups_spanning_physical_types")}
category = read("experiments/2026-10-02-decipherment-readiness/physical/current-checks.json")["lothal_single_category_per_complete_string"]["diagnostic_categories"]
category_summary = {k: category[k] for k in ("objects", "maximum_compatible_objects", "minimum_incompatible_objects")}
pool = read("experiments/2026-10-02-six-hour/khipu-control/conservation-check/main-v1/aggregate.json")
pool_rows = [x for x in pool["rows"] if x["prefix"] == 8 and x["condition"] == "four_swapped" and x["policy"] in ("baseline_half", "collective_half")]
selector = recoveries(read("experiments/2026-10-02-six-hour/reference-selector/main/results.json")["rows"])
mixture = recoveries(read("experiments/2026-10-02-six-hour/latent-forms/review-v1/reviewed-rows.json"))

assert unique["records"] == 1596 and unique["groups"] == 1526
assert abs(unique["gain_bits_per_noninitial_sign"] - 0.8483578853) < 1e-9
assert annotation["texts"] == 74 and annotation["noninitial_glyphs"] == 315
assert abs(annotation["gain_bits_per_noninitial_candidate_event"] - 0.7248273762) < 1e-9
assert copy_rates["physical_copies/record_columns"]["count"] == 159
assert copy_rates["physical_copies/block_columns"]["count"] == 54
assert selected_rates["uniform_reference_under_selected_law"] == "2783/54000"
assert selected_rates["selected_reference_under_selected_law"] == "667/13500"
assert lothal_summary["eligible_objects"] == 29 and lothal_summary["distinct_complete_strings"] == 9
assert category_summary == {"objects": 26, "maximum_compatible_objects": 20, "minimum_incompatible_objects": 6}
assert {(x["policy"], x["correct_relative"], x["wrong_relative"], x["abstained_ambiguity"]) for x in pool_rows} == {
    ("baseline_half", 133, 9, 58), ("collective_half", 190, 1, 9)}
assert {a: selector[a]["complete_maps"] for a in selector} == {
    "family_oracle": 310, "graph_multistart": 283, "length_slot": 168, "reference_selected": 309}
assert mixture["latent_mixture"]["complete_maps"] == 82
assert mixture["reference_selected_three"]["complete_maps"] == 79
assert mixture["reference_selected"]["complete_maps"] == 70

report_path = HERE / "REPORT.md"
report_bytes = report_path.read_bytes()
links = []
for target in re.findall(r"\]\(([^)]+)\)", report_bytes.decode("utf-8")):
    if target.startswith(("https://", "http://")):
        continue
    path = (HERE / target.split("#")[0]).resolve()
    links.append({"target": target, "exists": path.exists()})

out = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Read-only extracts, arithmetic assertions and local-link existence; no independent model replay or epigraphic verification.",
    "unique_prediction": unique,
    "candidate_event": annotation,
    "copy_calibration_at_five_percent": copy_rates,
    "deduplication_exact_rates_at_five_percent": selected_rates,
    "lothal": lothal_summary,
    "lothal_category_bound": category_summary,
    "four_swap_half_gate_final_prefix": pool_rows,
    "reference_selector": selector,
    "mixture": mixture,
    "input_hashes": inputs,
    "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
    "local_links": links,
    "all_local_links_exist": all(x["exists"] for x in links),
    "numeric_assertions_passed": True,
}
(HERE / "evidence-check.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"numeric_assertions_passed": True, "local_links": len(links), "missing_links": [x["target"] for x in links if not x["exists"]]}))
