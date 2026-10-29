# Shared evaluation harness: results

13 October 2026. Author: GPT-6.1-Sol, Codex API. This is a tooling and source-reproduction package. It adds five task commands under `bench/`, a versioned JSON envelope, source-pinned imports and a shared-round confirmation loader.

The final selftest passed all five tasks. All 50 local numerical comparisons matched their original endpoints, and all 17 interface checks passed. [Selftest](selftest-final.json), [comparisons](reproduction-final/comparisons.json), [interface cases](interfaces-v1.json).

## Generated controls

The known synthetic key stood 134.37 SD above its within-band rearrangements and passed the overall, order-only and grouped-half checks. The scrambled and random keys failed, as did the reversed-transition rival model. This generated grammar differs from the original study's running-text law. The original power separations, recalculated from its preserved aggregate scores, were Sanskrit 27.38, Latin 33.17, Tamil 37.15 and Sumerian 72.47 SD.

The planted large meaning-map effect passed. Under no effect, 7 of 100 trials passed, a rate of 0.07 against the nominal 0.05. The selftest retains a Wilson interval and the predeclared binomial tolerance. Its normal-law power rates are recorded for effects 0, 0.25, 0.5 and 1.5 response-noise SD. Additional design-shaped and categorical planting checks preserve shared object responses in [the interface output](interfaces-v1.json).

The loader checks passed for alias/text closure, the short-tablet exception, disjoint components, a whole-round freeze, changed predictions, site-proxy stripping, spending and a second seed's attempted reuse. Restoration and segmentation hand cases matched their stated arithmetic. Input checks reject invalid rankings/probabilities, mismatched queries and incomplete boundary coverage, and preserve existing output bytes.

## Local source comparisons

The table gives every reproduced number and its original witness. Score comparisons use absolute tolerance 1e-12; count comparisons require equality. The largest score difference is floating-point summation order. Imported source paths and hashes accompany the task outputs.

| Measurement | Original | Bench | Original witness |
|---|---:|---:|---|
| key-calibration: published key G | -0.39312362245075921 | -0.39312362245075572 | [source](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/stage3/summary.json) |
| key power arithmetic: sanskrit | 27.378769491253696 | 27.378769491253696 | [source](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/stage5/summary.json) |
| key power arithmetic: latin | 33.172836578943034 | 33.172836578943034 | [source](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/stage5/summary.json) |
| key power arithmetic: tamil | 37.147065531376704 | 37.147065531376704 | [source](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/stage5/summary.json) |
| key power arithmetic: sumerian | 72.471078593225457 | 72.471078593225457 | [source](../../experiments/2026-10-12-published-claim-tests/sanskrit-key/stage5/summary.json) |
| shots: faces | 5680 | 5680 | [source](../../experiments/2026-10-12-conjecture-shots/split-summary.json) |
| shots: components | 4104 | 4104 | [source](../../experiments/2026-10-12-conjecture-shots/split-summary.json) |
| shots: discovery families | 2349 | 2349 | [source](../../experiments/2026-10-12-conjecture-shots/split-summary.json) |
| shots: confirmation families | 2346 | 2346 | [source](../../experiments/2026-10-12-conjecture-shots/split-summary.json) |
| meaning-map: Shot B primary S | -0.56665866838106593 | -0.56665866838106593 | [source](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json) |
| meaning-map: Shot B distance SD | -0.43557086370047338 | -0.43557086370047338 | [source](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json) |
| meaning-map: Shot B p | 0.67013298670132981 | 0.67013298670132981 | [source](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json) |
| restoration: Markov2 top1 | 0.37270570608065928 | 0.37270570608065928 | [source](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json) |
| restoration: Markov2 top5 | 0.58871269821450867 | 0.58871269821450867 | [source](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json) |
| restoration: Markov2 top10 | 0.65451367211886624 | 0.65451367211886624 | [source](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json) |
| restoration release v1: inscription_number_accuracy | 23 | 23 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v1: classification_exact_accuracy | 19 | 19 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v1: strict_top1 | 0.74531835205992514 | 0.74531835205992514 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v1: strict_top5 | 0.83895131086142327 | 0.83895131086142327 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v2: inscription_number_accuracy | 62 | 62 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v2: classification_exact_accuracy | 55 | 55 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v2: strict_top1 | 0.70738636363636365 | 0.70738636363636365 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v2: strict_top5 | 0.86363636363636365 | 0.86363636363636365 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v2: source_row_recall random recall | 0.96578538102643852 | 0.96578538102643852 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v3: inscription_number_accuracy | 71 | 71 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v3: classification_exact_accuracy | 72 | 72 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v3: strict_top1 | 0.80054644808743169 | 0.80054644808743169 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v3: strict_top5 | 0.92349726775956287 | 0.92349726775956287 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v3: source_row_recall random recall | 1 | 1 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| restoration release v3: physical_line_recall random recall | 1 | 1 | [source](../../maintenance/2026-10-08-hf-public-release/release/benchmark/expected-metrics.json) |
| segmentation cohort count: sumerian_seals_all | 309 | 309 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_seals_all/branching_entropy | 0.69221924108853972 | 0.69221924108853972 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_seals_all/greedy_ngram | 0.43924101735970933 | 0.43924101735970933 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_seals_all/all_boundaries | 0.5571462098099037 | 0.5571462098099037 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_seals_all/no_boundaries | 0 | 0 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation cohort count: sumerian_lines_matched | 1859 | 1859 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_lines_matched/branching_entropy | 0.34013867488443761 | 0.34013867488443761 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_lines_matched/greedy_ngram | 0.605744822979292 | 0.605744822979292 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_lines_matched/all_boundaries | 0.67539682539682544 | 0.67539682539682544 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: sumerian_lines_matched/no_boundaries | 0 | 0 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation cohort count: egyptian_glyph_sentences_matched | 940 | 940 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: egyptian_glyph_sentences_matched/branching_entropy | 0.32453721937770774 | 0.32453721937770774 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: egyptian_glyph_sentences_matched/greedy_ngram | 0.38701382192221151 | 0.38701382192221151 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: egyptian_glyph_sentences_matched/all_boundaries | 0.34978951396861846 | 0.34978951396861846 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: egyptian_glyph_sentences_matched/no_boundaries | 0 | 0 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation cohort count: akkadian_letter_lines_matched | 1223 | 1223 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: akkadian_letter_lines_matched/branching_entropy | 0.36819244904777815 | 0.36819244904777815 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: akkadian_letter_lines_matched/greedy_ngram | 0.41112167300380231 | 0.41112167300380231 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: akkadian_letter_lines_matched/all_boundaries | 0.35763576357635762 | 0.35763576357635762 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |
| segmentation F1: akkadian_letter_lines_matched/no_boundaries | 0 | 0 | [source](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json) |

