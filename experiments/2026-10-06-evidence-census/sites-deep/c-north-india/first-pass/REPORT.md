# Findings

The batch contains **24 rows**, comprising 23 requested sites and the additional Tigrana record. Tigrana was included because the local coverage file places it in Inter-Riverine and gives it one TAG-class face; that local classification does not independently establish an excavated Indus inscription. No other added site was confirmed from the region-limited local list.

## Local corpus and published counts

Thirteen sites in the batch have a matching row in `local-site-coverage.json`, totaling **290 face records**: Kalibangan 212, Banawali 26, Rakhigarhi 13, Farmana 8, Bhirrana 6, Ropar/Rupar 5, Alamgirpur 3, Chandigarh 3, Karanpura 8, Tarkhanewala Dera 3, Hulas 1, Baror 1 and Tigrana 1. The sum is a corpus-record total, not 290 archaeological objects. Per-site object-family, CISI-ID, sign-class and metadata-field counts are carried through in `site-rows.json`.

| Site | Published claim found | Local record | Comparison limit |
|---|---:|---:|---|
| Kalibangan | Mahadevan 1977: 99 objects; later RMRL search excerpt: about 24 fish-sign texts | 212 faces; 197 distinct CISI IDs; K-number maximum 476 | Different dates, versions and units; no object-level join made |
| Banawali | Mahadevan 1977: 7 objects; CISI I labels B-1 through B-37 | 26 faces; 23 unique CISI IDs; maximum B-35 | Legacy total and later catalogue coverage are not reconciled |
| Chandigarh | Mahadevan 1977: 4 objects | 3 faces; 3 unique IDs; maximum Ch-4 | Apparent shortfall of one only if labels and counting units align |
| Farmana | 2 square seals plus 2 terracotta impression objects; one seal predates the reported season | 8 faces; 7 object families; no CISI IDs in local export | Report categories and local faces are not a direct count match |
| Hulas | 1 terracotta sealing, Reg. 990, unstratified | 1 face; Hls-1 | Candidate one-to-one match; object join still required |

The three Mahadevan figures are reported search excerpts of the 1977 site/type table and require inspection of the original printed table before citation as final counts. The CISI 1 page audit and duplicate-page warning from the earlier package were reused. The local export's highest CISI number is not treated as a site total: number sequences may contain gaps, aliases or catalogue additions.

## Publication and later-find coverage

Six sites have a final excavation monograph or report title identified in this search set: Kalibangan, Banawali, Rakhigarhi, Farmana, Mitathal and Hulas. For several others, the located source is an IAR annual summary or preliminary report rather than a final synthesis. This is a source-set count, not a claim that only six sites have final reports.

Four post-CISI find reports were located with direct inscription descriptions: Rakhigarhi (later seasons, including an inscribed lead ingot), Bhirrana (later excavation article and seal material), Karanpura (IAR two-letter seal and later material presentation), and Tarkhanewala Dera (IAR terracotta seal impression with Harappan letters). Manda's initial inscription report dates to 1976–77, before CISI 1, and is not counted as post-CISI. The source passages and confidence are in the row notes and `sources.json`.

The digital sources provide useful leads but incomplete object-level evidence. Search indexing exposed IAR plates/passages for Alamgirpur, Manda, Karanpura, Tarkhanewala Dera and Rakhigarhi. Large official PDFs for Hulas, Bhirrana and Rakhigarhi exceeded the web fetch limit; the RMRL PDF returned 404 after its indexed text was found. `sources.json` preserves these failures. Page-specific metadata for findspot, stratum, absolute dates, dimensions, media, accession and current holding is incomplete for nearly every site. Rows say where the work remains instead of treating absent metadata as evidence of absence.

## Largest gaps

The run did not meet the protocol target of three distinct queries per site. Several searches grouped multiple names; the executed queries are preserved in `searches.json`. Coordinates and campaign tables were not collected systematically. CISI page ranges were verified only for Kalibangan and Banawali from indexed contents. Counts by object class were not independently enumerated. We did not inspect full CISI volumes 1, 3.1 or 3.2, and no image-level joins were made. Therefore the batch is an exploratory evidence register, not a completed object census or a coverage estimate.
