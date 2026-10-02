# Recovering quantities from physical membership

Twenty-four simulated collections recovered the relative values of six unfamiliar labels after twelve complete container–contents observations. One independently counted object then fixed their absolute values in every collection. The same arithmetic procedure rejected scrambled membership and independent ownership badges. Missing contents produced a useful distinction: recording the missing pieces preserved the answer, while treating the remaining contents as complete rejected it.

The experiment connects the user's alien-artifact idea to an explicit calculation. The investigator receives unfamiliar labels and learns which objects contain which other objects. Conservation supplies equations; their rank measures how much they determine. This is a constructed benchmark with a concealed answer key and a supplied additivity hypothesis. The [protocol](PROTOCOL.md), [corrected results](main-corrected-anchor/results.json) and [generated worlds](main-corrected-anchor/worlds.json) contain the design and every case.

## How much each observation determines

Each collection has six randomly renamed values, `{1, 2, 3, 4, 6, 8}`. Each assembly contains two to four separately labelled children whose quantities add to the parent's quantity. Twelve assemblies train the solver and eight further assemblies assess it. Added unlinked objects make the single-label pool exactly balanced. The balanced text-only observations leave all 720 permutations of the value bag compatible.

For a complete assembly, the observed relation contributes a row to `A v = 0`: one parent label minus its child labels. Five independent rows identify a positive relative vector for six codes. Multiplying this vector by a constant preserves every equation. A physical count on one labelled object fixes that constant. The solver computes ranks and nullspaces with exact fractions.

A separate finite diagnostic supplies the known bag of six values and enumerates every assignment. This prior can determine a mapping before the physical equations determine the relative vector. Both assays are retained in the result table.

| Complete training assemblies | Unique finite assignment, out of 24 collections | Unique positive relative vector, out of 24 | Absolute values recovered with one count, out of 24 |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 |
| 2 | 2 | 0 | 0 |
| 3 | 12 | 0 | 0 |
| 5 | 23 | 7 | 7 |
| 8 | 24 | 23 | 23 |
| 12 | 24 | 24 | 24 |

At three assemblies, the finite candidate count ranged from one to eight, with median 1.5. Every unrestricted system still had at least three free linear coordinates. This gives a concrete way to inspect the information contributed by a prior: remove the supplied value bag and recompute the rank.

## Membership, missing pieces and ownership

| Condition at twelve training assemblies | Exact equality rank | Finite candidate maps | Correct relative vector recovered | Held-out acceptance of a unique positive ray |
|---|---|---|---:|---:|
| Complete membership | 5 in all 24 collections | 1 in every collection | 24/24 | 24/24 |
| Scrambled membership | 6 in all 24 | 0 in every collection | 0/24 | 0/24 |
| Six incomplete groups treated as complete | 6 in all 24 | 0 in every collection | 0/24 | 0/24 |
| Six incomplete groups recorded with inequalities | Rank 3 in 2; rank 4 in 5; rank 5 in 17 | 1 in every collection | 17/24 | 17/24 |
| Independent ownership labels | 6 in all 24 | 0 in every collection | 0/24 | 0/24 |

Scrambling preserves the parent-label frequencies and the multiset of child groups. Ownership labels are shuffled across all object slots, including fillers, and retain the same balanced label frequencies. Physical membership supplies the difference between these controls and quantity labels.

For incomplete groups, `parent ≥ visible children` retains the quantity carried by a missing child. At twelve observations, all 24 finite-bag analyses selected the correct assignment, but seven unrestricted systems retained additional relative assignments. The [integer certificates](integer-ambiguity-certificates.json) give another positive integer assignment in each of those seven collections, preserving every training equality, every incompleteness inequality and the one measured count.

For example, collection 20261015 admits both rows below after its available contents and a count of eight on label `g1`:

| Assignment | g0 | g1 | g2 | g3 | g4 | g5 |
|---|---:|---:|---:|---:|---:|---:|
| Concealed answer | 6 | 8 | 1 | 2 | 4 | 3 |
| Another compatible integer assignment | 12 | 8 | 2 | 4 | 8 | 2 |

The withheld complete assemblies reject the second row. Each of the seven certificates retains its exact constraints and a withheld check. These examples were constructed after the outcome to demonstrate the remaining ambiguity; they are separately labelled post-outcome reviews.

Short collections can also support a wrong positive relative vector. At the five-assembly prefix, two scrambled collections and three incorrectly completed collections had such a vector. All five failed the eight withheld relations. The [records](main-corrected-anchor/results.json) preserve their ratios, including a scrambled example with primitive values `[6, 1, 2, 4, 8, 1]`.

## Which object to count next

Under the finite known-bag diagnostic, each possible measurement partitions the remaining assignments by that label's value. The active rule chooses the label with the smallest expected number of survivors, then obtains its physical count. At the two-complete-assembly prefix, the active choice left a mean of 1.333 candidate assignments across the 24 worlds. Averaging all six possible code choices left 2.007. At one assembly, the corresponding means were 6.667 and 9.125.

These figures describe the specified six-value prior. The unrestricted solver uses the simpler collection rule: acquire enough independent physical relations to identify a positive relative vector, then count an object to fix scale. The recorded rank and remaining alternatives show which new observation would resolve the particular collection.

## Scope of the calculation

The inference class uses positive commensurate quantities, stable label values and independently observed membership. Missingness is known for the incomplete-content condition. The solver receives the additivity hypothesis; it does not discover an unrestricted purpose from images. The 24 seeds are the independent simulation units, while prefixes and controls reuse those worlds. Zero accepted controls in 24 worlds describes this experiment's sample. Graphics, manufacturing variation, mixed commodities, measurement noise and uncertain label recognition need separate tests.

The [archaeological target](ARCHAEOLOGICAL_TARGET.md) identifies a Susa envelope group where inside/outside observations could be collected. Its acquisition table specifies content membership, completeness and the separation of seal impressions from other exterior marks.

## Reproduce and review

Run the corrected implementation into a new directory:

```powershell
python src/six_hour/physical_information.py --output experiments/2026-10-02-six-hour/physical-information/repeat
python experiments/2026-10-02-six-hour/physical-information/verify_run.py experiments/2026-10-02-six-hour/physical-information/repeat --output experiments/2026-10-02-six-hour/physical-information/repeat-review.json
```

The [review](corrected-review.json) checks all 840 records by direct enumeration, rank over two prime fields, exact residuals, measurement-object identity and snapshot hashes. The implementation's determinant checks provide a second rank witness. The [blind inputs](blind-inputs/training.json) contain neutral object IDs, labels, membership and one count for 96 collections; [withheld relations](blind-inputs/withheld.json) and the [answer key](blind-export-key.json) are separate.

The first run remains in [main](main/results.json). Preparing the blind interface exposed an ownership-control count error. The [correction](ANCHOR_CORRECTION.md) was recorded before a new run, and the [comparison](anchor-correction-comparison.json) confirms that all 840 matrix triples and all unanchored ranks stayed unchanged. Use the corrected endpoint for ownership measurement diagnostics. The [retrospective](RETROSPECTIVE.md) records the approach, this repair and the subsequent checks.
