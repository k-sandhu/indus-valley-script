# Protocol: leak-free restoration refit across full-corpus alias and near-variant splits

Date: 22 November 2026. Status: pre-run protocol written before fitting any model. Related work: question [Q-0010](../../knowledge/questions/Q-0010-check-splits-all-faces.md), finding [F-0010](../../knowledge/findings/F-0010-base-shape-families-prediction.md), the [6 October modern-restoration review](../2026-10-06-modern-restoration/REVIEW.md), and Section 5 of the [22 October novelty review](../2026-10-22-field-novelty-review/REPORT.md).

## Objective and scope

We refit a ladder of masked-slot sign restoration models from scratch under three progressively stricter component-held-out cross-validation splits of the Paper 001 benchmark population. The 6 October audit identified two sources of cross-fold dependence in the original 1,596-string, 8,009-query benchmark: sixteen short one-sign and two-sign strings shared across faces in the full export transitively bridge 9.3% of queries across outer folds, and strings within one sign edit connect 25.2% of queries across folds. Earlier removal checks dropped linked training strings while holding hyperparameters fixed. Here we rebuild the full-corpus alias components and near-variant components before fold assignment, enforce component integrity in both outer and inner folds, refit every model with nested training-only selection, and estimate paired component-bootstrap intervals within and across splits.

This study measures graphic code prediction under synthetic single-slot deletion with known text length. It assigns no phonetic or semantic values and does not equate known-slot synthetic deletion with real damaged inscriptions of unknown missing span.

## Pinned inputs and storage

All inputs are local normalized files and tracked project tables verified by SHA-256 at runtime:

- Clean benchmark population: `data/normalized/lipi_clean_rtl_singleline.jsonl` (expected SHA-256 `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`). Loaded with `min_length=3` and `unique=True`, yielding 1,596 unique complete single-line right-to-left strings and 8,009 single-slot queries, keeping the union of `object_family_id` aliases for every deduplicated string.
- Full observed face register: `data/normalized/lipi_observed_faces.jsonl` (5,680 recorded faces, including short, incomplete, damaged, multiline, and left-to-right faces).
- Graphic base-shape family table (`F-0010`): `experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv` (coder 1 base-shape table mapping all 548 benchmark sign codes into 77 base classes).
- Saved Split 1 verification references: `results/restoration/benchmark.json`, `results/restoration/baseline_slot_audit.jsonl`, `experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl`, `experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl`, and `experiments/2026-10-06-modern-restoration/aggregate-results.json`.

