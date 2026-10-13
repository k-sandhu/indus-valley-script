# Adversarial review of the structure-first program

12 October 2026. A separate agent reviewed this program for code errors, departures from the protocol, unsupported inferences and prose problems. The review covered `README.md`, `PROTOCOL.md`, `starting-manifest.json`, `REPORT.md`, `RETROSPECTIVE.md`, `registry-entries.json`, every step report and amendment, the run summaries they cite, the verification files, the direction memo and all analysis code (`common.py`, `segmenters.py`, `step*/*.py`). File modification times were used to order events. Every rerun imports the frozen functions unchanged unless its docstring says otherwise, writes to a new directory under `data/raw/2026-10-12-structure-first/review-2026-10-12/`, and is post-outcome: if any result below is integrated, it should carry that label. No run directory and no file outside `review/` was changed.

## Findings at a glance

| No. | Severity | Location | Finding |
|---:|---|---|---|
| 1 | Major | Step 6; `REPORT.md` line 17 | The edge asymmetry changes sign with the unit and genre in the calibration corpora, and the report's account of the Ur III value is wrong |
| 2 | Major | `REPORT.md` lines 23–29 | The hypothesis ledger departs from the frozen predictions and weakens a description that is not in the ledger |
| 3 | Major | Step 2; `REPORT.md` line 9 | The copper conclusion is drawn although the frozen rule's condition (2c passes) failed; the named Parpola comparator was never used |
| 4 | Major | Step 1; `REPORT.md` line 7 | Contiguous cuts of the Wells number line give three quarters of the family gain; coder independence and the "base fixes" sentence are overstated |
| 5 | Moderate | Step 4, step 6 | The Ur III value drops units and truncates compound numbers; with units kept, the "failed" Ur III calibration succeeds |
| 6 | Moderate | Step 4 | "Item = next sign" is untested although step 6 found the preceding sign more informative; "rules out" ignores genre |
| 7 | Moderate | Protocol line 36 | Steps 2–4 ran before the step 1 endpoint and never used the adopted family layer; no amendment |
| 8 | Moderate | Protocol line 61 | Segmenter agreement with line breaks was never computed; the chosen segmenter recovers 76 of 76 breaks |
| 9 | Moderate | Step 5; `REPORT.md` line 15 | "None recovers words well" omits branching entropy on seal legends; the alternation statistic fails even on gold words |
| 10 | Moderate | Step 1 | The modifier claim rests on a pooled test; 0.0029 bits of every reported gain comes from the model mixture, not from grouping |
| 11 | Moderate | Step 2d | The test detects fivefold enrichment but not twofold; per-class odds ratios exceed 1 for classes with no matching hit |
| 12 | Moderate | All reports | Prior work is missing for results the reports present as findings |
| 13 | Minor | Step 3 | Interior lines counted twice, ties not shown, boustrophedon faces misread; the result survives stronger controls |
| 14 | Minor | Step 1 | Missing end symbol, unbalanced folds, kappa list; none changes a result |
| 15 | Minor | Step 2 | Permutation counts, label merges and amendment wording |
| 16 | Minor | Step 6 | Thin closed-class comparator, dropped segment-length measure, unverified typology, catalogue reading direction |
| 17 | Minor | Prose | Sentences that break `WRITING.md` or invite a language reading; documentation written before the review |

## Major findings

### 1. The edge asymmetry does not track head direction in the corpora used to interpret it

**Location.** `REPORT.md` line 17 and ledger row 27; `step6-language/REPORT.md` lines 3, 19, 27 and 29; `registry-entries.json`, STRUCTURAL-TYPOLOGY outcome.

**Evidence.** The frozen step 6 summary gives the asymmetry at two unit levels. Ur III seal legends are −0.204 by sign and +0.079 by word; Egyptian glyph sentences are +0.044 by sign and −0.107 by word; Ur III tablets are +0.005 and −0.004. Sumerian is head-initial in `typology.json`, and Egyptian, which the table omits, also places adjectives and genitives after the noun; yet the statistic takes both signs at each unit level, so in the calibration material its sign follows unit and genre. The headline contrast with IVS ("the reverse of Ur III seal legends") holds only if an Indus sign is compared with a cuneiform sign; at the word level the Ur III legends have the same sign as IVS.

