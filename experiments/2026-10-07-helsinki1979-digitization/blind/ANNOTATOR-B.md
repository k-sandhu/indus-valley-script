# Annotator B source record

The initial primary reference covers sample indices 20–39, with all 20 selected rows retained. It contains 105 printed drawing units: 86 glyph drawings and 19 editorial auxiliaries. Eight units retain two strict Finnish-code candidates. The primary reference was saved and hashed before the two repeated readings of indices 42 and 51, which contain five drawing units in a separate file.

The observations are an AI visual reference. Confidence labels describe visual judgment. The chart's lower numbers provide Finnish codes; codes and ranks are not converted to another catalogue. Units follow visual left-to-right order in the upright source, with viewing rotation 0 degrees throughout this block. Larger visible gaps are recorded without assigning original line or side boundaries. Original sign counts remain null.

## Source work and crop checks

Before GO, I read the repository instructions, README, knowledge index, writing rules, required registry entries, corpus retrospective, protocol and source definitions, and viewed the nine chart sheets. Selected rows were opened after the parent reported the complete prediction freeze at 2026-10-07T14:20:35Z. I used the supplied source crops, the chart atlas and the unchanged 1979 PDF. No recognition output, other annotator reference or comparison result was opened, and no glyph matcher was queried.

I checked each glyph box by making an exact-box crop from its source context using the supplied PDF coordinates. Wider PDF rendering resolved the printed margins of 24, 25 and 29. Their source rows are labelled 2429, 2559 and 2892. The fixed boxes clip target drawings at the right edge; the supplied context also truncates the margins of 24 and 29. All 20 target rows were present in the source context.

Eleven boxes contain complete glyph bodies. Three boxes, 22, 23 and 31, also retain the target underlines while excluding neighbouring-row and printed-margin ink. The other 17 fail this full-crop criterion. Body clipping occurs in 24, 25, 29, 33, 34, 36, 37, 38 and 39. Missing target underlines occur in 20, 21, 27, 29 and 30. Boxes 27, 34 and 36 include preceding-row underlines, and 20, 26, 28, 32 and 35 admit printed-margin ink. These diagnoses retain small margin intrusions as well as larger drawing losses.

The source drawings include broad damage patches, looped uncertain drawings and narrow end-loss markers. Row 37 is auxiliary-only and remains in the reference. Chart reinspection before the primary file was saved corrected a plain-fish label to 177 and distinguished the central downward stem of 192 from the stemless 581 drawing. Chart metadata checks confirmed the candidate codes against their recorded chart locations. The unresolved choices are the visually compatible tall-three-stroke codes 10/766 and oval-with-angular-arms codes 168/579.

## Blinding limit

The original locator included source-PDF OCR witness fields. I printed its entries 20–39 before viewing their crops. Nonempty witness fields occurred in 22, 26, 27, 29, 30, 31, 37 and 38; the readable 2343 in 22 was noticed before its source image. Other displayed strings were classification fragments or garbled text. After the parent supplied the cleaned locator, subsequent work used `selection-source-only.json`. The number comparison for this block therefore has this source-OCR exposure. The repeated rows 42 and 51 were read from the cleaned locator.

The primary file's pipeline-parameter blinding flag refers to the excluded pipeline implementation and freeze-manifest parameters. Required reading of PROTOCOL.md included its development parameter summaries. Recognition candidates and counts remained withheld.

## Frozen files

| File | SHA256 |
|---|---|
| `blind/reference-b.json` | `7034a77fd87c11ffb0fe4382622bdb4c0c7cff3bd638b5f36f95e086ec4cb2e3` |
| `blind/reference-b-repeat.json` | `5c04c14ea307691be8f5347ad167ba708d683f9782a8b647f90015c6be6e9790` |

Temporary exact-box crops and the three wider context crops are under `data/raw/2026-10-07-helsinki1979-digitization/annotator-b/`. They were rendered or cropped for source inspection, using PyMuPDF 1.28.2 and Pillow. The source is Kimmo Koskenniemi and Asko Parpola's *Corpus of Texts in the Indus Script* (1979), University of Helsinki, source PDF SHA256 `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27`, [official entry](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), CC BY 4.0. No source prose quotations were recorded.
