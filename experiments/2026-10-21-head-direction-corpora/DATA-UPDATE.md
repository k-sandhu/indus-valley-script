# Data update for maintainers

This package added seven sources and one new use of a held source. Maintainers can fold the entries below into [knowledge/DATA.md](../../knowledge/DATA.md) (section "Excavation reports, comparison corpora and context data held locally" and the rights table of section 7) and into [data/MANIFEST.json](../../data/MANIFEST.json) after merging. Hashes, URLs and retrieval times are in [acquisition/](acquisition/) and in the per-run `SOURCES.md` files under [codex/](codex/). All files are local under `data/raw/2026-10-21-head-direction-corpora/`.

## Proposed manifest entries

| Key | Status | Location | Size and SHA-256 of the key file | Rights status | Acquisition route |
|---|---|---|---|---|---|
| `asi-ar-1903-04` | held | local-only | PDF 204,293,478 bytes, `83ad9f30191c4aa2…` (second scan 38,614,635 bytes) | rights-unverified; Government of India 1906, public domain by age (our assessment) | Internet Archive `in.ernet.dli.2015.207529`, `in.gov.ignca.21816`, through `fetch_source.py` |
| `asi-ar-1909-10` | held | local-only | PDF 15,007,114 bytes, `96392b89b3dc54e8…` | as above, 1914 | `in.ernet.dli.2015.35501` |
| `asi-ar-1911-12` | held | local-only | PDF 33,076,046 bytes, `5e0695ea81c24167…` (second scan 18,393,279 bytes) | as above, 1915 | `in.ernet.dli.2015.207521`, `in.ernet.dli.2015.35495` |
| `asi-ar-1913-14` | held | local-only | PDF 50,488,078 bytes, `25943cb02f068dc9…` (second scan 24,146,577 bytes) | as above, 1917 | `dli.ministry.09311`, `in.ernet.dli.2015.35545` |
| `mahadevan-2003` | held | local-only | PDF 233,674,839 bytes, `2cc1fc9eab8fbe76…` | rights-unverified; copyright 2003, third-party upload without licence | Internet Archive item `iravatham-mahadevan-early-tamil-epigraphy-from-the-earliest-times-to-the-sixth-century-a.-d.` |
| `oracc-epsd2-admin-oakk` | held | local-only | 29,933,476 bytes, `4d4eaf78ba1fa6d9…` | explicit-license, CC0 declared in the JSON | `https://oracc.museum.upenn.edu/json/epsd2-admin-oakk.zip` |
| `cdli-bulk-2022` | held | local-only | `cdli_cat.csv` 154,768,722 bytes, `2e3232f75325b61c…`; `cdliatf_unblocked.atf` 86,897,831 bytes, `2896ec253767fa07…` | rights-unverified; CDLI terms: free re-use under common and fair academic practice with credit | GitHub `cdli-gh/data` at `d66b12b065af39a57d640576b4c7e098db5dac7f` (Git LFS media URLs) |

The held ORACC Ur III archive (`data/raw/2026-10-12-bronze-age-comparison/acquisition/sumerian-ur3-v1/response.bin`) was read in full for the first time: all 80,181 entries rather than the 3,000-entry sample.

## Derived local datasets

| Dataset | Records | Fields beyond the held Ur III record form |
|---|---:|---|
| Transcriptions of the Basarh and Bhita lists and Mahadevan's tables (`transcriptions/`) | 140 + 286 + 120 + 32 rows; 233 register rows; 25 findspot-index rows | entry, sub-entry, printed and PDF page, plate and figure, object text, material, dimensions, device, legend as printed with lines, translation, doubt and restoration flags, palaeographic date, findspot, depth, impressions, duplicates, cross-references |
| Normalised records (`normalized/brahmi.jsonl`, `sux-ur3`, `akk-sargonic`, `sux-sargonic`, each also as `.adapted.jsonl`) | 587; 31,512; 89; 175 | object id, object kind, genre (seal, sealing, coin), die id, impressions, site, findspot, depth, period, language and its basis, script, lines and line breaks in sign units, members, tags and tag sources, completeness |

## Coverage change

These are comparison corpora, not Indus objects, so the Indus coverage figures of DATA.md do not change. The project now holds, for the first time, seal legends in head-final languages with object and site: 556 Indo-Aryan records from Basarh and Bhita (495 objects; 413 with a findspot and 388 with a depth, all from Spooner's and Marshall's lists) and 31 Tamil-Brahmi records (25 with a site). The Ur III seal corpus grows from 522 sampled records to 31,512, and an Old Akkadian corpus of 264 records is new.

## Gaps for the data cards

The feasibility ledger, [FEASIBILITY.md](FEASIBILITY.md), lists the gaps: too few Old Akkadian Akkadian-language legends with a site (11 eligible), too few Tamil-Brahmi seals and rings (16), no West Semitic seal corpus (Avigad and Sass 1997 has no lawful digital copy; DASI blocked automated access), and no word-level head-final corpus. A data question card for a second head-final and a second head-initial seal corpus would carry these.
