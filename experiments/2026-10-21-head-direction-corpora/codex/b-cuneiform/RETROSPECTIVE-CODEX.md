# Cuneiform corpus run

We built 31,512 Ur III Sumerian records, 89 Sargonic Akkadian records and 175 Sargonic Sumerian records. Before grouping or eligibility decisions, they contain respectively 8,056, 74 and 122 distinct sign sequences of at least two signs, and 7,966, 69 and 110 distinct sign sequences in legends of at least two words. Their null-site counts are 992, 21 and 65. The outputs preserve damaged and unreadable legends, competing editions and unresolved catalogue cases.

The contributor is Codex in the GPT-6 family through the Codex API tool harness; the exact model identifier is not exposed. We wrote `PLAN-CODEX.md` before acquisition or code changes. We read the protocol, schema, transcription brief, acquisition helper, earlier normaliser and relevant research and redistribution records. This run acquires and normalises sources. It computes no statistic from protocol section 7 and reads no Indus legend.

## Sources and reproduction

The held archive has 561,755,376 bytes and SHA-256 `b220f3ee0707912d3c9c7dd5532b00a55248ba5f7b9c81ff5df121c53da69d92`, matching the supplied manifest. We parsed all 80,181 entries. The Old Akkadian download has 29,933,476 bytes and 5,472 entries. Both catalogues and all their JSON entries declare CC0. The three CDLI files came from the supplied commit URLs; their README dates the dump to August 2022. Every successful acquisition was checked again for its size and hash, and the media payloads are not Git LFS pointers. [SOURCES.md](SOURCES.md) gives every URL, size, hash, rights status and use.

Seven attempts to authenticate the ORACC connection failed. The shared urllib fetcher could not build the certificate chain with the available certificate stores and bundles. WinHTTP and native curl also failed. The eighth attempt downloaded the anonymous public file through the shared fetcher with peer authentication unavailable. Its acquisition record states that limitation. We checked the ZIP member names before reading any archive content. No downloaded code was imported or executed.

The earlier normaliser was present. We read it and copied its ORACC traversal, clean predicate, GDL unit rules and legacy categories into our own module. Reconstructing the specified 3,000-entry sample matches all 522 held seal records exactly across every original field: zero differences and zero extra records. It also recovers their 309 distinct sequences of at least two signs. The extended records retain those words, units and source word references. Their `gold` arrays contain raw ORACC POS codes, as required; the old broad categories belong to the separate reproduction projection. Exact results are in `codex-b/run-v6/reproduction.json` and the tracked counts.

## Repairs and retained evidence

The first inspection helper used the source id without the manifest key's `.json` suffix. We corrected that lookup and repeated the hash check in a new directory. Draft normalisations then exposed citation forms that differ from their written words. The lexicon now matches citation form with guide word, with whole-word spellings and explicit POS fallbacks recorded separately.

The coverage audit found two physical seals and direct sealings whose legends occur in the body without a seal-surface marker. We included those catalogue-defined cases. The final audit reports no missing physical seals or direct sealings in either archive, all 728 CDLI Old Akkadian catalogue seal entries represented, and no object retaining both source editions in the primary records. Superseded CDLI sections remain in `cuneiform-edition-alternates.jsonl`.

We corrected CDLI language provenance to `editor`, since its ATF headers supply the language declarations. ORACC token labels remain `token-language`. Equal word counts and other unresolved languages go to a separate file. A mixed-period catalogue entry is preserved in its own ledger.

The seeded manual check caught an object-type priority error. Generic ATF tablet directives had overridden more specific catalogue types such as bulla and envelope. We saved the former outputs in `codex-b/endpoint-v5-before-object-kind-repair/`, their counts in `counts-v5.json` and their code in `normalize_cuneiform-v5.py`. The final repair changes 1,593 object classifications and adds 25 unresolved composite-identity flags. `object-kind-repair.json` confirms zero unexpected differences, including no changes to text, units, tags, languages or membership.

