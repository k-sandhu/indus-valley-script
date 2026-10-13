# Post-review corrections, 13 October 2026

The package now supplies 27 exact or confirmed joins among 86 decided records. Nineteen add to the census, taking its 68-record lower bound to 87 across both acquisitions, or 84 within the original 114-record census. Accession coverage is 340 of 4,695 families (7.24%). The original files remain recoverable under `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/`, with relative paths and verified `SHA256.json` and `SHA256SUMS` lists for 49 starting files. These are dated corrections after the original protocol; `PROTOCOL.md` is unchanged.

The corrections use the [numerical and rights audit](../2026-10-13-data-round-1-verification/REPORT.md) and the [independent join check](verification/independent-check.md). No source was acquired. Saved museum records, Lipi identifiers and the Mackay–Marshall table package supplied the inputs. Penn attribution remains: Penn Museum Collections Data, Penn Museum, CC BY 4.0.

## Findings applied

| Finding | Correction | Files |
|---|---|---|
| F01 | Rewrote all 69 restricted-source decision rows as project classifications and saved-record locators, covering Indian Museum, National Museum, V&A, British Museum and Louvre. | `joins/decisions.py` |
| F02–F03 | Regenerated both join tables. The six-word comparison against saved restricted titles and descriptions finds no copied passage. Remaining matches in the reviewer CSV are bibliographic locators. Comparison details stay local. | `joins/join-table.csv`, `joins/q1019-decisions.csv` |
| F12 | Met 49.40.6 and 49.40.10: `indus_attributed` and `in_scope` true → false; attribution basis cleared; exclusion recorded as later-period. Dates are second century CE and first century BCE. | `harvest/met-records.json`, `harvest/review-overrides.json`, `apply_review_overrides.py` |
| F13 | IS.8:2-1951: originality original → modern-impression. IS.8:1-1951: object class sealing-or-impression → seal. | `harvest/vam-records.json`, override ledger and applier |
| F14 | AIC 1920.711 and 1920.712: attribution true → false; later-period exclusion. Their dates are 336–323 BCE. | `harvest/aic-records.json`, override ledger and applier |
| F15 | Reviewed all 12 V&A flags; excluded eight later objects and retained four. Summary classification counts now use reviewed flags. Penn's attributed count now covers its 47 reviewed retained rows; 942 broad matches remain in its note and query log. | `harvest_summary.py`, `harvest/summary.csv`, README and proposal files |
| F16 | Copied the inventory's whitespace/case normalization, POST alias and `type_group` rule, recording source `experiments/2026-10-12-data-inventory/coverage.py:type_group`. Retained existing display labels. | `coverage_museum.py`, `coverage/museum-coverage.json` |
| F17 | Replaced the precision placeholder with counts, interval, weaker joins, two Lothal faults, recovered join and unexamined sources. | `README.md` |
| F19 | Six newly joined families gain an axis, including two with no dimension before; the other four already had an axis. | `README.md`, `DATA-UPDATE.md`, `registry-entry.json` |

The independent reviewer recovered Indian Museum `10377/A7252/C.2803` as family 2194, CISI M-1809, through Marshall 1931 vol. II p. 403 row 199. The exact-match search missed the `DK-` prefix. Its decision changes from ambiguous to confirmed; material, motif, size and level agree. The original 125-family descriptive candidate set remains in the preserved starting table. The review precision still describes the original set: 26 checked, 26 supported, 0 qualified, 0 wrong, 100%, with a one-sided 95% exact lower bound of 89%.

The ledger records 45 field overrides. It also carries four existing Met photograph observations as `inscribed-by-image`, four existing Penn uninscribed decisions as `uninscribed`, and seven British Museum saved-record inscription judgments. These make selected-object counts reproducible from flags. The applier validates old values before writing and accepts new values on replay. The rebuilt files also include `coverage/summary.json`, `manifest-additions.json`; the proposals in `DATA-UPDATE.md`, `question-updates.md` and `registry-entry.json` carry the corrected counts and review links. `acquisition_record.py` was rerun and its output is unchanged.

## V&A decisions

Culture and period fields are empty for these 12 records. Saved date, place and object type, with the existing impression decision, supply the classifications below. Reasons are project summaries.

| Accession | Decision | Basis |
|---|---|---|
| IS.8:1-1951 | Retain; original seal | About 2500 BCE, Mohenjo-daro; correct object class |
| IS.8A-1951 | Retain; original fragment | About 2000 BCE; saved description and bibliography locate it at Mohenjo-daro |
| IS.8:2-1951 | Retain attribution; modern impression | Paired with IS.8:1-1951; excluded from original counts |
| IS.9-1951 | Retain attribution; outside inscription scope | Terracotta head, 2000 BCE, Mohenjo-daro; no stated inscription |
| RPS.721-2024 | Exclude | Photograph, 1930, India; river reference |
| CIRC.661-1956 | Exclude | Fabric, 1956, Helsinki; title match |
| 4643(IS) | Exclude | Painting, 1808; river reference |
| IS.60-1985 | Exclude | Cap, twentieth century, Indus Kohistan |
| T.989-2000 | Exclude | Fabric, 1979, Great Britain; title match |
| IS.2-1997 | Exclude | Shawl, mid twentieth century, Indus Kohistan |
| 1132-1869 | Exclude | Painting, 1862, London; river reference |
| D.1604-1907 | Exclude | Watercolour, nineteenth century, Attock; river reference |

