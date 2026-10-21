# Reproduction commands

Run from the repository root with Python 3.13. Source PDFs, normalized rows and the CISI image index are local-only inputs. Their hashes are in the acquisition record, register coverage and earlier source packages. Preserve every existing output. These commands describe the original sequence; a full replay needs a disposable copy with empty output paths and its own copied spending ledger.

Before creating the round, copy `bench/spent.json` to `data/raw/2026-10-20-h912-tablet-series/spent-initial.json` and `spent-private.json`, retaining the original hash. The study uses only the private copy. A new seed does not change the declared historical exposure.

```powershell
python -X utf8 -m bench shots --synthetic --directory experiments/2026-10-20-h912-tablet-series/synthetic-fixtures --out experiments/2026-10-20-h912-tablet-series/shots-synthetic-v1.json
python -X utf8 -m bench shots --action create --input data/normalized/lipi_observed_faces.jsonl --seed 2026-10-20-h912-tablet-series --ledger data/raw/2026-10-20-h912-tablet-series/spent-private.json --split experiments/2026-10-20-h912-tablet-series/round.json --out experiments/2026-10-20-h912-tablet-series/split-summary-v1.json
python -X utf8 experiments/2026-10-20-h912-tablet-series/analyze.py discovery --run discovery-v1
python -X utf8 experiments/2026-10-20-h912-tablet-series/acquire.py
python -X utf8 experiments/2026-10-20-h912-tablet-series/score.py fit
```

Discovery was read through the shared loader before participant registration, which that loader permits. PREDICTIONS.json, the final comparison code and FREEZE-NOTES.md were then completed. The preserved discovery diagnostic used the earlier alpha 0.05; its p = 0.5 and minimum-size failure are unchanged by the final alpha 0.025. The model probabilities did not change. Register and freeze the one participant before reading confirmation:

```powershell
python -X utf8 -m bench shots --action register --split experiments/2026-10-20-h912-tablet-series/round.json --ledger data/raw/2026-10-20-h912-tablet-series/spent-private.json --shot h912 --predictions experiments/2026-10-20-h912-tablet-series/PREDICTIONS.json --out experiments/2026-10-20-h912-tablet-series/bench-register-v1.json
python -X utf8 -m bench shots --action freeze --split experiments/2026-10-20-h912-tablet-series/round.json --ledger data/raw/2026-10-20-h912-tablet-series/spent-private.json --shot h912 --artifact experiments/2026-10-20-h912-tablet-series/analyze.py --artifact experiments/2026-10-20-h912-tablet-series/score.py --artifact experiments/2026-10-20-h912-tablet-series/PROTOCOL.md --artifact experiments/2026-10-20-h912-tablet-series/FREEZE-NOTES.md --artifact experiments/2026-10-20-h912-tablet-series/discovery-v1/model.json --artifact experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv --out experiments/2026-10-20-h912-tablet-series/bench-freeze-v1.json
python -X utf8 experiments/2026-10-20-h912-tablet-series/analyze.py confirmation --run confirmation-v1
python -X utf8 experiments/2026-10-20-h912-tablet-series/score.py confirm
python -X utf8 -m bench shots --action inspect --split experiments/2026-10-20-h912-tablet-series/round.json --ledger data/raw/2026-10-20-h912-tablet-series/spent-private.json --out experiments/2026-10-20-h912-tablet-series/bench-inspect-v1.json
```

The source register and inspections follow the scored outcome and have their own scope:

```powershell
python -X utf8 experiments/2026-10-20-h912-tablet-series/register.py
python -X utf8 experiments/2026-10-20-h912-tablet-series/inspect_sources.py
python -X utf8 experiments/2026-10-20-h912-tablet-series/verify.py
python -X utf8 experiments/2026-10-20-h912-tablet-series/descriptor_search.py
python -X utf8 experiments/2026-10-20-h912-tablet-series/screen_fish_frame.py
python -X utf8 tools/kb.py check
python -X utf8 tools/review_prose.py --path experiments/2026-10-20-h912-tablet-series --path knowledge/conjectures/C-0012-fish-category-four-unit-records.md --no-write
python -X utf8 tools/verify_knowledge_repo.py --output experiments/2026-10-20-h912-tablet-series/repo-verification-v1.json
```

The book and proof pages in `source-pages-v1/` were rendered with PyMuPDF from the cited one-based pages. Visual decisions are recorded in SOURCE-OBSERVATIONS.md and require source inspection, rather than a numerical rerun. The separate excavation package records its own acquisition and page-rendering commands. Fixed-path helpers refuse existing outputs; a verification replay needs a copied helper with a new destination and its own recorded hash.

The final two source-worklist helpers were added after scoring. They consume the saved face rows and the archaeological continuation's versioned source observations. Their empty descriptor match and fourteen-object eligibility screen are descriptive and supply no new confirmation. The latter helper requires the separate excavation observation file identified by its saved hash.
