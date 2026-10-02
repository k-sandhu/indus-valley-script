# Capacity and numeral-value audit

The inspected evidence supports a published candidate relation for three selected Harappa vessels. It does not establish an independent 4.04-litre unit, a decimal numeral value, or a translation.

## Source and object audit

Fuls's author-posted article reports repeated museum dimensions, geometrically estimated capacities, and alternative commodity-specific explanations. Its indexed Tables1-3 were readable; the original PDF layout was unavailable. H372's incomplete dimension row therefore retains an alignment flag. Raw measurement replicates, wall-thickness records and reconstructed coordinate profiles remain unavailable. The estimates are not measured liquid fills. Fuls's later numerical paper makes4.04L conditional on assigning10 to a long stroke. Wells2018's indexed abstract describes40.4L as calculated from three complete vessels. [Fuls2012 author posting](https://www.academia.edu/8808307/VOLUMENMA%C3%9FE_VON_TONGEF%C3%84%C3%9FEN_DER_INDUSKULTUR), [Fuls2020 author posting](https://www.researchgate.net/publication/373522958_Ancient_Writing_and_Modern_Technologies_-_Structural_Analysis_of_Numerical_Indus_Inscriptions), [Wells2018 chapter](https://www.jstor.org/stable/j.ctv19vbgkc.46).

The coarse glyph observations below come from the original CISI photographs, not their OCR. All three clusters use tall strokes; the visible H370 cluster lacks U. The first volume appears twice in the government PDF; the second copy has offset431 and supplies no new object. [CISI1 government scan](https://ignca.gov.in/Asi_data/76884.pdf).

| Object | Original plate | Original visible cluster | CISI excavation ID | Fuls Table1 excavation ID | Identity status |
|---|---|---|---|---|---|
| H370 | printed233/PDF269 | seven tall strokes |12908|1033b|discordant|
| H371 | printed234/PDF270 | six tall strokes+open U/V |1033a|1033a|agrees|
| H372 | printed234/PDF270 | three tall strokes+open U/V |unknown|12908|discordant|

CISI basic data printed372/PDF408 identifies museum/photo pairs M774607/HU1302, M774608/HU1304 and M774609/HU1307 respectively. This prevents silent reassignment of physical measurements. The indexed Fuls table could contain a bibliographic/object-label error, but that is unresolved; it is not a correction we can make from presumed stroke-volume agreement.

Vats's original text records excavation jars1033A/B near the MoundF pavement/drain, with heights3ft and2ft10in; the associated table records bones and other contents and calls them post-cremation urns. These independent heights agree with the two source outer heights but do not supply interior radii. The excavation photograph is PlateXXIIIa, PDF58, not PDF60. No original content is inferred from reuse or deposition. [Vats text, printed91,254-255](https://ignca.gov.in/Asi_data/18220.pdf), [Vats plates](https://ignca.gov.in/Asi_data/9842.pdf).

## Fit data and frozen predictions

The following computations preserve author-reported profile estimates under the printed CISI labels. They are conditional on resolving their measurement-object discordance.

| Object | Long strokes n | Profile estimate L |40.4n prediction L|Residual L|Geometric-model envelope L/stroke|
|---|---:|---:|---:|---:|---:|
| H372 |3|121.0|121.2|-0.2|39.60–41.20|
| H371 |6|240.6|242.4|-1.8|40.10–43.18|
| H370 |7|283.8|282.8|+1.0|40.39–41.84|

The zero-intercept least-squares scale is40.35319149L per stroke. At a frozen40.4 scale, residuals are−0.17%,−0.74%,+0.35%. These small deviations are encouraging for the selected family. The model envelopes are sensitivity ranges over three geometric reconstructions, not confidence intervals. Unknown wall thickness, asymmetry, filling level and source identity are additional uncertainties.

All three vessels are fitting examples used in the prior literature. A three-item permutation has only six assignments: an ordinary nonrandomized permutation test cannot have a p value below1/6 even before publication selection and exploration are considered. Our JSON enumerates the six assignments as an illustration; it reports no inferential p value.

## Why capacity cannot identify the long stroke as ten

Let n be the observed count of long strokes, q their numeric value, and u a volume in litres per numeric unit. A capacity model reads

`V = n*q*u`.

Its predictions depend only on q*u. For any positive c, replacing q by c*q and u by u/c leaves every predicted capacity unchanged. In particular,

`40.4*n =4.04*(10*n) =(40.4/12)*(12*n)`.

These are mathematical alternatives, not historical readings. The three capacities could estimate approximately40.4L per graphic stroke; they cannot select q=10 instead of1 or12. Establishing10 requires another independent relation tying long strokes to a securely interpreted smaller unit. A physical vessel-standard value obtained by dividing an assumed stroke value into the same fit is not that independent relation.

## Additional vessels and the held-out gap

The source-preserved eight-row table is in [source_capacity_table.csv](source_capacity_table.csv). No row has been discarded for an inconvenient result. Five additional prior cases remain outside a validated frozen same-module test: H95-2661 and MD1374 have different/uncertain mark clusters; MD63-3 and MD63-6 have uncertain numeral denominators and complex text; K90 has two rim strokes spatially separate from its body text. Their capacities can inform comparisons once scope is fixed, but they do not automatically falsify a commodity-specific hypothesis.

The excavation-author primary Fig12.2 confirms H95-2661/exc6640-501 and a scaled vessel profile. Its enlarged rim cluster has four tall/slanted strokes and no U. The paper reports four inscriptions on this vessel, two before and two after firing, and reuse as a sump pot. The single digital face cannot establish its complete original commodity context. [Kenoyer/Meadow1997, printed151 and161, PDF13 and23](https://www.harappa.com/sites/default/files/pdf/Kenoyer1997_Excavations%20at%20Harappa%201994-1995%20New%20Perspective.pdf).

The inspected K90 plate, printed319/PDF355, shows two tall rim marks and a separate three-sign body inscription containing U. Its visible alternating scale bar lacks legible unit labels. The source's30cm scaling assumption is retained as an author assumption; it is not independently established by this photograph.

There are currently **zero independently eligible held-out capacity observations**. A useful next test requires frozen graphic membership and commodity/context scope, independently tied physical measurements, and complete new vessels. Residue or content evidence would discriminate a volume model from a commodity-weight model. The three selected pots' proportionality alone cannot do so.

## Reproduction and limits

Run `C:\Python313\python.exe research/literature/metrology_audit.py` from the workspace. It produces the JSON and two CSVs here. Numeric table-spacing ambiguity, source-page edition offsets and internal arithmetic discordances remain explicit. The code uses author-reported values, performs no glyph recognition, and supplies no phonetic reading or language assignment.
