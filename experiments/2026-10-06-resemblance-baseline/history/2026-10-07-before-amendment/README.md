# Cross-script shape resemblance pilot

The pilot coded 42 Tamil Nadu base drawings, 36 readable cells from a seeded 42-cell Indus sample, 20 Ogham letters and 32 Tifinagh letters. Matching only segment and loop counts gave **30/42 Indus matches (71.43%)**, **24/42 Ogham matches (57.14%)** and **32/42 Tifinagh matches (76.19%)**. Adding all counted contacts, curves, terminals, components, dots, symmetry and orientation reduced these to **4/42 (9.52%)**, **1/42 (2.38%)** and **10/42 (23.81%)**. See [observed.json](run-v1/observed.json), fields `inventory`, `rule`, `matched`, `queries` and `rate`.

These measurements describe the declared descriptors and selected drawings. The accessible 2025 witness is an eight-page brochure, and the complete monograph was not recovered. The pilot cannot reproduce its reported 90% because the population and matching procedure behind that percentage remain unspecified in this witness. Six sampled Indus cells were excluded before outcomes, and 22 of the 36 included Indus annotations retain uncertainty. Complete-vector agreement between independent agent passes was **12/19 comparable drawings (63.16%)**, with one of the 20 assigned drawings excluded by the primary coder. [Agreement](run-v1/agreement.json), [input manifest](run-v1/manifest.json), [source observations](source-observations.json).

Status: **Exploratory**. The empirical descriptor null is **Synthetic**; computation has been rerun exactly. [REPORT.md](REPORT.md) explains the size controls, complexity differences, intervals and next study. [PROTOCOL.md](PROTOCOL.md) was written before coding and outcomes; its dated clarification also preceded outcomes. [RETROSPECTIVE.md](RETROSPECTIVE.md) records source failures and implementation checks. [sources.json](sources.json) separates opened sources from snippets and records rights. [registry-entry.json](registry-entry.json) is a proposal for the coordinator; the shared registry was not edited.

## Repeat from the repository root

The computation requires Python, NumPy and the preserved local raw `coder-a.json`, `coder-b.json` and `indus-selection.json`. The source preparation also requires PyMuPDF, Pillow and requests. These libraries were already installed; no installation was performed. All source extracts, annotation rows and per-query matches stay under `data/raw/2026-10-06-resemblance-baseline/`. A checkout without that local material cannot reproduce the manually coded endpoint.

```powershell
python experiments/2026-10-06-resemblance-baseline/analyze.py --verify
python experiments/2026-10-06-resemblance-baseline/verify_package.py
python experiments/2026-10-06-resemblance-baseline/analyze.py --output reviewer-run-01
python experiments/2026-10-06-resemblance-baseline/prepare_inputs.py --directory reviewer-sheets-01
python tools/review_prose.py --path experiments/2026-10-06-resemblance-baseline --no-write
```

`--verify` compares every aggregate and every local query result exactly. A new run refuses to overwrite an existing output directory. Source preparation reproduces the seeded selection and source sheets in a new raw subdirectory. For a fresh acquisition, use `prepare_sources.py --directory acquisition-review-01`; live URLs may return different bytes, so compare their hashes with [sources.json](sources.json) before treating them as the pilot witnesses. Each script sets library temporary directories within its raw directory.

`coder-a.json` is the endpoint input. `coder-a-controls-tamil.json` is a preparatory partial file retained as an intermediate witness; the pre-outcome T18 correction appears in the endpoint input. Preserve both files and use only the endpoint input for recomputation.

The numerical checks validate descriptor categories, the graph identity when junction degrees are known, nested matching rules, and Monte Carlo means against exact collision and finite-subset formulas. The separate reviewer should recode the uncertain drawings, particularly I14 and U2D3F, then check the 20-sign comparisons and the empirical-support limitation of the null. See [verification.json](verification.json) for checks already performed and [FILES.json](FILES.json) for every created path.
