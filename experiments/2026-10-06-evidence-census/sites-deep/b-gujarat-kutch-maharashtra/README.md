# Gujarat, Kutch and Maharashtra site census

This exploratory census contains 24 site rows: the 22 explicitly named sites, plus Pabumath and Juna Khatiya from the Gujarat/Kutch rows in the local coverage export. Pabumath is a verified added inscribed-object site: CISI 1 lists Pbm-1. Juna Khatiya remains a coverage lead because its local record is one unnumbered pottery face and the sources inspected did not establish an Indus inscription.

The local export records 489 faces across its 11 Gujarat/Kutch site labels. Lothal contributes 208 faces and 179 distinct CISI identifiers; Dholavira contributes 238 faces but only two CISI identifiers. The local rows count recorded faces, while published sources count objects, impressions, or texts. These measures are not directly interchangeable. The highest observed CISI number cannot serve as a denominator until sequence continuity is checked in the volumes.

The rows identify nine final-report publications by title or bibliographic record: Lothal, Dholavira, Surkotada, Kanmer, Nageshwar, Kuntasi, Rojdi, Rangpur and Daimabad. Six sites have post-CISI excavation or object reports located in the sources collected here: Dholavira, Gola Dhoro, Kanmer, Shikarpur, Khirsara and Padri. Bet Dwarka has inscribed-object reports, but the 1987 publication date does not establish whether it postdates the CISI 1 cutoff. These are discovery counts for this search pass, not claims that later reporting is exhaustive.

## Files

- [site-rows.json](site-rows.json) and [site-rows.csv](site-rows.csv): 24 site records with local coverage, published count notes, metadata and unresolved fields.
- [sources.json](sources.json): 45 literature and catalogue records, with opened/snippet-only access notes and reuse cautions.
- [searches.json](searches.json): 75 dated search records, three query formulations per site.
- [REPORT.md](REPORT.md): batch totals, count comparisons and major gaps.
- [PROTOCOL.md](PROTOCOL.md): question, inputs, selection rules and negative-result criteria.
- [RETROSPECTIVE.md](RETROSPECTIVE.md): approaches, problems and fixes.
- [registry-entry.json](registry-entry.json): proposed shared-registry record.

## Rebuild

From the repository root, run:

```powershell
python experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/build_site_rows.py
```

The script reads `experiments/2026-10-06-research-program/local-site-coverage.json` and rebuilds the aggregate JSON and CSV outputs. No third-party source files were downloaded into the owned directory; raw source material belongs in the paired ignored `data/raw/` directory. Source-specific reuse terms remain unverified unless noted in `sources.json`.

The site rows are exploratory. Many volumes and object inventories were available only as catalogue records, article pages or search-result excerpts. See the row-level source links and unresolved fields before using a count as a complete site total.
