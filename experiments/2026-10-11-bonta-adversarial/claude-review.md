# Adversarial review: Bonta extension, October 11 iteration

## Verdict

The structural core of the report holds up. Several of the reviewed signs strongly prefer the last position in a text. That result survives both the BH adjustment and the maximum-statistic check, and the demotions of ati, sam and sa were the right call. The ranking and grouping inside the carrier family do not hold up. The way W154, W156 and W158 are grouped is contradicted by the contexts they actually occur in.

The data also contain more specific evidence than the report uses. The carriers with jar-shaped heads (W154, W156) often follow stroke numerals; the plain carrier W151 never does in the witness strings I checked. The carrier signs are often followed by the comb sign W400. W154 and W158 share a fixed multi-sign formula that W156 never takes part in. These patterns allow sharper tests than final position, which about 40 codes and the jar sign all share.

The lexical control has a sandhi defect: it joins Sanskrit word parts without applying the sound changes at the join. That produces at least two false "not attested" results. Its support counts also have no baseline to compare against. The public catalogue shows the same drawing for W154, W156 and W158, so readers cannot see the differences the cards argue about. None of this argues for dropping the imaginative candidates. It argues for regrouping them and testing what the contexts actually predict.

## What I inspected and what I did not run

- **Tools:** I had only Read, Glob and Grep, so **I executed nothing**. I did not re-run any permutation, BH, maximum-statistic, Fisher or lexical calculation.
- **Code checked by reading:** `analyze.py`, `robustness.py` and `verify.py`. The permutation sampling, the BH step-up procedure, the maximum-statistic comparison and the Fisher hypergeometric sum all look correctly implemented.
- **Numbers cited below** come from the saved outputs, or from my own hand tallies of the distinct strings in the local `data/raw/2026-10-11-bonta-adversarial/run-v2/observation-witnesses.json` and `substitution-witnesses.json`. The hand tallies are marked as such and need a scripted recount.
- **Dictionary checks:** I verified Monier-Williams (MW) entries by searching the pinned local `mw.txt`.
- **Images:** I viewed all seven requested images. I did not open `catalogue.html` in a browser; I read its template and `catalogue-data.json` instead.
- **Not reviewed:** a new `subreviews/` directory appeared during this session.

## Findings, in priority order

### 1. High: the separation of W158 from W154/W156 is not supported by its contexts

**Where:** `REPORT.md:46`, `hypotheses.py:39-42`, `run-v2/robustness.json` `variant_contrasts[1]`

The Fisher test (p = 0.0062) treats "final" as the role being compared. Hand tallies of W158's 19 distinct strings show:
- 7 have W158 last.
- 10 have W158 immediately before W400.
- 1 has it immediately before the jar sign W740.
- 1 has it first.

So 18 of 19 W158 tokens are either last or directly before a closing sign. The equivalent figure for W154 is 31 of 32 (25 last, 5 before W400, 1 before W740). The real difference is how often W400 is attached after the carrier, not whether W158 is a closing sign.

Two further observations point the same way:
- **Shared formula.** W154 and W158 share a fixed formula, W46x–W806–carrier, optionally followed by W400 (W46x means one of W465–W475). W806 directly precedes W154 in 13 of 32 strings and W158 in 8 of 19, but W156 in none of its 34.
- **Template length.** The two templates W154 shares with W158 are three and four signs long, with the carrier in an internal slot. Three of the four templates W154 shares with W156 are two-sign texts.

On context evidence, W154 is at least as close to W158 as to W156. Strings that share a formula are not independent, so the Fisher test overstates the evidence.

**Remedy:**
- Define a closing block as the last sign plus a directly preceding carrier when the last sign is W400 or W740.
- Rerun the contrast on that basis.
- Cluster strings that share a preceding pair of signs, and report the effective sample size.
- Treat W154, W156 and W158 as one jar-head carrier complex that is split by context, not as a pooled pair plus an excluded code.

### 2. High: the substitution evidence was summarized selectively and is incomplete

**Where:** `REPORT.md:44`, `analyze.py:179`

The most frequent substitute for W151 is the jar W740, in 8 of 16 templates. The report does not mention this. It means the carrier mostly occupies the generic closing slot that the earlier audit already attributed to the jar (838/1,196 final).

The four templates shared by W154 and W156 are:
- W003 + carrier
- W004 + carrier
- W005 + carrier
- W255–W435 + carrier

