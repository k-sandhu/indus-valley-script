# Conditional reference laws for short inscriptions: copies, selection and fitting feasibility

Private working manuscript, 2 October 2026. The original main and imperfect-face main audits are complete. Authorship, affiliations and venue remain to be supplied. Computational analysis and writing used AI assistance. Code snapshots, finite tables, proposals, results and independent audits are retained in the project repository.

## Abstract

Permutation references for short inscriptions depend on the process that produced and selected the records. We test those dependencies using finite enumeration and known simulated populations with the project's preserved nested prediction statistic. Across 1,000 literal-copy populations, individual-record shuffling rejects 15.9% at a nominal 5% threshold, while object shuffling rejects 5.4%; the paired excess is 10.5 percentage points, with a 95% interval of 8.5–12.6. With two imperfect faces per object, the corresponding rates are 11.0% and 5.0%, with a paired excess of 6.0 points and interval 4.3–7.7. Six balanced binary records admit 8,000 column tables, of which 2,880 have distinct whole strings; rejection sampling is uniform on that subset. Deduplicating seven independent draws into six retained strings gives unequal subset masses, changing the exact 5% rejection probability from 5.0000% to 5.1537% under the uniform-unique reference. A matched selected-law reference gives 4.9407%. A separate same-margin witness has either one physical/text component and an undefined five-fold fit, or twenty components and a finite score. Explicit score extension and feasibility conditioning give different exact rejection fractions among usable observations. The examples specify record dependence, selection and the fitting domain together with a reference test.

## 1. The record process belongs in the reference question

A catalogue can contain independent objects, several impressions from one stamp, two faces of one object, or several descriptions of the same inscription. A reference that moves each row independently gives those cases the same freedom. A reference that keeps object observations together preserves a different set of possible tables. The question is whether those tables follow the law claimed for the observed population.

The project previously measured held-out local predictive gain in selected Indus transcriptions. Its main reference shuffles exact length/slot columns within site/type strata and rebuilds physical/text groups, folds and model selection for every proposal. A unique-string sensitivity rejects proposals that introduce a repeated whole string. [Original methods](../001-artifact-aware-prediction/methods.md). The present study examines the conditional sampling laws underlying that procedure. Its data are finite combinatorial tables and generated populations with specified dependence. They permit exact probabilities and independent replay.

The statistical principles have established precedents. Phipson and Smyth describe finite random-reference p-values, including the observed score in the rank calculation. Hemerik and Goeman develop exact random-permutation testing. Winkler and colleagues give block permutation methods for related observations. Hurlbert's experimental-design treatment explains how replicated observations depend on the experimental unit. Our contribution is the collection of explicit table laws, measured calibration outcomes and preserved domain failures for this short-record fitting procedure. [Primary rank source](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf), [exact testing](https://link.springer.com/article/10.1007/s11749-017-0571-1), [block permutation](https://pmc.ncbi.nlm.nih.gov/articles/PMC4644991/), [experimental units](https://doi.org/10.2307/1942661).

## 2. Statistic, sampling and checks

### 2.1 The preserved fitting statistic

The statistic is held-out dependent-minus-independent log score, measured in bits per noninitial sign. Physical aliases and identical whole strings define edges in a transitive component graph. Five outer folds keep components intact. Three inner folds select an independent unigram, length/slot or length/slot/metadata model and the local-dependency strength. The smoothing grid is 5, 20, 100, 500 and 2,000. Every observed and reference corpus repeats grouping, fold allocation, training-only selection and scoring from unchanged method snapshots. [Main protocol](../../experiments/2026-10-02-six-hour/null-calibration/MAIN_PROTOCOL.md), [snapshot hashes](../../experiments/2026-10-02-six-hour/null-calibration/sources/).

