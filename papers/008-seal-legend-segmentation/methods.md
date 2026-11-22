# Methods, splits, benchmark commands, and limitations

This companion document specifies the data filters, component-grouping rules, statistical procedures, cryptographic hashes and reproduction commands behind [manuscript.md](manuscript.md). All paths resolve from the repository root (`c:/Users/sandh/OneDrive/Projects/indus_valley_script` or equivalent checkout). Raw corpora, per-inscription tables, inventories and plate crops remain local under `data/` and `data/raw/` because of unresolved upstream redistribution rights; only aggregates, protocols and code are tracked in Git.

## 1. Shared corpus inputs and object grouping

All Indus structural analyses read from two normalized files built from the pinned Lipi export (`yajnadevam/lipi`, commit `fc8813a5`):

1. `data/normalized/lipi_observed_faces.jsonl` (SHA-256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`): all 5,680 inscribed faces, retaining Wells and ICIT visual sign codes, right-to-left reading-order codes (`signs_reading_rtl`), object types, field motifs, site names and CISI catalogue aliases.
2. `data/normalized/lipi_clean_rtl_singleline.jsonl` (SHA-256 `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`): complete single-line faces read right to left with no damaged or unknown signs. Deduplicating exact reading-order sequences of at least two signs yields 1,859 distinct texts containing 8,535 sign tokens across 577 attested Wells sign codes (1,312 distinct texts on seals, object type `SEAL*`).

To prevent leakage across evaluation splits, faces are grouped into connected components whenever they share a physical object identifier, a catalogue alias or an identical sign sequence. In the clean structural frame, the 1,859 distinct texts form 1,571 connected components (with one large component of 206 linked texts producing fold 0 of 537 texts against 312 to 344 texts in folds 1 to 4). Every cross-validation split, held-out calibration set and block bootstrap operates on whole components.

## 2. Graphic sign families and modifiers (step 1)

Package: `experiments/2026-10-12-structure-first/step1-signs/` (protocol SHA-256 `a2185b6331d3d9e6055c4ba5ee66da4e006b17067b1f5bc9c7ddfc0311de44c7`, coding SHA-256 `c2d55fb56e25b8d7f630f2680f9b85b9122cfa15b8718e08fa5b72c11f509f7d`).

- **Coding procedure.** All 722 Lipi font codes were rendered in Wells code order (48 glyphs per contact sheet, labelled with code and corpus token count). Coder 1 (Claude Opus 5.5) assigned every code a base family, stroke count (for numerals) and modifiers from a 14-term vocabulary (`encl`, `dots`, `inner`, `side`, `top`, `cap`, `bar`, `hatch`, `double`, `hold`, `pole`, `yoke`, `X`, `variant`). Coder 2 (a separate Claude Opus 5.5 subagent given only the sheets and vocabulary) coded the same 722 codes independently.
- **Inventories tested.** `W` (577 attested Wells codes), `V` (310 attested groups with identical base, modifiers and count; 359 in full vocabulary), `P` (444 attested Mayig or Parpola-level classes; 555 in vocabulary), `M` (438 attested Mahadevan numbers; 551 in vocabulary), `B_coder1` (78 attested base families; 85 in vocabulary), `B_coder2` (59 attested base families; 63 in vocabulary), and `modifier_signature` (271 groups pooling signs across bases by modifier set).
- **Predictive evaluation.** Every model predicts exact original `W` codes across five component-grouped folds (8,535 held-out tokens). The baseline is an interpolated Kneser–Ney bigram model (5.893 bits per sign; unigram 7.058 bits). Each candidate partition trains a class-based bigram model and interpolates it with the `W` bigram baseline (mixing weight `lambda` tuned inside training folds). Gains are measured in bits per sign against the baseline, with the identity-partition mixture gain (0.0029 bits) reported alongside 200 random partitions matched to each grouping's exact group-size distribution.
- **Post-outcome review controls.** Computed in `experiments/2026-10-12-structure-first/review/REVIEW.md`: 100 random contiguous-cut partitions placing 85 cuts along the Wells number line; splitting numeral families into singletons; merging one-substitution near-copies into the same fold; adding an end-of-text symbol; and testing nine individual modifiers one at a time.

## 3. Line-division recurrence, plate audit, and face adjudication

### 3.1 Line-division recurrence (step 3)
Package: `experiments/2026-10-12-structure-first/step3-segmentation/` (`run-linebreaks-2026-10-12-v3/summary.json`, after Amendments 1 and 2).

- **Population.** Of 118 faces carrying `/` in the Lipi visual code, 40 contain unknown, damaged or empty lines, 6 lack any line or crossing window of length 2 or more, and 3 are boustrophedon, leaving 69 clean multi-line faces (61 `SEAL:S`, 3 `POT:T:g`, 2 `TAB:C`, 1 `SEAL`, 1 `TAB:B`, 1 `IMPL`).
- **Test.** Each line (read right to left) is checked for exact contiguous recurrence inside clean single-line texts from other objects. Length-matched crossing windows straddling the break are checked under both line orders. Primary comparisons use a two-sided sign test on per-face recurrence rates, both pooled across line orders and under the conservative order (whichever order maximizes crossing-window recurrence on each face). Post-outcome review controls deduplicated identical faces, removed numeral-only lines, shifted the division to all other internal positions, and measured unsupervised segmenter recall across 76 divisions on 72 joined faces.

### 3.2 Plate audit and 29-face adjudication
Packages: `experiments/2026-10-20-seal-legend-units/plate-audit/` and `experiments/2026-10-22-face-adjudication/`.

- **Initial audit (Q-0027).** Of the 118 divided faces, 43 lacked held crops (32 CISI 3 numbers, 11 no CISI number). Three blinded AI readers (25 faces each) inspected the 75 photographed faces from CISI 1 and 2 crops, counting visible signs per group and recording segment placement, layout type (`wrapped`, `separate`, `other`) and confidence (`high`, `medium`, `low`). A division counted as confirmed when visible sign groups matched catalogue counts within one sign. Removing 38 unknown or damaged faces and 5 boustrophedon faces left 75 segmenter-usable faces (79 divisions), 33 of which received a verified plate order (30 reversed visual code, 3 forward: H-60, H-97, K-16).
- **Follow-up adjudication of 29 unresolved faces.** A two-pass protocol (`results-v1.json`, `VISUAL-PASS-1-FREEZE.json`) inspected 29 primary images and 8 alternate views before accessing rendered catalogue glyph sheets. A separate coordinating pass independently sealed first-pass observations and reviewed the second-pass graphic mappings. Dispositions separated accepted physical-layout observations (21 of 29) and provisional segment-to-group maps (12 of 29) from historical reading traversal (0 accepted).

## 4. Line-trained segmentation, Ur III calibration, and frozen inventory

Package: `experiments/2026-10-20-seal-legend-units/` (protocol SHA-256 `f31a4576d97044afb42a2e3158a2f98d6de054606ccf497a3e6cb110c966de15`, Amendments 1 and 2).

### 4.1 Model specification and features
Each internal position between adjacent signs of a joined legend is scored by a regularized conditional linear model ($\lambda = 1.0$) trained by maximum likelihood over the scribe's break choices (124 choices across 75 usable faces in the full fit; 59 to 63 training faces per fold in 5-fold component-grouped cross-validation). The model separates eleven standardized textual features (`w_unit`) from two layout features (`w_layout`), dropping `w_layout` at inference time:

1. `be_forward`: forward branching-entropy change across the candidate cut.
2. `be_backward`: backward branching-entropy change across the candidate cut.
3. `pmi`: pointwise mutual information of the adjacent sign pair straddling the cut.
4. `left_ends_text`: log rate at which the sign immediately before the cut ends single-line texts.
5. `right_starts_text`: log rate at which the sign immediately after the cut begins single-line texts.
6. `left_pair_ends_text`: how often the two-sign stretch ending at the cut ends single-line texts.
7. `right_pair_starts_text`: how often the two-sign stretch starting at the cut begins single-line texts.
8. `pair_count`: corpus frequency of the adjacent sign pair straddling the cut.
9. `crossing_triple_count`: corpus frequency of three-sign sequences straddling the cut.
10. `left_window_drop`: drop in corpus recurrence when extending the left window across the cut.
11. `right_window_drop`: drop in corpus recurrence when extending the right window across the cut.

Every feature is computed from the clean corpus with the scored face's entire object-family component removed. At test time, the model places a boundary wherever the unit score exceeds threshold $\tau$, chosen on training faces to maximize Youden's $J$.

### 4.2 Evaluation metric and baselines
Because line divisions label positive boundaries only, Indus segmentation is scored with `python -m bench segmentation` by Youden's $J = \text{recall}_{\text{div}} - \text{rate}_{\text{other}}$, where `boundary_precision` and `boundary_f1` remain explicitly `null`. Component-cluster bootstrap intervals (resampling connected object components) quantify uncertainty and paired differences against four comparators: `layout_only`, `branching_entropy`, `greedy_ngram` and `dp_unigram` (Dirichlet-process unigram segmenter). A post-protocol label-permutation control (`label-permutation.json`) relocates each face's divisions to random internal positions and refits across 200 trials.

### 4.3 Ur III Sumerian calibration
Using 309 distinct Ur III Sumerian seal legends (308 with line divisions, 1,187 word divisions, 718 line divisions, all 718 coinciding with word divisions; input SHA-256 `dedb9c3967d6bd2fe725406e2a46234673fcd8e5a3de2817dee27bc8ce1d899c`), we ran five-fold cross-validation under two training regimes: `supervised_75_labels` (exactly one line division sampled from each of 75 training legends per fold, matching the Indus label count) and `supervised_all_line_labels` (all 554 to 599 training line divisions per fold). Held-out predictions were scored against complete word boundaries (precision, recall, boundary F1, exact word F1) and line divisions (line J). Pre-stated pass rule: held-out word-boundary F1 of the 75-label model exceeds the cut-everywhere baseline (0.557) by at least 0.05 (achieved margin +0.061).

### 4.4 Build and held split, version 2 inventory, agreement, and prospective locks
Before building any inventory, 15% of object-family components were partitioned by deterministic hash into held-out calibration set H (171 seal legends of three or more signs), leaving build corpus B (1,687 clean texts, including 994 seal legends of three or more signs).

- **Version 1 to version 2 (Amendment 1).** Version 1 cut only where score exceeded $\tau$ (4.5% cut rate; 1 closing formula closing 9 of 994 build seals). Amendment 1 (frozen before reading H) added one cut at each legend's highest-scoring internal position (`FROZEN-v2.json`, build cut rate 29.1%, mean unit length 2.23 signs). Recurring multi-sign units formed the 225-unit inventory; final stretches of one to four signs following the peak junction in at least three unrelated components formed the 49-formula closing stock (`closing-stock.json` SHA-256 `85f3182f4968acb31b5c35d2647b02cbe668b4c30efc46c5eed7fb2d2518a7fd`; `inventory.json` SHA-256 `ad075f44a23b6ba9a99102e4c95eac29806a3cccb827057474d783113d07e813`).
- **Rule text and independent implementation.** `RULES-v2.md` (SHA-256 `8278c2c23664a35a9903c8400606bede1ca5184b0f57b36abfd3a8043d5a99bf`) fixes the longest 1-to-4-sign stock closing first (Rule 1), then cuts the opening into the fewest inventory units (Rule 2). An independent agent parsed all 171 legends in H (776 internal positions) from `RULES-v2.md` alone (`agreement-v2.json`, κ = 1.00).
- **Prospective scoring locks.** `PREDICTIONS.md`, `predictions.json`, `RULES-v2.md`, the lists and `score_prospective.py` are locked in `PREDICTIONS.sha256`. Power tables use 20,000 to 40,000 simulated pools drawn from H calibration rates (`calibration-v2.json`, `predictions.json`). Two statistic families are registered in `spent-entry.json`: `seal_legend_closing_structure` (P1–P3) and `line_division_unit_boundary` (P4).

## 5. Stroke-numeral fixity and comparative seal corpora

### 5.1 Stroke-numeral fixity (step 4)
Package: `experiments/2026-10-12-structure-first/step4-numerals/` (`run-2026-10-12/summary.json`, plus review sensitivities).

- **Population and comparison.** Short-stroke and tall-stroke numeral tokens in the 1,859 clean Indus texts preceding a non-numeral sign or text end yield 1,265 pairs and 56 qualifying items ($\ge 5$ tokens; 996 tokens). Ur III tablets contribute 3,421 numeral–word pairs (subsampled 200 times to 1,265 tokens; 38 to 48 qualifying items per draw), and Linear B supplies 201 commodity–number pairs (12 qualifying items, 146 tokens).
- **Metrics and sensitivities.** Primary measures are mean distinct values per qualifying item, token-weighted top-value share, and raw mutual information divided by value entropy, plus a 10,000-permutation null for Indus MI and a Jensen–Shannon divergence test between short-stroke (787) and tall-stroke (478) following distributions. Post-outcome sensitivities tested family-aware Indus values against unit-aware Ur III values, five-token rarefaction per item, permutation-debiasing (net MI ratio), removing value-2 tokens (691 remaining), and reversing item direction to the preceding sign.

### 5.2 Edge asymmetry and head-direction seal corpora
Packages: `experiments/2026-10-12-structure-first/step6-language/` and `experiments/2026-10-21-head-direction-corpora/` (protocol SHA-256 `9c496a9ef7cb43119344b6e1d6ac895a198b9633ebc641ac7d74a1d85742aba2`, Amendments 1–4).

- **Edge asymmetry (`sign.S1`).** Defined as normalized Shannon entropy of initial units minus normalized Shannon entropy of final units over distinct texts of length $\ge 2$, compared against within-text unit shuffles (95% range). Step 6 measured Indus clean (1,859), Indus seals (1,312), Ur III seals (309 sign, 308 word), Egyptian glyph sentences (1,696 sign, 1,301 word) and Ur III tablets (1,067 sign, 1,065 word).
- **Five comparative seal corpora.** Linked to physical objects and findspots, grouped by die, alias and identical sign sequence, excluding composite editions and casts: `ia-ganges` (Basarh and Bhita, 556 records / 495 objects / 245 eligible sign legends / 30 word), `ta-brahmi` (Mahadevan 2003 Tables 1.6–1.8, 31 records / 23 eligible sign including 7 coins / 7 word), `sux-ur3` (ORACC `epsd2/admin/ur3`, 31,512 records / 31,220 objects / 3,044 eligible sign / 3,026 word), `akk-sargonic` (ORACC `oakk` + CDLI, 89 records / 17 composites excluded / 11 eligible sign / 10 word), and `sux-sargonic` (175 records / 2 excluded / 42 eligible sign / 36 word).
- **Discrimination rules.** Frozen entry threshold: 25 eligible legends per corpus and at least two corpora per group (Amendment 4 added a secondary panel at threshold 20; 2,000 matched-size replicate draws at n = 196 and n = 18). Neither panel reached two head-initial corpora (`akk-sargonic` = 11), so all statistics reported `testable: false` and `kept: false`. Post-run exploratory counts recorded closing grammatical units (`exploratory-closing-units.json`) and adjacent title–name order across all lexical members (`exploratory-title-name-order.json`).

## 6. Seal-text circulation, Lothal plate check, and archival audit

### 6.1 Seal-text identity and circulation
Package: `experiments/2026-10-12-seal-text-identity/` (`run-2026-10-12/summary.json`, `sensitivity.json`, `review-response.json`, `segments.json`).

- **Population.** 1,430 complete single-line `SEAL*` faces of length $\ge 2$ without unknown signs from 29 named South Asian sites, taking one face per object family (lowest record identifier).
- **Statistics.** Locality (`S1`): mean share of same-text seal pairs found at one site (text-weighted primary, pair-weighted companion), tested against 10,000 global site shuffles (primary frozen null) and 10,000 length-stratified site shuffles (Amendment 2 exploratory sensitivity, plus Mayig variant merging yielding 81 shared texts). Coincidence (`S3`): exact expected duplicate pairs by length from an interpolated Kneser–Ney bigram model via dynamic programming over squared transition probabilities, fitted to all 2,164 distinct legible texts (primary) and refitted to 824 non-seal texts and 1,420 seal texts (review). Motif concordance (`S4`): same-motif pair share across 130 pairs with both motifs coded, tested against 10,000 within-site motif shuffles, with a breakdown comparing unicorn and non-unicorn pairs and a no-motif-as-category check. Cross-city sealings (`S5`): exact text matches between tags or sealings (`TAG*`) and eligible seals. Independent verification (`verify.py`) rebuilt populations, checked permutation means against exact hypergeometric expectations and checked coincidence DP by enumeration at lengths 1 and 2.

### 6.2 Blinded Lothal / M-895 plate check and archival pass 3
Packages: `experiments/2026-10-13-plate-checks/` (protocol SHA-256 `bd3e40402307091bd7d1d226bfd358ba5201f8f9ad3820fc17ed495f1874b4f9`) and `experiments/2026-10-24-office-seal-pass3/` (building on `2026-10-24-office-seal-evidence/`).

- **Plate measurements.** M-895 was rendered from CISI 2 printed p. 85 (PDF 120, zoom 8.34; calibrated on M-894, M-896, M-897 at 31.1 px/mm, giving 724 px = 23.3 mm against catalogue 23.4 mm). Lothal sealings L-161 to L-170 were inspected on CISI 1 printed pp. 276–278 (PDF 312–314) and Lipi crops (calibrated at 22.7 px/mm on 2:1 renders, 11.27 px/mm on L-161 Lipi crop, giving 23.4 mm face width, range 21.1 to 24.2 mm). Proportions of sign width along the text band are scale-invariant. A blinded second AI reader received eleven views renamed `X01` to `X11` (`second-reader-report.json`) without identity labels or expected outcomes.
- **Archival pass 3.** Bounded page-image reinspection of Rao 1985 Vol. II printed pp. 317–325 (PDF 68–76, SHA-256 `bc5f16e3d8836ac0f03b5b28e74fc9775ab042cf972fb64d59f082d7a8074865`) and CISI 1 printed p. 373 (PDF 409, SHA-256 `47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d`) documented the contradictory assignment of Plate CLXI F to both 1864 (L-164) and 1830 (L-161) and preserved all conflicting source assertions without collapsing object identities (`aggregate-v1.json`).

## 7. Reproduction and benchmark commands

Run from the repository root with Python 3.13, NumPy and SciPy, with local inputs present under `data/normalized/` and `data/raw/`:

```text
# Benchmark self-test and segmentation endpoint replay
python -m bench selftest --out <new-dir>/selftest.json
python -m bench segmentation \
  --reference data/raw/2026-10-20-seal-legend-units/run-2026-10-20/indus/plate_order-supervised-references.jsonl \
  --prediction data/raw/2026-10-20-seal-legend-units/run-2026-10-20/indus/plate_order-supervised-predictions.jsonl \
  --out <new-dir>/segmentation-replay.json

# Seal-legend units pipeline (plate audit, CV, permutation null, Ur III calibration, v2 inventory, agreement, predictions)
python -P experiments/2026-10-20-seal-legend-units/audit_summary.py --out <new-dir>
python -P experiments/2026-10-20-seal-legend-units/sumerian_calibration.py --run <new-run>
python -P experiments/2026-10-20-seal-legend-units/run_cv.py --run <new-run>
python -P experiments/2026-10-20-seal-legend-units/label_permutation.py --run <new-run> --perms 200
python -P experiments/2026-10-20-seal-legend-units/build_inventory_v2.py --version <new-v>
python -P experiments/2026-10-20-seal-legend-units/agreement.py --version v2 --agent <agent-file> --out <new-dir>/agreement.json
python -P experiments/2026-10-20-seal-legend-units/calibrate.py --version v2 --out <new-dir>/calibration.json
python -P experiments/2026-10-20-seal-legend-units/make_predictions.py --calibration <new-dir>/calibration.json --out <new-dir>/predictions.json

# Structure-first steps 1, 3, 4, 6 and seal-text identity verification
python -P experiments/2026-10-12-structure-first/step1-signs/analyze_step1.py
python -P experiments/2026-10-12-structure-first/step3-segmentation/analyze_step3.py
python -P experiments/2026-10-12-structure-first/step4-numerals/analyze_step4.py
python -P experiments/2026-10-12-structure-first/step6-language/analyze_step6.py
python -P experiments/2026-10-12-seal-text-identity/verify.py

# Head-direction comparative corpora
python -P experiments/2026-10-21-head-direction-corpora/discriminate.py --threshold 25 --out <new-dir>/t25
python -P experiments/2026-10-21-head-direction-corpora/discriminate.py --threshold 20 --out <new-dir>/t20
```

Note on provenance bug fixed after agreement run: in `agreement-v2.json` and `agreement-v2-junction.json`, the `rules_sha256` field recorded the hash of `RULES.md` (v1) due to a script slip that was fixed later; the independent agent actually read `RULES-v2.md`, whose hash (`8278c2c2...`) is verified in `FROZEN-v2.json` and `PREDICTIONS.sha256`.

## 8. Methodological limitations summary

1. **Single upstream Indus export:** Lipi (`fc8813a5`) omits CISI 3.1/3.2 gaps and post-catalogue finds and has unresolved redistribution rights.
2. **Small primary labelled division sample:** 33 plate-ordered faces (25 Mohenjo-daro) limit power on non-wrapped layouts (3 separate-field faces, J = 0.000) and regional generalization.
3. **AI visual inspection without human verification:** Sign-family coding, plate audits, 29-face adjudication and Lothal measurements all await human epigraphic review.
4. **In-sample vs out-of-sample inventory steps:** Amendment 1 responded to version 1's low cut rate on build corpus B before held set H was opened; P4's 62% rate on 58 divided seals is in-sample and therefore awaits fresh divided seals.
5. **Corpus size shortfalls in comparative tests:** Old Akkadian (11) and Tamil-Brahmi (23) fell short of the 25-legend threshold, leaving head-direction placement untestable until additional excavated corpora (such as Tell Brak, Tell Mozan, Kültepe, revised *Early Tamil Epigraphy*, Karur and Keeladi) are added.
6. **One-face-per-family rule in seal identity:** Taking the lowest record identifier per object family omitted one Harappa duplicate occurring on second faces (H-352, H-354, H-369), and Mohenjo-daro's 64% share of eligible seals (917 of 1,430) dominates global pair expectations.
