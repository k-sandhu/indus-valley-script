# Sign context and seals, package D2

The **post-launch amendment of 7 October** adds the coordinator's five caption-checked comparisons. None of eight adequately sampled sites is a corrected richness outlier after matching object type, object count and readable-token count. The all-face readable top-3/top-6/top-20 shares are **18.64%, 27.51% and 48.76%**. Sign 740 is terminal in **874/1,256 occurrences (69.59%)** in 2,497 selected complete texts. Recorded Harappa phase shares vary (heterogeneity q = **0.007**), while the dating-allocation confidence envelope permits changes from **−24.86 to +85.77 percentage points** between 3B and 3C. Core known motifs are **1,236/1,604 unicorn**; external known motifs are **15/27 Gaur**, including **13/13 known circular motifs**. The dated section in [REPORT.md](REPORT.md) explains scope and uncertainty, and the new outputs carry `stage: post-launch amendment`.

The package analyzes 5,680 observed faces grouped into 4,695 physical components. Sign 740 is 9.67% of all positions and 10.67% of readable positions. Its site association after accounting for object type has q = 0.5379; only sign 032 survives correction among the ten most frequent signs (q = 0.002). The site-area comparison rests on 17 sites and does not retain a corrected association under the amended whole-object reference law. See [REPORT.md](REPORT.md) and [sign-analysis.json](run-2026-10-07-01/sign-analysis.json).

Among 1,609 known square-seal motifs, 1,246 are unicorns (77.44%; HHI 0.6054). Clean texts on 910 unicorn seals average 4.7945 positions, compared with 4.0194 on 155 rare-motif seals (q = 0.0012 conditional on site/type). The sign-distribution difference fails the exploratory length-conditioned comparison (q = 0.20525). Complete measured square seals have n = 1,027 and size CV = 0.2886; text length increases by 1.1590 positions per doubling of face area after site/motif adjustment (q = 0.0002). See [motif-concentration.json](run-2026-10-07-01/motif-concentration.json), [motif-association.json](run-2026-10-07-01/motif-association.json), [exploratory results](exploratory-2026-10-07-01/results.json) and [dimensions.json](run-2026-10-07-01/dimensions.json).

The original endpoint is **Frozen evaluation**. The amended tests and supplemental measurement coverage are **Exploratory**. Arithmetic and deterministic rerun have status **Verified computation**, with 106 passing checks, zero failures and 82 recomputed reference tails in [checks-2026-10-07-01.json](checks-2026-10-07-01.json). A further [43 checks](final-checks-2026-10-07-01.json) recompute 26 exploratory tails, independently check all correction families with SciPy and reproduce the supplement. Together these give 149 passes and zero failures. Source and archaeological validation remain for the reviewer. Work crossed midnight after the October 6 assignment; all new computation directories are dated October 7.

## Files and inputs

[PROTOCOL.md](PROTOCOL.md) and [site-table.json](site-table.json) were frozen before computation. [AMENDMENT-2026-10-07.md](AMENDMENT-2026-10-07.md) describes the two post-outcome refinements. [SOURCE-NOTES.md](SOURCE-NOTES.md) records extent definitions, preview pagination and dimension coding. [sources.json](sources.json) contains 18 bibliographic records, opened-versus-snippet status, acquisition hashes and failures. [RETROSPECTIVE.md](RETROSPECTIVE.md) records the approaches, problems and outcomes. [registry-entry.json](registry-entry.json) proposes the shared registry entry without editing it. [FILE-MANIFEST.json](FILE-MANIFEST.json) inventories the initial package. The separate [follow-up manifest](FILE-MANIFEST-FOLLOWUP-2026-10-07.json) lists all added and changed paths for this continuation.

