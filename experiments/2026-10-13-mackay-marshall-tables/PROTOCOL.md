# Protocol: Mackay 1938 and Marshall 1931 seal tables, acquisition and join

Written 13 October 2026 before the repository was cloned or any join was computed. Later changes are added under "Amendments" with their date and reason; the text above that heading is not edited after the first computation.

## Questions

Q-1002 asks what the public repository `epachayan/indus-script` at commit `5c14a01f44296a01256a34e7e5e5e9fd82d9a67f` contains, under what terms, and with what file hashes. Q-1003 asks which rows of Mackay's 1938 "Tabulation of Seals" and Marshall's 1931 "Tabulation of Seals" correspond to which CISI numbers and local Lipi object families, and what size, material, findspot, level and field number each joined object gains. This package also measures how accurately the repository transcribes the printed tables and how accurately the join assigns rows to objects.

## Sources

1. The repository at the pinned commit, cloned into `data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script/`. Its README, `docs/DATA_NOTICE.md` and `LICENSE` were already saved on 12 October by the data inventory (source check D01). The tables used are `outputs/mackay_seal_table.csv` (Mackay, 709 rows), `outputs/marshall_seal_table_transcribed.csv` (Marshall, 560 rows; the repository marks `outputs/marshall_seal_table.csv` as a superseded OCR version, which is hashed and counted but not joined) and the per-page transcriptions under `transcriptions/`.
2. The local Lipi faces, `data/normalized/lipi_observed_faces.jsonl`, grouped to object families by `object_family_id`. Fields used: `source_cisi`, `metadata.excavation-idno`, `area-section`, `block-house`, `room-grid`, `depth`, `material`, `type`, `symbol`, `h`, `v`, `th` (inches) and the three millimetre fields.
3. Printed witnesses for verification. Marshall 1931 vol. II, pp. 402-405, is held twice: `research/literature/sources/marshall_1931_govscan_14985.pdf` and the Internet Archive scan saved by the evidence census (`.../focused-pass-2026-10-07/marshall-alt-pdf.body`). Mackay 1938 vol. I is not held; its Internet Archive scan (manifest entry `mackay-1938`, item `in.ernet.dli.2015.70071`) is downloaded once into the local directory for the table pages 369-391. CISI 1 and CISI 2, both held, are used to check joined CISI numbers against their printed excavation numbers and plates.

## Acquisition record

For each acquired file: URL, retrieval time (UTC), bytes, SHA256 and the observed rights notice, written to `acquisition.json` in this package. The clone is checked out at the pinned commit and its `git rev-parse HEAD` is recorded. Hashes are recorded for the two Mackay and Marshall output tables, the superseded Marshall OCR table, `outputs/findspots_mackay.csv`, `LICENSE`, `LICENSE-DATA` (if present), `docs/DATA_NOTICE.md` and `docs/DATASETS.md`.

## Transcription check

From each table, 30 rows are drawn at random with a fixed seed (Python `random.Random(20261013)`), and every printed column of each sampled row is compared with the page image: number, type, size, material, block, house, room or street (Mackay), area and serial (Marshall), level or depth, and field number. A row is wrong if any field differs from the print. The report gives the share of rows with any error and the error count per field. A difference that comes from an obvious printing error in the book is recorded as such and not counted against the transcription.

## Join rules

Keys are tried in order of strength, and later evidence only confirms or rejects a candidate.

