# Review of package Q, PDF extension and two-coder integration

Reviewed on 9 October 2026 against commit e14d9b3. I wrote only this file and `review-pdf/`. The earlier `REVIEW.md` and `review/` are unchanged. Temporary files lived in `data/raw/2026-10-08-bonta-review/reviewer-pdf-tmp/` and were deleted at the end. Evidence paths below are relative to the package directory.

## Verdict

Every computed number in the README and REPORT reproduces. The README commands regenerate the lexical, field, fish and validation outputs, with `lexical-test.json` differing only in its added `explicit_caption_only` field. The three-mapping replay reproduces the sensitivity outputs. The package verifiers pass 1,006/1,006 and 5,822/5,822 on the current tree. My own lexical code, written without importing the package's, gives 84/228, 83/206 and the same tails. The first coder's mapping was frozen by hash and committed (c6164ee, 01:00:56 EDT) before the second coder started (01:01 EDT) and before either return file was written (01:12 and 01:14 EDT). The packet contains no Bonta values and no first-coder answers. The problems are in what the numbers are made to mean. The clear-origin lexical subset, which carries the claim that the lexical excess is not circular, cannot detect an excess: three of its five strings are mahā- readings that its own construction makes unmatchable, and both matches rest on a pāla value that Bonta reached through lexical reasoning. The canonical field test reports 349 conflicts, of which 215 are jar or arrow in penultimate position, which PDF p. 15 permits, and 683 of the 942 clean texts contain no M field. Four objects (six readings) are probably joined to the wrong corpus object through a mistyped CISI alias. The REPORT opening ranks the lexical result more favourably than these findings allow.

## Checked claims

| Claim | Evidence | Result | Note |
|---|---|---|---|
| PDF SHA-256 12e8e6…5f14, 259 pages, Ghostscript 9.26, dated 3 June 2024, no folios | `pdf-2026-10-09-v1/witness-v3.json` | confirmed | recomputed hash; no page labels or printed numbers |
| 58 labelled Table 18 entries, 65 drawings, 17 caption forms, 14 field targets, 96 targets | `sign-catalogue-index.json`, `mapping-v2-frozen.json` | confirmed | package verifier and my contact sheet of the 96 packet crops |
| 1,200 rows, 859 attempts, 549 labels, 718 with transcription, 103 unclear flags, 713 joined, 338 families, 340 aliases, 146 unjoined | `reading-coverage-v5.json` | confirmed | recounted from the local inventory; see inventory defects below |
| Selection 640/859, 603 explicit-caption occurrences, 219 excluded | `lexical-selection-v2.json` | confirmed | all 603 caption strings occur on their cited PDF pages |
| Exact 73/196, 84/228, 72/174, 83/206, null means 23.78, 27.83, 24.07, 28.75, tails .0005 | `lexical-test.json`, `lexical-caption-sensitivity.json` | confirmed | rerun byte-identical; my own code gives means 27.89 and 28.54 |
| Normalized 100/228 (45.09) and 98/206 (46.39) | same | confirmed | |
| Clear-origin 2/5 exact (mean 0.75, 24/120 = .20), 3/5 normalized (70/120) | `lexical-caption-sensitivity.json` | confirmed | the frozen full selection gives 2/7; the README table omits it |
| Agreed-only 53/123, 52/108, 0/1; 330/640 and 303 retained occurrences | `two-coder-2026-10-09-v1/comparison.json` | confirmed | rerun identical |
| Fields 942/349/1178, 781/302/1386, 844/379/1246; shuffle means 419.87, 363.80, 380.65 | `pdf-2026-10-09-v1/field-test.json`, `two-coder-2026-10-09-v1/` | confirmed | numbers reproduce; interpretation discrepancy below |
| Fish adjacency 142/142/135 against 55.72/55.72/54.73 | `fish-units.json`, `comparison.json` | confirmed | |
| Mayig overlap 78/96, 72 exact, 10 disjoint, 8 first-coder missing, kappa 0.9217 (n=78) | `two-coder-2026-10-09-v1/agreement.json` | confirmed | recomputed; Wells 42 exact, kappa 0.9109 (46); Helsinki 6 exact, kappa 0.7193 (8); both-high 48/49; type splits 51/65, 16/17, 11/14 |
| Attribution: B069 alone changes 153 classifications, B078 62, B074/B075 omission 32/21 | `target-attribution.json` | confirmed | recomputed in `review-pdf/attribution-recheck.json` |
| Alias joins 713/859 and 338 families under all mappings; reference-supported 389/456/228 | `comparison.json` | confirmed | |
| Zero individually identifiable historical held-out entries | `lexical-test.json` | discrepancy | the derivation tables identify 129 derivation objects; a partial split is possible (below) |
| Clear-origin subset shows no detectable excess, which survives the mappings | REPORT opening, README | discrepancy | the subset has no power; first and second mappings are equal by construction |
| Canonical field rule reproduces the paper's T field | `field-rules.json` | discrepancy | T is narrower than p. 15 |
| 713 explicit CISI joins, none by equal ICIT numbers | `reading-coverage-v5.json` | confirmed with a defect | structurally CISI-only; ten objects carry a conflicting printed ICIT number |
| Registry entry outcome | `registry-entry.json` | discrepancy | the text has lost its spaces (see fixes) |

