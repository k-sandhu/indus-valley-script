# V2 adversarial review: Indus settlement working paper (pre-final revision)

**Scope.** This review uses only the supplied packet. I did not retrieve sources, run code, inspect figure pixels or check against the repository. Where I rely on my own knowledge, I mark it as unverified. This is a commissioned AI-model pass, not peer review.

## Readiness verdict

**Ready for the final write-up after targeted corrections. No redesign is needed.** The revision substantively addresses the prior major issues:

- Repeat-survey units and selection are stated.
- Capture–recapture is no longer treated as a floor.
- Reachability and preservation are separated.
- Cap, substrate and occupation ages are distinguished.
- The Cambay cores are acknowledged.
- Synthetic yields are removed.
- The design review's clarifications 1–2 and the P04, P16 and P17 rules are integrated.

**Arithmetic and containment I checked against the packet; all match:**

- Every Table 2 ratio: 84.9, 24.3, 51.3, 78.9, 14.7 and 3.25.
- 246/337 = 73.0%.
- The Green symbol cells sum to 199/779.
- 96/1,022 and 96/1,056.
- The square equivalents.
- The Lothal calendar conversions and midpoint ± half-widths.
- 1 − 0.9¹⁰ = 65.1%.
- 160 × 130 m = 2.08 ha, and 39 ft = 11.9 m.
- Kalibangan (both coordinates) falls in P06, Sutkagen-Dor and Pasni in P21, Kai in P18, and Ormara outside P21.

The remaining issues below are attribution, documentation and residual-logic problems that should be fixed before the final version.

---

## Material unresolved issues

### V2-F1 — Ganweriwala "2020" area is misdated or misattributed (§4.1, Figure 1)

**Passage.** "…and a 2020 estimate of approximately 33 hectares of visible mounded area… [R07,R08]"

**Problem.** The registered reading of R07, published in 2018, already lists "satellite-visible 33 ha." The registered reading of R08 (2020) contains no Ganweriwala area. As registered, the 33 ha figure predates 2020 and is not shown to come from R08. Figure 1 is explicitly about "different observations and dates," so the error propagates into the figure.

**Repair.**
- If R08 does report Ganweriwala's area, add its locator to the register and keep "2020."
- Otherwise, attribute the figure to R07 with the date and method it reports (e.g., "a satellite-visible estimate of ~33 ha reported in Gulzar 2018"), and relabel Figure 1.

### V2-F2 — Historical-ratio lineage and who read R38 (§2.1, §3.1, Abstract)

**Passages.**
- "Possehl's historical total, read in publisher extracts"
- "The underlying inventories have not been traced to a common compilation."

**Problems.**
1. The register says R38 was "read by separate author-commissioned Codex source-check pass." Section 2.1 presents this as the study's own reading. That blurs reviewer and author roles, which the review section is careful to separate elsewhere.
2. R01 itself cites "Possehl 2002." My unverified recollection is that Possehl's 2002 *The Indus Civilization: A Contemporary Perspective* gives 1,022 Mature sites split 406 Pakistan / 616 India. That matches R01's 406 + 616 subtotal. If so, the two totals are probably successive Possehl compilations (1999 appendix vs. a 2002 book), not independent summaries.
3. R01 reports "approximately 96," so 9.39% overstates precision.

**Repair.**
- Identify which Possehl 2002 work R01 cites.
- Replace "have not been traced to a common compilation" with "R01's 1,022 figure cites a Possehl 2002 source; whether it and R38's 1,056 are successive versions of one gazetteer has not been verified."
- In §2.1, state that the R38 extract was read by the commissioned Codex pass.
- Report R01's ratio as ≈9.4%.

### V2-F3 — P18 Ghazi Shah containment is undocumented (§5.4, Appendix A P18)

**Problem.** The revision summary says P18 was extended to include Ghazi Shah and Kai. Kai's coordinate (R49, 26.306 N 67.560 E) is registered and lies inside P18. R41's registered reading gives no coordinate for Ghazi Shah. My unverified recollection places Ghazi Shah near Johi in Dadu district, roughly 26.7°N, which would be north of P18's 26.6 bound. The packet cannot settle this.

**Repair.**
- Record Ghazi Shah's coordinate and its source in the R41 register entry and the candidates file.
- If it lies north of 26.6, extend P18 to the north. Otherwise, state that it is contained and give the checked point.
- Until then, do not describe the extension as including Ghazi Shah.

