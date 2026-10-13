# A working reading of the Indus inscriptions (Shot B, draft)

Written 12 October 2026 from the discovery half of the conjecture-shot split, before any withheld variable was loaded. The reading is the project's conjecture [C-0002](../../../knowledge/conjectures/C-0002-working-reading.md). Its frozen test on the confirmation half failed (primary score at the 33.0th percentile of its rearrangements, 0.44 standard deviations below their mean), and the conjecture is recorded dead; the outcome is summarised in [README.md](README.md). The reading below is kept as it was frozen. Its tests are in [PREDICTIONS.md](PREDICTIONS.md); the sign-by-sign map, with evidence and rival glosses, is [GLOSS-MAP.json](GLOSS-MAP.json); how it was built is in [EXPLORATION.md](EXPLORATION.md). Counts below are from distinct intact single-line texts of the discovery half unless stated otherwise ([grammar_summary.json](discovery/grammar_summary.json), [sign_profile.tsv](discovery/sign_profile.tsv), [reading_counts.json](discovery/reading_counts.json)). Glossed readings of every discovery text are kept locally in `data/raw/2026-10-12-conjecture-shots/shot-b-reading/glossed_discovery.jsonl`.

## The reading in brief

A seal legend names a holder and the office he holds. It may open with the great household he belongs to, linked by a short-stroke particle meaning "of"; it then gives his personal name, usually built on a "star" element; and it closes with his office, written head-last as a commodity or department followed by an office noun, sometimes with a determinative saying whether the legend names the man or the office as a body. The commonest office noun, the jar sign 740, means steward or storekeeper. Harappa's moulded and incised tablets are tokens of standard measures, labour and offices; Mohenjo-daro's copper tablets record named holders and their allotments; pottery marks give counts of standard units or the store a vessel belongs to.

## Seven classes

| Class | Signs | Role | Commonest members and glosses |
|---|---:|---|---|
| NUM | 13 | numerals; short strokes count items, tall strokes count standard units | 003 three, 004 four, 017 seven, 033 three units, 032 two units |
| LINK | 5 | links an institution to its holder | 002 of, 060 of, 741 household of |
| AFF | 5 | great household named at the opening | 861 and 817 the temple estate, 820 the royal household, 920 the household of the bow, 692 the household of the crossed staves |
| NAME | 29 | elements of personal names | 220 Star, 240 Elder Star, 235 Lord Star, 233 Barred Star, 798 Leaf-pincer, 803 Leaf-trident |
| COMM | 46 | commodities, units and departments; qualify an office or are counted | 700 standard measure, 390 share of grain, 590 granary bin, 176 cloth, 100 labour gang, 760 seed grain |
| TITLE | 17 | office and role nouns | 740 steward, 520 guard, 527 warden of an enclosure, 151 porter, 154 and 156 store-porter, 142 overseer, 140 lady |
| DET | 3 | closing determinatives | 090 the man, 400 the body, 621 the office |

The classes come from where a sign stands, what stands beside it and what it pictures. Signs that substitute for one another in identical frames were kept in one class: 817, 861 and 820 share 37 to 44 frames pairwise; 920 and 692 share 17; the comb 400 and the man 090 share 32 frames, almost all of them the slot after 740; the sheaf signs 390, 405 and 407 share 12 to 18 ([frames_summary.json](discovery/frames_summary.json)). Pictures then chose between readings with the same distribution: a jar for storage, a yoke-carrier, a lance, a staff-bearer, a rake, a sprouting vessel.

## Seal legends

The grammar is

```text
LEGEND  = [OPENER] NAME [CLOSING]
OPENER  = AFF LINK+   or a title prefix (140 lady, 142 overseer, 097 retainer, 091 partners, 061 chief of)
CLOSING = [NUM] [COMM]* HEAD [DET]   with HEAD a TITLE or a counted sheaf (390, 405, 407)
```

and the English pattern is "Of [household]: [name], [department] [office] [the man | the body]".

