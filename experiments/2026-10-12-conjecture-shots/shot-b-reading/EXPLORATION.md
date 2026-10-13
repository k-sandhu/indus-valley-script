# Shot B exploration record

12 October 2026, discovery half only. This file lists what was tried, in order, with the output of each step and the decisions it led to. The resulting reading is in [READING.md](READING.md), the map in [GLOSS-MAP.json](GLOSS-MAP.json) and the draft tests in [PREDICTIONS.md](PREDICTIONS.md). Every script runs from this directory with `python <script>`; outputs that list full sign sequences are written under `data/raw/2026-10-12-conjecture-shots/shot-b-reading/` and stay local.

## 1. Loading and the withheld fields

[common_b.py](common_b.py) loads the discovery half through `shots_common.load_half("discovery", strip=...)` with the coordinator's strip list. Listing the fields that survived the strip showed a metadata field `class` with codes such as `UC`, `SS`, `SC` and `VN`; `UC` with 350 discovery faces looks like a unicorn code, so `class` was added to the strip list for all later work. The value counts of `class`, `type`, `condition`, `preservation`, `sides` and `complete` were printed once while checking this. Object type was kept as instructed; it carries the seal shape (`SEAL:S`, `SEAL:R`, `SEAL:C`) and identifies copper tablets (`TAB:C`).

## 2. Sign profile

[explore_01_profile.py](explore_01_profile.py) counts tokens per sign over all 2,810 discovery faces and positions, neighbours and numeral adjacency over the 1,174 distinct intact single-line texts. Output: [sign_profile.tsv](discovery/sign_profile.tsv), [profile_summary.json](discovery/profile_summary.json). 556 sign types occur; 118 have at least ten tokens and carry 7,748 of the 8,941 known tokens. The profile fixed the positional picture used throughout: 740 is final in 345 of 476 positioned distinct tokens; 400 in 113 of 123; 817, 861 and 820 are initial and are followed by 002 in 42, 53 and 39 distinct texts; 060 is never initial or final, and 57 of its 76 distinct tokens follow 920, 692 or 820.

## 3. Recurring texts and segments

[explore_02_segments.py](explore_02_segments.py) tabulates the commonest complete texts, n-grams and two-sign edges by object group. Output: [segments_summary.json](discovery/segments_summary.json) (counts), local `segments_discovery.json` (sequences). It showed the opener pairs (817-002 opening 38 seal legends, 861-002 36, 820-002 30, 920-060 26), the closing phrases (760-740 ending 28 seal legends, 740-090 23, 033-520 16, 100-740 15), the tablet series dominated by tall strokes with 700, and the post-jar contrast on tablets, where 176-740-400 alone fills 33 incised-tablet faces.

## 4. Substitution frames

[explore_03_frames.py](explore_03_frames.py) counts shared (left, right) frames and clusters signs by context similarity. Output: [frames_summary.json](discovery/frames_summary.json). The clusters at cosine 0.35 separate a terminal group (740, 151, 520, 156, 527, 400, 621, 090, 390, 407, 405, 617, 700 and others), a pre-jar group (176, 384, 482, 100, 760, 923, 904, 717, 388, 900, 690, 615, 575, 585, 840, 460, 463, 335) and small paradigms: 705/706/711 before 033; 741/742/745; 550/555/554 before 527; 435/436; 845/321. The opener paradigm (817, 861, 820) and the post-740 paradigm (400, 090) were the clearest single findings.

## 5. Pictures

[render_frequent_signs.py](render_frequent_signs.py) draws the 118 signs from the local Lipi font in frequency order (local sheets under `glyphs/`). The sheets were viewed together with the Mayig descriptions, the second coder's notes in the structure-first step 1, and the prior meanings extracted from the October 11 catalogue without its statistics block ([prior_project_meanings.json](discovery/prior_project_meanings.json)). Pictures chose glosses among signs with the same distribution: the jar for storage, the yoke-carrier, the lance, the staff-bearer, the rake on a shaft, the sprouting vessel, the two grids, the man and the comb.

## 6. Decisions on the reading

**Openers.** Three readings were weighed for 817, 861 and 820 with 002: city names, ranks and great households. City names would make each opener concentrate at one site; the three are equally frequent (90 to 125 tokens) while the corpus is dominated by two cities, and they substitute in identical frames, which a city reading explains only for offices replicated across cities. Ranks predict an ordering that the texts do not show. The household reading was chosen, with city names kept as the rival gloss; it predicts that the openers are shared across cities (P1). 817 and 861 are near-identical in picture and context (cosine 0.988) and are treated as allographs.

**The jar 740.** A grammatical "of" (Mahadevan's earlier view, Bonta's "as") and a title were weighed. The bound antecedents (760 before 740 in 34 of 37 texts, 100 in 38 of 44) favour a compound of qualifier and head noun, as Mahadevan argued in 1982; the picture of a storage jar and the commodity-like antecedents chose steward over his priest.

**Determinatives.** The 090/400 paradigm after 740 splits by object type (seals 23 against 5, tablets 8 against 39), which led to reading 090 as the individual and 400 as the office as a body.

**Names and commodities.** Fish and leaf signs that fill the variable middle of legends became name elements. Signs inside recurring closing phrases, after numerals, or bound before 740 became commodities or units. This boundary is the least certain in the map; 415 (rake) and 255 (hatched creature) sit on it.

**Animals.** The reading has to say something about the field animal. Linking the animal to the opener or to the name would contradict facts already known: identical texts share animals only on unicorn seals, and seal texts did not predict unicorn against other animals in the 6 October package. The reading takes the unicorn as the emblem of the shared administration and predicts only that official legends carry it more often than names (P3), with a low expectation.

