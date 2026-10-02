# Recovering short encoded records from a known reference

CRYPTO-02. Synthetic experiment completed 2 October 2026. [Protocol](PROTOCOL.md), [all 1,152 trial rows](main/results.json), [96-condition table](review/conditions.csv), [arithmetic checks](review/checks.json).

The experiment recovered an eight-symbol encoding reliably when the reference population had distinctive transition patterns and the encoded population followed the same process. A changed administrative process exposed a different result: the best mapping could be confidently wrong while still predicting held-out records better than an unrelated reference.

## What was concealed and supplied

Each of 24 generated systems supplied 4,000 independently sampled reference records. A random bijection replaced its eight identities in a separately sampled population of three-to-seven-symbol records. The solver received 40, 160 or 640 encoded training records and zero, one, two or four correct identity anchors. It enumerated every compatible bijection, using either unigram frequency or a stationary first-order Markov score. Four hundred encoded records were reserved for evaluation.

Half the systems generate asymmetric transitions. The other half generate forms with first, middle and final slot preferences, plus an unobserved office state. The stationary Markov score approximates that second process. A declared sensitivity mixes 35% identity-dependent noise into encoded records while keeping the reference unchanged. A separately generated reference competes with the correct one.

The independent units are 24 generated systems. The 1,152 rows share reference samples, encodings or held-out records within each system; they should be read as a condition grid. Every table cell below contains 12 systems.

## Recovery under the stationary Markov score

The entries give complete mappings recovered out of 12. Partial recovery and every unigram comparison appear in the [condition table](review/conditions.csv).

| Generator and change | Training records | No anchors | One anchor | Two anchors | Four anchors |
|---|---:|---:|---:|---:|---:|
| Transition, unchanged | 40 | 12 | 12 | 12 | 12 |
| Transition, unchanged | 160 | 12 | 12 | 12 | 12 |
| Transition, unchanged | 640 | 12 | 12 | 12 | 12 |
| Transition, 35% mixture change | 40 | 12 | 12 | 12 | 12 |
| Transition, 35% mixture change | 160 | 12 | 12 | 12 | 12 |
| Transition, 35% mixture change | 640 | 12 | 12 | 12 | 12 |
| Administrative form, unchanged | 40 | 7 | 7 | 9 | 11 |
| Administrative form, unchanged | 160 | 11 | 12 | 12 | 12 |
| Administrative form, unchanged | 640 | 12 | 12 | 12 | 12 |
| Administrative form, 35% mixture change | 40 | 0 | 0 | 1 | 7 |
| Administrative form, 35% mixture change | 160 | 2 | 2 | 7 | 10 |
| Administrative form, 35% mixture change | 640 | 6 | 7 | 9 | 11 |

Frequency alone recovered no complete mapping in either unchanged generator at 40 records without anchors. At 640 records it recovered one of 12 transition systems and four of 12 administrative systems. Frequencies become easier to match when their differences are pronounced and stable; the present grid shows how short samples and distribution changes interfere with that match.

Correct anchors reduce the search space from 40,320 maps to 5,040, 720 or 24. Their value depends on which distinctions remain unresolved. The transition systems already offer enough distinctive structure for this solver; the changed form systems benefit more from supplied identities.

## Confidence and reference selection

Of 576 Markov condition rows, 96 select a wrong complete map. Twenty-six of those assign at least 95% conditional plug-in mass to the selected map. Eighty-three of the 96 still choose the correct reference over the unrelated reference on held-out records. These are descriptive counts over overlapping conditions, rather than an estimated error rate for historical decipherment.

For example, administrative seed `20361002`, 160 training records, no anchors and a 35% mixture change swaps two of the eight identities. The selected map receives approximately 0.9999987 conditional mass; the true map receives approximately 4.0 × 10⁻¹⁵. The selected reference still wins on holdout by 0.0972 bits per sign. The [recorded failures](review/confident-failures.json) make the exact alternatives inspectable.

This mass conditions on a fixed fitted reference, a stationary likelihood and a uniform prior over the permitted maps. It omits reference uncertainty and changes in the process that produced the encoded records. The result motivates an explicit process-change model, alternative reference families and an abstention test in the next experiment.

## Checks and practical use

Twelve checks passed. They compare the vectorized enumeration with direct sequence likelihoods, verify consistent observed-label renaming, recover a separated reference example, count anchor-compatible maps, check the complete grid and recorded accuracies, and inspect generation seed streams. The preserved code snapshot's hash matches the endpoint. The pilot remains separately available at [pilot/results.json](pilot/results.json).

The benchmark supplies known synthetic identities, a bijective encoding and a known reference system. Those are substantial inputs. Its practical contribution to Indus research is a reusable test for an anchored mapping method: report complete identity recovery alongside predictive fit, test changes in the generating process, and retain wrong confident alternatives. Applying the method to artifacts requires a separately justified reference and source-backed anchors.

## Next experiments

The original grid is complete and frozen. A later stress experiment will vary reference size, process changes and erroneous anchors. It will measure whether diagnostics can identify the resulting failures using evidence available to the solver. A generator-aware form model will help separate small-sample error from the stationary model's approximation of office and slot structure.
