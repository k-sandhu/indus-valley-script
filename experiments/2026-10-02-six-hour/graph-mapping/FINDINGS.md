# Mapping search and the score it optimizes

The multistart graph search reached the exact global score in 190 of 192 eight-symbol conditions. It recovered the generating identity map in 186. Four globally optimal maps differed from the truth, while two additional conditions retained optimization gaps. The saved cases separate a search failure from a statistical objective that prefers the wrong correspondence. [Review and case identifiers](review/checks.json).

The method also searched twenty-symbol maps. It recovered every identity in 70 of 96 transition conditions and 20 of 96 administrative-form conditions. Average symbol accuracy was 86.6% and 80.6% respectively. These larger conditions have no exhaustive global certificate. [Complete summary](review/summary.csv).

## From transitions to graph matching

For each short record, we count directed transitions, including a start and an end node. The reference supplies initial and successor probabilities with one pseudocount per category. A bijection maps the concealed codes to reference symbols, while the boundary nodes stay fixed. Its log likelihood is the sum of training edge counts multiplied by the corresponding reference log probabilities. This is a quadratic assignment problem.

We used SciPy's FAQ solver, which relaxes a permutation to a doubly stochastic matrix before projecting it back to a bijection. Its search can depend on the initial matrix. A frequency-based linear assignment supplies one starting point; the uniform barycenter supplies another. The multistart procedure includes these and ten randomized starts, refines each with 2-opt, and chooses the best training score from all retained candidates. [Protocol](PROTOCOL.md), [code](../../../src/six_hour/graph_mapping.py). FAQ and this refinement route are established methods. [Vogelstein et al.](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0121002), [SciPy implementation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.quadratic_assignment.html).

The grid contains 48 new generated systems, inventory sizes eight and twenty, reference samples of 40 and 400 records, training samples of 160 and 640 records, and process changes zero and 0.35. Transition controls generate variable-length Markov records. Administrative controls use three typed-slot forms. Each table row below averages eight repeated conditions within each of 12 generated systems, giving 96 conditions. The algorithms share the same input for every comparison.

## Recovery and optimization

| Family | Symbols | Method | Complete recovery / 96 | Mean symbol accuracy | Global optimum / 96 |
|---|---:|---|---:|---:|---:|
| Transition | 8 | Frequency assignment | 9 | 49.1% | 9 |
| Transition | 8 | FAQ barycenter | 61 | 78.9% | 63 |
| Transition | 8 | FAQ frequency start | 68 | 83.2% | 67 |
| Transition | 8 | Multistart and 2-opt | 90 | 97.4% | 94 |
| Administrative forms | 8 | Frequency assignment | 22 | 61.7% | 22 |
| Administrative forms | 8 | FAQ barycenter | 95 | 99.7% | 95 |
| Administrative forms | 8 | FAQ frequency start | 89 | 96.6% | 89 |
| Administrative forms | 8 | Multistart and 2-opt | 96 | 100% | 96 |
| Transition | 20 | FAQ barycenter | 39 | 60.3% | unavailable |
| Transition | 20 | Multistart and 2-opt | 70 | 86.6% | unavailable |
| Administrative forms | 20 | FAQ barycenter | 19 | 80.1% | unavailable |
| Administrative forms | 20 | Multistart and 2-opt | 20 | 80.6% | unavailable |

Multistart increased transition-family complete recovery over the barycenter by 30.2 percentage points for eight symbols and 32.3 points for twenty. Paired 95% bootstrap intervals, resampling the 12 systems after averaging their repeated conditions, are 15.6–45.8 and 19.8–44.8 points. The administrative increases were 1.0 point in both inventories, with intervals 0–3.1. [Paired system comparisons](review/paired-system-comparisons.json).

The two remaining eight-symbol search failures come from one transition system under process change 0.35. Their gaps are 40.27 and 346.36 bits at training sizes 160 and 640. The four conditions whose optimum excludes truth occur in two other shifted transition systems. These exact cases are useful regression inputs for a new optimizer or scoring model.

Held-out records provide a separate comparison. For transition controls, mean loss per edge fell from 2.774 to 2.645 bits between barycenter FAQ and multistart at eight symbols, and from 3.945 to 3.820 at twenty. Administrative twenty-symbol loss changed from 2.762 to 2.759. Training-score dominance follows from retaining the baseline candidates; improved held-out loss and identity recovery are measured outcomes.

The complete grid ran in about 42 seconds on the recorded local environment, including generation and eight-symbol enumeration. Mean multistart search time per condition was 13–66 milliseconds across family/inventory groups. This timing concerns the small declared benchmark. It does not estimate search time for a full Indus signary.

## Checks and next use

The review rebuilt all 384 reference, training and held-out count matrices through independent edge counters, checked every returned bijection and boundary match, and recomputed all 1,536 scores and outcome fields. A flattened matrix product independently enumerated the 192 small-condition maxima. All ten checks passed; the largest score discrepancy was `3.64×10⁻¹¹` bits. [Review code](../../../src/six_hour/review_graph_mapping.py).

The code supplies a scalable search component for a declared reference model. An Indus application would need that reference and a justified correspondence class: a sign-to-sound mapping, a numerical relation or a documented administrative code. The control shows how to report candidate-search quality separately from the evidence supporting the selected map. A next computational change should target the two exact failures, test a new score on fresh systems, or supply an additional independently acquired relation.
