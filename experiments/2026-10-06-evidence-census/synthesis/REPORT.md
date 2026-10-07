# Is the Indus evidence completely indexed?

No. The available registers do not establish a complete worldwide index, and the measured local indexes omit catalogue entries and substantial contextual metadata. The worldwide number of additional physical objects remains unknown. Within 19 inspected CISI 1 site ranges in Gujarat and north India, **327 of 493 catalogue identifiers match the local corpus and 166 do not**: 66.33% represented and 33.67% absent by identifier. The museum census contains **114 original-object records, 61 confirmed identifier joins and 53 unjoined records**. These are bounded measures of catalogue and identity coverage. Their units and overlapping populations prevent adding them into a worldwide missing-object estimate. See [coverage.json](coverage.json), `summary`, and [join-summary.json](join-summary.json).

The synthesis is Exploratory. The final arithmetic endpoint is Verified computation, with 728 passing checks. The source sample checks selected assertions at 20 sites, five per batch: 14 supported and six qualified. It supplies no population error-rate estimate and has not received the separate review requested for this work package. The [protocol](PROTOCOL.md), [sample audit](source-sample-audit.json) and [final checks](main-2026-10-07-v5/checks.json) preserve these scopes.

## What was joined and counted

The four active batches contain 123 rows. Explicit aliases and seven shared site entities reduce the joined frame to **115 site or provenance entities**. The frame includes regional labels and uncertain inscription classifications; it is a census selection, not an enumeration of all archaeological sites. Recomputed batch totals are:

| Batch | Rows | Local faces | Provisional object families | Sum of site-level distinct CISI identifiers |
|---|---:|---:|---:|---:|
| Pakistan/Afghanistan | 37 | 4,837 | 3,908 | 3,637 |
| Gujarat/Kutch/Maharashtra | 25 | 496 | 460 | 199 |
| North India | 25 | 290 | 271 | 232 |
| Finds abroad | 36 | 42 | 42 | 9 |

Every figure was recomputed from the site rows and checked against the saved batch aggregate. The pooled 5,665 face mentions contain 13 repeats: five from Nuhato's cross-batch coverage and eight from six Pakistan/Afghanistan sites also mentioned by the abroad batch. Assigning those entities once gives **5,652 represented local faces and 4,668 provisional families**. Another **28 faces and 27 families** carry the local label `Unknown`. The complete pinned Lipi derivative therefore has **5,680 faces and 4,695 families**. Family labels remain provisional physical identities. Exact rows, regional attribution and input hashes are in [coverage.json](coverage.json), `batch_recomputation`, `regions` and `sites`, and [input-manifest.json](input-manifest.json).

Nuhato and Gharo Bhiro are an explicit alias in CISI 2, p. xv. The 2018 Nuhato report, pp. 41–42, distinguishes the 1973 seal from a second seal recovered in 2018. Batch A could not open that report; batch B did. Five Pakistani cross-references and Shortughai also overlap A and D. Their observations are retained, with A supplying the regional attribution. Dilmun and Ur remain separate candidate provenance/identity cases: a local Dilmun-labelled accession is reported as found at Ur. [conflicts.json](conflicts.json), `Nuhato-overlap`, `Pakistan-cross-references` and `Foreign-find-denominator`, gives the source locators.

The register join contains 17 publication records, 32 publication-to-batch source links, 15 dataset source links and 37 collection source links. Shared URLs identify a source, while site names in titles supply candidate links. Neither operation merges physical objects. The 61 museum joins were replayed against pinned original museum records, all paired local faces and the saved concordances: 36 published CISI concordances, 13 exact excavation numbers, six normalized excavation numbers, five shared field/plate references and one published Marshall composite. They cover 61 local families and 67 faces. The candidate records remain separate under the local raw directory. See [register-joins.json](register-joins.json) and [join-summary.json](join-summary.json), `methods` and `status`.

## Coverage depends on the inventory

| Index or publication | Count and population | What this synthesis can measure |
|---|---|---|
| ICIT, published 2023 | 4,665 inscribed objects; 5,650 texts; 17,966 legible sign occurrences; 16,015 photos/drawings | Historical published totals. Current object-level inventory and field denominators unavailable. Fuls, CAA 2023 abstract 76, p. 281, opened saved PDF. |
| CISI | Edition- and site-specific catalogue entries, including comparison objects | Selected contiguous runs and local identifier membership. Full edition reconciliation remains incomplete. |
| Mahadevan 1977 | 2,906 selected inscribed objects from 3,455 photographed objects, with 549 exclusions | Printed selection and site counts, not present-day coverage of the IM77 web application. Introduction pp. 5–7; site table p. 6. |
| Lipi pinned derivative | 5,680 faces; 4,695 provisional families | All local face fields and source identifiers measured. Pin `fc8813a52e183d19c441631dc26c33a4dccbea39`. |
| Mayig pinned derivative | 179 faces and 1,003 tokens, all labelled Mohenjo-daro | A restricted source frame, not an additional 179 independent objects. Pin `ad2f1e218a34b8c33c57de0d6cb8d99272765bbb`. |
| Online museum census | 114 original-object records at six institutions | A selected online frame, not complete institutional holdings. Includes 108 direct records and six British Museum provider records. |

