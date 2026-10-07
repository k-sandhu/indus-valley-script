# Protocol

Date: 2026-10-06. Status: Proposed until the catalogue observations and joins below are recorded.

## Question

What public catalogues, datasets and image archives expose Indus objects or records, and what object-level metadata can be verified from their own interfaces? The survey measures public discoverability. It cannot establish that every surviving object or archive has been indexed.

## Inputs

1. The 2 October 2026 dataset landscape (`experiments/2026-10-02-dataset-landscape/README.md`, `landscape.json`, `SCHEMA.md`, `DATASET_PLAN.md`) and DATASET-LANDSCAPE-01 registry entry, reused for prior dataset descriptions and denominators.
2. Public institutional catalogue pages and APIs, repository hosting pages, dataset cards, and published source/collection pages located by live web search on 2026-10-06.
3. CISI/Helsinki and museum records only where object identity can be compared through an explicit shared identifier or a cited concordance. No identity is inferred from visual resemblance alone.

Raw HTML, JSON responses, and search-result snapshots will be stored under `data/raw/2026-10-06-evidence-census/collections-and-datasets/`. The owned directory contains only authored protocol, code, summaries, and source metadata.

## Method

For each named institution, run a documented public-site query using `Indus`, `Indus seal`, `Harappan seal`, `seal impression`, `Indus tablet`, or a documented catalogue API endpoint. Record the literal query, search date, count and its basis (direct result total, API total, sampled visible results, inaccessible, or snippet-only). Check fields on one or more returned records. Separate catalogue existence from confirmed Indus result count. If a search is unavailable, record the failed route and do not translate it into zero holdings.

For datasets and archives, record publisher/maintainer, content, version/date, size and count basis, metadata, license as stated by the source, access/download mechanism, and whether it contains original observations or reuses a listed publication/corpus. Retain only discovery witnesses needed to support metadata claims; do not download image collections.

The paired sample audit targets 30 records with a museum catalogue record and a CISI/CISI-derived corpus record. Candidates must have an explicit join key (museum accession, excavation number, CISI identifier, or a source-published crosswalk). For every pair, compare accession/identifier, findspot, excavation identifier, date, dimensions, material, image/view coverage and bibliography. Preserve disagreements by source; unresolved joins are reported separately. If fewer than 30 explicit joins are publicly inspectable, report the completed count and the missing evidence rather than substituting weak matches.

## Comparisons and selection

The institution list follows the assignment, including South Asian, European, North American, Gulf and Central Asian collections. Priority within the three-hour limit is official catalogue endpoints and sources naming Indus items; the remaining institutions receive explicit documented searches or inaccessible/unverified status. Historical counts are never presented as current totals. Search-result totals are not treated as counts of physical objects unless the catalogue identifies the result unit.

## Negative result

A negative result is an executed query returning a documented zero with an accessible result count. A missing result, blocked catalogue, absent API, search-engine snippet, or inaccessible source is recorded as unverified, not zero. The broad question receives no completeness claim; failure to find a joined object is not evidence it does not exist.

## Outputs

`collection-register.json` and `.csv`; `dataset-register.json`; `metadata-field-matrix.csv`; paired sample audit; `sources.json`; rerunnable acquisition/aggregation code; `README.md`, `REPORT.md`, `RETROSPECTIVE.md`; and a proposed registry entry. All counts retain a basis and observation date.

## Amendment, 2026-10-07

Live searches on 2026-10-06 established several direct catalogue records and discovery pages, but PowerShell HTTP requests to museum domains repeatedly failed during transfer. The web search/open tool exposed record text, while many institutional search totals and original response bodies remained unavailable. The planned 30-record museum-to-corpus comparison also could not be completed: no 30 explicit shared identifiers were validated. The outputs are therefore **Exploratory**, not a frozen catalogue census. The 30 audit slots remain empty and null counts mean unmeasured, not zero. This amendment records an access/scope limit after the first searches; it does not change the inclusion rule or treat visual similarity as an identity key.

The 35 requested collection rows do not all represent individually executed catalogue searches. `search_status` distinguishes pages returned by the batched live searches, institutions included in a search batch without a relevant result, and institutions retained as follow-up targets that were not separately searched. The `query` column is the literal query family or the retained query target. Only direct totals are entered as numeric result counts.
