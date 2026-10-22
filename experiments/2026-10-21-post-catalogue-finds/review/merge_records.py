"""Merge the per-run exposure logs and manifest proposals into package-level files.

Writes exposure-log.csv and manifest-proposals.json in the package directory.
Usage: python -I merge_records.py <repo root>
"""
import csv, json, pathlib, sys

root = pathlib.Path(sys.argv[1])
pkg = root / "experiments/2026-10-21-post-catalogue-finds"
logs = [pkg / "acquisition/exposure-log-1a.csv", pkg / "acquisition-web/exposure-log-1b.csv"] + sorted(pkg.glob("extraction/*/exposure-log-*.csv")) + sorted(pkg.glob("verification/exposure-log*.csv"))
rows = []
for p in logs:
    for r in csv.DictReader(open(p, encoding="utf-8")):
        rows.append({"source_id": r.get("source_id", ""), "agent": r.get("agent", ""), "access": r.get("access", ""),
                     "pages": r.get("pages", "") or r.get("pdf_page", ""), "purpose": r.get("purpose", "") or r.get("record", ""), "log": str(p.relative_to(pkg)).replace("\\", "/")})
rows.append({"source_id": "matching and review", "agent": "codex gpt-6.1-sol run 3; coordinator Claude Opus 5.5",
             "access": "tables only: extraction rows, CISI 1 and 2 basic data, local corpus identity fields", "pages": "none",
             "purpose": "merge, containment and joins; no source page or image opened", "log": "matching/final.md; review/"})
with open(pkg / "exposure-log.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def load(p):
    d = json.loads(p.read_text(encoding="utf-8"))
    return d["sources"] if isinstance(d, dict) and "sources" in d else d if isinstance(d, list) else list(d.values())
props = []
for p, who in [(pkg / "acquisition/manifest-proposals-1a.json", "codex run 1A"),
               (pkg / "acquisition-web/manifest-proposals-1b.json", "codex run 1B"),
               (pkg / "acquisition-coordinator/manifest-proposals-coordinator.json", "coordinator")]:
    for s in load(p):
        if isinstance(s, dict):
            props.append({**s, "proposed_by": who})
out = {"package": "experiments/2026-10-21-post-catalogue-finds", "question": "Q-1026",
       "note": "Proposed data/MANIFEST.json entries for sources acquired by this package. Every file is local-only under data/raw/2026-10-21-post-catalogue-finds/ and rights-unverified; maintainers fold the entries into the manifest.",
       "sources": props}
(pkg / "manifest-proposals.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(rows), "exposure rows;", len(props), "manifest proposals")
