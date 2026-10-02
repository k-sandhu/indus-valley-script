# Extra shrinkage returned first-order backoff

All five outer folds selected the pure first-order option from the eighteen frozen candidates. The resulting 8,009 predictions equal the preserved first-order endpoint, including every candidate mass, outcome and target loss. This post-outcome follow-up tested whether extra shrinkage of rare two-state histories would improve probability prediction after the earlier second-order model improved top-one accuracy but increased loss.

The [protocol](PROTOCOL.md) was frozen before fitting. It reuses 1,596 distinct strings, 1,526 physical/text components, the original outer folds and their three inner folds. The first-order strength stays twenty. For history count N, the added mixture has effective strength `α+κ+α*κ/N`; α comes from 5/20/100/500/2000 and finite κ from 0/20/100/500. Deduplicating equivalent pairs leaves seventeen finite choices plus exact first-order backoff. Inner held-out unknown-bucket loss selects the model. Beginning and end states participate in the complete likelihood, with all factors affected by a masked slot included in its conditional probability.

## Selection and measured outcomes

The best finite choice was α=2000, κ=500 in every outer training population. Its inner loss remained above backoff by 0.00846–0.00929 bits per slot. The selection therefore used no tie rule.

| Outer fold | Backoff inner loss, bits | Best finite inner loss, bits | Finite minus backoff |
|---|---:|---:|---:|
| 0 | 5.188612 | 5.197898 | 0.009286 |
| 1 | 5.262646 | 5.271614 | 0.008968 |
| 2 | 5.219459 | 5.227916 | 0.008457 |
| 3 | 5.276859 | 5.285890 | 0.009031 |
| 4 | 5.312505 | 5.321603 | 0.009098 |

The [complete result](main/results.json) preserves all ninety candidate/fold evaluations and saved-comparator correspondence. The following percentages use the same 8,009 queries.

| Model | Top one | Top five | Top ten | Bucket loss, bits | ECE | Top-label Brier |
|---|---:|---:|---:|---:|---:|---:|
| Adaptive selection, equal to M1 | 34.5861% | 58.4592% | 65.4264% | 5.119435 | 0.025564 | 0.165292 |
| Earlier top-one-selected M2 | 37.2706% | 58.8713% | 65.4514% | 5.247171 | 0.043506 | 0.170584 |
| Saved PMB | 33.8120% | 55.3377% | 62.7045% | 5.747731 | 0.080484 | 0.172794 |

Against M1, every paired difference and interval is exactly zero. Against the earlier M2, adaptive minus M2 top-one accuracy is −2.6845 percentage points, with a paired component interval of −3.3962 to −1.9588. Its loss difference is −0.127736 bits, interval −0.158777 to −0.097065. Top-five and top-ten differences are −0.4120 and −0.0250 points, intervals −0.9037 to 0.0736 and −0.4541 to 0.3977. These intervals use 10,000 resamples of the 1,526 components at seed 23102. The saved result also contains the paired PMB comparisons, text/type averages and Brier intervals.

Top-one accuracy is 18.2331% at initial positions, 33.5894% internally and 53.9474% at final positions. The corresponding earlier M2 values are 21.1153%, 36.0805% and 57.0175%. Frequency groups show the same prediction tradeoff: for codes appearing 2–4, 5–19 and at least twenty times, adaptive top-one accuracy is 0.2427%, 6.8618% and 42.1965%; M2 gives 1.2136%, 9.5863% and 45.0711%. All 205 singleton codes are absent from their training folds and receive zero exact restoration accuracy. The shared unknown bucket accounts for 3.1340% of true slots in the loss calculation. Every query has a finite score.

## Verification and reuse

The [independent review](review/verification.json) passed. It constructs flat unigram, initial, transition, triple and history counts, reconstructs all 8,009 query distributions, and compares complete-record likelihoods with the local masked factors. It checks 13,045 positive history contexts and 3,859 exact rational identities for the effective strength, including an additional finite-mixture probe. It reproduces every query/group/fold identity, hidden-target replacement check, top-k outcome, calibration summary and paired interval. Saved candidate masses and losses match exactly; the largest complete-likelihood discrepancy is 1.55×10⁻¹⁵ and the finite-factor discrepancy is 2.22×10⁻¹⁶. No rank difference needed a rational tie witness.

The main fit took 195.14 seconds and the independent review 12.45 seconds. [The main source](../../../src/six_hour/markov_adaptive.py) and [review source](../../../src/six_hour/markov_adaptive_verify.py) refuse to overwrite existing endpoints. Their [main](main/code_snapshot.py) and [review](review/code_snapshot.py) snapshots, imported [helpers](sources/) and recorded hashes preserve the executed implementation. Detailed source-linked slot predictions remain local. [The work record](RETROSPECTIVE.md) explains the design choices and next test premise.
