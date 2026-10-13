# Adversarial review of `review/draft-v1.md`: what remains to be found in the Indus Civilization

**Reviewer:** Claude Code CLI, model `claude-opus-5-5`.

**Evidence base:** only the supplied packet:
- the draft
- `sources-v2.json`
- `candidates-v2.json`
- the source audit and mountain notes
- `PROTOCOL.md`
- `analysis.py`
- four run-v2 outputs

I did not access external sources, run code, open figures or the GeoJSON, or read `make_map.py`. I recomputed all arithmetic by hand. Where I mention archaeological sites or controversies that are absent from the packet, they come from general disciplinary knowledge. They are marked as such and are things the author must source, not facts I verified.

---

## 1. Readiness and strongest defensible contribution

**Verdict: not ready for a final version. Major revision is needed, but it is tractable.**

Every published number the draft reproduces is arithmetically correct, and its cautions about units are sound. The problems lie in what the paper does with its evidence:

- **The "how much more" question is under-answered.** The paper leaves out the most direct quantitative evidence it already holds for the user's central question (F1). It also does not engage the estimation frameworks that a reader would expect to see tested (F2).
- **The 21 windows are too coarse to guide work.** Each covers thousands to tens of thousands of square kilometres, several overlap heavily, and none states an outcome that would count as failure (F3, F4).
- **Key anchors are missing.** Several standard sites and one well-known offshore controversy are absent. Their absence weakens the hidden-landscape argument exactly where the user asked for it (F6).
- **Chronologies are not on one scale.** Ages in BP, ka, uncalibrated BP and cal BCE sit side by side without conversion (F8).

**What survives review and constitutes the defensible contribution:**

1. **The denominator audit.** The draft separates 96/1022, 96/1056 and 142 (Early plus Mature through 2024) and refuses to blend them. This is correct and useful. The code enforces it, although only through matching scope labels (F21).
2. **The observation-chain argument (§8.1).** It explains why the number of missing sites cannot be identified from recorded counts alone, and why repeating a method that cannot detect buried sites adds nothing. This is the clearest piece of reasoning in the paper.
3. **The test template.** Each mechanism is paired with a rival explanation, a falsifying test and a comparison stratum, combined with a chronology-first rule for coastal, mountain and cave claims. The distinction between relative and global sea level is handled well.
4. **The excavation-selectivity synthesis (§3).** It draws on conservation, access, destruction and publication lag, and each constraint is tied to a dated example.

**What does not survive as a contribution:**
- The rectangles as drawn. They mostly restate the published priorities of Green, Orengo and Garcia-Molsosa.
- The synthetic artifact-yield numbers.
- The inscription-register metadata.

---

## 2. Core findings

Findings are numbered F1 onward across sections 2 to 4 so a response document can cite them. **Sci** marks a scientific problem; **Ed** marks an editorial one.

**F1. Major, Sci. The paper's best evidence on "how much more could be found" is missing from the text.**

*Passage:* Abstract and §§4.2, 5.3 and 9. The paper says it supplies "no upper bound on undiscovered sites" and offers qualitative statements instead.

*Reason:* Every intensive re-survey in the packet raised recorded counts substantially. These are the honest, local answers to the user's question, and several are absent from the manuscript:

| Re-survey observation (source) | Arithmetic | Descriptive meaning |
|---|---|---|
| Green: 169 of 199 map-feature positives unlinked to earlier reports (R10; in register, absent from text) | 169/199 = 84.9% | Most positives were not in prior reports. Some may be poorly located earlier visits. |
| Green: 64 off-map locations beyond the 199 | 64/263 = 24.3% | About a quarter of encountered sites had no map feature. |
| Garcia-Molsosa: 123 of 240 PAS sites match map features, 12 of them below 2 ha (R11; in register, absent from text) | 123/240 = 51.3% | About half of an independently known set has no historical-map trace. |
| Orengo: 266 of 337 clusters unmatched | 266/337 = 78.9% | Remote proposals are mostly absent from legacy lists, though identity is unconfirmed. |
| Orengo, excluding the 25 training and validation mounds | (71−25)/(337−25) = 46/312 = 14.7% matched | The overlap between the classifier and legacy lists, beyond the reference set. |
| Masudpur: legacy entry of 4 mounds at one coordinate becomes 13 mapped mounds (R29) | ×3.25 | Unit splitting under intensive mapping. |

