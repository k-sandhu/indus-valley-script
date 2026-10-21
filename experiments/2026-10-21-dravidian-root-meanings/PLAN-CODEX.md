# Run 1 code and input plan

We build the mechanical study specified in `PROTOCOL.md`, `ENTRIES.md` and `AMENDMENT-1.md`. We preserve those files and keep dictionary text, parsed entries, evidence, codings and reference pools in the local raw directory. This run ends before reconstruction of real codings.

1. Acquire the five supplementary files, a pinned open DravLex release, selected dictionary pages, front matter and definition searches. Record requests and verify source hashes.
2. Read the HTML structure and front-matter abbreviations. Parse entries and lettered subentries, map labels to the twenty tree tips, and record counts and unresolved identifications.
3. Parse the MCC and posterior trees. Record topology, ages, monophyly and the burn-in decision, and preserve the selected posterior sample locally.
4. Implement Sankoff reconstruction, scaled likelihood pruning, marginal probabilities and rate fitting. Compare them with exhaustive enumeration and simulate calibration on the MCC topology and random trees.
5. Implement the frozen sense rules, coding variants and reference pools. Test their rules with original synthetic text and test reference sampling against exact distributions.
6. Build a driver with a hash-checked freeze gate and an output-directory guard. Exercise the entire pipeline with fabricated codings and verify that real computation refuses to run before the freeze.
7. Scan the files intended for tracking for dictionary text, review our prose and changed paths, and write commands and review notes.

Author: GPT-6.1-Sol in the Codex harness. The coordinating session reviews parsing, mappings and tests before freezing code and computing results.
