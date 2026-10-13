# Amendment 3: power analysis on synthetic Indus-shaped corpora

Recorded 12 October 2026, after the Stage 3, 3f and 3g outcomes. Exploratory. [Script](stage5_power.py), [output](stage5/summary.json), [derived tables](stage5/derived.json).

Stage 3 showed that the key scores like its own permutations, and Stage 3g that fitted keys transfer to unseen texts for every language tried. Neither result says what a correct key, or a real encoding of a known language, would look like on the same measures at the same corpus size. Stage 5 supplies that reference.

For each of Sanskrit, Latin, Old Tamil and Sumerian, held-out text not used to train its model is cut into spans that start at word boundaries and match the lengths of the 1,859 unique Indus texts. Each consonant is written with one of the 577 Indus sign types: signs receive classes by the token-quota rule of Stage 3g, randomized within frequency strata, and a sign is drawn for each consonant in proportion to its Indus frequency among the signs of that class. Duplicate synthetic texts are discarded. The Stage 3g procedure then runs without change: the true key's order gain against 200 within-stratum permutations of itself; constrained annealing from token-matched random starts under each of the four models, fitted on half A and scored on half B (three runs per pair, 30 null starts per pair); and two full-corpus fits under the correct model to measure key recovery.

After the Stage 5 outcomes, [`stage5b_overlap.py`](stage5b_overlap.py) regenerated the same synthetic corpora from the same seed and counted how many half-B bigram and trigram tokens, and how many half-B texts with an internal trigram, are already attested in half A, for the synthetic and the real Indus texts ([output](stage5/ngram_reuse.json)).

The synthetic corpora are homophonic consonant encodings of running text. Real Indus texts may be formulaic, logographic or not linguistic, so the comparison shows how the measures behave under one well-defined alternative. The step count, temperatures and strata match Stage 3g.
