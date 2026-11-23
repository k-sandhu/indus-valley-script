# Data update: physical numerical anchors and Lothal attachment traces

Date: 2026-11-23  
Package: `experiments/2026-11-23-physical-anchors-lothal/`

## 1. New structured records produced

This package adds no new inscribed objects to the global corpus count (4,695 provisional objects and 5,680 faces in `data/normalized/lipi_observed_faces.jsonl`). It adds verified object-level metadata, plate readings, and physical reverse codings for two numerical anchors (`H-904` and `M-1383`) and for all 93 Lothal clay sealings (`L-124` through `L-216`):

| File | Scope | Content |
|---|---|---|
| `anchors-audit-v1.json` | `H-904` and `M-1383` | Primary plate readings, CISI 2 basic data reconciliations, Vats 1940 and Vidale 1987 and 1990 comparisons, Lipi corpus uniqueness counts, and exact algebraic range sensitivities |
| `lothal-attachments-v1.csv` | 93 Lothal sealings (`L-124` to `L-216`) | CISI 1 FC, excavation, and museum numbers; Table 1 impression counts and prose conflicts; Frenez and Tosi 12-level physical type; 6-class and 5-class diagnostic reverse taxonomy; binary wood and mobility encodings; context code and context basis; prose reverse evidence; and Rao 1985 discrepancy flags |
| `lothal-test-v1.json` | 68 joined Lothal objects (55 diagnostic Pop B; 26 diagnostic Pop A) | Die and impression component partitions, component-block permutation results, Leave-One-Component-Out cross-validation results, sensitivity controls, and within-component dispersion metrics |
| `verification-v1.json` | Independent checks | Automated consistency checks across both Table 1 transcription passes, taxonomy recomputation, anti-leakage component partitioning, Diophantine arithmetic, corpus uniqueness, and file integrity |

## 2. Primary source reconciliations and metadata clarifications

1. **`H-904` (Lipi family `1786`, Vats 1940 no. 477, find `J213`, Mound D):**
   - CISI 2 printed p. 338 (PDF p. 373) and the Lipi crops `H-904_A.jpg` and `H-904_B.jpg` resolve the short strokes on Face A that were previously unreadable in Vats 1940 Plate XCVI no. 477. Face A reads `002-840-032-740` (two short strokes and two long strokes flanking `840`, followed by `740`). Face B reads `817-368-645-900-033-700` (three full-height long strokes `033` between `900` and `700`).
   - Visual reading of CISI 2 basic data printed p. 444 (PDF p. 479) resolves bracketed digits from the automated pilot extract: FC `3477` (matching 3000 plus Vats 477), excavation `J 213`, Harappa Museum `HM 434` (National Museum of Pakistan accession `52.10xx`), photograph `P 1214`.
2. **`M-1383` (Lipi family `3679`, excavation `MN 82a`):**
   - CISI 2 plate printed p. 182 (PDF p. 217, `M-1383 A (1)` at 15% scale, `M-1383 A (2)`, and `M-1383 B`) resolves the prior metadata discrepancy between Lipi's `TAG:R` clay tag classification and Fuls's stoneware-bangle firing pot description. `M-1383` is a closed cylindrical stoneware-bangle firing container (saggar) from the 1982 Moneer area fieldwork (`MN 82a`, Excavation Branch Karachi `EXB`, Aachen and *Vergessene Städte am Indus* p. 272, C 77) with a unicorn-stamped clay sealing applied directly at its mouth.
   - Visual inspection of `M-1383 A (2)` confirms `740-575-017-031` clearly on the intact left portion of the impression and a diagonal fracture with erosion across the first three reading-order signs (`920-060-741`) on the right.
3. **`L-206` (excavation `2077`, museum `LTH SRG 1203`, FC `6016`) and Lothal discrepancies:**
   - Rao 1985 (*Lothal: A Harappan Port Town (1955–62)*, Vol. II, MASI 78, printed pp. 319, 321, 326, and Plate CLXII D) catalogues `2077` from Phase III, SRG 3, GX 10, layer 2, depth 3 ft 4 in, describing two seal impressions on the obverse and a deep groove left by a stick or reed on the reverse. CISI 1 printed p. 286 (`L-206 A 1-2`) and Frenez and Tosi 2005 Figure 3 (printed p. 98) depict the same deep smooth curved concavity.
   - CISI 1 reverse plates `L-124 B` (p. 268) and `L-190 B` and `L-190 F` (p. 282) supply sharper primary reverse views for two additional `G01` specimens alongside `L-206`.
   - `lothal-attachments-v1.csv` explicitly flags eight Rao 1985 versus Frenez and Tosi 2005 discrepancies (`L-125`, `L-126`, `L-128`, `L-161`, `L-164`, `L-190`, `L-193`, and `L-206`), including the Plate CLXI F conflict between `1830` (`L-161`) and `1864` (`L-164`).