*Fix:* Add a "re-survey yield" table to §4 or §9 carrying each source's population, period scope and selection rule. State that in every region re-examined with a new method, recorded locations grew by a large fraction. State also that these ratios are selection-dependent, mix periods, and cannot be pooled or extrapolated. This answers the user's question with evidence rather than with a refusal.

---

**F2. Major, Sci. Overlap-based estimation and discovery curves, the decisive rival frameworks, are not engaged.**

*Passage:* §8.1: "A lower bound on detection or preservation, or a validated sampling design, would be needed to obtain one."

*Reason:* The packet contains two-list overlap data, listed in F1. Two-source (Lincoln–Petersen) and multiple-list estimation are the standard tools for estimating a missing total. A reader will ask why they are not used.

The correct answer is not "impossible." It is "possible only under assumptions these data violate in a known direction":
- Remote detection and legacy recording both favour large, visible mounds. Small sites are under-represented on both lists.
- That positive dependence and heterogeneity bias naive two-list estimates **downward**.
- A size-stratified overlap estimate with matched footprints and period scope would therefore give at most a rough floor, not a total.

A discovery-curve analysis is a second rival. It plots cumulative first-reports against survey effort or date by district. A region still rising steeply is under-explored; a plateau is weak evidence of saturation.

*Fix:* Add a subsection to §8 that does three things:
- Names both approaches.
- States the closure requirements (same footprint, period, and site definition) and the dependence and heterogeneity problems.
- Lists the data each would need. For example, the count of legacy Cholistan sites inside Orengo's footprint is not in the packet, so do not compute it. MAHSA first-report dates would be needed for a discovery curve.

This turns the "no bound" position from an assertion into a demonstrated limit with a stated path forward.

---

**F3. Major, Sci. The "sampling windows" are regional and overlapping, so they cannot direct sampling.**

*Passage:* §2.3, §6 and Appendix A bounds.

*Reason:* Approximate planimetric areas, computed from the stated bounds with a spherical approximation (1° latitude ≈ 111 km; 1° longitude ≈ 111.3 km × cos of mid-latitude; marine area included):

| Window | Area (km²) | Window | Area (km²) | Window | Area (km²) |
|---|---|---|---|---|---|
| P01 | 43,300 | P08 | 17,600 | P15 | 4,850 |
| P02 | 5,310 | P09 | 13,900 | P16 | 7,110 |
| P03 | 6,770 | P10 | 3,290 | P17 | 12,900 |
| P04 | 3,740 | P11 | 30,700 | P18 | 15,900 |
| P05 | 5,130 | P12 | 3,390 | P19 | 9,370 |
| P06 | 10,300 | P13 | 2,710 | P20 | 10,300 |
| P07 | 2,690 | P14 | 22,100 | P21 | 18,000 |

The gross total is about 250,000 km², with a 16-fold range in window size.

Overlaps are large enough to collapse class distinctions:
- P02 lies entirely within P01.
- About 85% of P09 (Class C) lies within P08 (Class B), and both rest on R11 alone.
- About 60% of P07 lies within P03.
- P11 (alluvial ridge) and P18 (piedmont) share roughly 67.5–68.1°E by 25.0–26.3°N, which mixes the very strata the paper wants to contrast.

*Fix:* Do one of two things:
- Relabel the rectangles as "regions of interest" and define, inside each, named landform strata such as older alluvium versus a younger channel belt. Give each stratum a sampling unit, for example a 1 km² cell or a coring transect.
- Or clip each window to the published study footprint it relies on.

Resolve the P08/P09 and P11/P18 overlaps by landform, not by rectangle.

---

