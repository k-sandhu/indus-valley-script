---
id: C-0002
title: A working reading of Indus legends as household, name and office
status: dead
credence: 0.02
credence_history:
  - {date: 2026-10-12, value: 0.15, reason: "starting estimate in the Shot B brief"}
  - {date: 2026-10-12, value: 0.10, reason: "after discovery-half construction and synthetic dry runs, before freezing predictions"}
  - {date: 2026-10-12, value: 0.02, reason: "frozen primary test failed on the confirmation half (S = -0.567, 33.0th percentile, -0.44 SD); kill condition met"}
risk: long-shot
area: meaning
authors: [coordinator, "Claude Opus 5.5 via Claude Code (Shot B discovery agent)"]
prior_proposals:
  - "Iravatham Mahadevan 1977, The Indus Script: Texts, Concordance and Tables (Memoirs of the Archaeological Survey of India 77): positional classes and numeral combinations"
  - "Iravatham Mahadevan 1982, Terminal Ideograms in the Indus Script, in Harappan Civilization, ed. Gregory L. Possehl, pp. 313-314: jar = priest, lance = warrior, bearer = officer, suffixed to names"
  - "Iravatham Mahadevan 1986, Towards a Grammar of the Indus Texts: 'Intelligible to the Eye, if not to the Ears' (Tamil Civilization): short-stroke markers distinct from numerals; modified fish interchangeable"
  - "Asko Parpola, Seppo Koskenniemi, Simo Parpola and Pentti Aalto 1969, Decipherment of the Proto-Dravidian Inscriptions of the Indus Civilization: A First Announcement; Asko Parpola 1994, Deciphering the Indus Script: fish = star; numeral plus fish as asterism names"
  - "Walter A. Fairservis Jr. 1992, The Harappan Civilization and Its Writing: A Model for the Decipherment of the Indus Script: seal texts give name, title, occupation, status and family; a stroke as genitive"
  - "Bryan Wells 2008, The Classification of Indus Texts, Airavati pp. 275-288: tall strokes with 700 as number modules"
  - "Rajesh P. N. Rao 2018, The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor, in Walking with the Unicorn: carriers as labour, tablets as ration tokens"
  - "Nisha Yadav 2019, Structure of Indus Script (Indian Journal of History of Science): 817, 861 and 820 with 002 as opening modules"
  - "Project catalogues of 8-11 October (experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html), including Bonta's 740 = 'be, belong to'"
builds_on: [STRUCTURE-FIRST-PROGRAM-2026-10-12, SIGN-FAMILIES-2026-10-12, NUMERAL-BEHAVIOUR-2026-10-12, LINE-BREAKS-SEGMENTATION-2026-10-12, SEAL-TEXT-IDENTITY-LOCALITY-2026-10-12, experiments/2026-10-11-bonta-adversarial/REPORT.md, experiments/2026-10-12-anchor-expansion/claude-review.md]
tests: ["experiments/2026-10-12-conjecture-shots/shot-b-reading: frozen primary test failed, S = -0.567 at the 33.0th percentile of 10,000 rearrangements (z1 = -1.20, z2 = +0.63); P3-P5 and S1-S3 failed; kill condition met"]
---

# Claim

Indus legends are built from seven word classes: numerals, links, the names of great households, personal-name elements, commodities and units, office nouns and closing determinatives. A seal legend reads "of [household]: [personal name], [department] [office] [the man or the body]". The pair of short strokes after the openers 817, 861 and 820 is a particle meaning "of"; the fish signs are "star" elements of personal names; the jar 740 is the steward of the store named by the sign before it; the comb 400 marks an office as a body and the man 090 an individual holder. Harappa's moulded and incised tablets are tokens of standard measures, offices and labour; Mohenjo-daro's copper tablets record named holders and their fodder or grain allotments; pottery marks give capacities in standard units or the store a vessel belongs to. Because names and commodities belong to a city while households, offices and grammar are shared, and because office holders have larger seals bearing the emblem of the shared administration, the classes predict where seals were found, their size, their animal and their date. The full map is [GLOSS-MAP.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/GLOSS-MAP.json) and the reading [READING.md](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/READING.md).

# Why it might be true

- 817, 861 and 820 open legends and substitute for one another in 37 to 44 shared frames; 002 follows them in 134 of its 235 tokens in distinct discovery texts and follows a stroke numeral 6 times ([frames_summary.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/discovery/frames_summary.json), [reading_counts.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/discovery/reading_counts.json)).
- 740 ends 259 of 704 distinct discovery seal legends and is bound to its antecedents: 760 precedes it in 34 of 37 texts and 100 in 38 of 44 ([grammar_summary.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/discovery/grammar_summary.json)).
- After 740, the man 090 and the comb 400 share 32 frames; seals end 740-090 in 23 legends and 740-400 in 5, while tablets end 740-090 in 8 texts and 740-400 in 39 ([reading_counts.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/discovery/reading_counts.json)).
- On Harappa tablets, 203 of 237 intact faces with 700 are a stroke numeral plus 700; sheaf signs 390, 405 and 407 follow a numeral in 51 of 145 tokens and the granary bin 590 in 33 ([reading_counts.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/discovery/reading_counts.json)).
- The structure-first program found recurring units, a small closing class and stroke groups fixed to neighbouring signs ([REPORT.md](../../experiments/2026-10-12-structure-first/REPORT.md)), and the seal-text identity study found long legends almost never repeat while short recurring legends travel between cities ([what-12-october-established.md](../directions/what-12-october-established.md)).

