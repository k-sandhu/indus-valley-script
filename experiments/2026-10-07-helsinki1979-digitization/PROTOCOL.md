# Helsinki 1979 digitization protocol

Recorded 7 October 2026 before new recognition outcomes. Status: Proposed.

The question is whether page-specific crop detection and a chart-trained image recognizer can recover the printed drawings, inscription labels and classification fields in Koskenniemi and Parpola's *Corpus of Texts in the Indus Script* (1979). A printed occurrence is the recording unit. Repeated sort orders, wrapped rows and object-side conventions will remain explicit. Codes are Finnish lower chart codes; upper ranks define the edition's graphic classes.

## Inputs and previous results

Use the unchanged 180-page PDF, `research/corpus/primary/koskenniemi_parpola1979.pdf`, SHA256 `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27`, and the current 687-cell `research/chart_reference/manual_numeric_reference.json`. Copy the chart into this package at freezing and retain every numeric candidate and uncertainty underline. Source definitions are in `data/normalized/koskenniemi1979_definitions.json` and the later 1980 definitions. Attribution: Kimmo Koskenniemi and Asko Parpola, 1979, Department of Asian and African Studies, University of Helsinki, Research Reports 1, [official entry](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [handle](http://hdl.handle.net/10138/342677), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Read registry ROOT-15, ROOT-16, METHODS-font_fresh20_audit and METHODS-font_geometry_sensitivity. Reuse the chart labels, crop-library concept and candidate-set edit scoring from `src/font_pilot.py`, `src/font_fresh20.py`, `src/evaluate_font_pilot.py` and `src/evaluate_font_fresh20.py`. Reuse the fresh20 reference and clean bounds only for development. The frozen fresh20 failure remains unchanged: 14/20 matching counts, 2/20 strict top-one compatible rows and 5/20 top-five rows. The post-reference crop diagnostic has 18/20 matching counts and 6/20 and 16/20 compatible rows. This retry tests observed page geometry and a new image matcher.

## Development and freezing

Develop row geometry and recognition on chart pages 20 and 21 and previously inspected corpus PDF page 30. Earlier source overview pages 22 and 25 are excluded from evaluation. Use independently detected blank vertical bands or connected components instead of a cumulative pitch. Locate the narrow number/classification field separately from glyph ink; record uncertain field detection, OCR and order checks. Preserve continuation rows with missing labels rather than inventing IDs. Printed order can be a consistency check only where the edition's section documents that order.

Train a small image classifier or embedding with chart-only augmentations, and combine it with shape distances. Compare the new pipeline on the known page-30 fresh20 development reference with the published crop-repair diagnostic. Development outcomes select parameters; they estimate no fresh accuracy. Confidence calibration may use chart augmentations or the existing development reference, and its domain must be stated. A confidence left uncalibrated must be labelled as a score, not a probability.

Before a new reference is produced, write `freeze-manifest.json` with source and code hashes, exact parameters, chart snapshot hash, model hash, development pages, environment, seed and output schema. Freeze selection and predictions before releasing reference annotations. No correction selected from fresh outcomes changes that endpoint. Later corrections require a dated amendment, a new output directory and Exploratory status.

## Fresh evaluation

Use seed 20261007 to draw at least 60 printed rows without replacement from detected corpus rows on PDF pages 31 through 80. These pages are disjoint from development and the earlier specified pilot pages. Retain all sampled rows, including auxiliary-only, damaged, continued and unreadable rows. The sample estimates performance conditional on row detection; independently inspect wider page-column context to record missing, merged, clipped or extra rows, and report that limit.

Create high-resolution unmarked source crops with neighbouring context. Independent annotators receive source images, the numerical chart and definitions, but no recognition output, predicted counts or candidates. Record printed ID, classification positions, unit boundaries and candidate codes in visual left-to-right order, auxiliaries, blanks, uncertainty and chart locations. A disputed unit remains a candidate set or an unscorable observation with a reason. Annotation is an AI visual reference subject to reviewer checks. Preserve initial annotations and any later adjudication separately.

Report row crop correctness, drawn-unit counts, ordered candidate-set compatible whole rows at top one and top five, strict uniquely resolved sequence accuracy where measurable, and unit accuracy. For unequal lengths use explicit alignment/edit distance, and do not call edit reduction token accuracy. Give same-position accuracy on equal-count rows separately and aligned recall on all reference units. Inscription-number accuracy uses the blind visual string, including suffixes. Classification accuracy must retain blank positions. Report confidence reliability bins, Brier score and calibration error only on positions with an explicit correctness target. Use Wilson 95% intervals for row proportions and a seeded row bootstrap for unit/calibration summaries.

A negative result is fewer than 90% correctly cropped rows, fewer than 90% exact printed numbers, fewer than 95% matching drawn-unit counts or fewer than 80% whole-row top-five compatibility. A failed criterion blocks describing the output as a reliable complete transcription. Failure still permits a full provisional occurrence extraction and review queue, with every error and source gap retained.

## Full extraction and join

Process the whole edition's corpus sections. Emit JSONL with occurrence key, inscription number or null, page/column/row coordinates in PDF points, unit candidate codes, ranks and scores/confidence, auxiliary candidates, classification code, boundary blanks and flags. Preserve visual order; do not reverse a concatenated multiline or multiside row. Record sort-section and continuation uncertainty, source hash, licence and transformations. Produce aggregate coverage and a low-confidence/error queue. The import interface for package L must join by edition plus printed number and occurrence coordinates, retaining repeated witnesses and uncertain identities.

Search existing 1980 documentation and local concordance material for an explicit number-to-object join. Numeric equality across editions is insufficient. If no reliable join can be verified in this bounded run, record the search and supply the interface without reporting cross-corpus agreement. Applying the frozen restoration model is outside this package's validation endpoint and requires validated code and object crosswalks.

## Rights, storage and reproducibility

Write only inside this package and `data/raw/2026-10-07-helsinki1979-digitization/`. Render pages in memory and retain small evaluation crops and compressed review crops. Store page OCR, predictions and temporary arrays locally; a CC BY derived transcription and evaluation reference may be included in this package with attribution. Keep all new storage below 500 MB, including installed dependency growth when measurable. Set TMP, TEMP and MPLCONFIGDIR under local raw. Scripts must run from the repository root, use explicit output directories and refuse to overwrite frozen outcomes. Record failed downloads/searches, dependency versions and disk use. Run `tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write` and fix actual prose defects.

## Amendment, 7 October 2026, before fresh selection or annotation

Add PDF page 100 to development for the left-aligned sorted section. Source inspection found that its number field starts at about 9.5% of page width, rather than the initial 4.5% locator. Pages 22, 30, 80 and 100 were seen in a four-page overview during initial source discovery. Exclude page 80 from fresh selection, so the eligible range is pages 31 through 79. No page-80 row was individually inspected or scored, but this exclusion makes the exposure boundary explicit. Record the numeric font classifier trained from page-30 sequential labels, and a logistic confidence fit on the equal-count development rows. Retain ordinary OCR as a second witness. Four recognized classification digits are provisionally assigned a blank third position; this requires the blind classification comparison. Detect otherwise unanchored long ink bands as possible continuation rows with null numbers. Shape-canvas normalization was replaced with an aspect- and size-preserving chamfer distance after the first development result. Its outputs remain in `development/trial-01/`. The learned classifier contributes a fixed 0.03 times negative log probability to the shape cost; the segmentation penalty is 1.0. A sparse implementation of the same chamfer calculations avoids allocating full canvases repeatedly. These decisions precede the evaluation reference.

## Freeze record and reference comparison plan

The executable pipeline, parameters, classifier, numeric templates, logistic coefficients and 687-cell chart snapshot are frozen in [freeze-manifest.json](freeze-manifest.json). The final development endpoint is [development/page30_evaluation.json](development/page30_evaluation.json): 17/20 matching drawn counts, 6/20 compatible whole rows at top one and 12/20 at top five. This development result selected no reserved-row reference. The selection is [blind/selection.json](blind/selection.json): 60 rows drawn from 3,460 detected rows on pages 31–79. Independent annotation starts only after [prediction-freeze.json](prediction-freeze.json) records complete hashed predictions.

Three annotators own disjoint primary groups, sample indices 0–19, 20–39 and 40–59, and receive no predictions. For an additional source-only disagreement check, the first annotator rereads 30 and 35, the second rereads 42 and 51, and the third rereads 5 and 13 in separate repeat-reference files after completing their primary groups. These six repeated annotations never replace the primary reference or alter the frozen pipeline. Compare counts, numbers and ordered candidate sets, retaining every disagreement. This adds annotation review without selecting a more favourable endpoint. It was specified before any selected-row annotation began.

## Annotation disclosure, 7 October 2026, after annotation started

The locator manifest also retained `ocr_number_witnesses`, extracted from the PDF's original OCR layer during layout discovery. These are source OCR strings, rather than the new numeric classifier's predictions, but they can disclose possible numbers. Annotator A noticed that field while reading the permitted locator file, stated that it was not used to resolve any field, and continued reading pixels. Preserve the original selection and its hash. A separate [blind/selection-source-only.json](blind/selection-source-only.json) omits OCR witness strings and automated flags for continued annotation. Ask every annotator to disclose exposure in their note. Glyph candidates and pipeline unit counts remain withheld. Report the label-blinding limitation beside number accuracy, and give an annotation-group sensitivity without group A where possible. This locator repair is post-start and does not revise predictions, selection, primary references or the frozen recognition endpoint.


## Amendment, 7 October 2026: coordinator corrections and disk-gated repair

7 October 2026, coordinator follow-up: instructions recorded before new calculations.

### Amendment, 7 October 2026: Part 1 corrections (Exploratory)

Part 1 uses the existing frozen files and the Sonnet review in REVIEW.md. It
preserves the original pipeline, selection, predictions, references, models,
freeze manifests and evaluation outputs. New calculations are Exploratory.

1. Copy the prediction bytes into an owned portable input root; enumerate the
   existing digit NPZ, 60 source crops and nine chart sheets for tracking.
   A supplemental freeze record identifies the evaluator hash retrospectively;
   it does not claim that the evaluator was in the original manifest.
2. Retain 23/60 as the original subjective crop result and separately report
   A=4/20, B=3/20, C=16/20 and the review's objective edge tests, 14/60 and
   21/60 allowing a one-point crossing tolerance. Nine C acceptances fail the
   tolerant audit; eleven fail without tolerance.
3. Every first-endpoint headline carries the 60-row frame: PDF 31–79,
   3,460 of 11,369 detected occurrences; no sorted-section row was selected.
4. All 17 originally rotated pages are upright according to the review.
   Flag their 1,223 occurrences in a separate orientation overlay.
5. Build a subset triage queue using objective margin-edge crossings,
   narrow units at the number edge, incorrect orientation, missing fields,
   unmatched ink and numbered-section order violations. Exclude the universal
   classification/boundary flag and the old minimum-confidence rule. Keep all
   rows quarantined. Use priorities: orientation/complex-column/recall anomaly;
   clipping/fragment/unmatched ink; unresolved field/order; candidate
   cross-section disagreement. Compare detected page counts with the review's
   source counts without assuming every short page should print 72 rows.
6. Write the review's eleven unit-label corrections as an adjudication overlay
   with zero-based unit positions, source locations and original/new sets.
   Do not edit frozen references. The six repeated rows were fixed convenience
   indices, two in each 20-row group; no random-selection algorithm was recorded.
   Recompute calibration on the original same-position labels after excluding
   all three rotated selected rows, with 2,000 row-bootstrap replicates,
   seed 2026100707. Do not refit the model or select a favourable reference.

### Amendment, 7 October 2026: Part 2 design before layout development

Part 2 is Proposed and has not been run. The free-space check found
896,548,864 bytes on C:, below the user's 1,000,000,000-byte stop threshold.
The planned full transcription would write more than 50 MB. Compact Part 1
deliverables proceed; no repaired freeze, new evaluation or full extraction
is represented as completed.

The repair must localize field edges per page/column from source OCR boxes,
checked against print components, and retain an ink-based fallback. Record
offsets and witness conflicts. Determine orientation from readable header /
numeric content and reject unresolved orientation. Discover columns and row
bands without a fixed count, including pages 129–130. Preserve editorial
underlines and reject number-edge fragments. Keep the existing recognizer's
weights, chart and proposal scores unchanged. Freeze new code and parameters
before any new reference.

Draw 80 new rows with seed 2026100780: 28 numbered, 26 end-sorted and 26
beginning-sorted occurrences, excluding development pages and previously
annotated targets. Record section denominators and inclusion probabilities.
Two readers must independently read every selected row, without predictions
or OCR-number strings. Use uncropped chart cells that preserve vertical
position and a convention sheet for codes 2/25, narrow/wide hatching,
underline variants and editorial units. A third source-only reader adjudicates
disagreements before predictions are released for scoring. Preserve both
initial readings and adjudication.

Independently count and match printed rows on 18 seeded pages (six per
section) plus stress pages 62,129,130. Two source readers receive no detected
counts. Report matched-row recall and precision with intervals, separating
the random page frame from the prespecified stress pages. Missing rows must
remain in the denominator. Report the original four thresholds and add 95%
row recall on the random source-count frame, with page-bootstrap intervals.
Report all first-endpoint metrics, intervals and calibration beside the new
endpoint, with their distinct frames and reference conventions.

Proposed confidence release rule, to be confirmed in the new pre-reference
freeze: transcription eligibility requires all global reliability criteria,
resolved upright layout, no objective clipping/continuation/auxiliary ambiguity,
singleton top-one codes, agreement of independent numeric witnesses, minimum
unit confidence >=0.90 and product of unit confidences >=0.90. A qualifying
row can leave transcription quarantine; Package L still requires a reviewed
identity concordance and surface alignment before an object import. All other
rows stay quarantined. No confidence refit may use the new reference.

Before any step writing more than 50 MB, record shutil.disk_usage('C:\\').free.
If below 1 GB, stop that work and record the uncompleted steps. Keep new
follow-up storage under 500 MB. Render one page at a time in memory; retain
only evaluation/review crops. No existing source witness is deleted to free
space. Package L's available contract is HELSINKI-INTERFACE.md plus its dated
review-response amendment; the requested IMPORT_INTERFACE.md is absent.


### Amendment, 7 October 2026: storage resumption before layout development

Free space rose above 1 GB during the compact correction work (see follow-up/2026-10-07/storage-resumption-v1.json). Resume Part 2 under the same per-large-write gate. The preceding statement that Part 2 had not run remains its then-current state. The end-of-run storage-gate.json captured 2.65 GB free but retained stale stop-reason prose; the resumption record corrects that interpretation without replacing the output.


### Amendment, 7 October 2026: unlabelled-frame audit before any new reference

The repair/2026-10-07-v1 candidate was frozen and sampled, but no reference was started or released. Its unlabelled frame showed 125 candidate rows on an ordinary page because glyph-like numeric OCR strings formed extra margin clusters. Preserve this whole candidate as Superseded before evaluation. The replacement copies layout_v2.py to layout_v3.py and restricts ordinary-page OCR field candidates to within 35 PDF points of the documented two-column margin neighbourhoods. Native print features still discover the extra columns on compact end-sorted pages; row counts remain unconstrained. Freeze the replacement and evaluator before its source sample or reference. No v1 candidate accuracy is known.


### Amendment, 7 October 2026: second disk stop after the repaired sample

The pre-frame check found 917,327,872 bytes free and a later check found 256,331,776. The sampling helper had already written its 60,522,244-byte frame and finished before an interruption could take effect. Preserve the completed repaired freeze, 80 predictions, source crops and 21 source-count pages. No fresh reference or evaluation exists. Stop further repair work under the user cutoff; finish the compact correction deliverables. See follow-up/2026-10-07/storage-stop-v2.json for exact remaining steps and the process-control failure.
