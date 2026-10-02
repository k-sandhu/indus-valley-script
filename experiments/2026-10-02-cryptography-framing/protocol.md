# CRYPTO-01: permutation identifiability

Status at protocol creation: specified before execution; synthetic demonstration. Date: October 2, 2026.

Question: can a fitted Markov score or graphic frequency determine semantic names without externally grounded constraints?

Closest existing work: `src/identifiability_demo.py` and `src/verify_root.py::test_label_renaming_preserves_unanchored_objective` already check related label symmetry. This six-symbol enumeration makes the number of consistent maps and the effect of two fixed identities explicit for the cryptography memo. It is an extension for documentation, not a new theorem or a new search for an ancient reading.

Population: 18 explicitly defined synthetic sequences with six symbols; not Indus data. No hidden historical meaning is supplied.

Method: enumerate all 6! bijections; refit consistently using add-one start and transition counts; compare fitted log scores, unigram entropy and edge-count multisets. Enumerate maps preserving two fixed sign identities.

Expected algebraic result: fitted scores equal to floating-point tolerance; 720 maps without anchors and 24 preserving two anchors. Verification fails if any difference exceeds 1e-12, an edge-count multiset changes, or the counts disagree.

Command: `python src/exploratory/permutation_identifiability.py`. Output: `results.json` in this directory. Code hash is stored in the result. This is a reproducible identifiability illustration, not a new cryptographic theorem or Indus decipherment result.
