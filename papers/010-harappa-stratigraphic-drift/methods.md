# Statistical methods, sensitivity analyses, and reproduction commands

This companion document specifies the exact mathematical definitions, decision rules, sensitivity analyses, power simulations, and reproduction commands behind [manuscript.md](manuscript.md). All code runs under Python 3.13 with NumPy. Raw inscription rows and third-party source PDFs remain local-only under `data/raw/` and `data/normalized/`; tracked outputs hold aggregates, statistics, sign codes, and family identifiers.

## 1. Chronological clocks, excavation frames, and analytical units

### 1.1 Relative clock $u$

For any group of $N$ seals with an ordered chronological key $k_i$ (smaller values are older), let $r_i \in [1, N]$ be the average rank (mid-rank for ties) of $k_i$ computed by `strat_stats.average_ranks`. The normalized clock value is:

$$u_i = \frac{r_i - 0.5}{N} \in (0, 1).$$

- **Harappa Mound F confirmation (`C-0010`):** $k_i = -\text{stratum}_i$, where Vats's strata run from Stratum VII ($k = -7$, oldest) to Stratum I ($k = -1$, latest). Ranks are computed mound-wide over the $N = 173$ seals in qualifying trench frames (`scope="mound"` in `period_stats.add_clock`). Thirds are defined by fixed cut points on $u$: early third $u < 1/3$ (Strata VII–V, 46 seals), middle third $1/3 \le u < 2/3$ (Strata IV–III, 74 seals), and late third $u \ge 2/3$ (Strata II–I, 53 seals).
- **Harappa discovery (`C-0010`):** Frames are `(mound, chronology_source)` cells with at least 5 seals (99 seals in 7 frames). Because Vats strata and HARP periods are distinct scales, $u$ is ranked within each frame (`scope="frame"`).
- **Mohenjo-daro Mackay DK-G discovery and Marshall confirmation (`C-0006`):** $k_i$ is Mackay's level in feet against the DK datum (625 seals, ranked in one frame `DK`) or minus Marshall's depth in feet below the modern surface (434 seals, ranked within each of 15 area-section strata).

### 1.2 Excavation frames and unit merging

In Harappa Mound F, trench cells with at least 15 seals form their own frames (`FTrench I`: 37, `FGranery`: 37, `FTrench VI`: 33, `FTrench IV+V`: 24, unnamed `F-`: 22, `FTrench III`: 20). Smaller cells (`FTrench A`: 1, `FTrench V`: 1) are pooled into `F/rest` (size 2) and dropped because the pooled frame falls below the 5-seal minimum, leaving 173 seals.

Each object family contributes one legend face: the longest complete text without unknown signs or blanks, breaking ties by longest text overall and then lowest record identifier. Signs are stored in right-to-left reading order (`signs_reading_rtl`), corresponding to the reverse of the visual left-to-right string (`signs_visual_ltr`). In the Harappa edge rule (`period_stats.edge_text_fields`):

- A legend contributes a **closing sign** (`visual[0]`) if it is single-line (`single_line` true and no `/` in `text_code_visual_ltr`), its left edge is intact (`text_code_visual_ltr` starts with `+`), `visual[0] != "000"`, and it is not a complete one-sign legend (`length` is either `None` or $\ge 2$).
- A legend contributes an **opening sign** (`visual[-1]`) under the symmetric rule at the right edge (`text_code_visual_ltr` ends with `+` and `visual[-1] != "000"`).
- A legend contributes a **length** if `complete_observed` is true and `has_blank_space` is false.
- **Deduplication within frames:** For opening, closing, length, inventory, and variant tests, identical clean complete legends occurring in the same frame are merged into one unit whose clock value is the median $u$ of its copies. Incomplete or unknown-sign legends remain separate units. For the rectangular-seal positive control (PC), every physical seal counts once without text merging.

## 2. Primary test statistics and null distributions

Let $G$ partition the $n$ analytical units into excavation frames $F_1, \dots, F_m$. Every permutation test (`strat_stats.permutation_test`) draws $B = 9{,}999$ independent permutations $\pi^{(b)}$ that shuffle the vector $u$ strictly within each frame $F_g$, keeping frame sizes and marginal distributions of $u$ fixed. With the observed statistic $T_{\text{obs}} = T(u)$ counted as one draw:

