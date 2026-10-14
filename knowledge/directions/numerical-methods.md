# Numerical, inverse and constraint research directions

Date: 2 October 2026. Completed work includes an exact audit of a published numerical proposal and a controlled physical-membership experiment. Further designs are labelled below. Read [the registry](../experiments/registry.json) and [methods retrospective](../retrospectives/methods.md) before starting a new dated run.

## Completed conditional audit

Fuls proposes integer multipliers L and S for selected long-stroke and short-stroke positions, and a value v for sign W900. The two equations used here are `v=2S−L` and `vL+1=7S+5`. Eliminating v gives `(2L−7)S=L²+4`. With `d=2L−7`, the identity `4(L²+4)=d(2L+7)+65` proves that positive integer solutions require d to be a positive divisor of 65. The enumeration is therefore complete:

| L | S | v | Assumed M1383 expression 7+L |
|---:|---:|---:|---:|
| 4 | 20 | 36 | 11 |
| 6 | 8 | 10 | 13 |
| 10 | 8 | 6 | 17 |
| 36 | 20 | 4 | 43 |

Both ranges assumed for L, 8 to 13 and 8 to 18, select L=10, S=8, v=6, the 10/8/6 solution. Requiring L≥10 instead leaves two solutions. All positive solutions already have S≥8 and composite L. The first equation alone permits odd S, for example L=10,S=9,v=8. The source infers that S is even because `(v+L)/2` is an integer; that inference is invalid, although S is even in every joint solution of the two equations.

[audit_numerical_equalities.py](../../src/methods/audit_numerical_equalities.py) uses exact fractions, divisor enumeration and an independent finite brute-force check. [The frozen result](../../research/methods/results/numerical_equalities/numerical_equalities_audit.json) records the proof and assumptions. A separate [three-count sensitivity](../../research/methods/results/numerical_equalities/numerical_count_delta_sensitivity.json) changes the proposed count of tall strokes on the first face to two, three or four while holding the other relation fixed. These hypothetical changes in a coefficient produce materially different solution sets.

The proposal assumes equal quantities across faces, multipliers for selected places, the addition of specified groups and a range for a bangle count taken from outside the inscription. Source photographs corroborate some physical marks and joins. The Vidale chapter we inspected does not establish the count for M1383 or the identity of the object, both of which that range requires. The join between H904 and Vats's published object has documentary support; its link to the inscription Fuls numbered 3786 in the older ICIT database (ICIT3786) remains provisional. In the current Lipi export, ID 3786 refers to another object. [Source premises](../../research/literature/metrology/numerical_source_premises.json) and [the numerical audit](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md) keep these dependencies.

The equations and the 10/8/6 values predate this investigation. What we add is their full conditional solution set, the parity check, the sensitivity to the stroke coefficients and a record of the source assumptions. Further arithmetic on the same two equations would reproduce this result.

## Physical membership as an inverse problem

The [completed simulation](../../experiments/2026-10-02-six-hour/physical-information/README.md) hides six positive quantities and supplies physical parent–child membership, meaning which objects contain which other objects. Twelve complete relations identify the relative values in all 24 simulated worlds (generated collections). One separately counted object fixes their scale. When six relations are incomplete and are entered as inequalities, seven worlds still allow alternative positive integer values after the count. Exact certificates preserve those alternatives.

A membership relation supplies one row of a constraint matrix, and a count supplies an observation of scale. Preparing separate inputs for the solver also exposed a defect in the measurement design: the first run took the counted quantity in the ownership control from the value of an object's badge code instead of from the object itself, which changed that control's outcomes. The original and corrected results are both kept.

The [acquisition branch](../../experiments/2026-10-02-six-hour/physical-acquisition/PROTOCOL.md) extends this design to unrestricted positive values, counts known only within an interval, and the cost of each observation. Public descriptions of the available actions guide its choices while a separate oracle holds their outcomes. The original Susa objects in the Louvre provide real targets for the relation between contents and exterior marks. Comparable equalities for Indus objects, linked to their sources, have still to be acquired.

## 1. Resolve the observation table before fitting

The first feasible task is a table of numerical witnesses: each row records one source observation of a numerical-looking mark. A row should identify the physical object and face; the source volume, page and photograph; the excavation number; coarse stroke counts; the height and tier position of the strokes; candidate glyph classes; the proposed quantity relation; and where that relation comes from. Store observed marks separately from arithmetic operations assigned by an author. Keep alternatives when a mark is unclear.

The priorities are joining M1383 to its object and context, finding the figure or old register for the historical ICIT3786, and settling the segmentation of M331's faces. Retrieving a source can improve this table even if the proposed quantity relation stays unresolved. The task is complete when a reviewed table of observations and assumptions carries stable source identifiers. A catalogue match on number alone is not enough to join versions of a record.

The table depends on original photographs or drawings at sufficient resolution, source tables and registers, and the existing [metrology source inventory](../../research/literature/metrology/README.md). It should come before numerical optimization, because uncertain coefficients and units determine which solutions are feasible.

## 2. Constraint graphs and minimum premise sets