The step 6 report (line 19) says the legends "open with recurring elements (the divine determinative and royal names)". The review run `step6` shows otherwise. Of the 309 legends, 78 begin with *ur* and 58 with *lu₂*, the first elements of personal names of the Ur-DN and Lu₂-DN type; 30 (9.7%) begin with the divine determinative, and deleting it moves the asymmetry only from −0.204 to −0.182. The sign-level value measures how Sumerian personal names are spelled. The Ur III word-level closed-class figure (line 23, "0.561, led by the relational noun *dumu*") rests on four eligible words, one of them ARAD₂-zu at mean position 0.998.

The within-text shuffle is exceeded by every corpus with any positional regularity (Ur III signs, Egyptian words), so "survives every shuffle" (line 3) and "the contribution here is its size against a within-text shuffle" (line 29) state only that position matters. The step 6 amendment adopted this statistic after the rehearsal, when its IVS direction was already known: 35.2% of clean texts end in sign 740, the terminal "jar" documented by Mahadevan (1977). The concentration is not that one sign alone: removing texts ending in 740 leaves an asymmetry of +0.149 (review run `step6`). Under the step 5 rule (protocol line 81), a measure that does not separate known systems is descriptive for IVS.

**Recommended change.** Report the asymmetry as a descriptive property of Indus text endings, with the 740 share and the +0.149 figure. Give both unit levels wherever Ur III is compared, correct the mechanism in step 6 line 19, and delete "which matches the IVS asymmetry" and "which matches the Ur III legends" (line 27) and the "contribution" sentence. Remove ledger row 27. Next-step item 5 in `REPORT.md` should require the statistic at sign and word level on at least two head-initial and two head-final seal corpora before it can feed the frozen rule.

### 2. The hypothesis ledger departs from the frozen predictions

**Location.** `REPORT.md` lines 23, 25, 27 and 29; `step1-signs/REPORT.md` line 54.

**Evidence.** Protocol line 38 predicted that H-LANG and H-ADMIN would both pass the base and the modifier tests. Both failed the modifier test. Row 23 weakens H-LANG ("modifiers as grammatical markers") and marks H-ADMIN "Consistent, with modifiers as subtypes or quantities". That auxiliary assumption is equally available to a logo-syllabic language, where a modifier can mark a subtype of what a logogram denotes, so applying it to one hypothesis only tilts the ledger. The step 1 report itself (line 54) says the observed pattern matched none of the four predictions.

Row 25 weakens H-EMBLEM "for freely arranged signs", and line 29 calls "a script of independent emblems arranged freely" the description most clearly weakened. That description is not in the ledger. H-EMBLEM is "fixed identity labels tied to owners, groups or images" (protocol table), and fixed multi-sign labels would also be kept whole at a line break. The protocol gave no per-hypothesis prediction for the line-break test. Row 27 lists every hypothesis as consistent or not decided, which under protocol line 20 makes it descriptive.

**Recommended change.** Rebuild the ledger strictly from the frozen predictions. In the step 1 row, record that H-LANG and H-ADMIN both failed their modifier prediction and that H-EMBLEM's base prediction ("weakly or not at all") was not quantified in advance. Move the line-break and closing-asymmetry results to a list of descriptive results. Delete the first sentence of line 29 or restate it in terms of the four ledger descriptions.

### 3. The step 2 copper conclusion is drawn outside the frozen rule

**Location.** `REPORT.md` line 9; `step2-image-text/REPORT.md` lines 1, 3, 17 and 23; protocol lines 44 and 55; `registry-entries.json`, IMAGE-TEXT-TABLETS.

**Evidence.** Protocol line 55 licenses "copper and tablet texts pair with their images inside their own genre" when 2d fails and 2a and 2c pass. On copper, 2c failed (19.2% against a majority rate of 26.9%, p = 0.26). Step 2 line 23 substitutes 2b, which is not in the rule, and `REPORT.md` line 9 headlines pairing "inside each tablet genre". Test 2a is the outcome protocol line 53 attributes to series production: the 12 hare tablets carry one text and the 11 anthropomorph tablets carry one text.

The review run `step2` examined 2b. On copper, 4 of the 33 same-class text pairs share any sign pair, one of them a near-duplicate (Levenshtein distance 1 or containment); without near-duplicates the difference is 0.024 (p = 0.025), so the copper 2b result is real but rests on three or four pairs. On bas-relief tablets, 2b without near-duplicates falls to 0.0017 (p = 0.15). Test 2c on the Harappa tablets survives the same exclusion (bas-relief 25.5% against a 21.5% majority, p = 0.0025; incised 55.6% against 48.1%, p = 0.004).

