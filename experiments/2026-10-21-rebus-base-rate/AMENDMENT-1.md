# Amendment 1: two code repairs after the freeze

Recorded on 21 October 2026, after `results-v1/` had been computed and before any report was written. The protocol (SHA-256 `32f3dff6c863ef68273e44dbf0070653892a7701fc5d42c2391b83bb7e22ec25`) is unchanged.

## The verification script could not write its output

`code/verify.py` computed every check and then failed when it expressed the results directory relative to the repository root, because the path it was given was relative. We made it resolve both paths first. This repair changes no number. Frozen hash `9b7a106172ed6b516a4914c2d3797f4332c4def5c3c8ad9e5833bfb50fff25f4`.

## The stem rule treated "y" as a vowel

The independent reimplementation in `verify.py` reproduced the real search exactly but drew different replacement pools, and its null rate for the *veḷ* search was 0.3052 against the frozen 0.3084 ([verification-v1.json](verification-v1.json)). The cause was the vowel set in `code/rebus.py`, which included "y" because [y] is a vowel in IPA. In every transcription this study uses, "y" is the palatal glide. The stem rule (T1s) therefore removed the final consonant of 1,520 Tamil Lexicon headwords such as *nāy* "dog", *vāy* "mouth" and *cey* "to do". The defect reached every use of the stem: anchoring of compounds to a word, the productivity counts, the choice of replacement words and every comparison under T1s in both measurements. Comparisons under T0 and T0s in the homophone measurement do not use the stem and were unaffected.

We removed "y" from the vowel set and added a selftest check that *nāy* keeps its final *y* ([selftest-v2](selftest-v2/selftest.json), which passes). `verify.py` also kept fewer letters than `rebus.py` (it dropped Toda and Kota vowels such as ï), which made its Dravidian homophone rate 0.02331 against 0.02311; it now keeps every letter with its diacritics.

| File | Frozen SHA-256 | Repaired SHA-256 |
|---|---|---|
| `code/rebus.py` | `f9c84342a47cd4454aa57a144f3199d902ded60ea881e7932a8cf3f768c6d324` | `bfa65175b3383b8cad04d05f0078cfa7abcfbc673b0728f92a138f47c787ed42` |
| `code/selftest.py` | `a88a5ce83552aed04cb576dbc3bf4af6b1d6277ad244e8f083f8a903cfcd1031` | `03bd181b1169738dc265daef3b176cae109a689b1c7ab9f9a84b037a9874338f` |
| `code/verify.py` | `9b7a106172ed6b516a4914c2d3797f4332c4def5c3c8ad9e5833bfb50fff25f4` | `7d2ff8097c794d0341aee0abac70013862aeb76e228a23a4337cd8b290d560d9` |

The input tables are unchanged; their hashes are those in [FREEZE.json](FREEZE.json).

## What is kept and what is read

`results-v1/` (homophones `1d60d56a…6e76`, interlocks `0248d8b1…944b`) stays as computed with the frozen code, with [verification-v1.json](verification-v1.json) recording the disagreement that found the defect. `results-v2/` (homophones `a9cf4728…9adf`, interlocks `f6cae04b…081a`) was computed with the repaired code, and [verification-v2.json](verification-v2.json) agrees with it on all seven checks. The report reads the decisions from `results-v2/`. They are the same in both versions: the *veḷ* null rate is 0.3084 in v1 and 0.3052 in v2 (killed in both), the network rate 0.0053 and 0.0044 (passes in both), and the homophone measurement under T0s is identical.
