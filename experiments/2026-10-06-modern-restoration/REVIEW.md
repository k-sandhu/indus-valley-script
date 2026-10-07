# Review of package A: modern models on the Paper 001 restoration benchmark

## Verdict

The main results stand. Every headline number in README.md and REPORT.md reproduces: the three aggregate files regenerate byte for byte from the saved per-query predictions, my own code recomputes the accuracy table, all 20 paired contrasts, the learning curves and the seed ranges, and refitting modified Kneser–Ney (MKN, full inner grid, both text regimes), one GRU seed and one transformer seed on outer fold 0 returns bit-identical probabilities. The protocol was committed (00:02:54 on 7 October) before the first fit file (00:04:41), selection uses inner folds only, and an independent re-derivation of the extra-text pools finds no overlap with held-out objects or strings in the 5 outer and 15 inner allocations. The most important problem is the account of the 144–159 linked training strings per fold. The counts are right, but the report gives neither their source nor their size. Sixteen identical one- and two-sign texts on faces of different objects create all of them, joining 192 benchmark strings (748 queries, 9.3% of the benchmark). Training without the linked strings lowers top-one on those queries by 8.0 points for the saved first-order model, 9.0 for the saved second-order model and 5.9 for MKN, which is about 0.75, 0.84 and 0.55 points on the whole benchmark; removing the same number of unlinked strings changes them by less than 0.6 points. The ranking of the three refit n-gram models is unchanged and their paired differences move by at most 0.3 points. Three statements also need correction or completion: the extra-text loss gain comes almost entirely from 251 targets outside the training alphabet, frequency-stratum ECE says nothing about calibration, and the amendment understates what was known when the common-alphabet loss was added.

## Scope of this review

Reviewer: Claude Sonnet 5.5, 7 October 2026. Package produced by GPT-6.1-Sol (commit bbeaa4a, protocol snapshot commit 3183b4d). No package file was edited. What I wrote is this file, `review/` (scripts and aggregate JSON, no corpus text) and temporary files under `data/raw/2026-10-06-modern-restoration/review-tmp/` and `.../review/`, deleted at the end. Paths below are relative to `experiments/2026-10-06-modern-restoration/`. "Reproduced" means an identical file hash or identical arrays. "Recomputed" means my own code, which does not call the package's summary functions, gave the same value at the printed precision. Reproduction results have the status Verified computation. The link, near-variant and extra-text analyses are post hoc reviewer analyses (Exploratory) with the saved hyperparameters held fixed; they are not package results.

## Checked claims

