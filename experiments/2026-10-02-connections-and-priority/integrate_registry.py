"""Append this continuation's entries, preserving all earlier registry values."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE = "b37c8fa0a55daf36c39a580ac55787fe12ba3aae"
relative = "knowledge/experiments/registry.json"
path = ROOT / relative
baseline_bytes = subprocess.check_output(["git", "show", f"{BASELINE}:{relative}"], cwd=ROOT)
baseline = json.loads(baseline_bytes)
current = json.loads(path.read_text(encoding="utf-8"))
additions = json.loads((HERE / "registry-additions.json").read_text(encoding="utf-8"))
assert current["experiments"][:len(baseline["experiments"])] == baseline["experiments"]
assert {k: v for k, v in current.items() if k != "experiments"} == {
    k: v for k, v in baseline.items() if k != "experiments"}
by_id = {row["id"]: row for row in current["experiments"]}
for row in additions:
    if row["id"] in by_id:
        assert by_id[row["id"]] == row, f"Existing entry differs: {row['id']}"
    else:
        current["experiments"].append(row)
        by_id[row["id"]] = row
assert len(by_id) == len(current["experiments"])
path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
new_bytes = path.read_bytes()
changed = subprocess.check_output(["git", "diff", BASELINE, "--name-only"], cwd=ROOT,
                                  text=True).splitlines()
allowed = {"README.md", "knowledge/INDEX.md", "knowledge/retrospectives/README.md", relative,
           "knowledge/provenance/repository-verification.json",
           "knowledge/provenance/git-payload-review.json"}
unexpected = [p for p in changed if p not in allowed and not p.startswith(
    "experiments/2026-10-02-connections-and-priority/") and p !=
    "knowledge/directions/regional-numerical-connections-2026-10-02.md"]
assert not unexpected, unexpected
result = {"status": "pass", "baseline_commit": BASELINE,
          "baseline_registry_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
          "baseline_entries": len(baseline["experiments"]),
          "all_baseline_entries_unchanged": True,
          "registry_entries_after": len(current["experiments"]),
          "new_registry_sha256": hashlib.sha256(new_bytes).hexdigest(),
          "added_ids": [r["id"] for r in additions],
          "changed_preexisting_paths": changed, "unexpected_changes": unexpected,
          "scope": "Earlier registry values and tracked-path preservation; new source witnesses remain local-only"}
(HERE / "baseline-preservation.json").write_text(json.dumps(result, indent=2) + "\n",
                                                  encoding="utf-8")
print(json.dumps(result))
