# Harappa objects, excavation keys and physical observations

This run links primary figures and captions to 24 objects in an 81-object research frame. The acquired block covers all 22 copied steatite tablets H2218–H2239 and two rectangular comparison seals, H1710 and H1714. It restores the tablets' excavation-unit and item identifiers, records 66 displayed tablet faces, and makes the published variation in face arrangement available as a machine-readable table. The sources also provide one related seal and four photographed vessel fragments outside the frame. [Annotated ledger and observations](annotated/results.json).

The tablet group and its varied arrangements were published by Meadow and Kenoyer in 2000. Our contribution is the source-to-catalogue registration join, physical observation table, descriptive counts and access record. The preceding investigation had inspected H2238 individually; this run extends the image audit to the complete displayed group. [First coding pass](figure4-first-observations.json), [native-raster reinspection](figure4-native-reinspection.json).

## What was acquired

The frame follows three object groups identified in the 2010 HARP introduction, with rectangular seals added as comparisons. All targets remain in the [target ledger](annotated/target-ledger.csv), including the nine absent from the preserved export and the 57 for which this run acquired no identifiable object image.

| Published target group | Targets | Joined in the derivative export | Primary figure inspected in this run |
|---|---:|---:|---:|
| Copied tablets H2218–H2239 | 22 | 22 | 22 |
| Sealings and stopper H1719–H1725 | 7 | 6 | 0 |
| Stamped vessels H1727–H1766 | 40 | 32 | 0 |
| Rectangular seals H1704–H1715 | 12 | 12 | 2 |
| Total | 81 | 72 | 24 |

The main witness is Figure 4 in Meadow and Kenoyer's *The ‘Tiny Steatite Seals’ (Incised Steatite Tablets) of Harappa: Some Observations on Their Context and Dating*. The preserved author PDF has 21 pages. Figure 4 occupies PDF page 15, displaying author page 14; its caption is on PDF page 16, displaying author page 15. The corresponding mapped book pages are 334 and 335. The drawing shows three rectangular faces and a triangular section for each tablet, with a 0–3 cm scale bar below. Figure 2, PDF page 8, mapped book page 327, supplies the find-location plan. The [scale and pagination correction](corrections/2026-10-02-scale-and-pagination/README.md) preserves earlier annotation fields and records the revised source locators. [Original author-hosted chapter](https://www.harappa.com/sites/default/files/pdf/Kenoyer2000_The%20Tiny%20Steatite%20Seals%20of%20Harappa.pdf).

Meadow and Kenoyer's 2005 excavation chapter supplies a drawing and caption table for H1714, registration H2000-4487/9438-01. Their 2001 excavation summary supplies H1710, registration H98-3491/8322-21, as Figure 4.8. Both figures show the inscribed face and a convex lower profile with a perforation. H1714 has three visible graphic groups in a horizontal row. Fine grouping on H1710 remains unresolved in the small original image. [2005 chapter](https://www.harappa.com/sites/default/files/pdf/Kenoyer2005_Excavations%20at%20Harappa%202000-2001%20New%20insights%20on.pdf), [2001 source caption](https://www.harappa.com/indus4/e3.html), [coded comparison observations](additional-observations.json).

The supplementary vessel photograph comes from Wright, Shuldenrein and Mughal's Beas survey page. Its 4050×3252 original Figure 12 shows four fragments with impressed areas on curved vessel walls. The prose describes five impressed pointed-base goblet sherds. The four visible fragments have image-scoped identifiers; the fifth is retained as a reported object without a visible image. The page supplies no individual registration or CISI join. [Original survey page](https://www.harappa.com/beas/mapping-project), [our fragment observations](beas-observations.json).

## The recovered tablet context

