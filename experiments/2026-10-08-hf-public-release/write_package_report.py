"""Write Package O's aggregate report from completed validation."""
import json
from pathlib import Path
from build_release import HERE,ROOT,RAW,read,dump,sha

def main():
    v=read(HERE/'validation.json');tables=read(HERE/'release/provenance/table-manifest.json');private=read(HERE/'private-store/inventory-summary.json')
    if v['status']!='Verified computation':raise ValueError('Complete local validation first.')
    evidence='[validation.json](validation.json)'
    listing='| Configuration | Rows |\n|---|---:|\n'+''.join(f"| `{k}` | {s['rows']} |\n" for k,s in tables.items())
    readme=f'''# Package O: staged dataset and private-backup description

The local [release candidate](release/README.md) has **19 Hugging Face configurations, 2,739 table rows and 949 PNGs**. All configurations load with `datasets`; every image resolves, decodes and matches its source hash. The two staged benchmarks reproduce Package M’s published metrics, row outcomes, sensitivities and bootstrap intervals. {evidence}, `configurations`, `images`, `benchmark_scores`; [fresh-build comparison](build-replay-comparison.json), 971/971 files equal.

The candidate retains the **687-cell chart and 16 lower-code ambiguities**, **60 original and 80 repaired benchmark rows**, **306 reader records**, **68 museum-to-CISI joins**, **115 site/provenance entities** and the other tables listed below. The original references and the exploratory correction overlay remain separate. The [private-store card](private-store/README.md) describes **1,038 backed-up files and 3,406,008,409 bytes**, including the restore helper’s limited scope. Nothing was uploaded, no repository was created, no visibility changed and no Git history operation ran.

The underlying Helsinki source is CC BY 4.0. Our data CC BY 4.0 and code MIT licences are proposals awaiting the owner’s confirmation. Author, affiliation and contact remain marked placeholders in the candidate. [RELEASE-CHECKLIST.md](release/RELEASE-CHECKLIST.md) lists those decisions and the future private-review upload and visibility steps. Public release also needs a hosted-viewer check and the owner’s final decision.

## Files and repeat commands

[PROTOCOL.md](PROTOCOL.md) records selection and failure rules before packaging. [REPORT.md](REPORT.md) gives results and scope; [RETROSPECTIVE.md](RETROSPECTIVE.md) records the observed problems and fixes. [rights-audit.json](rights-audit.json), [sources.json](sources.json), [registry-entry.json](registry-entry.json) and [created-paths.json](created-paths.json) supply rights, source access, integration proposal and every created/changed path. The release’s [file-manifest.json](release/provenance/file-manifest.json) hashes every other staged file; it excludes itself to avoid a circular checksum. [Environment installation record](environment-installation.json) names the authorized venv additions.

Run from the repository root with the supplied `indus-ml` Python. `requirements.txt` inside the release records the validated packages. Set temporary/cache locations under Package O’s raw directory; the scripts do so themselves. They never call a Hub upload or repository API. Choose fresh names for output folders/files:

```powershell
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' -B experiments/2026-10-08-hf-public-release/build_release.py --out experiments/2026-10-08-hf-public-release/reviewer-build
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' -B experiments/2026-10-08-hf-public-release/write_documents.py --release experiments/2026-10-08-hf-public-release/reviewer-build
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' -B experiments/2026-10-08-hf-public-release/finalize_audit.py --release experiments/2026-10-08-hf-public-release/reviewer-build
& 'C:\\Users\\sandh\\.venvs\\indus-ml\\Scripts\\python.exe' -B experiments/2026-10-08-hf-public-release/validate_release.py --release experiments/2026-10-08-hf-public-release/reviewer-build --out experiments/2026-10-08-hf-public-release/reviewer-validation.json --raw-out data/raw/2026-10-08-hf-public-release/reviewer-validation
python -B tools/review_prose.py --path experiments/2026-10-08-hf-public-release --no-write
```

The builder needs the pinned local parent files, including Package M’s portable predictions and the seven-join supplement. The staged scorer needs only this candidate’s tables and NumPy/PyArrow. Run `release/code/score_benchmark.py --benchmark v1` or `v2` with a fresh `--out` filename. The dataset card gives examples for each configuration, images and new predictions. `verify_private_store.py` is a read-only checksum comparator for a separately restored backup; no remote restore was tested here.

## Table inventory

{listing}

## Reviewer checks

Repeat the local configuration loads, all 949 image hashes and both full score comparisons. Sample chart cells with retained alternatives, including PDF20 column4 row21’s three candidates, and inspect benchmark source boxes, underlines and invalid targets. Review the first benchmark’s 22 exposed OCR locators and v2’s reader disclosures. Compare the 19 CISI 1 ranges yielding 493/327/166 with v6 and inspect the seven new museum joins. Check proposed licences and placeholders before any upload. Raw prose/sequence scan details stay in [the local validation directory](../../data/raw/2026-10-08-hf-public-release/validation-2026-10-08-v6/); the final validation records the exact paths if its run suffix changes.
'''
    (HERE/'README.md').write_text(readme,encoding='utf8')
    report=f'''# Results of the local release audit

The candidate loads all **19 configurations and 2,739 table rows**, and **949/949 licensed PNGs** decode, resolve and match their hashes. Both benchmark comparisons pass every published numeric field covered by the portable scorer, with a tolerance of 1×10⁻¹². This includes row-level outcomes, Wilson intervals, calibration, original sensitivities, the repaired source-row recall and seeded 2,000-draw bootstrap intervals. These results establish local packaging and score reproduction. The hosted viewer, public permissions and expert review remain untested. [validation.json](validation.json), `configurations`, `source_checks`, `images`, `benchmark_scores`, `unverified`.

## Selected assets and rights

The 1979 source’s official final-version entry links CC BY 4.0: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki. [Institutional entry](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), [licence](https://creativecommons.org/licenses/by/4.0/). Package O opened that entry and its licence link; the original local PDF provenance and derivatives were reused. [sources.json](sources.json), `HELSINKI1979`, `CC-BY-4.0`.

The chart’s 687 numeric-label rows, 16 retained lower-code ambiguities and source crop coordinates compare directly with the manual reference. Each atlas PNG is copied without alteration. The source annotations were read by AI models and have no expert certification. The chart’s upper ranks and lower labels are graphic inventory numbers; they carry no authenticated readings. [validation.json](validation.json), `source_checks/chart_selected_fields`, `source_checks/chart_ambiguities`; [chart table](release/data/chart_reference.parquet).

The file-by-file [rights audit](rights-audit.json) records parent hashes, selected fields, every manifest-listed private exclusion and each staged asset. Helsinki derivatives use the source’s CC BY 4.0 terms; the project’s compilation/annotation contributions and code retain proposed CC BY 4.0/MIT terms. Those proposals do not activate a grant before owner confirmation. The [licence record](release/LICENSE) and [checklist](release/RELEASE-CHECKLIST.md) preserve that distinction.

Package A’s Lipi-derived predictions, models/counts and training register are excluded. No Lipi or Mayig record payload is staged. The full provisional 1979 transcription, provisional ledger import, repair frames, source PDFs, non-CC-BY page images, museum text/images and Ascalone catalogue rows are excluded. Package N supplied only its Proposed protocol at the initial inspection; no completed N readings were available for this selection. Its later work does not alter Package M’s frozen references. [rights-audit.json](rights-audit.json), `files/decision`; [protocol](PROTOCOL.md), selection rule.

## Frozen benchmark reproduction

| Outcome | Original 60-row frame | Repaired 80-row frame |
|---|---:|---:|
| Accepted proposed crop | 23/60 | 44/80 |
| Matching drawn-unit count | 33/60 | 59/80 |
| Correct inscription number | 23/60 | 62/80 |
| Exact classification field | 19/60 | 55/80 |
| Strict top-one compatible whole rows | 13/60 | 20/80 |
| Strict top-five compatible whole rows | 24/60 | 40/80 |

These are the unchanged frozen references’ scores, including the first readers’ crop judgments. Later objective crop audits and eleven code corrections are separate Exploratory records; they are not substituted into this table. The first sample is 60 numbered-section rows on PDF31–79. The repaired sample has quotas 28/26/26 over all three sections. Its aligned top-five unit recall is 304/352; random-page row recall is 1,242/1,286 on 18 pages, and stress-page recall is 561/561 on three pages. Four repaired global criteria fail. [validation.json](validation.json), `benchmark_scores/v1/summary`, `benchmark_scores/v2/summary`; [expected metrics](release/benchmark/expected-metrics.json), `v2/source_row_recall`.

The staged inputs contain 140 benchmark rows, 306 returned reading records, 21 chart cards, 21 source-count pages and 42 independent count readings. V1 includes 60 initial readings and six convenience repeats; v2 includes two 80-row readings and 80 adjudicated records. V1’s exploratory correction overlay and v2 adjudication notes are retained beside the original references. OCR strings were exposed in 22 v1 locators. V2’s shared helper collisions and directory-list observations are documented in the original reader metadata. All readers and adjudication were AI-assisted; agreement and computation do not supply human expert certification. [Reader metadata](release/benchmark/reader-metadata.json); [conventions](release/benchmark/CONVENTIONS.md); [table manifest](release/provenance/table-manifest.json).

The portable scorer reuses `evaluate.py`’s scoring functions unchanged and `evaluate_repair.py`’s two geometry functions, adding a standalone data loader, bootstrap replay and new-prediction CLI. A fresh build reproduced **971/971** payload/scorer files byte for byte: 19 Parquet files, 949 PNGs and three scorer files. [build-replay-comparison.json](build-replay-comparison.json), `results`. This replay did not rerun glyph recognition.

## Census and study aggregates

The census selection contains 115 site/provenance entities, 17 publication entries, 37 collection observations, 15 dataset entries, 38 catalogue coverage runs, 19 section-split rows, 140 field-completeness observations, 68 museum-to-CISI joins and 111 bibliographic source pointers. The site and aggregate tables use synthesis v6; the earlier publication register is used for its bibliographic fields only. Every count keeps its stated unit and frame. The 19 CISI 1 Gujarat/north India ranges yield **493 entries, 327 matches and 166 absent keys**, with the 75/91 section split. These are key comparisons against a pinned export, not a worldwide object census. [validation.json](validation.json), `source_checks/CISI1_BC_493_327_166`; [census summary](release/provenance/census-summary.json), `coverage`.

The join table selects public museum accessions, CISI identifiers, concordance locators and our join methods. Corpus record IDs, sign sequences, metadata payloads and museum prose/images are not copied. The 68 joins combine 61 earlier pairs with seven reviewed additions; the additions lack full paired-field adjudication. The census still records 46 unresolved museum records out of 114. [census summary](release/provenance/census-summary.json), `museum_joins`; [join table](release/data/evidence_museum_joins.parquet). The original bibliographic access scopes are retained; Package O did not reopen all archaeological sources. Source text and image rights remain source-specific.

Four metrology mass-band rows and nine chance-control rows are authored aggregate outputs from the corrected exploratory study. The 90 Dholavira weights of 5–100 g fit **13.716 g**, while the 147 weights of 1.3–5 g fit **14.280 g**. The legacy western 136/18 match counts are below the jitter comparison means **170.246/38.727**. The original data are Enrico Ascalone, *Bronze Age Weights from Mesopotamia, Iran & Greater Indus Valley* (2022), Weight & Value 3, Wachholtz, with a contribution by Jan Tavernier. [Source access record](sources.json), `ASCALONE2022`; [mass-band table](release/data/weight_mass_bands.parquet); [chance-control table](release/data/weight_chance_controls.parquet). The full fit requires excluded catalogue inputs and the private method/code record; these small tables alone cannot reproduce it.

## Contamination screens and private backup

The build uses explicit field allowlists and retains input hashes. The final screen compares **105 complete singleton benchmark reference rows** against **6,878 distinct excluded-corpus sequences** and finds **zero matching directions**. Shorter or ambiguous candidate sets are assessed through provenance and field allowlists, not an exhaustive candidate expansion. The textual screen finds **zero 15-word overlap windows** against **496 local text witnesses**, excluding exact bibliographic title fields. This is a screen over available witnesses, not a proof covering every third-party sentence. [validation.json](validation.json), `sequence_screen`, `prose_screen`; raw match files remain in the local raw directory.

The [private-store card](private-store/README.md) inventories **1,038 files and 3,406,008,409 bytes** from the preserved hosting manifest. It explains the two restoration directories and four Helsinki backups, per-file checksums, path-preserving restoration and the relationship with GitHub/public staging. The old restore command handles the restoration directories only. The Hub restore recipe includes all six sets, and the new read-only checksum comparator checks every manifest row. Manifest `verified` flags are inherited; remote availability and checksums were not queried again. [Inventory summary](private-store/inventory-summary.json); [checksum manifest](private-store/checksums-manifest.json).
'''
    (HERE/'REPORT.md').write_text(report,encoding='utf8')
    retrospective='''# Package O retrospective

The package produced a local candidate with 19 configurations, 2,739 table rows and 949 attributed PNGs, and documented the existing private backup. Both staged benchmarks reproduce their frozen numerical endpoints. The [report](REPORT.md) gives the resulting populations and limits, and [validation.json](validation.json) records the checks.

## Reused work and approach

The registry and October 6 contribution assessment were reviewed before selection. The earlier chart source audit, redistribution record and consolidated atlas audit supplied the 1979 source licence, crop provenance and 16 retained ambiguities. Package M’s portable prediction copy avoided the original local-only prediction path; its unchanged scorers, frozen references, two repaired readings, source adjudication and chart cards supplied the benchmark. Synthesis v6 and the trimmed census registers supplied the site-level facts and aggregate tables. The corrected metrology summaries supplied four mass-band and nine chance-control rows. No recognition training, full digitization, census rebuild or metrological fit was repeated.

The protocol was written before packaging or score computation. A builder selected fields explicitly, serialized heterogeneous returned rows as JSON strings inside Parquet and copied only the approved PNGs. Source hashes and per-file decisions were retained. Every manifest-listed private prediction/model file was individually excluded in the audit. New scorer code loaded only the staged tables; the original core scoring functions were copied unchanged. A separate fresh build compared all 971 data/image/scorer files byte for byte.

## Problems and fixes

The preliminary directory inspection looked for a first-run `blind/CONVENTIONS.md` that does not exist. The repaired v2 convention file exists and was staged; v1’s original reading conventions and disclosures remain in its reader metadata. A preliminary JSON inspection encountered a UTF-8 BOM; source readers use `utf-8-sig`.

The first validation attempt failed before a completed report because `datasets` generated a Windows lock filename exceeding the path limit. Changing the working directory to Package O’s local raw folder and using a relative cache path fixed that failure without changing data. The next attempt computed scores but stopped in the prose scanner because `utf8-sig` is not a recognized encoding name; replacing it with `utf-8-sig` fixed the scanner and the optional prediction-file reader. Both partial logs and score files remain under the local raw directory.

The first completed validation reported five failures. Four were schema-string comparisons: Parquet renamed a list child from `item` to `element` while preserving its type, nullability and values. The validator now normalizes only that child-name spelling. The fifth comparison filtered the Gujarat/north India edition as `CISI1`, but those source rows use `CISI1-1987`; applying the source’s actual identifier recovered the declared 19 ranges and 493/327/166 counts. No source table or benchmark result changed. The failed report is preserved as `validation-2026-10-08-v3-failed.json`.

The next pass succeeded. A later checksum review found that a regenerated file manifest would otherwise include its own previous checksum. The final manifest excludes itself and hashes every other staged file. Subsequent passed reports preserve the intermediate validation states. The scorer’s CLI default was also made valid from both the package script and its staged `code/` copy. A fresh build confirmed unchanged payload bytes after those repairs.

A final package-check helper initially decoded PowerShell’s redirected prose log as UTF-8. That log is UTF-16, so decoding it with its actual encoding fixed the check. The prose scan itself had completed with no flags; this failure occurred while reading its result.

## Outcomes and remaining work

The prose/sequence screens found no candidate overlap at their declared windows and complete-singleton scope. They supplement the source/field allowlist and do not replace provenance or expert review. The final prose scan inspected all package Markdown, including the candidate and private cards. No upload, repository creation, visibility change, contact, submission, Git history operation or edit to another contributor’s directory occurred. The authorized dependency installation used `pip --no-cache-dir` in `indus-ml`; its package file record is separate from research outputs.

The owner must confirm licences for our work and supply author, affiliation and contact. The coordinator’s future private upload must be followed by hosted loading/viewer checks. Package N’s initial snapshot contained a Proposed protocol only; any later verified transcription needs its own rights and source audit before addition. The private backup’s remote state and a full restore were not reverified. The metrology tables link to private methods and omit the catalogue inputs. These remaining decisions and checks are explicit in the release checklist.
'''
    (HERE/'RETROSPECTIVE.md').write_text(retrospective,encoding='utf8')
    dump(HERE/'registry-entry.json',dict(id='HF-PUBLIC-RELEASE-2026-10-08-O',theme='licensed public dataset staging and private-backup documentation',status='Verified computation',
        question='Can an attributed, rights-filtered local Hugging Face candidate load and reproduce the frozen Helsinki row benchmarks while the Lipi-derived backup remains private?',
        outcome='Staged 19 configurations, 2739 table rows and 949 PNGs. All local loads, hashes and benchmark scores pass. Fresh build reproduces 971/971 payload/scorer files. Private card inventories 1038 files and 3406008409 bytes. No upload or visibility change.',
        challenge='Unlicensed Lipi-derived private payloads, provisional full transcription, heterogeneous annotations, Windows cache path limit, Parquet list-child naming and source edition spelling.',
        remedy='Explicit field/file allowlist and individual exclusions; CC BY source attribution and proposed own-work licences; standalone unchanged scoring core; relative raw cache; semantic list-child-name comparison and exact CISI1-1987 filter. Preserved failed and intermediate passed validation reports.',
        evidence=['experiments/2026-10-08-hf-public-release/PROTOCOL.md','experiments/2026-10-08-hf-public-release/REPORT.md','experiments/2026-10-08-hf-public-release/validation.json','experiments/2026-10-08-hf-public-release/rights-audit.json','experiments/2026-10-08-hf-public-release/build-replay-comparison.json','experiments/2026-10-08-hf-public-release/release/README.md','experiments/2026-10-08-hf-public-release/private-store/README.md'],
        retry_when='The owner confirms own-work licences and author/contact fields, the reviewer completes source samples and local replay, and the coordinator supplies a private uploaded revision for hosted checks. Add later verified rows only after a separate provenance/rights audit.'))

if __name__=='__main__':main()
