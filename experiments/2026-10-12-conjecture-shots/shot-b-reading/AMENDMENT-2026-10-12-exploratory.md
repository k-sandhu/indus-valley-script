# Amendment, 12 October 2026: exploratory reading of the frozen outcome

Everything in this file was done after the confirmation outcome was known and is exploratory. The frozen result in [REPORT.md](REPORT.md) is unchanged. The summaries come from [explore_post_outcome.py](explore_post_outcome.py), which reads only the frozen output `confirmation/results.json` and the map; it does not read the confirmation half again. Output: [exploratory_class_summary.json](confirmation/exploratory_class_summary.json).

## Where the locality prediction went wrong

P1 predicted that name and commodity signs would be more concentrated by site than the shared vocabulary. On confirmation seals the class means of the bias-corrected site concentration run the other way: determinatives 0.102 (3 signs), titles 0.044 (13), numerals 0.038 (11), commodities 0.007 (31), names 0.000 (21), affiliations −0.004 (5) and links −0.033 (5). The most concentrated signs are the numeral 013 (three written as two over one, 0.474), the two-men sign 091 (0.374), the determinative 621 (0.248), the sheaf 405 (0.243) and the bracket 923 (0.228). The name stock, fish signs included, is the most evenly spread vocabulary, and the regional differences sit in closing terms and in the way a numeral is written. A local scribal convention would explain 013, and local offices would explain the titles and determinatives; the fish names look shared across cities.

## The openers

The affiliation signs are not concentrated by site (817 0.068, 861 −0.016, 820 0.003, 920 −0.028, 692 −0.048), which fits shared households better than the city-name rival. Their mean size residual, +0.109 log₂ units, is the highest of any class, but it comes from 692 alone (+0.503); the other four lie between −0.012 and +0.027. Official legends are therefore not larger in general.

## Near misses and reversals

P4 (z = 1.38, p = 0.082) went in the predicted direction: the Harappa-tablet signs 700, 405, 690 and 630 lean towards Harappa on seals (Harappa excess +0.14 to +0.40), with 176 neutral and 171 leaning away; among the copper-tablet signs 923 leans towards Mohenjo-daro (−0.247) while 845 and 585 lean towards Harappa. S1 also went in the predicted direction and missed at p = 0.051. S2 reversed: the five seal components ending 740-400 have a mean size residual of −1.13 log₂ units, less than half the area expected for their length and shape, against −0.02 for the 21 ending 740-090.

## The period field

The `period` values on confirmation seals mix two numbering systems: 2, 3, 4 and 5 on one side and Early, Intermediate and Late on the other. Each system probably belongs to one excavation, so the period concentration of P5 partly measures site. P5 should be redefined within one site's sequence before it is used again.
