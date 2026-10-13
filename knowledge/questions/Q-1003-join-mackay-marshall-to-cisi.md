---
id: Q-1003
title: Join the Mackay and Marshall seal tables to CISI M-numbers and the local Mohenjo-daro objects
status: open
area: data
kind: metadata
priority: 1
data_access: local-only
compute: hours
difficulty: standard
claimed_by: ""
claim_expires: ""
prior_attempts: [EVIDENCE-CENSUS-COLLECTIONS-01, OBJECT-LEDGER-PILOT-01]
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
