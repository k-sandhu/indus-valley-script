I read the listed files, the quantity-sensitivity outputs, the run-v2 rows for the codes cited below and all 20 entries in the local dossier. I looked at the seven glyphs plus W004 and W014. Nothing was executed; every count comes from saved JSON.

I take the protocol's framing as given and don't repeat it per finding: grades rank candidates rather than measure probability, the direction rule is a simple screen, and Sanskrit senses are comparison vocabulary. Long local records are cited by ID and slot. The only full code sequences I quote are records of three codes or fewer that are already public.

## High

**1. The "closing" rule credits signs that are almost never last.** `run-v2/integrate.py:25` counts an occurrence as closing if it is last, or if it sits directly before a final W400 or W740. For several supported results, that second clause provides nearly all the support:

| Result | Last in record | Closing matches | Matches via "before W740/W400" |
|---|---:|---:|---:|
| terminal_qualified_vessel family | 3/106 | 82 | ≥79 |
| toothed_border_box family | 0/50 | 15 | 15 |
| W752 (new, supported) | 0/17 | 14 | 14 |
| W585 (new, supported) | 1/27 | 18 | 17 |
| carrier_yoke, for contrast | 127/170 | 154 | 27 |

These come from `positions` and `role_scores` in `context/run-v2/summary.json`. These signs regularly sit just before the jar sign. The family name "terminal", the label "closing account category" and the table heading "Closing block" all misdescribe that. Their support also depends on W740 and W400 already being treated as closers, which came from earlier, already-seen analysis.

- **Fix:** split closing into "last" and "before W740/W400" counts in the tables. Describe these codes as qualifiers or stems of the following jar sign, keeping container-type, compound-ending and suffix rivals. The frozen grades can stay.

**2. Public examples show declared roles as if observed, misalign excerpts, and skip every failing family.** `integrate.py:218` copies each record's declared role list into the public example. `catalogue-template.html:27` prints it as "Whole-record role walk" with no pass/fail marks.
- **M-302 (W235 · W231 · W520):** the walk reads counted → counted → nonfinal, and all three roles fail.
- **Ad-1 and H-2143:** two of three declared roles fail in each.
- **M-280 excerpt (slots 2–4 of 7):** the 7-item role list sits under a 3-glyph window with no offset. W920, which is unresolved, appears aligned with "unconstrained". The list also reveals role classes for the four hidden slots.
- **Selection:** the example loop (`integrate.py:206–220`) sorts families by grade and stops at 36. All 24 mixed-context families therefore get no public example. The code comment says the selection includes "clipped counterexamples", but it doesn't select any.
- **Fix:** give each shown slot its own status (pass, exception, no rule, unresolved), aligned to the window. Give every family that has data at least one example, ideally one matching and one contrary record.

**3. Each family's meaning and Sanskrit words pass to every member.** Grades are per code, but `integrate.py:172–176` gives every member the family's meaning text and its full Sanskrit word list. The planned label narrowing won't remove those words.
- **arrow_shaft:** as a family it strongly prefers the last position (41/181 non-final against 139.9 expected). Yet W518 and W519 each pass as non-final and still carry "directional/authority shaft". Members that behave in opposite ways share one meaning.
- **human_agent:** the family also leans toward the last position (137/214 non-final against 168.1). W095, W097 and W104 pass individually as non-final "named agent".
- **W585 image:** a peaked A-frame with an upward arrow inside, two short uprights on top and feet turned outward. There is no lintel, so the doorway reading (Sanskrit *dvāra*) has nothing pictured to attach to. The sign fits the angular_support or arch_canopy descriptions better than "doorway". Its closing support comes from the before-W740 clause (finding 1).
- **W803 image:** a pointed leaf-shaped outline around a three-pronged stem. That is leaf_cluster's own description, yet leaf isn't among enclosed_emblem's rivals. The family boundary, not the evidence, decides whether a leaf-like sign gets counted support.
- **W240 image:** no closed body. It shows two Y-forked uprights over a narrow crossed stem; only the crossed tail resembles a fish.
- **Sanskrit word lists:** *kumbha* in its "corn/grain measure" sense (Manu 8.320) attaches to all 38 rim and terminal vessel codes. *Dhānya* and *sasya* (grain, crop) attach to every plant_branch member.

