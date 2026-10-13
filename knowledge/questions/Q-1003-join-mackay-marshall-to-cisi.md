---
id: Q-1003
title: Join the Mackay and Marshall seal tables to CISI M-numbers and the local Mohenjo-daro objects
status: done
area: data
kind: metadata
priority: 1
data_access: local-only
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-COLLECTIONS-01, OBJECT-LEDGER-PILOT-01, MACKAY-MARSHALL-TABLES-2026-10-13]
related: [Q-1002, Q-1006, Q-1013, Q-1022]
sources: [knowledge/DATA.md, experiments/2026-10-12-data-inventory/run-2026-10-12/field-coverage-by-site.csv, experiments/2026-10-06-evidence-census/synthesis/join-summary.json]
---

# Question

Which Mackay 1938 and Marshall 1931 seal-table rows correspond to which CISI M-numbers and local Lipi objects, and what size, material, findspot and level does each joined object gain?

# Why it matters

The excavation tables carry field numbers and findspots that the local export holds only in part. Joined, they give Mohenjo-daro seals an excavation registration, a findspot within a block and house, a level against a stated datum and a size from the excavator. The census already used Marshall's p. 402 tabulation to confirm two British Museum joins, so the route is known to work.

# What is needed

Read [DATA.md](../DATA.md). Inputs: the tables acquired under Q-1002; the local Lipi `excavation-idno` field, which carries strings such as `DK` field numbers for Mohenjo-daro; the CISI 1 and CISI 2 basic-data sections (Q-1005, Q-1006), which pair CISI numbers with excavation numbers; the held Marshall 1931 scan; and Mackay 1938, which is not held but is scanned on the Internet Archive (manifest entry `mackay-1938`). The tables are AI transcriptions, so every sampled join is checked against the printed table, not against the CSV alone. Keep the excavator's units: Mackay's sizes are in inches and his levels are relative to the DK datum, Marshall's depths are below the modern surface. Store every join with its basis (exact field number, normalized field number, published concordance) and keep ambiguous candidates separate.

# How to decide

Done when every table row has a disposition (joined to one CISI number, candidate set, or unmatched with reason) and a coverage table reports how many Mohenjo-daro objects gain each field. Check a random sample of 30 joins against the printed tables and CISI plates before reporting; stop and revise the join rule if more than two of the 30 are wrong.

# Prior attempts

No join of these tables has been attempted. The object ledger pilot and the museum census joined a few Mohenjo-daro objects through Marshall's tabulation by hand.

13 October 2026, [package](../../experiments/2026-10-13-mackay-marshall-tables/README.md). Every one of the 1,269 rows has a disposition ([row-dispositions.csv](../../experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/row-dispositions.csv)): 1,108 exact, 38 confirmed, 2 ambiguous and 121 unmatched with a reason. The joined rows cover 1,134 Lipi families and CISI numbers, 1,122 of them seals (85.1% of the 1,318 Mohenjo-daro seals). The key is the export's registration, which writes the field number followed by the excavator's catalogue number; the CISI basic data served as the check. Of 30 randomly sampled joins checked against the printed tables and the CISI excavation numbers, 29 are correct, none wrong and one unresolved, within the card's limit of two errors. Mohenjo-daro objects gain both face dimensions (+12), material (+5), a spatial unit (+10) and a level (+2); 1,134 gain a separated field number and a publication reference, 1,091 a size traced to the printed table in inches and 1,101 a level with its datum. The rules were amended three times after development runs (registration forms, variant keys, adjudication of contradicted candidates against the print); the amendments are in the package protocol.

Remaining items, for a successor card:

- Mackay No. 181: the printed table gives DK 14921, CISI gives DK 11492 for M-1195, and the export joins them. Compare Mackay's vol. II plate photograph of No. 181 with the CISI photograph of M-1195.
- Two ambiguous rows: Mackay No. 434 (two Lipi families, 2301 and 4045, carry the same registration DK5081434) and Marshall No. 483 (registration only; the print gives yellow faience, the export steatite).
- Mackay's plate volume is not held, and objects numbered above M-1659 (CISI 3.1) have no catalogue entry here, so joins to them were checked on the print and the registration alone.
- The 14 differences between the transcription and the print ([print-corrections.csv](../../experiments/2026-10-13-mackay-marshall-tables/verification/print-corrections.csv)) are recorded but not applied to the join table.
