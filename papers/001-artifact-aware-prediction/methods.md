# Detailed methods and frozen results

This companion to the [manuscript](manuscript.md), written 2 October 2026, describes completed procedures and identifies exploratory refinements by stage. Proposed additions are in [submission-gaps.md](submission-gaps.md).

Links to the corpus, definition JSON, crosswalk and source PDFs point to locally preserved inputs. In a Git clone, the [source-route review](../../experiments/2026-10-02-six-hour/integration-review/checkout-availability/REPORT.md) leads to their acquisition and transformation records. Aggregate results, code and numeric reviews are tracked.

## Data, coding and dependence

The input [lipi_clean_rtl_singleline.jsonl](../../data/normalized/lipi_clean_rtl_singleline.jsonl) has SHA-256 `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`. Completeness, single-line and direction filters precede model fitting. The [loader](../../src/methods/conditional_structure.py) also excludes codes for missing signs and blank space and applies a minimum length, normally three. With at least two signs the cleaned population has 2,930 records and 1,859 strings; with at least three it has 2,107 records and 1,596 strings. A face record, a physical artifact, a complete string and a connected component of linked records are different units.

We reverse the catalogue's visual left-to-right lists into reading order under the documented conventions, preserving raw codes and source direction; the catalogue shows seals as impressions, so its direction metadata refer to the impression. See [orientation_clarification.json](../../research/corpus/orientation_clarification.json).

Rows are linked by a shared artifact identifier or an identical complete string, and components are the transitive closure of these links. The main population with at least three signs has 1,526 components, the largest with 36 records. The unique-string population keeps one representative per string, chosen by a fixed rule, with the union of the artifact identifiers of all its copies (its physical aliases); it has 1,596 rows in 1,526 components, the largest with nine. The representative carries one site and object type, so this weighting changes the population being measured. Earlier unique runs that discarded aliases are superseded.

Five outer folds keep components intact (component-held-out) and balance the number of signs, with ties randomized under a seed. Inner folds rebuild components within the outer training subset. Leave-site-out tests exclude every component touched by any record of the held-out site, including duplicate copies; excluding only direct alias matches does not suffice. Final structural site scores are in separate `transitive_site_transfer.json` files; earlier `leave_site_out` fields can contain weaker exclusions.

The limited merge sensitivity applies [861→817, 405→390 and 706→705](../../research/methods/curated_allograph_collapse.json). Each pair shares an independently supplied Mayig coding class, checked by pairwise set intersection; photographic adjudication of these variants (allographs) remains open.

## Models and normalization

The training vocabulary V comprises the observed training codes plus `UNKNOWN`. The smoothed unigram model U adds 0.5 to every state. For count vector C, total n, prior Q and smoothing strength α,

`Smooth(C,Q;α)(c) = [C(c)+αQ(c)]/[n+α]`.

The independent models are U, `P(c|L,i)=Smooth(C[L,i],U;α)`, and `PM(c|L,i,s)=Smooth(C[L,i,s],P;α)`, where L is text length, i the position (slot) and s the site and object type. Let `B(c|a)=Smooth(C[a→·],U;α)`, the predecessor distribution pooled over positions, and `R(c|a)=B(c|a)/U(c)`. The dependent distribution is

`PMB(c|L,i,s,a)=PM(c|L,i,s)R(c|a)/Σb PM(b|L,i,s)R(b|a)`.

At the first position PMB equals PM. The denominator depends on the predecessor and target slot, and restoration retains it. The baseline and dependent models can select different α values. Unseen test codes map to `UNKNOWN` for likelihood scoring; exact glyph accuracy uses the original code.

## Nested selection and uncertainty

Five outer and three inner component-held-out folds use seed 20261001. Independent candidates are U, and P and PM at α∈{5,20,100,500,2000}; dependent candidates are PMB at those values. Selection maximizes inner held-out log likelihood of noninitial signs (all but the first). Each outer fold owns its training vocabulary and fitted choices.

The principal contrast is

`G=Σrecords Σi≥1[log2 qdependent(xi|history)−log2 qbaseline(xi|metadata)]/Nnoninitial`.

