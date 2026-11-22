# Methods, schema specification, join procedures and reproduction

Technical companion to [manuscript.md](manuscript.md), 22 November 2026. All relative links resolve from `papers/007-object-reconciliation-register/` to the repository root. Every command runs from the repository root with Python 3.13.

## 1. Pinned inputs and provenance hashes

All measurements and register builds derive from fixed local inputs recorded in [MANIFEST.json](../../data/MANIFEST.json) (146 sources as of 22 November 2026: 61 held, 17 partly held, 36 project outputs, 32 not held). Key upstream pins and SHA-256 digests:

| Input | Pin or edition | Local path | SHA-256 prefix | Rights status |
|---|---|---|---|---|
| Lipi observational faces | `yajnadevam/lipi` commit `fc8813a52e183d19c441631dc26c33a4dccbea39` | `data/normalized/lipi_observed_faces.jsonl` | `1220f5591a42abe7...` | No licence at pin; local-only |
| Earlier Indus website export | `yajnadevam/indus-website` commit `2434249` | `data/normalized/indus_website_observed.jsonl` | `ff842377a6b98d51...` | GPL-3.0 code; data unresolved; local-only |
| Mayig corpus | `mayig/indus-valley-script-corpus` commit `ad2f1e2` | `data/normalized/mayig_faces.jsonl` | Recorded in `source-manifest.json` | MIT (Carlson 2024); photographs separate |
| Mackay 1938 and Marshall 1931 tables | `epachayan/indus-script` commit `5c14a01f44296a01256a34e7e5e5e9fd82d9a67f` | `data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script/` | Mackay `0d2499b2...`; Marshall `5a339a78...` | Tables CC BY 4.0 (Koshy 2026); code MIT |
| CISI 1 basic data (assembled) | Joshi and Parpola 1987, printed pp. 366–375 | `data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl` | `15cb18a7d539d7ce...` | Copyright 1987 Finnish Academy; local-only |
| CISI 2 basic data (assembled) | Shah and Parpola 1991, printed pp. 435–447 (PDF `5258071b...`) | `data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi2-basic-data.jsonl` | `12254fff539499b9...` | Copyright 1991 Finnish Academy; local-only |
| Penn Museum collections CSV | 2026-10-07 edition (430,871 rows, 151,266,760 bytes) | `data/raw/2026-10-13-museum-open-access/penn/` | `a24614d5...a3778` | Data CC BY 4.0; images non-commercial |

Bulk local inputs reside at `D:\projects\indus_valley_script` with directory junctions and file links preserving logical `data/` paths in the checkout ([LOCAL_STORAGE.md](../../LOCAL_STORAGE.md)).

## 2. Schema version 2.0 specification

The core register (`register-v2.json`) validates against JSON Schema Draft 2020-12 in [schema-v2.json](../../experiments/2026-10-22-object-register/schema-v2.json) with `additionalProperties: false` on every object definition.

### 2.1 Top-level envelope and twelve core tables

Required root properties: `schema_version` (`"2.0"`), `status` (`"Exploratory"`), `selection_sha256` (SHA-256 of `PROTOCOL.md`), `sequence_policy` (`"No sign sequences; transcription payloads are local-only"`), and twelve array tables:

