# Protocol: North India site census

## Question and scope
For each named site in batch C, what excavation, publication, inscription-count, object-metadata, later-find, custody and access evidence can be verified from primary or substantial secondary sources, and how do those published counts compare with the local Lipi export? The supplied list contains 23 sites. The dated amendments describe additions from the local coverage register and published inscription catalogues.

## Inputs
The prior `sites-and-publications` package, `experiments/2026-10-06-research-program/local-site-coverage.json`, the local Lipi export summary, published excavation reports and catalogues, CISI volumes, ICIT and ASI/IAR records. Downloaded or source-derived payloads stay under the package's local raw directory.

## Method
Record each live web query with date, exact query, search service and returned results. For every site, run at least three distinct queries: site plus excavation/publication; site plus Indus seal/sealing/tablet; site plus CISI/ICIT or inscription count. Open at least one primary or substantial secondary source where available. Separate objects, faces, texts and impressions; do not sum counts across units. Capture exact bibliographic titles, source locations, coordinates and count date. Use `local-site-coverage.json` figures as face/annotation counts, not as archaeological object counts. Judge local coverage only against like-for-like published totals or CISI identifier runs, and label contiguous-number assumptions.

## Comparisons and selection
Use the primary excavation report for campaign and find-context details, CISI for catalogue inclusion and page range, ICIT/Mahadevan only when a published site-level count is accessible, and later ASI/IAR or peer-reviewed reports for post-CISI finds. Retain disagreements side by side. Include a new site only if it is in the specified local regions, is located in India, and a source reports an inscribed Indus object. Do not infer a missing count from a missing search result.

## Negative result
A negative result is a documented search set and/or inspected publication that does not provide the requested field. Record the exact query, search date, place searched and return. Use `not located in sources searched` with the search record rather than `not assessed`. Failure to access a source is not evidence that an item or report does not exist.

## Status and plan changes
Initial status: Exploratory. Any protocol change after observing results will be dated below and outputs affected by that change will be labelled exploratory. No count or coverage endpoint is frozen before source collection.

## Amendment log
- 2026-10-07 follow-up: Preserve the ten original files byte-for-byte under `first-pass/`. Replace the active register with site-specific, source-linked observations. Execute three individual queries for every site, retain the raw query/open responses locally, and inspect at least one primary or substantial secondary witness for each row. Reuse CISI 1's existing scan and OCR as locators, but read catalogue pages before taking counts. A failed field must link to the site's executed queries and inspected sources. Distinguish catalogue entries from inscriptions and track the date cutoff of each CISI part. Repair active UTF-8 text without altering the preserved first pass. Derive batch totals from explicit machine-readable fields and report completeness checks.
- 2026-10-07: The opening tally was corrected after counting the supplied list: it contains 23 named sites, not 24. One extra local site, Tigrana, was added from the Inter-Riverine coverage rows after the local export showed one TAG-class face. The row remains a local lead pending primary-source confirmation.
- 2026-10-07: Live search returned useful grouped queries and source leads but did not reach three distinct executed query strings for every site. The completed register remains Exploratory; `searches.json` lists the exact executed query set and the affected fields are marked unresolved.

## Follow-up amendment, 2026-10-07, after the disk interruption

The preceding insufficient-search statement describes the preserved first pass. The follow-up executes individual query strings for all 25 rows and records their raw grouped responses. Search counts use exact distinct strings naming that site; first-pass queries lacking saved responses are excluded. A grouped response is not attributed to a specific member query.

The scope contains 23 supplied sites, Tigrana from the Indian Inter-Riverine local register, and Rohira, added after CISI 1 p. 361 identified two seal impressions. Tigrana remains a local inscription lead. Other surveyed settlements enter this batch only when an inscription can be assigned securely to them. Pakistani local-region labels remain outside this package.

Counts are retained by source, date, unit and eligibility. CISI 1 entry totals include blank legends, indeterminate marks and geometric seals. Mahadevan's selected corpus, excavation graffiti instances and local faces/families receive separate denominators. Contiguity is checked on CISI 1 entry runs. Kalibangan's later K123–476 run cannot be checked without CISI 3.2 and stays unresolved. No site-wide text count is calculated from a mixture of these groups.

The final-report total means sites with an identified final excavation monograph. Short complete trial reports and chapters, including Siswal and Manda, are listed separately. The later-find total uses discoveries after the 1987 India catalogue baseline and separates previously catalogued sites from sites absent in CISI 1. Discovery dates are distinguished from later publication dates. All follow-up outputs are Exploratory because source selection and these definitions were refined during the audit.

The recovery audit checks saved JSON before replacement. PDFs and OCR serve as durable local witnesses; temporary page renders can be regenerated and are removed to conserve shared disk space. Active text is UTF-8; the first-pass archive retains its original bytes and damaged characters. Missing fields link to executed searches and the inspected publication location, with no implication that the archaeological quantity is zero.
