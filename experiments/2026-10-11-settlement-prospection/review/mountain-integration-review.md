# Mountain, cave and coastal integration review

Reviewed 11 October 2026. This bounded review checks the mountain evidence against the frozen manuscript and candidate register. It is a source-integration audit by the contributor who assembled that evidence, rather than an independent archaeological assessment. Neither frozen file was edited.

Reviewed endpoints:

- `review/draft-v1.md`: SHA-256 `dee0212d5b3c93b34a523c445404660a79eeaf72e5bda28dcadfcbfffaf5ac06`.
- `candidates-v2.json`: SHA-256 `04a2442bee8565d0cc56ba484122c829e891645a59d057f265678b574add63bb`.

## Required geographic and evidence-scope fixes

### 1. P18 excludes two of its named anchors

The government [Ghazi Shah inventory](https://doam.gov.pk/public/sites/7279), R41, gives latitude 26.454762389 N and longitude 67.464134722 E. The northern bound of 26.3 excludes it. A newly checked primary record establishes the same problem for Kai: the Government of Sindh 2015 [Introduction to the Inventory of Cultural Property](https://rio-heritage.org/wp-content/uploads/2016/10/introduction-inventory-of-cultural-property-in-the-province-of-sindh.pdf), printed p.14, Register by Locality, lists Kai Caves under identifier `KCV356300E2910326N`, coordinates 26°18′20.1″ N, 67°33′37.7″ E, and entry I/382. The latitude converts arithmetically to 26.305583 degrees, just beyond the frozen boundary. The indexed primary table was inspected; direct PDF access failed. These are published coordinates of known inventory entries, used here to audit an editorial rectangle.

Change the P18 rectangle to `[67.0, 25.0, 68.1, 26.6]` in the next candidate version and regenerate its map and GeoJSON. This is a coarse editorial expansion that includes both anchors, not a measured archaeological catchment. Rename the window **Kirthar piedmont, Jamshoro and southern Dadu** so its name also covers Ghazi Shah. Update draft lines 368 and 374 in the next manuscript version. Add a source observation for the Introduction's coordinate table; R43 currently points only to Volume I's descriptive entry.

The Volume I entry, printed p.383, describes Kai Caves as a natural cave in **deh Naig Sharif**. That administrative wording does not identify a separate dated “Naig cave,” establish the extent of the Naig valley sites, or reconcile the named upper and lower Kai cave groups. No separate primary coordinate for those groups or a Naig cavity was verified in this review. Replace the candidate's current “Kai-Naig cave names require concordance” with: **“Match the Kai inventory entry in deh Naig Sharif to the named cave groups and nearby valley sites before selecting a cavity for investigation.”**

### 2. P18's Class B scope must exclude an implied upgrade of cave evidence

Class B fits preservation comparisons around existing piedmont archaeology, including Ghazi Shah once the boundary is corrected. The cavity component still needs chronology and cultural attribution, meeting the manuscript's Class C definition. The present entry places that component within one Class B target without explaining the distinction.

Use this replacement for draft line 370 and the corresponding candidate fields:

> Existing mission survey and known valley occupations support Class B comparisons of piedmont preservation and low-relief activity. Test fan/interfluve contrasts and workshop/camp relationships. Matching the Kai inventory entry to named cave groups is a separate Class C task requiring identity and chronology. [R22, R37, R41, R42, R43]

Remove R44 from P18's candidate `source_ids` and appendix citation. Kakar's survey concerns northern Balochistan's Sulaiman Range, including Tor Ghar north of Musa Khel and Zhob-area shelters; it supplies neither local Kirthar evidence nor a dated Indus occupation. The [primary chapter](https://publications.dainst.org/books/dai/catalog/view/2043/2427/4466), printed pp.22 and 24, supports retaining R44 in §5.4 as an explicitly distant shelter-recording analogue. R22 includes Rohri as well as Ongar: its Rohri observations belong to P10, while its Lower Sindh quarry/workshop observations can inform the regional P18 comparison. Candidate annotation should name the relevant part of that source.

### 3. P21 needs the same external-analogue label already supplied for P19

Draft line 394 and P21 currently cite R26 and R31 without specifying their geographic contribution. R26 supplies Kech-Makran regional cultural context, not a local offshore land-surface chronology. [Biagi 2024](https://doi.org/10.1007/s44289-024-00003-y), R31, provides Las Bela and Lower Sindh coastal observations east of the Gwadar-Pasni rectangle. Their processes can inform a test, but their dated deposits do not date a surface within P21.

Replace P21's evidence origin with: **“Makran regional archaeological context and coastal preservation analogues from Las Bela and Lower Sindh outside this rectangle; local shoreline and occupation chronology remain to be established.”** Retain Class C and the proposed cores, sediment-environment checks and relative sea-level reconstruction. No change to the rectangle follows from these analogues.

## Chronology and inference checks

### Mehrgarh 2025: qualified correctly, with an optional precision edit

Draft line 129 accurately restricts the new result to the sampled Period I cemetery and records the exclusion of two dates. [Mutin and colleagues 2025](https://doi.org/10.1038/s41598-025-92621-5), Results, PDF p.3, identifies preferred model v1.1, manual exclusion of T509 and T551, and cemetery start 5223–4914 cal BCE. The agreement index rises from 51 in v1.0 to 98 in v1.1; this is model agreement, not an independent probability that the inferred chronology is correct. The full PDF was checked; its supplementary dataset was not acquired.

For precision, replace the sentence with: **“A 2025 tooth-enamel study estimates the sampled Period I cemetery's start at 5223–4914 cal BCE in the authors' preferred v1.1 model, after manually excluding two dates.”** Keep the following sentence limiting its relevance to Bronze Age surfaces. The source does not establish dates for every Kachi paleosol or demonstrate an Indus-age flood at the proposed fan contacts. The draft makes neither claim. P17 contains the official [Nausharo](https://doam.gov.pk/public/sites/8927) and [Mehrgarh](https://doam.gov.pk/public/sites/8911) inventory locations; its current Class C assignment is appropriate. Its northern Balochistan shelter possibilities remain proposed local investigations rather than applications of Kakar's distant survey.

### Kech date-seed study: current caveat holds; state the prospecting consequence directly

Draft line 187 correctly reports the unresolved relation between 13 classified seeds and 15 listed IDs. [Ivorra and colleagues 2024](https://doi.org/10.1016/j.jas.2024.106052), §2.2.1 and Table 2, PDF p.5, describes six Miri Qalat and seven Shahi Tump seeds but lists six MQ and nine ST IDs. Table 2 provides four conventional radiocarbon ages, not a calibrated calendar-phase table. Section 3.2, p.10, classifies 12 of 13 as wild morphotypes; §4.2, p.11, discusses damage-related selection that can favor rounded forms. The full PDF was read at these locators. The manuscript does not turn 12/13 into a regional cultivation percentage or identify the cohort as Mature Harappan.

The practical implication is clearer with this replacement for the paragraph's last sentence: **“The selected morphometric result makes modern palm groves a hypothesis for resource access that needs historical testing. It cannot establish ancient grove locations or the region's crop composition.”** R47 supports regional occupations and an archaeobotanical test; it does not observe fan burial within P16. Keep P16 Class C and describe fan aggradation as the proposed masking mechanism. A seed-cohort audit cannot locate a buried settlement.

### Caves, landslides and coast: no discovery probability has been imputed

Draft lines 133–137 distinguish proposed burial processes from observations and explicitly state that no route-cost surface, cave inventory or landslide chronology was computed. P16 and P17 list natural sediment lenses, different-period occupation, empty caves and reworking among their rivals. Candidate discovery counts, areas and artifact quantities remain null. The coast section likewise requires locally dated surfaces and separates inland paleoshorelines from possible inundation. These statements are appropriately bounded.

One sentence adds an unsupported operational ranking: “The strongest near-term mountain opportunity” at line 137. Access, field capacity and comparative expected return were not measured. Replace it with: **“Within the reviewed source frames, the proposed mountain work begins with buried or lightly represented activity around known occupations; cavity tests begin with identity and chronology.”** This describes the proposed research sequence without predicting discoveries or implying current feasibility.