1. `objects` (4,695 rows): `id` (`LIPI:<object_family_id>`), `selection_key`, `identity_status` (`identifier-supported` or `source-reported`), and 16 required `fields` (`object_type`, `material`, `holding`, `authenticity`, `catalogue_identifier`, `excavation_identifier`, `field_identifier`, `museum_accession`, `measurement`, `image_pointer`, `rights_pointer`, `face_count`, `length_bin`, `damage`, `export_excavation_identifier`, `bibliographic_locator`).
2. `contexts` (4,695 rows): 1:1 closure with `objects` via `id` (`CTX:<object_family_id>`) and `object_id`, holding 20 required context fields (`site`, `region`, `area`, `room_grid`, `stratum_phase`, `period_label`, `calendar_interval`, `dating_basis`, `dating_sample`, `excavation_unit`, `excavation_item`, `physical_contact_category`, `context_code`, `impression_count`, `findspot_site`, `reported_production_place`, `lot_identifier`, `country`, `periodization_scheme`, `design_classification`).
3. `surfaces` (5,680 rows): `id` (`LIPI:<record_id>`), `object_id`, and `fields` (`label`, `orientation`, `arrangement`, `alignment`).
4. `transcriptions` (0 rows): intentionally empty under `sequence_policy`.
5. `images` (6,826 rows): unique `(object_id, path)` records linking `object_id`, `source_id`, `rights_id`, `url`, `locator`, `kind`, `inspection_status` and `surface_alignment`.
6. `sources` (56 rows): bibliographic and provenance definitions with `quoted_words: 0` enforced by schema.
7. `identifiers` (16,434 rows): `object_id`, `scheme`, `value`, `status` (`confirmed` or `candidate`), `assertion_id` and `edition`.
8. `measurements` (11,993 rows): `object_id`, `dimension` (`horizontal`, `vertical`, `thickness`, `dimension_1`, `dimension_2`, `dimension_3`, `diameter` or `mass`), positive numeric `value` (`exclusiveMinimum: 0`), `unit` (`mm`, `cm`, `g` or `kg`), `method` and `assertion_id`.
9. `assertions` (225,223 rows in base `run-v2`; 230,697 after held-source integration): `id`, `object_id`, `field`, non-null `value`, `source_id`, structured `locator` (`path`, `record`, `field`, `page_or_url`, `page_missing_reason`), `method`, `confidence` (`source-reported`, `identifier-supported`, `candidate` or `derived`) and `review_status` (`"not-expert-reviewed"`).
10. `rights` (6,826 rows): `source_id`, `asset_ref`, `status` (`own-work`, `explicit-license`, `rights-unverified` or `mixed-assets`), `license`, `scope`, `disposition` (`reference-only` or `local-only`) and `notice_locator`.
11. `relationships` (6,329 rows): cross-source identity edges (`object_id`, `source_id`, `external_record`, `relation`, `status` in `{confirmed, candidate}`, `method`, `assertion_id`).
12. `correction_overlays` (0 rows in base `run-v2`; populated during held-source layout review and future human audits).

Every cell inside `objects[*].fields`, `contexts[*].fields` and `surfaces[*].fields` obeys a strict `oneOf` union: either `{value: <non-null>, assertion_ids: [<>=1 unique strings>], missing_reason: null}` or `{value: null, assertion_ids: [], missing_reason: <non-empty string>}`.

### 2.2 Compact sidecar exports

Each base register run writes six JSONL sidecars under local `data/raw/2026-10-22-object-register/<run>/` (interface defined in [INTERFACE.md](../../experiments/2026-10-22-object-register/INTERFACE.md)):

- `objects.jsonl`: one record per provisional family with `object_id`, `source_family_id`, `physical_identity_status: "provisional"`, `face_ids`, `aliases`, `pilot_aliases`, `fields` (each carrying `value`, `value_status`, `uncertainty`, `assertion_ids`, `missing_reason`), `conflicts`, `exposure_status: "unreviewed"` and `dependency_group_status: "not_constructed"`.
- `faces.jsonl`: one record per exported face with `face_id`, `object_id`, `source_record_id`, `source_cisi_raw`, `catalogue_key`, `image_links` (each carrying `path`, `sha256`, `kind`, `side_match`, `relation`, `join_status`), `conflicts` and `exposure_status`.
- `assertion-values.jsonl`: raw and normalized values for all assertions plus explicit `unknown` records for placeholder or empty source values, carrying `value_status`, `uncertainty`, `source_sha256` and `join_status`.
- `missing-values.jsonl`: explicit listing of every `unknown` object and context field with its `missing_reason`.
- `join-queue.jsonl` (1,348 rows): external records lacking a unique Lipi family join, pilot catalogue-only objects (20 keys), and quarantined implausible measurements.
- `cisi-reader-decisions.jsonl` (3,238 rows): every CISI double-reading disagreement row (`pass1`, `pass2`, `final`, `outcome`, `note`, `auto`, `source_sha256`).

The held-source integration (`experiments/2026-10-22-evidence-integration/run-v2/`) adds `candidate-reviews.jsonl` (358 rows), `exposure-events.jsonl` (1,018 historical plus 33 current face-review records), `changes.jsonl` and separately versioned lexical source reviews (`lexical-sense-review.jsonl` and `lexical-compound-review.jsonl`), which are never copied into archaeological object fields.

