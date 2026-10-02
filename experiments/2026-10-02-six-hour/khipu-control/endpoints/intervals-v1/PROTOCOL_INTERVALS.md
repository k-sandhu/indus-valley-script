# Recorded interval grouping

Written on October 2, 2026 before this follow-up calculates grouping scores. The source is the already pinned OKR SQLite database. This is a reference-controlled test of recorded physical geometry. The analyst has seen the source's published partitions and the database's cluster intervals while auditing KHI-01. The grouping rule is fixed here; the evaluator's partition labels and all numerical quantities are absent from its tested input.

## Shared source assumptions

Use UR063 / KH0300's eight level-one recorded clusters spanning pendants 1-111. Its reference accounting partition has six groups, ending at pendants 20, 38, 56, 76, 96 and 111. Use UR068 / KH0305's level-one recorded clusters wholly within pendants 14-73. Its reference partition has three groups, ending at pendants 33, 53 and 73. The published group counts, source range selection and reference partitions have already been seen. The primary comparison supplies only the group count to the grouping rule. A separate exploratory estimator receives no group count.

Treat cluster start and end coordinates as the recorded interval geometry. A candidate cut lies between two consecutive recorded clusters. Its observed gap is the next cluster's start minus the previous cluster's end. Use exact decimal fractions. Exclude the final cluster's trailing space because it has no following cluster within the selected range. Keep the recorded `SPACING` field as an audit field; do not substitute it for a computed inter-cluster gap. Record any overlaps, missing endpoints, non-monotone order or duplicate cord ranges before scoring. If a range cannot be represented as complete consecutive recorded clusters, stop that case and preserve the coverage failure.

## Fixed grouping rule and information loss

For a supplied group count g, select the g-1 largest inter-cluster gaps. Retain all admissible cut sets at the cutoff, including ties. A known exact gap is represented as a closed interval with equal lower and upper bounds. A missing gap has bounds zero to infinity. For uncertain gaps, each supplied interval is independent. A cut set is admissible when some choice within the intervals can rank every selected gap at least as high as every unselected gap. Return the entire admissible set, its exact count and the partition corresponding to every candidate. Do not choose a source-matching candidate from a tie.

The evaluator records whether the published partition survives, whether it is the sole candidate, the number of admissible partitions and boundary precision/recall for a unique answer. Score the count-free estimator separately. On complete positive point gaps it chooses the largest adjacent ratio between distinct sorted gap values, splitting above that threshold. Retain all tied largest-ratio thresholds. With missing or widened gap intervals, this estimator abstains and records the available group-count range. Equal point gaps also cause abstention.

Compare the recorded geometry against these controls:

1. Ordered clusters with the supplied group count and all metric distances removed. Enumerate every contiguous partition with g nonempty groups; retain exact ambiguity counts.
2. Ordered clusters without a group count or distances. Count all contiguous partitions, including one group and one group per recorded cluster.
3. Every distinct permutation of the recorded gap-value multiset across the eligible boundary positions. Keep cord order, cluster sizes and the supplied group count unchanged. Report exact recovery counts and all score distributions.
4. An equal-cord-count boundary baseline, restricted to eligible cluster boundaries. Enumerate the cut sets minimizing total absolute deviation from n/g cords per group and retain every tied optimum.
5. One missing gap at a time, plus all gaps missing. Preserve every alternative allowed by the fixed rule.
6. A forced-tie control in which all observed gaps equal one. Retain every tied cut set.

Translation of all cluster intervals by 100 units and multiplication by 1/10 or 10 must preserve the baseline partition candidates. An orientation reversal with mirrored reference boundaries is an invariance check.

## Measurement sensitivity

Widen every derived gap independently by a fixed radius r in source coordinate units, truncating the lower bound at zero. Radii are 0, 1/20, 1/10, 1/5, 1/4, 3/10, 1/2 and 1. This is a simulated gap-measurement sensitivity model applied to recorded point gaps. It does not estimate the original measurements' error distribution. Save exact interval bounds, all admissible cut sets and the first radius at which the source partition ceases to be uniquely selected.

The simple interval-ranking criterion is independently checked by a rational construction: assign each selected gap its upper bound and each unselected gap its lower bound, replacing an infinite selected upper bound with a finite rational value above every finite bound. Each saved candidate must satisfy the ranking. For rejected cut sets, retain a selected upper bound smaller than an unselected lower bound as an exact exclusion certificate.

## Records and freeze

The tested input contains stable cluster IDs, cord-number spans, start/end coordinates, eligible boundary indices and the optional group-count prior. Numerical knot values, cord quantities, accounting labels and reference cut sets stay outside it. Preserve the evaluator key separately under local-only source derivatives. Save all inferred candidates locally and publish aggregate counts with input hashes.

Freeze protocol bytes before running. Independently reconstruct interval gaps from the raw database, verify every candidate and exclusion certificate, verify permutation counts by their multiset formula, and check the information-loss counts with combinatorial identities. Freeze the code, manifests, input hashes, detailed-output hashes, aggregate scores, checks and retrospective in a new interval endpoint. Frozen protocol snapshots retain this original directory's relative-link context.