For 99 independently drawn reference scores, the one-sided Monte Carlo p-value is `(1 + exceedances)/100`, with equality included in the exceedance count. Exact finite calculations instead sum the full declared tail probability. Rejection fractions are reported at 1%, 5% and 10%. Monte Carlo rate intervals describe the generated trial collection. The conditional rank argument assumes that the observed and reference tables follow the same conditional law and that the fitting statistic is defined on its support.

Physical sampling blocks and held-out components serve different purposes. A physical block identifies observations tied by the generating process. A component identifies records excluded together from fitting. Rebuilding the latter on a shuffled table prevents a fitting leak; it does not alter that table's sampling probability. Both structures are saved and audited.

### 2.2 Conditional column spaces

Within a fixed length/slot/metadata cell, independent categorical draws give a table probability determined by the sign counts. Conditioning on those counts makes every labeled arrangement equiprobable. If a cell has `n` entries and category counts `m(v)`, it has `n!/∏m(v)!` distinct arrangements. Every arrangement has `∏m(v)!` generating labeled permutations. Repeated values therefore have equal multiplicity across arrangements.

Whole-string uniqueness restricts the complete table space. Uniform column proposals accepted only when all row strings differ remain uniform on that subset. This follows by conditioning a uniform proposal on its acceptance event. The waiting time changes computational cost; the accepted table law follows the restriction. We verify those probabilities by full enumeration and independent sampler counts. [Mathematical derivation](../../experiments/2026-10-02-six-hour/null-calibration/MATHEMATICS.md).

### 2.3 Physical observations and imperfect faces

Literal copies share a latent object's signs. Their matched reference permutes slot columns among objects within strata, then expands each object to its declared records. Equal copy counts preserve latent and expanded margins together. Unequal counts require weighted constraints or a reference conditioned on additional copy classes.

The imperfect-face experiment has twenty objects, two faces per object, three slots and eight categories. An observed face retains the latent sign with probability .9; otherwise it selects uniformly among the other seven signs. Face errors are independent conditional on that sign. The ordered vector of both face signs has probability `r(a,b)=Σ p(x)K(a|x)K(b|x)`. Conditioning on vector counts in a cell makes its labeled vector arrangements uniform. Permuting whole vectors preserves that joint margin and each face's scalar margin. [Observation law](../../experiments/2026-10-02-six-hour/null-calibration/noisy-faces/METHODS.md).

This experiment compares vector shuffling with individual-record column shuffling on the same 1,000 observed populations. Each case has 99 reference corpora per method. The original score and nested procedure are unchanged. Distinct seed namespaces prevent overlap between reference streams. An audit reconstructs all observations and proposals, joint margins, aliases, graph components, fold loads, p-values and aggregates, then repeats fifteen complete fits.

## 3. Finite spaces expose the sampling distinctions

### 3.1 Uniqueness conditioning

Six labeled binary records with three ones in each of three columns have `20³=8,000` complete tables. There are eight possible whole strings. Selecting six distinct strings with balanced columns requires omitting one complementary pair. Four possible omitted pairs and `6!` label arrangements give 2,880 unique tables. The exact rejection-sampler acceptance probability is .36, and every accepted table has probability `1/2,880`.

The preserved nested statistic was fitted on all 2,880 unique tables. Its inclusive tails reject exactly 5% at the 5% cutoff. Independent enumeration checks table identity, permutation multiplicity, acceptance and every saved tail. The ordinary tiny space includes component counts too small for the original five-fold fit; those cases motivated the separately specified domain experiment below. [Exact endpoint](../../experiments/2026-10-02-six-hour/null-calibration/exact/results.json), [independent audit](../../experiments/2026-10-02-six-hour/null-calibration/verification_exact.json).

### 3.2 Deduplication as an observed selection process

Drawing seven raw independent strings and retaining each distinct string once supplies a different law. Let the three binary slot probabilities be .2, .3 and .4. Condition on six retained strings with three ones in each retained column, then assign their row labels uniformly. The four support masses are 21.3333%, 24.6667%, 26.6667% and 27.3333%, ordered by omitted pairs `000/111`, `001/110`, `010/101` and `011/100`. A population directly conditioned on six unique strings gives 25% to each.

