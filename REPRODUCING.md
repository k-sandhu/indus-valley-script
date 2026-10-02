# Manual reproduction and evidence inspection

No CI/CD is configured. Run scripts explicitly from repository root. Most analysis tools assume the retained original `data/`, `research/`, `results/` and `output/` paths.

## Two different reproduction tasks

**Inspect the recorded evidence.** Read the manuscript's claim-evidence map, original result JSON files, plans, code snapshots, and hashes. Most of those are in Git. This does not require rerunning a 45-minute conditional-null job.

**Recompute from observational inputs.** This requires locally acquired data, compatible normalization/crosswalk outputs, and the recorded dependencies. The Git repository deliberately excludes the bulk source corpora and many downloaded witnesses. An empty clone is not a full input corpus.

Detailed slot-audit and context-prediction JSONL files stay local because their codes or sequences can reconstruct the source corpus. Their aggregate results are tracked. A paired benchmark reanalysis needs those preserved local audit files or a separately acquired input with matching hashes.

## Inputs and environment

See [source inventory](knowledge/provenance/SOURCES.md), [redistribution review](knowledge/provenance/REDISTRIBUTION.md), and [historical environment](output/environment.json). The first run used Python 3.13.5 on Windows. `requirements.txt` records observed versions; plotting originally used a separate `.vendor` tree. A single pip environment is a convenience rather than an exact reconstruction of that historical layering.

For a new isolated environment, use Python 3.13, create `.venv`, and install `requirements.txt`. Do not replace the machine's existing environment. The pinned source repositories are:

- [Lipi commit fc8813a](https://github.com/yajnadevam/lipi/tree/fc8813a52e183d19c441631dc26c33a4dccbea39), acquired into `data/lipi/`; no explicit repository licence found at the pinned audit.
- [Mayig commit ad2f1e2](https://github.com/mayig/indus-valley-script-corpus/tree/ad2f1e218a34b8c33c57de0d6cb8d99272765bbb), acquired into `data/mayig/`; retain its MIT notice.
- Institutional scans and primary source witnesses listed in the corpus/source inventories. `research/corpus/normalize_lipi.py`, `normalize_mayig.py` and `build_sign_crosswalk.py` record normalization behavior. Inspect their input/path assumptions before regenerating local inputs; do not overwrite frozen normalized files casually.

Record newly acquired file hashes. A live source may differ from the pinned first-run input. Use `output/evidence_manifest.json` and the import manifest to check identity; corpus counts alone are insufficient.

## Fast checks

```powershell
python tools/verify_knowledge_repo.py
python src/exploratory/permutation_identifiability.py
python src/verify_root.py
python src/methods/verify_methods.py
```

The root/methods checks require the preserved local inputs and results. Their historical pass record is not a substitute for a fresh pass after changes. The exact permutation illustration uses only the standard library and synthetic data.

`python tools/verify_knowledge_repo.py --verify-import` hashes every imported local file against `archive/2026-10-01-investigation/import-manifest.json`. It can take several minutes. The original selected 1,568-file evidence manifest and the new full preservation manifest have different scopes.

## Original analysis entry points

The historical commands below use default output directories and can overwrite old results. **Inspect help/defaults first; copy or specify a fresh output location before rerunning.** The original source and frozen outputs should remain unchanged. Exact long-run commands and seeds are in [methods reproduction](research/methods/REPRODUCING.md).

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

Re-running an old failed experiment without new evidence is usually unnecessary. Consult [the registry](knowledge/experiments/registry.json) for the reason to revisit, including alias leakage, selection, masking mismatch, source identity and post-reference tuning issues.

## Six-hour continuation packages

The new studies keep executed source/helper snapshots, parameters and output hashes in dated endpoints. Their protocols distinguish development, fresh generated evaluation, source replication and later mathematical refinements. The [session record](experiments/2026-10-02-six-hour/SESSION_LOG.md) is the entry point for all branches.

| Package | Inputs available from Git | Reproduction entry |
|---|---|---|
| [Paper 001](papers/001-artifact-aware-prediction/methods.md) | Aggregate restoration outputs, source snapshots, parameters and numeric review | Detailed query reanalysis also needs local corpus-derived slot audits |
| [Paper 002](papers/002-conditional-reference-laws/methods.md) | Generated populations, finite tables, proposal histories, method snapshots, results and auditors | Exact calculations are short; original main calibration took about 3.1 hours and imperfect-face calibration about 1.5 hours on the recorded host |
| [Paper 003](papers/003-physical-observations/methods.md) | Generated worlds, separated evaluator keys, exact certificates, protocols and auditors | Published-source replication additionally needs the locally retained source vectors; synthetic numerical controls use tracked generated inputs |
| [Paper 004](papers/004-reference-model-selection/methods.md) | Generated worlds, hidden mapping keys, generator/solver snapshots, exact/dual checks and independent reviewers | The two main mapping grids each took about 47 seconds on the recorded host; independent reviews take additional time |

Inspect a frozen endpoint before deciding to rerun it. New executions must use a fresh output directory, including independent-review reruns. The recorded seeds and helper hashes identify the actual calculation; changing a live working helper creates a new method even when its filename is unchanged.

The original full import was checked again during the continuation. Its [preserved report](knowledge/provenance/full-import-verification-2026-10-02-0924.json) covers 16,284 imported files and 1,568 selected historical evidence files, with no hash errors. Routine link/registry verification writes a separate mutable report.

## Portability limits

Most analysis paths resolve from the script's repository root. Some historical source-fetch, rendering or review helpers contain the original host's absolute paths; those are preserved as historical records and may require explicit path edits or copied input locations. Code snapshots remain unmodified so their recorded hashes retain meaning. Some acquisition requests failed historically and cannot be guaranteed to work against current servers.

The complete mixture endpoint is stored as eight compressed byte chunks. Run `python src/six_hour/latent_forms_package.py verify` to check the stream without writing a file. A clone can restore the original analysis path with the [reconstruction command](experiments/2026-10-02-six-hour/latent-forms/git-package/main-results-v1/RECONSTRUCT.md); the helper refuses to overwrite an existing destination and verifies each chunk and the full hash.

The [checkout-availability review](experiments/2026-10-02-six-hour/integration-review/checkout-availability/REPORT.md) inventories core navigation and gives selected source routes for all eighteen local-only targets. Its copied-document hashes fix the reviewed version. Later status edits remain visible in Git history.

A [clean-clone execution](experiments/2026-10-02-six-hour/integration-review/fresh-clone-execution/README.md) independently reconstructed the large mixture package and repeated the exact identification audit from tracked inputs. Its only copied-auditor change redirects output to a new temporary directory; original source and earlier reviews remain intact.