The corpus input is the existing `data/normalized/lipi_observed_faces.jsonl`, SHA256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`. Earlier context code, its frozen classifier result, the orientation check and Paper 002 were reused as described in the report. The primary JSON outputs are aggregate statistics. Third-party pages/PDFs, extracted witnesses, object identifiers and reference arrays stay in `data/raw/2026-10-06-sign-context-and-seals/`, which is local-only and Git-ignored. No shared repository files were changed.

## Rerun from the repository root

The computation uses Python, NumPy and SciPy; the recorded run used Python 3.13.5, NumPy 2.2.6 and SciPy 1.17.1. Source acquisition additionally uses Requests and pypdf. Existing local witnesses suffice to review sources without redownloading. Each computation refuses an existing output directory. Choose a fresh name if a command has already run.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TMP = Join-Path (Get-Location) 'data/raw/2026-10-06-sign-context-and-seals/tmp'
$env:TEMP = $env:TMP
$env:MPLCONFIGDIR = $env:TMP
python experiments/2026-10-06-sign-context-and-seals/analyze.py --run reviewer-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/verify.py --replicate reviewer-2026-10-07-01 --output reviewer-checks-2026-10-07-01.json
python experiments/2026-10-06-sign-context-and-seals/sensitivity.py --run reviewer-exploratory-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/supplement.py --run reviewer-supplement-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/finish_checks.py --exploratory reviewer-exploratory-2026-10-07-01 --supplement reviewer-supplement-2026-10-07-01 --output reviewer-final-checks-2026-10-07-01.json
python tools/review_prose.py --path experiments/2026-10-06-sign-context-and-seals --no-write
```

The primary run takes about 70 seconds on this machine. Defaults are seed 2026100701, 9,999 references and 2,000 bootstrap draws; changing them creates a different endpoint. The sensitivity uses seed 2026100702. The verifier compares all five analytical files with the original and checks the original saved local arrays. Its exploratory length-invariance check refers to the recorded exploratory directory; compare a fresh exploratory run's tests separately because its timestamp and runtime differ.

`supplement.py` accepts a fresh output name as shown above. `finish_checks.py` checks exploratory tails and correction values with a separate SciPy implementation. `inventory.py --output <fresh-filename.json>` inventories both owned directories. Source acquisition commands are `python experiments/2026-10-06-sign-context-and-seals/acquire_sources.py --batch <fresh-batch> --only <asset-id ...>`; identifiers and URLs are in that script. `build_sources.py` builds the bibliography from recorded batches. It is a manifest helper, not a frozen analysis rerun.

The reviewer should sample Kenoyer's printed p. 54/Table 4.2, Suryanarayan's printed p. 87/Table 4.1, Treccani's settlement hierarchy and **Chanu daro** section, and Lothal's tentative-list Description. Check open area bounds and uncertain footprints, family/side aliases, length-based representative selection, zeros and thickness ranges, exact preservation labels, and the three period cohorts around Harappa 3C. Obtain the unread style/size papers and identify the requested Rao motif precedent before extending interpretation. The package's results do not discriminate governance, workshop concentration and excavation selection.

## Post-launch lecture amendment, 7 October

[AMENDMENT-2026-10-07-LECTURE.md](AMENDMENT-2026-10-07-LECTURE.md) was written before the new computation. [sources-followup-2026-10-07.json](sources-followup-2026-10-07.json) adds eight records and nine acquisition attempts; the exact Wells tables behind the four lecture percentages and inventory bands were not recovered. Published concentration/end-position precedents and the Salūt bison discussion were opened. The 2023 encyclopedia primary page returned 403, so its quoted percentages remain secondary-summary evidence.

