# Annotator C source-reading record

The primary reference records all 20 assigned occurrences, sample indices 40–59, with 67 drawn units. The independent repeated reading records samples 5 and 13 with six drawn units. Both files were saved after their complete reading, and the repeated readings do not replace any primary annotation.

| File | SHA256 |
|---|---|
| [reference-c.json](reference-c.json) | `b7a1cf7f66916fa2c5dc1b5e2a6cbe46d7fbee8604407af55b39f7f2c9f6bea7` |
| [reference-c-repeat.json](reference-c-repeat.json) | `d4b005f0727a51b4de099b845fbca4e57057298f9b49d579076a3bfc4b7b28f7` |

## Source and procedure

The drawings come from Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), University of Helsinki, Research Reports 1. The original PDF hash is `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27`. The [official source entry](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/) links CC BY 4.0. The references are derived visual annotations of rendered source crops.

Before selected-row work, I read the repository instructions, README, knowledge index, writing rules, required registry entries, corpus retrospective, package protocol, source definitions and all nine numerical chart sheets. The parent released annotation after the 60 predictions were complete and hashed at 2026-10-07T14:20:35Z. No selected source row was inspected before that release.

I located each selected target by comparing its `glyph_pdf_box` with the supplied context box. I read the printed number and five-position classification directly from the source image, then compared each drawing visually with the chart sheets and individual cells in the existing chart atlas. Units are ordered from visual left to right in the upright source drawing. Every assigned source crop was upright; no viewing rotation was applied. No image matcher or computational nearest-candidate query was used.

The work remained blind to the recognition output, predicted unit counts, pipeline implementation, development files and other annotators' references. Chart-cell checks resolved the small square's plain versus underlined code and verified the plain fish's printed numerical label before the primary reference was saved. A magnified chart-cell inspection sheet was retained locally at `data/raw/2026-10-07-helsinki1979-digitization/annotator-c/chart-square-check.png`.

## Locator OCR exposure

The first locator request printed the original selection records for samples 40–59, including their `ocr_number_witnesses` fields. These were source-PDF OCR witnesses. I noticed number-like strings for samples 43 and 51, and nonmatching or fragmented strings for 42, 44 and 52. The output region covering 49–50 was truncated. Other visible assigned records had empty witness fields. I narrowed subsequent locator reads to coordinates and switched to `selection-source-only.json` when the parent supplied it.

The printed IDs in the reference were read from the source crops. Number readings for the exposed rows therefore have a weaker blinding boundary than the glyph readings. The source OCR exposure did not include recognition candidates or predicted unit counts. No source OCR witnesses were opened for the repeated samples 5 and 13.

## Crop observations and retained auxiliaries

Sixteen primary target boxes contain their target drawing completely without neighbouring marks. Four boxes fail that criterion:

| Sample | Printed ID | Observation |
|---|---|---|
| 43 | 4149 | The lower box edge includes upper horizontal strokes from the following 4150 auxiliary row. |
| 52 | 6153 | The upper box edge includes the preceding 6152B row's dashed underline. |
| 53 | 6174 | The lower box edge clips the lower target tips slightly and excludes the target's dashed underlines. |
| 56 | 8704 | The upper box edge includes the preceding 8703 square's dashed underline. |

The wider supplied contexts preserve the target observations in all four cases. Neighbouring strokes are excluded from the target unit count. The crop decisions concern the declared target box; the wider context deliberately contains parts of adjacent rows.

Ten of the 67 primary drawn units are editorial auxiliaries: combined narrow loss patches, whole-loss rectangles, wide estimated-loss patches, uninscribed-object stacks and a hatched uncertain-sign patch. Samples 41, 44, 50, 55 and 58 are auxiliary-only rows. All are retained. Four uncertainty underlines are recorded across samples 46 and 53 as unit attributes. They do not add to the drawn-unit count.

The references record plotted units and leave original sign counts null. Physical line and side extents are not reconstructed from the printed raster rows. Classification fields retain all five positions, including spaces, and sample 50 retains the printed A suffix.

## Checks and limits

Both JSON files contain every assigned index exactly once. Each drawn count equals the number of retained units, every classification string has five characters, and every selected code is supported by its recorded chart cell. The repeated readings were made after the primary file was saved and without access to A's annotations.

These are AI visual references. Their confidence labels describe visual judgments and are not calibrated probabilities. The initial files preserve the source readings before any comparison with recognition output or other annotators.

