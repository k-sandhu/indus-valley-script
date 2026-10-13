# Multiface administrative records

The [report](REPORT.md) develops Mukhopadhyay's semantic-scope recommendation into a whole-carrier module test. Copied bundles and the placement of W700-bearing faces account for the strongest associations. The proposed [carrier life cycle](HYPOTHESES.md) connects standing entitlements and canonical transaction tokens, with issuer, identity, sealed-package and commodity alternatives expressed as independent physical predictions. The [record schema](administrative-grammar.json) keeps observed graphic fields separate from their candidate functions.

## Preserved endpoints

The [protocol](PROTOCOL.md) preceded the original outcomes. [run-v1](run-v1/summary.json) contains four completed populations and ten family-adjusted tests, using 1,999 pilot and 9,999 tail allocations per population. The [dated amendment](AMENDMENT-2026-10-11-role-control.md) explicitly marks the W700-role refinement as post-outcome. [role-control-v1](role-control-v1/summary.json) uses 1,999 pilot and 4,999 tail allocations per population. Code and protocol snapshots remain in each endpoint.

[verify.py](verify.py) checks all 75,984 saved allocations with an independent counting implementation. Its [85 checks](verification.json) pass; the separate reviewer's [104 declared-law checks](../review/allocation-checks-v1.json) also pass. The [prototype counterexample](../review/prototype-counterexample.json) establishes why the selected-module-bag reference must be described as its own conditional law.

## Reproduction

Run from the repository root with Python 3.13, NumPy and SciPy available. The preserved seeds are 2026101117 for the original endpoint and 2026102117 for the role control. The code derives population-specific seeds from those values. A fresh name is required for both the tracked output and the corresponding local witness directory.

```powershell
C:/Python313/python.exe experiments/2026-10-11-two-approaches/administrative/analyze.py --out reproduction-main-2026-10-11 --pilot 1999 --references 9999 --seed 2026101117 --cap 1000000
C:/Python313/python.exe experiments/2026-10-11-two-approaches/administrative/role_control.py --out reproduction-role-2026-10-11 --pilot 1999 --references 4999 --seed 2026102117 --cap 1000000
C:/Python313/python.exe experiments/2026-10-11-two-approaches/administrative/verify.py --output verification-recheck-2026-10-11.json
```

The verifier targets the preserved `run-v1` and `role-control-v1` witnesses. The first two commands demonstrate regeneration into new directories; compare their aggregate statistics and seeds with the preserved endpoints. Creation times and measured runtimes can differ. Any cap failure stays unfinished and receives no p-value. No frozen output is overwritten.

The input must be the local `data/normalized/lipi_observed_faces.jsonl`, SHA256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`. [sources.json](sources.json) pins its upstream export, normalization conventions, literature witnesses and prior physical-use audit. Full strings, per-object joins and saved allocation arrays are local-only under `data/raw/2026-10-11-two-approaches/administrative/`. The report and aggregates can be read without exposing them; exact regeneration and allocation verification require them.

The [retrospective](RETROSPECTIVE.md) records the method change, dependence, review correction and unresolved observations. [registry-entry.json](registry-entry.json) is prepared for integration into the project registry by its maintainer. [changed-paths.json](changed-paths.json) records this package's files and dispositions.
