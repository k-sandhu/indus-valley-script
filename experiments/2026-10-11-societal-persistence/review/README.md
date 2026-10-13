# Independent review package

Start with [REVIEW.md](REVIEW.md). The package contains an independent reconstruction of the coordinator's frozen finite model, six explicitly invented counterexamples, selected primary precedents and [prospective archaeological tests](FALSIFIERS.md).

The [model checker](check_model.py) compares all declared state sets and policies without importing coordinator functions. Its [recorded output](model-checks-v1/checks.json) passes 5,218 checks. The [counterexample output](counterexamples-v1/counterexamples.json) passes six assertions. Alternative event laws are preserved inside the model-check output and identified separately from the exact reconstruction.

A later [shared-operation variant](CO-PRODUCTION-RESULTS.md) tests repair and teaching as outputs of one operation. It passes 1,133 checks across 16 aging-skill worlds and is explicitly post-baseline. Its result changes the original cost bottleneck under the new invented law.

To reproduce a computation, choose a new output directory. Both CLIs refuse existing output paths:

```powershell
C:/Python313/python.exe experiments/2026-10-11-societal-persistence/review/counterexamples.py --output experiments/2026-10-11-societal-persistence/review/counterexamples-v2
C:/Python313/python.exe experiments/2026-10-11-societal-persistence/review/check_model.py --output experiments/2026-10-11-societal-persistence/review/model-checks-v2
C:/Python313/python.exe experiments/2026-10-11-societal-persistence/review/source_audit_v3.py --output experiments/2026-10-11-societal-persistence/review/source-checks-v4
C:/Python313/python.exe experiments/2026-10-11-societal-persistence/review/co_production.py --output experiments/2026-10-11-societal-persistence/review/co-production-v2
```

The checker pins the coordinator's `run-v1` and validates that endpoint's code/protocol hashes. Its standard-library calculations require no third-party scientific package. The source audit additionally needs `pypdf` and `beautifulsoup4` and local witnesses. Its [90 passing checks](source-checks-v3/checks.json) follow two preserved locator failures caused by PDF interglyph spacing; earlier scripts and [failure records](source-checks-v2/failure.json) remain available. [sources.json](sources.json) records URLs, hashes, inspected scope and rights status. The own prose, code, protocols and aggregate enumerations can be reviewed from the repository; acquired publications and complete extractions remain in excluded `data/raw/` paths. The two inherited archaeological witnesses belong to the literature contributor's raw directory.

[RETROSPECTIVE.md](RETROSPECTIVE.md) records corrections and access limitations. [verification.json](verification.json) pins package outcomes and editorial checks; [changed-paths.json](changed-paths.json) lists this branch's files. This package has no calibrated archaeological model or empirical estimate of collapse risk.
