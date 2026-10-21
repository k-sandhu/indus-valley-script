# Checks

The source, accounting and replay checks passed 50 of 50 in [verification-v1.json](verification-v1.json). The author checker is separate from the builder; it is not an independent contributor review. Rebuilding into `replay-v1` reproduced the four tracked analytical files byte for byte.

The [scoped check](scoped-checks-v1.json) passed 19 Python syntax and JSON checks and found no broken link among the 16 local Markdown links then present. Raw photographs and detailed corpus joins were confirmed ignored by Git. The [source manifest](source-coverage-manifest.json) records the source and render hashes and the exact coverage changes.

`python tools/kb.py check` passed with 472 items, zero errors, zero warnings and two maintainer notes for the generated registry and map. Those shared generated files were not changed.

`python tools/verify_knowledge_repo.py --output experiments/2026-10-20-archaeological-setting/repository-integrity-v1.json` returned failure with 72 link errors outside this package. They include older DATA-UPDATE links and links to files still being written by concurrent fish and stratigraphy work. No error names an owned file. The [full result](repository-integrity-v1.json) preserves the workspace state at that check; it is not a finding about the completed state of other contributors' packages.

The final prose scan flagged four lines in the frozen protocol for slash compounds, including literal repository paths and shorthand for units and items. We retained its frozen wording. The report, retrospective, authorship correction and integration proposal had no remaining flags. The original protocol's unsupported model precision is corrected in [AUTHORSHIP.md](AUTHORSHIP.md).

Commands used for the analytical endpoint:

```text
python experiments/2026-10-20-archaeological-setting/acquire.py
pdftoppm -f 23 -singlefile -scale-to 2200 -png research/literature/sources/kenoyer_1997_excavations_pots.pdf data/raw/2026-10-20-archaeological-setting/mk1997-p23
pdftoppm -f 7 -singlefile -scale-to 2200 -png research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf data/raw/2026-10-20-archaeological-setting/km2010-p07
python -m bench shots --synthetic --directory data/raw/2026-10-20-archaeological-setting/shots-fixtures --out experiments/2026-10-20-archaeological-setting/shots-synthetic-v1.json
python experiments/2026-10-20-archaeological-setting/build.py --out experiments/2026-10-20-archaeological-setting/run-v1 --local-out data/raw/2026-10-20-archaeological-setting/run-v1
python experiments/2026-10-20-archaeological-setting/build.py --out experiments/2026-10-20-archaeological-setting/replay-v1 --local-out data/raw/2026-10-20-archaeological-setting/replay-v1
python experiments/2026-10-20-archaeological-setting/verify.py --out experiments/2026-10-20-archaeological-setting/verification-v1.json
python tools/review_prose.py --path experiments/2026-10-20-archaeological-setting --no-write
python tools/kb.py check
```