For support `S`, the seven-draw probability is proportional to `∏q(x) Σq(x)` over its retained strings. The fixed retained margins fix the product, while the sum varies. Each support spreads its mass over 720 row arrangements. Reweighting the existing nested scores gives a 5.1537% rejection fraction when the uniform-unique reference is retained. Matching the reference to the selected law gives 4.9407%. The largest excess over a nominal attainable cutoff is .6046 percentage points in this finite process. [Exact probabilities and tails](../../experiments/2026-10-02-six-hour/null-calibration/dedup-selection/results.json).

An independent recurrence propagates probabilities over the set of strings seen after each raw draw. It verifies the four support masses without using the occupancy formula and checks all 11,520 stored tail values. This example identifies the selection assumption required to interpret a uniqueness-conditioned reference beyond its selected population.

### 3.3 Copies and weighted margins

Four binary latent objects with balanced columns have 216 tables. Two copies per object expand them into eight records. Ordinary record columns admit 343,000 balanced tables, of which 216 preserve the declared copy pairs. Their supported-space probability is about .000630 under that ordinary reference. The matched object law stays on the copy-supported space.

An integer adjacency statistic permits exact expanded-space tails as copy count grows. Three copies per object give a 25% false-rejection fraction under the ordinary reference at its 5% cutoff. The matched object reference rejects 2.78%. Its smallest tail occupies six of the 216 tables, so tied ranks make it conservative. A separate integer dynamic program verifies the ordinary distributions for one through five copies. [Exact copy experiment](../../experiments/2026-10-02-six-hour/null-calibration/copy-tail-counts/README.md).

With unequal multiplicities `[1,1,1,2,2,3]`, fixing three latent ones and five expanded ones leaves six compatible columns. Unrestricted object shuffling preserves the expanded margin in only six of its twenty possible columns. A continuation-count sampler chooses each next sign in proportion to its exact number of legal completions. Every final column has probability `1/6`; three slots give 216 equiprobable tables. Both direct and rejection samplers preserve the constraints in 100,000 draws each. The direct stream's chi-square diagnostic is .01336 at its declared seed; exact branch probabilities and an independent replay remain available beside that uneven sample count. [Weighted conditional space](../../experiments/2026-10-02-six-hour/null-calibration/unequal-copy-counts/README.md).

## 4. Calibration in the full fitting procedure

### 4.1 Independent records, selected unique records and literal copies

The original main study generates 1,000 populations for each of three laws: independent slot draws, those draws conditioned on distinct whole strings, and two identical records per latent object. Each population receives 99 reference draws; copied populations receive both record-column and object-column references. This gives 3,000 observed fits and 396,000 reference fits. All methods repeat the complete nested statistic.

| Population and reference | Rejection at 1% | At 5% | At 10% |
|---|---:|---:|---:|
| Independent records, record columns | 1.1% | 5.0% | 9.9% |
| Unique records, uniqueness-conditioned columns | 1.1% | 5.9% | 10.6% |
| Literal copies, object columns | 1.1% | 5.4% | 10.3% |
| Literal copies, record columns | 4.8% | 15.9% | 27.0% |

At 5%, the marginal Wilson intervals for copied populations are 4.162–6.979% with object references and 13.765–18.296% with record references. Their paired excess is 10.5 percentage points, with a 20,000-draw interval of 8.5–12.6 points. The saved seed schedule links object-reference trial `i` to record-reference trial `i+500` in 500 pairs. Each method's marginal trials have distinct streams; the paired calculation resamples the 500 linked clusters to preserve the covariance between methods. The independent audit reconstructs all 928,424 proposals, all 396,000 accepted graph/fold allocations and every p-value, and repeats 33 complete fits. [Frozen endpoint](../../experiments/2026-10-02-six-hour/null-calibration/main/results.json), [full audit](../../experiments/2026-10-02-six-hour/null-calibration/verification_main.json), [paired seed audit](../../experiments/2026-10-02-six-hour/null-calibration/paired_seed_audit.json).

