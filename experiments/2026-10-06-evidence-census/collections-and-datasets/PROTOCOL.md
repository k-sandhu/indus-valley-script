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

## Depth pass amendment, 2026-10-07

The coordinating review identified that the first pass did not execute a separate query for every collection and that the 30 paired-audit slots contained no validated joins. This amendment expands the acquisition plan without replacing earlier observations. Before recording new outcomes, the pass will query each collection row where a public route can be reached, using multiple relevant terms (including Indus, Harappa/Harappan, Mohenjo-daro/Mohenjodaro, Lothal, seal, and tablet as appropriate). For every attempt, retain the exact URL or API call, date, HTTP status when observable, result count and count basis, duplicate-removal key, record fields inspected, and raw response or a precise failure record under the local raw directory. A failed preferred route triggers the listed public alternatives where available. Search-engine snippets remain snippet-only evidence and do not become catalogue counts.

Counts will be separated into returned catalogue records, records plausibly matching Indus material, and confirmed inscribed/sealed objects. Terms are deduplicated only by an explicit catalogue object identifier; where a route does not expose such identifiers or the complete result set, the unique-object count is unmeasured. A zero is reported only for an executed query with an accessible count. “Not found” means an executed query returned no matching object; “not queried” means no query was executed. Record-field presence is assessed from returned object records, not inferred from institutional collection descriptions. Licence and API/bulk-access statements are recorded separately for images and data.

For the paired audit, only an explicit shared identifier can establish a museum/corpus pair: CISI number, excavation number, Mackay/Marshall/Vats catalogue number, or a published concordance. Each candidate is labeled confirmed only after both records expose the same identifier or a cited concordance maps them. The pass will record the actual number of confirmed pairs even if it is below 30, list candidate joins that lack identifier-level confirmation, and compare fields only for confirmed pairs. All new counts and joins are exploratory until independently reviewed; prior outputs remain preserved as history.

## Execution amendment, 2026-10-07

The depth pass completed a targeted live query for each of the 37 register rows through grouped site-specific web searches or a direct catalogue/API route. The six-term repeated API query was run only against the Met, Cleveland, Art Institute of Chicago and Smithsonian endpoints; most other collections received one or a small number of site-specific search strings rather than all six terms. The search provider did not expose an upstream HTTP status or complete result count for those queries. Direct HTTP attempts were therefore used where stable routes were known, and their status/body or timeout is retained in the raw log. This fell short of a six-term, status-and-count capture for every institution. The outputs label that gap rather than imputing zeros; query counts per term are complete only for the four API endpoints in `museum-api-query-counts.csv`.

The `count` for Cleveland is a unique-object result for the Indus seal query; the British Museum and Louvre numbers are mixed-type culture/search-page totals, while Lothal's 133 is a category count with unadjudicated inscription status. The BM and Louvre search-page totals were visible in web-search excerpts, while local direct requests returned 403 and 429 respectively. All findings remain Exploratory. A future pass should obtain exact per-term catalogue responses from the Indian/Pakistani and other regional portals before estimating institution-level totals.

## Focused pass amendment, 2026-10-07

This pass addresses the coordinator's second follow-up. It concentrates on Museums of India and ASI catalogues, the British Museum, Penn, Louvre, Met website, MFA Boston and National Museum of Pakistan. Earlier outputs and raw responses are retained. New acquisition bodies and extracted third-party observations go into `focused-pass-2026-10-07` in the local raw directory. Current summary files will retain the earlier pass as a dated snapshot before updates.

For counts, an included record must describe an Indus inscription on a seal, sealing, tablet, pottery or another object. Culture totals and seal categories remain separate from inscription-confirmed objects. Search terms, HTTP outcomes, visible totals, pagination and deduplication by accession or catalogue object ID will be recorded. An inspected subset supplies a minimum only, unless the complete result set can be enumerated. A blocked or absent catalogue supplies no zero. Image licences will be taken from the record or its linked institutional terms.

The identifier audit will index the existing local Lipi observational export by excavation identifier and CISI reference. Exact matching is attempted first. Normalization may fold case, remove spaces and punctuation, and remove leading zeros within numeric components, while preserving every component. It may not remove unexplained trailing digits, convert museum accession numbers into excavation numbers, or equate identifiers from different sites. Multiple faces of one object are counted as one object through `object_family_id`. Ambiguous identifiers and composite identifiers remain candidates until a source resolves them. The `Hr 5635` / `HR 5635345` candidate will be traced to the original export or a published catalogue; a plausible prefix alone cannot confirm it.

For each confirmed pair, compare site, object type, material, dimensions and inscription description. Preserve source-specific values and missingness, including zero-valued corpus dimension placeholders. Report the number of museum records inspected, those with usable identifiers, exact and normalized joins, unresolved candidates, and distinct matched objects and faces. A negative outcome is no explicit match after these defined operations. Any further matching rule adopted after results will be labeled exploratory and documented separately.

### Composite identifier clarification, 2026-10-07

The first focused extraction found explicitly delimited plate references in corpus identifiers, such as a field number followed by `Pl. LI:9`. The museum gives that field number separately and cites the same published plate. Such a pair may be confirmed through the shared published plate reference, retaining the original composite string. This is an exploratory extension to the plain-string matcher. Undelimited digit concatenations remain unresolved unless a published concordance independently supplies the excavation and museum identifiers. CISI Volume 1's basic-data tables will be used for that purpose, with page images checked after OCR locates a row. Classification corrections exclude descriptions that explicitly deny an inscription or specify another script; ancient casting does not make a copper tablet a modern copy.

### Comparison and sample amendment, 2026-10-07

The focused frame is the inscription-confirmed original records inspected in the six accessible catalogues. Modern plaster impressions are counted separately. The full paired audit retains all confirmed joins; its 30-object sample is the first 30 confirmed rows after sorting by institution and normalized accession. This is a deterministic convenience sample enriched for retained identifiers, with no claim of random sampling. The match fraction uses the entire inspected original-record frame, including records lacking usable join keys.

Comparisons are exploratory. Site names are normalized to named archaeological sites; broad geography is labeled less specific. Structured material terms such as “Others” are uninformative, and “Stone” is a broader term than “Steatite.” Object-type comparisons preserve the corpus code and distinguish terminology differences between seals, sealings and tablets. Dimension checks convert explicit centimetres/inches to millimetres, omit zero-valued corpus placeholders, and compare sorted measurements only when the same number of positive, scalar dimensions exists. A difference exceeds the comparison tolerance when any paired measurement differs by more than the larger of 0.5 mm and 5% of the corpus measurement. Unlabelled axes, thickness ranges and unequal measurement coverage remain incomplete comparisons. Description checks compare explicit numeric sign counts only when both sources provide them; they do not validate a transcription.
