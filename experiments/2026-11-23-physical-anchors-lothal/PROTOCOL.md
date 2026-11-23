# Protocol: Physical Numerical Anchors and Lothal Sealing Attachment Geometry

Date frozen: 2026-11-23  
Package: `experiments/2026-11-23-physical-anchors-lothal/`  
Issues and questions addressed: GitHub Issue #21 (`Q-0011`, `Q-0012`, `Q-0019`)

## 1. Scope and prior exposure

We audit two physical anchors behind Fuls's conditional numeral equations (`F-0006` and Paper 003) and conduct a specimen-level attachment geometry audit and frozen statistical test on the 93 Lothal clay sealings catalogued by Frenez and Tosi (2005).

Prior to freezing this protocol we read only the orientation documents (`Q-0011`, `Q-0012`, `Q-0019`, `F-0006`, `knowledge/DATA.md`, `research/literature/metrology/numerical_source_audit.md`, `research/methods/NUMERICAL_CONSTRAINT_AUDIT.md`, `experiments/2026-10-02-six-hour/lothal-physical-use/README.md`, `graphic-coverage/results.json`, `selected-trace-observations.json`, `experiments/2026-10-02-connections-and-priority/lothal-contact/REPORT.md`, and `experiments/2026-10-24-office-seal-pass3/REPORT.md`). We have not opened the per-specimen Lipi-to-Lothal join payloads, have not inspected individual Lothal sign strings beyond the published group sizes of `G01` through `G09`, and have not run any statistical association or prediction test between Lothal inscriptions and attachment classes.

