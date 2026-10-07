# Revision retrospective

The first pass left coordinates, publication pages, class counts and metadata insufficiently checked. It was preserved in 25 files under `first-pass/` before any editing. The revision reuses its scope, query leads and source ledger, the broad census in `sites-and-publications`, the coordinator’s local coverage aggregate, and the repository’s Mackay 1943scan. The registry and literature retrospective helped identify the existing CISI scan and avoid treating repeated scans as separate evidence.

## Approaches and outcomes

Three regional revisions and the nearby-site additions supplied new searches and source inspections. The final assembler copies the coordinator’s local fields exactly, joins spelling variants such as Bala-kot and Balakot, and preserves corpus labels. It combines 37rows, 375search or inspection records and 669 source records. Every row has at least 3 distinct new queries and an opened source. The classification and mechanical checks are retained in [revision-audit.json](revision-audit.json).

The full CISI 2scan and the full Mahadevan 1977scan were recovered through public Internet Archive metadata and downloads after direct mirrors failed. CISI 2 was searchable. Mahadevan was image-only, so its pages 6–7and828were rendered and visually inspected while a separately downloaded OCR derivative supplied navigation. The primary counts now retain their page, class, unit, selection rule and date. The source PDFs and acquisition hashes are in the local raw directory.

An opened archaeological gazetteer supplied missing coordinates and campaign references. Its letter-spaced PDF text required whitespace normalization for name lookup. It also exposed disagreements with government coordinates and different campaign summaries. Those disagreements remain in the rows. A source-backed check replaced the first-pass Allahdino city-centre coordinate.

## Corrections

The Fuls 2023 regional index counts legible sign occurrences. The first pass had treated several bracketed figures as object totals; those comparisons were removed. CISI entries likewise include geometric seals, pottery marks and comparative material. Rehman Dheri’s270 entries were divided into 1 seal,266 pottery objects and3 tentative scrapers after inspecting the page 378caption. Later discussion of an old object and an excavation before CISI publication were removed from the strict post-CISI tally. Miri Qalat and nearby local labels appeared during the country check of the local corpus’s Iranian Plateau category; their addition is recorded as an exploratory scope amendment.

Nindowari’s 2011publication title was corrected from an unsupported first-pass title. Sutkagen-dor’s Stein reference was corrected to *An Archaeological Tour in Gedrosia*. Shortughai catalogue entries and seals were kept as different counts. UTF-8 repairs preserve the archived witnesses and correct active source summaries. Exact source titles were checked before mechanical repair.

## Failures and remedies

Direct source requests returned HTTP 403, 406 or 404, timed out, failed TLS connections or encountered an access challenge. Their source and acquisition records retain the unsuccessful route. Public previews often omitted the later catalogue and object pages; the revised tables use field-level unresolved records with search IDs instead of filling those pages from snippets.

Drive C filled during integration. Two redundant, regenerable derivatives were removed from this package’s common raw directory: the extracted `cisi2-archive.txt` and 13 Sibri page-render PNGs. The source PDFs, page-text JSON and Sibri OCR were preserved. After disk space returned, all revision JSON files were parsed again. No other package’s files were removed.

## Remaining work

The package completes the search and field-recording checklist, with unresolved values where the recorded sources did not supply an answer. Complete excavation inventories, the missing later CISI pages and current repositories require additional source access. The next numerical change should come from a named report page or object crosswalk. [REPORT.md](REPORT.md) gives the reviewer’s source and recomputation checks.
