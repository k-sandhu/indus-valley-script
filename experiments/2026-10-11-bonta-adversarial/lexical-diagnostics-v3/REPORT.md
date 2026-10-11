# Lexical repair and rival review

The finite join model verifies saṃvāha (MW 226133) and sāṃśa (240923), while preserving the absence of their unjoined queries samvāha and saaṃśa. The full pinned text and the alphabetic dictionary index agree on these records. All literal counts reproduce the preceding run. The repaired model applies the same stated boundary rules to every candidate residual, and scores all recovered rivals across each sign's original searched patterns.

| Code and selected comparison | Model | Patterns | Selected support | Rank with ties | Rivals with greater support | Full intersection |
|---|---|---:|---:|---:|---:|---:|
| W233 / ati | literal | 46 | 6 | 33 | 32 | 0 |
| W233 / ati | limited_join | 46 | 9 | 16 | 15 | 0 |
| W231 / sam | literal | 22 | 7 | 2 | 1 | 0 |
| W231 / sam | limited_join | 22 | 7 | 11 | 10 | 0 |
| W204 / sa | literal | 8 | 5 | 1 | 0 | 0 |
| W204 / sa | limited_join | 8 | 5 | 1 | 0 | 0 |

The rank is one plus the number of residuals with strictly greater pattern support. Multiple residuals can share it. A pattern contributes at most once to a residual, regardless of repeated objects or dictionary senses. The full search rankings and corpus windows are retained locally; the public [results](RESULTS.json) publish aggregate histograms and bounded leading rivals with exact dictionary entry/page identifiers.

Crosswalk sensitivities remove windows containing either original imported disputed codes or the union of both coders' disjoint Table 18 candidate sets. Both frames and their remaining pattern/family counts appear in the results. Removing every pattern leaves an undefined intersection, recorded as null. A disappeared frame supplies no positive lexical evidence.

The five new semantic anchors, bhārin, varga, dvāra, kṛṣi and lāṅgala, have no asserted phonetic windows in this iteration. Their stress tests enumerate two-component MW headwords with unknown components of one to six SLP1 letters containing a vowel, in both component orders. Fixed alternative stems and samples of up to 1,000 dictionary headwords of the same SLP1 length show how readily this construction produces alternatives. The independent control seed is 2026101103. The earlier control identities were not saved, so those draws cannot be replayed by identity.

The join rules cover final m before consonants, a/ā coalescence and i/ī vowel joins. Literal forms remain available. The inverse search forward-verifies each candidate against an exact indexed headword. General morphological parsing, arbitrary editing, voicing, retroflexion and the earlier broad normalization are excluded from this repair because they would enlarge the match space without a fixed linguistic model. Other Sanskrit joins remain outside its coverage.

The [protocol](PROTOCOL.json) and [pre-calculation amendment](AMENDMENT-01.json) were written before this computation. [Verification](verification.json) records input/code/output hashes and exact checks. These post-outcome counts describe dictionary-search flexibility and crosswalk sensitivity; they do not estimate historical reading probabilities.
