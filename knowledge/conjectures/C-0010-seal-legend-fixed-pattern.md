---
id: C-0010
title: "The seal legend kept one fixed pattern through Harappa's Periods 3B and 3C"
status: dead
credence: 0.02
credence_history:
  - {date: 2026-10-20, value: 0.35, reason: "starting estimate: the successor reading of the Mohenjo-daro stratigraphy shot, where no part of the legend changed with depth in either excavation"}
  - {date: 2026-10-20, value: 0.40, reason: "discovery on 99 period-labelled Harappa seals outside Vats's Mound F: closing stock steady (union stock 0.71 early, 0.73 late), no drift in opening signs (p 0.56), closing signs (p 0.59), length (p 0.51) or inventory (p 0.82), variants p 0.084, and rectangular seals rising (p 0.015); all at low power"}
  - {date: 2026-10-20, value: 0.02, reason: "frozen confirmation on Vats's Mound F (173 seals, read 03:35 UTC 21 October): P1, P2 passed (stock share 0.848 early, 0.805 late), P3 and P7 no drift, positive control passed (p 0.0017); variants (p 0.0001), length (p 0.003) and inventory (p 0.0016) drift with Holm p below 0.05, the kill condition (effects alone would have given 0.32)"}
risk: stretch
area: seals
authors: [k-sandhu, "Claude Opus 5.5 in Claude Code (Harappa legend-periods session)"]
prior_proposals:
  - "John Marshall (ed.) 1931, Mohenjo-daro and the Indus Civilization, vol. I, London: Arthur Probsthain, pp. 40-41. The sign forms undergo no perceptible alteration through the occupation of Mohenjo-daro."
  - "Mythili R. Rao and Iravatham Mahadevan, 'Archaeological Context of Indus Texts at Mohenjodaro', Journal of the Institute of Asian Studies (Madras), pp. 25-38 (presented June 1985). Mackay's DK-G seals grouped into Early, Middle and Late levels show no significant variation in the relative frequencies of frequent sign pairs. Read in the Wayback copy cited in C-0006."
  - "Asko Parpola 1994, Deciphering the Indus Script, Cambridge University Press, p. 54. Apart from stylistic variation tied to material, the script changed little during the Mature Harappan period."
  - "M. S. Vats 1940, Excavations at Harappa, vol. I, Delhi: Government of India, pp. 9-10 (archive.org in.gov.ignca.18220). Mound F Strata I-III are Late and IV-VII Intermediate; from Stratum IV downwards the mound holds an increasing proportion of 'tiny seals and sealings of an archaic type'."
  - "J. Mark Kenoyer and Richard H. Meadow 2010, 'Inscribed Objects from Harappa Excavations 1986-2007', in Corpus of Indus Seals and Inscriptions 3.1 (ed. A. Parpola, B. M. Pande and P. Koskikallio), Helsinki, pp. xliv-lviii. The opposing view: seal forms and bosses change through Periods 3A-3C, long rectangular seals with script alone are confined to 3C (p. xlix), and the authors expect that studies of change through time will overturn the assumption of a uniform signing system (p. lvi). https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf"
  - "Ayuha Suga 2024, 'Diachronic Changes in the Indus Script Based on the Proposed Arrangement of the Indus Seal', Journal of General Linguistics 26-27: 25-65. The opposing view from 1,137 seals assigned to Periods 3A, 3B and 3C by their carving style: the inventory of characters grows and long legends become commoner in the late period, so the script changed. Periods are inferred from seal style, without stratigraphic control. https://www.lingua.tsukuba.ac.jp/ippan/JGL/2024/GL26-27_3_paper2.pdf"
  - "Andreas Fuls, Corpus of Indus Inscriptions I (2022; 2nd ed. 2023), p. 13, as quoted in the harappa.com review (https://www.harappa.com/content/corpus-indus-inscriptions-i): rectangular seals increase in the later phases of Harappa Mound F and of DK-G at Mohenjo-daro. The book itself not seen."
builds_on: [MOHENJO-DARO-STRATIGRAPHY-2026-10-20, CHRONOLOGY-REGION-01, SIGN-CONTEXT-SEALS-01, SEAL-LEGEND-UNITS-2026-10-20, C-0006, experiments/2026-10-20-harappa-legend-periods/EXPLORATION.md]
tests: ["experiments/2026-10-20-harappa-legend-periods, frozen 20 October 2026 (03:34 UTC 21 October): P1 pass, P2 pass, P3 no drift, P4 drift, P5 drift, P6 drift, P7 no drift, PC pass; dead by the drift kill condition"]
---

# Claim

The Indus seal legend was written to one fixed pattern through the urban period, and the seal that carried it changed around it. At Harappa, from the end of Period 3B to the end of Period 3C, some three to four centuries of Vats's Mound F sequence, the same fifteen signs close about seven legends in ten (740 above all, then 520, 405, 154, 090 and the rest of the stock shared with Mohenjo-daro), the same signs open them, the same variants are cut within each sign class, legends keep their length, and no sign enters or leaves the inventory with the period. When the long rectangular seal with script alone arrives in Period 3C it takes the same legend. Mohenjo-daro's legends show the same pattern at the bottom and top of both excavated sequences. The legend was a standard already in place before the earliest seals these excavations reached, and each city kept it while it rebuilt.

# Why it might be true