## 1. Value-derivation classification

I read the PDF passages on how each of the 58 values was reached and classified them independently (`review-pdf/derivation-recheck.json`). Fifty-three entries agree with `value-derivations-v2.json` at the level of its four classes. The 49 "later extension" labels are fair for the great majority: pp. 77 and 106–168 describe repeated trial and cross-checking against known values, and several entries say that the value was the only one consistent with the data. PU and PATI are correctly placed as dictionary cross-checks (pp. 70–71, 75–76). The classification is too strict for five entries and too generous for three.

Too strict: mIn(a) (entry 29) is an M-field anchor (the fish as a weight unit, pp. 45–46, 55, 189), and AS, ISH and ASTI (50–52) are 2014 values argued from the predicate and possession construction (pp. 56–66). cAru (31) takes its value caru from the pot-like drawing and its stroke-numeral contexts (p. 185). None of these is a dictionary search.

Too generous: PAla (17) has two values with different histories. Pala comes from the M-field and weight context (pp. 50–51), while pāla came when Bonta realised that the sign is a common final element of names recorded in Monier-Williams (pp. 67–68, 202), and bala is fitted to balapati (p. 76). ASHVA (48) and GO (49) are pictorial, yet p. 215 supports ASHVA by the plausibility of seven of its eight readings and calls the value provisional, and p. 216 calls GO more tentative. These two values rest on the same readings the test scores. The locators for entries 18 and 19 (p. 68, where the bow derivation is at pp. 45–47, 55), 48 (p. 216; comments are on p. 215) and 49 (p. 217; p. 216) are off.

Recomputing the clear-origin result under each reading of the paper's account (`review-pdf/lexical-recheck.json`, exhaustive for the small sets, 1,999 draws for the largest; explicit-caption selection):

| Subset | Roles | Types | Exact hits (null mean) | Exact tail | Normalized hits (null mean) | Normalized tail |
|---|---|---:|---|---:|---|---:|
| Package clear-origin | 6, 17–19, 36, 48, 49; maha and bala dropped | 5 | 2 (0.75) | .20 | 3 (2.75) | .58 |
| Without ASHVA and GO | 6, 17–19, 36 | 3 | 1 (0.50) | .42 | 2 (2.00) | .75 |
| PAla restricted to pala | package roles | 5 | 0 (0.00) | 1.00 | 3 (2.75) | .58 |
| Plus fish and the 2014 values | add 29, 50–52 | 7 | 2 (0.70) | .17 | 3 (2.57) | .48 |
| Plus caru, vI and (e)ka | add 31, 12, 15 | 15 | 6 (4.42) | .20 | 8 (6.90) | .37 |
| Only types the subset can match | 17–19, 48 | 2 | 2 (0.67) | .33 | 2 (1.33) | .67 |

