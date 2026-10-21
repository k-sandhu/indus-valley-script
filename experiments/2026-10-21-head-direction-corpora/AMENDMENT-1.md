# Amendment 1: unit rules and the sampling of reported corpora

Written 21 October 2026 (UTC) while the briefs for the Codex runs were being written, before any source was transcribed or normalised and before any statistic was computed. It clarifies three points of [PROTOCOL.md](PROTOCOL.md) and [SCHEMA.md](SCHEMA.md) and changes no decision rule.

**Brahmi and Tamil-Brahmi clusters.** In SCHEMA.md the sentence on a consonant "with no vowel after it inside its word" refers to a consonant at the end of a word, which Brahmi writes with a virāma. Inside a word, Brahmi writes a consonant cluster and its vowel as one ligature, so `putrasya` has the units `pu`, `tra`, `sya`. Tamil-Brahmi writes no ligatures: each consonant of a cluster is written as its own sign, with the puḷḷi dot in the later stage and as a bare sign in the earlier one. For `ta-brahmi` records every consonant not followed directly by a vowel is therefore its own unit written with `·`, so a word such as `cāttaṉ` has the units `cā`, `t·`, `ta`, `ṉ·`. In `ta-brahmi` the letter `ḷ` is the retroflex lateral consonant; in `ia-ganges` it is the vocalic vowel.

**Older transliteration.** The conversion of the Survey's older convention also maps `ç` to `ś`. Where an editor prints a capital without its diacritic, the capital is lowered as printed; no form is corrected from other occurrences.

**Corpora reported beside the test.** The matched size n of section 8 is set by the four primary corpora. `sux-sargonic` is drawn at the same n when it holds at least n eligible legends and is otherwise reported as too small for that statistic. Sub-corpora are drawn at their own n, as section 9 states, and the two sensitivity runs recompute n from their own primary sets.

**Language of Indo-Aryan legends.** Where an entry carries no language remark, `language` follows the editor's general statement for the collection (Marshall: pre-Gupta legends Prakrit or mixed, Gupta and later Sanskrit), with `language_basis: editor` and the rule recorded in an extra field `language_rule`.
