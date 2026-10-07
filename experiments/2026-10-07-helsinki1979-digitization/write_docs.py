"""Write package prose from preserved aggregate endpoints; never change outcomes."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def read(path):return json.loads((HERE/path).read_text(encoding='utf-8'))


def proportion(d):
    return f"{d['success']}/{d['total']} ({100*d['rate']:.1f}%; 95% CI {100*d['ci95'][0]:.1f}–{100*d['ci95'][1]:.1f}%)"


def interval(values,percent=True):
    scale=100 if percent else 1
    return f"{values[0]*scale:.1f}–{values[1]*scale:.1f}%" if percent else f"{values[0]:.3f}–{values[1]:.3f}"


def main():
    metrics=read('evaluation/2026-10-07-frozen-v1/metrics.json');s=metrics['summary'];ci=metrics['row_bootstrap_95']
    full=read('runs/2026-10-07-full-v1/coverage.json');counts=full['counts']
    comparison=read('evaluation/annotation-comparison-v1.json');review=read('review/2026-10-07-v1/summary.json')
    integration=read('integration/2026-10-07-v1/summary.json');interface=read('integration/l-interface-check-v1.json')
    repeat_crop_disagreements=sum(r['primary_crop_correct']!=r['repeat_crop_correct'] for r in comparison['rows'])
    number_without_ocr=metrics['exploratory_sensitivities']['excluding_original_ocr_locator_witness_rows']['inscription_number_accuracy']
    sections=read('section-ranges.json')['sections']
    section_rows={x['section']:sum(p['rows'] for p in full['pages'] if x['pdf_start']<=p['pdf_page']<=x['pdf_end']) for x in sections}
    rotated_pages=[p['pdf_page'] for p in full['pages'] if p['layout']['rotation']]
    zero_pages=[p['pdf_page'] for p in full['pages'] if not p['rows']]
    report=f'''# Helsinki 1979 digitization results

The frozen pipeline failed all four reliability criteria on 60 reserved printed rows. It produced 288 drawing-unit candidates against 267 visually recorded units, with correct counts on 33 rows. Whole-row strict candidate compatibility was 13/60 at top one and 24/60 at top five. The full run attempted all 159 corpus pages and emitted {counts['printed_rows']:,} provisional occurrences with {counts['drawn_unit_candidates']:,} unit candidates. These outputs require source review before use as a reliable corpus. The endpoint is preserved in [metrics.json](evaluation/2026-10-07-frozen-v1/metrics.json), fields `summary` and `negative_result_criteria`; full counts are in [coverage.json](runs/2026-10-07-full-v1/coverage.json), field `counts`.

## Reserved-row results

The source reference has 229 glyph drawings and 38 editorial drawings. Every selected row remains in the evaluation, including auxiliary-only rows. An editorial rectangle or hatched span does not determine an ancient lost-sign count. All 267 drawn units have strict candidate labels; eight units have two candidates. The reference contains 52 rows with singleton codes throughout. These are independent AI visual readings, with original source crops and chart locations in [A](blind/reference-a.json), [B](blind/reference-b.json) and [C](blind/reference-c.json).

| Outcome | Result |
|---|---|
| Initial reference judges crop complete and free of neighbouring/margin ink | {proportion(s['row_crop_correctness'])} |
| Correct drawing-unit count | {proportion(s['drawn_unit_count_agreement'])} |
| Exact inscription number, including suffix | {proportion(s['inscription_number_accuracy'])} |
| Exact five-position classification, including blanks | {proportion(s['classification_exact_accuracy'])} |
| Strict compatible whole row, top one | {proportion(s['strict_top1']['whole_rows_all_sample'])} |
| Strict compatible whole row, top five | {proportion(s['strict_top5']['whole_rows_all_sample'])} |
| Unique exact sequence on singleton-reference rows | {proportion(s['uniquely_resolved_exact_sequence'])} |

Crop decisions themselves have a reference limit: {repeat_crop_disagreements}/6 repeated source checks disagree about crop correctness, although all six agree on target count, number and classification. Small margin intrusions and underlines account for several strict failures. The crop proportion describes initial AI judgments; its binomial interval does not include annotation uncertainty. Each disagreement remains in [annotation-comparison-v1.json](evaluation/annotation-comparison-v1.json), fields `rows[].primary_crop_correct` and `rows[].repeat_crop_correct`. The source examples and qualitative confidence are retained in the [annotator notes](blind/ANNOTATOR-A.md).

Top five means five image templates with retained numeric ambiguity, yielding a mean {s['strict_top5']['candidate_width_mean']:.3f} codes and maximum {s['strict_top5']['candidate_width_max']} in this sample. Strict top one happened to have singleton labels in every prediction; the 16 ambiguous lower-code chart cells remain in the full library. A compatible whole row requires equal counts and ordered intersecting candidate sets. Unique exact sequence further requires singleton predicted and reference sets. Its result is 10/52, so compatibility cannot be presented as authenticated unique transcription.

Strict aligned candidate recall is 199/267 (74.5%, row-bootstrap 95% CI {interval(ci['strict_top1_aligned_recall'])}) at top one and 224/267 (83.9%, CI {interval(ci['strict_top5_aligned_recall'])}) at top five. These values count matching units along a minimum-edit alignment and omit a penalty for extra predicted units. There are 95 and 71 summed candidate-set edits respectively. Same-position accuracy on the 33 equal-count rows is 103/140 (73.6%, CI {interval(ci['strict_top1_same_position_equal_count'])}) and 118/140 (84.3%, CI {interval(ci['strict_top5_same_position_equal_count'])}). The separate denominators are stored under `summary.strict_top1` and `summary.strict_top5`.

The relaxed shape-only endpoint permits underline variants in reference sets and has 15/60 compatible whole rows at top one and 25/60 at top five. It is a secondary comparison; the strict endpoint determines the declared failure. Thresholds were 90% clean crops, 90% numbers, 95% counts and 80% top-five whole rows. None passed.

## Inputs, development and frozen method

The input is Kimmo Koskenniemi and Asko Parpola's *Corpus of Texts in the Indus Script* (1979), Department of Asian and African Studies, University of Helsinki, Research Reports 1. Its unchanged 180-page PDF has SHA256 `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27`. The [official entry](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/) links [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The lower sign-chart number is the Finnish code and the upper number is a rank shared by variants; the source definitions are printed pp.15–17, PDF pp.16–18. The snapshot has 687 chart cells, including 16 ambiguous lower codes. Source/licence observations are recorded in [sources.json](sources.json).

Read registry ROOT-15, ROOT-16, METHODS-font_fresh20_audit and METHODS-font_geometry_sensitivity before this run. Reused resources were the chart labels, existing atlas, source definitions, page-30 fresh20 reference and geometry audit. The crop-library idea and candidate-set edit scoring came from `src/font_pilot.py`, `src/font_fresh20.py`, `src/evaluate_font_pilot.py` and `src/evaluate_font_fresh20.py`. This implementation rewrites the matcher for batched sparse chamfer distances and a small chart-trained CNN; it does not rerun or replace earlier frozen results. The October 6 contribution assessment supplied the bounded corpus-availability context. No new exhaustive precedent search was conducted.

Observed number-field ink bands anchor the vertical rows; nearest intervening blank bands set row edges. Unanchored long glyph bands can create null-number continuation candidates. Horizontal fields still use source-specific normalized regions. The algorithm scores right- and left-margin arrangements and 0/180-degree orientations. The page-37 selection shows the weakness of that score: its three selected source crops were inverted and had to be viewed upright for reference annotation. The predictions retain that orientation error. Source-only column and page geometry therefore remain the main retry requirement.

The recognizer uses all 687 chart crops. Its CNN trains on 147,456 constructed chart examples with affine scale/rotation/translation, stroke-width changes and Gaussian noise. A size-preserving symmetric chamfer distance supplies the principal shape cost; 0.03 times the classifier's negative log probability is added. Dynamic programming groups horizontal ink components with a fixed 1.0 unit penalty and retains unmatched components. Numeric templates come from the known sequential labels on PDF page 30. Tesseract reads digit/letter margin strings as a separate witness; suffix handling and blank classification positions remain provisional. Number-order comparisons are review diagnostics and never force corrected IDs.

Development used PDF pages 20, 21, 22, 25, 30 and 100. Page 80 was overview-exposed and excluded from evaluation. The final page-30 diagnostic has 17/20 correct counts, 6/20 strict compatible rows at top one and 12/20 at top five. The earlier post-reference source-crop repair had 18/20, 6/20 and 16/20 respectively. These development populations and methods do not provide a new generalization comparison. The first new development attempt and the interrupted dense-distance attempt are documented in [RETROSPECTIVE.md](RETROSPECTIVE.md); [trial-01](development/trial-01/page30_evaluation.json) preserves the first endpoint.

[freeze-manifest.json](freeze-manifest.json) records source, implementation, model, numeric-template, chart and calibration hashes plus parameters and environment. It was saved at 2026-10-07T14:10:06Z. Seed 20261007 selected 60 rows without replacement from 3,460 detected rows on PDF pages 31–79, across 33 pages. Row recall outside the detected frame is unmeasured. This frame covers the numbered section and its boundary with the end-sorted section; the remaining end-sorted and beginning-sorted pages have no fresh accuracy estimate. Predictions were complete and hashed at 2026-10-07T14:20:35Z before annotation GO messages; no fresh reference file existed then. [prediction-freeze.json](prediction-freeze.json) records the chronology and hashes. Each annotator owned 20 disjoint rows and two prespecified repeated readings, using source crops and chart images without predictions or a glyph matcher.

## Label exposure and reference disagreements

The original locator included source-PDF `ocr_number_witnesses` in 22 of the 60 rows. All three annotators saw some of those fields before they were removed from a separate [source-only locator](blind/selection-source-only.json). The original frozen locator remains unchanged. The notes specify noticed strings and continued pixel reading; no classifier predictions, glyph candidates or unit counts were supplied. Number accuracy therefore has weaker blinding than glyph accuracy. Excluding every row with a nonempty original OCR locator field gives {proportion(number_without_ocr)} exact numbers on 38 rows. This post-start sensitivity is labelled Exploratory in the [protocol disclosure](PROTOCOL.md) and in `metrics.json.exploratory_sensitivities`.

Six prespecified repeated readings agree on all six counts, numbers and classifications; four have identical compatible ordered strict candidate sets. Samples 30 and 35 have one and two candidate-set disagreements, respectively. Primary references and their hashes remain unchanged. The disagreements require source adjudication; they limit treating the AI reference as expert ground truth. [annotation-comparison-v1.json](evaluation/annotation-comparison-v1.json) preserves both-reading comparisons.

## Confidence calibration

The logistic fit uses 81 equal-count development positions, with 61 candidate-compatible top-one outcomes. Its predictors are top-one shape/classifier cost and the gap to the next candidate, with L2 regularization. Coefficients and fit population are in [calibration.json](development/calibration.json). On 140 resolved same-position units in equal-count reserved rows, Brier score is {s['calibration']['brier']:.4f} (row-bootstrap 95% CI {interval(ci['calibration_brier'],False)}) and ten-bin calibration error is {s['calibration']['ece10']:.4f} (CI {interval(ci['calibration_ece10'],False)}). Reliability bins are `metrics.json.summary.calibration.bins` and the [validation figure](figures/validation.png). These estimates are conditional on count agreement and candidate-set labels; they do not calibrate missing extent, object identity or fine-code uniqueness.

## Full extraction, review and object import

All 159 corpus pages, PDF 22–180, were attempted. The source ranges are 57 numbered-section pages, 52 end-sorted pages and 50 beginning-sorted pages, verified from boundary headers in [section-ranges.json](section-ranges.json). The extraction contains {section_rows['number_order']:,}, {section_rows['end_sorted']:,} and {section_rows['beginning_sorted']:,} occurrences in those sections. It reads some number string on {counts['numbers_read']:,} occurrences and retains {counts['unmatched_units']:,} unmatched units. All pages yielded detected rows. The orientation heuristic selected 180 degrees on {len(rotated_pages)} full-run pages; those values need source review.

[occurrences.jsonl](runs/2026-10-07-full-v1/occurrences.jsonl) contains one record per detected printed occurrence, with source page/column/row, source PDF coordinates, processed orientation, number, unit-local pixel boxes, top-five template codes/ranks/costs, confidence, auxiliary candidates, boundary blanks, classification and flags. Pixel boxes use the oriented 2x crop; `glyph_pdf_box` maps the row to original PDF points. `serialization` is visual left-to-right in the processed crop. An erroneous orientation therefore affects order as well as shape. Physical sides and lost ancient sign counts remain unresolved. Repeated printed numbers are retained and cannot define deduplicated carriers from these outputs.

The frozen baseline review queue contains every row because classification positions require review. A subsequent [priority queue](review/2026-10-07-v1/priority-queue.jsonl) separates {review['counts'].get('priority_0',0):,} unresolved-number/unmatched-ink rows, {review['counts'].get('priority_1',0):,} rows whose minimum drawing-unit confidence is below 0.75 and {review['counts'].get('priority_2',0):,} rows needing remaining field/boundary review. A row without scored units receives a minimum of zero and remains in review. The local compressed PNG row crops support these checks. There are {review['number_order_nonincreasing_pairs']:,} nonincreasing within-column number pairs in the numbered section; no source ID was rewritten from that check. [review summary](review/2026-10-07-v1/summary.json) also compares the digit classifier with Tesseract and original OCR and records repeat-witness consistency, using unverified recognized number groups.

The 1980 *Documentation and Duplicates of the Texts in the Indus Script* provides a Finnish-to-Mahadevan cross-reference table at printed/PDF 27, §2.2.1, explained at p. 24. Four table pairs were inspected. One OCR value disagreed with the source image. The source crop and copied rows remain local because that edition's reuse licence is unverified. No direct CISI/object concordance or local sign-class comparison was completed; exact search locations and the failed first clip are in [concordance-search.json](concordance-search.json).

The [Package L adapter](IMPORT_INTERFACE.md) emits edition-qualified text numbers and occurrence segments with the concrete fields expected by its importer. All {integration['counts'].get('quarantine',0):,} staged rows are quarantined: there is no reviewed object crosswalk, and transcription flags remain. A read-only exercise of Package L's pure importer on 60 staged rows accepted {interface['accepted']} and quarantined {interface['quarantined']}; interface fields, rights and distinct segments passed. The [interface check](integration/l-interface-check-v1.json) records both code and ledger hashes. No Package L file was changed. The frozen restoration model was not supplied these candidates because reliable transcription and a supported inventory/object conversion remain absent.

## Reproduction and remaining work

[README.md](README.md) gives commands for evaluation, selected-row recomputation, full extraction, review, integration and verification. The audit checks frozen hashes, unique sample/occurrence keys, per-row and full-page totals, candidate-set arithmetic and storage. A fresh selected-row recomputation already reproduces all 60 number/classification fields, unit boundaries and top-five template candidates, with confidence differences below 1e-6; see [sample-rerun-v1.json](verification/sample-rerun-v1.json). Artifact paths, sizes and hashes are enumerated in [file-manifest.jsonl](file-manifest.jsonl); existing source inputs are recorded in [sources.json](sources.json).

The completed part is a frozen negative evaluation, a full provisional extraction, independent source references and a quarantined import interface. A reliable complete coded corpus, expert adjudication of the references, complete auxiliary/boundary recovery, verified carrier identifiers and an external sign-class comparison remain unfinished. A retry needs per-page horizontal-field localization, an orientation check independent of two-line numeric geometry, source-preserving underline bounds, and a fresh reference made after freezing those repairs.
'''
    readme=f'''# Package M: Helsinki 1979 digitization

The new pipeline failed its 60-row frozen test: 23/60 clean crops, 33/60 matching unit counts, 23/60 exact inscription numbers, 13/60 strict compatible whole rows at top one and 24/60 at top five. All four reliability criteria failed. The package contains {counts['printed_rows']:,} provisional printed occurrences and {counts['drawn_unit_candidates']:,} unit candidates from all 159 corpus pages, plus source references and a review queue. These files do not yet supply the reliable complete corpus sought by this package.

The [report](REPORT.md) gives intervals, calibration, crop and reference disagreements, and label-blinding limits. Exact outcomes are [metrics.json](evaluation/2026-10-07-frozen-v1/metrics.json), field `summary`; extraction totals are [coverage.json](runs/2026-10-07-full-v1/coverage.json), field `counts`. The primary reference has 267 drawn units, including 38 editorial units. Number accuracy after excluding all 22 source-OCR-exposed locator rows is 13/38. Six repeated visual readings agree on counts and printed fields; four agree on ordered strict candidate sets, and crop judgments disagree on four. Initial references remain unchanged.

## Files and source attribution

[PROTOCOL.md](PROTOCOL.md) records the pre-outcome plan, freeze and subsequent disclosure. [freeze-manifest.json](freeze-manifest.json), [prediction-freeze.json](prediction-freeze.json), [chart-snapshot.json](chart-snapshot.json), `development/` and `blind/` retain the frozen dependencies and independent annotations. The CC BY derived extraction is [occurrences.jsonl](runs/2026-10-07-full-v1/occurrences.jsonl). The [priority queue](review/2026-10-07-v1/priority-queue.jsonl) links to compressed local row crops; all rows retain field/boundary review requirements. [IMPORT_INTERFACE.md](IMPORT_INTERFACE.md) and [staged rows](integration/2026-10-07-v1/ledger-import.jsonl) preserve source-qualified identities. All {counts['printed_rows']:,} staged rows remain quarantined, with zero verified external object joins. [RETROSPECTIVE.md](RETROSPECTIVE.md), [sources.json](sources.json) and [registry-entry.json](registry-entry.json) complete the record. [validation.png](figures/validation.png) plots the reserved row outcomes and conditional calibration.

Source: Kimmo Koskenniemi and Asko Parpola (1979), *Corpus of Texts in the Indus Script*, Research Reports 1, Department of Asian and African Studies, University of Helsinki. [Persistent handle](http://hdl.handle.net/10138/342677), [institutional licence witness](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Chart crops, evaluation crops, annotations and transcription are source-derived changes made here. Retain the title, authors, source URL, licence and modification notice with those assets. Our new code/prose have no separately assigned blanket licence. The 1980 PDF, extracted text, source crops and copied crosswalk rows stay in local raw because its licence is unverified.

## Run from the repository root

The existing interpreter is `C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe`. The freeze records exact recognition-package versions; the [interface check](integration/l-interface-check-v1.json) records the later schema-check dependencies. This package installed PyMuPDF, OpenCV and jsonschema with its four dependencies using `pip --no-cache-dir`; NumPy, SciPy, Pillow, PyTorch, Tesseract and plotting support were already available. `pipeline.py` uses the saved chart-trained weights and calibrated coefficients. TMP, TEMP and MPLCONFIGDIR are under the local raw directory.

Use new output paths on every repeat. These commands recompute from preserved inputs without replacing frozen endpoints:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate.py --out experiments/2026-10-07-helsinki1979-digitization/evaluation/reviewer-recompute
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/rerun_frozen_sample.py --predictions-out data/raw/2026-10-07-helsinki1979-digitization/reviewer-sample-v2.json --audit-out experiments/2026-10-07-helsinki1979-digitization/verification/reviewer-sample-v2.json
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/verify.py --out experiments/2026-10-07-helsinki1979-digitization/verification/reviewer-v2.json
```

The selected-row recomputation processes only 60 rows and already passed. A full repeat costs about {full['seconds']/60:.1f} minutes on this environment and creates another payload plus compressed crops; check the local storage limit before repeating it:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' experiments/2026-10-07-helsinki1979-digitization/pipeline.py full --out experiments/2026-10-07-helsinki1979-digitization/runs/reviewer-repeat
```

The original development/freezing/selection commands were `pipeline.py develop`, `pipeline.py freeze` and `pipeline.py sample`. Do not run `develop` over this frozen package: it rewrites dependencies. Develop a subsequent dated experiment instead. Freeze/sample commands refuse existing endpoints.

Other rerunnable scripts are `build_review_queue.py`, `prepare_import.py`, `check_ledger_interface.py` and `compare_annotations.py`, each with `--out` for a new owned directory/file. `review_package_prose.py` captures the required root prose scan and input hashes in [prose-review-v1.json](verification/prose-review-v1.json). `plot_results.py` regenerates the derived figure; `write_docs.py` regenerates prose from aggregate outputs. `inventory_files.py` updates the derived [file manifest](file-manifest.jsonl) and [inventory totals](file-manifest-summary.json). The [final verification](verification/2026-10-07-v1.json) records input checks and storage, including installed dependency bytes. The file manifest enumerates every created package/raw asset and installed distribution file. No shared registry, index, manuscript, history or other package was edited.

Reviewer checks: repeat evaluation and the 60-row computation; sample exact glyph boxes against wider source context, especially indices 14–16, 24, 29, 30, 35, 42 and 51; adjudicate the two repeated glyph disagreements and four crop disagreements; inspect number suffixes, classification blanks and auxiliary units; confirm all staged rows remain quarantined without an inspected object concordance. Run `python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write`.
'''
    retrospective=f'''# Retrospective: Helsinki 1979 digitization

The complete new pipeline failed its reserved-row evaluation and left {counts['printed_rows']:,} provisional occurrences for review. All 159 corpus pages were processed. The fixed 60-row endpoint has 33 matching counts and 24 strict top-five compatible whole rows; source number and crop judgments pass on 23 rows each. The [report](REPORT.md) and [metrics](evaluation/2026-10-07-frozen-v1/metrics.json) preserve the results and uncertainty.

## Approaches and observed changes

The repository registry and corpus retrospective identified fixed row-pitch drift as the earlier failure. The new method anchored vertical rows to observed two-line numeric fields and chose intervening blank gaps. It reused the numerical chart, atlas, source definitions, known page-30 reference and previous scoring concepts. It added chart-only CNN augmentations, size-preserving chamfer costs, numeric templates and a development confidence fit. It did not replace the earlier failed or post-reference endpoints.

The first development matcher normalized templates into square canvases and added a larger learned-model cost. Its predictions and evaluation are preserved under `development/trial-01/`. Development comparison prompted a return to source-size-preserving chamfer distances with a small learned-model contribution. A dense distance implementation was slow and its development process was deliberately interrupted. Sparse template-ink indexing reduced repeated array allocation. Final development had 17/20 correct counts and 6/20 and 12/20 compatible rows at top one/five. No reserved reference existed during these changes.

Source overview inspection showed three printed arrangements. Page 100 was added to development to correct the left-margin field locator. The overview had included page 80, so that page was excluded from selection before a reference existed. Source headers later verified section ranges 22–78, 79–130 and 131–180. These source navigation records remain separate from reconstructed object identity.

Numeric templates trained on page-30 known labels recovered many fields that Tesseract read as 1923 instead of 1023 during development. This improvement did not generalize to the reserved population: the final number score is 23/60. Static horizontal field regions still clipped numbers and target drawings on shifted pages. The 0/180 orientation score inverted three selected page-37 crops. The source readers viewed those drawings upright and preserved the resulting errors in the frozen comparison. Neither number order nor repeated number consistency was used to force IDs.

## Annotation challenges and preserved failures

Predictions were frozen before three annotators received GO. Each read 20 disjoint source rows and two repeated rows without glyph candidates or predicted counts. Exact-box source checks exposed underlines omitted from target crops, clipped rightmost drawings, printed-margin leakage and adjacent-row ink. Wider source context allowed all 60 targets to be read, but only 23 initial crop judgments passed. Four of six repeated crop judgments disagree, so that proportion retains a qualitative reference limit. Counts, numbers and classifications agree in all six repeats; strict ordered candidates agree in four. Expert adjudication remains required.

The original locator unexpectedly contained source-PDF OCR witnesses. All three annotators saw some label-like strings. The frozen locator was preserved, a filtered copy was supplied, and each annotator disclosed exposure. Number accuracy has this blinding limit. Excluding all 22 rows with nonempty source OCR fields yields 13/38 correct numbers; glyph candidates and counts remained withheld throughout. The primary references were never edited after comparison.

Recognition and calibration were evaluated separately from row acquisition. The primary sample has 267 modern drawing units, including 38 editorial units. Aligned top-five recall reaches 224/267, while whole-row compatibility is 24/60 because counts, order and every candidate intersection must agree. Calibration on 140 equal-count positions has Brier score {s['calibration']['brier']:.4f} and ten-bin error {s['calibration']['ece10']:.4f}; it cannot qualify the many rows with wrong counts or identities. The selected-row recomputation reproduced all 60 frozen fields, unit boundaries and top-five candidates.

## Concordance, rights and integration

The four inspected entries in the local 1980 documentation link Finnish text numbers to Mahadevan numbers. A CISI/object join remains unverified. An initial source clip truncated destination digits and was retained as a failed inspection; a wider 4x crop resolved four pairs and one OCR disagreement. Raw text, source crops and copied mappings stayed local because the 1980 licence is unverified. No direct object join or external sign-class comparison was completed.

Package L's actual importer became available during this run. The adapter was matched to its required fields, source-qualified segments and exact rights spelling without changing any Package L file. The first interface attempt failed because jsonschema was absent, without writing an endpoint. Installing it and its four dependencies inside the authorized environment enabled the repeat. The failure log remains in local raw. Its pure importer was tested on 60 staged occurrences with an empty crosswalk: zero accepted, 60 quarantined. The full staging payload contains {counts['printed_rows']:,} quarantined occurrences. Repeated sort appearances remain separate witnesses.

PyMuPDF, OpenCV and the schema-check dependencies were installed without a pip cache inside the authorized environment. Pages were rendered in memory; source contexts, selected crops and compressed row crops are retained inside the two owned directories. The audit counts installed distribution bytes as well as package/raw assets against the 500 MB allowance. Source-derived 1979 assets retain CC BY 4.0 attribution. No PDF was redownloaded, no public release was made and no repository history or shared research file was changed.

## Remaining work

The next method needs per-page horizontal-field localization and an independent orientation check, plus glyph bounds that retain editorial underlines while excluding margin ink. It must freeze those changes before a new reserved reference. The references need expert source adjudication, particularly samples 30/35 and crop decisions 5/13/42/51. A reviewed edition-to-object concordance and source-surface alignment are required before importing carrier identities or comparing the local corpus. The reliable complete transcription remains unfinished.
'''
    entry=dict(id='M-2026-10-07-helsinki1979-digitization',theme='licensed corpus font digitization',status='Failed',
        question='Can observed row geometry and chart-trained recognition provide a reliable complete Helsinki 1979 transcription?',
        outcome=f'Frozen 60-row evaluation: 23 clean crops, 33 correct unit counts, 23 correct numbers, 13/60 strict top-one and 24/60 top-five compatible whole rows. Full provisional extraction: {counts["printed_rows"]} occurrences, {counts["drawn_unit_candidates"]} candidate units across 159 pages. All reliability criteria fail; all staged rows quarantined.',
        challenge='Static horizontal fields, orientation scoring, clipped underlines/units, margin leakage, source OCR exposure in locator and visual-reference disagreements.',
        remedy='Preserved frozen implementation/predictions/references; source-only locator copy and exposure sensitivity; complete provisional extraction; priority review; quarantined Package L interface; selected-row recomputation and source/hash/count audits.',
        evidence=['experiments/2026-10-07-helsinki1979-digitization/PROTOCOL.md',
                  'experiments/2026-10-07-helsinki1979-digitization/evaluation/2026-10-07-frozen-v1/metrics.json',
                  'experiments/2026-10-07-helsinki1979-digitization/evaluation/annotation-comparison-v1.json',
                  'experiments/2026-10-07-helsinki1979-digitization/runs/2026-10-07-full-v1/coverage.json',
                  'experiments/2026-10-07-helsinki1979-digitization/verification/2026-10-07-v1.json'],
        retry_when='New per-page field/underline/orientation procedures are frozen before a fresh reference; expert chart/source adjudication and an inspected object/surface concordance become available.')
    for name,text in [('REPORT.md',report),('README.md',readme),('RETROSPECTIVE.md',retrospective)]:
        (HERE/name).write_text(text,encoding='utf-8')
    (HERE/'registry-entry.json').write_text(json.dumps(entry,indent=2),encoding='utf-8')


if __name__=='__main__':main()