## 7. The map and the grammar

[build_gloss_map.py](build_gloss_map.py) writes [GLOSS-MAP.json](GLOSS-MAP.json) from the hand table and the discovery evidence, with bands and attributes. The first build stopped because 905 had no entry; it was added as a commodity (double portion, the copper-tablet form of 904). Classes: COMM 46, NAME 29, TITLE 17, NUM 13, LINK 5, AFF 5, DET 3; 24 signs are official; 14 carry stock H and 6 stock MD.

[gloss_texts.py](gloss_texts.py) applies the map and the slot grammar to every discovery text (local `glossed_discovery.jsonl`) and writes [grammar_summary.json](discovery/grammar_summary.json). On 704 distinct seal legends, 152 open with an affiliation and link, 401 end in a title, 66 in a determinative and 80 in a commodity; 97 end in a sign outside the map. Rule checks found 58 legends with an affiliation sign after the first position (often 140 or a rare sign before 920) and 148 with a link after something other than an affiliation, link or numeral, mostly rare initial signs followed by 002. These were read as rarer households and titles outside the map; the map was not changed.

While READING.md was written, several counts were checked with inline commands: the contexts of eighteen key signs, the texts opening with each opener, the endings 740-090 and 740-400 by object group, numeral and sheaf adjacency, the 700 tablet pairs and the commonest closing phrases. [explore_04_counts.py](explore_04_counts.py) reproduces the cited counts in [reading_counts.json](discovery/reading_counts.json). Two numbers changed in the process: the commonest closing phrase 590-390-740 ends 12 seal legends (14 counts every occurrence), and 002 follows a stroke numeral 6 times once the twelve-stroke 055 counts as a numeral (5 without it).

## 8. Designing the test

The first design used per-sign z statistics. Because z grows with a sign's frequency, it was replaced by effect sizes: bias-corrected concentration for site and period, mean residual for size, and share excess for the unicorn and for Harappa against Mohenjo-daro. The size model first used text length and its square. On the first synthetic null dataset the S3 correlation between stroke count and size residual came out at ρ = 0.36, and in case the quadratic fit was leaving length in the residual, length was entered instead as indicators for each length from 1 to 12. The same dataset still gave ρ = 0.39 (two-sided p = 0.02), while eight further synthetic seeds gave −0.11 to 0.25 with no two-sided p below 0.15, so the first value is read as chance. The indicator model was kept.

Position bands were set at final share ≥ 0.40 and initial share ≥ 0.30, and frequency bands at 10–19, 20–39, 40–99 and 100 or more tokens, giving twelve cells of 2 to 19 signs. Whole gloss records move under rearrangement so that class and attributes stay consistent.

## 9. Dry runs of the confirmation script

[confirm.py](confirm.py) was run only on synthetic withheld fields attached to the discovery half. With random fields ([synthetic_dryrun_null.json](discovery/synthetic_dryrun_null.json)) the combined score is 1.02 standard deviations below its rearrangement mean. With planted effects ([synthetic_dryrun_planted.json](discovery/synthetic_dryrun_planted.json)), P2 detects a 25% increase in linear seal size for official legends at z = 3.6 and P1 detects names leaning to one of three sites at z = 1.1, and the combined score is 1.31 standard deviations above its rearrangements, which fails the pass rule. Across eight more random datasets ([synthetic_seed_check.json](discovery/synthetic_seed_check.json)) the combined distance ranged from −1.31 to +0.36, averaging −0.4 with all nine runs. Eligible signs on the synthetic data: 90 for site, 89 for size, 81 for the unicorn, 67 for period.

## 10. Credence

The starting credence was 0.15. It is lowered to 0.10 before freezing. Two reasons carry the change: the unicorn component runs against a known result, and the dry runs show that the combined score passes only with clear support from at least two of the five components, while sign-level effects are diluted because every sign in a legend shares that legend's site, size and animal.

## 11. What was seen of withheld variables

No withheld field was loaded. The aggregate facts known in advance, and the few object-level glimpses that occurred while building the map, are listed in the last section of [PREDICTIONS.md](PREDICTIONS.md). Shot A's directory and the size, motif and site outputs of earlier packages were not opened, apart from the October 11 catalogue row of sign 740, whose site counts were displayed once before the extraction was restricted to meanings.

## 12. Coordinator review and freezing

The coordinator approved the draft with one change before freezing: the primary score became S = z₁ + z₂ (site concentration and size), with P3, P4 and P5 kept as individual predictions, each passing at one-sided p < 0.05. The reasons are recorded in [PREDICTIONS.md](PREDICTIONS.md). `confirm.py` was changed to compute the new primary score, its numerals-fixed sensitivity, the kill-condition verdict, the eligible group sizes and a five-component reference sum without a pass rule. The dry runs were repeated: on random synthetic fields S stands 0.78 standard deviations below its rearrangements; with planted effects z₁ = 1.06, z₂ = 3.56 and S stands 3.13 standard deviations above them and passes; over eight more random datasets S ranged from −1.71 to +2.03 and one passed. PREDICTIONS.md and GLOSS-MAP.json were then frozen and the SHA-256 of PREDICTIONS.md written to `PREDICTIONS.sha256`. The single confirmation run and its outcome are recorded in [README.md](README.md), [confirmation/results.json](confirmation/results.json) and the [exploratory amendment](AMENDMENT-2026-10-12-exploratory.md).
