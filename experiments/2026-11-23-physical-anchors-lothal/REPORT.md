# Physical numerical anchors and Lothal sealing attachment geometry

We audited two physical objects behind Fuls's published numeral equations (`H-904` for `Q-0011` and `M-1383` for `Q-0012`) and evaluated whether seal legends at Lothal predict physical container or fastening classes (`Q-0019`). Three findings emerge from inspecting the held primary plates, catalogues, and sealing reverses. First, CISI 2 photographs confirm both faces of `H-904` (`002-840-032-740` and `817-368-645-900-033-700`) and show that Fuls's prose label `W032` for three long strokes is a slip for `W033`, while the historical integer join `ICIT 3786` to `H-904` remains formally provisional because we lack Figure 16 and ICIT access. Second, CISI 2 plate p. 182 confirms that `M-1383` is a unicorn-stamped clay sealing applied directly to the mouth of a stoneware-bangle firing container (`MN 82a`), resolving the earlier clay-tag metadata conflict, yet zero held primary sources verify the 82-fragment and 15 to 20 reconstructed bangle count behind Fuls's base selection. Third, independent visual checks of CISI 1, Rao 1985, and Frenez and Tosi 2005 confirm that `L-206` (`2077`) bears a deep curved cylindrical recess incompatible with an angular board edge, and our frozen die-grouped permutation and cross-validation tests across 55 diagnostic joined Lothal sealings (36 distinct seal components) find no evidence that inscription features predict fastening or container class better than chance.

## Shared methods and source scope

Before examining any Lothal sign-to-attachment cross-tabulation, we wrote and froze [PROTOCOL.md](PROTOCOL.md) (SHA-256 `4b73b5d4...`) and coded all 93 Lothal sealings (`L-124` through `L-216`) strictly from Frenez and Tosi's Table 1 and physical reverse prose. All local renders from copyright-unresolved scans remain outside Git under `data/raw/2026-11-23-physical-anchors-lothal/` (physical path `D:\projects\indus_valley_script\data\raw\2026-11-23-physical-anchors-lothal\`). Exact structured outputs are saved in [anchors-audit-v1.json](anchors-audit-v1.json), [lothal-attachments-v1.csv](lothal-attachments-v1.csv), [lothal-test-v1.json](lothal-test-v1.json), and [verification-v1.json](verification-v1.json). These primary checks examine published photographs, basic-data tables, and excavation catalogues rather than the physical museum specimens; no statistical test here applies `bench/` because Part A audits catalogue identity and arithmetic bounds while Part B tests archaeological reverse-trace prediction outside inscription-corpus tasks.

## Part A: Numerical anchor audit (`Q-0011` and `Q-0012`)

### `Q-0011`: `H-904` and the historical identifier `ICIT 3786`

**Verdict: physical object and both inscribed faces verified; historical `ICIT 3786` join strongly supported by corpus uniqueness (1 of 4,695 objects) but formally provisional.**

Four independent primary records bind CISI `H-904` (Lipi family `1786`) to Vats 1940 Plate XCVI no. 477 and excavation number `J213` from Mound D at Harappa:

| Field | Vats 1940 (p. 349, Pl. XCVI no. 477) | CISI 2 (p. 338 plate, p. 444 basic data) | Lipi export (`1786.1`, `1786.2`) |
|---|---|---|---|
| Catalogue and concordance ID | No. 477 | `H-904`, FC `3477` (3000 + 477) | `H-904`, family `1786` |
| Excavation registration | `J213`, Mound D, depth 2 ft 0 in | `J 213` | `J213 (D)477`, Stratum I, -2.0 ft |
| Material and dimensions | White steatite, type h, 0.65 × 0.28 in | Rectangular incised tablet, no iconography | White steatite `TAB:I`, 16.5 × 7.1 mm |
| Museum and photo source | Not printed | `HM 434`, `52.10xx`; photo `P 1214` | Not recorded |

