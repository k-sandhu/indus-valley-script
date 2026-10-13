"""Verify immutable endpoints and inventory this worker's owned package."""
from __future__ import annotations

import json
from pathlib import Path
import platform
import re

from grammar import digest, write_json
import numpy as np
import scipy

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
LOCAL = ROOT / "data/raw/2026-10-11-two-approaches/grammar"


def main():
    verification = PACKAGE / "verification.json"
    changed = PACKAGE / "changed-paths.json"
    if verification.exists() or changed.exists():
        raise FileExistsError("The final package audit is frozen; preserve it.")
    checks = []
    for run in ("run-v1", "run-v2-mixture", "run-v3-matched-mixtures"):
        completion = json.loads((PACKAGE / run / "completion.json").read_text())
        assert completion["complete"]
        for filename, expected in completion["tracked_output_sha256"].items():
            assert digest(PACKAGE / run / filename) == expected, (run, filename)
        for filename, expected in completion["local_only_output_sha256"].items():
            assert digest(LOCAL / run / filename) == expected, (run, filename)
        checks.append({"check": f"{run} completion and all frozen tracked/local output pins", "pass": True})
    primary = json.loads((PACKAGE / "run-v1/verification.json").read_text())
    assert primary["status"] == "verified-computation"
    review = ROOT / "experiments/2026-10-11-two-approaches/review/mixture-checks-v1.json"
    if review.exists():
        reviewer = json.loads(review.read_text())
        assert all(check["pass"] for check in reviewer["checks"])
        checks.append({"check": "independent parallel mixture review", "pass": True,
                       "checks_passed": len(reviewer["checks"]), "review_sha256": digest(review)})
    carry = json.loads((PACKAGE / "carry-forward.json").read_text())
    assert digest(ROOT / carry["input_path"]) == carry["input_sha256"]
    assert digest(ROOT / carry["local_class_model_path"]) == carry["local_class_model_sha256"]
    assert digest(PACKAGE / "predict.py") == carry["own_predictor_code_sha256"]
    mixtures = json.loads((PACKAGE / "run-v2-mixture/results.json").read_text())
    matched = json.loads((PACKAGE / "run-v3-matched-mixtures/results.json").read_text())
    assert carry["class_mixture_weight"] == mixtures["carry_forward_weight_from_pooled_inner_scores"]
    assert carry["position_mixture_weight"] == matched["carry_forward_position_weight_from_pooled_inner_scores"]
    checks.append({"check": "carry-forward inputs arrays predictor and pooled-inner weights", "pass": True})
    links = []
    for filename in ("REPORT.md", "README.md", "RETROSPECTIVE.md", "FUTURE-PREDICTIONS.md"):
        path = PACKAGE / filename
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("http://", "https://")):
                continue
            resolved = (path.parent / target).resolve()
            assert resolved.exists(), (filename, target)
            links.append({"document": filename, "target": target})
    prose = json.loads((PACKAGE / "prose-review.json").read_text())
    assert not prose["flags"]
    checks.append({"check": "owned prose scan and local Markdown links", "pass": True, "local_links": len(links)})
    sources = json.loads((PACKAGE / "sources.json").read_text())
    for source in sources["sources"]:
        if "local_witness" in source:
            witness = ROOT / source["local_witness"]
            assert witness.exists()
            source["local_witness_sha256"] = digest(witness)
            source["local_witness_bytes"] = witness.stat().st_size
    write_json(PACKAGE / "sources.json", sources)
    own_files = [path for path in PACKAGE.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    local_files = [path for path in LOCAL.rglob("*") if path.is_file()]
    planned = own_files + [changed, verification]
    write_json(changed, {"ownership": ["experiments/2026-10-11-two-approaches/grammar/", "data/raw/2026-10-11-two-approaches/grammar/"],
                         "tracked_candidate_paths": sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in planned),
                         "local_only_paths": sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in local_files),
                         "global_files_changed_by_this_worker": [], "old_endpoints_overwritten": False,
                         "publication_or_visibility_changed": False})
    payloads = {str(path.relative_to(PACKAGE)).replace("\\", "/"): digest(path) for path in own_files}
    payloads["changed-paths.json"] = digest(changed)
    write_json(verification, {"status": "verified-computation-and-package-integrity", "checks": checks,
                              "primary_verification_path": "run-v1/verification.json",
                              "primary_forward_tokens_verified": primary["grammar_forward_tokens_independently_recomputed"],
                              "all_three_endpoints_preserved": True, "bulk_outputs_local_only": True,
                              "own_files_sha256": payloads, "own_file_count_including_this_manifest": len(payloads) + 1,
                              "local_only_file_count": len(local_files),
                              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                              "scope": "Arithmetic, source/input pins, immutable outputs, prose/link inventory and reviewer checks. Semantic functions remain hypotheses."})
    print(json.dumps({"status": "complete", "owned_files": len(payloads) + 1, "local_only_files": len(local_files), "checks": checks}))


if __name__ == "__main__":
    main()
