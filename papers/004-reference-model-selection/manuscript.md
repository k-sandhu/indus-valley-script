# Choosing record models before symbolic mapping: reference-conditioned recovery controls

Complete private working manuscript, 2 October 2026. Authorship, affiliations and venue are pending. Computational work and writing used AI assistance. Protocols, generated worlds, source snapshots, independent reviews and all outcomes are preserved in the private repository.

## Abstract

Recovering a bijection between two symbol inventories depends on the distinctions retained by the reference model. We compare boundary-seeded graph mapping with linear assignment of record-length/slot profiles on generated short records. In a first grid of 48 new systems, length/slot assignment recovers 55 of 96 twenty-symbol administrative mappings, compared with graph mapping's 25; graph mapping recovers 74 of 96 twenty-symbol transition mappings, compared with zero for slot profiles. A second fresh grid chooses the score family using three-fold held-out reference likelihood before mapping truth is opened. Both likelihoods condition on the observed record length; the graph model includes its exact length normalizer. The selected decoder recovers 46 of 96 twenty-symbol administrative maps and 76 of 96 transition maps, matching the supplied-family diagnostic in both. At eight symbols it loses one recovery relative to that diagnostic. Independent counts, likelihoods, small-inventory enumeration and assignment dual bounds accompany the first grid. The second audit checks every reference choice, likelihood and dual bound, and certifies exact likelihood ties. The result supplies a known-system control for selecting a record model from available reference observations, with the external reference and inventory correspondence kept explicit.

## 1. A mapping search needs a record model

A frequency profile, a transition graph and a position-specific form preserve different information. They can each be transformed by a symbol bijection and compared with a reference population. A search succeeds when the retained information distinguishes the true assignment and the optimizer finds it. Those are separate empirical questions.

The project earlier enumerated eight-symbol maps under reference uncertainty, erroneous supplied identities and changes in record mixture. A subsequent graph-mapping experiment scaled the search to twenty symbols and checked eight-symbol optima exhaustively. It exposed both optimization gaps and training objectives that preferred wrong identities. [Reference experiment](../../experiments/2026-10-02-six-hour/reference-uncertainty/FINDINGS.md), [graph search](../../experiments/2026-10-02-six-hour/graph-mapping/FINDINGS.md).

This study follows one observed difficulty: twenty-symbol administrative mappings often had high average symbol accuracy but low complete recovery under the pooled transition objective. The generated records had typed slots and forms with distinct lengths. We therefore specified a model retaining length and slot, then tested whether the reference population could choose between that model and a transition model. Both stages use fresh generated systems after their respective protocols.

Linear assignment, graph matching and held-out model selection are established methods. The graph search uses the FAQ and 2-opt implementations; the assignment uses SciPy's modified Jonker–Volgenant solver. Neural decipherment work also uses matching or flow constraints with known-system evaluation. These precedents provide algorithms and evaluation principles. The present contribution is a matched recovery comparison, a reference-only selection procedure and preserved optimization/identity failures under declared short-record mechanisms. [FAQ primary article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0121002), [assignment implementation](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.linear_sum_assignment.html), [Luo, Cao and Barzilay 2019](https://aclanthology.org/P19-1303/).

## 2. Data and methods

### 2.1 Known systems and withheld identities

Each grid has twelve systems in each combination of two generator families and inventories of eight or twenty symbols. A transition family draws a start distribution and transition rows from Dirichlet distributions, then generates records of length three through eight. An administrative family has four disjoint symbol pools and three forms of lengths four, five and six. Each form draws independent symbols from its typed slot distributions. Form probabilities vary across generated systems.

A random bijection encodes the training and test identities. The reference remains in its original category names. Reference sizes are 40 and 400 records; encoded training sizes are 160 and 640. Each system contributes a baseline process and a .35 change. For transition records, the change mixes a shifted start distribution and a shifted successor distribution into each row. For administrative records, it changes the mixture of forms while retaining their slot distributions. Four hundred independently generated encoded records supply the test set for each change condition.

The two sample sizes and two changes yield eight conditions per system, or 384 per grid. Systems are the resampling units; repeated conditions remain together. The first grid uses seed 810261002 with declared inventory/family/replicate offsets. The selector grid uses fresh seed 910261002 and the same offset design. Generated records and hidden maps are retained; source snapshots, seeds and library versions reconstruct the generator parameters. [First protocol](../../experiments/2026-10-02-six-hour/slot-mapping/PROTOCOL.md), [selector protocol](../../experiments/2026-10-02-six-hour/reference-selector/PROTOCOL.md).

