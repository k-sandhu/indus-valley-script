# Proposed changes to knowledge/DATA.md from the CISI 2 basic-data pilot

All changes come from [README.md](README.md) and [coverage.json](coverage.json) of this package. The transcribed values behind them are local only, in `data/raw/2026-10-13-cisi2-basic-data-pilot/`, pending a rights decision on CISI (copyright 1991 Finnish Academy of Science and Letters, reuse unverified). DATA.md should say so wherever it cites the new numbers. No CC BY or other attributed source is introduced.

The museum numbers below count a value as usable when the CISI 2 cell gives a museum code with a number, including 23 numbers with one bracketed digit; without those, the corpus gain is 179 objects instead of 202 (453 objects, 9.6%).

## Opening paragraph

Replace "…53.4% a local image, 5.8% a museum number, and none a calendar date." with:

> …53.4% a local image, 10.1% a museum number (5.8% before the CISI 2 basic-data pilot of 13 October added 202 Mohenjo-daro seals, values local), and none a calendar date.

## Section 1, "Inscribed-object corpora and catalogues"

CISI 2 row. Replace the "Identifiers and fields" cell with:

> CISI numbers; basic data (printed pp. 434–447, PDF 469–482) in five columns: CISI number, FC concordance number, excavation number, museum and registration numbers (with National Museum of Pakistan accessions), photograph sources; no findspot, depth, material or dimension column

and the "Known defects" cell with:

> Page order complete for the catalogue (printed page = PDF − 35 for pp. 1–447); small digits blurred, so about 7% of basic-data cells stay uncertain after double reading ([pilot](README.md))

CISI 1 row. Replace "basic data with museum and excavation numbers" with:

> basic data (printed pp. 365–375) in the same five columns as CISI 2, with (o) and (t) markers in the excavation column; no findspot, depth, material or dimension column

## Section 1, "Project registers, frames and releases"

Add a row:

| Source | Size | Where | Notes |
|---|---|---|---|
| [CISI 2 basic-data pilot](README.md) (13 October) | 327 entries, M-621 to M-947; 283 joined to Lipi families | Values local (rights unverified); schema, accuracy, coverage and per-object field flags tracked | Two blind readings, 90.5% cell agreement, 119 of 1,635 cells left bracketed; procedure for the remaining 22 CISI 2 and about 20 CISI 1 half-column blocks |

## Section 2, "Metadata coverage"

In the coverage table change the Museum column for three rows, and add a note under the table:

| Group | Museum before | Museum after |
|---|---:|---:|
| All objects | 5.8 | 10.1 |
| Seals | 9.5 | 18.5 |
| Mohenjo-daro | 12.0 | 23.3 |

Note to add after the table's source line:

> Museum after 13 October adds the CISI 2 basic data for M-621 to M-947 (202 seals at Mohenjo-daro gain a museum number, from local values; [coverage.json](coverage.json)). Other columns are unchanged: the CISI basic data prints no findspot, depth, material or dimensions.

In the "Conflicts" paragraph, add:

> For the 278 Mohenjo-daro objects in M-621 to M-947 that have an excavation number in both sources, Lipi's `excavation-idno` equals the CISI 2 number for 40 (mostly objects with FC numbers below 1000) and, for 182 with four-digit FC numbers, is the CISI 2 number followed by the FC concordance number without its first digit; 12 differ only in the area prefix (DK against DK-B or DK-C), 4 are values crossed between two entries (M-653 with M-655, M-656 with M-707), where plate measurements show CISI 2's table to be wrong, 2 differ where the page confirms the CISI 2 number, 3 are truncated or carry another suffix, and 35 cannot be compared because the printed cell is uncertain. Museum numbers agree with the older export for all 71 comparable objects ([pilot README](README.md)).

## Section 4, "Target object record"

| Field | Change |
|---|---|
| `identifiers` | Current coverage: add "FC concordance number for 283 objects (CISI 2 pilot, local)". Best source: keep. |
| `excavation_registration` | Best source: "CISI basic data (prints the excavator's number; Lipi appends FC digits to it, see section 2); excavation tables". |
| `museum` | Current coverage: "10.1% (older export 5.8%, plus 202 from the CISI 2 basic-data pilot, local); 68 census joins". |
| `material` | Best source: replace "CISI basic data" with "CISI plate captions (form-class symbols, CISI 2 Table 2)". |
| `dimensions` | Best source: replace "CISI basic data" with "CISI plates (inscribed sides printed at 2:1)". |
| `findspot`, `depth` | No change; note that the CISI basic data does not supply them. |

## Section 5, "Acquisition and enrichment priorities"

Rank 3 (Q-1005, Q-1006): replace "What it changes" with:

> Museum numbers and holding institutions for the Indian and Pakistani collections; the M-621 to M-947 pilot raised museum coverage from 5.8% to 10.1%; about 5 hours of double-read agent work remain for both volumes (2.8 for CISI 2, 2.4 for CISI 1 at the CISI 2 rate) ([procedure](PROCEDURE.md))

## Section 7, "Rights"

No change to the table. The row "CISI volumes, Mahadevan 1977, excavation reports, author PDFs" already covers the transcription: values local, page locators, counts and our observations tracked.
