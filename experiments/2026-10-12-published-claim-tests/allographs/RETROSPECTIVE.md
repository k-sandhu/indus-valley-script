# Study C retrospective

A Claude Opus 5.5 subagent ran Study C unattended on 12 October 2026 as part of the published-claim tests package. It owned `experiments/2026-10-12-published-claim-tests/allographs/` and `data/raw/2026-10-12-decipherment-claim-tests/allographs/`.

## Approach

The run began by reading the preprint's sections on sign classification, allographs, sibilants and nasals, conjuncts, direction markers and stylistic variants (2.11, 4.4, 4.10–4.14), then the app functions that interpret the key (`canonize`, `mkregex`, `xlitize` in `index.vue`; `resolveXlit` in `glyphs.vue`). Before any outcome was computed it inspected the key's row types and canonical chains, the corpus inventory and frequency strata, and the sizes of the candidate pair sets, and recorded these in `PROTOCOL.md` (SHA-256 `3e83fd098fb3…a2cc5d50`). The primary script then ran once (about two minutes). Diagnostics followed after the results had been read, and an independent verification script recomputed 43 headline quantities with separate code; all agreed.

## Problems and how they were handled

- The preprint uses "allograph" for a graphically distinct sign of one phoneme, with stylistic variants beneath it, while the key's `canonical` column encodes the variant relation and its `xlit` column the phoneme. The study tested both layers separately (variant pairs and same-value base pairs).
- The app has two value paths. `json-2-csv` parses codes without a leading zero as numbers, and the main page then overwrites a variant's own value with its canonical's. The glyph page's `resolveXlit` matches the documented rule, so it was adopted; the three affected rows are reported, and the homophone primary set uses base signs only.
- Eight variants point to other variants. Roots were found by following pointers, which form a function without cycles.
- A family of n variants contributes n(n−1)/2 dependent pairs. The protocol used a stratified relabelling null that keeps each set's pair structure, and cluster bootstrap over roots, values or Mayig classes.
- The two most frequent codes were alone in their log₂ strata. Strata with fewer than five codes were merged downward, which makes the top stratum span 130 to 902 tokens and matches W740 only coarsely.
- The Mayig crosswalk turned out to assign exactly one class per code, so its intersection rule reduces to class identity.
- `python -I` could not import NumPy from the user site-packages, so the authored scripts were run without it; all inputs are local data files.
- After P1-out passed, a post-outcome check by Wells catalogue distance found a similar excess among adjacent codes that the key assigns to different roots, mostly stroke numerals. It is reported as a diagnostic and does not alter the frozen decisions. `diagnostics.py` was extended once with this block and rerun with the same seeds; earlier diagnostic values were unchanged.
- The conjunct decomposition test had a null mean of 0.11 matches and therefore no power. It is reported as uninformative.
- The subagent's harness refused report-type Markdown files, so `REPORT.md` and this retrospective were returned as text and saved by the coordinating session.

## Outcomes

The key's variant pairs beat frequency-matched pairs on minimal-pair substitution (10.9 times) and neighbour similarity, including pairs in different Mayig classes (4.6 times), with a much larger excess where key and Mayig classes agree (34 times). The key's homophone bases failed both primary tests (p = 0.13 and 0.21) while sharing positional profiles. The preprint's jar-stroke ordering holds in 94 of 97 eligible texts (48 expected). Its statement that variants rarely co-occur fails in aggregate because of the fish signs. Outputs, seeds and input hashes are in `run-2026-10-12/`; sequence-bearing example lists stay local.
