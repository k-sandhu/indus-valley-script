# Acquisition and census retrospective

The package produced 36 site/provenance rows and retained the coordinator's 42 local faces. The earlier broad pass supplied the frame, while its unassessed metadata required new source checks. Live searches recovered a 2022 CISI volume absent from the assignment's volume list, current institutional download routes for two excavation reports, and a project account of recent Umma surveys. The row frame and arithmetic reproduce; many catalogue joins and geographic fields remain open.

## Reused work

Before research, the root instructions, README, knowledge index, writing rules, redistribution policy, registry and relevant retrospectives were read. The contribution assessment, Frenez lecture check and external phonetic-anchor audit supplied existing cautions and source leads. The earlier `sites-and-publications` census and `local-site-coverage.json` supplied the site frame and local figures. No shared file was edited.

The registry checks covered COMM-02's failed recovery of the Tell Jokha illustrated report, OXUS-SOURCE-02's original Gonur and Altyn recovery, SUSA-SOURCE-02's separation of weights from inscriptions, and the dataset-landscape denominator problem. `acquire_sources.py` copied existing Gadd, Frenez 2016, Frenez 2018, Sarianidi 2005 and Kircho 2008 PDFs into this package's raw directory. Gadd's pre-existing OCR supplied the readable catalogue text because the acquired PDF has almost no extractable text. The Frenez 2018 acquisition was a supporting lead; the final rows rely on the cited specimen sources. These earlier witnesses were preserved.

## Approaches, problems and remedies

Three subject searches per row covered inscription literature, excavation/publication history and geography or later finds. A fourth targeted Mahadevan/ICIT query was then run for every row. General corpus results did not supply inspected site subtotals. Additional searches addressed missing bibliographies, present CISI coverage and Murda Sang's locality. `searches.json` contains 182 queries and names pooled responses explicitly; the web tool does not supply an unambiguous result-to-query mapping within a batch.

The initial direct downloads of Laursen 2010 and Vidale/Frenez 2015 returned HTTP 403. Their PDFs were readable through the web reader, and this access distinction remains in `sources.json` and the raw acquisition logs. Old ISAC file paths returned 404 for Nippur and Tell Asmar. Current landing-page download links pointed to versioned public S3 objects; `acquire_s3.py` recovered both original reports. The British Museum record returned 403 when opened, so its current online fields are attributed to snippets and checked against Gadd where possible. A Persee HTML download encountered an access page and did not establish a Murda Sang witness; the direct excavation narrative corrected its locality to Kanrach valley.

The CISI 3.3 institutional excerpt was acquired locally after a web-reader failure. It contains the preface and contents but lacks catalogue plates. A dated protocol amendment added this source before the aggregate endpoint. It revealed that local large catalogue numbers are legitimate identifiers in mixed site sequences. The build therefore retained the raw identifier diagnostics and left coverage fractions undefined. Existing Gonur recovery established a 2004 elephant seal independently of a cuneiform cylinder; the 2022 preface confirmed the absence of Gonur's promised corpus from that volume.

The Dilmun label required a production/findspot distinction: BM123208 was found at Ur. Its exact local family join remains unresolved. At Salut, two impressed rim fragments may belong to one vessel; the object minimum combines one vessel with the separate chlorite seal. Hajar's local tablet label and a published al-Hajjar prism need a photograph-level comparison. These decisions are recorded with their source locations in the rows.

Verification found that the new CISI extraction check compared LF output with an existing Windows CRLF witness. The script now checks normalized text content and preserves the original bytes and hash. The saved census itself reproduced without a changed endpoint. The independent verifier checks actual JSON/CSV agreement and resolves 779 source links. Hash checks cover eight PDFs used in row evidence.

## Outcome and unfinished work

There are 23 named-site rows and 13 additional or cross-reference rows. Fourteen rows have final-report bibliographic identifications, nine have sourced coordinates, and four have later inscription-related reports. No dated find could be matched to a supported complete CISI cutoff. The selected published object minima sum to 36 under the row-specific inclusion decisions, with incomplete inventories and uncertain signs retained explicitly.

The incomplete work is source acquisition and object reconciliation: full Kjaerum and other final catalogues, actual CISI plates, Mahadevan/ICIT site subtotals, most geographic coordinates and verified modern subdivisions, and many custody/registration statements. At several sites, a substantial regional source was opened but the main specimen catalogue was not obtained. Those rows contain search-linked unresolved fields. A repeat should acquire those witnesses or perform object joins; it should not rerun the same broad searches and interpret another count of mixed glyptic entries as an Indus inscription inventory.

The reviewer should rerun the build, independent verification and prose check; sample Laursen Table 1 and Figs. 10/14/15, Nippur plate 89, CISI 3.3 preface and contents, and Salut pp. 116–118; and inspect the Gadd/British Museum accession correspondence. All raw witnesses remain local, and no shared registry or manuscript was changed.
