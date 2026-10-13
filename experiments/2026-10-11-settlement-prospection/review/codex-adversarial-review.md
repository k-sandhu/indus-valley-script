# Independent Codex adversarial review of the frozen first draft

Reviewed endpoint: `draft-v1.md`, frozen on 2026-10-11, SHA-256 `dee0212d5b3c93b34a523c445404660a79eeaf72e5bda28dcadfcbfffaf5ac06`. Supporting endpoints are `sources-v2.json`, `candidates-v2.json` and `run-v2`. This review preserves those files. The reviewer owns this report and `codex-checks.json`; the manuscript author owns revisions and the response record.

The manuscript can become a useful research working paper after the corrections below. Its main quantitative conclusions survived the checks undertaken here. It separates historical excavation counts, survey observations and constructed examples, and gives testable proposals for the hidden settings requested by the user. The remaining material problems concern one geographic boundary, one survey-method attribution, a rejection rule that can confuse landform age with occupation age, and presentation defects. No high-severity error overturning the central argument was established. Release should follow targeted revision and inspection of the final rendered paper. This is an independent model-assisted adversarial reading, not formal archaeological peer review or validation by fieldwork.

## Scope and independent checks

The reviewer read the frozen manuscript, source and candidate registers, analysis code, output tables, manifests and selected primary source cases. The earlier independent source audit is preserved at `../research/independent-source-audit.md`. Primary-source access limits remain those recorded there and in the source register; this review does not claim exhaustive reading of all 47 references.

`codex-checks.json` records 24 independent checks: 23 passed and one failed. The six frozen file hashes, analysis script and input hashes, thirteen aggregate-output hashes, local witness hashes and numerical-figure hashes matched their manifests. Recounting the input registers independently recovered 115 coordinate-register entries, 85 coordinate pairs, 85 South Asian entries with 76 pairs, and a separate 86-site chronology cohort with 213 phase labels, including 49 radiocarbon-basis labels across 28 site entries. Those phase labels remain metadata rather than independent laboratory measurements.

The Green table transcription was checked against the primary table already inspected in the source audit. An independent exact-rational rounding calculation recovered the same unique positive integers, totaling 199 among 779 checks. Symbol groups reproduced 2/5 combined, 150/393 form-line, 21/154 shaded and 26/227 hachure positives. Historical ratios, Cholistan subtraction, square-equivalent geometry, excavation volumes, constructed fragment counts and repeated-detection arithmetic agreed. The reviewer did not import or rerun `analysis.py`; these checks used direct input reads and separate arithmetic.

All 21 rectangles have valid longitude/latitude order and ranges. The frozen GeoJSON polygons match their candidate rectangles. Ten selected anchors from the prior coordinate register lie in their relevant windows: Ganweriwala, Rakhigarhi, Masudpur, Harappa, Lakhanjo-daro, Miri Qalat, Nausharo, Lothal, Sutkagen-dor and Sotka Koh. These are containment checks of source-reported coarse points. They do not establish geolocation accuracy or geological suitability throughout each rectangle. Ghazi Shah, checked against the government inventory, falls outside P18. Kai/Naig cave concordance and exact point containment for Khundowala/Mulhiawala remain unverified.

## Source-confirmed errors

### F1 (moderate): P18 excludes a supporting settlement

**Passage.** Appendix A, frozen lines 368–374: “Kirthar piedmont, Sindh Kohistan-Jamshoro” and “West/south/east/north: [67.0, 25.0, 68.1, 26.3].” Its supporting references include Ghazi Shah evidence, and the main discussion treats that settlement as a foothill anchor.

