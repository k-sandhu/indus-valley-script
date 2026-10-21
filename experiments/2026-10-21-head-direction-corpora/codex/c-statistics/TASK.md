# Codex run C: the Brahmi normaliser, the record validator and the statistics of the discrimination test

Today is 21 October 2026 (UTC). The project is testing which statistics of seal legends separate head-final from head-initial languages, on readable comparison corpora only (`experiments/2026-10-21-head-direction-corpora/PROTOCOL.md`, with `AMENDMENT-1.md`, `SCHEMA.md` and `TRANSCRIPTION-BRIEF.md`). Three other Codex runs are acquiring and transcribing the sources right now. You write the code that turns their transcriptions into records, validates records, and computes the protocol's statistics and keep rule, and you test it on synthetic data and on one regression against an earlier result. You do not run the analysis on any real comparison corpus; the coordinator runs it once, after the inputs are reviewed.

## Owned paths

- In `experiments/2026-10-21-head-direction-corpora/`: `hd_common.py`, `hd_stats.py`, `discriminate.py`, `normalize_brahmi.py`, `validate_records.py`, `selftest.py`, `lexicon-brahmi.tsv`, `TOOLS.md`, `selftest.json`
- `experiments/2026-10-21-head-direction-corpora/codex/c-statistics/` (plan, notes, retrospective)
- `data/raw/2026-10-21-head-direction-corpora/codex-c/` (synthetic fixtures, test outputs, scratch)

Do not open `data/raw/2026-10-21-head-direction-corpora/transcriptions/`, `normalized/`, `src-*` or `pages-*`: they are being written by the other runs. Build and test on synthetic records you generate in `codex-c/` and on the held file named in the regression below. All code uses the Python standard library only, so that it runs under `python -I` without NumPy; every script has a docstring giving its command line and takes every path as an argument.

## 1. `hd_common.py`

