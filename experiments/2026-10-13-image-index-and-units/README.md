# Face-level image index and dimension units audit, 13 October 2026

Package `image-index-and-units` of data round 1, answering question cards [Q-1004](../../knowledge/questions/Q-1004-face-level-image-index.md) and [Q-1020](../../knowledge/questions/Q-1020-dimension-units-audit.md). Protocol [PROTOCOL.md](PROTOCOL.md), hashed before computing ([PROTOCOL.sha256](PROTOCOL.sha256)), with [Amendment 1](AMENDMENT-1.md) (caption check of every file name, name corrections, aliases) and [Amendment 2](AMENDMENT-2.md) (the ordinal side rule withdrawn after the targeted check). Status: verified computation on hash-checked local inputs, with visual readings of printed captions by an AI model (Claude Opus 5.5).

## Results

### Images

Every one of the 8,722 local Lipi crops now has a record with its hash, parsed name, CISI volume and, for 97% of links, the PDF and printed page of the plate it was cut from ([image-files.csv](run-2026-10-13/images/image-files.csv)). Every face of `lipi_observed_faces.jsonl` is linked to the files that show its object, with the kind of view and the side relation ([face-image-links.csv](run-2026-10-13/images/face-image-links.csv), 8,444 links), and the 2,677 faces without any image are listed with the reason ([faces-without-image.csv](run-2026-10-13/images/faces-without-image.csv)).

The share of objects with any image changes little, from 53.4% to 54.6% (2,509 to 2,562 objects; faces 51.9% to 52.9%). What changes is the kind of image. The Lipi index lists 6,570 files, and for seals more of them are impressions than photographs (1,777 against 1,266 seal links); most of the 2,152 files outside it are photographs of one side of an object, 1,780 of them named in the form `M-12_A.jpg`. Counting only the indexed files, 17.6% of objects (seals 10.5%) have a photograph of the object's own inscribed side; with all files it is 46.0% (seals 68.3%). For faces the same measure rises from 846 to 2,181 (14.9% to 38.4%). These face-side figures count objects with one face row, whose face is presumed to be on side A, and 21 objects with several faces whose sides were verified by viewing. For the other 881 objects with several faces the index links every file to every face and leaves the side open (Amendment 2); 383 of the 902 objects with several faces have files showing at least as many distinct sides or numbered inscriptions as the object has faces.

| Group | Objects | Any image, inventory rule | Any image, this index | Object photo of the face side, Lipi index files only | Object photo of the face side, all files | Impression of the face side, all files | Several faces: objects / with enough views |
|---|---:|---:|---:|---:|---:|---:|---:|
| All objects | 4,695 | 53.4 | 54.6 | 17.6 | 46.0 | 31.7 | 902 / 383 |
| Seals | 2,239 | 69.5 | 70.4 | 10.5 | 68.3 | 65.4 | 37 / 29 |
| Tablets, bas-relief | 709 | 50.8 | 51.3 | 28.5 | 29.8 | 1.1 | 382 / 156 |
| Tablets, incised | 527 | 33.8 | 34.0 | 6.6 | 7.8 | 1.9 | 390 / 145 |
| Tablets, copper | 190 | 88.4 | 88.4 | 71.6 | 72.1 | 0.0 | 40 / 36 |
| Tags and sealings | 213 | 43.2 | 46.9 | 34.7 | 37.6 | 0.5 | 33 / 7 |
| Pottery | 630 | 16.8 | 18.9 | 16.5 | 18.1 | 0.0 | 6 / 4 |
| Other | 187 | 26.7 | 29.4 | 20.3 | 24.6 | 2.7 | 14 / 6 |
| Harappa | 1,921 | 42.6 | 43.2 | 13.2 | 28.6 | 17.4 | 750 / 286 |
| Mohenjo-daro | 1,795 | 73.8 | 74.8 | 22.4 | 69.7 | 53.4 | 107 / 83 |
| Dholavira | 230 | 0.9 | 0.9 | 0.4 | 0.9 | 0.9 | 7 / 0 |
| Kalibangan | 197 | 42.6 | 42.6 | 13.2 | 37.6 | 26.4 | 9 / 4 |
| Lothal | 182 | 90.1 | 94.0 | 41.8 | 86.3 | 46.7 | 18 / 6 |
| Chanhu-daro | 72 | 45.8 | 50.0 | 11.1 | 48.6 | 38.9 | 2 / 1 |
| 72 other sites | 298 | 28.2 | 32.9 | 19.5 | 30.2 | 9.7 | 9 / 3 |

Percentages of objects; source [coverage.csv](run-2026-10-13/images/coverage.csv), which also gives face-level figures. Tablets score low on the face-side columns because most have several faces, whose sides are left open.

