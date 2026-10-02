"""Verify completed extension provenance and an unchanged prior seed prefix."""
import argparse
import json
from pathlib import Path

from conditional_structure import digest


def main(args):
    target = Path(args.result)
    result = json.loads(target.read_text(encoding="utf-8"))
    extension = result["extension"]
    prior_path = Path(extension["prior_path"])
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    assert extension["complete"] is True
    assert digest(prior_path) == extension["prior_sha256"]
    assert result["observed"] == prior["observed"]
    assert result["null_position"] == prior["null_position"]
    initial = prior["null_position_metadata"]["values"]
    current = result["null_position_metadata"]
    assert current["values"][:len(initial)] == initial
    assert len(current["values"]) == current["permutations"] == extension["parameters"]["permutations"]
    assert not current.get("in_progress", False)
    observed = result["observed"]["gain_bits_per_noninitial_sign"]
    exceedances = sum(v >= observed for v in current["values"])
    assert current["p_one_sided"] == (1 + exceedances) / (1 + current["permutations"])
    files = list(Path("src/methods").glob("*.py")) + list(Path("research/methods/code_snapshots").glob("*.py"))
    matches = {}
    for key in ["runner_sha256", "fit_source_sha256", "nested_source_sha256", "loader_source_sha256"]:
        matches[key] = [str(path) for path in files if digest(path) == extension[key]]
        assert matches[key], f"No preserved source for {key}"
    audit = {
        "result_path": str(target), "result_sha256": digest(target),
        "prior_sha256_verified": extension["prior_sha256"],
        "unchanged_prior_metadata_seed_prefix": len(initial),
        "unchanged_observed_and_position_reference": True,
        "completed_metadata_shuffles": current["permutations"],
        "metadata_exceedances": exceedances, "p_one_sided": current["p_one_sided"],
        "matched_preserved_sources": matches,
        "extension_elapsed_seconds": extension["elapsed_seconds"],
        "scope": "Provenance/completion verification; the randomization reference remains conditional on its stated margins.",
    }
    output = target.with_name("extension_audit.json")
    output.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", default="research/methods/results/joint_nested_primary_1000/joint_nested_results.json")
    main(parser.parse_args())