**Evidence.** The [Pakistan Department of Archaeology and Museums entry for Ghazi Shah](https://doam.gov.pk/public/sites/7279) gives 26.454762389 N, 67.464134722 E. The latitude lies north of the rectangle's 26.3 N bound. The witness is preserved as `data/raw/2026-10-11-settlement-prospection/MOUNTAIN_GHAZI_GOV2026.html`; the mountain supplement records its provenance. This is the only failed containment check in `codex-checks.json`.

**Fix.** Preserve candidates-v2 and author a revised rectangle and name encompassing the intended Jamshoro–Dadu/Kirthar–Bhit comparison. State separately whether Kai/Naig is a verified subarea or a concordance lead outside the mapped claim. Generate a new map endpoint from the revised candidate register and update the appendix and map references together. The author has reported that this correction is planned; its completion has not been checked in this frozen-draft review.

### F2 (low): Green's 2018 filter is attributed to imagery

**Passage.** Frozen line 119: “later imagery excluded apparent ponds and dunes before field visits.” R10's sources-v2 observation similarly says “2018 imagery prefilter.”

**Evidence.** [Green et al. 2019](https://doi.org/10.3390/rs11182089), PDF p.10, states that the corresponding Survey of India map was rechecked. Apparent pond and dune symbols were then omitted before field visits. The paper specifies 12 ponds and 42 dunes in this description. It does not attribute this selection step to a satellite-imagery filter.

**Fix.** Replace the phrase with “later historical-map review excluded apparent ponds and dunes before field visits.” Carry the correction into a new source-register version. The changing selected sample and the manuscript's resulting restriction on generalization remain supported.

## Hypothesis-design and interpretation findings

### F3 (moderate): the rejection rule needs a stratigraphic unit

**Passage.** Frozen line 167: “If a dated surface is too young, too old, eroded or permanently marine during the target period, it leaves the archaeological candidate set.” The preceding sentence says speculative windows “should be inexpensive to reject at the first stage.”

**Evidence and implication.** The study proposes burial beneath later alluvium, colluvium and city deposits. A young cap can cover older occupation. An old terrace can carry younger occupation. Dating a substrate, cap, marine layer or redeposited organic sample therefore does not by itself reject the occupation hypothesis for the entire window. These are competing interpretations generated by the manuscript's own formation processes, rather than a demonstrated factual error in any cited site. Obtaining the necessary stratigraphic chronology can also require expensive cores and laboratory work; no pilot cost data support the cost claim.

**Fix.** Define the rejected object as a particular occupation-horizon or preserved-surface prediction after stratigraphic interpretation. Explain together that cap and substrate ages constrain the vertical sequence, while occupation samples test the phase. Retain an unresolved status when the relevant horizon was not observed. Replace “inexpensive” with the proposed order of archive, preservation and chronology checks, or provide an explicit cost basis.

### F4 (moderate): direct geographic support remains incomplete for some windows

**Passage.** P21, frozen line 394, cites R26 and R31 for a “broad coastal/submerged hypothesis” in the Gwadar–Pasni rectangle. Section 2.3 says each window has “a source connection.”

**Evidence and implication.** R26 concerns Miri Qalat/Kech inland of the P21 coastal bounds. R31 concerns Las Bela and Lower Sindh, east of this rectangle. They support regional analogies and methods, but they do not supply direct local landform chronology for P21. The manuscript already calls P21 a broad Class C proposal, which is appropriate. The geographic checks undertaken here cover only selected anchors, and cannot establish all named-location containment in P01, P12, P18 or P20.

**Fix.** Add a direct known-settlement anchor where available and distinguish it from regional environmental analogies. The [DOAM Sutkagen-Dor entry](https://doam.gov.pk/public/sites/8639) supplies 25.516666667 N, 61.966666667 E, within P21. It can support location and known archaeology; its broad inventory chronology should not supply a newly inferred coastal date. State in the package that geographic validation is partial. Complete Kai/Naig and remote-proposal concordance before advertising parcel-specific coverage. This is a bounded source-coverage limitation, not evidence that the windows lack archaeology.

### F5 (low): the synthetic density definition can count recovery twice

**Passage.** Frozen line 173 defines d as “the recoverable fragment density per cubic metre” and r as “the retained recovery fraction,” then uses Y = V d r.

**Evidence and implication.** The saved computation multiplies an assumed fragment density by a recovery fraction once. Its units and arithmetic are correct. Calling d “recoverable” could instead make readers understand it as an already observed recovery density, in which case multiplying by r again would apply recovery twice.

**Fix.** Define d as the deposited or surviving fragment density of a stated material class before collection, and r as the fraction recovered and retained under the specified protocol. Preserve the constructed status and the absence of an empirical density calibration. No numerical change is required.

### F6 (low): the abstract can imply a verified 2026 status for a 2020 cohort

**Passage.** Frozen line 7: “266 unmatched candidates await secure identity and chronology.”

**Evidence and implication.** The 266 result is the difference between the 337 clusters and 71 legacy matches reported by [Orengo et al. 2020](https://doi.org/10.1073/pnas.2005583117). The study has not reconciled subsequent field confirmation location by location through 2026. The full body attributes the study and limits its claims, but the abstract's present tense is broader.

**Fix.** Attribute the figures explicitly to the 2020 analysis and say that later confirmation status was not comprehensively reconciled. Do not infer that all 266 remain untested today. This changes the temporal claim, not the subtraction or the original candidate status.

## Editorial and artifact findings

### F7 (moderate): the coordinate diagram's labels are unreadable

**Artifact.** `map-v1/survey-windows.png`, inspected visually during this review. The rectangle ID labels appear as white silhouettes; the legend retains readable IDs, but the plotted rectangles cannot be reliably matched to it. The author independently identified the same rendering defect.

**Fix.** Preserve map-v1 and generate a corrected version with readable dark IDs or unambiguous callouts. Inspect the actual PNG used by the final document and the final PDF page at normal reading size. Polygon consistency and hashes establish data preservation, not readable rendering.

### F8 (low): assembly defects interrupt reading and reference lookup

**Passages.** Frozen line 5 has `# # Abstract`; line 27 has `itsJanuary`; line 35 has `AppendixB`; lines 157–163 have labels such as `CholistanP 01-P02`; line 173 joins “isV=10000 Afh.” Similar compressed words occur in appendix headings and prose.

**Evidence and implication.** These are observable assembly defects in the frozen Markdown. Some also split stable candidate IDs, making correspondence between table, appendix and map harder to follow. The scientific content can be retained while improving reading.

**Fix.** Correct headings, spaces, candidate IDs and formula presentation in the revised manuscript. Keep frozen source wording intact. Inspect the rendered formulas, table widths, references and figure captions. Replace the future-tense review plan at frozen line 223 with the actual review record and the model identity returned by the Claude CLI. Appendix B's promised package README and reproduction commands also need to exist and resolve in the final package.

## Important challenges that did not establish additional errors

The historical 1022/96 teaching-chapter count, Possehl's primary 1056/96 count and Gadekar's 142 Early-plus-Mature count through 2024 remain distinct. The manuscript does not calculate a present ratio from these incompatible scopes. The unresolved inventory discrepancy is appropriately left open.

The Cholistan training and validation cases are included within the reported matches, and visible selected mounds plus iterative refinement do not establish region-wide held-out recall. The manuscript describes this limitation and does not call the 266 unmatched clusters confirmed new Indus settlements. Ganweriwala's legacy, ground-survey and visible-mound areas remain different measurement definitions. The Green positives span periods and selection rules; their rates are not promoted to national Indus probabilities. These were central failure modes targeted in the earlier audit, and the frozen draft handles them.

The hidden-city and alluvial proposals recognize survival and truncation as alternatives. Mountain discussion distinguishes pre-Indus Mehrgarh, local sequences, Indus affiliations and uncertain cave evidence. The cited Kai inventory does not provide an Indus date; landslide-covered occupation remains a hypothesis. The coast section uses local relative sea level and dated terrestrial surfaces, recognizes inland former shores and natural/reworked rivals, and does not authenticate offshore geometric anomalies as cities. These are appropriate limits for the evidence actually available.

The selected date-seed case is represented cautiously. [Ivorra et al. 2024](https://doi.org/10.1016/j.jas.2024.106052), PDF p.5, describes six Miri Qalat plus seven Shahi Tump seeds, while Table 2 lists six MQ IDs and nine ST IDs with four radiocarbon ages. Section 3.2 again refers to thirteen studied seeds. This confirms the manuscript's cohort-reconciliation question; it does not establish which two samples were excluded or why. The reviewer found no basis to convert that selected classification sample into a regional cultivation percentage.

## Readiness and remaining limits

The working-paper argument is supported at the level of a structured narrative review and a reproducible aggregate audit. Its distinctive work is the reconciliation and comparative test design; it has not executed a new remote-sensing detector, route model, cave inventory, geomorphic survey or offshore investigation. The final title, abstract and conclusion should retain that scope.

A release decision should require F1–F3 and F7 to be resolved, the smaller wording and assembly fixes to be incorporated, actual review provenance to replace future plans, and a targeted check of revised register references and the rendered paper. The author can answer F4 with clearer partial-validation language and an improved direct local anchor while preserving unverified subareas as leads. The author should record the response to every finding without altering the frozen draft or this report. Remaining source-access gaps, incomplete location concordance and absence of field calibration should be reported together in the final methods and limitations.

Changed paths in this review task: `review/codex-adversarial-review.md` and `review/codex-checks.json`. The preceding initial task created `research/independent-source-audit.md`; it was not changed during the manuscript review.