## 3. Acceptance, normalization and conflict rules

1. **Usable values and placeholders.** Strings are stripped and case-folded against `{"", "-", "--", "- -", "?", "??", "???", "unknown"}`. `None` in Lipi `symbol` and `cult` is treated as a usable asserted absence. In dimension fields, `0` and non-positive numbers are unusable; range strings matching `^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*$` with a positive upper bound count toward inventory dimension presence (`any_positive_dimension_including_ranges = 3,598`) but are never converted into scalar measurements in `measurements`.
2. **Dimension plausibility bound.** Positive scalar measurements exceeding 1,000 mm are retained in `assertions` and `measurements` with `uncertainty: "implausible"`, logged in `join-queue.jsonl`, and withheld from accepted `object.measurement` fields (quarantining one 3,000 mm value).
3. **Catalogue-key normalization.** Base keys are normalized by regex `^\s*([A-Za-z?]+)[-. ]*0*(\d+)(?:[A-Ca-c])?(?:\s*(?:bis|ter|quater))?\s*$` to `<prefix_lower>-<integer>`. Ambiguous or multi-key strings return `None` and are never normalized.
4. **Non-merging family rule.** Physical families (`LIPI:<object_family_id>`) are never merged when an external identifier matches two families; ambiguous external rows move to `join-queue.jsonl`.
5. **Conservative CISI cell acceptance.** For CISI 1 and CISI 2 rows joined uniquely via `object-flags.csv` (`join == "one-family"`), any cell whose column appears in an `auto: true` Amendment 2 merge, an `undecidable` or `absent` adjudication, `uncertain_columns`, or contains `[` is withheld from accepted object fields (`target = None`) and marked `status: "candidate"` in `identifiers` when applicable. If column 1 itself has an unresolved pass-1 vs. pass-2 base-number dispute, the entire row's identity relationship is downgraded to `status: "candidate"` and all its cells are withheld from accepted fields.
6. **Conflict flagging.** During `finish()`, a field is assigned `value_status = "unknown"` when `value is None`, `"inferred"` when every supporting assertion has `confidence == "derived"`, `"catalogued"` otherwise, and `"conflicting"` whenever two or more distinct JSON-serialized values exist across supporting assertions for a non-repeated field (fields outside `REPEATED_FIELDS = {measurement, catalogue_identifier, export_family_identifier, museum_accession, bibliographic_locator, image_pointer, rights_pointer, face_count, length_bin, damage, field_identifier}`). The displayed `value` is the first-source assertion rather than an adjudicated winner.
7. **Image side-match quarantine.** Four catalogue keys flagged by the 20 October line-division plate audit (`H-603`, `M-663`, `M-1187`, `M-1202`) are forced to `side_match: false` and `join_status: "needs-later-audit-review"` in `faces.jsonl` while keeping their object-level links visible.

## 4. Adapter join procedures

