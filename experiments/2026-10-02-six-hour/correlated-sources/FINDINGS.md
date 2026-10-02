# Copied identity reports and mapping confidence

Ten copies of a mistaken identity report can dominate the statistical evidence for a symbol mapping. In the shifted administrative condition with eight reported identities, the independent-copy treatment recovered the true mapping in 1 of 48 trials and selected a wrong mapping with at least 95% conditional mass in 46. Counting the report once recovered 25 mappings, with 11 confident errors. A source-level swap model recovered 41, with four confident errors. [Complete condition table](review/summary.csv).

The experiment separates two forms of dependence. Derivative reports repeat one source's claim. Within that source, a single transposition changes two identities together. Recording the source once removes the first dependence; modelling its shared error addresses the second. These distinctions matter when several catalogue records or publications inherit one reading.

## Design

We generated 24 new transition systems and 24 administrative-form systems. Each has eight concealed symbol identities, 400 reference records and nested training samples of 40 and 160 records. The administrative systems contain typed slots and mixtures of forms. The transition systems generate ordered Markov sequences. The reference scorer integrates uncertainty in first-order transition probabilities using the frozen CRYPTO-03 method. It enumerates all 40,320 bijections. [Protocol](PROTOCOL.md), [generation and scoring code](../../../src/six_hour/correlated_sources.py).

Source A reports the true identities or a uniformly chosen transposition of two identities. We reveal one, two, four or eight codes in a random order. One, three or ten derivative reports copy that same information. Source B is absent or reports the correct identities on the same codes. The assumed reporting channel is unchanged with probability `1−q` and applies each of the 28 possible swaps with probability `q/28`, for `q=0.1` or `0.5`. Its single-code marginal reports the correct identity with probability `1−q/4` and any particular wrong identity with probability `q/28`.

The four treatments use hard identity constraints, independent per-code errors with every copy counted, independent per-code errors with source A counted once, or the coupled swap channel with source A counted once. Source B enters once. Both source states are deliberately included as stress conditions; their equal representation does not estimate an archaeological error rate. The channel's assumed error probabilities and its support are part of the model.

There are 73,728 condition records over 48 generated systems. A displayed row below contains 48 trials: two training sizes for each of 24 administrative systems. The simulations share reference data and nested training samples within a system. Paired intervals resample the 24 systems after averaging their two training sizes.

## What copying changes

The following results use a 35% change in the administrative process mixture, a swapped source A, all eight reported codes and `q=0.1`. Confident error means a selected wrong map whose normalized conditional mass is at least 0.95.

| Treatment | Copies of A | Correct maps / 48 | Confident errors / 48 | Empty candidate sets / 48 |
|---|---:|---:|---:|---:|
| Hard claims | 1 or 10 | 0 | 48 | 0 |
| Independent copied claims | 1 | 25 | 11 | 0 |
| Independent copied claims | 10 | 1 | 46 | 0 |
| Independent claims, source once | 1 or 10 | 25 | 11 | 0 |
| Coupled source channel | 1 or 10 | 41 | 4 | 0 |

Ten copies increase the independent model's confident-error rate by 72.9 percentage points relative to counting A once. The paired 95% bootstrap interval is 60.4–85.4 points. Relative to the coupled model, the increase is 87.5 points, with interval 77.1–95.8. [Paired comparisons](review/paired-system-comparisons.json).

The effect develops as more claims reveal the source's error. With two reported codes, the independent-copy treatment has one confident error when A is counted once and three with ten copies. With four codes, those counts are five and 21. Some early prefixes never expose either swapped identity, so they agree with the truth even though the full source is wrong.

Counting copies once leaves the three source-once treatments invariant by construction. The observed deterioration comes from changing the copied treatment's likelihood while holding the generated system and reports fixed. Its output approaches the hard-constraint result as the repeated likelihood overwhelms the sequence score.

## Adding a second source

In the same eight-code condition, one correct source B raises recovery to 45/48 for both source-once probabilistic treatments, with no confident errors. Counting ten copies of A alongside B instead yields 3/48 recoveries and 45 confident errors. Hard constraints retain no compatible map in any of the 48 trials because A and B disagree.

The second report is correct in this controlled test. For an actual application, source B's likelihood would come from its acquisition and measurement process. The channel already makes clear where that information enters: source likelihoods are multiplied across independently acquired sources, and copied claims remain attached to their originating source.

## Computation and reuse

An independent calculation rebuilt integrated sequence scores and inverted the reporting channel by enumerating possible source swaps. It replayed 18,432 rows, including conditions from every generated system, and reproduced all selected maps and outcomes. The largest score difference was `5.00×10⁻¹²` bits and the largest mass difference `3.94×10⁻¹³`. All 12 checks passed. [Review checks](review/checks.json), [review code](../../../src/six_hour/review_correlated_sources.py).

Source-dependence modelling has an established literature. Dong, Berti-Equille and Srivastava's *Integrating Conflicting Data: The Role of Source Dependence* studies copied information in data integration. Our experiment supplies a small exact mapping control with a known source-error mechanism. It measures that control's outcomes and provides reusable likelihood code. [Primary paper](https://www.vldb.org/pvldb/vol2/vldb09-pvldb47.pdf).

The next useful application is a provenance graph for candidate numerical or identity claims. Each claim needs its original object, image, author reading and copying links. Alternative readings of one image can contribute measurement evidence under a shared object model. Separately observed quantity relations can provide additional source likelihoods. The experiment gives a way to compare those treatments before fitting a proposed Indus interpretation.