**F4. Major, Sci. The falsification tests carry no decision rules.**

*Passage:* Appendix A, "Rival and test" lines. For example, P01: "Ground-check proposed clusters; date intact occupation and compare matched noncandidate tiles."

*Reason:* No window states:
- the sampling unit
- the effort
- the number of candidate and control units
- whether surveyors will be blind to which units are candidates and which are controls
- which observed outcome would demote the hypothesis

As written, no result could fail a window. Only P04 mentions blinding.

*Fix:* Add four fields to each entry: unit, effort, minimum comparison, and pre-declared demotion outcome. A demotion outcome can be stated without invented numbers. Example: "candidate and matched non-candidate tiles show no difference in datable cultural material under equal blind effort." Another: "no core reaches a dated target-age surface within reachable depth." Require blind candidate/control assignment for all surface checks.

---

**F5. Major, Sci and Ed. The paper both claims and denies that its classes are priorities, and never states a priority.**

*Passage:* §2.3 says the classes "are neither probabilities of discovery nor an assessment of current field access." `candidates-v2.json` uses `"priority_classes"` and `"priority_class"`, and §6 refers to "priority classes."

*Reason:* The protocol's item 4 asks for a comparison under explicit information, preservation and feasibility criteria. §6 lists three agendas but applies no criteria to the windows and chooses none. A reader cannot tell what the author would actually do first.

*Fix:* Rename the classes to "evidence class" everywhere, including the JSON, GeoJSON and figure legend. Then state an explicit, reasoned first priority and a second (section 5 below), and score each window on the protocol's three criteria using ordinal labels with a one-line justification.

---

**F6. Major, Sci. Standard anchors and a known controversy are missing for the user's hidden settings.**

These are reviewer knowledge, not in the packet. The author must source each one before use.

- **Beneath alluvium.**
  - Mohenjo-daro's earliest deposits are widely reported to lie below the modern plain and water table. This is the canonical Indus case of alluvial burial; the draft uses Moenjodaro only for conservation.
  - Kalibangan, a major excavated Ghaggar site, appears to fall inside P06 and is never mentioned.
- **Beneath later settlement.** The commonest case in northwest India is a living village sitting on a mound, which is widely reported at Rakhigarhi. The draft treats only the industrial-city case (Sukkur).
- **Destruction pathways.** Three well-known pathways are omitted:
  - historical brick robbing (Harappa bricks used as railway ballast)
  - clay extraction for brick kilns
  - looting of Balochistan sites
- **Former coasts now inland.**
  - Dholavira and the Rann of Kutch margins are absent, even though R33 (Srivastava) concerns exactly this inland transition.
  - Sutkagen-dor and Sotka Koh, the classic Harappan sites near the Makran coast, are absent from P21 and §5.5.
- **Submerged.** §5.5's sentence about "rectangular rock patterns, isolated objects and a single old radiocarbon result" plainly alludes to the Gulf of Khambhat offshore "submerged city" claim without naming it. Name the claim, source it, and state the specific evidential failures. Allusion is less clear and less fair to readers.
- **Mountains.** The mountain section covers only Balochistan and Kirthar. The Himalayan foothill margin is absent, including Manda on the Chenab and Ropar at the Sutlej exit. That margin connects directly to R16's foothill-flood evidence. So is the Gomal valley approach. Shortugai is a reminder that Indus-affiliated presence extends far beyond the plains.

*Fix:* Add these as anchors, controls or rivals with proper sources, or explicitly justify their exclusion.

---

**F7. Moderate, Sci. The mountain evidence was lost in integration.**

*Reason:*
- The mountain notes propose five windows. Swat (window 5) was dropped, but R46 (Olivieri) remains in the reference list and is cited nowhere in the text.
- The Ghazi Shah spring corridor (window 2) was folded into P18. By my recollection, which the author must verify, Ghazi Shah lies west of Manchar Lake north of 26.3°N, outside P18's northern bound.
- Besenval's Kech-Makran account (M06), the only source on Kech floods and erosion, did not enter `sources-v2.json`. P16 therefore cites R47, a date-palm seed morphometry study that says nothing about fan aggradation.