Earlier inspection of Vats 1940 Plate XCVI no. 477 left the short strokes on the `840` face unresolved because of halftone blur. The CISI 2 plate on printed p. 338 (PDF p. 373) and its Lipi crops (`H-904_A.jpg`, `H-904_B.jpg`) are sharp on both sides and confirm the exact same tablet chip-for-chip:

- **Face A (`H-904 A`)**: visual left-to-right shows jar `740`, two full-height long strokes (`032`), double-arc `840`, and two shorter vertical strokes (`002`) in the upper and middle register near the slightly worn right edge. Reading order (right-to-left) is `002-840-032-740`.
- **Face B (`H-904 B`)**: visual left-to-right shows tall vessel `700`, three full-height long strokes (`033`), crescent `900`, cross `645`, `368`, and `817`. Reading order (right-to-left) is `817-368-645-900-033-700`.

This resolves the conflict noted in [numerical_source_audit.md](../../research/literature/metrology/numerical_source_audit.md). Fuls (2020 and 2023, printed p. 30) described three long strokes beside `W700` and `W900` while printing the code `W032`. In Wells and ICIT coding, `W033` denotes three long strokes (visible on `H-904 B`) and `W032` denotes two long strokes (visible on `H-904 A`). Fuls's prose coefficient of three is graphically accurate for `H-904 B`, and his label `W032` on that face is a typographical slip for `W033`.

Across all 4,695 provisional objects (5,680 faces) in `lipi_observed_faces.jsonl`, `H-904` (family `1786`) is the sole multi-face object carrying `900` on one face and `840` on the opposite face. Current Lipi family `3786` is `M-1540`, a single-face Mohenjo-daro copper tablet (`DK10076`, seven signs `806-845-061-407-850-900-740`), confirming that `ICIT 3786` in Fuls's paper reflects either ICIT database renumbering or a leading-digit slip relative to `1786`. Under the strict decision rule in [Q-0011](../../knowledge/questions/Q-0011-audit-the-held-h904-historical-join.md), we keep the historical identifier join `ICIT 3786` to `H-904` formally provisional until Figure 16 or an authenticated ICIT concordance is inspected.

**Implication for `F-0006` and Paper 003.** Confirming three long strokes on Face B and two long plus two short strokes on Face A removes the two-stroke graphic sensitivity branch for `H-904`. It leaves the core semantic gap untouched: Face A carries one unmodelled sign (`740`) and Face B carries three unmodelled signs (`817-368-645`), and no archaeological evidence shows that the two faces state equal quantities of a shared commodity or that those four signs can be set aside.

### `Q-0012`: `M-1383` and the stoneware-bangle count

**Verdict: physical identity as a stoneware-bangle firing container sealing confirmed; the 82-fragment and 15 to 20 bangle count fails verification in all held primary sources and fails to isolate base 10 under published saggar capacities.**

Inspecting CISI 2 plate printed p. 182 (PDF p. 217) and basic data printed p. 439 (PDF p. 474) resolves the apparent conflict between Lipi's clay-tag record (`TAG:R`, `Clay`, `Bull1`, `MN 82a`) and Fuls's description of a stoneware-bangle firing pot. The plate heading reads `MOHENJO-DARO 1382-1383 SEAL IMPRESSIONS on pots, on tags` and shows three views:

1. `M-1383 A (1)` at 15% scale shows a complete closed cylindrical terracotta firing container (saggar) with a clay sealing applied directly across its top mouth.
2. `M-1383 A (2)` shows a close-up of that oval mouth sealing bearing a unicorn-and-standard impression and seven signs (`740-575-017-031-741-060-920` visual left-to-right; `920-060-741-031-017-575-740` right-to-left). The four leftmost signs (`740-575-017-031`) are crisp on the intact clay; a diagonal fracture and surface abrasion cut across the three right-hand signs (`741-060-920`), matching Fuls's note that the opening three signs are eroded.
3. `M-1383 B` shows the broken mouth and lid cross-section of the saggar.