### V2-F4 — Residual merged or ambiguous demotion rules (Appendix A, §2.3, §6)

The P04, P16 and P17 fixes landed. Several rules still conflate premises the paper itself separates.

**P06.** "age-incompatible terrestrial conditions" can be read as rejecting an older terrace. Section 2.2 says an old terrace can support later occupation, so this reading contradicts the paper. Replace with:
> "…where adequate logs demonstrate scour or truncation of the target-age interval, or show that only younger terrestrial ground existed; older substrate alone leaves later use unresolved."

**P14.** "Demote an ancient occupation interpretation if … a different cultural period." Another period's archaeology is still occupation; this repeats the original P04 error. Replace with:
> "Demote the ancient-occupation interpretation if dated deposits support recent wetness or natural sediments; demote only the Indus attribution if dated cultural deposits belong to another period."

**P07.** The rule merges two premises: a contemporaneous catchment link (tested by dates) and off-mound concentration (tested by effort). Split it into two sentences, each with its own condition.

**P09.** The tested relationship is still unnamed. Adopt the design review's wording, which tests "contemporaneous channel use" and adds "earlier abandonment does not reject later occupation of the channel margin."

**P13.** R19 already establishes that Kotada and Morodharo are the same locality, so the "alias-independent discovery" test is already resolved. Restate P13 as a test of phase-specific exterior extent only.

**General rule.** Sections 2.3 and 6 omit spatial (lateral) coverage, which §8.3 correctly requires. Add the design review's default sentence verbatim to §6: "A negative can demote the stated premise only for inspected units with adequate effort, visibility, spatial coverage, depth and chronology…"

**Typo.** P17 ends "insufficient.." in both the appendix and the register.

### V2-F5 — Pilot inference unit and holdout use (§8.3)

**Passages.**
- "Among adequate profiles it estimates the proportion retaining the predicted terrestrial surface"
- "Eight of the 24 sampled blocks… are held aside"

**Problems.**
1. Profiles are clustered within blocks, and each stratum has only six blocks. A profile-level proportion overstates precision.
2. It is unclear whether the descriptive survival proportions use all 24 blocks or only the 16 non-holdout blocks.
3. The cover-over-margins stratum is where reachability is worst. Adequate profiles may be very few, or zero, in exactly the stratum where preservation is hypothesized.

**Repair.**
- State that the block is the inferential unit.
- Report profile counts nested within blocks, with cluster-aware intervals.
- State that descriptive survival summaries use all adequately resolved blocks, and that the holdout applies only to evaluating a fitted prediction rule.
- State that a stratum with no adequate blocks yields "unresolved," not a survival estimate.

### V2-F6 — "Ordinal" assessments lack a rubric (§2.3, §6, Appendix A preamble)

**Problems.**
- The preamble calls the information and preservation judgments "ordinal assessments," but the preservation fields are free text with no levels.
- Section 2.3 promises an "information/preservation/feasibility assessment," yet no region has a feasibility field.
- Twelve of 21 regions are rated High for information, so the scale barely discriminates.
- No criteria or assessor are stated.

**Repair.**
- Define a three-level rubric for each dimension (for example, information High = a published candidate set plus a decisive test defined).
- Give each preservation entry a level plus its rationale.
- Add an explicit "Feasibility: unverified" field to every region.
- State that the assessments are editorial judgments by the AI-assisted drafting process, not elicited expert ratings.

### V2-F7 — Overlap partitioning covers only two of the six overlaps (§2.3, §6)

**Problem.** Partition rules are given only for P08/P09 and P11/P18. The others are unaddressed:
- P02 lies entirely inside P01, and both are Class A field candidates. P01's random classifier-negative cells and P02's map-negative landforms could draw the same cells.
- P03 overlaps both P04 and P07.
- P05 overlaps P06.

**Repair.** Add one sentence: any 1 km² cell eligible under more than one region enters a single shared frame, carries all applicable labels, and is sampled once. Name P01/P02 explicitly: P02 margin transects are excluded from P01's negative draw.

### V2-F8 — Numerical provenance gaps (Appendix B, claim register)

**Problems.**
1. The v3 run reads `sources-v2.json`, while corrections live in `sources-v4.json`. The revision summary says primary omitted anchors were added. If R38 or its 1,056 figure was added after v2, the 9.09% ratio may not be produced by the declared run. Nothing in the packet shows that the numeric inputs are unchanged between v2 and v4.
2. Several numbers new to this revision have no output row in Appendix B:
   - the calendar conversions in the §2.2 table
   - 2.08 ha and 0.6 ha
   - 11.9 m
   - ~6050 BCE