### 2.2 Two mapping objectives

For length/slot mapping, estimate each reference cell distribution with one pseudocount per symbol. An absent cell is uniform. Let `C[L,j,c]` count encoded training code `c` at slot `j` in records of length `L`. The assignment weight for mapping code `c` to reference symbol `r` is `W[c,r]=Σ C[L,j,c] log₂ q(r|L,j)`. Maximizing the sum of selected weights is a linear assignment. The decoder receives observed lengths, slots and the common inventory size, while hidden role pools and true identities remain in evaluation.

The graph objective sums encoded transition counts multiplied by reference log probabilities after a bijection. Fixed start/end matches include boundary likelihoods. Each glyph row has one pseudocount for each of the `k` glyph destinations and END; the start row has one per glyph. The comparator retains two deterministic FAQ initializations, ten randomized starts and 2-opt refinements, then chooses the largest training score across all refined and unrefined candidates. Solver seeds are declared by condition. The slot and graph decoders use the same records and inventory.

In the first grid, enumeration of all 40,320 eight-symbol bijections verifies the linear maximum. At every inventory size, a separate continuous assignment relaxation provides a dual bound and inequalities checked against the selected score. The independent reviewer forbids each selected code match in turn to find tied alternative assignments. Numerical equality uses a declared `10⁻⁸` score tolerance; the dual checks use `10⁻⁷`. The selector grid has separate dual programs and exact prime-factor certificates for retained alternative maps.

### 2.3 Select the model from reference prediction

The second grid assigns known-reference records to three random folds using seed `system seed + 50`. Each model fits on two folds and scores the third. The selector receives only reference records, inventory size and that seed. It receives no generator family, encoded test records, mapping answer or hidden probabilities.

Both scores are probabilities for an entire record conditional on its observed length. The slot model multiplies its cell probabilities. The first-order model multiplies start, interior transitions and end, then divides by its probability of the specified length. If `π` is its start row, `A` its glyph-to-glyph transition matrix and `e` its end-probability column, that normalizer is `π A^(L−1) e`. It puts both models on the same conditional sequence space. A tiny fully enumerated sequence space checks that each conditional distribution sums to one.

Choose the model with the larger pooled held-out reference log score; ties choose graph. Then fit both mapping methods on the full reference and encoded training sample, and retain the chosen map. Mapping accuracy is opened only in evaluation. A supplied-family diagnostic selects slot for administrative records and graph for transition records. That diagnostic uses the known generator family; it measures the cost of reference-only selection in this design.

### 2.4 Outcomes and uncertainty

Report complete identity recovery, the fraction of symbols correctly mapped and optimal-score ties. A correct returned map is scored as point recovery; tied compatible maps are reported separately. In the selector grid, each test record is scored under both conditional reference models using the same selected map and a common token denominator. Their conditional whole-record likelihoods can be compared. The first grid retains unconditional graph loss per edge and conditional slot loss per token; those scores and denominators remain separate.

Twenty thousand bootstrap draws resample the twelve systems within a family/inventory, after averaging the eight repeated conditions within each system. Intervals describe the generated design and chosen fitting procedure. Model-development decisions followed preceding outcomes, while each new grid had fresh systems and a pre-generation protocol.

## 3. Results

### 3.1 Profiles improve administrative mapping

| Family | Symbols | Slot: complete maps | Graph: complete maps | Slot: symbol accuracy | Graph: symbol accuracy |
|---|---:|---:|---:|---:|---:|
| Transition | 8 | 21/96 | 90/96 | 60.16% | 98.31% |
| Transition | 20 | 0/96 | 74/96 | 24.43% | 89.27% |
| Administrative forms | 8 | 96/96 | 91/96 | 100% | 97.92% |
| Administrative forms | 20 | 55/96 | 25/96 | 92.76% | 85.05% |

The twenty-symbol administrative recovery difference is 31.25 percentage points, interval 21.875–41.667. Its symbol-accuracy difference is 7.7083 points, interval 4.5833–11.1458. For twenty-symbol transition records, slot minus graph recovery is −77.0833 points, interval −83.3333 to −70.8333. [Frozen results](../../experiments/2026-10-02-six-hour/slot-mapping/main/results.json), [paired summaries](../../experiments/2026-10-02-six-hour/slot-mapping/review/summary.json).

