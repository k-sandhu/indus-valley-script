# Lexical source review

We reviewed all 24 forms used by the existing Tamil rebus input table against their original dictionary entries and the held proposal pages. The review resolves two language-attribution errors, selects 38 dictionary senses or contextual entries, and documents four limited relationships between written forms and dictionary lemmas. The frozen forty-entry Winslow audit also finds a wrong accepted boundary and two rejected compounds with directly documented boundaries. The local review records contain every decision, including unresolved cases.

The two language corrections change which forms belong in the Tamil candidate list. In *Dravidian and the Indus script: On the interpretation of some pivotal signs* (1997), printed p.171, PDF p.5, Parpola lists āvu under Kannada and Telugu; his Tamil and Malayalam forms are ā and āṉ. In *'Hind leg' + 'fish': towards further understanding of the Indus script* (2009), printed p.63, PDF p.27, he attributes the animal hind-thigh form tōḷ to Toda and the leg or foot form tāḷ to Tamil. We checked both original PDF pages visually. The earlier extraction had admitted āvu and tōḷ as Tamil alternatives for those cited senses. These alternatives should be removed from that Tamil list while their actual languages remain recorded.

## Dictionary senses and written forms

The 24 forms have 56 exact Tamil Lexicon records. We inspected their original DSAL HTML blocks, preserving each page hash and character span. A selection names its stable entry identifier, homograph, role and relevant sense. The detailed records keep every exact alternative, so later reviewers can challenge a selection without reconstructing the lookup. The 15 homograph sets identified in the earlier input audit require sense selection when the outcome depends on meaning or origin; counts of an exact written form may aggregate homographs.

Several first-row matches had the wrong sense. The carrying-pole kā is homograph 4 on p.840, and its protection comparison uses homograph 3. Cattle ā is homograph 8 on p.201. The exact eḻu entry on p.540 concerns a pillar; iru on p.326 means great or black; nominal kāvu on p.903 concerns sacrifice or ointment. Their desired interpretations require the separate evidence below.

| Input | Direct dictionary evidence | Accepted scope |
|---|---|---|
| aṟu | aṟu-mīṉ, p.181, explicitly cites numeral āṟu³, p.259 | Numeral combining form in this compound |
| eḻu | eḻu-mīṉ, p.544, explicitly cites ēḻu, p.568 | Numeral combining form in this compound |
| iru | iru-kaṇ, p.326, explicitly cites iraṇṭu | Numeral combining form in this compound |
| kāvu | kāvu-¹, p.903, describes carrying with a shoulder pole | Verb citation form |

These relations have source evidence and a defined context. None changes the exact-token counter or permits universal spelling substitution. The earlier aṟu-to-aṟṟu fallback remains excluded: aṟṟu has comparison and grammatical-increment senses. Likewise, muruku and botanical murukku retain their different consonants, and veḷ, vēḷ and veḷi retain their different vowels.

We also distinguish what a proposed picture names. In *Study of the Indus script* (2005), printed p.57, PDF p.30, the crab supports a grasping action, koḷ, and the proposed comparison is kōḷ taking or planet. Kōḷ is not selected as a noun meaning crab. The piḷḷai entries support child and young-animal uses, and aṇiṟ-piḷḷai explicitly means squirrel; the standalone Tamil squirrel sense asserted in *A Dravidian solution to the Indus script problem* (2010), printed p.26, PDF p.25, remains unverified in the inspected dictionary entries.

The records preserve printed historical citations without assigning earliest dates. Parpola 1997 p.175 discusses kāvaṭi, reports its absence from Old Tamil literature and cites a 1628 chronicle for the cult. We have recorded his claims and their location. Checking the cited chronicle, old texts and their dates is separate work. The celestial sense of tāḷ also remains a textual question: the Tamil Lexicon labels it comet, while Parpola 2009 p.63 discusses a constellation interpretation of the old poem.

## The frozen compound sample

[FREEZE.json](FREEZE.json) pins the protocol, selector, complete input table and selected row identifiers before original sample entries were read. SHA256 ranking selected forty rows across six strata: 6 accepted with an origin flag, 6 other accepted etymology splits, 8 other accepted splits, 6 rejected subentries screened for possible increments, 8 rejected principal entries without etymology, and 6 other rejected subentries. Three previously known failures were excluded into a separate regression set. The original protocol calls some unflagged strata nonloan; source inspection shows that this means only **no row flag**. Five reviewed subentries occur under marked parents whose marks were absent from the derived rows.

| Existing parser result | Source-review disposition | Count |
|---|---|---:|
| Accepted split | Supported member boundary | 17 |
| Accepted split | Wrong member boundary | 1 |
| Accepted split | Unresolved sense or member identity | 2 |
| Rejected entry | Directly supported missed compound | 2 |
| Rejected entry | Unresolved | 9 |
| Rejected entry | Outside two-noun or two-member scope | 9 |

The wrong accepted split is aintaru, Winslow p.195. The parser returns aint plus aru; the Tamil Lexicon p.577 gives ai-n-taru for five celestial trees. The two directly supported omissions are tāyccittampalam, a children's game, and maṉamalarcci, cheerfulness. Their Tamil Lexicon entries mark the boundaries. The latter cites Winslow, so the later dictionary is a boundary cross-check rather than an independent historical attestation. The rejected set also includes infinitive phrases, grammatical material and a three-member plant name. Nine entries lack enough evidence to adjudicate their eligibility or morphology.

Agreement with source-supported boundaries is 17/18 among adjudicable accepted rows. Across all twenty selected accepted rows, treating the two unresolved cases as failures or successes gives bounds of 85–95%. This measures boundaries, allowing source-documented junction variants. It does not measure whether both members are eligible native picture nouns. Unequal stratum sampling and the missing population of true compounds prevent dictionary-wide precision or recall claims.

The regression cases retain their source meanings. Murukkampū is a coral-tree flower, and murukkañcettal is dry murukku wood. Both need a general increment rule to enter the extracted compound table. Jamīṉ means land; its parsed ja plus mīṉ split comes from treating the parent ja letter as a lexical root.

## Repair and next work

The new source wrapper recognizes grammatical headers beginning “is a letter of … alphabet” and prevents a split from that root. It suppresses the false jamīṉ split in the reviewed set. It also carries parent origin marks in separate fields, preserving the distinction between a borrowed parent and the history of an entire compound. This is a post-outcome general guard with source-attested tests. It does not add increment rules, repair aintaru, or re-extract the complete dictionary.

Thirteen focused tests check source identity, hashes, ambiguity rejection, scope-limited relations, the guard and deterministic replay of the forty-row selection. The shared shots synthetic test passes. [verification-v2.json](verification-v2.json) records the author checks; [results-v1.json](results-v1.json) records the counts. Detailed reviews remain local under `data/raw/2026-10-22-lexical-source-review/run-v1/`. No rebus effect was recomputed and no real confirmation cohort was opened. The source decisions are provisional AI review without specialist Tamil credentials.

The strongest supported statement is that specific language labels, senses and compound boundaries in the existing evaluation inputs can now be corrected from cited sources. The deciding next evidence is a Dravidianist's review of the unresolved morphology and historical senses, followed by a complete versioned extraction with declared noun eligibility and an independently reviewed compound sample. That would permit a calibrated comparison using the corrected lexical pools.
