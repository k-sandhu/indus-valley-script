# Reproducing the structural analyses

Run commands from the workspace root. The recorded environment is Python 3.13.5 and NumPy 2.2.6; these analyses otherwise use the standard library. The input and source hashes, all parameters, and exact seeds are saved in each JSON output. Seed 20261001 is used throughout; metadata nulls add 10000, and older conditional held-out transfer diagnostics use their separately declared offsets.

The observational input is `data/normalized/lipi_clean_rtl_singleline.jsonl` (SHA-256 `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`). Its acquisition, completeness filters, direction normalization, and provenance are documented in `research/corpus/normalize_lipi.py` and the corpus reports. It is a derivative transcription associated with a disputed decipherment. Proposed sounds, Sanskrit interpretations, and translation files are not inputs. No source license was found for the large export: keep these local research inputs separate from any public redistribution of our code/results. The MIT Mayig crosswalk is a coding-scheme sensitivity from shared historical catalogues, not archaeological replication or proof of every glyph's allography.

Use a fresh output directory for a new run. Earlier unique-loader results named `nested_unique` and `classaware_unique` are archived and superseded because they dropped physical aliases of retained strings; current code preserves all aliases. The separate `transitive_site_transfer.json` files supersede earlier direct-overlap and alias-only site-transfer numbers within otherwise corrected nested runs. They exclude entire physical-artifact/identical-string components touching the test site. `RESULT_INDEX.json` provides a compact index and explicit cautions.

Verify the eight integrity checks and synthetic calibration:

```powershell
python src/methods/verify_methods.py
```

Read-only arithmetic/provenance audits of the source-font development pilot and frozen fresh20 endpoint:

```powershell
python src/methods/audit_font_pilot.py
python src/methods/audit_font_fresh20.py
```

They verify complete ID coverage, independent candidate-set edit calculations and saved summaries; the fresh20 audit also verifies exact sampling and frozen chart-candidate propagation. These do not certify the AI glyph reference as expert gold. The frozen follow-on test performs poorly and remains a negative acquisition result.

The subsequent source inspection diagnoses clipping and adjacent-row contamination. The separate post-reference geometry development diagnostic retains the identical frozen chart, matcher, penalty and horizontal bounds; it does not replace the frozen endpoint:

```powershell
python src/methods/font_geometry_sensitivity.py --geometry research/corpus/primary/font_fresh20/geometry_audit/recommended_clean_bounds.json --output research/methods/results/reproduction_font_geometry_sensitivity
```

Strong training-only nested baseline comparison, with the original fixed-partition null diagnostics:

```powershell
python src/methods/nested_conditional.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output research/methods/results/reproduction_nested --permutations 1000 --position-permutations 200
```

Post-audit null that repeats sequence-dependent grouping, outer folds, inner model selection and prediction:

```powershell
python src/methods/nested_joint_null.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output research/methods/results/reproduction_joint_nested --permutations 100 --position-permutations 100
```

The primary metadata-preserving null was extended to 1,000 corpora in a separate directory, retaining all original 100 outcomes and continuing their exact seed sequence. The position-preserving null remains 100. The extension output records the prior-output hash and the source hashes used for its additional fits:

```powershell
python src/methods/extend_nested_null.py --prior research/methods/results/reproduction_joint_nested/joint_nested_results.json --output research/methods/results/reproduction_joint_nested_1000 --permutations 1000
```

The extension accepts a completed prior run; use a fresh output directory and inspect its `extension.complete` field before reporting the endpoint. In-progress checkpoints are not completed significance results.

```powershell
python src/methods/audit_extension.py --result research/methods/results/reproduction_joint_nested_1000/joint_nested_results.json
```

The audit verifies the unchanged observed result and position null, the original metadata-seed prefix, completed count and exceedances, and available source versions matching every extension hash. The completed primary run has zero exceedances in 1,000 metadata shuffles, reference p=1/1001; this describes the declared transcription randomization model, not linguistic status.

The independent numerical-algebra audit uses exact integer/fraction arithmetic and an unbounded divisor proof, with a separate finite enumeration check:

```powershell
python src/methods/audit_numerical_equalities.py
```

Its constraints are conditional on Fuls's proposed quantity equalities, positional assignments and external range. Their arithmetic uniqueness does not validate a historical numeral reading. The derivation and source-assumption limits are in `NUMERICAL_CONSTRAINT_AUDIT.md`.

Repeat either with `--unique` for one deterministic representative of each whole string, retaining all physical aliases. Add `--collapse research/methods/curated_allograph_collapse.json` for the three compatible-class merges. The retained representative's metadata is still a sensitivity choice. `nested_conditional.py --min-length 2` runs the short-text sensitivity; the original multi-record version contains a giant transitive group, so its unique-string version must accompany it.