## 3. Specific missing sources identified for `knowledge/DATA.md`

No local source closes the remaining historical and counting gaps below. Maintainers can fold these exact targets into `knowledge/DATA.md` and `data/MANIFEST.json`:

1. **For `Q-0011` (`H-904` historical ID `ICIT 3786`):** Fuls (2020 and 2023) Figure 16 pixels (PDF p. 16 / printed p. 30 of the 2023 ResearchGate posting, blocked by HTTP 403 and device check) or an authenticated ICIT database crosswalk (HTTP 401; `Q-1011`).
2. **For `Q-0012` (`M-1383` bangle fragment and reconstructed bangle count):**
   - Halim, M. A. and M. Vidale (1984), *Kilns, Bangles and Coated Vessels: Ceramic Production in Closed Containers at Moenjodaro*, in M. Jansen and G. Urban (eds.), *Interim Reports Vol. 1*, Aachen, pp. 63–97 (not held; we hold only *Interim Reports Vol. 2*, 1987).
   - *Vergessene Städte am Indus: Frühe Kulturen in Pakistan vom 8.–2. Jahrtausend v. Chr.* (Mainz, 1987), p. 272, catalogue item C 77 (cited by CISI 2 p. 439 for `M-1383 A (1)`; not held).
   - Wells, B. K. (2015), *The Archaeology and Epigraphy of Indus Writing*, Archaeopress, pp. 94–95 (only the publisher preface sample is held locally; `Q-1011`).
3. **For Lothal (`Q-0019` and attachment testing):** Unpictured reverses of the remaining 58 Lothal sealings absent from Frenez and Tosi Figures 3–7, plus the missing Lipi transcriptions for elephant-cohort sealings `L-171` and `L-172` and the other 23 unjoined Lothal sealings.

## 4. Local-only rendered plate extracts (not tracked in Git)

All rendered page extracts and zoomed plate crops derived from local copyright-unresolved scans are stored locally under `data/raw/2026-11-23-physical-anchors-lothal/` (physical path `D:\projects\indus_valley_script\data\raw\2026-11-23-physical-anchors-lothal\`):

| File | Bytes | SHA-256 prefix | Source PDF and page |
|---|---:|---|---|
| `cisi2_H904_plate_p373.png` | 2,469,842 | `f2bc56c7ad1c5a7e` | `cisi2-archive.pdf` PDF p. 373 (printed p. 338) |
| `cisi2_H904_plate_zoom.png` | 338,148 | `031f3ccb7a84b5aa` | `cisi2-archive.pdf` PDF p. 373 zoom of `H-904 A` and `H-904 B` |
| `cisi2_H904_basic_p479.png` | 2,209,208 | `3a6be747465d7804` | `cisi2-archive.pdf` PDF p. 479 (printed p. 444) |
| `cisi2_H904_basic_zoom.png` | 280,039 | `0ca73b5382fd0861` | `cisi2-archive.pdf` PDF p. 479 zoom of `H-904` row |
| `cisi2_M1383_plate_p217.png` | 2,768,911 | `0ffb4b422ab02c90` | `cisi2-archive.pdf` PDF p. 217 (printed p. 182) |
| `cisi2_M1383_basic_p474.png` | 2,509,318 | `c6762de3f46c7dbe` | `cisi2-archive.pdf` PDF p. 474 (printed p. 439) |
| `cisi2_M1383_basic_zoom.png` | 354,558 | `ff4335bdee7c2ac1` | `cisi2-archive.pdf` PDF p. 474 zoom of `M-1383` row |
| `vidale_1990_fig7_p10.png` | 2,573,350 | `26dd587b4d9bc74b` | `vidale_stoneware_primary.pdf` PDF p. 10 (Figs. 6–7) |
| `vidale_primary_p1.png` to `p3.png` | 1,012,582 | `c024485a`, `272a91dc`, `737cf6d1` | `vidale_stoneware_primary.pdf` PDF pp. 1–3 |
| `cisi1_L206_plate_p322.png` | 1,020,808 | `c16bac680519946e` | `joshi_parpola_1987_cisi1.pdf` PDF p. 322 (printed p. 286) |
| `rao1985_pdf72.png`, `pdf76.png`–`pdf79.png` | 3,432,553 | `62b206fe`..`a7aafe4a` | `rao1985lothal-part2.pdf` PDF pp. 72, 76–79 (printed pp. 321, 325–328) |
| `rao1985_plate_p491.png`–`p493.png` | 1,561,211 | `bd237317`, `6d1a7962`, `bfce4471` | `rao1985lothal-part2.pdf` PDF pp. 491–493 (Plates CLXI–CLXIII) |
