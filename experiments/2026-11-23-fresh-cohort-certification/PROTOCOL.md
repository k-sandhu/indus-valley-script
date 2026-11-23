# Protocol: fresh post-catalogue cohort certification

Date: 23 November 2026. Scope: non-purchase execution of GitHub Issue #20, covering question cards [Q-1014](../../knowledge/questions/Q-1014-dholavira-inventory.md) (Dholavira inventory) and [Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md) (post-catalogue finds), together with institutional data-access drafts for [Q-1011](../../knowledge/questions/Q-1011-icit-access-and-fuls-wells-corpora.md) (ICIT) and [Q-1017](../../knowledge/questions/Q-1017-harp-harappa-context-registers.md) (HARP).

This protocol is frozen before opening candidate object rows, inspecting PDF pages, or running the certification script. Its SHA-256 digest is recorded in `PROTOCOL.sha256`.

## 1. Objective and blinding rule

All 4,695 provisional objects in the base register (`data/raw/2026-10-22-object-register/run-v2/objects.jsonl`) currently carry `exposure_status` different from `fresh`. Our goal is to deterministically adjudicate every row in the existing post-catalogue inventories against every local corpus and join register, certify which post-catalogue inscribed objects are genuinely absent from the local corpus and unspent, verify whether held local PDFs contain readable figures or plates for them, and compute the exact statistical power of the certified fresh seal cohort against the frozen predictions P1 to P4 of [PREDICTIONS.md](../2026-10-20-seal-legend-units/PREDICTIONS.md).

**Strict blinding rule.** Sign sequences, sign counts, text lengths, reading directions, and motif-based or text-based identity guesses remain sealed throughout this study. Scripts may inspect bibliographic metadata, site names, excavation registrations, catalogue numbers, object types, findspots, dimensions, page numbers, figure or plate captions, and embedded image-object presence in held PDFs. No script or analyst in this package may transcribe signs, inspect sign sequences of candidate objects, or run any hypothesis test or scorer (`score_prospective.py` or `python -m bench`) on candidate objects.

## 2. Input populations and reference registers

Every input is read-only and hashed before processing:

1. **Post-catalogue object inventory (503 rows)**: `experiments/2026-10-21-post-catalogue-finds/objects.csv`, supplemented by `join-decisions.csv` (291 rows), `local-unnamed.csv` (41 rows), `matching/source-register.csv` (258 rows), and `exposure-log.csv`.
2. **Candidate identity and exposure audit (358 rows)**: `data/raw/2026-10-22-candidate-identity-exposure/run-v3/reconciled-dispositions.csv`, `candidate-reviews.jsonl`, `duplicate-relations.jsonl`, and `exposure-events.jsonl`.
3. **Pinned Lipi corpus (4,695 families, 5,680 faces)**: `data/normalized/lipi_observed_faces.jsonl` (metadata and identifier fields only; sign fields are not loaded into any matching decision) and `data/raw/2026-10-22-object-register/run-v2/objects.jsonl` (4,695 base register records).
4. **Mackay 1938 and Marshall 1931 seal-table joins (1,146 rows)**: `experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv`.
5. **CISI 1 and 2 basic-data joins (3,680 rows, 2,602 joined to Lipi families)**: `experiments/2026-10-13-cisi-basic-data-full/object-flags.csv`, `data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl` (1,543 rows), and `cisi2-basic-data.jsonl` (2,139 rows).
6. **Spent-split ledger**: `bench/spent.json`.
7. **Held local PDFs**: files recorded in `matching/source-register.csv`, plus the held site reports documented in `knowledge/DATA.md` (Bisht 2015 preliminary Dholavira report, Farmana 2011, Rakhigarhi Nath 2014 draft, Surkotada MASI 87, Kanmer draft chapters, and Tarkhanewala-Dera).
8. **Cross-reference reserve**: `experiments/2026-10-20-fresh-test-collection/coverage-summary.json` and `experiments/2026-10-20-reserved-test-program/REPORT.md` (checked for overlap so Farmana objects are never double counted).

## 3. Deterministic certification rules

