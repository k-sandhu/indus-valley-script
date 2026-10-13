# Segmentation scoring

This task measures internal boundary precision, recall and F1 against complete word divisions, with exact-word span scores from the original rehearsal. It also checks whether a segmentation recovers catalogued line divisions. A line break establishes a required boundary; other positions are unlabelled. The latter mode therefore reports recall and boundary rate elsewhere, with precision/F1 explicitly null.

```text
python -m bench segmentation --synthetic --out experiments/NEW-DATE-my-study/segmentation-synthetic.json
python -m bench segmentation --references data/raw/my-study/boundaries.json --predictions data/raw/my-study/proposed.json --out experiments/NEW-DATE-my-study/segmentation.json
python -m bench segmentation --local-rehearsal --out experiments/NEW-DATE-my-study/readable-cohorts.json
python -m bench segmentation --local-lines --out experiments/NEW-DATE-my-study/catalogue-divisions.json
python -m bench segmentation --local-rehearsal --methods dp_unigram,all_boundaries --sweeps 2000 --out experiments/NEW-DATE-my-study/dp-cohorts.json
```

Reference rows carry `id`, `length`, `boundaries` and `complete` (default true). Prediction rows carry the same `id` and their `boundaries`. Position `i` is a cut between positions `i−1` and `i`. Lists must contain sorted distinct integers strictly inside the text. Missing, extra or duplicate rows and out-of-range boundaries are rejected. Runs keep complete references separate from `complete: false` line-only references. Inputs need no source sequences when only lengths and boundaries are being scored.

Output gives boundary and exact-word scores for complete references, or required-division hits/recall for partial references. The everywhere and nowhere baselines are always available. Local modes import branching entropy, greedy n-grams and the Dirichlet-process segmenter used in structure-first. Defaults run the fast methods and both trivial baselines; explicitly request `dp_unigram` to rerun its 2,000 sweeps. The hand case has two true positives, two false positives and one false negative: precision 1/2, recall 2/3 and F1 4/7.

A segmentation claim declares its cohorts and comparison before scoring and improves boundary F1 over the everywhere baseline on withheld complete-boundary material. It reports results for each readable cohort and uncertainty on independent source groups. Required-line recall alone cannot establish that additional predicted cuts are correct. The current wrapper scores predictions and baselines; it does not turn a descriptive rehearsal into a newly withheld evaluation.

`--local-rehearsal` rebuilds the original cohorts from local normalized Bronze Age records, using the pinned clean Indus length profile and the original sampling seed: 309 Sumerian seals, 1,859 Sumerian lines, 940 Egyptian glyph sentences and 1,223 Akkadian letter lines. It reproduces branching-entropy F1 0.6922192410885397 on seals and the other fast-method scores in [the step 5 summary](../../experiments/2026-10-12-structure-first/step5-rehearsal/run-segmentation-2026-10-12/summary.json). The original [report](../../experiments/2026-10-12-structure-first/step5-rehearsal/REPORT.md) gives DP mean F1 0.531 against the everywhere baseline's 0.485.

`--local-lines` follows [the segmenter-agreement review](../../experiments/2026-10-12-structure-first/review/review_step3_segmenter_breaks.py), using the currently held joined-face list and both line orders. That local list now contains the corrected 69 faces used in [step 3](../../experiments/2026-10-12-structure-first/step3-segmentation/REPORT.md), with 73 required divisions. The bench re-score finds branching-entropy hits 26 and 41, and greedy hits 70 and 64. The earlier review reported 72 faces and 76 divisions, with branching-entropy hits 29/44 and DP hits 76/74. The source list's population changed after that reviewed endpoint; the current re-score is saved separately and does not replace those recorded numbers.

Local inputs are `data/normalized/lipi_clean_rtl_singleline.jsonl`, `data/normalized/lipi_observed_faces.jsonl`, `data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl`, and `data/raw/2026-10-12-structure-first/step3-linebreak-faces.json`. [DATA.md](../../knowledge/DATA.md), `python tools/fetch_data.py --list` and [REPRODUCING.md](../../REPRODUCING.md) give source holdings, pins and restore routes. Full sequences stay in these local inputs; bench outputs their aggregate scores and hashes.
