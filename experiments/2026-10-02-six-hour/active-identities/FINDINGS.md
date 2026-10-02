# Choosing identities to measure

Selecting the identity with the largest posterior entropy reduced the measurements needed to recover the simulated map. A confidence-based stopping rule behaved differently: the same policy more often crossed 95% conditional mass while selecting a wrong map. This trade-off persisted after accounting for the generated system as the comparison unit.

The [main grid](main/results.json) contains 48 new systems, 576 reference/training/process conditions and 15,552 saved measurement-prefix records. Three policies see the same encoded records: random choice, posterior-entropy choice and highest training-frequency choice. Each requests one reliable identity at a time from a separate oracle. The search continues through all eight requests so that the histories remain available for evaluation.

## Measurement cost and conditional stopping

The table pools four sample-size conditions per system. Each row therefore contains 96 paired condition histories from 24 systems. A measurement count is the first prefix whose selected map equals the concealed answer. The stopping diagnostic chooses the first prefix with map mass at least 0.95, including prefix zero, and checks whether that selected map was correct.

| Administrative process | Query rule | Mean measurements to exact map | Wrong 95%-mass stopping decisions |
|---|---|---:|---:|
| Unchanged | Random | 1.573 | 3/96 |
| Unchanged | Entropy | 0.906 | 7/96 |
| Unchanged | Frequency | 2.208 | 3/96 |
| 35% mixture change | Random | 3.552 | 17/96 |
| 35% mixture change | Entropy | 2.500 | 25/96 |
| 35% mixture change | Frequency | 4.167 | 15/96 |
| 70% mixture change | Random | 5.667 | 44/96 |
| 70% mixture change | Entropy | 4.885 | 60/96 |
| 70% mixture change | Frequency | 5.552 | 31/96 |

The [condition table](review/conditions.csv) retains every reference size, training size and process condition. The [paired comparison](review/paired-system-comparisons.json) averages the four size conditions within each system and resamples the 24 system averages. At 35% process change, entropy choice uses 1.052 fewer measurements than random choice, with a 95% paired bootstrap interval of 0.698–1.396 fewer. Its wrong stopping rate is 8.33 percentage points higher, with interval 0.00–17.71. At 70% change, the corresponding measurement reduction is 0.781, interval 0.490–1.083; the stopping-error increase is 16.67 points, interval 7.29–26.04.

The stationary transition family begins with the correct map in all unchanged-process histories, so no measurements are required for exact recovery in those cases. With 70% mixture change, entropy choice averages 1.083 measurements, random choice 1.531 and frequency choice 1.656. Their wrong stopping decisions are 20/96, 19/96 and 16/96. These results make the generator family part of the acquisition question.

## What the query rule knows

The solver starts with a conditional mass over all 40,320 bijections. After `k` exact identity observations it retains `(8−k)!` compatible maps and renormalizes their original scores. Its entropy query chooses the code whose possible identity responses have the largest entropy. For an exact response, this equals the expected reduction in map entropy. The policy receives those compatible maps, their masses, the remaining code IDs, training frequencies and a random generator. It receives no answer vector or oracle state.

The fixed scores make exact recovery monotone along this particular history. Once the true map wins, restricting to a smaller compatible set that still contains it cannot introduce a higher-scoring rival. Thus the protocol's first-correct and permanently-correct prefixes coincide by construction. This is a property of the benchmark's update rule; a solver that refits its model after each observation could behave differently.

These observations separate two uses of model uncertainty. It can help select a measurement even when its probability estimates are poorly calibrated. Using the same probability threshold to decide that enough evidence has been acquired requires an additional assessment. The saved histories provide controlled examples for testing alternatives such as reserved verification measurements, disagreement between generative models and confidence calibration across known systems.

## Relation to other fields

Information-based measurement selection is established work. MacKay's [1992 paper](https://authors.library.caltech.edu/records/efefp-2j353) develops Bayesian information criteria and discusses their dependence on the hypothesis space. Tang, Sloman and Kaski's [2026 AISTATS paper](https://proceedings.mlr.press/v300/tang26d.html) combines informativeness with representativeness and a correction for error amplification under model mismatch. Its regression setting and acquisition formulas offer a subsequent comparison; this experiment implements exact identity entropy and the two named controls.

For the Indus project, the next measurement might concern a physical relation, a preserved sign feature, a quantity or a securely joined context. Each has a different likelihood and cost. The [physical-acquisition branch](../physical-acquisition/PROTOCOL.md) tests unrestricted quantities and interval measurements. The [Lothal source audit](../lothal-physical-use/PROTOCOL.md) identifies the attachment observations that could define another acquisition problem. Independent identity measurements are supplied assumptions here, with a reliable oracle and a shared eight-symbol inventory.

## Review and reuse

[Thirteen checks](review/checks.json) pass. Every history preserves the observations, factorial candidate counts and recovery flags. An independent likelihood calculation reindexes encoded counts into reference coordinates and matches the frozen implementation within `5.01e-12` total bits. It replays 648 prefix records, matching selected maps and queries; the largest map-mass discrepancy is `1.89e-13`.

```powershell
python src/six_hour/active_identities.py --output experiments/2026-10-02-six-hour/active-identities/repeat
```

Use a fresh endpoint. The checked pilot and two serialization failures remain separate. The main run took 176.7 seconds. The [retrospective](RETROSPECTIVE.md) records those repairs, the oracle separation and the interpretation of the stopping diagnostic.