Protocol line 44 names `research/literature/copper_constraints.csv` as a published comparator. The manifest hashes it, but `analyze_step2.py` never reads it and no report mentions it. The file records Parpola's class-level observation (2008, pp. 134–136) that copper tablets of one image type share an obverse text, so the copper half of the headline is already published. Line 17 attributes 2a to "mould and casting series"; the Mohenjo-daro copper tablets are usually described as engraved, so the confound is a series of copies made to one model.

**Recommended change.** State the frozen decision genre by genre. For bas-relief and incised tablets, 2a and 2c pass and 2d fails, so the rule's conclusion applies. For copper, 2c fails, so the rule's conclusion does not apply; report copper 2b as descriptive, with the pair count. Cite Parpola (2008; 1994) for the copper image–text tie, and either compare against the comparator or record its omission in an amendment. Replace the "each tablet genre" headline with this scoped statement.

### 4. Step 1: catalogue order carries most of the family gain, and the interpretation exceeds the test

**Location.** `REPORT.md` line 7; `step1-signs/REPORT.md` lines 3, 34 and 54; `step1-signs/render_sheets.py` lines 59–77; `registry-entries.json`, SIGN-FAMILIES.

**Evidence.** The contact sheets present the glyphs in Wells code order, 48 to a sheet, each labelled with its code and token counts. The families follow that order closely. Coder 1's 78 attested families form 98 contiguous runs of the attested Wells sequence, 65 families are a single run, and 479 of 576 adjacent attested codes share a family; coder 2's 59 families form 87 runs, with 490 of 576 adjacent pairs shared. On the cut-or-not decision between adjacent codes, the coders agree with kappa 0.79 (review run `step1`).

The same run placed 85 random cuts on the Wells number line, with no visual judgement, 100 times. These partitions gain 0.0164 bits per sign on average (5th–95th percentile 0.0124–0.0197, maximum 0.0212), and every one exceeds the frozen null's 95th percentile of 0.0061. Coder 1's families gain 0.0219, above all 100. About three quarters of the family gain is therefore available from the order in which the Wells catalogue arranges signs by graphic class, and the coders' judgement adds about 0.005 bits per sign. The first-coder table was last written at 01:51:29, five and a half minutes after the last sheet (01:46:02).

The program was run by an AI model (protocol line 3), and the second coder was an agent it launched that reported its own procedure (RETROSPECTIVE line 13). Two instances of a model that may know the published sign lists, coding the same ordered sheets, do not support "it does not depend on one person's judgement" (step 1 line 34).

For signs unseen in training, the Parpola-level and Mahadevan-level groupings lower loss to 13.93 bits, against 14.19 for coder 1's families (`by_training_frequency` in the frozen summary). The published allograph lists do better on the rare signs the headline is about, which step 1 line 3 summarizes as "the same with smaller gains". Signs seen ten or more times gain nothing (4.847 to 4.859 bits), and no test examined contrast within a base, so "the base fixes where a sign can occur; added elements distinguish members within a base" (`REPORT.md` line 7, step 1 line 54) describes no measured result.

Three checks support the frozen result. Splitting the numeral families into singletons leaves the gain at 0.0231 (p = 0.005). One-substitution near-copies across folds do not carry it (finding 14). Adding the end symbol does not change it (finding 14).

**Recommended change.** Rewrite the headline along the lines of "Grouping Wells codes by graphic family improves held-out prediction of rare codes; random contiguous cuts of the Wells order recover about three quarters of the gain." Report the contiguous-partition comparison as post-outcome, disclose that both coders are AI agents working from code-ordered sheets with frequency labels, give the P and M unseen-sign losses, and delete the "base fixes" sentence. A further coding round should use sheets in shuffled order without counts.

## Moderate findings

### 5. The Ur III numeral value drops units, and this explains the failed calibration

**Location.** Protocol line 73; `step4-numerals/analyze_step4.py` lines 103–114; `step6-language/analyze_step6.py` lines 182–183; `step4-numerals/REPORT.md` line 7; `step6-language/REPORT.md` line 23; RETROSPECTIVE line 21.

