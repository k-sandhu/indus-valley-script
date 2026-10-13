# Proposed question-card updates

From package `2026-10-13-mackay-marshall-tables`, 13 October 2026.

## Q-1002: Acquire the machine-readable Mackay 1938 and Marshall 1931 seal tables at a pinned commit

Status: `open` → `done`. Set `prior_attempts: [MACKAY-MARSHALL-TABLES-2026-10-13]`.

Outcome note to add under "Prior attempts":

> 13 October 2026, [package](../../experiments/2026-10-13-mackay-marshall-tables/README.md). The repository is cloned at `5c14a01f44296a01256a34e7e5e5e9fd82d9a67f` into `data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script/` (local); the clone was made by hand rather than with `tools/fetch_data.py`, to keep it in the package's own directory. `LICENSE-DATA` places the transcribed tables under CC BY 4.0 with a stated attribution, `LICENSE` places the code under MIT, and `docs/DATA_NOTICE.md` limits MIT to `scripts/`. Row counts: `outputs/mackay_seal_table.csv` 709, `outputs/marshall_seal_table_transcribed.csv` 560, the superseded `outputs/marshall_seal_table.csv` 356, `outputs/findspots_mackay.csv` 130. The Marshall table the card names is the superseded OCR version; the transcribed file is the one to use. Hashes are in [acquisition.json](../../experiments/2026-10-13-mackay-marshall-tables/acquisition.json) and the proposed manifest entry. Against the print, 0 of 30 sampled Mackay rows and 3 of 30 Marshall rows were wrong.

## Q-1003: Join the Mackay and Marshall seal tables to CISI M-numbers and the local Mohenjo-daro objects

Status: `open` → `done`, with the follow-ups below left for a new card or for this card's successor. Set `prior_attempts: [EVIDENCE-CENSUS-COLLECTIONS-01, OBJECT-LEDGER-PILOT-01, MACKAY-MARSHALL-TABLES-2026-10-13]`.

Outcome note to add under "Prior attempts":

> 13 October 2026, [package](../../experiments/2026-10-13-mackay-marshall-tables/README.md). Every one of the 1,269 rows has a disposition ([row-dispositions.csv](../../experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/row-dispositions.csv)): 1,108 exact, 38 confirmed, 2 ambiguous and 121 unmatched with a reason. The joined rows cover 1,134 Lipi families and CISI numbers, 1,122 of them seals (85.1% of the 1,318 Mohenjo-daro seals). The key is the export's registration, which writes the field number followed by the excavator's catalogue number; the CISI basic data served as the check. Of 30 randomly sampled joins checked against the printed tables and the CISI excavation numbers, 29 are correct, none wrong and one unresolved, within the card's limit of two errors. Mohenjo-daro objects gain both face dimensions (+12), material (+5), a spatial unit (+10) and a level (+2); 1,134 gain a separated field number and a publication reference, 1,091 a size traced to the printed table in inches and 1,101 a level with its datum. The rules were amended three times after development runs (registration forms, variant keys, adjudication of contradicted candidates against the print); the amendments are in the package protocol.

Remaining items:

- Mackay No. 181: the printed table gives DK 14921, CISI gives DK 11492 for M-1195, and the export joins them. Compare Mackay's vol. II plate photograph of No. 181 with the CISI photograph of M-1195.
- Two ambiguous rows: Mackay No. 434 (two Lipi families, 2301 and 4045, carry the same registration DK5081434) and Marshall No. 483 (registration only; the print gives yellow faience, the export steatite).
- Mackay's plate volume is not held, and objects numbered above M-1659 (CISI 3.1) have no catalogue entry here, so joins to them were checked on the print and the registration alone.
- The 14 differences between the transcription and the print ([print-corrections.csv](../../experiments/2026-10-13-mackay-marshall-tables/verification/print-corrections.csv)) are recorded but not applied to the join table.

## Q-1022: Convert depth strings to metres against a named datum

No status change. Add to "Prior attempts" or the card's inputs:

> 13 October 2026: the Mackay and Marshall join gives 1,101 Mohenjo-daro objects a level with its datum (Mackay: DK datum, or the SD bench mark 2.2 ft above it for the SD area; Marshall: below the modern surface), keyed by Lipi family in [join-table.csv](../../experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv). The export's depth strings agree with the table levels for 1,107 of 1,110 comparable rows.
