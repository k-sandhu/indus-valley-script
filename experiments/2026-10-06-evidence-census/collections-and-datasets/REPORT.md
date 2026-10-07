# Public collection records and corpus joins

Status: **Exploratory**. Focused observations: 7 October 2026. [Earlier report](history/2026-10-07-depth-pass/REPORT.md).

This pass documents **114 inscription-confirmed original records** across six catalogues: 108 retrieved directly and six British Museum records returned by the search provider. **61/114 (53.51%)** join to the existing Lipi export through explicit identifiers or published concordances. The outputs establish record minima, field coverage and a completed paired audit. Completeness of the wider evidence index remains unestablished because major inventory totals and some catalogue routes remain unavailable. [Summary fields inspected_original_records, direct_http_200_original_records and confirmed_join_records](focused-summary.json).

## Catalogue counts and their bases

| Collection | Confirmed original records | Search frame and unresolved coverage |
|---|---:|---|
| National Museum, New Delhi | 76 | Seven-term portal union: 1,827 record IDs; 108 unique candidates inspected, including 32 with unconfirmed inscriptions. |
| Indian Museum, Kolkata | 18 | Union: 2,082 IDs; 42 unique candidates. Also ten plaster copies, 12 unconfirmed inscriptions and two other-script records. |
| Allahabad Museum | 0 found in this frame | 65 keyword results; no seal/tablet/inscription candidate in returned titles/descriptions. Holdings total unmeasured. |
| Penn Museum | 5 | Complete Indus Script filter: 34 records, five original seals and 29 plaster impressions by type/material facets. Broader site queries remain partly unadjudicated. |
| Met | 5 | Website totals: Indus 76, Harappa 27, Mohenjo-daro one, Indus seal 3,234. Five seals individually inspected; broad totals include other material. |
| Louvre | 4 | Four per-object JSON records HTTP 200. Search HTTP 429; earlier 21-result excerpt includes mixed objects. |
| British Museum | 6 cached witnesses | Official seal text returned by search provider. Direct HTTP 403 and malfunctioning browser search prevented an inscription inventory count. |
| MFA Boston | Unmeasured | Three searches HTTP 403; browser blank. Five MFA-numbered seals appear at Penn and are counted there once. |
| ASI site museums | Unmeasured | Earlier Lothal category: 133 Seals & Sealing records and one object witness with five signs. Lothal/Kalibangan requests timed out; Dholavira/Rakhigarhi inventories not located in bounded official searches. |
| National Museum of Pakistan, Karachi | Unmeasured | Official description located; focused transfer failed with SSL EOF. No public object-level inventory located by these searches. |

The minima come from [collection-register.json, focused_pass](collection-register.json), [portal candidate counts](portal-candidate-counts.csv) and [the six-catalogue summary](focused-summary.json). Exact URLs, UTC timestamps, HTTP statuses and read counts are in [focused-query-log.csv](focused-query-log.csv), covering 417 direct attempts. Provider/browser observations are separately preserved in local raw web-*.json and browser-attempts.json. Provider text does not expose upstream HTTP status. Failed access supplies an unmeasured count; Allahabad's zero records a completed bounded search.

Institution names here identify catalogue attribution. Physical custody was not independently checked. CISI's 1987 table attributes L-1 and L-45 to the Lothal site museum, while the portal names National Museum, New Delhi; the audit preserves both labels without establishing a transfer. Penn's five originals retain MFA accession numbers and Penn loan numbers. Raw cisi1-concordance-transcription.json records these holder differences.

The portal requires museumId=all. Its own JavaScript exposes the JSON fetch route with searchterm, pageNo, facetFilters and anaglyph. All 156 pages of seven queries were captured: Indus 54, Harappa 216, Harappan 1,972, Mohenjo-daro 238, Mohenjodaro 1,781, Chanhu-daro 20 and Lothal two. Their union has **4,007 recordIdentifier values**. Candidate selection from title/description produced 158 object pages, all HTTP 200. Institution/accession deduplication leaves **154 candidates: 94 confirmed originals, ten plaster copies, 44 unconfirmed inscriptions and six other-script/modern-drawing records**. [Per-term counts](portal-term-counts.csv), [selection code](focused_enumerate.py), [classification code](focused_classify.py); raw portal-enumeration.json and portal-unique-review.json.

New Delhi's descriptions identify 36 seals, 14 sealings, 20 tablets, three inscribed pottery records and three other inscribed objects. The last category includes a lance head, a brick-shaped object and a pictograph-bearing record titled Mountain Goat without an explicit object type. Kolkata's 18 comprise 13 seals and five sealings. Description-based inclusion leaves uncertain records outside the minimum, including questioned inscriptions and an unfinished seal intended to receive script. Ancient copper casting is not classified as a modern reproduction. [Summary by_institution.*.object_types](focused-summary.json); raw review statuses and decision bases.

