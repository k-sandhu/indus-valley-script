# Scientific visual atlas

The final atlas is `run-v7`: 23 figures, each supplied as a 3420 × 2160 PNG at 300 dpi and an SVG. It covers the twelve-town source register, building histories, materials, named changes to circulation, documentary contexts, prior results and the proposed deciding study. All graphic assets remain at `D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/visuals/run-v7/`.

Use `manifest-run-v7.json` for captions, original data values, exact assertion IDs, source titles, primary URLs, locators and asset hashes. `validation-run-v7.json` passes 577 checks. `visual-review-run-v7.json` records the individual image review. The local ZIP contains the 46 exports, both contact sheets and the accompanying records. `release-run-v7.json` identifies that ZIP and its hash.

## Choosing figures

The selected contact sheet is `selected-cover-contact.jpg`. Figure 01 is the clearest general opening image because it introduces all twelve places without reconstructing an ancient landscape. Figure 06 is the strongest opening for the building-history argument: the source's approximate stages and its interruptions appear together. Figure 18 introduces the orientation method; its synthetic label must remain visible wherever it is used.

| Figure | Content |
|---|---|
| 01 | Twelve-town location index, inherited WGS84 coordinates |
| 02 | Source-domain reference index, with completeness unassessed |
| 03 | Assertion coverage by research module |
| 04 | Reported materials by architectural function and phase |
| 05 | Selected change and retention assertions across twelve towns |
| 06 | Dholavira's seven source-model stages and interruptions |
| 07 | Banawali's village, enclosure, clearance and retained outline |
| 08 | Kanmer's open space and later infill with retained orientation |
| 09 | Three separate Farmana circulation changes with reported dimensions |
| 10 | Mohenjo-daro residence inequality, median area and sample counts |
| 11 | Structure and excavation counts with their original units |
| 12 | Dholavira context rows, raw stage labels and qualifications |
| 13 | Dholavira inscription flags, including missing and uncertain cases |
| 14 | Harappa's 22-tablet series, reported cutting hands and recovery groups |
| 15 | Lothal's unreconciled sealing populations |
| 16 | Object manufacture, operation and recovery relations |
| 17 | Earlier positive results, failed predictions and missing physical joins |
| 18 | Synthetic local and pooled fourfold orientation order |
| 19 | Exact sign-test planning power under independent pairs |
| 20 | Institutional rivals and their architectural and documentary predictions |
| 21 | Prospective workflow joining building episodes, access and objects |
| 22 | Four specific source chains and the next relation to acquire |
| 23 | Six published dimension-pair ratios for named architectural parts |

## Interpretation

Figures 02 and 03 describe this research record. They give neither settlement frequencies nor a completeness score. Figure 05 selects examples for navigation; its empty cells mean that no example was selected. Architectural quantities retain their units, excavation scope and reconstruction status. Recovery stage, manufacture, use and abandonment remain separate relations. The Mohenjo-daro century labels and the Dholavira calendar scheme come from source models. The atlas supplies no common calendar axis across towns.

Figures 07–09 use project-authored geometry to explain reported sequences. Their rectangles and strips have no archaeological scale or surveyed north reference. Figure 18 uses generated angles with known district labels and does not implement the 2026 paper's clustering procedure. Figure 19 assumes independent, non-tied comparisons; shared towns and caches reduce the information available to an archaeological study. Figure 20 selects three broad institutional accounts for explanation. The integrated test design also evaluates household coordination and recovery-driven patterns, and allows combinations of these processes.

Figure 23 retains the six original dimension pairs, phase labels and qualification fields in the manifest. Six architectural parts in three towns provide an exploratory comparison. Their printed precision supplies no error model, and intentional canonical proportions remain untested.

## Rebuilding

Run from the repository root with Python 3.13 and matplotlib, NumPy and Pillow:

```text
C:\Python313\python.exe -X utf8 experiments/2026-10-24-urban-form-and-inscription-ecology/modules/visuals/build_atlas.py --run run-v8
C:\Python313\python.exe -X utf8 experiments/2026-10-24-urban-form-and-inscription-ecology/modules/visuals/verify_atlas.py --run run-v8
```

Choose an unused run name. Rendering refuses to replace an existing output directory and requires validated science `run-v3`. Earlier graphic runs preserve the source state and the presentation errors recorded in the retrospective. The accepted assets, captions and manifest are those in `run-v7`.

The strongest reading supported by these figures is that local rebuilding and inherited urban frameworks coexisted. Banawali, Kanmer and Farmana supply named sequences through which we can study that relationship. A deciding test would join dated construction and access changes to independently defined documentary production groups, then compare frozen institutional predictions on new contexts while controlling shared caches, object identities and recovery.