### 4.2 Imperfect faces

At nominal 1%, 5% and 10% thresholds, the matched face-vector reference rejects 0.5%, 5.0% and 10.4% of the 1,000 simulated populations. The individual-record reference rejects 2.5%, 11.0% and 19.6%. At 5%, the Wilson intervals are 3.813–6.531% and 9.208–13.091%, respectively. The paired difference is 6.0 percentage points, with a 20,000-draw bootstrap interval of 4.3–7.7 points. There are 41 joint rejections, 69 record-only, nine vector-only and 881 joint nonrejections. [Frozen main result](../../experiments/2026-10-02-six-hour/null-calibration/noisy-faces/main/results.json), [full audit and paired calculations](../../experiments/2026-10-02-six-hour/null-calibration/noisy-faces/verification_main.json).

All 99,000 individual-record references change the joint vector margins. The 99,000 matched references preserve them. Recomputed components range from fifteen to twenty in observed tables, nine to twenty in record references, and thirteen to twenty in vector references. Thus both methods account for their proposed tables during fitting, while their proposal laws still differ.

Across 60,000 observed object slots, 48,821 pairs agree. The observation kernel predicts agreement probability `142/175`, and whole-string agreement probability `(142/175)³`. Among 20,000 objects, 10,817 observed strings are equal. The audit also records 11,868 replacements in 120,000 face slots. Those checks locate the simulation's supplied error law; they are not fitted archaeological error rates.

## 5. Fitting feasibility and observed abstention

The original fitting algorithm requires enough groups for nonempty outer folds and inner selection. A twenty-object witness connects consecutive objects through shared complete strings. Transitive physical/text closure makes one component, and the preserved fit raises `ZeroDivisionError`. A within-stratum ordered-vector shuffle creates twenty components and a finite score with the same vector margins. Both tables have positive probability under the declared imperfect-face generator. [Witness, failure and shuffled table](../../experiments/2026-10-02-six-hour/null-calibration/domain-support/main-v2/results.json).

The conditional sampler's table law is well defined in that witness, while the original statistic is only partially defined. A subsequent frozen protocol compares two explicit responses on all 8,000 binary tables. The first assigns zero gain to reference tables with fewer than five components and abstains when the observed table is unusable. The second conditions the reference on the usable subset. Of all tables, 5,760 are usable and 2,240 trigger abstention.

| Nominal cutoff | Extended law over all observations | Extended law among usable observations | Feasibility-conditioned reference among usable observations | Conditioned reference over all observations, including abstention |
|---:|---:|---:|---:|---:|
| 1% | .3250% | .4514% | .4514% | .3250% |
| 5% | 5.0000% | 6.9444% | 4.7917% | 3.4500% |
| 10% | 9.8750% | 13.7153% | 9.9653% | 7.1750% |

At 5%, 400 extended-law rejections occupy 5% of all tables and 6.9444% of usable tables. A feasibility-conditioned reference changes the denominator and rejects 276 of 5,760 usable tables. Independent graph traversal checks all component counts, and score-frequency counting checks all full and conditional tails. The experiment reuses 2,880 frozen unique scores and adds the 2,880 five-component fits. [Guard protocol](../../experiments/2026-10-02-six-hour/null-calibration/domain-support/GUARD_PROTOCOL.md), [exact result](../../experiments/2026-10-02-six-hour/null-calibration/domain-support/guard-exact/results.json), [verification](../../experiments/2026-10-02-six-hour/null-calibration/domain-support/verification.json).

The finite example distinguishes calibration over a declared population from calibration after reporting only usable observations. A future reference implementation needs its score extension, abstention policy or selection law specified before fitting.