V&A attributed flags change from 12 to 4; its summary stays at 4, now derived from those flags. Inscribed originals stay at 2 and impressions at 1. Among attributed records, original flags change from 12 to 3, including the head outside scope.

## Before and after counts

| Measurement | Before | After |
|---|---:|---:|
| Package exact or confirmed joins | 26 | 27 |
| New joins and new families against census | 18 | 19 |
| Combined joined museum records | 86 | 87 |
| Census-scope lower bound | 83 | 84 |
| All decided records: confirmed / ambiguous | 24 / 29 | 25 / 28 |
| Q-1019: confirmed / ambiguous | 15 / 22 | 16 / 21 |
| No-usable-key cohort: confirmed / ambiguous | 9 / 19 | 10 / 18 |
| Indian Museum: confirmed / ambiguous | 1 / 8 | 2 / 7 |
| Families with an accession | 339 (7.22%) | 340 (7.24%) |
| Families gaining a first museum number | 15 | 16 |
| Seal accession coverage | 247/2239 (11.0%) | 248/2239 (11.1%) |
| Mohenjo-daro accession coverage | 242/1795 | 243/1795 |
| Pottery denominator, all three coverage stages | 629 | 630 |
| Other denominator, all three coverage stages | 188 | 187 |
| Met attributed flags and summary count | 45 | 43 |
| Met in-scope flags | 7 | 5 |
| AIC attributed flags | 2 | 0 |
| V&A attributed flags | 12 | 4 |
| Penn summary attributed-record count | 942 broad matches | 47 reviewed retained rows |
| Combined coverage, brackets included | 541 (11.52%) | 542 (11.54%) |
| Combined coverage, whole cell unbracketed | 518 (11.03%) | 519 (11.05%) |
| Combined coverage, any definite number | 533 (11.35%) | 534 (11.37%) |

New manifest fields explicitly record the 84 census-scope joins, 340 accession-covered objects, 16 first-number gains and four V&A records. Pottery numerators remain 5, 6 and 8; other numerators 2, 3 and 3. Their displayed percentages stay unchanged. The package still decides 86 records, including all 46 Q-1019 records. Exact joins stay at 2, unmatched 25, uninscribed 5, impressions 1 and reproduced census joins 8. Q-1019 unmatched and uninscribed stay at 8 and 1. Candidate additions stay at 5. Axis gains remain 6, first dimensions 2, finer findspots 1 and open image gains 0. The rounded accession headline remains 7.2%.

## Recall search and coordinator decisions

`recall_search.py` searches all 59 non-joined decision rows after the added join. It normalizes carried accession, excavation, field, registration and museum identifiers, including slash/semicolon components and two-number composite accessions. It searches every Lipi excavation identifier and CISI key plus the saved Mackay–Marshall field numbers without a site filter. Ten records have hits: four confined to one family and six with multiple families. There are 92 candidate rows in [recall-candidates.csv](joins/recall-candidates.csv). The nonnumeric accession `dki` supplies many area-prefix hits, retained for completeness. No join was added from this search.

The four single-family records are Met 49.40.1, Penn L-141-157, Indian Museum 11085/ A6686 and National Museum 3714. A substring can occur in a figure number or another site's record. A single-family hit needs its printed row read. Where the existing table package has no row, the output gives the CISI entry and page range to search, marking the identifier row as not yet located. The coordinator must arrange these image checks.

The reviewer-owned `verification/independent-check.csv`, line 15, contains a Lipi sign sequence. It remains untouched. The coordinator must remove the sequence or keep the CSV local before public commit. Families 2067 and 2084 need a separate shared-corpus correction; family 2067's identifier-linked fields should be withheld from propagation pending that check. V&A raw responses remain due for deletion by 10 November 2026.

## Offline validation

Ran the override applier, `build_joins.py`, `coverage_museum.py`, `harvest_summary.py`, `acquisition_record.py`, `write_manifest_additions.py`, `recall_search.py` and the verifier's `check_counts_post_fix.py`. The latter saves [combined-coverage-post-fix.json](../2026-10-13-data-round-1-verification/combined-coverage-post-fix.json) from current local CISI 2 final rows with an input hash; the original combined coverage file stays unchanged. Override replay changes no file, join validation has no problems, and every type classification agrees with the inventory rule. Final prose check: `python tools/review_prose.py --path experiments/2026-10-13-museum-open-access --no-write`.

The identifier joins survived review, and the recovered seal shows that concatenated area and catalogue references hide usable links. The deciding next test is to read the recall candidates against printed rows and count the additional identities that hold.
