# Object-ledger review response

The preserved first selection contains **200 carriers**, but its **74-slot alphabetical fill reached only Eastern Headwaters, Gujarat/Kutch and Harappa**. Lower Indus has 46% of the 4,104 frame carriers and entered that selection through only 18 museum-linked objects; Kalibangan entered zero. The new hash-ordered selection also has 200 carriers, with 44 Lower Indus and ten Kalibangan records. It covers 39 export site labels, compared with 34 originally. Both selections are purposive, and the revised selection follows the observed review, so its status is Exploratory. [Coverage](revision-2026-10-07-v4/coverage-comparison.json), `frame_regions`, `original`, `hash_ordered`.

## Selection and coverage

The original fill visited alphabetically ordered strata and stopped at position 90 among 313 strata. It added 17 Eastern Headwaters, 31 Gujarat/Kutch and 26 Inter-Riverine carriers. The revised fill orders JSON-encoded stratum keys by SHA-256 with seed `object-ledger-review-20261007|`, then uses the original within-bucket object hash. Its 74 additions comprise 27 Inter-Riverine, 26 Lower Indus, eight Gujarat/Kutch, four Eastern Headwaters, four export-labelled Iranian Plateau, two Persian Gulf, two Upper Indus and one South India carrier. The period, tablet, museum and Lothal stages retain their original quotas. [Selection code](revision_selection.py), `seeded_round_robin`, `revised_selection`; [frozen reviewer recount](review/selection-check.json), `fill_last_stratum_position_in_sorted_order`.

| Export region | Frame carriers | Original selection | Hash-ordered selection |
|---|---:|---:|---:|
| Central Asia | 3 | 3 | 3 |
| Eastern Headwaters | 34 | 17 | 4 |
| Gujarat/Kutch | 197 | 78 | 55 |
| Inter-Riverine | 1932 | 69 | 70 |
| Iranian Plateau | 11 | 5 | 8 |
| Lower Indus | 1891 | 18 | 44 |
| Mesopotamia | 11 | 5 | 4 |
| Persian Gulf | 17 | 5 | 9 |
| South India | 2 | 0 | 1 |
| Upper Indus | 6 | 0 | 2 |

The site tables are complete in `coverage-comparison.json`, `sites_export` and `sites_accepted`. After census alias normalization there are 33 and 38 distinct site/area labels, respectively; Girsu and Tello are one site. Luristan and Ornach area are regional/area labels. The frame omits 591 export families without an eligible catalogue base, including 228 Dholavira and eight Kanmer families. The revised sample still reflects the mandatory Harappa and Lothal quotas. [Coverage file](revision-2026-10-07-v4/coverage-comparison.json), `original_fill_audit`, `original_unreached_frame_sites`, `hash_unreached_frame_sites`.

Over all 4,695 export families, area, room/grid and period labels are present on 73.887%, 39.723% and 50.692%. On the original 180 matched carriers these rates are 52.222%, 15.556% and 38.333%; on the revised 180 they are 61.667%, 25.000% and 37.778%. This demonstrates the effect of selection on metadata coverage. [Comparison](review-response-2026-10-07-v3/comparison.json), `full_export_presence`, `endpoints.*.field_presence`.

## External carriers

The original Iranian Plateau quota included one Iranian and four Pakistani carriers by census country. The revised mandatory group takes all four Iranian frame carriers: two Susa, one Tepe Yahya and one Luristan. Its other mandatory groups are six Gulf, five Mesopotamian and three Central Asian carriers. BM-123208 is assigned to Mesopotamia by its Ur excavation. Later fill adds seven other external export carriers, including four Pakistani cross-references; those are shown by country below and retain attributed export-region assertions. The original and revised external totals are 18 and 25. [Coverage](revision-2026-10-07-v4/coverage-comparison.json), `external_carriers`, `external_by_country`, `external_by_site`.

