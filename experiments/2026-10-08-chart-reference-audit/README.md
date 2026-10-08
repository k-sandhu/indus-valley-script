# 1979 chart-reference audit

Current reference: [chart-reference-v2.1.json](chart-reference-v2.1.json), dated 8 October 2026. Status: Exploratory, two AI readings, no expert review. It contains 687 cells, eight primary-code corrections and two class corrections relative to the original reference. Twenty-two rows change values or alternatives; confidence updates bring the total to 36 changed numeric records. All 16 old lower-code ambiguities are provisionally settled. The lower-code list contains 687 distinct codes. The class numbers cover 1 through 401 in nondecreasing order. Counts are in [comparison-v2.1.json](comparison-v2.1.json), `summary`.

The [review](REVIEW.md) prompted the added class correction at `p20_c3_r33`, 85 to 86, confirmed by our own native-pixel inspection. V2.1 records 33 cells at medium confidence and 654 at high qualitative confidence. Thirty-two confidence labels were lowered from v2; the existing medium 333 remains medium. The current consumer guidance is [RECOMMENDED-USE.md](RECOMMENDED-USE.md).

The first pass differed from the original in 21 codes; 15 of those differences were reader errors corrected on reinspection. In the original audit, 630 cells were read once by one model and checked only by the class and code sequence. Two final corrections, `p20_c4_r1` and `p21_c6_r31`, followed hints from the v3 adjudicator. The reviewer's 63-cell blind reading, after its native-pixel checks, agrees with every sampled class and code. Its whole-chart pixel sweep finds no code disagreement and supports the added class correction. The 939-digit nearest-neighbor check flagged the same class digit; this is a consistency check, not an independent label source. [REPORT.md](REPORT.md) explains the sample, shared errors and scan resolution.

Code 360 at `p20_c4_r13` remains medium confidence. The v3 adjudicator and reviewer's first eye pass read 350; both our inspection and the reviewer's final native-pixel analysis support the rounded 6 outline. The separate `p21_c1_r19` prints 350 with a flat-topped middle digit. The worn code 734 at `p21_c7_r21` and faint class 300 at `p21_c4_r21` also remain provisional at medium confidence.

[impact-v2.1.json](impact-v2.1.json) lists exact consumer paths and fields. Code-set changes still affect 11 v1 reference units and eight v3 units. V2 has no directly joined code-set change, with 18 units requiring candidate-identity review; v3 has 31. The current join identifies 36 template records and 36 release chart rows. Stored prediction payloads change at 72 v1 and 100 v2 alternatives, including rank metadata. Code-set changes alone remain 60 and 83 alternatives. No replacement scores were computed, and no consumer was edited.

## Reproduce the review amendment

Run from the repository root with the existing local inputs. The scripts write only this package and its local raw directory. Reviewer files and the original v2 outputs are pinned in [preserved-inputs-v2.1.json](preserved-inputs-v2.1.json). The amendment input is [amendment-decisions-v2.1.json](amendment-decisions-v2.1.json).

```powershell
$auditPython = 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe'
$auditPackage = 'experiments/2026-10-08-chart-reference-audit'
& $auditPython -B "$auditPackage/amend-reference.py" render
& $auditPython -B "$auditPackage/amend-reference.py" apply
& $auditPython -B "$auditPackage/impact.py" --reference "$auditPackage/chart-reference-v2.1.json" --comparison "$auditPackage/comparison-v2.1.json" --out "$auditPackage/impact-v2.1.json" --integrity-out "$auditPackage/consumer-input-integrity-v2.1.json" --raw-subdir revision-2026-10-08-v2.1
python -B tools/review_prose.py --path $auditPackage --no-write | Tee-Object -FilePath data/raw/2026-10-08-chart-reference-audit/revision-2026-10-08-v2.1/prose-scan.txt
& $auditPython -B "$auditPackage/verify.py" --version 2.1
```

The rendering command is optional when the eight native crops already exist. Replaying the amendment uses saved digit decisions; it does not supply a fresh human reading. New outputs are [cell-observations-v2.1.json](cell-observations-v2.1.json), [comparison-v2.1.json](comparison-v2.1.json), [impact-v2.1.json](impact-v2.1.json), [consumer-input-integrity-v2.1.json](consumer-input-integrity-v2.1.json), [verification-v2.1.json](verification-v2.1.json) and [file-inventory-v2.1.json](file-inventory-v2.1.json). [sources-v2.1.json](sources-v2.1.json) records reused review witnesses. Original v2 files remain as historical outputs. Avoid the legacy default `audit.py compare`, `impact.py` and `verify.py` commands when replaying this amendment; the explicit arguments above select the new outputs.

New local crops, their manifest, extracted release rows and the prose scan are under [revision-2026-10-08-v2.1](../../data/raw/2026-10-08-chart-reference-audit/revision-2026-10-08-v2.1/). Existing page/cell renders and preliminary-output history remain local. The current inventory enumerates all paths, distinguishing reviewer-owned witnesses.

The reviewer should rerun the amendment, impact and versioned verifier; check the preserved hashes; inspect class 86 and the medium-confidence decisions; and resolve the v3 sample 58/unit 0 location conflict and unlocated candidate identities before migration. [RETROSPECTIVE.md](RETROSPECTIVE.md) records the initial interruptions and subsequent review fixes. The registry proposal has not been inserted into the shared registry.
