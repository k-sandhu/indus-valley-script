# Exact consensus with incorrect physical memberships

Protocol specified before generation or outcome inspection, 2 October 2026. This follow-up uses fresh simulated decimal accounts. It changes the fitting rule from requiring every relation to maximizing the number of exactly satisfied relations.

## Question and prior method

Can a positive positional decoder survive a small number of incorrect memberships, and which wrong or ambiguous decoders remain after that repair? Fischler and Bolles introduced fitting from small subsets and testing the resulting consensus in their 1981 RANSAC paper. Their example also considers all pair combinations for a small dataset. We use exhaustive exact fitting in two free dimensions, retaining every best solution. [Author-institution PDF, printed pages 383-385](https://www.sri.com/wp-content/uploads/2021/12/ransac-publication.pdf), [author preprint on deterministic maximum-consensus fitting](https://arxiv.org/abs/1710.10003v2). This is a numerical control for the physical-observation design. Source assets and their retrieval and rights observations are in [the acquisition manifest](source-acquisition.json); downloaded witnesses remain local.

## Generated accounts and isolated inputs

There will be 300 base seeds, 20261010000 through 20261010299. Each supplies eight training accounts, eight freshly drawn withheld accounts and three separately drawn counted objects. Each account contains three leaf quantities drawn uniformly from integers 0-299. In additive conditions, a parent's quantity is their sum. Units, tens and hundreds features are generated from these quantities. The true values used by the generator are `(1,10,100)`.

The solver receives training mark features, parent-child membership and a counted object's feature vector `[1,0,0]` with value one. This count fixes the unit value. The two other values range over all strictly positive real numbers; the solver receives no base, order restriction, integer restriction, finite value bag, corruption count or condition label. Given integer equations, every unique solution and every retained family has an exact rational representation. Unopened quantities, withheld relations and count targets remain in a separate evaluator key. Generation writes this projection before inference; scoring opens the evaluator only after the inference manifest is saved.

The five conditions share the clean training quantities within each seed:

| Condition | Training observations | Withheld relations |
|---|---|---|
| Complete | All eight memberships correct | Eight fresh complete accounts |
| Two swapped memberships | Swap one child between two randomly chosen parents | Eight fresh complete accounts |
| Four swapped memberships | Choose four distinct parents, pair them, and swap one child within each pair | Eight fresh complete accounts |
| Two incomplete memberships | Remove one child's association in two randomly chosen parents; solver treats the resulting groups as complete | Eight fresh complete accounts |
| Ownership | Assign all eight parent quantities independently, uniformly from 0-897 | Eight fresh ownership accounts with independently assigned parents |

A swap can accidentally preserve a relation. The evaluator records both intended affected accounts and actual violations at the true decoder. Leaves stay distinct by object identity. Three withheld counts use fresh quantities drawn uniformly from 0-897 and do not enter fitting. Ownership features still encode their generated quantities; their assumed additive function is the competing explanation.

## Exact candidate class and ties

With unit value `u=1`, each account becomes a line `a + b t + c h = 0` in the positive `(t,h)` quadrant. A zero row is satisfied everywhere. A nonzero constant row is satisfied nowhere. Coincident lines are grouped for geometry but every original account remains a separate vote.

Enumerate every positive intersection of two nonparallel lines, every line's feasible open positive interval, and the unconstrained positive plane. Intersections supply isolated candidate points. A line family carries the count of rows satisfied throughout that line. The plane carries the number of zero rows. Evaluate support against every original row. Retain all points and continuous families tied for maximum support. A single point is unique only when there is no tied family. Positivity is strict; points on either coordinate axis are excluded. Families receive two different positive witnesses and exact open bounds. Preserve infeasible lines and failed positivity checks in diagnostic records.

This enumeration is complete for exact maximum consensus in two dimensions: any solution satisfying two independent lines occurs at their intersection; solutions satisfying one independent line belong to its positive family; solutions satisfying no nonzero line remain in the positive plane. The finite candidate list does not replace those families.

## Decision rules and comparator

The primary consensus rule accepts a unique best point when its support is at least `ceil(3n/4)` for a prefix of `n` accounts. It abstains on ties or continuous families and rejects a unique point below the threshold. A separately scored half-consensus threshold, `ceil(n/2)`, measures the effect of a more permissive gate. The thresholds are fixed here, without an estimated outlier probability or confidence interpretation.

The all-relations comparator uses the existing exact positive equality decoder with the same count and input equations. It accepts a unique positive vector, retains a positive family or rejects an infeasible system. Evaluate every prefix from one through eight accounts. Continue after any early accepted answer so that later rejection, replacement or ambiguity is preserved.

## Scores and withheld checks

Report final and prefix counts of correct unique vectors, wrong unique vectors, ties/families and rejection for every condition and decision rule. The evaluator tests whether the true vector belongs to the best consensus set, even when fitting abstains. Record first accepted cost in number of relations, any earlier wrong unique vector, and its later state. Prefixes and policies share worlds; the independent units are the 300 seeds within each condition.

For every accepted vector, record all eight withheld relation residuals and three independent count residuals exactly. A false accepted vector's passage or failure is preserved. For the ownership condition, additive residuals test the proposed function; decoder accuracy separately tests its numerical values. Also record the true decoder's support, each accepted decoder's excluded training rows, and exact localization against the actual violation set. No withheld check can change the frozen selection rule or retroactively replace an inferred vector.

Three constructed diagnostics accompany the random worlds: eight zero rows preserve a plane; eight copies of `[-10,-9,1]` preserve a line; and repeated rows from `[-10,1,0]`, `[0,-10,1]`, `[-2,1,0]`, `[-28,0,1]` produce competing positive intersections. They are separately labelled and excluded from recovery rates.

## Independent verification and preservation

Verification enumerates all subsets of the eight relations and uses rational row reduction to determine feasible positive affine sets. For every prefix it derives the maximum feasible subset size and the union's unique/ambiguous status, independently of the arrangement implementation. It checks every saved positive witness and vector against original rows, both threshold decisions, all evaluator residuals, the generator's projection and static absence of evaluator access inside fitting functions. Constructed diagnostics test plane, line and discrete ties. Source assets and endpoint files are hashed separately.

The endpoint is written to a fresh `main-v1/` directory. Protocol, code, generated projections, evaluator keys, inferences, scores, aggregate results, verification and a retrospective are retained. No frozen KHI-01, KHI-02, PHYS-01 or PHYS-02 file is changed. Any implementation repair found after a run will use a new correction note and endpoint. Prose and encoding are reviewed before handoff; protocol snapshots retain this directory's original relative-link context.
