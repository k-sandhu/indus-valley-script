# Methods retrospective

This account records observable analysis choices, errors, repairs and outcomes from the 1–2 October 2026 investigation. The [experiment registry](../experiments/registry.json) and [methods result index](../../research/methods/RESULT_INDEX.json) retain machine-readable paths. Manuscript preparation is a separate later task.

## Research question and initial design

The methods work sought structural constraints that could be tested without assigning sounds. The main avenues were local dependence beyond length/position/metadata, exact-frame substitution, finite-template adequacy, external context, and numerical equality proposals. Primary-literature review ran alongside analysis. It established that broad positional classes, Markov restoration, modified-fish interchangeability and duplicate controls had prior support, which narrowed the contribution to new measurements and their evaluation rules.

The normalized ≥3 input has 2,107 records, 1,596 strings and 1,526 transitive artifact/string components. Source definitions and code order were checked before interpreting specific sign patterns. The distinction between two short strokes W002 and two tall strokes W032 mattered for proposed numerical modules. The code order was eventually confirmed against explicit primary examples and seal-impression conventions. [Source definitions](../../data/normalized/source_definitions.json) and [orientation clarification](../../research/corpus/orientation_clarification.json) preserve those decisions.

## Structural modelling: pilot, stronger baseline and full null

The first implementation compared smoothed independent unigram/slot/metadata distributions with a normalized local transition model at fixed smoothing 20. It also counted exact wildcard frames. `pilot`, `raw_primary` and `collapsed_primary` retain this stage. The fixed strength was too weak for sparse metadata cells, making the baseline lose predictive performance. The original comparison therefore overstated the advantage relative to a better independent model.

The repair was training-only nested selection: three inner grouped folds selected from smoothing 5,20,100,500,2000, within five outer grouped folds. PM@500 and PMB@100 were chosen in every main fold. Gain was 0.890 bits per noninitial sign, with conditional component interval 0.817–0.965. Reversal, compatible-class merges, unique strings and the inclusion of two-sign texts were tested separately.

The early permutation diagnostics kept observed data-derived group/fold assignments fixed. Whole-string links change when a corpus is shuffled, so a later full-procedure reference repeated grouping, folds, tuning and prediction. The main metadata reference was extended from 100 to 1,000 while preserving its original prefix and exact seeds. It had zero exceedances; p=1/1001. Position-only and fixed-fold diagnostics remain archived at their recorded resolutions.

The unique-string reference raised a separate sampling issue: ordinary column shuffles can create duplicate strings in a population selected to be unique. A post-pilot rejection sampler conditioned on no repeated resulting whole string. The completed run accepted 1,000 corpora from 6,569 proposals, in 2,686.75 seconds, with zero exceedances of the 0.848-bit observed gain. Its null mean was 0.0071 bits. Every accepted seed is recorded. This is an additional sampling-rule sensitivity with an explicit conditional reference.

| Stage | Retained result family | How to use it |
|---|---|---|
| Fixed-20 pilot | `pilot`, `raw_primary`, `collapsed_primary` | Historical baseline diagnosis and initial design record. |
| Nested comparison | `nested_pilot`, `nested_primary`, `nested_reverse`, `nested_collapsed` | Main fitted gains and declared sensitivities. |
| Unique rows before alias repair | `nested_unique` | Superseded unique population. |
| Unique rows after alias repair | `nested_unique_preserved_aliases` | Current unique fitted gain and CI. |
| Two-sign extension | `nested_length2`, `nested_length2_unique_preserved_aliases` | Short-text sensitivity; the multi-record version has a giant component. |
| Full refitting null | `joint_nested_primary`, `joint_nested_primary_1000`, `joint_nested_unique` | Complete-procedure references; check each trial count and conditioning rule. |
| Unique-conditioned full null | `joint_nested_unique_conditioned_1000` | Current sampling-rule sensitivity and completion audit. |

Each directory is under `research/methods/results/`; exact filenames and hashes are in [RESULT_INDEX.json](../../research/methods/RESULT_INDEX.json). The scripts are [conditional_structure.py](../../src/methods/conditional_structure.py), [nested_conditional.py](../../src/methods/nested_conditional.py), [nested_joint_null.py](../../src/methods/nested_joint_null.py) and [nested_unique_conditioned.py](../../src/methods/nested_unique_conditioned.py).

## Deduplication and site-transfer errors

An early unique loader chose one representative per text and dropped artifact identifiers attached to discarded copies. Different retained texts on those objects could then cross folds. The shared loader was repaired to union every copy's `artifact_aliases` before grouping. This changed component membership in unique analyses and required downstream restoration and frame analyses to be rerun. Root preserved [the old restoration endpoint](../../results/restoration_superseded_lost_aliases/) and saved corrected results at the original current restoration path.

Site-transfer checks initially removed direct string/artifact overlap, then direct aliases. A component can also reach a test-site artifact indirectly through another exact string. The final [alias_safe_site_transfer.py](../../src/methods/alias_safe_site_transfer.py) removes entire transitive components touched by the raw test site. Corrected results are separate `transitive_site_transfer.json` files. Earlier embedded site fields and intermediate `alias_safe_site_transfer.json` remain available for comparison.