1. **Field number.** The table's field number (Mackay `field_no`, Marshall `area` + `serial`) is normalized by upper-casing, removing spaces, dots and hyphens between the area prefix and the number, and stripping leading zeros. The Lipi `excavation-idno` is normalized the same way. A candidate is a Lipi family whose normalized string equals the normalized field number, or begins with it and continues with the row's own seal number (the export often appends the excavator's catalogue number to the registration).
2. **Published concordance.** Where a CISI basic-data entry or plate caption prints the excavation number or the Mackay or Marshall number for a CISI entry, that pairing is a candidate.
3. **Confirming attributes.** Object type (Mackay or Marshall seal type against the Lipi `type` code and shape), material, size (inches, within 0.06 in on each of the two face dimensions, compared without regard to order) and findspot (area, block, house, room) and level or depth (within 0.2 ft, sign ignored) are compared. These attributes never create a candidate.

Each table row and each Lipi family receives one disposition:

- **exact**: exactly one Lipi family carries the row's field number as its whole normalized `excavation-idno`, or as the field number followed by the row's own seal number, no other row shares that field number, and no confirming attribute contradicts it.
- **confirmed**: a single candidate found through a weaker key (a field number read with a typographic variant, a concordance entry, or a field number shared by several rows) for which at least two confirming attributes agree and none contradicts.
- **ambiguous**: two or more candidates, or one candidate with a contradicting attribute. All candidates are kept with the reason.
- **unmatched**: no candidate, with the reason (no field number, field number absent from the export, site range not in the export).

A contradiction is a material difference (steatite against faience, copper or clay), a type difference (square seal against cylinder, tablet or sealing) or a size difference larger than 0.15 in on the larger dimension. Differences within those limits are counted as disagreements but do not reject the join. No match is forced: a row with no surviving candidate stays unmatched.

## Join accuracy

From the exact and confirmed joins, at least 30 are drawn at random (seed 20261014), stratified so that each class contributes in proportion to its size and confirmed joins contribute at least ten if there are that many. Each sampled join is checked by hand against the printed table row (field number, type, size, material, findspot) and against the CISI entry for the joined number (plate photograph for type and motif, and the excavation number where the basic data print one). A join is correct when the printed table row and the CISI entry describe the same object. Precision is correct over checked, reported with a Wilson 95% interval. If more than two of the 30 are wrong, the join rule is revised and the revision recorded as an amendment before any coverage is reported.

## Coverage measurement

Coverage is measured at object level (Lipi family) with the data inventory's usable-value rules (`experiments/2026-10-12-data-inventory/PROTOCOL.md`), for three groups: Mohenjo-daro seals (`type` beginning `SEAL`), all Mohenjo-daro objects, and all objects. The fields are dimensions (any size and both face dimensions), material, findspot (block, house, room or street; Marshall gives only an area), level or depth, and field number. Before is the Lipi value alone; after counts an object as covered if Lipi or a joined row (exact or confirmed) has a usable value. The number of objects gaining each field is after minus before. Where both sources have a value, the comparison counts agreements and disagreements per field, with the tolerances above, and keeps units distinct: Mackay and Marshall sizes in inches, Mackay levels relative to the DK datum, Marshall depths below the modern surface. Lipi depth strings are compared to the table level only after the sign and unit are checked by hand on a sample.

## Rights and tracked outputs

The table licence is read from the files at the pinned commit. If the data notice grants CC BY 4.0 for the transcribed tables, the join table may carry the joined table values with the attribution recorded in the README and in `DATA-UPDATE.md`. Lipi values are not reproduced in tracked files; tracked outputs hold Lipi family ids, CISI numbers, table row ids, the table's own values, dispositions, counts and coverage. The repository clone, the Mackay and Marshall scans, page crops and any listing that shows Lipi values beside table values stay in `data/raw/2026-10-13-mackay-marshall-tables/`.

## Amendments

All amendments below were made on 13 October 2026 after development runs of the join and before the final run (`run-2026-10-13/`) and the join-accuracy sample. They are post-outcome refinements: each was prompted by what the development runs returned, and the report states how many joins each one affects.

**Amendment 1: registration forms.** The Lipi `excavation-idno` writes Marshall's areas under different prefixes: Marshall's C, E, B, A and F appear as `DK-C`, `DK-E`, `DK-B`, `DK-A` and `DK-F`, his DK area as `DK-B` or `DK-C` (occasionally `DK`), and his D area as `D` or `DK-D`. These aliases were read off development matches in which the serial and the plate number both agreed, and are fixed in `MARSHALL_ALIASES` in `join_tables.py`. The export also writes a registration followed by several catalogue numbers (`DK 5941394+400`, `HR 2240471/472/473`) and, for a few Marshall seals, by a plate reference (`VS 875CXIV:532`). These are parsed as a field number followed by a list of catalogue numbers. A family whose registration names several rows that share its field number is joined to each of them: these are the excavator's duplicate listings of one object, which the transcription notes record (for example Nos. 394 and 400, both DK 5941).

**Amendment 2: variant keys.** The protocol allowed a "field number read with a typographic variant" without defining the variant. Three forms are used: the catalogue number agrees and the field number is within two edits (insertion, deletion, substitution or adjacent transposition); the field number agrees and the catalogue number is one edit away; or the registration is the field number followed by a single letter (`HR 1400a`). A variant candidate is generated only for a row with no exact-key candidate and only for a family that no row reaches by an exact key. A development run that also accepted any field-number-only registration one edit away produced 40 candidates for 30 rows, 20 of them tablets; 26 were contradicted on type, material or size and 11 more had fewer than two agreeing attributes. That form was dropped, except for the single-letter suffix.

**Amendment 3: adjudication of contradicted exact-key candidates.** Eleven candidates reached by field number plus catalogue number were contradicted on material or size, which under the rules above makes them ambiguous. Each was read against the printed table. Where the print confirms the transcribed value, so that the conflict lies between the excavator's table and the Lipi record rather than in the transcription, and at least two other attributes agree, the join is classified as confirmed and the conflict is counted among the disagreements. Where the evidence points to a different object the candidate is rejected. Decisions and evidence are in `verification/contradiction-adjudication.csv`; ten were accepted, one left ambiguous (Marshall No. 483, where no other attribute can be compared), and two variant or suffix candidates were rejected.

Two corrections to the code bring it into line with the rules above and are not rule changes. The Lipi type code `SEAL:C` denotes a circular seal and `SEAL:CY` a cylinder; the first development run treated `SEAL:C` as a cylinder and extended type contradictions beyond square seals. The block-and-house parser split `8III` as block 8I, house II.
