# Site census batch B

Status: Exploratory. Revision audited 7 October 2026 UTC.

The batch covers 25 sites, including added Kanewal, with 130 recorded live queries and at least three site-specific searches per site. It records 496 local faces/460 families; ten CISI 1 ranges contain 317 catalogue objects; Mahadevan 1977 gives 175 selected inscribed objects across five sites. Twelve completed campaign reports are identified and relevant passages from six are read. Two directly checked catalogue baselines have later inscribed finds; Nuhato provides one further case whose older CISI 2 citation still needs direct checking. See [REPORT.md](REPORT.md) and [aggregate-results.json](aggregate-results.json) for the count bases.

## Files

[site-rows.json](site-rows.json) contains one structured row per site; [site-rows.csv](site-rows.csv) serializes nested cells as JSON. [sources.json](sources.json) records curated bibliographies and every discovered source header, with opened, preview, bibliography and snippet states separated. [searches.json](searches.json) records actual queries and raw-response paths. [source-access.json](source-access.json) records downloads and failures. [PROTOCOL.md](PROTOCOL.md) includes dated amendments, and [RETROSPECTIVE.md](RETROSPECTIVE.md) describes changes and limitations. The proposed shared-registry record is [registry-entry.json](registry-entry.json).

The original ten files are preserved byte for byte in [first-pass](first-pass/preservation-manifest.json). They contain historical errors and damaged text; the current UTF-8 files replace them for use. [build-audit.json](build-audit.json) reports archive hash checks. [created-paths.json](created-paths.json) inventories every owned/raw artifact.

## Reproduce from the repository root

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/build_site_rows.py
python experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/write_reports.py
python tools/review_prose.py --path experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra --no-write
```

The builder uses Python’s standard library, `evidence_catalog.py`, the coordinator’s unchanged local coverage file and preserved raw B/O response logs. It makes no network requests. Markdown/report inventories are written by the second command. `first-pass/` is never modified.

For source acquisition, run `acquire_sources.py <plan-path>` using one of the four `acquisition-plan*.json` files here. It requires requests, beautifulsoup 4 and PyMuPDF, already available during this audit. Acquisitions are cached, including failures; use a new ID to retry a failed route. It sets TMP, TEMP and MPLCONFIGDIR under the paired raw directory. The documented live-search queries require manual/tool replay; they are not fabricated by the builder.

## Reviewer checks

Rebuild aggregates and compare the JSON/CSV rows. Check all first-pass SHA-256 values, the printed CISI ranges, Mahadevan’s pp. 6–7 tables, Rangpur p. 130, Desalpar IAR p.10, Nagwada IAR p.20 and Nuhato pp. 14, 41–42. Sample the source/page evidence and coordinate conflicts. Resolve Rojdi’s CISI 3.2 pages and directly inspect Nuhato’s CISI 2 citation. Review the prose findings for current files separately from the unchanged archive.