Represent each proposed equality as a constraint node linked to the physical witnesses that support it, the values assigned to graphics and the arithmetic assumptions. Label independent observations, source interpretations and restrictions chosen by the analyst. Use exact integer enumeration or an SMT solver (a program that decides whether logical and arithmetic constraints can be met) to compute the feasible parameter set for each named package of premises. If a package is inconsistent, report a minimum unsatisfiable subset, the smallest group of premises that already contradict each other; if it has many solutions, identify which additional independent relation would distinguish them.

The experiment asks which assumptions select 10/8/6 and which are redundant, and extends the current two-equation proof to a larger verified set. Compare declared premise packages and report their full feasible sets. For small cases, a bounded enumeration can be checked against exact elimination.

This needs at least one additional relation grounded in a source, with its operation and units assigned independently. Without it, the current divisor proof already answers the question. Success is a reproducible map of feasible sets and their dependence on premises. Failure is also informative if the proposed readings cannot satisfy the same verified object constraints.

## 3. Held-out quantity prediction

Freeze candidate value systems, place assignments, operations and units on a training group, then predict a quantity counted or measured independently on a separate group of objects. A recorded total, a count of contents, a capacity with a known unit, or an externally identified numerical companion could supply a target. Training and test groups must not share physical aliases (one object under several catalogue numbers), mould copies, repeated complete formulae or a common reconstruction.

Score absolute error or a declared measurement likelihood, compare candidate systems with simple graphic-count baselines, and keep targets known only within an interval. Report every eligible object, including failures and unavailable measurements. Symbol groups left out of an equation need an explicit treatment before prediction.

A successful prediction would connect the conditional system to an external target. A poor prediction, or an alternative system that performs equally well, would limit identification. At present we lack an independently eligible vessel or count anchor from the same module that could be held out. Finding one is the critical dependency.

## 4. Capacity and unit-scale identifiability

The existing capacity example identifies only the product of a stroke value and the unit size. In a model such as `Vj=a·Nj(L,S,v)`, where a is the unit size, a change in a can be offset by a change in the proposed count scale. The first investigation's [identifiability demonstration](../../src/identifiability_demo.py) preserves this issue. An experiment that infers values from volumes should calculate the parameter symmetries, the rank of the constraints and the profile likelihood explicitly before reporting a fitted base.

Acquire vessel dimensions, reconstruction uncertainty, vessel type, commodity context and measurement units from primary records. Compare a model that assigns a direct volume to each stroke with declared positional systems. Fit the calibration on one group and predict another. Propagate uncertainty in diameter and height through the model of vessel shape, and allow units specific to a commodity only when source evidence justifies them.

A base becomes identifiable only if an independent observation fixes the relevant scale or the relation between places. The experiment can still estimate the identifiable product when the separate parameters remain ambiguous. Completion requires a table of identified combinations, competing parameter sets that fit equally well, and held-out prediction errors.

## 5. Gap geometry as additional count evidence

Our completed statistical estimate of how many signs a gap has lost was right 46.30% of the time, below the 51.07% scored by always guessing one. A proposed retry adds the physical width of the gap, surviving ink or traces, position relative to the edge, sign spacing, and material and layout. Build a benchmark certified against sources by masking known spans in measured images, holding out whole groups of related artifacts or formulae.

A proposed model would combine `P(survivors|k,L)` from the frozen sign model, where k is the number of lost signs and L the full length, with a geometry likelihood `P(width,traces|k,layout)` and an explicit prior on observations and counts. Estimate the variation in spacing on training objects, and treat ligatures and editorial blank marks separately. Compare geometry alone, text alone, both combined and constant controls. Freeze how crops are generated and the reference counts before scoring.

The main dependencies are reliable original images, a reference that can be counted and a measured layout. Our frozen test of reading printed rows from images (the fresh20 font study) already showed how crops that drift off their targets can dominate scores. Clean artificial masks test the implementation; naturally eroded specimens, whose true contents are uncertain, are a later evaluation population. A useful result must beat always guessing one under the same gap-sampling design, with coverage and calibration disclosed.

## 6. Constrained latent templates and production alternatives

Mixtures of templates with independent slots left structure they could not predict, including in the generated office-routing system, which encodes no speech. A further experiment can fit a documented production mechanism with explicit dependencies: a small state machine, a grammar of typed slots, or a model of latent routes. Compare its held-out likelihood with that of PMB, our model that adds the preceding sign to length, position, site and object type, on identical group partitions and alphabets. Select complexity on training data and report the constraints the model learns.

This test concerns whether a model is adequate. It becomes informative if a specified small mechanism predicts held-out structure more efficiently, or if its errors expose a stable constraint that needs another relation. Artifact type defined by a source, the role of a paired face and the production batch can condition the model when those labels were obtained independently of the text. Increasing arbitrary template capacity until the model memorizes the corpus would make the test uninterpretable.

## 7. Known-system recovery controls

Before applying a new inverse decoder to Indus data, test it on a documented numerical or administrative sign system whose values are withheld from the fitting procedure. Match text length, how finely the inventory is divided, ambiguity, dependence between duplicates and missing data as far as feasible. Include a nonphonetic control with known generation rules.

