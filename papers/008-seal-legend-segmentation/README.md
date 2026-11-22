# Paper 008: Line-trained segmentation, graphic families, and cross-city circulation of Indus seal legends

Complete working manuscript, 22 November 2026 (related to Issues #19 and #4), prepared with AI research and writing assistance. Author names, affiliations and a submission venue have not been assigned.

## Contents

- [manuscript.md](manuscript.md): Complete draft manuscript integrating seven dated experimental packages (`2026-10-12-structure-first`, `2026-10-12-seal-text-identity`, `2026-10-13-plate-checks`, `2026-10-20-seal-legend-units`, `2026-10-21-head-direction-corpora`, `2026-10-22-face-adjudication`, and `2026-10-24-office-seal-pass3`), covering findings `F-0010`–`F-0013`, `F-0018`–`F-0030`, `F-0042` and `F-0043`.
- [methods.md](methods.md): Detailed corpus filters, component-grouping splits, feature definitions, Ur III calibration, SHA-256 provenance, exact `bench` and script reproduction commands, and methodological limitations.
- [claim-evidence-map.md](claim-evidence-map.md): Complete mapping of every numerical claim, interval, p-value and archival finding in the manuscript to its repository file and exact JSON key.

## Summary of core verified measurements

- **Graphic families:** Base families gain 0.0219 bits per sign (p = 0.005) over a Kneser–Ney bigram baseline and lower unseen-sign loss from 14.60 to 14.19 bits (13.93 under Parpola and Mahadevan classes); modifier signatures fail (0.0035 bits, net 0.0006, p = 0.114); random contiguous cuts of the Wells number line recover 0.0164 bits.
- **Line-division segmentation:** Catalogued lines recur more than crossing windows (23 vs 4 faces, p = 0.0003); plate audit confirms 65 of 75 divisions with 0 contradictions and identifies Lipi visual-code reversal; line-trained segmenter reaches Youden's J = 0.718 (95% CI 0.586–0.838) on 33 plate-ordered faces against 0.348 for Dirichlet process and 0.117 for branching entropy. On 309 Ur III seal legends (75 single-line labels), it reaches word-boundary F1 = 0.618 (precision 0.908, recall 0.468) against 0.557 cut-everywhere and 0.692 for branching entropy.
- **Frozen closing stock & prospective tests:** 49-formula closing stock and 225-unit inventory achieve κ = 1.00 inter-implementation agreement across 171 held legends (776 positions); 76.0% of held legends close with a stock formula (20.7% shuffled), with four hashed prospective predictions (`PREDICTIONS.sha256`) awaiting unread CISI 3.1 and post-catalogue seals.
- **Numeral fixity & head-direction controls:** Indus stroke values are more fixed per following sign than Ur III commodity counts (3.61 vs 4.53–5.15 values; top share 0.606 vs 0.407–0.450), with near-fixed pairs (`520` after 3 tall strokes 38/41, `585` after 7 strokes 16/17). Across five readable seal corpora (Indo-Aryan, Tamil-Brahmi, Ur III, Old Akkadian, Sargonic Sumerian), final-sign concentration tracks closing formulae rather than head direction (`akk-sargonic` +0.134); the frozen discrimination test remains untestable because Akkadian (11) and Tamil-Brahmi (23) fall below threshold 25.
- **Seal-text circulation & Lothal audit:** Among 1,430 seals across 29 sites, 65 texts recur (41 spanning sites) and 0 of 445 seals of ≥ 6 signs repeat. The frozen locality test gives p = 0.313 (0.473 vs 0.448); motif concordance is unicorn-driven (88 of 89 matches); 13 of 16 matching sealings link only to other-site seals. Blinded plate measurements show Lothal sealings L-161–L-170 share M-895's four signs but come from a differently carved seal of matching face width (23.4 vs 23.3 mm), while Rao (1985) assigns Plate CLXI F conflictingly to both 1864 (L-164, p. 319) and 1830 (L-161, p. 325).

## Pre-submission human review checklist

Before submitting to a venue or preprint server, independent human epigraphists and archaeologists should complete:

- [ ] Inspect the 33 plate-ordered multi-line halftone crops (especially forward-order exceptions H-60, H-97, K-16, the 3 separate-field faces, and L-5 / H-98) and the 12 provisional face-adjudication segment maps (`2026-10-22-face-adjudication`).
- [ ] Verify M-895's surviving animal field (unicorn vs unidentifiable horned animal) on CISI 2 p. 85 and confirm the four-sign reading and elephant motif on L-161–L-170 (CISI 1 pp. 276–278), plus L-166's left edge.
- [ ] Resolve Rao 1985 Plate CLXI F specimen binding (object 1864 = L-164 vs object 1830 = L-161) and inspect calibrated underside and edge geometry of L-164 to adjudicate jar-stopper vs wooden-box reconstructions.
- [ ] Run a human sign-family recoding from shuffled glyph sheets without Wells code order or token counts, checking low-agreement families and the twelve-stroke grid on photographs.
- [ ] Acquire unread CISI 3.1 and post-catalogue seal transcriptions and execute the hash-locked `score_prospective.py` script once on P1–P4.