**Evidence.** Protocol line 73 defines the Ur III value as the digit *n* of `NUM:n(unit)`. Of the 3,421 Ur III pairs, 865 have a unit other than diš, so 1(u) (ten), 1(geš₂) (sixty) and 1(barig) (a capacity measure) all receive value 1; 780 are the last token of a compound number, so 1(u) 5(diš) contributes 5; 268 are ordinals in -kam (review run `step4b`). Step 4 line 7 calls this "the digit of the numeral token" without these consequences.

With digit and unit kept (review run `step6-numeral-order`), the step 6 numeral-order test detects the Ur III number-before-commodity order: following excess 0.735 bits against preceding 0.514, where the frozen definition gave 0.266 against 0.282. The calibration failure reported in step 6 line 23 and RETROSPECTIVE line 21 comes from the value construction. The frozen descriptive label should stay, because the definition would change after the outcome.

The step 4 direction survives every repair tried. With system-distinguished values in both corpora (IVS stroke family plus count, Ur III digit plus unit; run `step4c`), IVS has 4.50 values per item against 6.09–7.05, a top share of 0.551 against 0.357–0.405, and MI over value entropy of 0.524 against 0.447–0.484. Protocol line 73 also asks for subsampling to the IVS number of qualifying items; `subsample()` matches tokens only, leaving Ur III with 38–48 items against 56. Rarefied to five tokens per item, IVS shows 2.43 values against 2.90–3.19 and a top share of 0.662 against 0.513–0.566. The plug-in MI is strongly biased at these sizes (the IVS permutation mean is 0.61 of 1.07 bits). Net of the permutation mean, the IVS ratio is 0.197 against 0.059–0.096 for Ur III. The Linear B raw ratio (0.499) exceeds IVS (0.457) while its net ratio is 0.090. The step 4 report gives no Linear B figures, although the registry entry says Linear B is "reported in full".

**Recommended change.** Describe the Ur III value construction in step 4. Add the unit-aware, rarefied and net-MI comparisons as labelled post-outcome sensitivities, report the Linear B figures, and prefer net MI in future protocols. Correct the stated cause of the calibration failure in step 6 and the retrospective.

### 6. Step 4 assumes the counted item follows the numeral

**Location.** `step4-numerals/REPORT.md` lines 3, 20 and 28; `REPORT.md` lines 13, 26 and 29.

**Evidence.** The frozen step 6 numeral-order test found the preceding sign more informative about IVS stroke values than the following sign (excess 0.480 against 0.407 bits; 0.819 against 0.691 with family-aware values in run `step6-numeral-order`). With the unit-aware calibration of finding 5, Ur III (number before commodity) shows following above preceding and Linear B (number after logogram) the reverse, so IVS falls on the Linear B side; this is post hoc and descriptive. Rerunning step 4 with the preceding sign as the item (run `step4-preceding`) gives a net MI ratio of 0.221 against 0.197, and the strongest fixed associations become the text-initial signs 861, 817 and 820 followed by two short strokes (98%, 92% and 77%), the opener pairs listed in step 3. The fixed and spread groups in step 4 line 20 depend on which side is taken as the item.

Step 4 line 28 says the result "rules out a reading of the stroke system as a uniform counting notation like Ur III accounting". The comparison sets seal and tablet texts against administrative accounts. A count written on an object that records a standard allotment, rank or capacity would also show one value per item. Stroke groups bound to particular signs and read as fixed expressions rather than counts are discussed by Parpola (1994), for example the stroke-and-fish groups, and Mahadevan's (1977) concordance tabulates the numeral–sign pairs.

**Recommended change.** Report the measures for both item directions and state the item definition as an assumption in the methods paragraph. Replace "rules out" with the measured contrast against Ur III accounts, add the genre difference to the methods, and cite the earlier numeral literature.

### 7. The step 1 decision was not applied to steps 2–4

**Location.** Protocol line 36; direction memo line 44; `step1-signs/analyze_step1.py` line 354.

**Evidence.** Protocol line 36 makes "W codes plus the coarsest grouping that passes" the working representation for steps 2–4, and the direction memo runs steps 2–5 after step 1 has fixed the representation. The summaries were written in the order step 2 (01:57:58), step 4 (02:02:19), step 3 line breaks (02:03:37), step 5 (02:05:31) and step 1 (02:08:40). A five-null smoke test at 01:56:24 had already shown the coder-1 families passing. No step 2–4 script uses a family layer, and step 1 line 54 adopts the layer "for later work". No amendment records the change. The code's adoption order also places coder 1 (85 groups) ahead of coder 2 (63 groups), although coder 2's is the coarsest passing grouping under the literal rule.