The key comparison rescores the published assignment under its preserved dense model. Shot B recomputes its frozen measures and feeds them to the common rearrangement engine, including the original 10,000-draw seed. Restoration rescores saved masked predictions and the original JSON parents of all three visual-row/page releases. Segmentation rebuilds the four readable cohorts and reruns branching entropy, greedy n-grams and both trivial baselines. These are source reproductions, with no retraining of the historical restoration models.

## Population and preserved scope

The new October 13 seed gives 2,341 discovery and 2,354 confirmation families in 4,104 components. [Manifest](round-1.json) and [aggregate summary](round-1-summary.json). It inherits seal-size, site and motif exposures from the October 12 input. No confirmation statistic was read through this new round. Its real-population freshness requires source and object-identity review.

The currently held line-break list contains the corrected 69 faces and 73 required divisions. The re-score finds branching-entropy hits 26/73 and 41/73 under the two line orders, and greedy hits 70/73 and 64/73. [Current re-score](reproduction-final/segmentation-lines.json). The earlier reviewed endpoint used 72 faces and 76 divisions. Its 29/76 and 44/76 branching figures remain in the original report. This source-population change is preserved explicitly; the current results are not presented as a reproduction of those older division counts. Precision/F1 remain null for these positive-only labels.

The full 2,000-sweep DP rehearsal and the original multilingual blind-annealing power study were not rerun. The task can invoke the original DP scorer; the required segmentation source number is reproduced by the fast methods. The four original key-power distances are aggregate arithmetic reproductions, while the new key controls use independently generated plaintext and the same current scorer as real inputs. Joint planting of multiple predictions on one variable requires a separately declared generative law; the generic power command rejects that case rather than silently overwriting responses.

All scientific outputs here are aggregates or generated controls. Acquired texts, full real sign sequences and source images were read in place and not copied into either owned directory. Earlier implementation endpoints remain in `selftest-v1.json`, `selftest-v2.json`, `reproduction-v1/` and `reproduction-v2/`. [Changed paths and sources](CHANGES.json), [complete created-path inventory](PATHS.json).

## Commands and coordinator checks

```text
python -m bench selftest --directory experiments/2026-10-13-bench/selftest-shot-fixtures-final --out experiments/2026-10-13-bench/selftest-final.json
python -B experiments/2026-10-13-bench/reproduce.py reproduction-final
python -B experiments/2026-10-13-bench/check_interfaces.py interfaces-v1.json
python tools/review_prose.py --path bench --no-write
python tools/review_prose.py --path experiments/2026-10-13-bench --no-write
```

These endpoints now exist; choose new names when rerunning. The coordinator should repeat the synthetic controls and source comparisons, inspect closure and read logs, review population freshness and the partial line labels, and integrate the proposed shared text in [INTEGRATION.md](INTEGRATION.md). This author-performed reproduction does not supply an independent verification tier. The coordinator's prompt, launcher and other contributors' packages are unchanged. No network call, CI workflow or Git mutation was made.

Both final prose scans report zero flags. The shared knowledge check reports one error: `knowledge/MAP.md` differs from a fresh build. [Check log](kb-check.log). The map is outside this package's edit scope; the coordinator rebuilds it after integrating the new retrospective and proposed records.

The strongest supported claim is that the shared scorers distinguish a known generated encoding from its scrambled controls while preserving the project's recorded scores. The deciding next check is an independent contributor's rerun, followed by a frozen prediction on newly reviewed object evidence.
