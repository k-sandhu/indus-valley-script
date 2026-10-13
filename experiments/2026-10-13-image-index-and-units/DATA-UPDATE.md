# Proposed changes to knowledge/DATA.md

From the package [image-index-and-units](README.md), 13 October 2026. Numbers come from `experiments/2026-10-13-image-index-and-units/run-2026-10-13/`. No third-party data with an attribution requirement is added; the sources used are already in DATA.md section 1.

## Section 1, table "Inscribed-object corpora and catalogues"

Lipi export row, column "Known defects": append

> 23 crop file names name the wrong object (for example `H-502_B.jpg` shows H-902 B) and 8 write I for l in the prefix; `h`, `v`, `th` hold each size as recorded, in inches, millimetres or centimetres, not only inches ([image index and units](../experiments/2026-10-13-image-index-and-units/README.md))

Project normalized files row is unchanged. Add a row after "Project registers, frames and releases":

| Source | Size | Where | Notes |
|---|---|---|---|
| [Face-level image index and dimension audit](../experiments/2026-10-13-image-index-and-units/README.md) (13 October) | 8,722 file records, 8,444 face–image links, 3,664 keys placed on CISI 1 and 2 plate pages; 17,040 size values with unit, precision and flags | Tracked (identifiers, joins, counts; the dimension table holds record-level Lipi sizes); OCR text and contact sheets local | Sides of faces on 881 objects with several faces are left open |

## Section 2, compact table

Keep the inventory's Image column as the 12 October measurement and add a footnote under the table:

> Image coverage by the face-level index of 13 October: any image 54.6% of objects (seals 70.4%, Mohenjo-daro 74.8%, Harappa 43.2%); a photograph of the object's inscribed side 46.0% (seals 68.3%), against 17.6% when only the files in the Lipi index are counted ([coverage.csv](../experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/coverage.csv)).

## Section 2, paragraph "Placeholders and units": replace the sentence beginning "The millimetre sizes are mostly conversions" with

> The fields `h`, `v` and `th` hold each size as recorded and the millimetre fields its conversion. Of 17,040 face-axis values, 5,643 were recorded in inches (2,295 to 0.1 in, 3,298 to 0.01 in), 389 in millimetres and 102 in centimetres, mostly without a unit in the string, 4,250 exist only in millimetres (2,501 whole, 1,749 to 0.1 mm), and 6,656 are empty or zero. The millimetre value reproduces the recorded value for all but 38 (23 rounded, 15 different); the inventory's 228 inch–millimetre mismatches are 180 values recorded in millimetres, 42 in centimetres and 6 true mismatches ([dimension summary](../experiments/2026-10-13-image-index-and-units/run-2026-10-13/dimensions/summary.json)).

## Section 2, paragraph "Conflicts": replace "and sizes agree for 2,018 objects and differ for 206" with

> and sizes agree on every comparable axis for 2,340 objects and differ for 9, with 20 more giving the lower end of a Lipi thickness range; the 206 differences counted on 12 October were mostly (199) Lipi thickness ranges that the comparison rule did not read as numbers ([website-disagreements.csv](../experiments/2026-10-13-image-index-and-units/run-2026-10-13/dimensions/website-disagreements.csv))

## Section 2, paragraph "Images": replace with

> **Images.** The 8,722 local image files are photograph crops cut from the CISI 1 and 2 plates with their printed captions. The face-level index ([face-image-links.csv](../experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv)) parses every name, corrects 26 names against the printed caption, reads the caption of 231 of the 299 files named by volume and page, and places files on their plate page (CISI 1 PDF page = printed + 36, CISI 2 = printed + 35). Any image: 2,562 objects (54.6%) and 3,003 faces (52.9%); a photograph of the face's own side: 2,159 objects (46.0%) and 2,181 faces (38.4%); an impression of it: 1,489 objects (31.7%). Face-side figures cover objects with one face row and 21 objects verified by viewing; the 881 other objects with several faces have their files linked without a side. A random sample of 60 links had 60 correct identities and kinds. Of the 2,677 faces without an image, 661 have no CISI number and 1,926 have numbers beyond the ranges of CISI 1 and 2.

## Section 4, target record

- `images` row, "Current coverage": `Any image 54.6%; photograph of the face side 46.0% (one-face objects and verified sides); file hash, page and kind per link (Q-1004)`
- `dimensions` row, "Current coverage": `Any 76.6%; all three 28.8%; unit of record and precision known for every value (Q-1020)`
- `faces` row, "Current coverage": append `; side of each face unassigned on 881 objects with several faces`

## Section 5, priorities

- Rank 6, Q-1004: change "What changes" to `Done 13 October for files, pages and single-face sides; remaining: sides of faces on 881 multi-face objects by viewing`.
- Rank 20, Q-1020: change "What changes" to `Done 13 October; value checks against excavation tables wait for Q-1003`.
