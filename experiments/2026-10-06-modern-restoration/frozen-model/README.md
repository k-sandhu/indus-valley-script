# Frozen carry-forward recipe

The record chooses `ensemble` with extra text `True` using pooled inner loss. Its full-data fit is recorded separately from the adaptive outer procedure’s evaluation score. Configuration, epochs, seeds and code/input/payload hashes are in [manifest.json](manifest.json). Imported repository helpers and the loader interface are pinned in [code-dependencies.json](code-dependencies.json). Corpus-derived counts, weights and training identities remain local-only. [Training register](training-register.json) supplies the future contamination screen.

`inference.py` loads the hashes and predicts every known slot without tuning. Its JSONL input has `seq` arrays of string graphic codes, preserving their leading zeros, and optional `object_type`, `site`, `region` and `symbol` fields. Output must be a fresh path inside the assigned local raw directory. A hidden target is overwritten by the model’s MASK or enumerated candidate; its placeholder does not affect that slot’s prediction.

```powershell
& C:/Users/sandh/.venvs/indus-ml/Scripts/python.exe -B experiments/2026-10-06-modern-restoration/inference.py --input data/raw/2026-10-06-modern-restoration/fresh-input.jsonl --output data/raw/2026-10-06-modern-restoration/fresh-predictions.jsonl
```

Future evaluation must obtain a fresh source-reviewed population, screen its object and string connections against the training register and broader source graph, freeze its query law before scoring, and keep this recipe unchanged. Naturally damaged gaps also need an independently supported missing-slot count.