Every tablet's caption registration matches one derivative physical-object family. The source provides the full form `H{year}-{registration}/{excavation-unit}-{item}`. For example, H2218 joins through H97-3319 to source specimen 11, whose caption restores unit 8040, item 13. Figure specimen numbers and CISI numbers have different orders, so joining by position would assign the wrong contexts. [Caption registration ledger](figure4-caption-ledger.json), [computed joins](annotated/results.json).

Sixteen tablets have unit 8040 and distinct item numbers. The source describes sixteen tablets recovered together in a clump, two nearby finds, and four scattered finds in the same area. Its text and find-location plan identify the six other specimens: 9 and 16 nearby, and 6, 17, 18 and 20 scattered. These agree with the six registrations outside unit 8040. Their units are 8038, 6951, 8010, 6937, 6560 and 8039 respectively.

The published stratigraphic argument places all 22 tablets in debris deposited after curtain wall 296 and the fill between it and perimeter wall 250, before Period 3C material arrived. We record this as late Period 3B deposition. The date field carries that wall-and-dump basis. H1714 carries the source's literal `3C?` with a surface-wash context; H1710 carries its caption's `3C` assignment. The witnesses provide scale-bearing drawings for measurement, while museum accession and individually reported object dimensions remain absent for these 24 targets. [Source assertions and coordinates](figure4-caption-ledger.json), [comparison dating fields](additional-observations.json), [scale correction](corrections/2026-10-02-scale-and-pagination/correction.json).

The source authors assigned the tablets to at least three engravers after microscopic inspection of fine-grain moulds. That published interpretation is stored beside the drawing observations. The recovered deposition keys show how each group occurs in the clump and nearby area:

| Published engraver group | Tablets | Unit-8040 clump | Nearby | Scattered |
|---|---:|---:|---:|---:|
| 1 | 6 | 5 | 0 | 1 |
| 2 | 9 | 7 | 2 | 0 |
| 3 | 7 | 4 | 0 | 3 |

The group counts make this a useful study of repeated production and subsequent gathering. The inscriber worked around a three-sided object, making the same inventory of forms on multiple separate blocks. The source's mould examination addresses the cutting operation; the excavation keys address where the objects were deposited. Both can now be joined to the corpus at the object level.

## Visible arrangements

We coded descriptive forms before consulting catalogue sign sequences. `A` denotes an open angle-like form, `D` a closed diamond-like form and `C` the complex form on the top displayed face. Each readable face places its form beside short upright strokes. The native source raster resolves seven direct stroke counts: five faces with three strokes and two with four. On specimens 8 and 16, all three faces are clear enough to record the pattern 3, 4, 3. Specimen 18's middle face has three strokes, extending the earlier H2238 observation. Other fine counts remain unassigned. [Native reinspection](figure4-native-reinspection.json).

The two lower displayed faces are readable as a pair on 19 tablets. Their middle form, middle position and bottom position occupy all eight combinations allowed by the declared coding. Three bottom faces remain obscured by dense hatching, all within published engraver group 3.

| Middle form | Middle form beside strokes | Bottom form beside strokes | Tablets |
|---|---|---|---:|
| A | left | left | 2 |
| A | left | right | 2 |
| A | right | left | 2 |
| A | right | right | 5 |
| D | left | left | 2 |
| D | left | right | 3 |
| D | right | left | 1 |
| D | right | right | 2 |

This table quantifies the variation described in the original chapter. Each row links to the supporting registrations and source specimen numbers in [the display summary](display-summary/results.json). Top, middle, bottom and left/right refer to the published drawing. A separate [representation audit](../tablet-representation/README.md) computes which groups remain when lower faces exchange or their displayed ends reverse. [Descriptive summary method](DISPLAY-SUMMARY.md).

## Methods and source assumptions

The [protocol](PROTOCOL.md) preceded acquisition of the new figures. We froze the [first image block](FIRST-IMAGE-BLOCK.md), saved a first visual coding pass, and preserved a separate refinement after inspecting the embedded 3394×4393 original raster. Every crop has its original bounds and hash. Registration parsing uses the caption for excavation-unit/item keys and the derivative identifier only to find the corresponding catalogue family. It does not read sign sequences or transfer derivative dimensions into primary-source fields.

