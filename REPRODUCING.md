# Manual reproduction and evidence inspection

No CI/CD is configured. Run scripts explicitly from the repository root. Most analysis tools assume the retained original `data/`, `research/`, `results/` and `output/` paths.

## Two different reproduction tasks

The first task is to inspect the recorded evidence: the manuscript's claim-evidence map, the original result JSON files, plans, code snapshots and hashes. Most of these are in Git, and inspecting them does not require rerunning anything, such as the 45-minute job that simulates a conditional null distribution.

The second task is to recompute results from the observational inputs. This needs locally acquired data, compatible outputs of the normalization and sign-crosswalk scripts, and the recorded dependencies. The Git repository deliberately excludes the bulk source corpora and many downloaded witnesses (copies of primary sources), so a fresh clone does not contain the full input corpus.

The detailed JSONL files of the restoration benchmarks, the slot audits and context predictions that record each query, stay local because their sign codes or sequences could be used to rebuild the source corpus. Their aggregate results are tracked. A paired reanalysis of a benchmark needs those preserved local audit files, or a separately acquired input with matching hashes.

The [reviewed sign catalogue](experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html) embeds its data and can be opened directly from a clone, including its attributed detail crops from the chart. To serve it in a browser, run `python -m http.server 8769 --bind 127.0.0.1` from the repository root and open `/experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html`. The [adversarial report](experiments/2026-10-11-bonta-adversarial/REPORT.md) lists the local inputs needed to rebuild the catalogue and recompute its results.

## Inputs and environment

See the [source inventory](knowledge/provenance/SOURCES.md), the [redistribution review](knowledge/provenance/REDISTRIBUTION.md) and the [historical environment](output/environment.json). The first run used Python 3.13.5 on Windows. `requirements.txt` records the package versions observed then; plotting originally used a separate `.vendor` tree. A single pip environment is a convenience and does not exactly reconstruct that historical layering.

For a new isolated environment, use Python 3.13, create `.venv` and install `requirements.txt`. Do not replace the machine's existing environment. The pinned source repositories are:

- [Lipi commit fc8813a](https://github.com/yajnadevam/lipi/tree/fc8813a52e183d19c441631dc26c33a4dccbea39), acquired into `data/lipi/`; no explicit repository licence was found in the audit of the pinned commit.
- [Mayig commit ad2f1e2](https://github.com/mayig/indus-valley-script-corpus/tree/ad2f1e218a34b8c33c57de0d6cb8d99272765bbb), acquired into `data/mayig/`; retain its MIT notice.
- Institutional scans and primary source witnesses listed in the corpus and source inventories. `research/corpus/normalize_lipi.py`, `normalize_mayig.py` and `build_sign_crosswalk.py` record how the inputs were normalized. Inspect the inputs and paths they assume before regenerating local inputs, and do not overwrite frozen normalized files casually.

Record the hashes of newly acquired files. A live source may differ from the pinned input of the first run. Check identity with `output/evidence_manifest.json` and the import manifest; matching corpus counts alone do not establish it.

## Fast checks

```powershell
python tools/verify_knowledge_repo.py
python src/exploratory/permutation_identifiability.py
python src/verify_root.py
python src/methods/verify_methods.py
```

The root and methods checks require the preserved local inputs and results. A historical pass record does not replace a fresh pass after changes. The exact permutation illustration uses only the standard library and synthetic data.

`python tools/verify_knowledge_repo.py --verify-import` hashes every imported local file against `archive/2026-10-01-investigation/import-manifest.json` and can take several minutes. The original evidence manifest of 1,568 selected files and the new full preservation manifest have different scopes.

## Original analysis entry points

The historical commands below write to default output directories and can overwrite old results. Inspect each command's help and defaults first, and copy or specify a fresh output location before rerunning. The original source and frozen outputs should remain unchanged. Exact long-run commands and seeds are in [methods reproduction](research/methods/REPRODUCING.md).

| Analysis | Entry point | Existing evidence |
|---|---|---|
| One-known-slot restoration | `src/restoration.py benchmark` | `results/restoration/` |
| Site-held restoration | `src/restoration.py crosssite --out <new-dir>` | `results/restoration_crosssite/` |
| Another annotation | `src/independent_annotator.py` | `results/independent_annotator/` |
| Quality sensitivity | `src/independent_quality_sensitivity.py` | Source-quality sensitivity and original plans |
| Unknown gap-count recovery | `src/gap_restoration.py benchmark` | `results/gap_restoration/` |
| Matched gap prior | `src/methods/gap_design_matched.py --prior results/gap_restoration --output <new-dir>` | Methods matched-design output |
| Scale identifiability | `src/identifiability_demo.py` | `results/identifiability/` |
| Complete numerical audit | `src/methods/audit_numerical_equalities.py` | `research/methods/NUMERICAL_CONSTRAINT_AUDIT.md` |
| Fresh20 frozen recognition | `src/evaluate_font_fresh20.py` | `research/visual_digitization/font_fresh20/` |
| Nested unique-conditioned reference | `src/methods/nested_unique_conditioned.py` | `research/methods/results/joint_nested_unique_conditioned_1000/` |

Rerunning an old failed experiment without new evidence is usually unnecessary. [The registry](knowledge/experiments/registry.json) records why each attempt failed and what would justify revisiting it, including alias leakage, selection, masking mismatch, source identity and tuning after the reference comparison was seen.

## Six-hour continuation packages

The studies of the six-hour session keep snapshots of the executed source and helper scripts, their parameters and the hashes of their outputs in dated endpoints, output directories that are never overwritten. Their protocols distinguish development runs, evaluations on freshly generated data, replications of published sources and later mathematical refinements. The [session record](experiments/2026-10-02-six-hour/SESSION_LOG.md) is the entry point for all branches.

| Package | Inputs available from Git | Reproduction entry |
|---|---|---|
| [Paper 001](papers/001-artifact-aware-prediction/methods.md) | Aggregate restoration outputs, source snapshots, parameters and numeric review | Detailed query reanalysis also needs local corpus-derived slot audits |
| [Paper 002](papers/002-conditional-reference-laws/methods.md) | Generated populations, finite tables, proposal histories, method snapshots, results and auditors | Exact calculations are short; original main calibration took about 3.1 hours and imperfect-face calibration about 1.5 hours on the recorded host |
| [Paper 003](papers/003-physical-observations/methods.md) | Generated worlds, separated evaluator keys, exact certificates, protocols and auditors | Published-source replication additionally needs the locally retained source vectors; synthetic numerical controls use tracked generated inputs |
| [Paper 004](papers/004-reference-model-selection/methods.md) | Generated worlds, hidden mapping keys, generator and solver snapshots, exact and dual checks, and independent reviewers | The two main mapping grids each took about 47 seconds on the recorded host; independent reviews take additional time |

Inspect a frozen endpoint before deciding to rerun it. New executions, including reruns for independent review, must use a fresh output directory. The recorded seeds and helper hashes identify the actual calculation; changing a working helper script creates a new method even when its filename stays the same.

The original full import was checked again during the continuation. Its [preserved report](knowledge/provenance/full-import-verification-2026-10-02-0924.json) covers 16,284 imported files and 1,568 selected historical evidence files, with no hash errors. Routine verification of links and the registry writes a separate report that each run replaces.

## Hosted outputs

Package A's per-query predictions, inner-fold arrays and model checkpoints (`data/raw/2026-10-06-modern-restoration/main/` and `frozen-model/`, 1,034 files, 3.09 GB) were moved on 7 October 2026 to the private Hugging Face dataset `ksaw008/indus-research-data` because the local disk was full. Every file was verified against the Hub by size and checksum before the local copy was removed; [hf-hosting-manifest.json](experiments/2026-10-06-research-program/hf-hosting-manifest.json) lists each path and SHA-256. Restore them before rerunning package A's reviews or replays, after logging in with `python -m huggingface_hub.cli.hf auth login`:

```powershell
python experiments/2026-10-06-research-program/hf_host.py restore --repo ksaw008/indus-research-data
```

Third-party scans, captures and corpora were not uploaded and remain local.

## Portability limits

Most analysis paths resolve from the script's repository root. Some historical helpers for fetching sources, rendering or review contain the original host's absolute paths; they are preserved as historical records and may need explicit path edits or copied input locations. Code snapshots stay unmodified so that their recorded hashes keep their meaning. Some acquisition requests failed historically, and none is guaranteed to work against current servers.

The complete output of the latent-forms mixture analysis is stored as eight compressed byte chunks. Run `python src/six_hour/latent_forms_package.py verify` to check the stream without writing a file. A clone can restore the original analysis path with the [reconstruction command](experiments/2026-10-02-six-hour/latent-forms/git-package/main-results-v1/RECONSTRUCT.md); the helper refuses to overwrite an existing destination and verifies each chunk and the full hash.

The [checkout-availability review](experiments/2026-10-02-six-hour/integration-review/checkout-availability/REPORT.md) lists the core navigation pages and gives selected source routes for all eighteen link targets that exist only locally. The hashes of the documents it copied fix the reviewed version, and later status edits remain visible in Git history.

A [clean-clone execution](experiments/2026-10-02-six-hour/integration-review/fresh-clone-execution/README.md) independently reconstructed the large mixture package and repeated the exact identification audit from tracked inputs. Its only change to the copied auditor redirects output to a new temporary directory; the original source and earlier reviews remain intact.