- Upper-tail one-sided $p$-value (P3, P4, P6, P7, PC):
  $$p = \frac{1 + \sum_{b=1}^{B} \mathbf{1}\!\left(T(\pi^{(b)} u) \ge T_{\text{obs}} - 10^{-12}\right)}{B + 1}.$$
- Two-sided $p$-value centred at the permutation null mean $\bar{T}_{\text{null}}$ (P1 permutation test, P5):
  $$p = \frac{1 + \sum_{b=1}^{B} \mathbf{1}\!\left(\left|T(\pi^{(b)} u) - \bar{T}_{\text{null}}\right| \ge \left|T_{\text{obs}} - \bar{T}_{\text{null}}\right| - 10^{-12}\right)}{B + 1}.$$
- Standardized score: $z = (T_{\text{obs}} - \bar{T}_{\text{null}}) / s_{\text{null}}$, where $s_{\text{null}}$ is the sample standard deviation (`ddof=1`) of the $B$ null draws.

### 2.1 Closing-stock equivalence (P1) and early level (P2)

Let $S$ be the frozen 15-sign closing stock (`090`, `151`, `154`, `156`, `226`, `400`, `405`, `407`, `520`, `527`, `595`, `617`, `621`, `740`, `892`), defined as the union of Mackay's 12 DK-G closing signs and the 8 signs closing at least 5 legends of length $\ge 2$ with final share $\ge 0.5$ in the 253-family non-confirmation Harappa pool. For each closing unit $i$ ($n = 130$), let $I_i = \mathbf{1}(\text{closing}_i \in S)$.

- **P1 observed difference:**
  $$\Delta_{\text{stock}} = \frac{\sum_{i: u_i \ge 2/3} I_i}{n_{\text{late}}} - \frac{\sum_{i: u_i < 1/3} I_i}{n_{\text{early}}}.$$
- **Equivalence interval:** Within each frame $F_g$, resample $|F_g|$ units with replacement ($B = 9{,}999$ replicates, seed `20261022`), recomputing $\Delta_{\text{stock}}^{(b)}$. Take the 5th and 95th percentiles as the 90% interval (and 2.5th and 97.5th as the 95% interval). P1 passes if the 90% interval lies strictly inside $(-0.25, +0.25)$ and survives the ten-deletion check; P1 fails if its two-sided within-frame permutation $p \le 0.05$, $|\Delta_{\text{stock}}| \ge 0.15$, and it survives the ten-deletion check; otherwise P1 is inconclusive.
- **P2 early level:** $p_{\text{early}} = \sum_{i: u_i < 1/3} I_i / n_{\text{early}}$. P2 passes if $p_{\text{early}} \ge 0.55$ and remains $\ge 0.55$ after deleting one early-third stock-closing legend (`(k - 1) / (n_early - 1)`).

### 2.2 Slot identity: opening signs (P3) and closing signs (P7)

Signs appearing in at least $k = 5$ units form their own categories; rarer signs are pooled into `OTHER`, yielding $C$ categories (`C = 6` for P3, `C = 5` for P7). With category sizes $n_c$, category means $\bar{u}_c$, and overall mean $\bar{u}$ (`strat_stats.between_ratio_factory`):

$$T_{\text{slot}}(u) = n \cdot \frac{\sum_{c=1}^{C} n_c (\bar{u}_c - \bar{u})^2}{\sum_{i=1}^{n} (u_i - \bar{u})^2}.$$

### 2.3 Graphic variant choice (P4)

Using `data/normalized/mayig_wells_class_crosswalk.json`, retain Wells codes that map to exactly one Mayig class in classes with at least two such codes. For each merged legend (from `all_legends`) and each Mayig class present in it, create one `(legend, class)` row carrying the legend's most frequent Wells code in that class (breaking ties by lower code). Retain Mayig classes having at least two codes with $\ge 3$ tokens each and at least 10 total rows in those retained codes (in Mound F: `P004`, `P086`, `P316`, `P364`, `P385`; 228 total rows across all mapped classes, with the five qualifying classes entering the sum). For each qualifying class $m$ with $K_m$ retained codes and row subset $J_m$, let $T_{\text{slot}, m}(u_{J_m})$ be the between-code rank statistic on $u_{J_m}$. Then (`strat_stats.variant_statistic_factory`):

