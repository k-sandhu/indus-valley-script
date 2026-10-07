# Is the Indus evidence completely indexed?

No. The census demonstrates gaps in catalogue-identifier matching and metadata in the measured local index, while current inventories and several publication sections remain unexamined. The worldwide number of additional physical objects is unknown. Across 19 CISI 1 site ranges, 327 of 493 identifiers match locally and 166 are absent keys. The reviewed museum frame now has a lower bound of 68 matched records among 114 originals, with 46 unresolved. [coverage.json](coverage.json), `summary`, and [join-summary.json](join-summary.json) contain these results.

The **local corpus** means the pinned Lipi derivative of 5,680 records, whose internal numbering follows the ICIT-derived export. A **face** is one source-defined side or text-bearing view recorded in that export. A **provisional family** groups face rows by local `object_family_id`; physical identity across the whole corpus remains unadjudicated. An **absent key** is a catalogue base identifier with no exact or recorded source-attested alias match among local identifiers. An object could still occur under another identifier or without a catalogue key. The relationship between the local export and current ICIT inventory has not been established.

This is an Exploratory synthesis. The [Sonnet review](REVIEW.md) confirmed 55 of 57 original headline numbers and identified corrections to counting, joins and source locators. V6 applies those corrections and records the post-trim inputs. Its [850 arithmetic checks](main-2026-10-07-v6/checks.json) and [1,093 verification checks](verification-2026-10-07-v6.json) pass; a fresh replay matches all eleven aggregate files. These checks validate computation and pinned bytes. Archaeological assertions retain their source and review status.

## Frame and count bases

The four batches contain 123 rows, joining to 115 site/provenance entities. Recomputed local totals match the saved rows and aggregates:

| Batch | Rows | Faces | Provisional families | Sum of site-level distinct CISI keys |
|---|---:|---:|---:|---:|
| Pakistan/Afghanistan | 37 | 4,837 | 3,908 | 3,637 |
| Gujarat/Kutch/Maharashtra | 25 | 496 | 460 | 199 |
| North India | 25 | 290 | 271 | 232 |
| Finds abroad | 36 | 42 | 42 | 9 |

The 5,665 face mentions include 13 cross-batch repeats: five Nuhato faces and eight faces at six A/D shared sites. Assigning each site entity once gives 5,652 faces and 4,668 families in the site frame. Another 28 faces and 27 families have the label `Unknown`, bringing the complete derivative to 5,680 faces and 4,695 families. These are label-based counts. The source-attested Nuhato/Gharo Bhiro alias and regional attribution are in [register-joins.json](register-joins.json), `site_aliases`; input hashes are in [input-manifest.json](input-manifest.json).

Eight printed catalogue sections have no contributing site row and no local site label: **Maski, Mehi and Shahi-Tump** in CISI 1, one entry each; **Kalako-deray, Lewan-dheri (Dar Dariz), Loebanr, Periano-ghundai and Tarakai Qila** in CISI 2, together 13 entries. B3 reopened both contents pages. [coverage.json](coverage.json), `frame_omissions`, records their prefixes, counts and pages. Maski lies in Karnataka, outside the four regional batch scopes. The 16 catalogue entries require classification and object-level matching before incorporation into an inscription inventory.

| Comparator | Source population and count | Availability for this synthesis |
|---|---|---|
| ICIT, 2023 publication | 4,665 objects, 5,650 texts, 17,966 legible sign occurrences, 16,015 photographs/drawings; 29 tables | Historical abstract totals; current object inventory unavailable. Fuls, CAA 2023 abstract 76, p.281. |
| CISI | Versioned photographic catalogue entries, including related objects | Selected printed ranges and concordances; complete later sections unexamined. |
| Mahadevan 1977 | 2,906 selected inscribed objects from a 3,455-object photographic card catalogue, with 549 exclusions | Printed site table p.6 and selection pp.5?7; current IM77 web inventory unmeasured. |
| Lipi derivative | 5,680 faces and 4,695 provisional families | Full pinned local export, pin `fc8813a52e183d19c441631dc26c33a4dccbea39`. |
| Mayig derivative | 179 Mohenjo-daro faces and 1,003 tokens | Restricted annotation export, pin `ad2f1e218a34b8c33c57de0d6cb8d99272765bbb`. |
| Museum census | 114 selected online original-object records at six institutions | 108 direct records and six British Museum provider records; institutional full inventories unmeasured. |

Bibliography, opened-content scope and exact witnesses are in [sources.json](sources.json). Derivative pins and counts also reuse the [October 2 landscape](../../2026-10-02-dataset-landscape/landscape.json). No current common object inventory links all these totals, so subtraction cannot estimate worldwide omissions.

