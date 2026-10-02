# Methods for the validation allocation comparison

This analysis reuses KHI-04's frozen generated worlds, final candidate sets and held-out observations. The analyst had seen its aggregate outcomes and two exact failures before the [new protocol](PROTOCOL.md) was frozen. The comparison is a post-outcome refinement. Its observations come from the source files pinned in [source-pins.json](main-v1/source-pins.json). The 1,400 worlds share 200 base seeds across seven conditions.

## Observations, premises and cost

Each world offers eight held-out account coefficient rows and three independently measured count-feature rows. An account equation has right side zero under a complete-membership, same-quantity additive model. Ownership-control parents were independently valued; their account rows test this proposed function. Count measurements supply absolute right sides. All observations are exact in this experiment. A counted view already has the correct unit-object count from KHI-04, fixing its first positional value. An unmeasured view receives no initial scale observation.

Every possible check's coefficient row and type are available before selection. Targets and inferred decoder sets are withheld from selection. Checking an account relation or measuring a count each spends one abstract unit. The study holds the number of checks equal across policies at budgets zero through three. Archaeological acquisition effort, count uncertainty and missing validation memberships are absent. A prospective physical study needs those costs and observation errors specified separately.

The projection builder reads the sealed source key to extract held-out coefficient rows. It writes [selector-inputs.jsonl](main-v1/selector-inputs.jsonl) containing only check IDs, types, rows and available anchor rows. The separate [targets.jsonl](main-v1/targets.jsonl) contains measured right sides and true vectors for scoring. World IDs remain outer bookkeeping; the selector receives no world ID, condition, truth, target or decoder prediction. The anchor's coefficient row is `[1,0,0]`, and its value remains outside selection.

## Selection rules

Account-first uses the first account rows in their original order. Count-first uses count rows first. Greedy rank repeatedly chooses the row with the largest increase in exact coefficient rank, including the available anchor coefficient row. Ties use account order followed by count order. Rank is computed with exact minors. When no remaining row raises rank, the rule still uses the declared tie order to spend its budget.

Uniform random draws an unordered subset of the same budget size from the eleven checks. The implementation enumerates all subsets: 1, 11, 55 and 165 at budgets zero, one, two and three. Per-world outcomes are averaged with those exact denominators. No random seed or sampled subset can affect this comparison.

[selection-manifest.json](main-v1/selection-manifest.json) seals the 11,200 deterministic selection records before evaluation opens either targets or candidate decoder sets. The selector's function arguments are `checks`, `anchor_rows`, `budget` and `policy`; static inspection checks its separation from targets and decoder files. This is code-level isolation.

## Validation of points, rays and families

The evaluation uses prefix-eight optimum sets from the frozen local and collective fitters and retains their 75% and 50% support gates. A rejected training result remains rejected. A gate-passing set is intersected with selected validation equations, preserving all its original tied points and families. The original collective equality or halfspace remains binding in the collective model.

A normalized point `(1,t,h)` represents an arbitrary positive ray without scale, or a fixed absolute point with the counted unit anchor. Its linear constraints are `v -t*u = 0` and `w -h*u = 0`, where `(u,v,w)` are absolute positional values. A normalized line family gives a homogeneous plane. The implementation intersects these restrictions and the selected equations by exact rational row reduction, then enforces strict positivity and any original collective halfspace. An independent inequality-elimination calculation checks the deterministic families.

Every surviving part receives an empty/point/family status, affine dimension, base, directions and positive witness where applicable. Duplicate absolute points are merged. A tied set with a continuous part remains ambiguous in absolute values. Relative identification is recorded separately when every surviving part belongs to the same positive ray. Homogeneous checks preserve scale freedom even after they distinguish ratios. Count checks can fix scale or exclude a ray whose measurements demand inconsistent scales.

The principal detection outcome concerns originally wrong unique rays: either validation excludes the ray or it remains compatible. Correct original rays are checked for preservation. The analysis also records validated correct or wrong absolute points and surviving ambiguity after filtering original tied sets. These outputs use the true vector only during scoring. The original support objective and selected training candidates are unchanged.

## Independent arithmetic checks

The main verifier reconstructs the source projection, checks every deterministic selection and greedy choice using a separate permutation/minor rank calculation, and recomputes selected residuals directly. It independently classifies every deterministic ambiguous-set part using its own rational reduction and inequality elimination, checking bases, directions and positive witnesses. All aggregate rows are rebuilt from the saved per-world records.

Uniform-random ray checks also have an independent combinatorial calculation. For a known absolute vector, the number of passing subsets of size `k` is `choose(g,k)`, where `g` checks have zero residual. For an unmeasured ray, checks that impose no scale form a common group; nonzero count predictions form groups by the positive scale they require. Passing subsets contain universal checks and at most one compatible scale group. Summing these groups yields exact expected survival and scale-identification counts without replaying the evaluator's subset filter.

The [additional review](additional-review/verification.json) independently classifies random subsets for gate-passing ambiguous optimum sets. It extends the original review's coverage while preserving its narrower verification record. Compatible wrong rays from random subsets are retained with selected IDs, normalized values and any fixed absolute point. Constructed diagnostics check scale-free rays, count-fixed scale, a family cut to a point, inconsistent strict positivity and a halfspace boundary. No numerical repair was needed during this branch.

## Reuse and preservation

Reusable files are [projection and selection](../../../../src/six_hour/khipu_validation.py), [exact intersection geometry](../../../../src/six_hour/khipu_validation_geometry.py), [evaluation](../../../../src/six_hour/khipu_validation_evaluate.py), [main verification](../../../../src/six_hour/khipu_validation_verify.py) and [additional family review](../../../../src/six_hour/khipu_validation_family_review.py). Python 3.13.5 and the standard library produced these records. A new study requires new dated output constants and a prospective policy protocol. Writers refuse to replace existing files. The code, source pins, projections, selections, scores and both reviews are preserved with their hashes. Frozen protocol snapshots retain the original protocol directory's relative-link context.
