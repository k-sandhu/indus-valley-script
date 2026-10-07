# North India site census: completed follow-up

The register covers **25 sites**: the 23 supplied sites, Tigrana from the local Inter-Riverine register, and Rohira from CISI 1 p. 361. Every site has at least five distinct executed follow-up searches and an opened primary or substantial secondary source. The 223 follow-up queries are indexed in [searches.json](searches.json). Findings remain **Exploratory**; unavailable fields carry search and source-location records.

[aggregates.json](aggregates.json) records six sites with an identified final excavation monograph and nine with reported inscribed discoveries after the 1987 India catalogue baseline. Three of those nine were already in CISI 1. The nine inspected CISI 1 sections contain **176 catalogue objects**. The local register contains **290 faces, 271 object families and 232 distinct CISI identifiers** across this batch. These totals have different units and dates.

## Files and reused inputs

- [REPORT.md](REPORT.md): findings, comparisons, gaps and review targets.
- [site-rows.json](site-rows.json) and [site-rows.csv](site-rows.csv): all ten requested field groups for each site. CSV mapping/list cells contain JSON strings.
- [sources.json](sources.json): bibliography, opened versus snippet status, locations, access and reuse terms for 911 observed records. Unused leads can have unresolved authors or dates.
- [PROTOCOL.md](PROTOCOL.md): protocol and dated amendments.
- [RETROSPECTIVE.md](RETROSPECTIVE.md): approaches, corrections and disk recovery.
- [registry-entry.json](registry-entry.json): proposed entry; the shared registry was not edited.
- [checks.json](checks.json), [validation.json](validation.json), [file-manifest.json](file-manifest.json): aggregate checks, record checks and the complete retained path inventory.

The prior broad census supplied site/publication leads. The coordinator's `experiments/2026-10-06-research-program/local-site-coverage.json` supplies local figures unchanged for matching rows. Existing CISI 1 scan/OCR witnesses were reused and catalogue pages inspected to establish ranges and classes. The ten original files remain byte-for-byte in `first-pass/`, checked against [first-pass-manifest.json](first-pass-manifest.json). Active deliverables are UTF-8; the archive retains its original damaged text.

PDFs, OCR, web responses, acquisition failures and recovery records are local-only under `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/`. No third-party page or image payload is included in this owned directory. A fresh checkout needs those excluded witnesses to rebuild the index.

## Rerun from the repository root

```powershell
python -X utf8 experiments/2026-10-06-evidence-census/sites-deep/c-north-india/build_site_census.py
python -X utf8 experiments/2026-10-06-evidence-census/sites-deep/c-north-india/write_reports.py
python -X utf8 experiments/2026-10-06-evidence-census/sites-deep/c-north-india/validate_census.py
python tools/review_prose.py --path experiments/2026-10-06-evidence-census/sites-deep/c-north-india --no-write
```

The builder reads [evidence_notes.py](evidence_notes.py), the local register and saved search/acquisition records, with no network requests. Validation checks references, JSON/CSV agreement, active encoding and archive hashes; it does not verify archaeological claims. `finalize_manifest.py` separately checks retained PDFs and writes the path inventory. Acquisition helpers are retained for source recovery, with temporary directories confined to local raw. The audit and cleanup scripts record one-time actions and should not be rerun over their original manifests.