| # | Claim | Evidence | Result | Note |
|---|---|---|---|---|
| 1 | Required files exist | README, PROTOCOL, REPORT, RETROSPECTIVE, `registry-entry.json`, `sources.json`, code, aggregates | confirmed | Registry entry uses the registry's nine fields and an unused id. The package also holds AMENDMENT, RECOVERY, RELATED-WORK and VERIFICATION-AMENDMENT notes. |
| 2 | Saved masks, targets, artifacts, groups and folds match (8,009 queries, 1,596 strings, 1,526 components, seed 20261006) | `benchmark-audit.json` `correspondence`; `review/reproduction-hashes.json` | confirmed | `data.py` rerun is byte-identical. |
| 3 | MKN 39.7178% top-one, 4.581891 bits | `aggregate-results.json` `models.classical/extra0/loss.summary`; `review/recomputed-headlines.json` | confirmed | From the saved arrays: 39.71782%, 4.581891. |
| 4 | Saved first order 34.5861% / 5.119435 bits; second order 37.2706% / 5.247171 bits | `comparators` | confirmed | Recomputed from the saved audits. |
| 5 | GRU 38.0946% / 4.604726; transformer 34.1990% / 4.966507 | `models.gru/extra0/loss`, `models.transformer/extra0/loss` | confirmed | |
| 6 | Ensemble + extra 41.1662%, 4.347675 native bits, ECE 0.9805% | `models.ensemble/extra1/loss.summary` | confirmed | Common-alphabet loss 4.092267. |
| 7 | 12-row table of top-1/5/10, native loss, common loss, ECE | REPORT lines 11–24 | confirmed | Largest difference 0.0. |
| 8 | Ensemble + extra minus first order +6.5801 [5.7417, 7.4341]; minus second order +3.8956 [3.1808, 4.6509] | REPORT lines 51–52 | confirmed | All 20 contrast rows (top-one and native loss, 2,000 draws, seed 23101) match; largest difference 0.0. |
| 9 | Learning curves: 16 cells; 100% minus 75% = +1.7106, +1.2111, +1.2611, +1.2486 points | `learning-curves.json`; `review/recomputed-curves.json` | confirmed | Increments 25→50→75→100 for MKN: 2.68, 2.02, 1.71; all positive and shrinking. |
| 10 | Seed ranges of six neural procedures | REPORT lines 144–149; `review/recomputed-seed-ranges.json` | confirmed | |
| 11 | Capacity table; transformer at the 45-epoch cap in 119 of 180 inner fits | `training-diagnostics.json` | confirmed | GRU 1 of 180. Of 15 outer transformer fits per regime, 9 ran all 45 epochs. Pooled inner bits and parameter ranges recomputed from the inner records. |
| 12 | Extra pools: 5,680 faces, 1,533 candidates, 3,304 tokens; 501–506 strings and 1,419–1,427 tokens per fold; 807–828 faces excluded | `benchmark-audit.json` `outer_extra` | confirmed | My own candidate rule and closure select exactly the same faces in all five folds (`review/leak-audit.json`). |
| 13 | Zero violations in 5 outer and 15 inner allocations | `extra-graph-audit.json`; `review/leak-audit.json` | confirmed | See leakage section. |
| 14 | 144–159 benchmark training strings per fold linked to test strings | `extra-graph-audit.json`; `review/graph-links-summary.json` | confirmed, incomplete | My counts: 145, 159, 148, 144, 144. Mechanism and size are not reported; see links section. |
| 15 | Loss selection picks MKN order 3, scale 1 in all ten fold/regime cells | `main/classical-f*-extra*-selection.json` | confirmed | |
| 16 | Selection depends on inner statistics only | `main/*-selection.json` | confirmed | All 50 selection records agree with the argmin of their saved inner statistics; 120 pooled inner statistics recompute from the inner records; 180 neural epoch counts equal the ceiling of the median inner epoch. |
| 17 | 205 singleton target types, all unseen in benchmark-only training | `models.classical/extra0/loss.summary.frequency_strata.1` | confirmed | 251 queries (3.13%) have targets outside the training alphabet; 191 (2.38%) with extra text. |
| 18 | Protocol written before fitting | PROTOCOL.md; commit 3183b4d | confirmed | PROTOCOL.md modified 23:58:09 on 6 October; the file in 3183b4d (00:02:54) has the same SHA-256 (4076b9c4…). First fit files 00:04:41. |
| 19 | No grid or training limit changed after outcomes | `frozen-model/manifest.json` `code_sha256` | confirmed | `data.py` and `models.py` equal their copies in 3183b4d; `run.py` (written 00:04:26) equals `main/code-snapshots/run.py`. |
| 20 | Amendment: the aggregation code changed "after the first outer n-gram fold was available" | AMENDMENT-2026-10-07.md; raw `classical.log`, `classical-summary.log` | discrepancy | All ten n-gram outer cells had finished at 00:09:07 and the n-gram summary, including extra versus no extra, was printed at 00:16:07. `summarize.py` was edited at 00:17:35 and the amendment written at 00:18:07. The Exploratory label is correct; the stated timing understates what was available. |
| 21 | Frozen recipe: ensemble + extra, pooled inner loss 4.523950, 2,233 texts, 9,744 tokens | `frozen-model/manifest.json` | confirmed | The ten pooled inner losses recompute; the loader passes all payload and code hashes. 1,596 + 637 strings, 8,009 + 1,735 tokens. |
| 22 | Frozen loader: hidden replacement exactly unchanged; batch difference 6.99e-08 | `frozen-inference-v2-verification.json` | confirmed | Rerun differs only in the sample path. |
| 23 | Internal verification: 13 classical configurations, 102 neural checkpoints, 14 ensemble arrays | `verification.json` | confirmed | Rerun is byte-identical. |
| 24 | Path and hash inventory | `file-manifest.json` | confirmed | `inventory.py --verify` checks 4,316 hashes. |
| 25 | Tracked outputs are aggregates only | 1,266 tracked package files | confirmed | No record id, sign sequence or per-query field; `frozen-model/` holds hashes, configuration and counts. |
| 26 | "The rare-target and boundary rows below locate that calibration cost" | REPORT line 56 | discrepancy | Frequency strata are defined by the outcome; see calibration section. |
| 27 | Extra text lowers common-alphabet loss by 0.2990 bits (MKN) | `direct_contrasts.classical/extra_minus_noextra` | confirmed, interpretation incomplete | 94% of the change comes from 251 queries; see calibration section. |
| 28 | Figure `figures/learning-curves.png` (REPORT line 100) and `plot-requirements.txt` (README line 37) | `git status --ignored` | discrepancy | Both are ignored by Git (`*.png`, `*.txt`), so a clone has a broken image and no requirements file. The SVG is tracked. |
| 29 | `environment.json`: `installed_packages_during_task` is empty | `environment.json`; README line 37 | discrepancy | Written before the plotting packages were installed; README discloses the installation. |
| 30 | Aeneas Table 2: 40.5% CER and 46.5% top-20 (known length) | `RELATED-WORK.md`; `sources.json` | confirmed in the author PDF; unverifiable in the typeset article | The publisher page redirects to an authorization step. |

