# CISI1 scan, image and artifact units

Primary source: Joshi and Parpola1987, [Corpus of Indus Seals and Inscriptions, Volume1](https://ignca.gov.in/Asi_data/76884.pdf). Source SHA256 `47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d`.

## Exact scan repetition

The government-hosted PDF has862 pages. `audit_cisi_scan.py` extracts and hashes every embedded page image. For each first-volume page1–431, the ordered list of image SHA256 values exactly equals that on pageN+431. There are431 duplicate groups, all at offset431, and no exception. `cisi1_page_image_audit.json` preserves the per-page lists.

Retain PDF1–431 for evidence; PDF432–862 adds no new photographed object. This is an image-identity audit, not an archaeological estimate.

| Volume component | First scan PDF pages | Printed pages | Repeated scan PDF pages |
|---|---:|---|---:|
| Front cover and front matter |1–36| Roman-numbered introduction endingXXXII |432–467|
| Black-and-white photographs, including Addenda |37–400|1–364|468–831|
| Form-class table and basic-data catalogue |401–411|365–375|832–842|
| Corrigenda on final catalogue page |411|375|842|
| Map |412|376|843|
| Colour photographs |413–428|377–392|844–859|
| Rear blank/cover pages |429–431|Unnumbered|860–862|

For ordinary Arabic-numbered pages1–392, first-scan PDF page=printed page+36; repeat-scan PDF page=printed page+467. Roman front-matter pageXXIV is PDF28 and XXV is PDF29.

## Primary counting conventions

IntroductionXXIV–XXV(PDF28–29) distinguishes uppercase object-side codes from lowercase impressions of those sides. It defines *bis*, *ter*, and *quater* as additional photographs of the same side. Parenthesized numbers can identify views or enlargements; unparenthesized inscription numbers identify separate inscriptions on one side. Therefore object, side, inscription, impression, view, and scan-page identifiers must be represented separately. A second photograph may improve legibility without adding an object or independent inscription.

The Corrigenda p.375(PDF411) also identifies erroneous distinct object numbers. In particular, duplicate photos were included in the H252–H277 series on pp.218–222; H266–H275 were deleted and reserved for later-volume objects. H356A/B/C are H354A/B/C *bis*. These cannot support replication. Mirror and side-label corrections must precede direction checks. The source page is preserved as `renders/cisi1_pdf411.png`; catalogue OCR is a locator only.

## H355 targeted adjudication

H355 is illustrated on printed231(PDF267) with three uppercase sides A,B,C. B and C each show a U-like sign and three long strokes. They have separate side captions; neither is a *bis* view or a lowercase impression. The H356 correction applies to H354, and does not merge or relabel H355.

Basic data printed372(PDF408) identifies H355 as Mahadevan1977 line3889, excavation1274, museumASI63.11.233, photographHU716. H354/H356 share excavation1278 and museumASI63.11.131, whereas H355's identifiers differ. These records independently support the catalogue's distinction.

This validates a single object's two numbered faces with the same visible three-stroke module. It does not establish that they encode equal quantities, or justify a general equal-quantity rule for all tablets. The source is a catalogue audit, and its photography remains too coarse to certify every small glyph feature. Full-page renders at3×: `renders/cisi1_pdf267.png` and `renders/cisi1_pdf408.png`.

H2238 is outside this volume, whose Harappa sequence endsH382. A subsequently acquired primary excavation chapter partly resolves the gap: [Meadow and Kenoyer2000](https://www.harappa.com/sites/default/files/pdf/Kenoyer2000_The%20Tiny%20Steatite%20Seals%20of%20Harappa.pdf), internal pp.14–15/PDF15–16, Fig.4 specimen18, identifies H95-2613/6560-01 and depicts three short strokes beside the diamond-like sign. The digital H2238 excavation number matches. Status: primary drawing supports three-stroke exception; photograph/fine-glyph identity unverified. See `h2238_primary_audit.md`.