So the shared slot is mainly "after a stroke numeral". The catalogue examples H-366 and H-81 are both "W003 + carrier".

W527 and W617 are missing from the `selected` list in `analyze.py:179`, so the shortlist cites templates for W527 only through W400's row, and W617 has no template audit of its own. The public `substitution-audit.json` contains no template lengths, so readers cannot check the claim that many templates are short.

**Remedy:**
- Add W527, W617 and W158 to the substitution audit.
- Publish template-length distributions and the class of each substitute (numeral, jar, person sign) as aggregates.
- State in the report that the jar is W151's main substitute.

### 3. High: position tests do not discriminate between meanings, and part of the enrichment comes from partner signs

**Where:** `REPORT.md:3`, `REPORT.md:30-38`

A within-text shuffle cannot separate a sign's own preference for last position from its partner's preference for first position. In two-sign texts, "last" simply means "the partner went first", and numerals strongly go first. By hand tally:

| Code | Final tokens in two-sign strings |
|---|---|
| W156 | 12 of 26 |
| W154 | 5 of 25 |
| W161 | 3 of 10 |

The opening claim that carriers show the "closest agreement between their pictures and repeated closing positions" adds an unstated grammatical assumption: no picture of a carrier predicts last position on its own. The table also shows p at the resolution floor (1/5,001) and so hides the ordering. The z-scores do show it:

| Code | Final-position z |
|---|---:|
| W400 | 19.7 |
| W527 | 10.2 |
| W151 | 9.6 |
| W154 | 6.9 |
| W617 | 5.5 |
| W156 | 5.4 |
| W161 | 5.0 |

**Remedy:**
- Report the z-scores in the table.
- Report enrichment separately for strings of three or more signs, and conditional on the partner's class.
- Fit a joint ordering model (for example Plackett–Luce) as the stronger null.
- Rate pictorial support and positional support on separate axes in the table.

### 4. Medium-high: defects in the lexical control

**Where:** `analyze.py:155`, `run-v2/lexical-adversarial.json`

- **Sandhi.** Line 155 builds `residual+s` with no sound change at the join. As a result the JSON marks "samvāha" (`lexical-adversarial.json:649-651`) and "saaṃśa" (`:1302-1303`) as not attested. The pinned MW has saṃvāha (226133, "bearing or carrying along") and sāṃśa (240923, "having … shares"). The control fractions for prefix attestation are biased low in the same way (sam- becomes saṃ- before most consonants; ati- becomes aty- before vowels).
- **No baseline.** The support counts (ati 6/46, sam 7/22) are not compared with how well the other 40 residuals fit the same patterns. The normalized counts (14/46 and 9/22) are not shown in the report.
- **Identical lists.** W233 and W231 get the same 41 residuals because the two-sign window's residual set depends only on bhāra. That number measures how many compounds bhāra forms, not evidence about either sign pair.
- **Disputed imported values.** The imported values feeding these windows include crosswalks on which the two coders' candidate sets did not overlap (`graphic-sensitivity.json`):

  | Bonta sign | Value | Wells codes |
  |---|---|---|
  | B004 | PA | W205–W209 |
  | B017 | PAla | W064 |
  | B032 | vAsu | W530 |
  | B035, B036 | kara | W455, W532 |
  | B003 | nI | W924 |
  | B041 | RASHTRA | W845 |

The demotions still stand, but their reason should be restated as "no residual stands out", not "literal failure". Separately, the protocol (`PROTOCOL.json`, test 5) required rival lists and controls for the shortlisted extensions too. bhārin, varga, dvāra, kṛṣi and lāṅgala received neither.

**Remedy:**
- Apply sandhi when joining word parts, or test both the joined and unjoined forms.
- Rank the selected residual against every competing residual.
- Rerun after excluding windows that contain a disputed crosswalk.
- Extend the rival enumeration to the shortlisted anchors.

### 5. Medium: the visual catalogue cannot show the distinctions it argues

**Where:** `verification.json:105-111`, `catalogue-data.json:2030-2036`, `catalogue-template.html:24`

