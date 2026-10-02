"""Read preserved endpoints and produce a bounded physical-readiness audit."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


groups_path = "experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json"
groups = read(groups_path)["groups"]
fits = {}
for view, excluded in [("diagnostic_categories", {"undiagnostic"}), ("all_recorded_categories", set())]:
    rows = []
    for group in groups:
        counts = {k: v for k, v in group["physical_types"].items() if k not in excluded}
        n = sum(counts.values())
        best = max(counts.values(), default=0)
        rows.append({"group_id": group["group_id"], "objects": n, "category_counts": counts,
                     "maximum_compatible_objects": best,
                     "minimum_incompatible_objects": n - best,
                     "all_maximizers": sorted(k for k, v in counts.items() if v == best)})
    fits[view] = {"rows": rows, "objects": sum(x["objects"] for x in rows),
                  "maximum_compatible_objects": sum(x["maximum_compatible_objects"] for x in rows),
                  "minimum_incompatible_objects": sum(x["minimum_incompatible_objects"] for x in rows)}

metrology_path = "research/literature/metrology/source_and_identifiability_audit.json"
metrology = read(metrology_path)
capacity_rows = metrology["source_preserved_capacities"]
eligibility = {"source_rows": len(capacity_rows),
               "eligible_independent_heldout_rows": sum(bool(x["eligible_independent_heldout_40_4_test"]) for x in capacity_rows),
               "rows": [{"object": x["object"], "eligible": x["eligible_independent_heldout_40_4_test"],
                         "liquid_fill_measured": x["volume_is_measured_liquid_fill"]} for x in capacity_rows]}

solutions = []
for L, S, v in [(4, 20, 36), (6, 8, 10), (10, 8, 6), (36, 20, 4)]:
    residuals = [v - (2*S-L), v*L+1-(7*S+5), (2*L-7)*S-(L*L+4)]
    assert residuals == [0, 0, 0]
    solutions.append({"L": L, "S": S, "v": v, "bangle_expression_7_plus_L": 7+L, "residuals": residuals})

susa = []
for values in [(1, 2, 1, 2), (1, 2, 2, 1)]:
    residual = sum(a*b for a, b in zip((3, 3, -3, -3), values))
    assert residual == 0
    susa.append({"internal_and_external_class_values": values, "residual": residual})

assert fits["diagnostic_categories"]["objects"] == 26
assert fits["diagnostic_categories"]["minimum_incompatible_objects"] == 6
assert fits["all_recorded_categories"]["objects"] == 29
assert fits["all_recorded_categories"]["minimum_incompatible_objects"] == 9
assert eligibility["source_rows"] == 8
assert eligibility["eligible_independent_heldout_rows"] == 0

write("current-checks.json", {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Post-outcome descriptive source audit. No fresh prediction targets or simulation sweeps.",
    "protocol_sha256": sha(OUT / "PROTOCOL.md"), "code_sha256": sha(Path(__file__)),
    "input_hashes": {groups_path: sha(ROOT / groups_path), metrology_path: sha(ROOT / metrology_path)},
    "lothal_single_category_per_complete_string": fits,
    "metrology_eligibility": eligibility,
    "published_equality_solution_substitutions": solutions,
    "susa_equal_mixture_witnesses": susa,
    "checks_passed": 12,
})

registry_path = "knowledge/experiments/registry.json"
registry = read(registry_path)["experiments"]
audited = {
    "ROOT-09": "Broad site/type/motif and microcontext endpoints: target availability and object dependence.",
    "ROOT-10": "Paired-face summary and numeric-object audit; original source recommendations.",
    "ROOT-11": "Candidate-pair priority and source illustration audit; no independent referent.",
    "ROOT-13": "Exact equality audit, original-source premises and four-solution substitution check.",
    "ROOT-14": "Capacity identity/eligibility audit and scale invariance.",
    "ROOT-19": "Original specimen joins and preserved source/scan identity notes.",
    "METHODS-numerical_equalities": "Original numerical-equality result and premise audit.",
    "CONTEXT-01": "Source-defined physical frames and context availability.",
    "PHYS-01": "Physical-information source targets, corrected count anchor, positive alternatives.",
    "PHYS-02": "Acquisition report/source measurements, undercovered count and held-out scale failures.",
    "ARCH-01": "Harappa object/caption/display ledgers and scale/orientation correction.",
    "ARCH-02": "Lothal table/trace/source assertions, joins and complete-string groups.",
    "ARCH-03": "Harappa tablet representation and source-defined orientation premises.",
    "COMM-02": "Tell Jokha original-report pointer, photographed panel and failed retrieval records.",
    "GEOM-01": "Stamp geometry sources and prospective transfer protocol.",
    "KANMER-01": "Object frame, registrations, source-relative views and proposed handling protocol.",
    "KANMER-02": "Original bibliography/holding and final-page acquisition amendment.",
    "KHI-01": "Six actual accounts, source exposure, published alignment and reconstruction scope.",
    "KHI-02": "Source-selected physical intervals, grouping priors and tied/missing gaps.",
    "KHI-03": "Fresh generated noisy-membership consensus and false accepted vectors.",
    "KHI-04": "Fresh generated collective-conservation premises and rank-one failure.",
    "KHI-05": "Post-outcome validation policies, rank, scale and check availability.",
}
ids = [entry["id"] for entry in registry]
assert len(ids) == len(set(ids))
assert set(audited) <= set(ids)
write("coverage.json", {
    "created_utc": datetime.now(timezone.utc).isoformat(), "registry_sha256": sha(ROOT / registry_path),
    "registry_entries": len(ids), "catalogue_read_ids": ids,
    "physical_source_and_endpoint_review": [{"id": k, "scope": v} for k, v in audited.items()],
    "remaining_ids": [x for x in ids if x not in audited],
    "coverage_definition": "All catalogue entries read for scope. Detailed endpoint/source review is limited to the listed physical subset; other agents own linguistic/corpus/statistical readiness.",
})
print(json.dumps({"lothal": {k: {x: v[x] for x in ["objects", "maximum_compatible_objects", "minimum_incompatible_objects"]} for k, v in fits.items()},
                  "eligible_capacity_rows": eligibility["eligible_independent_heldout_rows"],
                  "registry_entries": len(ids), "detailed_physical_ids": len(audited)}, indent=2))
