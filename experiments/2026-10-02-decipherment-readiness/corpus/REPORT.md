# Corpus readiness for decipherment tests

The project already contains short, paired-surface inscriptions with archaeological source joins that the principal prediction population mostly excludes. It also has enough Lothal sealing evidence to test a specific physical-use restriction on a repeated inscription. The missing input for an authenticated numerical or lexical reading is an independent referent linked to the inscribed object: a documented content count, commodity, named person, office or other outcome that could choose between proposed readings.

This audit inventories actual Indus records and their source witnesses. Generated administrative systems and khipu controls belong to method evaluation and supply no additional Indus observations. The [evidence inventory](inventory-final-2026-10-02/evidence-inventory.json) records counts, schemas and input hashes; [registry coverage](inventory-final-2026-10-02/coverage.json) lists all 101 reviewed IDs. No earlier prediction experiment was rerun.

## Photographs and transcriptions already present

| Resource | Preserved observations | Source relation and usable information |
|---|---|---|
| Lipi normalized observation table | 5,680 rows, 4,695 numeric families, 19,946 code tokens | Derivative sign strings and catalogue metadata, retaining CISI references, visual order and proposed object-family joins. |
| Mayig normalized table | 179 faces from 179 families, 186 annotated lines, 1,003 P-class tokens | A second transcription of a Mohenjo-daro unicorn-seal block; 94 faces have no P000 and zero annotator damage/uncertainty. |
| Older website export | 2,543 rows, 11,135 tokens | A version comparison from the same upstream maintainer as Lipi. Physical-reference joining is needed because numeric IDs changed between versions. |
| Lipi local image assets | 8,722 files, including 8,716 JPG and six PNG files | The upstream image index references 6,570 existing files under 3,318 catalogue keys. It leaves 2,152 files unindexed. |
| Primary editions | Helsinki 1979 corpus, 1980 documentation, 1982 concordance and the CISI 1 scan | Drawings, source conventions and published photographs. The CISI scan repeats the book, and photographic suffixes can show the same physical side more than once. |
| Source-coded object frames | Harappa, Lothal and Kanmer blocks described below | Object-specific captions, registrations, relative dating, physical measurements and inspected figures, each with its observation basis. |

The new exact image-index join finds existing images for 2,944 Lipi rows from 2,507 families, including 1,400 of the 2,107 principal prediction rows. All 179 Mayig families have an indexed image route through the preserved Lipi assets. These are catalogue-key joins; the correct side and image polarity still need their source-specific checks. Hashing the image directory gives 8,709 different byte hashes and 13 duplicate-file excesses. Different image bytes can still show the same object or side. [Image accounting and schema checks](inventory-final-2026-10-02/evidence-inventory.json).

Three purposive image checks confirm that the local assets include a pictorial seal impression, the marked H904 surface and a L124 rear contact witness. The [sample record](filter-supplement-2026-10-02/results.json) retains file hashes and visible features without copying pixels. The wider image collection has no complete source-side, polarity or photograph-versus-drawing annotation. Its present file count therefore describes available witnesses. A physical-object photographic census would require that annotation.

The existing 25-object plate audit and targeted source checks are preserved in [the adjudications](../../../research/corpus/plate_audit/adjudications.json) and [final source notes](../../../research/corpus/FINAL_SOURCE_NOTES.md). Mayig's compatibility arrays connect 396 P classes to 498 Wells IDs. They retain multiple candidate forms, and the [orientation record](../../../research/corpus/orientation_clarification.json) documents reversal of verified single-line visual lists into computational reading order. Multiline and multisided records retain a separate boundary problem.

## What the metadata actually says

The large table provides catalogue assertions. The earlier availability audit found that these fields are copied unchanged across every face in a numeric family. Family counts describe their coverage more directly than repeated face counts. Its [source-basis record](../../../experiments/2026-10-02-six-hour/context-audit/source-assertions.json) documents which Harappa claims were checked against original publications.

