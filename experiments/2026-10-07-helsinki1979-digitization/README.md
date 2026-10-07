# Package M: Helsinki 1979 digitization

The new pipeline failed its 60-row frozen test: 23/60 clean crops, 33/60 matching unit counts, 23/60 exact inscription numbers, 13/60 strict compatible whole rows at top one and 24/60 at top five. All four reliability criteria failed. The package contains 11,369 provisional printed occurrences and 57,426 unit candidates from all 159 corpus pages, plus source references and a review queue. These files do not yet supply the reliable complete corpus sought by this package.

The [report](REPORT.md) gives intervals, calibration, crop and reference disagreements, and label-blinding limits. Exact outcomes are [metrics.json](evaluation/2026-10-07-frozen-v1/metrics.json), field `summary`; extraction totals are [coverage.json](runs/2026-10-07-full-v1/coverage.json), field `counts`. The primary reference has 267 drawn units, including 38 editorial units. Number accuracy after excluding all 22 source-OCR-exposed locator rows is 13/38. Six repeated visual readings agree on counts and printed fields; four agree on ordered strict candidate sets, and crop judgments disagree on four. Initial references remain unchanged.

## Files and source attribution

[PROTOCOL.md](PROTOCOL.md) records the pre-outcome plan, freeze and subsequent disclosure. [freeze-manifest.json](freeze-manifest.json), [prediction-freeze.json](prediction-freeze.json), [chart-snapshot.json](chart-snapshot.json), `development/` and `blind/` retain the frozen dependencies and independent annotations. The CC BY derived extraction is [occurrences.jsonl](runs/2026-10-07-full-v1/occurrences.jsonl). The [priority queue](review/2026-10-07-v1/priority-queue.jsonl) links to compressed local row crops; all rows retain field/boundary review requirements. [IMPORT_INTERFACE.md](IMPORT_INTERFACE.md) and [staged rows](integration/2026-10-07-v1/ledger-import.jsonl) preserve source-qualified identities. All 11,369 staged rows remain quarantined, with zero verified external object joins. [RETROSPECTIVE.md](RETROSPECTIVE.md), [sources.json](sources.json) and [registry-entry.json](registry-entry.json) complete the record. [validation.png](figures/validation.png) plots the reserved row outcomes and conditional calibration.

Source: Kimmo Koskenniemi and Asko Parpola (1979), *Corpus of Texts in the Indus Script*, Research Reports 1, Department of Asian and African Studies, University of Helsinki. [Persistent handle](http://hdl.handle.net/10138/342677), [institutional licence witness](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Chart crops, evaluation crops, annotations and transcription are source-derived changes made here. Retain the title, authors, source URL, licence and modification notice with those assets. Our new code/prose have no separately assigned blanket licence. The 1980 PDF, extracted text, source crops and copied crosswalk rows stay in local raw because its licence is unverified.

## Run from the repository root

The existing interpreter is `C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe`. The freeze records exact recognition-package versions; the [interface check](integration/l-interface-check-v1.json) records the later schema-check dependencies. This package installed PyMuPDF, OpenCV and jsonschema with its four dependencies using `pip --no-cache-dir`; NumPy, SciPy, Pillow, PyTorch, Tesseract and plotting support were already available. `pipeline.py` uses the saved chart-trained weights and calibrated coefficients. TMP, TEMP and MPLCONFIGDIR are under the local raw directory.

Use new output paths on every repeat. These commands recompute from preserved inputs without replacing frozen endpoints:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate.py --out experiments/2026-10-07-helsinki1979-digitization/evaluation/reviewer-recompute
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/rerun_frozen_sample.py --predictions-out data/raw/2026-10-07-helsinki1979-digitization/reviewer-sample-v2.json --audit-out experiments/2026-10-07-helsinki1979-digitization/verification/reviewer-sample-v2.json
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/verify.py --out experiments/2026-10-07-helsinki1979-digitization/verification/reviewer-v2.json
```

The selected-row recomputation processes only 60 rows and already passed. A full repeat costs about 52.1 minutes on this environment and creates another payload plus compressed crops; check the local storage limit before repeating it:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/pipeline.py full --out experiments/2026-10-07-helsinki1979-digitization/runs/reviewer-repeat
```

The original development/freezing/selection commands were `pipeline.py develop`, `pipeline.py freeze` and `pipeline.py sample`. Do not run `develop` over this frozen package: it rewrites dependencies. Develop a subsequent dated experiment instead. Freeze/sample commands refuse existing endpoints.

Other rerunnable scripts are `build_review_queue.py`, `prepare_import.py`, `check_ledger_interface.py` and `compare_annotations.py`, each with `--out` for a new owned directory/file. `review_package_prose.py` captures the required root prose scan and input hashes in [prose-review-v1.json](verification/prose-review-v1.json). `plot_results.py` regenerates the derived figure; `write_docs.py` regenerates prose from aggregate outputs. `inventory_files.py` updates the derived [file manifest](file-manifest.jsonl) and [inventory totals](file-manifest-summary.json). The [final verification](verification/2026-10-07-v1.json) records input checks and storage, including installed dependency bytes. The file manifest enumerates every created package/raw asset and installed distribution file. No shared registry, index, manuscript, history or other package was edited.

Reviewer checks: repeat evaluation and the 60-row computation; sample exact glyph boxes against wider source context, especially indices 14–16, 24, 29, 30, 35, 42 and 51; adjudicate the two repeated glyph disagreements and four crop disagreements; inspect number suffixes, classification blanks and auxiliary units; confirm all staged rows remain quarantined without an inspected object concordance. Run `python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write`.