The shared assumptions are that the published registration identifies the intended object, that the drawing preserves the displayed arrangement, and that the accompanying archaeological description applies to its stated specimens. Observation fields distinguish visible pixels, captions, published descriptions and interpretations. A material or phase named in a caption has a different basis from a visible stroke or hole. Object joins leave the physical source sides unaligned with derivative face codes.

The code refuses to overwrite completed endpoints. It saves hashes, source coordinates and code snapshots with the initial frame, annotation endpoint and descriptive summary. All acquired PDF, HTML, OCR, raster and crop witnesses remain local-only under `local-witness/`. Tracked files contain our annotations, factual identifiers, methods, access records and aggregates.

## Next experiment

The recovered tablet keys support a source-defined production study that includes the short inscriptions omitted by the principal length-at-least-three sign-model population. A useful next acquisition is a photographic or 3D record of the 22 tablets with both ends and each adjoining face identified. Two independent coders could then record physical face order, incision directions, stroke counts and damaged regions while the published engraver labels remain concealed. The unit-8040 clump can be compared with the six other finds after those observations are frozen. This would test whether repeated forms retain the same physical arrangement and cutting habits across the published production groups.

The vessel branch has a different immediate target: stamping geometry. A flat rectangular seal pressed against a curved wet vessel wall can leave an uneven contact region. A forward model can calculate contact depth across a seal face, then predict which edge strokes survive at each pressure and vessel radius. Its measurements should include the footprint boundary, sign positions, groove direction and break edge. H1714's scale-bearing drawing and the four Beas photographs supply candidate geometries for developing that method; calibrated vessel images and identified stamps are needed for testing a specific pairing. [Recorded physical observations](annotated/results.json).

## Approaches, challenges and fixes

The full CISI 3.1 plates and basic-data tables were sought through author, Helsinki, library and public archive routes. The accessible Helsinki and Finna records supplied bibliographic or printed-holding information. The HELDA web route failed at retrieval. No full plate witness was acquired, so the current frame preserves the sealing, stopper and forty vessel targets as source gaps. The successful route was to follow individual registrations into earlier original HARP publications. [Exact access routes and outcomes](source-access-log.json).

Several source-handling problems affected the work. The first 180 dpi render hid fine details that were clearer in the native PDF image; separate first-pass and revised annotations preserve that change. Dense hatching still prevents three lower-face readings. Tesseract read H1714's phase as `3C2`; checking the caption pixels recovered `3C?`. The 2001 article contents had stale links, while its older public `/indus4/` URL redirected to the working author page. Its expected photograph proved to be a drawing, which the observation table records. An image-header check also corrected a transcribed height from 568 to 566 pixels. The [format refinement](source-format-refinement.json) preserves that correction beside the original notes.

The initial registration parser required a trailing word boundary. The derivative export concatenates some identifiers and figure labels, such as `H97-3319Figure 12.11`, so that parser found no match. The pre-output failure was preserved, the locator was changed to stop at the final registration digit, and all 25 caption registrations then joined uniquely. [Failure record](annotation-join-first-failure.json).

The Beas source describes five fragments while its linked image shows four. Both counts remain in the ledger. Fine stamp grouping, polarity, individual registrations and dimensions are unresolved for those fragments. These specific gaps guide the next source request and prevent the same public-page search from being repeated without a new target.

The [verifier](verify.py) executes each frozen code snapshot unchanged while supplying its original workspace paths. Both replays reproduce every result field except creation time. To repeat them, select fresh replay/output directories; the code protects completed endpoints. The working helper is [harappa_object_frame.py](../../../src/six_hour/harappa_object_frame.py). All 97 integrity, accounting and replay checks passed in [verification.json](verification.json).
