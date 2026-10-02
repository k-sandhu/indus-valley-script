# Checking a proposed mapping with a reserved observation

Additional identity observations detected many wrong proposals that had already crossed 95% model mass. Choosing two identities by the frozen posterior's marginal entropy caught all 60 wrong proposals in the largest administrative process change. A random two-identity audit caught 56. The new run contains 48 generated systems, 576 conditions and 4,032 audit records. [Main result](main/results.json), [reviewed summary](review-clean/summary.csv).

Every proposal comes from the same search rule: acquire reliable identities by maximum entropy until the selected map first reaches 0.95 conditional mass. Freeze that map and posterior. Then select previously unqueried identities and accept the proposal only if its predictions agree with every response. Failed proposals remain rejected; this experiment does not fit a replacement afterward. Correct proposals all pass under the supplied reliable-oracle assumption.

## Wrong acceptances and cost

Each row below pools four sample-size conditions from 24 systems, giving 96 proposals. The two fixed-size audits use up to two extra observations. The bound-based rule chooses the smallest random audit whose worst-case probability of accepting a wrong bijection is at most 0.05.

| Generator and mixture change | Wrong proposals before audit | Wrong acceptances, random two | Wrong acceptances, entropy two | Wrong acceptances, bound rule |
|---|---:|---:|---:|---:|
| Transition, unchanged | 0 | 0 | 0 | 0 |
| Transition, 35% | 0 | 0 | 0 | 0 |
| Transition, 70% | 29 | 5 | 4 | 0 |
| Administrative, unchanged | 8 | 3 | 1 | 0 |
| Administrative, 35% | 13 | 5 | 2 | 1 |
| Administrative, 70% | 60 | 4 | 0 | 0 |

Under the largest administrative change, both two-observation rules average 5.531 total observations, including the earlier search. Entropy verification accepts all 36 correct proposals and rejects all 60 wrong ones. Random verification accepts the same 36 correct proposals, accepts four wrong ones and rejects 56. Averaging the four size conditions within each system and bootstrapping the 24 paired system averages gives an entropy-minus-random wrong-acceptance difference of −4.17 percentage points, with a 95% interval of −8.33 to −1.04. The unchanged and 35% comparisons have intervals spanning zero. [Paired system comparisons](review-clean/paired-system-comparisons.json).

The bound rule uses more observations. Its mean total cost is 6.469, 6.802 and 6.875 observations for the three administrative conditions. It makes one wrong acceptance among their 288 proposals. Its exact expected wrong-acceptance count for those proposals, summing the random audit probabilities, is 0.345. A single observed acceptance is compatible with a probabilistic rule. For unchanged transition systems, the initial proposal is already correct in all cases; the bound rule still requests six observations because its guarantee covers an unknown wrong bijection.

The complete table retains one-, two- and three-observation audits for both selection policies. In this sample, entropy verification often detects errors efficiently. Its effectiveness depends on how the candidate model distributes uncertainty across the remaining identities. Random selection supplies a calculation that uses the remaining identity set and a stated error pattern.

## Exact audit probability

Let U be the number of unqueried identities and m the number where the frozen proposal disagrees with the truth. For a uniform sample of k distinct identities,

`P(audit passes | frozen proposal) = choose(U−m,k) / choose(U,k)`.

The numerator counts subsets containing only correctly proposed identities. A wrong bijection has at least two disagreements, because changing the image of one code forces a change elsewhere. Earlier revealed pairs are correct, so those disagreements all lie in the remaining set. Replacing m with two gives the worst-case pass probability. With eight remaining identities, observing six yields `1/28`, approximately 3.57%; observing five yields `3/28`, approximately 10.71%.

This guarantee concerns one frozen proposal, exact identity responses and uniform sampling. Repeatedly proposing new maps after failed audits would require accounting for the additional acceptance opportunities. An archaeological application also needs the measurement's own error model. The present probability calculation assumes that a requested identity can be established independently and correctly.

## Observation boundary and review

The search and audit selectors receive candidate maps, model weights, unqueried code IDs and their random generator. The complete audit selection is saved before the response oracle is called. The answer key enters outcome evaluation and the exact error-probability check. The entropy audit ranks identities under the frozen posterior and does not update that ranking during the audit.

[Twelve review checks](review-clean/checks.json) pass. The verifier recalculates all 4,032 acceptance/cost records and enumerates every subset for all 2,304 uniform audits. It independently regenerates one condition from each of the 48 systems, evaluates the likelihood in reference coordinates and replays 336 audits. Maximum score difference is `4.55e−12` bits; maximum mass difference is `3.88e−13`.

The code protects completed endpoints. Reproduction uses a fresh output directory with the [protocol](PROTOCOL.md) in its parent. [The retrospective](RETROSPECTIVE.md) records the checked pilot, review-code cleanup and interpretation of rejected proposals. The next step is to identify an archaeological measurement whose outcome can be predicted before it is acquired.