Every row in the 503-row post-catalogue inventory is reconciled with the 358-row candidate audit (`source_row_id` = `row_id`) and assigned to exactly one mutually exclusive certification tier.

### Cross-corpus overlap checks

For every row we compute deterministic, site-qualified identifier joins against:
- all 4,695 Lipi families (exact CISI key, whole-token excavation registration after site-prefix normalization such as `DHR-` or Kanmer season-number tokens, and prior confirmed family links);
- all 1,146 Mackay/Marshall join rows (field number and excavator catalogue number for Mohenjo-daro);
- all 3,680 CISI 1 and 2 basic-data rows (2,602 joined to Lipi families plus 1,078 catalogued CISI entries without a Lipi family), checking CISI numbers and printed excavation numbers;
- `bench/spent.json`, confirming whether any Lipi family or source hash linked to the row appears in any spent split or recorded confirmation read.

### Tier definitions

1. **`already_present_or_exposed`**: Assigned if any of the following holds:
   - `catalogue_status` is `in_baseline`, `in_cisi3`, or `possible_in_cisi3` (the object belongs to a CISI volume rather than post-catalogue finds);
   - the row has a verified identifier match to a Lipi family (`local_match == 'matched'`, `identity_status == 'identifier_supported_provisional_family'`, or a new deterministic registration or CISI hit against Lipi, Mackay/Marshall, or CISI 1–2);
   - the row carries a documented historical inscription-image display (`reviewed_exposure_status == 'source_page_image_display_recorded_object_scope_unresolved'`);
   - the row's linked object or source was consumed in `bench/spent.json` or in an earlier statistical analysis.
   Sub-reason tags distinguish `cisi_catalogued`, `matched_to_lipi_identifier`, `confirmed_known_in_reserve_audit`, and `image_or_statistical_exposure`.

2. **`blocked_by_alias_ambiguity`**: Assigned to rows not in Tier 1 when absence from Lipi cannot be established because the site holds an unindexed or unregistered pool of compatible Lipi or CISI objects without an accession crosswalk:
   - Dholavira rows (`site_code == 'DHV'`) that retain candidate links to Dholavira's unregistered Lipi pool (including rows with post-protocol `context_join_family` proposals, because `2026-10-22-candidate-identity-exposure` retained them as `candidate_only` without an accession crosswalk);
   - Surkotada rows (`site_code == 'SKT'`) whose potsherd entries compete against CISI 1's four unnumbered Surkotada potsherds;
   - any other post-catalogue row whose `unresolved_candidate_family_ids` or `local_family_ids` contains two or more unregistered or ambiguous Lipi families that cannot be separated without an external accession concordance.

3. **`certified_absent_sealed`**: Assigned to rows not in Tiers 1 or 2 when ALL of the following hold simultaneously:
   - `catalogue_status == 'post_catalogue'` and `inscription_status == 'definite'`;
   - zero confirmed or candidate links to any of the 4,695 Lipi families, zero links to the 1,146 Mackay/Marshall joins, and zero links to the 2,602 CISI 1–2 basic-data joins (and zero links to the remaining 1,078 unjoined CISI 1–2 entries);
   - absence is positively verified by site exhaustion (zero Lipi/CISI entries at the site), site-plus-object-type exhaustion (zero compatible-type Lipi/CISI entries at the site), or exhaustive registration/findspot/dimension disjointness against every compatible local object at that site;
   - no unresolved `possible_duplicate_of` conflict that would double-count the same physical object (where a duplicate pair exists between two absent rows, at most one primary witness row with the fuller publication record may be kept only if resolved; unresolved pairs stay in Tier 4 unless one row is explicitly a secondary citation of the same physical object);
   - zero usage in `bench/spent.json` or any prior statistical scoring run, and zero recorded inscription-image display;
   - a held local PDF exists on disk (`sha256` verified against `source-register.csv`), the publication reports a photograph or line drawing (`photo_published == 'yes'` or `drawing_published == 'yes'`), and our blind PDF plate-locator audit confirms that the cited PDF page (or adjacent plate page) exists in the file and contains an embedded raster image or drawing figure matching the reported plate or figure label without inspecting sign sequences.

   Each `certified_absent_sealed` record additionally records:
   - `object_class`: `seal` (eligible for P1–P4) versus `sealing`, `tablet`, `pottery`, or `other`;
   - `absence_proof_basis`: `site_absent_in_lipi_and_cisi`, `site_type_absent_in_lipi_and_cisi`, or `site_registration_context_disjoint`;
   - `metadata_completeness`: presence of `(site, registration, object_type, dimensions)` and whether dimensions are recorded in the held source metadata;
   - `participant_exposure_scope`: exact historical access summary from `2026-10-22-candidate-identity-exposure`, specifying which prior agents (e.g., 2026-10-21 Codex extraction runs) must be excluded from blind transcription.