This error demonstrated why source identity must survive every representation change. Deduplication, glyph merging and choice of a metadata representative can alter the graph. Grouping should be recomputed after each transformation, and every split should check all aliases rather than only the representative ID.

## Substitution candidates and selection

Initial exact-frame counts highlighted W817/W861, W817/W820, several fish pairs, W390/W405 and W705/W706. The independent crosswalk showed that some leading pairs share historical graphic classes. Literature review found the opener environments and modified-fish interchangeability in earlier work.

Class-aware discovery separated shared-class, disjoint-class and unresolved pairs. Early held-out permutation diagnostics fixed training discoveries, and five training partitions overlapped. The full joint reference subsequently repeated discovery, grouping and transfer for each shuffled corpus. Aggregate disjoint-class transfer was five in the multi-record population, with metadata-null mean 5.005 and p≈0.541. The unique population had three transfers and stronger aggregate evidence; uniqueness-conditioned transfer gave p≈0.003. The merged multi-record sensitivity remained unexceptional.

A post-pilot frequency-adjusted maximum statistic increased sensitivity for rare pairs. The primary reference was extended to 10,000 trials. For W176/W904 its primary family-wise probability was approximately 0.130, while unique weighting gave a smaller adjusted value and a nonsignificant raw maximum-support result. These endpoints make the selected pair's support sensitive to population and statistic.

Three W176/W904 contexts were exported for source review. The M289 primary plate corroborated broad forms; H697 and Ad3 supplied derivative photographic witnesses; other objects remained incompletely photographed. Ad3/H2139 had already been juxtaposed in a 2025 bulletin. The transfer assay can evaluate a published example, while source and priority checks still determine what the example contributes.

Retained families: `classaware_pilot`, `classaware_primary`, `classaware_collapsed`, `classaware_unique` (old aliases), `classaware_unique_preserved_aliases`; `joint_transfer_primary`, `joint_transfer_collapsed`, `joint_transfer_unique`, `joint_transfer_unique_conditioned`; `adjusted_max_primary`, `adjusted_max_primary_10000`, `adjusted_max_unique`. Code is [substitution_validation.py](../../src/methods/substitution_validation.py), [substitution_joint_null.py](../../src/methods/substitution_joint_null.py), [substitution_adjusted_max.py](../../src/methods/substitution_adjusted_max.py) and [export_candidate_audit.py](../../src/methods/export_candidate_audit.py). The [candidate priority audit](../../research/literature/candidate_pair_novelty_audit.md) and [photo-status record](../../research/corpus/plate_audit/pair_176_904/audit_status.json) accompany these outputs.

## Template models and comparison systems

Independent-slot mixtures were fitted first with a smaller family, then with 16/32/64 components. The extended template model gained 0.142 bits over the independent baseline; PMB still exceeded it by 0.748 bits. A generated office-routing system, with no speech encoding in its mechanism, also yielded PMB−template gain of 0.631 bits. This supplied a counterexample to specificity of the tested template assay.

The literature team acquired Sproat's comparison corpora and preserved author order and simultaneous composite units. Conservative totem flattening left 180 clear ≥3 units, 176 distinct texts and 173 components. OOV coverage was poor, approximately 43.7% of noninitial tokens. Its small positive fitted gain was unexceptional under the fitted metadata reference. Weather station/identical-text closure created one component; grouped cross-validation was infeasible under that rule, and this obstacle was recorded.

`templates_primary`, `templates_extended`, `workflow_templates`, `totem_nested`, `totem_joint_nested` and `totem_templates` retain these fits. [assess_controls.py](../../src/methods/assess_controls.py) documents feasibility. Units, uncertain exclusions and known source aliases are described in [the comparison-data README](../../research/literature/nonlinguistic_controls/README.md). Sproat's conceptual critique and Nair's 2026 comparator/template preprint preceded this investigation; the specific fitted assay and grouping measurements are the project contribution.

## Reviews of root analyses

Root implemented known-slot restoration, unknown-count gaps, independent annotation and context/paired-face experiments. Methods work inspected their grouping, probability normalization, sampling laws and interpretations without editing root files.

Known-slot restoration included the candidate-dependent successor normalizer and did not inspect the masked target. After the alias repair its exact top-one scores were 16.99% and 33.81%, over 8,009 slots. Equal-text weighting retained the advantage, while rare-type coverage and mass calibration were weaker. [audit_root_restoration.py](../../src/methods/audit_root_restoration.py), [root_restoration_audit.json](../../research/methods/root_restoration_audit.json) and [restoration_frequency_audit.json](../../research/methods/restoration_frequency_audit.json) record the checks.

The gap prototype's artificial observation law included a clipped count range. Methods derived the missing factor `1/min(3,L−2)` and reweighted the saved posteriors while preserving models and queries. Accuracy changed from 43.05% to 46.30% locally; always-one remained 51.07%. The result stayed below the design control. [GAP_MODEL_REVIEW.md](../../research/methods/GAP_MODEL_REVIEW.md), [gap_design_matched.py](../../src/methods/gap_design_matched.py) and `gap_design_matched/gap_design_matched.json` preserve the derivation and result.