**Recommended change.** Add an amendment stating that steps 2–4 ran on W codes alone and why. A family-level version of 2d and of the segmentation would be the matching sensitivity. Reconcile the adoption with the "coarsest" wording.

### 8. The protocol's segmenter–line-break comparison was never run

**Location.** Protocol line 61 ("Each segmenter's agreement with line breaks is reported"); `step3-segmentation/REPORT.md`; `analyze_step3.py`.

**Evidence.** Neither step 3 script computes this. Review run `step3-segmenter-breaks` ran the frozen segmenters on the clean texts plus the 72 joined multi-line faces in both line orders. The Dirichlet-process segmenter places a boundary at 76 of 76 breaks in the forward order and 74 of 76 in the reverse, against 37% of other positions in the same texts. Greedy n-gram reaches 73 and 67 of 76 against 49%, and branching entropy 29 and 44 of 76 against 37%. These are recall figures: line breaks show where boundaries must fall, not where they must not. They are the only boundary evidence internal to IVS, and they qualify `REPORT.md` line 35 and step 5 line 26.

**Recommended change.** Add the result to step 3 as a protocol output computed in review, and use line breaks as the held-out check in the next segmentation work.

### 9. Step 5 generalizes beyond its own table

**Location.** `REPORT.md` line 15; `step5-rehearsal/REPORT.md` lines 3, 18 and 26.

**Evidence.** On Ur III seal legends, the cohort closest in genre to the Indus seals, branching entropy reaches boundary F1 0.692 and word F1 0.448, against 0.557 and 0.187 for a boundary everywhere (the Dirichlet-process segmenter: 0.604 and 0.301). The mean-F1 rule correctly chose the Dirichlet process, but "None recovers words well" (line 3) omits this. On gold words, alternation is 0.056–0.069 in all four corpora, so the statistic does not separate them even with perfect segmentation; the Kober-style failure belongs to the statistic at this scale. "Falls to a third or less of the true-word rate" (`REPORT.md` line 15) is wrong for two cohorts: Sumerian lines fall to 0.031 of 0.064 (48%) and seal legends to 0.021 of 0.056 (38%). Linear B, the script Kober's method was developed on, was planned for the rehearsal (direction memo line 50) and left out without comment.

**Recommended change.** Report the seal-legend result, scope the conclusion to the alternation statistic and the mean over cohorts, correct the fraction, and note the Linear B omission.

### 10. The modifier claim and the reported gains

**Location.** `step1-signs/REPORT.md` line 38; `REPORT.md` lines 7 and 23; `registry-entries.json`, SIGN-FAMILIES.

**Evidence.** With every code in its own class, the frozen class model still gains 0.0029 bits per sign (run `step1-identity`), because interpolating the Kneser–Ney bigram with an add-0.5 bigram helps on its own. The random-partition null controls for this, but the reported gains include it: the mixture accounts for more than half of the V, P and M gains (0.0043–0.0052) and for 0.0029 of the modifier-signature gain of 0.0035. Run `step1-coverage` shows that the modifier-signature groups cover 43.9% of held-out tokens and change their loss by −0.011 bits on average; the positive total comes from the other tokens. "It does show that no modifier class behaves like a uniform grammatical marker" (line 38) is a claim about each modifier, while the frozen test pooled them. Tested one at a time in the same run, none of nine modifiers passes (p from 0.14 to 0.93), so the sentence is supported only by this post-outcome test.

**Recommended change.** Report gains net of the identity partition. Either cite the per-modifier tests as post-outcome or restrict the sentence to the pooled grouping.

### 11. What test 2d could detect

**Location.** `step2-image-text/REPORT.md` line 19; `REPORT.md` line 9; `analyze_step2.py` line 193; step 2 amendment line 5.

**Evidence.** The null expectation is 3.0 matching hits, half of it (1.52) from the unicorn class, and the anthropomorph class has one matching seal. In run `step2`, raising each class's hit rate on matching seals to *k* times its rate on other seals gives power 0.22 at *k* = 2, 0.91 at *k* = 5 and 1.0 at *k* = 10. Counting seal objects instead of distinct text–animal pairs gives the same result (3 hits against 3.00, p = 0.62; run `step2-objects`). The Haldane odds ratios in `summary.json` exceed 1 for classes with no matching hit (anthropomorph 31.9, buffalo 11.0, goat 7.0), as the verifier also found; the amendment set `null` only for classes with no hits at all.