Two features of the package subset explain why it cannot support a conclusion. Three of its five types (mA with PAla, DAna and ASHVA) are the mahā- readings Bonta glosses as mahāpāla, mahādhana and mahāśva (pp. 110, 208, 216). Dropping maha, as the protocol requires, makes them unmatchable, so the best possible score is 2/5. The null histogram over the 120 assignments is 60, 36, 18 and 6 assignments scoring 0, 1, 2 and 3, so a tail of .05 needs three hits, and the subset can reach only two. The two matches are dhanapāla (the reading that led Bonta to pāla, pp. 68–69) and aśvapāla, and both depend on pāla. Broadening the subset to every value the paper derives without a dictionary search leaves the exact tail at .17 or higher in every variant, and none approaches .05. This subset has no power in either direction, so the REPORT's statement that its absence of excess survives all mappings carries no information. Under agreed-only it holds a single type.

The early values can be split in part. The 129 MH and ICIT labels used in the derivation narrative and Tables 7–17 (pp. 39–77) are objects Bonta had seen when he fixed the early values. Restricting to selected readings whose roles are all early values (PU, PATI, ma, pala, dhana, tra, mina and the 2014 values) gives 16 types and 11 exact hits against a null mean of 3.76. Excluding derivation objects leaves 8 types with 5 hits against 2.14 (tail .026; `review-pdf/heldout-sensitivity.json`). All five hits use PU, PATI or maha, the three values the paper reports finding or fitting through the dictionary. Without those three values and without bala, the same split gives 0 of 3 hits. The paper says the early values were adopted after repeated confirmation (p. 76), so this split is not sealed. It does show that "zero held-out entries" refers only to sealed batches.

## 2. Lexical tests

The README commands reproduce 83/206 (tail .0005), 52/108 (agreed-only, .0005), 2/5 (.20) and 0/1 (1.0). The 603 explicit-caption occurrences behind the 206 types all have their proposed string on the cited PDF page, and every type has as many caption tokens as roles. The strings are Bonta's own captions. What the test scores is whether some combination of his Table 18 variants for those roles forms a headword, so his gloss is used only to locate the glyph window. In the figure checks of section 3, the caption tokens sit on the right-hand glyphs in reading order, and for the long inscriptions R0887, R0928 and R0430 the caption covers only the underlined part of the figure.

The null permutes the value bundles among the roles in the panel. That keeps the inventory, the variants, the initial-only maha restriction (it travels with the bundle) and the sequence set fixed. I added a null that permutes only within Table 18 classes (CV, VCV, CVC(V), CCV, logograms, ligatures). The excess stays: 83 hits against a mean of 35.2 (maximum 55 in 1,999 draws) for explicit captions, and 98 against 54.6 normalized. A smaller point is that the bundles come from the Table 18 lists, and some section headers state additional variants, mostly vowel length and sibilants (SENA stored only as senā, ARYA as ārya, for example). The exact endpoint is therefore slightly conservative, and the normalized endpoint, which collapses those differences, matches Bonta's own position that vowel length is not distinguished (p. 68).

The dictionary pin and licence are recorded. `sources.json` (id `MW`) gives sanskrit-lexicon/csl-orig commit 55e8add…, the file hash 555ecf5a…cff8 (which matches the local file and `lexical-selection-v2.json`), 194,059 alphabetic headwords, and CC BY-SA 4.0 from the repository LICENSE, which the local copy confirms. The REPORT notes that a dictionary-specific licence was not located. The data are untracked.

## 3. Reading inventory and joins

I drew 30 attempts with seed 20261016 (16 explicit-caption, 4 other selected, 8 unselected, one Table 21 entry, one unclear-flagged) and compared label, caption, glyph order and count, and role against rendered figures and the Table 18 crops (`review-pdf/sample-readings.json`). Twenty-eight are fully consistent. Two show extraction defects: R1097 stores the catalogue code H-206 as its transcription, and R0146 omits the caption transcription SA-DEVA that is on the page. Counting across the inventory, four continuation rows share the first defect and twelve rows with an evident bracketed transcription have an empty `proposed_reading`, which includes five readings of MH9091 (deva dhanapāla). The unclear flag uses a keyword list without "doubtful", "questionable" or a question mark. My keyword search (those words and any question mark) finds 94 attempt rows with such wording, 60 of them unflagged; R0354, whose transcription the paper calls doubtful, is one. The role column is almost entirely a default: 812 of 859 attempts read "not individually labelled", and 704 are "illustration" without a derivation or check distinction. The derivation-section readings of Tables 15 and 16 (bhūdhana, bhūma) are inventoried but not counted as attempts.

