# Evidence census synthesis retrospective

Completed 7 October 2026 for Package B3. The result is an Exploratory synthesis with verified arithmetic and a 20-site source sample. It establishes bounded gaps in local catalogue and metadata coverage; the worldwide additional-object total remains unmeasured. [REPORT.md](REPORT.md) gives the findings and source locators.

## Inputs and approaches used

Read the repository guidance, research registry, contribution assessment, relevant retrospectives and October 2 dataset specification before computing the synthesis. Reused the four active batches' site rows and source witnesses, the superseded first-pass publication register as leads, the coordinator's site-coverage counts, and the collections census's 114 original museum records and 61 proposed identifier joins. The October 2 local corpus audit supplied pins and comparator units. No contributing package builder was rerun because its write paths belong to another contributor.

Wrote [PROTOCOL.md](PROTOCOL.md) and [sample-selection.json](sample-selection.json) before calculating synthesis outcomes or reviewing the selected source passages. The offline builder independently sums site rows, registers explicit aliases, computes catalogue membership, replays museum joins and normalizes metadata placeholders. Source-level links retain their match basis and candidates. Object crosswalks and absent identifier lists stay in the local raw directory; aggregate outputs contain no copied transcription corpus.

The source check reused saved PDFs and the saved Dholavira report mirror. Image rendering was needed for scanned IM77/CISI pages. Twenty sites were checked, with five from each batch. Fourteen selected assertions were supported and six qualified. Saved Nuhato and CISI witnesses resolved the cross-batch alias and later-seal conflict without a new web query. [sources.json](sources.json) records 19 clean bibliographic entries, content-opening status and prior failed access routes.

## Problems, changes and outcomes

| Problem observed | Change made | Preserved outcome |
|---|---|---|
| Batch A uses `site_label_rows`; the initial verifier expected a different row-count field. | Read the batch's actual aggregate fields and retain the failed development run. | `development-2026-10-07-v1/checks.json` has one failed check; subsequent main runs pass. |
| Literal spelling differences omitted six site labels from joins. | Use the contributing rows' explicit `local_corpus.site` aliases before matching local faces. | Corrected totals include 5,652 represented faces; all per-label coordinator counts agree. |
| The first automatic range interpretation could treat later catalogue references as a uniform run. | Restrict extraction to source-defined CISI 1/2 ranges and explicitly define Rehman Dheri/Sarai Khola ranges. | Harappa's CISI 3.1 subsets remain source assertions rather than inferred complete ranges. |
| Dataset/source and publication names alone supplied ambiguous register links. | Add exact source-URL links and keep title/name candidates separate. | v3 and later contain 32 publication-to-batch source links with their evidence basis. |
| Cultural-period strings and numerical catalogue dates occupied one audit concept. | Add a separate calendar-attribution rule and leave independent dating unadjudicated where required. | v4 and later count 68 numerical museum date assertions; Lipi has no numerical date assertion in its `time` field. |
| Final table inspection found the CISI 1 Amri prefix differed from local Ai identifiers. | Add the source-attested CISI 2 prefix concordance while preserving the printed prefix. | v5 raises selected A-range matches from 811 to 813 of 936. B/C's 327/493 result is unchanged. |
| Long snippet text appeared in source-title fields. | Emit only path, source ID and length, and classify flagged headers separately. | 17 records in five files flagged; no title payload copied into B3. |

The dated protocol amendments label these post-outcome corrections. Earlier development and main endpoints remain unchanged. Top-level tables copy v5 and identify their source endpoint in `OUTPUT-MANIFEST.json`. A fresh replay matches all ten aggregate files; 1,069 verification checks pass. The four authored JSON ledgers also reproduce in a separate annotation replay. Package checks pass 94 copy, link, syntax and accounting checks. The manual prose scanner reports no flags in five Markdown files.

## Remaining work for review and acquisition

The B3 source sample validates selected assertions, not every field or entry. Dholavira's original page rasters, Halim's Sarai Khola paper and Dales's Balakot paper were not opened here. Full current ICIT and complete later CISI inventories remain unavailable for a worldwide denominator. Museum identifiers need independent concordance sampling; content disagreements require original views and measurement conventions. Publication dates and custody statements must retain their own cutoffs.

No new live search or download was attempted, so B3 has no failed new search/download to report. Earlier failures remain preserved in the contributing ledgers and are referenced in `sources.json`. No shared registry, manuscript, source witness or earlier plan was edited. The ranked acquisition routes and schema/pilot changes are Proposed; no contact, submission, account, publication, automation or repository-history operation occurred.

The reviewer should rerun the builder into new owned/raw directories, compare the result with v5, repeat the 20 selected source assertions, inspect absent catalogue-key classifications, and review the 61 museum concordances and conflict fields. The [README](README.md) supplies the commands and output inventory.
