# Field definitions

## Shared notes

Outer schemas are fixed; nested JSON retains optional reader fields and ambiguity. Null means unrecorded or unmeasured under the stated frame; zero is a measured outcome. Portable source labels identify original parent witnesses that are excluded. URLs are access pointers, rather than payload licences. Edition codes, printed occurrences, catalogue entries, face records and provisional families have separate namespaces and denominators. Chart and benchmark readings were AI-assisted and await expert certification.

Table `status` values are `Exploratory` and `Frozen evaluation`. Arithmetic validation uses `Verified computation`; the baseline criterion outcome is `Failed`. Mixed chart/benchmark components retain CC BY 4.0 for edition content and CC0 1.0 for project additions. Census/metrology compilations and documentation use CC0 1.0.

## chart_reference

| Field | Arrow type | Definition |
|---|---|---|
| `cell_id` | `string` | Stable chart coordinate key, using one-based PDF page and zero-based chart column/row. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `column` | `int64` | Zero-based chart column; a printed layout coordinate. |
| `row` | `int64` | Zero-based chart row; a printed layout coordinate. |
| `rank` | `int64` | Preferred upper printed rank label; repeated ranks do not identify unique drawings. |
| `code` | `int64` | Preferred lower printed graphic code. It is an inventory label, with no assigned sound or meaning. |
| `alternatives` | `list<element: int64>` | Other retained readings of the lower numeric label. Empty means no additional label candidate was retained. |
| `rank_alternatives` | `list<element: int64>` | Other retained upper-label readings. |
| `numeric_confidence` | `string` | Qualitative AI label-reading judgment inherited from the reference; it is not a calibrated probability. |
| `previous_rank` | `int64` | Original upper class when changed, otherwise null. |
| `previous_code` | `int64` | Original chart code when changed, otherwise null. |
| `previous_alternatives` | `list<element: int64>` | Original lower-code alternatives when changed; an empty list differs from null. |
| `previous_rank_alternatives` | `list<element: int64>` | Original upper-class alternatives when changed, otherwise null. |
| `previous_numeric_confidence` | `string` | Original qualitative confidence when changed, otherwise null. |
| `changed_fields` | `list<element: string>` | Names of changed numeric fields relative to the original reference. |
| `change_note` | `string` | Short old-to-new numeric change description; null when unchanged. |
| `dashed_auxiliary` | `bool` | Whether the chart cell was annotated as a dashed auxiliary drawing; null preserves an unrecorded judgment. |
| `source_crop_pdf_points` | `list<element: double>` | Chart crop [left, top, right, bottom] in PDF points. |
| `image_path` | `string` | Logical PNG name; image_assets gives storage. Extract embedded images with code/extract_images.py. |
| `annotation_method` | `string` | Authored description of how numeric chart labels were read. |
| `reference_version` | `string` | Reviewed chart numeric-reference version; 2.1 in this release. |
| `source_url` | `string` | Official source or licence attribution URL. |
| `source_pdf_sha256` | `string` | SHA256 of the unchanged acquired 1979 PDF, which is not bundled. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |
| `image` | `struct<bytes: binary, path: string>` | Embedded PNG, exposed as a datasets Image feature. |

## benchmark_rows_v1

| Field | Arrow type | Definition |
|---|---|---|
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `occurrence_key` | `string` | Pipeline locator for a printed occurrence; it does not establish a physical-object identity. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `section` | `string` | number_order, end_sorted or beginning_sorted section of the edition. |
| `context_image_path` | `string` | Logical context PNG name corresponding to context_image. |
| `exact_image_path` | `string` | Logical target-box PNG name, null in v1. |
| `locator_json` | `string` | JSON object with sample coordinates, crop hashes and selection fields. See the nested-field notes below. |
| `reference_json` | `string` | Frozen reference JSON with portable source pointers. |
| `prediction_json` | `string` | Frozen chart-only prediction JSON with ranked alternatives and unit-level confidence. |
| `reference_chart_correction_flags_json` | `string` | Per-reference-unit flags from the chart impact: corrected cells, field changes, candidate-identity warnings and locator conflict. |
| `prediction_chart_correction_flags_json` | `string` | Per-predicted-unit flags for alternatives whose template_key points to a changed chart cell. |
| `reference_kind` | `string` | Initial disjoint AI reading in v1 or adjudication following two AI readings in v2. |
| `original_ocr_locator_exposed` | `bool` | Whether v1 locator metadata contained OCR strings before the blinding correction; false in v2. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |
| `context_image` | `struct<bytes: binary, path: string>` | Embedded wider-context PNG, exposed as a datasets Image feature. |

