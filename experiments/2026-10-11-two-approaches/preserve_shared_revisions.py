"""Recover baseline versions without reverting newer shared-workspace files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-11-two-approaches/coordinator/preserved-start-v1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_bytes(spec):
    result = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, default=1)
    parser.add_argument("--include-unreachable-git", action="store_true")
    args = parser.parse_args()
    if args.version < 1:
        raise ValueError("Version must be positive")
    output = HERE / f"shared-revisions-v{args.version}.json"
    raw_output = RAW.parent / f"preserved-start-v{args.version}"
    if output.exists() or raw_output.exists():
        raise SystemExit("Preservation version exists; keep it and choose a new version.")
    baseline = json.loads((HERE / "baseline-v1.json").read_text(encoding="utf-8"))
    changed = [record for record in baseline["files"]
               if not record["navigation_may_be_extended"]
               and digest((ROOT / record["path"]).read_bytes()) != record["sha256"]]
    target_hashes = {record["sha256"] for record in changed}
    candidates = {}
    all_object_count = 0
    if args.include_unreachable_git:
        metadata = subprocess.run(["git", "cat-file", "--batch-all-objects",
                                   "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
                                  cwd=ROOT, capture_output=True, check=True)
        target_sizes = {record["bytes"] for record in changed}
        for line in metadata.stdout.decode("ascii").splitlines():
            object_id, kind, size = line.split()
            all_object_count += 1
            if kind == "blob" and int(size) in target_sizes:
                data = subprocess.run(["git", "cat-file", "blob", object_id], cwd=ROOT,
                                      capture_output=True, check=True).stdout
                value = digest(data)
                if value in target_hashes:
                    candidates[value] = (data, {"kind": "git-blob-by-exact-hash", "object_id": object_id})
    for directory in (ROOT / "experiments/2026-10-11-bonta-adversarial",
                      ROOT / "experiments/2026-10-08-bonta-extension"):
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in (".py", ".md", ".html", ".json"):
                data = path.read_bytes()
                value = digest(data)
                if value in target_hashes:
                    candidates[value] = (data, {"kind": "preserved-local-snapshot",
                                              "path": path.relative_to(ROOT).as_posix()})
    reflog = subprocess.run(["git", "reflog", "--all", "--format=%H", "-100"],
                            cwd=ROOT, capture_output=True, text=True, check=True)
    refs = list(dict.fromkeys(reflog.stdout.splitlines()))
    records = []
    raw_output.mkdir(parents=True, exist_ok=False)
    for record in changed:
        match = candidates.get(record["sha256"])
        if match is None:
            for ref in [":", "HEAD:"] + [value + ":" for value in refs]:
                data = git_bytes(ref + record["path"])
                if data is not None and digest(data) == record["sha256"]:
                    match = (data, {"kind": "git-object-witness", "spec": ref + record["path"]})
                    break
        saved = None
        if match is not None:
            saved = raw_output / "baseline" / record["path"]
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(match[0])
            assert digest(saved.read_bytes()) == record["sha256"]
        current_copy = raw_output / "current" / record["path"]
        current_copy.parent.mkdir(parents=True, exist_ok=True)
        current_copy.write_bytes((ROOT / record["path"]).read_bytes())
        records.append({"path": record["path"], "baseline_sha256": record["sha256"],
                        "current_sha256": digest((ROOT / record["path"]).read_bytes()),
                        "baseline_recovered": match is not None,
                        "baseline_copy": saved.relative_to(ROOT).as_posix() if saved else None,
                        "current_copy": current_copy.relative_to(ROOT).as_posix(),
                        "witness": match[1] if match else None})
    result = {"status": "shared-workspace-revision-preservation",
              "policy": "Do not revert current files. Recover exact original versions where existing snapshots/Git witnesses permit.",
              "changed_files": records, "recovered": sum(r["baseline_recovered"] for r in records),
              "unrecovered": sum(not r["baseline_recovered"] for r in records),
              "current_files_modified_by_this_script": 0,
              "git_objects_metadata_inspected": all_object_count,
              "scope": "The listed prior-program documents/code changed since the starting pins; new-program empirical endpoints are separate.",
              "code_sha256": digest(Path(__file__).read_bytes())}
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"changed": len(records), "recovered": result["recovered"],
                      "unrecovered": result["unrecovered"], "output": str(output)}))


if __name__ == "__main__":
    main()