The main fit selects PM with α=500 and PMB with α=100 in all five outer folds, with 8,199 noninitial tokens; the unique-string fit has 6,413. Five thousand component-bootstrap draws resample the already fitted held-out component scores, sum numerator and denominator, then take their ratio. These intervals condition on the corpus and fitted models; they do not refit selection or propagate all transcription uncertainty.

The main result is [nested_primary/nested_results.json](../../research/methods/results/nested_primary/nested_results.json). The corrected unique-string result is [nested_unique_preserved_aliases/nested_results.json](../../research/methods/results/nested_unique_preserved_aliases/nested_results.json). The earlier pilot with α fixed at 20 remains archived because its metadata baseline was smoothed too weakly.

## Full-procedure permutation references

We permute signs independently within each exact `(length,slot,site/type)` cell, preserving its multiset of signs and the row metadata. We record cell counts and token mobility (the share of tokens free to move), because singleton cells cannot change. For each shuffled corpus, [nested_joint_null.py](../../src/methods/nested_joint_null.py) rebuilds the string-dependent groups, reallocates folds, retunes smoothing and computes held-out scores. Earlier references with fixed groups and folds are retained as conditional diagnostics.

The main metadata reference has 1,000 corpora, extending an earlier 100 with their outcomes and seed prefix preserved; the length-and-slot-only reference remains at 100. [The completion audit](../../research/methods/results/joint_nested_primary_1000/extension_audit.json) verifies counts, unchanged observed values and preserved outcomes.

For unique weighting, [nested_unique_conditioned.py](../../src/methods/nested_unique_conditioned.py) rejects proposed shuffles that create any repeated whole string, sampling the original reference conditional on all strings being distinct. The completed post-pilot run accepts 1,000 corpora from 6,569 proposals, keeps every accepted seed and reruns the nested fit on each. [Its audit](../../research/methods/results/joint_nested_unique_conditioned_1000/completion_audit.json) verifies source and input hashes and seed agreement with the independently audited rejection sampler.

The one-sided probability is `(1+exceedances)/(1+accepted trials)`, where an exceedance is a shuffled gain at least as large as the observed gain. Zero exceedances in 1,000 gives 0.000999000999. Shuffled gains can be negative through the dependent model's estimation error and smoothing. Significance is judged against the fitted reference distribution under the stated exchangeability assumption.

## Independent annotation and uncertain events

[independent_annotator.py](../../src/independent_annotator.py) scores the Mayig transcription, whose class labels (P labels) map through a crosswalk to sets of compatible fine codes. It excludes every training component touched by CISI (*Corpus of Indus Seals and Inscriptions*) source artifacts M1–M199 or by a complete fine-code string compatible with an eligible test sequence. This removes 170 training strings, leaving 1,426 strings and 1,362 components. Of 86 eligible faces, five have an unmapped class and seven a position (event) with no candidate seen in training, leaving 74 faces, 73 groups linked by artifact or P-label sequence, and 315 noninitial events.

For candidate sets Ai, the forward state is initially `f1(c)=PM(c|L,0,s)1[c∈A1]`, then

`fi(c)=1[c∈Ai]Σa fi−1(a)PMB(c|L,i,s,a)`.

The final sum gives the specified whole-event probability. Intermediate normalization with an accumulated log scale prevents underflow. Singleton sets recover ordinary fine-code scoring; short-sequence brute force checks the recursion. Candidate sets can overlap across P labels, and each is scored on the fine-code alphabet. Unsupported fine candidates receive zero event probability. Twenty scored faces contain some unsupported alternatives, so a sensitivity on the 54 fully supported faces is retained. Main metadata assume Mohenjo-daro and SEAL:S; subtype-unspecified scoring is separate. The 10,000-draw group bootstrap conditions on the fitted training model. See [the complete event output](../../results/independent_annotator/candidate_event_test.json).

## Known-slot restoration

[restoration.py](../../src/restoration.py) hides each of the 8,009 slots across 1,596 unique strings in 1,526 components in turn, with length known. The fixed-length local posterior multiplies the candidate's predecessor transition by its transition into the next surviving sign, removing absent factors at the boundaries. Only factors common to every candidate cancel. Three inner component-held-out folds choose α separately by exact top-one accuracy, the share of slots whose top-ranked candidate is the original code; both models select 20 in all outer folds. A stable sort resolves ties. Targets unseen in training (out of vocabulary, OOV) remain exact failures even if the `UNKNOWN` bucket receives mass.

