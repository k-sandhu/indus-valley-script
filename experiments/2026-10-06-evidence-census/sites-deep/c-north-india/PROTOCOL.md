# Protocol: North India site census

## Question and scope
For each named site in batch C, what excavation, publication, inscription-count, object-metadata, later-find, custody and access evidence can be verified from primary or substantial secondary sources, and how do those published counts compare with the local Lipi export? The initial list contains 24 sites; additional Indian sites will be included only when the specified Eastern Headwaters or Inter-Riverine local coverage rows identify them and live searching verifies inscribed Indus material.

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
- 2026-10-07: The opening tally was corrected after counting the supplied list: it contains 23 named sites, not 24. One extra local site, Tigrana, was added from the Inter-Riverine coverage rows after the local export showed one TAG-class face. The row remains a local lead pending primary-source confirmation.
- 2026-10-07: Live search returned useful grouped queries and source leads but did not reach three distinct executed query strings for every site. The completed register remains Exploratory; `searches.json` lists the exact executed query set and the affected fields are marked unresolved.