**Fix:**
- Give W240, W585 and W803 per-code meanings.
- Flag members whose positional direction opposes their family's.
- Show only the Sanskrit senses that name the pictured part on member cards, and move function or measure senses to a separate layer.

Some members pass while their family fails: W095/097/104, W317, W495, W503, W518/519, W585 and W803/806/838. About 141 members were screened individually, and a direction-only rule across two splits will pass some by chance. The protocol already allows a random-label control (PROTOCOL.md:21), but it hasn't been run. Until it is, show these as "member passes; family does not".

## Medium

**4. One linked cluster dominates the transfer split.** The largest cluster (237 strings, 802 codes) falls in transfer. That is 33% of transfer strings and 26% of its codes (REPORT-v1.md:5). Results that pass transfer by less than one occurrence could be decided by that cluster alone:
- binding_bowtie: 29 against 28.935 expected
- angular_support: 1 against 0.4
- woven_mesh: 1 against 0.458

The report describes the split accurately but doesn't state this consequence. **Fix:** report transfer results with that cluster removed.

**5. Exceptions aren't broken down, and repeated phrases survive deduplication.** The fish family's 742 exceptions mix three situations:
- A second fish in a run of fish: M-38 has four fish and only one passes.
- A fish after a long stroke: W032 directly before W220 in H-1657, M-38, H-20 and L-87.
- Fish that are first in the record or otherwise placed.

The three-sign sequence W255–W435–W690 recurs in K-10, M-38 and H-20, with a W436 variant in H-278. Removing identical strings still leaves it counted as several independent occurrences. **Fix:** tabulate exceptions by what comes before them, and add a sensitivity for shared sequences.

**6. The competing readings in the viewer aren't true alternatives.** This goes beyond the planned commodity/grammatical display. In `catalogue-template.html:25`, the `semantic()` function never relabels connector or quantity families. So every issuer/name reading still says "Binding, paired joining or relationship marker", although a name reading would most naturally absorb those middle signs. The issuer reading only adds "issuer/name emblem:" in front of the commodity gloss. The expanded-proxy sensitivity also shows binding_bowtie following quantity signs in both splits (direction-changes.json:2781). That is a post-hoc "counted item" rival to the connector reading, and it is currently invisible. **Fix:** relabel every family under each reading, and give connectors "name part" and "counted item" alternatives.

**7. Occupation, office and measure senses are presented as picture-based comparisons.** The earlier review (SE03) caught only W125, the mesh pair, W420 and W521. The same move recurs:
- "transport service" (carrier_yoke)
- "cultivation service" (toothed_tool_bearer, via *kṛṣaka* "cultivator", cited only from Cāṇakya)
- "named office" (staff_bearer, via *adhikārin* "superintendent", whose record supplies no textual date)
- "two-person service group", "paired carrier service", "hide worker" and "aquatic-product handler"
- *kumbha* as a grain measure

**Fix:** keep the senses that name the pictured object on cards: *vivadha*, *śikya*, *matya*, *daṇḍin* ("carrying a staff") and *kumbha* ("jar"). Move the occupation, office and measure senses into a labelled scenario layer.

**8. The quantity sensitivity is properly separate, but its flags invite role-switching.** It isn't wired into run-v2, and no primary grade changed. However, `direction-changes.json` applies the counted-sign test to every family and code, whatever role was declared:
- binding_bowtie (declared connector) and gateway_compound (declared closing) both show `proxy_directional_criterion_met: true` (lines 2781 and 2806).
- So do W125, W520, W550, W555 and W585.
- In the other direction, W503, a new supported code, and W416 lose support under the broader quantity set.

**Fix:** limit that flag to families declared as counted. Mark W503's card as dependent on the narrow W001–W005 set.

