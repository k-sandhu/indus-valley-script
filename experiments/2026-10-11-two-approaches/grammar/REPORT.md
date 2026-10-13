# Learned classes, record fields and compositional predictions

A learned class grammar improves prediction over a positional baseline, but its standalone probability loss is worse than a tuned sign-level Markov model. A later exploratory repair mixes the two predictors. That mixture gains **0.0557 bits per token** over an equally tuned Markov-plus-position mixture, with a conditional component-bootstrap interval of **0.0436–0.0675**. The useful result is a small contribution from shared sign classes alongside specific sign transitions. The original grammar failure remains the primary frozen outcome.

The work develops Rao, Yadav and Vahia's recommendation to infer a stochastic grammar from inscriptions. The package contains fitted classes, explicit productions, structured rival mechanisms, a frozen prefix predictor and hypotheses for later physical/context tests. All outcomes concern graphic code sequences in one derivative corpus. Proposed record functions below are hypotheses; the model supplies no authenticated sounds, meanings or language identification.

## What was carried forward from previous research

[Rao et al. (2009)](https://homes.cs.washington.edu/~rao/PNASIndus.pdf), Discussion, printed p. 13690/PDF page 6, propose direct machine-learning grammar induction. [Yadav et al.](https://arxiv.org/abs/0901.3017) connect context classes and a stochastic grammar. [Tiwari (2026)](https://aclanthology.org/2026.nlp4dh-1.28.pdf), sections 4.7 and 5.4, already fits a categorical HMM and interprets positional latent states. The earlier repository also fitted mixtures of independent slots, which did not match its sequential predictor. This package therefore contributes a different grouped predictive comparison and a checked backoff extension, without claiming the first grammar or first sign classes.

The [source ledger](sources.json) gives reading depth, locators, pins and rights handling. The companion [literature census](../literature/LANDSCAPE.md) covers segmentation, contextual classes and other recent field grammars in greater detail. Numeric codes retain the repository's documented right-to-left reading order; labels from a source using another serialization convention cannot be transported directly.

## Population, model and probability law

The [pre-outcome protocol](PROTOCOL.md) fixes the population and model grids. Physical-family and identical nonempty string links were joined across **all 5,680 observed faces before filtering**. Retained analysis uses **1,596 distinct complete, clear, single-line texts**, length 3–13, with **8,009 code tokens** and 548 graphic types. Every duplicate text keeps its object aliases. Five outer and three inner folds respect the full transitive closure; only inner predictions select configurations.

This graph has 1,363 analysis components. One component contains 180 texts and 688 tokens, 8.59% of the benchmark. Its size reflects short-text and physical-object bridges as well as deliberately conservative equality of placeholder-bearing strings. Omitting only placeholder string edges in a graph census leaves 1,369 eligible components and a174-text largest component. The primary fits retain the declared larger graph. Token-weight concentration gives an effective component count of 123.1 under `(sum weights)^2 / sum(weights^2)`. The reported intervals resample components with fitted models and folds held fixed; they do not include renewed model selection or source-transcription uncertainty. [Census](run-v1/manifest.json), [component diagnostic](post-outcome-diagnostics.json).

Each fit builds its output alphabet from training codes plus one UNKNOWN bucket. Thus likelihood is the probability of the **mapped alphabet sequence conditional on its observed length**. All distinct original codes absent from that fit map to the same UNKNOWN event. The 257 OOV tokens, 3.21%, cannot receive probabilities as separate unseen graphic identities. All comparator families share the same fitted alphabet and OOV mapping. No end factor is appended: every successive next-code distribution sums to one for a given length.

The grammar learns a distribution of signs for each hidden class and a distribution of class-to-class transitions. In the selected contextual variant, length and slot index alter the class transition probabilities while sign emissions remain shared across lengths. Its sequence probability sums over every class path:

`P(c1…cL | L) = sum_q pi_L(q1) E(q1,c1) product_j A_(L,j)(q[j-1],qj) E(qj,cj)`.

This is a weighted finite-state grammar. A class can recur, several classes can emit the same code, and the score at a position uses the prefix and length only. Posterior class labels and Viterbi paths are descriptive analyses of complete training texts; they are not used to give the predictor access to future targets. [Reusable implementation](grammar.py), [explicit state-path and normalization tests](run-v1/self-tests.json).

## Frozen grammar result and exploratory backoff repair

Lower cross-entropy is better. The first three rows belong to the original protocol; the last two were constructed after those outcomes were seen.

| Predictor | Bits per token | Status |
|---|---:|---|
| Position and length |6.5884|Frozen run-v1 comparator|
| Tuned first/second-order Markov with positional adjustment |5.8246|Frozen run-v1 comparator|
| Learned class grammar |6.2972|Frozen run-v1 method|
| Markov plus position |5.7691|Post-outcome matched backoff control|
| Markov plus class grammar |5.7134|Post-outcome class backoff method|

The standalone grammar gains 0.2912 bits over position, interval 0.2512–0.3313, and loses 0.4726 bits against Markov, interval−0.5161 to−0.4264. It loses in every outer fold. All five folds select 12 contextual states with emission strength 20, the largest state count in the declared grid. Twelve is a selected capacity setting, not an estimated archaeological inventory of twelve functions. [Primary results](run-v1/results.json).

The registered unseen-bigram stratum explains the repair's motivation. For 1,942 noninitial known targets whose exact bigram was absent from training, losses are 7.8322 for position,9.1518 for Markov and 8.2365 for the grammar. Class sharing partly repairs sparse transition prediction, while position remains the best of these three on that stratum. On 4,312 known targets in seen bigrams, Markov scores 3.2611 and grammar 4.4926. Both parts of this comparison are needed: the stratum result does not overturn the grammar's pooled failure.

The [post-outcome protocol](POST-OUTCOME-PROTOCOL.md) fixes a convex probability mixture and eight allowed weights, including zero. Its weight depends on inner validation likelihood, without a gate that inspects the actual outer target. The [matched-control amendment](AMENDMENT-V3.md) applies the same grid and alphabet to Markov-plus-position. The original primary endpoint is unchanged.

| Comparison, positive favors class mixture |Bits per token|Conditional 95% interval|
|---|---:|---:|
|Markov loss minus class-mixture loss|0.1113|0.0972–0.1268|
|Position-mixture loss minus class-mixture loss|0.0557|0.0436–0.0675|
|Position-mixture loss minus class-mixture loss, equal-text weighting|0.0568|Point sensitivity|
|Position-mixture loss minus class-mixture loss, noninitial tokens|0.0349|Point sensitivity|

The class mixture beats the position mixture in every fold, with gains 0.0601, 0.0752, 0.0634, 0.0388 and 0.0411. The selected class weights are 0.2, 0.3, 0.3, 0.2 and 0.2; position weights are 0.2, 0.2, 0.2, 0.2 and 0.1. The class increment is 0.0760 on 7,752 known target tokens and−0.5569 on 257 OOV-bucket targets. Its present benefit is stronger representation of known codes, with weaker unknown-bucket calibration. Removing the largest component from the saved predictions, without refitting, gives a0.0551-bit class increment over positional backoff. [Matched results and strata](run-v3-matched-mixtures/results.json), [fixed-prediction sensitivity](post-outcome-diagnostics.json).

These are exploratory results on outer outcomes exposed before the mixture family was proposed. A later unseen corpus must use the saved recipe without retuning to test whether the increment transfers.

## The learned field inventory

The full-data descriptive grammar uses a configuration chosen by pooled inner scores, without selecting on outer loss. Classes below are ordered by their mean position. Listed codes are the highest-probability emissions; they are not exhaustive memberships or equivalent meanings. Initial/internal/final shares are posterior occupancy fractions. [Full class and production inventory](run-v1/learned-grammar.json).

|Class|Leading graphic codes|Initial / internal / final occupancy|Working structural description|
|---|---|---|---|
|C01|817,820,861,920|96.5% /2.0% /1.5%|Concentrated opening family|
|C02|032,031,235,240|85.6% /14.0% /0.4%|Broad early family|
|C03|032,590,125,575|73.8% /24.9% /1.3%|Alternative early family|
|C04|235,240,705,032|27.0% /71.4% /1.7%|Repeatable early core|
|C05|002,060,741,001|0.0% /97.7% /2.3%|Concentrated internal linker family|
|C06|861,390,368,220|0.0% /90.9% /9.1%|Broad internal family|
|C07|033,240,590,220|1.3% /96.0% /2.7%|Middle core|
|C08|003,004,550,806|4.9% /86.4% /8.7%|Alternative late core|
|C09|100,760,032,390|0.3% /96.5% /3.2%|Late core|
|C10|400,090,001,679|0.5% /32.8% /66.7%|Late attachment family|
|C11|390,407,527,617|0.5% /25.1% /74.3%|Alternative completion family|
|C12|740,520,151,700|0.0% /27.6% /72.4%|Concentrated completion family|

C01 assigns about 55.0% of its emission mass jointly to 817/820/861. C05 assigns 50.7% to 002 and 16.4% to 060. C12 assigns 73.7% to 740 and 12.7% to 520. Some broad middle classes share codes; for example 032 appears among four leading inventories. This supports a context-dependent class representation rather than one fixed class for each sign.

The most frequent coarse production is `C02 C09 C12`, with 100 descriptive texts. `C01 C05 C07 C09 C12` has 92, and `C02 C08 C11` has 74. The paths `C01 C05 C04 C07 C09 C12` and `C01 C05 C08 C11` have 73 and 72. Repeated C04 appears in `C04 C04 C07 C09 C12` and `C01 C05 C04 C04 C07 C09 C12`, with 30 and 28 texts. These suggest alternative core-to-completion routes and optional repetition. The counts describe Viterbi segmentations of the training population.

Cross-fold emission alignment has mean Jensen–Shannon divergence 0.205–0.285 bits. Matched top-six emission overlap averages 51.4–63.9%. Opening 817/820/861, internal 002/060 and completion 740/520 families recur, while several broad intermediate classes split or exchange signs. The evidence supports recurring anchors more clearly than every twelve-way class boundary. [Stability audit](run-v1/classes-stability.json).

## A compositional theory worth testing

One useful hypothesis is **completion of a field followed by an optional late attachment**. C12 often precedes C10: coarse paths `C02 C12 C10` and `C02 C09 C12 C10` occur 59 and 38 times. A selected post-outcome code audit finds 245 internal occurrences of 740 and 607 final occurrences. The sequences 740→400 and 740→090 supply 73 and 66 edges, with the right code final in 72 and 60 cases. 520→400 supplies seven further edges, all ending the text. Thus a frequent completion graphic can participate in a larger construction with an added tail. These counts are aggregate observations selected after examining the learned classes, without a significance or novelty claim. [Selected-code diagnostic](post-outcome-diagnostics.json).

In a **typed administrative record**, the opening family could set an issuer or record namespace, the C05 family could introduce a value or relation, the central classes could specify entities and qualifiers, and a C12-like marker could complete that reference. A C10 tail could then apply an operation, authorization or account category to the completed field. This predicts that the tail varies with document use while the preceding entity/value remains stable within physical issuing groups. Independently joined sealings, container marks and manufacturing cohorts could test that relationship.

In a **compound name or title construction**, the same completion marker could be a head or category term, with the later tail a grammatical ending or postposed title element. This predicts parallel tails across unrelated semantic categories and stable modification of compound heads, rather than restriction to one commodity or container function. A fixed phonetic proposal would need additional independent correspondences; the class grammar alone does not choose a language.

A **mixed notation** could combine conventional names or titles with logographic account fields. On that account, class-sharing should be strongest in the field material, while sign-specific transitions retain information inside names. The mixture result makes this division worth testing, although a wholly conventional emblem system also produces it. Distinguishing these scenarios requires the relationship between inscription structure and object use, find context, repeated issuing groups or independently measured contents. The [future prediction sheet](FUTURE-PREDICTIONS.md) freezes practical tests and their failure conditions.

## Structured rivals and specificity

The synthetic controls have optional opening/qualifier fields, a repeatable middle class and a final class, with identical code emissions under two semantic accounts. Administrative fields and a compositional clause interpretation are independent realizations of the same generator. The labels in both controls are invented. In all six held-out runs the learned grammar beats Markov by 0.276–0.348 bits per token. All select eight contextual states with emission strength 5. The original grammar's capacity to recover reusable fields therefore appears under both constructed accounts. [Controls, seeds and full mechanism](run-v1/structured-controls.json).

The exact semantic twin uses the same generated code rows under either account. Relabelling the hidden fields changes no probability factor, so the sequence likelihood ratio is 1 for every sequence. This is an explicit nonidentifiability witness: an inferred compositional grammar cannot select semantic labels when rival accounts share its observation law. It carries forward the specificity issue developed by [Raghavendra (2026)](https://arxiv.org/html/2608.02999v1). The synthetic mechanism is illustrative and is not a matched reconstruction of the entire Indus distribution. The totem and weather limitations are retained in the retrospective.

## Verification and reuse

The [verification script](verify.py) independently replays all 8,009 grammar forward token scores from saved arrays, checks alphabet construction and OOV flags, reproduces aggregate losses and verifies hashes and split separation. Its largest saved-score difference is 3.55×10^-15 bits. Toy enumeration checks probability sums at lengths 1–4 and explicit hidden-state path sums. The post-outcome audit reproduces every outer mixture score exactly. [Primary verification](run-v1/verification.json), [mixture audit](post-outcome-diagnostics.json). The companion reviewer independently rebuilds positional probabilities and checks mixture selection in [57 review checks](../review/mixture-checks-v1.json).

The [carry-forward manifest](carry-forward.json) freezes twelve contextual classes, second-order Markov strength 20 with positional exponent 0.5, positional strength 100 and both mixture weights 0.2. The full class arrays and all rows/predictions remain local-only under `data/raw/2026-10-11-two-approaches/grammar/`. Public or private Git contains code, protocols, aggregate results and hashes, rather than reconstructible bulk input.

Use [predict.py](predict.py) to inspect the normalized prediction from a specified prefix and assumed length. The command reads the pinned local source and arrays; it never receives a future target. [README](README.md) gives manual commands, and [retrospective](RETROSPECTIVE.md) records the choices, review-driven controls and limits. No repository-wide file, publication setting, CI/CD workflow or automation was changed by this package.
