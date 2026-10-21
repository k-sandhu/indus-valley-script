# Data changes from the seal-legend unit package

For the maintainers who fold package records into [DATA.md](../../knowledge/DATA.md) and [data/MANIFEST.json](../../data/MANIFEST.json). Folded into DATA.md on 20 October 2026: the Lipi row of section 1, the project registers table, the "Line divisions" and "Images" paragraphs of section 2 and the `faces` row of section 4. The package acquired no new source; it adds face-level fields from viewing the CISI 1 and 2 plate crops already held, and one correction to how the Lipi export's line divisions are read.

## New face-level fields

For the 75 faces of the Lipi export that carry a catalogue line division and have a plate crop, [audit-table.csv](plate-audit/audit-table.csv) records whether the division is confirmed (65 yes, 10 unclear, 0 contradicted), the number of sign groups seen and their counts from the top, where the code's first segment sits on the face (lower line 55, upper line 8, left, right or field 4, undetermined 8), the layout of the second group (wrapped 57, separate 7, other 11), and a confidence. The other 43 divided faces have no crop: 32 carry CISI 3 numbers and 11 have no CISI number. These are AI readings of halftone crops (Claude Opus 5.5, three readers of 25 faces each); a quarter are low confidence. The verdict files are local in `data/raw/2026-10-20-seal-legend-units/plate-audit/`, with their hashes in [audit-summary.json](plate-audit/audit-summary.json).

## Reading order of divided legends

The export's `text_code_visual_ltr` lists the lines of a divided legend in the reverse of the catalogue's reading order, and its `signs_reading_rtl` is the exact reversal of the whole visual code. The reading-order field therefore starts with the line the catalogue reads first, which is the upper line on 43 of the 46 faces placed with high or medium confidence. The three exceptions (H-60, H-97, K-16) read the lower line first. DATA.md and the normalized-file notes should say that the visual code's first segment is the line read last; the structure-first step 3 analysis and the `--local-lines` bench mode treated the line order as unknown and scored both orders.

## Image-index observations

The readers confirmed the identities that the 13 October index had already given to `vol1_page_368_seal_16_no_valid_id.jpg` (C-22 a), `vol2_page_304_seal_7_no_valid_id.jpg` and `_seal_8_` (H-415 a bis and A bis) and `vol2_page_381_seal_4_no_valid_id.jpg` (H-999 A). They reported four points the index does not record:

- `M-663_imp_a.jpg` and `M-663_a_7g.jpg` are byte-identical (SHA-256 prefix `a88e580499da94fb`), so they count as one impression.
- `M-1187_A_M-1183_B_M-1189_a.jpg` is captioned M-1188 and M-1189 on the plate; the name gives the wrong first two keys.
- The crop H-603 (1) a shows a different object from the H-603 (2) seal whose counts match the code.
- M-1202 carries a second inscription on edge C, which belongs to another side of the object.

## Coverage

No object gains an identifier, dimension, findspot or date. Seventy-five divided faces (65 of them confirmed) now have a plate-checked division and, for 46, a plate-checked line order; this is the first face-level layout field in the project's records.
