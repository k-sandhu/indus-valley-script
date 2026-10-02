# South Indian stroke groups and specimen connections

The Tamil Nadu graffiti project supplies a usable comparative collection for repeated strokes and compound marks. We acquired both volumes of K. Rajan and R. Sivanantham's 2026 *Inscribed Potsherds of Tamil Nadu: Graffiti and Tamiḻi*, then pinned the public [TNSDA/RMRL web catalogue](https://tngraffiti.in/). The new calculation finds 480 reported occurrences of plain stroke forms and 194 compound forms with explicit plain-stroke components in this snapshot. These records give us named specimens and finite populations for further observation.

The immediate numerical question is which marks express a count, unit, personal identifier or another distinction. The acquired fields supply graphic classes and archaeological context summaries. A value test needs a quantity or readable numerical expression attached to the same identified object. A historical connection to Indus usage additionally needs dated intermediate or contact evidence. These requirements define the scope of the following results.

## What the sources let us connect

The [2026 volume I](https://tamildigitallibrary.in/Articles/062969_Inscribed_Potsherds_of_Tamil_Nadu_Vol_1) describes stroke variants on printed pp.387–388 and photographs their representatives in Plate 5.136, printed p.684. The classes include vertical and horizontal groups, counts one through nine, and a sixteen-line form. Its Figures 3.5–3.8 place graffiti beside Tamiḻi writing on pottery, a cave inscription and the Anaikottai seal. The [2026 volume II](https://tamildigitallibrary.in/Marc-Articles/062968_Inscribed_Potsherds_of_Tamil_Nadu_Vol_2) links normalized compounds to specimen registrations in its concordance and separately records Tamiḻi potsherd readings, excavation year, trench, depth and ware. These are acquisition routes for joint specimen studies.

The portal's base-sign route maps 42 government identifiers to its internal RMRL numbers. Its family routes provide separate distributions over site, habitation/burial context, ware and depth. The filter route can restrict those distributions to a site and sign. Its Indus-comparison route contains the authors' proposed shape parallels and example catalogue references. The concordance supplies component arrays for compounds, creating another connection between a stroke form and surrounding graphics.

We preserved these namespaces separately. Government identifier `39.1` describes one horizontal line; `39.10` describes six. String handling preserves the distinction. RMRL component number 87 refers to the government's base sign 39. Querying the concordance with government sign 39 works; an exploratory query with internal number 87 returned a server error. The working retrieval code is [acquire_portal.py](acquire_portal.py), with its [48-read manifest](portal-v1/acquisition.json).

The family responses contain aggregate margins. A site's frequency and a depth's frequency can come from different specimens, so the arrays cannot provide a joint specimen row. The inspected responses have no vessel capacity, measured mass, contents count, radiocarbon sample key or calendar date. The printed books and original excavation registers are the next route for those joins. A test filter for Keeladi's three-vertical-line class returned five occurrences and their ware/depth margins; the preserved [response record](additional-api-acquisition.json) identifies the exact request.

## New measurements on the pinned snapshot

[The aggregate endpoint](aggregate-v1/results.json) covers 42 base forms, 546 variants and 1,522 composites. Summing site margins gives 3,095 base occurrences, 3,366 variant occurrences and 2,884 composite occurrences, or 9,345 in total. Every form's habitation, ware and depth margins sums to its site count. The separate sites route reports 9,349 occurrences across 53 site labels.

The four differing cells have literal keys ` 14.13C`, `2.54C `, `20.` and `9.29C  `. Three contain surrounding spaces, and one has an incomplete dot suffix. The snapshots preserve these spellings. A future normalizer can trace corrections to a source row rather than silently assign a shape. The portal's family `totals` fields use base occurrences alongside numbers of variant/composite forms, so their combined sum has mixed units. Our endpoint counts forms and occurrences separately.

Sixteen plain stroke classes account for 480 reported occurrences. Three additional decorated variants bring the base-and-variant family to 501. The following distribution follows the printed graphic descriptions and the portal's occurrence margins:

| Visible line count | Reported occurrences |
|---:|---:|
| 1 | 105 |
| 2 | 195 |
| 3 | 99 |
| 4 | 49 |
| 5 | 17 |
| 6 | 6 |
| 7 | 1 |
| 8 | 4 |
| 9 | 3 |
| 16 | 1 |

These are counts of the authors' recognized forms. Broken marks and geometric decoration need specimen-level inspection. The photographs identify, for example, three lines on ARM-G-0004, eight on PMR-G-0039 and the sixteen-line class on KLD-ASI-G-0476. Those selected photographs have not yet been joined to individual occurrence rows in the aggregate API. The actual specimen image and its excavation registration should accompany any subsequent numerical proposal.

The [compound membership endpoint](stroke-membership-v2/results.json) contains 209 queried compound keys. Explicit plain-stroke components occur in 194 of them; 15 have opaque component representations for this question. Among the 194, 142 have one contiguous stroke block and exactly one other component. Those forms account for 413 of the 491 reported occurrences in the resolved group. Thirteen forms contain separated stroke blocks, and 40 contain more than one other component. Their arrangement gives concrete cases for comparing a simple count-plus-category form with more complex structures.

The first calculation required a complete name map for every surrounding component and retained 115 forms. The [membership refinement](STROKE-MEMBERSHIP-REFINEMENT.md) removes that unnecessary requirement: membership in the fixed sixteen plain-stroke codes suffices to count their explicit positions while leaving other graphics unnamed. Both endpoints are retained. This is a post-outcome exploratory analysis of the portal's normalized compounds.

Three concordance checks expose an important representation limit. Forms 1.6C and 39.13C agree between the digital arrays and printed tables. For 4.19C, specimen SGI(PPT)-G-0137, volume II printed p.779/PDF104 shows six components and two separated stroke blocks; the portal has five components and one block. The independent source review also found that the final printed base component 5.0 maps to variant 5.7 in the digital array. The digital endpoint remains unchanged. Source photography and the printed concordance must resolve such cases before a semantic test uses their component order.

## Which connection to pursue next

The most informative South Indian target is a specimen with both readable Tamiḻi and graffiti, secure excavation context and a measurable object feature. Start from the joint photographs in Figures 3.5–3.8, assign each view its actual registration, and join that registration to the Tamiḻi table and graffiti concordance. The plate montage alone leaves several individual joins open. A bounded study can then compare stroke groups across repeated readable names or independently documented vessel quantities, recording cutting order where grooves intersect.

The stroke representatives supply a second target set. Obtain calibrated views and the original context records for the large-count forms, particularly KLD-ASI-G-0476 and PMR-G-0039, together with complete vessels such as ARM-G-0004. Record whether the marks form isolated groups, overlap decoration, continue across a break or follow a vessel edge. Capacity requires a complete profile or a measured vessel; contents require an independently documented deposit.

A third route is to connect the printed concordance's component sequences to the photographic specimens for the 13 digitally split-block forms. Confirming separated tallies around another mark would constrain how a proposed quantity expression is segmented. The working finite population and the disagreement at 4.19C make that check more specific than another broad shape-similarity search.

These connections were investigated in earlier graffiti scholarship. Our contribution here is acquiring the current source witnesses, checking the deployed catalogue's connections and calculating an explicit stroke-context population. [The independent novelty review](../novelty/REPORT.md) places the collection beside earlier work. The [retrospective](RETROSPECTIVE.md) and [verification](verification.json) record retrieval problems, representation changes and checked totals.