**Recommended change.** Replace "ordinary seal vocabulary that does not follow the animal" with the detectable effect (no enrichment of fivefold or more). Report each class's 2×2 counts with the expected matching count, or an exact conditional odds ratio with its interval.

### 12. Prior work is missing

**Location.** `REPORT.md` lines 5–17 and the step reports.

**Evidence and change.** Several results are presented under "What the six steps established" without the work that reported them first. Each report should name it in a related-work sentence. Graphic families and allograph grouping are the organizing principle of the Wells sign list and of Mahadevan's (1977) and Parpola's (1994) lists (step 1). The copper image–text tie is Parpola's (2008; 1994) (step 2). Segmentation of texts into recurring sequences goes back to Koskenniemi (1981) and appears in Yadav et al. (2010); whether line divisions were already used as segmentation evidence should be checked in Parpola (1994) and Wells' publications before step 3 calls the line-break result "independent evidence". Numerals in fixed sign combinations are discussed by Parpola (1994) and tabulated in Mahadevan's (1977) concordance (step 4). Positional concentration of text-final signs appears in Mahadevan's (1977) positional tables and in Yadav et al.'s (2010) analysis of text beginners and enders (step 6). The ledger's nonlinguistic descriptions should cite Farmer, Sproat and Witzel (2004) and Sproat (2014), and the entropy argument Rao et al. (2009).

## Minor findings

### 13. Step 3 line breaks: small errors and stronger controls

**Location.** `step3-segmentation/linebreaks.py` lines 32–33 and 70–74; `step3-segmentation/REPORT.md` lines 3, 11–14 and 24; `REPORT.md` line 11.

**Evidence.** The verifier showed that interior lines of the four three-line faces are counted twice, so 22.9% and 24.8% should read 22.7% and 24.1%. The table omits the 45 tied faces; the decision rests on 27 faces, which `REPORT.md` line 11 presents as "72 multi-line faces". Faces marked BUS are read with every line reversed, which is wrong for one line of a boustrophedon text; all three used BUS faces are ties. Six of the decided faces are Chanhu-daro seals with a separate line of stroke numerals, and the `/` in the catalogue may mark a sign group set apart in the seal field rather than a wrapped line, so "scribes kept recurring units whole when they wrapped text" (line 24) assumes the catalogue's meaning.

The result survives every control in run `step3`. Counting identical faces once gives 22 against 4 (p = 0.0005), and dropping faces with a numeral-only line gives 17 against 2 (p = 0.0007). Moving the break to every other position of the same joined text lowers the mean line-minus-crossing difference from 0.186 to 0.029 (forward order; p = 0.0001 for the observed sum against a random other cut per face, and the same in the reverse order), so the result does not come from lines containing text edges. Virtual breaks placed in single-line texts of the same length favour lines in 63% of decided cases, against 96% for real faces in the same forward order.

**Recommended change.** Correct the two rates, show ties, handle BUS faces line by line, word the break as "where the catalogue marks a line division", and add the shifted-break control as post-outcome support.

### 14. Step 1 implementation details with no effect on the result

The protocol's baseline has start and end symbols (line 34), but `Data` in `analyze_step1.py` adds no end symbol. With it, the family gain is 0.0222 (p = 0.0099 with 100 nulls; run `step1`). Union-find links 206 distinct texts through 464 object families into one component, which puts 537 texts in fold 0 against 312–344 elsewhere; this is over-grouping, not leakage. Near-copies differing in one sign can cross folds, but only 22 of 615 rare held-out tokens have a same-family one-substitution copy in training, and refolding with such pairs joined gives a gain of 0.0265 (p = 0.005; run `step1-nearcopies`). The kappa list in step 1 line 7 omits cap (0.74) and hold (0.61). The "Groups" column counts unattested codes (85 against 78 attested families). The report should mention the end symbol and the fold sizes and complete the kappa list.

### 15. Step 2 smaller departures

