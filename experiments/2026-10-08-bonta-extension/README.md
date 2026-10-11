# Exploratory Bonta extension

The [current report](run-2026-10-09-v5/REPORT.md) and [visual catalogue](run-2026-10-09-v5/catalogue.html) assign preferred working interpretations to 713 Wells codes, including 596 new assignments and 117 inherited Bonta proposals. Sixteen new Sanskrit anchor families cover seventeen codes. The [Sanskrit source table](SANSKRIT-ANCHORS.md) identifies the specific dictionary senses, including homonyms and later attestations.

Use [candidates.csv](run-2026-10-09-v5/candidates.csv) for a compact table or [candidates.json](run-2026-10-09-v5/candidates.json) for meanings, alternatives, graphic classes, source pointers, observation counts and both lexical-search scenarios. The [verification](run-2026-10-09-v5/verification.json) checks coverage, independently recomputed positions, unchanged input hashes, dictionary completions and worked-example records. It verifies the computation and source links; historical meanings remain exploratory.

The [protocol](PROTOCOL.json) describes the authorized construction exercise. The [October 9 amendment](AMENDMENT-2026-10-09.json) adds the saved second edition, new Sanskrit comparisons and internet source searches. [The retrospective](RETROSPECTIVE.md) records implementation decisions and limitations.

## Preserved runs

- `run-2026-10-08-v1`: original dossiers and dictionary search using the mapped Bonta proposals.
- `run-2026-10-09-v2`: new-anchor preferred/alternative searches and first full candidate catalogue.
- `run-2026-10-09-v3`: catalogue projection with worked examples selected for the named anchor relationships.
- `run-2026-10-09-v4`: drawing-review corrections for W383, W951 and W953; prior code versions are preserved in `history/`.
- `run-2026-10-09-v5`: current projection includes relational/juncture functions for W001, W002 and W060, with numerical readings retained. Both lexical search outputs are reused byte for byte from v2 in every later projection. These projections do not rerun or improve the lexical result.

## Reproduce locally

The source dependencies named in `PROTOCOL.json` must already be present. They are retained locally under `data/` and are not bundled in this research record. Python requires `numpy`, `Pillow`, `fonttools` and `brotli`. The run directories below must be new.

```powershell
python -X utf8 experiments/2026-10-08-bonta-extension/analyze.py --run run-NEW-baseline
python -X utf8 experiments/2026-10-08-bonta-extension/extend_search.py --run run-NEW-search
python -X utf8 experiments/2026-10-08-bonta-extension/render_glyphs.py
python -X utf8 experiments/2026-10-08-bonta-extension/build_catalogue.py --run run-NEW-catalogue --search-run run-NEW-search
```

The extension and catalogue code intentionally use the preserved October 8 dossiers and dictionary index. The new baseline command produces a separate endpoint for inspection; using a different baseline in the extension requires an explicit code/protocol amendment. Run `verify_catalogue.py --run run-2026-10-09-v5` for the current endpoint and its v2 search dependency. For a changed model, adapt that check and preserve the former verification.

Open the HTML locally, or serve the project root on `127.0.0.1`. A local server was used to inspect the catalogue at port 8769. The viewer’s source drawing links resolve into the locally retained `data/` directory. A copy of the authored HTML alone retains the meanings and counts but requires those drawings or the existing licensed chart cells to show pictures.

Raw inscription strings, complete lexical witnesses, dictionary excerpts, worked account strings and rendered font drawings remain under `data/raw/2026-10-08-bonta-extension/`. The catalogue records aggregate positions and selected neighbouring codes, not a redistributed full corpus. Reused Mayig descriptions carry [the MIT notice](LICENSE-MAYIG.md). Existing Helsinki chart cells retain their source attribution. The selected semantic hypotheses were written for this project.
