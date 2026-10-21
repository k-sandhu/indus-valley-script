# Commands for the comparison-corpus tools

Run these commands from the repository root with Python 3.13. The tools use the standard library and explicitly locate sibling modules under `python -I`. Every output named below must be new. Normalisation and validation compute no statistics.

First prepare a local JSON object mapping each printed source identifier to its reviewed rights status. Supply the status recorded during acquisition. Where an edition's collection statement supplies a missing language or script stage, prepare a local source-rules JSON object as described in [the run notes](codex/c-statistics/NOTES-CODEX.md). The four supported printed sources are `asi-ar-1903-04`, `asi-ar-1913-14`, `asi-ar-1911-12` and `mahadevan-2003`.

```text
python -I experiments/2026-10-21-head-direction-corpora/normalize_brahmi.py --transcriptions <reviewed-source-1.jsonl> <reviewed-source-2.jsonl> --rights <rights.json> --lexicon experiments/2026-10-21-head-direction-corpora/lexicon-brahmi.tsv --source-rules <reviewed-source-rules.json> --out <local-new-brahmi-records.jsonl> --review <local-new-member-review.tsv>
python -I experiments/2026-10-21-head-direction-corpora/validate_records.py --records <local-new-brahmi-records.jsonl> <local-cuneiform-records.jsonl> --out <local-new-validation.json>
```

The normaliser writes one SCHEMA.md record per transcription entry and a TSV with each member, tag, tag source, language and occurrence count. It preserves the extra source fields, the printed legend and the source locators in those local records. It refuses unresolved language, script or identity fields. The optional `--source-rules` argument can be omitted when every entry supplies the necessary metadata. The validator writes total and invalid record counts and a count for each failed check. It returns exit code 1 for invalid records and 2 for an input or output error. Review the member table and transcriptions against the edition before any real analysis.

Run the synthetic selftest in a new work directory. Its default regression and reference inputs are the two files specified by run C; `--regression` and `--reference` can set their paths explicitly. The work directory holds generated fixtures, member review, deliberate validator failures and two complete synthetic summaries. The report holds each check's result, the exchangeability rate, the regression values and code hashes.

```text
python -I experiments/2026-10-21-head-direction-corpora/selftest.py --work data/raw/2026-10-21-head-direction-corpora/codex-c/selftest-4 --out experiments/2026-10-21-head-direction-corpora/selftest.json
```

The selftest invokes the following synthetic command twice with distinct output directories and checks byte-identical summaries. The default selftest uses 24 matched replicates, 200 permutations for each S3 reference and 1,000 permutations for each S1 reference. Its 300-draw exchangeability test uses eight matched replicates per draw. The production default remains 2,000 replicates.

```text
python -I experiments/2026-10-21-head-direction-corpora/discriminate.py --records data/raw/2026-10-21-head-direction-corpora/codex-c/selftest-4/five-corpora.jsonl --out data/raw/2026-10-21-head-direction-corpora/codex-c/synthetic-example --replicates 24 --synthetic
```

After the reviewed inputs and any amendments are frozen, the project runs the real comparison once:

```text
python -I experiments/2026-10-21-head-direction-corpora/discriminate.py --records <local-brahmi-records.jsonl> <local-cuneiform-records.jsonl> --out experiments/2026-10-21-head-direction-corpora/run-2026-10-21 --replicates 2000
```

`discriminate.py` writes only `summary.json` in the new output directory. It includes all nine statistics, eligibility counts, primary corpus summaries, keep conditions, directions and gaps, the exchangeability probability, the secondary Sumerian comparison, sub-corpora, both sensitivity panels, metadata coverage and full-set S1 shuffle references. Hashes identify the four governing documents, every package code file used or delivered by run C, the acquisition helper, lexicon, run C brief, common rules and every input record file. `--documents` can name another directory containing the four governing documents. The summary contains aggregates and no legends. Run C has run this command only with `--synthetic`.

The tracked deliverables are the six Python modules, the general-vocabulary lexicon, this guide, `selftest.json` and the run C plan, notes and retrospective. Synthetic fixtures, member tables, normalized records, validation details, scratch status snapshots and synthetic summaries stay under the ignored `data/raw/2026-10-21-head-direction-corpora/codex-c/` directory. Printed-source transcriptions, source images and all normalized comparison records remain local. A production aggregate summary can be tracked after review.