## Reproduction log

Environment as recorded in `environment.json`: Python 3.13.5, NumPy 2.5.3, PyTorch 2.14.1+cu126, RTX 4070 Laptop GPU. Free disk space was 6.1–6.8 GB throughout; the largest file I wrote was 1.2 MB and the three large duplicates were deleted after hashing. Total compute was about 10 minutes.

1. `data.py --output review/...` and `audit_extra.py --output review/... --witness-name review-tmp/...`: `benchmark-audit.json` and `extra-graph-audit.json` reproduced byte for byte.
2. `summarize.py --run main --output review/...` (55 s) and with `--curves` (39 s): `aggregate-results.json` (SHA-256 184ca496…) and `learning-curves.json` (fcbec551…) reproduced byte for byte, including the paired intervals.
3. `verify.py --run main --output review/...` (67 s): `verification.json` (7f171914…) reproduced byte for byte. It refits 13 classical outer configurations and compares every probability, checks hidden-target replacement on all 8,009 queries, reloads 102 neural checkpoints and rebuilds 14 ensemble arrays; the largest difference from the independent scalar MKN is 1.8e-15.
4. `verify_frozen.py --prefix review/reviewer-frozen-inference`: same record as `frozen-inference-v2-verification.json` except the sample path. `training_diagnostics.py --output review/...`: identical (642 fit records). `inventory.py --verify`: 4,316 hashes verified.
5. `review/refit_check.py` → `review/refit-check.json` (39 s). Fold 0, benchmark-only and with extra text: all 24 inner fits of the MKN grid rerun, saved inner losses and accuracies equal (difference 0.0), the selected configuration (order 3, scale 1.0) is the saved one, and the refit outer array is bit-identical. One GRU seed (20261006, width 64, 40 epochs) and one transformer seed (width 128, 45 epochs) refit on outer fold 0 give bit-identical probabilities to the saved arrays.
6. `review/recompute_headlines.py`, `recompute_curves.py`, `recompute_seeds.py` → `recomputed-headlines.json`, `recomputed-curves.json`, `recomputed-seed-ranges.json`: own code for top-k, native and common loss, five-bin ECE and the component bootstrap; agreement with REPORT and with the per-query JSONL fields is exact.
7. Further reviewer analyses, each a script in `review/` that reads the package's local inputs and writes one JSON of aggregates: `leak_audit.py` → `leak-audit.json`; `graph_links.py` → `graph-links-summary.json`; `graph_rules.py` → `graph-rule-sensitivity.json`; `link_respect.py` → `link-respect-estimate.json` (200 random-removal repeats for the Markov models, 100 for MKN); `neighbor_probe.py` → `neighbor-probe.json`; `neighbor_exposure.py` → `neighbor-exposure.json`; `variant_respect.py` → `variant-respect-estimate.json`; `extra_neighbors.py` → `extra-neighbor-exposure.json`; `extra_decomposition.py` → `extra-text-decomposition.json`; `coverage90.py` → `coverage-at-90-percent-mass.json`; `sentence_start_probe.py` → `sentence-start-probe.json`. The three large rerun outputs (`aggregate-results.json`, `learning-curves.json`, `verification.json`) were deleted after their hashes went into `reproduction-hashes.json`; the commands above regenerate them.
8. `python -X utf8 -B tools/review_prose.py --path experiments/2026-10-06-modern-restoration --no-write`: 9 files, 0 flags.

