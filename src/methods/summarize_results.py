"""Compact result index without copying corpus text or simulation arrays."""
import json
from pathlib import Path


BASE = Path("research/methods/results")
def small(value):
    if isinstance(value, dict):
        return {k: small(v) for k, v in value.items() if k not in {"values", "null_max_values", "max_support_values", "accepted_seeds", "inner_scores", "inner_noninitial_cross_entropy_bits", "pair_support", "top_pairs", "frames", "new_frames", "contexts"}}
    if isinstance(value, list):
        return [small(v) for v in value]
    return value


summary = {"scope": "Structural constraints and falsification work; no phonetic assignments, translations, or language identification", "results": {}}
for directory in sorted(BASE.iterdir()):
    records = {}
    for filename in ["nested_results.json", "alias_safe_site_transfer.json", "transitive_site_transfer.json", "template_results.json", "substitution_validation.json", "adjusted_max_results.json", "joint_null_results.json", "joint_nested_results.json", "conditional_results.json", "gap_design_matched.json", "numerical_equalities_audit.json", "numerical_count_delta_sensitivity.json", "audit.json", "completion_audit.json", "evaluation_post_reference.json"]:
        path = directory / filename
        if not path.exists():
            continue
        full = json.loads(path.read_text(encoding="utf-8"))
        entry = {"path": str(path), "design": full.get("design"), "parameters": full.get("parameters"), "elapsed_seconds": full.get("elapsed_seconds")}
        for key in ["input_sha256", "source_sha256", "dependency_source_sha256", "extension"]:
            if key in full:
                entry[key] = small(full[key])
        if filename in {"nested_results.json", "joint_nested_results.json"}:
            entry.update({"observed": small(full.get("observed")), "largest_group": max(full.get("group_sizes", [0])), "leave_site_out": small(full.get("leave_site_out")), "null_position": small(full.get("null_position")), "null_position_metadata": small(full.get("null_position_metadata"))})
        elif filename in {"alias_safe_site_transfer.json", "transitive_site_transfer.json"}:
            entry.update({"records": full["records"], "groups": full["groups"], "largest_group": max(full["group_sizes"]), "leave_site_out": small(full["leave_site_out"])})
        elif filename == "template_results.json":
            entry.update(small({k: v for k, v in full.items() if k not in {"input_sha256", "source_sha256", "dependency_source_sha256", "parameters", "folds"}}))
        elif filename == "substitution_validation.json":
            entry.update(small({k: full.get(k) for k in ["records", "groups", "maximum_known_distinct_class_pair_support", "transfer_counts_by_category", "null_position", "null_position_metadata"]}))
        elif filename == "joint_null_results.json":
            entry.update(small({k: full.get(k) for k in ["records", "observed_transfer", "observed_grouping", "null_position", "null_position_metadata"]}))
        elif filename == "adjusted_max_results.json":
            entry.update(small({k: full.get(k) for k in ["records", "null_position", "null_position_metadata"]}))
        elif filename == "gap_design_matched.json":
            entry.update(small({k: full.get(k) for k in ["unique_texts", "physical_text_components", "posterior_adjustment", "original_models", "design_matched_models", "design_matched_local_minus_independent", "design_matched_local_minus_constant_one", "design_matched_minus_original", "limitations", "prior_result_sha256", "source_output_hashes"]}))
        elif filename == "numerical_equalities_audit.json":
            entry.update(small({k: full.get(k) for k in ["scope", "assumed_equalities", "derived_relation", "all_admissible_solutions", "range_sensitivities", "redundant_assumptions_in_exact_joint_system", "first_equality_parity_audit", "source_cautions", "brute_force_check"]}))
        elif filename in {"numerical_count_delta_sensitivity.json", "audit.json", "completion_audit.json"}:
            entry.update(small(full))
        elif filename == "evaluation_post_reference.json":
            entry.update(small({k:v for k,v in full.items() if k != "rows"}))
        else:
            entry.update(small({"primary": full.get("primary"), "null_position": full.get("null_position"), "null_position_metadata": full.get("null_position_metadata"), "transfer_position": full.get("substitutions", {}).get("transfer_null_position"), "transfer_metadata": full.get("substitutions", {}).get("transfer_null_position_metadata")}))
        if directory.name in {"nested_unique", "classaware_unique"}:
            entry["superseded_caution"] = "Unique loader dropped original artifact aliases; superseded by *_preserved_aliases results. Full-graph adjusted counts unchanged by this repair."
        if filename == "substitution_validation.json" or filename == "conditional_results.json":
            entry["conditional_transfer_caution"] = "Foldwise training discoveries remain fixed during held-out permutation. The aggregate is a conditional diagnostic; prefer joint_transfer_* for a full-procedure null."
        if filename == "nested_results.json":
            entry["fixed_fold_null_caution"] = "Original data-derived groups/folds fixed under shuffling; joint_nested_* reruns grouping and nested fitting."
            entry["site_transfer_caution"] = "Earlier site-transfer values exclude direct overlaps only; use separate transitive_site_transfer.json where present for full component-safe transfer."
        records[filename] = entry
    if records:
        summary["results"][directory.name] = records
target = Path("research/methods/RESULT_INDEX.json")
target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps({"output": str(target), "runs_indexed": len(summary["results"])}))