CISI 2 basic data p. 439 records `M-1383`, FC `0762`, excavation `MN 82a` (the 1982 Moneer area fieldwork by the German-Italian team), repository `EXB` (Excavation Branch, Karachi), and photograph source `Aachen; A (1): VSI, p. 272, C 77` (*Vergessene Städte am Indus*, Mainz 1987). Mackay 1938 Vol. I contains zero references to `MN 82a` because the saggar was recovered 44 years later. Across the entire 5,680-face corpus, `M-1383` is the sole face containing adjacent `017` and `031`.

Despite confirming the physical support, zero held primary sources establish the 82 stoneware-bangle fragments or the 15 to 20 reconstructed complete bangles that Fuls (printed p. 29) cites through Wells (2015, pp. 94–95). Neither Halim and Vidale (1984, *Interim Reports Vol. 1*, pp. 63–97), nor *Vergessene Städte am Indus* (1987, p. 272, C 77), nor Wells (2015, pp. 94–95) is held in full locally. The two primary stoneware studies we do hold tell a broader technological story:

- **Vidale 1987** (*More Evidence on a Protohistoric Ceramic Puzzle*, *Interim Reports Vol. 2*, pp. 105–111) examines a 1984–1985 DK-B,C fused kiln-slag block containing two directly attested bangles inside one inner bowl and gives a conjectural total of 10 bangles (five bowls of two, noting an apparent seven-bowl anomaly), with no mention of `M-1383`, `MN 82a`, or 82 fragments.
- **Vidale 1990** (*Stoneware Industry of the Indus Civilization: An Evolutionary Dead-End in the History of Ceramic Technology*, *Ceramics and Civilization* Vol. V, PDF pp. 9–10, Fig. 7) reconstructs large outer saggars holding 5 to 6 stacked inner saggars, each containing 2 to 3 bangles, giving a technological range of **10 to 18 bangles** per outer saggar, closed around the mouth with **three oval clay sheets impressed by a standard Indus unicorn stamp seal** before firing.

**Implication for `F-0006` and Paper 003.** The exact positive whole-number solutions to Fuls's two equations (`v = 2S - L` and `vL + 1 = 7S + 5`) are `(L, S, v) = (4, 20, 36)`, `(6, 8, 10)`, `(10, 8, 6)`, and `(36, 20, 4)`, yielding `7 + L` equal to 11, 13, 17, and 43. Fuls's unverified 15 to 20 bangle range (`8 <= L <= 13`) leaves only `(10, 8, 6)`. Substituting Vidale 1990's published saggar capacity of 10 to 18 bangles (`3 <= L <= 11`) leaves **three of the four solutions intact** (`11`, `13`, and `17`). Worse for the numerical-anchor premise, Vidale 1990 documents that potters stamped each saggar mouth three times with an ordinary unicorn stamp seal, which points to batch-level workshop or administrative sealing rather than a custom tally of that single saggar's bangle count.

## Part B: Lothal attachment geometry and frozen text-to-context test (`Q-0019`)

### Specimen audit of `L-206` and `G01` reverse views

**Verdict: narrow contrast confirmed.** All three held primary sources independently verify a deep, smooth curved concavity on `L-206` incompatible with an angular board-edge-only attachment for `G01`, and CISI 1 provides two additional primary reverse photographs (`L-124 B` and `L-190 B` and `L-190 F`) showing mutually distinct contact geometries under the same eight-sign legend.

| Witness | Locator | Recorded obverse and context | Recorded physical reverse geometry | Functional interpretation |
|---|---|---|---|---|
| Rao 1985 (MASI 78 Vol. II) | pp. 319, 321, 326; Pl. CLXII D (PDF p. 492) | No. `2077`; two seal impressions; Phase III, SRG 3, GX 10, layer 2, 3 ft 4 in | Deep curved U-shaped groove visible in two plate views; text notes "deep groove" (p. 321) and "reed-mark" (p. 326) | Stick or reed covering a cargo package |
| Joshi and Parpola 1987 (CISI 1) | Plate p. 286 (`L-206 A 1-2`, PDF p. 322); basic data p. 373 | `L-206`, FC `6016`, excav. `2077`, `LTH SRG 1203`, ASI photo; two impressions (`1` on flank, `2` carrying `G01` legend) | High-resolution profile clearly shows a deep smooth continuous concave arc between projecting clay wings | None imposed |
| Frenez and Tosi 2005 | p. 74, Table 1 p. 94, Fig. 3 p. 98 | `L-206`, 2 impressions, context `W` | Cone-arc shaped section with broad smooth curved inner recess (three views matching CISI 1 profile) | Polished cylindrical wooden peg on a wall |

