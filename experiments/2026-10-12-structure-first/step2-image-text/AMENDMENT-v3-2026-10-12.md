# Amendment after verification and review: permutation counts, odds ratios, label merges and the comparator

Recorded 12 October 2026 after the verifier (`../verification/VERIFICATION.md`) and the adversarial review (`../review/REVIEW.md`, findings 3, 11 and 15). Runs `run-2026-10-12/` and `-v2/` are unchanged; `run-2026-10-12-v3/` is the endpoint.

**Permutations.** The protocol specifies 10,000 label permutations for test 2c; the first two runs used 2,000 for 2b and 2c. Run v3 uses 10,000 for every test. All conclusions are unchanged (2d: 3 matching hits against 3.01, p = 0.62).

**Odds ratios.** The second run reported a Haldane-corrected odds ratio for classes with no matching hit, which produced values above 1 from the correction alone. Run v3 reports each class's 2×2 counts and the expected number of matching hits under the margins, and an odds ratio only when every cell is nonzero.

**Label merges.** The code merges unicorn variants (`Bull1:*`), goat variants (`Goat:*`) and short-horned bulls (`Bull`, `Bull2`, `Bull3`), and treats `None`, `-`, `Othr` and `Unknown` as unlabelled. These rules were written into the code before the first run and were not in the protocol. Labels such as `CompBull` stay separate.

**Correction to the first amendment.** The first amendment says the specificity rule was corrected "before its 2d result was interpreted". The first run had printed its 2d result (p = 0.845) and the output had been read when the defect was noticed: four copper classes had no specific sign groups at all. The correction follows the protocol's wording and did not move the result toward significance.

**The Parpola comparator.** The protocol names `research/literature/copper_constraints.csv` as a published comparator, and the analysis never read it. That file records Parpola's class-level observation (2008, pp. 134–136) that copper tablets of one image type share an obverse text, which is the published precedent for test 2a on copper, and lists pairs of image types that share a text. No quantitative comparison with it was made; the step 2 report cites it as prior work.