All local raw renders and cropped plate images will be stored under `data/raw/2026-11-23-physical-anchors-lothal/` (physical path `D:\projects\indus_valley_script\data\raw\2026-11-23-physical-anchors-lothal\`), kept outside Git.

## 2. Part A: Numerical anchor audit (`Q-0011` and `Q-0012`)

### 2.1 `Q-0011`: H-904 and the historical identifier ICIT 3786

Inputs to inspect:
1. Local corpus records for `H-904`, Lipi family `1786`, and Lipi record `3786` in `data/normalized/lipi_observed_faces.jsonl`, `data/lipi/`, and `data/indus_website/`.
2. CISI 2 (`data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf`): basic data row for `H-904` (printed pp. 434–447) and the CISI 2 photographic plate for `H-904`, rendered at high resolution locally.
3. Vats 1940 (`research/literature/sources/vats_1940_govscan_18220.pdf` printed p. 349 / PDF 378 and `vats_1940_govscan_9842.pdf` Plate XCVI no. 477 / PDF 200) and the retained crop `research/literature/metrology/primary_numeric/vats_h904/477_crop12x.png`.
4. Local CISI basic data and image-index outputs (`experiments/2026-10-13-cisi-basic-data-full/`, `experiments/2026-10-13-image-index-and-units/`).

Checks and decision criteria:
- Verify whether CISI 2 basic data, CISI 2 plate photographs, Vats 1940 text/plate, and Lipi agree on excavation number (`J213`, Mound D, Vats 477), material, dimensions, and sign counts on both faces of `H-904`.
- Visually count long and short strokes on both faces of `H-904` in the highest-resolution held plate (CISI 2 and Lipi crops alongside Vats 1940), recording any unreadable or ambiguous marks separately from clearly visible strokes.
- Test uniqueness in the held corpus: count how many two-face objects in `lipi_observed_faces.jsonl` contain both the `W700`/`W900`/long-stroke cluster on one face and the `W840`/long-stroke/short-stroke cluster on the opposite face.
- Decision rule per `Q-0011`: accept the historical join `ICIT 3786 = H-904` as confirmed only if an explicit historical concordance, Fuls Fig. 16, or an authenticated ICIT register connects the integer `3786` to `H-904`. Otherwise separate the confirmed physical join (`H-904 = Vats 477 = J213`) from the provisional historical identifier join (`ICIT 3786 -> H-904`) and record the exact missing witness.

### 2.2 `Q-0012`: M-1383 and the reconstructed stoneware bangle count

Inputs to inspect:
1. Local corpus records and image crops for `M-1383` in `data/normalized/lipi_observed_faces.jsonl`, `data/lipi/`, and `data/indus_website/`.
2. CISI 2 basic data row and photographic plate for `M-1383` (and neighbouring entries `M-1375`–`M-1395` to detect numbering shifts or object-class grouping), rendered at high resolution locally.
3. Mackay 1938 Vol. I and Vol. II (`data/raw/2026-10-13-mackay-marshall-tables/mackay1938/mackay1938_vol1_dli70071.pdf`, `data/raw/2026-10-21-town-axes/plan-B/downloads/mackay1938_vol2.pdf`), Marshall 1931, and held stoneware bangle literature (`research/literature/sources/jansen_urban1987_interim2_govscan_77275.pdf`, `vidale_stoneware_primary.pdf`, `vidale_stoneware_ocr.txt`, and any other local text mentioning `M-1383`, `MN82`, `bangle`, or `saggar`).

Checks and decision criteria:
- Verify the physical object depicted as `M-1383` in CISI 2: object class (sealing/clay tag on stoneware bangle saggar vs. independent clay tag), excavation number (`MN82a` or printed equivalent), museum accession, photograph source, motif, and exact visible sign sequence.
- Check whether any held source connects `M-1383` to the 82 stoneware bangle fragments and 15–20 reconstructed complete bangles cited via Wells (2015, pp. 94–95) in Fuls (2020/2023).
- Decision rule per `Q-0012`: pass only if a held primary source establishes both (a) the link between `M-1383`'s inscription and a specific firing container/assembly and (b) the documented fragment count, refitting procedure, and uncertainty of the 15–20 bangle estimate. Keep the physical identity of `M-1383` in CISI 2 distinct from the unverified bangle-count premise.

## 3. Part B: Lothal attachment geometry and frozen text-vs-context test (`Q-0019`)

### 3.1 Specimen audit of `L-206`

We will inspect every held witness for `L-206`:
1. CISI 1 basic data (printed pp. 365–375) and plate page for `L-206` (`research/literature/sources/joshi_parpola_1987_cisi1.pdf`) plus Lipi image crops for `L-206`.
2. Frenez and Tosi (2005) Table 1, prose (printed p. 74 / PDF 12 and all other mentions of `L-206`), and Figure 3 (printed p. 98 / PDF 36).
3. Rao 1985 (`data/raw/2026-10-21-town-axes/dating/lothal/rao1985lothal-part2.pdf` and `.txt`), searched by `L-206`'s CISI 1 excavation number, to check Rao's original description, findspot, and plate reference.
4. For comparison within `G01`, we will also inspect CISI 1 plates for the other ten `G01` sealings (`L-124`–`L-129`, `L-190`, `L-191`, `L-193`, `L-197`) to check whether any additional `G01` reverse or profile view resolves a second contact geometry.

We will code `L-206`'s contact geometry, surface texture, fastening trace, and preservation independently from the unannotated reverse/profile views before integrating source interpretations. Decision rule per `Q-0019`: confirm the narrow contrast if independently linked views of `L-206` show a continuous deep curved concavity incompatible with an angular board-edge-only attachment for `G01`, and report any unresolved features without forcing a functional label.

### 3.2 Complete 93-sealing attachment-trace table (`L-124` to `L-216`)

Coding is performed strictly from physical reverse and attachment evidence in Frenez and Tosi (2005) Table 1 (`data/six-hour/lothal/table-coding/reviewed-pass.csv` and `independent-first-pass.csv`) and prose (`data/six-hour/lothal/extracted.txt` / `frenez-tosi2005.pdf`), WITHOUT viewing Lipi sign strings during coding.

Each of the 93 sealings receives:
- `cisi_id` (`L-124` through `L-216`), `impressions_table`, `impressions_prose_conflict` (flagging Table 1 vs. prose discrepancies such as `L-174` and `L-179`), `context_code` (`W`, `W1`, `W2`, `O`, `?`), and `context_basis` (`documented_findspot` for `W`/`O`, `stamp_derived_inference` for `W1`, `area_association` for `W2`, `unresolved` for `?`).
- `frenez_physical_type`: the exact 12-level category from Table 1 (`wooden_box`, `locker`, `structure`, `peg_on_wall`, `parallel_canes`, `woven_straw`, `wicker`, `pottery`, `leather_sack`, `single_rope`, `other`, `undiagnostic`).
- `reverse_class_6` (deterministic physical taxonomy frozen here):
  - `wood_plank_peg`: `wooden_box`, `locker`, `structure`, `peg_on_wall`
  - `reed_cane_matting`: `parallel_canes`, `woven_straw`, `wicker`
  - `jar_vessel_pottery`: `pottery`
  - `flexible_cloth_leather`: `leather_sack`
  - `cord_rope_only`: `single_rope`
  - `unidentifiable_other`: `undiagnostic`, `other`
- `diagnostic_class_5`: identical to `reverse_class_6` for the five diagnostic classes and `NULL` (excluded from attachment-prediction tests) for `unidentifiable_other`.
- Secondary binary physical targets (frozen here):
  - `is_wood_plank_peg`: `1` if `reverse_class_6 == "wood_plank_peg"`, `0` if in the other four diagnostic classes, `NULL` if `unidentifiable_other`.
  - `mobility_class`: `mobile_container` (`wooden_box`, `pottery`, `parallel_canes`, `woven_straw`, `wicker`, `leather_sack`) vs. `architectural_fixture` (`structure`, `locker`, `peg_on_wall`); `single_rope`, `other`, and `undiagnostic` are `NULL`.
- `rao_discrepancy_flag`: explicitly flags `L-161` and `L-164` for Rao 1985 Plate CLXI F conflict (p. 319 vs. p. 325) plus any additional Rao 1985 vs. CISI 1 / Frenez and Tosi discrepancies identified during the audit.

### 3.3 Die and impression component grouping (anti-leakage rule)

Repeated impressions from the same seal must never split across training and test folds or across independent permutation units. We define two nested component partitions on joined objects:
1. **Primary partition (`die_component_strict`)**: two objects are placed in the same component if (a) they share an identical complete reading-order sign sequence, OR (b) Frenez and Tosi (2005) assign them to the same seal/die (including the 12-object elephant cohort `L-161`–`L-172` and any other explicitly attested same-seal matches in prose).
2. **Conservative partition (`die_component_substring`)**: merges any partial/incomplete inscription into a component if its contiguous legible sign sequence (length ≥ 3) is an exact substring of that component's complete sequence and its recorded motif does not contradict the component's motif.

All cross-validation splits use Leave-One-Component-Out (LOCO) over `die_component_strict` (primary) and `die_component_substring` (sensitivity).

### 3.4 Frozen inscription features and populations

Two pre-registered analysis populations (restricted to objects with non-null `diagnostic_class_5`):
- **Population A (Primary — Complete clean single-line texts, length ≥ 3)**: the subset of the 29 eligible complete objects whose reverse is diagnostic (non-`unidentifiable_other`).
- **Population B (Expanded — All joined objects with ≥ 1 legible sign and diagnostic reverse)**: uses the longest legible face per object (breaking ties deterministically by face order), adding an explicit `is_complete_face` indicator.

Frozen feature definitions extracted deterministically from `data/normalized/lipi_observed_faces.jsonl` (never using interpretive/translation columns):
1. `text_length`: integer count of legible signs on the selected face.
2. `closing_sign`: terminal sign in reading order (`signs_reading_rtl[-1]`), collapsed to signs occurring in ≥ 2 distinct components plus `OTHER` (computed inside each CV fold to prevent fold leakage).
3. `has_stroke_numeral`: binary indicator (`1`/`0`) for presence of a canonical stroke-numeral sign on the face. The canonical stroke-numeral code set is defined strictly from Wells/Lipi numeric stroke codes (`001`–`045` vertical/short/stacked stroke series, verified against the Lipi sign chart prior to inspecting Lothal texts and recorded verbatim in the output JSON).
4. `frequent_signs`: binary indicator vector for individual signs occurring in ≥ 3 distinct components (selected inside each CV fold for prediction; across all components for omnibus permutation statistics).
5. `animal_motif`: categorical motif from Lipi `symbol` field (`Bull1`, `Elep`, `None_or_dash`, `Other`).

### 3.5 Frozen statistical tests and baselines

All random permutations use fixed PRNG seed `20261123` and `B = 10,000` draws. Exact one-sided permutation p-value: `p = (1 + count(T_perm >= T_obs)) / (B + 1)`.

1. **Component-block permutation test of feature-to-attachment association**:
   - Under the null, the mapping from component `c` to its inscription feature vector `X_c` is permuted uniformly across the `K` components, while keeping each component's constituent specimens and their true physical attachment labels `Y` untouched. (If a component has multiple specimens with slightly different face completeness or motif strings in Population B, the component's ordered feature bundle moves as a single block.)
   - Primary test statistics evaluated under both **component-equal weighting** (each component contributes total weight 1, primary anti-multiplicity metric) and **specimen-equal weighting** (secondary metric):
     - Normalized mutual information (`NMI`) and bias-corrected Cramer's `V` for `animal_motif`, `closing_sign`, and `has_stroke_numeral` against `diagnostic_class_5` and `is_wood_plank_peg`.
     - Absolute Spearman rank correlation `|rho|` for `text_length` against `is_wood_plank_peg` and `mobility_class`.
2. **Component-held-out prediction (LOCO CV)**:
   - Classifiers: (a) L2-regularized multinomial/binary logistic regression (`C = 1.0`, `class_weight="balanced"`), and (b) simple Naive Bayes / smoothed empirical log-odds classifier (`alpha = 1.0`).
   - Targets: `diagnostic_class_5` (primary multiclass), `is_wood_plank_peg` (secondary binary), and `mobility_class` (secondary binary).
   - Metrics: component-weighted balanced accuracy (primary), specimen-weighted accuracy, and macro-F1.
   - Baselines: (i) majority-class baseline inside each training fold, (ii) die-grouped empirical class-prior baseline, and (iii) exact `B = 10,000` component-block permutation distribution of the full LOCO CV pipeline (`Naive Bayes` exact `B = 10,000`; `LogisticRegression` `B = 1,000` if runtime requires, or `10,000` if fast).
3. **Sensitivity controls (frozen)**:
   - **Documented-context control**: repeat component-block permutation restricted to objects with documented findspot `W` vs. `O` (never treating stamp-derived `W1` as an independent context variable).
   - **Rao Plate CLXI F control**: repeat primary tests dropping `L-161` and `L-164` (the two objects entangled by Rao 1985 p. 319 vs. p. 325) and also dropping the entire `G02` elephant component to measure whether any signal survives outside `G02`.
   - **Within-component attachment dispersion test**: for every component with ≥ 2 diagnostic specimens, compute observed within-component class purity and Shannon entropy and compare against random specimen groupings of the same component sizes (`B = 10,000`).

### 3.6 Independent verification (`verify.py`)

A standalone verification script `verify.py` will independently:
1. Cross-check all 93 rows of `lothal-attachments-v1.csv` against both `reviewed-pass.csv` and `independent-first-pass.csv` (expecting 100% agreement on all 93 object IDs, impression counts, physical types, and context codes).
2. Recompute the deterministic physical taxonomy mappings (`reverse_class_6`, `diagnostic_class_5`, `is_wood_plank_peg`, `mobility_class`) and verify zero discrepancies.
3. Verify strict anti-leakage: confirm zero overlap of `die_component_strict` and `die_component_substring` IDs between training and test folds in every LOCO split, and confirm that multi-specimen components (`G01`, `G02`, `G03`, etc.) stay intact in every permutation sample.
4. Independently recompute key summary counts and permutation p-values from scratch and record all check verdicts in `verification-v1.json`.