## benchmark_rows_v2

| Field | Arrow type | Definition |
|---|---|---|
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `occurrence_key` | `string` | Pipeline locator for a printed occurrence; it does not establish a physical-object identity. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `section` | `string` | number_order, end_sorted or beginning_sorted section of the edition. |
| `context_image_path` | `string` | Logical context PNG name corresponding to context_image. |
| `exact_image_path` | `string` | Logical target-box PNG name, null in v1. |
| `locator_json` | `string` | JSON object with sample coordinates, crop hashes and selection fields. See the nested-field notes below. |
| `reference_json` | `string` | Frozen reference JSON with portable source pointers. |
| `prediction_json` | `string` | Frozen chart-only prediction JSON with ranked alternatives and unit-level confidence. |
| `reference_chart_correction_flags_json` | `string` | Per-reference-unit flags from the chart impact: corrected cells, field changes, candidate-identity warnings and locator conflict. |
| `prediction_chart_correction_flags_json` | `string` | Per-predicted-unit flags for alternatives whose template_key points to a changed chart cell. |
| `reference_kind` | `string` | Initial disjoint AI reading in v1 or adjudication following two AI readings in v2. |
| `original_ocr_locator_exposed` | `bool` | Whether v1 locator metadata contained OCR strings before the blinding correction; false in v2. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |
| `context_image` | `struct<bytes: binary, path: string>` | Embedded wider-context PNG, exposed as a datasets Image feature. |
| `exact_image` | `struct<bytes: binary, path: string>` | Embedded proposed target-box PNG in v2/v3, exposed as a datasets Image feature. |

## benchmark_rows_v3

| Field | Arrow type | Definition |
|---|---|---|
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `occurrence_key` | `string` | Pipeline locator for a printed occurrence; it does not establish a physical-object identity. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `section` | `string` | number_order, end_sorted or beginning_sorted section of the edition. |
| `context_image_path` | `string` | Logical context PNG name corresponding to context_image. |
| `exact_image_path` | `string` | Logical target-box PNG name, null in v1. |
| `locator_json` | `string` | JSON object with sample coordinates, crop hashes and selection fields. See the nested-field notes below. |
| `reference_json` | `string` | Frozen reference JSON with portable source pointers. |
| `prediction_json` | `string` | Frozen chart-only prediction JSON with ranked alternatives and unit-level confidence. |
| `reference_chart_correction_flags_json` | `string` | Per-reference-unit flags from the chart impact: corrected cells, field changes, candidate-identity warnings and locator conflict. |
| `prediction_chart_correction_flags_json` | `string` | Per-predicted-unit flags for alternatives whose template_key points to a changed chart cell. |
| `reference_kind` | `string` | Initial disjoint AI reading in v1 or adjudication following two AI readings in v2. |
| `original_ocr_locator_exposed` | `bool` | Whether v1 locator metadata contained OCR strings before the blinding correction; false in v2. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |
| `context_image` | `struct<bytes: binary, path: string>` | Embedded wider-context PNG, exposed as a datasets Image feature. |
| `exact_image` | `struct<bytes: binary, path: string>` | Embedded proposed target-box PNG in v2/v3, exposed as a datasets Image feature. |

## benchmark_readings

