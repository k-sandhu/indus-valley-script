"""Manual integrity checks for the knowledge package. No CI/CD is involved."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-import", action="store_true", help="Hash every imported local source file; may take several minutes")
    args = parser.parse_args()
    errors = []
    required = ["README.md", "knowledge/INDEX.md", "knowledge/experiments/registry.json", "REPRODUCING.md",
                "papers/001-artifact-aware-prediction/manuscript.md", "papers/001-artifact-aware-prediction/methods.md",
                "papers/001-artifact-aware-prediction/claim-evidence-map.md",
                "knowledge/provenance/REDISTRIBUTION.md", "knowledge/directions/research-roadmap.md"]
    errors += [f"Missing required file: {p}" for p in required if not (ROOT/p).is_file()]
    registry = json.loads((ROOT / "knowledge/experiments/registry.json").read_text(encoding="utf-8"))
    ids = [row["id"] for row in registry["experiments"]]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate experiment IDs")
    for row in registry["experiments"]:
        for p in row["evidence"]:
            if not (ROOT/p).exists():
                errors.append(f"Missing evidence for {row['id']}: {p}")
    # Check the new navigational material, not historical archives whose original links are preserved.
    docs = [ROOT/p for p in ("README.md", "REPRODUCING.md", "CONTRIBUTING.md", "REUSE.md")]
    docs += list((ROOT/"knowledge").rglob("*.md")) + list((ROOT/"papers").rglob("*.md"))
    docs += list((ROOT/"experiments").rglob("*.md"))
    broken = []
    frozen_link_contexts = []
    document_snapshot_contexts = {}
    capture_root = ROOT/'experiments/2026-10-02-six-hour/integration-review/checkout-availability'
    for summary_path in capture_root.glob('captured-*/summary.json'):
        captured = json.loads(summary_path.read_text(encoding='utf-8'))
        for original, snapshot in captured.get('document_snapshots', {}).items():
            snapshot_path = ROOT/snapshot
            expected = captured['document_hashes'][original]
            if not snapshot_path.is_file() or hashlib.sha256(snapshot_path.read_bytes()).hexdigest() != expected:
                errors.append('Captured document hash mismatch: ' + snapshot)
                continue
            document_snapshot_contexts[snapshot_path] = (ROOT/original).parent
    resolved_document_contexts = []
    for doc in docs:
        if not doc.is_file():
            continue
        content = doc.read_text(encoding="utf-8")
        link_base = doc.parent
        if doc in document_snapshot_contexts:
            link_base = document_snapshot_contexts[doc]
            resolved_document_contexts.append({'snapshot':doc.relative_to(ROOT).as_posix(),
                                              'source_context':link_base.relative_to(ROOT).as_posix()})
        elif doc.name.lower().endswith("protocol_snapshot.md") and (doc.parent.parent/"PROTOCOL.md").is_file():
            # Byte-preserved copies retain links relative to the original protocol.
            link_base = doc.parent.parent
            frozen_link_contexts.append({"snapshot":doc.relative_to(ROOT).as_posix(),
                                         "source_context":link_base.relative_to(ROOT).as_posix()})
        elif doc.name.upper() in {"PROTOCOL.MD", "PROTOCOL_PREFIX.MD"}:
            # Some endpoint packages preserve the canonical filename as well as bytes.
            # Find an identical ancestor original without editing its relative links.
            for ancestor in doc.parent.parents:
                if ancestor == ROOT.parent:
                    break
                candidate = ancestor/doc.name
                if candidate.is_file() and candidate.read_bytes() == doc.read_bytes():
                    link_base = ancestor
                    frozen_link_contexts.append({"snapshot":doc.relative_to(ROOT).as_posix(),
                                                 "source_context":link_base.relative_to(ROOT).as_posix()})
                    break
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            target = target.split("#",1)[0].strip().strip("<>")
            if not target or re.match(r"[a-zA-Z][\w+.-]*:", target):
                continue
            target = unquote(target)
            if not (link_base/target).exists():
                broken.append({"file": doc.relative_to(ROOT).as_posix(), "target": target})
    errors += [f"Broken link: {r['file']} -> {r['target']}" for r in broken]
    listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    forbidden = [p for p in listed if p.startswith(".github/workflows/") or (p.startswith("data/") and p != "data/README.md")]
    if forbidden:
        errors.append(f"Forbidden distributed paths: {forbidden}")
    large = [p for p in listed if (ROOT/p).is_file() and (ROOT/p).stat().st_size > 90*1024*1024]
    if large:
        errors.append(f"Oversized Git blobs: {large}")
    paper = ROOT / "papers/001-artifact-aware-prediction/manuscript.md"
    words = len(paper.read_text(encoding="utf-8").split()) if paper.exists() else 0
    if words < 2500:
        errors.append("Manuscript is too short to satisfy the complete-paper deliverable")
    imported = 0
    historical_selected = 0
    if args.verify_import:
        manifest = json.loads((ROOT/"archive/2026-10-01-investigation/import-manifest.json").read_text(encoding="utf-8"))
        for row in manifest["files"]:
            path = ROOT/row["path"]
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
                errors.append("Imported evidence changed or missing: " + row["path"])
            imported += 1
        historical = json.loads((ROOT/"output/evidence_manifest.json").read_text(encoding="utf-8"))
        for row in historical["files"]:
            # The old root README was archived when the new knowledge index replaced it.
            mapped = "archive/2026-10-01-investigation/README.original.md" if row["path"] == "README.md" else row["path"]
            path = ROOT/mapped
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
                errors.append("Historical selected evidence changed or missing: " + row["path"])
            historical_selected += 1
    result = {"status": "pass" if not errors else "fail", "registry_entries": len(ids), "new_markdown_documents_checked": len(docs),
              "manuscript_words": words, "distributed_files": len(listed), "imported_files_hashed": imported,
              "historical_selected_files_hashed": historical_selected, "errors": errors,
              "frozen_protocol_link_contexts":frozen_link_contexts,
              "document_snapshot_link_contexts":resolved_document_contexts,
              "scope": "repository structure, local links, preserved evidence and distribution checks; not peer review or archaeological validation"}
    dest = ROOT/"knowledge/provenance/repository-verification.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not errors else 1)

if __name__ == "__main__":
    main()