Rao 1985 and Frenez and Tosi 2005 disagree on the functional object (package stick or reed versus cylindrical wall peg), yet both their descriptions and all three plates (`Pl. CLXII D`, CISI 1 p. 286, Fig. 3) agree on the underlying geometry: a smooth continuous cylindrical recess. Moreover, CISI 1 preserves clear reverse photographs for two other `G01` specimens: `L-124 B` (p. 268) shows crisp crossing interlaced straw or matting on an irregular curved back, while `L-190 B` and `L-190 F` (p. 282) show a sharp longitudinal channel flanked by parallel transverse striations on a T-section structural contact. Thus three independently photographed `G01` sealings exhibit physically distinct contact geometries.

### Complete 93-sealing attachment distribution

Coding all 93 Lothal sealings (`L-124` through `L-216`) strictly from Frenez and Tosi Table 1 and physical reverse prose in [lothal-attachments-v1.csv](lothal-attachments-v1.csv) yields 74 diagnostic reverses and 19 unidentifiable or unclassified reverses:

| Six-class reverse taxonomy | Count (all 93) | Frenez and Tosi Table 1 subtypes | Joined in Lipi (68) | Diagnostic Pop B (55) | Complete Pop A (26) |
|---|---:|---|---:|---:|---:|
| `wood_plank_peg` | 43 | `wooden_box` (15), `structure` (10), `locker` (9), `peg_on_wall` (9) | 32 | 32 | 19 |
| `jar_vessel_pottery` | 21 | `pottery` (21) | 14 | 14 | 2 |
| `reed_cane_matting` | 7 | `parallel_canes` (5), `woven_straw` (1), `wicker` (1) | 7 | 7 | 4 |
| `flexible_cloth_leather` | 2 | `leather_sack` (2) | 1 | 1 | 1 |
| `cord_rope_only` | 1 | `single_rope` (1) | 1 | 1 | 0 |
| `unidentifiable_other` | 19 | `undiagnostic` (18), `other` (1) | 13 | 0 | 0 |

Across the 73 diagnostic sealings with a container-versus-fixture assignment, 45 are mobile containers and 28 are architectural fixtures. Comparing Rao 1985 printed pp. 319–328 against Frenez and Tosi 2005 identifies eight specimen-level discrepancies flagged in [lothal-attachments-v1.csv](lothal-attachments-v1.csv): the Plate CLXI F conflict entangling `L-161` (`1830`) and `L-164` (`1864`), plus six reverse-surface reinterpretations (`L-125`, `L-126`, `L-128`, `L-190`, `L-193`, and `L-206`) where Rao's report labels diverse linear or concave traces as "reed-mark" or "plain".

### Frozen die-grouped permutation and cross-validation tests

Joining the 93 sealings to `lipi_observed_faces.jsonl` recovers 68 objects (86 faces), 29 complete clean single-line texts of length at least three (26 with diagnostic reverses in Population A, forming **9 strict die components**), and 55 diagnostic sealings with at least one legible sign in Population B (forming **36 strict die components**; the conservative substring partition produces the exact same 36 components). Every Leave-One-Component-Out (LOCO) cross-validation split and every component-block permutation (`B = 10,000` for Naive Bayes and association tests; `B = 1,000` for L2 logistic regression; seed `20261123`) holds each die component intact so repeated impressions of `G01` (`n = 11` diagnostic in Pop B, including `L-189` and `L-198` via Frenez and Tosi p. 84) and `G02` (`n = 10`, `L-161` through `L-170`) never leak across folds.

**Prediction fails to beat chance or baselines.** Across all pre-registered targets, populations, and models, component-held-out prediction does not exceed the component-block permutation null or die-grouped prior baselines:

| Test (Population, target, model) | Specimens / Components | Comp.-weighted bal. acc. | Null mean | Perm. `p` | Comp.-prior baseline | Spec.-weighted bal. acc. (`p`) |
|---|---:|---:|---:|---:|---:|---:|
| Pop A, 5-class diagnostic, Naive Bayes | 26 / 9 | 0.2339 | 0.2116 | 0.3944 | 0.2500 | 0.2467 (0.3357) |
| Pop A, 5-class diagnostic, LogReg | 26 / 9 | 0.2339 | 0.2030 | 0.3706 | 0.2500 | 0.2467 (0.3437) |
| Pop A, wood vs. non-wood, Naive Bayes | 26 / 9 | 0.5145 | 0.4250 | 0.3301 | 0.5000 | 0.6541 (0.1305) |
| Pop B, 5-class diagnostic, Naive Bayes | 55 / 36 | 0.2261 | 0.1817 | 0.2099 | 0.2000 | 0.2411 (0.1489) |
| Pop B, 5-class diagnostic, LogReg | 55 / 36 | 0.1911 | 0.1787 | 0.3946 | 0.2000 | 0.1723 (0.5255) |
| Pop B, wood vs. non-wood, Naive Bayes | 55 / 36 | 0.4553 | 0.4755 | 0.5831 | 0.5000 | 0.5421 (0.3145) |
| Pop B, wood vs. non-wood, LogReg | 55 / 36 | 0.6013 | 0.5023 | 0.1808 | 0.5000 | 0.6264 (0.1538) |
| Pop B, mobile vs. fixture, Naive Bayes | 54 / 35 | 0.2903 | 0.4775 | 0.9623 | 0.5000 | 0.2429 (0.9848) |

**Individual script features show zero association with container class.** In Population B (`n = 55`, `K = 36`, component-equal weighting), text length (`|rho| = 0.1423`, `p = 0.3889` against wood; `0.0552`, `p = 0.7484` against mobility), closing sign (`NMI = 0.1444`, `p = 0.7947` against 5-class; `0.0206`, `p = 0.9548` against wood), and presence of Wells and Lipi stroke numerals `001`–`045` (`NMI = 0.0223`, `p = 0.9424` against 5-class; `0.0017`, `p = 0.8965` against wood) all track random expectation. In Population A (`K = 9`), stroke numerals have zero variation (`NMI = 0.0000`, `p = 1.0000`) and closing sign yields `NMI = 0.4228` (`p = 0.0808`).

**An unadjusted motif contrast vanishes under documented-context control.** In unadjusted Population B (`K = 36`), the Lipi `animal_motif` field shows a nominal association with binary wood versus non-wood (`Cramer's V = 0.4497`, `p = 0.0275`; `NMI = 0.1346`, `p = 0.0342`). Inspecting the contingency table shows that this contrast separates records with an observed animal motif (`Bull1`: 11.0 wood vs. 6.0 non-wood; `Elep`: 1.0 wood vs. 0 non-wood) from partial or damaged impressions lacking a recorded motif (`None_or_dash`: 3.64 wood vs. 12.36 non-wood, mostly pottery rims). When we apply our prespecified documented-findspot control (`W` vs. `O`, excluding stamp-derived `W1` and unprovenanced `?`, `n = 31`, `K = 15`, within-context permutation), the motif association disappears (`Cramer's V = 0.4039`, `p = 0.2549` for wood; `p = 0.2876` for 5-class). Among complete Population A seals, motif is completely null (`p = 0.6386`).

**Sensitivity controls confirm stability against Rao Plate CLXI F and `G02`.** Dropping both contested objects `L-161` and `L-164` (`n = 53`, `K = 36`) leaves every component-weighted metric unchanged (`LOCO comp_bal_acc = 0.2261`, `p = 0.2099`) because eight remaining impressions retain the `G02` component intact. Dropping the entire `G02` elephant component (`n = 45`, `K = 35`) yields `LOCO comp_bal_acc = 0.2598` (`p = 0.0843`), confirming that `G02` did not mask an underlying text-to-container rule among the remaining 35 seals.

