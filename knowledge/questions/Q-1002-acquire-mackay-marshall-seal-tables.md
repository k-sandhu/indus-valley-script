---
id: Q-1002
title: Acquire the machine-readable Mackay 1938 and Marshall 1931 seal tables at a pinned commit
status: done
area: data
kind: data-acquisition
priority: 1
data_access: public
compute: minutes
difficulty: starter
claimed_by: ""
claim_expires: ""
prior_attempts: [MACKAY-MARSHALL-TABLES-2026-10-13]
related: [Q-1003, Q-1030]
sources: [knowledge/DATA.md, data/MANIFEST.json, experiments/2026-10-12-data-inventory/sources.json]
---

# Question

Acquire the public repository `epachayan/indus-script` at commit `5c14a01f44296a01256a34e7e5e5e9fd82d9a67f` and record what its seal tables contain. Its README describes a 709-row transcription of Mackay's 1938 "Tabulation of Seals" (type, size in inches, material, block/house/room or street, level relative to the DK datum, field number) and a 560-row transcription of Marshall's 1931 table (type, size, material, excavation area, depth below the surface), both checked against an OCR cross-check. A Zenodo record (DOI 10.5281/zenodo.23281781, CC BY 4.0) describes the same work; its version note says the tables were produced by an AI model, and it holds only a preprint PDF, so the repository is the data source.

# Why it matters

Mohenjo-daro has 1,795 provisional objects in the local corpus, but only 41.0% carry all three dimensions and 41.6% a chronology label. The two excavators' tabulations give each seal they list a size, a material, a level or depth and a findspot (Mackay: block, house and room; Marshall: excavation area). The repository states that its transcribed data are CC BY 4.0 and that Mackay 1938 is out of copyright; Mackay 1938 itself is not held locally.

# What is needed

Read [DATA.md](../DATA.md). Run `python tools/fetch_data.py --fetch epachayan-mackay-marshall` (or `--dry-run` first); the tool clones into a new `data/raw/<date>-fetch/` directory and checks out the pinned commit. Record file hashes for `outputs/mackay_seal_table.csv`, `outputs/marshall_seal_table.csv`, `outputs/findspots_mackay.csv` and the notices `docs/DATA_NOTICE.md` and `LICENSE`. Count rows and fields, and confirm the licence statement in the repository's data notice. Add the hashes to the manifest entry.

# How to decide

Done when the copy is local, its hashes and row counts are in the manifest entry, and the data notice's licence wording is recorded in a dated source record. If the data notice does not grant reuse for the tables, record that and keep the copy local.

# Prior attempts

None. The repository was identified during the 12 October 2026 inventory; the evidence census had listed it only as a search result.

13 October 2026, [package](../../experiments/2026-10-13-mackay-marshall-tables/README.md). The repository is cloned at `5c14a01f44296a01256a34e7e5e5e9fd82d9a67f` into `data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script/` (local); the clone was made by hand rather than with `tools/fetch_data.py`, to keep it in the package's own directory. `LICENSE-DATA` places the transcribed tables under CC BY 4.0 with a stated attribution, `LICENSE` places the code under MIT, and `docs/DATA_NOTICE.md` limits MIT to `scripts/`. Row counts: `outputs/mackay_seal_table.csv` 709, `outputs/marshall_seal_table_transcribed.csv` 560, the superseded `outputs/marshall_seal_table.csv` 356, `outputs/findspots_mackay.csv` 130. The Marshall table this card names is the superseded OCR version; the transcribed file is the one to use. Hashes are in [acquisition.json](../../experiments/2026-10-13-mackay-marshall-tables/acquisition.json) and the manifest entry `epachayan-mackay-marshall`. Against the print, 0 of 30 sampled Mackay rows and 3 of 30 Marshall rows were wrong.