Tracked scripts and aggregate outputs live in `experiments/2026-11-22-restoration-leak-free/`. Per-query prediction files and fold assignment registers remain local-only under `data/raw/2026-11-22-restoration-leak-free/` (physical path `D:\projects\indus_valley_script\data\raw\2026-11-22-restoration-leak-free\`), containing no corpus payloads in Git.

## Three cross-validation splits

Every split evaluates the exact same 1,596 benchmark strings and 8,009 `(record_id, slot)` queries under five outer folds assigned by greedy token-load balancing with randomized ties (`seed = 20261006`), keeping every component intact.

### Split 1: baseline Paper 001 reproduction

Split 1 reproduces the saved Paper 001 partition exactly. Components are built only from the 1,596 benchmark rows by joining rows that share a physical `artifact_aliases` entry or identical benchmark string (1,526 components). Inner three-fold splits inside each outer training fold rebuild benchmark-only components with `seed = 20261006 + fold`, matching Paper 001, `MARKOV-01`, `MARKOV-03`, and the 6 October study.

### Split 2: full-corpus transitive-alias-clean split (Q-0010)

Split 2 builds transitive connected components over the union of all 5,680 faces in `lipi_observed_faces.jsonl` and all 1,596 benchmark representatives before any length or completeness filtering. Two records join when they share any of the following four keys:

1. Physical family identifier: `object_family_id` or any entry in a benchmark row's `artifact_aliases`.
2. CISI base key: `source_cisi` trimmed, uppercased, and reduced to its leading `<prefix>-<number>` token, excluding placeholders (`-`, `--`, empty values, and strings containing `?`).
3. Excavation identifier scoped by site: `(upper(site), norm(excavation-idno))`, where `norm` strips whitespace and punctuation (`-`, `_`, `.`, `/`, `,`), uppercases letters, and excludes placeholders (`-`, `--`, `- -`, `Unknown`, empty values, strings containing `?`, and digit-free site prefixes such as `BNL`).
4. Complete face sign sequence: any identical nonempty `signs_reading_rtl` sequence of length one or greater across the entire 5,680-face register, including one-sign and two-sign faces and damaged or multiline faces.

Benchmark rows inherit their full-corpus component roots and are assigned as whole components to five balanced outer folds (`seed = 20261006`). Inner three-fold splits inside each outer training set group outer training rows strictly by their Split 2 component identifiers (`seed = 20261006 + fold`), so zero full-corpus alias links cross either outer or inner boundaries.

### Split 3: near-variant-clean sensitivity split

Split 3 begins from Split 2's full-corpus components over the 1,596 benchmark strings and merges any two benchmark strings that satisfy either of two textual proximity rules:

1. Unit edit distance: Levenshtein edit distance equal to one (one sign substitution, insertion, or deletion between two benchmark strings).
2. Graphic-family identity: identical sequences after projecting every sign code to its `F-0010` base shape in `sign_components_v1.tsv`.

Whole merged components are assigned to five balanced outer folds (`seed = 20261006`). Inner three-fold splits preserve Split 3 component identifiers (`seed = 20261006 + fold`), guaranteeing that no benchmark training string lies within one edit or shares a base-shape sequence with any validation or test string.

## Models and nested selection

Each outer fold constructs its own training vocabulary consisting strictly of sign codes observed in that fold's training rows plus one `UNKNOWN` state. Test sign codes absent from the training vocabulary count as exact misses for top-1, top-5, and top-10 accuracy, and map to `UNKNOWN` when computing held-out bucket cross-entropy in bits per slot. All rankings use stable descending probability sort.

PyTorch is not installed in this workstation's Python 3.13 environment (`numpy` 2.2.6 only). We therefore pair the four prior Paper 001 and 6 October classical models with two fast, exact-probability graphic-family and skip-bigram ensemble models:

1. **`PM` (independent metadata baseline):** Paper 001 position, length, site, and object-type model (`Restorer(..., bidirectional=False)`). Inner three-fold selection chooses $\alpha \in \{20, 100, 500, 2000\}$ by exact top-1 accuracy (ties favor larger $\alpha$), matching Paper 001.
2. **`M1` (first-order Markov):** Time-homogeneous first-order Markov restorer with start and end states and destination-unigram shrinkage (`MarkovRestorer`). Inner three-fold selection chooses $\alpha \in \{20, 100, 500, 2000\}$ by exact top-1 accuracy (ties favor larger $\alpha$), matching `MARKOV-01`.
3. **`M2` (second-order Markov with backoff):** Second-order Markov restorer shrinking observed two-state histories toward the first-order model with fixed $\alpha_1 = 20$. Inner three-fold selection chooses $\alpha_2 \in \{5, 20, 100, 500, 2000, \text{None}\}$ by exact top-1 accuracy (ties favor later grid entries, matching `MARKOV-03`).
4. **`MKN` (bidirectional modified Kneser–Ney):** Finite-vocabulary interpolated modified Kneser–Ney model (`models.MKN` from the 6 October study) computing the exact conditional slot posterior over candidate fills from the full joint sequence likelihood (combining left and right contexts and boundary states). Inner three-fold selection minimizes held-out bucket cross-entropy over order $k \in \{2, 3, 4, 5\}$ and discount scale $d \in \{0.75, 1.0\}$.
5. **`MKN-GF` (MKN with graphic-base-family Markov pooling):** Log-linear mixture $P(c) \propto P_{\text{MKN}}(c)^{1 - w_{\text{gf}}} P_{\text{GF}}(c)^{w_{\text{gf}}}$ combining the inner-selected `MKN` posterior with an exact generative first-order class Markov model `GF-M1` built on the `F-0010` base-shape classes. In `GF-M1`, each training sign $c$ belongs to its base class $g(c)$, and `UNKNOWN` forms its own singleton class $g_{\text{UNK}}$. From the Jeffreys-smoothed unigram $U(c) = (C(c) + 0.5) / (N_{\text{tok}} + 0.5 |V|)$, class priors are $P_0(g) = \sum_{c \in g} U(c)$, within-class emissions are $P_{\text{emit}}(c \mid g) = U(c) / P_0(g)$, and start and class transitions shrink toward $P_0$ and destination prior $P_{\text{dest}}$ (including `END` with weight $N_{\text{texts}} + 0.5$) with strength $\alpha_g$. The slot posterior is the exact Bayes conditional of the full sequence likelihood. Inner three-fold selection minimizes bucket cross-entropy over $\alpha_g \in \{5, 20\}$ and $w_{\text{gf}} \in \{0.0, 0.05, 0.10, 0.15, 0.20, 0.30\}$.
6. **`MKN-GF-SB` (MKN + graphic-base-family + skip-bigram and position ensemble):** Log-linear mixture $P(c) \propto P_{\text{MKN}}(c)^{1 - w_{\text{gf}} - w_{\text{sb}}} P_{\text{GF}}(c)^{w_{\text{gf}}} P_{\text{SB}}(c)^{w_{\text{sb}}}$ adding a skip-bigram and position-slot comparator `SB-Pos`. For a hidden slot $i$ in a text of length $L$, `SB-Pos` combines the length-and-slot distribution $P_{\text{pos}}(c \mid L, i)$ (smoothed toward $U(c)$ with $\alpha_{\text{pos}} = 20$) with distance-2 skip-bigram lift ratios $R_{\text{skip2}}(c \mid x_{i-2}) = P_{\text{skip2}}(c \mid x_{i-2}) / U(c)$ (when $i \ge 2$) and $R_{\text{skip2}}(x_{i+2} \mid c) = P_{\text{skip2}}(x_{i+2} \mid c) / U(x_{i+2})$ (when $i + 2 < L$), using $\alpha_{\text{skip}} = 20$, normalized over the training vocabulary. Inner three-fold selection uses the `MKN` order and scale and `GF-M1` strength selected inside the same outer training fold, and minimizes inner bucket cross-entropy over $w_{\text{gf}} \in \{0.0, 0.05, 0.10, 0.15, 0.20\}$ and $w_{\text{sb}} \in \{0.0, 0.05, 0.10, 0.15, 0.20, 0.25\}$. Including $w_{\text{gf}} = 0$ and $w_{\text{sb}} = 0$ allows exact fallback to `MKN` when neither addition improves inner held-out loss.

## Metrics, uncertainty, and verification

For every split and model we report slot-weighted exact top-1 accuracy, exact top-5 inclusion, exact top-10 inclusion, held-out bucket cross-entropy loss (bits per slot), five-bin expected calibration error (ECE), position-stratum summaries (initial, internal, final), equal-text-weight accuracy, and out-of-vocabulary target rates.

Uncertainty uses paired 10,000-draw component-bootstrap 95% confidence intervals (`seed = 20261122`), conditioned on the fitted models and corpus population:

- Within each split, all 15 pairwise model differences resample that split's intact components (1,526 in Split 1; 1,361 in Split 2; 964 in Split 3). We also compute a Split 1 sensitivity resampling over Split 2's 1,361 components.
- Across splits for the same model on the same 8,009 paired queries, Split 2 minus Split 1 resamples Split 2's 1,361 components, while Split 3 minus Split 1 and Split 3 minus Split 2 resample Split 3's 964 components. Because Split 3 strictly coarsens Split 2 and Split 2 strictly coarsens Split 1, each cross-split comparison resamples over the coarser dependence partition.

An independent verification script (`code/verify.py`) will run after fitting and write `verification-v1.json`. It checks:

1. Input SHA-256 digests and exact query count (8,009 queries per model and split).
2. Exact numerical reproduction on Split 1 against the saved `PM`, `M1`, `M2`, and `MKN` endpoints.
3. Zero cross-fold full-corpus alias leakage (object family, CISI base key, normalized site and excavation identifier, and identical nonempty face string of any length across all 5,680 faces) in every outer and inner fold of Split 2 and Split 3, and zero cross-fold Levenshtein-1 or `F-0010` base-family leakage in every outer and inner fold of Split 3.
4. Unit self-tests and independent brute-force complete-sequence likelihood replay on sampled queries verifying hidden-target invariance, exact normalization, and probability agreement across all six models.
