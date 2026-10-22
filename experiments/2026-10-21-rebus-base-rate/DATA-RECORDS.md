# Data records for maintainers

This package adds comparison lexicons, an Old Tamil compound vocabulary, a Sangam word-frequency source and concept pools. None of them is an inscribed-object record, so the object coverage counts in `knowledge/DATA.md` section 2 do not change. The exact files, hashes, byte counts, retrieval times and rights notices are in [SOURCES.json](SOURCES.json); the derived tables are listed there under `derived`. Everything below stays local under `data/raw/2026-10-21-rebus-base-rate/` except the concept pool definitions in [pools-v1.json](pools-v1.json).

## Proposed row for DATA.md section 1, comparison corpora

| Kind | Source and size | Rights |
|---|---|---|
| Lexicons for rebus base rates | DEDR (Burrow and Emeneau 1984, DSAL edition, 514 pages, 5,623 entries); Turner's CDIAL (DSAL edition, 836 pages, 15,418 entries); Madras *Tamil Lexicon* (DSAL edition, 4,351 pages with entries, 117,803 entries, 56,154 two-member compounds); ePSD2 Sumerian glossary (Oracc JSON, 15,940 lemmas); Rau 2019 Munda cognate sets; Backstrom and Radloff 1992 Burushaski wordlists via Lexibank; Concepticon 3.4.0; NoRaRe 1.1 concreteness; 17 Sangam texts from Project Madurai ([package](README.md)) | DEDR and CDIAL all rights reserved; Tamil Lexicon CC BY-NC-ND 2.0; ePSD2 and Rau CC0; Backstrom and Concepticon CC BY 4.0; NoRaRe CC BY-NC 4.0; Project Madurai distribution with header |

## New derived tables and their fields

| Table (local) | Built by | Fields |
|---|---|---|
| `derived-v1/dedr-entries.jsonl` | `code/parse_dedr.py` | `num`, `page`, `langs`, `subgroups` (SD1, SD2, CD, ND), `groups` [`lang`, `forms`, `gloss`, `gloss_id`] |
| `derived-v1/cdial-entries.jsonl` | `code/parse_cdial.py` | `num`, `page`, `head`, `head_forms`, `reconstructed`, `glosses`, `langs`, `subgroups` (Indo-Aryan zones) |
| `derived-v1/tamil-lex-entries.jsonl` | `code/parse_tamil_lex.py` | `page`, `head` (Tamil script), `hom`, `translit`, `star` (foreign-origin asterisk), `pos`, `members`, `verb`, `gloss`, `tamil_text` |
| `derived-v1/epsd2-lemmas.jsonl` | `code/extract_epsd2.py` | `id`, `headword`, `cf`, `gw`, `pos`, `icount`, `senses` [`mng`, `icount`, `pos`], `parts`, `n_forms`, `forms`, `periods` |
| `derived-v1/pools-full-v1.json` | `code/pools.py` | Concepticon `id`, `gloss`, `class`, `key`, `field`, `category`, `concreteness` |

## Proposed entries for data/MANIFEST.json

The proposed source entries are in [MANIFEST-PROPOSAL.json](MANIFEST-PROPOSAL.json), one per source, using the manifest's existing fields (`id`, `title`, `kind`, `status`, `location`, `local_paths`, `rights`, `fetch`, `hashes`, `size`, `notes`).

## Gaps recorded

No machine-readable full dictionary of a Munda language or of Burushaski was found. Bodding's *A Santal Dictionary* (1929–1936), Hoffmann's *Encyclopaedia Mundarica* and Berger's *Die Burushaski-Sprache von Hunza und Nager* (1998) exist in print or as page images. A study that needs Munda or Burushaski at dictionary scale needs one of them transcribed, or permission to use an existing digitisation.