*Fix:*
- Either restore Swat as a low-expectation boundary control or remove R46.
- Check Ghazi Shah's inventory coordinate against P18, and extend the bound or create a separate window.
- Add M06 to the register and replace R47 in P16.

---

**F8. Moderate, Sci. Chronologies are never placed on the paper's own reference scale.** Details are in section 3.

*Fix:* Add one short convention table that converts every cited age to calendar BCE, states its calibration and reservoir status, and sets it against the 2600–1900 BCE working interval.

---

**F9. Moderate, Sci. The yield section overstates what it shows and adds little.**

*Passage:* Abstract: "demonstrate sensitivity of artifact recovery to deposit density and sampling." Also §7.1.

*Reason:*
- Only density varies across the three scenarios. Area, fraction, thickness and recovery are fixed, so "sampling" sensitivity is not demonstrated.
- *d* is defined as "recoverable fragment density" and *r* as the "retained recovery fraction." The definitions overlap, which invites double-counting of recovery losses.
- The 12,000 to 1,200,000 range brackets Harappa's "almost one million potsherds" in the very next paragraph. That invites the anchoring the text disclaims.
- The output shows only that a product of terms is linear in each term.

*Fix:* Keep the formula in one sentence with *d* defined as in-ground density. Delete the three scenario numbers and the figure. Replace them with the evidence-expectation table in section 5.3 and fix the abstract wording.

---

**F10. Moderate, Sci and Ed. The inscription-register metadata is irrelevant to the question asked.**

*Passage:* §2.2 (115 and 86 entries) and Appendix B's first paragraph.

*Reason:* By the paper's own admission, these cohorts cannot measure settlement coverage. They consume reader attention and imply relevance they lack.

*Fix:* Move them to the repository README or the run notes and delete them from the manuscript.

---

**F11. Moderate, Sci. The paper leans heavily on sources it could not fully read, and the provenance of one key count is not traced.**

*Passage:* §2.1: "The source register records … local witness hash."

*Reason:* In `sources-v2.json`, 17 of 47 entries have `raw_witness: null`: R01, R02, R06, R14, R17, R23, R25, R26, R28, R29, R31, R32, R34, R36, R37, R38 and R43. Several of these carry load-bearing claims:
- the 142 count (R02)
- the 1056 count (R38)
- Masudpur and Rakhigarhi (R29)
- the Lothal sea-level fall (R32)
- the coastal middens (R31)
- the Khambhat synthesis (R34)
- Giosan (R17), which is the sole source for P11 and whose local copy was a CAPTCHA page

Separately, R01 cites "Possehl 2002 and Settar & Korisettar 2002." The draft calls R38 "Possehl's own 2002 chapter," which implies R38 is the source behind the 1022 figure. That has not been established; the 406 + 616 subtotals may derive from the edited volume. The 142 is also Gadekar's extension of Uesugi's compilation, an attribution the audit records but the draft omits.

*Fix:*
- In §2.1, state that 30 of 47 sources have local witnesses and name the load-bearing exceptions.
- Phrase §3.1 as "two historical totals of 1022 and 1056, whose source inventories have not been traced to a common compilation."
- Attribute the 142 to Gadekar's extension of Uesugi.

---

**F12. Moderate, Ed (with scientific consequence). Review independence is mislabelled.**

*Passage:* "Review and data availability": "independent Codex adversarial reading and a Claude Code Opus-5.5 CLI review." The audit is also titled "Independent source audit."

*Reason:* The protocol says to "report this as author-led adversarial review unless an independent reviewer is actually engaged." AI model reviews commissioned within the project are not independent peer review.

*Fix:* Describe these as "AI-model adversarial reviews commissioned by the author." Record that this review was returned by `claude-opus-5-5` and worked from a supplied packet without external access.

---

**F13. Moderate, Ed. Repeated cautions and boilerplate impede comprehension.**