The corrected regional face totals are 4,837, 491, 290 and 34. The corresponding recovered IM77 named-site totals are 2,596, 175, **117** and **12**. Tarkhanewala Dera is one object on printed p.6; the inherited north-India row and aggregate both used two and summed to 118. V6 retains the inherited value and uses the primary table. The abroad 12 covers Umma, Kish, Susa, Girsu/Tello and Ur; IM77 also has five unknown-provenance West Asian objects, making its historical West Asian subtotal 17. Abroad CISI 1 cells are null with `not_applicable_to_abroad_frame`, rather than object-count zeros. See [region-coverage.csv](region-coverage.csv), `IM77_count_status`, and [coverage.json](coverage.json), `IM77_inherited_count`.

## What the absent catalogue keys contain

| Selected frame | Entries | Matched by identifier | Absent keys | Absent in pottery/graffiti sections | Absent in other sections |
|---|---:|---:|---:|---:|---:|
| Gujarat/Kutch/Maharashtra | 317 | 196 | 121 | 57 | 64 |
| North India | 176 | 131 | 45 | 18 | 27 |
| Combined | 493 | 327 | 166 | **75** | **91** |
| Lothal, within combined frame | 290 | 179 | 111 | 52 | 59 |
| Kalibangan, within combined frame | 122 | 96 | 26 | 10 | 16 |
| Banawali, within combined frame | 37 | 23 | 14 | 6 | 8 |

Thus 66.33% of the 493 identifiers are matched by identifier. The class split follows printed catalogue sections, including Banawali's mixed tablets/graffiti section B24?29. It is a section classification, with individual script eligibility unresolved. [catalogue-section-split.csv](catalogue-section-split.csv) records all 19 sections and recomputed missing-key counts; the review's [detailed section table](review/cisi1-class-split.csv) separates Lothal seals, impressions and tablets. Lothal has 34 absent seal keys and 25 absent impression keys. Kalibangan has 12 absent seal keys; Banawali has eight. Across the whole local corpus the review found no alternative site label carrying any of these 166 keys.

The prior Pakistan comparison read only the first run of each multi-run string. It contained four runs at four sites, rather than the six stated in the original report: 936 entries and 813 matches. V6 reads all runs. The five CISI 1 runs at those four sites contain **1,040 entries, 910 matches and 130 absent keys**. Harappa's H278?382 adds 104 distinct catalogue entries and 97 matches. The interval has 105 printed number slots, but CISI 1 p.375 corrects the H356 caption to H354, a duplicate. Harappa's CISI 2 runs H266?275, H356 and H383?1019 contain **648 entries, 506 matches and 142 absent keys**. Mohenjo-daro's standalone M595 is also parsed. Editions overlap and are reported separately in [catalogue-coverage.csv](catalogue-coverage.csv), `printed_number_slots`, `exclusions` and `prefix_basis`.

Other source-specific gaps include Rehman Dheri's 270 mixed entries, two matching keys and 268 absent keys; and Sarai Khola's ten photographed entries, with no local matches. CISI 2 p.xviii attributes 68 graffiti on potsherds to Halim 1972 and reports partial photographic recovery. CISI 2 p.xv reports 28 Balakot drawings whose objects could not be located for photography. B3 has read these CISI statements and the selected plates; Halim and Dales remain unopened. The [source sample](source-sample-audit.json) retains these scopes. The review also identifies five Daimabad absent entries reported by Sali with signs, alongside two comparative entries among its seven absent keys; [batch-corrections.json](batch-corrections.json) records this attributed finding.

Count attribution matters at Lothal. **Rao 1985 p.305 gives 91 sealings**, as opened by the reviewer; B3 has not opened it. **Frenez and Tosi 2005 give 93 for Rao's finds**, pp.67?68 and 70?71, rather than establishing a new recount. CISI 1 L124?216 contains 93 sealing entries, while IM77 selects 75. Their difference needs an excavation-number crosswalk. Rao is now listed with its actual access status in `sources.json`, `RAO1985`.

Dholavira's mirror places 225 recovered seals and 60 sealings on **p.233**. It gives 194 inscription-analysis seals and 139 positive cases on p.242, and 61 sealings on p.308, with four undated and an inconsistent remaining 59. The reviewer also saw a chart summing to 58, a motif table of 136 against prose 130, and locality/period populations of 204 and 185. Those observations are attributed to the review's page scans; B3 retains the user-upload mirror and has not inspected the original upload rasters. [conflicts.json](conflicts.json), `Dholavira-counts`, keeps each population and locator. Shortughai's 84 and Tepe Yahya's 112 entries are mixed catalogue populations, and Salut's two impressed fragments may belong to one jar.

## Metadata and museum matching

The field audit counts export presence on faces, and museum presence on selected original records. Its [field-completeness.csv](field-completeness.csv) separates measured values, inherited rules, structural schema absences and unmeasured fields.