The independent-annotator forward recursion summed compatible fine-state paths correctly. Methods reviewed source-range removal, transitive exclusion, unsupported-candidate handling, overlap of coding sets, and the event-likelihood estimand. The 74-face main gain was 0.725 bits, with 54 fully supported faces reported separately. [The audit](../../research/methods/independent_annotator_audit.json) names these checks.

Context permutations originally moved row labels despite duplicate/mixed-label whole-string groups. Root implemented deterministic one-representative-per-global-string sensitivities. The corrected independent-text seal/tablet gain was 0.0482 nats with p=0.0005; the Bull1 gain was −0.0568 with p=0.556. Microcontext known-period probabilities ranged from 0.0560 to 0.0864 across weighting/merging variants. Paired geometry tests did not establish a quantity interpretation. Root files and [its retrospective](root-investigation.md) retain these experiments.

## Numerical and source constraint audit

Methods checked Fuls's proposed `v=2S−L` and `vL+1=7S+5`. Exact elimination yields `(2L−7)S=L²+4`; hence `2L−7` divides 65. The positive integer triples are (4,20,36), (6,8,10), (10,8,6) and (36,20,4). The stated L ranges 8..13 or 8..18 leave 10/8/6. The joint equations already impose the reported even S values and composite L values. The source's argument from integer `(v+L)/2` to even S was separately refuted with a first-equation counterexample.

The audit also explored hypothetical first-face tall-stroke counts two, three and four, each with the other proposed relation held fixed. The three-case result is in [numerical_count_delta_sensitivity.json](../../research/methods/results/numerical_equalities/numerical_count_delta_sensitivity.json). It was once misdescribed in a report draft as 35 coefficient sensitivities; the final report corrected that statement and named the separate script.

Primary-source work identified additional limits: a historical numeric tablet ID cannot be joined to the current object with the same integer; the H904/Vats physical join has documentary support, but the author's historical ICIT3786 link remains provisional; M1383's external count range was not established by the inspected original Vidale chapter. Exact computation remains conditional on the proposed quantities, ranks and range. [NUMERICAL_CONSTRAINT_AUDIT.md](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md) and [source premises](../../research/literature/metrology/numerical_source_premises.json) separate those layers.

## Printed-font evaluation and geometry repair

Read-only audits checked the ten-row development pilot and a frozen fresh20 sample: ID coverage, reference hashes, candidate-set edit dynamic programming, candidate width and count summaries. On fresh20, 96 drawn units had 107 predictions, 14 row counts matched, strict top-one had 69 edits and two compatible whole rows; top-five had 60 edits and five whole rows. The metric is summed edit distance, with insertions/deletions/substitutions and set compatibility.

Primary crop review found top clipping in 18 rows and following-row ink in 14. The methods-owned post-reference geometry diagnostic changed vertical bounds using source-only reviewed gaps, retaining frozen horizontal bounds, chart snapshot, matcher, penalty and manual candidate unions. Predictions were saved before evaluation against already known references. It produced 96 units, 18 matching counts, 24 strict top-one edits and six whole rows; top-five had six edits and 16 whole rows. These are development measurements after the fresh reference had been revealed.

The frozen chart had 14 ambiguity cells; later atlas corrections yielded 16. Fresh scores retain the original snapshot. The ten-row pilot also disclosed partial row-1020 reference leakage during a crop repair and preserved its nine-row exclusion. [FONT_PILOT_AUDIT.md](../../research/methods/FONT_PILOT_AUDIT.md), `font_pilot_audit`, `font_fresh20_audit` and `font_geometry_sensitivity` keep these distinctions and hashes. Root independently reproduced the geometry arithmetic.

## Integrity checks, reporting and reuse

Eight methods checks passed for normalization, OOV behavior, connected splits, alias retention, transitive site exclusion, exact null margins, distinct-frame counts and a nonphonetic synthetic control. Source snapshots preserve helper versions tied to historical hashes. Long jobs checkpointed progress; completion audits verified accepted counts and seeds before the report used them. The final [quantitative review](../../research/methods/FINAL_REPORT_REVIEW.md) checked the 18-page report and resolved the coefficient-count and CLI-spacing mistakes.

For future work, select the current endpoint from the registry before running a script. A retry should name its new input, corrected premise or changed predictor. Preserve failed outcomes, especially unknown-count recovery, totem coverage, the weather grouping obstacle and fresh20 acquisition. Keep the independent alphabet, candidate sets, sampling law, graph and weighting rule attached to every number. A model change can then be evaluated against an identifiable previous result rather than an undocumented favorable variant.

The [reproduction guide](../../research/methods/REPRODUCING.md), [manuscript methods](../../papers/001-artifact-aware-prediction/methods.md) and [submission gaps](../../papers/001-artifact-aware-prediction/submission-gaps.md) provide the next entry points. No old fit needs repeating to rediscover these findings.
