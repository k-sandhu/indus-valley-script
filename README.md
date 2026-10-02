# Indus Valley script research knowledge base

This repository preserves evidence, methods, manuscripts, exploratory ideas and failed approaches from an ongoing Indus script investigation. It currently contains **no authenticated translation, sound value, language identification or decipherment**.

The repository is private. Its local equivalent is this project folder. No CI/CD workflows are included; scripts are reusable research tools run manually. Review input and derived material before any future public release.

## Start here

| Purpose | Read |
|---|---|
| Findings available for reuse and discussion | [Research contributions](knowledge/research-contributions.md) |
| Evidence we have and need for decipherment | [Decipherment readiness review](knowledge/directions/decipherment-readiness-2026-10-02.md) |
| New numerical connections and independent publication assessment | [Regional connection findings](knowledge/directions/regional-numerical-connections-2026-10-02.md), [study records](experiments/2026-10-02-connections-and-priority/README.md) |
| Original sources that change the numerical candidates | [Source recovery findings](knowledge/directions/source-recovery-2026-10-02.md), [source audits and registered views](experiments/2026-10-02-source-recovery/README.md) |
| Graphic prediction and restoration | [Paper 001](papers/001-artifact-aware-prediction/manuscript.md) |
| Conditional sampling and related records | [Paper 002](papers/002-conditional-reference-laws/manuscript.md) |
| Numerical constraints and physical observations | [Paper 003](papers/003-physical-observations/manuscript.md) |
| Selecting a record model before mapping symbols | [Paper 004](papers/004-reference-model-selection/manuscript.md) |
| Detailed statistical methods | [Methods](papers/001-artifact-aware-prediction/methods.md) |
| What is established, exploratory, failed or untested | [Knowledge index](knowledge/INDEX.md), [experiment registry](knowledge/experiments/registry.json) |
| What we tried and how problems were resolved | [Retrospectives](knowledge/retrospectives/README.md) |
| New research directions and priorities | [Research roadmap](knowledge/directions/research-roadmap.md) |
| Cryptography framing and recent model results | [Cryptography memo](knowledge/directions/cryptography.md) |
| Completed six-hour investigation | [Session record](experiments/2026-10-02-six-hour/SESSION_LOG.md) |
| Source identity, rights and catalogue caveats | [Sources](knowledge/provenance/SOURCES.md), [redistribution](knowledge/provenance/REDISTRIBUTION.md) |
| Original completed report | [18-page report](output/pdf/indus_script_research_report.pdf) |
| Inspect the 687-cell chart | [Local interactive atlas](output/chart_atlas/index.html) |
| Repeat an analysis without rediscovering prior failures | [Reproduction guide](REPRODUCING.md), [contribution guide](CONTRIBUTING.md) |

## Current empirical position

The first investigation began October 1, 2026 and ran for four hours and two minutes. Its code and evidence paths are preserved under `src/`, `research/`, `results/` and `output/`. The original README and import manifest are retained in [the archive](archive/2026-10-01-investigation/README.md).

- In the unique-text evaluation, local sequential dependencies improved predictive log score by approximately **0.848 bits per noninitial sign** under the declared filters and controls.
- Artificial one-known-slot restoration reaches **37.27% exact top-one** with second-order context, compared with **34.59%** for first order and **33.81%** for the earlier local model on the same **8,009 masks**. Second order has greater probability loss; loss-based tuning selects first order in every fold.
- A different annotation of shared archaeological sources retained a positive candidate-event score gain after source/text-overlap exclusions.
- Unknown gap-count prediction **failed** to beat the constant-one control: **46.3% versus 51.1%**.
- A published numerical proposal has four positive-integer solutions before an additional archaeological range restriction. The selected 10/8/6 values remain conditional on the proposal's unverified premises.

These measurements describe graphic-code prediction in selected transcriptions, including artificial masking and alternate annotation of shared sources. The manuscript's claim-evidence map defines each population and outcome; the [priority audit](research/literature/evidence_and_novelty_matrix.md) places the methods alongside earlier Markov, duplication-control and administrative-system research.

The current continuation also has exact sampling-law examples, known-system mapping controls, numerical acquisition studies and source frames for Harappa, Lothal and Kanmer. At a nominal 5% threshold, literal-copy simulations reject 5.4% with matched object references and 15.9% with record-wise references; imperfect-face simulations give 5% and 11%. A reference-only model selector recovers 309 of 384 simulated symbol maps, compared with 283 for graph mapping and 168 for slot mapping alone. A complete-inventory constraint increases numerical recovery from 133 to 190 of 200 worlds with four incorrect local assignments. The [session record](experiments/2026-10-02-six-hour/SESSION_LOG.md) links each experiment, its preserved failures and its independent review.

## Repository organization

```text
papers/       complete manuscript drafts, detailed methods, evidence maps
knowledge/    indexed findings, retrospectives, directions, source caveats
experiments/  dated new protocols and their separately recorded results
research/     preserved original plans, audits, source notes and experiments
src/          reusable original and exploratory analysis code
results/      preserved root experiment outputs, including superseded results
output/       original report, atlas, summaries and verification manifests
archive/      original README, import record, historical documentation
tools/        manual preservation, indexing and verification utilities
data/         locally preserved inputs; bulk inputs excluded from Git
templates/    experiment and source-review templates for future work
```

No top-level blanket licence is assigned to third-party material. See [reuse status](REUSE.md). The local import preserves acquired inputs and source witnesses; Git contains our written findings, reusable code, selected resources, summaries, and acquisition/provenance records. A GitHub checkout alone therefore does not contain every input required for all original analyses.

## Research memory rule

Before a new run, search [the registry](knowledge/experiments/registry.json), the retrospectives and `research/`. Revisit an unsuccessful path when a named new dataset, method, corrected assumption or independent source makes the retry informative. Keep the old endpoint and explain the change. Interesting imaginative proposals belong in the knowledge base with an explicit test and a status; they do not become readings by repetition.