$$T_{\text{var}}(u) = \sum_{m} \left(T_{\text{slot}, m}(u_{J_m}) - (K_m - 1)\right).$$

### 2.4 Legend length (P5)

Across complete merged legends ($n = 105$), convert length $L_i$ within each frame $F_g$ to its normalized mid-rank $x_i = (r_{g}(L_i) - 0.5) / |F_g|$ (`strat_stats.stratified_spearman_factory`). The statistic is the Pearson correlation between $x$ and $u$, tested two-sided:

$$r_{\text{len}}(u) = \frac{\sum_{i=1}^{n} (x_i - \bar{x})(u_i - \bar{u})}{\sqrt{\sum_{i=1}^{n}(x_i - \bar{x})^2 \sum_{i=1}^{n}(u_i - \bar{u})^2}}.$$

### 2.5 Sign inventory (P6)

Across all merged legends ($n = 172$), retain every readable sign $s \neq \text{"000"}$ present in at least $m_{\min} = 8$ legends (`21` qualifying signs in Mound F). Let $n_s$ be the number of legends containing $s$ and $\bar{u}_s$ their mean $u$. With population variance $\text{Var}(u) = \frac{1}{n}\sum_{i=1}^{n}(u_i - \bar{u})^2$ (`period_stats.inventory_factory`):

$$T_{\text{inv}}(u) = \frac{\sum_{s} n_s (\bar{u}_s - \bar{u})^2}{\text{Var}(u)}.$$

### 2.6 Positive control (PC)

Across all $N = 173$ physical seals in frames, let $R_i = \mathbf{1}(\text{object\_type}_i = \text{"SEAL:R"})$. The statistic is the Pearson correlation between $R$ and $u$, tested one-sided (upper tail).

## 3. Multiplicity, influence, and credence rules

- **Holm step-down adjustment:** Applied across the six primary $p$-values ($m = 6$: P1 permutation $p$ and P3–P7). Ordering $p_{(1)} \le \dots \le p_{(6)}$, $p^{\text{Holm}}_{(j)} = \max_{l \le j} \min(1, (m - l + 1) p_{(l)})$.
- **Ten-deletion single-unit influence rule:**
  - For a P1 pass, rank all units by $|\Delta_{\text{stock}, -i} - \Delta_{\text{stock}}|$ descending, take the top 10, and recompute the 90% bootstrap interval ($1{,}999$ resamples each). The rule is met if all 10 intervals stay strictly inside $(-0.25, +0.25)$.
  - For any drift test (P3–P7) with $p \le 0.05$, rank all units by how much deleting unit $i$ moves the statistic toward its null ($T_{-i} - T_{\text{obs}}$ for one-sided upper tests; $|T_{-i}| - |T_{\text{obs}}|$ for two-sided P5), take the 10 smallest (most null-ward) values, and rerun the within-frame permutation test ($2{,}999$ draws each). The outcome is `drift` only if $\max_{k=1\dots 10} p_{-i_k} \le 0.10$; otherwise `inconclusive`. If raw $p > 0.10$, the outcome is `no drift`; if $0.05 < p \le 0.10$, `inconclusive`.
- **Leave-one-frame-out diagnostics:** For every drift test reaching $p \le 0.05$, drop each of the six trench frames one at a time and rerun the permutation test ($2{,}999$ draws). Reported without altering the frozen outcome.
- **Joint credence rule (`C-0010`):** Starting credence is 0.40. Additive effects are P1 (+0.05 pass, −0.02 inconclusive, −0.10 fail), P2 (+0.02 pass, −0.06 fail), P3 (+0.05 no drift, −0.03 inconclusive, −0.10 drift), P4–P6 (+0.02, −0.02, −0.08 each), and P7 (+0.04, −0.03, −0.10). Positive gains on P1 and P3–P7 count at half weight if PC fails. If P1 fails or any of P3–P7 reads `drift` with Holm $p \le 0.05$, the kill condition overrides and sets credence to 0.02 (`dead`).