The sources and exact editions are in [sources.json](sources.json), `ICIT2023`, `IM77`, `CISI1`, `CISI2` and `CISI33`; derivative counts and pins are in [coverage.json](coverage.json), `index_counts`, and the [October 2 landscape](../../2026-10-02-dataset-landscape/landscape.json). ICIT objects, Lipi families and published catalogue entries have different inclusion rules. Their totals cannot supply a worldwide recall fraction through subtraction.

The corrected regional face totals are 4,837 for Pakistan/Afghanistan, 491 for Gujarat/Kutch/Maharashtra, 290 for north India and 34 for the abroad frame. Available IM77 main-table counts cover seven, five and seven sites in the first three regions, respectively, summing to 2,596, 175 and 118 selected objects. No abroad subtotal was reconstructed; its zero in `IM77_sites_with_count` denotes lack of a recovered count. [region-coverage.csv](region-coverage.csv) retains the denominator and scope.

The most useful catalogue comparison is confined to the 19 CISI 1 ranges with explicitly recorded endpoints in batches B and C:

| Frame | Catalogue entries | Matching local base identifiers | Absent local base identifiers |
|---|---:|---:|---:|
| Gujarat/Kutch/Maharashtra: ten ranges | 317 | 196 | 121 |
| North India: nine ranges | 176 | 131 | 45 |
| Combined | **493** | **327** | **166** |
| Lothal, within that combined frame | 290 | 179 | 111 |
| Kalibangan, within that combined frame | 122 | 96 | 26 |
| Banawali, within that combined frame | 37 | 23 | 14 |

The absent keys are already indexed in the printed catalogue. Their disposition in the local transcription export is unresolved: some may represent excluded non-text objects, aliases or source selection. Catalogue classes include geometric and indeterminate specimens. Exact range membership resolves an earlier comparison problem at Kalibangan: its 197 local CISI identifiers span later numbering, while 96 fall within K1–122. [catalogue-coverage.csv](catalogue-coverage.csv) supplies all 19 ranges and the separate selected A ranges. A's six selected CISI 1 ranges contain 936 entries, of which 813 match after the Amri/Ai concordance; they are not the whole Pakistan catalogue. Later ranges overlap earlier editions and remain separate.

Larger source-specific pools include **Rehman Dheri's 270 mixed entries, with two matching local keys and 268 absent keys**, and **Sarai Khola's ten photographed entries, with no local keys**. CISI 2 p. xviii attributes 68 marked Sarai Khola sherds to Halim 1972; only ten were photographically recovered for that catalogue. The 58-object difference concerns this historical photographic selection. CISI 2 p. xv records 28 published Balakot drawings whose objects were not located for photography. Those original excavation articles were not opened in B3. The [sample audit](source-sample-audit.json), rows `Rehman Dheri`, `Sarai Khola` and `Balakot`, distinguishes inspected plates from cited earlier reports.

Source disagreements also prevent simple inventory subtraction. Lothal has 91 sealings in the earlier report and 93 in Frenez and Tosi's 2005 reanalysis, pp. 67–68; IM77's 75 selected sealings and CISI 1's 290 entries use other populations. Dholavira's saved report mirror gives 225 recovered seals, 194 analysed seals and 139 inscription-positive seals, with 60–61 sealings in conflicting sections. Original Dholavira page rasters remain unverified. Shortughai's 84 and Tepe Yahya's 112 CISI 3.3 entries cover mixed classes and scripts. Salut's seal and two impressed fragments imply two to three carriers, depending on whether the fragments belong to one jar. These bases and locators are preserved in [conflicts.json](conflicts.json).

## How much metadata is present?

The field audit measures export presence, using face records for Lipi and original-object records for museums. Positive dimensions exclude zero placeholders. A room/grid field supplies a findspot proxy; a cultural-period code supplies a period attribution. Calendar attribution and linkage to an independently dated sample have separate fields. The complete definitions and numerators are in [field-completeness.csv](field-completeness.csv), `basis`, `measurement` and `evidence`.

| Field in the Lipi derivative | Present / 5,680 faces | Percent |
|---|---:|---:|
| Named site | 5,652 | 99.51% |
| Room/grid findspot proxy | 2,191 | 38.57% |
| Period or phase | 3,172 | 55.85% |
| Depth | 2,810 | 49.47% |
| Time/period code | 3,067 | 54.00% |
| At least one positive dimension | 4,441 | 78.19% |
| All three positive dimensions | 1,151 | 20.26% |
| Material | 4,706 | 82.85% |
| Excavation/registration `idno` | 5,147 | 90.62% |
| CISI row identifier | 5,019 | 88.36% |
| Numerical calendar attribution | 0 | 0% |
| Independent dating-observation link | 0 | 0% |
| Photograph link in the normalized row | 0 | 0% |
| Item-level rights link in the normalized row | 0 | 0% |

