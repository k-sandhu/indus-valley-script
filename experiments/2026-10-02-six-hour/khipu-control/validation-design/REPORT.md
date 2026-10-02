# Independent validation rows resolve a repeated-carry failure

Choosing checks by coefficient rank removes the wrong decoder that passed eight fresh account relations in KHI-04. On its four-swap baseline population, greedy rank rejects all nine wrong final rays with two checks when the unit value is already counted, or three checks when scale is unmeasured. Count-first needs fewer checks on this population: one count rejects all nine with the unit anchor, and two counts reject them without it.

This is a post-outcome comparison on KHI-04's fixed generated observations and candidate sets. The [protocol](PROTOCOL.md) states the prior exposure, equal check-count budget and selection interface. [Methods](METHODS.md) explains physical premises and how validation retains rays and continuous families. Policy choices were [sealed](main-v1/selection-manifest.json) before scoring opened decoder candidates or measured targets.

## Wrong rays remaining compatible with selected observations

The table uses the four-swap local-consensus population at the 50% support gate. Nine of its 200 worlds originally had a wrong unique relative ray. Each entry counts how many of those nine remain compatible after the indicated number of checks. Uniform-random entries are expected counts, rounded to three decimal places; [aggregate.json](main-v1/aggregate.json) retains exact fractions.

| Available scale | Selection policy | One check | Two checks | Three checks |
|---|---|---:|---:|---:|
| Unit anchor counted | Account-first | 5 | 2 | 1 |
| Unit anchor counted | Count-first | 0 | 0 | 0 |
| Unit anchor counted | Greedy rank | 3 | 0 | 0 |
| Unit anchor counted | Uniform random | 3.545 | 1.418 | 0.606 |
| Unmeasured | Account-first | 5 | 2 | 1 |
| Unmeasured | Count-first | 9 | 0 | 0 |
| Unmeasured | Greedy rank | 3 | 1 | 0 |
| Unmeasured | Uniform random | 6.000 | 3.545 | 2.024 |

Greedy rank includes the available anchor row when selecting independent checks. With that anchor, two selected rows reach coefficient rank three in all 200 four-swap worlds. Without the anchor, three selected rows reach rank three in all 200. Three account-first checks reach rank three with the anchor in 170 worlds; without it, homogeneous account equations reach rank two in 170 and rank one in 30. Account checks leave absolute scale free.

One independently counted object works differently in the two views. With known unit scale, its measured value tests the candidate's predicted absolute quantity. With unmeasured scale, every wrong ray in this nine-world group can adopt a positive scale that fits the first count. The second independent count compares those fitted scales and rejects all nine. Count-first therefore outperforms the generic rank rule at the smallest useful budget here, even though its two-row set has rank two without the anchor. The original candidate sets also contribute constraints.

## The rank-one witness

World `20261020124-four_swapped` has the wrong normalized candidate `(1,4/3,22)`. All eight fresh account rows are multiples of `-10u -9t +h = 0`, or zero. The [saved trajectories](main-v1/rank-one-failure-trajectories.json) show the following selections.

| View and policy | Selected checks at the first rejection | Rank including anchor |
|---|---|---:|
| Counted, count-first | `count-0` | 2 |
| Counted, greedy rank | `account-0`, `count-0` | 3 |
| Unmeasured, count-first | `count-0`, `count-1` | 2 |
| Unmeasured, greedy rank | `account-0`, `count-0`, `count-1` | 3 |

Account-first retains the wrong candidate through all three tested budgets. In the unmeasured view, greedy rank's second check fixes the wrong absolute vector `(645/23,860/23,14190/23)` on the original wrong ray. Its third check rejects that vector. This intermediate outcome is saved alongside the eventual rejection. A successful count fit and an identified scale can coexist with wrong ratios.

The first count supplies `6v +8w = 5160`. Both the true vector `(6,60,600)` and the wrong scaled vector satisfy it. The second count supplies `6u +6v +3w = 2196`; the wrong vector has residual `1092/23`. These quantities are evaluator observations, opened after row choices were sealed.

## Filtering tied candidates

Validation also intersects originally ambiguous optimum sets with the selected observations. Gate rejection remains rejection. The experiment does not return to discarded training candidates after an optimum set is excluded.

For four-swap local consensus at the 50% gate, either counted-view greedy rank with two checks or counted-view count-first with one check yields 190 correct absolute points and rejects ten worlds. The original result had 133 correct rays, nine wrong rays and 58 ambiguous sets. The extra 57 correct points come from filtering those ambiguous sets. One ambiguous optimum lacked the true decoder and is excluded with the nine wrong unique rays.

For collective consensus at the same gate, counted-view count-first with one check and counted-view greedy rank with two checks each yield 199 correct absolute points and reject the remaining wrong world. Its original result had 190 correct rays, one wrong ray and nine ambiguous sets. In the unmeasured view, three greedy-rank checks or two count-first checks give the same 199 correct absolute points.

All original correct rays are preserved by the tested checks. The fifteen wrong collective rays caused by a misdeclared partial pool are all rejected by counted-view greedy rank with two checks, unmeasured greedy rank with two checks, or unmeasured count-first with two checks. The independent ownership controls retain their original gate rejections.

## Verification and preserved outputs

The [main verification](main-v1/verification.json) checks 11,200 sealed selection records, 33,600 deterministic validation records, 5,736 optimum-part classifications, 108,970 selected residuals, 185,600 distinct random-subset rank calculations and 30,640 analytic random-ray expectation checks. The [additional review](additional-review/verification.json) independently checks random subsets on originally ambiguous optimum sets and preserves compatible wrong random-choice witnesses. Both use arithmetic separate from the selector and fitted-set intersection implementation.

The complete aggregate has 896 condition/view/budget/selector/fitter comparisons, covering both original support gates. Selected IDs, measured targets, positive families, discrete points and rejected cases remain available in the sealed endpoint. [The retrospective](RETROSPECTIVE.md) records the failed selection routes and the information required for a prospective collection study.