## 4. Exploratory post-outcome and companion analyses

- **Format-controlled Mound F tests (`post_outcome.py`, $9{,}999$ draws):** (1) Joint trench-and-format frames (`f"{trench}|{'R' if SEAL:R else 'S'}"`); (2) square seals only ($N = 147$); (3) rectangular seals only ($N = 26$); (4) interior sign count $L_i - 2$ on complete ordered legends of length $\ge 2$ (24 early, 44 middle, 32 late); (5) per-sign contributions to P6 and per-class within-trench permutation tests for P4.
- **Cross-site sign check (`post_outcome_signs.py`, $9{,}999$ draws):** Two-sided within-frame permutation test of $\bar{u}_s - \bar{u}$ for signs `806`, `817`, `233`, `900`, `390`, `590` and `741`, plus length correlation, across Mound F confirmation (172 legends), Harappa discovery (98 legends), and Mackay DK-G (610 legends).
- **Mohenjo-daro convergence score (`post_outcome_convergence.py`, $9{,}999$ draws):** Let $c_{\text{MD}}(s)$ and $n_{\text{MD}}$ be token counts across 1,352 Mohenjo-daro seal faces, $c_{\text{H}}(s)$ and $n_{\text{H}}$ across the 253 non-Mound-F Harappa seal families, and $V$ the union vocabulary size. Each sign receives score:
  $$\ell(s) = \ln\!\frac{c_{\text{MD}}(s) + 0.5}{n_{\text{MD}} + 0.5 V} - \ln\!\frac{c_{\text{H}}(s) + 0.5}{n_{\text{H}} + 0.5 V}.$$
  Each merged Mound F legend receives the mean $\ell(s)$ over all its readable signs (171 units) and over its interior signs `signs[1:-1]` (130 units), correlated with $u$ by two-sided within-trench Pearson permutation test.
- **Companion city-level graphic variation (`2026-10-20-script-variation`):** Hierarchical smoothed count model (shrinkage weight 20, one pseudocount per candidate fine code) predicting Wells code within nine eligible Mayig graphic families from family, carrier, material, motif, preservation, CISI volume, position, length, and neighbouring graphic classes, compared against the same model adding `site` at every level. Evaluated on 306 confirmation components (one hashed target per alias and repeated-text component) by mean $\log_2$-probability gain in bits with 95% component-bootstrap intervals.

## 5. Pre-freeze power summary (Harappa Mound F)

Simulated in `discovery-v2/power.json` on Mound F's exact 6-frame, 7-stratum layout populated from the 253-family Harappa pool (400 null replicates, 200 per alternative, 999 permutations or resamples per replicate; standard error $\approx 0.035$). Mixing exchanges strata randomly for 25% or 50% of seals per trench after planting.

| Scenario | Test | Unmixed rate | 25% mixed | 50% mixed |
|---|---|---:|---:|---:|
| Null (no planted effect): P1 pass / fail | P1 | 0.558 / 0.043 | not run | not run |
| Null (no planted effect): false-positive drift | P3–P7 | 0.035–0.058 | not run | not run |
| Closing-stock true shift 0.10: P1 pass / fail | P1 | 0.350 / 0.075 | not run | not run |
| Closing-stock true shift 0.20: P1 pass / fail | P1 | 0.105 / 0.310 | not run | not run |
| Closing-stock true shift 0.30: P1 pass / fail | P1 | 0.025 / 0.680 | not run | not run |
| Opening sign shifted by period in 25% / 35% of legends | P3 | 0.635 / 0.890 | 0.420 / 0.680 | 0.215 / 0.405 |
| Closing sign shifted in 25% / 50% of stock closers | P7 | 0.365 / 0.990 | 0.275 / 0.835 | not run |
| Variant shifted in 25% / 50% of tokens | P4 | 0.310 / 0.925 | 0.225 / 0.730 | not run |
| Late third longer by 0.5 / 0.8 / 1.2 signs | P5 | 0.155 / 0.380 / 0.580 | 0.110 / 0.220 / 0.335 | not run |
| One interior sign shifted in 25% / 50% of legends | P6 | 0.130 / 0.585 | 0.150 / 0.390 | not run |
| Rectangular seals rising 10% to 25% / 10% to 30% | PC | 0.385 / 0.515 | 0.240 / 0.395 | not run |

