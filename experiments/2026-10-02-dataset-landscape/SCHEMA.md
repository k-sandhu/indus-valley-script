# Proposed entities for an Indus evidence dataset

Design specification, 2 October 2026. The basic chain is a physical object, one of its surfaces, an inscription on that surface, a source transcription, and the observed sign occurrences. Images and contextual observations attach to the relevant object, surface or inscription through explicit witnesses. The schema has not yet been populated or implemented as a database.

An observation carries its source, locator, method, reviewer status and missingness. Where sources disagree, preserve their assertions and attach a separate adjudication. Namespaced source identifiers and internal identifiers remain distinct. Null fields need a reason such as not recorded, unavailable, unreadable, not applicable or unresolved.

| Entity | Main fields | Purpose |
|---|---|---|
| `source` | `source_id`, title, authors, publication date, edition/version, URL/DOI, source category | Identify a publication, catalogue, archive, repository or own measurement protocol. |
| `rights_record` | `rights_id`, applicable asset/source, status, license/permission, notice locator, scope, attribution, review date | Describe the exact basis for inclusion. Status vocabulary follows the existing redistribution record. |
| `asset` | `asset_id`, `source_id`, media type, source URL, SHA256, bytes, acquisition date, parent asset, transformation, `rights_id`, public disposition | Track a file or reference-only external asset. Local paths are kept out of public exports. |
| `object` | `object_id`, collection scope, reported authenticity status, object-type assertions, current holding assertions | Represent a physical object. A generated example never receives an archaeological object ID. |
| `identifier_assertion` | `assertion_id`, `object_id` or candidate objects, scheme, raw identifier, source/version, locator, match status | Preserve museum, excavation, CISI, IM77 and export aliases without cross-version numeric joins. |
| `surface` | `surface_id`, `object_id`, source surface label, arrangement, observed orientation, status | Identify a face or surface. Unresolved arrangements retain candidate labels. |
| `inscription` | `inscription_id`, surface(s), source-defined extent, lines, manufacture assertions, coverage/completeness | Distinguish one text from another while preserving uncertain physical boundaries. |
| `image_view` | `view_id`, `asset_id`, target object/surface, locator or image region, view direction, polarity, scale, resolution, coverage | Relate photographs, drawings, impressions, RTI and 3D views to the physical evidence. |
| `transcription` | `transcription_id`, `inscription_id`, source, inventory/version, annotator/method, line structure, visual-order convention, reading-order hypothesis, review status | Preserve competing transcriptions as versions rather than a silently corrected string. |
| `sign_occurrence` | `occurrence_id`, `transcription_id`, line/position, raw source code, candidate codes, damage/uncertainty, blank/loss status, bounding region | Represent a position or observed span. Unknown extent differs from one missing sign. |
| `sign_definition` | inventory/version, code, graphic description, source witness, variants/features, publication status | Keep Wells, Mahadevan, Parpola and Finnish codes distinct. Code equality across systems is not assumed. |
| `crosswalk_assertion` | source and target inventory versions/codes, candidates, relation type, source witness, token/feature scope, adjudication | Keep exact, broad, variant and unresolved correspondences separate. Do not close overlapping candidates transitively. |
| `context_observation` | target object/assemblage, field, raw value, normalized value, units, dating range/basis, source locator, observation method, missing reason | Store provenance, measurements, contents and other physical observations with their grounds. |
| `motif_observation` | target object/surface/view, feature category, raw description, annotator, method, evidence region, uncertainty | Record non-text iconography separately from a proposed word or religious identity. |
| `relationship_assertion` | endpoints, relation type, source/locator, status, reviewer, uncertainty | Represent same object, same stamp, repeated text, shared source image, same assemblage and comparative similarity as different relations. |
| `claim` | claim ID, author/source, proposed interpretation, supporting and conflicting observations, status, test, chronology | Attribute archaeological interpretations and decipherment hypotheses without turning them into authenticated labels. |
| `annotation_review` | target, reviewer role, review date, inputs disclosed, agreed/disputed fields, alternatives, decision and rationale | Preserve expert, curator and AI annotation status and every change in an adjudication. |
| `evaluation_manifest` | task, eligible record set, exclusions, dependence groups, fixed source versions, split rules, algorithm, hashes, output paths | Define a reusable evaluation population with its own independence assumptions. |
| `release_manifest` | version, included tables/assets, hashes, rights disposition, source coverage, checks, attribution, missing material | State exactly what a public package contains. |
| `synthetic_example` | separate example ID, generating procedure, seed, supplied truth, source calibration, purpose | Keep simulations and graphic aids out of archaeological counts. |

## Identity rules

One excavation lot can contain many objects. One object can have many catalogue aliases, surfaces and photographs. An impression can belong to a different physical object from the seal that made it. A repeated string on separate objects does not establish a shared stamp. A photographic suffix such as `bis` is a witness rule from its source, not an additional object.

Every uncertain identity or classification is an assertion with a status. Accepted physical identity can drive object joins and evaluation grouping. Candidate sign crosswalks or resemblance links cannot drive those joins. A link to the same archaeological source remains the same evidence origin even when another annotator supplies a transcription.

## Missingness and corrections

Preserve raw placeholder strings, including zero-valued dimension fields, alongside normalized nulls and their reasons. Do not interpret an unfilled quantity as zero. Missing dates remain missing; a broad cultural-period label has its own dating basis. Unreadable signs retain candidate sets or loss spans, with the photographed area that supports them.

Corrections create a new annotation or source assertion and reference the older one. Frozen source versions and experiment inputs remain reconstructible. A curated current view may choose reviewed values, while its record lists the source assertions and selection rule. Unresolved differences remain visible in that view.

## Export rules

Export relations as separate JSONL/Parquet tables and preserve identifiers across formats. A SQLite export implements foreign keys and supplies documented joins. Public views include only covered payloads and use stable source URLs for reference-only assets. Public file records do not expose local machine paths.

The dataset card reports physical objects, inscription records, transcription versions, image witnesses, sign occurrences and source documents separately. Related collections have scope and dates on every object. Proposed translations live in the claim table. Synthetic examples have a separate configuration and their own count.