| Catalogue field | Rows with an informative value | Families with an informative value |
|---|---:|---:|
| Site | 5,652 | 4,668 |
| CISI reference | 5,019 | 4,075 |
| Excavation identifier | 5,147 | 4,206 |
| Area or section | 4,260 | 3,469 |
| Room or grid | 2,191 | 1,865 |
| Material | 4,706 | 3,871 |
| Object type | 5,679 | 4,694 |
| Time label | 3,067 | 2,380 |
| Period label | 2,318 | 1,887 |
| Phase label | 2,653 | 2,039 |
| Depth | 2,810 | 2,375 |

Area, excavation identifier, depth, room/grid and a chronological label occur together in 1,444 rows from 1,163 families. Of those rows, 1,433 come from Harappa or Mohenjo-daro. Chronology uses site-specific period and phase categories; the HARP account documents dates assigned from context and dates assigned through material, style or technique. The current export lacks a per-record dating-basis field. Its 2,870 missing depth strings and zero-valued dimensions were already identified in the [metadata audit](../../../experiments/2026-10-02-six-hour/context-audit/README.md), which supplies the counting rules used here.

Iconography has 2,506 reported motif rows, 2,635 rows recording literal `None` and 539 missing or unknown rows. `cult` is another retained catalogue field, with graphic/accessory codes such as `Trough` and `SAN`; this review found no independently validated semantic-referent definition for those codes. Object type, material, motif, proposed support and proposed purpose each describe a different part of an object. A `seal` type alone supplies no named user or contents label.