## 6. Frozen artifact hashes and reproduction commands

### 6.1 Harappa Mound F freeze (`2026-10-21T03:34:45Z`)

Recorded in `experiments/2026-10-20-harappa-legend-periods/bench/shots-freeze.json`:

- `PREDICTIONS.json`: `d3c37d2990ccc89c7e5027ec4b46629987f9a174c5f330d88fb3748a22489ac9`
- `data/normalized/lipi_observed_faces.jsonl`: `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`
- `data/normalized/mayig_wells_class_crosswalk.json`: `9fea45e16be1218d148473dad440f806a2f0c12c954c79347db2584324cc1f71`
- `discovery-v2/frozen-parameters.json`: `ccced192a9c35e460dec03939df8372c249b561569a5c5786436b7223187f19c`
- `period_score.py`: `e4c47b60961fc7f17db6388444f1b441e37614417cbadc269bfd0dd7cf92f067`
- `period_stats.py`: `78929e9776318bc715e235b6720206c2492845a9103f333aff9fffcebac0ab42`
- `strat_stats.py`: `d7b38ddd1a93532ffe4d64a9e1578517cded7825a3e4c029acd8fb59e89a09f1`

### 6.2 Reproduction commands

Every script refuses to overwrite an existing output directory or file. Rerunning from scratch requires fresh output paths (and a fresh split and ledger copy for the `bench shots` steps, because the original split is already opened) plus local copies of the Lipi export and Mackay and Marshall table joins.

```text
# 1. Mohenjo-daro stratigraphy (C-0006)
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/build_inputs.py
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/explore_mackay.py experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2-rerun
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/power.py experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2/frozen-parameters.json experiments/2026-10-20-mohenjo-daro-stratigraphy/power-rerun.json
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/verify_independent.py experiments/2026-10-20-mohenjo-daro-stratigraphy/verify-rerun.json
python -P experiments/2026-10-20-mohenjo-daro-stratigraphy/post_outcome.py experiments/2026-10-20-mohenjo-daro-stratigraphy/post-outcome-rerun

# 2. Harappa Mound F stratigraphy (C-0010)
python -P experiments/2026-10-20-harappa-legend-periods/build_inputs.py
python -P experiments/2026-10-20-harappa-legend-periods/explore_discovery.py experiments/2026-10-20-harappa-legend-periods/discovery-v1-rerun
python -P experiments/2026-10-20-harappa-legend-periods/make_parameters.py experiments/2026-10-20-harappa-legend-periods/params-rerun.json experiments/2026-10-20-harappa-legend-periods/constants-rerun.json
python -P experiments/2026-10-20-harappa-legend-periods/rehearse_discovery.py experiments/2026-10-20-harappa-legend-periods/rehearsal-rerun
python -P experiments/2026-10-20-harappa-legend-periods/reliability.py experiments/2026-10-20-harappa-legend-periods/reliability-rerun.json
python -P experiments/2026-10-20-harappa-legend-periods/power.py experiments/2026-10-20-harappa-legend-periods/discovery-v2/frozen-parameters.json experiments/2026-10-20-harappa-legend-periods/power-rerun.json
python -P experiments/2026-10-20-harappa-legend-periods/verify_independent.py experiments/2026-10-20-harappa-legend-periods/verify-9999-rerun.json 9999
python -P experiments/2026-10-20-harappa-legend-periods/post_outcome.py experiments/2026-10-20-harappa-legend-periods/post-outcome-rerun
python -P experiments/2026-10-20-harappa-legend-periods/post_outcome_signs.py experiments/2026-10-20-harappa-legend-periods/sign-check-rerun.json
python -P experiments/2026-10-20-harappa-legend-periods/post_outcome_convergence.py experiments/2026-10-20-harappa-legend-periods/convergence-rerun.json
```

Original confirmation runs used `confirm.py` against the frozen `bench shots` splits (`experiments/2026-10-20-mohenjo-daro-stratigraphy/shots/round.json` and `experiments/2026-10-20-harappa-legend-periods/shots/round.json`), with read logs preserved in `shots/round.access.jsonl`.