**Openers.** Among 591 seal legends of three or more signs, 151 (25.5%) open with an affiliation followed by a link, and 34 of all 704 legends open with a title prefix. The pair 002 follows 817, 861 or 820 in 134 of its 235 tokens and follows a stroke numeral six times ([reading_counts.json](discovery/reading_counts.json)), so in this slot it is read as a particle meaning "of". Mahadevan's 1986 grammar already separated the raised short strokes from numerals, and Fairservis read a paired dash as the genitive. Sign 820 also takes 060, which otherwise follows 920 and 692, and 920-060 is usually followed by a jar with inner strokes (741, 742, 745), read "household of". Rare initial signs followed by 002 (148 legends place a link after something other than an affiliation, numeral or link) are read as rarer households outside the map. The shortest seal of this type is a bare opener, for example B-5, 817-002, "of the temple estate": the seal of the institution itself.

**Names.** The variable middle of a legend is the holder's name. Fish signs dominate it: 220, 240, 235, 233 and 231 substitute in shared frames and occur after the opener or at the start. Following Parpola's star reading of the fish, they are read as theophoric "star" elements, with the added marks distinguishing named stars (Elder Star, Lord Star, Barred Star); a numeral before a fish forms an asterism name, as in Parpola's six-star Pleiades and seven-star Great Bear. Leaf signs (798, 803, 806) are the second large name stock.

**Offices.** The closing unit is a head-last office phrase. The jar 740 ends 259 of 704 seal legends (36.8%) and is preceded by a small set of bound qualifiers: 760 stands before it in 34 of 37 texts, 100 in 38 of 44, 923 in 10 of 11, 176 in 24 of 37. Mahadevan (1982) observed that terminal signs are tied to their antecedents too closely to be case endings and read the jar as an ideogram for a priest. This reading keeps his observation and takes the picture literally: the jar is a store vessel, its bound antecedents name what is stored or the department, and 740 is the steward. Thus C-17, 100-740, is "steward of the labour gang", and 013-840-740 (M-1915) is "steward of three double bales". The other office heads close in the same way: 527 after the bale signs 550, 555 or 554 (M-939, 550-527, "warden of the bale enclosure"); 520 after 705-033 or 706-033 ("guard of the three filled bowls"); 617 after the staff-bearer 142 (H-72, 142-617, "overseer, keeper of the twin granaries"); the yoke-bearers 151, 154, 156 and 158, often counted (M-188, 031-156, "one store-porter").

**Shares.** A legend can close with a numeral and a sheaf sign instead of an office: H-585, 003-390, "three shares". Of 145 sheaf tokens in distinct texts of all object types, 51 follow a numeral directly and 33 follow the granary bin 590 (590-390-740, "granary-share steward", closes 12 seal legends, more than any other three-sign closing phrase). A seal reading "three shares" names the holder of a standing allotment by the size of the allotment.

**Determinatives.** After 740 comes the man 090 or the comb 400. On seals 23 legends end 740-090 and 5 end 740-400; on moulded tablets the counts are 4 and 22, on incised tablets 4 and 17. The man marks a legend that names an individual holder, the comb one that names the office as a body; individuals carry seals and institutions issue tablets.

## Tablets and other objects

**Harappa moulded and incised tablets.** Of 237 intact tablet faces carrying 700, 203 are a stroke numeral and 700, mostly two, three or four tall strokes: H-2125, 033-700, "three standard measures". These are ration or allotment tokens. Office tablets end in 740-400, as in H-1273, 176-740-400, "the cloth stewardship", and labour tokens count porters, as in H-2223, 003-156, "three store-porters". Few tablets open with an affiliation (17 of 134 moulded tablets of three or more signs, 2 of 49 incised).

**Copper tablets.** None of 40 distinct copper-tablet texts opens with an affiliation. They give a name and an allotment: a fish name, a filled bowl, a count of three standard units and the fodder signs 845 and 407. Sign 845 has 25 of its 28 discovery tokens on copper tablets and 407 has 57 of its 91, so they are read as Mohenjo-daro's own vocabulary for fodder allotments.