Measure whether the algorithm recovers values up to an identifiable scale or permutation, whether its uncertainty covers the true system, and whether several wrong systems fit equally well. Fix the selection rule before revealing the control's dictionary. This gives a measurable recovery target and can reveal failures caused by sparse data or by the coding scheme.

A documented khipu control is now complete, with inputs derived from sources kept local while their rights remain unresolved. Its alignment of published accounts and its tests on generated hidden values are listed below. Further control corpora should supply comparable source coordinates, an independent dictionary and a clear reuse status.

## Recording decisions

Each proposed experiment needs a dated protocol naming the new evidence, the target, the baselines, how related objects are kept out of the test group, the parameter symmetries, the boundaries of the candidate space and the stopping rule. Use a fresh output directory and keep every candidate system that satisfies the stated constraints. A language model can suggest a model or a source query; any arithmetic or meaning it suggests enters the table as an analyst's hypothesis until checked independently.

The most valuable next step is completing the source-linked witness table and identifying an external quantity that can be held out. Constraint solvers can then narrow a declared set of hypotheses. The current exact proof remains the baseline against which that additional evidence should be measured.

## New recovery and observation results

The [physical-observation manuscript](../../papers/003-physical-observations/manuscript.md) combines exact positive constraints, policies for the cost of observation and a documented control on how khipu are represented. Complete relations between wholes and parts identify ratios, counts fix scale, and valid intervals can leave a bounded range of scales. An explicit example with the wrong scale passes every withheld conservation relation (a whole equals the sum of its parts) and fails on independently counted objects, which shows which observation measures the remaining uncertainty.

The Puruchuco khipu control reproduces sixteen of twenty published account columns with total absolute error sixteen. An ordered flat list with known positions keeps this result; losing the correspondence between positions produces much larger errors. A separate decimal simulation recovers the remaining positional values in 299 of 300 complete worlds after one counted unit fixes the first value. The unresolved world keeps two explicit positive alternatives. Without the quantities, the gaps between cord clusters select the two published partitions under a largest-gap rule and under an equal-cord-count rule, both kept in the result. [Control and source audit](../../experiments/2026-10-02-six-hour/khipu-control/README.md), [interval comparison](../../experiments/2026-10-02-six-hour/khipu-control/INTERVALS.md).

[Exact consensus](../../experiments/2026-10-02-six-hour/khipu-control/robust-decoder/REPORT.md), which keeps the answer supported by the most accounts, tolerates incorrect memberships in fresh worlds. With a gate that accepts a unique answer only when at least three quarters of the accounts support it, it recovers 281 of 300 cases with two swapped memberships and accepts four wrong value vectors. In the saved example where the majority is wrong, one true relation is repeated five times, and two corrupted memberships then give a false vector seven votes against six for the truth. This is why we would collect a new relation with different coefficients instead of more repetitions of the same constraint.

A separate [collective-inventory experiment](../../experiments/2026-10-02-six-hour/khipu-control/conservation-check/REPORT.md) records the whole pool independently of the local assignments. With four swaps and a gate requiring 50% support, it raises recovery from 133 to 190 of 200 fresh worlds and reduces accepted errors from nine to one. A false declaration that the inventory is complete gives fifteen accepted errors. One wrong local decoder passes eight fresh relations that together have rank one, adding only one independent constraint, and fails three independent counts.

The completed [validation-design comparison](../../experiments/2026-10-02-six-hour/khipu-control/validation-design/REPORT.md) tests which withheld checks remove those errors. A wrong decoder gets the ratios between values wrong, so all its rescalings form a wrong ray. With the scale fixed, one count rejects all nine accepted wrong local decoders, while choosing checks by coefficient rank needs two. With the scale free, checking counts first needs two and rank-first needs three. The first count without a scale anchor can choose an absolute point on a wrong ray, leaving the ratio error for the next count to test. These controls favour recording how a measurement cuts the feasible set of solutions, alongside its coefficient rank.

[Conditional reference laws](../../papers/002-conditional-reference-laws/manuscript.md) specify how chance comparisons built by shuffling should treat related observations, the selection of records and the populations in which a model can be fitted. In the study of objects with two imperfectly recorded faces, shuffling the paired face readings together gives 5% rejection at a nominal 5%, and shuffling individual records gives 11%. Exact finite examples keep every conditional probability and the fitting failures that prompted a declared extension.

Recording quality shared across the slots of an object adds a second measurement mechanism. On 300 fresh populations, the original nested prediction score rejects 4% under broad shuffling of whole reading vectors and 3% under shuffling conditioned on quality. A score of observed agreement between adjacent slots, specified afterward and tested on 1,000 fresh populations, gives 94.2% versus 1.0%. Exact table weights and independently computed integer tails locate the fault in the broad shuffle; the paired outcomes show how much a calibration check depends on the statistic chosen. [Quality comparison](../../experiments/2026-10-02-six-hour/null-calibration/shared-quality/README.md), [agreement diagnostic](../../experiments/2026-10-02-six-hour/null-calibration/shared-quality/agreement-diagnostic/README.md).
