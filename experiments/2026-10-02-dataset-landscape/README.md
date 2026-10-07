# Existing Indus datasets and a proposed public collection

Review completed on 2 October 2026. Broad Indus corpora already exist. The closest predecessor is the Interactive Corpus of Indus Texts (ICIT), which joins texts, images, archaeological metadata and analysis tools. This review did not establish a single openly downloadable, permission-cleared package containing all the layers proposed below. The search cannot prove that no such package exists.

Our project contains a useful research collection built partly from those earlier corpora. Its present size and selected source corrections do not establish that it is more complete than ICIT or CISI. A public dataset project should identify measurable improvements on matched objects and document its remaining omissions.

The completed work here is a source comparison, aggregate input audit and build specification. A new integrated archaeological corpus has not been built or published. Raw API responses, source pages, cards and the conference PDF remain local under `data/raw/2026-10-02-dataset-landscape/`.

## Existing collections

| Collection | What it already supplies | What this review could establish |
|---|---|---|
| [ICIT](https://www.epigraphica.de/indus/menueindus.htm) | A broad database with objects, inscriptions, images, excavation identifiers, material, direction, preservation, iconography and spatial/statistical tools. | Its 2023 report lists 4,665 objects, 5,650 texts, 17,966 legible sign occurrences and 16,015 photos/drawings in 29 tables. These are historical counts. The public landing page asks users to request access; current internal coverage and bulk-data rights were not inspected. |
| [CISI photographic corpus](https://researchportal.helsinki.fi/en/projects/corpus-of-indus-seals-and-inscriptions/) | Published photographs, object sides and catalogue documentation. Verified volume records include [3.1, 2010](https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-volume-3-new-material-untr/) and [3.2, 2019](https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-32-shahr-i-sokhta-mundigak). | Our accessible scans are not a verified complete image collection. Access to a scan does not establish permission to redistribute its photographs. |
| [Mahadevan IM77 application](https://indusscript.in/), described by [RMRL](https://www.rmrl.in/en/irc) | Online corpus and concordance based on *The Indus Script: Texts, Concordance and Tables* (1977). | Institutional provenance is clear. A current full export and its bulk reuse terms were not verified. RMRL also lists an expanded concordance among planned activities. |
| [Helsinki 1979](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/) and [1982](https://researchportal.helsinki.fi/en/publications/a-concordande-to-the-texts-in-the-indus-script/) editions | Published graphic texts, sign tables and concordance. | Their official pages link CC BY 4.0. They offer a licensed digitization route, with attribution. Original text boundaries and glyph identities still need review. |
| [Mayig](https://github.com/mayig/indus-valley-script-corpus) | Structured JSON with sign features, line, damage and uncertainty annotations. | Our pinned subset has 179 faces and 1,003 token positions. The actual repository notice is MIT. Photograph rights have separate origins. Upstream main was not recounted. |
| [Lipi](https://github.com/yajnadevam/lipi) and derivative exports | A broad inscription CSV and metadata; some forks make the same records available elsewhere. | Our pin has 5,680 rows, 4,695 provisional source families and 19,946 token positions. Its source interpretations are excluded from our observed extraction. No license was found at the pin; current GitHub metadata also reports no detected license. |
| Hugging Face resources | [Generated sequences](https://huggingface.co/datasets/hellosindh/indus-script-synthetic), a [research-state mirror](https://huggingface.co/datasets/Zer0pa/Indus-Valley-lane-state), and a [focused sign audit](https://huggingface.co/datasets/junafinity/p316-p147-p217-indus-branch-audit-20260609). | Their cards and API file inventories describe different research products. None of these descriptions establishes the complete integrated archaeological collection proposed here. Full mirror bundles and image permissions were not audited. |
| Glyph and interpretation collections | Isolated glyph PNGs, recognition code, author reading tables, website compilations and SQLite research packages. | These provide useful precedents or candidate inputs. Their record counts, proposed readings and licensing require separate treatment. The detailed [source comparison](landscape.json) names each reviewed resource. |

The ICIT count is verified from Andreas Fuls, abstract 76, printed/PDF page 281 of the [CAA 2023 abstract book](https://2023.caaconference.org/wp-content/uploads/sites/29/2023/04/abstract_book_v13.pdf#page=281). The acquired page was rendered and visually checked. Its 1.2 million database entries are not 1.2 million ancient inscriptions.

## What we have

The [aggregate audit](main-v1/local-input-audit.json) reads the pinned derivatives and reproduces 39 existing count/missingness checks. All passed. It preserves input paths, byte counts and SHA256 values. The [audit code](audit_local_inputs.py) writes no inscription rows or sign sequences into its result.

| Local source or resource | Size | Meaning of the count |
|---|---:|---|
| Lipi observed export | 5,680 records; 4,695 provisional families; 19,946 token positions | Source groupings and transcription records, with editorial markers retained. The family count is not a complete physical-identity audit. |
| Earlier website export | 2,543 records; 11,135 token positions | Overlapping historical export, not additional archaeological discoveries. |
| Mayig annotation | 179 faces; 1,003 token positions | Another annotation of largely shared source objects. |
| Helsinki chart resource | 687 cells, including 16 ambiguous lower-code labels | An AI-annotated source table with crop provenance, not 687 distinct authenticated signs or expert-certified labels. |
| Harappa short-record frame | 22 objects, 66 faces | A source-linked subset already represented in the corpus. |

The main export's historical missing-value rule finds no time field for 2,613 records (46.00%), no room/grid field for 3,489 (61.43%), and no block/house field for 4,167 (73.36%). These are source-field gaps, not estimates of what survives in excavation archives. Several dimension columns contain zero placeholders, and the literal depth string `- -` is outside that old missing-value rule. The new audit exposes those cases separately. A future importer must preserve why a value is missing and distinguish a placeholder from a measurement.

Our useful additions include recorded catalogue disagreements, object and image joins, the sign atlas, uncertainty conventions, dependence checks, code and preserved failure records. Much of this information still sits in separate study files. There is no finished common object register covering all of it, no broad expert-reviewed image annotation set, and no release manifest clearing every inherited asset.

## The useful next project

Build a common register connecting each physical object to its sides, inscriptions, images, source editions, excavation context and competing transcriptions. Include early and exceptional records and every text length. Preserve related regional collections in their own dated namespaces, with explicit links describing why they are relevant.

The [build plan](DATASET_PLAN.md) defines source acquisition, a 200-object pilot, quality comparisons and public packaging. The [schema specification](SCHEMA.md) explains the entities and joining rules. These are proposed requirements, not completed coverage claims.

The proposed public product has a factual core and linked research layers. The core holds source-backed observations; the other layers hold comparative material, published interpretations and simulations with their origins visible. An inscription has no authenticated translation field populated by a proposed decipherment.

Measure improvement against ICIT, IM77 and public derivative datasets on a declared common object set. Count added verified objects, downloadable licensed images, reviewed transcriptions, resolved identifier joins, contextual measurements and explicit disagreements. Publish both missing and unresolved records in the coverage report. A larger folder or more synthetic sequences cannot increase the archaeological object count.

## Reuse and proposed hosting

Use [Hugging Face](https://huggingface.co/docs/hub/datasets-overview) for downloadable tables and compatible dataset views. Use [Zenodo](https://help.zenodo.org/docs/deposit/about-records/) for citable releases with a DOI; its [versioning documentation](https://help.zenodo.org/docs/deposit/manage-versions/) explains how revised files receive a separate linked record. Keep the existing repository for manual code and documentation, without CI/CD or deployment scaffolding.

For a first public package, include only assets with a documented reuse basis. Helsinki's CC BY editions, covered Mayig material and our own work have promising routes, subject to payload and attribution review. Unresolved sources can have bibliographic records and access instructions while their images and bulk sequences remain local. A downstream repository's license does not by itself clear inherited material.

No external publication, account creation, author message or repository visibility change occurred in this run. The user's suggested public dataset remains a build direction; source review and a concrete release payload are still required.

## Reproduction and research memory

Run from the repository root:

```powershell
python experiments/2026-10-02-dataset-landscape/audit_local_inputs.py --output experiments/2026-10-02-dataset-landscape/replay-v2/local-input-audit.json
```

The replay requires local-only derivatives and discovery witnesses. Acquisition scripts also require new output directories below `data/raw` and refuse to reuse a preserved directory. Use [capture_catalogue_metadata.py](capture_catalogue_metadata.py) and [capture_source_witnesses.py](capture_source_witnesses.py) with separately dated endpoints; the second script reads the existing discovery snapshot to pin cards.

The [retrospective](RETROSPECTIVE.md) records discovery limitations, the PDF extraction repair and source handling. Consult the original [corpus retrospective](../../knowledge/retrospectives/corpus-and-transcription.md) before attempting glyph OCR or cross-catalogue conversion. Those earlier failures require new acquisition geometry or reviewed source evidence.