An additional post-pilot nested metadata null conditions on the unique-string sampling rule, rejecting proposed shuffled corpora with newly duplicated whole strings. The models and complete nested fit repeat for each accepted corpus, and exact accepted seeds/proposal counts are saved. Do not interpret an in-progress checkpoint as the completed endpoint:

```powershell
python src/methods/nested_unique_conditioned.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output research/methods/results/reproduction_joint_nested_unique_conditioned --permutations 1000
```

The recorded completed run accepts 1,000 corpora from 6,569 proposals in 2,686.75 seconds, with zero exceedances of the observed 0.848358-bit gain and reference p=1/1001. Its completion audit verifies current source/input hashes, every observed fold score against the alias-preserving prior, and all accepted seeds against the earlier independently audited rejection sampler:

```powershell
python src/methods/audit_nested_unique_conditioned.py
```

This audit reads the retained completed run in `results/joint_nested_unique_conditioned_1000/`; use its script as the explicit checks for a reproduction in another output directory.

Joint full-procedure exact-frame transfer, including training discovery on every null corpus:

```powershell
python src/methods/substitution_joint_null.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --classes data/normalized/mayig_wells_class_crosswalk.json --output research/methods/results/reproduction_joint_transfer --permutations 1000
```

Repeat with `--unique` and with the declared `--collapse` argument. `substitution_validation.py` additionally records the raw full-universe maximum-support result and class-separated conditional held-out diagnostics. The post-pilot frequency-adjusted maximum uses a symmetric pooled mean and includes every pair found in any observed/null corpus:

```powershell
python src/methods/substitution_adjusted_max.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --classes data/normalized/mayig_wells_class_crosswalk.json --output research/methods/results/reproduction_adjusted_max --permutations 10000
```

Extended latent independent-slot templates and a known nonphonetic control:

```powershell
python src/methods/template_comparison.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output research/methods/results/reproduction_templates --component-grid 16,32,64 --min-per-component 5
python src/methods/generate_workflow_control.py
python src/methods/template_comparison.py --input research/methods/controls/workflow_codes.jsonl --output research/methods/results/reproduction_workflow --component-grid 16,32,64 --min-per-component 5
```

The control's ground truth is an ordered handoff route between office entities, with no speech encoding. Its residual dependence is a constructive specificity check for this fitted template family. Neither a positive Indus gain nor a small permutation p-value is a language-identification probability.

Source-published nonphonetic comparators retain author order and simultaneous-unit boundaries. Their flattening and artifact-identity limitations are documented by the literature team; do not silently replace compound units with sequential inner members. The following reproduces the exploratory totem comparison and the weather grouping obstacle:

```powershell
python src/methods/assess_controls.py
python src/methods/nested_joint_null.py --input research/literature/nonlinguistic_controls/TotemPoles_author_ordered.jsonl --output research/methods/results/reproduction_totem --permutations 100 --position-permutations 100
python src/methods/template_comparison.py --input research/literature/nonlinguistic_controls/TotemPoles_author_ordered.jsonl --output research/methods/results/reproduction_totem_templates --component-grid 16,32,64 --min-per-component 5
```

Totem unseen-token rates are very high and these corpora are not matched samples for a language classifier. Weather station/duplicate closure contains only one component, so no grouped five-fold score is reported.

To preserve uniqueness as well as exact null marginals in the unique-string substitution sensitivity, use rejection sampling:

```powershell
python src/methods/substitution_joint_null.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --classes data/normalized/mayig_wells_class_crosswalk.json --output research/methods/results/reproduction_unique_conditioned --permutations 1000 --unique --require-unique-null
```

Every accepted seed and total rejection-attempt count is saved. This sensitivity conditions on whole-string uniqueness in the supplied representative population; it does not repair unknown physical aliases in the original archaeological catalogues.

The root gap-count benchmark is exploratory and does not outperform its constant-one design control. To reproduce the separate artificial-masking-law sensitivity after running that benchmark:

```powershell
python src/methods/gap_design_matched.py --prior results/gap_restoration --output research/methods/results/reproduction_gap_design_matched
```

This exactly reweights the unchanged held-out count posteriors by `1/min(3,L-2)`. It verifies the original source/input hashes, reconstructs every query and fold, and uses the same physical/whole-text component bootstrap. Its prior describes the artificial sampling design and must not replace a historical erosion assumption. The original predictor and output are preserved.

Refresh the compact result index:

```powershell
python src/methods/summarize_results.py
```

`code_snapshots/` preserves earlier source versions where saved hashes changed during repairs. The original fixed smoothing-20 endpoint remains archived in `raw_primary`, along with all declared sensitivities; its metadata baseline overfits relative to the stronger nested-selected baseline. Report that limitation rather than substituting a favorable exploratory endpoint without disclosure.
