# Detailed methods and frozen endpoints

Companion to the [manuscript](manuscript.md), written 2 October 2026. Procedures below describe completed work, with exploratory refinements identified by stage. Proposed additions are in [submission-gaps.md](submission-gaps.md).

## Data, coding and dependence

The input [lipi_clean_rtl_singleline.jsonl](../../data/normalized/lipi_clean_rtl_singleline.jsonl) has SHA-256 `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`. Its observational completeness, line-layout and direction filters precede model fitting. The [loader](../../src/methods/conditional_structure.py) additionally excludes missing/blank codes and applies a minimum length, normally three. The clean ≥2 population has 2,930 records and 1,859 strings; ≥3 has 2,107 records and 1,596 strings. A face record, physical artifact, complete string and connected component are different units.

Catalogue strings are visual left-to-right lists. Computational reading order reverses those lists under the documented conventions. Preserve raw codes and source direction; the catalogue represents seals using impressions, so direction metadata refers to that convention. See [orientation_clarification.json](../../research/corpus/orientation_clarification.json).

Rows are connected by any physical alias or identical complete string, with transitive closure. The main ≥3 population contains 1,526 components, largest 36 records. Global uniqueness retains a deterministic representative and the union of every physical alias attached to its copies, giving 1,596 rows and 1,526 components, largest nine. The representative has one metadata stratum, so this weighting changes the population being measured. Earlier unique runs that discarded aliases are superseded.

Five outer folds keep components intact and balance token load after seeded tie randomization. Inner folds rebuild components on the outer training subset. Leave-site-out tests exclude all components touched by a raw held-out-site record; direct alias intersection does not suffice. Final structural site scores live in separate `transitive_site_transfer.json` files. Earlier `leave_site_out` fields can contain weaker exclusions.

The limited merge sensitivity applies [861→817, 405→390 and 706→705](../../research/methods/curated_allograph_collapse.json). These share independently supplied historical coding classes. Membership is checked by pairwise set intersection, while photographic allograph adjudication remains open.

## Models and normalization

Training vocabulary V comprises the observed training codes plus `UNKNOWN`. Smoothed unigram U adds 0.5 to every state. For count vector C, total n and prior Q,

`Smooth(C,Q;α)(c) = [C(c)+αQ(c)]/[n+α]`.

The independent models are U, `P(c|L,i)=Smooth(C[L,i],U;α)`, and `PM(c|L,i,s)=Smooth(C[L,i,s],P;α)`, where s is site/type. Let `B(c|a)=Smooth(C[a→·],U;α)` and `R(c|a)=B(c|a)/U(c)`. The dependent distribution is

`PMB(c|L,i,s,a)=PM(c|L,i,s)R(c|a)/Σb PM(b|L,i,s)R(b|a)`.

At the first position PMB equals PM. The denominator depends on the predecessor and target slot; restoration retains it. The baseline and dependent models can have different selected α values. Unseen test codes map to `UNKNOWN` for likelihood scoring; exact glyph accuracy uses the original code.

## Nested selection and uncertainty

Five outer and three inner component-held-out folds use seed 20261001. Independent candidates include U and P/PM at α∈{5,20,100,500,2000}; dependent candidates are PMB at those values. Selection maximizes inner noninitial held-out log likelihood. Each outer fold owns its training vocabulary and fitted choices.

The principal contrast is

`G=Σrecords Σi≥1[log2 qdependent(xi|history)−log2 qbaseline(xi|metadata)]/Nnoninitial`.

The main fit selects PM@500 and PMB@100 in all five outer folds, with 8,199 noninitial tokens. Unique weighting has 6,413 noninitial tokens. Five thousand component-bootstrap draws resample already fitted held-out component scores, sum numerator and denominator, then take their ratio. These intervals condition on the corpus and fitted models; they do not refit selection or propagate all transcription uncertainty.

The main endpoint is [nested_primary/nested_results.json](../../research/methods/results/nested_primary/nested_results.json). The corrected unique endpoint is [nested_unique_preserved_aliases/nested_results.json](../../research/methods/results/nested_unique_preserved_aliases/nested_results.json). The earlier fixed-20 pilot remains archived because its metadata baseline was insufficiently regularized.

## Full-procedure permutation references

Independently permute signs within each exact `(length,slot,site/type)` cell, preserving its multiset and row metadata. Record cell counts and token mobility because singleton cells cannot change. For each null corpus, [nested_joint_null.py](../../src/methods/nested_joint_null.py) rebuilds data-dependent groups, reallocates folds, retunes smoothing and computes held-out scores. Earlier fixed-group/fold references are retained conditional diagnostics.

