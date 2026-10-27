# Findings

A finding card records a result, its exact evidence, the population it covers and its status class. Start with a theme, then follow a card to the versioned output or primary-page source check. Counts and conclusions keep the date and scope of the original result.

The [status vocabulary](../registry/VOCABULARY.md) distinguishes verified computations, evaluations frozen before their reported outcome, exploratory refinements, failed tests, source reviews and synthetic controls; proposed, superseded and record classes preserve plans and research history. Verification tiers describe contributor review separately. The project's interpretations live in the [conjectures](../conjectures/README.md) and [working model](../WORKING-MODEL.md).

## The corpus and its gaps

These cards establish the population we can retrieve and the records still missing from it. Counts refer to the dated source frames on each card; the complete base register retains provisional identities and unresolved readings.

- [F-0007](F-0007-catalogue-identifiers-missing-from-export.md) Of 493 checked CISI 1 identifiers, 166 have no corpus match, including 75 in pottery and graffiti sections. *source-review*
- [F-0008](F-0008-museum-joins-are-a-lower-bound.md) At least 68 of 114 inspected museum records join corpus objects, with 46 unresolved in that census. *source-review*
- [F-0009](F-0009-site-frame-coverage-in-the-local-export.md) The census site list covers 5,652 of 5,680 corpus faces and reduces 123 entries to 115 site or provenance labels. *source-review*
- [F-0039](F-0039-the-base-register-preserves-all-4695-provisional-objects-and-5680-face.md) The base register retains all 4,695 provisional objects and 5,680 faces with 225,223 attributed assertions and zero certified-fresh objects. *exploratory*
- [F-0047](F-0047-fourteen-catalogue-view-relations-recovered-from-existing-image-assets.md) Fourteen reviewed catalogue-view relations link thirteen held assets to twelve keys, adding zero newly available pilot photographs. *source-review*

## Sign order and prediction

Preceding signs help predict a text, and closing positions draw from a smaller sign stock. Restoration accuracy and probability loss measure different properties, so both remain visible here.

- [F-0001](F-0001-sequential-prediction-on-unique-texts.md) Knowing the previous sign improves prediction by 0.848 bits per noninitial sign across 1,596 distinct texts. *verified-computation*
- [F-0002](F-0002-second-order-known-slot-restoration.md) Two-sign context ranks the hidden sign first in 37.27% of 8,009 artificial gaps, against 34.59% for one-sign context. *verified-computation*
- [F-0003](F-0003-second-order-probability-loss-worsens.md) Probability loss worsens from 5.1194 to 5.2472 bits per hidden sign when the restoration model uses two signs of context. *verified-computation*
- [F-0004](F-0004-loss-selection-returns-first-order.md) All five validation folds choose the one-sign model when smoothing is selected by probability loss, retaining 34.5861% top-one accuracy. *exploratory*
- [F-0022](F-0022-initial-and-final-sign-concentration-differs.md) Initial-minus-final sign entropy is +0.260 across 1,859 distinct texts, against −0.017 to +0.018 under within-text shuffling. *frozen-evaluation*

## Graphic families and added marks

Shared base shapes carry predictive information, especially for rare signs. The separate tests of coder agreement and added marks show which grouping choices the evidence supports.

- [F-0010](F-0010-graphic-base-families-improve-prediction.md) Base-shape families improve held-out prediction by 0.0219 bits per sign beyond the ungrouped model, exceeding random groupings (p = 0.005). *frozen-evaluation*
- [F-0011](F-0011-agreement-between-the-two-sign-codings.md) Two graphic-family codings of 577 sign codes agree at adjusted Rand indices 0.884 unweighted and 0.975 weighted by occurrences. *verified-computation*
- [F-0012](F-0012-modifier-signatures-fail-the-grouping-test.md) Grouping signs by their added marks performs no better than random groups of the same sizes (p = 0.11). *failed*
- [F-0013](F-0013-base-families-reduce-unseen-code-loss.md) For 267 held-out signs whose code is absent from training, base families reduce loss from 14.60 to 14.19 bits per sign. *frozen-evaluation*

## Lines, units and segmentation