Met's page=2 route repeated the first 42 results; offset=42 supplied the remaining 34. Pages for 49.40.1–4 and 1984.482 were inspected. Three small photograph witnesses confirm signs where the main text does not explicitly describe script. The seal in 49.40.1 is counted once with its modern impression. [Met search](https://www.metmuseum.org/art/collection/search?q=Indus), [49.40.4](https://www.metmuseum.org/art/collection/search/324065); raw met-offset42.body and met-photo-*.body.

Karachi and several ASI museums have no measured public inscription inventory in this pass. New Delhi's government profile reports over 3,500 Harappan objects on permanent loan in 2018; that historical, mixed-object figure cannot quantify an unindexed inscription group. [Source NM-3500](sources.json). BM's 724 culture objects and Lothal's 133 seal/sealing category records likewise have broader count bases.

## Fields and reuse conditions

| Inspected originals | Records | Accession | Named site | Date/period | Dimensions | Material heading | Bibliography | Excavation/source-assisted key |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| New Delhi | 76 | 76 | 72 | 76 | 57 | 76 | 0 | 60 |
| Kolkata | 18 | 18 | 17 | 12 | 18 | 18 | 0 | 9 |
| BM | 6 | 6 | 6 | 6 | 5 | 6 | 4 | 4 |
| Penn | 5 | 5 | 5 | 5 | 0 | 5 | 5 | 5 |
| Louvre | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 0 |
| Met | 5 | 5 | 0 | 5 | 5 | 5 | 0 | 0 |

[Focused field counts](focused-field-counts.csv) supply the numerators and denominators. The [wider matrix](metadata-field-matrix.csv) retains other collections and dataset schema rows. Bibliography is absent from **101/114 records**, dimensions from **25/114**, date/period from **6/114**, and a named site from **10/114**. Provenance/geography headings are populated in 112 records, including broad Indus Valley values. Louvre AO 9036 qualifies Mohenjo-daro with question marks. Material headings sometimes say Others or Stone. The key column includes compound museum numbers whose excavation component is supported by the crosswalk; it does not count dedicated excavation-number headings.

Image slots are exposed for **105/114 records**. Three Penn originals have no object images; the six BM witnesses have unmeasured image counts. Multiple slots occur in 96 records, with physical view identity unverified. Penn's illustrated originals expose five and six images; each Louvre record exposes two. Met counts are primary-image minima. Portal image URLs were recorded without bulk image downloads. [Fields photographs, multiple_views and image_count_unmeasured](focused-field-counts.csv); raw per-record image_slots.

| Institution | Image terms | Data terms and access |
|---|---|---|
| Met | Five records mark images Public Domain; eligible assets CC0. | Basic eligible collection data CC0; website succeeded, earlier API HTTP 410 retained. |
| Penn | Research, educational and personal use with credit; commercial use excluded from that grant. | Advertised CSV: CC BY 4.0, 144.25 MB, updated 2026-09-30, images excluded; not downloaded. |
| Louvre | Specified private/scientific/educational uses of medium-format photographs; credit and permalink. Print provision includes EU publisher and 1,500-copy limit; other uses require agreement and may incur fees. | Record information Etalab Open Licence 2.0, attribution and update date. Object JSON works. |
| BM | Most Trustee-owned images CC BY-NC-SA 4.0, subject to marked-item/third-party exceptions; policy text returned by provider. | General bulk-data grant unverified. |
| Indian portal, ASI, Karachi | No open reuse licence verified for sampled routes. | No open data grant verified; internal portal fetch provides search access without establishing a redistribution licence. |

