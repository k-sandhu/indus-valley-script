# Retrospective

22 November 2026.

## Approach

We moved directly from the 27 October source inventory to programmatic mining of held local primary archives (`cdli_cat.csv`, `cdliatf_unblocked.atf`, ORACC `oakk.zip`, ORACC `epsd2-admin-ur3.zip`, `joins.csv`, `sources.json`, `gadd1932.pdf`, and `external_phonetic_anchor_audit.md`). Writing [PROTOCOL.md](PROTOCOL.md) before running extraction established the strict Cohort 1 versus Cohort 2 split, the 19-field record schema, and explicit physical versus composite tracking.

## Challenges and fixes

1. **Broad Meluhha pattern false positives.** An initial exploratory scan for `luh-ha` matched hundreds of refined-silver (`ku3 luh-ha`) and purification (`szu-luh-ha`) tablets. Tightening the scan to `me-luh` variants and auditing every borderline line isolated three genuine third-millennium and second-millennium false positives (`P135796` personal name `e-lum-me-luh`, `P257207` `me-luh-luh` purification rites, and `P346234` verb `u3-me-luh-luh`) alongside 83 later or undated records (73 Neo-Assyrian, 2 Neo-Babylonian, 1 Middle Babylonian, 6 undated `BAM` medical texts, and 1 undated mathematical text) that had to be excluded from Cohort 1 because later Meluhha refers to Nubia and Kush.
2. **Cross-archive gaps in CDLI versus ORACC.** Querying ORACC's lemmatized `gloss-qpn.json` indices recovered five genuine Ur III Meluhha tablets (`P331231`, `P512784`, `P516138`, `P516366`, and `P518135`) whose transliterations were missing from the 2022 CDLI ATF dump, while querying `cdli_cat.csv` directly located `P525331` (`AO 22310`, Shu-ilishu's seal) and seven physical Early Dilmun royal vessel inscriptions (`P507617` to `P507623`) from Bahrain.
3. **Composite double-counting risks.** The Susa Ur III query returned 33 sealed or seal-related entries, of which 12 (`P454287` to `P458708`) were CDLI composite seal records derived from the 20 transliterated physical tablets. Similarly, CDLI held 4 composite entries (`P507624` to `P507627`) alongside the 7 physical Dilmun vessels, and 11 composite royal or literary editions among the 135 contemporary Meluhha texts. We linked the 12 Susa and 4 Dilmun composites inside `source_dependence` and `associated_seals` instead of counting them as physical carriers, and flagged the 11 Meluhha composites explicitly with `is_composite: true`.
4. **Cuneiform tokenization and literary name leakage.** On the first build, regex word boundaries (`\b`) split hyphenated Sumerian tokens and tripped over Akkadian underscore logograms (`_sagi_`, `_ensi2_`, `_gur_` in `P332451`), causing `dub-sar` to trigger `unit: sar`, `i3-dub` to trigger `oil (i3)`, `zu2-lum` to trigger `ivory (zu2)`, and `ki` ("earth" in literary compositions) to capture 85 Sumerian verbal forms as personal names. Replacing `\b` with hyphen-preserving whitespace boundaries after stripping editorial markers (`_`, `#`, `?`, `!`, `[`, `]`), using ORACC `PN` and `RN` lemmas exclusively when present, and restricting the `ki <PN>-ta` agency rule to administrative texts removed those false matches and reduced Cohort 1 unique personal names from 744 to 543 while recovering `ensi2 szuszin{ki}` and `sagi` on `P332451`.

## Outcome

All 196 register records, summary tables, CSV extracts, and local-only raw derivatives on `D:` built deterministically and passed all 7 independent verification checks in [verify.py](code/verify.py), including exact SHA-256 verification of all 9 input files and direct lookup of all 163 unique CDLI P-numbers in `cdli_cat.csv`.
