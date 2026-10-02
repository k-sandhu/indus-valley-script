"""Preserve the first investigation locally without importing runtime caches or Git internals."""
from pathlib import Path
import hashlib
import json
import shutil
import argparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\sandh\Documents\Codex\2026-10-01\decipher-and-decode-the-indus-valley")
INCLUDE = ("research", "output", "results", "src", "PLAN.md", "data")
EXCLUDE = {".git", "__pycache__", "node_modules", ".pytest_cache"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair-imported-inputs", action="store_true", help="Preserve mismatching local data copies in quarantine, then restore the original source bytes")
    args = parser.parse_args()
    rows = []
    repairs = []
    for name in INCLUDE:
        source = SOURCE / name
        files = [source] if source.is_file() else source.rglob("*")
        for item in files:
            if not item.is_file() or any(part in EXCLUDE for part in item.relative_to(SOURCE).parts):
                continue
            rel = item.relative_to(SOURCE)
            target = ROOT / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if target.read_bytes() != item.read_bytes():
                    if not args.repair_imported_inputs or rel.parts[0] != "data":
                        raise RuntimeError(f"Refusing to overwrite a changed file: {rel}")
                    previous = target.read_bytes()
                    backup = ROOT / "archive/2026-10-01-investigation/interrupted-import" / rel
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    if backup.exists() and backup.read_bytes() != previous:
                        raise RuntimeError(f"Quarantine conflict: {rel}")
                    backup.write_bytes(previous)
                    stage = target.with_name(target.name + ".import-part")
                    shutil.copy2(item, stage)
                    stage.replace(target)
                    repairs.append({"path": rel.as_posix(), "previous_sha256": hashlib.sha256(previous).hexdigest(), "preserved_variant": backup.relative_to(ROOT).as_posix(), "cause": "mismatch found during resumed import; not inferred from hash alone"})
            else:
                # An interrupted copy must not leave a truncated file at the final path.
                stage = target.with_name(target.name + ".import-part")
                shutil.copy2(item, stage)
                stage.replace(target)
            content = item.read_bytes()
            rows.append({"path": rel.as_posix(), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
            if len(rows) % 1000 == 0:
                print(json.dumps({"copied_and_checked": len(rows), "current_path": rel.as_posix()}), flush=True)
    original_readme = ROOT / "archive" / "2026-10-01-investigation" / "README.original.md"
    original_readme.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE / "README.md", original_readme)
    dest = ROOT / "archive" / "2026-10-01-investigation" / "import-manifest.json"
    dest.write_text(json.dumps({"source": str(SOURCE), "excluded_runtime": sorted(EXCLUDE | {".vendor", ".playwright-cli", "tmp"}), "repaired_existing_inputs": repairs, "files": rows}, indent=2), encoding="utf-8")
    print(json.dumps({"files": len(rows), "bytes": sum(r["bytes"] for r in rows), "manifest": str(dest)}))

if __name__ == "__main__":
    main()