The raw Lipi CSV contains nonempty Sanskrit assignments on 3,826 rows, translations on 1,765 and notes on 47. These are upstream interpretive columns. The [normalizer's field list](../../../research/corpus/normalize_lipi.py) excludes them, along with its listed decipherment files; this audit confirms their absence from the normalized analytical schemas. It retains `class`, which includes categories defined from sign structure. The 355 `VN` rows discussed below are such a nominated candidate pool. Modern catalogue numbers and registrations identify objects; they supply no ancient personal names.

Within the reviewed corpus and the three source frames, there is no authenticated phonetic value, ancient personal-name label, commodity identity or inscription-linked cargo count available as an evaluation answer. Current quantities are counts of surviving objects, impressions and drawn strokes, plus dimensions and three Kanmer masses. The [numerical-premise audit](../../../research/literature/metrology/numerical_source_premises.json) records the unresolved M1383 content-count join and H904's paired-face assumptions. This is the common evidential scope for the tests below.

## Short and paired records excluded by the main benchmark

The main population requires a complete, right-to-left, single-line record with at least three coded signs. It contains 2,107 rows. That filter removes 353 of the 355 `VN` rows: 336 have length two, 17 length one and two length three. Of all 355, 309 meet the clean RTL single-line rule, and only two pass the length threshold. The preserved Wells definition describes VN as sign 700 plus a numeral. This class nominates a short numerical-pattern pool; it provides no externally established numerical value. [New filter counts](filter-supplement-2026-10-02/results.json), [class definition account](../../../research/corpus/CORPUS_REPORT.md).

| Source-defined Harappa group | Published objects | Joined objects and faces | Principal eligible objects |
|---|---:|---:|---:|
| Copied tablets H2218–H2239 | 22 | 22 objects, 66 faces | 0 |
| Sealings and stopper H1719–H1725 | 7 | 6 objects, 8 faces | 0 |
| Stamped vessels H1727–H1766 | 40 | 32 objects, 32 faces | 2 |
| Total | 69 | 60 objects, 106 faces | 2 |

All 66 copied-tablet faces are complete, single-line and labelled RTL, with two coded signs each. Their exclusion is entirely the length rule. Seven of the eight joined sealing faces are incomplete, and the remaining complete face has unspecified direction. The vessel block contains 18 one-sign, ten two-sign and four three-sign faces; direction and preservation reduce it to two eligible objects. These filters serve a sequential prediction task while leaving most of this physical-use evidence outside its population.

The acquired Harappa Figure 4 contains 22 tablet drawings with three faces apiece, source registrations and unit/item joins. Sixteen share excavation unit 8040, described as a clump; two were nearby and four scattered. Their late Period 3B deposition follows the source's wall-and-fill argument. The frame adds two rectangular-seal drawings, one outside-frame comparison drawing and four Beas vessel photographs. Its 24 in-frame objects have source images and 25 caption registrations join across the wider observed frame. [Object-frame report](../../../experiments/2026-10-02-six-hour/harappa-object-frame/README.md).

Native-raster reinspection directly counts seven tablet faces: five groups of three strokes and two groups of four. Specimens 8 and 16 each display the three-face pattern 3, 4, 3. The 66 two-token export records encode those stroke groups as graphic units, so token length and stroke count answer different questions. Keep the source drawing, each face, end orientation and damage region with the paired record. Physical longitudinal orientation and source-to-export face alignment remain unresolved; the [separate scale/pagination correction](../../../experiments/2026-10-02-six-hour/harappa-object-frame/corrections/2026-10-02-scale-and-pagination/README.md) supplies usable figure coordinates.

H904 is a useful exception to the short-record coverage problem. Both of its joined export faces, of lengths four and six, enter the principal population. The Vats J213/no. 477 source join supplies its paired physical identity. The proposed equal quantities across those faces still require their numerical premises and an external quantity test. The current data permit checking the graphics and consistency of a declared equation; they cannot choose its quantity meaning from the arithmetic alone.

## A physical-use hypothesis that can be tested now

Lothal provides the clearest existing matched block. The source table covers 93 clay sealings, 68 of which join to 86 corpus faces. Twenty-nine objects have complete eligible strings, representing nine distinct strings. One eight-sign string, G01, occurs on eleven objects across seven source categories. G02 accounts for another ten objects, all assigned wooden-box supports with an elephant motif in derivative metadata. The source figures show 35 labelled objects, and the existing selected trace audit records twelve. [Coverage](../../../experiments/2026-10-02-six-hour/lothal-physical-use/join-refined/results.json), [recurrence](../../../experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json).

Four G01 objects already have separate image-observation records: L124, L126, L193 and L206. L124 has crossing ribbed rear patches; L126 has a folded, pleated contact surface; L193 has angular adjoining contacts; L206 has a deep concavity and an edge channel. These observations have figure, view and page coordinates. The authors' proposed straw cover, flexible sack, structure and peg are stored separately from those visible geometries. [Trace observations](../../../experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/selected-trace-observations.json).

A bounded hypothesis is that the G01 inscription designates one narrowly specified closure/contact geometry. Its predicted outcome is the same observable contact and fastening configuration on every readable G01 object. A competing hypothesis treats it as a marking reused across several closure operations. Another treats the occurrences as records from one recurring stamp or responsible unit, whose particular identity is still unknown. The acquired images can test the narrow geometric restriction without inventing a commodity or user label. The [current test design](CURRENT-TEST.md) specifies the object unit, blind trace coding, stamp/side checks and treatment of unreadable views.

The strongest present comparison has four inspected G01 objects, with additional views available in the source. Source categories should guide acquisition, while the endpoint records contact geometry and fastening traces. Warehouse inference W1 partly follows stamp recurrence in the publication, so it is unsuitable as an independent answer for a sign-based warehouse classifier. The two largest string groups account for 21 of the 29 eligible objects; they form two recurring evidence groups, rather than 21 independent texts.

Kanmer supplies a complementary four-pendant frame with repeated broad fronts and different marked reverses. Three objects have registrations, trench/layer entries, dimensions and masses; four have numbered reverse photographs. Twenty-five scanner display views are preserved, with no raw mesh acquired. Individual hole-axis, wear or residue measurements and direct laboratory dates are absent. Its current operational test concerns suspension, display and attachment. The proposed passport/user interpretation has no named user or access event in the acquired record. [Kanmer source frame](../../../experiments/2026-10-02-six-hour/kanmer-physical-use/README.md), [source continuation](../../../experiments/2026-10-02-six-hour/kanmer-physical-use/source-continuation-2026-10-02/REPORT.md).

The most useful next semantic acquisition would join one of these fixed physical frames to an independently known referent. For numerical proposals, that means an inscription-linked count or measured inventory that survives uncertainty about fragment reconstruction and object membership. For actor or office labels, it means a repeated inscription linked to an independently identified administrative actor or documented use event. The existing source coordinates, registers and short-face preservation make those acquisitions specific.
