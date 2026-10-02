# Numerical, inverse and constraint research directions

Date: 2 October 2026. Completed work includes an exact audit of a published numerical proposal and a controlled physical-membership experiment. Further designs are labelled below. Read [the registry](../experiments/registry.json) and [methods retrospective](../retrospectives/methods.md) before opening a new dated run.

## Completed conditional audit

Fuls proposes integer multipliers L and S for selected stroke positions and value v for W900. The two equations used here are `v=2S−L` and `vL+1=7S+5`. Eliminating v gives `(2L−7)S=L²+4`. With `d=2L−7`, the identity `4(L²+4)=d(2L+7)+65` proves that positive integer solutions require a positive divisor of 65. Enumeration is complete:

| L | S | v | Assumed expression 7+L |
|---:|---:|---:|---:|
| 4 | 20 | 36 | 11 |
| 6 | 8 | 10 | 13 |
| 10 | 8 | 6 | 17 |
| 36 | 20 | 4 | 43 |

Both assumed L ranges 8..13 and 8..18 select 10/8/6. An L≥10 condition leaves two solutions. All positive solutions already have S≥8 and composite L. The first equation alone permits odd S: L=10,S=9,v=8. Thus the source's inference that integer `(v+L)/2` makes S even is invalid, while even S follows from the joint solution set.

[audit_numerical_equalities.py](../../src/methods/audit_numerical_equalities.py) uses exact fractions, divisor enumeration and an independent finite brute-force check. [The frozen result](../../research/methods/results/numerical_equalities/numerical_equalities_audit.json) records the proof and assumptions. A separate [three-count sensitivity](../../research/methods/results/numerical_equalities/numerical_count_delta_sensitivity.json) changes the proposed first-face tall-stroke count to two/three/four with the other relation held fixed. Those hypothetical coefficient changes produce materially different solution sets.

The proposal assumes equal quantities across faces, selected place multipliers, addition of specified groups and an external bangle-count range. Source photographs corroborate some physical marks and joins. The inspected Vidale chapter does not establish the inscription-specific M1383 count or identity required for that range. The H904/Vats object join has documentary support; its link to the author's historical ICIT3786 remains provisional. Current Lipi ID 3786 refers to another object. [Source premises](../../research/literature/metrology/numerical_source_premises.json) and [the numerical audit](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md) retain these dependencies.

The proposed equations and 10/8/6 values precede this investigation. The completed contribution is their full conditional solution set, the parity check, coefficient sensitivity and source-assumption record. Further arithmetic using the same two equations would reproduce this endpoint.

## Physical membership as an inverse problem

The [completed simulation](../../experiments/2026-10-02-six-hour/physical-information/README.md) supplies six unknown positive quantities and physical parent–child membership. Twelve complete relations identify relative values in all 24 simulated worlds. One separately counted object fixes their scale. When six relations are incomplete and are entered as inequalities, seven worlds retain alternative positive integer values after the count. Exact certificates preserve those alternatives.

A physical membership relation supplies a row of a constraint matrix; a count supplies a scale observation. Preparing separate solver inputs also found a measurement-design defect: identifying an object's badge with its counted quantity changed ownership-control outcomes. The original and corrected endpoints preserve that repair.

The [acquisition branch](../../experiments/2026-10-02-six-hour/physical-acquisition/PROTOCOL.md) extends this design to unrestricted positive values, interval counts and observation cost. Public action descriptors guide its choices while a separate oracle holds their outcomes. The original Louvre Susa objects provide source targets for the relation between contents and exterior marks. Source-linked Indus equalities remain an acquisition task.

## 1. Resolve the observation table before fitting

The first feasible task is a source-linked numerical witness table. Each row should identify a physical object and face, source volume/page/photo, excavation number, coarse stroke counts, height/tier position, candidate glyph classes, proposed quantity relation and its evidential origin. Store observed marks separately from author-assigned arithmetic operations. Preserve alternatives when a mark is unclear.

Priorities are the M1383 object/context join, the historical ICIT3786 figure or old register, and the M331 face segmentation. A source-retrieval result can improve this table even if it leaves the proposed quantity relation unresolved. The completion criterion is a reviewed observation/assumption table with stable source identifiers. A number-only catalogue match is inadequate for joining versions.