*Reason:* Most paragraphs end with a "does not establish" or "rather than" clause. Examples include the two consecutive negations in §4.1 on Ganweriwala, and the negations in §4.2, §5.3 and §5.4. Each Appendix entry repeats "Bounds have 0.1-degree editorial precision; access has not been assessed," 21 times in total. The title and correction metadata for *Hidden in Plain Sight* in §2.1 is register detail, not argument.

*Fix:*
- Gather the shared assumptions once, in a short §2.4 ("What every number and window in this paper does and does not mean"), and write later sections as positive statements.
- Put the boilerplate once at the head of Appendix A.
- Move publication-metadata asides to the register.

---

## 3. Source, chronology, attribution and numerical errors

**Arithmetic independently confirmed** (no errors found):
- 96/1022 = 9.39% and 96/1056 = 9.09%.
- 337 − 71 = 266, and 246/337 = 73.0%.
- Green's Table 1: all twelve recovered integers reproduce the displayed percentages, for example 68/116 = 58.62%, 16/201 = 7.96% and 12/76 = 15.79%. Uniqueness holds because 100/n far exceeds 0.01 at these denominators.
- Green's row and column totals: 393/150, 154/21, 227/26 and 5/2 by symbol; 501/86, 220/91 and 58/22 by size class. The grand total is 779/199 = 25.55%.
- Square equivalents: 100, 223.6, 547.7, 816.7 and 1414.2 m.
- Kotada's 100 × 60 m = 0.6 ha. Ghazi Shah's 160 × 130 m = 2.08 ha (mountain notes).
- 30 ha × 0.01 × 1 m = 3,000 m³, giving 12,000, 120,000 and 1,200,000 fragments.
- 1 − 0.9¹⁰ = 0.6513. 200 × 0.5 = 1,000 × 0.1 = 100.
- Metadata partitions: 72 + 13 + 3 + 27 = 115; South Asian coordinates 2 + 47 + 27 = 76; phases 6 + 123 + 84 = 213; radiocarbon labels 0 + 33 + 16 = 49; sites with radiocarbon 0 + 19 + 9 = 28.

**Errors and unsupported statements:**

1. **"six above 20 ha" (§4.2).** This figure is not in the R08 register observation. Add a locator or remove it.
2. **The 71 legacy matches include the 25 reference mounds.** State the non-reference overlap of 46 of 312 (F1) wherever the 71 appears, so readers do not take 71/337 as a measure of recall.
3. **Green's symbol counts (§5.3)** are recovered from rounded percentages, not printed in the source. Say "recovered from Table 1 percentages."
4. **"199 of 779" in the abstract.** Add "of any period." The positives include Painted Grey Ware and historic material.
5. **Green's selection rules.** Specify "ten negative locations per regional grid unit (2017)" rather than "after negative visits." Also state the bias directions:
   - The 2018 pre-filter, which excluded apparent ponds and dunes, should raise the checked positive rate above that of all mapped features.
   - The stopping rule's direction depends on heterogeneity between grid units, so it cannot be signed.
   
   This lets the paper say something stronger than "cannot generalize."