- **Baseline data inventory (`2026-10-12-data-inventory`):** Computes face-level and family-level usable-value coverage across 33 Lipi keys, cross-checks the older website export on raw CISI key, and hashes all local PDFs and images.
- **CISI 1 and CISI 2 basic data (`2026-10-13-cisi2-basic-data-pilot`, `2026-10-13-cisi-basic-data-full`):** Renders CISI 2 at zoom 8.34 (3,252 × 4,542 px foreground) and CISI 1 at zoom 4 into ~14-line overlapping half-column strips across 43 blocks (plus 17 CISI 2 tail strips under Amendment 1). Sixteen isolated AI reader instances execute two blind passes (pass 2 reads column bands in two sweeps). `compare_passes.py` aligns rows and emits disagreements; all CISI 1 disagreements (106 + 6 corrigenda), all CISI 2 pilot disagreements (156) and three new CISI 2 blocks (pp. 437L–439L, 256 decisions) are adjudicated against page strips; remaining 2,870 CISI 2 disagreements are merged under Amendment 2 keeping the union of allowed digits. Joins require unique `(prefix, integer)` match to one Lipi family (`2,602 / 3,680` join-eligible rows).
- **CISI 3 range coverage (`2026-10-13-cisi3-range-coverage`):** For each prefix whose CISI 1 or 2 ceiling was measured by the evidence census, enumerates integer slots from `cisi12_last + 1` to the maximum base number in Lipi. Each absent slot inherits the first-segment object class (`POT`, `SEAL`/`TAB`/`TAG`, or `other`) when lower and upper nearest present neighbours agree, and `mixed` otherwise. Verified independently from raw `data/lipi/src/assets/data/inscriptions.csv`.
- **Mackay 1938 and Marshall 1931 tables (`2026-10-13-mackay-marshall-tables`):** Parses Lipi `excavation-idno` as field number optionally followed without separator by excavator catalogue number(s), applying Marshall area aliases (`C`→`DKC`, `E`→`DKE`, `DK`→`DKB`/`DKC`, etc.). Exact joins require matching field number (or field + catalogue number) with no type, material or size contradiction (tolerances: 0.06 in size agreement, 0.15 in contradiction, 0.2 ft level agreement). Variant joins allow up to two edits in field number when catalogue number agrees, one edit in catalogue number when field number agrees, or a trailing letter, requiring at least two agreeing attributes. Eleven exact-key contradictions were adjudicated against printed page images.
- **Museum open-access harvest and Q-1019 review (`2026-10-13-museum-open-access`):** Queries Met API v1.1, Cleveland Open Access API, AIC API, Smithsonian Open Access S3 bulk bucket (`nmnhanthro`, `fsg`, `nmaa`), Penn CSV, V&A API v2 and saved British Museum search pages, logging every request with SHA-256. Joins are `exact` on unique normalized identifier and `confirmed` through printed CISI 1 basic data, Marshall 1931, Mackay 1938, Mackay 1943 or numbers painted on objects in CISI photographs with agreeing site and object type; description-only matches remain `ambiguous` with enumerated candidate counts.
- **Face-level image index and dimension audit (`2026-10-13-image-index-and-units`):** Hashes and parses all 8,722 local crops, cross-checks filenames against Tesseract OCR of printed captions, visually inspects all 182 OCR-key mismatches (correcting 23 misnamed objects and 26 total overrides) and 299 volume-and-page filenames (reading 231 captions), maps 3,664 keys onto CISI 1 and 2 plate pages, and links single-face objects plus 21 visually verified multi-face objects at side level while leaving 881 multi-face objects linked at object level. Dimension units are inferred by matching `h`, `v`, `th` against millimetre fields under factors 25.4, 10 and 1 within tolerances 0.051, 0.51 and 0.6 mm.
- **Post-catalogue finds (`2026-10-21-post-catalogue-finds`):** Fixes each site's CISI baseline year before extraction, sweeps post-1987 IAR, *Puratattva*, *Man and Environment*, excavation reports and 367 web queries, extracts one row per physical object without recording sign strings or motifs (preserving exposure boundaries), and matches locally under two separate rules: frozen strict protocol (unique registration or cited plate only: 10 matched, 55–291 absent) and labelled post-outcome context join (unique site, area, trench, phase, type and material or Dholavira grid square with no depth, layer or period conflict, plus Khirsara plate join: 77 matched, 55–224 absent).
- **Held-source integration (`2026-10-22-evidence-integration`):** Extends base `run-v2` with sealed dual-pass face layout reviews (29 faces), supplemental image links (6 links, 5 payloads), candidate identity and exposure records (358 rows, 1,018 historical documentation records), and regression tests (`test_integrate.py`).

## 5. Reproduction and verification commands

All builders refuse to overwrite existing output directories; supply fresh dated directory names for every replay.

### Fetch and verify local inputs

```text
python tools/fetch_data.py --list
python tools/fetch_data.py --show lipi
python tools/fetch_data.py --verify cisi-1
python tools/fetch_data.py --fetch lipi --dry-run
```

### Baseline inventory and Round 1 data packages