I recomputed the join from the printed CISI aliases and the pinned Lipi faces. It equals the package's join. No joined record is reached through a corpus ICIT-like number. In the 12 sampled joins in `review-pdf/join-audit.json`, the printed alias, the corpus CISI code and the site agree in every case; three figures are shorter than the corpus text (5 against 10 glyphs, 7 against 17, 3 against 7), which fits the partial figures the paper often prints. Glyph count equals the joined text length for 573 of 713 attempts and is within one for 79 more. The audit found one thing the package missed. For 20 attempt rows (10 objects), the ICIT number printed in the manuscript differs from the ICIT-style family of the joined corpus object. For six of them, at four objects, the figure's glyph count equals that of the object the printed ICIT number names, and differs from the CISI-joined one:

| Printed CISI | Printed ICIT | Corpus object of ICIT number | Figure glyphs | Joined object length | ICIT object length | Rows |
|---|---|---|---:|---:|---:|---|
| H-271 | 513 | H-1671 | 6 | 4 | 6 | R0374 |
| M-707 | 2983 | M-507 | 4 | 7 | 4 | R0633, R0860, R0873 |
| M-106 | 3401 | M-1016 | 4 | 6 | 4 | R0917 |
| M-122 | 3557 | M-1221 | 7 | 3 | 7 | R0951 |

M-122 and M-106 look like M-1221 and M-1016 with a dropped digit, but length agreement is suggestive only, because partial figures are common. In five of the other six disagreements the CISI object matches the figure and the printed ICIT number is probably a typing error (M-356 is printed with ICIT 2582 where the corpus has 2852); K-59 matches neither object. The 33 source-qualified entries are a different set. These joins are about 1% of 713 and leave the headline counts standing, but the object counts and any object-level audit need them flagged. Twenty-one of the 146 unjoined attempts could join through the same label in another joined row, the basis the package used only for Table 21.

## 4. Field test

`field-rules.json` follows the paper for P (the juncture closing the prefix; two of the three juncture signs are P-exclusive, p. 20, which I confirmed on the rendered page), for M (O at most two, F at most three non-repeating, MS = MA-like sign with the stroke numeral; p. 21), for C as residual, and for the exclusion of the 19 Table 19 templates. The repeated-O conflict is an unstated extension affecting three texts. The T rule departs from the text. Rendered p. 15 says the jar sign almost always occurs in final or penultimate position, and p. 57 describes further terminal-environment signs. The rule accepts only a final jar or arrow, and the rule's source list omits pp. 15 and 57.

I reimplemented the classifier and reproduced 942/349/1178 and the shuffle mean 419.87 (395–445) exactly. Then I changed the one condition. Among the 289 texts flagged for a terminal outside the final slot, 215 have it in penultimate position and 280 have no other reason. Admitting a penultimate terminal gives:

| Rule | Clean | Conflict | Indeterminate | Shuffle mean clean (95%) | Tail |
|---|---:|---:|---:|---|---:|
| Package, final only | 942 | 349 | 1,178 | 419.9 (395–445) | .0005 |
| Final or penultimate (p. 15) | 1,144 | 136 | 1,189 | 622.5 (596–649) | .0005 |

The excess over shuffles holds, and the conflict count falls by 61%. The composition of the clean texts also matters. Of 942, 259 contain an M field, 323 are C plus T only (a text ending in a jar or arrow), and the rest have a P juncture without M. The clean-count excess therefore restates mainly the final jar and arrow tendency that package D2 already measured. The paper's distinctive claim is the M order. Among the 331 texts with two or more M units, 288 (87.0%) are in O-F-MS order, against a mean of 58.9% (54.4–63.4%) when the units of each text are shuffled (tail .0005; `review-pdf/field-decomposition.json`). That is the cleaner ordering result and belongs in the REPORT.