Catalogue line divisions provide observed boundaries to test inferred units against. Readable corpora show how much boundary recovery is possible at this scale and how the chosen unit changes a structural comparison.

- [F-0018](F-0018-lines-recur-more-than-crossing-windows.md) Among 69 divided faces, 23 favour recurrence of whole lines, 4 favour stretches crossing a break and 42 tie (p = 0.0003). *frozen-evaluation*
- [F-0019](F-0019-indus-alternation-has-few-stems.md) Only 2 of 68 inferred stems occur with multiple final signs, a rate inside all four matched comparison ranges. *frozen-evaluation*
- [F-0020](F-0020-mean-segmentation-accuracy-at-indus-scale.md) Across four readable corpora at Indus scale, the best segmenter reaches boundary F1 0.531 against 0.485 for cutting everywhere. *frozen-evaluation*
- [F-0021](F-0021-seal-legend-segmentation-rehearsal.md) Branching entropy finds Ur III seal-legend word boundaries at F1 0.692 against 0.557 for cutting everywhere. *frozen-evaluation*
- [F-0023](F-0023-edge-asymmetry-changes-with-the-unit.md) Ur III seal-legend edge asymmetry changes from −0.204 by sign to +0.079 by word. *frozen-evaluation*

## Strokes and numbers

Stroke groups are often fixed to their neighbouring signs. The numeral-equation result records exactly which arithmetic follows from its assumed equalities and physical range.

- [F-0006](F-0006-four-conditional-numeral-solutions.md) Fuls's assumed numeral equations have four positive integer solutions; restricting the long-stroke multiplier to 8–13 leaves (10, 8, 6). *verified-computation*
- [F-0024](F-0024-stroke-values-are-tied-to-following-items.md) Indus stroke groups take 3.61 values per following sign on average, against 4.53–5.15 for matched Ur III counted items. *frozen-evaluation*
- [F-0025](F-0025-two-near-fixed-stroke-combinations.md) Sign 520 follows three strokes in 38 of 41 cases, and sign 585 follows seven in 16 of 17. *exploratory*

## Seals, sealings and where texts travel

Recurring seal texts connect sites, while long legends remain individually distinct in the selected corpus. Animal pairings, seal size and the source disputes over Lothal closures each constrain the proposed office interpretation.

- [F-0026](F-0026-recurring-seal-texts-span-sites.md) Among 1,430 eligible seals, 65 texts recur on 174 seals and 41 of those texts span sites. *frozen-evaluation*
- [F-0027](F-0027-long-seal-texts-do-not-repeat.md) None of 445 eligible seals with six or more signs shares its complete text with another. *frozen-evaluation*
- [F-0028](F-0028-frozen-duplicate-locality-test-does-not-pass.md) The same-site share for recurring texts is 0.473 against a shuffled 0.448, leaving the planned concentration test unpassed (p = 0.31). *frozen-evaluation*
- [F-0029](F-0029-unicorn-pairs-account-for-motif-matches.md) Of 89 identical-text seal pairs sharing an animal, 88 are unicorn pairs; only 1 of 42 pairs involving another animal matches. *exploratory*
- [F-0030](F-0030-sealings-match-seals-from-other-cities.md) Of 16 sealings or tags matching a seal text, 13 match only seals found elsewhere, carrying 4 of the 6 distinct texts. *verified-computation*
- [F-0035](F-0035-legends-closing-in-four-signs-sit-on-larger-seals.md) Eleven confirmation seals ending in four specified signs show ×1.35 excess face area (p = 0.021), a result dependent on three 820 seals. *frozen-evaluation*
- [F-0042](F-0042-l-164-has-conflicting-published-jar-stopper-and-wooden-box-interpretat.md) Rao's jar-stopper interpretation of L-164 and the later tentative wooden-box interpretation share a cord-fastened flat underside in a twelve-object group. *source-review*
- [F-0043](F-0043-rao-assigns-plate-clxi-f-to-two-different-lothal-objects.md) Rao assigns Plate CLXI F to 1864 on p. 319 and 1830 on p. 325; CISI identifies them separately as L-164 and L-161. *source-review*

## Tablets, images and manufacture

Text-to-image prediction differs among tablet genres. The Harappa clump adds a source-reported manufacturing relation and a recovery group whose physical use remains to be established.

