# Package A: modern models on the Paper 001 restoration benchmark

Owned directory: `experiments/2026-10-06-modern-restoration/`. Local raw directory: `data/raw/2026-10-06-modern-restoration/`. Python environment with CUDA PyTorch: `C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe` (RTX 4070, 8 GB); you may install further packages into that environment. The system Python also has numpy, scipy, pandas and scikit-learn.

## Question

Paper 001's known-slot restoration benchmark masks each position of 1,596 distinct strings (8,009 queries) under five artifact/string-held-out outer folds built from 1,526 transitive components, seed 20261006. A conventional first-order Markov model reaches 34.59% exact top-one and a second-order model 37.27%, with worse probability loss (5.1194 versus 5.2472 bits). The user asks whether newer and stronger machine-learning models can do better. Answer three things: whether stronger classical smoothing or neural sequence models improve top-one accuracy and probability loss on the same queries; whether additional training text from outside the benchmark population helps; and whether the task is limited by data rather than model capacity.

## Inputs and code to reuse

Read `papers/001-artifact-aware-prediction/manuscript.md`, its `methods.md` and `claim-evidence-map.md`, `experiments/2026-10-02-six-hour/markov-order2/` (PROTOCOL, FINDINGS, `main/code_snapshot.py`, `main/results.json`), `src/restoration.py` and the restoration outputs under `results/restoration/`. Rebuild the exact benchmark population, components, folds and query keys with the existing code, and verify that your reconstruction matches the saved query keys, targets and fold assignments before fitting anything. Report any mismatch rather than working around it.

The full observed export `data/normalized/lipi_observed_faces.jsonl` (5,680 faces, with site, region, object type, motif symbol and metadata) contains texts outside the benchmark population: short texts, multi-line faces and other reading directions. It can supply extra training text only after removing every face connected to a test component through an object alias, object family or identical string. Implement that exclusion explicitly and report how many faces and tokens it adds per fold.

## Models

Specify in `PROTOCOL.md`, before fitting, the model families, hyperparameter grids, training seeds and selection rules. Cover at least:

1. Interpolated modified Kneser–Ney n-grams of orders 2–5, scoring each candidate through the full-sequence likelihood as the second-order study does.
2. A bidirectional recurrent masked-slot model (LSTM or GRU) over left and right context.
3. A small transformer masked language model (for example two to four layers, width 64–128) with strong regularization and early stopping on inner folds.
4. The best neural family with conditioning on object type, site or region, and motif symbol, to measure what archaeological metadata adds.
5. Each family trained with and without the extra out-of-population text.
6. A log-probability ensemble of the best n-gram and best neural model, with weights chosen on inner folds.

Select hyperparameters with three inner component-held-out folds inside each outer training set. Use held-out log loss as the primary selection criterion; report top-one-selected variants as a declared secondary analysis. Train neural models with at least three seeds and report the spread. Keep every outer-fold query unseen during selection.

## Outcomes

Report top-one, top-five and top-ten accuracy, bucket loss in bits, calibration error, position strata (initial, internal, final) and frequency strata, each with paired component-bootstrap differences against the saved first-order and second-order predictions on identical queries. Add a learning curve: train the best classical and best neural model on 25%, 50%, 75% and 100% of each outer training set, with and without extra text, and say whether accuracy is still rising at full size.

These masks have already been used by earlier models, so label all comparisons as exploratory results on a reused benchmark. Before finishing, freeze the single model you would carry forward (configuration, code hash and weights or counts) in a `frozen-model/` record so a future fresh population, such as a newly digitized corpus block, can test it without retuning.

Put per-query predictions in the local raw directory and aggregate results in the owned directory. Check the probability computations on a small case by brute force, and confirm that replacing the hidden target leaves each prediction unchanged.

## Precedents to cite and compare

Yadav et al. 2010, *PLoS ONE* 5(3): e9506 (deduplicated corpus, five-fold cross-validation, 74% sensitivity within the 90% cumulative-probability set); Rao et al. 2009; Venkatesh and Farghaly 2023 (*Journal of Emerging Investigators*); Tiwari 2026 (NLP4DH); Assael et al. 2022 (Ithaca) and 2025 (Aeneas); Papavassileiou and Kosmopoulos 2024 (ML4AL, Linear B restoration). State plainly how your setup and numbers relate to theirs.