The last four measures describe fields in the derivative. Upstream images, dating evidence and source-level licences require separate review. Mayig's 179 normalized faces have named sites and CISI keys; the remaining nominated context, measurement, image and item-rights fields are absent from that derivative. ICIT, full CISI editions and the IM77 web application have unmeasured field denominators here. Published feature descriptions establish availability without establishing a completeness percentage.

Across the 114 selected museum records, all 114 have accessions and material descriptions; 104 have named sites, 108 a date/period label, 68 an explicit numerical calendar attribution, 89 dimensions, 78 excavation/source-assisted registration keys and 13 bibliography fields. There are **105 image slots among 108 records whose image fields were measured**; three Penn records lack slots and six British Museum image fields remain unmeasured. Slots have not all been inspected as photographs. Exact excavation contexts, stratum, independent dating and item-level rights completeness were not adjudicated across this museum frame. The inherited summary's 80 usable keys includes two other references outside the 78-key registration field. [field-completeness.csv](field-completeness.csv) preserves each institution's denominator.

Identifier agreement does not resolve the content of every field. The 61 joined museum records include one site disagreement, four material disagreements, five dimension comparisons outside the earlier audit's tolerance and nine numerical sign-count disagreements. Surface scope and measurement conventions remain possible causes. See [join-summary.json](join-summary.json), `comparisons`, and the local paired records; these disagreements require object/view review.

## Where further evidence would come from

[priority-gaps.json](priority-gaps.json) ranks eight overlapping pools by documented scale, contextual evidence and acquisition route. The largest unmeasured task is obtaining a current ICIT inventory, complete CISI sections and object-level holding inventories for major collections. This would establish source denominators and dispositions. The largest measured context pool is Harappa plus Mohenjo-daro: **4,640 local faces and 3,716 provisional families**, from `coverage.json.sites`. Publication tables, HARP reports and field-register archives could add find units, dated assemblages and registration concordances.

Rehman Dheri and Lothal have the largest quantified local catalogue-key gaps, at 268 and 111. Rangpur's 222 broadly marked sherds, Karanpura's 157 graffiti instances, Sarai Khola's 68 reported sherds, Balakot's 28 drawings and Bhagwanpura's 21 marked tablets/sherds offer comparative classifications and phase context. The exact source pages are attached to rank 5; their units and mark classes vary. Later Dholavira, Kalibangan, Farmana and Rakhigarhi inventories need catalogue cutoffs and registration joins. The 53 unjoined museum records need concordances. Smaller foreign-find pools can add unusually specific contexts, such as Nippur's registered floor-context seal and Gonur's room/area find.

The routes are full publications first, then permissioned museum, excavator or archive requests where the record remains missing. No request was sent. Raw scans, extracted rows, paired objects and page images stay local. Reading access and database access have separate redistribution terms; museum data policies also have different scopes from image policies. Each ranked pool carries its rights constraint. The complete index would need a versioned site authority, source inventory, disposition for every catalogue row, accepted and candidate identifier assertions, object/fragment/surface distinctions, source-backed metadata and rights records for every asset. [SCHEMA-AMENDMENTS.md](SCHEMA-AMENDMENTS.md) maps those requirements onto the October 2 specification and proposes a 200-object pilot.

## Source checks and editorial repairs

The 20-site selection was recorded before its source outcomes. B3 inspected 31 PDF pages and three Dholavira mirror passages through the reusable page extractor, plus the Nuhato report's pp. 41–42 for the overlap conflict. The six qualified sample outcomes concern an unopened underlying article, a mirror rather than page raster, an endpoint rather than every catalogue entry, or mixed object classes. Exact source hashes, PDF page numbers and tested assertions are in [sources.json](sources.json) and [source-sample-audit.json](source-sample-audit.json). B3 made no live web searches or new downloads; saved witnesses resolved the named conflicts. Prior failed search/download routes remain linked in `sources.json.search_and_access_log`.

The title-length audit flags **17 records in five batch files**. Inspection classifies 13 as prose/snippet payloads, including one copied record appearing twice, and four as extended bookseller/review metadata. These titles were not copied into B3 outputs. [source-title-audit.json](source-title-audit.json) and [source-title-review.json](source-title-review.json) identify records for the coordinator to trim in:

- `sites-deep/a-pakistan-afghanistan/sources.json`
- `sites-deep/a-pakistan-afghanistan/revision-west-upper-sources.json`
- `sites-deep/b-gujarat-kutch-maharashtra/sources.json`
- `sites-deep/c-north-india/sources.json`
- `sites-deep/d-finds-abroad/sources.json`

The remaining completeness uncertainty is concentrated in current inventories, inaccessible full catalogues, publication cutoffs, unjoined registrations, comparative-object eligibility and metadata still present only in books or archives. A defensible completeness statement would name the acquired editions and account for every row in those editions. This synthesis supplies selected denominators and a route to that inventory; it cannot bound material that has not been enumerated.