At Mohenjo-daro the twelve-sign closing stock closes 73% of legends at the bottom and at the top of Mackay's DK-G sequence and of Marshall's sections, and opening signs, variants and length show no change that repeats from one excavation to the other ([stratigraphy report](../../experiments/2026-10-20-mohenjo-daro-stratigraphy/REPORT.md)). That test left one gap: Marshall's sections span little depth, and the rise of rectangular seals seen in DK-G did not repeat in them, so the drift half might have been untested. At Harappa the 3B–3C differences in sign frequency and legend length measured across all inscribed faces shrank inside single excavation frames ([CHRONOLOGY-REGION-01](../registry/attempts/CHRONOLOGY-REGION-01.json)). On the 99 period-labelled Harappa seals outside Mound F, the closing stock closes 0.71 of early-third and 0.73 of late-third legends, no drift test comes near significance except variant choice (p = 0.084), and rectangular seals rise from 0.09 to 0.29 of the seals (p = 0.015) ([exploration](../../experiments/2026-10-20-harappa-legend-periods/EXPLORATION.md), [exploration.json](../../experiments/2026-10-20-harappa-legend-periods/discovery-v1/exploration.json), [rehearsal](../../experiments/2026-10-20-harappa-legend-periods/discovery-v2/rehearsal/rehearsal.json)). A legend that names a standing office, household or institution in a fixed formula is what a seal-using administration needs to keep recognisable across generations; the seal's material form carried the fashion.

# Predictions

The frozen statistics, nulls, influence rules and power are in [PREDICTIONS.md](../../experiments/2026-10-20-harappa-legend-periods/PREDICTIONS.md). P1 to P7 and PC are tested once on the 175 Mound F seals with a Vats stratum, with strata ranked over the mound (Stratum VII oldest) and permutations within Vats's trenches. A drift test reads "no drift" when p exceeds 0.10 and "drift" when p is at most 0.05 and survives single deletions.

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P1 | The closing-stock share is the same in the early third (Strata VII–V, 3B to 3B/C) and the late third (Strata II–I, late 3C) | Mound F legends with the closing sign read | 90% interval of late minus early inside ±0.25, surviving single deletions; fail if permutation p ≤ 0.05 and the difference is at least 0.15 | +0.05; inconclusive −0.02; fail −0.10 | pass: −0.044, interval −0.190 to 0.102 |
| P2 | The stock is in place in the early third | Early-third legends | At least 0.55 close in the stock | +0.02 / −0.06 | pass: 0.848 of 33 |
| P3 | Opening signs carry no period information | Mound F legends with the opening sign read | No drift | +0.05; inconclusive −0.03; drift −0.10 | no drift: z = 0.09, p = 0.39 |
| P4 | Variant choice carries no period information | All Mound F legends | No drift | +0.02; −0.02; −0.08 | drift: z = 5.94, p = 0.0001 |
| P5 | Legend length does not change | Complete Mound F legends | No drift (two-sided) | +0.02; −0.02; −0.08 | drift: r = 0.273, p = 0.003 |
| P6 | The sign inventory does not change | All Mound F legends | No drift | +0.02; −0.02; −0.08 | drift: z = 3.73, p = 0.0016 |
| P7 | Which stock sign closes a legend carries no period information | Mound F legends with the closing sign read | No drift | +0.04; −0.03; −0.10 | no drift: z = −0.65, p = 0.70 |
| PC | Rectangular seals become commoner through the sequence (positive control) | Every Mound F seal | Positive correlation, one-sided p ≤ 0.05 | gains of P1 and P3–P7 count half if it fails | pass: r = 0.230, p = 0.0017 |
| PP1 | In HARP's own seals (CISI 3.1, not held), at least 60% of Period 3A and 3B legends close in the fifteen-sign stock, and opening signs of 3A–3B seals against 3C seals within Mound E or Mound AB show no drift under P3's statistic | CISI 3.1 catalogue with HARP period labels | As stated, at least 25 legends in each period | +0.05 / −0.10 | untested |

The credence after the test is 0.40 plus the effects, held between 0.02 and 0.90.

# Kill condition

The card is dead if P1 fails or any of P3 to P7 finds drift, with a Holm-adjusted p-value at most 0.05 over P1 and P3 to P7: the closing stock changes its share between the early and late thirds of Mound F, or the opening signs, closing signs, variants, length or inventory change with the period beyond what single misplaced seals explain.

# Record

- 20 October 2026: card written at credence 0.35 as the successor reading of [C-0006](C-0006-closing-stock-fixed-from-lowest-levels.md).
- 20 October 2026: discovery on the period-labelled Harappa seals outside Vats's Mound F ([EXPLORATION.md](../../experiments/2026-10-20-harappa-legend-periods/EXPLORATION.md)); credence raised to 0.40 before the freeze.
- 20 October 2026: predictions frozen by hash with the bench shots loader and tested once on 173 Mound F seals in six trench frames ([REPORT.md](../../experiments/2026-10-20-harappa-legend-periods/REPORT.md), [results.json](../../experiments/2026-10-20-harappa-legend-periods/confirmation-v1/results.json)). The closing frame held: the fifteen-sign stock closes 0.848 of early-third and 0.805 of late-third legends, and neither the opening sign (p = 0.39) nor the closing sign (p = 0.70) changes. The positive control passed, with rectangular seals rising from 0.07 to 0.23 of the seals (p = 0.0017). The body of the legend changed: complete legends average 4.0, 4.8 and 5.3 signs by third (p = 0.003), the sign inventory changes (p = 0.0016) and so does variant choice (p = 0.0001), each at a Holm-adjusted p below 0.05 and surviving single deletions. The card is dead at 0.02 under its frozen rule. Exploratory analyses after the read show the drift on square seals alone and with format held fixed, the added length between the first and last sign, signs 806, 817 and 233 absent or nearly absent from the early third, and interior signs that become less like Mohenjo-daro's. The report states the successor reading, a fixed closing formula joined to a body that changed with time, and freezes three predictions for HARP's Period 3A–3C seals in CISI 3.1. PP1 is left untested with the card.
