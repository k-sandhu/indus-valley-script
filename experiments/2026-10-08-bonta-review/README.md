# Package Q: PDF-review corrections

Jar/arrow final tendencies, fish clustering and M-unit order reproduce. The broad lexical panel remains construction-dependent; the frozen clear-origin panel cannot attain significance. Wider field boundaries, historical validation success and physical metrology remain unresolved. Results are Exploratory, based on two AI coding rounds without specialist review.

| Headline result | First | Second | Agreed-only |
|---|---:|---:|---:|
| Frozen final-only fields: clean/conflict/indeterminate | 942/349/1178 | 781/302/1386 | 844/379/1246 |
| Final-or-penultimate fields | 1144/136/1189 | 970/100/1399 | 1040/172/1257 |
| Widened clean shuffle mean | 622.54 | 563.38 | 583.56 |
| M units in O–F–MS order | 288/331 | 226/249 | 288/331 |
| M-order shuffle mean | 58.87% | 68.39% | 58.89% |
| Fish adjacency / shuffle mean | 142/55.72 | 142/55.72 | 135/54.73 |

All widened-clean, M-order and fish tails are **.0005**. The first frozen clean count has **683/942 texts without M**, including **323 C-plus-T only**; its excess largely restates terminal position. Jar and arrow final counts remain **838/1,196** and **192/225**, with **358** and **33** exceptions. [First fields](pdf-review-response-2026-10-09-v1/first/field-corrections.json), [second](pdf-review-response-2026-10-09-v1/second/field-corrections.json), [agreed-only](pdf-review-response-2026-10-09-v1/agreed_only/field-corrections.json); [terminal exceptions](response-2026-10-08-v2/terminal-exceptions.json).

Broad exact matching remains **84/228** full-selection and **83/206** explicit-caption, tails **.0005**. The scorer reads manuscript roles/value bundles; external mapping files are absent from the scoring path, so first/second equality is by construction. Agreed-only removes target coverage and gives **53/123** full and **52/108** caption types. The earlier ten-type panel has **8/10 PU/PATI contexts** used in dictionary-based derivation; all **13** permutations scoring at least nine keep PU, and **0/600** moving it reaches nine. [Frozen panels](pdf-2026-10-09-v1/lexical-caption-sensitivity.json); [census](review/role-pair-census.json).

The frozen clear-origin result **2/5, tail .20**, is the best attainable score after dropping maha from three mahā- types. Both hits use dictionary-derived pāla; one uses reading-supported ASHVA. The full-selection **2/7** and agreed-only **0/1** remain preserved. The partial split excluding **129 derivation labels** yields **5/8**, tail **.0256**, with all five hits requiring PU, PATI or maha. It removes named derivation examples, while their historical reservation and subsequent value fitting remain unresolved. The corrected anchor-only panel gives **0/7 exact** (null mean zero), **2/7 normalized**, tail **.7556**; the numeral-motivation sensitivity gives **4/13 exact**, tail **.4860**. The sources cannot supply a larger independently reserved test. [Lexical corrections](pdf-review-response-2026-10-09-v1/lexical-corrections.json); [source diagnostics](pdf-review-response-2026-10-09-v1/source-diagnostics.json).

Explicit alias matches remain **713/859 attempts and 338 object families**. Six readings on H-271, M-707, M-106 and M-122 have probable mistyped-CISI aliases; excluding them gives **707/859 and 334 families**. Four catalogue-code transcriptions and twelve empty captions are repaired: **718 → 726** attempts have transcriptions. The row-local uncertainty search adds **57 flags**, **103 → 160**, without defining a failed-reading rate. [Join evidence](pdf-review-response-2026-10-09-v1/join-corrections.json); [inventory corrections](pdf-review-response-2026-10-09-v1/reading-corrections.json).

The [derivation successor](pdf-review-response-2026-10-09-v1/value-derivations-v3.json) separates pala/pāla/bala, adds the fish, caru and 2014 predicate anchors, marks ASHVA/GO as reading-supported and fixes their locators. Mayig agreement remains **72 exact singleton, 78/96 overlapping, ten disjoint and eight first-reader missing**, κ **.9217 (n=78)**. Wells/Helsinki overlap is 78, κ **.9109 (n=46)** / **.7193 (n=8)**. The blind second packet is preserved. The first coder saw Table 18 families when coding the 17 caption forms. [Agreement](two-coder-2026-10-09-v1/AGREEMENT.md); [disagreements](two-coder-2026-10-09-v1/DISAGREEMENTS.md).

## Source and file scope

The 259-page manuscript witness, 58 Table 18 labels, 65 drawings, 96 coding targets and [blind packet](../../data/raw/2026-10-08-bonta-review/second-coder-v1/) stay preserved. The source inventory retains **1,200 rows and 859 attempt rows**. The ledger retains **1,021 records**, with versioned source and test corrections. PDF crops, complete captions, corrected inventory rows and per-query predictions remain local raw. [Witness](pdf-2026-10-09-v1/witness-v3.json); [corrected reading index](pdf-review-response-2026-10-09-v1/reading-index-v5.json); [ledger](claims.md).

[REVIEW-PDF.md](REVIEW-PDF.md) and [review-pdf/](review-pdf/) were reused unchanged. Current summaries and the previous ledger are preserved in [history/2026-10-09-before-pdf-review/](history/2026-10-09-before-pdf-review/). [PDF-REVIEW-FILES.json](PDF-REVIEW-FILES.json) lists this phase’s changes; [FILES.json](FILES.json) inventories current contents. Shared registry/index and other contributors’ directories were untouched. [Report](REPORT.md), [protocol](PROTOCOL.md), [retrospective](RETROSPECTIVE.md), [sources](sources.json), [registry proposal](registry-entry.json).

## Repeat from the repository root

System Python, PyMuPDF and Pillow are used. Choose a new output basename within both package trees; scripts refuse existing endpoints. The lexical audit reuses the reviewer’s independent matcher read-only and the pinned dictionary. Repeat the field command for `second` and `agreed_only`.

```powershell
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_review_sources.py --output-dir pdf-review-replay-2026-10-09-02 --render
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_review_lexical.py --output-dir pdf-review-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_review_fields.py --output-dir pdf-review-replay-2026-10-09-02 --mapping first
python -B -X utf8 experiments/2026-10-08-bonta-review/verify_pdf_review.py --replay pdf-review-replay-2026-10-09-02 --output pdf-review-checks-replay-2026-10-09-02.json
python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write
```

The completed replay passes **9,271/9,271 checks**, including **5,670 protected existing file hashes**. Preservation checks are recorded in [pdf-review-checks-2026-10-09-v2.json](pdf-review-checks-2026-10-09-v2.json). Earlier PDF and second-coder verifiers remain evidence for their frozen endpoints. Reviewer sampling should repeat the source-origin passages on manuscript pp. 45–47, 55, 67–68, 185–187 and 215–216; terminal rule p. 15; the twelve repaired captions; probable joins on pp. 126, 172, 210–211, 221 and 226; and the partial-split membership. The separate introductory letter’s p. 5 and the manuscript foreword’s p. 5 are distinct documents. Language Log’s chance remark belongs to Yves Rehbein’s **7 March 2025 reader comment**, quoting a YouTube commenter. Kalyanaraman’s substantive content remains unverified after HTTP 403. [Remaining scope](COMPLETION.md).
