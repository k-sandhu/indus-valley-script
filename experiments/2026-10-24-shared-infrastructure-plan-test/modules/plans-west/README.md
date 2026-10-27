# Western source-plan audit

Read [RESEARCH.md](RESEARCH.md) for the result and exact source locators. All acquired source images, page renders, crops, annotations and detailed traces remain local-only under:

`D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west/`

The logical prefix is `data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west/`. The checkout retains the project data junction; D is the physical storage location.

| File | Schema and scope |
|---|---|
| sources.json | `{sources:[...]}`; 14 source-use records, including 6 inherited PDFs and 8 new HARP image-source records |
| inventory-freeze.json | Frozen 23-panel named inventory, seven dimensional targets, one registration target and explicit missing targets |
| plan-panels.json | `{panels:[...]}`; 23 original panels, exact source/page/figure, transforms, north, scale and local endpoint references |
| measurements.json | `{measurements:[...],registration:{...},decision:{...}}`; 7 dimensions, one descriptive registered pair and null P1 effect |
| episodes.json | `{episodes:[...]}`; 15 source-defined cases including one source-eligibility case; source observations and interpretations remain distinguished |
| visual-assets.json | `{assets:[...]}`; 12 selected annotated boards with hashes, captions and exact source locators |
| coverage.json | New acquisitions and fields, unresolved gaps and failed routes |
| validation.json | Hash, schema, transform, arithmetic, local-storage and visual checks |
| module-freeze.json | Final authored-file hashes and pointers to the immutable raw inputs |

`acquire.py`, `freeze_inventory.py`, `prepare_panels.py`, `measure.py`, `build_cases.py` and `render_boards.py` preserve the authored processing steps. Acquisition, inventory, crop, measurement and board output directories refuse accidental overwrites. The renderer currently targets the final `boards-v2` directory; reproduce into a new versioned directory instead of replacing it. A replay must keep the frozen inventory and unchanged source files.

The observations are exploratory. They were coded before receiving the parallel module's newly assembled documentary overlay, with earlier source examples already known. The author record is GPT-6 family, exact serving variant unknown, Codex desktop.