| Field | Arrow type | Definition |
|---|---|---|
| `benchmark` | `string` | v1 or v2 benchmark identifier. |
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `reader` | `string` | A, B or C research-role label. |
| `kind` | `string` | primary, convenience_repeat, independent or adjudicated reading. Repeats were fixed convenience selections. |
| `reading_json` | `string` | Original returned reading JSON with portable source pointers. |
| `chart_correction_flags_json` | `string` | Per-unit chart-change flags for this reading, separate from the frozen reading JSON. |
| `source_file` | `string` | Portable original reader/card witness label. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## benchmark_readings_v3

| Field | Arrow type | Definition |
|---|---|---|
| `benchmark` | `string` | v1 or v2 benchmark identifier. |
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `reader` | `string` | A, B or C research-role label. |
| `kind` | `string` | primary, convenience_repeat, independent or adjudicated reading. Repeats were fixed convenience selections. |
| `reading_json` | `string` | Original returned reading JSON with portable source pointers. |
| `chart_correction_flags_json` | `string` | Per-unit chart-change flags for this reading, separate from the frozen reading JSON. |
| `source_file` | `string` | Portable original reader/card witness label. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## benchmark_chart_cards

| Field | Arrow type | Definition |
|---|---|---|
| `benchmark` | `string` | v1 or v2 benchmark identifier. |
| `card_id` | `string` | Original chart-card sheet stem; sheet sequence is not a train/test split. |
| `image_path` | `string` | Logical PNG name; image_assets gives storage. Extract embedded images with code/extract_images.py. |
| `source_file` | `string` | Portable original reader/card witness label. |

## benchmark_count_pages

| Field | Arrow type | Definition |
|---|---|---|
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `frame` | `string` | random or stress source-count page frame. |
| `image_paths` | `list<element: string>` | List of licensed count-page PNGs relative to the dataset root. |
| `reference_json` | `string` | Frozen reference JSON with portable source pointers. |
| `detections_json` | `string` | JSON list containing only row_anchor_y_2x and margin_xyxy_2x, the geometry used for row-recall matching. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## benchmark_count_readings

| Field | Arrow type | Definition |
|---|---|---|
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `reader` | `string` | A, B or C research-role label. |
| `reading_json` | `string` | Original returned reading JSON with portable source pointers. |
| `source_file` | `string` | Portable original reader/card witness label. |

## benchmark_count_pages_v3

| Field | Arrow type | Definition |
|---|---|---|
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `frame` | `string` | random or stress source-count page frame. |
| `image_paths` | `list<element: string>` | List of licensed count-page PNGs relative to the dataset root. |
| `reference_json` | `string` | Frozen reference JSON with portable source pointers. |
| `detections_json` | `string` | JSON list containing only row_anchor_y_2x and margin_xyxy_2x, the geometry used for row-recall matching. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## benchmark_count_readings_v3

| Field | Arrow type | Definition |
|---|---|---|
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `reader` | `string` | A, B or C research-role label. |
| `reading_json` | `string` | Original returned reading JSON with portable source pointers. |
| `source_file` | `string` | Portable original reader/card witness label. |

## evidence_sites

| Field | Arrow type | Definition |
|---|---|---|
| `site` | `string` | Site or provenance entity label reconciled by synthesis v6. An entity can denote a provenance group. |
| `assigned_region` | `string` | Census work-batch region, not a claim of an ancient administrative division. |
| `local_faces` | `int64` | Aggregate face-record count in the pinned local export. |
| `local_families` | `int64` | Aggregate provisional object-family count in the pinned local export. |
| `local_cisi_identifiers` | `int64` | Count of distinct local CISI identifiers for this site/provenance entity. |
| `IM77_main_selected_objects` | `int64` | Count in Mahadevan 1977 printed p.6, under that edition’s selection rules. Null is unmeasured or unlisted. |
| `IM77_count_status` | `string` | Whether the IM77 value comes from the printed table or the entity is not listed there. |
| `ICIT_object_count` | `int64` | Site-level ICIT count if established; retained null when unmeasured. |
| `worldwide_missing_objects` | `int64` | Retained null: the census did not establish a worldwide object denominator. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## evidence_publications

