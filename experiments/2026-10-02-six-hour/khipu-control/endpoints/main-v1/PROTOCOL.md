# Khipu numerical representation control

Protocol written on October 2, 2026 before this branch computes relation scores. The data pin is Open Khipu Repository commit `4039ca51f4de661d80d0160596309c983a62a9c7`. Acquired bytes and hashes are in [acquisition.json](acquisition.json). Raw assets and record-level derivatives stay under `data/six-hour/khipu/` in the local project.

## Source and prior exposure

The bounded source set is the seven-account Puruchuco hierarchy in the Khipu Field Guide notebook [Replicating Puruchuco](https://khipufieldguide.com/notebook/appendix/notebooks/12%20-%20Replicating%20Purucucho.html), based on Urton and Brezine's published work. Six original accounts are present in the acquired OKR database: UR063, UR064, UR066, UR067, UR068 and UR073. The guide's CM009 reconstruction remains a separate witness. Our source audit will record stable KH identifiers, cord counts, missing-record markers, levels, parent links, positions, colour coverage and numerical-reading fields.

Source review exposed the guide's UR063 values and its UR068 values and totals before this protocol. A subsequent full-page browser read also exposed the twenty UR067 target values and the published totals of 3498 and 3482. This is a replication of a published relation with computational input separation. The analyst has seen the published reference answer. The source-specific partition, alignment and discrepancies are preserved.

The acquisition helper calculates no relation. Structural inspection so far found that pendant `ATTACH_POS` is zero throughout the selected accounts, that recorded `cord_cluster` divisions can differ from the published accounting subunits, and that CM009 has no database record. Source-derived cluster labels will be described as recorded partitions. These fields cannot supply a new measurement of the spacing used by the original authors.

## Actual-source calculation

The primary reference calculation uses UR068 pendants 14–33, 34–53 and 54–73 as three twenty-cord rows, then sums each column to predict UR067 pendants 13–32. These one-based ranges are fixed from the guide's code. The tested predictor receives the three source rows and their representation, with no target quantities. The evaluator keeps target quantities in a separate local answer-key file. Each output records the hashes of its inputs. Evaluator scores must never enter the predictor or select its alignment.

Scores are the number of exactly matched columns, total absolute error, signed total error, and complete-vector equality. Record all twenty residuals locally. Use integer arithmetic. Report results with the denominator twenty and retain every mismatch.

Compare the following representations and controls:

1. Published grouped order: fixed three-by-twenty alignment.
2. Ordered flat stream with the published start, width and row count supplied: reshape the same sixty values. This tests whether the explicit group labels add information once order and dimensions are known.
3. Within-row reversal, all eight combinations. Preserve quantities and group membership.
4. Relative cyclic shifts: fix the first row and enumerate all twenty-by-twenty shifts of the other two rows. Report the entire score distribution and the published alignment's rank. This is a control calculation using the reference evaluator, with no claim of learning a new alignment.
5. Within-row independent shuffling, ten thousand replicates from seed 2026100201. Preserve each row's value multiset.
6. Unordered sixty-value bag, ten thousand equal-size random allocations from seed 2026100202. Preserve the global multiset and number of slots.
7. Sorted-bag allocation, increasing values reshaped into three rows of twenty.

Swapping the three whole rows must preserve the prediction exactly. With an ordered flat stream and known dimensions, the same arithmetic is recoverable; any claimed loss must identify which coordinate or partition information was removed.

The secondary source audit compares the reference readings with integer totals extracted from OKR knot clusters, using only independently documented field semantics. A mismatch stays attached to its source edition and stable cord identifiers. No target value will be repaired to improve a score. If numerical semantics cannot be independently verified, this comparison stops at coverage and records the obstacle.

## Synthetic matched experiment

Generate three hundred independent worlds with seeds 2026100300 through 2026100599. Each world has eight accounts. Every account has three leaf quantities drawn uniformly from integers 0 through 299; its parent stores their sum, at most 897. Encode each quantity as the three digits in base ten, attached to three physical positions. The tested decoder sees these feature counts, parent–child memberships and one independently counted one-unit object's feature vector. Numerical weights, quantity readings and the source world's answer key are withheld from it.

The decoder assumes positive additive values for the three positions and uses exact rational arithmetic. A parent–child relation contributes `(parent features − sum(child features)) · weights = 0`. The counted object fixes its own feature vector's value at one. Do not supply a bag of known weights. Classify each endpoint as one positive solution, several positive solutions, or no positive solution. For ambiguous cases, save two distinct exact positive witnesses. The evaluator records correct unique answers and false unique answers separately. Save ranks before and after the anchor, all equations and exact solution certificates.

Run matched representations on each world: full physical position and membership; randomly permuted sibling order; position retained with all membership removed; membership retained with the three positions collapsed to a single knot-count feature; and scrambled parent–child membership across accounts. Scrambling preserves the feature multiset and the number of children per parent. Seeds for controls are derived separately from the world seed and written in the record. A sibling permutation is an invariance check.

Also run two negative conditions. In incomplete accounts, remove one randomly selected child's membership from four of the eight accounts while retaining the original parent. In ownership accounts, parent quantities are independent draws from 0 through 897 and are unrelated to the children. Use the same representations and record rejection, ambiguity and false unique answers. These conditions test whether the proposed numerical relation itself supplies misleading constraints.

This decimal accounting system is a simulation inspired by the documented numerical positional structure of khipus. It measures what the representation contributes under specified assumptions. Its generated worlds, exact arithmetic and grouping controls remain separate from the Puruchuco source calculation.

## Checks and frozen endpoints

Before scoring, verify that the predictor cannot read the evaluator key, that the source partition matches the fixed ranges, and that the source-derived and synthetic directories are separate. After scoring, independently recompute every sum and exact certificate with a second arithmetic implementation. Verify all row permutations and synthetic sibling permutations. Record failed acquisition routes, source exposure, parsing problems, code repairs and unsuccessful controls in the retrospective.

Freeze this protocol's bytes, the source and code hashes, input manifests, inferred outputs, evaluator scores, aggregate results and verification reports in a fresh endpoint directory. Further methods need a new protocol and fresh endpoint. A frozen protocol snapshot keeps relative links in the original protocol directory's context.
