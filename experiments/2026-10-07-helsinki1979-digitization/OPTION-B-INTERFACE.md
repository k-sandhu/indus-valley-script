# V3 proposals for complete source verification, 8 October 2026

The option-B package consumes the quarantined JSONL named in
[HOST-FILES.txt](HOST-FILES.txt). Its content hash, size, page coverage and row
counts are in [full-summary.json](repair/2026-10-08-v3/full-summary.json).
Keep the proposal file immutable. Record human, independent AI and
adjudicated readings in the verification package's own files, keyed by the
proposal inventory and physical-line occurrence key. Resolve missing lines
and wrong continuation links against the original source as part of the
complete page pass.

There is one record per detected physical glyph line. Each has `pdf_page`
(one-based PDF index), `pdf_column` and `row_index` (zero-based),
`glyph_pdf_box` and optional `margin_pdf_box` in PDF points from the page's
top-left corner. `field_line_boxes_pdf` separates the two field lines.
`occurrence_key` identifies that physical line; `segment_id` is its source
coordinate string. `line_kind` is `numbered` or `continuation`.
`text_occurrence_key` links a continuation to its provisional preceding
numbered line, and `continuation_of` is null on numbered lines. A continuation
inherits its parent's proposed number and has no classification field.
Source ownership remains a review question.

`inscription_number` is a proposed literal string, including any letter
suffix. `classification_code` preserves the recognizer's proposed five
positions. `margin_ocr` and the digit-library fields retain their witnesses.
Neither numerical order nor duplicate text supplies a physical-object join.
Each item in `units` has a source `unit_pdf_box`, up to five ranked
`alternatives` with Finnish lower-code candidate sets and graphic-class
`ranks`, shape costs, a `confidence` and an optional `underline_pdf_box`.
Alternative sets retain inherited chart ambiguities. Unit order is visual
left-to-right within that physical line. For a reviewed numbered occurrence,
concatenate its reviewed lines top-to-bottom while retaining line breaks.

Confidence uses the unchanged original development logistic coefficients.
It has not been recalibrated for v3; the development bins are in
[diagnosis.json](repair/2026-10-08-development-record-v1/diagnosis.json),
`development_summary.calibration`. The completed fresh evaluation reports Brier 0.1117 and ECE10
0.1153 on 315 resolved equal-count positions; see [metrics](repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json),
`summary.calibration`, with stored row-bootstrap intervals. `minimum_unit_confidence` and `confidence_product` summarize that
same fit and confer no release status.

An empty recognition window can produce a non-finite score in the frozen
matcher. The separate [transport manifest](repair/2026-10-08-v3/full-transport-manifest.json)
records post-freeze export handling: those units retain geometry, export
`alternatives: []` and `confidence: null`, and flag the row unresolved. Their
original proposal payloads, with non-finite floats recorded as strings, stay
in the local `invalid-unit-witnesses.jsonl` beside the full output. They need
source inspection before any classification. This handling changes no frozen
evaluation prediction or valid full-run candidate.

`auxiliaries` records detected uncertainty underlines and proposed modern
editorial marker kinds. `boundary_blanks` records observed inter-unit window
gaps with unresolved interpretation. Ancient lost-sign extent and physical
surface identity remain unresolved. `flags`, `quarantined: true`,
`released: false`, `review_status: unreviewed`, the inventory version,
source hash and pipeline-freeze hash accompany every record.

The page inventory counts detections rather than proving complete edition
coverage. Unnumbered lines consisting only of short components can evade the
tall-component continuation detector. Number/field ink and truncated final
drawings remain visible in development targets 27, 53 and 76. The complete
verification package must inspect every source column and add missing-line
records under its own inventory; a review of only emitted proposals would
leave those omissions untested.

The [schema](option-b-schema.json) defines the transport fields. The package
L [contract](../2026-10-07-object-ledger/HELSINKI-INTERFACE.md) accepts
letter-suffixed strings and per-occurrence segment identifiers. Its ledger
shape requires an adapter after verification, plus independently reviewed
carrier and surface concordances. A numbered string and its repetition
supply no such concordance. This task changes no ledger file and imports or
releases no proposal.

Attribution: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus
Script* (1979), University of Helsinki,
[handle](http://hdl.handle.net/10138/342677),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Raster cropping,
numerical proposals and their arrangement are modifications by this project.


## Completed endpoint and package N, 8 October 2026

The fresh v3 endpoint fails four global criteria; all proposals remain
quarantined. The proposal hash and source geometry are immutable. Package N
should consume this inventory under its [contract](../2026-10-08-helsinki1979-row-verification/INPUT_CONTRACT.md),
keeping its own chart-versioned source readings, missing-line additions,
continuation adjudications and release decisions. Its [pilot](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md)
recommends a second screening pilot with v3, clarified coincident-code and
unit-kind conventions and package P's reviewed chart. The two-AI pilot has
not measured or completed the authorized human/expert source check.

Preserve alternative `template_key` values when adapting chart codes. The
four disclosed cell-label differences affect five explicit reference-key
units and 10 top-five proposed units in this sample, across three cells.
The adjudication notes additionally name row 58 unit 0 at 20:4:1 while its
reference records 21:7:5, both labelled 506. Resolve that locator against the
source in the verification record. Never remap repeated code 506 or 206 by a
global numeric substitution. The frozen proposals, cards and scored codes
remain unchanged; corrected mappings enter N's declared vocabulary and a
separately frozen future recognition pipeline. [Cell-use audit](repair/2026-10-08-endpoint-record-v1/diagnosis.json),
`chart_label_audit`, `chart_location_witness_disagreement`.
