# Deduplication changes a conditional sampling law

In this known independent-slot process, retaining the distinct strings from seven raw records gives a different conditional law from drawing six records conditional on uniqueness. The difference changes the exact 5% rejection probability of the preserved nested statistic from 5.0000% to 5.1537% when its uniform-unique reference is retained. A reference matched to the selection law gives 4.9407%.

The raw process draws seven three-sign binary strings. Slot probabilities of one are .2, .3 and .4, with independent slots and records. Retain each string once, condition on obtaining six distinct strings and three ones in every retained column, then assign the six retained strings to labels uniformly. Four supports satisfy those conditions; each omits a complementary pair from the eight possible strings.

| Omitted pair | Probability sum of retained strings | Selected support probability | Uniform-unique support probability |
|---|---:|---:|---:|
| 000,111 | .64 | 21.3333% | 25% |
| 001,110 | .74 | 24.6667% | 25% |
| 010,101 | .80 | 26.6667% | 25% |
| 011,100 | .82 | 27.3333% | 25% |

Each support S can arise through six raw occupancy vectors, one for each string that appears twice. Summing their seven-draw multinomial probabilities gives `(7!/2) × ∏q(x) × Σq(x)` over x∈S. The retained column margins fix the product. The remaining sum distinguishes the supports. Uniformly labeling each support spreads its mass over its 720 arrangements.

All 2,880 labeled tables and their nested scores already exist in the frozen exact enumeration. This experiment reuses those scores and changes only the known observation-law weights. It fits no new models. The exact rejection probabilities are:

| Threshold | Uniform law and uniform reference | Selected law and uniform reference | Selected law and matched reference |
|---:|---:|---:|---:|
| 1% | .9722% | 1.0130% | .9370% |
| 5% | 5.0000% | 5.1537% | 4.9407% |
| 10% | 9.9306% | 9.9333% | 9.9333% |
| 25% | 25.0000% | 25.1704% | 24.9574% |

Across every attainable cutoff, the largest excess over the nominal cutoff for the selected law with the uniform reference is .6046 percentage points, at a cutoff of 38.9583%. The matched selected-law tails satisfy the conservative rank property at every cutoff. The simpler integer adjacency score gives a further example: at a .25 threshold, its rejection probability changes from .25 to 4/15 under selection. These magnitudes belong to the declared seven-record process.

An independent audit propagates exact probabilities over the set of strings seen after each of the seven draws, verifying the support masses without the occupancy formula. It also rechecks all 11,520 saved tail probabilities through sorted prefix sums. [Results](results.json), [verification](verification.json), [protocol](PROTOCOL.md), [code](run.py).

The archaeological source selects and weights records through catalogue and preservation processes that require their own assumptions. The manuscript's unique reference is explicitly conditional on its selected transcription population. This example supplies a finite observation-process test for extending that reference to a proposed sampling history.