## 5. Agreement

I recomputed every agreement figure from `mapping-v2-frozen.json` and `coder2-merged.json` (`review-pdf/agreement-recheck.json`); they match to four places, and the confidence and type splits match. The mapping hash 0ab1c267…40aa5 appears in the freeze record, in the registration, and in the git blob at c6164ee. The 794 packet files match the manifest hashes, the manifest records `contains_first_mapping` and `contains_author_values` as false, the text files contain none of Bonta's labels or values, and the 96 crops are bare drawings (nine carry inherited JPEG metadata only). Part 1 reports opening nothing outside the packet except its helper folder and a listing of the parent folder, and the coordinator's brief relays the same for part 2.

Three limits on reading the agreement. Kappa equals raw agreement for practical purposes here, because the chance term is 0.018 over about 80 classes. The first coder's basis text is boilerplate for most rows, and for the 17 caption forms it says the drawings were compared "with Table 18 family", so for those rows the first coding was informed by Bonta's grouping while the second was blind. The second coder separated half-height from full-height strokes by the ink-to-box ratio of the crop and flags that inference as the main uncertainty for the juncture and stroke signs that define the field test.

## 6. Report and boundaries

The REPORT opening should rank the evidence as follows: the positional tendencies and the M ordering are the strongest result; the lexical excess exists but is conditional and mostly circular for values found by dictionary search (the 13/720 and eight-of-ten PU/PATI finding has dropped from the opening); the clear-origin subset is uninformative; the validation rate, field boundaries and physical metrology cannot be judged from the sources. The current opening says the lexical excess "also survives", says the clear-origin absence of excess survives all mappings, and counts conflicts without saying how many the rule creates. "Zero held-out" is stated without the partial split. The first and second mappings yield identical lexical scores because the test never reads the mapping, so "survives all three mappings" holds trivially for the lexical result. "Two AI coding rounds without specialist review" appears four times in the REPORT and twice in the README. The validation section uses "PDF p. 5" for the manuscript foreword and, a few lines later, for the undated introductory letter hosted by Jeff Lindsay, which is a separate document.

No tracked file carries PDF crops or page images (no image files are tracked in the package; the PDF, captions, dictionary and sources are untracked and ignored). A 16-word scan of all 317 text files in the package and review directories against the PDF text, the page-text witness, the 12 captions, the letter and the IMSc text finds only the manuscript's exact title and a list of sign labels. Ledger quotations are seven, each at most 11 words. The prose scan reports no flags in 34 files, which cannot catch the spacing defect in `registry-entry.json`. `git status --porcelain` shows `.gitignore`, `knowledge/INDEX.md` and `knowledge/experiments/registry.json` modified and the other contributors' untracked directories, all present at session start, plus my `review-pdf/` and this file. No package file changed.

## Reproduction log

| Step | Command (from the repository root) | Result |
|---|---|---|
| Lexical, full and caption-only | `pdf_lexical.py score` with `--output-root review-pdf/rerun-01` | identical (parsed JSON); `lexical-caption-sensitivity.json` byte-identical |
| Fields, fish, validation | `pdf_fields.py`, `pdf_validation.py` to `review-pdf/rerun-01` | byte-identical; four raw prediction and annotation files hash-identical |
| Three-mapping sensitivity | `second_coder_sensitivity.py prepare`, then `field`, `lexical`, `joins` for first, second and agreed_only to `review-pdf/rerun-02` | 27 of 31 JSON files identical; differences are set order in `MS_patterns` (three files) and the protocol hash in the registration |
| Package verifiers | `verify_pdf_followup.py`, `verify_second_coder.py` with `--output review-pdf/...` | 1,006/1,006 and 5,822/5,822 |
| Reviewer code | `lexical_recheck.py`, `field_decomposition.py`, `field_penultimate.py`, `heldout_sensitivity.py`, `join_audit.py`, `agreement_recheck.py`, `attribution_recheck.py`, `derivation_recheck.py`, `sample_readings.py` | outputs in `review-pdf/` |

The package's own README verification step uses saved replay directories that I did not recreate; I compared my reruns with the package outputs directly.

