# Coordinator integration text

These are proposed additions. This package changed only `bench/` and its own experiment files. The coordinator's `CODEX-PROMPT.md` and `launch.sh` were read-only inputs and are excluded from the created-path inventory. Shared documents, cards, the registry, manifests and other agents' packages are unchanged.

## AGENTS.md

Insert this bullet after the hard rule about preserving plans, outputs and source witnesses:

```markdown
- Every submitted reading, sign key, meaning map or conjecture attaches the relevant versioned output from `python -m bench <task>`. Read `bench/README.md` when choosing the protocol. Use the shared shots loader for confirmation, freeze every registered participant before the first read, and check `bench/spent.json` for prior use of the statistic family. A new seed over examined objects does not establish freshness.
```

Add this row to the intent table:

```markdown
| Evaluate a reading, key, map, restoration or segmentation | [bench](bench/README.md); `python -m bench <task> --help` | start-study, test-conjecture, verify-study |
```

## CONTRIBUTING.md

Insert after the paragraph beginning “Conjectures follow” in “Before starting”:

```markdown
Choose the relevant [bench task](bench/README.md) when recording a protocol. Every submitted reading, key, meaning map or conjecture attaches its bench JSON and frozen specification. Restoration and segmentation proposals attach scorer outputs and declared comparisons. Inputs and code hashes, construction data, population freshness and failed predictions remain part of the evidence record.
```

Add to “Verification and completion” after the existing check commands:

```markdown
Changes to the shared harness also run `python -m bench selftest` into a new dated output file. A contributor who changes a scorer reproduces its pinned source endpoint and records any population or definition difference. Bench outputs and freeze records enter the attempt's `evidence`; maintainers integrate cards and rebuild the knowledge map after review.
```

## Repository skills

Append to `.claude/skills/orient/SKILL.md`:

```markdown
For a reading, key, meaning map, conjecture, restoration model or segmentation, read [bench/README.md](../../../bench/README.md) and the relevant task guide before choosing a test.
```

Append to `.claude/skills/start-study/SKILL.md`:

```markdown
Select the relevant [bench task](../../../bench/README.md) in the protocol, exercise its synthetic mode, and declare the comparison and pass rule before outcomes. Record the resulting versioned JSON and hashes in the owned package. Acquire or restore required local inputs through `knowledge/DATA.md` and `tools/fetch_data.py`.
```

Append to `.claude/skills/test-conjecture/SKILL.md`:

```markdown
Use `python -m bench shots` to register the whole round and freeze every participant before confirmation opens. Check the spending ledger and record prior exposure. Meaning maps measure discovery reliability, re-split variance, plausible-effect power and a rank or component-influence criterion before freezing; site construction strips identity and order proxies. Attach the relevant bench result and one joint credence rule for predictions sharing objects.
```

Append to `.claude/skills/verify-study/SKILL.md`:

```markdown
Recompute the relevant bench output from its recorded input, code hashes and seed, preserving the submitted endpoint. Check population identity and source access as well as scores; catalogue line divisions provide positive boundary labels, while readable-script word references provide complete labels. Changes to `bench/` also run `python -m bench selftest` and reproduce a source number for every affected scorer.
```

## knowledge/DATA.md

Add to the “Project registers, frames and releases” table:

```markdown
| [Shared evaluation harness](../bench/README.md) (13 October 2026) | Five task commands, synthetic selftest and 50 matched local numerical comparisons | Tracked code, protocols, generated controls and aggregates; acquired corpora and detailed derivatives remain local. Adds scoring, split-use, reliability and power records; no new objects or metadata coverage. |
```

Add immediately after that table:

```markdown
The [bench package](../experiments/2026-10-13-bench/REPORT.md) records task inputs and their hashes. A new October 13 partition contains 2,341 discovery and 2,354 confirmation families in 4,104 components, and inherits the earlier seal-size, site and motif exposures. The corrected local line-break list has 69 faces and 73 required divisions; the earlier 72-face, 76-division review endpoint remains separate. The harness adds no source acquisition or object-level metadata assertions.
```

## data/MANIFEST.json and registry

Add `manifest-entry.json` to the manifest's `sources` list as a project output after review. Recompute manifest counts and the updated date against the coordinator's current tree; other data agents may have added entries. No corpus source, object field or coverage denominator changes through this entry.

Review `registry-entry.json` and add it under `knowledge/registry/attempts/BENCH-HARNESS-2026-10-13.json`. It contains the exact eleven requested registry fields. Add the authors record `{"model": "GPT-6.1-Sol", "harness": "Codex API"}` if the coordinator's registry schema includes contributor metadata. Run `python tools/kb.py build` and `python tools/kb.py check` after integrating the shared edits.

The coordinator should independently run the final selftest and `reproduce.py` in new directories, inspect source hashes and read logs, review the real-population freshness rule, and verify that only generated controls and aggregate results enter Git. Neither code nor outputs add a CI workflow or publication step.