| Country from census | Original | Hash ordered |
|---|---:|---:|
| Afghanistan | 1 | 1 |
| Bahrain | 2 | 3 |
| Iran | 1 | 4 |
| Iraq | 6 | 5 |
| Kuwait | 1 | 1 |
| Oman | 0 | 3 |
| Pakistan | 4 | 4 |
| Turkmenistan | 2 | 2 |
| United Arab Emirates | 1 | 1 |

| Canonical site/area | Original | Hash ordered |
|---|---:|---:|
| Altyn Depe | 1 | 1 |
| Failaka | 1 | 1 |
| Girsu/Tello | 2 | 1 |
| Gonur Depe | 1 | 1 |
| Hajar | 1 | 1 |
| Janabiyah | 1 | 1 |
| Kalba | 1 | 1 |
| Karzakan | 0 | 1 |
| Kish | 1 | 1 |
| Luristan | 1 | 1 |
| Miri Qalat | 1 | 1 |
| Murda Sang | 1 | 1 |
| Nindowari-damb | 1 | 1 |
| Nippur | 1 | 1 |
| Ornach area | 1 | 0 |
| Ras al-Jinz | 0 | 2 |
| Salut | 0 | 1 |
| Shortughai | 1 | 1 |
| Sibri | 0 | 1 |
| Susa | 0 | 2 |
| Tepe Yahya | 0 | 1 |
| Umma | 1 | 0 |
| Ur | 1 | 2 |

Gadd's *Seals of ancient Indian style found at Ur* (C. J. Gadd, 1932, Proceedings of the British Academy 18:191-210), printed13-14/PDF24-25, identifies BM 123208 and U.17649 in Ur tomb-shaft filling. The accepted site and findspot now read Ur. Dilmun is a separately attributed production-place assertion; its independent basis and the export-family match remain review questions. [Primary scan](https://ignca.gov.in/Asi_data/33779.pdf); [corrected register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), `objects[selection_key=BM-123208]`, corresponding context and assertions.

## Identifiers, dimensions and dates

The original 149 accepted excavation strings comprise **126 registrations free of the identified citations/placeholders**, 20 figure/plate-bearing cells and three other leading-hyphen values. Across all source assertions, 42 carriers have explicit figure/plate citations. Forty-two distinct contaminated alias strings occupy 92 repeated alias rows because multiple faces repeat metadata. The revised view separates registrations, lots, bibliography and original export strings. It has zero figure/plate-bearing accepted registration cells or registration aliases. Two prefix-only BNL strings enter specific review questions. [Identifier recount](review-response-2026-10-07-v3/comparison.json), `original_identifier_restated`; each revised `identifier-audit.json` records normalized registrations. The 104-carrier strict unparsed export baseline and newly parsed identifiers are distinct from the original accepted-view count of 126.

After parsing and corrections, accepted registration fields are present on 145 original-selection and 151 revised-selection carriers. Their corpus-derived parsed fields are present on 143 and 149 carriers. These counts include registrations separated from combined export/citation strings; they do not change the original 126 clean-string recount. [Original identifier audit](revision-2026-10-07-v4/corrected-original/identifier-audit.json), [revised identifier audit](revision-2026-10-07-v4/hash-ordered/identifier-audit.json), `accepted_registrations`, `export_registrations`.

H-2218's full export string is `H97-3319Figure 12.11`. Its primary caption restores `H97-3319/8040-13`, with unit8040 and item13 separated. PBM-1 receives PBM024 and dated holder code KC from CISI 1 printed375/PDF411; PMB024 remains a candidate variant. B3-V6-016 records the applied action. A dated holder code describes the catalogue snapshot, without establishing a current institution. [Corrected register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), `export_excavation_identifier`, `excavation_identifier`, `lot_identifier`, `bibliographic_locator`, `correction_overlays[correction_id=B3-V6-016]`.