The device filled while writing a draft manual-check packet. We preserved that failed directory and recovered space by removing only catalogue extracts whose byte hashes matched retained copies. The archives, corpus outputs and review evidence remain. `storage-repair.json` names the retained copies and the removed duplicates. The earlier draft output directories remain under `codex-b/`.

## Final commands and checks

The final normalisation was run from the repository root with this command. Reproduction requires fresh output, scratch and count paths because the script refuses existing output files.

```powershell
python -I experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/normalize_cuneiform.py --ur3-archive data/raw/2026-10-12-bronze-age-comparison/acquisition/sumerian-ur3-v1/response.bin --ur3-manifest data/raw/2026-10-12-bronze-age-comparison/normalized-v4/manifest.json --held-records data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl --oakk-archive data/raw/2026-10-21-head-direction-corpora/src-oracc-oakk-archive-v8/oakk.zip --cdli-cat data/raw/2026-10-21-head-direction-corpora/src-cdli-data-cat-v1/cdli_cat.csv --cdli-atf data/raw/2026-10-21-head-direction-corpora/src-cdli-data-atf-v1/cdliatf_unblocked.atf --lexicon experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/lexicon-cuneiform.tsv --output-dir data/raw/2026-10-21-head-direction-corpora/normalized --scratch-dir data/raw/2026-10-21-head-direction-corpora/codex-b/run-v6 --counts experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/counts.json --acquisition-record experiments/2026-10-21-head-direction-corpora/acquisition/oracc-oakk-archive-v8.json --acquisition-record experiments/2026-10-21-head-direction-corpora/acquisition/cdli-data-cat-v1.json --acquisition-record experiments/2026-10-21-head-direction-corpora/acquisition/cdli-data-atf-v1.json --acquisition-record experiments/2026-10-21-head-direction-corpora/acquisition/cdli-data-readme-v1.json
python -I experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/validate_outputs.py --records-dir data/raw/2026-10-21-head-direction-corpora/normalized --counts experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/counts.json --schema experiments/2026-10-21-head-direction-corpora/SCHEMA.md --out experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/validation-v6.json
python -I tools/review_prose.py --path experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform --no-write
```

The independent validator checks all 32,366 primary and outside-corpus records. All 808,580 assertions pass, including required fields, object identifiers, parallel arrays, member tags, line membership, NFC and count agreement. `coverage-v6.json` records the final coverage audit. The normalisation itself took 242.953 seconds; `RUN-TIMING-CODEX.json` records the measured session duration from the plan's creation.

We drew ten records per corpus with seed `b-check` and compared the archived source words, line divisions, damage, tags and metadata by hand. All 30 text and line comparisons match after the declared normalisation. The source packets stay local in `codex-b/check-v6/`; `hand-checks.json` records the identifiers and the source qualifications. Separate live-page checks were not made because the allowed network URLs name the archive and dump files. The object-type defects found during this review were repaired, and composite identities and language conflicts remain explicit review cases.

The prose scan has no flags in our authored Markdown. Flags in the supplied, unchanged `CODEX-PROMPT.md` and `TASK.md` are retained. The repository was already dirty with concurrent work. We used read-only Git commands, left those changes untouched and limited our writes to the owned paths. `FILES-CODEX.json` inventories created files and retained diagnostics; `PATH-AUDIT-CODEX.json` records the final ownership check.

## What remains

[REVIEW-DECISIONS-CODEX.md](REVIEW-DECISIONS-CODEX.md) collects the decisions needed before analysis: physical links for 25 composite editions, 88 language review cases, mixed legends, null sites, chronology conflicts, four readable CDLI alternatives to unreadable ORACC sections, and questioned or unlisted lexical assignments. An authenticated independent copy of the Old Akkadian archive and separate live-page checks remain external verification steps.

We now have a complete record of the selected source entries and their seal legends, including the cases that could change the comparison population. A philological and object-identity review of the flagged records will decide whether the language split made from the source annotations and its physical-object links support the intended comparison.