The administrative forms have different observed lengths. Conditioning on length retains the form-specific slots while changes in form frequency alter pooled statistics. The transition model instead needs the current symbol to predict its successor. Slot profiles discard that pairwise relation. These outcomes follow the supplied mechanisms and identify the observations each score uses.

All linear optima pass enumeration or dual-bound checks. Twenty-three conditions retain at least one code movable at the same optimum within tolerance. Alternative maps remain in the output. The largest independent numerical disagreement is `8.57 × 10⁻¹⁰`. The grid took 47.37 seconds, including both mapping methods and exact/dual checks. [Independent verification and tied maps](../../experiments/2026-10-02-six-hour/slot-mapping/review/verification.json).

### 3.2 Reference-only selection on fresh systems

| Family | Symbols | Reference-selected | Fixed slot | Fixed graph | Supplied-family diagnostic |
|---|---:|---:|---:|---:|---:|
| Transition | 8 | 92/96 | 26/96 | 92/96 | 92/96 |
| Transition | 20 | 76/96 | 0/96 | 76/96 | 76/96 |
| Administrative forms | 8 | 95/96 | 96/96 | 94/96 | 96/96 |
| Administrative forms | 20 | 46/96 | 46/96 | 21/96 | 46/96 |

The reference selector chooses graph for every transition reference and slot for every twenty-symbol administrative reference. At eight administrative symbols, it chooses slot in six of twelve forty-record references and all twelve four-hundred-record references. The six small-sample graph choices produce one fewer complete recovery than the supplied-family diagnostic. The selected decoder recovers 309 of all 384 conditions; the diagnostic recovers 310. [Fresh-world endpoint](../../experiments/2026-10-02-six-hour/reference-selector/main/results.json).

The twenty-symbol administrative selector-minus-graph recovery difference is 26.04 percentage points, with a paired twelve-system interval of 14.58–38.54. Its eight-symbol administrative difference from fixed slot is −1.04 points, interval −3.13–0.00. The exact assignment audit retains eleven slot-tie conditions and 32 equality witnesses. Five tied administrative conditions enter the selected outputs. [Independent report](../../experiments/2026-10-02-six-hour/reference-selector/review/REPORT.md), [paired comparisons](../../experiments/2026-10-02-six-hour/reference-selector/review/additional-v1/paired-comparisons.json).

The fresh selector grid has its own fixed-method comparison. It retains the graph's transition recovery and the slot model's twenty-symbol administrative recovery without receiving the family label. Its outcomes are evaluated on the new systems saved with that grid.

## 4. What this supplies for an unfamiliar script

The study starts with an external reference whose symbols and record process are known. The inventory correspondence is a bijection, record boundaries and length are observed, and generator changes have a declared form. Those premises define the current recovery problem. An Indus application would need an independently justified reference or functional observation, plus a model for graphic identity, segmentation and mixtures. The current experiment supplies a way to test those model choices on a known control before investing in an archaeological mapping.

The most useful observation can be the record's form or physical role. Here an observable length preserves an administrative form, and held-out reference prediction chooses the associated score. In other collections, a container class, face role, operational stage or measured quantity could provide the conditioning variable. Its source must be recorded separately from the symbolic mapping so its predictive value can be checked.

Future controls should include several forms with the same length, overlapping role inventories and uncertain record boundaries. Those designs would measure where the current slot conditioning loses the information that made this example tractable. An acquired reference or object relation can then replace a declared generator premise in a new experiment.

## 5. Verification and availability

The first grid's independent implementation rebuilds every cell count and profile weight, checks all training/test likelihoods and answer-key comparisons, reenumerates eight-symbol optima, verifies dual inequalities and retains all code-exclusion alternatives. The selector review passes 6,489 checks: every fold and choice, all 1,536 returned-row likelihoods, 384 independent slot dual programs and exact conditional mass at lengths one through four. Its state-vector recursion independently reconstructs the graph length normalizer. Prime-factor cancellation certifies 32 alternative likelihood equalities across eleven tied slot conditions. The failed first pilot is retained: a NumPy boolean prevented JSON serialization after fitting, and a Python-boolean conversion allowed the deterministic pilot to complete into a new endpoint.

Code, generated inputs, hashes, protocols, outcomes and retrospectives are project artifacts in the private repository. [Methods and claim files](methods.md) give exact paths. Primary literature provides the existing algorithm precedents. New source observations and future trials should retain the current endpoints and state the changed premise before execution.
