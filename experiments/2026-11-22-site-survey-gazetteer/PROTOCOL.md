# Protocol: Reconciled Indus site and survey-effort gazetteer

Date frozen: 22 November 2026. Scope: deterministic reconciliation of local site, town, excavation, prospection, and survey-effort registers held in this repository. This protocol is fixed before running `code/build_gazetteer.py` and defines the data units, reconciliation rules, conflict retention policy, excavation and survey-effort classifications, and independent verification checks.

## 1. Objective and input registers

We build a single versioned gazetteer (`gazetteer-v1.json` and `gazetteer-v1.csv`), an explicit alias and homonym table (`aliases-v1.csv`), a survey-effort and prospection-window register (`survey-effort-v1.json`), and a coverage summary (`coverage-v1.json`). No new fieldwork, satellite classification, or external scraping is performed. Every record traces back to one or more of the following held local inputs:

1. `experiments/2026-10-26-indus-living-atlas/mapping/run-v2/atlas-data.json`: 115 place entities (112 located points and 3 unlocated labels) and 18 living-town or abandoned-city continuity records.
2. `experiments/2026-10-26-indus-living-atlas/living-towns/towns.json`: full structured metadata for the 18 living-town and comparison cases.
3. `experiments/2026-10-24-q1032-town-axis-register/run-v5/town-axis-table.json`: 34 candidate Harappan towns with competing coordinate candidates, architectural line counts, dated-part assertions, and radiocarbon assertion counts.
4. `experiments/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/coverage.json` and `experiments/2026-10-06-evidence-census/sites-and-publications/site-register.json`: 115 reconciled provenance entities with local corpus counts (Lipi faces, provisional object families, IM77 counts, and CISI coverage) and 89 site-register rows (88 named entities plus `Unknown`).
5. `experiments/2026-10-21-post-catalogue-finds/sites.csv` and `objects.csv`: 26 site rows (21 post-catalogue sites with main inscribed finds plus 5 baseline or uncertain-only sites, excluding the summary total row `All sites`), adding 2 excavated or reported find localities absent from the 115-place atlas (`Dhalewan` and `Indiranagar (Kanpur)`).
6. `experiments/2026-10-11-settlement-prospection/candidates-v5.json` and `sources-v6.json`: 21 editorial prospection windows (`P01` through `P21`) and 72 source observations covering regional surveys, named non-corpus sites, and remote-sensing mound proposals.
7. `experiments/2026-10-12-satellite-prospection/exports-v2/atlas-data-v2.json`, `reconnaissance-register.csv`, `blocks-v1.json`, and `blocks-v2.json`, together with held spatial concordance files under `data/raw/2026-10-12-satellite-prospection/` (MAHSA API query responses, Orengo et al. 2020 study-area polygon, and Singh et al. 2017 derived sediment core coordinates) and the held local witness `data/raw/2026-10-11-settlement-prospection/RAJESH2025.pages.json` for Kotada in Lodrani.

## 2. Four distinct analytical units

Paper 005 (*The Indus excavation gap: what repeat surveys reveal and how to test hidden settlement landscapes*) requires four archaeological units to remain separate. Conflating them distorts site counts, excavation percentages, and settlement areas. The gazetteer enforces this separation structurally:

