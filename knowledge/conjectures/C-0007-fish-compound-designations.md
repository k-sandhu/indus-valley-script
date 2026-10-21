---
id: C-0007
title: "Fish combinations form an ordered designation field"
status: strengthened
credence: 0.45
credence_history:
  - {date: 2026-10-20, value: 0.35, reason: "Registered starting judgement"}
  - {date: 2026-10-20, value: 0.55, reason: "Frozen order and numeral comparisons pass their joint rule"}
  - {date: 2026-10-20, value: 0.45, reason: "Stronger post-outcome references narrow the numeral result; ordered composition remains supported"}
risk: stretch
area: meaning
authors: ["Codex, GPT-6 family, desktop harness; exact backend identifier not exposed"]
prior_proposals: ["Asko Parpola 1994, Deciphering the Indus Script; 2010, A Dravidian solution to the Indus script problem", "Iravatham Mahadevan 1986, Towards a Grammar of the Indus Texts: modified-fish substitutions", "Steven C. Bonta 2024: clustered fish signs, as audited in the October 8–9 review"]
builds_on: ["FISH-CONTEXT-2026-10-20", "NUMERAL-BEHAVIOUR-2026-10-12", "experiments/2026-10-20-fish-context/confirmation-v1/results.json", "experiments/2026-10-20-fish-context/confirmation-v1/meaning-map.json", "experiments/2026-10-20-fish-context/freeze-v1.json"]
tests: ["experiments/2026-10-20-fish-context/REPORT.md", "experiments/2026-10-20-fish-context/adversarial-v1/results.json"]
---

# Claim

Fish combinations form an ordered designation field within seal legends. Successive fish forms carry different parts of one compound label. The field can identify a person, affiliation, office or category; its component sounds remain unassigned.

# Why it might be true

A discovery-learned fish order predicts the reserved seal texts in 43 dependency groups, against eight groups opposing it and two ties. The frozen p-value is 0.0000003434. A later comparison against independent position frequencies gains 0.343 bits per group, and excluding Mohenjo-daro leaves 13 favourable groups, two opposed and one tie. The most common directed relation, W235 before W240, has 14 occurrences against two in reverse. [Primary result](../../experiments/2026-10-20-fish-context/confirmation-v1/results.json), [stronger references](../../experiments/2026-10-20-fish-context/adversarial-v1/results.json).

The numeral success is less specific: preceding context predicts slightly better overall, and removing value two eliminates the fish-specific gain over a general quantity reference. The meaning-map carrier prediction fails (p = 0.4855). The [bench output](../../experiments/2026-10-20-fish-context/confirmation-v1/meaning-map.json) and [freeze](../../experiments/2026-10-20-fish-context/freeze-v1.json) therefore support a structural field without selecting one social or economic meaning. The corpus has prior exposure; this is a frozen evaluation on that material.

# Predictions

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | Fish order learned on discovery predicts reserved seal combinations | October 20 split | At least 15 untied groups, at least 75% favourable, p <= 0.05/3 | Part of the registered joint update to 0.55 | passed |
| P2 | Fish-specific stroke values predict better than a generic count reference | Same split | Positive mean and all deletion means, at least 15 untied groups, p <= 0.05/3 | Same joint rule; stronger references later reduce the judgement to 0.45 | passed against the declared Q reference |
| P3 | Fish signs have an extra seal preference after controls and matched labels | Same split, shared meaning-map bench | p <= 0.05/3 and every deletion contrast positive | At most +0.05; failure leaves that increment at zero | failed |
| P4 | The frozen order transfers to newly source-checked seal texts | New physical objects or previously unexamined source block | At least 30 independent unequal-fish combinations, at least 75% favourable and a positive gain over the frozen positional reference | Raise to 0.60 on pass; lower to 0.20 on failure | prospective |

# Kill condition

Drop the compound-designation interpretation if a sufficiently sized new source block is explained by independent positional roles and the frozen order has no predictive gain, or if source images show that the apparent compounds are a recurring transcription or face-boundary error. Preserve the measured ordering of the old export.

# Record

20 October 2026: the registered A+B rule gave 0.55. Author examination of stronger references narrowed the interpretation and set the current credence at 0.45. Neither a Dravidian sound value nor a particular deity was tested. Verification tier: submitted, with author arithmetic checks.
