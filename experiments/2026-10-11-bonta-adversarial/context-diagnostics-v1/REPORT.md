# Context and encoding audit after the external review

This post-outcome audit reuses 1,859 distinct complete reading-order strings from 2,930 faces. It calculates conditional analytic moments and context aggregates; it generates no new permutations. The frozen [protocol](PROTOCOL.json) keeps the two stroke definitions, closing-block rule and formula clusters together. A formula cluster is a descriptive grouping, not a proven independent archaeological observation.

The context counts are:

| Code | Last token | Closing block | Immediately after W001–W005 | Immediately after W002–W005 | After W806 | W465–W475/W806 formula |
|---|---:|---:|---:|---:|---:|---:|
| W151 | 49/57 | 53/57 | 0/57 | 0/57 | 0/57 | 0/57 |
| W154 | 25/32 | 31/32 | 5/32 | 5/32 | 13/32 | 13/32 |
| W156 | 26/34 | 30/34 | 9/34 | 9/34 | 0/34 | 0/34 |
| W158 | 7/19 | 18/19 | 2/19 | 2/19 | 8/19 | 8/19 |
| W161 | 10/10 | 10/10 | 0/10 | 0/10 | 0/10 | 0/10 |
| W130 | 2/8 | 3/8 | 0/8 | 0/8 | 0/8 | 0/8 |

W154/W158's terminal-only descriptive Fisher value is 0.006246759; using the declared closing block changes it to 1.000000000. The difference in attached terminal signs should therefore accompany the earlier terminal-only contrast. W154 and W158 share a W806 formula; W156 has a different profile. Both stroke definitions remain displayed, including any W001 cases.

| Code | Final tokens, length 2 | Final tokens, length ≥3 | Expected final, length ≥3 | Analytic final z, length ≥3 |
|---|---:|---:|---:|---:|
| W151 | 13/14 | 36/43 | 10.452 | 9.220 |
| W154 | 5/5 | 20/27 | 6.152 | 6.448 |
| W156 | 12/12 | 14/22 | 5.536 | 4.205 |
| W158 | 1/1 | 6/18 | 5.143 | 0.450 |
| W161 | 3/3 | 7/7 | 1.486 | 5.162 |
| W400 | 14/14 | 156/178 | 45.373 | 19.306 |
| W527 | 6/6 | 32/37 | 7.641 | 10.055 |
| W617 | 5/5 | 21/38 | 8.430 | 4.983 |
| W130 | 0/1 | 2/7 | 1.869 | 0.114 |
| W142 | 1/7 | 0/32 | 7.216 | -3.088 |

These z scores separate two-sign records from longer strings under the same length/multiset reference. They do not supply a partner-controlled ordering model. No new Monte Carlo p values accompany them.

The six carrier/tool categories occupy 121 distinct preceding-pair clusters. Each cluster's support and closing rate are in [formula-clusters.json](formula-clusters.json), with opaque identities and public class flags. Repeated strings were removed before clustering; shared formulas, moulds and production traditions can still make the category counts dependent.

| Code | Exact substitution templates | Length distribution |
|---|---:|---|
| W151 | 16 | 2: 10, 3: 4, 4: 2 |
| W154 | 8 | 2: 3, 3: 4, 4: 1 |
| W156 | 12 | 2: 8, 3: 4 |
| W158 | 3 | 3: 2, 4: 1 |
| W161 | 4 | 2: 3, 5: 1 |
| W400 | 10 | 2: 5, 3: 2, 4: 2, 5: 1 |
| W527 | 6 | 2: 4, 3: 1, 5: 1 |
| W617 | 4 | 2: 3, 3: 1 |
| W130 | 0 | none |
| W142 | 8 | 2: 5, 3: 2, 5: 1 |

The jar W740 substitutes for W151 in 8 of its 16 exact templates. [Substitution aggregates](substitution-aggregates.json) give every alternative and pairwise length distribution, including W527 and W617. Residual templates are retained only in the local source input.

The W130 orientation check finds 3 strings with W035 immediately before W130. Of these, 0 end in W171 and 3 begin with W171. Source IDs and the orientation metadata are in [orientation-and-examples.json](orientation-and-examples.json). The reading-order field is used as supplied; no extra reversal is applied.

W142 is final in 1/39 tokens, with expectation 10.716 and analytic z -3.618. Genuinely medial candidate records are 2162.1 (M-2063), 3365.1 (M-972), 3620.1 (M-1315). This output supplies their IDs/CISI only, for later bounded example selection.

Splitting W617 into G617a followed by G617b leaves 1859 distinct recoded strings. The ordered pair is terminal 26 times and belongs to the declared closing block 28 times. [Encoding sensitivity](W617-recoding.json) reports each abstract token's analytic positions. G617a cannot be last and G617b cannot be first by construction. A tokenwise reference breaks their adjacency; an inseparable-pair reference restores the original block. The grid construction therefore changes the apparent position evidence without adding source observations.

The pooled counts and expectations match frozen run-v2, exact substitution counts are symmetric, and the retained terminal Fisher table reproduces. [Verification and hashes](manifest.json) identify every input, calculation file and output.
