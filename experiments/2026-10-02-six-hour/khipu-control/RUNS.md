# Running the controls

Run from the project directory. The source assets are local-only, so a fresh checkout needs acquisition before the source calculation. Endpoint commands refuse existing output files. Use a fresh dated branch directory to make a new run; preserve these frozen outputs.

The scripts use Python's standard library, Beautiful Soup for the initial source extraction, and SciPy for the independent 512-state feasibility check. The recorded run used Python 3.13 and SciPy 1.17.1. No training model, GPU or network service is needed after acquisition.

```powershell
python src/six_hour/khipu_acquire.py
python src/six_hour/khipu_source.py audit
python src/six_hour/khipu_source.py prepare
python src/six_hour/khipu_control.py source
python src/six_hour/khipu_evaluate.py source
python src/six_hour/khipu_verify.py source
python src/six_hour/khipu_control.py synthetic
python src/six_hour/khipu_evaluate.py synthetic
python src/six_hour/khipu_verify.py synthetic
python src/six_hour/khipu_verify.py freeze
```

The supplemental technical pages and release witnesses were acquired through a separate HTTP batch. Their exact URLs and hashes are in [acquisition-supplement-01.json](acquisition-supplement-01.json); retrieve those assets to their listed local paths before the freeze command. The source predictor writes detailed permutations under `data/six-hour/khipu/`. The synthetic generator writes its generated features, separate evaluator key and all exact inference states under `endpoints/main-v1/`.

To check a frozen manifest, calculate SHA256 for each listed file and compare its bytes and hash with the manifest. Protocol snapshot links retain their original directory context, as stated in the manifests. [Source verification](source-verification.json) and [simulation verification](endpoints/main-v1/verification.json) record the completed arithmetic checks.
