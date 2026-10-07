# Backward chronology: review corrections

Status: Exploratory; arithmetic: Verified computation. The corrected table has **65 rows, 50 sources, 17 claims and 30 dated contributing rows** (2 A, 15 B, 13 C). Broad possible coverage has no empty century; A+B at any strength has two 100-year empty bins. The high/moderate-calendar A+B longest internal run ranges **400–1,600 years** across 80 Pirak/Perumbalai scenarios, with 1,600 years at the current low ratings. If Perumbalai is hypothetically moderate the range is 400–1,200. The result depends on those two rows and the inclusion rule, and measures inventory coverage. [Summary](run-2026-10-07-04/summary.json), `gaps`; [scenarios](sensitivity-04/gap-sensitivity.json), `scenario_ranges`; [comparison](coverage-02/comparison.json).

Use [inputs-05/evidence-table.json](inputs-05/evidence-table.json) and [CSV](inputs-05/evidence-table.csv) for current rows; [sources](inputs-05/sources.json) for exact citations, opened-page scope and local hashes; [REPORT](REPORT.md) for source corrections and the revised fifth-century comparison; [COVERAGE](coverage-02/COVERAGE.md) for all 33 centuries; [TEST-DESIGNS](TEST-DESIGNS.md) for seven falsifiable designs and acquisition/power targets. The two earlier evidence/run endpoints remain unchanged. Their documentation now points here; previous documentation is preserved in [documentation-before](documentation-before/).

Pirak is split into its captioned Period II and IIIA specimens, C/low, with no primary absolute date secured. The opened CISI 2 p. 381 entries Pk-15–17 are Period IB, so that citation does not join the later seals. The original 1979 chronology and 2010 recalibration chapter remain unopened. The 2012 publisher paper and primary catalogue sections were opened. Perumbalai's locator and strength were corrected; omitted marked and unmarked dated contexts were added; site-wide counts follow one exclusion rule. Eight claim and ten bibliographic records were repaired or retain explicit uncertainty. [Field changes](inputs-05/correction-log.json); [recovery audit](recovery-audit.json).

The earlier amendment's 193 added specimens comprise 191 inscribed sherds/sealing and two motif-bearing specimens without surviving script. Its protocol's negative source-recovery conditions were met for the causal kiln replacement, direct circa-2800 hearth/sample join, and authenticated aligned two-script pair: all three remain unrecovered. The primary evidence supports an early local mark/seal sequence, while the diagnostic post-urban transmission chain remains unverified. [Dating details](inputs-05/dating-details.json), `specimen_units`, `harappa`; [lecture audit](inputs-05/lecture-claim-audit.json); [contact records](inputs-05/contact-items.json).

Rerun from the repository root with Python 3. No installation is needed for the documentary computations. Every output path must be fresh and remain inside this amendment. Existing output directories are rejected.

```powershell
$e = 'experiments/2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections'
python -X utf8 "$e/build_corrections.py" --output "$e/reviewer-inputs-01"
python -X utf8 "$e/analyze_coverage.py" --inputs "$e/reviewer-inputs-01" --output "$e/reviewer-run-01"
python -X utf8 "$e/gap_sensitivity.py" --inputs "$e/reviewer-inputs-01" --output "$e/reviewer-sensitivity-01"
python -X utf8 "$e/power_targets.py" --output "$e/reviewer-power-01.json"
python -X utf8 "$e/document_coverage.py" --output "$e/reviewer-coverage-02"
python -X utf8 "$e/audit_recovery.py" --output "$e/reviewer-recovery-01.json"
python -X utf8 "$e/verify_review.py" --output "$e/reviewer-checks-01.json"
python tools/review_prose.py --path experiments/2026-10-06-backward-chronology --no-write
```

The builder reuses the 54-row amendment, its source/claim/audit records and existing raw witnesses. The coverage code reuses the inherited estimator functions; the sensitivity script adopts the review's row-substitution method. The October 2 South India work supplied the Tamil Nadu books and earlier annotation problems. CISI 2 was reused from the evidence-census package. [Retrospective](RETROSPECTIVE.md) records recovery attempts and text revisions.

Optional network recovery is separate from computation. Run `recover_sources.py --output data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections/reviewer-recovery-01`. It uses three observed URLs, caps each response at 25 MB, validates PDF signatures and sets TMP/TEMP/MPLCONFIGDIR under that fresh raw directory. It does not retrieve the unopened 1979 report or 2010 chapter. All raw pages, excerpts, images and response payloads remain local-only. Ten search batches and five original downloads, including two HTTP 403 failures, are preserved. [Recovery audit](recovery-audit.json), `query_witnesses`, `acquisitions`.

The reviewer should repeat full-field CSV/JSON equality, both new run reproductions, the 80-scenario range, power arithmetic and pre-existing file hashes, then sample Pirak's captions/catalogue periods, Volume II's calibration table and Sali's Phase V pages. The complete created/changed path list is [file-manifest.json](file-manifest.json). [Checks](review-checks-02.json) distinguishes verified computation from archaeological associations still requiring primary joins.
