# CRYPTO-02: recovery with an external reference and anchors

Status: protocol fixed before the first run. Date: October 2, 2026.

The earlier label-symmetry demonstration used an internally fitted model. This experiment adds a separately observed reference system and asks when its symbol identities can be recovered from short encoded sequences.

## Synthetic systems

Use eight symbols and two generators: a transition system with asymmetric preferences, and an administrative form system with slot preferences and a hidden office state. Each supplies a known reference population and a separately sampled encoded population. The encoding is a randomly chosen bijection. Its true mapping is retained only for evaluation.

The principal reference and test populations use the same generator. A domain-shift sensitivity changes reference symbol/transition preferences. A wrong-reference comparison uses another independently generated system. Candidate mappings must obey zero, one, two or four externally supplied correct symbol identities.

## Search and scoring

Enumerate every anchor-compatible bijection. Fit a stationary Markov model on 4,000 reference strings, with add-one smoothing. Rank mappings by the encoded training population's likelihood under that fixed reference. Compare with a unigram-only mapping score. Evaluate symbol-mapping accuracy and transformed held-out likelihood on 400 separately sampled encoded strings.

Test encoded training sizes 40, 160 and 640, with 12 seeded repetitions for each condition. Sequences are three to seven symbols long. A first implementation check uses smaller runs; those are tagged as a pilot and are kept separate from the declared grid.

## Outcomes

Record full-map accuracy, fraction of symbol identities recovered, best-to-second score gap, the true mapping's rank, exact anchors and number of compatible maps, held-out log score, and whether the correct reference beats the wrong reference. Report every grid condition, including domain shift and failure cases.

This is a controlled mapping experiment with known synthetic identities. Its role is to identify data/anchor requirements and misleading scores before choosing an archaeological application. The eight-symbol scale and supplied reference system are explicit assumptions; the Indus corpus has a much larger uncertain inventory and no equivalent known-language reference.

## Integrity checks

Identity/noise-free examples must recover a deliberately separated reference mapping. Anchor-compatible maps must number `(8-a)!`. Training/test generation must remain separate. Changing the hidden encoding consistently must preserve reference-relative scoring. A wrong-reference case stays in the output even when it scores well.

Save parameters, seeds, code hash, all trial rows and a summary under this experiment directory. Do not overwrite the pilot with a later run.
