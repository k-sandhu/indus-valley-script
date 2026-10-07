# Weight metrology package

The parser covers **2,058 catalogue entries**, including **938 Greater Indus records**. A 60-entry rendered-page audit found **5 period-field errors (8.33%)**, repaired before fitting, with **0 observed mass/+x errors**. The intact certain Dholavira sample contains **298 objects**: unit **14.003 g** (bootstrap 95% interval **13.819–14.518**), fitted signal CV **4.32%** (interval **2.41–15.85%**). Its broader 568-object frame has **17.24% CV**. Of **701 western records**, **136 (19.40%)** have a smaller Indus residual than every local alternative, and **18 (2.57%)** meet the additional close-fit rule. [Report](REPORT.md), [validation](parser-validation-v2.json), [model results](runs/2026-10-06-main/model-comparisons.json), [western results](runs/2026-10-06-main/western-compatibility.json).

The principal mass fits are a Frozen evaluation, with arithmetic recorded as Verified computation. Per-site Monte Carlo seed deviations are labelled Exploratory in [implementation notes](IMPLEMENTATION-NOTES.md). The separate [Gulf supplement](gulf-supplement.json) is Exploratory: **6/7** selected Qala'at al-Bahrain weights fall within 3% of either 13.5 or 13.65 g with the source-derived Gulf series. A complete Gulf assemblage analysis and several requested full-text precedent reviews remain unfinished. [Source access record](sources.json).

## Files and source handling

Start with [PROTOCOL.md](PROTOCOL.md), [REPORT.md](REPORT.md) and [RETROSPECTIVE.md](RETROSPECTIVE.md). The main endpoint is `runs/2026-10-06-main/`; [summary tables](summary-tables/manifest.json) flatten counts, unit intervals, quantogram peaks and western sensitivities. [Verification](verification.json) independently checks 45 likelihoods, 169 cosine scores and all 701 western classifications. A [full rerun](reproduction.json) reproduced all 18 numerical files and nine local derivatives byte for byte. [Registry proposal](registry-entry.json) is for the coordinator to integrate. [File inventory](FILES.json) enumerates the package's created files and local raw witnesses with hashes.

The source PDF already held by the project is `data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf`. The parser rows are local-only at `data/raw/2026-10-06-weight-metrology/extraction-v6/catalogue-rows.json`. The local directory also holds earlier extraction witnesses, 60-entry audit images, downloaded literature, web-result records, bootstrap draws and object assignments. No third-party payload was copied into the owned directory.

Reused prior work: the regional-west entry framing/dehyphenation approach, the 938-entry site-count audit, +x/mark handling from its census, and the Susa accession-collision/mass-disagreement findings. Their locations and the registry checks are documented in the retrospective. No shared registry, index, manuscript or earlier endpoint was changed.

## Rerun from the repository root

Requirements are Python, NumPy, SciPy, PyMuPDF (`fitz`) and Pillow. The endpoint used Python 3.13.5, NumPy 2.2.6 and SciPy 1.17.1. Scripts refuse existing output paths. Use fresh names on later reviews. Set library temporary locations inside the local raw directory in PowerShell:

```powershell
$metrologyTemp = Join-Path (Get-Location) 'data/raw/2026-10-06-weight-metrology/tmp'
New-Item -ItemType Directory -Force -Path $metrologyTemp | Out-Null
$env:TMP = $metrologyTemp
$env:TEMP = $metrologyTemp
$env:MPLCONFIGDIR = Join-Path $metrologyTemp 'mpl'
```

Extract all entries and regenerate the fixed random sample's PDF crops:

```powershell
python -X utf8 experiments/2026-10-06-weight-metrology/parse_catalogue.py --raw-output data/raw/2026-10-06-weight-metrology/review-extraction --summary-output experiments/2026-10-06-weight-metrology/review-extraction.json --render-sample
```

The audit script reconstructs the recorded author review and checks repairs. Running it does not perform a new visual review. The reviewer should inspect the regenerated crops and full source pages independently, especially IDs 652, 758, 892, 930 and 1892, and the seven crop-repair IDs in the raw audit.

```powershell
python -X utf8 experiments/2026-10-06-weight-metrology/validation_audit.py --output experiments/2026-10-06-weight-metrology/review-validation.json --raw-output data/raw/2026-10-06-weight-metrology/review-manual-validation.json
```

Recompute all main fits, 1,800 bootstrap refits and ten 999-surrogate quantograms. The original run took 137 seconds on this environment; timing varies. This repeats the documented successive seeds.

```powershell
python -X utf8 experiments/2026-10-06-weight-metrology/analyze.py --rows data/raw/2026-10-06-weight-metrology/review-extraction/catalogue-rows.json --output experiments/2026-10-06-weight-metrology/runs/reviewer-rerun --raw-output data/raw/2026-10-06-weight-metrology/reviewer-rerun
python -X utf8 experiments/2026-10-06-weight-metrology/verify.py --output experiments/2026-10-06-weight-metrology/review-verification.json
```

`verify.py` checks the original frozen endpoint. Compare a fresh run's numerical output hashes with the original using `compare_runs.py`; timestamp/path/timing manifests are checked separately.

```powershell
python -X utf8 experiments/2026-10-06-weight-metrology/compare_runs.py --actual experiments/2026-10-06-weight-metrology/runs/reviewer-rerun --actual-raw data/raw/2026-10-06-weight-metrology/reviewer-rerun --output experiments/2026-10-06-weight-metrology/review-reproduction.json
python -X utf8 experiments/2026-10-06-weight-metrology/make_summaries.py --output experiments/2026-10-06-weight-metrology/review-summary-tables
python -X utf8 experiments/2026-10-06-weight-metrology/gulf_supplement.py --output experiments/2026-10-06-weight-metrology/review-gulf.json --raw-output data/raw/2026-10-06-weight-metrology/review-gulf-scores.json
python tools/review_prose.py --path experiments/2026-10-06-weight-metrology --no-write
```

`acquire_sources.py` records the public PDF downloads, including failures, and refuses to overwrite `literature/acquisition.json`. Remeasurement, complete analytical-attribution joins, independent page review, source class/context reconciliation and additional Gulf assemblages require new evidence and separately dated work.
