# Revised design review

Reviewed 11 October 2026. Scope: `revised-body-v2.md` §§2.2, 2.3, 6, 8.1 and 8.3, plus the planned `DESIGNS`, `common_comparison`, `common_access` and `pilot_scope` wording in `revise_registers.py`. The body initially reviewed has SHA-256 `1ccaf833465fdc48c8cbcca7000744b59ee3908b0565606b128f608da6ec1db7`; the revision script read for its planned wording has SHA-256 `66e3429e9505bd8c8fe3c2df8b08628b1ae3125004bde9d62f9ea5706ffaf1c6`. This is a bounded design review by the statistical-methods and mountain-evidence contributor. No manuscript or register was edited, the revision script was not executed, and no new sources were searched.

The revised body is scientifically coherent overall. It distinguishes chronological systems, limits the rectangles to regional indexing, treats inadequate-depth observations as unresolved, and separates another-period archaeology from failure to find archaeology. The 24-block pilot is explicitly an illustrative workload with no power claim. Core spacing, reachable depth, dating capacity, local access and conservation decisions remain conditional. Capture–recapture is now described as a proposed model, and the misleading guaranteed-floor interpretation has been removed.

## Material clarification 1: keep reachability separate from preservation

At §8.3, line 237, the first estimand is “the proportion of sampled transects reaching a surviving target-age terrestrial surface.” This is a valid measure of the combined outcome of access, method reach and preservation. It cannot by itself compare surface survival between strata: thick younger cover could reduce the numerator by preventing cores from reaching a preserved surface. The following sentence correctly makes short cores unresolved, but the proportion's denominator remains unclear.

Replace the first three sentences of that paragraph with:

> Record the proportion of attempted transects that adequately resolve the target-age interval. Among those adequate profiles, record whether the predicted terrestrial surface survives, together with its depth, continuity and evidence of scour. Profiles that do not reach or date the relevant interval remain unresolved and are reported separately. A preservation premise loses support within the sampled landform and accessible frame when adequately resolved profiles contradict its predicted surface history.

Keep the sentence about cap ages, substrate ages and redeposited charcoal. “Adequate” needs a local protocol definition: the profile must reach the relevant sedimentary unit or bracket its missing interval, supply the required chronological resolution, and cover enough of the proposed feature to address its premise. A core at sufficient depth can still miss a narrow feature laterally. Geological evidence can reduce support for preservation at the inspected unit; archaeological absence needs method performance and spatial coverage appropriate to the hypothesized occupation.

This restriction should also appear in the candidate default: **“A negative can demote the stated premise only for inspected units with adequate effort, visibility, spatial coverage, depth and chronology for that target. Unreached, insufficiently dated or inadequately covered units remain unresolved.”** The candidate-versus-comparison precision clause at §6, line 176, is sound and should carry through to defaults. A nonsignificant difference alone supplies no concentration demotion rule.

## Material clarification 2: an invisible class remains unidentified

Section 8.1, lines 217–219, handles matching, closure, heterogeneity and positive dependence correctly. The final proposal for a model “accompanied by ... an explicit class of sites inaccessible to all methods” needs one additional distinction. Recording or adding that class to a model does not estimate its membership from capture histories. A model can describe the class while leaving its size completely unidentified.

Replace the last sentence of line 219 with:

> Size-stratified, multi-method records with jointly inspected match histories could support estimation within their defined detection frame, accompanied by sensitivity to dependence. Sites inaccessible to all included methods remain unidentified unless external constraints supply information about that class.

The repetition example at line 215 is correctly labeled as independent visits with constant assumed detection. Its probability concerns units capable of being detected. The opening observation-chain model and the near-zero detection statement already provide that context; no additional numerical calculation is needed.

## Material corrections in the planned candidate wording

The new defaults record method calibration, locked intervention limits, prior effort, inaccessible and undatable observations, practical blinding and limited precision. `common_access` and `pilot_scope` clearly leave access unverified and treat only P08/P09's 24 blocks as an illustrative workload. Most demotion rules now concern sampled units and preserve unresolved outcomes. The following rules still merge premises that can have different outcomes.

**P04, script line 58.** Another-period archaeology cannot demote the archaeological interpretation of a historical-map symbol. It can demote its Indus attribution. Replace the rule with:

> Demote Indus attribution when adequately dated cultural context supports another period. Demote archaeological interpretation only when adequate investigation supports a natural feature without cultural context.

**P16, line 70.** A local non-Indus occupation can be buried beneath a fan; the cultural result does not reject the burial premise. Replace the combined rule with:

> Demote the tested Indus affiliation when dated context supports another tradition or period. Demote the burial prediction only when adequate logs exclude the predicted buried surface in the relevant sedimentary unit and interval.

**P17, line 71.** Stratigraphy of another age does not by itself reject a target-age usable surface. An older substrate can have been occupied later, as §2.2 correctly explains. Replace the rule with:

> Demote the preservation prediction where adequate stratigraphy shows truncation of the target-age interval or demonstrates that only younger terrestrial ground existed. Earlier substrate formation alone leaves later use unresolved; occupation attribution requires its own context and dates.

**P09, line 63.** Name the chronological relationship being tested. A younger fill can postdate use of an older channel; an abandoned channel margin can support later settlement. Replace the demotion rule with:

> For a prediction of contemporaneous channel use, demote the link when adequately constrained construction or active-use intervals are incompatible with occupation. A fill date alone leaves that relationship unresolved. Earlier abandonment does not reject later occupation of the channel margin.

**Legacy comparison fields.** The script adds `minimum_comparison` but appears to retain `comparison_stratum` from the frozen register. The old P10 description includes “archaeologically negative sections,” while P17 includes “empty shelters.” Those labels conflict with the improved new comparisons. Set `comparison_stratum` to the new comparison wording, or remove that legacy key with an explicit schema change. Material/process controls, unresolved comparison parcels and adequately inspected archaeological negatives need distinct statuses.

The illustrated holdout also needs a clear denominator: replace “one third of eligible blocks” at body line 235 with **“eight of the 24 sampled blocks, allocated within strata and kept together by correlated landform unit.”** This is a clarification of the stated workload, with no assertion that eight blocks supply sufficient validation precision.

The chronology orientation table in §2.2 introduces no material inconsistency within this review's scope. Its retained conventional-shell status and distinction between substrate, cap and occupation dates protect the proposed coring interpretation. The effort-adjusted curve at §8.1, line 221, is also appropriately described as a diagnostic requiring method and footprint histories, rather than a fitted undiscovered-site total.