**Pottery.** Pottery marks are short: 71 of 88 distinct complete pottery texts have one or two signs ([segments_summary.json](discovery/segments_summary.json)). The commonest are single numerals (two tall strokes on 18 faces), 700 and the doorway 440. A count of standard units gives the capacity; 440 marks the storeroom the vessel belongs to.

**Sealings.** Sealings carry seal legends and follow the seal grammar; 4 of 18 sealings of three or more signs open with an affiliation.

## Prior proposals adopted and rejected

- Iravatham Mahadevan, *The Indus Script: Texts, Concordance and Tables* (Memoirs of the Archaeological Survey of India 77, 1977): positional classes and numeral combinations, adopted as the structural frame.
- Iravatham Mahadevan, "Terminal Ideograms in the Indus Script", in *Harappan Civilization*, ed. Gregory L. Possehl (Oxford & IBH, 1982), pp. 313–314: terminal signs are ideograms bound to their antecedents and suffixed to names; jar = priest, lance = warrior, bearer = officer or functionary. Adopted for the lance and the bearer and for the bound structure; the jar is read as steward rather than priest because its antecedents look like stored goods and departments (sprouting vessel, labour gang, bales, fruit), not ritual qualifiers. His earlier view of the terminal signs as grammatical suffixes (papers of 1970 to 1973, as he reports there) is kept as the rival gloss for 740.
- Iravatham Mahadevan, "Towards a Grammar of the Indus Texts: 'Intelligible to the Eye, if not to the Ears'" (*Tamil Civilization*, 1986): separates short-stroke markers from numerals and treats modified fish as interchangeable. Adopted for 002 as a particle and for the fish as one name stock.
- Asko Parpola, Seppo Koskenniemi, Simo Parpola and Pentti Aalto, *Decipherment of the Proto-Dravidian Inscriptions of the Indus Civilization: A First Announcement* (1969), and Asko Parpola, *Deciphering the Indus Script* (Cambridge University Press, 1994): the fish as "star". Adopted for the fish signs as theophoric name elements. Parpola's "Deciphering the Indus Script" essay on harappa.com, section "The Pleiades and the Seven Sages": numeral plus fish as asterism names, adopted for numeral-fish pairs inside names.
- Walter A. Fairservis Jr., *The Harappan Civilization and Its Writing: A Model for the Decipherment of the Indus Script* (Brill, 1992): seal texts identify the bearer "by name, title, occupation, social status, family"; a stroke mark as genitive. Adopted for the overall legend content and for the particle reading of 002; his Dravidian readings and his "chief" values are not used.
- Bryan Wells, "The Classification of Indus Texts", in *Airavati* (2008), pp. 275–288: the 700 plus stroke modules on Harappa tablets. Adopted for 700 as a counted measure.
- Rajesh P. N. Rao, "The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor", in *Walking with the Unicorn: Social Organization and Material Culture in Ancient South Asia*, ed. D. Frenez, G. M. Jamison, R. W. Law, M. Vidale and R. H. Meadow (Archaeopress, 2018): carrier signs as labour and tablets as ration tokens. Adopted for the tablet genres and the porter titles.
- Nisha Yadav, "Structure of Indus Script" (*Indian Journal of History of Science*, 2019), and the opener modules it summarises: 817, 861 or 820 with 002 as text-initial units. Adopted as the opener slot; the household reading is this project's.
- The project's October 8–11 catalogues ([run-v6 catalogue](../../2026-10-11-bonta-adversarial/run-v6/catalogue.html)), including Bonta's reading of 740 as "be, belong to": consulted for every sign and kept in each map entry's prior proposals. Their sound values and Sanskrit words are not used; their structural observations on closing blocks are.

## What the map does not cover

The map covers 118 signs and 7,748 of 8,941 known discovery tokens. Only 323 of 704 distinct seal legends consist entirely of mapped signs; the rest contain at least one rarer sign, glossed "?" in the local readings. Glosses of commodities and names are the most arbitrary part of the reading: within a class the predictions test only the class and its attributes, so "cloth" for 176 or "Lord Star" for 235 has no test of its own here.