| Field | Arrow type | Definition |
|---|---|---|
| `publication_id` | `string` | Stable identifier in the authored publication register. |
| `title` | `string` | Exact bibliographic source title as recorded; title trimming is retained in source metadata. |
| `authors_editors` | `string` | Named publication authors or editors in the source register. |
| `year` | `int64` | Publication year; string or null in the heterogeneous source bibliography. |
| `venue` | `string` | Publisher, journal, series or institutional venue as recorded. |
| `url` | `string` | Source access URL, not a grant of rights to its payload. |
| `access_record` | `string` | Inherited record of opening/search scope. The packaging run did not reopen every archaeological source. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## evidence_collections

| Field | Arrow type | Definition |
|---|---|---|
| `institution` | `string` | Museum or collection institution label. |
| `region` | `string` | Register’s modern regional grouping. |
| `confirmed_record_minimum` | `int64` | Minimum original inscription-confirmed records in a bounded query. Null is unmeasured; zero is a query outcome. |
| `count_basis` | `string` | Authored definition of the reported count and its source/time frame. |
| `record_fields_json` | `string` | JSON of field-availability assessments for an institution; these are assessments, not copied object records. |
| `source_ids` | `list<element: string>` | IDs in the collections source register, prefixed collections: in evidence_sources. |
| `query_date` | `string` | Recorded date of the bounded collection query. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## evidence_datasets

| Field | Arrow type | Definition |
|---|---|---|
| `name` | `string` | Dataset-register name. |
| `size_json` | `string` | JSON of historical aggregate size measures and units; missing size remains null inside JSON. |
| `count_basis` | `string` | Authored definition of the reported count and its source/time frame. |
| `reported_reuse_terms` | `string` | Recorded licence or unresolved-rights assessment of the external dataset; that dataset is not included here. |
| `version_basis` | `string` | Recorded version/time scope of the external dataset observation. |
| `source_ids` | `list<element: string>` | IDs in the collections source register, prefixed collections: in evidence_sources. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## evidence_catalogue_coverage

| Field | Arrow type | Definition |
|---|---|---|
| `site` | `string` | Site or provenance entity label reconciled by synthesis v6. An entity can denote a provenance group. |
| `batch` | `string` | Contributing site-census batch. |
| `edition` | `string` | CISI1/CISI2 source edition identifier, including the inherited CISI1-1987 spelling. |
| `prefix` | `string` | Printed catalogue identifier prefix. |
| `first` | `int64` | First number of the inspected catalogue run. |
| `last` | `int64` | Last number of the inspected catalogue run. |
| `pages` | `string` | Printed catalogue page/range locator. |
| `input_pointer` | `string` | Parent register pointer used by synthesis v6. |
| `matching_prefix` | `string` | Local comparison prefix, including documented aliases. |
| `prefix_basis` | `string` | Authored evidence for prefix correspondence. |
| `printed_number_slots` | `int64` | Number slots before named duplicate-caption exclusions. |
| `exclusions` | `string` | JSON text listing source-number exclusions, including the H356 caption correction where relevant. |
| `catalogue_entries` | `int64` | Catalogue base keys in the defined run after exclusions. |
| `local_matching_entries` | `int64` | Exact or recorded-alias catalogue keys found in the pinned local export. |
| `local_absent_entry_keys` | `int64` | Keys absent under the matching rules; their objects may exist under other identifiers. |
| `fraction` | `double` | local_matching_entries divided by catalogue_entries. |
| `scope` | `string` | Authored definition of the count frame and its limitations. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## evidence_catalogue_sections

