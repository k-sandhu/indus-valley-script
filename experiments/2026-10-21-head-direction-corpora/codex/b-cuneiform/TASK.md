# Codex run B: build the Ur III and Old Akkadian seal-legend corpora

Today is 21 October 2026 (UTC). The project is building comparison corpora of seal legends in head-final and head-initial languages for a test written in `experiments/2026-10-21-head-direction-corpora/PROTOCOL.md`. Your part is the head-initial side: every Ur III seal legend in the ORACC archive the project already holds, and the seal legends of the Old Akkadian (Sargonic) period from ORACC and the Cuneiform Digital Library Initiative (CDLI), normalised to `SCHEMA.md`.

## Owned paths

- `experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/` (code, lexicon, plan, counts, retrospective)
- `experiments/2026-10-21-head-direction-corpora/acquisition/oracc-oakk-*.json` and `cdli-data-*.json`
- `data/raw/2026-10-21-head-direction-corpora/src-oracc-oakk-*/` and `src-cdli-data-*/` (one new directory per downloaded file)
- `data/raw/2026-10-21-head-direction-corpora/normalized/sux-ur3.*`, `akk-sargonic.*`, `sux-sargonic.*` and `cuneiform-*` (normalised records and review tables)
- `data/raw/2026-10-21-head-direction-corpora/codex-b/` (scratch, unpacked archives)

## Inputs

1. Held, read in place and never modified: the ORACC `epsd2/admin/ur3` JSON archive, `data/raw/2026-10-12-bronze-age-comparison/acquisition/sumerian-ur3-v1/response.bin` (a zip of 561,755,376 bytes; its request record is `request.json` beside it, and `data/raw/2026-10-12-bronze-age-comparison/normalized-v4/manifest.json` gives its hash under `source_hashes`; verify the SHA-256 before use). The 12 October package normalised a fixed sample of 3,000 of its 80,181 entries into `normalized-v4/records.jsonl` (522 seal records, 309 distinct legends of two or more signs). You use all entries.
2. To download, each into its own new directory with `python -I experiments/2026-10-21-head-direction-corpora/fetch_source.py`:
   - `https://oracc.museum.upenn.edu/json/epsd2-admin-oakk.zip` (about 29.9 MB), source id `oracc-oakk`, rights `explicit-license` with note "CC0, as declared in the ORACC JSON (verify the declaration in the unpacked files)".
   - The CDLI bulk data in the GitHub repository `cdli-gh/data` at commit `d66b12b065af39a57d640576b4c7e098db5dac7f` (committed 2023-10-11; the README dates the data dump). The two data files are stored with Git LFS, so fetch `https://media.githubusercontent.com/media/cdli-gh/data/d66b12b065af39a57d640576b4c7e098db5dac7f/cdli_cat.csv` and `.../cdliatf_unblocked.atf`, and the README from `https://raw.githubusercontent.com/cdli-gh/data/d66b12b065af39a57d640576b4c7e098db5dac7f/README.md`. Source id `cdli-data`, rights `rights-unverified` with note "CDLI terms of use: text may be freely copied, aggregated and re-used according to common and fair academic practice, with credit to CDLI (https://cdli.earth/terms-of-use); the repository has no licence file". If a file arrives as an LFS pointer, record that and fetch the media URL.
3. Unpack zips with the standard library into a new directory under `codex-b/` that holds no code, after checking every member name for absolute paths and `..`.

## The earlier normaliser

The code that wrote `normalized-v4/records.jsonl` is in `experiments/2026-10-12-bronze-age-comparison/reference_sources.py` (earlier versions under `history/`); the logs `data/raw/2026-10-12-bronze-age-comparison/normalization-v*.log` show how it was run. Import nothing from it into a run over downloaded data without reading it first; copy the functions you need into your own module. Reuse its ORACC reading of the object, surface and line structure, its separation of seal surfaces from the account they are impressed on, its unit and word conventions (`units`, `words`, `word_units`, `source_word_refs`, `gold`) and its handling of breaks and damage, so that your `sux-ur3` records reproduce the 522 held seal records for the same 3,000 entries. Report that reproduction (records matched exactly, records differing, and why). If the code cannot be found, write the parser from the ORACC JSON and still report the comparison with the held records.

## Corpora

