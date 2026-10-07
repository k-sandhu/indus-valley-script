# Evidence census synthesis, Package B3

The available evidence does **not** establish a complete Indus index. The worldwide number of missing physical objects remains unknown. Across 19 inspected CISI 1 site ranges, **327 of 493 catalogue identifiers match the local corpus and 166 do not**. The selected online museum frame contains **114 originals, 61 confirmed identifier joins and 53 unjoined records**. These overlapping source frames have different counting units. [REPORT.md](REPORT.md) explains the bases, source disagreements and acquisition gaps.

The four active site batches' **123 rows** join to **115 site/provenance entities**, representing **5,652 local faces and 4,668 provisional families**. Another **28 faces and 27 families** have unknown site labels. On the full 5,680-face derivative, **2,191** have room/grid context, **4,441** a positive dimension and **4,706** material. Calendar dates, independent dating links, image links and item-rights links are absent from its normalized fields. [coverage.json](coverage.json), `summary`, and [field-completeness.csv](field-completeness.csv), `basis`, define those measures.

Status: Exploratory synthesis and Proposed schema/pilot amendments. The v5 arithmetic endpoint passes **728 checks**. A fresh replay matches all ten JSON/CSV aggregates, and [verification-2026-10-07-v2.json](verification-2026-10-07-v2.json) passes **1,069 checks**. A purposive source check covers **20 sites**, five per batch, with **14 supported and six qualified selected assertions**. Separate contributor/source review remains outstanding.

[Package checks](package-checks-2026-10-07-v1.json) pass 94 copy, link, syntax and accounting checks. The four authored ledgers reproduce in [annotation replay checks](annotation-replay-checks-2026-10-07-v1.json). The final [prose scan](prose-review-2026-10-07-v2.json) reports no flagged wording in the five Markdown files; source interpretation still requires the review below.

## Outputs

| File | Contents |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Pre-outcome method, sample rules and dated correction amendments. |
| [REPORT.md](REPORT.md) | Direct answer, count bases, metadata measures, uncertainty and source-title repairs. |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Reused work, observed problems, corrections and remaining review. |
| [coverage.json](coverage.json), [coverage.csv](coverage.csv), [region-coverage.csv](region-coverage.csv) | Site and regional figures, source count assertions and undefined worldwide coverage. |
| [catalogue-coverage.csv](catalogue-coverage.csv) | Selected CISI ranges and local base-identifier membership. |
| [field-completeness.csv](field-completeness.csv) | Measured field presence and unmeasured denominators for each index. |
| [register-joins.json](register-joins.json), [join-summary.json](join-summary.json) | Source/site links, candidate statuses and museum object-join aggregates. |
| [priority-gaps.json](priority-gaps.json) | Eight overlapping acquisition pools, routes and rights constraints. |
| [SCHEMA-AMENDMENTS.md](SCHEMA-AMENDMENTS.md) | Proposed entity/field additions and stratified 200-object pilot. |
| [sources.json](sources.json), [sample-selection.json](sample-selection.json), [source-sample-audit.json](source-sample-audit.json), [conflicts.json](conflicts.json) | Bibliography, opening status, 20-site sample, observations and seven conflicts. |
| [source-title-audit.json](source-title-audit.json), [source-title-review.json](source-title-review.json) | 17 flagged headers in five files, with no copied title payload. |
| [checks.json](checks.json), [input-manifest.json](input-manifest.json), [OUTPUT-MANIFEST.json](OUTPUT-MANIFEST.json) | Recomputed checks, input pins and top-level byte-copy provenance. |
| [registry-entry.json](registry-entry.json) | Proposed entry for the coordinator; shared registry was not edited. |
| [created-paths.json](created-paths.json) | Every created file under both B3 roots, size, hash and local-raw disposition. |

Top-level computed tables are byte copies of `main-2026-10-07-v5/`. Preserve `development-2026-10-07-v1/`, the main endpoints v2–v5, and `replay-2026-10-07-v1/`; the development run failed one check and earlier computations have documented method limitations. Use v5 for final figures. The separately named source checks and object crosswalks stay under `data/raw/2026-10-06-evidence-census/synthesis/`. No payload from another package was moved or edited.

## Reproduce from the repository root

The arithmetic builder uses the Python standard library. Source-page extraction additionally uses the installed PyMuPDF package. Choose new output names on each rerun; scripts refuse to overwrite an existing endpoint. They constrain writes to this package's owned and local-raw roots and set library temporary locations under the chosen raw endpoint.

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python -B experiments/2026-10-06-evidence-census/synthesis/build_synthesis.py --output-dir experiments/2026-10-06-evidence-census/synthesis/reviewer-2026-10-07-v1 --raw-dir data/raw/2026-10-06-evidence-census/synthesis/reviewer-2026-10-07-v1
python -B experiments/2026-10-06-evidence-census/synthesis/verify_synthesis.py --compare experiments/2026-10-06-evidence-census/synthesis/reviewer-2026-10-07-v1 --output experiments/2026-10-06-evidence-census/synthesis/reviewer-verification-2026-10-07-v1.json
python -B experiments/2026-10-06-evidence-census/synthesis/review_sources.py --output-dir data/raw/2026-10-06-evidence-census/synthesis/reviewer-sources-2026-10-07-v1 --render
python -B tools/review_prose.py --path experiments/2026-10-06-evidence-census/synthesis --no-write
```

`review_sources.py` recreates 31 PDF-page witnesses and three saved Dholavira mirror passages. Nuhato's pp. 41–42 were additionally opened for the overlap conflict; their original path and hash are in `sources.json`. Page extraction is mechanical; repeat visual/source judgment separately. `write_annotations.py --output-dir experiments/2026-10-06-evidence-census/synthesis/reviewer-annotations-2026-10-07-v1` replays the four authored JSON ledgers into a new directory. It preserves recorded observations and does not conduct a new source review. `finalize_package.py` copied the first final aggregates and wrote the title-header review; it intentionally refuses to replace top-level files. Its `--inventory` mode can write a newly named full file inventory.

## Checks to repeat

Recompute all batch row totals and compare the new endpoint with v5. Check alias attribution for Nuhato/Gharo Bhiro and the six A/D cross-references. Inspect catalogue membership for Lothal L1–290, Kalibangan K1–122, Banawali B1–37, Rohira Rhr1–2, Rehman Dheri Rhd1–270 and the Amri/Ai concordance. Classify absent keys before calling them additional physical objects. Repeat all 20 source assertions at their exact locators, including Dholavira's mirror qualification. Sample the 61 museum concordances, then examine the field disagreements. Check the room/grid, phase, dimension-placeholder, calendar-attribution and image-slot rules before interpreting completeness percentages.

Full current ICIT, complete later CISI/holding inventories, some final excavation catalogues, original Dholavira page images and independent expert adjudication remain missing. No worldwide missing-object count or global coverage percentage was computed. All new work and failed preliminary outcomes are confined to the two authorized B3 paths.
