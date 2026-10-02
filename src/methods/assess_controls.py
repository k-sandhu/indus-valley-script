"""Record control comparability and grouping obstacles without changing units."""
import json
from pathlib import Path

from conditional_structure import digest, group_records, load_records, make_folds


paths = {
    "Indus": "data/normalized/lipi_clean_rtl_singleline.jsonl",
    "OfficeRoutes": "research/methods/controls/workflow_codes.jsonl",
    "TotemPoles": "research/literature/nonlinguistic_controls/TotemPoles_author_ordered.jsonl",
    "WeatherIcons": "research/literature/nonlinguistic_controls/WeatherIcons_author_ordered.jsonl",
}
results = {}
for name, path in paths.items():
    raw, excluded = load_records(path)
    unique, unique_excluded = load_records(path, unique=True)
    groups = group_records(raw)
    unique_groups = group_records(unique)
    info = {"input": path, "input_sha256": digest(path), "records": len(raw), "unique_strings": len(unique), "tokens": sum(len(r["seq"]) for r in raw), "types": len({s for r in raw for s in r["seq"]}), "groups": len(groups), "largest_group": max(map(len, groups)), "unique_groups_preserving_all_artifact_aliases": len(unique_groups), "largest_unique_group": max(map(len, unique_groups)), "fivefold_possible": len(groups) >= 5, "exclusions": excluded, "unique_exclusions": unique_excluded}
    if len(groups) >= 5:
        assignment, _ = make_folds(raw, groups, 5, 20261001)
        total, unknown = 0, 0
        for fold in range(5):
            known = {s for i, r in enumerate(raw) if assignment[i] != fold for s in r["seq"]}
            for i, row in enumerate(raw):
                if assignment[i] == fold:
                    total += len(row["seq"]) - 1
                    unknown += sum(s not in known for s in row["seq"][1:])
        info["heldout_noninitial_tokens"] = total
        info["heldout_noninitial_OOV_tokens"] = unknown
        info["heldout_noninitial_OOV_fraction"] = unknown / total
    results[name] = info
output = Path("research/methods/controls/comparability_assessment.json")
output.write_text(json.dumps({"scope": "Exploratory source/unit comparability audit, not a writing classifier", "source_sha256": digest(__file__), "results": results}, indent=2), encoding="utf-8")
print(json.dumps({name: {k: value for k, value in info.items() if k in {"records", "unique_strings", "tokens", "types", "groups", "largest_group", "unique_groups_preserving_all_artifact_aliases", "largest_unique_group", "heldout_noninitial_OOV_fraction"}} for name, info in results.items()}, indent=2))
