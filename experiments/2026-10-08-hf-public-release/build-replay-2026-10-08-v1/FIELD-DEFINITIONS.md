# Field definitions

PNG paths are relative to the dataset root. Null means unmeasured or unrecorded unless a field definition supplies a narrower meaning. JSON columns are UTF-8 JSON strings; decode them with `json.loads`. Numeric inventory codes follow the 1979 chart and must not be conflated with Wells, ICIT or Mahadevan code namespaces.

## chart_reference

| Field | Arrow type | Definition |
|---|---|---|
| `cell_id` | `string` | Stable chart coordinate key, using one-based PDF page and zero-based chart column/row. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `column` | `int64` | Zero-based chart column; a printed layout coordinate. |
| `row` | `int64` | Zero-based chart row; a printed layout coordinate. |
| `rank` | `int64` | Preferred upper printed rank label; repeated ranks do not identify unique drawings. |
| `code` | `int64` | Preferred lower printed graphic code. It is an inventory label, with no assigned sound or meaning. |
| `alternatives` | `list<item: int64>` | Other retained readings of the lower numeric label. Empty means no additional label candidate was retained. |
| `rank_alternatives` | `list<item: int64>` | Other retained upper-label readings. |
| `numeric_confidence` | `string` | Qualitative AI label-reading judgment inherited from the reference; it is not a calibrated probability. |
| `dashed_auxiliary` | `bool` | Whether the chart cell was annotated as a dashed auxiliary drawing; null preserves an unrecorded judgment. |
| `source_crop_pdf_points` | `list<item: double>` | Chart crop [left, top, right, bottom] in PDF points. |
| `image_path` | `string` | PNG path relative to the dataset root. Use snapshot_download to obtain image files. |
| `annotation_method` | `string` | Authored description of how numeric chart labels were read. |
| `source_url` | `string` | Official source or licence attribution URL. |
| `source_pdf_sha256` | `string` | SHA256 of the unchanged acquired 1979 PDF, which is not bundled. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## benchmark_rows_v1

| Field | Arrow type | Definition |
|---|---|---|
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `occurrence_key` | `string` | Pipeline locator for a printed occurrence; it does not establish a physical-object identity. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `section` | `string` | number_order, end_sorted or beginning_sorted section of the edition. |
| `context_image_path` | `string` | Relative PNG showing the selected row with wider printed context. |
| `exact_image_path` | `string` | Relative PNG of the frozen proposed glyph box in v2. Null for v1, whose box is recorded in locator_json. |
| `locator_json` | `string` | JSON object with sample coordinates, crop hashes and selection fields. See the nested-field notes below. |
| `reference_json` | `string` | Lossless JSON of the original scoring reference. See the nested-field notes below. |
| `prediction_json` | `string` | Lossless JSON of the frozen chart-only row prediction. It includes ranked templates and graphic-code candidate sets. |
| `reference_kind` | `string` | Initial disjoint AI reading in v1 or adjudication following two AI readings in v2. |
| `original_ocr_locator_exposed` | `bool` | Whether v1 locator metadata contained OCR strings before the blinding correction; false in v2. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## benchmark_rows_v2

| Field | Arrow type | Definition |
|---|---|---|
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `occurrence_key` | `string` | Pipeline locator for a printed occurrence; it does not establish a physical-object identity. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `section` | `string` | number_order, end_sorted or beginning_sorted section of the edition. |
| `context_image_path` | `string` | Relative PNG showing the selected row with wider printed context. |
| `exact_image_path` | `string` | Relative PNG of the frozen proposed glyph box in v2. Null for v1, whose box is recorded in locator_json. |
| `locator_json` | `string` | JSON object with sample coordinates, crop hashes and selection fields. See the nested-field notes below. |
| `reference_json` | `string` | Lossless JSON of the original scoring reference. See the nested-field notes below. |
| `prediction_json` | `string` | Lossless JSON of the frozen chart-only row prediction. It includes ranked templates and graphic-code candidate sets. |
| `reference_kind` | `string` | Initial disjoint AI reading in v1 or adjudication following two AI readings in v2. |
| `original_ocr_locator_exposed` | `bool` | Whether v1 locator metadata contained OCR strings before the blinding correction; false in v2. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## benchmark_readings

| Field | Arrow type | Definition |
|---|---|---|
| `benchmark` | `string` | v1 or v2 benchmark identifier. |
| `sample_index` | `int64` | Zero-based index within the v1 or v2 frozen benchmark. The two index spaces are separate. |
| `reader` | `string` | A/B/C research-role label. These references were produced by AI readers; no human expert certification is recorded. |
| `kind` | `string` | primary, convenience_repeat, independent or adjudicated reading. Repeats were fixed convenience selections. |
| `reading_json` | `string` | Lossless returned row or count-page reading JSON, including candidate ambiguity and source observations. |
| `source_file` | `string` | Repository-relative parent file. Parent content is not necessarily distributed with the public candidate. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## benchmark_chart_cards

