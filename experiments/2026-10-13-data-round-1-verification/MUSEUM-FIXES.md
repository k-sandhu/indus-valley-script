# Museum corrections handoff, 13 October 2026

All ten museum findings (F01?F03, F12?F17 and F19) are applied within the permitted paths. The recovered Indian Museum join is included; the recall search supplies candidates for the coordinator's printed-page checks. Public publication still needs the reviewer CSV sign sequence handled as noted below. No network request, harvest acquisition script, Git mutation or shared-file edit was made.

This was the Codex primary agent's offline post-review correction run. The request specifies GPT-6.1-Sol; no independently verifiable runtime model identifier is exposed here. The independent identity observations are Claude Opus 5.5's, linked in the package review. The protocol and original verification report, findings and combined coverage remain intact. Penn attribution remains: Penn Museum Collections Data, Penn Museum, CC BY 4.0.

## Findings and changes

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


## Before and after

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


The pre-review precision paragraph was a placeholder; it now records 26 checked, 26 supported, 0 qualified, 0 wrong, 100%, and an 89% one-sided 95% lower bound. The original 26-join review set is retained as the denominator.

Museum first-number gain over the common website/census baseline and after the CISI 2 pilot both change from 15 to 16. The pilot still contributes 202 first museum numbers after the museum package. No family gains its first number from both packages. The combined totals use the current local final pilot rows, with an input hash in `combined-coverage-post-fix.json`; they include 542 (11.54%), 519 (11.05%) and 534 (11.37%) families under the three rules. The original totals 541, 518 and 533 are preserved in `combined-coverage.json`.

## Recall and coordinator decisions

`recall_search.py` searches all 59 non-joined decision rows after the added join. It normalizes carried accession, excavation, field, registration and museum identifiers, including slash/semicolon components and two-number composite accessions. It searches every Lipi excavation identifier and CISI key plus the saved Mackay–Marshall field numbers without a site filter. Ten records have hits: four confined to one family and six with multiple families. There are 92 candidate rows in [recall-candidates.csv](../2026-10-13-museum-open-access/joins/recall-candidates.csv). The nonnumeric accession `dki` supplies many area-prefix hits, retained for completeness. No join was added from this search.

The four single-family records are Met 49.40.1, Penn L-141-157, Indian Museum 11085/ A6686 and National Museum 3714. A substring can occur in a figure number or another site's record. A single-family hit needs its printed row read. Where the existing table package has no row, the output gives the CISI entry and page range to search, marking the identifier row as not yet located. The coordinator must arrange these image checks.

The reviewer-owned `verification/independent-check.csv`, line 15, contains a Lipi sign sequence. It remains untouched. The coordinator must remove the sequence or keep the CSV local before public commit. Families 2067 and 2084 need a separate shared-corpus correction; family 2067's identifier-linked fields should be withheld from propagation pending that check. V&A raw responses remain due for deletion by 10 November 2026.


The coordinator should integrate the museum proposals into shared DATA, manifest, question and registry files, retain Penn attribution, arrange recall-candidate page-image checks and handle the reviewer CSV before commit. This run neither changed nor judged the coordinator's concurrent CISI 2 corrections.

## Validation

All seven museum correction/rebuild commands exited successfully with network connection calls disabled for the validation replay. The nine generated outputs replay byte-identically. All saved harvest records stay identical on a second override application. All 4,695 family type classifications match the inventory rule. Join validation has no problems, the 49 preserved files match their SHA256 list, and the protocol/reviewer files stay unchanged during replay. A six-word comparison finds zero restricted title/description prose matches; the sole match line consists of permitted bibliographic locators in the independent CSV. Source comparison detail is local. The prose scan reports no flags.

Commands, run from the repository root with Python bytecode writing disabled:

```text
python -B experiments/2026-10-13-museum-open-access/apply_review_overrides.py
python -B experiments/2026-10-13-museum-open-access/build_joins.py
python -B experiments/2026-10-13-museum-open-access/coverage_museum.py
python -B experiments/2026-10-13-museum-open-access/harvest_summary.py
python -B experiments/2026-10-13-museum-open-access/acquisition_record.py
python -B experiments/2026-10-13-museum-open-access/write_manifest_additions.py
python -B experiments/2026-10-13-museum-open-access/recall_search.py
python -B experiments/2026-10-13-data-round-1-verification/check_counts_post_fix.py
python tools/review_prose.py --path experiments/2026-10-13-museum-open-access --no-write
```

## Every changed or created path

Changed existing package files:

