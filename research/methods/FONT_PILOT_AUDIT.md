# Image-only source-font pilot audit

The independent arithmetic audit of `research/visual_digitization/fresh_font_pilot_corrected/evaluation_all_endpoints.json` passes. The frozen predictions contain ten unique inscription IDs exactly matching the reference, and both recorded SHA256 hashes agree with the current files. A separately implemented dynamic program reproduces every reported candidate-set edit distance, compatible-row count, unit total, and unit-count agreement for all four penalties.

At penalties 0.5 and 1, the ten rows have 61 reference units and 61 predicted units, with the correct unit count on every row. Strict top1 has 15 summed edits and two completely candidate-compatible rows; strict top5 has four summed edits and six completely compatible rows. Excluding the partially disclosed row 1020 leaves 52 units, 11 top1 edits, three top5 edits, and the same two/six whole-row counts. The top1 same-position candidate mismatch count also happens to equal the edit count for these equal-length endpoints. That coincidence does not turn edit distance into a general token-accuracy measure.

Penalty 2 gives 58 predicted units, seven correct row unit counts, 20 top1 edits and ten top5 edits; penalty 4 gives 48 units, one correct row count, 34 top1 edits and 29 top5 edits. Preserving these endpoints prevents reporting only the best pilot penalty.

Correct total or row unit counts do not certify segmentation boundaries. Zero candidate-set edit distance requires matching lengths and ordered nonempty candidate intersections; it does not establish a unique code identity. The reference remains an AI visual comparison to the historical printed chart, with qualitative ambiguity rather than expert gold. The pipeline's top5 is five template alternatives, not an independently normalized probability or calibrated confidence. No duplicate template codes occur in the saved pilot top5 lists, but that fact should be checked for later chart revisions.

The strict reference has four ambiguous units among 61, with at most two codes per unit; shape-only has seven ambiguous units, with at most four codes. Recording these set sizes makes compatibility endpoints easier to assess. The identical strict and shape-only aggregate pilot scores do not independently certify underlining distinctions.

The partial row 1020 disclosure occurred while a source-observed template-crop defect was repaired. Excluding that row does not remove any possible effect of disclosed information on global pipeline choices. These ten rows are a development pilot. A fresh sample evaluated with a frozen penalty and frozen, uncertainty-preserving chart labels supplies the useful subsequent validation.

The evaluator's current ID-count assertion alone would allow duplicate prediction IDs replacing a missing reference row. The saved data do not have that defect: the separate audit verifies unique IDs and exact set equality. A future evaluator should assert both properties directly.

Audit implementation: `src/methods/audit_font_pilot.py`. Output: `results/font_pilot_audit/audit.json`.

## Frozen follow-on twenty-row test

The independent read-only audit of the subsequent source-only twenty-row evaluation also passes. It reproduces the exact seed 20261015 selection from PDF p. 30, columns 0/1, rows 8–34, verifies unique IDs and complete reference coverage, and matches all recorded source/result hashes. Every predicted numeric candidate set equals the retained chart snapshot's set for its image-template key. Thus later chart corrections have not replaced the frozen numeric alternatives in this test.

The prespecified all-20 endpoint, with penalty 1 fixed after development, contains 96 modern drawn units: 91 charted glyph units plus five editorial auxiliaries. It predicts 107 units, with matching row counts on 14/20 rows. Strict top1 has 69 summed candidate-set edits and two whole-compatible rows; top5 has 60 edits and five whole-compatible rows. Shape-only top1 has 67 edits and the same two rows. These are substantially worse acquisition results than the development pilot; they do not establish reliable source transcription.

Top1 here means one image template with mean 1.028 numeric candidates and maximum 3, rather than one uniquely predicted code. Top5 has mean 5.037 candidates and maximum 8 because frozen numeric-label ambiguity is retained. The strict manual reference has ten ambiguous units among 96, with maximum two candidates; shape-only has 16 ambiguous units with maximum four. Every row distance, width and all subset summaries agree with a separately implemented dynamic program.

Excluding every source-classified loss/inaccessibility row leaves 16 rows with 85 charted units, 95 predictions, 11 matching row counts, 62 strict top1 edits and two whole-compatible rows. The poor generalization remains on that sensitivity. It is a sensitivity rather than a replacement primary endpoint. Editorial drawn units and uncertain original lines/sides prevent interpreting the 96-unit denominator as an ancient text-length count.

The frozen endpoint remains unchanged. Implementation: `src/methods/audit_font_fresh20.py`. Output: `results/font_fresh20_audit/audit.json`.

## Acquisition geometry diagnosis and development sensitivity

Subsequent source-image inspection establishes that the frozen pipeline's crop geometry is a major failure component. Corpus's all-20 audit finds top clipping on 18 targets, including 14 clear and four marginal truncations, and following-row ink in 14 crops. Only rows 1023 and 1024 show complete target ink without neighbouring ink. Fixed 40.25-pixel row pitch drifts against approximately 39.6-pixel source spacing at 2x rendering, with column offsets. This makes the failed endpoint a failure of the complete acquisition pipeline; it cannot be attributed purely to glyph-shape generalization. The diagnosis is `../corpus/primary/font_fresh20/geometry_audit/manual_geometry_findings.json`.

A separately labelled post-reference development diagnostic uses the corpus agent's source-only clean vertical bounds. It preserves every original horizontal limit, the exact frozen chart snapshot, image-template library metadata, matcher and penalty 1. Complete new predictions are saved before scoring against already-known reference truth. Original frozen predictions/evaluation/source files are unchanged and their hashes verified.

With clean source geometry, it predicts 96 drawn units, with matching row counts on 18/20 rows. Strict top1 has 24 summed candidate-set edits and six whole-compatible rows; top5 has six edits and 16 whole-compatible rows. Shape-only top1 has 23 edits and the same six rows. Top1 code-set width has mean 1.0625 and maximum 3; top5 has mean 5.198 and maximum 9. The improvement identifies a substantial acquisition geometry problem, while its use of post-reference source inspection prevents treating it as fresh validation or replacing the frozen failure. It still does not establish unique fine-code transcription or original ancient text boundaries.

Implementation: `src/methods/font_geometry_sensitivity.py`. Predictions, hashes, crops and evaluation: `results/font_geometry_sensitivity/`.
