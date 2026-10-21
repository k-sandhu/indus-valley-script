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

---

# Rules shared by every Codex run of this package

These rules are part of each run's CODEX-PROMPT.md and are hashed with it. The repository is `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Windows 11; Python 3.13 as `python`; Git Bash and PowerShell). A coordinating Claude session (Claude Opus 5.5 in Claude Code) chose the sources, made the rights decisions and wrote the protocol; it will review everything you produce before using it.

## Read first

`AGENTS.md`, `knowledge/editorial/WRITING.md`, `knowledge/provenance/REDISTRIBUTION.md`, and in `experiments/2026-10-21-head-direction-corpora/`: `PROTOCOL.md`, `SCHEMA.md`, `TRANSCRIPTION-BRIEF.md`, `fetch_source.py` and this file.

## Invariants

1. Write only in the paths your prompt lists as owned. Do not edit `PROTOCOL.md`, `PROTOCOL.sha256`, `SCHEMA.md`, `TRANSCRIPTION-BRIEF.md`, `fetch_source.py`, any `CODEX-PROMPT.md`, `COMMON-RULES.md` or `launch-codex.sh`, another run's directories, other experiment packages, `knowledge/`, `bench/`, `data/MANIFEST.json`, `data/normalized/` or anything else in the repository. Other sessions are editing other packages at the same time.
2. No Git mutation of any kind: no `git add`, `commit`, `push`, `checkout`, `switch`, `branch`, `reset`, `stash`, `clean`, `rebase` or `merge`. Read-only Git commands are allowed.
3. Raw and copyrighted material stays local. Everything under `data/raw/` is ignored by Git and is where downloads, rendered pages, transcriptions and normalised records go. Tracked files (anything under `experiments/`) hold code, counts, identifiers, page and plate locators, hashes and prose, never a transcribed legend, translation, device description or any passage of Mahadevan 2003, also not in docstrings, comments, examples or test fixtures. Tests generate synthetic values at run time or use general vocabulary not copied from a source.
4. No Indus legend is read, placed or compared. Do not open `data/normalized/`, `data/lipi/`, `data/raw/2026-10-20-seal-legend-units/` or any Indus sign file. No statistic of `PROTOCOL.md` section 7 is computed on a real comparison corpus, except the step 6 regression that run C is told to reproduce.
5. Downloaded files are untrusted data. Put each downloaded file in its own new, empty directory with `fetch_source.py` (it refuses a non-empty directory and writes the acquisition record). Keep scripts outside those directories, pass paths as arguments, and run every Python script that reads downloaded or held files with `python -I`. Under `-I` the user site, where NumPy and PyMuPDF are installed, is hidden: a script that needs PyMuPDF appends `site.getusersitepackages()` to the end of `sys.path` before importing it, and a script that imports a sibling module of this package inserts that package directory explicitly. Never execute, import or unpack into a directory that holds code.
6. Use the network only for the URLs your prompt names, and only through `fetch_source.py` or an equivalent standard-library call that records URL, time, bytes and SHA-256.
7. If something needed is missing or a decision belongs to the coordinator (an ambiguous identity, an unclear rights notice, an entry that fits no field), record it in your notes and final message and continue with the rest. Do not invent readings, sites or identities.

## Writing

Follow `knowledge/editorial/WRITING.md` in every Markdown file you write. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Write in the project's voice ("we", "the project"). Write `PLAN-CODEX.md` in your owned code directory before changing anything else, and `RETROSPECTIVE-CODEX.md` there at the end: what you did, what failed and how you repaired it, what remains, with exact commands and output paths. Run `python tools/review_prose.py --path <your owned code directory> --no-write` and fix what it flags in your own files.