- **Carrier variants.** `W154.png` and `W156.png` have the identical SHA-256 hash (`30b648…`). W158 maps to the same P004/V145 chart cell (`catalogue-data.json:2030-2036`). The W158 card describes "crossed/rotated" font features that only exist in the local font. In that font sheet, W156 adds interior body strokes to W154, and W158 has raised arms with hanging ovals and no visible yoke bar. A public reader sees one drawing for all three.
- **W617 schematic.** The authored drawing (`catalogue-template.html:24`) has 2×4 cells per grid. The local font has about 3×5, and M-81A shows multi-row grids.
- **W527.** The font glyph is a box of horizontal bars attached to a stem, which visually resembles the W400 comb with an added stroke. "W527 as a W400-derived closing variant" is a missing rival.

**Remedy:**
- Add authored schematics of the distinguishing strokes for W154, W156 and W158.
- Label the W617 drawing "not to cell count".
- Add the W400-variant rival to the W527 card.

### 6. Medium: W617's segmentation outweighs its positional result

W617 has no 1979 chart class (`catalogue-data.json:1654-1656`), and Mayig encodes it as two P268 tokens. Only the Wells/Lipi coding treats it as one token.

In the M-81A impression I saw two grids separated by a clear gap. In the "a bis" view they may differ in width; this needs measuring, not my eyeball. W617's position profile also differs from the other closing signs:
- It is not under-represented at the start (8/43).
- Its final tendency is weak at Harappa (5/11 against 3.1 expected).

There is also a visual rival the report omits. Both M-16A and M-81A show the gridded upper part of the cult "standard" placed in front of the animal, which looks like the grid signs.

**Remedy:**
- Recompute W617's position statistics under the two-token encoding.
- Keep the paired-compartment meaning conditional on segmentation.
- Rank W617 below the pictorial leads until that is settled.

### 7. Medium: maximum-statistic design and protocol deviation

The maximum-statistic adjustment is single-step. It takes the maximum over all 596 codes, including very rare ones whose discrete counts produce extreme z values. W142's medial z of 3.46 sits near the median of the null maximum (p = 0.478), so that result mostly reflects the size of the test family.

W142 also avoids the final position: 1 of 39 overall, 0 of 28 at Mohenjo-daro, z = −3.58. That is its most distinctive positional fact, and the report omits it.

The protocol specified controlling "the family of 17 original anchor codes". The analysis instead used BH over 596 codes × 3 positions, and the report does not disclose the deviation.

**Remedy:**
- Declare a minimum-count family before the next run.
- Use a step-down maximum-statistic or minP procedure.
- Disclose the change from the protocol.

### 8. Medium: the family frame is less deduplicated, not stricter

**Where:** `REPORT.md:31-38`

W156 has 58 tokens in the family frame against 34 distinct strings. The difference comes mainly from moulded "W003 + W156" tablets, each counted as its own family. The report presents the family column as a sensitivity check without saying that it re-adds duplicates.

**Remedy:** say so in the table note, and add a frame that clusters strings by shared formula.

### 9. Medium: sense-ledger errors and missing direct anchors

**Where:** `hypotheses.py:120`, `:125`, `:143`

| Entry | Ledger says | MW record shows |
|---|---|---|
| kṛṣaka (55086) | "Epic and later" | Only a Cāṇakya citation |
| gopāla (67231) | "Later comparison" | VS. xxx and ŚBr. iv citations |
| adhikārin (4197.1) | "superintendent or one entitled to an office" | "superintendent, governor", with no citation |

W130's leading anchors (kṛṣaka "ploughman/farmer", lāṅgala "plough") select a plough. The M-16A image shows teeth hanging from a horizontal bar carried at the shoulder. The direct harrow word with Vedic citations is not in the ledger; see the additions below.

### 10. Low-medium: publication and reproducibility

- `verification.json` hashes only the run-v5 outputs. The run-v2 diagnostics and the local permutation file are not hashed there.
- `analyze.py:198` hardcodes `C:/Windows/Fonts/arial.ttf`, so it fails on other platforms.
- The permutations and the lexical-control draws share one random-number stream, so changing one changes the other.
- `sources.json` has no Lipi entry with a rights status, although the 19 public examples derive from Lipi. `THIRD_PARTY_NOTICES.md` does cover them.
- The 19 examples are 18 objects (H-72 is used twice).
- Both W142 examples are [W142, W617] two-sign texts in which W142 is first. They illustrate the opposite of the "medial" claim.
- The prose tiers in `REPORT.md:3` order the families differently from the table.

Historic bytes appear preserved: verification reports 90 earlier files unchanged. I did not re-hash them.

## Corrected candidate ranking

