# Shot B: a working reading of the inscriptions

This package built a gloss map and grammar for the Indus inscriptions on the discovery half of the conjecture-shot split, froze predictions about variables the map was not built from, and tested them once on the confirmation half. The brief is [SHOT.md](SHOT.md) and the method is the two-stage design in [../DESIGN.md](../DESIGN.md).

The map assigns 118 signs to seven classes (numerals, links, great households, personal-name elements, commodities and units, offices, closing determinatives) with English glosses ([GLOSS-MAP.json](GLOSS-MAP.json), [READING.md](READING.md)). Its frozen primary score, the standardised site-concentration contrast plus the standardised size contrast, came out at S = −0.567, the 33.0th percentile of 10,000 rearrangements of its own labels (pass required the 95th), 0.44 standard deviations below their mean, with z₁ = −1.20 and z₂ = +0.63. The kill condition was met and the conjecture [C-0002](../../../knowledge/conjectures/C-0002-working-reading.md) is recorded dead. An independent recomputation confirms the fail decision ([verification.json](verification.json)).

## Files

| File | Content |
|---|---|
| [REPORT.md](REPORT.md) | the result, every prediction and check, and what it means for the reading |
| [EXPLORATION.md](EXPLORATION.md) | construction record on the discovery half, with every output path |
| [READING.md](READING.md), [GLOSS-MAP.json](GLOSS-MAP.json) | the reading, the grammar and the sign-by-sign map |
| [PREDICTIONS.md](PREDICTIONS.md), [PREDICTIONS.sha256](PREDICTIONS.sha256) | frozen predictions; hashes of the predictions, the map and confirm.py |
| [confirm.py](confirm.py) | the frozen scoring script |
| [confirmation/results.json](confirmation/results.json) | the frozen outcome; [run-stdout.json](confirmation/run-stdout.json) is its console summary |
| [confirmation-access.jsonl](confirmation-access.jsonl) | log of the two reads of the confirmation half (confirm.py, then verify.py) |
| [verify.py](verify.py), [verification.json](verification.json) | independent recomputation of S, z₁, z₂ and the pass decision |
| [AMENDMENT-2026-10-12-exploratory.md](AMENDMENT-2026-10-12-exploratory.md) | post-outcome exploratory summaries |
| [registry-entry.json](registry-entry.json) | proposed registry entry for the coordinator |
| `discovery/` | aggregate discovery outputs and synthetic dry runs |

Glossed readings of every discovery text, segment tables and glyph sheets are local under `data/raw/2026-10-12-conjecture-shots/shot-b-reading/`.

## Rerunning

From this directory, with Python 3.13, NumPy, SciPy and scikit-learn and the local corpus and split:

```text
python explore_01_profile.py        # sign profile
python explore_02_segments.py       # recurring texts and segments
python explore_03_frames.py         # substitution frames
python render_frequent_signs.py     # local glyph sheets
python build_gloss_map.py           # GLOSS-MAP.json (must reproduce the frozen hash)
python gloss_texts.py               # glossed readings and grammar statistics
python explore_04_counts.py         # counts cited in READING.md
python confirm.py --synthetic [--plant]   # dry runs on random withheld fields
python check_synthetic_seeds.py     # calibration over eight synthetic seeds
python confirm.py                   # confirmation run (each run is logged)
python verify.py                    # independent recomputation
python explore_post_outcome.py      # exploratory summaries of the frozen output
```

`confirm.py` refuses to read the confirmation half unless PREDICTIONS.md matches the hash in PREDICTIONS.sha256.
