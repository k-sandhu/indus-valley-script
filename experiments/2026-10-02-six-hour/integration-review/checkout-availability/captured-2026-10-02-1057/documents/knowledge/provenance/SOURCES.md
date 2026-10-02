# Sources and local witnesses

This inventory records the inputs acquired during the October 1–2, 2026 investigation. The [import manifest](../../archive/2026-10-01-investigation/import-manifest.json) preserves 16,284 files and 1,523,734,911 bytes from the original workspace. Paths below are relative to this repository. A source marked **local-only** exists in the preserved local project but is excluded from Git; its link will require that local copy.

The inventory separates a publication, its acquired file, its transcription and our analysis. Each can have a different author, version and reuse status. Asset-level decisions are recorded in [REDISTRIBUTION.md](REDISTRIBUTION.md). Catalogue conventions and matching rules are in [catalogue-caveats.md](catalogue-caveats.md).

## Machine-readable inputs

| Source and pin | Acquired contents | Local paths and evidence | Recorded reuse status |
|---|---|---|---|
| [Mayig](https://github.com/mayig/indus-valley-script-corpus), `ad2f1e218a34b8c33c57de0d6cb8d99272765bbb` | 179 Mohenjo-daro unicorn seal faces, 186 lines, 1,003 P-class tokens; 396 schema classes and 498 Wells candidate IDs | Local-only `data/mayig/`; [summary](../../data/normalized/mayig_summary.json), [file hashes](../../data/normalized/mayig_file_hashes.json), [normalizer](../../research/corpus/normalize_mayig.py) | Actual upstream `LICENSE`: MIT, Michael Carlson 2024. Photograph rights require their own source record. |
| [Lipi](https://github.com/yajnadevam/lipi), `fc8813a52e183d19c441631dc26c33a4dccbea39` | 5,680 rows, 4,695 numeric families, 5,804 parts, 19,946 tokens, 714 codes | Local-only `data/lipi/src/assets/data/inscriptions.csv`; [summary](../../data/normalized/lipi_summary.json), [normalizer](../../research/corpus/normalize_lipi.py) | No `LICENSE` found at this pin. Raw and source-derived sequence data remain local-only. |
| [Earlier Indus website export](https://github.com/yajnadevam/indus-website), `2434249618b1e74de3f26d28b90dfde093c3dd94` | 2,543 observational rows, 11,135 tokens, 1,903 unique sequences in SQL | Local-only `data/indus_website/`; [summary](../../data/normalized/indus_website_summary.json), [text-only SQL parser](../../research/corpus/normalize_indus_website.py) | Upstream GPL-3.0. Coverage of particular imported corpus/image assets needs source review. |

The imported directories omit their nested `.git` folders. Their recorded pins come from the original acquisition, not from Git metadata retained in this repository. The normalization scripts call `git -C ... rev-parse HEAD`; running them unchanged on an imported folder could resolve the parent research repository instead. Reacquire a fresh upstream clone at the recorded commit and verify input hashes before rerunning. Preserve the imported inputs and existing summaries.

Lipi's proposed translations, Sanskrit fields, notes and interpretation tables were excluded from the observational extraction. The older SQL includes destructive statements and was parsed as text. Both exports have the same upstream maintainer; the older one supplies a version comparison. Mayig supplies another annotation of shared CISI photographs.

| Pinned input or derivative | SHA256 |
|---|---|
| Lipi raw `inscriptions.csv`, 1,210,601 bytes | `c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c` |
| Earlier `population-script.sql` | `04d5a2c0f239458e4151d006b10c6ace638ee63f961083cf0331fd23309d2a24` |
| `data/normalized/lipi_observed_faces.jsonl` | `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db` |
| `data/normalized/lipi_clean_rtl_singleline.jsonl` | `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8` |
| `data/normalized/mayig_faces.jsonl` | `033b8e40d4fdfa1f4a2c51390c8fd5f95eae35c6c835b47776c969ab947a19b7` |
| `data/normalized/mayig_sign_schema.json` | `a3c129c90efc8e339f5ddf9442d13e387ced1a9047fb6b1c5ab7e179b6a4dc0e` |
| `data/normalized/mayig_wells_class_crosswalk.json` | `9fea45e16be1218d148473dad440f806a2f0c12c954c79347db2584324cc1f71` |

These sequence derivatives remain local-only under the current repository policy. Our normalizers, aggregate summaries and source-audit prose are retained separately.

## Helsinki primary editions

All three PDFs were acquired unchanged. Their [provenance records](../../research/corpus/primary/) describe URLs, retrieval methods, bytes, hashes, page counts and transformations.

| Edition | Official access and local witness | Acquired file | Reuse evidence |
|---|---|---|---|
| Koskenniemi and Parpola 1979, *Corpus of Texts in the Indus Script* | [University of Helsinki entry](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [persistent handle](http://hdl.handle.net/10138/342677); local-only [PDF](../../research/corpus/primary/koskenniemi_parpola1979.pdf), [manifest](../../research/corpus/primary/koskenniemi_parpola1979_provenance.json) | 16,935,355 bytes; 180 PDF pages including repository cover, 179 book pages | Official entry explicitly links [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) for the final published version. |
| Koskenniemi and Parpola 1980, *Documentation and Duplicates* | [Public Helsinki file](https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf); local-only [PDF](../../research/corpus/primary/koskenniemi_parpola1980.pdf), [manifest](../../research/corpus/primary/koskenniemi_parpola1980_provenance.json) | 8,143,483 bytes; 98 pages | Explicit reuse license unverified. |
| Koskenniemi and Parpola 1982, *A Concordance to the Texts in the Indus Script* | [Official entry, whose URL spells “concordande”](https://researchportal.helsinki.fi/en/publications/a-concordande-to-the-texts-in-the-indus-script/), [public PDF](https://tuhat.helsinki.fi/ws/portalfiles/portal/209717802/indus_concordance_1982.pdf); local-only [PDF](../../research/corpus/primary/koskenniemi_parpola1982.pdf), [manifest](../../research/corpus/primary/koskenniemi_parpola1982_provenance.json) | 16,767,043 bytes; 201 pages | Official entry explicitly links CC BY 4.0. |

| Edition | SHA256 |
|---|---|
| 1979 | `7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27` |
| 1980 | `0ced4102dc6197246df6c84e4b730ed380f41085a4a1ea8dd8a6459332da37d1` |
| 1982 | `07d24564cd3abf23620a3cd9d417c9931c9d3e1aafb204d7c4fd49b4022d043c` |

The old 1979 portal file returned 403 to direct requests; `downloadMedia` timed out. Clicking the ordinary public portal link in Chrome downloaded `indus_corpus_1979.pdf` through HELDA, and the completed file was copied unchanged. The HELDA download-page URL returned HTML to `urllib`. The 1980 and 1982 public PDF links worked directly. These routes are documented so a failed HTTP request is distinguishable from an unavailable publication.

The 1979 corpus prints plotted glyphs. Its OCR layer supplies some usable prose, but glyph OCR produces punctuation, Latin letters and digits. The 1982 file is image-only; its tiny extracted text file contains page separators. The [extraction assessment](../../research/corpus/primary/1979_extraction_assessment.md) and local-only [1979](../../data/normalized/koskenniemi1979_definitions.json)/[1980 definitions](../../data/normalized/koskenniemi1980_definitions.json) preserve verified editorial rules.

The [687-cell atlas](../../output/chart_atlas/index.html) is a cropped and manually annotated derivative of the 1979 CC BY edition. Credit Koskenniemi and Parpola, the University of Helsinki source, and CC BY 4.0; describe the cropping and numerical annotation. The [consolidated audit](../../research/corpus/primary/chart_complete/consolidated_atlas_audit.json) verifies all claimed crop pixels and source-table coverage. The [reference](../../research/chart_reference/manual_numeric_reference.json) retains 16 lower-code ambiguities. Earlier frozen references remain under `research/visual_digitization/`.

## Photographic sources and author reproductions

The files and crops in this table are local-only. Source pages and observations are recorded in the linked audits.

| Source | Access, local file and use | Acquisition/rights record |
|---|---|---|
| Joshi and Parpola 1987, CISI volume 1 | [IGNCA scan](https://ignca.gov.in/Asi_data/76884.pdf); [local PDF](../../research/literature/sources/joshi_parpola_1987_cisi1.pdf). Used for the 25-object audit, fish/stroke comparison and missing-slot search. | 31,508,998 bytes, 862 pages; explicit reuse license unverified. [Page-image audit](../../research/literature/cisi1_page_image_audit.json) and [counting/errata notes](../../research/literature/cisi1_counting_and_errata.md). |
| Fuls 2010 database help and labelled example | [Help PDF](https://www.epigraphica.de/indus/help_onlinedatabase.pdf), [public menu](https://www.epigraphica.de/indus/menueindus.htm); [local help](../../research/corpus/primary/fuls2010_help.pdf). M1088 photograph and four sign images verify displayed order. | 827,406-byte help, 16 pages; reuse license unverified. [Image manifest](../../research/corpus/primary/fuls_menu_image_provenance.json), [orientation clarification](../../research/corpus/orientation_clarification.json). |
| Parpola 2011 unicorn study | [Author PDF at Harappa](https://www.harappa.com/sites/default/files/pdf/Parpola_A_2011_unicorn%20%281%29.pdf); [local PDF](../../research/corpus/primary/parpola2011_unicorn.pdf). Fig. 15, printed 142/PDF 19 reproduces H697B after CISI2:316. | 3,343,015 bytes, 65 pages. Direct request 403; visible public PDF download succeeded. [Manifest](../../research/corpus/primary/parpola2011_unicorn_provenance.json). Reuse license unverified. |
| Kenoyer and Meadow 2010, *Inscribed Objects from Harappa* excerpt | [Harappa PDF](https://www.harappa.com/sites/default/files/pdf/KenoyerMeadow%202010%20Inscribed%20Objects%20from%20Harappa.pdf); [local excerpt](../../research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf). Excavation identifiers and secondary-dump qualification. | 276,900 bytes, 15 pages, no figures. Direct request 403; visible download succeeded. [Manifest](../../research/corpus/primary/kenoyer_meadow2010_inscribed_objects_provenance.json). Reuse license unverified. |
| Parpola 2020 bone-rod paper | [HELDA content](https://helda.helsinki.fi/server/api/core/bitstreams/5994c972-f2c5-4520-954d-8a9b63d27b25/content); [local PDF](../../research/corpus/primary/parpola2020_bone_rods.pdf). H697 comparison is prose, rather than a newly acquired obverse photograph. | 374,402 bytes, 7 pages; [manifest](../../research/corpus/primary/parpola2020_bone_rods_provenance.json). A source URL includes 2019 although the publication is 2020. Reuse license unverified. |
| Meadow and Kenoyer 2000, tiny seals | Literature-acquired primary PDF under `research/literature/sources/`; Fig. 4 specimen 18, PDF 15–16 identifies H95-2613/6560-01. [H2238 audit](../../research/corpus/plate_audit/H2238_face_audit.json). | Source-file SHA256 below; graphic middle-face observation verified, opposite-face count unresolved. Reuse license unverified. |
| HARP public tablet photographs | [Life and death slide](https://www.harappa.com/slide/life-and-death-harappan-seals-and-tablets), [three groups](https://www.harappa.com/indus2/149.html); local images `research/corpus/plate_audit/H2238_gallery/`. | Photographs credited to HARP/Meadow/Kenoyer. Public captions lack specimen IDs. [Gallery manifest](../../research/corpus/plate_audit/H2238_gallery/gallery_provenance_observations.json). Explicit open license unverified. |

| Acquired witness | SHA256 |
|---|---|
| CISI1 PDF | `47a4da4227cfb7baa56d6a561e25797225499d0ec54f5a702a82c67ab4746d4d` |
| Fuls 2010 help | `800c650a88743eb53b9816fb42fdec517c4c5c5172059f69899c73d609fe6556` |
| Parpola 2011 | `a10b375beea210a5b2b8ae3a5930ecdf1c0e64a9d8b52b7b84be14a591fec468` |
| Kenoyer/Meadow 2010 excerpt | `7a8fea92fbc7a8810ad9d47e5740a83e4896bc46facd1ec6eb7f51c329ecf2d9` |
| Parpola 2020 bone rods | `5beefb15d0d87e6d2a57df054aaf9eeb56002979871f1dc8aedc1257adfa2241` |
| Meadow/Kenoyer 2000 tiny seals | `967ebcb058e5611de4089facba852adac418108adfc36bf793d0588ba0d8b751` |
| HARP `79_3.jpg` | `8407bfa8212a781c9dfd5399ad6e3976c4e2e254585478e099c32a46cb69ee05` |
| HARP `harappa-tablets-group.jpg` | `449a1e91aa74228f396f40d50b79ee126550ff31bee4f182fcad52b661bc88ff` |

## Literature archive and numerical anchors

The [retrieval log](../../research/literature/source_retrieval_log.json) gives requested URL, retrieval time, HTTP status, local filename, magic bytes, hash, page count and extraction outcome. The [identity index](../../research/literature/source_identity_index.json) preserves title checks, including wrong-file acquisitions. It is the detailed inventory for Rao, Yadav, Sinha, Sproat, Mukhopadhyay, Parpola, Mahadevan and subsequent papers. License review remains asset-specific; an author-posted PDF and a successful download record establish access.

| Archive group | Evidence and status |
|---|---|
| Rao Science and PNAS author PDFs | [Science](https://homes.cs.washington.edu/~rao/ScienceIndus.pdf), [PNAS](https://homes.cs.washington.edu/~rao/PNASIndus.pdf). Our `primary/rao2009_science.pdf` and `rao2009_pnas.pdf` hash identically to literature's copies: respectively `70e0a332f9521b1f4f1d4c2cb94f7a5a49ec05080aebc807dcca8235302ea3e5` and `642d316d4635a958e8cba240572e8aa9d25c5b520e37a487a2157bb0043345d5`. Independently coded full research inputs were not acquired from their supplements. |
| RMRL scans and 2025 bulletin | Local-only `research/literature/sources/rmrl/` holds public flipbook pages/configurations and a URL/hash manifest. Current [bulletin 6 PDF](https://rmrl-site-files.s3.us-east-1.amazonaws.com/PDFFIles/bulletin/bulletin-No-6-June-2025.pdf), 50 pages, SHA256 `af5f67d803a4c8bdda75c27bf113fd67f32cf2a88a680fc5530e3aa334e86a87`. Earlier guessed bulletin URL returned 404. Explicit reuse license unverified. |
| Airavati 2008 | [Publisher PDF](http://www.varalaaru.com/airavati/airavati_final_high.pdf), local-only `research/literature/sources/airavati_2008.pdf`, 503 pages. SHA256 `2d30c6dcc426925b03da8e63dd7b861148c092f93e111f72ec9479c744f20503`. Wells's classification chapter is printed 275–288. Explicit reuse license unverified. |
| Vats 1940 and Jansen/Urban 1987 | Government scans under `research/literature/sources/`. [Final hashes](../../research/literature/metrology/primary_numeric/final_source_hashes.json) record two Vats volumes and the interim report. H904 Plate XCVI no. 477 and text printed 349 identify J213, area D. Vidale's firing-installation chapter supplies a reconstruction but leaves the M1383 inscription/content join unresolved. [Source-premise audit](../../research/literature/metrology/numerical_source_premises.json). Explicit reuse licenses unverified. |
| Fuls numerical proposal | The inspected [2023 author reprint](https://www.researchgate.net/profile/Andreas-Fuls/publication/373522958_Ancient_Writing_and_Modern_Technologies_-_Structural_Analysis_of_Numerical_Indus_Inscriptions/links/64f04b160f7ab20a8667db0b/Ancient-Writing-and-Modern-Technologies-Structural-Analysis-of-Numerical-Indus-Inscriptions.pdf) has 34 PDF pages, printed 15–48. Indexed text was inspected; a complete local Fig. 16 witness was not acquired. Historical ICIT3786 correspondence remains open. [Final source review](../../research/literature/report_source_review_final.md). |

## Sproat comparison corpora

[Author archive](https://richardsproat.com/data/non-linguistic-symbols/corpora.zip): ZIP SHA256 `fb50ff5acb5221ba75e134cc7a36619e1d990b5680ad8681bcde5c447b6b8f73`. A generic downloader saved the ZIP as `research/literature/sources/sproat_2014_corpora.html`; magic bytes and archive validity identify the format. Extracted XML, schema and extensionless README are local-only under `research/literature/sources/sproat_2014_corpora/`. XML carries explicit Apache 2.0 notices; the [manifest](../../research/literature/sources/sproat_2014_corpora/manifest.json) preserves hashes.

The local-only JSONL derivatives under `research/literature/nonlinguistic_controls/` preserve complete source symbol sequences, descriptions, bibliography and unit paths. Weather has 10,142 five-day forecasts and 50,710 tokens; the compound-preserving totem encoding retains 180 strings and 878 units. Their [flattening manifest](../../research/literature/nonlinguistic_controls/flatten_manifest.json) records exclusions and transformation hashes; [README](../../research/literature/nonlinguistic_controls/README.md) explains order and dependence. Releasing these derivatives needs retained source notices and an explicit transformation description. The XML license record covers this archive; source photographs and underlying cited books are separate assets.

## Gaps carried forward

No open independently coded complete EBUDS/Mahadevan/Wells corpus was acquired through the searched primary supplements. ICIT bulk access required registration. CISI2/3 complete photographic volumes were not acquired. Several author PDFs were accessible only as indexed text or browser views, so source coordinates may refer to text inspection rather than figure pixels. The retrospective records each affected object and acquisition route.

The new [Kenoyer/Meadow HARP introduction](https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf) is a 17-page lead distinct from our 15-page excerpt. Jamison, Uesugi and Yamaguchi's 2023 unicorn study, DOI `10.1016/j.ara.2023.100486`, is a context-coding lead. The community-suggested Tell Jokha TJ17-PRO-S56 object requires inspection of Fig. 6.61 in the SAHI 2017 report before entering an archaeological table. These were leads at handoff, with no claimed object verification here.

## October 2 source additions

| Source branch | Acquisition, observations and reuse record |
|---|---|
| Harappa figure scale and pagination | [Separate correction](../../experiments/2026-10-02-six-hour/harappa-object-frame/corrections/2026-10-02-scale-and-pagination/README.md) preserves the original source hash and old endpoints. Figure 4 has a 0–3 cm bar; author-copy and book page numbers are mapped explicitly. |
| Kanmer excavation and scanner reports | [Source register](../../experiments/2026-10-02-six-hour/kanmer-physical-use/source-register.json), [source account](../../experiments/2026-10-02-six-hour/kanmer-physical-use/SOURCES.md) and [provenance](../../experiments/2026-10-02-six-hour/kanmer-physical-use/PROVENANCE.md) preserve the 2010/2011/2012/2023 witnesses, page coordinates and reuse observations. Original PDFs, images, object ledger and detailed annotations are local-only. |
| Kanmer original bibliography and final-volume holding | [Separate source amendment](../../experiments/2026-10-02-six-hour/kanmer-physical-use/source-continuation-2026-10-02/SOURCES.md) preserves original journal contents, RIHN annual reports, an author CV/proof and institutional catalogue coordinates. It adds publication dates and an exact acquisition packet without changing specimen joins. Raw witnesses and detailed ledgers remain local. |
| Puruchuco numerical control | [Acquisition](../../experiments/2026-10-02-six-hour/khipu-control/acquisition.json) and [source audit](../../experiments/2026-10-02-six-hour/khipu-control/SOURCE_AUDIT.md) pin the repository/database and guide comparison. Repository code/docs have MIT terms; the database's data licence remains unresolved. Raw database, guide pages and detailed source-derived vectors stay local. Published target values were exposed during source review and are labelled a reference replication. |
| Contact-mechanics and experimental archaeology methods | [Sources](../../experiments/2026-10-02-six-hour/stamp-geometry/SOURCES.md), [acquisition](../../experiments/2026-10-02-six-hour/stamp-geometry/acquisition.json) and [provenance](../../experiments/2026-10-02-six-hour/stamp-geometry/source-provenance.json). Project-generated figures and simulations are tracked; acquired papers and artifact images remain local. |
| Consensus fitting method | [RANSAC acquisition](../../experiments/2026-10-02-six-hour/khipu-control/robust-decoder/source-acquisition.json) and [source review](../../experiments/2026-10-02-six-hour/khipu-control/robust-decoder/source-review.json) identify the primary 1981 method and exact pages. Source PDFs stay local; generated worlds, witnesses and code are project work. |