**9. Shared chart images carry single-code captions.** One public chart cell is reused for several codes:
- W004/W014: four strokes in a row versus two over two in the font. Also W005/W015, W006/W016 and W007/W017.
- W025–W029.
- W153–W156 and W158, although W154, W156 and W158 had different earlier proposals.
- W240/W242.

The visible caption (`catalogue-template.html:21`) shows only the code; the shared status is only in the alt text. **Fix:** caption each image with its chart class and the codes sharing it.

## Low

- **Companion path:** the local viewer loads a fixed `companion.json` path that every build overwrites (`integrate.py:249`) and doesn't check the run. The frozen run-v1 viewer would therefore show run-v2 records.
- **Search index:** `search_text` (`integrate.py:201`) indexes old meanings for unresolved slots, including sound values: W435/W436 "hu", W924 "nī/ne/ni" and W920 "king". The record view shows those same slots as unresolved.
- **Dossier sampling:** 14 of the 20 local dossier entries come from strings of 10 or more signs, which are 1.8% of all strings. The 10–13-sign seals and the 11-sign H-278 tablet should be checked against CISI photographs for line and segment structure; I couldn't verify that.
- **Header stat:** "Codes with supported role: 31" counts only newly reviewed codes; 62 codes hold that grade overall.

The report arithmetic checks out (104+226+68+79+62 = 539). The 11 suppressed images, the separate 1,859 string / 2,930 face counts, and the three-code public limit are implemented as described.

## Competing readings of four complete public records

None of these has an unresolved slot.
- **Sh-69, Shortughai seal (W003 · W426).**
  - **Preferred:** three bundles of stalks.
  - **Account:** a three-bundle consignment.
  - **Name:** a name starting with a numeral ("Three-Stalk").
  - **Grammatical:** numeral plus classifier used as a title.
  - On a seal, a fixed quantity reads more naturally as an emblem or standing allotment than as a transaction. Nothing in the record decides between the four.
- **H-1855, Harappa tablet (W118 · W153 · W400).**
  - **Preferred:** handler, load-carrier, then a closing comb/class sign.
  - **Name:** a two-part name plus W400 as a title.
  - **Grammatical:** two nouns plus a suffix.
  - W153 only counts as closing because it sits before W400, so the reading assumes W400 is a closer.
- **Ad-1, Allahdino seal (W590 · W390 · W740).**
  - **Preferred:** a measured crop consignment.
  - **Name:** a two-sign name plus the common W740 ending.
  - **Grammatical:** stem, stem, suffix.
  - W590 and W390 both fail the counted rule. Nothing in the name or grammatical readings requires them to keep that rule, so this record actually counts against the account reading.
- **H-2143, Harappa tablet (W792 · W740 · W090).**
  - W740 is in the middle and W090 is last, which breaks both declared roles.
  - A grammatical or segment-break reading has no exceptions: W740 would be a linker or case marker before a person or title.
  - The same pattern recurs locally: W740 at slot 9 of 12 in M-391 and slot 8 of 10 in H-8, and two rim-vessel signs at slots 3 and 7 in H-76.

## Strongest supportable new comparisons

- **Closed-body fish signs (W220, W235, W255) as counted items after short strokes.** They occur about 2.5 times the expected rate in both splits, and *matsya* names the pictured object. W240's membership should be qualified.
- **W155,** a new carrier member: the carrier family is genuinely last-position (127/170). *Vivadha* and *śikya* name what is pictured.
- **W525 and W526,** panel on a staff: their family is genuinely last-position (46/59).
- **W426,** stalks joined at a base, compared with *stamba* and *kāṇḍa*: 4 of 5 occurrences follow strokes. The sample is small but clean.
- **A "before the jar" slot (W752, W760, W772, W773, W585).** This is a reliable structural pattern, not a meaning.

The main gap between these comparisons and meanings is that every position test fits an account, a name or title, or a grammatical reading of the same order equally well. On top of that, the step from picture to Sanskrit relies on an 1899 dictionary that dates later literary use. Only records that tell these genres apart could close it, such as sealings or tags with independent transactional context.
