# Printed chart numbering audit

Status: Proposed. Written on 8 October 2026 before rendering or recording new readings. The shared work-package brief gives 7 October; this package uses the environment date and the assigned 8 October directory.

The question is whether the 687 numeric entries in `research/chart_reference/manual_numeric_reference.json` reproduce the upper class numbers and lower sign codes printed on PDF pages 20–21 of Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979). The audit concerns this edition's numbering. The new reference will remain Exploratory pending independent review.

## Inputs and prior work

Use the existing PDF, SHA256 `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27`, the existing atlas's cell coordinates and the original reference's cell identities. Reuse coordinates from `output/chart_atlas/reference.json`; do not reuse its numeric readings as new observations. The PDF text layer supplies no values. Render pixels with PyMuPDF at 6 pixels per point or more. Save full pages, cell crops and comparison sheets only under `data/raw/2026-10-08-chart-reference-audit/`.

Registry ROOT-15 and the corpus/transcription retrospective record earlier manual digit reads, 16 retained lower-code ambiguities and duplicate-label checks. HELSINKI1979-DIGITIZATION-01 records failed frozen recognizer evaluations. Those evaluations will not be rerun. The new evidence is the named chart-label disagreement reported in package N and a complete fresh pixel reading. Read N's returns only for chart observations; their inscription sequences do not establish chart values.

## Reading and comparison

Read every cell in page/column/row order from labelled image sheets showing the printed upper number, drawing and lower number. Record both numbers without printing the old values beside the sheet. Retain per-cell confidence, candidate alternatives when pixels do not discriminate them, source crop coordinates and a note for every difficult digit. Confidence is a qualitative judgement, not an error probability. Record the observation list before computing differences against the old reference.

Then compare every upper/lower value and alternative set. Reinspect mismatches, all 16 old ambiguous cells and every duplicate code in larger crops, at least 12 pixels per point. Test the coordinator's suggested 205/206/208 and 486 readings from pixels. Upper class order should be nondecreasing down columns and across column boundaries, with repeated classes allowed. Lower codes need not be monotone; nearby numeric families are supporting checks only. A duplicate code triggers drawing comparison rather than automatic replacement: the edition may repeat a drawing or print an error. Report every surviving duplicate and whether its drawings differ. Never choose a digit solely to enforce uniqueness or sequence.

A negative result is an unresolved printed digit, a contradiction among the digit pixels and consistency checks, or a surviving code shared by visibly different drawings. Such cases remain explicit candidates or printed anomalies in v2. A full audit requires an image reading for all 687 cells; any uninspected cell must be marked pending instead of copied as verified.

## Revised reference and consumer impact

Create `chart-reference-v2.json` with the original fields and row structure, updated numeric fields and a per-changed-cell `change_log` giving old/new fields and evidence. Preserve uncertainty and auxiliary metadata separately. Preserve the original reference and atlas bytes. Make a machine-readable comparison for every primary-value change, alternative removed/retained and upper-class change.

Locate the 60-row v1 and 80-row v2 benchmark references, package M's v3 blind packet, recognizer templates/chart snapshots/position cards, package N's reader cards, and package O's public-release chart, benchmarks and scoring code. Distinguish direct cell-identity joins from numeric-label-only candidates. A numeric substitution is not reliable when an old code labels multiple cells. List exact file paths, row or unit identifiers and JSON/table fields. Keep per-inscription extracted rows local; tracked outputs contain counts, locators and label changes without whole sequences. Do not compute replacement benchmark scores or change consumers.

Recommend a versioned chart snapshot, a separately dated sensitivity scoring run that maps by cell identity when available, and a new release version. Report code-labelled candidates whose graphic identity cannot be established from the existing records.

## Integrity, sources and deliverables

Record hashes of reused PDF, reference, atlas metadata and relevant frozen consumer inputs before analysis; verify them afterwards. Reproduction scripts write only this package and its local raw directory, set temporary/cache paths there and suppress bytecode writes. No dependency installation is planned. Keep raw source pixels and extracted consumer rows local. Include source title, authors, year, venue/publisher, URL, opened/snippet status, rights and transformations in `sources.json`. Record failed searches and downloads, including zero when none were attempted.

Deliver the reference, complete own-observation table, comparison and impact aggregates, code, README, REPORT, RETROSPECTIVE and proposed registry entry. Run `python tools/review_prose.py --path experiments/2026-10-08-chart-reference-audit --no-write` from the repository root and fix substantive wording flags. Independent review should replay generation, check coverage and hashes, inspect changed/ambiguous/duplicate cells, sample unchanged cells, and repeat consumer joins.

## Amendment, 8 October 2026

After the saved first-pass readings, the user supplied package M v3's card-label observations for four cells. Inspect only that section of `repair/2026-10-08-v3/blind/adjudication-notes.json`. Test each proposed printed number on larger raster crops, including the claim that `20:4:13` prints 350. Include v3's newly available adjudicated reference in the consumer joins. These follow-up decisions and their outputs are Exploratory. Preserve the first-pass readings separately so that this added evidence cannot silently replace them.

Model-service interruptions stopped the work several times. Resume by parsing every saved JSON file, checking image coverage and examining incomplete deliverables. Consumer joins begin only after the saved first pass and the explicit reinspection decisions have been recovered. When a unit's candidate code has no matching chart location, report a potential mapping separately; do not silently replace a code shared by several chart cells. The impact analysis counts changed labels and locators, without computing new scores.

During final continuation review, add a 24x comparison for `p21_c8_r5`, `p20_c3_r18` and `p21_c8_r2`. This revisits the same reader's saved 571 decision after the preliminary comparison. Preserve the preliminary exploratory reference, comparison, observations, decisions and impact under the local `continuation-history/` directory before making that refinement. Keep the frozen first-pass readings unchanged. The final 671 decision remains Exploratory.

## Review amendment, 8 October 2026: v2.1

Apply the coordinator's review follow-up using `REVIEW.md` and the saved `review/` outputs as read-only witnesses. Before changing values, inspect `p20_c3_r33` and neighboring classes in new local raster crops. If the second digit supports 6, change class 85 to 86 in `chart-reference-v2.1.json`. Preserve v2, all original computed outputs, the first-pass observations and every reviewer file. Pin these files before the amendment and verify them afterwards.

Lower qualitative confidence to medium for the six cells required by the review, every cell the reviewer rates below high, cells whose saved evidence explicitly records worn or broken deciding digits, the two unsettled whole-chart pixel cases, and the new class decision. Record each reason separately. This conservative rule is chosen before producing amended counts; a medium label does not introduce an alternative printed code. Retain 360 at `p20_c4_r13` if the pixels support its rounded 6 outline, and record both the reviewer's initial 350 and final 360 evidence. Reuse the 63-cell blind reading, pixel-sweep resolutions and nearest-neighbor check without rerunning or editing reviewer scripts.

Generate dated amendment observations and comparison, then run parameterized `impact.py` and `verify.py` into new v2.1 outputs. Keep extracted release rows and new images under the local revision directory. The comparison must distinguish value changes from confidence changes. Report the 15 first-pass code misreads, the 630 cells initially read once, and the two code corrections prompted by v3 hints. The reviewer sample agrees on 63 classes/codes; the full sweep found no code disagreement but one class correction and two unresolved digit checks. These remain two AI readings without expert review, with status Exploratory. Update consumer guidance and prose, and rerun the prose scan with `--no-write`.