1. `recorded_locality`: A named place entry in a catalogue, archaeological inventory, excavation report, or continuity register. One recorded locality can span multiple physical mounds (for example, the 13 mapped mounds of Masudpur recorded under one legacy coordinate) or represent a modern town overlapping an ancient site. Regional provenance labels that do not name a bounded settlement (`Dilmun`, `Luristan`) are tagged explicitly with `unit_class = "regional_provenance_label"` so they are never counted as discrete settlements.
2. `physical_mound_or_scatter`: A discrete topographic mound, artifact scatter, fortified enclosure, quarry, cemetery, cave, or unverified remote-sensing landform cluster. Documented sub-site physical features (such as Valamio Timbo at Shikarpur, the 100 by 60 metre fortified enclosure at Kotada in Lodrani, the 13 mapped mounds at Masudpur, or the twin mounds at Mitathal) are stored in each locality's `physical_units` array. Unverified remote-sensing proposals (`B01-T0115`, `B04-T0180`, `B04-T0257`, `Khundowala`, `Mulhiawala`) enter the gazetteer with `unit_class = "physical_mound_or_scatter"` so they remain separate from ground-confirmed localities.
3. `phase_footprint`: The occupied area or chronological envelope attributed to a specific cultural phase or measurement definition. Area estimates that use different physical definitions are never merged into an average or error bar. For example, Ganweriwala preserves three distinct footprint assertions (81.5 ha legacy estimate, 66.7 ha December 2015 surface cultural-material spread, and circa 33 ha 2020 visible mounded area), and Kotada in Lodrani preserves its 0.6 ha fortified enclosure separately from its unmeasured broader multi-period settlement. Phase spans from the atlas, Q-1032 dated-part register, and living-town review are stored in `phase_footprints` with their source and chronological scope.
4. `excavated_deposit`: A documented excavation campaign, trial trench, salvage cutting, borehole, or stratigraphic exposure. Having one excavated deposit places a locality in an excavated category without implying that its entire surviving area was opened. For example, Shortughai records 993 square metres opened out of 2.5 hectares, Dholavira records 13 seasons between 1989 and 2005, and Lakhanjo-daro records four 2017 trenches cut through modern industrial disturbance. All documented campaigns and deposit observations are stored in `excavated_deposits`.

## 3. Domain roles

Because the combined inputs serve four different research functions, every gazetteer entry carries a `domain_role` field so downstream analyses can filter cleanly:

- `indus_or_contact_inscribed_locality`: 115 entities from the Evidence Census and Living Atlas (including South Asian Indus localities and contact-zone findspots in Mesopotamia, Iran, the Persian Gulf, and Central Asia) plus 2 post-catalogue inscribed-find localities (`Dhalewan` and `Indiranagar (Kanpur)`).
- `indus_prospection_or_survey_locality`: 8 documented South Asian Indus or regional survey localities held in the settlement and satellite prospection registers that lack entries in the inscription-focused 115-place atlas (`Padta Bet`, `Dwajagadh`, `Kotada (Lodrani)`, `Ghazi Shah`, `Lakhapar`, `Bahola`, `Kaj`, `Kanjetar`).
- `living_town_continuity_reference`: 14 modern-town continuity comparison cases from `living-towns/towns.json` that do not overlap an existing Indus atlas locality (`Peshawar`, `Multan`, `Taxila`, `Varanasi`, `Ujjain`, `Mathura`, `Patna / Pataliputra`, `Rajgir / Rajagriha`, `Srinagar and Burzahom`, `Vadnagar`, `Lumbini`, `Tilaurakot / Kapilavastu`, `Anuradhapura`, `Mahasthangarh / Mahasthan`). The 4 overlapping living-town records (`Harappa`, `Rupnagar / Ropar`, `Dholavira`, `Mohenjo-daro`) merge directly onto their canonical Indus localities.
- `remote_sensing_proposal`: 5 unverified remote-sensing mound clusters (`B01-T0115`, `B04-T0180`, `B04-T0257`, `Khundowala`, `Mulhiawala`).

## 4. Reconciliation, aliases, and homonym disambiguation

1. Canonical identifiers use lowercase ASCII slugs matching existing Living Atlas IDs wherever possible. Cross-register records join through an explicit deterministic mapping table defined in code and exported verbatim in `aliases-v1.csv`.
2. Mandatory cross-register reconciliations resolved explicitly include:
   - `Kotada (Lodrani)` with `Morodharo`, `Kotda`, and `Lodrani` (Rajesh et al. 2025, `R19`).
   - `Gola Dhoro (Bagasra)` with `Bagasra`, `Gola Dhoro`, `Bagasara`, and Q-1032 town slug `gola-dhoro`.
   - `Ropar (Rupar)` with `Rupar`, `Ropar`, `Rupnagar`, living-town record `LT-11` (`Rupnagar / Ropar`), and post-catalogue code `RPR`.
   - `Chanhu-daro` with `Chanhujo-daro`, `Chanhudaro`, and `Chanhu Daro`.
   - `Lakhanjo-daro` with `Lakhan-jo-daro`, `Lakhian-Jo-Daro`, `Lakhian jo Daro`, `Lakheen-Jo-Daro`, and contextual locality alias `Sukkur` (noting that Sukkur is the modern industrial municipality containing Lakhanjo-daro, not a synonym for the ancient boundary).
   - `Desalpar` with `Desalpur`, `Desalpar-Gunthli`, `Gunthli`, `Dlp`, and Q-1032 town slug `desalpur`.
   - `Tarkhanewala Dera` with `Tarkhanewala-dera`, `Tarkhanawala Dera`, and `Chak 86`.
   - `Nuhato` with `Gharo Bhiro` and `Garho Bhiro`.
   - `Shikarpur` with local mound name `Valamio Timbo` (`Valmio Timbo`).
   - `Rakhigarhi` with `Rakigarhi`, `Rakhigadhi`, `Rakhi Shahpur`, `Rakhi-Shahpur`, and `Rakhi-Khas`.
   - All alternate spellings, diacritic forms, catalogue codes, and site-register variants across all 144 records.