| Field | Arrow type | Definition |
|---|---|---|
| `benchmark` | `string` | v1 or v2 benchmark identifier. |
| `card_id` | `string` | Original chart-card sheet stem; sheet sequence is not a train/test split. |
| `image_path` | `string` | PNG path relative to the dataset root. Use snapshot_download to obtain image files. |
| `source_file` | `string` | Repository-relative parent file. Parent content is not necessarily distributed with the public candidate. |

## benchmark_count_pages

| Field | Arrow type | Definition |
|---|---|---|
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `frame` | `string` | For benchmark_count_pages, random or stress page frame. For weight_chance_controls, the legacy/canonical metrological multiplier rule named in the method report. Evaluate each frame separately. |
| `image_paths` | `list<item: string>` | List of licensed count-page PNGs relative to the dataset root. |
| `reference_json` | `string` | Lossless JSON of the original scoring reference. See the nested-field notes below. |
| `detections_json` | `string` | JSON list containing only row_anchor_y_2x and margin_xyxy_2x, the geometry used for row-recall matching. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## benchmark_count_readings

| Field | Arrow type | Definition |
|---|---|---|
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `reader` | `string` | A/B/C research-role label. These references were produced by AI readers; no human expert certification is recorded. |
| `reading_json` | `string` | Lossless returned row or count-page reading JSON, including candidate ambiguity and source observations. |
| `source_file` | `string` | Repository-relative parent file. Parent content is not necessarily distributed with the public candidate. |

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
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

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
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## evidence_collections

| Field | Arrow type | Definition |
|---|---|---|
| `institution` | `string` | Museum or collection institution label. |
| `region` | `string` | Register’s modern regional grouping. |
| `confirmed_record_minimum` | `int64` | Minimum original inscription-confirmed records in a bounded query. Null is unmeasured; zero is a query outcome. |
| `count_basis` | `string` | Authored definition of the reported count and its source/time frame. |
| `record_fields_json` | `string` | JSON of field-availability assessments for an institution; these are assessments, not copied object records. |
| `source_ids` | `list<item: string>` | IDs in the collections source register, prefixed collections: in evidence_sources. |
| `query_date` | `string` | Recorded date of the bounded collection query. |
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## evidence_datasets

| Field | Arrow type | Definition |
|---|---|---|
| `name` | `string` | Dataset-register name. |
| `size_json` | `string` | JSON of historical aggregate size measures and units; missing size remains null inside JSON. |
| `count_basis` | `string` | Authored definition of the reported count and its source/time frame. |
| `reported_reuse_terms` | `string` | Recorded licence or unresolved-rights assessment of the external dataset; that dataset is not included here. |
| `version_basis` | `string` | Recorded version/time scope of the external dataset observation. |
| `source_ids` | `list<item: string>` | IDs in the collections source register, prefixed collections: in evidence_sources. |
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

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
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

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
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

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
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## evidence_museum_joins

| Field | Arrow type | Definition |
|---|---|---|
| `institution` | `string` | Museum or collection institution label. |
| `museum_record_id` | `string` | Published museum catalogue identifier. |
| `museum_accession` | `string` | Published accession string; formatting is preserved. |
| `museum_url` | `string` | Published museum object page, if recorded or recoverable from its identifier. |
| `cisi` | `string` | Published CISI key linked to the museum accession. Local corpus rows and sign sequences are omitted. |
| `join_method` | `string` | Authored identifier/concordance method supporting the join. |
| `shared_identifier` | `string` | Public excavation/plate identifier used to support the join; null when only the supplement evidence is retained. |
| `join_evidence` | `string` | Authored source/page/identifier observation supporting the join. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |

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
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |

## weight_mass_bands

| Field | Arrow type | Definition |
|---|---|---|
| `group` | `string` | Dholavira mass band in grams: below-1.3, 1.3-to-5, 5-to-100 or above-100. |
| `n` | `int64` | Number of weights in the stated band. |
| `unit_g` | `double` | Fitted metrological unit in grams under the cited model and multiplier rules. |
| `signal_cv_percent` | `double` | Fitted relative signal variation expressed as a percentage. |
| `signal_probability` | `double` | Fitted signal-mixture probability; not a probability of an archaeological interpretation. |
| `within_3_percent_n` | `int64` | Weights within the method’s 3% proximity rule. |
| `unit_ci95_low_g` | `double` | Lower endpoint of the fitted-unit bootstrap interval, grams. |
| `unit_ci95_high_g` | `double` | Upper endpoint of the fitted-unit bootstrap interval, grams. |
| `method_path` | `string` | Repository-relative method/report citation. Its code repository is presently private. |
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## weight_chance_controls