- `experiments/2026-10-13-museum-open-access/DATA-UPDATE.md`
- `experiments/2026-10-13-museum-open-access/README.md`
- `experiments/2026-10-13-museum-open-access/RETROSPECTIVE.md`
- `experiments/2026-10-13-museum-open-access/coverage/museum-coverage.json`
- `experiments/2026-10-13-museum-open-access/coverage/summary.json`
- `experiments/2026-10-13-museum-open-access/coverage_museum.py`
- `experiments/2026-10-13-museum-open-access/harvest/aic-records.json`
- `experiments/2026-10-13-museum-open-access/harvest/bm-records.json`
- `experiments/2026-10-13-museum-open-access/harvest/met-records.json`
- `experiments/2026-10-13-museum-open-access/harvest/penn-records.json`
- `experiments/2026-10-13-museum-open-access/harvest/summary.csv`
- `experiments/2026-10-13-museum-open-access/harvest/vam-records.json`
- `experiments/2026-10-13-museum-open-access/harvest_summary.py`
- `experiments/2026-10-13-museum-open-access/joins/decisions.py`
- `experiments/2026-10-13-museum-open-access/joins/join-table.csv`
- `experiments/2026-10-13-museum-open-access/joins/q1019-decisions.csv`
- `experiments/2026-10-13-museum-open-access/manifest-additions.json`
- `experiments/2026-10-13-museum-open-access/question-updates.md`
- `experiments/2026-10-13-museum-open-access/registry-entry.json`
- `experiments/2026-10-13-museum-open-access/write_manifest_additions.py`

Created package files:

- `experiments/2026-10-13-museum-open-access/REVIEW-CHANGES.md`
- `experiments/2026-10-13-museum-open-access/apply_review_overrides.py`
- `experiments/2026-10-13-museum-open-access/harvest/review-overrides.json`
- `experiments/2026-10-13-museum-open-access/joins/recall-candidates.csv`
- `experiments/2026-10-13-museum-open-access/joins/recall-summary.json`
- `experiments/2026-10-13-museum-open-access/recall_search.py`

Regenerated with unchanged bytes:

- `experiments/2026-10-13-museum-open-access/harvest/acquisition-record.json`

Created verification deliverables:

- `experiments/2026-10-13-data-round-1-verification/check_counts_post_fix.py`
- `experiments/2026-10-13-data-round-1-verification/combined-coverage-post-fix.json`
- `experiments/2026-10-13-data-round-1-verification/MUSEUM-FIXES.md`

Created local correction/validation files:

- `data/raw/2026-10-13-data-round-1-verification/apply_museum_fixes.py`
- `data/raw/2026-10-13-data-round-1-verification/validate_museum_post_fix.py`
- `data/raw/2026-10-13-data-round-1-verification/museum-rights-post-fix-detail.json`
- `data/raw/2026-10-13-data-round-1-verification/museum-post-fix-command-log.json`
- `data/raw/2026-10-13-data-round-1-verification/museum-post-fix-validation.json`
- `data/raw/2026-10-13-data-round-1-verification/combined-museum-coverage-post-fix.csv`

Created local preservation files (each copy verified before edits):

- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/DATA-UPDATE.md`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/PROTOCOL.md`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/README.md`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/RETROSPECTIVE.md`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/__pycache__/candidates.cpython-313.pyc`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/__pycache__/classify.cpython-313.pyc`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/__pycache__/lipi_index.cpython-313.pyc`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/__pycache__/mo_common.cpython-313.pyc`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/acquisition_record.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/build_joins.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/candidates.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/cisi1_locate.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/classify.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/coverage/museum-coverage.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/coverage/summary.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/coverage_museum.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/acquisition-record.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/aic-queries.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/aic-records.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/bm-records.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/cleveland-queries.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/cleveland-records.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/met-queries.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/met-records.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/penn-queries.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/penn-records.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/smithsonian-queries.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/smithsonian-records.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/summary.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/vam-queries.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest/vam-records.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_aic.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_bm.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_cleveland.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_met.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_penn.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_smithsonian.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_summary.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/harvest_vam.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/joins/__pycache__/decisions.cpython-313.pyc`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/joins/decisions.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/joins/join-table.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/joins/q1019-decisions.csv`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/lipi_index.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/manifest-additions.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/mo_common.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/question-updates.md`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/registry-entry.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/write_manifest_additions.py`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/SHA256.json`
- `data/raw/2026-10-13-museum-open-access/pre-review-2026-10-13/SHA256SUMS`


The recovered seal establishes that the exact-match pass missed a usable composite identifier. The deciding next test is to read every recall candidate against its printed row and measure how many further museum identities hold.