A separate constructive bound establishes fitting feasibility for some original main reference laws. If each physical block contains one complete string and blocks have no other physical links, joining equal strings yields one component per distinct string. The number of codes used in any fixed slot bounds that component count below. Singleton-record column references preserve this premise; matched literal-copy references preserve it at the object level. The original independent and unique margins supply a bound of eight components, and copied-object margins supply six to eight. Five positive-weight components suffice for the actual greedy outer and inner allocations to remain nonempty. An audit checks all 3,000 margins, all 396,000 saved reference groupings and 29,169 allocation cases. Record-column references on copies violate the one-string-per-block premise in all 99,000 sampled tables, so the bound applies to their object comparator only. The same premise fails in the imperfect-face domain witness. [Bound protocol](../../experiments/2026-10-02-six-hour/null-calibration/domain-support/SUPPORT_PROTOCOL.md), [completed support audit](../../experiments/2026-10-02-six-hour/null-calibration/domain-support/support-bound/results.json).

## 6. Estimating the supplied observation channel

A bounded follow-up fits the known symmetric kernel to the 1,000 frozen imperfect-face populations. Agreement identifies the shared replacement rate on its positive-association branch. If `H` is observed agreement, the direct estimate is `(7/8)[1−sqrt((8H−1)/7)]`, with the declared endpoint handling. A penalized ordered-pair likelihood jointly estimates the rate and each cell's latent distribution. It uses fixed Dirichlet(1.5) cell penalties, a Beta(1.5,1.5) rate penalty and three starts. A matched shrinkage baseline was added before fitting. [Protocol and comparison amendment](../../experiments/2026-10-02-six-hour/null-calibration/noisy-channel/PROTOCOL.md), [method and results](../../experiments/2026-10-02-six-hour/null-calibration/noisy-channel/README.md).

The true rate is .1. Agreement and joint mean estimates are .099261 and .101605, with mean absolute errors .023162 and .022195. Direct known-rate frequency inversion yields 10,335 negative components across 5,466 of 6,000 ten-object cells. Exact absence probabilities predict 10,331.87 negatives across these 1,000 populations. A constrained joint estimate has mean frequency total variation .245280, compared with .334097 for projected inversion and .227690 for matched shrinkage. Pooling each of the six site/slot cells across the 1,000 populations uses sixty thousand observed pairs in total. Mean cell total variation is then .012236 for joint correction and .020967 for raw marginals. Small-cell estimation and pooled correction therefore have different measured outcomes.

An independent audit reconstructs every pair table, four thousand objectives and traces, six thousand projection checks, eight fits and the 20,000 bootstrap draws. Exact agreement-count and category-set recurrences supply separate sampling checks. Uniform latent frequencies also give an explicit unequal-observer rate ambiguity; nonuniform marginals identify the rate ratio under the declared kernel. [Recovery audit](../../experiments/2026-10-02-six-hour/null-calibration/noisy-channel/main/verification.json), [identification calculation](../../experiments/2026-10-02-six-hour/null-calibration/noisy-channel/IDENTIFICATION.md). A kernel with correlated faces or shared object quality needs its own observation model.

## 7. Application and availability

An archaeological application needs an observation model for which records belong to one artifact, which objects are literal copies, how uncertain faces were encoded, and how catalogue selection or deduplication changed the population. These inputs determine the conditional table law. A new archive with unequal record multiplicities can use the weighted-count calculation once those physical relations are established. A candidate-error model can preserve ordered alternative vectors when its observation premises are stated.

The results here support selecting and testing those premises with explicit counterexamples. The original Indus analyses remain conditional on their selected transcription population. Their predictive gains and p-values have separate evidence files; the present synthetic studies supply measured behavior under known laws and identify changes needed for broader sampling claims.

All finite tables, authored code, method snapshots, generated results, protocols and retrospectives are preserved privately. The [methods and evidence map](methods.md) gives reproduction paths and exact claim files. Raw archaeological corpora and unresolved-rights witnesses remain local under their source manifests. Frozen endpoints preserve failed fits and earlier designs beside their documented refinements.
