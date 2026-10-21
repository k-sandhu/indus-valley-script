---
id: C-0013
title: "Fish runs on seals are birth-star names"
status: open
credence: 0.03
credence_history:
  - {date: 2026-10-21, value: 0.05, reason: "Starting estimate: the direction note's integrated astral model"}
  - {date: 2026-10-21, value: 0.03, reason: "Discovery half fails N1 and N3 as written; calibration retires N2; fish runs match the Brahmi asterism profile at matched size but appear on 36% of legends against 6-8% asterism names among Brahmi donors"}
risk: long-shot
area: meaning
authors: ["Claude Opus 5.5 (claude-opus-5-5), Claude Code desktop app, for k-sandhu"]
prior_proposals: ["Asko Parpola 1990, Astral proper names in India: an analysis of the oldest sources, with argumentation of an ultimately Harappan origin, The Adyar Library Bulletin 53: 1-53", "Asko Parpola 1994, Deciphering the Indus Script; 2010, A Dravidian solution to the Indus script problem"]
builds_on: ["FISH-CONTEXT-2026-10-20", "C-0007", "C-0008", "knowledge/directions/parpola-forward-2026-10-20.md"]
tests: ["experiments/2026-10-21-birth-star-names (frozen prediction, unscored)"]
---

# Claim

A run of fish signs in the name part of an Indus seal legend is the holder's birth-star name, the name of the asterism the moon occupied at his or her birth. The runs form a closed class of about 30 to 40 names, built from five common fish forms (in the project's sign coding: plain, top-marked, capped, barred and inner-marked) and their ordered combinations, and the plain fish is the favourite, as Puṣya is in the early Brāhmī donor lists. The stroke groups written before a fish are a separate element of the legend and not part of the star name.

# Why it might be true

Lüders's 1912 list of Brāhmī inscriptions gives the signature of a known birth-star naming system. Of 757 donor occurrences, 42 carry names formed from asterisms under a strict marking and 57 under a broad one (5.5% and 7.5%). They use only 12 or 16 of the 25 asterism labels, Puṣya alone supplies 19 of them, and their normalised entropy (0.775, 0.835) is lower than that of other name elements of the same count (0.99), which form an open vocabulary with Chao1 near 2,300 ([calibration](../../experiments/2026-10-21-birth-star-names/calibration-v1/calibration.json)). Two independent markings agree with kappa 0.97.

On the discovery half of a new split, fish runs in name position have 33 types in 246 occurrences, Chao1 38.6, and at the Brāhmī sample size of 57 they have 17 types, normalised entropy 0.82 and a commonest-type share of 0.25, inside the 95% ranges of the broad Brāhmī class ([discovery](../../experiments/2026-10-21-birth-star-names/discovery-v1/results.json), [checks](../../experiments/2026-10-21-birth-star-names/discovery-v2/checks.json)). The four commonest runs cover 62–75% of runs at Mohenjo-daro, Harappa, Lothal and Dholavira, as a calendar shared by the cities would make them, and the run type is independent of the sign that follows it (permutation p = 0.36), as a name given at birth is independent of the holder's later title.

Two observations count against the claim. Runs of most other sign families of similar frequency are as closed as fish runs at matched size or more so (the jar family B740 has 8 run types in 143 occurrences), so closure alone does not single out fish. And 36% of discovery seal legends carry a fish run in name position, five to six times the Brāhmī share of 5.5–7.5%, so the Harappan custom would have to be far more widespread than in early historic India.

# Predictions

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | Prefix-plus-run compounds have Chao1 between 24 and 45 while opening vocabulary keeps growing (direction note N1) | Fresh seals: absent CISI 3.1/3.2 numbers and Q-1026 finds | Chao1 24–45 and 95% of matched opening draws above 45 | +0.04 only with P2 and P5 (cap 0.12) | failed on discovery (Chao1 186); fresh test frozen |
| P2 | Fresh fish runs fall inside the 33-type discovery inventory | Same | At most 15% of fresh runs of new types | Failure: 0.005, dead | prospective, frozen |
| P3 | Fresh fish runs have the evenness and commonest-type share of the Brāhmī asterism names | Same, compared at n* = min(fresh runs, 57) | Both inside the broad Brāhmī 95% ranges | With P2: both P3 and P4 pass 0.06, one 0.03, neither 0.01 | prospective, frozen |
| P4 | The four commonest discovery runs keep their share at the fresh sites | Same | Share 0.50–0.85 | As P3 | prospective, frozen |
| P5 | One fish modifier distinguishes exactly three bases with balanced pairs, matching the three paired asterisms (direction note N3) | Same | Exactly one such modifier, pair ratios 1/3–3 | +0.04 only with P1 and P2 | failed on discovery; fresh test frozen |

All five share objects and are governed by one joint rule in the [frozen predictions](../../experiments/2026-10-21-birth-star-names/PREDICTIONS.json). Scoring waits for at least 40 fresh fish runs in name position ([scoring instructions](../../experiments/2026-10-21-birth-star-names/SCORING.md)). If the discovery profile holds, P2–P4 pass together with probability 0.88 at 40 runs; an open vocabulary, a site-specific profile, a near-monopoly or a flat class of 27 names passes with probability at most 0.05 ([power](../../experiments/2026-10-21-birth-star-names/power-v2/power-broad.json)).

# Kill condition

The claim is dead if more than 15% of the fish runs on fresh seals are of types absent from the discovery inventory, so that the runs are an open vocabulary rather than a closed list of star names. A pass cannot by itself separate the claim from fish runs being an ordinary closed family of signs with the same profile; that needs an observation tied to birth, such as two runs in one legend behaving as independent draws for holder and parent, or a fish run on a seal matched to an independently dated birth season.

# Record

21 October 2026: the direction note's N1 and N3 fail on the discovery half as written, and N2 is retired because the Brāhmī calibration shows that a known birth-star class is less even than matched open vocabulary. The claim was narrowed to fish runs without their stroke prefix, predictions P1–P5 were frozen at 03:36 UTC with the scorer and reference data, and the credence was set at 0.03. No fresh text has been scored. Verification tier: submitted.
