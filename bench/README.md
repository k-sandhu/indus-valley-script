# Shared evaluation harness

`bench/` gives contributors the same tests for a sign key, meaning map, conjecture, restoration model or segmentation. A useful proposal predicts withheld observations or scores beyond rearrangements of its own assignments under a declared reference law. The harness preserves the project's earlier scoring definitions, supplies generated controls, records input and code hashes, and writes versioned aggregate JSON. Run it manually from the repository root with Python 3.13, NumPy and SciPy.

| Task | What it measures | Guide |
|---|---|---|
| `key-calibration` | Independent language-model score, frequency-band rearrangements, order-only separation and grouped-half checks | [Key calibration](key-calibration/README.md) |
| `meaning-map` | Directional class contrasts on object variables, within-band rearrangements, reliability, influence and planted-effect power | [Meaning maps](meaning-map/README.md) |
| `shots` | Alias/text closure, shared-round freezing, audited reads and statistic-family spending | [Conjecture shots](shots/README.md) |
| `restoration` | Known-slot graphic recovery, paired component comparisons and frozen release visual-row scores | [Restoration](restoration/README.md) |
| `segmentation` | Complete word-boundary precision/recall/F1, readable-script baselines and required line-break recall | [Segmentation](segmentation/README.md) |
| `selftest` | Generated positive/negative controls, nominal-rate simulations, hand calculations and loader failure cases | All five tasks |

```text
python -m bench selftest --out experiments/NEW-DATE-my-study/selftest.json
python -m bench key-calibration --help
```

Every reading, key, meaning map or conjecture submitted to this project attaches the relevant bench output. A restoration or segmentation proposal attaches its scorer output and comparison. Save each run at a new dated endpoint; existing output files are refused. A result uses `schema_version: "1.0"`, `task`, `synthetic` and `provenance`, followed by task-specific scores. Nonfinite measurements become JSON `null`, with an explicit computability field where needed. Exit status is 0 for a completed scoring run, 1 for a failed selftest and 2 for rejected inputs. A failed scientific prediction is a valid completed run.

The pass rules measure a proposal against its declared statistical control. The experiment record must establish how the proposal was constructed and which observations were withheld. Checks on a supplied key across two halves are fixed-key diagnostics; they become transfer evidence when the key was frozen without access to the scored material. Repartitioning examined objects leaves prior exposure in the spending ledger. A reviewer checks population freshness, source identity, alias closure, frozen predictions and the joint credence rule before accepting a claim.

Inputs may be JSON or JSONL. Acquired texts, sign sequences, source images and detailed derivatives stay local under [REDISTRIBUTION.md](../knowledge/provenance/REDISTRIBUTION.md). Bench emits aggregate results and source hashes. Detailed real-data exports belong under `data/raw/YYYY-MM-DD-bench/`; the October 13 implementation wrote none. [DATA.md](../knowledge/DATA.md) and [fetch_data.py](../tools/fetch_data.py) describe local inputs and acquisition pins. A fresh clone can run every synthetic mode; local reproductions need the separately held sources.

Submit an attempt entry with the schema used by [the registry](../knowledge/registry/README.md): `id`, `theme`, `status`, `question`, `outcome`, `challenge`, `remedy`, `evidence`, `retry_when`, `status_class` and `area`. Its evidence links the bench JSON, frozen specification and retrospective. Contributors propose shared-document edits in their owned package. Maintainers integrate entries under `knowledge/registry/attempts/`, run `python tools/kb.py build`, and review `python tools/kb.py check`. The [October 13 package](../experiments/2026-10-13-bench/PLAN.md) contains source comparisons and integration text.

Project code is under the Unlicense and documentation/generated aggregates under CC0 1.0. Imported project methods retain their source paths and SHA-256 hashes. Third-party inputs retain their source terms in [LICENSE](../LICENSE) and [REUSE.md](../REUSE.md).