**Repair.**
- Add a statement, backed by a check, that every numeric field consumed by the run is identical in v2 and v4. Otherwise, rerun the analysis against v4.
- Either add a small output for the inline conversions, or list them in the claim register as hand arithmetic, giving formula and inputs.

### V2-F9 — Review provenance and premature verification claims (Review and reproducibility, Appendix B)

**Problems.**
1. "The final checks cover source links, revised bounds, frozen hashes, reproducible outputs and the actual rendered PDF" is written before the final version and PDF exist.
2. The bounded design review, by "the statistical-methods and mountain-evidence contributor," directly shaped §8.3 and Appendix A. It is not disclosed, and the contributor's nature (human or AI model) is not identified.
3. This second Claude pass is not listed.

**Repair.**
- Write the checks sentence only after the checks are run, and report their actual results, including any failures.
- List every review pass with its type, model or role, scope and tool access: the Codex check, Claude pass 1, the bounded design review, and Claude pass 2.

### V2-F10 — "Omissions" wording outruns what the comparisons show (Abstract, §4.3, §9)

**Passages.**
- "Repeat surveys nevertheless reveal substantial omissions locally"
- "additional methods can produce substantial recorded additions"

**Problem.** The comparisons support different things:
- Only Green's field-checked positives and off-map encounters are confirmed archaeological locations absent from earlier reports, and even those are qualified by poorly located earlier visits.
- Orengo's 266 are unconfirmed proposals.
- Masudpur is unit splitting.
- The PAS→map row shows that historical maps omit known sites, not that site records omit sites.

**Repair.**
- Abstract: "Repeat field checks in one landscape found many archaeological locations absent from earlier reports; remote and cartographic comparisons identify further candidates and unit changes whose identity remains unresolved."
- §4.3: change "recorded additions" to "recorded additions and unconfirmed candidates."

### V2-F11 — Chronology footnote for ka-scale ages (§2.2 table)

**Problem.** The table converts R15 and R16 "ka" ages using a 1950 origin. My unverified understanding is that these studies rely substantially on OSL ages, which are conventionally expressed relative to the measurement year, not 1950. The difference of about 60–70 years is immaterial at "roughly," but the paper's own §2.2 says OSL ages "retain their different meanings."

**Repair.** Add a table note: "ka ages are treated as approximately calendar; where OSL-based, their reference year differs from 1950 by decades, below the stated precision."

### V2-F12 — Review-response residue and register gaps in prose (§§3.3, 5.4, 5.5, Appendix A)

These are non-blocking but should be cleared before final:

- §5.5: "Cores are part of that evidence and should be acknowledged" reads as a reply to a reviewer. Replace with "The reported evidence includes cores."
- §5.4: R42 is an archaeometric preliminary-report abstract, not a "primary excavation abstract." Say "a 2025 archaeometric report abstract records excavation at the site."
- §3.3: R21's registered observation does not cover "2017 trenches" or "deep pits mixing ancient finds with modern garbage." Add these to the claim register, or trim them to the registered reading.
- Appendix A has concatenation artifacts: "Compare Size-stratified," "Compare Known-context," "Mechanism: Alluvial."

---

## Status of prior major issues

| Prior issue | Status |
|---|---|
| Repeat-survey table with units and selection | Resolved |
| Capture–recapture, dependence, effort curves | Resolved; the invisible-class sentence was adopted |
| Region renaming, comparisons, demotion | Mostly resolved; see V2-F4 and V2-F7 |
| Ordinal assessments | Added but under-specified (V2-F6) |
| Field allocation deferred; 24-block illustrative pilot | Resolved; inference unit needs stating (V2-F5) |
| P18 extended to Ghazi Shah and Kai | Kai verified; Ghazi Shah undocumented (V2-F3) |
| Coastal uplift and Khambhat cores | Resolved |
| Cap/substrate vs. occupation ages; reachability vs. preservation | Resolved |
| Calendar scale and reservoir status | Resolved; minor note (V2-F11) |
| Yield and inscription material moved to supplements | Resolved |
| Review provenance | Partial (V2-F9) |
| Legacy `comparison_stratum` field | Not verifiable from this packet; the shown register fields omit it |

No finding requires new fieldwork, source retrieval beyond confirming locators already in the register, or a site total.