4. **`conditionally_absent_needs_plate_check`**: Assigned to all remaining post-catalogue rows, including:
   - verified-absent post-catalogue rows that lack a published photograph or drawing, lack a held local PDF, fail the PDF page/plate locator check, or carry an unresolved duplicate flag;
   - post-catalogue rows with `inscription_status == 'uncertain'` that are absent from Lipi;
   - post-catalogue rows at sites with a small local Lipi population (such as Farmana, Kanmer, Bagasra, Rakhigarhi, Shikarpur, Bhirrana, Khirsara, Rupar, Tarkhanewala Dera, Baror, Karanpura, Ganweriwala, or Nuhato) where one or more resolving fields (registration, dimensions, or a plate check against a small candidate set) remain open, or where a post-protocol `context_join_family` was proposed without an identifier match.

## 4. Blind PDF plate-locator check

For every row that is a candidate for `certified_absent_sealed` (or verified absent with a held PDF), a Python script using PyMuPDF (`fitz`) opens the local PDF solely to verify:
1. File existence, byte size, and SHA-256 match against `source-register.csv`.
2. Total page count and bounds check for the recorded `pdf_page` (or locating the printed page / plate number by searching page headers and figure/plate captions only).
3. Presence of embedded raster images (`page.get_images()`) or vector drawings (`len(page.get_drawings())`) on the target page and matching plate/figure caption token (e.g., `Pl.`, `Fig.`), logging only page number, image count, image dimensions in pixels, and matched caption label.
4. No page images are rendered to the agent for visual viewing, and no inscription sign-reading text is printed or parsed. Every PDF read is appended to `data/raw/2026-11-23-fresh-cohort-certification/pdf-access-log.jsonl`.

## 5. Statistical power against frozen predictions P1 to P4

For the resulting `certified_absent_sealed` seal cohort (size $n_{\text{sealed}}$) and sensitivity pools (including conditionally absent seals if resolved by plate checks, and assuming the CISI 3.1 single-line eligibility yield of 60% reported in `PREDICTIONS.md` as well as 100% upper bound), we compute exact pass bounds and statistical power against P1, P2, P3, and P4 using the exact calibration parameters and formulas frozen in `experiments/2026-10-20-seal-legend-units/predictions.json` and `make_predictions.py` (seed `20261021`, 40,000 simulations for P1/P3, 20,000 for P2, exact binomial tail for P4).

## 6. Independent verification and outputs

Tracked outputs in `experiments/2026-11-23-fresh-cohort-certification/`:
- `PROTOCOL.md` and `PROTOCOL.sha256`
- `code/certify_fresh_cohort.py`
- `code/verify.py`
- `fresh-cohort-v1.json` and `fresh-cohort-v1.csv` (all 503 rows with certification tier, sub-reason, cross-checks, plate locator status, and exposure scope)
- `summary-v1.json` (tier counts by site and object class, 503 + 358 accounting, P1–P4 power tables, Farmana cross-check)
- `verification-v1.json` (independent checks: zero Lipi/CISI/spent overlap in `certified_absent_sealed`, exact row conservation across 503 and 358 rows, source SHA-256 verification)
- `REQUEST-ICIT-Q1011.md` and `REQUEST-HARP-Q1017.md`
- `REPORT.md`, `DATA-UPDATE.md`, and `RETROSPECTIVE.md`

Local derived logs under `data/raw/2026-11-23-fresh-cohort-certification/` (D: junction):
- `pdf-access-log.jsonl`
- `input-hashes.json`
