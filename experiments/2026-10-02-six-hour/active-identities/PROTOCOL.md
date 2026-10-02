# Choosing the next independent identity observation

CRYPTO-04. Protocol fixed on 2 October 2026 after CRYPTO-03 and before pilot or main outcomes.

The previous grid retained high conditional mapping confidence under a changed process. This experiment asks whether a solver can choose useful independent identity observations despite that mismatch. Each observation supplies the true identity of one observed code. A separate oracle holds those identities and reveals only the requested one.

Generate 24 new seeded systems in each of the same transition and administrative families. Use nested references of 40 and 400 records, encoded training populations of 40 and 160 records, and process-mixture changes of 0%, 35% and 70%. Fit the specified stationary Dirichlet-integrated reference predictive score and enumerate all 40,320 eight-symbol maps once per condition. A uniform prior on those maps defines their conditional masses.

Compare three query rules on the same data: random remaining identity, maximum posterior entropy of a remaining identity, and largest training frequency among the remaining codes. The entropy rule maximizes expected reduction in map entropy for an exact identity response under the fitted posterior. Frequency is an observable acquisition heuristic. Each policy receives only labels, training counts, scores, compatible maps and earlier revealed identities. It must choose a code before the oracle response. All observations have equal declared cost.

Run every policy through all eight observations, even if its mass exceeds 0.95 earlier. Preserve the selected map, map mass, conditional map entropy, candidate count, actual recovery, symbol accuracy and next query at each prefix. Define a retrospective confidence stopping diagnostic as the first prefix with mass at least 0.95; measure its errors against the known answer without actually stopping the experiment. Also retain the first correct prefix and the first prefix from which all subsequent selected maps remain correct. These distinguish a lucky temporary answer from stable recovery.

Record all 576 system/sample/process conditions and each policy's nine prefixes. The 48 systems are independent simulation units; sizes, shifts, models and query policies within one system share source data. Compare policy differences by paired system summaries. Do not count the resulting 15,552 prefix rows as independent replications.

Before the main grid, check that posterior masses normalize, the entropy rule equals the expected map-entropy reduction from enumeration, each policy hides identities until after selection, every revealed identity is respected, remaining map counts equal `(8-k)!`, and all eight identities select the true map. Keep separate pilot and main outputs, code and helper hashes, all generated seeds and runtime. Preserve failed assumptions and any later repairs in separate endpoints.

The experiment supplies a shared eight-symbol inventory, a bijection and reliable external identity measurements. Its contribution is an observation-selection test under these assumptions. An archaeological application needs to specify the physical measurement and how it independently establishes the proposed identity.
