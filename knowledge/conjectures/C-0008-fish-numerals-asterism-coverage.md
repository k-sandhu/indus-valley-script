---
id: C-0008
title: "Three, six and seven asterism names cover short-stroke fish combinations on seals"
status: weakened
credence: 0.05
credence_history:
  - {date: 2026-10-20, value: 0.15, reason: "Registered narrow astronomical long shot"}
  - {date: 2026-10-20, value: 0.05, reason: "Fails minimum sample, canonical coverage and predictive-score rules"}
risk: long-shot
area: meaning
authors: ["Codex, GPT-6 family, desktop harness; exact backend identifier not exposed"]
prior_proposals: ["Henry Heras and Asko Parpola: fish-to-star rebus and numeral-fish asterisms", "Asko Parpola 2010, A Dravidian solution to the Indus script problem, printed17: six-fish and seven-fish"]
builds_on: ["FISH-CONTEXT-2026-10-20", "experiments/2026-10-20-fish-context/freeze-v1.json", "experiments/2026-10-20-fish-context/confirmation-v1/results.json"]
tests: ["experiments/2026-10-20-fish-context/confirmation-v1/results.json"]
---

# Claim

Short-stroke groups immediately before plain fish on seals chiefly form the asterism names three-star, six-star and seven-star. Their distribution follows a fixed celestial-name inventory.

# Why it might be true

The graphic seven-plus-fish inscription on H-9 is clear, and Parpola compares it with later Dravidian star names. This card tests a stronger population claim than that particular reading. The registered model puts 90% of its mass on values 3, 6 and 7, excludes the two-long-stroke compounds and compares its predictive score with generic quantities and fish-specific expressions. [Frozen specification](../../experiments/2026-10-20-fish-context/PREDICTIONS.json), [bench freeze](../../experiments/2026-10-20-fish-context/freeze-v1.json).

Only 17 qualifying reserved groups exist. Eleven have canonical values, a share of 0.647 with a 95% interval of 0.413–0.827. The model loses 0.340 bits per group to the quantity reference and 0.753 to fish-specific expressions. It fails the minimum-20, coverage and score rules. Some short strokes could be connective constructions, so the failure applies to this population model and its classification of the strokes. [Exact results](../../experiments/2026-10-20-fish-context/confirmation-v1/results.json), field `/comparisons/primary_seals/numbers/narrow_celestial`.

# Predictions

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | Canonical values dominate and predict reserved examples better than both rivals | October 20 split | At least 20 groups; Wilson95 lower bound >=0.8; positive score gain over Q and L; strict-stroke pass | 0.30 if all pass, otherwise 0.05 | failed |
| P2 | The inventory transfers to independently qualified numeral-fish uses | New source block distinguishing numerals from connective marks | At least 40 groups; the same frozen model beats both rivals and covers at least 80% | Raise to 0.30 on pass | prospective |

# Kill condition

Drop this population claim when a source-qualified sample of at least 40 independent numeral-fish objects gives a 95% upper bound below 0.8 for the canonical share, or the frozen celestial model consistently loses to both rivals on that sample. A particular celestial reading needs its own linguistic and archaeological test.

# Record

20 October 2026: weakened to 0.05 under the registered rule. The result supplies no authenticated pronunciation, language identification or rejection of every celestial use of fish. Verification tier: submitted.
