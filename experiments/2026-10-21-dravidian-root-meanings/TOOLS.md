# Reproducing the mechanical run

Run these commands from the repository root with Python 3.13, NumPy 2.2 and SciPy 1.17. `pdftotext` must be on PATH. Each command that reads acquired material uses isolated Python. The scripts add their own code directory and the interpreter's installed user-package directory explicitly; they do not process package-directory `.pth` files or import downloaded code.

In PowerShell, set the two task paths once:

```powershell
$studyCode = 'experiments/2026-10-21-dravidian-root-meanings/code'
$studyLocal = 'data/raw/2026-10-21-dravidian-root-meanings/codex-run1'
```

## Acquisition and input preparation

Run acquisition serially. Requests use the study's descriptive User-Agent, a minimum interval of 0.65 seconds and up to four attempts with back-off. A saved file is reused only when its hash matches the request log. Archives are inspected for unsafe paths and symbolic links before extraction. Extraction refuses an existing destination; an acquisition rerun reuses an already extracted source.

```powershell
python -I "$studyCode/acquire.py" kolipakam
python -I "$studyCode/acquire.py" dravlex
python -I "$studyCode/acquire.py" dedr
python -I "$studyCode/acquire.py" s4
python -I "$studyCode/tips.py"
python -I "$studyCode/dedr_parse.py"
python -I "$studyCode/tips.py"
python -I "$studyCode/validate_run1.py" audit
python -I "$studyCode/tree.py"
python -I "$studyCode/coding.py"
python -I "$studyCode/reference.py"
```

The first mapping command records the front-matter rules. The second adds every label encountered in the selected parsed inputs. Review the uncertain identifications and the local parse audit before freezing. The dictionary search cards and their resolution are in `s4-result-resolution.json`; `s4-entries.json` identifies the files actually used by S4. Earlier parsed files outside that index remain local records of parser development.

`tree.py` extracts the supplementary PDF's text and searches for a burn-in statement. It records the evidence locally, inspects only the XML run and tree-logger tags, counts posterior records and selects 1,000 trees. `--burnin FRACTION` permits an explicitly reviewed supplementary-text decision. The run used the protocol's 0.10 default. The compressed sample has a fixed gzip timestamp for reproducible bytes. The posterior ZIP was extracted during acquisition; its regenerable extraction was removed after a storage failure. The reader streams the verified ZIP when that cache is absent.

## Tests and release checks

```powershell
python -I "$studyCode/test_recon.py"
python -I "$studyCode/compute.py" --synthetic "$studyLocal/synthetic-v2"
python -I "$studyCode/compute.py"
python -I "$studyCode/validate_run1.py" scan
python tools/review_prose.py --path experiments/2026-10-21-dravidian-root-meanings --no-write
python -I "$studyCode/validate_run1.py" status
git status --short
```

The selftest writes `run1/selftest.json`. It includes exhaustive comparisons, closed cases, planted traits, sense-rule and parsing tests, reference draws, output guards and 500 calibration simulations for each tree family. Both known-rate and fitted-rate calibration tables have ten probability bins and exact binomial intervals. Simulated and fabricated traits are the only traits reconstructed in this run.

The synthetic command exercises both the MCC topology and a random tree, including all sensitivity branches and a three-tree sample for the posterior-summary code. Choose a new local output directory for another synthetic run. The command without `--synthetic` is expected to fail while `FREEZE.json` is absent. The test suite separately checks missing, mismatched and matching freeze hashes, and rejection of an existing output directory.

The source-text scan compares all code and aggregate files against parsed forms and segments longer than three characters. It exempts vocabulary in the frozen class rules, records literal overlaps locally and distinguishes Python syntax from prose and strings. Ordinary English, filenames, grammar labels, booleans and source-name overlaps receive a local review record. The tracked scan reports counts and hashes without reproducing the matches. Review that local record when reproducing the check.

## Frozen computation

The coordinating session writes `FREEZE.json` after review. The simplest accepted structure is an object whose `code_hashes` member maps every relative filename under `code/` to its SHA-256. The gate compares the complete file set, including unexpected extra files. Every study script disables bytecode writes.

After freezing, run:

```powershell
python -I experiments/2026-10-21-dravidian-root-meanings/code/compute.py
```

It creates `results-v1/results.json` and local `results-v1-detail/`. Both directories must be absent. It reserves them before reconstruction and leaves a failed run in place. The primary fit covers all needed meanings and every pooled head. S5 refits each needed meaning on all 1,000 trees. The resulting computation can take substantially longer than the tests.

For S8, place a JSON array in local `manual-recode.json`. Each object gives `meaning`, `entry`, `form_index`, `segment_index` and boolean `member`. An optional `segment_sha256` checks the normalised segment. `coding.py --recode PATH` prepares an explicit recode file; the driver also detects the default local filename and prepares S8 before reconstruction. A post-outcome S8 analysis needs its own preserved output package because this driver never overwrites `results-v1/`.

## Files and handling

| Destination | Contents | Handling |
|---|---|---|
| `code/` | Acquisition, parsing, mapping, tree reader, reconstruction, coding, reference draw, driver, tests and validation | Track |
| `run1/` | Source manifests, parse counts, mapping, tree summary, pool sizes, selftests, scan and verification counts, path inventory | Track |
| `PLAN-CODEX.md`, `TOOLS.md`, `CODEX-NOTES-RUN1.md` | Plan, commands and review record | Track |
| `downloads/kolipakam2018/`, `downloads/kolipakam2018-posterior/` | Five supplement files, source metadata and extraction metadata; full posterior retained in its ZIP | Local |
| `downloads/dravlex/` | Pinned archive, licence metadata and extracted data | Local |
| `codex-run1/dedr/` | Dictionary pages, definition searches and front matter | Local |
| `codex-run1/parsed/`, `codex-run1/codings/`, `codex-run1/reference/` | Dictionary text, per-tip evidence, coding variants and pools | Local |
| `codex-run1/posterior/` | Selected tree sample | Local |
| Other files under `codex-run1/` | Request logs, audits, review records, synthetic outputs and guard fixtures | Local |

`run1/created-paths.json` lists the individual tracked and local files. The source manifests record acquisition coverage for later integration into the shared data records. This run edits no shared record and computes no reconstruction on real codings.