Dependencies: original photographs or drawings at sufficient resolution; source tables and registers; the existing [metrology source inventory](../../research/literature/metrology/README.md). This stage should precede numerical optimization because uncertain coefficients and units determine its feasible set.

## 2. Constraint graphs and minimum premise sets

Represent each proposed equality as a constraint node linked to physical witnesses, graphic coefficients and arithmetic assumptions. Label independent observations, source interpretations and analyst-selected restrictions. Use exact integer enumeration or an SMT solver to compute the feasible parameter set for each named premise package. If a package is inconsistent, report a minimum unsatisfiable subset; if it has many solutions, identify which independent additional relation would distinguish them.

The experiment asks which assumptions select 10/8/6 and which are redundant, while extending the current two-equation proof to a larger verified set. Compare declared premise packages and report their full feasible sets. A bounded enumeration can be checked against exact elimination for small cases.

Required new evidence is at least one additional source-grounded relation with independently assigned operation and units. Without it, the current divisor proof already answers the question. Success is a reproducible map of feasible sets and premise dependence. Failure is also informative if proposed readings cannot satisfy the same verified object constraints.

## 3. Held-out quantity prediction

Freeze candidate value systems, place assignments, operations and units on a training group, then predict a quantity independently counted or measured on a separate object group. A recorded total, contents count, capacity with a known unit, or externally identified numerical companion could supply a target. Training and test groups must exclude physical aliases, mould copies, repeated complete formulae and shared reconstruction episodes.

Score absolute error or a declared measurement likelihood, compare candidate systems and simple graphic-count baselines, and retain interval-censored targets. Report every eligible object, including failures and unavailable measurements. Additional symbol groups omitted from an equation need an explicit treatment before prediction.

A successful prediction would connect the conditional system to an external target. A poor prediction or an alternative system with equal performance would limit identification. At present, the project lacks an independently eligible same-module held-out vessel/count anchor. Finding one is the critical dependency.

## 4. Capacity and unit-scale identifiability

The existing capacity example identifies a product of stroke value and unit size. A model such as `Vj=a·Nj(L,S,v)` can admit a compensating change in a and the proposed count scale. Root's [identifiability demonstration](../../src/identifiability_demo.py) preserves this issue. An inverse-volume experiment should explicitly calculate the parameter symmetries, constraint rank and profile likelihood before reporting a fitted base.

Acquire vessel dimensions, reconstruction uncertainty, vessel type, commodity context and measurement units from primary records. Compare a direct per-stroke volume model with declared positional systems. Fit calibration on one group and predict another. Propagate diameter/height uncertainty through the vessel-shape model, and allow commodity-specific units only when source evidence justifies them.

A base becomes identifiable only if an independent observation fixes the relevant scale or relative place relation. The experiment can still estimate the identifiable product when the separate parameters remain ambiguous. Completion requires a table of identified combinations, competing equally fitting parameter sets and held-out prediction errors.

## 5. Gap geometry as additional count evidence

The completed statistical count predictor scored 46.30%, below always-one at 51.07%. A proposed retry adds physical width, surviving ink/traces, edge position, sign spacing and material/layout. Build a source-certified benchmark by masking known spans in measured images, with whole artifact/formula groups held out.

A proposed model would combine `P(survivors|k,L)` from the frozen sign model with a geometry likelihood `P(width,traces|k,layout)` and an explicit observation/count prior. Estimate spacing variation on training objects; treat ligatures and editorial blank marks separately. Compare geometry-only, text-only, combined and constant controls. Freeze crop generation and reference counts before scoring.

Primary dependencies are reliable original images, a countable reference and measured layout. The fresh20 font study already showed how crop drift can dominate scores. Synthetic clean masks test implementation; naturally eroded specimens are a later evaluation population with uncertain references. A useful result must beat the matched design control with coverage and calibration disclosed.

## 6. Constrained latent templates and production alternatives

Independent-slot mixtures left predictive residuals, including on the generated nonphonetic office system. A further experiment can fit a documented production mechanism with explicit dependencies: a small state machine, typed slot grammar, or latent route model. Compare its held-out likelihood with PMB on identical group partitions and alphabets. Select complexity using training data and expose the learned constraints.