Tests 2b and 2c use 2,000 permutations (`analyze_step2.py` lines 235–236), where protocol line 50 specifies 10,000 for 2c. The label merges (unicorn variants, goat variants, short-horned bulls) are defined in code, not in the protocol, and `Bull:i:J` and `CompBull` stay separate from the unicorn and composite classes. The amendment was written 34 seconds after the first run printed its 2d result (p = 0.845); "before its 2d result was interpreted" should say that the output had been seen. The correction follows the protocol text and did not move the result toward significance.

### 16. Step 6 smaller points

Protocol line 87 lists the segment length distribution as profile item (iv). It is not reported, and the amendment does not drop it. `typology.json` states that its values were entered from memory and not checked; step 6 line 27 states them as facts. The clean frame contains only texts the catalogue marks R/L, so the reading direction, and with it which end is "final", is a catalogue judgement; the report should say how direction was determined for these texts.

### 17. Prose

The following sentences break `knowledge/editorial/WRITING.md` or could be read as language evidence.

- `REPORT.md` line 5, "What the six steps established": several results are descriptive or null. "Results" is accurate.
- `REPORT.md` line 29, "numerals that sometimes count": counting is an interpretation; "numerals that take many values before some signs and one value before others" states the measurement.
- `step2-image-text/REPORT.md` line 3, "The texts therefore belong to their image within a genre": vague; state what 2a and 2c measured.
- `step3-segmentation/REPORT.md` line 3, "independent evidence", and line 24, "any account of the script has to explain": rhetorical; give the measured contrast.
- `step4-numerals/REPORT.md` line 28, "rules out" (finding 6).
- `step5-rehearsal/REPORT.md` line 26, "The finding also bounds earlier and future work": no content; say which claims it affects.
- `step6-language/REPORT.md` line 3, "survives every shuffle", and line 27, "which matches the IVS asymmetry" placed directly after the list of South Asian candidates: a reader can take this as support for a head-final South Asian language. Finding 1 gives the replacement.
- `step1-signs/REPORT.md` line 34, "so it does not depend on one person's judgement" (finding 4).

`RETROSPECTIVE.md` line 26 says the review files are in `review/` "with the responses recorded beside them", `README.md` lists `review/`, and the registry status reads "verified-reviewed". These were written before the review existed; update them when the responses are recorded.

## Checks that found no error

The Dirichlet-process Gibbs conditional in `segmenters.py` matches the exact ratio of joint probabilities under the Goldwater, Griffiths and Johnson unigram model to within 5×10⁻¹⁴ over 300 random states (`check_dpseg.py`). The Kneser–Ney and class-model probabilities in `analyze_step1.py` are normalized over the vocabulary; the class terms use training counts only, λ is chosen on component-grouped inner folds, and identical texts cannot cross folds. The step 1 null permutes class labels over the vocabulary with the start class fixed and uses the upper tail, as the protocol states. The step 2 nulls permute labels over objects (2a), text types (2b, 2c) and seal text–animal pairs (2d), all one-sided upper. The corrected 2d specificity rule matches protocol line 51. The step 3 crossing windows straddle the break as intended, apart from the interior-line double count. The step 4 numeral items and the step 6 edge-asymmetry statistic are computed as their reports describe. The near-fixed numeral combinations are not a single production series: 520 after three strokes occurs in 38 distinct texts from five named sites and one unrecorded site, and 585 after seven in 16 texts from four sites (run `step4b`).

## Reproducing the review runs

From the repository root, run `python -X utf8 experiments/2026-10-12-structure-first/review/<script> --out data/raw/2026-10-12-structure-first/review-2026-10-12/<directory>` with these pairs: `review_step1.py` (`step1`), `review_step1_coverage.py` (`step1-coverage`), `review_step1_identity.py` (`step1-identity`), `review_step1_nearcopies.py` (`step1-nearcopies`), `review_step2.py` (`step2`), `review_step2_objects.py` (`step2-objects`), `review_step3.py` (`step3`), `review_step3_segmenter_breaks.py` (`step3-segmenter-breaks`), `review_step4.py` (`step4b`), `review_step4_units.py` (`step4c`), `review_step4_preceding.py` (`step4-preceding`), `review_step6.py` (`step6`) and `review_step6_numeral_order.py` (`step6-numeral-order`). `check_dpseg.py` takes no arguments and prints its result. The empty directory `review-2026-10-12/step4` is a first attempt of `review_step4.py` that stopped on a value-encoding error before writing; `step4b` is the complete run.

## Responses

To be recorded by the program owner beside each finding.
