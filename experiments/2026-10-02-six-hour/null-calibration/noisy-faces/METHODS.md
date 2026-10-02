# Conditional law of the ordered face-vector reference

The synthetic population has two observed faces per latent object. For one slot in a fixed stratum, let the latent code X have distribution p. A face retains X with probability 1−ε and otherwise draws uniformly from the other seven codes. Its observation kernel is

`Kε(a|x) = 1−ε if a=x; ε/7 otherwise`.

Conditional on X, the two face errors are independent. Their ordered sign vector V=(Y1,Y2) therefore has probability

`r(a,b) = Σx p(x) Kε(a|x) Kε(b|x)`.

Different objects supply independent vectors with that same r within the stratum. Each slot has its own p, and the vectors are independent across slots under the declared generator. This is a controlled observation process with ε=.1, rather than an estimated transcription-error model for the archaeological corpus.

Let h(v) count the observed vectors of each type in a length/slot/stratum cell containing n objects. The probability of any labeled arrangement with those counts is `∏v r(v)^h(v)`. Conditioning on h makes that expression constant, so its distinct arrangements are uniform. There are `n!/∏v h(v)!` arrangements. Uniformly permuting the n labeled vectors gives every arrangement `∏v h(v)!` generating permutations. Independent cell permutations consequently sample the exact conditional table law.

The two faces' scalar record counts are also preserved. For code a, the expanded count is

`m(a) = Σv h(v)[1(v1=a)+1(v2=a)]`.

Preserving h fixes m and each face label's marginal count. Physical aliases, record identifiers, lengths and metadata remain attached to the destination object. For every proposed table, the fitting routine then rebuilds its transitive physical/text components, allocates folds and tunes the original models. The fitting statistic is arbitrary for the conditional-law argument, provided the same defined procedure is used for observed and reference tables.

The ordered faces agree at a slot when neither is replaced or when both replacements choose the same alternative. Thus

`P(Y1=Y2) = (1−ε)² + ε²/7 = 142/175` at ε=.1.

The independent slots give whole-string equality probability `(142/175)³`. The audit checks observed equality and replacement counts against the saved latent truth and reports those totals. Fits and references receive the observed records alone.

The finite sampler checks use four labeled objects. With four distinct binary face vectors there are 24 distinct columns and 13,824 three-slot tables, each with one generating permutation per column. With two copies each of vectors 00 and 11 there are six columns and 216 tables, each with four generating permutations per column. The independent audit verifies every table probability and replays all 200,000 sampled tables through a separately implemented shuffle. [Finite output](exact/results.json), [verification](verification_exact.json).

The main source uses the corrected disjoint namespaces in [MAIN_BUDGET.md](MAIN_BUDGET.md). The original pilot and finite-sampler snapshots remain available with their hashes. [The shared related-work note](../RELATED-WORK.md) links this reference to established repeated-measurement block permutation.
