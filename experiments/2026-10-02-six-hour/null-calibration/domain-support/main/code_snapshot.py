"""Exhibit a face-vector conditional space containing an infeasible grouped fit."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "knowledge").is_dir())
PARENT = ROOT / "experiments/2026-10-02-six-hour/null-calibration"
FOLDER = PARENT / "domain-support"


def run():
    output = FOLDER / "main"
    if output.exists():
        raise FileExistsError("Refusing an existing domain witness")
    output.mkdir(parents=True)
    shutil.copyfile(__file__, output / "code_snapshot.py")
    snapshot = PARENT / "noisy-faces/main/code_snapshot.py"
    spec = importlib.util.spec_from_file_location("frozen_faces_domain", snapshot)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    old, helper, joint, hashes = module.preserved_methods()
    # Distinct base-eight words use a fixed multiplicative index ordering.
    strings = [tuple(f"{(value // divisor) % 8 + 1:03d}" for divisor in [64, 8, 1]) for value in [(73 * i) % 512 for i in range(21)]]
    assert len(set(strings)) == 21
    rows = []
    for index in range(20):
        site = f"site_{int(index >= 10)}"
        artifact = f"artifact_{index:03d}"
        for face in range(2):
            rows.append({"record_id": f"record_{len(rows):03d}", "seq": strings[index + face], "artifact": artifact,
                         "artifact_aliases": [artifact], "site": site, "object_type": "SEAL:S", "stratum": (site, "SEAL:S")})
    groups = joint.rebuild_groups(rows)
    assert len(set(groups)) == 1
    failure = None
    try:
        old.fit(rows, joint)
    except Exception as error:
        failure = {"exception": type(error).__name__, "message": str(error)}
    assert failure is not None
    attempts = []
    for offset in range(10000):
        seed = 2026100208 + offset
        proposed = module.vector_shuffle(rows, seed)
        proposed_groups = joint.rebuild_groups(proposed)
        count = len(set(proposed_groups))
        attempts.append({"seed": seed, "components": count})
        assert module.vector_margins(rows) == module.vector_margins(proposed)
        assert old.margins(rows) == old.margins(proposed)
        assert all(all(a[key] == b[key] for key in a if key != "seq") for a, b in zip(rows, proposed))
        if count >= 5:
            compact, full = old.fit(proposed, joint)
            break
    else:
        raise RuntimeError("No feasible conditional table found in the declared seed search")
    result = {"status": "complete", "simulation": True, "connected_rows": rows, "connected_components": 1,
              "connected_fit_failure": failure, "feasible_rows": proposed, "feasible_components": count,
              "feasible_score": compact, "feasible_full_score": full, "search_attempts": attempts,
              "same_ordered_vector_margins": True, "same_expanded_record_margins": True,
              "positive_observed_probability_argument": "Each latent category has positive p and every kernel entry is positive at epsilon .1.",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "protocol_sha256": hashlib.sha256((FOLDER / "PROTOCOL.md").read_bytes()).hexdigest(),
              "preserved_face_source_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(), "preserved_method_hashes": hashes}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "failure": failure, "feasible_components": count, "attempts": len(attempts)}), flush=True)


if __name__ == "__main__":
    run()