| Field | Arrow type | Definition |
|---|---|---|
| `site` | `string` | Site or provenance entity label reconciled by synthesis v6. An entity can denote a provenance group. |
| `range` | `string` | Inspected printed CISI 1 identifier range; retained as source-table text. |
| `entries` | `string` | Catalogue entries in the inspected range; retained as source-table numeric text. |
| `matching_keys` | `string` | Catalogue keys matched to the local export; retained as source-table numeric text. |
| `absent_keys` | `string` | Catalogue keys absent under the comparison rule; retained as source-table numeric text. |
| `absent_graffiti_or_pottery_sections` | `string` | Absent keys in the pottery/graffiti section frame; retained as source-table numeric text. |
| `absent_seal_impression_tablet_other_sections` | `string` | Absent keys in the other carrier sections; retained as source-table numeric text. |
| `printed_pages` | `string` | Printed-page locators supporting the section split. |
| `classification_basis` | `string` | Authored rule assigning catalogue keys to section frames; a section does not establish an object’s linguistic status. |
| `evidence` | `string` | Parent file/field citation for the aggregate observation. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## evidence_field_completeness

| Field | Arrow type | Definition |
|---|---|---|
| `index` | `string` | Dataset, museum or schema frame being assessed. |
| `unit` | `string` | Unit counted, such as face records or museum records. |
| `denominator` | `int64` | Count in the stated measurement frame; null where no measured denominator exists. |
| `field` | `string` | Metadata field being assessed. |
| `present` | `int64` | Count with field presence under basis; null for unmeasured/schema assessments. |
| `missing` | `int64` | Count without field presence under basis; null for unmeasured/schema assessments. |
| `percent` | `double` | 100 times present/denominator where measured; structural absence does not receive a measured percentage. |
| `measurement` | `string` | Measured export presence, inherited rule, structural schema absence or other stated measurement class. |
| `basis` | `string` | Exact authored operational presence rule or source-frame qualification. |
| `evidence` | `string` | Parent file/field citation for the aggregate observation. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## evidence_museum_joins

| Field | Arrow type | Definition |
|---|---|---|
| `institution` | `string` | Museum or collection institution label. |
| `museum_record_id` | `string` | Published museum catalogue identifier. |
| `museum_accession` | `string` | Published accession string; formatting is preserved. |
| `museum_url` | `string` | Published museum object page, if recorded or recoverable from its identifier. |
| `cisi` | `string` | Published CISI key in one of the 49 independently cited joins; placeholder values are null. |
| `join_method` | `string` | Authored identifier/concordance method supporting the join. |
| `shared_identifier` | `string` | Public excavation/plate identifier used to support the join; null when only the supplement evidence is retained. |
| `join_evidence` | `string` | Authored source/page/identifier observation supporting the join. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |
| `identifier_sources_json` | `string` | JSON mapping each identifier field to its museum URL or printed catalogue citation. |

## evidence_sources

| Field | Arrow type | Definition |
|---|---|---|
| `source_id` | `string` | Namespaced bibliography ID: synthesis: or collections:. |
| `title` | `string` | Exact bibliographic source title as recorded; title trimming is retained in source metadata. |
| `authors` | `string` | JSON string containing the recorded author list/string. |
| `year` | `string` | Publication year; string or null in the heterogeneous source bibliography. |
| `venue` | `string` | Publisher, journal, series or institutional venue as recorded. |
| `url` | `string` | Source access URL, not a grant of rights to its payload. |
| `access_record` | `string` | Inherited record of opening/search scope. The packaging run did not reopen every archaeological source. |
| `opened_by_packager` | `bool` | False for archaeological sources inherited from census registers; consult access_record for the contributing package’s scope. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |

## weight_mass_bands

| Field | Arrow type | Definition |
|---|---|---|
| `group` | `string` | Dholavira mass band in grams: below-1.3, 1.3-to-5, 5-to-100 or above-100. |
| `n` | `int64` | Number of weights in the stated band. |
| `unit_g` | `double` | Hypothesized common base mass under the public method description, grams. |
| `signal_cv_percent` | `double` | Fitted relative signal variation expressed as a percentage. |
| `signal_probability` | `double` | Fitted signal-mixture probability; not a probability of an archaeological interpretation. |
| `within_3_percent_n` | `int64` | Weights within the method’s 3% proximity rule. |
| `unit_ci95_low_g` | `double` | Lower endpoint of the fitted-unit bootstrap interval, grams. |
| `unit_ci95_high_g` | `double` | Upper endpoint of the fitted-unit bootstrap interval, grams. |
| `method_path` | `string` | Relative public method link in docs/METHODS.md. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## weight_chance_controls