## Source checks

I opened the PDF itself and checked cited sources against the local witnesses or the web. Titles, authors, years and attributed content are accurate for: Bonta's introductory letter (the quoted wording is in the letter's text, a document separate from the manuscript); the IMSc *Annual Report 2014–2015* (Bonta listed as an invited speaker, meeting 4–5 May 2015, PDF p. 92); Sengupta's fish-symbolism article (Bonta's mina proposal, citing Bonta 2010: 57–59); Rao's *The Indus Script and Economics* (follows Wells and Bonta on patterned and complex texts); Yajnadevam's manuscript (cites Bonta's compounding argument); Morpurgo Davies, "Decipherment" (rendered p. 420 states the tested-on-results and coherence criteria); Mahadevan's account of Parpola's rebus conditions on harappa.com; Krishnamurti, *The Dravidian Languages* (Cambridge University Press, 2003, chapter 6, whose summary gives noun-noun compounds with an example); Fairservis (honorific suffix passages present; I did not check the cited page numbers); the Cologne repository licence. Language Log's post is dated 6 March 2025, but the chance-hit remark is a 7 March reader comment quoting a YouTube comment, so "6 March discussion" should say that. Mukhopadhyay (2019) could not be opened by me: the local file is the interstitial the sources record, and Nature redirected to its identity service, so its content is unverifiable here. The Kalyanaraman page is correctly recorded as unverified.

## Method and scope

The protocol amendments precede the outputs they govern: the freeze and registration hashes match, the package verifier checks the protocol prefix hashes for P-L and P-W, and git places the mapping before the returns. Exploratory and post-outcome labels are present on the caption sensitivity, the target attribution and the clear-origin construction. Two registered choices shape the results beyond what the REPORT says: the maha restriction removes three of five clear-origin types, and the classification of ASHVA and GO as pictorial gives the second clear-origin hit. I found no claim of decipherment, no authenticated sound or meaning, and no rights problem in tracked files. My own outputs carry identifiers and counts only; corpus text codes stay out of them.

## Required fixes

1. Rewrite the lexical part of the REPORT opening and the clear-origin conclusion. State that the subset cannot detect an excess (best attainable 2/5, tail .20), that its two matches use the pāla value reached through lexical reasoning and the ASHVA value supported by its own readings, and that adding the values the paper derives without a dictionary search leaves the exact tail at .17 or higher. Reclassify entries 29, 31 and 50–52, mark pāla, ASHVA and GO as mixed, and correct the locators for entries 18, 19, 48 and 49 in a new versioned derivation file.
2. Correct the field-test reporting. Either admit a penultimate terminal, as p. 15 does, or rename the 215 penultimate cases "outside the registered rule" instead of conflicts. Add the M-order result (288/331) and say that 683 of 942 clean texts have no M field.
3. Flag the four objects with conflicting CISI and ICIT identifiers (H-271/513, M-707/2983, M-106/3401, M-122/3557) as probable misjoins, and report the 338 object families with and without them.
4. Replace "zero identifiable held-out entries" with a statement of the derivation-object split and its caveat.
5. Repair `registry-entry.json`, whose outcome string runs words together ("means55.72", "Full lexical84/228", "Clear-origin2/5", "ICIT68firstlabels48joined").
6. Rewrite the REPORT and README openings in ranked order, state each caveat once, and name which letter or document "PDF p. 5" refers to.

## Optional improvements

- Fix the 4 catalogue-code transcriptions and 12 unparsed transcriptions, add "doubtful", "questionable" and "?" to the unclear flag, and record the derivation-section readings of Tables 13–17 as derivation attempts.
- Report the class-restricted null beside the global one and the exact-versus-normalized difference for logograms whose bundles omit a stated vowel-length variant.
- Report the full-selection clear-origin result (2/7) in the README table.
- Note that the first coder compared the 17 caption forms with the Table 18 family and so was not blind for them.
- Join the 21 unjoined attempts that share a label with a joined row, labelled as a same-manuscript alias join.
- Say in the Language Log citation that the chance-hit remark is a reader comment of 7 March 2025.
