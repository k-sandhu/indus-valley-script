# Sign context and seals, package D2

The package analyzes 5,680 observed faces grouped into 4,695 physical components. Sign 740 is 9.67% of all positions and 10.67% of readable positions. Its site association after accounting for object type has q = 0.5379; only sign 032 survives correction among the ten most frequent signs (q = 0.002). The site-area comparison rests on 17 sites and does not retain a corrected association under the amended whole-object reference law. See [REPORT.md](REPORT.md) and [sign-analysis.json](run-2026-10-07-01/sign-analysis.json).

Among 1,609 known square-seal motifs, 1,246 are unicorns (77.44%; HHI 0.6054). Clean texts on 910 unicorn seals average 4.7945 positions, compared with 4.0194 on 155 rare-motif seals (q = 0.0012 conditional on site/type). The sign-distribution difference fails the exploratory length-conditioned comparison (q = 0.20525). Complete measured square seals have n = 1,027 and size CV = 0.2886; text length increases by 1.1590 positions per doubling of face area after site/motif adjustment (q = 0.0002). See [motif-concentration.json](run-2026-10-07-01/motif-concentration.json), [motif-association.json](run-2026-10-07-01/motif-association.json), [exploratory results](exploratory-2026-10-07-01/results.json) and [dimensions.json](run-2026-10-07-01/dimensions.json).

The original endpoint is **Frozen evaluation**. The amended tests and supplemental measurement coverage are **Exploratory**. Arithmetic and deterministic rerun have status **Verified computation**, with 106 passing checks, zero failures and 82 recomputed reference tails in [checks-2026-10-07-01.json](checks-2026-10-07-01.json). A further [43 checks](final-checks-2026-10-07-01.json) recompute 26 exploratory tails, independently check all correction families with SciPy and reproduce the supplement. Together these give 149 passes and zero failures. Source and archaeological validation remain for the reviewer. Work crossed midnight after the October 6 assignment; all new computation directories are dated October 7.

## Files and inputs

[PROTOCOL.md](PROTOCOL.md) and [site-table.json](site-table.json) were frozen before computation. [AMENDMENT-2026-10-07.md](AMENDMENT-2026-10-07.md) describes the two post-outcome refinements. [SOURCE-NOTES.md](SOURCE-NOTES.md) records extent definitions, preview pagination and dimension coding. [sources.json](sources.json) contains 18 bibliographic records, opened-versus-snippet status, acquisition hashes and failures. [RETROSPECTIVE.md](RETROSPECTIVE.md) records the approaches, problems and outcomes. [registry-entry.json](registry-entry.json) proposes the shared registry entry without editing it. [FILE-MANIFEST.json](FILE-MANIFEST.json) inventories every created file in both owned directories.

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
