# Coverage record

22 November 2026.

This package upgrades the eight bibliographic source pointers in the 27 October inventory ([sources.json](../2026-10-27-readable-external-records/sources.json)) into a deterministic, edition-linked register of 196 records ([register-v1.json](register-v1.json)) mined from nine held local inputs. It adds no new raw downloads from external websites, makes no physical merges in the Indus sign corpus, and leaves `knowledge/MAP.md`, `knowledge/experiments/registry.json`, and `data/MANIFEST.json` untouched for maintainer integration.

## New structured coverage

- **Contemporary Meluhha cuneiform records (`explicit_meluhha_mention`)**: 135 records (`124` physical carriers and `11` dependent composite editions) across Old Akkadian, Lagash II, Ur III, Early Old Babylonian, and Old Babylonian corpora, including Louvre `AO 22310` (`P525331`, `S014339`) and five Ur III records recovered from the held ORACC Ur III archive (`P331231`, `P512784`, `P516138`, `P516366`, `P518135`) absent from the 2022 CDLI transliteration dump. Extracted fields cover 45 commodity and unit classes, 28 titles and institutional roles, 524 unique personal and royal names, and 12 records with linked seals.
- **Ur III Susa sealed administrative transactions (`susa_sealed_transaction`)**: 21 physical sealed objects (20 with local CDLI transliterations and `@seal` legends, including `P332451` / `BDTNS 157897` / `MDP 54, 029`, plus 1 unpublished carrier `P520278`), linking 12 dependent CDLI composite seal records (`P454287` to `P458708`) without double-counting.
- **External Gulf and Mesopotamian Indus-style seals (`gulf_indus_style_seal`)**: 29 physical objects unifying Laursen (2010) Table 1 West Asian and unprovenanced Gulf Type seals (nos. 6 to 27), Karzakan no. 56, Kalba `K4`, Ra's al-Junayz `RJ 12803`, Susa cylinder `Louvre SB 2425`, and Gadd (1932) Ur seals nos. 1, 6, and 7, with duplicate Lipi witness `6000.1` deduplicated into Ur seal `3898.1`.
- **Early Dilmun named royal inscriptions and tokens (`dilmun_named_seal`)**: 7 physical CDLI stone vessel inscriptions from A'ali and Qal'at al-Bahrain (`P507617` to `P507623`, linking 4 dependent composites `P507624` to `P507627`) naming `Yagli-El`, `Rimum`, and `Inzak`, plus 1 embargoed abstract-tier entry for Laursen and colleagues' 2026 Bahrain stamped tokens (`ECR-DLM-EXT05`).
- **Chronologically separated controls (`later_control`)**: 3 Cohort 2 records (Persepolis Fortification Elamite, Early Historic Tamil-Brahmi seals and rings, and Roman-period Berenike and Sumhuram Tamil-Brahmi pottery).

## Local-only derivatives and storage paths

Bulk transliteration excerpts, exclusion audits, and source hashes remain local-only under `data/raw/2026-11-22-external-contact-register/`, which resolves through the repository junction to `D:\projects\indus_valley_script\data\raw\2026-11-22-external-contact-register\`:

| Logical path | Physical path | Bytes | Contents |
|---|---|---:|---|
| `data/raw/2026-11-22-external-contact-register/atf-excerpts-local-v1.jsonl` | `D:\projects\indus_valley_script\data\raw\2026-11-22-external-contact-register\atf-excerpts-local-v1.jsonl` | 45,240 | Extracted Meluhha, Susa, and Dilmun ATF lines and seal sections (local only). |
| `data/raw/2026-11-22-external-contact-register/excluded-records-audit-v1.json` | `D:\projects\indus_valley_script\data\raw\2026-11-22-external-contact-register\excluded-records-audit-v1.json` | 40,554 | Audit log of 3 excluded false positives, 83 later or undated Meluhha hits, 20 excluded or deduplicated round-seal rows, and 2 Middle Babylonian Failaka seals. |
| `data/raw/2026-11-22-external-contact-register/source-hashes-v1.json` | `D:\projects\indus_valley_script\data\raw\2026-11-22-external-contact-register\source-hashes-v1.json` | 3,213 | Byte counts and SHA-256 digests of all 9 held input files. |

## Remaining acquisition gaps

1. Full text and plates of Laursen and colleagues (2026, *JNES* 85(1): 115–145, DOI `10.1086/739820`), embargoed until 1 April 2027, to upgrade `ECR-DLM-EXT05` from abstract tier to object-level accessions and verified seal legends.
2. High-resolution seal impression photographs for the sealed Ur III Girsu and Irisagrig Meluhha tablets (`P114609`, `P116633`, `P206053`, `P235705`, `P374962`, `P453801`, `P492732`) and museum photographs of the British Museum and Penn Museum Ur seals.
3. Full catalogue pages 67 to 70 of Mahadevan's revised *Early Tamil Epigraphy* and the full text of Sidebotham and colleagues (2025) if Cohort 2 controls are expanded to individual object level.