6. **Das 2022 (§5.5).** State whether 4150 ± 230 BP and 3625 ± 200 BP are calibrated. If they are calendar BP, they correspond to about 2200 BCE (2430–1970) and about 1675 BCE (1875–1475). The fall would then begin inside the Mature interval and continue past it, which is the archaeologically relevant point and is currently left implicit.
7. **Singh 2021.** 3.9–3.8 ka is roughly 1950–1850 BCE, straddling the paper's own 1900 BCE reference boundary. Say so. These are the flows most relevant to late Mature occupation of the Ghaggar flanks, not merely "a different phenomenon."
8. **Biagi 2024 (uncalibrated BP, marine shell).** The draft handles this correctly. Keep it, and add it to the conversion table as "not convertible without reservoir correction."
9. **Srivastava 2023 inconsistency.** The catch is correct: 3000 BP is about 1050 BCE, against 4750–3750 BP for 2800–1800 BCE. Move it from the main text to the source register or a footnote, since it is an erratum note about another paper.
10. **The Mehrgarh 2025 tooth-enamel chronology (§5.4)** is accurate but tangential to the Bronze Age burial argument. Shorten it to a clause or remove it.
11. **The Kech seed paragraph (§7.2)** audits a cohort irrelevant to the paper's question. Its last sentence ("motivate testing modern-date-grove analogies") is also unclear. Remove it (section 6).
12. **"Kirthar piedmont already has an active archaeological research history" (§5.4).** R37's page date is unverified, so "active" is unsupported. Use "an established."
13. **Figure 1 label "Legacy site boundary".** The 81.5 ha estimate has an uncertain procedure, so "boundary" implies a mapped polygon that may not exist. Use "Legacy area estimate."
14. **The MAHSA figure of about 10,000 all-period legacy entries (R13)** is in the register but missing from §3.1. It is the most current scale reference available. Add it with its all-period scope.
15. **The Rakhigarhi 127 locations (§4.3)** need the survey radius from the register (15 km) to be meaningful.
16. **Window source fit:**
    - P15 cites R32 (Lothal) for the south Saurashtra coast. That transfers a different coastal setting.
    - P21 cites R26, an inland site, and R31, which covers Siranda and Lower Sindh, so nothing is specific to the Gwadar–Pasni coast.
    - P14 rests on R18 alone, a SAR ecology paper, which is weak for Class B.
    - P12 rests on two institutional notices (R20, R28) describing existing projects. It should be marked "existing project; coordinate, do not duplicate" rather than offered as a window.
17. **References:**
    - R35 and R46 are listed but uncited.
    - The order runs R47, R46, R43, R44, R45.
    - `published-count-arithmetic.json` and `historical-map-checks.json` use source IDs (LUCKNOW_CHAPTER, GADEKAR2026, ORENGO2020, GREEN2019) that do not join to the R-numbers. Harmonize them so claims can be audited by machine.
18. **"approximately 96" (R01) is reported as an exact 96.** Retain the source's qualifier.
19. **Conversion artifacts:**
    - "# # Abstract" heading.
    - Missing spaces: "itsJanuary", "Cholistan,337", "matches;266", "Gulzar'sDecember", "PeriodIcemetery", "isV=10000 Afh", "fragments/m³give", "uncalibratedBP", "colleagues'2022", "isN q", "andq=0.5", "havepnear", "SupplementS 1", "digitalchapter".
    - "CholistanP 01-P02" and similar in the §6 table.
    - "AppendixA/B", "ClassA/B/C", "Figure1".

**Cultural attribution.** The attribution handling is generally careful. Miri Qalat is treated as a long local sequence, Nausharo as local traditions with Harappan seals, Kotada as mixed periods, and caves as unattributed. I found no case in which a non-Indus Bronze Age community is labelled Harappan.

---

## 4. Prediction, sampling and geography flaws; omitted rivals

**F14. Moderate, Sci. The geometry of some windows does not match its own labels.** These points come from reviewer recollection of approximate coordinates and must be checked against the GeoJSON with anchor points added.

- **P11 "Dadu–Badin" [67.5, 24.7, 68.7, 27.0].** Badin town lies at roughly 68.8°E, 24.65°N, outside the box.
- **P01 "Eastern Cholistan" [70–72°E, 27.8–29.8°N].** At about 43,000 km², it appears to cross the international border into Indian territory to the southeast. It also appears to include the irrigated Indus plain around Rahim Yar Khan and Bahawalpur. "Eastern" does not describe a box that spans the whole desert.
- **P15 [western bound 70.4°E].** This bound sits near the Veraval–Somnath coast, where Kaj and Kanjetar are commonly placed. Verify that the named anchors fall inside.
- **P18 and Ghazi Shah** (F7).

*Fix:* Add anchor-point coordinates for every named site to `candidates-v2.json`. Add a point-in-box check to the verification suite, so a window can never omit its namesake.

---

