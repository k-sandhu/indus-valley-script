# Evidence census synthesis, Package B3

No complete worldwide index is established. The local Lipi derivative matches 327 of 493 identifiers in 19 inspected CISI 1 ranges; 166 are absent keys, split into 75 in pottery/graffiti sections and 91 in other sections. The museum join count is now a lower bound of 68 among 114 originals, with 46 unresolved. The worldwide number of additional physical objects remains unknown. [REPORT.md](REPORT.md) defines the units and explains the source populations.

Here, a face is one source-defined side or text-bearing view in the pinned 5,680-record local corpus. A provisional family groups those records by a local object identifier. An absent key has no exact or recorded alias match in that export; the corresponding physical object may still occur under another key. The 115 site/provenance entities account for 5,652 faces by site label, while 28 faces have unknown sites.

V6 records the coordinator's post-trim inputs and the Sonnet review corrections. Its corrected Pakistan CISI 1 comparison is 910 matches in 1,040 catalogue entries across five runs at four sites. The north India IM77 count is 117. Seven checked museum additions bring the total to 68 families and 74 faces. [coverage.json](coverage.json), [catalogue-coverage.csv](catalogue-coverage.csv) and [join-summary.json](join-summary.json) contain these numbers.

The synthesis remains Exploratory. A fresh replay matches all eleven aggregate files, with [1,093 verification checks](verification-2026-10-07-v6.json) passing. [The endpoint](main-2026-10-07-v6/checks.json) passes 850 arithmetic checks. These checks establish computation and pinned bytes; source interpretation and unresolved identities retain their review status. The original 20-site sample verdicts 14/6 and the review's source-wide 18/2 verdicts are recorded separately.

[Package checks](package-checks-2026-10-07-v6.json) pass 173 checks, including unchanged hashes for 64 earlier endpoint files. The [prose scan](prose-review-2026-10-07-v6.json) finds no flags in 19 current, preserved and reviewer Markdown files.

## Current outputs and preservation

| Output | Contents |
|---|---|
| [PROTOCOL.md](PROTOCOL.md), [REPORT.md](REPORT.md), [RETROSPECTIVE.md](RETROSPECTIVE.md) | Method amendments, answer and observed corrections. |
| [coverage.json](coverage.json), [coverage.csv](coverage.csv), [region-coverage.csv](region-coverage.csv) | Local frame, corrected IM77 counts, catalogue comparisons and eight omitted sections. |
| [catalogue-coverage.csv](catalogue-coverage.csv), [catalogue-section-split.csv](catalogue-section-split.csv) | Complete multi-run parsing, H356 duplicate correction and the 166-key section split. |
| [field-completeness.csv](field-completeness.csv) | Measured field presence, twelve structural schema absences, inherited rules and unmeasured fields. |
| [register-joins.json](register-joins.json), [join-summary.json](join-summary.json) | Source/site links and the expanded museum lower bound. |
| [priority-gaps.json](priority-gaps.json), [SCHEMA-AMENDMENTS.md](SCHEMA-AMENDMENTS.md) | Eight acquisition pools and Proposed schema/200-object pilot changes. |
| [sources.json](sources.json), [sample-selection.json](sample-selection.json), [source-sample-audit.json](source-sample-audit.json), [conflicts.json](conflicts.json) | 21 bibliographic entries, opening scopes, original sample verdicts, reviewer verdicts and corrected locators. |
| [batch-corrections.json](batch-corrections.json) | 53 proposed row/ledger corrections for batch owners; no batch edited. |
| [source-title-audit.json](source-title-audit.json), [source-title-review-v6.json](source-title-review-v6.json) | Widened screening candidates and checks that all 32 reviewer residual IDs have coordinator removal markers. |
| [checks.json](checks.json), [input-manifest.json](input-manifest.json), [OUTPUT-MANIFEST.json](OUTPUT-MANIFEST.json) | Current checks, post-trim pins and top-level copy provenance. |
| [registry-entry.json](registry-entry.json) | Updated proposal; shared registry unchanged. |
| [created-paths-v6.json](created-paths-v6.json), [v6-changed-paths.json](v6-changed-paths.json) | Current package inventory and every B3 path created or changed in this follow-up. |

Top-level aggregate files copy `main-2026-10-07-v6/`; authored annotation ledgers copy the dated amendment directory named in `OUTPUT-MANIFEST.json`. `pre-v6-2026-10-07/` preserves the preceding top-level state and code. All earlier endpoints and the reviewer files remain unchanged. Third-party extracted records, museum pairs and small page witnesses stay under the paired local raw directory.

The v5 replay/verification statements describe the creation-time state. Five source ledgers changed after the coordinator's two title trims, making seven v5 verification checks stale. Batch B's `created-paths.json` and C/D's `file-manifest.json` also predate the edits. The review found stale hashes in batch D's `build.py --verify` and `inventory.py --verify`; B3 has not rewritten those manifests or rerun mutation-producing batch builders. Current v6 pins match the edited ledgers.

## Reproduce from the repository root

The builder uses the Python standard library and existing local inputs. Source rendering uses the already installed PyMuPDF package. Use new output names on every replay; existing endpoints are preserved. No full PDF download or volume rendering is needed.

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python -B experiments/2026-10-06-evidence-census/synthesis/build_synthesis.py --output-dir experiments/2026-10-06-evidence-census/synthesis/reviewer-2026-10-07-v6 --raw-dir data/raw/2026-10-06-evidence-census/synthesis/reviewer-2026-10-07-v6
python -B experiments/2026-10-06-evidence-census/synthesis/verify_synthesis.py --compare experiments/2026-10-06-evidence-census/synthesis/reviewer-2026-10-07-v6 --output experiments/2026-10-06-evidence-census/synthesis/reviewer-verification-2026-10-07-v6.json
python -B experiments/2026-10-06-evidence-census/synthesis/amend_v6_records.py --output-dir experiments/2026-10-06-evidence-census/synthesis/reviewer-amendments-2026-10-07-v6
python -B experiments/2026-10-06-evidence-census/synthesis/make_batch_corrections.py --output experiments/2026-10-06-evidence-census/synthesis/reviewer-batch-corrections-2026-10-07-v6.json
python -B tools/review_prose.py --path experiments/2026-10-06-evidence-census/synthesis --no-write
```

The builder consumes `v6-correction-inputs.json`, the small raw seven-join supplement and the review's catalogue-section counts. `prepare_v6.py` created these recorded inputs once and refuses to overwrite them. `amend_v6_records.py` replays the attributed source/locator amendments from the preserved pre-v6 state; it does not perform a new source review. `write_annotations.py` and its original replay outputs document the v5 annotation method. `review_sources.py` remains available for selected-page extraction; the v6 bibliographic and concordance pages have their own small manifests under `review-fixes-2026-10-07-v1/` in the local raw root.

## Reviewer checks

Compare a new build with v6 and inspect the post-trim input hashes. Repeat IM77 p.6 for Tarkhanewala Dera and West Asia; CISI 1 contents and p.375 corrigenda for Harappa H278?382; CISI 2's three Harappa runs; and the 75/91 section split. Check the seven added joins against CISI 1 pp.373,375, Marshall p.402, saved museum accessions and unique local families. Review the 46 unresolved query dispositions and distinguish the original 61-record field-comparison denominator from the seven new pairs.

Check the eight omitted catalogue sections and the 53 proposed batch corrections before integrating them. Verify bibliography/access scope, especially unseen Rao 1985 p.305, Dholavira mirror p.233, Nippur catalogue p.113 and the CISI 3.3 excerpt. Current ICIT and complete later catalogues remain acquisition work.
