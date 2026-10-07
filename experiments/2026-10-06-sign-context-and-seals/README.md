# Sign context and seals, package D2

The package analyzes 5,680 observed faces grouped into 4,695 physical components. Sign 740 is 9.67% of all positions and 10.67% of readable positions. Its site association after accounting for object type has q = 0.5379; only sign 032 survives correction among the ten most frequent signs (q = 0.002). The frozen 17-site area law gives sign 520 q = 0.044 (minimum/maximum q = 0.044/0.047); it fails without the two cities (q = 0.387) and under the amended law (q = 0.223). The expanded 18-site post-review comparison has minimum q = 0.146 across its area vectors. See [REPORT.md](REPORT.md) and [sign-analysis.json](run-2026-10-07-01/sign-analysis.json).

Among 1,609 known square-seal motifs, 1,246 are unicorns (77.44%; HHI 0.6054). Clean texts on 910 unicorn seals average 4.7945 positions, compared with 4.0194 on 155 rare-motif seals (q = 0.0012 conditional on site/type). The sign-distribution difference fails the exploratory length-conditioned comparison (q = 0.20525). Complete measured square seals have n = 1,027 and size CV = 0.2886; text length increases by 1.1590 positions per doubling of face area after site/motif adjustment (q = 0.0002). See [motif-concentration.json](run-2026-10-07-01/motif-concentration.json), [motif-association.json](run-2026-10-07-01/motif-association.json), [exploratory results](exploratory-2026-10-07-01/results.json) and [dimensions.json](run-2026-10-07-01/dimensions.json).

The original endpoint is **Frozen evaluation**. The amended tests and supplemental measurement coverage are **Exploratory**. Arithmetic and deterministic rerun have status **Verified computation**, with 106 passing checks, zero failures and 82 recomputed reference tails in [checks-2026-10-07-01.json](checks-2026-10-07-01.json). A further [43 checks](final-checks-2026-10-07-01.json) recompute 26 exploratory tails, independently check all correction families with SciPy and reproduce the supplement. Together these give 149 passes and zero failures. The independent [review](REVIEW.md) reproduced these values and sampled sources. Work crossed midnight after the October 6 assignment; all new computation directories are dated October 7.

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
python experiments/2026-10-06-sign-context-and-seals/sensitivity.py --run reviewer-exploratory-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/supplement.py --run reviewer-supplement-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/finish_checks.py --exploratory reviewer-exploratory-2026-10-07-01 --supplement reviewer-supplement-2026-10-07-01 --output reviewer-final-checks-2026-10-07-01.json
python tools/review_prose.py --path experiments/2026-10-06-sign-context-and-seals --no-write
```

The primary run takes about 70 seconds on this machine. Defaults are seed 2026100701, 9,999 references and 2,000 bootstrap draws; changing them creates a different endpoint. The sensitivity uses seed 2026100702. The verifier compares all five analytical files with the original and checks the original saved local arrays. Its exploratory length-invariance check refers to the recorded exploratory directory; compare a fresh exploratory run's tests separately because its timestamp and runtime differ.

`supplement.py` accepts a fresh output name as shown above. `finish_checks.py` checks exploratory tails and correction values with a separate SciPy implementation. Source acquisition commands are `python experiments/2026-10-06-sign-context-and-seals/acquire_sources.py --batch <fresh-batch> --only <asset-id ...>`; identifiers and URLs are in that script. `build_sources.py` builds the bibliography from recorded batches. It is a manifest helper, not a frozen analysis rerun.

## Post-launch lecture amendment, 7 October

The lecture comparisons find no corrected richness outlier among eight sites. Readable top-3/top-6/top-20 shares are **18.64%, 27.51%, 48.76%**; **874/1,256 sign-740 occurrences (69.59%)** are terminal in the selected texts. Core known motifs include **1,236/1,604 unicorns**; external known motifs include **15/27 Gaur**, including **13/13 known circular motifs**. Exact outputs and the corrected period interpretation are linked below.

[AMENDMENT-2026-10-07-LECTURE.md](AMENDMENT-2026-10-07-LECTURE.md) was written before the new computation. [sources-followup-2026-10-07.json](sources-followup-2026-10-07.json) adds eight records and nine acquisition attempts; the exact Wells tables behind the four lecture percentages and inventory bands were not recovered. Published concentration/end-position precedents and the Salūt bison discussion were opened. The 2023 encyclopedia primary page returned 403, so its quoted percentages remain secondary-summary evidence.

The complete new endpoint is [post-launch-2026-10-07-02](post-launch-2026-10-07-02/summary.json), containing `richness.json`, `concentration.json`, `terminal740.json`, `period-stability.json` and `external-motifs.json`. Richness curves for every site, shared curves and corrected site-reference comparisons are in `richness.json`; extrapolation stops at twice each sample. Figures show [richness curves and conditional bands](figures-post-launch-2026-10-07-02/richness-curves.svg) and [terminal excess rates](figures-post-launch-2026-10-07-02/terminal740-excess.svg). The [42-object external list](../../data/raw/2026-10-06-sign-context-and-seals/post-launch-2026-10-07-02/external-objects.csv) stays local-only. Its geographic classification uses the declared export regions; some Iranian Plateau entries are Indus-peripheral Balochistan sites. The Gulf/Mesopotamia sensitivity supplies a narrower external comparison.

[checks-post-launch-2026-10-07-02.json](checks-post-launch-2026-10-07-02.json) records **760 passes, zero failures**. Four new analytical files reproduce byte for byte. External aggregates reproduce after checking and normalizing their run-specific local paths; both external-object lists reproduce byte for byte. Checks verify 101 prior pinned files, the previous manifest and exact archives of the four updated living documents. The first follow-up run stopped at a NumPy-integer serialization error; its two completed outputs, local references, code and [failure record](post-launch-2026-10-07-01/FAILURE.json) remain unchanged. The original D2 endpoints are preserved.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TMP = Join-Path (Get-Location) 'data/raw/2026-10-06-sign-context-and-seals/tmp'
$env:TEMP = $env:TMP
$env:MPLCONFIGDIR = $env:TMP
python experiments/2026-10-06-sign-context-and-seals/lecture_followup.py --run reviewer-post-launch-2026-10-07-01
python tools/review_prose.py --path experiments/2026-10-06-sign-context-and-seals --no-write
```