3. Each row in `aliases-v1.csv` carries an `alias_relation` (`canonical_name`, `spelling_variant`, `local_mound_name`, `rediscovery_name`, `catalogue_code`, `modern_municipality_context`, `subsite_mound_name`, `ambiguous_toponym`) and a boolean `ambiguous_homonym`.
4. Homonyms are never collapsed automatically. In particular, `Kotada` is a widespread Kutchi toponym for a fortified mound that appears on Dholavira (Khadir Island), Kotada in Lodrani (Bela Bet), and Kotada Bhadli (Kachchh Mainland). All occurrences of `Kotada` carry `ambiguous_homonym = true` with an explicit `disambiguation_note` requiring island or village context before matching.

## 5. Coordinate precision, attribution, and conflict preservation

1. Silent averaging is prohibited. Every distinct coordinate assertion from every input register is retained in `coordinate_assertions` with `lat`, `lon`, `datum` (`WGS84` or `unspecified`), `precision_class`, `source_register`, `source_citation`, `evidence_status`, and `selection_role` (`primary_retained`, `competing_retained`, `superseded_retained`, `excluded_retained`).
2. Precision classes follow a seven-value controlled vocabulary:
   - `surveyed_sub_100m`: published GPS, total-station, or arcsecond survey coordinate tied directly to the archaeological feature (for example, Kotada in Lodrani in Rajesh et al. 2025, Juna Khatiya and Padta Bet 2019 survey table, or DOAM sub-arcsecond points).
   - `image_located_site`: architectural enclosure or mound identified directly on satellite imagery in Q-1032 (`observed-image-location`) or satellite prospection (`B01-T0115`, `B04-T0180`, `B04-T0257`).
   - `catalogued_arcsecond`: site coordinate in the atlas or Q-1032 reported to arcsecond or roughly four-decimal-degree precision without direct imagery confirmation.
   - `catalogued_arcminute`: coordinate rounded to one arcminute (roughly 1.5 to 2 km) or two decimal degrees.
   - `approximate_regional_5km`: living-town index pin with stated 5 km regional precision in `living-towns/towns.json`.
   - `gazetteer_unquantified`: inherited gazetteer or approximate coordinate whose precision is unstated in its source.
   - `unlocated`: no coordinate in held local sources (`Wattoowala`, `Luristan`, `Dilmun`, `Dhalewan`, `Indiranagar (Kanpur)`, `Lakhapar`, `Bahola`, `Kaj`, `Kanjetar`, `Khundowala`, `Mulhiawala`).