**F15. Major, Sci. The design confounds discovery with effort.**

All Class A windows, and most Class B, sit where survey effort is already highest. Any discovery rate measured there will mix the underlying settlement density with prior effort, as §4.3 itself recognizes but the design does not address. No stratum samples low prior effort.

*Fix:*
- Record prior effort per stratum: published survey coverage and years.
- Include at least one comparable landform stratum with little prior survey.
- Report results normalized by effort.

Without this, the agenda cannot answer "how much more."

---

**F16. Moderate, Sci. Detection heterogeneity by size is acknowledged but not designed for.**

The classifier references are large mounds, 246 of 337 proposals are under 5 ha, and Green's size-1 class has the lowest rate (86/501 = 17.2%).

*Fix:* Stratify every ground-truthing sample by size class. Report positive predictive value per size class, meaning the fraction of proposed candidates that prove archaeological. It is the quantity that converts candidates into an expected count.

---

**F17. Moderate, Sci. Some omitted rivals change the reading of the evidence.**

- **Settlement mobility and short-lived occupation.** Many small locations may be successive phases of a few mobile villages. This affects both counts and "missing" totals.
- **Incidental exposure.** A century of canal digging, tube wells, brick-kiln pits and construction across the Punjab plains both destroys and exposes sites. This makes a wholly unnoticed large buried city less plausible than many small ones, in the same direction as §4.2's argument. Frame it as a hypothesis to evaluate, not a finding.
- **Tectonic setting on Makran (P21).** The Makran coast is commonly described as uplifting, with raised marine terraces. If local evidence confirms this, the expected position of Indus-period shores there is raised or inland, not submerged. P21 lists "possible inundation" and "raised terraces" together without saying which the local evidence favours. Source the tectonic regime and re-frame P21 so that submergence is the rival explanation.
- **Borders and security.** Constraints are noted for Ganweriwala but not for P01, P16, P21 or other windows near borders. Feasibility is "not assessed," which is acceptable, but should be flagged where it is foreseeably decisive.

---

**F18. Minor, Sci. Landslides.** The draft concedes that no evidence of landslide burial was found in the Indus contexts it reviewed. Keep landslides as one paragraph of mechanism and remove them from window labels and comparison strata, where they read as a target.

---

## 5. Recommendations for a usable pilot, a truthful priority and artifact expectations

### 5.1 Truthful first priority: a desk-based concordance pilot

Build a reconciled register of three published sets against MAHSA and published gazetteers:
- Orengo's 337 clusters
- Green's 779 checked features plus 64 off-map locations
- Garcia-Molsosa's 646 mapped features and 240 PAS sites

Assign each record one status: already recorded, probable alias, no match, or coordinates insufficient. Also record the coordinate offset and whether a period assignment is available.

**Why this is first:**
- It needs no permits.
- It uses published data plus MAHSA access, which requires partner agreement and is not just "existence checked."
- It directly converts "266 unmatched" into the number of candidates absent from any accessible record, which is the honest local answer to "how much is new."
- It supplies the overlap data that F2's estimators need.
- It prevents rediscovery claims.

**Deliverables:** the register, size-stratified match rates, and, if MAHSA first-report dates exist, a district discovery curve.

**Decision rule:** if most unmatched candidates prove to be aliases, field effort shifts from discovery to phase and extent mapping.

### 5.2 Conditional second priorities, each needing a named partner

**(a) Blind ground-truthing in Cholistan (P01).** Use a size-stratified random subsample of the unmatched clusters plus matched non-candidate tiles, with equal effort and blind assignment. This yields the first positive predictive value by size class. It is the single number most needed to turn remote proposals into expected sites.

**(b) One paired-landform coring test.** Use P08's older-versus-younger alluvium (Garcia-Molsosa) or P06's flank-versus-channel contrast. Declare in advance:
- the transects
- the core count
- the reachable depth
- the criteria for recognizing the target surface
- the dating budget
- the demotion rule

Report negative cores. This is the only proposed test that measures burial rather than visibility.