# Predictions

Frozen in [PREDICTIONS.md](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/PREDICTIONS.md) and scored once on the confirmation half ([results.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/confirmation/results.json), verified independently in [verification.json](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/verification.json)). Each contrast compares two class groups of per-sign effects against 10,000 rearrangements of the gloss records within frequency and position bands. At the coordinator's review before freezing, the primary score became S = z₁ + z₂; P3 to P5 became individual tests.

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | Names and commodities are more concentrated by site than households, titles, links, determinatives and numerals | 1,086 confirmation seal (component, site) units; 52 local and 37 pan signs | enters S | via S | failed: z = −1.20, opposite direction |
| P2 | Official legends are on larger seals than others of the same length and shape | 846 confirmation seal components with dimensions; 19 official and 67 other signs | enters S | via S | predicted direction, z = +0.63 |
| S | Primary score z₁ + z₂ | as above | above the 95th percentile of rearrangements (2.073) | pass: 0.30; fail with positive distance: 0.06; kill condition: dead | failed: S = −0.567, 33.0th percentile, −0.44 SD; kill condition met |
| P3 | Official signs go with the unicorn more than name signs | 784 square-seal units with a recorded animal | one-sided p < 0.05 | +0.03 if passed | failed: z = −1.32, p = 0.898 |
| P4 | Harappa-tablet vocabulary is commoner at Harappa and copper-tablet vocabulary at Mohenjo-daro on seals | 855 seal units at the two cities | one-sided p < 0.05 | +0.01 if passed | failed: z = +1.38, p = 0.082 |
| P5 | Names are more concentrated by period than shared vocabulary | 475 seal units with a recorded period | one-sided p < 0.05 | +0.03 if passed | failed: z = −0.51, p = 0.690 |
| S1 | Commodity signs less often on steatite than their object type predicts | 1,714 components with a material | one-sided p < 0.05 | none | failed: p = 0.051, predicted direction |
| S2 | Seals ending 740-400 larger than seals ending 740-090 | 5 and 21 seal components | one-sided p < 0.05 | none | failed: reversed, p = 0.999 |
| S3 | Stroke count before a final sheaf rises with seal size | 29 seal components | ρ > 0, one-sided p < 0.05 | none | failed: ρ = −0.19 |
| PP1 | 18% to 32% of newly published seal legends of three or more signs open with an affiliation and link | new publications | inside the range | prospective | untested |
| PP2 | In new texts with a numeral other than 002 and a sheaf sign, a numeral directly precedes the sheaf in at least 55% | new publications | at least 55% | prospective | untested |
| PP3 | New Harappa tablets with 700 are numeral plus 700 on at least 80% of intact faces; 740-400 outnumbers 740-090 on new tablets and the reverse on new seals | new publications | all three hold | prospective | untested |
| PP4 | In a deposit with seals and sealings, official legends have more sealings per seal than name-only legends | future excavation | direction holds | prospective | untested |
| PP5 | A translated Indus office legend renders 740 as steward or storekeeper and a final 090 as a person | a bilingual find | as stated | prospective | untested |

# Kill condition

The conjecture is dead if the primary score fails the pass rule and either stands at or below the mean of its rearrangements, or P1 and P2 both fall below their rearrangement means. Met on 12 October 2026: S stood 0.44 standard deviations below the rearrangement mean.

# Record

- 12 October 2026: map, grammar and draft predictions built on the discovery half by the Shot B discovery agent; credence lowered from 0.15 to 0.10 because the unicorn component runs against a known result and synthetic dry runs show the combined score needs clear support from at least two components ([EXPLORATION.md](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/EXPLORATION.md)). Predictions await the coordinator's review before freezing.
- 12 October 2026: at the coordinator's review the primary score was reduced to S = z₁ + z₂, with P3 to P5 as individual tests; on synthetic withheld fields with planted effects the new S stood 3.13 standard deviations above its rearrangements. Predictions, map and scoring script were frozen (PREDICTIONS.md SHA-256 c864fea5…312a04).
- 12 October 2026 (03:48 UTC on 13 October): single confirmation run. S = −0.567, 33.0th percentile, −0.44 standard deviations; z₁ = −1.20, z₂ = +0.63; P3, P4, P5 and S1 to S3 failed. An independent recomputation gave S = −0.525 and the same fail decision. The kill condition is met: status dead, credence 0.02. Post-outcome exploration ([AMENDMENT-2026-10-12-exploratory.md](../../experiments/2026-10-12-conjecture-shots/shot-b-reading/AMENDMENT-2026-10-12-exploratory.md)) finds the name stock the most evenly spread vocabulary and determinatives, titles and the numeral form 013 the most site-concentrated; a reversed-locality conjecture (shared names, city-specific closing vocabulary) can be tested on the discovery half's unread site field after its own freezing.
- 13 October 2026, adversarial review ([REVIEW.md](../../experiments/2026-10-12-conjecture-shots/review/REVIEW.md)): "dead" is the correct consequence of the frozen kill rule, and the evidence supports the narrower statement that this map fails this test. The frozen code gives −0.44 standard deviations on the confirmation half and +0.88 on the discovery half with its real withheld fields, a fail on both without a kill on the second. Per-sign site concentration correlates at r = −0.092 between halves, so the site component can detect only very large effects; a size effect of 1.2 times the face area fails and 1.5 times passes. The grammar, the individual glosses and other class structures were not tested. The reversed-locality reading proposed after the outcome reverses again on the discovery half and is not carried forward.