The main metadata reference has 1,000 corpora; its extension preserves the original 100 outcomes and seed prefix. Its position-only reference remains at 100. [The completion audit](../../research/methods/results/joint_nested_primary_1000/extension_audit.json) verifies counts, unchanged observed values and preserved outcomes.

For unique weighting, [nested_unique_conditioned.py](../../src/methods/nested_unique_conditioned.py) rejects proposed column shuffles that create any repeated whole string. It samples the original reference conditional on complete-string uniqueness. The completed post-pilot run accepts 1,000 corpora from 6,569 proposals, preserving every accepted seed. It reruns the nested fit on each accepted corpus. [Its audit](../../research/methods/results/joint_nested_unique_conditioned_1000/completion_audit.json) verifies source/input hashes and seed agreement with the independently audited rejection sampler.

The one-sided probability is `(1+exceedances)/(1+accepted trials)`. Zero exceedances in 1,000 gives 0.000999000999. Negative fitted-null gains can arise from dependent estimation and regularization. Significance is evaluated against the fitted reference distribution under the stated exchangeability law.

## Independent annotation and uncertain events

[independent_annotator.py](../../src/independent_annotator.py) excludes all training components touched by CISI M1–M199 source artifacts or by an eligible test sequence compatible with a fine-code complete string. It removes 170 training strings, leaving 1,426 strings and 1,362 components. The test has 86 eligible faces, five unmapped and seven without a supported candidate in at least one event, leaving 74 faces, 73 artifact/P-text groups and 315 noninitial events.

For candidate sets Ai, the forward state is initially `f1(c)=PM(c|L,0,s)1[c∈A1]`, then

`fi(c)=1[c∈Ai]Σa fi−1(a)PMB(c|L,i,s,a)`.

The final sum gives the specified whole-event probability. Intermediate normalization with accumulated log scale prevents underflow. Singleton sets recover ordinary fine-code scoring; short-sequence brute force checks the recursion. Candidate sets can overlap across P labels, and each is scored on the fine-code alphabet. Unsupported fine candidates receive zero event probability. Twenty scored faces contain some unsupported alternatives, so a 54-face fully supported sensitivity is retained. Main metadata assumes Mohenjo-daro/SEAL:S; subtype-unspecified scoring is separate. The 10,000-draw group bootstrap conditions on the fitted training model. See [the complete event output](../../results/independent_annotator/candidate_event_test.json).

## Known-slot restoration

[restoration.py](../../src/restoration.py) masks each of the 8,009 slots across 1,596 unique strings in 1,526 components. The fixed-length local posterior multiplies the candidate's predecessor transition by the next survivor's candidate-dependent transition, removing absent factors at the boundaries. Only factors common to every candidate cancel. Three inner grouped folds choose α separately by exact top-one accuracy; both families select 20 in all outer folds. Stable ranking resolves ties. OOV fine targets remain exact failures even if an `UNKNOWN` bucket receives mass.

Report slot-weighted top-one and top-k inclusion, paired component-bootstrap accuracy differences, equal-text means and frequency strata. Calibration compares maximum posterior mass with observed exact correctness. [benchmark.json](../../results/restoration/benchmark.json) contains complete summaries; cross-site tests remove whole components using the raw site populations.

### October 2 conventional comparator

The [new protocol](../../experiments/2026-10-02-six-hour/markov-baseline/PROTOCOL.md) specifies a position-independent first-order model with learned start probabilities and an end state E. Its state vocabulary matches each existing outer training fold. For internal masks between a and b, score candidate c by `A(a,c)A(c,b)`; use `π(c)A(c,b)` initially and `A(a,c)A(c,E)` finally. Normalize over candidate glyph states, excluding E. Outgoing rows shrink toward a training destination unigram; start counts shrink toward the training glyph unigram.

The 20261006 grouping/fold construction reproduces all 8,009 saved identities, targets, groups and folds. Strength is selected from 20/100/500/2000 by three grouped inner folds maximizing exact top-one; ties favor greater strength. The PM/PMB predictions are reused. Ten thousand paired component draws with seed 142 produce conditional contrast intervals. Confidence bins are fixed at width .2. Macro-code weights use inverse true-code frequency in the complete benchmark and remain fixed during component resampling. [Results](../../experiments/2026-10-02-six-hour/markov-baseline/main/results.json) record these choices, and an [independent counter verification](../../experiments/2026-10-02-six-hour/markov-baseline/verification.json) checks every ranking and target loss. The smoothing rule differs from Rao et al.'s modified Kneser–Ney rule.

### October 2 second-order comparison

