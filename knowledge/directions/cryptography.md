# Cryptography as an experimental framing

Research direction and synthetic test, updated October 2, 2026.

## Recent model-assisted cipher work

Frode Weierud's primary archive account, updated September 24, 2026, validates the key and plaintext for the 82-letter MVUEH Enigma message after Carter Leffen supplied an AI-assisted break. The account describes selection of a promising message, comparison with a previously solved related message, a repeated place-name crib, generated simulator/search software, and discovery of transcription problems. It also records archival leads whose original message image remained unlocated. Its validation depended on a known encoding, German plaintext and a related message. We did not independently reproduce the break. [Primary account](https://www.cryptocellar.org/bgac/the-mvueh-break.html).

The July 2026 *CryptanalysisBench* preprint reports 191 tasks and model-produced attacks, including a SpoC design flaw and a KINDI proof flaw. It separates design-level attacks, implementation problems and successes on weakened variants. Its useful methodological lesson here is automatic verification against an explicit reference problem, with success categories kept distinct. [Authors' paper, v2](https://arxiv.org/abs/2607.18538v2).

A Vals AI August 31 report proposes a book-index solution to Urquhart's Cyphral Distich, with counting and source caveats. [Original report](https://www.vals.ai/blogs/fable-solves-cyphral-distich). A September 1 replication report challenges the solution against a specific 1653 witness. [Replication attempt](https://github.com/reticuli-labs/panel-artifacts/blob/main/distich-refutation-2026-09-01/FINDINGS.md). Later discussion identifies possible copy-specific differences and incomplete physical verification. [Schneier's update and comments](https://www.schneier.com/blog/archives/2026/09/claude-fable-solves-a-historical-cipher.html). Resolving this dispute requires choosing the physical witness and reproducing the proposed coordinates against it.

The Enigma account was updated September 24; the benchmark's current version is dated July 29. These are the strongest relevant sources found in the October 2 search.

## Which features transfer to Indus research?

The useful transfer is a workflow: select tractable targets, reconstruct the generative process, seek independent anchors, represent uncertain transcription, and implement searches with checkable outcomes. A promising result would then be tested on unselected objects. This approach can investigate an ordinary writing or administrative system as well as an intentional cipher.

| Cryptanalytic tool | Possible Indus adaptation | Required evidence and control |
|---|---|---|
| Frequency, repeated strings and n-grams | Graphic constraints and candidate segmentation | Physical/text alias control and metadata baselines |
| Related-message comparison | Paired faces, recurring sealings, administrative archives | Source photographs and context establish the physical relation before comparing strings |
| Cribs | Candidate commodity, recipient, place or count anchored by external records | Independent archaeological justification, competing anchors and held-out predictions |
| Error-tolerant decoding | Candidate-set transcription and damage channels | Frozen photo labels, explicit uncertainty/OOV cases and count uncertainty |
| Constraint satisfaction / minimum-cost matching | Joint graph-to-role or candidate-language mapping | Measure equivalence classes and sensitivity to anchors; include nonlinguistic controls and adversarially wrong comparators |
| Key verification | Predicted observations on untouched artifacts | Graphic and contextual accuracy is initially checkable; historical lexical meanings require independent anchors |

Neural decipherment research offers minimum-cost flow and related-language matching, evaluated on Ugaritic and Linear B. [Luo, Cao and Barzilay 2019](https://aclanthology.org/P19-1303/). Later work jointly models segmentation and cognate alignment using phonetic constraints. [Luo and colleagues 2021](https://aclanthology.org/2021.tacl-1.5/). An Indus application would need to test the choice of related-language comparator, segmentation and phonetic assumptions. The known-system benchmark below would let us study those requirements first.

## An identifiability obstacle we can test exactly

Let `x` be the observed sign sequence and let `pi` be any bijection of sign names. If a model and its sufficient statistics are relabelled consistently, the probability of `pi(x)` is the same as that of `x`. The transition table and graph change their names, not their topology. A score trained solely on the observed corpus cannot choose between arbitrary semantic labellings from that invariance alone.

Geometry, verified quantities, known languages, archaeological context and bilinguals supply additional constraints that may break these symmetries. A fixed external reference can therefore distinguish mappings that an internally refitted model scores equally.

We implemented [an exact six-symbol demonstration](../../experiments/2026-10-02-cryptography-framing/README.md): all 720 relabellings preserve the fitted Markov score, entropy and count graph when the model is transformed consistently. Two fixed symbol identities reduce the remaining maps to 24. This gives the next benchmark a measurable target: how much each independently supplied anchor reduces the mapping ambiguity.

## Mapping benchmark and its next extensions

**CRYPTO-02, completed synthetic grid.** The first concrete benchmark uses eight-symbol transition and administrative-form generators. It supplies a separately sampled known reference and enumerates all anchor-compatible mappings of short encoded records. [Protocol and findings](../../experiments/2026-10-02-six-hour/anchor-benchmark/FINDINGS.md). Under unchanged transition processes, Markov scoring recovered all 12 mappings in each declared condition. Under a changed administrative process, recovery fell and some wrong maps received more than 95% conditional model mass. Held-out preference for the correct reference frequently persisted in those failures.

**CRYPTO-03, finite reference and erroneous identities.** The [next grid](../../experiments/2026-10-02-six-hour/reference-uncertainty/FINDINGS.md) varies reference size, training size and one erroneous supplied identity. Its 2,592 trials use 24 new systems. Integrating reference parameters reduces confident errors in unchanged administrative records, while changed processes leave failures. An erroneous anchor excludes the correct mapping, and held-out score sometimes favors that constrained approximation. The reference population, supplied identities and scoring model remain part of the claim.

**CRYPTO-04, choosing the next observation.** The [acquisition experiment](../../experiments/2026-10-02-six-hour/active-identities/FINDINGS.md) uses 48 new systems. Maximum identity entropy reduces the observations needed to reach the exact mapping. Under a 70% administrative mixture change, it averages 4.885 observations, compared with 5.667 for random selection. Stopping at 95% model mass produces 60 wrong decisions among 96 condition histories for entropy selection and 44 for random selection. Selecting useful measurements and deciding that enough evidence has been gathered are separate tasks.

The [reserved-verification protocol](../../experiments/2026-10-02-six-hour/reserved-verification/PROTOCOL.md) adds an observation after the proposed mapping is frozen. It compares randomly reserved identities with model-selected identities and an exact sampling bound. Its reviewed results will guide the next archaeological acquisition design.

A generator-aware form comparator could expose the effect of approximating office and slot structure with a stationary model. Later controls can include short phonetic labels, mixed logographic/numeral inventories and multilingual trade labels. Their ground truth would let us compare permutation search, minimum-cost assignment and Bayesian constraint methods on the same target.

Keep the reference population and every supplied anchor visible in the protocol. Measure identity recovery, confidence, equivalence-set size and performance on separately generated records. These outcomes identify the observations an archaeological application would need.

## Promising tractable target selection

1. Begin with verified repeated artifacts or a documented sealing archive.
2. Separate a physical-sign repair problem from a semantic-mapping problem. Improve photo transcription and alias provenance before assigning words.
3. Seek a minimal independent anchor: exact repeated-object relation, additive count, container category, or securely associated commodity. Record what rival interpretations remain possible.
4. Prefer hypotheses that predict a previously withheld observation and fail decisively if wrong. Reserve full inscription translation for a stronger evidence stage.
5. Stop a search when many incompatible mappings achieve equivalent scores. Preserve the candidates and specify the external observation needed to distinguish them.

## Starting point for the next run

The first project measured sequential prediction, graphic restoration and missing-count recovery. Those outputs are the starting evidence for an anchored mapping experiment. [Original methods](../../research/methods/FINDINGS.md). The next run should add a specified external constraint or test recovery on a known system. Source photographs and catalogue joins deserve attention alongside the solver: the recent cipher examples show how a transcription problem can change an otherwise promising search.