Of the 2,677 faces without an image, 661 have no CISI number (228 of Dholavira's 230 objects among them) and 2,016 have a CISI number for which no crop exists. Of these, 1,926 lie beyond the numbers that CISI 1 and 2 cover (Harappa above H-1019: 1,378; Mohenjo-daro above M-1659: 410; Kalibangan above K-122: 101; Chanhu-daro above C-50: 37), so their photographs belong to CISI 3 or to excavation reports. In the other direction, 1,838 files show 844 catalogue numbers that have no Lipi face, which gives Q-1007 (the 1,032 CISI entries the census found unmatched) a photograph to inspect for each of them, and 68 volume/page files show no readable caption.

**Name check and corrections.** Each crop carries its printed CISI caption, so every file name could be checked against it. Tesseract found the file's own key in the caption of 6,152 of the 8,465 files named by key; in 182 it read a different key. Viewing those 182 showed that most were OCR digit errors, but 23 file names name the wrong object, for example `H-502_B.jpg` (caption H-902 B), `M-500_A (1).jpg` (M-900 A), `L-19_A_1-3.jpg` (L-190 A 1-3), `K-823_B.jpg` (H-823 B) and `AL-18_A_1_LV_.jpg` (Kd-16 A (1)). They are corrected in [name-overrides.tsv](name-overrides.tsv), together with three names whose object is right: `His-1_A.jpg` (Hls-1), `Ad-8_ma.jpg` (caption Ad-8 aa) and `H-795_B.jpg`, whose crop also shows H-800 F. Eight files with I written for l in the prefix (`DIv`, `BIk`, `DIp`) are joined to the corrected key, and the CISI 1 numbers Amri-1 and Amri-2 are joined to Lipi's Ai-1 and Ai-2 through CISI 2's own cross-reference ([key-aliases.tsv](key-aliases.tsv)). The 299 files named by volume and page were read on contact sheets: 231 carry a legible caption naming 273 views of catalogue objects, among them the unknown-provenance seals ?-1 to ?-6 of CISI 2, and 182 of these files now link to Lipi faces ([volpage-readings.tsv](volpage-readings.tsv)). The page in their names is the PDF page of the scan: `vol1_page_297` shows L-99 C, which stands on PDF 297 (printed 261).

**Precision.** A random sample of 60 links was viewed with the printed captions: 60 show the linked object (Wilson 95% interval 94.0–100%), 60 have the stated kind, and 58 of 59 decided links have the stated side relation. A sample of 15 links from corrected names, aliases, several-object crops and caption-read files had 15 of 15 right on identity. All 52 sampled links from single-face objects had the right side. The ordinal rule for objects with several faces was right in 34 of 40 decided links (15 of 18 in its targeted sample), which is why it was withdrawn ([verification-results.json](verification-results.json), [verification-verdicts.csv](verification-verdicts.csv)).

**Pages.** The CISI 1 and CISI 2 scans were read with tesseract; running headings and captions place 3,664 catalogue keys on plate pages ([key-pages.csv](run-2026-10-13/pages/key-pages.csv)). The PDF page minus the printed page is 36 in CISI 1 and 35 in CISI 2, matching the plate-check package's locators (L-161 on PDF 312, M-895 on PDF 120). Twenty-one files form eight groups of byte-identical files.

### Dimensions

The Lipi fields `h`, `v` and `th` are not an inch field. They hold the value as recorded, in whichever unit the record used, and the millimetre fields are its conversion. Of the 17,040 face-axis values, 6,656 are empty or zero, 5,643 were recorded in inches, 4,250 exist only in millimetres with no recorded unit, 389 were recorded in millimetres and 102 in centimetres, most of these without a unit in the string (`24.63(ext)`, `2.85`). The millimetre value reproduces the recorded value exactly (within 0.05 mm of the conversion rounded to 0.1 mm) for 5,285 inch, 292 millimetre and 97 centimetre values; 23 more are rounded, and 15 disagree ([conversion-mismatches.csv](run-2026-10-13/dimensions/conversion-mismatches.csv)). The data inventory's 228 inch–millimetre "mismatches" are 180 values recorded in millimetres, 42 recorded in centimetres and 6 true mismatches.

| Unit of record | Values | Precision of the record | Millimetre value is a conversion |
|---|---:|---|---|
| Inch | 5,643 | 0.1 in (2.54 mm): 2,295; 0.01 in (0.25 mm): 3,298; 1 in: 37; 0.001 in: 13 | exact 5,285, rounded 19, mismatch 13 |
| Millimetre, only the millimetre field filled | 4,250 | 1 mm: 2,501; 0.1 mm: 1,749 | not applicable |
| Millimetre, in the recorded field | 389 | 0.01 mm: 331; 0.1 mm: 28; 1 mm: 30 | exact 292, rounded 3, mismatch 1 |
| Centimetre | 102 | 0.1 cm: 86; 0.01 cm: 9; 1 cm: 7 | exact 97, rounded 1, mismatch 1 |
| None (empty or zero) | 6,656 | | |

The precision is that of the digits as stored. Two-decimal inch values are not hidden fractions of an inch: 23.5% fall within rounding of a sixteenth, against 20.0% expected by chance, and 27.4% equal a whole millimetre converted, against 25.4% by chance. Millimetre-only values are not lost inch conversions either: those with one decimal sit on the 0.1-inch grid at 5.2% (chance 4.0%) and on the 0.01-inch grid at 40.1% (chance 40.2%) ([summary.json](run-2026-10-13/dimensions/summary.json), `grid_tests`).

**Older website export.** Its `SEALID` equals the Lipi family number for 2,540 of 2,543 records (same CISI key or both empty), and its sizes are millimetres stored as `FLOAT`. Axis by axis, 2,340 objects agree on every comparable axis and 9 disagree. Twenty more give for thickness the lower end of a Lipi range such as `5 - 9`. The inventory's 206 disagreeing objects are 199 objects whose Lipi thickness is a printed range, which its rule did not read as a number, 3 where one source has a zero, and 4 with different values ([website-disagreements.csv](run-2026-10-13/dimensions/website-disagreements.csv)). Seal C-1 shows the pattern of a replaced measurement: the website holds the conversions of the recorded inches (51.3, 37.8, 2.5 mm) while Lipi's millimetre fields hold 50, 52.8 and 15.5. Mayig's corpus files carry no size field.

**Flags.** Besides the 6,656 empty or zero values, the [dimension table](run-2026-10-13/dimensions/dimension-table.csv) flags 421 recorded values with no millimetre conversion, 291 millimetre values in the recorded field, 97 extant (`(ext)`) measurements of fragments, 82 thickness ranges with a zero lower end, 137 single values set against a range or the reverse, 8 values over 150 mm or 1,000 mm, 5 inch readings of values that only make sense in millimetres, and smaller groups of uncertain, estimated, reversed or malformed strings. Faces of one object never differ on a size.

**Seals in the October 12 split.** Rebuilt with Shot A's own code and the frozen split, without touching its confirmation log ([split-counts.json](run-2026-10-13/dimensions/split-counts.json)):

| Half | Population | Seals | Both face sizes from inches | Both rounded to 0.1 in | At least one rounded to 0.1 in | Recorded in mm, no unit (whole mm) | mm or cm in the recorded field | Mismatch or website disagreement |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Discovery | Shot A size-text population, one per component | 590 | 432 | 135 | 200 | 129 (76) | 28 | 1 and 3 |
| Confirmation | same | 582 | 434 | 146 | 219 | 122 (82) | 26 | 1 and 3 |
| Discovery | all seal families with usable size | 742 | 536 | 173 | 256 | 168 (97) | 37 | 1 and 3 |
| Confirmation | same | 731 | 535 | 180 | 268 | 158 (110) | 38 | 2 and 3 |

Shot A's exploration counted 460 inch and 130 millimetre seals in the discovery half because it flagged every non-empty recorded field as inches; 28 of those 460 were recorded in millimetres or centimetres. The halves carry the same mixture, so a size contrast within a half is not driven by a unit imbalance between halves, but in each half about a third of the seals have at least one face size known only to 2.54 mm and about a quarter have both, and in each half 21 to 39 seals have a face side of exactly 25.4 mm, one inch.

## Method

Part 1 follows the protocol and Amendment 1. [build_index.py](build_index.py) hashes and parses every file name with the CISI 1 conventions for side letters, impressions (lower case), numbered inscriptions, parts in parentheses and extra photographs (`bis`, `ter`), adds the captions read on the volume/page files and the name corrections, places each key on a volume and page from [page_index.py](page_index.py), and links faces. [crop_ocr.py](crop_ocr.py) and [cisi_pages.py](cisi_pages.py) produce the local OCR text. [contact_sheet.py](contact_sheet.py) makes the sheets that were viewed, and [verify.py](verify.py) drew the samples with a fixed seed and scores the recorded verdicts. Part 2 is [dimensions.py](dimensions.py): each recorded string is parsed for numbers, ranges, unit suffixes and markers, its unit is the factor (25.4, 10 or 1) that maps it to the millimetre field within 0.051, 0.51 or 0.6 mm, and the website export is joined by `SEALID`.

```text
python -P experiments/2026-10-13-image-index-and-units/cisi_pages.py
python -P experiments/2026-10-13-image-index-and-units/crop_ocr.py --workers 14
python -P experiments/2026-10-13-image-index-and-units/page_index.py --out experiments/2026-10-13-image-index-and-units/run-<date>/pages
python -P experiments/2026-10-13-image-index-and-units/build_index.py --out experiments/2026-10-13-image-index-and-units/run-<date>/images
python -P experiments/2026-10-13-image-index-and-units/dimensions.py --out experiments/2026-10-13-image-index-and-units/run-<date>/dimensions
python -P experiments/2026-10-13-image-index-and-units/verify.py score
```

`build_index.py` reads the page index from `run-2026-10-13/pages/`; point `PAGE_INDEX` at a new run to rebuild from fresh OCR. The scripts run with `python -P` rather than `-I` because Pillow is installed in the user site; `-P` still keeps the script and working directories off the import path. OCR output, contact sheets and development runs are local in `data/raw/2026-10-13-image-index-and-units/`.

## Sources and licences

| Source | Used for | Licence or rights status |
|---|---|---|
| Lipi export, commit `fc8813a`: `data/normalized/lipi_observed_faces.jsonl` (SHA-256 `1220f559…`), `seal_id_and_image_mapping.json` (`8069120d…`), 8,722 crops in `data/lipi/public/seal_images/` | faces, sizes, image files | No licence at the pin (`knowledge/provenance/REDISTRIBUTION.md`); crops reproduce CISI photographs |
| Older Indus website export, commit `2434249`: `data/normalized/indus_website_observed.jsonl`, `data/indus_website/population-script.sql` | sizes, join | GPL-3.0 repository (`data/indus_website/LICENSE`); data coverage unresolved |
| Mayig corpus, commit `ad2f1e2` | checked for size fields | MIT, Michael Carlson 2024 (`LICENSES/Mayig-MIT.md`) |
| Joshi and Parpola 1987, *Corpus of Indus Seals and Inscriptions. 1. Collections in India* (`research/literature/sources/joshi_parpola_1987_cisi1.pdf`) | conventions (printed pp. XXIV–XXV), page index | Copyright 1987 Finnish Academy; local only |
| Shah and Parpola 1991, *Corpus of Indus Seals and Inscriptions. 2. Collections in Pakistan* (`cisi2-archive.pdf`) | page index | Copyright 1991 Finnish Academy; local only |
| Evidence census `catalogue-coverage.csv`; October 12 split and Shot A code | volume ranges, Amri alias; split counts | Project outputs |

No network access was used. Tracked outputs hold file names, hashes, identifiers, parsed fields, joins, page locators, counts and the reader's judgements; images, OCR text and page renders stay local. The dimension table and mismatch lists carry record-level size values from Lipi, which has no licence. They are outside the project's CC0 dedication in the same way as the object ledger's attributed metadata, and whether they stay tracked is listed for the coordinator below.

## Limits

The visual readings are an AI model's readings of halftone crops; caption reading is reliable at the sizes used, while the sign counts used to judge sides are approximate, and sides were settled only where the two faces' counts differ. The page index rests on OCR of headings and captions and places 3,664 of the catalogue keys; a key it misses has a volume but no page. The 2,087 key-named files whose caption OCR could not read (1,957 with text but no key, 130 with no text) keep their file-name key, and the random sample bounds their error rate rather than checking each. The dimension audit establishes the unit and precision of each stored value and the agreement between two derivatives of the same upstream records; it does not check any value against the objects, because CISI 1 and 2 print no sizes ("the actual measures of the objects will be listed separately in the third volume", CISI 1 printed p. XXV).

## Files

[PROTOCOL.md](PROTOCOL.md), [PROTOCOL.sha256](PROTOCOL.sha256), [AMENDMENT-1.md](AMENDMENT-1.md), [AMENDMENT-2.md](AMENDMENT-2.md), scripts listed under Method, [volpage-readings.tsv](volpage-readings.tsv), [name-overrides.tsv](name-overrides.tsv), [key-aliases.tsv](key-aliases.tsv), [verified-sides.tsv](verified-sides.tsv), [verification-sample.csv](verification-sample.csv), [verification-verdicts.csv](verification-verdicts.csv), [verification-results.json](verification-results.json), `run-2026-10-13/` (`pages/`, `images/`, `images-v1-ordinal-rule/`, `dimensions/`), [RETROSPECTIVE.md](RETROSPECTIVE.md), [DATA-UPDATE.md](DATA-UPDATE.md), [manifest-additions.json](manifest-additions.json), [question-updates.md](question-updates.md), [registry-entry.json](registry-entry.json).

## For the coordinator

1. The dimension table, mismatch lists and split detail hold record-level Lipi sizes; decide whether they stay tracked under the object-ledger precedent or move to the local directory with only the counts tracked (Q-1028).
2. The 23 misnamed Lipi crops could be reported upstream to the Lipi maintainer; that is an external contact and an owner decision.
3. The side of each face on the 881 objects with several faces needs a viewing pass of both sides, about 800 objects with images; the verified-sides table is the format.
