# Protocol: edition-linked register of contemporary Meluhha, Susa, and Dilmun contact records

22 November 2026.

## Goal and scope

We build a source-verified, edition-linked register of contemporary third-millennium and early second-millennium BCE external contact records relevant to the Indus region, paired with a chronologically separated set of later dated comparative controls. This study follows the 27 October readable-external-records scoping inventory ([REPORT.md](../2026-10-27-readable-external-records/REPORT.md)), the round-seal catalogue joins ([joins.csv](../2026-10-12-round-seal-tradition/joins.csv)), and the artifact audit ([external_phonetic_anchor_audit.md](../../research/literature/external_phonetic_anchor_audit.md)).

We mine held local primary editions and catalogues without acquiring unverified web claims, without inventing missing plates or accessions, and without assigning phonetic values or lexical meanings to Indus signs. Because this work builds a structured metadata and attestation register rather than a reading proposal, sign key, segmentation, or confirmation statistic, `python -m bench` does not apply.

## Strict chronological cohorts

Every record in the register belongs to exactly one of two cohorts. No later control is ever merged into contemporary counts or cross-tabulations.

### Cohort 1: contemporary contact records (`cohort_1_contemporary`)

Cohort 1 covers third-millennium and early second-millennium BCE witnesses (approximately 2350 to 1600 BCE) across four mutually exclusive evidence classes:

1. `explicit_meluhha_mention`: Mesopotamian cuneiform tablets, monumental inscriptions, and seals dated to the Old Akkadian, Lagash II, Ur III, Early Old Babylonian, or Old Babylonian periods that explicitly attest Meluhha (`me-luh-ha` and verified orthographic variants, including broken spellings `me-luh#-[ha]` and `me-luh-ta`), mined from the union of the CDLI catalogue (`cdli_cat.csv`), the CDLI transliteration dump (`cdliatf_unblocked.atf`), the ORACC Old Akkadian administrative archive (`oakk.zip`), the ORACC Ur III administrative archive (`epsd2-admin-ur3.zip`), and the Louvre and CDLI records for Shu-ilishu's cylinder seal (`AO 22310`, `P525331`, `S014339`). Verified lexical or verbal false positives (Sumerian `me-luh-luh` "purification rites" in `P257207`, `u3-me-luh-luh` "wash" in `P346234`, and the unrelated personal name `e-lum-me-luh` in `P135796`) are excluded. Later-period attestations of Meluhha (Middle Babylonian, Amarna, Neo-Assyrian, Neo-Babylonian, and undated first-millennium `BAM` medical texts, where the toponym shifted geographically to Nubia and Kush, plus undated mathematical text `P217674`) are excluded from Cohort 1 and logged in a separate local audit file.
2. `susa_sealed_transaction`: Physical Ur III sealed administrative tablets, bullae, and related carriers excavated at Susa and recorded in CDLI (`provenience` containing `Susa`, `period` containing `Ur III`, with a recorded `seal_id`, `seal_information`, or `@seal` transliteration section), including `P332451` (`BDTNS 157897`, `MDP 54, 029`, `TS.B 140`, `NMI BK 00696`). Dependent CDLI composite seal records (`CDLI Seals ... (composite)`) are linked to their physical carriers under `associated_seals` and `source_dependence` rather than counted as additional physical transactions.
3. `gulf_indus_style_seal`: West Asian, Gulf, and unprovenanced Indus-style and Gulf Type inscribed seals established in Gadd (1932), Laursen (2010), `experiments/2026-10-12-round-seal-tradition/joins.csv`, and `research/literature/external_phonetic_anchor_audit.md`. This comprises Laursen's Table 1 West Asian and unprovenanced Gulf Type seals (nos. 6 to 27), Karzakan seal no. 56, Kalba K4, Ra's al-Junayz RJ-2, the Susa cylinder seal (`Louvre SB 2425`), and Gadd's Ur seals nos. 1, 6, and 7. Laursen's Group 1 South Asian circular seals (nos. 1 to 5, from Chanhu-daro and Mohenjo-daro) and the Linear Elamite western Iranian seal (no. 28) are excluded from the external register. The duplicate Lipi witness `6000.1` is merged into Ur seal `3898.1` (`U.17649`, `BM 123208`, Gadd no. 16, Laursen no. 21) rather than double-counted.
4. `dilmun_named_seal`: Early second-millennium BCE Early Dilmun cuneiform-inscribed royal vessels and stamped seal tokens from Bahrain naming local rulers (`Yagli-El`, `Rimum`) and the Dilmun deity `Inzak`. This comprises the seven physical CDLI exemplars from the Royal Mounds of A'ali and Qal'at al-Bahrain (`P507617` to `P507623`, with their four dependent composite editions `P507624` to `P507627` linked in `source_dependence`) and the abstract-tier record for the three stamped Bahrain tokens bearing impressions of two Yagli-El seals reported by Laursen and colleagues (2026, *JNES* 85(1): 115–145, embargoed PDF until 1 April 2027). Middle Babylonian Failaka seals (`P511661`, `P511663`) postdate the Indus period and are excluded from Cohort 1.

### Cohort 2: later dated comparative controls (`cohort_2_later_control`)