We report slot-weighted top-one and top-k inclusion, paired component-bootstrap accuracy differences, means weighting each text equally, and frequency strata. Calibration compares the largest posterior probability with observed exact correctness. [benchmark.json](../../results/restoration/benchmark.json) contains complete summaries; cross-site tests remove whole components touched by any record of the held-out site.

### Conventional first-order Markov model (October 2)

The [new protocol](../../experiments/2026-10-02-six-hour/markov-baseline/PROTOCOL.md) specifies a position-independent first-order model with transition matrix A, learned start probabilities π and an end state E. Its state vocabulary matches each existing outer training fold. For an interior hidden sign between a and b, candidate c scores `A(a,c)A(c,b)`; the first slot uses `π(c)A(c,b)` and the last `A(a,c)A(c,E)`. Scores are normalized over candidate signs, excluding E. Each row of A shrinks toward the training unigram of destination states; start counts shrink toward the training sign unigram.

The grouping and fold construction with seed 20261006 reproduces all 8,009 saved identities, targets, groups and folds. Three component-held-out inner folds select strength from 20/100/500/2000 by exact top-one; ties favour greater strength. The PM and PMB predictions are reused. Ten thousand paired component draws with seed 142 give conditional intervals for the differences. Confidence bins have fixed width .2. Code-averaged (macro) accuracy weights slots by inverse true-code frequency in the complete benchmark, fixed during component resampling. The [results](../../experiments/2026-10-02-six-hour/markov-baseline/main/results.json) record these choices, and an [independent counter verification](../../experiments/2026-10-02-six-hour/markov-baseline/verification.json) checks every ranking and target loss. The smoothing rule differs from Rao et al.'s modified Kneser–Ney rule.

### Second-order Markov model (October 2)

[MARKOV-03](../../experiments/2026-10-02-six-hour/markov-order2/README.md) keeps the first-order comparison's exact queries, physical aliases, components and seed 20261006. It uses two start states, an end state and next-state counts after each two-state history. Each row shrinks toward the first-order row for its latest state, with first-order strength fixed at 20. Candidate scoring multiplies all factors involving the hidden state, including the next two factors when present. Inner exact top-one selection considers 5, 20, 100, 500, 2,000 and backoff-only (first order alone), then chooses 20/20/100/20/20 across outer folds.

The separately specified MARKOV-04 keeps the same class and grid but minimizes summed inner bucket loss, the negative log2 probability of the true sign with unseen signs pooled as `UNKNOWN`. All folds choose backoff-only. Both are model-development runs after the first-order comparison, on the preserved benchmark. Ten thousand component-bootstrap draws with seed 23101 compare models on the same queries. The [findings](../../experiments/2026-10-02-six-hour/markov-order2/FINDINGS.md) report exact top-k, text- and code-averaged accuracy, loss and calibration together.

The independent reviewer reconstructs flat pair and triple counts and uses full-record likelihoods. In one MARKOV-03 query, floating-point evaluation swapped two lower-ranked candidates; exact rational likelihoods show both displaced ranks are exact ties, and target outcomes are unchanged. The original failed review and its refinement are separate results. Both final reviews check all 8,009 queries, candidate masses, losses, correspondence, hidden-target invariance and code and protocol hashes.

## Unknown gap counts and observation law

[gap_restoration.py](../../src/gap_restoration.py) erases one internal gap per intact unique string: `k∼Uniform{1,…,min(3,L−2)}`, then a start drawn uniformly among positions leaving a sign on each side. The predictor sees both surviving sides and compares candidate counts 1–3, summing over hidden fine codes with a dynamic program, a training-derived full-length prior and frozen α=20.

For m surviving signs, candidate length is L=m+k. The artificial masking procedure, or observation law, contributes `1/[min(3,L−2)(L−k−1)]`. Since `L−k−1=m−1` is shared by all candidates, it cancels and leaves the term from the cap at three. [gap_design_matched.py](../../src/methods/gap_design_matched.py) verifies every query and source hash, then reweights the unchanged saved posteriors by `1/min(3,m+k−2)`. The original result remains preserved.