Shared helpers: JSONL reading and writing, SHA-256 of files, the seeded random generator (`random.Random(int(sha256(text).hexdigest(), 16))`), median and percentiles with a stated definition (linear interpolation between order statistics, as NumPy's default), and the union-find used for legend grouping.

## 2. `normalize_brahmi.py`

Input: the transcription JSONL files of `TRANSCRIPTION-BRIEF.md` for the sources `asi-ar-1903-04` (Bloch, Basarh), `asi-ar-1913-14` (Spooner, Basarh), `asi-ar-1911-12` (Marshall, Bhita) and `mahadevan-2003` (Tamil-Brahmi), with the extra fields named in their run briefs (`scan`, `legend_nagari_as_printed`, `table`, `row`, `script_stage`, `literal_rendering`, `figure`, `section_refs`). Output: records in the form of `SCHEMA.md` for the corpora `ia-ganges` and `ta-brahmi`.

- Transliteration: for the three Survey sources convert the older convention to IAST (`chh` → `ch`, then `ch` → `c`, `sh` → `ṣ`, `ṛi` → `ṛ`, `ṁ` → `ṃ`, `ç` → `ś`), lower-case, NFC. Mahadevan's transliteration is kept. Remove the editor's brackets and question marks from the forms used for units and words, and set `completeness` (`restored` when brackets mark restored letters but the legend is whole; `damaged-edge` when the editor marks the first or last letters lost; `damaged-internal`; `illegible`; `no-legend`) and `reading_doubtful` from them and from the `doubtful`, `restored` and `illegible_part` fields.
- Words and members: words are the editor's space-delimited words; members are the hyphen-separated parts of a word.
- Sign units, by the rules of `SCHEMA.md` and `AMENDMENT-1.md`: Brahmi akṣaras with conjunct clusters for `ia-ganges`; separate consonant signs for `ta-brahmi`; anusvāra, visarga and candrabindu attach to the preceding akṣara; an initial or post-vowel vowel is its own unit; a word-final consonant is its own unit with `·`; hyphens are removed before forming units; spaces end units. Treat the aspirates (`kh gh ch jh ṭh ḍh th dh ph bh`) as single consonants. In `ta-brahmi`, `ḷ` is a consonant; in `ia-ganges`, a vowel.
- Lines: from `legend_lines_as_printed` when given (`line_division_basis: edition`), else one line (`none`).
- Identity by source (`PROTOCOL.md` section 4): Bloch entries are seal varieties attested by impressions (`genre: sealing`, `object_kind: clay-sealing`, `object_id` and `die_id` `bloch1903:<entry>`, `impressions` from the entry); Spooner entries are clay lumps with sub-entries for their impressions (`object_id` `spooner1913:<register>`, `record_id` per sub-entry, `die_id` `spooner1913-die:<entry><sub>`, aliases for every Bloch number Spooner equates with the seal as `bloch1903:<n>`, and the duplicate register numbers in a separate field `duplicate_objects`); Bhita entries 1–13 are seal dies or signets (`genre: seal`) and the rest sealings (`genre: sealing`), with `object_id` and `die_id` `marshall1911:<entry>`; Mahadevan rows are `mahadevan2003:T<table>.<row>`, seals and rings `genre: seal`, coins `genre: coin`. Sites: `Basarh` and `Bhita` for the Survey sources; for Mahadevan the site as given, normalised to the place name (a river bed at Karur gives `site: Karur` with the river bed in `findspot`); no site gives `site: null`.
- Language: the entry's language remark; else the rule of `AMENDMENT-1.md` with `language_rule` recorded.
- Tags from `lexicon-brahmi.tsv`, which you write and track: columns `form`, `tag`, `language`, `note`, holding general seal vocabulary of Sanskrit, Prakrit and Tamil (titles and honorifics such as `mahārāja`, `rājan`, `rāño`, `śrī`, `bhaṭṭāraka`, `kumārāmātya`, `yuvarāja`, `mahādevī`, `śreṣṭhin`, `sārthavāha`, `kulika`, `nigama`, `adhikaraṇa`, `kō`; relations such as `putra`, `putrī`, `bhāryā`, `makaṉ`; deities; the places Vaiśālī and Tīrabhukti). A member matches a form exactly or after removing one ending from a declared list of case endings (Sanskrit `-sya -asya -āyāḥ -yāḥ -aḥ -ā -am -aṃ -e -ena`, Prakrit `-sa -asa -iye -ye`, Tamil `-aṉ -ṉ`), the longest first. A member that matches nothing is tagged `NAME` with `tag_source: default-name`. Write a local review table (`--review` path) listing every member with its tag, tag source and count.
- Every record gets `transcription` (method and transcriber from the input) and `rights` from a `--rights` JSON mapping source id to status.

## 3. `validate_records.py`

Checks every record of any corpus against `SCHEMA.md`: required fields present and typed; `units` equals the concatenation of `word_units`; one `line_of_word` per word and indices within `lines`; `lines` flattened equals `words`; one `tags` and one `tag_source` per member and members flattened per word; allowed values of `genre`, `object_kind`, `completeness`, `line_division_basis` and the tag set; unique `record_id`; `site` null only with a reason field. It writes a count of failures by check and exits non-zero on any failure.

## 4. `hd_stats.py`

Pure functions over lists of legends, each legend a sequence of units (strings), and, for `word.S4` and `word.S5`, a sequence of tagged members. Implement exactly the statistics of `PROTOCOL.md` section 7:

- normalized entropy of a counter, divided by log₂ of the number of distinct units in all positions of the legend set; 0.0 when that number is at most 1 (the step 6 convention);
- `S1` = normalized entropy of first units − of last units;
- `S2` = share of legends whose last unit is among the three commonest last units, ranked by count descending and then by the unit string;
- `S3` = share of legends whose last unit is among the ⌈|T|/10⌉ commonest last units (same ranking) minus the mean of that share over 200 within-legend shuffles, the stock recomputed on each shuffle, with the shuffle seed derived from the caller's seed;
- `S4` = (title-then-name − name-then-title) / their sum over adjacent members in reading order across word boundaries; null when the sum is 0;
- `S5` = (numeral-first − numeral-second) / their sum over adjacent pairs of a `NUMBER` member and a member tagged neither `NUMBER` nor `GRAM`; null when the sum is 0;
- `S6` = over words of at least two sign units, normalized entropy of their first signs − of their last signs, the inventory being the signs of those words; null below 20 such words.

## 5. `discriminate.py`

`python -I experiments/2026-10-21-head-direction-corpora/discriminate.py --records <jsonl> [<jsonl> …] --out <new directory> [--replicates 2000] [--synthetic]` implements `PROTOCOL.md` sections 4, 8 and 9 and `AMENDMENT-1.md`:

1. Group the records of each corpus by union-find over shared `die_id`, shared aliases and identical sign-unit sequences; choose one record per group (`complete` before `restored`, then more units, then the smallest `record_id`); a legend is eligible when the chosen record is `complete` or `restored`. Sign level and `within.S6` use eligible legends of at least two sign units; word level, at least two words; `word.S4` and `word.S5`, eligible legends of at least two words with at least one counted pair.
2. The `ta-brahmi` population is genre `seal` (seals and rings); at a level where it holds fewer than 25 eligible legends it becomes seals, rings and coins, flagged; with still fewer, `ta-brahmi` does not enter.
3. Primary corpora: head-final `ia-ganges`, `ta-brahmi`; head-initial `sux-ur3`, `akk-sargonic`. A corpus enters a statistic with at least 25 eligible legends (15 for S4 and S5). n = min(400, ⌊0.8 × smallest entering eligible set⌋). R replicates; in replicate r each entering corpus draws n legends without replacement with the seed `2026-10-21-head-direction-corpora:<statistic>:<corpus>:<r>`. Report per corpus: eligible count, n, median, 5th and 95th percentiles, share of null replicates.
4. Keep rule (section 9): testable with at least two entering corpora per group; kept when (1) the medians are completely separated, which fixes the direction; (2) at least 95% of replicates are completely separated in that direction, a replicate with any null value counting as not separated; (3) every entering corpus is non-null in at least 99% of replicates. Report the three conditions, the direction, the gap between the nearest medians, and the chance probability of complete separation under exchangeable corpora, 2·h!·i!/(h+i)! for h and i entering corpora.
5. Reported beside the decision: `sux-sargonic` at the same n when large enough; sub-corpora (by `source` for `ia-ganges`; by genre for `ta-brahmi`; by `site` for `sux-ur3` and `akk-sargonic`, each with at least 15 eligible legends) drawn at their own common n with the seed prefix `…:sub:`, with whether every head-final sub-corpus median lies on the head-final side of every head-initial one; the run without records marked `reading_doubtful`; the run with `ia-ganges` restricted to Sanskrit; and for `S1` at sign and word level the step 6 within-legend shuffle reference on each corpus's full eligible set (1,000 shuffles: observed value, shuffle mean, 2.5th and 97.5th percentiles).
6. Write `summary.json` with `schema_version`, the SHA-256 of `PROTOCOL.md`, `SCHEMA.md`, `TRANSCRIPTION-BRIEF.md`, `AMENDMENT-1.md`, every code file and every input, R, the seed prefix, the eligibility counts per corpus and level, and every result above. Refuse an existing output directory. `--synthetic` marks the output as synthetic.

## 6. `selftest.py` and the step 6 regression

`python -I experiments/2026-10-21-head-direction-corpora/selftest.py --work data/raw/2026-10-21-head-direction-corpora/codex-c/selftest-<n> --out experiments/2026-10-21-head-direction-corpora/selftest.json` runs:

- hand-calculated values of S1 to S6 on small legend sets, including ties in the rankings, a one-unit inventory, null cases and the shuffle reference;
- akṣara segmentation on general vocabulary written in the test itself (for example `putrasya` → `pu tra sya`; `mahārājasya` → `ma hā rā ja sya`; `kumārāmātyādhikaraṇasya` → `ku mā rā mā tyā dhi ka ra ṇa sya`; `saṃgha` → `saṃ gha`; `bhagavat` → `bha ga va t·`; `īśvara` → `ī śva ra`; Tamil-Brahmi `cāttaṉ` → `cā t· ta ṉ·`), the older-convention conversion (an invented word such as `Shreshṭhi-putrasya` → members `ṣreṣṭhi`, `putrasya`; `chh` and `ch`), ending removal and lexicon tagging;
- validator failures on deliberately broken records;
- grouping and eligibility on synthetic records with shared dies, shared aliases, identical legends and damaged duplicates;
- the keep rule on synthetic corpora: two head-final corpora with concentrated last units and two head-initial ones with concentrated first units must keep `sign.S1`; four corpora drawn from one generator must keep a statistic in about one third of 300 independent synthetic draws (report the rate and its binomial interval); a corpus below 25 legends must not enter; the Tamil fallback must switch populations;
- determinism: two runs with the same inputs give identical `summary.json` apart from timing fields;
- the step 6 regression: on the held file `data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl` (read with `-I`, never modified), take the records with `corpus == "sumerian"` and `kind == "seal"`, build each legend's sign sequence by concatenating `word_units`, keep the first occurrence of each distinct sign sequence of at least two signs (in file order), and compute `S1` at sign level with `hd_stats` on those legends; then build each legend's word sequence as the tuple of its `word_units` (each word a tuple of signs), keep those of at least two words, and compute `S1` at word level. The results must round to −0.204 (309 legends) and +0.079 (308 legends), the values of `experiments/2026-10-12-structure-first/step6-language/run-2026-10-12/summary.json` (`/profiles/sumerian_seals/sign_level/edge_asymmetry` and `/word_level/edge_asymmetry`). Compute only `S1` on this file; no other statistic of section 7 is computed on any real corpus.

## Deliverables

The files listed under owned paths, `selftest.json` with every check and its result, and `TOOLS.md` giving the order of commands from transcriptions and cuneiform records to `summary.json`, what each writes and where, and which outputs are tracked.

## Verification

1. `python -I experiments/2026-10-21-head-direction-corpora/selftest.py …` passes every check, including the regression.
2. `discriminate.py --synthetic` on a generated set of five corpora completes and writes a `summary.json` with every field of section 5.6.
3. No tracked file contains a legend or reading from a source; the test vocabulary is general and written by you.
4. `git status --porcelain` shows changes only inside your owned tracked paths.

## Final message

List every path you created, the selftest result with the regression values, the synthetic keep rate for exchangeable corpora, the command sequence, any point where the protocol was ambiguous and how you resolved it, and the time the run took.