The museum parser now accepts explicit mm, cm/cms., centimetre/centimeter variants, labelled axes and inches. Inches convert at 25.4mm. Unlabelled arrays remain dimension_1 etc.; labelled height/width/thickness/diameter preserve their stated axes. It adds fifteen measurement assertions from seven previously skipped records in the corrected original selection. H-221's 0.8x1.8cms. becomes 8 and 18mm, giving **130 dimension-bearing carriers against 127**, a gain of **three**. [Parser](revision_builder.py), `dimensions`; [completeness](revision-2026-10-07-v4/corrected-original/completeness.json), `field=measurement`.

The 22 tablets retain the caption's late Period 3B label and receive the full approximate 3B interval, **2450-2200 BCE**. The late qualifier supplies no narrower interval. The export's 2600-1900 BCE conversion remains a historical source assertion. Accepted labels and intervals now share the HARP periodization scheme. H-1688's queue cites the source introduction's Mound E street-deposit attribution at about 2600 BC, printed liii; that page was reused from the reviewer check. [Period table](../2026-10-06-chronology-region/main-2026-10-07-v1/period_mapping.json), `label=Period 3B`; [register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), tablet `calendar_interval`, `periodization_scheme`.

## Lothal evidence, completeness and review

CISI 1 printed375 corrects L-141's two views to A(1)/A(2) and places L-174 among tags with several impressions. Printed279 shows two square impressions on L-174. The accepted count is now two for each, with the Table1 count one retained. L-141's caption-to-impression interpretation needs expert confirmation. The opened plates are printed272/PDF308 and 279/PDF315. The L-173 to L-175 eligibility questions use the catalogue's geometric-design classification; L-173's page attribution is inherited from the reviewer. [Register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), the two `impression_count` cells and their assertion references; [review queue](revision-2026-10-07-v4/corrected-original/review-queue.json), `catalogue_only`, `impression_count_conflict`. Joshi and Parpola are recorded as CISI editors.

The following field counts use the same 180 matched carriers within each selection. Presence means a nonplaceholder, noncandidate attributed assertion. Dates are period or museum attributions; no object-associated dating sample was recovered.

| Field | Original corpus | Corrected original | Revised corpus | Revised ledger |
|---|---:|---:|---:|---:|
| museum_accession | 0 | 26 | 0 | 25 |
| material | 137 | 144 | 143 | 149 |
| area | 94 | 94 | 111 | 111 |
| room_grid | 28 | 28 | 45 | 45 |
| period_label | 69 | 69 | 68 | 68 |
| calendar_interval | 0 | 62 | 0 | 57 |
| excavation_unit | 0 | 22 | 0 | 22 |
| excavation_item | 0 | 22 | 0 | 22 |
| measurement | 127 | 130 | 128 | 130 |
| dating_sample | 0 | 0 | 0 | 0 |

The corrected original register contains 6,991 assertions, 445 measurements and 259 source-record surfaces/transcriptions. The revised register has 7,004 assertions, 449 measurements and 262 source-record surfaces/transcriptions. Surface identities preserve annotation boundaries; their physical face alignment remains open. All nulls have reasons. Non-Lothal-table impression/context/contact fields now say not applicable, and derived source-class/region assertions have a derived confidence level. [Summaries](revision-2026-10-07-v4/corrected-original/summary.json), [revised summary](revision-2026-10-07-v4/hash-ordered/summary.json); [missingness counts](review-response-2026-10-07-v3/comparison.json), `endpoints.*.null_reasons`.

Twenty-one catalogue pointers now give individual plate pages in each selection. The remaining 27 corrected-original and 26 revised pointers still locate only the sealing section. Full Finnish Concordance/holder/photo-source columns, the other selected Lothal caption conventions and current holdings behind KRS/RGR catalogue codes remain incomplete. These tasks are recorded in [sources.json](sources.json), `review_response.remaining_source_tasks`.

There are 51 confirmed operational relationships and 34 candidate edges on the corrected original selection; the revised selection has 50 and 15. Confirmed museum objects number 26 and 25. Both retain21 inherited museum adjudications, including two material, two dimension-tolerance and two inscription-count disagreements; additional unadjudicated pairs number five and four. Distinct attributed values remain grouped by field in each `disagreements.json`; they include compatible source scopes as well as disagreements. [Original joins](revision-2026-10-07-v4/corrected-original/join-report.json), [revised joins](revision-2026-10-07-v4/hash-ordered/join-report.json), `confirmed_relationships`, `candidate_relationships`, `museum_field_adjudications`.

