# Indus script research investigation

This workspace investigates structural constraints and restoration limits. It contains **no established decipherment, language identification, sound value or authenticated translation**.

Research began **2026-10-01 23:07:54 UTC**. The minimum four-hour period ends **2026-10-02 03:07:54 UTC**. The final report builder checks that timestamp and completion of the strongest 1,000-shuffle reference. The final18-page report was generated after4.01 elapsed hours and has passed quantitative and visual review.

## Findings and their scope

| Result | Evidence | Interpretation |
|---|---|---|
| Sign order predicts held-out graphics | +0.890 bits per noninitial sign; conditional grouped 95% interval 0.817â€“0.965; full-procedure metadata null, 0/1,000 exceedances, Monte Carlo p=1/1,001 | Sequencing constraint under the specified transcription model; not a test that identifies language |
| The unique-text reference also remains positive | +0.848 bits; 1,000 duplicate-rejecting draws from 6,569 proposals, 0 exceedances, p=1/1,001 | Preserves physical aliases and the unique-string sampling rule; same underlying corpus |
| Separate manual annotation preserves order gain | 74 Mayig seal faces; +0.725 bits per candidate event, interval 0.551â€“0.899; 1,426 source/compatible-text-excluded training strings | Different annotation of shared photographs/catalogues, with explicit candidate coverage limits |
| A verified one-sign slot can be ranked | Exact top-one 33.8% versus 17.0% baseline; top-five 55.3% versus 35.5%, across 8,009 masked slots | Common graphic suggestions; rare-sign accuracy and calibration are poor |
| Unknown gap length remains unreliable | Design-matched count accuracy 46.3% versus 51.1% always-one control | Failed extension; actual eroded sections cannot be replaced with one presumed slot |
| Vessel capacity alone cannot assign ten to a long stroke | The same capacity fit supports 40.4Ã—n, 4.04Ã—10Ã—n, or (40.4/12)Ã—12Ã—n | Independent unit/count evidence is required; no new numeral value established |
| A numerical proposal has a finite conditional solution set | The two proposed equalities imply exactly (L,S,v)=(4,20,36),(6,8,10),(10,8,6),(36,20,4); the cited range leaves (10,8,6) | Exact mathematical constraint, conditional on unverified semantic/equality premises |
| Frozen image acquisition fails; geometry repair helps | 20 withheld-reference rows: 14 matching counts, 2 first-candidate whole rows; subsequent clean crops: 18 matching counts, 6 first-candidate rows | Original scores preserved; repair is post-reference development and needs fresh validation |

Confidence intervals condition on fitted models and do not encompass every transcription, selection or archaeological uncertainty. Previous-sign dependence also occurs in the constructed nonphonetic control. These findings provide research tools and constraints, without solving the script.

## Inspect the evidence

- Final or draft PDF: `output/pdf/indus_script_research_report.pdf`; edition and exact elapsed time: `output/report_build.json`.
- Structural methods, competing baselines, nulls and defects: [research/methods/FINDINGS.md](research/methods/FINDINGS.md), [RESULT_INDEX.json](research/methods/RESULT_INDEX.json).
- Corpus/source identity: [research/corpus/CORPUS_REPORT.md](research/corpus/CORPUS_REPORT.md).
- Published prior and source locations: [research/literature/evidence_and_novelty_matrix.md](research/literature/evidence_and_novelty_matrix.md).
- Numerical assumptions: [research/literature/metrology/README.md](research/literature/metrology/README.md), [research/methods/NUMERICAL_CONSTRAINT_AUDIT.md](research/methods/NUMERICAL_CONSTRAINT_AUDIT.md).
- Source plans and research log: `research/*PLAN.md`, [research/WORK_LOG.md](research/WORK_LOG.md).
- Manual 1979 chart numeric reference and acquisition pilot: `research/chart_reference/`, `research/visual_digitization/`. Neither is an accepted full inscription corpus.
- Searchable 687-cell source-image atlas: [output/chart_atlas/index.html](output/chart_atlas/index.html). Open locally; search by code/rank and filter retained numeric ambiguities.
- Frozen fresh20 image evaluation: [evaluation_frozen_endpoint.json](research/visual_digitization/font_fresh20/evaluation_frozen_endpoint.json), independently checked in `research/methods/results/font_fresh20_audit/`.
- Post-reference geometry diagnostic: `research/methods/results/font_geometry_sensitivity/`; same frozen chart/matcher, repaired source-only vertical crops. Kept separate from blind validation.
- Final file/source hashes and Python environment: `output/evidence_manifest.json`, `output/environment.json`.
- Concise machine-readable overview: `output/research_summary.json`; prioritized next tests: [research/NEXT_TESTS.md](research/NEXT_TESTS.md).

## Reproduce

Run from this directory. Python 3.13 with NumPy, SciPy, pandas, scikit-learn, Pillow, PyMuPDF, OpenCV and reportlab is available on the research host. Plotting uses a local `.vendor` installation of matplotlib. Versions are recorded in the environment manifest.

```powershell
python src/verify_root.py
python src/methods/verify_methods.py
python src/restoration.py benchmark
python src/restoration.py crosssite --out results/restoration_crosssite
python src/independent_annotator.py
python src/independent_quality_sensitivity.py
python src/gap_restoration.py benchmark
python src/methods/gap_design_matched.py --prior results/gap_restoration --output research/methods/results/reproduction_gap_design_matched
python src/identifiability_demo.py
python src/methods/audit_numerical_equalities.py
python src/evaluate_font_fresh20.py
```

Use fresh output directories for long comparative reruns. Exact seeds, hashes, group definitions and stronger null commands are in [research/methods/REPRODUCING.md](research/methods/REPRODUCING.md). Root plans distinguish before-outcome designs from post-audit exploratory sensitivities. Existing superseded outputs are retained and labelled; their best numbers are not combined.

For an exploratory graphic query:

```powershell
python src/restoration.py predict --sequence "817,002,?,740" --site "Mohenjo-daro" --type "SEAL:S" --alpha 20
```

Provide `--exclude-artifact` with the actual observational object-family ID for a source case. Matching training texts can exist on other objects; the interface warns about overlap. A question mark specifies exactly one glyph. The tool rejects `000` and `999` as proof of a one-sign slot.

## Source acquisition and reuse

Pinned observational repositories:

- [Mayig](https://github.com/mayig/indus-valley-script-corpus/tree/ad2f1e218a34b8c33c57de0d6cb8d99272765bbb), Michael Carlson 2024, MIT: manual CISI annotation and local P-class crosswalk.
- [Lipi](https://github.com/yajnadevam/lipi/tree/fc8813a52e183d19c441631dc26c33a4dccbea39): no repository license found. Bulk files stay local; acquisition does not license redistribution. Sanskrit/translation/interpretation fields are excluded.
- [1979 institutional corpus](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/), Koskenniemi and Parpola: official CC BY 4.0, attributed source for chart images and the small original-font pilot.

Normalization entry points are `research/corpus/normalize_lipi.py`, `normalize_mayig.py`, `build_sign_crosswalk.py` and `normalize_indus_website.py`. Historical stable codes, Wells IDs, Mahadevan IDs and local Mayig P IDs are distinct inventories. Numeric coincidence does not establish object or sign identity.

No public distribution or publication of the bulk derivative corpus is included in this investigation. A code/result package can be reviewed locally; further work should use the pinned acquisitions and recorded source rights.