This test concerns model adequacy. It becomes informative if a specified small mechanism predicts held-out structure more efficiently, or if its errors expose a stable constraint requiring another relation. Source-defined artifact type, paired face role and production batch can condition the model when their labels were obtained independently of the text. Increasing arbitrary template capacity until it memorizes the corpus would remove the test's interpretability.

## 7. Known-system recovery controls

Before applying a new inverse decoder to Indus data, test it on a documented numerical or administrative sign system whose values are withheld from the fitter. Match text length, inventory granularity, ambiguity, duplicate dependence and missingness as far as feasible. Include a nonphonetic control with known generation rules.

Measure whether the algorithm recovers values up to an identifiable scale or permutation, whether its uncertainty covers the true system, and whether several wrong systems fit equally well. Fix the selection rule before revealing the control dictionary. This gives a measurable recovery target and can reveal failures caused by sparsity or the coding scheme.

A documented khipu control is now complete, with source-derived inputs kept local while their rights remain unresolved. Its published account alignment and generated hidden-value tests are indexed below. Further control corpora should supply comparable source coordinates, an independent dictionary and a clear reuse status.

## Recording decisions

Each proposed experiment needs a dated protocol naming new evidence, target, baselines, family exclusion, parameter symmetries, candidate-space boundaries and stopping rule. Use a fresh output directory and retain all candidate systems that satisfy the stated constraints. A language-model suggestion can propose a model or source query; its suggested arithmetic or meaning enters the table as an analyst hypothesis until independently checked.

The next action with the greatest value is completing the source-linked witness table and identifying a held-out external quantity. Constraint solvers can then narrow a declared hypothesis set. The current exact proof remains the baseline against which that additional evidence should be measured.

## New recovery and observation results

The [physical-observation manuscript](../../papers/003-physical-observations/manuscript.md) combines exact positive constraints, observation-cost policies and a documented khipu representation control. Complete whole-part relations identify ratios, counts fix scale, and valid intervals can leave a bounded scale range. An explicit wrong-scale example passes every withheld conservation relation and fails independently counted objects, showing which observation measures the remaining uncertainty.

The Puruchuco control reproduces sixteen of twenty published account columns with total absolute error sixteen. Ordered flattening with known addresses retains the result; lost correspondence produces much larger errors. A separate decimal simulation recovers remaining positional values in 299 of 300 complete worlds after one counted unit fixes the first value. The unresolved world retains two explicit positive alternatives. Cluster intervals independently select two published partitions under a largest-gap rule and an equal-cord-count rule, both retained in the result. [Control and source audit](../../experiments/2026-10-02-six-hour/khipu-control/README.md), [interval comparison](../../experiments/2026-10-02-six-hour/khipu-control/INTERVALS.md).

[Exact consensus](../../experiments/2026-10-02-six-hour/khipu-control/robust-decoder/REPORT.md) tolerates incorrect memberships in fresh worlds. Its three-quarter gate recovers 281 of 300 two-swap cases and accepts four wrong vectors. The saved wrong-majority example repeats one true relation five times; two corrupted memberships then give a false vector seven votes against six for truth. This motivates collecting a new relation whose coefficients differ, rather than increasing repetitions of the same constraint.

A separate [collective-inventory experiment](../../experiments/2026-10-02-six-hour/khipu-control/conservation-check/REPORT.md) records the whole pool independently of local assignments. With four swaps and a 50% support gate, it increases recovery from 133 to 190 of 200 fresh worlds and reduces accepted errors from nine to one. An erroneous completeness declaration gives fifteen accepted errors. One wrong local decoder passes eight fresh rank-one relations and fails three independent counts. The next validation design can choose measurements by the additional directions they constrain.

[Conditional reference laws](../../papers/002-conditional-reference-laws/manuscript.md) specify related observations, selection and usable fitting populations. The imperfect-face study gives 5% rejection at a nominal 5% under matched face-vector shuffling and 11% under scalar-record shuffling. Exact finite examples retain every conditional probability and the fitting failures that prompted a declared extension.
