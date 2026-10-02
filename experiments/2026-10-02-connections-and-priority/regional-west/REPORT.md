# Regional weights and numerical records

The western route now has an object-level numerical test and a concrete Central Asian recovery target. We joined a marked Susa weight to its museum record, reconstructed a published relation among three measured weights, and checked a straight tally model against all explicitly coded marks in the catalogue's Susa entries. At Gonur, the strongest numerical lead is a reported hoard of 26 possibly marked clay tokens. Its original figure and field identifiers are the next records to acquire.

This run generated the object table, uncertainty bounds, graphic census, and recovery priorities. The archaeological objects and the proposed Susa relation were published earlier. The calculations are exploratory and were designed after seeing the masses. Source observations and prior interpretations have separate fields in [evidence-table.json](evidence-table.json) and [evidence-table.csv](evidence-table.csv). Raw documents, catalogue derivatives and images remain local-only.

The clearest Susa object is Louvre **SB 13677 / AS 2615**, catalogue 224: a hematite ovoid weighing **334.25 g**. The book describes four engraved circles. The [Louvre notice](https://collections.louvre.fr/ark:/53355/cl010186254) describes four points, repeats both identifiers, and cites that exact entry and Plate 5. The compressed plate cannot resolve the fine shape. Macro images should establish whether the marks are drilled depressions, circular outlines, or another form.

Ascalone proposed that this weight marked an equivalence among regional systems, including a quarter of a Dilmun mina. We assessed the proposed common base using his likely Indus imports: **SB 13323 / AS 9546**, a 13.43 g discoid, and **SB 17774 / AS 5724**, a 27.25 g jasper cuboid. The latter has a catalogue range of 2500–2000 BCE. The ovoid and discoid entries lack a creation-date range. Their current join is at the site level. [Ascalone 2022](https://airus.unisalento.it/retrieve/c39309c8-8dae-4dba-b990-86171612edf6/E.%20Ascalone%2C%20Bronze%20Age%20Weights%20from%20Mesopotamia%2C%20Iran%20and%20Greater%20Indus%20Valley_compressed.pdf), pp. 49, 62–63, 69–70; Plates 5, 22.

The historical proposal gives coefficients **25:1:2** in a common base. The coefficient 25 comes from a quarter of a 100-unit mina; four visible circles alone do not supply it. The inferred bases are 13.37 g, 13.43 g and 13.625 g.

| Calculation | Result |
| --- | ---: |
| Smallest symmetric variation allowing all three bases to overlap | 0.944619% |
| Smallest allowance when differences must come entirely from mass loss | 1.871560% |
| SB 13677 mass predicted by 25 times half the SB 17774 mass | 340.625 g |
| Difference from the published SB 13677 mass | 6.375 g |
| Unit implied by four equal additive marks on SB 13677 | 83.5625 g |

With a 1% symmetric allowance, the common-base interval is 13.4901–13.5051 g. With a 2% loss allowance, it is 13.6250–13.6429 g. These are sensitivity bounds, without a calibrated manufacturing or damage distribution. Exact arithmetic and all intervals are in [numerical-compatibility.json](numerical-compatibility.json), produced by [analyze.py](analyze.py) under [PROTOCOL.md](PROTOCOL.md).

The rival model gives every repeated mark a fixed mass within the same recorded shape, material and date category. The census found **69 explicitly coded Susa entries**. Eight have unknown missing mass written +x; one combines strokes and a circle; three have unresolved accession collisions. The ratio analysis contains 57 measurements: 49 stroke, 7 cross and 1 circle. [marked-weight-census-v2.json](marked-weight-census-v2.json) records aggregate ranges and every member's catalogue ID.

| Shape, material and graphic family | Objects | Mass per mark | Minimum symmetric variation |
| --- | ---: | ---: | ---: |
| Ovoid, hematite, strokes | 4 | 8.270–10.195 g | 10.425% |
| Ovoid, stone, strokes | 17 | 0.565–496.500 g | 99.773% |
| Ovoid, limestone, strokes | 8 | 8.491–5022.500 g | 99.662% |
| Duck, limestone, strokes | 3 | 491.900–511.167 g | 1.921% |
| Ovoid, stone, cross | 3 | 4.000–4.250 g | 3.030% |
| Ovoid/discoid pebble, stone, cross | 2 | 3.810–4.150 g | 4.271% |

All multi-object groups lack creation dates in their entries. Recovering those dates will permit narrower historical comparisons. Some objects are chipped despite having a printed numerical mass; the condition remains in the local extraction. The limestone ducks provide a candidate common large unit. The wider stroke groups require different unit levels, periods, fractional notation, or other uses of the mark. A separate unrestricted unit for each artifact would fit every mass. A useful model therefore needs a recorded unit or a repeated convention within a dated assemblage.

The duck group consists of **SB 9342 / AS 13821**, cat. 598, 2459.50 g with five strokes; **SB 9340 / AS 13820**, cat. 603, 3067.00 g with six; and **SB 13748 / SH 095373**, cat. 608, 4940.00 g with ten. The last is slightly chipped. The cross-marked ovoids are **SB 13552 / AS 9522**, cat. 38, 4.00 g; **SB 13561 / AS 9520**, cat. 44, 4.17 g; and **SB 13177**, cat. 50, 4.25 g. The pebbles are **SB 13564**, cat. 669, 3.81 g, and **SB 15535**, cat. 670, 4.15 g. Measurement locators: Ascalone pp. 44, 59, 61–62, Plates 1, 16–17, 21. The book cites Soutzo 1911 for the ducks and SB 13177.

The complete pure-circle comparison has only SB 13677. Its additive 83.5625 g unit and the published quarter-mina reading need an external observation to separate them. A second dated circle-marked weight with a readable unit label would be particularly useful. The newer chapter *Note on New Weights from Susa: Further Evidence on Susa-Indus Commercial Transactions and Cultural Relations*, pp. 461–495, belongs in this recovery packet. [Publisher contents](https://brill.com/edcollchap/book/9789004541436/front-1.pdf) verify its publication; full text remains to acquire.

A readable control uses Girsu **AO 247**, 82.53 g with a 10-shekel inscription, and **AO 248**, 41.55 g with 5 shekels. Both entries belong to the 1881 excavations and the 2100–2000 BCE range. Their bases, 8.253 g and 8.310 g, require 0.344141% symmetric variation or 0.685921% loss allowance. Source: Ascalone p. 80; Jan Tavernier's appendix p. 180, Plate 27. This demonstrates the calculation with an attested reading while preserving the uncertainty of the Susa coefficients.

At Gonur, the elephant seal has a useful museum join: **Excavation 9, Room 19**, white steatite, 3.8 × 3.9 × 1 cm, Fine Arts Museum, Ashgabat. The [exhibition label](https://www.museicapitolini.org/sites/default/files/f_file/Vetrina%201%20sottosezione%20B.pdf) supplies dimensions missing from the older discussion. The reported 26-token hoard came from a room near the **Gonur North Palace entrance**, with original locator **Sarianidi 1998 Fig. 41**. Its exact room, inventory, layer and date remain to recover. These separate contexts make field records especially valuable. Sources: [Bonora et al. 2014](https://www.persee.fr/doc/paleo_0153-9345_2014_num_40_1_5616), p. 66; [Kaniuth 2010](https://www.vorderas-archaeologie.uni-muenchen.de/personen/wiss_mitarbeiter/kaniuth/publikationen/kaniuth-2010_amit-42.pdf), pp. 5–6.

Altyn Depe's two-sign seal came from **Excavation 9, Room 105**. The proposed numerical tablet came from **Excavation 5, Room 18, Altyn 11**, an earlier phase; its original locator is **Kircho 2008b Plate 94.2**, reproduced as Bonora Fig. 12. At Tepe Yahya, the one-mark 13.37 g object **Z.82** has a 4500–4000 BCE catalogue context. It supports an earlier graphic/weight comparison. **Z.2266**, 10.58 g with reported 1–4–1 dots on three sides, needs its chronology and all-face images.

The envelope search recovered Englund's 2006 article after correcting a hostname certificate mismatch. It supplies illustrations of SB 1940, SB 1927 and Susa 77,2130.2. It yielded no newly matched unequal internal token mixture and exterior count. The existing SB 1940 packet remains three round tokens and three rods. An unequal comparison or direct token/impression geometry would provide another constraint. Acquisition routes and failures are in [ACQUISITION_LOG.md](ACQUISITION_LOG.md).

A bounded text search checked all **938 Greater Indus catalogue records**, including **870 Dholavira objects**. No description contains an explicit marking, inscription, incision, dot, engraving or graffito term. Selected Dholavira Plates 56, 58, 60–62 also yielded no readable Indus glyph joined to a mass. The compressed photographs do not show every face. [indus-weight-audit.json](indus-weight-audit.json) preserves complete ID coverage and the search expression. Tavernier's 29-object appendix supplies regional cuneiform and Elamite controls. Dholavira is promising for a context join: the chapter reports 505 objects with archaeological context. Match DHR numbers, grids and levels to original seal and sealing inventories, then inspect candidate weights in full photographs.

| Recovery packet | Original locator | Observation needed |
| --- | --- | --- |
| SB 13677, SB 13323, SB 17774 | Ascalone cats. 224, 694, 698; Louvre cl010186254 | Mark geometry, calibrated masses and dated assemblage |
| Three ducks and five cross objects above | Ascalone cats. 38, 44, 50, 598, 603, 608, 669, 670 | Full mark images and creation dates |
| Gonur North 26-token hoard | Bonora p. 66 → Sarianidi 1998 Fig. 41 | Original figure, room, inventory and associated sealings |
| Gonur Indus seal | Kaniuth p. 5 Fig. 2.2 → Sarianidi 2005 p. 258 Fig. 114 | Field number and Room 19 counted/weighed objects |
| Dholavira sign/weight assemblage | Ascalone cats. 1189–2058; pp. 135–136 | DHR plus grid/level join to seal and sealing records |
