# Reference uncertainty and an erroneous identity anchor

CRYPTO-03. Protocol written 2 October 2026, after the completed CRYPTO-02 grid and before these runs.

The first benchmark fixed a fitted reference model. Its failures motivate two questions: does integrating reference uncertainty reduce wrong confident mappings, and can the held-out penalty from an erroneous anchor expose a bad supplied identity?

Use the same eight-symbol transition and administrative-form generator definitions from the frozen CRYPTO-02 code. Generate 12 new seeded systems in each family. Separately sample references of 40, 400 and 4,000 records, encoded training populations of 40, 160 and 640 records, and encoded test populations of 400 records. Test an unchanged process and the declared 35% mixture change. Retain all ground-truth encodings for evaluation only.

Compare a plug-in stationary Markov likelihood with its Dirichlet-integrated reference predictive likelihood. Both use a symmetric add-one prior for start probabilities and every transition row. The integrated score marginalizes the uncertain reference parameters before observing the encoded training population. For row counts r and mapped encoded counts c, its contribution is

`[log Γ(sum(r)+K) − log Γ(sum(r)+sum(c)+K) + Σj (log Γ(rj+cj+1) − log Γ(rj+1))] / log(2)`.

Use the corresponding formula for initial counts. Score complete ordered strings; multinomial coefficients are absent because the observations are sequences. Enumerate all compatible bijections. The integrated predictive score updates its parameters with the mapped training counts for held-out prediction; the plug-in comparator retains its fixed reference fit. Report the distinction explicitly.

Test three supplied-identity conditions: no anchors, two correct anchors, and two asserted anchors of which the second is wrong. To make the wrong pair internally compatible with a bijection, exchange two true destination identities, including that second identity and an unanchored one. This avoids a trivial duplicate-destination contradiction. Wrong-anchored runs remain in the analysis regardless of fit.

For each likelihood and condition, record exact and partial mapping recovery, mapping-equivalence ranks when truth remains allowed, conditional mapping mass, held-out score and selected map. Compare the wrong-anchored held-out score with the unanchored and correct-anchored scores using the same test sample. Report every reference/training-size condition and descriptive seed-level failure counts. Conditions from the same generated system share samples and are not independent replications.

Before the main grid, check integrated scoring against direct sequential Dirichlet prediction, vectorized score against scalar enumeration, label-renaming invariance, normalization of map mass, anchor consistency and separate sample seeds. Preserve a small pilot separately. Refuse to replace any completed result; save protocol hash, parameters, every trial row and code snapshots. The supplied generators, eight identities and bijection remain the benchmark's assumptions. These results will inform a solver diagnostic and a subsequent acquisition test.
