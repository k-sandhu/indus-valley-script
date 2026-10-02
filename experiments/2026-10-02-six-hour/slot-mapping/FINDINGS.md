# The mapping score needs the distinctions in the record process

Length/slot assignment recovered all 96 eight-symbol administrative mappings and 55 of 96 twenty-symbol mappings. The graph comparator recovered 91 and 25, respectively. For the twenty-symbol administrative family, the paired recovery gain is 31.25 percentage points, with a generated-system bootstrap interval of 21.875–41.667 points. Symbol accuracy rises from 85.0521% to 92.7604%. [Main result](main/results.json), [independent summary and intervals](review/summary.json).

The comparison uses 48 fresh generated systems: twelve per family and inventory size. Each contributes eight conditions from reference sizes 40/400, training sizes 160/640 and process change 0/.35. Sample-size and change conditions reuse the same world. The twelve generated systems are the resampling units within a family/inventory.

| Generator | Symbols | Length/slot: complete maps | Graph: complete maps | Length/slot: symbol accuracy | Graph: symbol accuracy |
|---|---:|---:|---:|---:|---:|
| Transition process | 8 | 21/96 | 90/96 | 60.1563% | 98.3073% |
| Transition process | 20 | 0/96 | 74/96 | 24.4271% | 89.2708% |
| Administrative forms | 8 | 96/96 | 91/96 | 100% | 97.9167% |
| Administrative forms | 20 | 55/96 | 25/96 | 92.7604% | 85.0521% |

## Why the two models differ

The administrative generator has three forms with different lengths, four role pools and independent draws within each typed slot. Observed length identifies the form. Conditional length/slot counts preserve its distinct symbol distributions even when the mixture of forms changes. A stationary transition graph pools those distributions across occurrences. The length/slot decoder sees the observed length and slot, with no supplied pool identities or generator probabilities.

The transition generator instead uses the preceding symbol to choose the next one. Length/slot profiles omit those pairwise distinctions. Graph mapping therefore has higher recovery in that family. At twenty symbols, its 74 recovered conditions compare with zero for the slot method. The paired recovery difference is −77.0833 percentage points for slot minus graph, with an interval of −83.3333 to −70.8333.

The two likelihood objectives have different sufficient statistics. For length/slot mapping, each code-to-reference assignment contributes an independent entry to a linear weight matrix. SciPy's modified Jonker–Volgenant solver maximizes the selected entries. Graph mapping optimizes a quadratic assignment with fixed boundary identities using the preserved multistart/2-opt procedure. [Protocol and implementation source](PROTOCOL.md), [previous graph study](../graph-mapping/FINDINGS.md).

Each selected map was evaluated under both reference models on 400 independently generated records. In twenty-symbol administrative worlds, average slot loss is 2.30977 bits per token for slot-selected maps and 2.35064 for graph-selected maps. Average graph loss is 2.72293 bits per edge for slot-selected maps and 2.71851 for graph-selected maps. A score can prefer its selected mapping while another model recovers more true identities. Per-token and per-edge losses have different denominators and are reported separately.

## Optimization and unresolved identities

At eight symbols, every linear assignment objective was checked against all 40,320 maps. Every condition also has an independent continuous assignment relaxation, a saved dual bound and checked dual inequalities. The largest arithmetic disagreement across all count, likelihood and certificate checks is `8.57 × 10⁻¹⁰`. These computations establish the selected linear score within the declared numerical tolerance.

The independent review forbids each selected code assignment in turn and finds the best alternative. Twenty-three conditions retain a code movable at the optimum within `10⁻⁸` score tolerance. Their alternative maps are preserved. A solver's selected bijection is therefore accompanied by its remaining alternatives. [Every tie check and witness](review/ties.json).

The main grid took 47.37 seconds. Reported assignment solver times average roughly 11–26 microseconds, while graph search averages 13–51 milliseconds by family/inventory. Those timings exclude data acquisition, count construction, verification and exhaustive enumeration. They describe this machine and bounded inventory sizes.

## Reuse

This is a post-outcome model comparison on new generated systems. Linear assignment, slot-conditioned models and graph matching are established methods. The new measurements show how their score families behave under the declared record mechanisms. A useful next test would choose a score family from held-out reference prediction before opening mapping truth. More complex forms with shared lengths, uncertain segmentation or mixed operations would require a broader observation model.
