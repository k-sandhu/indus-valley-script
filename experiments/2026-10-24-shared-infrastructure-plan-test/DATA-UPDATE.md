# Proposed data integration

This package adds plan measurements and object-context eligibility records for Q-0040 and the C-0017 to C-0019 proposals. The six-town primary frame is Farmana, Kanmer, Banawali, Harappa, Dholavira and Lothal. Mohenjo-daro is a declared supplementary source-availability control. The earlier Q-1032 axes and horizon results remain at their original endpoints. They supply regional site index points only; no true-north bearing or horizon is transferred to a small excavation feature.

## Coverage added

| Record | Added coverage | Meaning of the denominator |
|---|---|---|
| Source-use register | 42 uses; 35 distinct recorded payload hashes | Repeated editions, uses and image records are not independent publications or excavation observations |
| Measured plan quantities | 18: seventeen lengths and one angle | Local source-plan readings, including one published-dimension check; not eighteen independent episodes |
| Architectural cases | 29: fourteen eastern and fifteen western cases | Authored sequence or source-eligibility assessments with overlapping views and source-event groups |
| Geometric registration | One descriptive pair, two fitted panels | Independent grid fit in Harappa Area C; comparable earlier partition exposure remains missing |
| Context assessments | 32 frozen assessments | Object and cohort assessments can overlap; no claim of 32 physical objects |
| Dating entries | 78; 76 with a determination or TL result, two paragraph entries lacking raw BP | Published entries preserve repeated specimens, lab methods and source conventions; not 78 independently dated repairs |
| Dholavira row gates | All 225 inherited rows, unchanged | Accession strings and literal field gates; physical aliases and original-use events remain unadjudicated |
| Lothal provenance audit | All 93 Table 1 rows independently recounted | Table labels remain distinct from prose totals and older populations |
| Qualified comparisons | Zero complete persistence episodes; zero matched C-0018/C-0019 pairs | Eligibility under this fixed source frame; no archaeological absence claim |

The authoritative aggregate is `run-v1.json`, SHA-256 `1217731e249aa6cb51eaeebc9a7346a2ec291dccbbdd6fff7616847d199ddd3d`. It records module-qualified source IDs and every input hash. The context prejoin freeze is `e574bfea349db809810cdb8b7fb06f832af41549f79f0b2de5e271fca7faddec`. Post-freeze clarifications and review leads remain separate, without recoding its counts.

## Sources and access changes

The eastern module adds a bounded public preview of the original Kanmer annual report, with title and copyright evidence for 2011. The full report remains unavailable. It records 25 frozen feature candidates in five windows, four failed pair candidates, seven retained measurements, two unmeasured candidates and one angle withdrawn after visual review. Its source and acquisition manifests preserve the individual preview-page routes and hashes.

The western module adds eight HARP source images and their eight caption pages. It audits 23 original panels, supplies twelve annotated boards, and recovers Lothal Figure 17 from the held text scan. The complete Lothal street-network plate and matched earlier/later Block B plans remain missing. A title search, alternate OCR failure and crop repairs are preserved in its acquisition and clarification records.

The context module reuses twenty held source records, including inaccessible or mismatched routes retained as such. It produces seventeen local source panels, a dated-sample register, formation assessments and bounded plan anchors. The file named kanmer2013.pdf is publisher HTML, and an inherited Kanmer Chapter 8 viewer shell is not the chapter. Those files do not become acquired full articles. Dholavira's usable field counts are 211 stratum and 201 depth labels; `CLARIFICATION-01.json` explains the different counts obtained by retaining Unst. markers and preserves all source cells.

The supplementary Mohenjo-daro module reuses Mackay's original plan scan and acquires the official Green, Alam and Petrie 2026 additional-files archive. Its summary CSV recovers published 80% Gini intervals, while individual house polygons and street vectors remain unavailable. Mackay's fifth fixed street chord is unmeasurable. Both the failed first render selection and the two plausible Plate XIX edges remain available locally.

Method and map records add a local QGIS 3.44 documentation page and Natural Earth 1:110 million land GeoJSON. Historic England method guidance and Natural Earth public-domain terms were read through the web tool; direct-fetch failures remain recorded. The map uses a modern land outline without reconstructed ancient rivers or coastlines.

## Fields to retain

Plan records preserve source and panel identity, PDF index, printed page and figure, source hash, crop and rotation, image dimensions, local feature identity, source phase namespace, scale convention, north reference, reading radius, quantity, conditional bounds, source-survey uncertainty and explicit ineligibility reasons. Detailed coordinates and acquired pixels remain local. The recorded north references include downward-pointing north in two Dholavira plans and a rotated East Gate display crop.

Context records preserve registration and alias status, material, deposit, formation, named feature, source phase, dating evidence IDs, rejected date candidates, missing links and the qualified-pair gate. Date records retain laboratory and specimen identity, material, reported determination, calibration convention, source intervals, relation to construction, intrusion and residuality concerns. Original use, manufacture, reuse and final discard remain distinct. No sign meaning or authenticated sound value is added.

## Storage and integration

Logical root: `data/raw/2026-10-24-shared-infrastructure-plan-test/`. Physical root: `D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/`. The C: checkout reaches the same directory through its existing junction. Full sources, OCR, table-row derivatives, traces, rendered plans, images, PDF, presentation, offline explorer and delivery archives stay under that D: root. The checkout retains authored prose, code, aggregate tables, source manifests and review records.

No global object-count gain is claimed. The 225 Dholavira rows were already extracted; this run adds computable eligibility gates and a recount, without adding 225 newly discovered objects. Maintainers can integrate this coverage note and the module acquisition manifests into DATA.md and MANIFEST.json after review. The shared documents, generated knowledge map, conjecture cards and spending ledger are not edited by this contribution.