```text
# 1. Baseline metadata inventory (12 October)
python -I experiments/2026-10-12-data-inventory/coverage.py --out experiments/2026-10-12-data-inventory/run-<date>
python -I experiments/2026-10-12-data-inventory/build_manifest.py --check-only

# 2. CISI 3.1 and 3.2 range coverage and independent raw verification
python -P experiments/2026-10-13-cisi3-range-coverage/count_ranges.py --out experiments/2026-10-13-cisi3-range-coverage/run-<date> --local data/raw/2026-10-13-cisi3-range-coverage/run-<date>
python -P experiments/2026-10-13-cisi3-range-coverage/check_raw.py --run experiments/2026-10-13-cisi3-range-coverage/run-<date> --local data/raw/2026-10-13-cisi3-range-coverage/run-<date>

# 3. Mackay 1938 and Marshall 1931 seal-table join
python -P experiments/2026-10-13-mackay-marshall-tables/join_tables.py --out experiments/2026-10-13-mackay-marshall-tables/run-<date> --local data/raw/2026-10-13-mackay-marshall-tables/run-<date>
python -P experiments/2026-10-13-mackay-marshall-tables/summarize_verification.py

# 4. Museum open-access offline rebuild from saved inputs
python experiments/2026-10-13-museum-open-access/apply_review_overrides.py
python experiments/2026-10-13-museum-open-access/build_joins.py
python experiments/2026-10-13-museum-open-access/coverage_museum.py

# 5. Face-level image index and dimension audit
python -P experiments/2026-10-13-image-index-and-units/build_index.py --out experiments/2026-10-13-image-index-and-units/run-<date>/images
python -P experiments/2026-10-13-image-index-and-units/dimensions.py --out experiments/2026-10-13-image-index-and-units/run-<date>/dimensions
python -P experiments/2026-10-13-image-index-and-units/verify.py score

# 6. CISI 1 and CISI 2 full basic-data selftest (53/53)
python experiments/2026-10-13-cisi-basic-data-full/selftest.py
```

### Base object register (`run-v2`) and held-source integration

Requires Python 3.13 and `jsonschema`.

```text
# Build base object register, verify 232,837 raw values, and run 12 synthetic mutation tests
python experiments/2026-10-22-object-register/build_register.py --out data/raw/2026-10-22-object-register/replay-<date> --summary-dir experiments/2026-10-22-object-register/replay-<date>
python experiments/2026-10-22-object-register/verify_sources.py --run data/raw/2026-10-22-object-register/replay-<date> --output experiments/2026-10-22-object-register/replay-source-check-<date>.json
python experiments/2026-10-22-object-register/selftest.py

# Rebuild held-source integration register and run 8 integration regression tests
python -X utf8 experiments/2026-10-22-evidence-integration/integrate.py --out data/raw/2026-10-22-evidence-integration/replay-<date> --summary experiments/2026-10-22-evidence-integration/replay-<date> --faces data/raw/2026-10-22-face-adjudication/face-reviews.jsonl --adjudications data/raw/2026-10-22-evidence-integration/face-adjudications.jsonl --candidates data/raw/2026-10-22-candidate-identity-exposure/run-v3/candidate-reviews.jsonl --events data/raw/2026-10-22-candidate-identity-exposure/run-v3/exposure-events.jsonl --senses data/raw/2026-10-22-lexical-source-review/run-v1/sense-review.jsonl --compounds data/raw/2026-10-22-lexical-source-review/run-v1/compound-review.jsonl
python -X utf8 -m unittest discover -s experiments/2026-10-22-evidence-integration -p test_integrate.py -v
```

Deterministic replay of base register `run-v2` reproduces all seven output files identically ([replay-comparison.json](../../experiments/2026-10-22-object-register/replay-comparison.json)):

- `register-v2.json`: `f05aa500a133062f7aa6e07b9a433dcf14375625a018879b64392a2271634e42`
- `objects.jsonl`: `0f8c82d917c8b77790b940a484dbc4c4ecf49cb2fd693e90ac39a5f78527d19f`
- `faces.jsonl`: `f38d963d2ddd755315116d23cbacf02c2eaaea2650d193781a4a54bde64d2bc4`
- `assertion-values.jsonl`: `48f42b49794a94597acb06d6a5449a7efd5e128d8c5021eda1338fcf8727a88b`
- `missing-values.jsonl`: `3df69d2ccbf7a5ebbd95559342a11b26c4e280bcfbbc40cc3652d3912bf8f764`
- `join-queue.jsonl`: `946cb5ea6675f6711e3f3239a3b0731b2d0c2ce3d72a69b4064f0b6131baf9d4`
- `cisi-reader-decisions.jsonl`: `75ae9cec4ca769c96c8e756c8e19cfcecdc6263766142b8f876e9ad39c06dede`