3. Primary coordinate selection follows a transparent hierarchy while retaining every alternative:
   - First, an `observed-image-location` verified on exposed architecture or mound features in Q-1032 (such as the corrected Surkotada citadel at `23.6113, 70.9174` or Sutkagen-dor enclosure at `25.4985, 61.9503`), or an explicitly verified primary field-survey coordinate (such as Kotada in Lodrani `23.913770, 70.650247` or DOAM government reference `28.598889, 71.150000` for Ganweriwala).
   - Second, where Q-1032 has an imagery-confirmed mound point that repairs a coarse gazetteer point (notably Banawali, where Q-1032 locates the protected 6 ha mound at `29.5984, 75.3923` whereas the atlas inherited a Getty TGN point 13.9 km away at `29.516, 75.5`), we retain the imagery-confirmed point as `primary_retained` and preserve the earlier atlas coordinate as `competing_retained` with an explicit conflict record.
   - Third, where Q-1032 retained an unverified Wikipedia or Wikidata village point that diverges sharply from an excavation-report or Uesugi site coordinate (such as Rojdi, Desalpar, Kunal, and Gola Dhoro's excluded Bagasara town point), we retain the archaeological site coordinate as `primary_retained` and keep the competing or excluded Q-1032 points explicitly flagged in `coordinate_assertions`.
   - Fourth, for all other Atlas sites, the current Living Atlas coordinate is retained as `primary_retained`.
4. Conflict quantification: for every locality with two or more coordinate assertions, we compute the exact WGS84 Haversine distance between every pair of assertions and record `max_coord_spread_km` (across all retained assertions, including excluded town locators) and `active_coord_spread_km` (excluding assertions explicitly marked `excluded_retained`, such as Bagasara town in Amreli district for Gola Dhoro). We assign `coord_conflict_tier`:
   - `documented_unquantified_conflict`: inherited source warning documents a major unresolved locator conflict even where only one coordinate point is held numerically (`Nindowari`, roughly 78 km conflict; `Tell Abraq`, possible Tarut Island mis-locator).
   - `material_conflict_ge_1km`: `max_coord_spread_km >= 1.0` km.
   - `minor_offset_0.1_to_1km`: `0.1 <= max_coord_spread_km < 1.0` km.
   - `consistent_lt_0.1km`: multiple assertions within 0.1 km of each other.
   - `single_assertion`: exactly one coordinate assertion held.
   - `unlocated`: zero coordinate assertions held.

## 6. Excavation status and living-town overlap

Every record receives one primary `excavation_status` from a fixed five-value vocabulary:

1. `remote_proposal_unverified`: remote-sensing mound cluster without documented field ground-truthing or excavation.
2. `buried_under_living_town`: archaeological settlement or urban continuity locus predominantly covered by an active modern city, town, village, fort, or industrial estate where archaeological observation is limited to bounded urban or salvage cuttings or remains unexcavated (`Lakhanjo-daro`, `Rakhigarhi`, `Chandigarh`, `Manda`, `Peshawar`, `Multan`, `Varanasi`, `Mathura`, `Patna / Pataliputra`, `Vadnagar`, `Srinagar and Burzahom`).
3. `excavated`: documented excavation, systematic trenching, or trial pits on an accessible archaeological mound, settlement, or cemetery not predominantly buried under a living town.
4. `surface_surveyed`: documented field survey, exploration, or surface collection with no excavation or trial trenching recorded in our held sources.
5. `unknown`: no fieldwork record in held sources, or provenance known only from a museum or catalogue publication without a site-level excavation or survey record.

To avoid hiding real nuance behind a single label, every record also carries two orthogonal fields: `has_excavation_record` (boolean, true whenever any excavation, trial trench, or urban salvage cutting is documented, including under living towns such as Rakhigarhi, Lakhanjo-daro, Chandigarh, Manda, Peshawar, Varanasi, Mathura, Patna, and Vadnagar) and `living_town_overlap` (`predominantly_buried_under_living_town`, `partial_modern_overlap`, `nearby_distinct_settlement`, `none`, `unknown`). Under this scheme, Harappa and Ropar (Rupar) remain `excavation_status = "excavated"` with `living_town_overlap = "partial_modern_overlap"`, preserving both their extensive open-reserve excavations and Kenoyer's observation that roughly one quarter of Harappa lies beneath the modern town.

## 7. Survey-effort layer

To separate "no recorded site" from "unsurveyed", `survey-effort-v1.json` maintains:

1. A catalogue of documented survey and field-research campaigns held in our sources (Mughal 1974 to 1977 Cholistan; Orengo et al. 2020 Cholistan satellite detection; Petrie et al. TwoRains and Land, Water and Settlement in Haryana and Punjab; Green et al. 2019 historical-map field checks; Garcia-Molsosa et al. 2023 Harappa and Punjab map and PAS reconciliation; HARP 1986 to present at Harappa; Bisht and ASI Kutch and Dholavira 1989 to 2005; University of Kerala, KSKV Kachchh, MSU Baroda, NoGAP, and GIAP Kutch and Bela Bet projects; MAHSA all-period heritage database and our local API probe responses; Singh et al. 2017 and 2021 Ghaggar-Hakra coring; Giosan et al. 2012 fluvial landscape; Conesa et al. 2014 North Gujarat SAR; MAFI French Mission in Sindh, Balochistan, and Kirthar piedmont; French Archaeological Mission in Makran; Biagi surveys of Rohri Hills, Siranda, and Lower Sindh; Dales 1962 Makran coast; Gujarat and Saurashtra estuarine and coastal studies by Farooqui, Das, Gupta, and Vedpathak; Sindh Directorate of Antiquities Sukkur urban rescue; and the October 2026 four-block satellite reconnaissance `B01` through `B04`).
2. Per-window survey-effort profiles for all 21 prospection windows (`P01` through `P21`), recording:
   - Window bounding box (`bbox_lonlat`), evidence class, and `I`, `P`, and `F` levels inherited from `candidates-v5.json`.
   - Documented prior survey campaigns overlapping the window.
   - Gazetteer localities falling inside the editorial bounding box (counted separately by `unit_class` and `excavation_status`, using primary retained coordinates).
   - Held spatial concordance assets overlapping the window (Orengo AOI polygon overlap, Singh et al. 2017 sediment cores, satellite prospection blocks `B01` through `B04`, and MAHSA held API query hits).
   - `survey_effort_class`: `intensive_ground_survey`, `targeted_excavation_and_local_survey`, `historical_map_and_remote_screening`, `reconnaissance_or_geomorphic_only`, or `undocumented_or_unacquired_survey_archive`.
   - `absence_interpretation`: explicit statement of whether low recorded site counts reflect true negative ground checks, unacquired survey archives, or surface concealment beneath alluvium, dunes, urban fabric, or altered coasts.
3. Per-locality `survey_effort_tags` and `prospection_window_ids` attached directly to every record in `gazetteer-v1.json` and `gazetteer-v1.csv`.

## 8. Redistribution and storage boundaries

Tracked files in `experiments/2026-11-22-site-survey-gazetteer/` contain only our own code, documentation, factual coordinate and bibliographic summaries, and CC0-safe derived tables. Raw excerpts extracted from local-only third-party witnesses (MAHSA JSON hits, Orengo AOI polygon vertices, Singh core tables, and Rajesh 2025 page extracts) are written exclusively to `data/raw/2026-11-22-site-survey-gazetteer/raw-concordance-extract-v1.json` (physical path `D:\projects\indus_valley_script\data\raw\2026-11-22-site-survey-gazetteer\raw-concordance-extract-v1.json`), with SHA-256 digests recorded in `coverage-v1.json` and `DATA-UPDATE.md`.

## 9. Independent verification criteria

`code/verify.py` will run independently after `code/build_gazetteer.py` and write `verification-v1.json`. It must verify:

1. Deterministic hash reproducibility of all upstream inputs and generated outputs.
2. Zero entity loss across all reconciled inputs (all 115 Atlas and Evidence Census entities, all 34 Q-1032 towns, all 18 Living Towns, all 26 Post-Catalogue site rows, all 8 additional prospection localities, and all 5 remote-sensing proposals accounted for).
3. Zero silent coordinate averaging (every `primary_retained` coordinate equals one of the verbatim retained `coordinate_assertions`, and every pairwise Haversine spread matches an independent recomputation within 0.001 km).
4. Strict separation of the four analytical units (`unit_class` valid, remote proposals never labelled `recorded_locality` or `excavated`, Ganweriwala and Kotada area definitions kept separate).
5. Alias integrity (every mandatory cross-register alias resolves to the expected canonical ID, zero unflagged non-homonym collisions across distinct canonical IDs, and `Kotada` explicitly flagged as an ambiguous homonym).
6. Survey-effort completeness (all 21 prospection windows `P01` through `P21` present, bounding-box containment recomputed independently, every locality tagged with survey-effort metadata).
7. CSV and JSON row-count and field parity across `gazetteer-v1.json`, `gazetteer-v1.csv`, `aliases-v1.csv`, and `coverage-v1.json`.
8. Redistribution hygiene (no raw third-party page text or full MAHSA tile payloads inside tracked files).