- `sux-ur3`: every seal legend in the Ur III archive whose words are Sumerian (ORACC token language `sux`); legends whose words are mostly Akkadian are counted and written to `cuneiform-ur3-akkadian.jsonl`, outside the corpus.
- `akk-sargonic` and `sux-sargonic`: seal legends of the Old Akkadian period, split by the language of their words. Sources: the seal surfaces of the ORACC `epsd2/admin/oakk` texts (sealings on tablets and envelopes, lemmatised) and, from CDLI, (a) artifacts of period "Old Akkadian" whose object type is a seal (cylinder or stamp), and (b) seal sections of Old Akkadian tablets, envelopes and bullae in the ATF that ORACC does not already supply. Where a P-number is in both, use the ORACC edition and add the CDLI identifiers as aliases. A legend of mixed language goes to the corpus of the majority of its words, with a flag.

## Normalisation

Write every record in the form of `SCHEMA.md`, with these rules. `object_id` is the P-number of the sealed tablet, envelope or bulla for a sealing, and of the seal for a seal; `object_kind` and `genre` follow from the CDLI or ORACC object type. `die_id` is the CDLI composite seal number (S-number) where the catalogue or ATF links the impression to one, else null. `site` is the normalised provenience; a provenience recorded as uncertain or unknown gives `site: null`, and such records are listed in `cuneiform-site-unknown.jsonl` and counted. `lines` come from the ATF line structure (`line_division_basis: atf`). `text_genre` keeps the ORACC or CDLI genre of the tablet. `gold` keeps ORACC part-of-speech codes. Tags follow `SCHEMA.md`: ORACC proper-noun codes decide `NAME`, `DIVINE`, `PLACE` and `NUMBER` (`tag_source: editor-pos`); common nouns and adjectives are tagged `TITLE`, `KIN`, `GRAM` or `OTHER` from `codex/b-cuneiform/lexicon-cuneiform.tsv`, which you write and track (columns: form or ORACC citation form and guide word, tag, note), covering at least the titles and relations common in seal legends (`lugal`, `ensi₂`, `dub-sar`, `šabra`, `sanga`, `nu-banda₃`, `sukkal`, `šagina`, `ugula`, `šar`, `arad₂`/`ARAD₂`, `dumu`, `dumu-munus`, `dam`, `geme₂`), each with its ORACC guide word; unlemmatised CDLI words not in the lexicon are tagged `NAME` with `tag_source: default-name`. Write every member tagged by `lexicon` or `default-name` with its count to the local review table `cuneiform-tag-review.tsv`. `completeness` follows the edition's damage marks: `damaged-edge` when the first or last sign is broken or missing, `restored` when the legend is complete with restorations, `illegible` when no word is readable. `transcription.method` is `digital-edition`.

Group nothing and drop nothing: deduplication and eligibility belong to the analysis code (`PROTOCOL.md` section 4). Do write, per corpus, the number of distinct sign-unit sequences, so the coordinator can see the corpus sizes.

## Deliverables

- `codex/b-cuneiform/normalize_cuneiform.py` with a docstring giving its command line, taking every input and output path as an argument.
- `normalized/sux-ur3.jsonl`, `akk-sargonic.jsonl`, `sux-sargonic.jsonl` and the review tables, local.
- `codex/b-cuneiform/counts.json` (tracked, counts only): per corpus, records, distinct objects, distinct sign-unit sequences, distinct sequences of at least two signs and of at least two words, records by genre, object kind, site (top 15 and other), language basis, completeness and tag source; records with `site: null`; records with a `die_id`; records with line divisions; share of members tagged by ORACC part of speech; and the reproduction check against the held records.
- `codex/b-cuneiform/SOURCES.md` (source id, URL, bytes, SHA-256, rights, what was used).

## Verification

1. The held archive's SHA-256 matches the manifest; every download record shows its size and hash.
2. The reproduction check against the 522 held seal records, with every difference explained.
3. Every record validates: `units` equals the concatenation of `word_units`, `line_of_word` has one entry per word, `tags` and `tag_source` have one entry per member, and the required fields of `SCHEMA.md` section "Identity and provenance" are present.
4. Ten records drawn at random per corpus (seed `b-check`) compared by hand with their ORACC or CDLI page text; differences reported.
5. `git status --porcelain` shows changes only inside your owned tracked paths.

## Final message

List every path you created, the acquisition checks, the reproduction result, the counts per corpus (records, distinct legends of at least two signs and of at least two words, records without a site), the ten-record checks, the decisions the coordinator must make (mixed-language legends, seals without provenience, lexicon entries you were unsure of), and the time the run took.