Each row is rated separately for picture, position and a context that is specific to the proposed meaning. No historical probabilities are implied.

| Rank | Family | Codes | Change | Basis |
|---|---|---|---|---|
| 1 | Plain load-carrier, closing category | W151 | Kept | Clear yoke picture; z 9.6. Mainly substitutes for the jar; never follows W002–W005 (0/57, hand tally) |
| 2 | Closing class or collective after items and agents | W400 | Raised | z 19.7. Follows the jar 73 times and the carriers often. Comb and harrow picture anchors added |
| 3 | Jar-head carrier complex: counted container-load *or* container-bearer, both co-leading | W154, W156, W158 | W158 rejoins; the measure reading is promoted | Numeral contexts in 5/32 and 8/34 strings; shared W806 formula; slot before W400 |
| 4 | Marked carrier, possible allograph of W151 | W161 | Lowered | 10 tokens; shares only two two-sign templates with W151 |
| 5 | Bounded closing class, with a W400-variant rival | W527 | Lowered | z 10.2 but no template audit of its own; the picture also resembles a comb |
| 6 | Staff-bearer in a non-final agent or name slot | W142 | Raised | Clear picture; final avoidance 1/39 |
| 7 | Paired grids, conditional on segmentation | W617 | Lowered | Two-token encodings elsewhere; possible resemblance to the "standard" |
| 8 | Toothed-implement (harrow or rake) bearer | W130 | Re-anchored | 8 strings; W035 strokes precede it in 3 of them, all ending with W171 |

## Targeted Sanskrit additions

All sounds remain conditional. Each prediction below has to be scored against context patterns fixed in advance.

1. **vivadha / vīvadha** (MW 199980, p. 987,1). Senses: shoulder-yoke for carrying burdens (TĀr., ĀśvGṛ.); store of grain or provisions (Kāv., Pañcat.); pitcher (W.); royal income (L.).
   - Only the yoke sense is early.
   - *Prediction:* a "provisions/consignment" reading for W151 predicts that it follows numerals and commodity signs. A "carrier/agent" reading predicts it follows person signs and names. W151's 0/57 numeral rate currently favours the agent reading.

2. **bhāra as a unit of weight** (149885, "= 20 Tulās", Hariv., Suśr.) and **kumbha as a grain measure** (52482, "= 20 Droṇas", Mn. viii.320), for W154 and W156.
   - *Prediction:* the measure reading predicts that numerals directly precede these signs much more often than W151 and person signs, and that their slot alternates with other counted signs. The numeral templates also contain W390, W405 and W407, which fits this.

3. **matya** (155069, p. 776,2, "a harrow, roller", TS., Br.) for W130, alongside lāṅgala.
   - *Prediction:* a harrow implement should be a toothed bar like the one in M-16A, with no share or handle. W130 should keep co-occurring with W400 and with counted contexts.

4. **kaṅkata** (41666, "a comb", AV.) as the pictorial anchor for W400, beside the functional words gaṇa and varga.
   - *Prediction:* if W400 names an object, it should behave like other object signs in compounds. If it is a collective marker ("group of carriers"), the signs before it should be enriched for person and carrier signs compared with the signs before the jar.

## Minimum changes for the next iteration

1. **Carrier grouping.** Rerun the W154/W158 contrast using closing blocks and formula clustering. Regroup W154, W156 and W158 as one complex with context-defined subtypes.
2. **Substitution audit.** Add W527, W617 and W158. Publish template-length and substitute-class aggregates. State that the jar is W151's main substitute.
3. **Numeral test.** Declare a numeral set in advance, then compare how often numerals directly precede W151, W154, W156, W158, W130 and person signs, clustered by formula.
4. **Lexical control.** Apply sandhi when joining word parts, rank each selected residual against its rivals, exclude disputed-crosswalk windows, and run rival enumeration for the shortlisted anchors.
5. **Position reporting.** Report z-scores, results for strings of three or more signs, and W142's final avoidance. Disclose the change from the protocol's multiplicity family.
6. **Catalogue.** Add distinguishing schematics for W154, W156 and W158. Label the W617 cell counts. Add the W527 rival. Use an example where W142 is genuinely medial.
7. **Sense ledger.** Correct kṛṣaka, gopāla and adhikārin, and add the four anchors above.
8. **Records.** Hash the run-v2 outputs in `verification.json`, remove the Windows font path, and add a Lipi rights entry to `sources.json`.
