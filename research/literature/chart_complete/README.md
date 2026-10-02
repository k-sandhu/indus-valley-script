# Original 1979 numeric-label audit: PDF20 columns5-9

This independently transcribes all175 occupied cells in zero-based columns5-9 and rows0-34 of original PDF20/printed19. No project OCR labels, matching scores, root templates, expected mappings, or automated glyph recognition were inspected. Inputs were high-resolution crops rendered directly from the primary PDF. Earlier randomly sampled cells overlap this complete transcription; do not count their readings as new independent observations.

Source: Koskenniemi and Parpola1979, `research/corpus/primary/koskenniemi_parpola1979.pdf`, SHA256 `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27`. Source provenance and exact crop geometry appear in `source_manifest.json`.

`manual_numeric_labels.json` and `.csv` preserve each upper rank, lower stable Finnish code, confidence, alternatives, numeric-underlining observations, zero-based coordinates and original-image crop. All175 upper ranks are high confidence.174 lower codes are high confidence. Column7,row22 has best784, alternative764, medium confidence; do not choose between them solely to agree with a predicted mapping. No numeric labels were visibly underlined in these columns. Dashed dividers associated with glyph groups are separate from numeric underlining.

Additional12x original label crops resolved several6/5 ambiguities. Column5,row21 reads469; an initial6x impression459 was corrected from the larger original crop. Column6,row31 reads136. Column8,row4 reads161 and row26 reads176. Column9,row8 reads186, row20 lower186 and row24 upper196. Column7,row22 remains ambiguous even in its zoom crop.

Reproduce crops with `research/literature/chart_label_audit/render_full_pdf20_owned.py`; that first writes them under `chart_label_audit/full_pdf20_columns5_9/`. The identical images are copied here. Serialize manual entries with `research/literature/chart_label_audit/save_full_pdf20_owned.py`; it performs no recognition. The original crop observations remain available for independent re-reading.

**Scope:** numeric label extraction only. These labels do not validate a glyph transcription, ICIT correspondence, historical allograph relation, numerical value, phonetic reading, or meaning.

## Complete independent PDF21 transcription

`full21_audit.json` and `.csv` contain all337 occupied cells of PDF21/printed20:35 rows in columns0–8 and22 in column9. The original chart was read independently at6x resolution, with original12x crops for uncertain labels. The root reference, numeric OCR, templates and predictions were never inspected. The earlier fresh20 sample and earlier30-cell audit remain separate and unchanged; full-chart reconciliation is not a new blind validation set.

The initial independent reference had all337 upper ranks and336 lower codes marked high confidence, with lower c4r22=333 best/533 alternative. Post-comparison original12x reinspection of22 disagreement cells preserves thirteen lower-code ambiguities, including that initial case. All337 upper ranks remain high confidence. No numeric underlining was observed; glyph-group dashed dividers are separate. The source geometry and every original strip are under `full_pdf21/`. Run `render_full_pdf21.py` to render originals and `save_full_pdf21.py` to serialize the manual labels; neither script performs OCR or reads a predicted reference.

Original12x crops resolved column6,row8 as330/367, row9 as331/385, row20 as336/361 and row28 as342/726. Column4,row6 now reads290/436 at12x. Its earlier30-cell audit preserved435 best with436 alternative; this later clarification does not revise the score of that earlier blind audit. The fresh20 sample was available during this full independent reading, so agreement with that sample cannot be counted again as independent validation.

After comparison, `full21_audit_before_adjudication.json/.csv` preserve the initial337 entries. `full21_reconciliation/` preserves original12x crops for the22 cells, without rendered reference/prediction labels. Current c5r34 has205 best,206/208 alternatives after a larger original crop; its initial206 remains unchanged in the saved initial file. Later source reinspection retains5/6 alternatives for c0r1,c0r18,c0r29,c3r2,c3r4,c4r6,c6r9,c6r17,c7r6,c8r5,c9r5. Thus earlier claims that c6r9=385 and c4r6=436 were resolved are superseded by explicit candidate unions. A third reader should receive both candidates and the original source, not an expected mapping. This is a numeric reference audit, not expert glyph gold.

## Fresh PDF21 spot check

`fresh21_audit.json` contains20 newly sampled cells from PDF21/printed20, excluding the earlier15 sampled PDF21 cells. Seed20261013 uses Python `random.Random`, a column-major then row-major eligible frame of322 cells, and sampling without replacement. The full eligible chart has337 occupied cells. No root reference table, predictions, templates or OCR labels were read. `fresh21_sampling_manifest.json` preserves sampling coordinates and original crop geometry; `fresh_pdf21/` preserves the20 source crops and two contact sheets. All20 upper and lower numeric labels are high confidence; none shows numeric underlining. The original12x crops were also inspected for c0r10 (208/703) and c8r33 (387/363). Run `sample_fresh_pdf21.py`, then `save_fresh_pdf21.py`, to reproduce the sampling/crops and serialize the manually entered readings.

## Later duplicate-label source adjudication

`duplicate_labels/adjudication.json` preserves16 original cells checked after the parent flagged duplicate best codes. This is post-comparison source reinspection, not a fresh blind score; all prior337 and175 tables remain in `*_before_duplicate_adjudication` files. PDF21 c8r16 has best63/alternative53; fourteen PDF21 lower codes remain ambiguous. PDF20 c7r25 was corrected363=>383 and c9r19 576=>676. PDF20 c4r1 upper rank was corrected85=>86 from the original24x crop. Two original numeric506 labels remain duplicated; no uniqueness constraint is used. PDF20 c4r21 has reader disagreement465/485/486 and remains uncertain in the cross-reader adjudication file. Initial fresh20 scores remain unchanged.
