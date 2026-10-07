# Protocol: Indus inscribed evidence by site and publication

Date: 2026-10-06. Status: Proposed before source discovery and local counting.

## Question
Can the findable published excavation evidence for Indus-inscribed objects be mapped to archaeological sites and publication records, and what metadata is reported for those records?

## Inputs
1. Primary and institutional bibliographic records and excavation publications found by live web search.
2. The prior comparison at `experiments/2026-10-02-dataset-landscape/landscape.json`, including ICIT historical counts and known CISI coverage.
3. The pinned local `data/normalized/lipi_observed_faces.jsonl` and `data/normalized/mayig_faces.jsonl`, counted by `site` where the field is present.
4. Existing repository source frames and catalogue caveats for Harappa, Lothal and Kanmer.

Acquired third-party pages, PDFs and extracted source rows belong only in the local raw directory. This report records bibliographic and page locators, not source facsimiles.

## Method
Search live web for publication records and source-reported inscribed finds, prioritizing excavators, official agencies, publishers, institutional repositories and original corpora. For every result, record whether the source page or text was opened, the exact title/author/year and page or figure locator when recoverable, access, and whether any count is a source count, count of illustrated representations, or a secondary/news claim. Keep objects, faces, texts, sign occurrences and photographs as separate measures; never sum across overlapping publications.

Create site rows from attested site names in source records. Include explicit sites outside local corpus coverage when discovered. Record each metadata field as Present, Absent in inspected source, or Not assessed. `Not assessed` is not a claim that the source lacks that field. Local counts are reproducible counts of rows grouped by literal `site` value; they are not unique physical objects and may include repeated faces/records.

Create publication rows for identified excavation reports, corpus volumes and catalogues. Add gap rows only where a source makes an observable report of an inscribed find and a cross-check establishes it is absent from the checked CISI volumes, ICIT historical count evidence, and both local files. If one of those comparisons cannot be established, label the gap as a candidate and list which indexes were checked.

## Comparisons and selection
Compare the observed publication set with the earlier ICIT/CISI inventory; compare local site-row counts against the source-backed site register. Prefer exact primary locators over snippets or news summaries. A result based on a conference abstract, press story or search snippet is never promoted to an exact excavated-object count.

## Outcomes and negative result
Report the number of distinct site rows, number with an identified primary publication/report, number and basis of source counts, and field availability only across assessed source-site pairs. Report accessible-index share only for a defined denominator with an explicit counted unit. A negative result is a search that finds no additional source or metadata after the declared query set; it does not establish that no other evidence exists. Failure to open a publication is reported as a search/access failure, not as evidence that a source is absent.