The policy sources are [Met Open Access](https://www.metmuseum.org/hubs/open-access), [Penn download](https://collections.penn.museum/collections/objects/data.php) and [image terms](https://www.penn.museum/about/statements-and-policies/terms-and-conditions), [Louvre CGU §§4.1.1.2 and 4.1.2](https://collections.louvre.fr/en/page/cgu), and [BM image policy](https://www.britishmuseum.org/terms-use/copyright-and-permissions/images-and-photography). Exact titles and access states appear in [sources.json](sources.json). Acquired payloads, source rows and unresolved-rights images remain local-only.

## Identifier audit

**80/114** originals carry an excavation-style identifier or usable published-reference key under the protocol. **61/80 (76.25%)** match; the full-frame fraction is **61/114 (53.51%)**. New Delhi matches 46/76, Kolkata 9/18, Penn 5/5 and BM 1/6. Met and Louvre have no confirmed joins in this inspected export. [Summary usable_identifier_records, join_fraction_usable and by_institution](focused-summary.json).

Methods yield **13 exact excavation matches, six normalized matches, 36 published CISI concordance joins, five shared field-and-plate joins and one Marshall composite join**. They identify 61 different object_family_id values and 67 faces. [paired-full-audit.csv](paired-full-audit.csv) retains every comparison. The [30-object sample](paired-sample-audit.csv) contains the first 30 confirmed rows sorted by institution and normalized accession; this convenience sample is selected for explicit identifiers. The 53 unjoined records and matching attempts remain in raw unconfirmed-join-candidates.json.

The reused export contains 5,680 faces and 4,695 provisional families, with usable excavation values on 1,831 Mohenjo-daro faces and 2,652 Harappa faces. Normalization preserves components while folding case, punctuation, spacing and numeric leading zeros. Undelimited concatenations require a published concordance. CISI Volume 1's basic-data tables supply excavation and museum registration numbers: 42 rows were transcribed and visually checked, and 41 occur under their stated CISI reference in this export; H-224 is absent under that exact reference. [Dataset focused_pass_review](dataset-register.json), raw cisi1-concordance-transcription.json; [Joshi and Parpola 1987, pp. 366–372](https://ignca.gov.in/Asi_data/76884.pdf).

BM 1947,0416.4 gives **Hr 5635**. Marshall explicitly pairs **HR 5635 with plate number 345**, explaining all components of the export's **HR 5635345**, record 2478.1, CISI M-1906. The original CSV contains the concatenation; normalize_lipi.py copies it unchanged. The table supports the join, while zero corpus thickness remains a missing-value placeholder. [Museum record](https://www.britishmuseum.org/collection/object/A_1947-0416-4), [Marshall 1931, Volume II, p. 404](https://archive.org/details/in.ernet.dli.2015.62023), raw marshall-table-055.png, audit row 1947,0416.4.

A normalized DKI838 lookup found corpus record 3750.1. The primary CISI table maps NMI 56 / DKI 838 to **M-543**, whose export identifier is **DK1838**. The published registration concordance supplies the accepted pair; the other hit is retained as a rejected collision. No global I/1 conversion is applied. BM Dk7665, VS823 and Hr629 candidates remain unconfirmed because their export strings append unexplained components. [Audit rejected_direct_collision](paired-full-audit.csv); raw paired-comparisons.json, key National Museum, New Delhi|dki-838-56.

Site agrees in 58 confirmed pairs, disagrees in one and is less specific or missing in two. DK5175/143 lists Harappa in the portal versus Mohenjo-daro in CISI M-304 and the export. Four material disagreements concern DK8516/1283 and H-278 (museum terracotta versus corpus steatite), H-225 (copper versus steatite), and DHR2617 (steatite versus terracotta). Eight have uninformative/missing material, two use broader Stone and two use Clay/Terracotta terminology. [Summary comparisons](focused-summary.json); raw paired values keyed by accession.

Object-type labels agree in 49 pairs and differ in terminology in 12, principally sealing versus a tablet code. Dimensions are museum-missing in 20, incomplete for comparison in 27, within tolerance in nine and outside tolerance in five. The five flags are 10376/A7703, DK4807/57, HR5787/106, SRG3017/1256 and SRG5040/1259. Scalar millimetre comparisons require equal measurement coverage and use the larger of 0.5 mm or 5% as tolerance. Sorted axes and different measurement conventions limit interpretation. Explicit single-face sign counts agree in 16, differ in nine and are uncomparable in 36. Photograph and segmentation review is needed for those flags. [Comparison columns](paired-full-audit.csv), [protocol](PROTOCOL.md#comparison-and-sample-amendment-2026-10-07).

## Reused inputs and reviewer checks

The pass reused the [2 October landscape](../../2026-10-02-dataset-landscape/README.md), existing Lipi CSV/export, research/corpus/normalize_lipi.py and the complete CISI Volume 1 scan from source recovery. The earlier attribution of 76884.pdf to Volume 3 was corrected to Volume 1; original wording remains in history. Dataset sizes/version bases are retained with focused annotations for Lipi, CISI and museum portals.

Run the README's offline command. Check all seven portal totals and accession deduplication against raw pages. Sample the 30 selected pairs and DKI838 collision against CISI page images, Penn field/plate references and Marshall p. 404. Reinspect the site, material, dimension and sign-count flags. Repeat blocked searches in a fresh browser and check current image/data policies before reuse. Full inventory totals need successful acquisition and wider inscription review.