**Defer to desk-chronology only:** P15, P19, P20 and P21 (coasts), plus caves. The first deliverable for each is a dated, local relative sea-level or landform age argument from existing literature. That is cheap to reject, consistent with §6's own principle.

### 5.3 Artifact expectations

Replace the yield numbers with a table by setting. Columns:
- the evidence classes realistically expected
- the minimum diagnostic for Indus attribution
- the principal failure mode

Qualitative rows, without counts:

| Setting | Realistic expectation |
|---|---|
| Small rural and buried sites | Ceramics, debitage, bone and plant remains. Low counts but high information per sample. |
| Urban rescue contexts | Mixed or redeposited material is likely. Value lies in intact lower contexts. |
| Caves | Small assemblages. Value lies in dated hearths and floors. |
| Offshore | Effectively no recoverable in-situ evidence until chronology is established. |
| Seals and inscribed objects | Rare and clustered by context (Harappa's season-to-season variation). No rate is estimable. |

---

## 6. Claims to remove

1. The three synthetic yield values (12,000, 120,000 and 1,200,000), their figure, and the abstract's "and sampling."
2. Inscription-register metadata in §2.2 and Appendix B.
3. The Kech date-seed paragraph in §7.2.
4. "They do not authenticate a proposed decipherment by themselves" (§7.2). It is an unprompted corrective aside that the argument does not need.
5. "six above 20 ha," unless a locator is added.
6. "active" for the Kirthar research history.
7. "Dadu–Badin" as a name, if Badin is confirmed outside the window.
8. "independent" for the commissioned AI reviews and audit.
9. The 21 repeated boilerplate sentences in Appendix A, and the *Hidden in Plain Sight* title and correction details in §2.1 (move them to the register).
10. R35 and R46, unless they are cited in the text.
11. "Local landform chronology controls these proposals" in the abstract. It is vague; state the chronology-first rule plainly instead.

---

## 7. Checks performed and checks unavailable

**Performed:**
- Recomputed every ratio, percentage, area, volume, yield and probability in the draft and run-v2 outputs (section 3), including Green's 12-cell integer recovery, its uniqueness, and both marginal partitions.
- Recomputed metadata partitions from `metadata-coverage.json`.
- Computed window areas, overlaps and containment from `candidates-v2.json` bounds.
- Cross-checked every in-text citation against the reference list and `sources-v2.json` (uncited references, ordering, null witnesses).
- Compared the mountain notes' windows and sources against the integrated draft (lost Swat window, lost M06, merged Ghazi Shah).
- Checked the draft against `PROTOCOL.md` items 1–5 and the review clause.
- Compared each window's cited sources with its claimed mechanism.
- Read `analysis.py` conceptually. Findings:
  - `two_cohorts_remain_distinct` only tests 85 ≠ 86, so it would fail if the counts happened to match and pass if the cohorts were merged. Replace it with a real record-level join test or delete it.
  - `scoped_percent` guards only by equality of label strings.
  - `green_published_totals` checks the transcription against hard-coded totals from the same table.
  - The `manifest` amendment block is unconditional, so a fresh rerun would claim the Possehl amendment regardless. Pass it as an argument.
  - Several checks use exact float equality. They pass at these values but are fragile.
  - The figure of 49 checks includes 12 identical rounding checks and 13 input-validation mutation tests, so the number should not be presented as evidential weight.

**Unavailable:**
- Any external source, full text, supplement or database, including MAHSA, Green's Supplement S1, the Orengo legacy footprint, and Gadekar's and Possehl's full texts.
- Verification of source hashes or witness contents.
- Code execution, output regeneration, and inspection of rendered figures.
- `make_map.py` and the GeoJSON.
- Authoritative coordinates for anchor sites. The F14 geometry flags rest on my approximate recollection and are requests for verification, not findings.
- Whether the input metadata files are tracked for clean-clone reproduction.
- Every site, controversy and tectonic characterization I name in F6 and F17 as absent from the packet. These come from general knowledge and must be sourced by the author before use.
