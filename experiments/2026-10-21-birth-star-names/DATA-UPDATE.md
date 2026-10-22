# Proposed additions to DATA.md and the data manifest

For maintainers to fold into [knowledge/DATA.md](../../knowledge/DATA.md) and `data/MANIFEST.json` after merging. The machine-readable entries are in [manifest-additions.json](manifest-additions.json).

## New comparison source

The project now holds a calibration corpus for a known naming system: Lüders's 1912 *List of Brahmi Inscriptions* in two Internet Archive scans, with OCR text and page images, held locally in `data/raw/2026-10-21-birth-star-names/sources/` ([sources and rights](SOURCES.md)). It is public domain. From it we extracted 819 donor rows from "gift of", "dedication of" and "erection of" clauses, of which 757 are personal donor occurrences after duplicate removal and exclusion of collectives, places and labels. Each row carries the entry number, the Prakrit name and Lüders's Sanskrit equivalent as read in each scan, two independent asterism markings and their resolution ([calibration-v1/luders-donors.csv](calibration-v1/luders-donors.csv), tracked).

Coverage limits: entry numbers come from OCR and are reliable to within a few entries for rows read by only one scan; names in clauses that name a relative rather than the donor, and most co-donors, are not extracted; the personal-name index at the end of the list was not used because its two-column OCR is too damaged. A future pass could read the index from the page images to count persons rather than inscriptions.

## Fields added for Indus objects

None. The study read the discovery half of a new split and wrote aggregate counts of fish runs (`discovery-v1/inventories.json`), which list short sign combinations and their frequencies, not full texts.

## Gaps this study depends on

The frozen predictions can be scored only when at least 40 fish runs stand in name position on seals that the pinned corpus does not hold. That needs the CISI 3.1 volume ([Q-1008](../../knowledge/questions/Q-1008-acquire-cisi-3-1.md)), CISI 3.2 ([Q-1009](../../knowledge/questions/Q-1009-acquire-cisi-3-2.md)) or a published corpus of post-catalogue seals, above all Dholavira ([Q-1026](../../knowledge/questions/Q-1026-post-catalogue-finds.md)). At the discovery rate of 0.37 name-position fish runs per seal legend, about 110 fresh seal legends would supply 40 runs.

## Shared ledger

`bench/spent.json` gained split `078aef2d…` (seed `2026-10-21-birth-star-names`) with the inherited fish families and no confirmation read.