| Field | Arrow type | Definition |
|---|---|---|
| `frame` | `string` | Legacy or canonical metrological reference/multiplier rule in docs/METHODS.md. |
| `draws` | `int64` | Number of simulated comparison draws. |
| `observed_geometric_n` | `int64` | Observed matches under the method’s geometric rule. |
| `observed_close_n` | `int64` | Observed matches under the method’s close rule. |
| `geometric_mean` | `double` | Mean geometric-rule matches in the simulated comparison. |
| `close_mean` | `double` | Mean close-rule matches in the simulated comparison. |
| `geometric_simulation_interval95` | `string` | JSON text giving the central 95% simulation interval for geometric matches. |
| `close_simulation_interval95` | `string` | JSON text giving the central 95% simulation interval for close matches. |
| `fraction_ge_observed_geometric` | `double` | Fraction of simulated draws with at least the observed geometric match count. |
| `fraction_ge_observed_close` | `double` | Fraction of simulated draws with at least the observed close match count. |
| `null_model` | `string` | Randomization rule: jitter-0.15, jitter-0.35 or site-log-uniform. |
| `method_path` | `string` | Relative public method link in docs/METHODS.md. |
| `source_locator` | `string` | Portable source label with exact row/field pointer. |
| `status` | `string` | Exploratory or Frozen evaluation; see shared notes. |

## image_assets

| Field | Arrow type | Definition |
|---|---|---|
| `image_path` | `string` | Logical PNG name; image_assets gives storage. Extract embedded images with code/extract_images.py. |
| `component` | `string` | Configuration or image component served by this PNG. |
| `role` | `string` | chart_cell, row_context, exact_proposal_crop, chart_card or page_count_context. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `source_path` | `string` | Portable original parent-image witness label. |
| `sha256` | `string` | SHA256 of the staged PNG bytes. |
| `bytes` | `int64` | PNG byte count. |
| `storage` | `string` | embedded or loose_png; each PNG is stored once. |
| `license` | `string` | Source image licence, CC BY 4.0. |
| `source_url` | `string` | Official source or licence attribution URL. |

## Nested benchmark fields

References contain sample_index, printed_inscription_id, classification_literal, crop_correct, drawn_unit_count and ordered units. A unit's strict_candidate_codes combines drawing, underline and vertical-position evidence; shape_only_candidate_codes is a broader diagnostic set. Empty strict sets are unresolved. Damage/hatching is a modern editorial drawing unit with unknown ancient sign extent. valid_printed_target=false is scored as a false detection in v2/v3.

Prediction units contain confidence in [0, 1] and ranked alternatives, each with codes. Original template order, costs and confidence reproduce alignment/calibration. v2/v3 section supplies stratified bootstrap membership. Classifications preserve five positions, including spaces. serialization records visual ordering; confidence and template scores describe model output.

Locator coordinates ending _2x use two pixels per PDF point; _pdf_box/_pdf_points use PDF points. Original crop filenames are locator observations; outer logical paths and image columns locate assets. Count references give columns, extents, counts and centers. Recall greedily matches nearest eligible centers within nine PDF points; continuation lines do not add numbered occurrences. V3 numbered recall uses the numbered anchor, while physical-line recall uses glyph-box centers and includes continuations. Per-unit correction flags never change frozen codes: corrected_cell identifies a linked changed record; candidate_identity_review flags possible unlocated identities; locator_conflict retains conflicting witnesses. Reader metadata retains process disclosures, and the v1 overlay is separate from frozen scoring.