**Within-component dispersion quantifies two contrasting sealing roles.** Comparing the two multi-impression components in Population B against random groupings of equal size (`B = 10,000`) isolates a stark structural split:

| Component | Diagnostic specimens | 5-class counts | 5-class entropy (null) | `p` (more homogeneous) | 12-class entropy (null) | `p` (more homogeneous) |
|---|---:|---|---:|---:|---:|---:|
| `G01` (`L-124` group) | 11 | 7 wood, 2 pottery, 1 reed, 1 leather | 1.4911 bits (1.3347) | 0.6963 | 2.2222 bits (2.2631) | 0.4362 |
| `G02` (`L-161`–`L-170`) | 10 | 10 wood (`wooden_box`) | 0.0000 bits (1.3084) | 0.0022 | 0.0000 bits (2.2051) | 0.0001 |

A single eight-sign unicorn seal (`G01`) spans six of Frenez and Tosi's twelve physical types and four of five coarse reverse classes, showing dispersion statistically indistinguishable from a random draw across the entire Lothal assemblage (`p = 0.6963`). By contrast, the four-sign elephant seal (`G02`) is confined exclusively to polished wooden boxes with fingernail tallies (`p = 0.0001` in 12-class taxonomy).

## Verification

Our standalone script [verify.py](verify.py) ran ten independent checks and passed all ten (`10/10`, recorded in [verification-v1.json](verification-v1.json)): protocol SHA-256 integrity, 100% row-level and cell-level match across all 93 sealings against both `reviewed-pass.csv` and `independent-first-pass.csv`, independent deterministic recomputation of all reverse taxonomy columns, presence of the `L-161`, `L-164`, and `L-206` discrepancy flags, exact Lipi join totals (68 objects, 86 faces, 29 complete texts), strict component partitioning with zero fold leakage for `G01` and `G02`, brute-force re-solution of Fuls's Diophantine equations over `1 <= L, S <= 2000`, corpus-wide uniqueness rechecks for `H-904` and `M-1383`, and existence of every referenced local plate render.

## Boldest supported reading and deciding test

**Boldest supported reading.** Neither the published Mohenjo-daro and Harappa numeral anchors nor the Lothal sealing archive supports treating standard Indus stamp-seal inscriptions as commodity or container counts. At Lothal, seal legends identify individual seal-holders or administrative offices rather than container types, fastening mechanics, or packaged commodities: one official (`G01`) stamped the same eight-sign legend onto jars, woven-straw covers, leather bags, wooden boxes, structural gratings, and wall pegs, while another (`G02`) managed a specialized wooden-box routine with separate fingernail tallies on the clay margin. By the same administrative logic, the unicorn-stamped saggar sealing `M-1383` applied in sets of three around a stoneware firing pot records workshop or official authorization rather than an exact batch count of 17 bangles, leaving Fuls's base-10 selection without a verified physical scale anchor.

**Deciding test.** Two targeted acquisitions would decide these claims cleanly. First, obtain Halim and Vidale (1984, *Interim Reports Vol. 1*, pp. 63–97), *Vergessene Städte am Indus* (1987, p. 272, C 77), and Wells (2015, pp. 94–95) to check whether `MN 82a` (`M-1383`) has a documented fragment refit count and whether multiple saggars sealed by the *same* unicorn seal contain different bangle counts: if two saggars bearing impressions of the same unicorn seal hold substantially different bangle totals (or if `M-1383`'s unicorn seal recurs on non-saggar contexts), the batch-count reading of `M-1383` is falsified. Second, acquire unpictured reverse photographs and die-level comparisons for the remaining 58 Lothal sealings (especially `L-171` and `L-172` and the other 11 recurrent seals counted by Frenez and Tosi p. 83) and test on a fresh withheld set of multi-impression sealings from Kalibangan, Harappa, and Mohenjo-daro whether same-die cohorts exhibit bimodal dispersion (generalist seals spanning containers versus rare specialist seals) with zero out-of-component predictive power from sign features.
