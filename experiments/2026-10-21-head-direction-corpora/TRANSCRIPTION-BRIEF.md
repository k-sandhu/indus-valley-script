# Transcription brief for the printed seal lists

Written 21 October 2026 for the agents who transcribe the Basarh, Bhita and Tamil-Brahmi lists. The transcriptions are the record of what each edition prints about each inscribed object. They stay local under `data/raw/2026-10-21-head-direction-corpora/transcriptions/`; tracked files hold only counts, identifiers, page locators and hashes.

## What to transcribe

Transcribe every numbered entry of the list, including entries without a legend, so that the record is complete for every object the editor describes. For each entry record, as printed:

1. the entry number and, for Spooner's list, the register number and every sub-entry (8 A, 8 B);
2. the printed page and the PDF page, and every plate and figure reference given for the entry or for its duplicates;
3. the object: material, shape, dimensions, whether it is a seal die, a ring, a clay sealing or a token, and the string or cord marks the editor reports;
4. the device (emblem) in the editor's words, shortened to at most fifteen words;
5. the legend in the editor's transliteration, character for character, with the editor's diacritics, capitals, hyphens, spaces, brackets and question marks, and the line breaks of the legend where the editor states them (in words such as "in two lines", or by printing the lines separately or numbering them); where the editor gives no line division, record that none is given;
6. the editor's translation of the legend, and any remark that a reading is doubtful, restored from a duplicate, or partly illegible;
7. the date the editor assigns (usually from the letter forms), and any language remark (Prakrit, Sanskrit, mixed);
8. the findspot as printed: trench, square, house, room, stratum, depth and its reference point;
9. the number of impressions or duplicates, the register numbers of the duplicates, and every cross-reference to another collection (Spooner cites Bloch's numbers; Marshall cites Basarh seals);
10. the museum or collection where the editor names one.

## How to read

Read every list page from a rendered page image at 300 dots per inch or more. The Internet Archive OCR text (`_djvu.txt`) is only a draft: its diacritics are unreliable, and every legend, number and findspot must be checked against the image. Where the image itself is unclear, record the best reading, mark the field `uncertain`, and give the reason. Do not complete, correct or modernise a reading from knowledge of Sanskrit, Prakrit or Tamil; a legend the editor prints with an error is transcribed with the error, and a note may say what the editor's own discussion implies. The transliteration convention of each edition is kept exactly; the conversion to IAST happens later in code.

## Output

One JSON object per entry in `transcriptions/<source>.jsonl` with the fields `source`, `entry`, `sub_entry`, `page_printed`, `page_pdf`, `plates`, `object_text`, `material`, `dimensions`, `object_kind`, `device`, `legend_as_printed`, `legend_lines_as_printed` (a list, or null when the edition gives no line division), `line_division_evidence`, `translation_as_printed`, `doubtful`, `restored`, `illegible_part`, `date_as_printed`, `language_note`, `findspot_as_printed`, `depth_as_printed`, `impressions`, `duplicates`, `cross_references`, `museum`, `uncertain_fields` (a list of field names with reasons) and `transcriber`. A per-source `transcriptions/<source>.notes.md` records the page range read, the entries found, the conventions of the edition, every uncertain reading and anything in the list that does not fit these fields.
