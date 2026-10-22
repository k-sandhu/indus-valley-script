---
id: C-0015
title: "Harappan towns were laid out on the setting point of a star"
status: weakened
credence: 0.04
credence_history:
  - {date: 2026-10-21, value: 0.10, reason: "Starting estimate frozen in experiments/2026-10-21-town-axes/PROTOCOL.md"}
  - {date: 2026-10-21, value: 0.10, reason: "Frozen test undecided: four dated towns with true-north deviations, eight needed; the Pleiades version (P1) fails"}
  - {date: 2026-10-21, value: 0.04, reason: "Amendment 1 secondary analysis on eleven towns with plan-based deviations: no significant correlation of deviation with layout date (r = 0.46, one-sided p = 0.082)"}
risk: long-shot
area: archaeology
authors: ["Claude Opus 5.5 (claude-opus-5-5), Claude Code desktop harness"]
prior_proposals: ["Holger Wanzke 1987, 'Axis Systems and Orientation at Mohenjo-Daro', Interim Reports vol. 2, printed pp. 33-44 (Aldebaran for the streets, Procyon for the 'Granary')", "knowledge/directions/parpola-forward-2026-10-20.md, study 4 (the Pleiades)"]
builds_on: ["TOWN-AXES-2026-10-21", "experiments/2026-10-21-town-axes/PROTOCOL.md", "experiments/2026-10-21-town-axes/AMENDMENT-1.md"]
tests: ["experiments/2026-10-21-town-axes/REPORT.md (frozen test undecided, Pleiades version failed; secondary analysis failed P0)"]
---

# Claim

Harappan builders aligned the main axes of each new town on the setting point of a bright star or star group on the western horizon, so that a town's deviation from the cardinal directions records the year it was laid out. In the Pleiades version every town is turned clockwise, by about half a degree more for each century of later layout; in the Aldebaran version towns laid out before about 2050 BCE are turned anticlockwise and later towns clockwise.

# Why it might be true

Wanzke measured Mohenjo-daro's main streets at about 8 gon (7.2°) clockwise and proposed a star on the Kirthar horizon. The Pleiades head the asterism list that Parpola places in the Harappan calendar, and their setting point moved north by about 0.6° per century in the third millennium BCE at these latitudes ([validation](../../experiments/2026-10-21-town-axes/validation-v1/validation.json)). A true-north survey of Mohenjo-daro confirms a street system near +6° beside house blocks near +0.5° ([report](../../experiments/2026-10-21-town-axes/REPORT.md)).

# Predictions

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P0 | Deviation rises with later layout date | True-north deviations and layout dates of at least eight towns | One-sided permutation p < 0.05, Spearman ρ > 0, every leave-one-out r > 0 | Fail with n ≥ 8: 0.02, dead; pass: 0.40 with P3, 0.15 without | undecided on imagery (n = 4, p = 0.33); failed on plans (n = 11, p = 0.082) |
| P1 | Pleiades: every town clockwise, slope about 0.5° per century | Same | ≥ 80% clockwise, none below −2σ, slope interval contains the model slope and excludes 0 | Decides whether the Pleiades version survives | failed: Dholavira −5.5 ± 1.5, Lothal −1.9 ± 0.3 |
| P2 | Aldebaran: sign change about 2050 BCE | Same | ≥ 80% predicted signs among ≥ 8 eligible towns | Decides whether the Aldebaran version survives | failed (2 of 4 on imagery; 7 of 9 on plans) |
| P3 | The target chosen on Mohenjo-daro, Harappa and Kalibangan beats cardinal intent and a constant offset elsewhere | Same | Lower χ² than both, χ² probability > 0.05 | See P0 | failed on imagery and on plans |
| P4 | Prospective: true-north surveys of Kalibangan, Surkotada, Kanmer, Chanhu-daro, Farmana, Banawali, Rakhigarhi and Shikarpur, added to the four imagery towns, show deviation rising with layout date | GNSS or drone survey, or plans registered to ground control; the frozen scorer | P0's rule on all towns with true-north values | Pass: 0.15; fail: 0.01, dead | untested |

# Kill condition

Deviation and layout date are uncorrelated across at least eight towns measured to true north (P4 failing), or the deviations of the regional towns stay beyond 8°, outside the reach of any star or the sun at the equinoxes in 3000–1900 BCE.

# Record

- 2026-10-21, [TOWN-AXES-2026-10-21](../../experiments/2026-10-21-town-axes/REPORT.md). Frozen protocol: stage 1 on Mohenjo-daro (+0.80 ± 1.84) and Harappa (+0.01 ± 0.51) chose the equinoctial sunset over Alcyone (χ² 0.38 against 0.97); P0 undecided with four towns (power 0.24); P1, P2 and P3 failed. Credence unchanged at 0.10 by the frozen rule. Amendment 1, declared before any value was read, scored eleven towns with plan-based deviations: P0 failed (r = 0.46, p = 0.082; without Rangpur r = 0.07). Credence 0.04, status weakened. Wanzke's "1° to 2°" (p. 37) describes the house blocks and his 8 gon (pp. 33–34) the main streets.
