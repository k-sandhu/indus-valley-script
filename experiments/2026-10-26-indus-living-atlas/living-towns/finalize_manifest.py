"""Write the owned-path manifest and publication-scope checks; no data edits."""
import hashlib
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ATTEMPT = ROOT / "knowledge/registry/attempts/SOUTH-ASIA-LIVING-TOWNS-2026-10-26.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="changed-paths.json")
    parser.add_argument("--validation", default="validation-v3.json")
    args = parser.parse_args()
    out = HERE / args.out
    if out.exists():
        raise SystemExit(f"Refusing existing {out.name}")
    files = sorted(p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p != out)
    files.append(ATTEMPT)
    acquisitions = []
    for name in ["acquisition-v1.json", "acquisition-v2.json"]:
        acquisitions += [r["logical_path"] for r in json.loads((HERE / name).read_text(encoding="utf-8"))["records"] if r["status"] == "retrieved"]
    # NUL input preserves exact Windows paths without shell parsing or newline translation.
    proc = subprocess.run(["git", "check-ignore", "--stdin", "-z"], cwd=ROOT,
                          input=b"\0".join(p.encode("utf-8") for p in acquisitions) + b"\0", capture_output=True)
    ignored = [x.decode("utf-8") for x in proc.stdout.split(b"\0") if x]
    integrity = json.loads((HERE / "repository-integrity-v1.json").read_text(encoding="utf-8"))
    own_errors = [e for e in integrity["errors"] if "living-towns" in str(e) or "SOUTH-ASIA-LIVING-TOWNS" in str(e)]
    result = dict(schema_version="1.0", created_at=datetime.now(timezone.utc).isoformat(),
                  model="GPT-6; exact runtime build unavailable", harness="Codex API workspace", python=sys.version,
                  changed_paths=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p)) for p in files],
                  manifest_self="This file is omitted from its own hash list.",
                  final_validation=args.validation, frozen_data={n: sha(HERE / n) for n in ["towns.json", "sources.json"]},
                  publication_check=dict(acquired_responses=len(acquisitions), ignored=len(ignored), all_acquired_ignored=set(acquisitions) == set(ignored),
                                         owned_source_images_or_pdfs=[p.relative_to(ROOT).as_posix() for p in files if p.suffix.lower() in {".png", ".jpg", ".pdf"}]),
                  repository_snapshot=dict(errors=len(integrity["errors"]), owned_errors=own_errors),
                  commands=["python experiments/2026-10-26-indus-living-atlas/living-towns/acquire_sources.py",
                            "python experiments/2026-10-26-indus-living-atlas/living-towns/acquire_supplement.py",
                            "python experiments/2026-10-26-indus-living-atlas/living-towns/inspect_witnesses.py",
                            "python experiments/2026-10-26-indus-living-atlas/living-towns/build_register.py",
                            "python experiments/2026-10-26-indus-living-atlas/living-towns/validate.py --out validation-v3.json",
                            "python experiments/2026-10-26-indus-living-atlas/living-towns/check_package.py --out checks-v1.json --integrity",
                            "python experiments/2026-10-26-indus-living-atlas/living-towns/check_package.py --out checks-v2.json",
                            "python experiments/2026-10-26-indus-living-atlas/living-towns/finalize_manifest.py"],
                  endpoint_policy="Acquisition, inspection, validation and check commands refuse existing endpoints. Reproduce with a fresh dated directory or a new --out name where supported; the primary source manifests retain exact URLs and hashes.")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(paths=len(files) + 1, raw_ignored=result["publication_check"]["all_acquired_ignored"], owned_repository_errors=len(own_errors), frozen_data=result["frozen_data"])))


if __name__ == "__main__":
    main()