Not run: `run_all.py` (full retraining; the disk has no room), `plot_curves.py` (writes into the package's `figures/`), `acquire_sources.py`, `extract_literature.py` and `finish_when_ready.py` (network, local literature copies and a one-off continuation).

## Source checks

All eight sources in `sources.json` are marked opened and none is marked snippet-only. I opened each through WebFetch, a local copy, or both.

| Source | How opened | Checked | Result |
|---|---|---|---|
| Yadav et al. 2010, *PLoS ONE* 5(3): e9506 | publisher page; local HTML | Title, six authors in order; 1,548-text EBUDS with one copy of each repeated text and multi-line and damaged texts removed; 80:20, five parts, 100 random-deletion repetitions; 74% sensitivity of the bigram model with signs under 90% of the cumulative probability counted as true positives (Fig. 14, Table 5); the cross-validation section reports no top-one figure | accurate. Smoothing is Witten-Bell with Katz backoff. |
| Rao et al. 2009, *PNAS* 106(33): 13685–13690 | local PDF text | Title and authors; page 4 gives about 74% accuracy for filling in deleted signs and cites ref. 10, which is the Yadav et al. n-gram paper (arXiv 0901.3017); page 6 states that modified Kneser–Ney smoothing was used | accurate. RELATED-WORK.md does not say that Rao et al. used modified Kneser–Ney. |
| Venkatesh and Farghaly 2023, *J. Emerging Investigators* 6 | publisher abstract page; local PDF | 2,223 unique texts, 80% train and 20% test, 100 random single-sign deletions averaged; Hit@1 about 35%, Hit@5 about 57%, Hit@10 about 63% (page 5); the abstract's 63% is Hit@10; n-gram order chosen "after trying various n values" on the test dataset (page 4) | accurate |
| Tiwari 2026, NLP4DH, pp. 314–319 | ACL page; local PDF | 6,579 inscriptions; 80/20 split stratified by object type (§4.1); BiLSTM next-token model; real-test perplexity 2.60 (Table 4) | accurate |
| Assael et al. 2022 (Ithaca), *Nature* 603: 280–283 | PMC full text via WebFetch | 9,441 duplicates removed; 78,608 inscriptions; identifier endings 3 and 4 held out; hidden spans of 1–10 characters; 61.8% top-one and 26.3% CER; eight transformer blocks | accurate. The local download is a reCAPTCHA page, as `sources.json` says. |
| Assael et al. 2025 (Aeneas), *Nature* 645: 141–147 | local author PDF; web search for the citation | Table 2: 40.5% CER and 46.5% top-20 for 20-character restoration with known length; Trismegistos identities and 90% fuzzy matches removed; identifier endings 3 and 4 held out (page 8) | accurate for the author PDF. The typeset article could not be opened (the publisher page redirects to an authorization step), so its Table 2 is unverified. The local "PDF" from the publisher is an HTML page, as recorded. |
| Papavassileiou and Kosmopoulos 2024, ML4AL, pp. 115–129 | ACL page (abstract only); local PDF | 426 A&B sequences; leave-one-out; 30.28%, 50.23%, 57.75% (Table 3); transfer 25.65% and 24.71% top-one (Table 4); no overall improvement (§5.3) | accurate |
| Chen and Goodman 1998, Harvard TR-10-98 | local PDF text (WebFetch could not parse the PDF) | Equation 26 on PDF page 20: Y, D1, D2, D3+ | accurate |

One attribution is wrong. PROTOCOL.md line 21 calls the finite-vocabulary floor "not an exact reproduction of the 2010 estimator". The 2010 paper smooths with Witten-Bell and backs off with Katz; modified Kneser–Ney is the estimator of Rao et al. 2009. The package's MKN is therefore a higher-order interpolated version of an estimator that was already applied to this script, and RELATED-WORK.md should say so. To relate its numbers to Yadav's 74% directly, I computed the same event from the saved arrays: the true code lies inside the smallest set holding 90% of the predicted probability for 86.2% of queries under MKN (mean set size 85 codes), 87.3% for the ensemble and 88.3% for the ensemble with extra text (`review/coverage-at-90-percent-mass.json`). The corpora, deletion laws and models differ, so these figures do not rank the two studies.

## Method and scope findings

### Leakage and the extra-text exclusion

The exclusion logic in `data.py` (`Corpus.__init__`, `Corpus.extra`) builds one union-find over every observed face and every benchmark representative, joining on object key and on identical nonempty strings. It drops from the candidate pool every face whose root is a root of a held-out record and keeps the first face per distinct string. I re-implemented the candidate rule from PROTOCOL.md and the closure from scratch (`review/leak_audit.py`). My pools equal the package's in all five folds (same faces). In each of the 5 outer and 15 inner allocations, no fitted benchmark string or extra face shares an alias, object family or identical string with a held-out row, and no extra face lies in the closure of one.

Secondary probes (`review/leak-audit.json`, `review/extra-neighbor-exposure.json`) found small overlaps. Per fold, at most 2 extra strings of three or more signs lie inside a test string and at most 5 contain one, against 36–41 and 49–84 benchmark training strings. 133 of the 1,596 test strings (8.3%) have a one-sign-edit neighbour among the fitted extra strings (36 if only extra strings of three or more signs count), against 509 (31.9%) among benchmark training strings. Twenty of 4,172 site and excavation-number identifiers appear under two or more object families; for one of them the two benchmark strings (7 queries) lie in different outer folds. The closure removes 53–54% of the 1,533 candidate faces in every fold, because the faces of the largest link set sit in every fold's closure. As a result, 120 of the 637 strings in the frozen model's extra pool (19%; 23 one-sign, 61 two-sign, 15 three-sign, 21 longer) occur in no evaluated fold pool.

### Selection and timing

`run.py` selects with `choices(stats)` on pooled inner statistics and sets neural epochs from the inner records; outer predictions are written after the index is fixed. The checks in claim 16, and the exact reproduction of fold 0's full inner grid and selection from the training rows alone, show that no outer query enters selection. The sequence of events is: protocol 23:58 (6 October); commit with protocol, `data.py`, `models.py` 00:02:54; `run.py` 00:04:26; first fits 00:04:41; all n-gram outer cells 00:09:07; n-gram summary 00:16:07; `summarize.py` edited 00:17:35; amendment 00:18:07; neural stage finished 00:56:45; disk-full error 01:13:36; aggregates 01:48–01:49; freeze 01:51; package commit 02:06:46. The primary (loss) and secondary (top-one) criteria are in the protocol. One protocol sentence differs from the code: "Restore the lowest-loss epoch" is implemented as restoring the last epoch that improved on the best loss by at least 0.001. Selected settings are uniform: MKN order 3 and scale 1, GRU 64×1, transformer 128×2 (often at the epoch cap), ensemble weight 0.5 in every fold. The frozen recipe was chosen by pooled inner loss and I recomputed its ten candidates.

An implementation probe (`review/sentence_start_probe.py`, `sentence-start-probe.json`) gives start-anchored lower-order n-grams raw counts instead of continuation counts, a convention some toolkits use. It does not help: 39.67% and 4.630 bits against 39.72% and 4.582, and 21.55% against 21.74% on initial slots. The rebuild without that change reproduces the package's probabilities exactly.

### The 144–159 links and Paper 001's independence claim

I rebuilt the object and string graph with my own union-find (`review/graph_links.py`, `review/graph_rules.py`; outputs `graph-links-summary.json` and `graph-rule-sensitivity.json`). It reproduces the six bridged sets (169 saved components, largest 157) and the per-fold counts. No single non-benchmark face touches two saved components, so the sets form through chains: a benchmark string sits on object X, another face of X carries a one- or two-sign text, the same text appears on a face of object Y, and Y carries a different benchmark string. Sixteen texts (4 of one sign, 12 of two) do all the bridging; the three that reach the most saved components reach 46, 44 and 37, through 127, 93 and 111 faces. The six sets contain 1,785 non-benchmark faces, 1,302 of them with fewer than three signs.

| Link rule over the observed export | Bridged sets | Saved components joined | Largest set | Test queries touched |
|---|---:|---:|---:|---:|
| Object keys and identical strings of any length (package rule) | 6 | 169 | 157 | 748 |
| Identical strings of two or more signs | 4 | 156 | 150 | 680 |
| Identical strings of three or more signs; object keys only; strings only | 0 | 0 | 0 | 0 |

The 192 strings in the six sets hold 748 queries (9.3%); per fold 138, 115, 159, 163 and 173 queries (7.2–10.8%). The touched queries are already easier in the saved results (top-one 38.8%, 40.9% and 41.4% for first order, second order and MKN, against 34.2%, 36.9% and 39.5% elsewhere). The linked training strings are close relatives of them: 36% of the 192 strings have a linked training string one sign edit away, against 13% (SD 2%) for random samples of the same size drawn from unlinked training strings of the same fold, and 26% against 14% share a contiguous trigram (`review/neighbor-probe.json`).

Refitting with the saved hyperparameters (first order alpha 20; second order 20, 20, 100, 20, 20; MKN order 3, scale 1.0) on each fold's training set minus its linked strings, and scoring the touched queries (`review/link-respect-estimate.json`):

| Model | Touched queries, full training | Linked strings removed | Change, points [95% component bootstrap] | Same-size random removal of unlinked strings, points | Whole benchmark |
|---|---:|---:|---:|---:|---:|
| First order | 38.77% | 30.75% | −8.02 [−10.29, −5.73] | +0.26 ± 0.47 | 34.59% → about 33.84% |
| Second order | 40.91% | 31.95% | −8.96 [−11.68, −6.37] | +0.09 ± 0.52 | 37.27% → about 36.43% |
| MKN | 41.44% | 35.56% | −5.88 [−8.87, −3.20] | +0.58 ± 0.54 | 39.72% → about 39.17% |

The refits with full training reproduce the saved per-query outcomes on all 8,009 queries for all three models. The estimate keeps the other 7,261 queries unchanged, which is what a split that respected the links would do for them, and does not rerun hyperparameter selection or the neural models. The paired differences among the three n-gram models move by 0.09–0.29 points, and resampling the 1,363 link sets instead of the 1,526 saved components changes the headline interval ends by at most 0.21 points (ensemble + extra minus first order: +6.58 [5.72, 7.55] against [5.74, 7.43]; GRU minus second order still spans zero).

The saved split shares no object, alias or complete string across folds. For the 9% of queries in link sets, the linked strings nevertheless carry usable information: removing them costs 6–9 points, and a third of the touched strings have a linked string one sign away, which points to variants of one inscription type on different objects. The manuscript already says that the closure reduces known leakage without identifying every dependency, so its text remains accurate; the touched-query share and effect above are the figures to add. A broader dependence sits outside the link sets. 509 of the 1,596 strings (31.9%; 2,016 queries, 25.2%) have a training string in their fold one sign edit away, and top-one on their queries is 47.8%, 52.1% and 54.4% for first order, second order and MKN against 30.2%, 32.3% and 34.8% elsewhere. Removing those neighbours lowers the affected queries by 5.9, 9.2 and 7.1 points (random removal of the same number: +0.4, 0.0, +0.4), which is about 1.5, 2.3 and 1.8 points on the whole benchmark, and about a third of the second-order gain over first order (0.85 of 2.68 points) disappears when those neighbours are removed (`review/variant-respect-estimate.json`, `review/neighbor-exposure.json`). This applies to every model and is part of what the benchmark measures, but it bears on the report's reading of the learning curves, since extra training strings also add variant coverage.

### Calibration and the common-alphabet loss

ECE is the five-bin, equal-width, count-weighted absolute gap between mean top-label mass and exact top-one accuracy (`old.summarize` in `src/six_hour/markov_baseline.py` for the table, `subset_summary` in `summarize.py` for the strata); my implementation matches all 12 reported values. Every procedure is overconfident, and the ECE is close to the overall gap: MKN has mean top-label mass 0.4499 against accuracy 0.3972 and ECE 5.28%; the ensemble with extra text has 0.4211 against 0.4117 and ECE 0.98%. REPORT line 56 says the rare-target and boundary rows locate the calibration cost. The frequency strata are defined by the target's frequency in the whole benchmark, which is the outcome. In the singleton stratum no query can be correct (205 targets absent from training), so its ECE of 30.65% is the mean confidence and carries no calibration information. The position strata (initial 10.19%, internal 5.53%, final 3.51% for MKN) are defined before the outcome and can be read as calibration.

The common-alphabet loss is defined as stated: the mass of every code outside the benchmark-only training alphabet, including the UNKNOWN token, is pooled into one event, and benchmark-only models are unchanged. Splitting the 8,009 queries by whether the target is in that alphabet (`review/extra-text-decomposition.json`):

| Family | 7,758 in-alphabet targets: top-one change with extra text, points [95%] | Common loss change, bits [95%] | 251 outside targets: common loss, no extra → extra | Share of total loss change from outside targets |
|---|---:|---:|---:|---:|
| MKN | −0.12 [−0.55, +0.30] | −0.019 [−0.040, +0.002] | 14.60 → 5.63 | 94% |
| GRU | −0.06 [−0.66, +0.55] | −0.044 [−0.070, −0.018] | 13.56 → 5.51 | 86% |
| Transformer | +0.50 [−0.04, +1.04] | −0.101 [−0.124, −0.078] | 14.38 → 6.20 | 72% |
| Conditioned neural | +0.13 [−0.52, +0.78] | −0.050 [−0.077, −0.023] | 13.22 → 5.78 | 83% |
| Log ensemble | +0.39 [−0.13, +0.89] | −0.040 [−0.060, −0.020] | 13.82 → 5.53 | 87% |

The extra pool supplies counts for codes that occur only in outside text, and the benchmark-only models give those codes the 0.5-count floor; top-one on the outside targets never changes. Extra text therefore adds no measurable top-one accuracy in any family, and its probability gain is mostly vocabulary coverage of 3% of the queries. Neither README nor REPORT states this answer. The metric that shows the large gain was added after the n-gram outcomes were visible (claim 20).

### Contrasts the report does not tabulate

The prompt's first question is whether newer models improve on the best classical one. Paired contrasts against MKN, from my bootstrap (`review/recomputed-headlines.json`, `unreported_paired_contrasts`): GRU −1.62 points [−2.54, −0.66] with loss +0.023 bits [−0.028, +0.075]; transformer −5.52 [−6.57, −4.39] with +0.385 bits; conditioned neural −1.21 [−2.14, −0.28]; ensemble +1.07 [+0.43, +1.69] with −0.191 bits [−0.216, −0.166]; ensemble + extra minus MKN + extra +1.56 [+0.97, +2.14]; ensemble + extra minus ensemble +0.37 [−0.12, +0.86]. The neural models alone do not beat MKN, and the gain comes from combining them. The neural scores average three seeds; single seeds reach 36.5–37.0% for the GRU.

### Scope, rights and tracked outputs

No claim of decipherment, sound or meaning, no novelty or state-of-the-art claim, and no resemblance argument appears in the package; PROTOCOL.md line 46 prohibits them. The tracked directory has no third-party payload: PDFs, HTML and extractions are in the git-ignored raw directory, and `sources.json` carries citations, locators and paraphrase without quotation. A scan of the 1,266 tracked package files and of `review/` for record ids, sign sequences and per-query keys found only field-name lists. `frozen-model/` tracks `manifest.json` (hashes, configuration, counts, the aggregate benchmark audit), `training-register.json` (path, hash, counts), `code-dependencies.json` and a README; the counts, checkpoints and training register are local. The manifest status "Frozen evaluation" describes a recipe selected on a reused benchmark whose `selection_status` field says Exploratory.

### Writing

The prose scan reports no flags. Reading the files turned up: REPORT line 5, "This limits an independence claim for the broader register", names no claim and no size; line 111, "positive in 4 of four curves", and "directly answer"; the caveat that curves and intervals do not establish a ceiling or an architecture limit recurs in README line 39, REPORT lines 102 and 126 and PROTOCOL line 38, and the conditioning of intervals on fitted models in REPORT lines 29 and 151, so each belongs in one methods paragraph; README lines 9 and 35 are long enumerations of links and stages that would read better as short lists; the answers to the prompt's first question (do neural models beat MKN?) and second question (does extra text help?) appear only as table rows.

### Boundaries

At the end of the review `git status --porcelain` lists, inside this package, only the untracked `review/` directory and `REVIEW.md`. The package's own commit bbeaa4a touches only files in this directory. The same listing shows modified or untracked files in the field-recommendations, chronology-region, backward-chronology and sign-context-and-seals packages, in `experiments/2026-10-06-evidence-census/synthesis/` and at `knowledge/retrospectives/2026-10-06-research-program.md`; that set changed while I worked, none of it is mine, and no tracked file outside this package was edited by the package or by me. The two ignored package files named in claim 28 predate the review. My temporary files under the raw directory (`review-tmp/` and `review/`) are deleted; the raw directory again holds only the package's own files.

## Required fixes, in order

1. Replace REPORT line 5 and README paragraph 2 with the source and size of the links: sixteen identical one- and two-sign texts on faces of different objects; six sets, 192 strings, 748 queries (9.3%); none when links need three or more signs; touched-query effect and whole-benchmark bound (about 0.5–0.8 points for the n-gram models), pointing to `review/link-respect-estimate.json` or a package equivalent. Update the registry entry's `challenge` to match.
2. State in README and REPORT what extra text does: top-one unchanged within about ±0.5 points in every family, loss gain concentrated in the 251 targets outside the training alphabet (72–94% of the common-alphabet change).
3. Remove the inference from frequency-stratum ECE (REPORT line 56) and keep the position strata as the calibration diagnostic.
4. Record a dated erratum for the modified Kneser–Ney attribution (PROTOCOL.md line 21, "the 2010 estimator") and add the Rao et al. 2009 smoothing fact to RELATED-WORK.md. The protocol is frozen, so record the correction as a dated erratum.
5. Record a dated correction to AMENDMENT-2026-10-07.md: all ten n-gram outer cells and the n-gram summary preceded the change.
6. Make the REPORT figure and the pinned plotting requirements part of the tracked record: embed `figures/learning-curves.svg` or force-add the PNG, and force-add `plot-requirements.txt` or copy its contents into the README.
7. Fix the prose items listed under Writing.

## Optional improvements

- Tabulate the paired contrasts of each neural family and of the ensemble against MKN (numbers above).
- Report the 90%-mass coverage beside Yadav's 74%.
- Add the near-variant exposure (31.9% of strings, 25.2% of queries) to the limitations and to the reading of the learning curves and of the second-order gain.
- Note that the loss-selected second-order model is the first-order model (MARKOV-04), so the loss gain over the best saved comparator by loss is −0.5375 bits [−0.5852, −0.4914], not −0.6653.
- Document that the frozen extra pool includes 120 strings that no evaluated fold used.
- Resample link sets as a sensitivity in the bootstrap; the interval ends change by at most 0.21 points.
- Refresh `environment.json` (plotting packages) or point to `figures/learning-curves-environment.json`.
- Align the protocol's epoch-restoration sentence with the code by erratum, and describe the manifest status as an Exploratory frozen recipe.
