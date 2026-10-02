# Methods and assumptions

This branch has a published-source replication and a generated known-system experiment. The source calculation uses the Khipu Field Guide's existing Puruchuco partition and alignment. Source review displayed all values used in that calculation, including the reference targets, before protocol freeze. The tested predictor receives source rows only; a separate evaluator receives the target key. The analyst's prior exposure is recorded in the [protocol](PROTOCOL.md). CM009 is an author reconstruction from Mackey's thesis and is kept separate from the six original OKR records. Source-derived detailed vectors remain local. The simulation uses generated decimal accounts and supplies no archaeological readings.

## Published alignment

The reference predictor sums three twenty-cord rows: UR068 pendants 14-33, 34-53 and 54-73. Its target is UR067 pendants 13-32. The ranges are one-based and fixed from the guide. The scorer counts exact columns, sums absolute residuals, sums signed residuals and checks complete-vector equality. Every operation uses integers. The predictor function has no file reads or target argument.

The comparison separates three changes to the representation. An ordered flat list retains the same coordinates when its start and twenty-column width are supplied. Reversing or shifting rows changes coordinate correspondences while retaining their value multisets. A shuffled bag also removes the original row allocation. Whole-row permutations preserve the sums because addition is commutative.

The control set contains all eight row-reversal combinations, all 400 relative cyclic shifts after fixing the first row, 10,000 independent within-row shuffles, 10,000 equal-size allocations of the full sixty-value bag and a sorted-bag allocation. Seeds are fixed in the protocol. The entire score distributions are retained; the published alignment is evaluated without fitting or repairing it.

An independent parser checks the source extraction against the acquired HTML. Independent scalar loops reconstruct each recorded permutation and sum. They verify all scores and the equality between grouped order and ordered flattening. [Verification](source-verification.json) records the hashes and 20,411 checked predictions.

## Hidden positional values

The generator draws three leaf quantities per account from integers 0-299. Their parent stores the sum, at most 897. Each quantity is represented by three digit counts at three positions. The decoder sees the counts, physical memberships and the features of an independently counted one-unit object. Its three positive values are unknown; the generator's true values are 1, 10 and 100.

For each account, the difference between the parent's features and the summed children's features supplies a homogeneous linear equation. The counted object supplies an absolute equation. Exact row reduction gives the ranks and the affine solution family. Strict positivity distinguishes a unique positive point, an open family of positive points and an empty set. An ambiguous endpoint retains two different rational witnesses, which also certify a continuous family between them.

The main run uses 300 seeds, three conditions and five representations. Complete accounts conserve quantities. Incomplete accounts lose one child's membership in four of eight accounts. Ownership accounts assign parent quantities independently. The representations retain the complete features and memberships, rearrange siblings, remove membership, collapse positional counts to one feature, or scramble child membership across parents. Child counts are preserved when scrambling.

Each world is scored after every prefix of one through eight account relations, under the [prefix supplement](PROTOCOL_PREFIX.md). The evaluator checks a unique decoder against all 32 generated cord quantities after inference. It records false unique answers separately and follows whether later relations reject them. Recovery of the numerical decoder and validity of the accounting interpretation are distinct recorded properties.

Verification uses exact Gram determinants to recompute ranks, checks the row space of every saved reduced system, tests each positive witness in the original equations and checks each negative certificate. An independently seeded sample of 512 states is also checked with linear programming. [The verification record](endpoints/main-v1/verification.json) covers all 36,000 states, 24,154 positive witnesses and 7,200 sibling-permutation pairs. Static input inspection covers the tested functions; the process runs in the ordinary local workspace.

## Use for Indus research

The transferable observation is the information required by a numerical hypothesis. A whole-part relation becomes useful when both the relevant marks and physical membership survive. Repeated versions of one relation can leave the numerical scale ratios unresolved. A later independent relation can reject a value assignment that was unique under an incomplete set of observations. These requirements can guide a bounded Indus acquisition plan once suitable object groups and independent measurements are identified.