Lookup counts are recomputed from assertion locators after normalization: **1,064**, mean 5.32, and **1,044**, mean 5.22. Excluding rights-rule rows and selection attribution gives **841**, mean 4.205, and **821**, mean 4.105. Both medians then equal three. This counts distinct input-record lookups per carrier, without a timed human cost. Six relevant primary pages supplied corrections; the access log records nine inspected page images including initial navigation checks. `new_image_inspections=4` in the summaries counts the four CISI page images. The queues have156 questions on 85 carriers and 138 on 81. [Summaries](revision-2026-10-07-v4/corrected-original/summary.json), [revised summary](revision-2026-10-07-v4/hash-ordered/summary.json), `source_lookup_cost`, `source_lookup_cost_without_rights_and_selection`; [access log](../../data/raw/2026-10-07-object-ledger/review-response-2026-10-07/source-access-log.json).

## Validation, rights and Helsinki import

The strengthened validator catches **26/26 reviewer mutations** and **17/17 sequence fixtures**. It checks source-record existence, cell/row assertion equality, reference ownership, units, mass, finite quantities, broad plausibility limits, Harappa label/interval compatibility and date-source attribution. The disclosure guard scans JSON, JSONL, CSV and Markdown, including one- and two-sign forms. It is a heuristic: ordinary accession, page, aggregate-count and family numerals receive explicit metadata/context exclusions, so a source-content review remains necessary. The final whole-package scan covered 225 files and left eight alerts in the unchanged reviewer's own page/count-run summary. Those describe bibliographic and completeness counts, and are manually classified as metadata. The revised endpoint directory has zero alerts. [Mutation results](verification-2026-10-07-v3/mutations.json), `caught`, `total`; [final fixture repeat](sequence-guard-review-response-2026-10-07-v2.json), `files`; [directory scan](validation-review-response-2026-10-07-v2.json), `errors`; [full scan and classification](full-directory-sequence-review-2026-10-07-v1.json), `flags`, `manual_classification`.

The Lothal chapter's Zenodo record states CC BY4.0, as verified in the supplied reviewer source check; the online notice was not reopened here. The L-174 chapter-image rights record carries that licence, while CISI plate assets retain their separate unresolved rights. No copied images, descriptions or transcription payloads are in the revised metadata layers. The file name describes these exclusions; Lipi metadata is retained under the private research policy, with public reuse unresolved. [Sources](sources.json), `review_response`; [ledger rights](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), `source_id=lothal2005`; [author deposit](https://zenodo.org/records/5514283).

Package M supplies 11,369 occurrences, including 944 unresolved numbers and 65 letter-suffixed occurrences. With no historical crosswalk, **zero are accepted and all 11,369 quarantined**. Synthetic tests accept suffixes, expand reviewed occurrence mappings, round-trip Package M crosswalk fields and create a surface on a catalogue-only carrier. No synthetic identity enters either register. CISI 1 printed365/PDF401 identifies its Finnish Concordance column; its relationship to the 1979 edition requires verification. [Interface results](verification-2026-10-07-v3/helsinki-interface.json), `number_counts`, `real_accepted`, `real_quarantined`; [interface specification](HELSINKI-INTERFACE.md).

All164 pre-response endpoint/review files retain their hashes. The original 158 checks pass through the protocol-prefix replay wrapper. Twenty-three revised selection/result files replay byte for byte, with replay copies only in raw. Direct source-value checks compare3,335 original-selection and 3,408 revised-selection assertions without a mismatch; other transformations remain outside that resolver's scope. [Preservation](verification-2026-10-07-v3/preservation.json), [replay](review-response-2026-10-07-v3/replay-comparison.json), [assertion audit](review-response-2026-10-07-v3/assertion-values.json), `endpoints.*.counts`.
