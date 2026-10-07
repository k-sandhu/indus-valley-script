# Protocol

## Question
For each named Gujarat, Kutch and Maharashtra site, what archaeological, publication, catalogue, count, metadata, post-CISI, holding and reuse evidence can be verified from the local census and live web sources? Are any same-region inscribed sites missing from the supplied list?

## Inputs
The local starting point is `experiments/2026-10-06-research-program/local-site-coverage.json`. The earlier broad census is `experiments/2026-10-06-evidence-census/sites-and-publications/`. Existing CISI and ICIT findings are reused only as attributed starting evidence. Live searches, source pages and bibliographic records are recorded in `searches.json` and `sources.json`; downloaded third-party material, if any, stays in the paired `data/raw/` directory.

## Method
Search each site by name with at least three distinct query formulations: excavation/report, inscribed object/CISI/ICIT, and later finds/publication. Open at least one primary or substantial secondary source per site where available. Record source title, authorship, year, venue, URL and access state. Extract counts only with a stated unit (objects, faces, texts or impressions), source location and count date. Keep disagreement records side by side. Compare CISI identifier prefixes and observed maximum numbers with local distinct-ID counts; treat numeric gaps as coverage indicators only when volume numbering can be checked. Record unfilled fields with the actual search log rather than an implicit claim of absence.

## Comparisons and selection
Include the 22 explicitly named package sites and every additional regional label in local-site-coverage.json. The local union adds Pabumath and Juna Khatiya. Pabumath is a verified added inscribed-object site (CISI1 Pbm-1); Juna Khatiya is retained as a coverage lead because the local row is an unnumbered pottery face and inscription status is unresolved. Prefer excavation reports, CISI catalogue records, ASI publications and peer-reviewed publications. Search snippets are discovery evidence, not opened-source evidence.

## Negative results
A negative result means only that the specified source or query did not expose the requested evidence. It does not establish that no object, report or later find exists. Where a field remains unavailable, retain the search strings, search location, date and result summary. No total corpus coverage percentage will be calculated from CISI maxima or local corpus counts.

## Planned outputs
`site-rows.json`, `site-rows.csv`, `sources.json`, `searches.json`, `REPORT.md`, `README.md`, `RETROSPECTIVE.md`, `registry-entry.json`, and a rerunnable aggregation script. Any post-outcome change will be dated and labelled exploratory.
