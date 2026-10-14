# Method precedents for the mapping follow-ups

We checked these primary sources on 2 October 2026. Our mapping experiments generate artificial record systems, hide their symbols behind a one-to-one code, and ask whether a method can recover the code from reference records of the original system. The sources locate these methods in earlier work. Our measured contributions are the system generators, the choice of reference model, the recovery results and the independent checks.

## Latent inference and search

Knight, Nair, Rathod and Yamada’s *Unsupervised Analysis for Decipherment Problems* (2006) uses a noisy-channel model, expectation-maximization over hidden plaintext and Viterbi decoding. It covers letter substitution, character conversion, phonetic and word-based problems. The reference model and the channel producing the observations enter its inference explicitly. Our latent-form experiment, in which no record is labelled with its form, likewise infers hidden structure: it fits a finite mixture to separately generated reference records, then finds a one-to-one mapping by repeated assignment steps. [Knight et al. 2006](https://aclanthology.org/P06-2065/).

Hauer, Hayward and Kondrak’s *Solving Substitution Ciphers with Combined Language Models* (2014) combines character and word models and compares beam search with Monte Carlo tree search. Its source corpus represents the plaintext language. It applies game-search methods to decipherment. A future benchmark could compare search budgets on small inventories, where the exact maximum of our transition-graph score is known. [Hauer, Hayward and Kondrak 2014](https://aclanthology.org/C14-1218/).

Kambhatla, Bigvand and Sarkar’s *Decipherment of Substitution Ciphers with Neural Language Models* (2018) scores complete candidate plaintexts with a neural model during beam search. Aldarrab and May’s *Can Sequence-to-Sequence Models Crack Substitution Ciphers?* (2021) trains a multilingual decoder and evaluates synthetic and historical substitution ciphers. Their results suggest a future control on known languages in which a learned decoder and our explicit mapping scores receive comparable reference information. That control would need fixed training languages, inventory rules and boundary treatment, and untouched test systems. [Kambhatla, Bigvand and Sarkar 2018](https://aclanthology.org/D18-1102/), [Aldarrab and May 2021](https://aclanthology.org/2021.acl-long.561/).

## Parameter recovery and observation recovery

Allman, Matias and Rhodes’s *Identifiability of parameters in latent structure models with many observed variables* gives algebraic conditions under which exact probabilities determine the parameters of a mixture of product distributions. It separates parameters identified in general from exceptional ambiguous sets. A theoretical analysis of our mixture would need to verify the component count, the grouping of observed positions and the rank conditions. The current control measures finite-sample recovery of the mapping. [Allman, Matias and Rhodes](https://arxiv.org/abs/0809.5032).

A mixture's components can be relabelled together without changing its observed probabilities. A recovered grouping of forms therefore needs a separate archaeological observation of each form's role before it acquires a historical interpretation. The immediate question is whether keeping a hidden distinction between forms improves recovery on the generated records, and whether the gain survives a matched smoothing control.

## Reusable comparisons

The next comparison should keep the [overlapping-form records](../../experiments/2026-10-02-six-hour/overlapping-forms/README.md), artificial forms that share length and symbols, as a diagnostic set, and generate fresh systems for the evaluation. A single-profile control with the same pseudocounts (small counts added to smooth the estimates) separates mixture structure from extra smoothing. Choosing the number of forms by a declared rule tests our current assumption of three components. More random starts and exact small-inventory optima measure the cost of search. A shift between the reference population and the encoded records is a separate question, because a well-optimized mapping can still maximize a misspecified score.

Search-engine crawl dates for several older PDFs appeared recent; the publication years above follow the original paper and proceedings records. This check covers these particular precedents and does not establish priority across all decipherment research.
