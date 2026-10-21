"""Prepare an isolated Git index for the reviewed task, without changing HEAD."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PACKAGES = [
    "2026-10-20-reserved-test-program", "2026-10-20-fresh-test-collection",
    "2026-10-20-khirsara-reserve", "2026-10-20-farmana-reserve-review",
    "2026-10-20-foreign-script-audit", "2026-10-20-foreign-script-blind-review",
    "2026-10-20-foreign-script-verification",
]
REGISTRIES = ["RESERVED-TEST-PROGRAM", "FRESH-TEST-COLLECTION", "KHIRSARA-RESERVE", "FOREIGN-SCRIPT-AUDIT"]


def git(*args, env=None):
    return subprocess.check_output(["git", *args], cwd=ROOT, env=env).decode("utf-8").strip()


def main():
    output = HERE / "publication-package-v1.json"
    if output.exists():
        raise SystemExit("Preserve the existing packaging record; choose a new version")
    roots = ["experiments/" + name for name in PACKAGES]
    roots += [f"knowledge/registry/attempts/{name}-2026-10-20.json" for name in REGISTRIES]
    paths = sorted(git("ls-files", "--others", "--exclude-standard", "--", *roots).splitlines())
    included, excluded = [], []
    for name in paths:
        path = ROOT / name
        reason = None
        if name == "experiments/2026-10-20-fresh-test-collection/freeze.py":
            reason = "Hard-coded reserved measurements; preserve locally."
        elif path.suffix == ".json":
            value = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(value, dict) and "distributed_files" in value and "errors" in value:
                reason = "Whole-repository diagnostics contain unrelated document contexts."
        if reason:
            excluded.append({"path": name, "reason": reason})
        else:
            if path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".html", ".xml", ".txt"}:
                raise SystemExit("Unexpected source-like file: " + name)
            included.append({"path": name, "bytes": path.stat().st_size,
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    base = git("rev-parse", "origin/main")
    record = {"base_commit": base, "source_checkout_head": git("rev-parse", "HEAD"),
              "included": included, "excluded": excluded,
              "self_path": output.relative_to(ROOT).as_posix(),
              "reserved_raw_payload_opened": False}
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    index_dir = Path(git("rev-parse", "--absolute-git-dir")) / "task-reserve-publication-v1"
    index_dir.mkdir(exist_ok=False)
    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(index_dir / "index")
    git("read-tree", base, env=env)
    names = [r["path"] for r in included] + [record["self_path"]]
    pathspec = index_dir / "paths.txt"
    pathspec.write_bytes(b"\0".join(name.encode("utf-8") for name in names) + b"\0")
    git("add", "--pathspec-from-file=" + str(pathspec), "--pathspec-file-nul", env=env)
    actual = git("diff", "--cached", "--name-only", base, env=env).splitlines()
    if sorted(actual) != sorted(names):
        raise SystemExit("Isolated index differs from explicit reviewed file list")
    tree = git("write-tree", env=env)
    state = {"base": base, "tree": tree, "index": env["GIT_INDEX_FILE"], "file_count": len(actual),
             "excluded_count": len(excluded), "branch": "codex/reserved-collection-overseas-audit"}
    (index_dir / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state))


if __name__ == "__main__":
    main()