- [F-0014](F-0014-bas-relief-image-prediction.md) Bas-relief tablet texts predict image class in 24.8% of cases, against 21.5% for the majority guess. *frozen-evaluation*
- [F-0015](F-0015-incised-tablet-image-prediction.md) Incised tablet texts predict image class in 57.4% of cases, against 48.1% for the majority guess. *frozen-evaluation*
- [F-0016](F-0016-copper-image-prediction-fails.md) Copper-tablet texts predict image class in 19.2% of cases, below the majority guess's 26.9%. *failed*
- [F-0017](F-0017-copper-groups-do-not-transfer-to-seal-animals.md) Copper-tablet sign groups occur with matching seal animals 3 times against 3.01 expected (p = 0.62). *failed*
- [F-0045](F-0045-the-h-2218-to-h-2239-tablets-share-a-reported-cutting-method.md) The 22 H-2218–H-2239 tablets share a reported cutting direction and stroke order across at least three engravers, with sixteen recovered in a clump. *source-review*

## Fish signs and H-912

The fish cards separate a repeated graphic order from the identity and excavation context of the vessel-and-fish tablet. Functional readings of those constructions have their own conjecture cards.

- [F-0036](F-0036-parpola-2010-vessel-fish-figure-is-h912.md) Parpola's 2010 Figure 6 matches H-912 B on CISI 2 p. 339, while its caption and prose name H-902. *source-review*
- [F-0037](F-0037-learned-fish-order-predicts-seal-combinations.md) The frozen fish order wins in 43 reserved dependency groups, loses in eight and ties in two (p = 0.0000003434). *frozen-evaluation*
- [F-0038](F-0038-h912-source-depth-is-a-range.md) H-912's primary source gives a 4–7-foot depth range; the export's 5.5 feet equals its midpoint. *source-review*

## Archaeological contexts of objects and towns

Named excavation keys and architectural parts make published contexts traceable. Floor, street and building-phase assertions retain the dating basis supplied by each source.

- [F-0040](F-0040-h-1657-has-a-published-late-period-3c-floor-context.md) The reviewed H-1657 source chain places the seal on Room 591's floor in Trench 43, assigned to late Period 3C. *source-review*
- [F-0041](F-0041-h-1688-joins-field-key-h90-1600-and-lower-mound-e-street-levels.md) H-1688 joins H90-1600/3166-1 and lower street levels in Mound E area C, assigned to Period 3A. *source-review*
- [F-0046](F-0046-the-town-register-separates-architectural-axes-and-building-episodes-a.md) The 34-town register preserves 1,380 line and system records, 118 dated-part assertions and 620 radiocarbon assertions by architectural part. *source-review*

## Calibration and readable comparisons

Failed predictions and known-system controls define what the methods can establish. Readable comparison objects enter a test population only after identity, completeness and language checks.

- [F-0005](F-0005-gap-count-estimator-loses-to-constant-one.md) The lost-sign count estimator scores 46.30%, below 51.07% for always guessing one. *failed*
- [F-0031](F-0031-literal-copy-reference-calibration.md) In 1,000 simulated copied-record corpora, whole-object shuffling rejects a true null in 5.4% against 15.9% for record shuffling. *synthetic*
- [F-0032](F-0032-imperfect-face-reference-calibration.md) In 1,000 simulated imperfect-face corpora, keeping faces together rejects a true null in 5% against 11% for separate shuffling. *synthetic*
- [F-0033](F-0033-reference-only-symbol-map-selection.md) Reference-based method selection recovers 309 of 384 simulated symbol maps, against 283 for graph mapping and 168 for slot mapping. *synthetic*
- [F-0034](F-0034-gloss-map-fails-to-predict-seal-site-and-size.md) The 118-sign class-and-gloss map fails to predict confirmation-half seal site and size, scoring at the 33.0th percentile of rearrangements. *failed*
- [F-0044](F-0044-tell-brak-reg257-is-matthews-catalogue-308-and-tb1058.md) Tell Brak REG257 joins Matthews catalogue 308 and TB1058, with a partly restored cup-bearer legend and zero corpus admissions. *source-review*

## Results recorded in packages but not yet carded

