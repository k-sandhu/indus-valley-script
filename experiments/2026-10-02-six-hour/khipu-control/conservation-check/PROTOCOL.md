# A collective conservation check under uncertain membership

Protocol specified before generation or outcome inspection, 2 October 2026. This is a fresh synthetic follow-up to the frozen [consensus experiment](../robust-decoder/REPORT.md). It adds an independently observed collective relation and keeps the original consensus decision rules for comparison.

## Physical observation and question

An observer links eight labelled parent records to one pooled inventory of their child objects. This observation supplies inclusion and completeness at the whole-collection level, separately from the individual parent-child assignments. The additive hypothesis requires the same commodity and units, a single accounting event, no loss or exchange during pooling, and parent records representing their contents' quantities. The pool is complete when every constituent object is present. If its missingness is declared, positive missing quantities give an inequality instead.

For the complete pool, the sum of the eight parent values equals the sum of all pooled child values. Swapping child associations preserves the pooled multiset and this relation. Its coefficient row is also the sum of local rows when those rows contain the same complete pool. The additional information is the separately observed validity of the collective relation during local reassignment. It adds no row rank to a correctly specified complete local system. A missing pool changes the observation and its completeness premise.

The numerical question is whether enforcing that collective relation changes the exact best consensus set and its errors. A checking relation draws on the wider idea of redundancy for detecting errors, described in [Hamming's 1950 article, printed pages 148-150](https://zoo.cs.yale.edu/classes/cs323/doc/Hamming.pdf). Here quantities and continuous positive values replace binary messages. The experiment supplies a physical operation model rather than an archaeological claim about ancient error-correcting codes. Method sources, their versions and rights observations are in [the acquisition record](source-acquisition.json).

## Fresh worlds and separate scale

Generate 200 base seeds, 20261020000 through 20261020199. Each seed supplies eight training accounts with three leaf quantities drawn uniformly from integers 0-299, eight freshly drawn withheld accounts and three freshly drawn counted objects. Each record has units, tens and hundreds features. Additive parents sum their leaves; ownership parents have independent quantities drawn uniformly from 0-897.

A seed-specific positive scale is drawn uniformly from integers 1-7 and multiplies every generated physical quantity. The true values are `(s,10s,100s)`. Fitting receives no bag of possible scales. One observation condition supplies a count on feature vector `[1,0,0]`; its measured value is `s`. The other condition supplies no count. Homogeneous fitting normalizes the first value to one as a mathematical gauge. A unique normalized vector identifies a relative ray. The supplied count fixes that ray's scale in the counted condition. Unmeasured runs retain arbitrary positive scale even when their ratios are correct.

Projected component inputs contain mark features, local memberships, the independently recorded parent/pool inventories, the completeness descriptor and the scale observation available to that condition. They contain no numerical answer key or corruption labels. Keys and held-out targets remain in separate files. Fitting receives only local coefficient rows, the collective coefficient row and its equality/inequality kind. Evaluation opens the keys after inference and its hashes are saved.

## Observation conditions

| Condition | Local membership | Observed collective inventory and supplied constraint |
|---|---|---|
| Complete | Eight complete groups | All 24 children present; equality |
| Two swapped | Swap one child between two randomly selected parents | Same 24-child pool; equality |
| Four swapped | Two disjoint parent pairs each swap one child | Same 24-child pool; equality |
| Local missing, complete pool | Remove one association in two accounts; children remain identifiable in the global pool | Full independently observed pool; equality |
| Missing pool, declared | Remove those two objects from local groups and the observed pool | Partial pool; inequality `parents >= observed children` |
| Missing pool, misdeclared | Same actual partial pool | Erroneous supplied completeness; equality |
| Ownership | Parent quantities assigned independently | Complete pool with a proposed additive interpretation; equality |

Within a seed, conditions reuse their clean quantities, withheld objects and scale. Swaps preserve distinct object identities and can exchange equal quantities. Missing objects can have zero quantity. Record both intended operations and actual violations, including any accidental agreement. The solver treats visible local groups as complete in the consensus objective; the collective descriptor supplies the specified completeness information.

## Exact fitting and fixed decisions

The baseline uses the frozen KHI-03 positive maximum-consensus implementation. It ignores the collective observation. The new fitter maximizes the same local support subject to the collective equality or inequality. It searches the entire strictly positive domain of the two normalized remaining values, with no base, monotonicity or integer prior.

For an equality, enumerate intersections of local lines with each other and the collective line; retain only points satisfying the collective equation. Feasible line families coincide with the collective line unless the collective row is zero. For an inequality, retain admissible local intersections and clip each positive line family by the closed collective halfspace. The remaining positive plane is included whenever feasible. Strict positivity remains open; equality at the inequality bound is allowed. Record open/closed bounds and exact positive witnesses. Preserve every point and family tied for best local support. A unique answer consists of one point and no tied family. An empty collective domain is rejected separately.

Compare both baseline and collective fitting under the same two frozen gates: at least `ceil(3n/4)` and at least `ceil(n/2)` supporting local accounts for prefix `n`. The collective observation is a hard supplied constraint and contributes no vote. All four policies continue through prefixes one to eight, recording early wrong solutions, later replacement, ambiguity and rejection. No threshold changes after outcomes.

## Evaluation and withheld checks

For each condition and gate, report final correct relative rays, wrong unique rays, tied/family sets and rejection. Report counted-condition correct and wrong absolute vectors separately. No unmeasured run is an absolute identification. Check whether the true normalized vector remains in each best set. Count independent units by seeds; conditions, scales, policies and prefixes share worlds.

Every accepted normalized vector receives exact residuals on eight fresh held-out relations. In the counted condition, multiply it by the observed scale and check all three held-out counts. In the unmeasured condition, test whether one positive scale can satisfy all three counts and retain the scale witness or incompatibility. This evaluator-only consistency check leaves the inferred ray unchanged. Ownership held-out parents are also independent; their relation residuals test the proposed additive function. Numerical correctness and function compatibility remain separate fields.

Record the collective observation's residual at the true decoder, the measured pool's omitted objects, raw best-support counts, all optimal families, and cases where a wrong supplied aggregate forces rejection or a false point. A complete pool and a partial pool have separate source witnesses in the synthetic operation log. Reconstruct aggregate coefficients directly from inventory features during verification; do not replace them with presumed correct local equations.

## Verification and preservation

Independently enumerate every subset of the eight local relations. For each prefix, rational row reduction and a separately evaluated collective constraint determine feasibility, positivity, maximum local support and the union's point/family status. The inequality check clips the affine family with exact closed bounds. Verify every saved witness, threshold, true-vector retention flag, held-out residual and scale claim. Reconstruct all projected memberships and pool lists from their recorded operations. Check the coefficient sum invariance for complete swapped pools and its change under missing pools. Inspect fitting functions for key or file access.

Constructed diagnostics cover a nonzero equality restricting a plane to a line, a line intersected at one positive point, an inequality retaining its closed boundary, a completely infeasible collective observation, and unrestricted scale without a count. Keep those cases outside recovery percentages. Source witnesses stay local; generated observations and exact checks are project work.

Write one fresh `main-v1/` endpoint with frozen protocol, source manifest, code, projections, evaluator key, inferences, scores, independent reviews and retrospective. Preserve KHI-03 and all earlier endpoints. Any necessary post-run repair receives a distinct note and endpoint. Complete prose and UTF-8 review before handoff. Frozen protocol snapshots retain this directory's original relative-link context.