| Field | Arrow type | Definition |
|---|---|---|
| `frame` | `string` | For benchmark_count_pages, random or stress page frame. For weight_chance_controls, the legacy/canonical metrological multiplier rule named in the method report. Evaluate each frame separately. |
| `null` | `string` | Mass-randomization rule used to generate the comparison, named in the metrology method. |
| `draws` | `int64` | Number of simulated comparison draws. |
| `observed_geometric_n` | `int64` | Observed matches under the method’s geometric rule. |
| `observed_close_n` | `int64` | Observed matches under the method’s close rule. |
| `geometric_mean` | `double` | Mean geometric-rule matches in the simulated comparison. |
| `close_mean` | `double` | Mean close-rule matches in the simulated comparison. |
| `geometric_simulation_interval95` | `string` | JSON text giving the central 95% simulation interval for geometric matches. |
| `close_simulation_interval95` | `string` | JSON text giving the central 95% simulation interval for close matches. |
| `fraction_ge_observed_geometric` | `double` | Fraction of simulated draws with at least the observed geometric match count. |
| `fraction_ge_observed_close` | `double` | Fraction of simulated draws with at least the observed close match count. |
| `method_path` | `string` | Repository-relative method/report citation. Its code repository is presently private. |
| `source_locator` | `string` | Exact parent file and JSON pointer/data-row/source ID. Repository paths are evidence pointers, not public URLs. |
| `status` | `string` | Research status, preserving the difference between Exploratory findings and Frozen evaluation records. |

## image_assets

| Field | Arrow type | Definition |
|---|---|---|
| `image_path` | `string` | PNG path relative to the dataset root. Use snapshot_download to obtain image files. |
| `component` | `string` | Configuration or image component served by this PNG. |
| `role` | `string` | chart_cell, row_context, exact_proposal_crop, chart_card or page_count_context. |
| `pdf_page` | `int64` | One-based page of the acquired PDF, including the repository cover. It differs from book pagination. |
| `source_path` | `string` | Repository-relative PNG parent path. |
| `sha256` | `string` | SHA256 of the staged PNG bytes. |
| `bytes` | `int64` | PNG byte count. |
| `license` | `string` | Source image licence, CC BY 4.0. |
| `source_url` | `string` | Official source or licence attribution URL. |

## Nested benchmark fields

`reference_json` and row `reading_json` retain `sample_index`, `printed_inscription_id`, `classification_literal`, `crop_correct`, `drawn_unit_count` and the ordered `units`. A unit’s `strict_candidate_codes` combines drawing, underline and vertical-position observations; `shape_only_candidate_codes` is a broader diagnostic set. An empty strict set means unresolved. `unit_kind` records a glyph or modern editorial drawing such as damage/hatching; loss drawings do not imply a known original number of signs. Unit indices and source extents remain as returned by each reader. `valid_printed_target=false` is a false detection in v2. Optional crop explanations, underlines, blank gaps and source-window observations preserve the reader’s own record. The JSON objects can differ in optional fields across readers; the tabular outer schema is fixed.

`prediction_json.units[*].alternatives` is ranked in template order and retains `template_key`, `codes`, `ranks`, distances/costs and synthetic template scores. `confidence` is the development logistic confidence when present. A synthetic softmax score is not a probability over authenticated readings. The original template order and confidences are needed to reproduce candidate widths, alignment and calibration. Each prediction’s number and classification can be null or wrong. `serialization` describes visual ordering, not a linguistic reading direction or physical-object surface concordance.

`locator_json` gives PDF coordinates, target/context boxes, crop paths/hashes and the frozen sample’s section. Zero-based pipeline `pdf_column`/`row_index` values are detector coordinates; reader source-column indices may use their original conventions. Field names ending `_2x` are pixels at two pixels per PDF point. Boxes ending `_pdf_box` or `_pdf_points` use PDF points. `source_crop` is the wider context filename; v2 `exact_crop` is the proposed glyph-box filename. Use the outer relative image paths to open the staged copies.

Count-page `reference_json` and count `reading_json` contain `columns`, `x_extent_pdf`, `row_count`, `row_centers_pdf`, and continuation-line coordinates where recorded. A numbered printed occurrence counts once, while an unnumbered continuation adds a physical line without adding an occurrence. `detections_json` contains detector centers/field boxes only. The recall scorer greedily matches the nearest eligible source/detection centers within nine PDF points and counts unmatched detections as false positives.

`benchmark/reader-metadata.json` preserves original notes, timing and blinding disclosures; returned rows are in the reading tables. `benchmark/v1-exploratory-adjudication-overlay.json` is a post-outcome correction record and is not applied to the frozen v1 score. `benchmark/v2-adjudication-notes.json` preserves the source-only adjudicator’s decisions. PNGs and their source hashes are listed in `image_assets`.