The remaining dated attempt records include measured outcomes, acquisition limits and reviews; repository maintenance records are in the [experiment registry](../experiments/registry.json). Their original status classes and recorded verification tiers appear below; an unspecified tier is labelled unrecorded. Related passes keep their own entries so that a later correction can be followed to its source.

- [BENCH-HARNESS-2026-10-13](../../experiments/2026-10-13-bench/REPORT.md) Five shared task commands reproduce 50 source comparisons and pass 17 interface checks without certifying a fresh population. *verified-computation*, unrecorded
- [CISI-BASIC-DATA-FULL-2026-10-13](../../experiments/2026-10-13-cisi-basic-data-full/README.md) CISI 1 and 2 supply 1,543 and 2,139 transcribed entries, with 2,602 joined families and unresolved readings retained under the recorded acceptance rules. *source-review*, unrecorded
- [CISI2-BASIC-DATA-PILOT-2026-10-13](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md) The 327-entry CISI 2 pilot reaches 90.5% cell agreement and joins 283 families while retaining 119 bracketed cells. *source-review*, unrecorded
- [CISI3-RANGE-COVERAGE-2026-10-13](../../experiments/2026-10-13-cisi3-range-coverage/README.md) The export contains 1,463 of 2,590 inferred CISI 3 number slots, leaving 1,127 absent slots with neighbour-based object-class estimates. *verified-computation*, unrecorded
- [DATA-ROUND-1-FOLLOW-UP-2026-10-13](../../experiments/2026-10-13-data-round-1-verification/README.md) All 19 review findings are resolved, and corrected museum-number coverage reaches 542 of 4,695 objects, or 519 under the whole-cell certainty rule. *verified-computation*, unrecorded
- [DATA-ROUND-1-VERIFICATION-2026-10-13](../../experiments/2026-10-13-data-round-1-verification/REPORT.md) The offline museum and CISI outputs reproduce, while the original review records 19 findings, including nine publication blockers, before the follow-up corrections. *source-review*, unrecorded
- [IMAGE-INDEX-AND-UNITS-2026-10-13](../../experiments/2026-10-13-image-index-and-units/README.md) The image index records 8,722 files and 8,444 face-image links, with 97% of links placed on a catalogue page and unresolved side assignments retained. *verified-computation*, unrecorded
- [MACKAY-MARSHALL-TABLES-2026-10-13](../../experiments/2026-10-13-mackay-marshall-tables/README.md) Of 1,269 excavation-table rows, 1,146 join 1,134 Mohenjo-daro objects, including 1,122 of 1,318 seals. *verified-computation*, unrecorded
- [MUSEUM-OPEN-ACCESS-2026-10-13](../../experiments/2026-10-13-museum-open-access/README.md) The seven-institution harvest and separate join review raise the confirmed museum-record lower bound from 68 to 87. *source-review*, unrecorded
- [PLATE-CHECKS-C0004-SHOTA-RIVALS-2026-10-13](../../experiments/2026-10-13-plate-checks/README.md) Two readers match the four-sign text on the Lothal sealings and M-895, while different cutting and spacing distinguish their stamps and M-895's animal remains unresolved. *source-review*, unrecorded
- [ATTEMPT-0001](../../experiments/2026-10-15-route-test-metadata/README.md) All eight sampled rectangular seals labelled None have signs only, while six of twelve square examples are unreadable where a motif would lie, lowering recorded seal-motif coverage to 89.9%. *source-review*, unrecorded
- [ARCHAEOLOGICAL-SETTING-2026-10-20](../../experiments/2026-10-20-archaeological-setting/REPORT.md) The 47-target audit distinguishes 40 pre-firing vessel stamps, six low-fired tags and one unbaked stopper, with two individually joined excavation contexts. *source-review*, submitted
- [FOREIGN-SCRIPT-AUDIT-2026-10-20](../../experiments/2026-10-20-foreign-script-audit/REPORT.md) The 33-face audit lowers the legacy foreign contrast from 0.1654 to 0.0536 after eligibility corrections, with every family-bootstrap interval spanning zero. *source-review*, unrecorded
- [FRESH-TEST-COLLECTION-2026-10-20](../../experiments/2026-10-20-fresh-test-collection/REPORT.md) The Farmana source block has 36 candidate identifiers, including fifteen conditionally absent pottery objects, sixteen unresolved cases and five known matches. *source-review*, unrecorded
- [HARAPPA-LEGEND-PERIODS-2026-10-20](../../experiments/2026-10-20-harappa-legend-periods/REPORT.md) Harappa's closing stock remains stable while length, inventory and variants change, with three drift tests surviving the registered corrections and killing the fixed-pattern conjecture. *frozen-evaluation*, unrecorded
- [KHIRSARA-RESERVE-2026-10-20](../../experiments/2026-10-20-khirsara-reserve/REPORT.md) The source search verifies the 2012 Khirsara article and its issue route but recovers zero new seal images or fresh-test objects. *source-review*, unrecorded
- [MOHENJO-DARO-STRATIGRAPHY-2026-10-20](../../experiments/2026-10-20-mohenjo-daro-stratigraphy/REPORT.md) Mohenjo-daro's closing-stock shares remain 73.1% at the bottom and 72.5% at the top, while failure to detect predicted front-of-legend drift kills C-0006. *frozen-evaluation*, unrecorded
- [RESERVED-TEST-PROGRAM-2026-10-20](../../experiments/2026-10-20-reserved-test-program/REPORT.md) Farmana supplies fifteen conditionally absent pottery records but zero approved objects for the frozen seal tests. *record*, unrecorded
- [SCRIPT-VARIATION-2026-10-20](../../experiments/2026-10-20-script-variation/REPORT.md) Across 306 independent text components, adding city loses 0.01584 bits per target, with a 95% interval from −0.04107 to +0.00610. *exploratory*, submitted
- [SEAL-LEGEND-UNITS-2026-10-20](../../experiments/2026-10-20-seal-legend-units/REPORT.md) On 33 faces with verified line order, the line-trained segmenter reaches J = 0.718, with a 95% interval of 0.586–0.838. *frozen-evaluation*, unrecorded
- [BIRTH-STAR-NAMES-2026-10-21](../../experiments/2026-10-21-birth-star-names/REPORT.md) Among 757 donor occurrences, 42 strict asterism names form a skewed class, overturning the proposed flatness rule before five predictions were frozen for fresh seals. *exploratory*, submitted
- [DRAVIDIAN-ROOT-MEANINGS-2026-10-21](../../experiments/2026-10-21-dravidian-root-meanings/REPORT.md) The DEDR star-sense reconstruction reaches root probability 0.524, but the homophonous fish-and-star form reaches 0.41 and the reviewed credence is 0.20. *frozen-evaluation*, submitted
- [HEAD-DIRECTION-CORPORA-2026-10-21](../../experiments/2026-10-21-head-direction-corpora/REPORT.md) The eligible corpora contain 245 Indo-Aryan, 23 Tamil-Brahmi, 3,044 Ur III and eleven Akkadian legends, leaving the frozen discrimination test below its entry minimum. *frozen-evaluation*, unrecorded
- [NORTH-B-CORRESPONDENCE-2026-10-21](../../experiments/2026-10-21-north-b-correspondence/REPORT.md) Northern forms retain m- in 83 of 88 Tamil m- comparisons and show b- in 50 of 55 Tamil v- comparisons, leaving P5 unresolved by its frozen rule. *frozen-evaluation*, submitted
- [PLAN-REGISTRATION-2026-10-21](../../experiments/2026-10-21-plan-registration/REPORT.md) Fourteen plans at eight towns were registered, but the failed Dholavira validation withholds the derived values from scoring under the frozen rule. *frozen-evaluation*, submitted
- [POST-CATALOGUE-FINDS-2026-10-21](../../experiments/2026-10-21-post-catalogue-finds/README.md) The 503-row census identifies 301 post-catalogue inscribed objects and bounds corpus absence at 55–291 under the frozen join rule. *source-review*, submitted
- [REBUS-BASE-RATE-2026-10-21](../../experiments/2026-10-21-rebus-base-rate/REPORT.md) Matched random pairs reproduce the single interlock in 30.5% of cases, while all four encoded network links recur together in 0.44% of draws. *frozen-evaluation*, submitted
- [TOWN-AXES-2026-10-21](../../experiments/2026-10-21-town-axes/REPORT.md) The 29-town study leaves the primary test below its eight-town minimum and rejects the Pleiades version, while its eleven-town secondary test gives p = 0.082. *frozen-evaluation*, submitted
- [TOWN-ORIENTATIONS-VERIFICATION-2026-10-21](../../experiments/2026-10-21-town-orientations-verification/REPORT.md) The independent study reproduces all 83 astronomical predictions within 0.026 degrees but finds bearing and dating disagreements that leave the frozen test undecided. *frozen-evaluation*, submitted
- [CANDIDATE-IDENTITY-EXPOSURE-01](../../experiments/2026-10-22-candidate-identity-exposure/REPORT.md) Review of all 358 candidate rows preserves 24 existing identifier links, 306 candidate-only rows and 28 unlinked rows, with zero confirmation-eligible objects. *exploratory*, submitted
- [EVIDENCE-INTEGRATION-01](../../experiments/2026-10-22-evidence-integration/REPORT.md) The integration adds 5,474 review assertions to the unchanged 4,695-object population, accepting 21 provisional layouts while retaining unresolved identity relations. *exploratory*, reviewed
- [FACE-ADJUDICATION-29-01](../../experiments/2026-10-22-face-adjudication/REPORT.md) All 29 reviewed faces receive dispositions, supporting 21 provisional spatial layouts and twelve source-segment maps without assigning historical reading traversal. *source-review*, submitted
- [FIELD-NOVELTY-REVIEW-2026-10-22](../../experiments/2026-10-22-field-novelty-review/REPORT.md) The separate review identifies two scientific cores for focused papers and names source and validation repairs for the other publication candidates. *source-review*, submitted
- [LEXICAL-SOURCE-REVIEW-01](../../experiments/2026-10-22-lexical-source-review/REPORT.md) The 24-form source review corrects two language assignments and finds seventeen supported, one wrong and two unresolved splits among twenty accepted sample cases. *exploratory*, submitted
- [READING-EVAL-READINESS-01](../../experiments/2026-10-22-reading-eval-readiness/REPORT.md) Exact written-form counting finds nine kā tokens against 22,287 historical prefix matches on the same 162,399-token stream, exposing a required input repair. *exploratory*, submitted
- [REBUS-BLIND-TEMPLATES-2026-10-22](../../experiments/2026-10-22-rebus-blind-templates/REPORT.md) Parpola's words yield compounds for nine of 38 blind pairs against 4.97 expected, a ratio of 1.81 with a 95% interval of 0.93–2.72. *frozen-evaluation*, submitted
- [REBUS-WINSLOW-2026-10-22](../../experiments/2026-10-22-rebus-winslow/REPORT.md) The Winslow rerun fails P2: zero of 2,500 matched replacement pairs shares a member because the starting muruku compound class is absent. *frozen-evaluation*, submitted
- [UNIT-READINESS-01](../../experiments/2026-10-22-unit-readiness/REPORT.md) The executable queues cover 118 divided faces, 881 unresolved multiface objects and 358 post-catalogue rows, with zero certified-fresh cohorts. *source-review*, submitted
- [EIGHT-DIRECTIONS-2026-10-24](../../experiments/2026-10-24-eight-directions/REPORT.md) Eight source contributions extend identity, face, context, sealing, tablet, lexical, readable-control and construction records with their remaining acquisition requirements. *record*, submitted
- [EIGHT-DIRECTIONS-PASS2-2026-10-24](../../experiments/2026-10-24-eight-directions-pass2/REPORT.md) Eight second-pass contributions add context and source evidence, including the separately reviewed H-1657 floor attribution, while admitting zero new object merges, face bridges or readable legends. *record*, submitted
- [EIGHT-DIRECTIONS-PASS3-2026-10-24](../../experiments/2026-10-24-eight-directions-pass3/REPORT.md) Eight third-pass contributions recover a Harappa field key, restricted am rules, the Tell Brak catalogue and a Lothal plate conflict, with four source chains separately checked. *record*, submitted
- [HARAPPA-CONTEXT-EXTENSION-2026-10-24](../../experiments/2026-10-24-harappa-context-extension/REPORT.md) Nine Harappa identities receive source-qualified context dispositions, with two uncontested full keys, a retained lot conflict and zero independently dated confirmation seals. *source-review*, submitted
- [LEXICAL-EVIDENCE-PASS2-2026-10-24](../../experiments/2026-10-24-lexical-evidence-pass2/REPORT.md) Sixteen frozen lexical cases yield eight supported contextual increments, one contradicted candidate, six homograph separations and one grammatical-label conflict. *source-review*, submitted
- [LEXICAL-EVIDENCE-PASS3-2026-10-24](../../experiments/2026-10-24-lexical-evidence-pass3/REPORT-v2.md) Grammar Rules 37, 128 and 129 identify an am-taking plant class and restricted stem changes, while the five mandatory lexical cases remain source-qualified. *source-review*, submitted
- [LEXICAL-EXTRACTION-EXTENSION-2026-10-24](../../experiments/2026-10-24-lexical-extraction-extension/REPORT.md) Re-extraction of 69,310 Winslow records changes the two-member table from 18,426 to 25,653 rows, with comparative-scorer eligibility still false. *exploratory*, submitted
- [OBJECT-IDENTITY-EXTENSION-2026-10-24](../../experiments/2026-10-24-object-identity-extension/REPORT.md) All 28 selected Dholavira identities agree across both source tables, with zero accepted corpus-family bridges. *exploratory*, submitted
- [OBJECT-IDENTITY-PASS2-2026-10-24](../../experiments/2026-10-24-object-identity-pass2/REPORT.md) Ten photographed Dholavira targets retain 62 candidate families and 274 relationships despite four exact dimension triples, because the identity admission evidence is incomplete. *exploratory*, submitted
- [OBJECT-IDENTITY-PASS3-2026-10-24](../../experiments/2026-10-24-object-identity-pass3/REPORT.md) The held-asset audit identifies 2,152 filenames outside the application map and 284 anonymous crops, recovering zero qualifying Dholavira identity bridges. *source-review*, submitted
- [OFFICE-SEAL-PASS2-2026-10-24](../../experiments/2026-10-24-office-seal-pass2/REPORT.md) Three of five audited objects have registered non-obverse photographs, while L-164 and L-167 lack those views in the selected sources. *source-review*, submitted
- [READABLE-SEAL-CONTROLS-2026-10-24](../../experiments/2026-10-24-readable-seal-controls/REPORT.md) Eighteen readable-control candidates yield zero new eligible legends after duplicate, language and damage checks. *exploratory*, submitted
- [READABLE-SEAL-PASS2-2026-10-24](../../experiments/2026-10-24-readable-seal-pass2/REPORT.md) Four Urkesh cases yield three deferrals and one exclusion, leaving the frozen readable-control counts unchanged. *exploratory*, submitted
- [SHARED-INFRASTRUCTURE-PLAN-TEST-2026-10-24](../../experiments/2026-10-24-shared-infrastructure-plan-test/REPORT.md) The follow-up records eighteen plan quantities and 32 context assessments but zero fully qualified persistence episodes or matched documentary pairs. *exploratory*, submitted
- [TABLET-USE-PASS2-2026-10-24](../../experiments/2026-10-24-tablet-use-pass2/REPORT.md) The bounded search recovers three workshop-context comparisons and zero new registered use relations for the target tablets or controls. *source-review*, submitted
- [TABLET-USE-PASS3-2026-10-24](../../experiments/2026-10-24-tablet-use-pass3/REPORT.md) Nineteen held pages and nine visual inspections clarify the workshop and dump descriptions without adding a registered target-use relation. *source-review*, submitted
- [TOWN-PHASE-LINKS-2026-10-24](../../experiments/2026-10-24-town-phase-links/REPORT.md) Twenty-four inspected pages yield eleven architectural relations and zero surveyed-wall-to-construction-sample joins. *source-review*, submitted
- [TOWN-PHASE-PASS2-2026-10-24](../../experiments/2026-10-24-town-phase-pass2/REPORT.md) Two primary sources verify TF-19's locus and four restoration episodes without completing a wall-to-construction-sample join. *source-review*, submitted
- [TOWN-PHASE-PASS3-2026-10-24](../../experiments/2026-10-24-town-phase-pass3/REPORT.md) Twelve inspected pages recover a site-plan locator and earlier conservation photographs, with zero construction-sample joins. *source-review*, submitted
- [UNIT-SOURCE-EXTENSION-2026-10-24](../../experiments/2026-10-24-unit-source-extension/REPORT.md) One recovered divided-face crop reduces the queue from 43 to 42, and eight provisional face-side bridges cover four of five objects. *source-review*, submitted
- [UNIT-SOURCE-PASS2-2026-10-24](../../experiments/2026-10-24-unit-source-pass2/REPORT.md) Seven source routes recover one candidate Dholavira panel and zero admitted new face bridges, leaving 42 faces without crops. *source-review*, submitted
- [UNIT-SOURCE-PASS3-2026-10-24](../../experiments/2026-10-24-unit-source-pass3/REPORT.md) The seven-case follow-up adds zero face bridges and leaves the queue at 42 after distinguishing the 17-page public scan from the held 15-page chapter. *source-review*, submitted
- [URBAN-FORM-INSCRIPTION-ECOLOGY-2026-10-24](../../experiments/2026-10-24-urban-form-and-inscription-ecology/REPORT.md) The urban comparison records 287 source-qualified assertions, 134 quantity rows and three untested institutional conjectures across twelve core towns and one hinterland relation. *source-review*, submitted
- [CROP-CONTINUITY-2026-10-25](../../experiments/2026-10-25-crop-continuity/REPORT.md) Nine phase summaries at five sites show crop persistence with changing shares, including Bahola's winter increase of 10.42 percentage points. *source-review*, submitted
- [CULTURAL-TRANSMISSION-THEORIES-2026-10-25](../../experiments/2026-10-25-continuity-theories/REPORT.md) Three transmission conjectures begin at credences 0.65, 0.50 and 0.20, with no historical prediction confirmed. *source-review*, submitted
- [INDUS-CITY-3D-2026-10-26](../../experiments/2026-10-26-indus-living-atlas/reconstruction/REPORT.md) Seven offline model scenes contain 49 source-and-assumption feature records and seven metric OBJ exports, with no new archaeological observation. *record*, submitted
- [INDUS-LIVING-ATLAS-2026-10-26](../../experiments/2026-10-26-indus-living-atlas/README.md) The atlas preserves 115 place entities and 112 located points, seven model scenes and separate later-occupation comparisons. *exploratory*, submitted
- [INDUS-MARKER-CONTINUITY-2026-10-26](../../experiments/2026-10-26-indus-living-atlas/README.md) Twelve sources support sixteen located observations of posturban persistence and changing markers, with no uninterrupted modern-town sequence established. *source-review*, submitted
- [OBJECT-PILOT-INTEGRATION-2026-10-26](../../experiments/2026-10-26-object-pilot/REPORT.md) Twenty pilot records consolidate 539 inherited assertions and two conflict summaries, with fourteen reviewed index relations and zero physical merges. *record*, reviewed
- [OBJECT-PILOT-REGISTER-2026-10-26](../../experiments/2026-10-26-object-pilot-register/REPORT.md) Twenty dossiers preserve 539 assertions and 138 missing-evidence rows while retaining all 62 Dholavira candidate families and 274 relationships. *source-review*, submitted
- [SOURCE-CONFLICTS-2026-10-26](../../experiments/2026-10-26-source-conflicts/REPORT.md) Both pilot identity conflicts remain unresolved, with the original Lothal photograph register and Harappa object cards named as deciding records. *source-review*, submitted
- [SOUTH-ASIA-LIVING-TOWNS-2026-10-26](../../experiments/2026-10-26-indus-living-atlas/living-towns/REPORT.md) The eighteen-case comparison uses 24 source records and finds no complete source-audited Indus-to-present occupation sequence among its candidates. *source-review*, submitted
- [READABLE-EXTERNAL-RECORDS-2026-10-27](../../experiments/2026-10-27-readable-external-records/REPORT.md) Eight source pointers distinguish contemporary contact records from later Iranian and Tamil-Brahmi comparisons, with zero evaluation-corpus admissions. *exploratory*, unrecorded