The full new run took 18.67 seconds with seed 2026100703, 9,999 references and 2,000 bootstrap draws. The computations use existing NumPy/SciPy. Optional `plot_followup.py --input <run> --output <fresh-figure-directory>` requires the local Matplotlib 3.11.2 install. OneDrive made that install online-only; the review received PermissionError and plotting is currently unavailable. Existing SVGs remain available. No plotting package was reinstalled or hydrated. `acquire_followup_sources.py --batch <fresh-name> --only <asset-id ...>` preserves new source witnesses and failures. `build_followup_sources.py` is a bibliography helper whose existing output is protected from overwrite.

## Recovery after the disk interruption

The [7 October recovery audit](recovery-audit-2026-10-07-01.json) found all 1,850 previously inventoried files intact: 1,849 recorded hashes matched, all JSON files parsed, and no repair or statistical rerun was needed. [RETROSPECTIVE.md](RETROSPECTIVE.md) records the user-reported Windows error 112 interruption and the format/link checks. Cleanup removed only a regenerable 145,391-byte font cache, recorded in [recovery-cleanup-2026-10-07.json](recovery-cleanup-2026-10-07.json). No source, endpoint or required dependency was removed. The [recovery manifest](FILE-MANIFEST-RECOVERY-2026-10-07.json) records both directories after that recovery; the current revision manifest adds the second follow-up changes. Both earlier manifests remain as historical snapshots.

The recovery audit and manifest record their earlier observation. After this requested protocol/source revision and OneDrive's availability change, use the current revision checker below; the historical recovery command expects the former files.

## Second follow-up after the Sonnet review

The original [site table](site-table.json) and all frozen numerical endpoints remain unchanged. The dated [protocol amendment](PROTOCOL.md) and [supplementary source table](site-extents-review-2026-10-07.json) add the Treccani site-entry extents and Banawali's 16-ha bounding square. Across four area vectors, the expanded **18-site, 4,452-object** comparison has minimum q values **0.177, 0.146, 0.156 and 0.167**. No sign passes correction. Results and the separately corrected nested label are in [post-review-2026-10-07-01](post-review-2026-10-07-01/summary.json); reference values are compressed locally.

The period q = **0.007** concerns 3C labels sharing **2200–1900 BCE**, with the review's 3C-only p = **0.0006**. Unambiguous 3B **6/7** and 3C **112/123** unicorns do not contradict the lecture's persistence statement. [REPORT.md](REPORT.md) quotes the caption-based summary accurately and retains the broad change envelope. The report also adds four precedents, the Ameri source of the approximate 65% multi-site average, explicit motif-code cross-checks and the second Salūt record's disagreement.

[sources-review-2026-10-07.json](sources-review-2026-10-07.json) distinguishes the opened Ameri chapter, Cambridge abstracts and Archaeopress contents. `sources.json` corrects the Banawali log and withdraws the unverified Frenez p. 167 attribution. Their exact preceding versions are archived in `pre-second-followup-2026-10-07/`. The original verification scripts pin the pre-amendment protocol and source metadata; those historical assertions no longer target the living files. The current checker validates their archived versions, original protocol prefix, frozen endpoints and the new references.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TMP = Join-Path (Get-Location) 'data/raw/2026-10-06-sign-context-and-seals/tmp'
$env:TEMP = $env:TMP
python experiments/2026-10-06-sign-context-and-seals/second_followup.py --run repeat-post-review-2026-10-07-01
python experiments/2026-10-06-sign-context-and-seals/verify_second_followup.py --run repeat-post-review-2026-10-07-01 --output repeat-post-review-checks-2026-10-07.json
python tools/review_prose.py --path experiments/2026-10-06-sign-context-and-seals --no-write
```

`second_followup.py --prepare` created the supplementary table before the first new area run; it refuses its existing input. The new run takes about 15 seconds, uses only NumPy/SciPy, and refuses existing output directories. No original endpoint needs to be rerun to check this revision. The removed duplicate checks file and its retained canonical digest are recorded in [revision-maintenance-2026-10-07.json](revision-maintenance-2026-10-07.json). All changes from this second follow-up are listed in [revision-manifest-final-2026-10-07.json](revision-manifest-final-2026-10-07.json), including unresolved OneDrive availability for the optional plotting install.

[checks-post-review-2026-10-07-01.json](checks-post-review-2026-10-07-01.json) records **395 passes, zero failures**. It reads all available historical artifacts with archived metadata substitutions and leaves the **1,670 online-only plotting files** unopened. The new compressed reference archive is **5,313,306 bytes**.