Cohort 2 holds later readable corpora with `indus_contact_evidence_class` set to `later_control`:

1. Achaemenid Persepolis Elamite administrative tablets (Hallock 1969, OIP 92, approximately 509 to 493 BCE, `EXT-06`), used as a functional control for ration accounting and sealed authorization.
2. Early Historic South Indian Tamil-Brahmi inscribed personal items (third century BCE to third century CE, `EXT-07`, including the Karur silver ring naming `Peravatan` and the sixteen frozen seals and rings in `experiments/2026-10-24-readable-seal-controls/`).
3. Roman-period Indian Ocean Tamil-Brahmi pottery inscriptions from Berenike, Myos Hormos, and comparative Sumhuram (Sidebotham et al. 2025, first century CE, `EXT-08`, indexed excerpt tier only).

## Record schema

Every entry in `register-v1.json` carries these exact fields:

- `record_id`: unique stable identifier (`ECR-MEL-*`, `ECR-SUS-*`, `ECR-GLF-*`, `ECR-DLM-*`, `ECR-CTL-*`).
- `cohort`: `cohort_1_contemporary` or `cohort_2_later_control`.
- `region`: standardized modern and ancient geographic label.
- `carrier`: physical object type or composite edition type.
- `is_composite`: boolean distinguishing composite text editions (`true`) from physical objects or physical object groups (`false`).
- `museum_accession`: museum inventory or accession number, or `null` when unavailable in held sources.
- `cdli_or_bdtn_id`: CDLI P-number, BDTNS identifier, or catalogue identifier (`null` if none exists).
- `excavated_locus`: documented excavation site and findspot, kept strictly distinct from museum location or stylistic attribution.
- `date_period`: period and date range, retaining competing scholarly dates separately when sources disagree (as for Louvre `AO 22310`).
- `script_and_language`: writing system and language classification.
- `primary_edition`: primary bibliographic citation from the held source.
- `edited_transliteration_status`: provenance and rights status of any transliteration (`cdli_atf_held_local`, `oracc_json_held_local`, `cdli_and_oracc_held_local`, `bdtns_and_cdli_atf_held_local`, `published_reading_in_secondary_capture_local`, `indus_lipi_checked_local`, `gadd_1932_plate_local`, `abstract_only_embargoed`, `indexed_excerpt_only`, or `catalogue_metadata_only`). Full raw transliterations and third-party captures remain local-only under `data/raw/2026-11-22-external-contact-register/`.
- `goods_and_units`: list of structured commodity and metrological unit attestations extracted from the primary text or edition.
- `personal_names`: list of attested personal names extracted from ORACC lemmatization, structured cuneiform lines, seal legends, or primary editions.
- `titles_and_offices`: list of attested titles, offices, and institutional roles (such as `eme-bal me-luh-ha`, `lu2 me-luh-ha`, `ugula me-luh-ha`, `ra-gaba me-luh-ha`, `nu-banda3 ma2 me-luh-ha`, `sukkal`, `ensi2`, `dub-sar`, `ARAD2`).
- `associated_seals`: list of linked CDLI seal identifiers, composite seal P-numbers, museum seal numbers, or seal legend summaries.
- `indus_contact_evidence_class`: one of `explicit_meluhha_mention`, `susa_sealed_transaction`, `gulf_indus_style_seal`, `dilmun_named_seal`, or `later_control`.
- `source_dependence`: classification and linked identifiers distinguishing independent physical carriers from composite editions, duplicate witnesses, or abstract-tier summaries.
- `source_sha256`: mapping of repository-relative logical source file paths to exact SHA-256 hex digests.

## Extraction and verification plan

1. `code/build_register.py` deterministically computes SHA-256 hashes of all held input files, mines CDLI (`cdli_cat.csv`, `cdliatf_unblocked.atf`), ORACC (`oakk.zip`, `epsd2-admin-ur3.zip`), the round-seal joins (`joins.csv`), the external-anchor audit (`external_phonetic_anchor_audit.md`), and the external-records inventory (`sources.json`), and writes:
   - tracked outputs in `experiments/2026-11-22-external-contact-register/`: `register-v1.json`, `summary-v1.json`, and `meluhha-commodities-titles-v1.csv`;
   - local-only bulk derivatives and exclusion audits in `data/raw/2026-11-22-external-contact-register/` (physically `D:\projects\indus_valley_script\data\raw\2026-11-22-external-contact-register\`): `atf-excerpts-local-v1.jsonl`, `excluded-records-audit-v1.json`, and `source-hashes-v1.json`.
2. `code/verify.py` independently re-reads the raw source files without importing `build_register.py`, recomputes every source SHA-256 hash, verifies zero conflation between Cohort 1 and Cohort 2, checks every CDLI P-number against `cdli_cat.csv`, verifies physical versus composite accounting, confirms that excluded false positives and later-period Meluhha hits are absent from Cohort 1, and checks all aggregate counts of personal names, titles, commodities, and associated seals, writing `verification-v1.json`.
3. Every markdown document in this directory is scanned with `python tools/review_prose.py --path experiments/2026-11-22-external-contact-register --no-write`, and all genuine style flags are resolved before finalizing.
