# Data update proposal: fresh post-catalogue cohort certification

Date: 23 November 2026. Package: `experiments/2026-11-23-fresh-cohort-certification/`. Prepared for maintainer review; no repository-wide file (`knowledge/DATA.md`, `data/MANIFEST.json`, `knowledge/MAP.md`, `knowledge/experiments/registry.json` or `bench/spent.json`) was edited by this run.

## New sources acquired

None. This package operated strictly under the non-purchase scope of GitHub Issue #20 (`Q-1014` and `Q-1026`), auditing already-held local PDFs and registers.

## New derived files and storage paths

| Logical path | Physical path on this workstation | Tracked | Content |
|---|---|---|---|
| `experiments/2026-11-23-fresh-cohort-certification/fresh-cohort-v1.json` | Checkout | Yes | Full 503-row certification record with cross-corpus checks, plate-audit results and exposure scope |
| `experiments/2026-11-23-fresh-cohort-certification/fresh-cohort-v1.csv` | Checkout | Yes | Flat 503-row certification table |
| `experiments/2026-11-23-fresh-cohort-certification/summary-v1.json` | Checkout | Yes | Tier counts, 503 and 358 accounting, P1–P4 power tables and 19 pinned input hashes |
| `experiments/2026-11-23-fresh-cohort-certification/verification-v1.json` | Checkout | Yes | Independent 10-check verification record |
| `data/raw/2026-11-23-fresh-cohort-certification/pdf-access-log.jsonl` | `D:\projects\indus_valley_script\data\raw\2026-11-23-fresh-cohort-certification\pdf-access-log.jsonl` | No (local-only) | Audit log of all 27 blind PDF page and caption probes |
| `data/raw/2026-11-23-fresh-cohort-certification/input-hashes.json` | `D:\projects\indus_valley_script\data\raw\2026-11-23-fresh-cohort-certification\input-hashes.json` | No (local-only) | SHA-256 and byte counts of all 19 read-only input files |

## Changes in coverage and certification status

- **Base register (4,695 Lipi families)**: unchanged; 0 of 4,695 carry `exposure_status=fresh` (`unreviewed`: 4,695).
- **Post-catalogue cohort certification (503 rows; 358 audited candidates)**:
  - **8 objects certified as `certified_absent_sealed`** with verified local PDF plate pages: **3 seals** (`PCF-DHL-002` Dhalewan PDF p. 294, `PCF-GDH-002` Gola Dhoro (Bagasra) PDF p. 9, `PCF-JKR-001` Juni Kuran PDF p. 42), **3 sealings** (`PCF-DHL-003` Dhalewan PDF p. 298, `PCF-SKP-005` and `PCF-SKP-006` Shikarpur PDF p. 8) and **2 tablets** (`PCF-LKD-001` Lakhanjo-daro PDF p. 13, `PCF-SKP-007` Shikarpur PDF p. 8).
  - **1 Dholavira false-absent corrected**: `PCF-DHV-141` (registration `33693`, grid `35x63x4`, Stage VI), marked `absent` in `2026-10-21-post-catalogue-finds`, was reclassified to `blocked_by_alias_ambiguity` after finding unregistered Lipi rectangular seal family `4277` in the same grid square (`35 x 63 x 4`) and Period `6` under `Middle Town-` alongside eight Dholavira seal families with blank spatial coordinates.
  - **5 Farmana rows reconciled with `2026-10-20-fresh-test-collection`**: `PCF-FRM-001` through `PCF-FRM-005` were moved from `candidate_only` to `already_present_or_exposed` (`confirmed_known_in_2026_10_20_farmana_reserve_audit`), and Farmana's 15 absent marked-pottery rows remain tracked separately outside the 503-row table so no physical object is double counted.
  - **2 held-file format gaps documented**: `man-environment-22-23` (`PCF-BTD-002`) and `man-environment-35` (`PCF-MTL-001`) are held locally only as DjVu OCR text files (`H06258_djvu.txt`, `H06324_djvu.txt`), not as PDFs with plates; acquiring the *Man and Environment* 35 PDF would certify Mitathal seal `PCF-MTL-001`.
  - **2 interleaved image-only IAR plate gaps documented**: `PCF-GDH-008` (`1995-1996.pdf`, PDF pages 27–29) and `PCF-GDH-011` (`Indian_Archaeology_1996_97_A_Review.pdf`, PDF pages 32 and 34) have embedded image-only plate leaves right next to their text pages without an OCR caption layer.

## Proposed additions to `knowledge/DATA.md` and `data/MANIFEST.json`

1. Add one project-output entry in `data/MANIFEST.json` for `experiments/2026-11-23-fresh-cohort-certification/summary-v1.json` (and `fresh-cohort-v1.csv`).
2. Add one paragraph under `knowledge/DATA.md` summarizing the 23 November 2026 fresh-cohort certification counts (`8 certified_absent_sealed`, `88 conditionally_absent_needs_plate_check`, `230 blocked_by_alias_ambiguity`, `177 already_present_or_exposed`) and noting that the unsent access drafts [REQUEST-ICIT-Q1011.md](REQUEST-ICIT-Q1011.md) and [REQUEST-HARP-Q1017.md](REQUEST-HARP-Q1017.md) await maintainer approval.
