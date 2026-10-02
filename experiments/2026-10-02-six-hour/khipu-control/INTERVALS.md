# Grouping from recorded cluster intervals

Recorded inter-cluster gaps selected the published six-group UR063 partition and the three-group UR068 partition, with one admissible answer in each case. The equal-cord-count baseline selected the same partitions. These two source cases therefore fit both grouping rules. [Scores](endpoints/intervals-v1/aggregate.json), [exact verification](endpoints/intervals-v1/verification.json) and [protocol](PROTOCOL_INTERVALS.md).

## Source information and priors

The input contains eight recorded UR063 clusters spanning pendants 1-111 and fourteen UR068 clusters within pendants 14-73. It uses stable cluster IDs, cord spans and recorded start/end coordinates. The primary rule receives the published group count, six or three. The source range selection, group counts, partitions and interval records were already seen during source review. Numerical quantities and reference cut sets are absent from the grouping function's input. This is a reference-controlled measurement test using the pinned database.

For each possible boundary, the rule computes the next cluster's start minus the previous cluster's end. It selects the largest five or two gaps. Every tied or interval-compatible cut set is retained. A separate estimator without a group count selects the largest ratio between adjacent distinct gap levels; it chose six and three groups on these recorded point gaps.

## Distances, group sizes and order

| Information or rule | UR063 | UR068 |
|---|---:|---:|
| Recorded intervals, supplied count, largest-gap rule | 1 correct candidate | 1 correct candidate |
| Cord counts, supplied count, equal-size rule | 1 correct candidate | 1 correct candidate |
| Order and supplied count, no distance or size-selection rule | 21 partitions | 78 partitions |
| Order alone, no supplied count | 128 partitions | 8192 partitions |
| Exact gap-multiset permutations matching the reference | 20 of 420 | 2 of 156 |

The equal-size baseline minimizes the sum of absolute differences between each group's cord count and the average group size. Its minimum was 9 cords for UR063 and zero for UR068. The baseline's success shows that the supplied count and the recorded cluster sizes offer a second route to the partition in these cases. The distance permutation controls isolate which boundary carries a large gap while preserving the gap distribution and cord order.

## Missing measurements and interval width

Each missing gap is represented by a nonnegative unbounded interval. The rule preserves all compatible partitions. With every gap missing, it retained all 21 and 78 partitions. Making every gap equal also retained those complete sets. A missing value never became a zero observation.

The measurement sensitivity model independently widens each recorded gap by a radius in source coordinate units. It is a specified perturbation model; the archive supplies no error distribution for these measurements.

| Gap radius | UR063 admissible partitions | UR068 admissible partitions |
|---:|---:|---:|
| 0 | 1 | 1 |
| 0.05 | 1 | 1 |
| 0.10 | 1 | 1 |
| 0.20 | 1 | 1 |
| 0.25 | 10 | 12 |
| 0.30 | 10 | 12 |
| 0.50 | 15 | 78 |
| 1.00 | 21 | 78 |

The smallest selected point gap is 1 and the largest unselected gap is 0.5 in both cases. Their uncertainty intervals stay separated when the radius is below 0.25. At 0.25 the intervals meet, allowing multiple rankings and partitions. The source partition remained among the candidates at every radius tested.

Verification checked all 626 inference records, 1097 rational ranking witnesses and 22,537 exact exclusion certificates. Every possible cut set was accounted for. Independent checks reconstructed the gaps from SQLite, verified the multiset permutation counts, recomputed the size baseline and checked translation, scale and orientation invariance. The [frozen endpoint](endpoints/intervals-v1/freeze-manifest.json) preserves the protocol, code, manifests, aggregate scores, verification and retrospective.

The next acquisition decision is the ambiguous boundary's distance and its measurement resolution. A prospective test should add source accounts with documented groups selected before inspecting their intervals. That would compare the largest-gap and equal-size rules on cases where they predict different partitions.