Sampled counts are 815 ones, 454 twos and 327 threes, so the constant-one control, which always guesses one, scores 815/1596=51.0652%. Query seed is 20261012, fold seed 20261006, and the matched-law 10,000-draw component bootstrap seed is 142. The original and reweighted results use the same queries and fitted models.

## Templates, controls and frame transfer

[template_comparison.py](../../src/methods/template_comparison.py) fits, per text length, finite mixtures of templates whose slots have independent sign distributions, selecting from 16, 32 or 64 templates with at least five texts each. The known [nonphonetic routing control](../../research/methods/controls/workflow_codes.jsonl), whose sequences record routes between offices, tests whether dependence beyond that fitted family is specific to language. Corpora published by other authors keep the authors' order and simultaneous composite units. The totem corpus's OOV coverage and the weather corpus's closure into one component prevent treating them as matched language classifiers.

A substitution frame is a fixed-length context identical in every slot but one wildcard. Training components supply discoveries; held-out transfer requires a new frame. Support counts distinct frames, separating pairs that share a mapped graphic class from pairs with disjoint classes. [substitution_joint_null.py](../../src/methods/substitution_joint_null.py) repeats discovery and transfer on every shuffled corpus. Aggregate counts and pair-level maximum statistics have separate reference distributions. Frequency-adjusted maxima are post-pilot sensitivities.

## Extra shrinkage of two-state histories

The [adaptive follow-up](../../experiments/2026-10-02-six-hour/markov-adaptive/PROTOCOL.md) reuses the same hidden slots and component folds, with first-order strength still twenty. For a two-state history seen `N>0` times in training, the second-order weight is multiplied by `N/(N+κ)`, giving effective strength `α+κ+ακ/N`; unseen histories use first order. The grid has seventeen distinct finite settings from α=5/20/100/500/2000 and κ=0/20/100/500, plus exact first-order backoff. Three inner component folds minimize bucket loss. Complete hidden-sign probabilities include start and end events and all later factors involving the candidate.

Every outer fold selects backoff. [The result](../../experiments/2026-10-02-six-hour/markov-adaptive/main/results.json) preserves all ninety candidate-by-fold losses and the paired component intervals. [Independent flat-count review](../../experiments/2026-10-02-six-hour/markov-adaptive/review/verification.json) reconstructs every query, verifies the rational effective-strength identities and checks full-chain probabilities. Detailed source-linked predictions remain local. This protocol follows earlier outcomes and compares models on reused development records.

## Reproduction and preservation

The recorded structural environment is Python 3.13.5 and NumPy 2.2.6, otherwise the standard library. Image and source pipelines need additional packages declared in their scripts and [environment.json](../../output/environment.json). Each output embeds hashes and parameters. Run from the repository root, and write new fits to new dated directories. The retained [reproduction guide](../../research/methods/REPRODUCING.md) supplies all auxiliary commands and the rules for source snapshots.

```powershell
python src/methods/verify_methods.py
python src/methods/nested_joint_null.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output experiments/NEW-DATE/joint_nested --permutations 100 --position-permutations 100
python src/methods/extend_nested_null.py --prior experiments/NEW-DATE/joint_nested/joint_nested_results.json --output experiments/NEW-DATE/joint_nested_1000 --permutations 1000
python src/methods/nested_unique_conditioned.py --input data/normalized/lipi_clean_rtl_singleline.jsonl --output experiments/NEW-DATE/joint_nested_unique --permutations 1000
python src/methods/gap_design_matched.py --prior results/gap_restoration --output experiments/NEW-DATE/gap_design_matched
```

Replace `NEW-DATE` with a fresh dated experiment identifier. Read the registry before running these commands, and use saved results for inspection. Preserve frozen results and record source revisions if a bug is repaired. The [claim map](claim-evidence-map.md) distinguishes the file with the observed confidence interval from the file with its stronger permutation reference, and [the retrospective](../../knowledge/retrospectives/methods.md) names superseded paths.
