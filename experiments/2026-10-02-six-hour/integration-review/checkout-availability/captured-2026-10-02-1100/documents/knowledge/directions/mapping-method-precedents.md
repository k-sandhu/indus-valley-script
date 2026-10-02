# Method precedents for the mapping follow-ups

Primary-source check, 2 October 2026. These sources locate the mapping methods in earlier work and identify useful next comparisons. The project’s measured contributions are its specified generators, reference choices, recovery outcomes and independent checks.

## Latent inference and search

Knight, Nair, Rathod and Yamada’s *Unsupervised Analysis for Decipherment Problems* (2006) uses a noisy-channel model, expectation-maximization over hidden plaintext and Viterbi decoding. It covers letter substitution, character conversion, phonetic and word-based problems. The reference model and observation channel enter its inference explicitly. Our unlabelled-form control likewise uses latent inference, with a finite mixture fitted from an independent generated reference and a bijective mapping found by assignment updates. [Primary paper](https://aclanthology.org/P06-2065/).

Hauer, Hayward and Kondrak’s *Solving Substitution Ciphers with Combined Language Models* (2014) combines character and word models and compares beam search with Monte Carlo tree search. Its source corpus represents the plaintext language. This supplies an established cross-field example of game-search methods used for decipherment. A future benchmark could compare search budgets when the project’s graph objective has a known exact small-inventory maximum. [Primary paper](https://aclanthology.org/C14-1218/).

Kambhatla, Bigvand and Sarkar’s *Decipherment of Substitution Ciphers with Neural Language Models* (2018) scores complete candidate plaintexts with a neural model during beam search. Aldarrab and May’s *Can Sequence-to-Sequence Models Crack Substitution Ciphers?* (2021) trains a multilingual decoder and evaluates synthetic and historical substitution ciphers. Their results suggest a future known-language control in which a learned decoder and our explicit mapping scores receive comparable reference information. That control would need fixed training languages, inventory rules, boundary treatment and untouched test systems. [2018 paper](https://aclanthology.org/D18-1102/), [2021 paper](https://aclanthology.org/2021.acl-long.561/).

## Parameter recovery and observation recovery

Allman, Matias and Rhodes’s *Identifiability of parameters in latent structure models with many observed variables* studies mixtures of product distributions through algebraic identification conditions. It distinguishes generic parameter identification from exceptional ambiguous parameter sets. For a later theoretical analysis of our mixture, the component count, grouping of observed slots and rank conditions would need explicit verification. Finite-sample mapping recovery remains the measured target of the current control. [Author paper](https://arxiv.org/abs/0809.5032).

Component labels can be permuted together without changing a mixture’s observed probabilities. A recovered form grouping therefore needs a separate archaeological role observation before its labels acquire a historical interpretation. The immediate computational question is whether preserving a latent distinction improves recovery on the specified generated records, and whether the gain survives a matched smoothing control.

## Reusable comparisons

The next mapping comparison should retain the [overlapping-form records](../../experiments/2026-10-02-six-hour/overlapping-forms/README.md) as a diagnostic set and create fresh systems for a new evaluation. A matched single-profile smoothing control separates mixture structure from extra pseudocounts. A declared form-count selection tests the current three-component prior. More random starts and exact small-inventory optima measure search cost. Reference-population shift remains a separate axis because a well-optimized mapping can still maximize a misspecified score.

Search-engine crawl dates for several older PDFs appeared recent during this check. Publication years above follow the original paper and proceedings metadata. The source check covers these particular precedents; its query record does not establish priority across all decipherment research.