[MARKOV-03](../../experiments/2026-10-02-six-hour/markov-order2/README.md) retains the comparator's exact queries, physical aliases, components and seed 20261006. It uses two start states, an end state and next-state counts after each two-state history. Each row shrinks toward the first-order row after its latest state, with a fixed first-order strength of 20. Candidate scoring multiplies all factors involving the masked state, including the next two factors when present. Inner exact top-one selection considers 5, 20, 100, 500, 2,000 and backoff-only, then chooses 20/20/100/20/20 across outer folds.

The separately specified MARKOV-04 retains the same class and grid but minimizes summed inner bucket loss. All folds choose backoff-only. These are post-comparator model-development runs on the preserved benchmark. Ten thousand component-bootstrap draws with seed 23101 compare their unchanged query populations. The [findings](../../experiments/2026-10-02-six-hour/markov-order2/FINDINGS.md) report exact top-k, equal-text/code accuracy, loss and calibration together.

The independent reviewer reconstructs flat edge and triple counts and uses full-record likelihoods. One lower-rank floating-point discrepancy in MARKOV-03 has two exact rational tie witnesses; target outcomes remain unchanged. The original failed review and its refinement are separate endpoints. Both final reviews check all 8,009 queries, candidate masses, losses, correspondence, hidden-target invariance and code/protocol hashes.

## Unknown gap counts and observation law

[gap_restoration.py](../../src/gap_restoration.py) draws one internal gap per intact unique string: `k∼Uniform{1,…,min(3,L−2)}`, then a valid internal start uniformly. The predictor observes both surviving sides and compares candidate counts 1–3. It sums hidden fine-state paths using a dynamic program, a training-derived full-length prior and frozen α=20.

For survivor count m, candidate length is L=m+k. The artificial observation law contributes `1/[min(3,L−2)(L−k−1)]`. Since `L−k−1=m−1`, cancellation leaves the clipping term. [gap_design_matched.py](../../src/methods/gap_design_matched.py) verifies every query and source hash, then reweights unchanged saved posteriors by `1/min(3,m+k−2)`. The historical endpoint remains preserved.

Sampled counts are 815 ones, 454 twos and 327 threes, yielding the constant-one control 815/1596=51.0652%. Query seed is 20261012, fold seed 20261006, and the matched-law 10,000-draw component bootstrap seed is 142. The original and reweighted results use the same queries and fitted models.

## Templates, controls and frame transfer

[template_comparison.py](../../src/methods/template_comparison.py) selects finite independent-slot mixtures from 16,32,64 components with minimum component size five. The known [nonphonetic routing control](../../research/methods/controls/workflow_codes.jsonl) tests whether residual dependence beyond that fitted family is specific to language. Source-published controls preserve author order and simultaneous composite units. Totem OOV coverage and weather's one-component closure prevent treating them as matched language classifiers.

Exact substitution frames have one wildcard and identical remaining length/slot/context. Training components supply discoveries; held-out transfer requires a new frame. Support counts distinct frames, with shared mapped graphic classes separated from disjoint classes. [substitution_joint_null.py](../../src/methods/substitution_joint_null.py) repeats discovery and transfer on every shuffled corpus. Aggregate counts and pair-level maximum statistics have separate reference distributions. Frequency-adjusted maxima are post-pilot sensitivities.

## Reproduction and preservation

The recorded structural environment is Python 3.13.5 and NumPy 2.2.6, otherwise the standard library. Image/source pipelines have additional packages declared in their scripts and [environment.json](../../output/environment.json). Each output embeds hashes and parameters. Run from repository root; new fits must use new dated directories. The retained [reproduction guide](../../research/methods/REPRODUCING.md) supplies all auxiliary commands and source-snapshot rules.

```powershell
python src/methods/verify_methods.py
python src/methods/nested_joint_null.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output experiments/NEW-DATE/joint_nested --permutations 100 --position-permutations 100
python src/methods/extend_nested_null.py --prior experiments/NEW-DATE/joint_nested/joint_nested_results.json --output experiments/NEW-DATE/joint_nested_1000 --permutations 1000
python src/methods/nested_unique_conditioned.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output experiments/NEW-DATE/joint_nested_unique --permutations 1000
python src/methods/gap_design_matched.py --prior results/gap_restoration --output experiments/NEW-DATE/gap_design_matched
```

Replace `NEW-DATE` with a fresh dated experiment identifier. Read the registry before running these commands, and use saved results for inspection. Preserve frozen endpoints and record source revisions if a bug is repaired. The [claim map](claim-evidence-map.md) distinguishes the observed CI file from its stronger null file, and [the retrospective](../../knowledge/retrospectives/methods.md) names superseded paths.