| Lipi field | Present among 5,680 faces | Percent |
|---|---:|---:|
| Named site | 5,652 | 99.51% |
| Room/grid context | 2,191 | 38.57% |
| Any area/section, block/house or room/grid | 4,376 | 77.04% |
| Period or phase | 3,172 | 55.85% |
| Depth | 2,810 | 49.47% |
| Time/period code | 3,067 | 54.00% |
| At least one positive numeric dimension | 4,441 | 78.19% |
| All three positive dimensions | 1,151 | 20.26% |
| Material term | 4,706 | 82.85% |
| Nonempty `excavation-idno` | 5,147 | 90.62% |
| CISI identifier | 5,019 | 88.36% |
| Numerical calendar attribution in `time` | 0 | 0% |

The excavation field includes 146 hyphen-led strings, some referring to figures or plates. Its presence does not establish 5,147 authenticated excavation numbers. The twelve fixed zeros identified by the review are now `structural_schema_absence`: three Lipi fields for independent dating, photographs and item-rights links, and nine Mayig fields. They have no percentage or measured missing-record count. Upstream assets need their own audit. Mayig's named sites and CISI keys remain measured on 179 faces. Full ICIT, CISI and the IM77 web application have unmeasured field denominators here.

In the museum frame, 114 have accessions and material terms, 108 a date/period label, 68 numerical calendar attributions, 89 dimensions and 13 bibliography fields. Image slots occur on 105 of 108 records with measured image fields; six British Museum fields are unmeasured. Reproducible raw-field counts are **112 nonempty site strings and nine nonempty `excavation_raw` fields**. Earlier counts of 104 adjudicated named sites and 78 source-assisted registration keys are retained as `inherited_rule_not_recomputed`; their exact rules were not reproduced. Exact context, stratum, independent dating and item-level rights remain unmeasured across this museum frame.

The original 61 museum joins were a lower bound. B3 checked the seven proposed additions against saved museum records, printed tables and unique local families: three Lothal records through CISI 1 p.373; two British Museum seals through Marshall 1931 p.402; and two Banawali full excavation strings with CISI 1 p.375 support. One Banawali match explicitly removes the trailing museum component 1145. The result is **68 joined records, 68 families and 74 faces**. British Museum record content comes from the saved provider response; direct access had been blocked. Supplementary pairs remain local in `data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/additional-join-pairs.json`, and [join-summary.json](join-summary.json) records methods and denominators.

The 46 unresolved records comprise **13 failed string matches, two untried usable keys and 31 without a usable key in the original pass**. The last category can still gain a published concordance. The join count remains a lower bound. The earlier one site, four material, five dimension and nine sign-count disagreements apply to the original 61-record comparison sample. Seven new joins have not received its full field adjudication.

## Acquisition, review and preservation

[priority-gaps.json](priority-gaps.json) ranks eight overlapping pools. Current ICIT, complete CISI sections and major holding inventories would establish source denominators. Harappa and Mohenjo-daro supply the largest local context pool, at 4,640 faces and 3,716 families. Rehman Dheri and Lothal have the largest quantified catalogue-key gaps. Comparative regional marks, later Dholavira/Kalibangan/Farmana/Rakhigarhi inventories, unresolved museum registrations and foreign-find contexts need publication tables or permissioned museum, excavation and archive access. Each pool records a route and rights constraint. No request was sent.

A complete index requires an inventory disposition for every nominated source entry, versioned identifiers, object/fragment/surface relations, source-backed context and separate rights for data and image assets. [SCHEMA-AMENDMENTS.md](SCHEMA-AMENDMENTS.md) maps these onto the October 2 design and retains the Proposed 200-object pilot.

The original purposive 20-site audit retains 14 supported and six qualified endpoint-bound verdicts. The review's source-wide re-adjudication gives 18 supported and two qualified. [source-sample-audit.json](source-sample-audit.json) stores both, with corrected Nippur, Karanpura, Banawali, Tepe Yahya, Gonur and Nagwada locators and the Bhagwanpura figure correction. The bibliography now has 21 entries with opening scope, including Rao as unseen by B3, CISI 3.3 as a 40-page excerpt and Dholavira as a user-upload mirror.

The coordinator's two trim scripts replaced source-title prose in five batch files after v5. **Batch B/C/D file-hash manifests predate those edits**, and the review found stale hashes in two batch D verify commands. B3 leaves those packages unchanged. V6 pins the post-trim source bytes. The earlier 17-title audit is historical; widened screening now returns 365 candidates across current, subsidiary and preserved first-pass ledgers, without copying their titles. These are screening candidates, including legitimate bibliography, rather than 365 established prose payloads. The review's 32 residual prose IDs have been checked against the coordinator's removal markers in [source-title-review-v6.json](source-title-review-v6.json).

[batch-corrections.json](batch-corrections.json) passes 53 row/ledger corrections and qualifications to the batch owners, including Chanhu-daro, Pabumath, Daimabad, Chandigarh, Rakhigarhi, Ur and Susa. All original endpoints, the review and its supporting files remain unchanged. `pre-v6-2026-10-07/` preserves the preceding top-level state, and [OUTPUT-MANIFEST.json](OUTPUT-MANIFEST.json) identifies the updated v6 copies.
