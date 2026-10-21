# Head-direction comparison corpora

Package of 21 October 2026 for question [Q-0037](../../knowledge/questions/Q-0037-design-a-head-direction-seal-comparison.md) and study 7 of [Taking Parpola's readings further](../../knowledge/directions/parpola-forward-2026-10-20.md). It acquires seal legends in two head-final languages (Indo-Aryan seals and sealings from Basarh and Bhita; Tamil-Brahmi seals, rings and coins) and two head-initial ones (Ur III Sumerian; Old Akkadian), normalises them to one record form, fixes the protocol that decides which statistics separate the two groups, and runs it on the readable corpora alone. No Indus legend is read or placed.

Contributors: Claude Opus 5.5 (Anthropic) in Claude Code, a side session of the project's main session, which chose the sources, made the rights decisions, wrote the protocol, the amendments, the edition rules and all prose, and reviewed every delegated output; Codex CLI 0.160.1 running GPT-6.1-Sol (`gpt-6.1-sol`, reasoning effort `xhigh`), which fetched and transcribed the sources, normalised the cuneiform corpora and wrote the statistics code under the briefs in [codex/](codex/).

## Reading order

1. [REPORT.md](REPORT.md): what was measured and what it supports.
2. [PROTOCOL.md](PROTOCOL.md) (hashed in [PROTOCOL.sha256](PROTOCOL.sha256) before any statistic), with [SCHEMA.md](SCHEMA.md) and [TRANSCRIPTION-BRIEF.md](TRANSCRIPTION-BRIEF.md), and the four amendments written before computation: [1](AMENDMENT-1.md) (unit rules), [2](AMENDMENT-2.md) (transliteration by source), [3](AMENDMENT-3.md) (editorial marks, code corrections, lexicon), [4](AMENDMENT-4.md) (corpus sizes, exclusions, a second panel).
3. [FEASIBILITY.md](FEASIBILITY.md): sources, object and site linkage, eligible legends, gaps and how to close them.
4. [RETROSPECTIVE.md](RETROSPECTIVE.md) and [RETROSPECTIVE-CODEX.md](RETROSPECTIVE-CODEX.md).
5. [DATA-UPDATE.md](DATA-UPDATE.md): new sources and coverage for the manifest.

## Outputs

[run-2026-10-21/summary.json](run-2026-10-21/summary.json) is the frozen run (entry threshold 25); [run-2026-10-21-threshold-20/summary.json](run-2026-10-21-threshold-20/summary.json) is the declared second panel of Amendment 4. [FROZEN-INPUTS.json](FROZEN-INPUTS.json) gives the hashes of every input, code file and document at the moment the runs started. [corpus-counts.json](corpus-counts.json), [selftest.json](selftest.json) and [bench-selftest.json](bench-selftest.json) hold the counts and tests; [exploratory-title-name-order.json](exploratory-title-name-order.json) and [exploratory-closing-units.json](exploratory-closing-units.json) hold the counts made after the runs, and [summarize_run.py](summarize_run.py) prints a run's tables. [QUESTION-UPDATES.md](QUESTION-UPDATES.md) proposes the card changes, and the registry entry is `knowledge/registry/attempts/HEAD-DIRECTION-CORPORA-2026-10-21.json`. Every tracked output holds aggregates, identifiers and hashes; legends, transcriptions and records stay under `data/raw/2026-10-21-head-direction-corpora/`.

## Reproducing

From the repository root with Python 3.13, after restoring the local sources (their URLs and hashes are in [acquisition/](acquisition/); the held Ur III archive is listed in DATA.md):

```text
python -I experiments/2026-10-21-head-direction-corpora/selftest.py --work <new local dir> --out <new json>
python -I experiments/2026-10-21-head-direction-corpora/normalize_brahmi.py --transcriptions <the four transcription files> --rights <rights.json> --lexicon experiments/2026-10-21-head-direction-corpora/lexicon-brahmi.tsv --source-rules <source-rules.json> --corrections <corrections.json> --out <brahmi.jsonl> --review <review.tsv>
python -I experiments/2026-10-21-head-direction-corpora/codex/b-cuneiform/normalize_cuneiform.py ...   (command in codex/b-cuneiform/RETROSPECTIVE-CODEX.md)
python -I experiments/2026-10-21-head-direction-corpora/adapt_cuneiform.py --records <corpus.jsonl> --out <corpus.adapted.jsonl>
python -I experiments/2026-10-21-head-direction-corpora/validate_records.py --records <all record files> --out <validation.json>
python -I experiments/2026-10-21-head-direction-corpora/discriminate.py --records <all record files> --exclusions <exclusions.json> [--minimum-legends 20] --out <new dir> --replicates 2000
```

The coordinator's local review inputs (rights, source rules, corrections and exclusions) are under `data/raw/2026-10-21-head-direction-corpora/review/`, and their hashes are in FROZEN-INPUTS.json.
