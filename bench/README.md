# Shared evaluation harness

`bench/` gives contributors the same tests for a sign key, meaning map, conjecture, restoration model or segmentation. A proposal is useful when it predicts observations withheld from it, or when it scores better than rearrangements of its own assignments drawn under a declared reference law (the probability rule for the rearrangements). The harness keeps the project's earlier scoring definitions, supplies generated controls, records input and code hashes, and writes versioned aggregate JSON. Run it by hand from the repository root with Python 3.13, NumPy and SciPy.

| Task | What it measures | Guide |
|---|---|---|
| `key-calibration` | Independent language-model score against rearrangements within frequency bands, a sign-order test, and checks on two halves that keep related texts together | [Key calibration](key-calibration/README.md) |
| `meaning-map` | Predicted differences between sign classes in object variables against within-band rearrangements; reliability, single-object influence and planted-effect power | [Meaning maps](meaning-map/README.md) |
| `shots` | Grouping of aliases and identical texts, freezing every shot before confirmation opens, logged reads, and a ledger of statistic families already tested | [Conjecture shots](shots/README.md) |
| `restoration` | Recovery of a sign hidden at a known position, paired comparisons with a baseline, and printed-row recognition scores for the frozen release | [Restoration](restoration/README.md) |
| `segmentation` | Word-boundary precision, recall and F1 against complete word divisions; baselines from readable scripts; recall of required line breaks | [Segmentation](segmentation/README.md) |
| `selftest` | Generated positive and negative controls, nominal error-rate simulations, hand calculations and loader failure cases | All five tasks |

```text
python -m bench selftest --out experiments/NEW-DATE-my-study/selftest.json
python -m bench key-calibration --help
```

Every reading, key, meaning map or conjecture submitted to this project attaches the relevant bench output. A restoration or segmentation proposal attaches its scorer output and comparison. Save each run at a new dated endpoint; the harness refuses existing output files. A result has the fields `schema_version: "1.0"`, `task`, `synthetic` and `provenance`, followed by the task's scores. A measurement that is not a finite number becomes JSON `null`, with an explicit computability field where needed. The exit status is 0 for a completed scoring run, 1 for a failed selftest and 2 for rejected inputs. A run whose scientific prediction fails is still a valid completed run.

A pass rule compares a proposal only with its declared statistical control; the experiment record must show how the proposal was constructed and which observations were withheld. Checks of a supplied key on two halves describe that fixed key, and they become evidence of transfer when the key was frozen without access to the scored material. Re-splitting examined objects leaves their earlier exposure in the spending ledger, `bench/spent.json`. Before accepting a claim, a reviewer checks population freshness, source identity, alias grouping, the frozen predictions and the joint credence rule for predictions that share objects.

Inputs may be JSON or JSONL. Acquired texts, sign sequences, source images and detailed derivatives stay local under [REDISTRIBUTION.md](../knowledge/provenance/REDISTRIBUTION.md), and the harness writes only aggregate results and source hashes. Detailed exports of real data belong under `data/raw/YYYY-MM-DD-bench/`; the October 13 implementation wrote none. [DATA.md](../knowledge/DATA.md) and [fetch_data.py](../tools/fetch_data.py) describe local inputs and their pinned source versions. A fresh clone can run every synthetic mode; reproducing results on real data needs the separately held sources.

Submit an attempt entry with the schema used by [the registry](../knowledge/registry/README.md): `id`, `theme`, `status`, `question`, `outcome`, `challenge`, `remedy`, `evidence`, `retry_when`, `status_class` and `area`. Its `evidence` links the bench JSON, the frozen specification and the retrospective. Contributors propose edits to shared documents inside their own package. Maintainers integrate entries under `knowledge/registry/attempts/`, run `python tools/kb.py build` and review `python tools/kb.py check`. The [October 13 package](../experiments/2026-10-13-bench/PLAN.md) contains the source comparisons and the text proposed for integration.

Project code is under the Unlicense, and documentation and generated aggregates are under CC0 1.0. Methods imported from earlier project work keep their source paths and SHA-256 hashes. Third-party inputs keep their source terms, recorded in [LICENSE](../LICENSE) and [REUSE.md](../REUSE.md).
