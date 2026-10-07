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

## Amendment, 7 October 2026: source audit after coordinator review

The coordinator found that the first pass did not meet the checklist. Its ten files are preserved byte for byte in `first-pass/`, with SHA-256 values in `first-pass/preservation-manifest.json`. The revised outputs remain Exploratory. They supersede the first pass for current use without altering its record.

Run and preserve at least three actual, distinct live searches for each of the 24 sites. Save the exact query, returned source URLs, retrieval time and raw tool response in the paired raw directory. Open a primary report or substantial secondary source for each site and preserve the access outcome. A catalogue landing page alone does not meet the source-reading requirement. Use existing CISI scans and earlier source audits where available; inspect the site's catalogue and basic-data pages directly. Discard first-pass guesses, including borrowed coordinates, object classes and unsourced numerical counts.

Each unresolved field will contain the site-specific search IDs and an account of the sources inspected, rather than a uniform partial label. Counts will contain a value or explicit unresolved status, class, unit, publication year or season cutoff, printed page or figure, and evidence ID. Catalogue-entry counts will be distinguished from complete excavation inventories. An absent catalogue entry or search hit will not be assigned zero archaeological finds. Published count totals will be reported only for a stated, nonoverlapping count basis. Metadata availability will be assessed from particular object captions, inventories and illustrations, with source locations.

For post-CISI finds, distinguish a find excavated or reported after the applicable catalogue's source cutoff from a later article describing older finds. Search IAR and Pakistan Archaeology by site and season. Final-report totals will count monographs or reports presented as completed campaign publications, with bibliographic verification separated from full-text inspection. Coordinate disagreements will be recorded instead of silently choosing a site or village point. Every generated current file will be UTF-8; the first-pass byte archive will retain its original damaged text as historical evidence.

## Amendment, 7 October 2026: additional site and count units

Reading the 1977–78 annual review for Pabumath exposed an explicit report of inscribed pottery at Kanewal, p. 21, item 22. Add Kanewal under the existing regional inclusion rule and apply the same three-search and source-reading requirements. The resulting batch has 25 sites, including the explicitly requested Nuhato cross-reference in Sindh. Juna Khatiya remains a local corpus lead requiring an original inscription witness.

The ICIT search exposed Fuls 2023’s regional list of legible sign occurrences. Retain those published site aggregates with their sign unit; they will not enter an object-count total. A regional shared query is recorded once and does not count toward the minimum of three site-specific searches. Record new-site reports published after 1987 separately from later finds at sites with an existing catalogue section. Nagwada’s 1987–88 season straddles 1987; its annual-review publication is 1993. These refinements and all affected outputs are Exploratory.
