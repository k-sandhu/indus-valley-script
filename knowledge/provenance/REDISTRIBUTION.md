# Redistribution record

Since 11 October 2026 the public repository has held the reviewed research record. Bulk acquired corpora, downloaded papers, source images and OCR remain in the local project. The [October 11 asset review](../../experiments/2026-10-11-public-release/ASSET-REVIEW.md) and [publication manifest](../../experiments/2026-10-11-public-release/publication-manifest.json) document the current release. This policy records source-specific terms and handling.

## Current handling

| Material | Evidence | Current handling | Public-release preparation |
|---|---|---|---|
| Our prose, code, protocols, aggregate results and source manifests | Written during this project; source dependencies cited | Tracked, subject to the project's repository policy | Choose the project's own license separately; review copied passages, embedded witnesses and source-derived payloads. |
| 1979 and 1982 Helsinki editions | Official entries explicitly link CC BY 4.0 | Original downloaded PDFs remain local; selected 1979 atlas crops and annotations are tracked | Retain author/title/source/license attribution and identify cropping/annotation. Carry forward numerical ambiguities and editorial markers. |
| 1980 Helsinki documentation | Public file; explicit reuse license unverified | Local-only PDF, extracted text and crops; own source notes tracked | Resolve the edition's rights or publish bibliographic pointers and our summaries without the downloaded witness. |
| Mayig source repository | Actual MIT license, Michael Carlson 2024 | Bulk `data/` local; own normalizer and summaries tracked | Preserve the MIT notice for covered copies. Trace any CISI photographs to their separate rights record. |
| Lipi raw data and sequence derivatives | No license found at pinned commit | Local-only raw assets and `data/normalized/` | Obtain a documented reuse basis before including a bulk corpus or record-level derivatives in a public package. Publish acquisition code, pins and aggregates meanwhile. |
| Earlier Indus website source | GPL-3.0 repository license | Local-only acquired SQL/code/assets; own parser tracked | Determine covered components, retain notices and source obligations where applicable; trace imported corpus/images separately. |
| Sproat author XML archive | Explicit Apache 2.0 notices in XML | Source archive and derived JSONL local-only | Include license/notice material and describe compound-token transformation. Review raw bibliography/description fields and any separately sourced assets. |
| CISI photographs, Harappa/HARP images, government-hosted scans, author PDFs, RMRL pages | Public access recorded; explicit open licenses usually unverified | Downloaded PDFs, images, OCR and flipbook configurations local-only | Review each asset's source notice or seek permission when needed. Keep source URLs, page coordinates, hashes and our own observations available. |
| Original project report and chart atlas | Own report; atlas derived from CC BY 1979 | Selected PDF/HTML/PNG exceptions to `.gitignore` | Inspect embedded material and attribution before changing visibility or submitting for publication. |

The current [`.gitignore`](../../.gitignore) excludes all bulk `data/` except its README; PDFs, most images, HTML/TXT/XML downloads; `research/literature/sources/**`; `research/literature/primary/**`; and `research/literature/nonlinguistic_controls/*.jsonl`. Source directories also contain third-party `config.js`, `mySchema.xsd`, an extensionless README and a GIF. The directory exclusions cover these files even where extension rules would miss them.

The nonlinguistic JSONL files retain full source-derived content: symbols, compound members, descriptions, bibliography, timestamps and XML unit paths. Their format is a transformation of the source archive. The source XML's Apache notices are absent from the JSONL itself, so a release should package the notices and [transformation record](../../research/literature/nonlinguistic_controls/flatten_manifest.json) alongside it.

Detailed slot audits and context-prediction JSONL files also remain local. Their target codes or whole sequences can reconstruct the unresolved-rights input corpus. Aggregate benchmark JSON, uncertainty summaries, code, seeds and hashes remain in Git; the local project preserves the detailed records needed for paired reanalysis.

## Asset record to keep

For a new witness, record source title/authors/year, exact URL and access route, retrieval time, local path, byte count, SHA256, file format, page count where relevant, and the observed rights notice. Keep the notice's own URL or a local witness. Record transformations such as extraction, OCR, cropping, reordering, tokenization and manual annotation with parent hashes.

Use one of these statuses: `own-work`, `explicit-license`, `permission-recorded`, `rights-unverified`, or `mixed-assets`. Specify the actual license and scope beside `explicit-license`. Keep the permission record if one exists. For `mixed-assets`, list each component's origin rather than assigning the whole bundle the most permissive component's license.

Our source summaries are useful tracked records, while a JSON field can still contain a copied third-party passage or a full sequence. Review payloads, including generated manifests, rather than relying on extensions. Short source examples should have a purpose, attribution and a checked quotation scope. Large OCR files remain local.

## Before adding material to the public repository

1. Inspect the proposed tracked file list, including exceptions and extensionless files. Check the import manifest and all parent-source records.
2. Separate our writing/code/aggregates from raw inputs, source-derived corpora, photographs and reproduced pages. Review the report's embedded figures and the atlas's attribution.
3. For each third-party asset, record the applicable license or permission and satisfy the recorded notice/attribution requirements. Keep unresolved assets local and publish acquisition instructions or source pointers where useful.
4. Check the release description against what a fresh checkout actually contains. List local-only inputs and their acquisition pins; do not imply that excluded witnesses are downloadable from the repository.
5. Preserve every frozen endpoint and subsequent correction as separate dated files. Public packaging can select material without altering the historical research record.

Repository visibility and external publication remain user decisions. The current private maintenance authorization covers the knowledge base; source handling continues according to this record. No CI/CD or recurring publication process is part of this project.
