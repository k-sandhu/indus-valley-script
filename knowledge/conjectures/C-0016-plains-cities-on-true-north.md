---
id: C-0016
title: "The plains cities were laid out on true north, the regional towns on their landform"
status: open
credence: 0.30
credence_history:
  - {date: 2026-10-21, value: 0.30, reason: "Starting estimate after TOWN-AXES-2026-10-21: four true-north towns within 2° of cardinal except Dholavira; plan-based regional towns turned anticlockwise by 8-30°; both observations post-outcome"}
risk: stretch
area: archaeology
authors: ["Claude Opus 5.5 (claude-opus-5-5), Claude Code desktop harness"]
prior_proposals: []
builds_on: ["TOWN-AXES-2026-10-21", "experiments/2026-10-21-town-axes/REPORT.md", "C-0015"]
tests: []
---

# Claim

The builders of the Indus-plain cities fixed true north by observing the sky and laid out Harappa's Mound F, the house blocks of Mohenjo-daro and the Lothal dock within two degrees of it. The walled towns of Kutch, Saurashtra and the Ghaggar plain were set out on local axes that follow the landform beside them, the river channel, ridge or shoreline, and are turned anticlockwise from the cardinal directions by 5 to 30 degrees. A town's deviation records its setting, not its date.

# Why it might be true

On Esri World Imagery, measured by two agents blind to each other, Harappa's Mound F lies at +0.01 ± 0.51°, Mohenjo-daro's house blocks at +0.5 ± 0.4° (its main streets at +6.0 ± 1.0°), the Lothal dock at −1.9 ± 0.3° and the Sutkagen-dor enclosure at −0.4 ± 0.5° (one measurer, low confidence). Dholavira's castle lies at −5.5 ± 1.5°, as Vahia and Menon (2013) found ("inclined 6° to the west of north"). The published plans of the regional towns, whose north arrows are not stated to be true, put Surkotada at −15.1° (and −15.5° by a second measurer), Kalibangan's lower-city grid at −15.5° (−12.9°), Chanhu-daro at −19.9° on a dated magnetic plan corrected with IGRF, Farmana at −22.3°, Kanmer at −29.3° and Rojdi at −8.4° ([table](../../experiments/2026-10-21-town-axes/table-v1/settlement-axes.json), [exploratory table](../../experiments/2026-10-21-town-axes/exploratory-v1/table.json)). The plan arrows err by about 3° (root mean square against imagery at four towns), far less than these deviations. Jansen's 1979 values agree for Surkotada (−16 gon) and Kalibangan's main street (−13 gon). These observations were made after the frozen star test was scored.

# Predictions

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | True-north bearings of Kalibangan KLB-2, Surkotada, Kanmer, Chanhu-daro and Farmana are turned anticlockwise by more than 5° | GNSS or drone survey of exposed walls, or plans registered to at least three ground control points | At least four of the five towns below −5°, each beyond 2σ | Pass: 0.45; fewer than three: 0.10 | untested |
| P2 | The deviation of each regional town matches the azimuth of its nearest major landform | Landform azimuths measured on the Copernicus DEM by an agent blind to the deviations, frozen before P1 is read | At least 70% of regional towns within 5°, against a null of landform azimuths rotated at random | Pass: 0.55 with P1; under 40%: 0.10 | untested |
| P3 | A newly measured walled town on open floodplain, with no landform within 2 km, deviates by less than 3° | True-north measurement of such a town (Rakhigarhi or Ganweriwala if exposed) | Absolute deviation < 3° | Pass: +0.05; fail: −0.10 | untested |

# Kill condition

True-north surveys put three or more of the five regional towns of P1 within 3° of the cardinal directions, or the landform match of P2 falls below 40%.

# Record

- 2026-10-21: proposed from the town-axes package as the boldest reading its measurements support; no prediction has been tested.
