# Run C retrospective

Authors: GPT-6.1-Sol in the Codex desktop harness, 21 October 2026 UTC. We implemented the Brahmi normaliser, record validator, shared helpers, nine discrimination statistics and the protocol's primary and secondary reports. We used the standard library throughout and ran file-reading scripts under `python -I`.

## What we checked

The final command passed all ten check groups in 44.961 seconds:

```text
python -I experiments/2026-10-21-head-direction-corpora/selftest.py --work data/raw/2026-10-21-head-direction-corpora/codex-c/selftest-4 --out experiments/2026-10-21-head-direction-corpora/selftest.json
```

The [tracked selftest report](../../selftest.json) records hand calculations for S1–S6, ranking ties, null cases, the shuffle reference, general-vocabulary segmentation, older transliteration, every declared case ending, all four source identity conventions, normaliser and validator command execution, 22 deliberately broken record cases, transitive grouping, Tamil fallback, pair-specific thresholds and the keep rule's boundaries. It records the code hashes used by the final test.

Two invocations of the full synthetic discrimination command produced byte-identical summaries with all required sections. The first invocation was:

```text
python -I experiments/2026-10-21-head-direction-corpora/discriminate.py --records data/raw/2026-10-21-head-direction-corpora/codex-c/selftest-4/five-corpora.jsonl --out data/raw/2026-10-21-head-direction-corpora/codex-c/selftest-4/synthetic-run-1 --documents experiments/2026-10-21-head-direction-corpora --replicates 24 --synthetic
```

The second used `synthetic-run-2` as its output directory. Both hold five generated corpora and all nine statistics, sub-corpus reports, both sensitivity panels, the secondary Sumerian comparison, S1 shuffle references and hashes. Existing output directories are refused. The primary sign S1 positive control was kept in the expected direction. The sensitivity without doubtful records recomputed n from 20 to 28, including the declared Tamil population switch.

The exchangeability test kept sign S1 in 106 of 300 independent synthetic draws, a rate of 0.353333, with a Wilson 95% binomial interval of 0.301408–0.408967. Each draw used eight matched replicates and the same generator for all four corpora. Its corpus values are stable under subsampling because the common internal inventory is present in every legend. An exhaustive check of the 24 orderings of four values kept eight, reproducing the probability of one third.

The held step 6 regression reproduced 309 distinct sign legends and 308 word legends. Sign S1 rounds to −0.204 and word S1 to +0.079; the exact values are in the selftest report. Their differences from the earlier stored values are within `1e-12`. The held file's SHA-256 was unchanged. This was the only computation on real comparison records, and it computed S1 alone.

## Failures and repairs

The first attempt passed the synthetic checks and the regression's population and rounded-value assertions. Its final comparison failed because the earlier summary stores `edge_asymmetry` as an object. We corrected the lookup to its `asymmetry_initial_minus_final` field. The report remains at `data/raw/2026-10-21-head-direction-corpora/codex-c/selftest-1-result.json`. The second attempt passed all ten groups.

An added Tamil pair-threshold test then failed because its fixture put an OTHER member between the title and name. We supplied an adjacent pair in the fixture and retained its failed report as `codex-c/selftest-3-result.json`, with work in `codex-c/selftest-final/`. The fourth attempt passed. No failed report or synthetic output was overwritten.

Review of the eligibility code also led us to retain the counts and full-set S1 description of Tamil populations that are too small to enter. Their exclusion from matched sampling is explicit. Further tests check that a qualifying Tamil word population can enter S4 with 15 pair-bearing legends, that separate impressions on one clay lump stay separate, and that duplicate object numbers do not become legend aliases.

## Handoff

[TOOLS.md](../../TOOLS.md) gives the normalization, validation, test and production command sequence. [NOTES-CODEX.md](NOTES-CODEX.md) records the literal older-convention conversion, missing collection-language defaults, gap markers, alias formats, word identities, Tamil thresholds, quantiles, sub-corpus sample size and shuffle seeds. The source-rules interface lets reviewed collection statements supply missing metadata without modifying the transcriptions. No source was acquired, no source legend was placed in a tracked file, and no object coverage claim changed.

The workspace contained unrelated changes before this run, and concurrent contributions remained present. We used read-only Git commands with a per-command ownership exception and preserved those changes. Local status snapshots and the created-path inventory are under `data/raw/2026-10-21-head-direction-corpora/codex-c/`.

The synthetic controls support a methodological claim: stable differences between exchangeable corpora can pass the full keep rule at about the stated probability of one third. The reviewed comparison run will decide which statistics separate the actual traditions under the frozen protocol.
