# Shared evaluation harness: instructions for GPT-6.1-Sol

You are packaging the project's evaluation procedures as one harness, `bench/`, so that any contributor or agent who proposes a reading, a segmentation, a restoration model or a conjecture runs the same calibrated tests. The repository root is `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (Windows; Python 3.13 as `python` with numpy 2.2, scipy 1.17 and scikit-learn 1.9; Git Bash and PowerShell). Today is 13 October 2026. A coordinating Claude session wrote these instructions and will review the result. Four other agents are writing data packages under `experiments/2026-10-13-*` right now; leave them alone.

The lesson behind this harness, from the project's own record and from other multi-agent efforts: agents optimise whatever test they are given, so the test must be close to perfect. Fitting a sign key or meaning map to the Indus corpus is cheap (random consonant strings pass a lexical readability test 92–100% of the time), so a claim counts only when it stands clear of rearrangements of itself, or predicts material it was not built from.

## 1. Read first

`AGENTS.md`, `knowledge/editorial/WRITING.md`, `knowledge/provenance/REDISTRIBUTION.md`, `LICENSE`, `knowledge/directions/key-calibration-2026-10-12.md` and the code it cites in `experiments/2026-10-12-published-claim-tests/` (the Sanskrit key study: rearrangement nulls, language models, the synthetic power analysis), `experiments/2026-10-12-conjecture-shots/DESIGN.md`, `shots_common.py`, `REVIEW-RESPONSE.md` (its seven rules for later shots), the restoration benchmark and scorer in `experiments/2026-10-08-hf-public-release/` (README and `release/benchmark`, `release/code`), `papers/001-artifact-aware-prediction/methods.md`, the segmentation scoring of `experiments/2026-10-12-structure-first/step3-segmentation/` and `step5-rehearsal/`, and `tools/kb.py`. Search with `python tools/kb.py search calibration` and similar before writing anything new; reuse code by importing or by copying with a recorded source path and hash.

## 2. What to build

Create a Python package `bench/` runnable as `python -m bench <task> ...` from the repository root, standard library plus numpy and scipy only. Each task has a stable command-line interface, a JSON output with a schema version, a `--synthetic` mode that runs on generated data shipped or generated inside the repository, and the same code path for real local data when it is present.

1. **`key-calibration`**: given a proposed sign-to-value key (JSON) and a language model or word list, score the key on the corpus and on rearrangements of its own values among signs of matched frequency, as the calibration memo specifies; report the score, the rearrangement distribution, the distance in standard deviations and the transfer test across held-out halves and across unrelated languages where models are available. `--synthetic` builds an Indus-shaped corpus by encoding a known text with a known homophonic key, so a correct key, a scrambled key and random keys can be compared; report the separation the published-claim tests found (a correct key stands 27 to 72 standard deviations clear).
2. **`meaning-map`**: the rearrangement test for class or gloss maps against object properties, generalised from Shot B (`experiments/2026-10-12-conjecture-shots/shot-b-reading/confirm.py`): any map of sign to label, any set of declared directional predictions over object variables, within-band rearrangements, and a power report that plants effects of stated size. Include the review's lessons: report split-half reliability of each per-sign measure, and support an influence or rank criterion.
3. **`shots`**: create a new discovery/confirmation split for a new round of conjecture shots (same closure rules as `shots_common.py`, new seed), a sealed loader that requires frozen predictions with recorded hashes before the confirmation half opens and logs every read, and a ledger `bench/spent.json` recording which statistic families (for example seal size, site, motif) each split's confirmation half has been used for. The October 12 split's confirmation half is spent for seal size, site and motif statistics; record that. Do not modify `experiments/2026-10-12-conjecture-shots/`.
4. **`restoration`**: a stable wrapper around the existing restoration benchmark and scorer (Paper 001's known-slot masks and the Hugging Face release scorer), reproducing their recorded numbers on local data and running a synthetic check without it.
5. **`segmentation`**: boundary precision, recall and F1 against catalogued line divisions and against the readable-script cohorts of structure-first step 5, with the baselines those reports used.

For each task write `bench/<task>/README.md`: what the task answers, its inputs and outputs, the command, the pass rule a claim should meet, which local data it needs and how to get it (point to `knowledge/DATA.md` and `tools/fetch_data.py`), and the earlier results it reproduces with links.

Write `bench/README.md`: the purpose in one paragraph, the task table, the rule that every reading, key, meaning map or conjecture submitted to the project attaches the relevant bench output, and how results enter the registry.

## 3. Tests and verification

`python -m bench selftest` runs every task's synthetic mode and checks known answers: a correct synthetic key passes and scrambled or random keys fail; a planted meaning-map effect of large size passes and no effect fails at about the nominal rate; the restoration and segmentation scorers reproduce small hand-computed cases. On this machine, where local data exist, reproduce at least one recorded number per task from its original package and save the comparison. Save all outputs in `experiments/2026-10-13-bench/`.

## 4. Rules

- Edit only: `bench/**` and `experiments/2026-10-13-bench/**` (this prompt stays unchanged). Do not edit `AGENTS.md`, `README.md`, cards, the registry or any other file; write `experiments/2026-10-13-bench/INTEGRATION.md` listing the exact lines the coordinator should add to `AGENTS.md`, `CONTRIBUTING.md`, the skills and `knowledge/DATA.md`, and a proposed `registry-entry.json` (fields id, theme, status, question, outcome, challenge, remedy, evidence, retry_when, status_class, area).
- Never copy acquired corpus texts, sign sequences or third-party data into tracked files; synthetic data and aggregate outputs only. Real-data runs read local files and write their detailed outputs under `data/raw/2026-10-13-bench/`.
- No CI workflows, no network access needed, no `git commit`, `push`, `checkout`, `reset`, `stash` or `clean`.
- Write `PLAN.md` first, `CHANGES.json` as you go, and `RETROSPECTIVE.md` at the end.

## 5. Writing

Follow `knowledge/editorial/WRITING.md`. Maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Run `python tools/review_prose.py --path bench --no-write` and the same for your experiment directory.

## 6. Final message

Every path created; the selftest result; each reproduced number with its original; anything not finished and why; and what the coordinator should check.