The complete new endpoint is [post-launch-2026-10-07-02](post-launch-2026-10-07-02/summary.json), containing `richness.json`, `concentration.json`, `terminal740.json`, `period-stability.json` and `external-motifs.json`. Richness curves for every site, shared curves and corrected site-reference comparisons are in `richness.json`; extrapolation stops at twice each sample. Figures show [richness curves and conditional bands](figures-post-launch-2026-10-07-02/richness-curves.svg) and [terminal excess rates](figures-post-launch-2026-10-07-02/terminal740-excess.svg). The [42-object external list](../../data/raw/2026-10-06-sign-context-and-seals/post-launch-2026-10-07-02/external-objects.csv) stays local-only. Its geographic classification uses the declared export regions; some Iranian Plateau entries are Indus-peripheral Balochistan sites. The Gulf/Mesopotamia sensitivity supplies a narrower external comparison.

[checks-post-launch-2026-10-07-02.json](checks-post-launch-2026-10-07-02.json) records **760 passes, zero failures**. Four new analytical files reproduce byte for byte. External aggregates reproduce after checking and normalizing their run-specific local paths; both external-object lists reproduce byte for byte. Checks verify 101 prior pinned files, the previous manifest and exact archives of the four updated living documents. The first follow-up run stopped at a NumPy-integer serialization error; its two completed outputs, local references, code and [failure record](post-launch-2026-10-07-01/FAILURE.json) remain unchanged. The original D2 endpoints are preserved.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TMP = Join-Path (Get-Location) 'data/raw/2026-10-06-sign-context-and-seals/tmp'
$env:TEMP = $env:TMP
$env:MPLCONFIGDIR = $env:TMP
python experiments/2026-10-06-sign-context-and-seals/lecture_followup.py --run reviewer-post-launch-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/verify_followup.py --replicate reviewer-post-launch-2026-10-07-01 --output reviewer-post-launch-checks-2026-10-07-01.json
python tools/review_prose.py --path experiments/2026-10-06-sign-context-and-seals --no-write
```

The full new run took 18.67 seconds with seed 2026100703, 9,999 references and 2,000 bootstrap draws. The computations use existing NumPy/SciPy. Optional `plot_followup.py --input <run> --output <fresh-figure-directory>` uses Matplotlib 3.11.2 and dependencies installed only under the local raw directory, and sets its writable configuration directory there. `acquire_followup_sources.py --batch <fresh-name> --only <asset-id ...>` preserves new source witnesses and failures. `build_followup_sources.py` is a bibliography helper whose existing output is protected from overwrite.

Reviewer priorities are the exact Chao1/Chao2 formulas and extrapolation limits, type/length block preservation, the clean-text terminal filter and logarithmic Poisson-binomial tails, ambiguous 3B/C allocation bounds, the one-object 3A cohort in the interval model, and the Gaur code/region mapping for external finds. The 95% dating envelope allows zero and both directions of a ten-percentage-point change. A millennium-long constancy claim remains outside the dated sample's 700-year scope.

## Recovery after the disk interruption

The [7 October recovery audit](recovery-audit-2026-10-07-01.json) found all 1,850 previously inventoried files intact: 1,849 recorded hashes matched, all JSON files parsed, and no repair or statistical rerun was needed. [RETROSPECTIVE.md](RETROSPECTIVE.md) records the user-reported Windows error 112 interruption and the format/link checks. Cleanup removed only a regenerable 145,391-byte font cache, recorded in [recovery-cleanup-2026-10-07.json](recovery-cleanup-2026-10-07.json). No source, endpoint or required dependency was removed. The [recovery manifest](FILE-MANIFEST-RECOVERY-2026-10-07.json) lists the final state of both owned directories, including every created or changed path. Both earlier manifests remain as historical snapshots.

Artifact review can be repeated without loading the reference arrays into memory or rerunning statistics:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TMP = Join-Path (Get-Location) 'data/raw/2026-10-06-sign-context-and-seals/tmp'
$env:TEMP = $env:TMP
$env:MPLCONFIGDIR = $env:TMP
python experiments/2026-10-06-sign-context-and-seals/recovery_audit.py --manifest FILE-MANIFEST-RECOVERY-2026-10-07.json --output reviewer-recovery-audit-2026-10-07-01.json
```
