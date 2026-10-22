---
id: C-0014
title: "Parpola's interlocks measure the Tamil lexicon, not the script"
status: open
credence: 0.55
credence_history:
  - {date: 2026-10-21, value: 0.55, reason: "Starting estimate after REBUS-BASE-RATE-2026-10-21: the rebus interlocks that hold arise for random words in 8-43% of cases, the veḷ link is dead as evidence, and the published network is rare (0.44%) only if its five templates were all that were tried"}
risk: stretch
area: language
authors: ["Claude Opus 5.5 (claude-opus-5-5), Claude Code desktop app, for k-sandhu"]
prior_proposals: []
builds_on: ["REBUS-BASE-RATE-2026-10-21", "knowledge/directions/parpola-forward-2026-10-20.md", "knowledge/directions/key-calibration-2026-10-12.md", "FISH-CONTEXT-2026-10-20", "C-0008", "C-0011"]
tests: ["experiments/2026-10-21-rebus-base-rate/REPORT.md (retrospective prediction P3 passed; P1 and P2 untested)"]
---

# Claim

The interlocking Dravidian readings that Asko Parpola presents for the Indus script record the density of the Old Tamil compound vocabulary and the choice of the sign sequences he examined, not the language of the inscriptions. Applied to sign sequences chosen before any Tamil compound is looked up, his procedure finds attested interlocks for his word assignments no more often than for random Tamil words of the same compounding productivity and frequency.

# Why it might be true

Each of Parpola's rebus interlocks that holds in the *Tamil Lexicon* is something the Lexicon supplies for random words. The compounds W1-X and X-W2 share a member for 30.5% of random replacements of *muruku* and *mīṉ*; 43% of random picturable concepts have a word that is the first member of some X-*mīṉ* compound; 8–11% complete the spindle link with *kaṭavuḷ* ([interlocks.json](../../experiments/2026-10-21-rebus-base-rate/results-v2/interlocks.json), fields `/null/I1_T0s/K50`, `/null/pictures_T0s`). Parpola's own *muruku* and *mīṉ* even meet in a second, irrelevant member, *puḷi* "sour". Single homophones are also cheaper in Dravidian than in Indo-Aryan or Sumerian: 2.31% of picture–name pairs against 1.50% and 0.45% ([homophones.json](../../experiments/2026-10-21-rebus-base-rate/results-v2/homophones.json), field `/prediction_single_homophone`).

The four interlocks that hold for his words occur together in only 0.44% of random replacements (`/null/network_T0s`). That rarity is a property of the conjunction, and a conjunction of cheap links is rare only when few were tried. With per-link chance rates near 0.21, four successes become more likely than not once about 17 sign sequences have been examined ([exploratory.json](../../experiments/2026-10-21-rebus-base-rate/exploratory-v1/exploratory.json), field `/E3_template_multiplicity`). Parpola has worked on the script since 1964 and the 2010 paper presents his best cases; one of its five interlocks, *Muruka-p-piḷḷai*, comes from modern Jaffna names rather than from a dictionary. The numeral compounds *aṟu-mīṉ* and *eḻu-mīṉ* are not chance, but they show only that *mīṉ* means "star"; the stroke count that most often precedes the fish on seals, two, has no star compound in the Lexicon.

# Predictions

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | On at least 20 Indus sign pairs not used in Parpola 2010, each frozen with the picture identification of his 1994 sign list before any Tamil compound is looked up, his word assignments yield attested *Tamil Lexicon* interlocks at less than twice the rate of random words matched on productivity and frequency | Parpola 1994 sign list (to acquire), the *Tamil Lexicon* tables and code of REBUS-BASE-RATE-2026-10-21 | ratio of hit rates below 2 | pass: to 0.8; fail with ratio at least 3: dead | untested (prospective) |
| P2 | The *veḷ* search rerun in a second Tamil dictionary with compounds (Winslow 1862 or Kadirvelu Pillai, both on DSAL) again finds a shared member for more than 20% of random replacement pairs | DSAL Winslow or Kadirvelu Pillai | random-pair rate above 0.20 under the stated rule | pass: +0.05; fail: −0.10 | untested (prospective) |
| P3 | Every rebus interlock of Parpola 2010 that holds in the *Tamil Lexicon* arises for random words of the same kind in at least 5% of cases | *Tamil Lexicon*, REBUS-BASE-RATE-2026-10-21 | each per-link rate at or above 0.05 | recorded as the starting evidence | passed after the fact (I1 30.5%, I2 25–43%, I5 7.8–10.8%; I3 does not hold for his words) |

# Kill condition

In the blind template test of P1, Parpola's assignments yield attested interlocks at least three times as often as matched random words, with the lower end of the 95% interval of the ratio above 1.5.

# Record

- 2026-10-21. Created from [REBUS-BASE-RATE-2026-10-21](../../experiments/2026-10-21-rebus-base-rate/REPORT.md) at credence 0.55. The frozen rules killed the *veḷ* interlock as evidence (30.5% against a 20% threshold), passed the network (0.44% against 1%) and failed the prediction that single homophones are as easy in Dravidian as elsewhere (ratio 2.37 against a band of 0.5–2). A post-outcome estimate at Parpola's narrower search depth puts the *veḷ* link at 7.8%.
