# Package Q: independent coding integrated

Positional tendencies and fish clustering survive all three mappings. The broad lexical excess remains conditional on construction; the clear-origin subsets show no detectable excess. Field totals and graphic coverage vary across the two AI coding rounds, with specialist review still pending.

Mayig overlap is **78/96**: **72 exact singleton matches**, **ten disjoint nonempty sets**, **eight first-reader missing sets**. Paired-singleton kappa is **0.9217 (n=78)**. Wells/Helsinki overlap is also **78/96**. [Agreement and confidence/type splits](two-coder-2026-10-09-v1/AGREEMENT.md); [all 38 candidate/component disagreements](two-coder-2026-10-09-v1/DISAGREEMENTS.md).

| Exploratory result | First | Second | Agreed-only |
|---|---:|---:|---:|
| Clean / conflict / indeterminate fields | 942/349/1178 | 781/302/1386 | 844/379/1246 |
| Fish adjacency / shuffle mean | 142/55.72 | 142/55.72 | 135/54.73 |
| Full lexical exact hits / types | 84/228 | 84/228 | 53/123 |
| Explicit-caption exact hits / types | 83/206 | 83/206 | 52/108 |
| Clear-origin exact hits / types | 2/5 | 2/5 | 0/1 |
| Clear-origin exact tail | .20 | .20 | 1.0 |
| Alias-joined attempts | 713 | 713 | 713 |
| Fully reference-supported attempt figures | 389 | 456 | 228 |

All broad lexical, fish and canonical-clean tails are .0005. The agreed-only panel retains **330/640** full-selection occurrences and **303** explicit-caption occurrences. Source-reading scores are identical under first/second external classes because the manuscript’s sign assignments remain fixed. The agreed-only calculation changes coverage. **Zero historical held-out entries** are individually identified. [Aggregate comparison](two-coder-2026-10-09-v1/comparison.json).

B069 and B078 are the main field cases for later adjudication; B017 and B052 account for the clear-origin types lost under agreement filtering. Both-high confidence agrees on 48/49 targets, with B043 disjoint. No disputed target was resolved. `class` means chart `rank`; direct code joins verify the ordinary numeric offsets, with P000 as a damage exception and P373/P374 absent from the chart. Code 369 is absent from Mayig’s direct code lists. [Reference check](two-coder-2026-10-09-v1/reference-check.json); [post-outcome target diagnostics](two-coder-2026-10-09-v1/target-attribution.json).

## Repeat the independent-coding sensitivity

From the repository root, choose new owned/raw output directories. The replay reads the frozen operational mappings and selections. Repeat the field, lexical and join commands for `second` and `agreed_only`, then use the verifier to compare the new endpoints.

```powershell
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py prepare --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py field --mapping first --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py lexical --mapping first --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py joins --mapping first --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/verify_second_coder.py --replay two-coder-replay-2026-10-09-02 --output two-coder-checks-replay-2026-10-09-02.json
python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write
```

The registered amendment and its operational clarification precede the main outputs. Earlier outputs and both returns remain frozen. The completed three-mapping replay passes **5,822/5,822 checks**, including **5,465 protected file hashes**. [SECOND-CODER-FILES.json](SECOND-CODER-FILES.json) inventories every created/changed path, and [two-coder-checks-2026-10-09-v2.json](two-coder-checks-2026-10-09-v2.json) records preservation and replay checks. The following paragraphs retain the PDF phase’s source inventory and frozen first-mapping results.

The owner’s **259-page PDF** matches the retained page-text edition. It has no printed folios; citations use one-based PDF pages. Table 18 contains **58 labelled assignments** (55 plus AS, ISH and ASTI) and **65 drawings**. With 17 caption-associated forms and 14 field targets, the frozen first coding covers **96 targets**: **85 singleton, three ambiguous, eight unmapped** Mayig assignments; **88/96** have Wells/Helsinki candidates. **59/65** Table drawings have class candidates. Counts distinguish drawings from archaeological sign classes. [Witness](pdf-2026-10-09-v1/witness-v3.json); [mapping](pdf-2026-10-09-v1/mapping-freeze-v2.json).

The blind [second-coder packet](../../data/raw/2026-10-08-bonta-review/second-coder-v1/) contains **96 neutral crops**, **687 chart cells**, Mayig metadata/contact sheets, instructions and `return-template-v2.json`. It omits proposed values and the first mapping. The mapping hash is `0ab1c2673d12026c8e628f794c45983414ca176d660c0db9bf599379b5940aa5`. The second coding is integrated in the three-mapping sensitivity. All endpoints remain **Exploratory**, with two AI coding rounds and no specialist review. [Packet index](pdf-2026-10-09-v1/second-coder-packet-v2.json).

The [reading inventory](pdf-2026-10-09-v1/reading-index-v4.json) has **1,200 source rows**, **859 attempt rows**, **549 distinct labels** and **718 explicit transcriptions**. Explicit manuscript aliases join **713/859 attempts** to **338 object families**; **146 attempts** remain unjoined. Thirty-three joined entries have source qualifiers requiring object review. Repeated illustrations, partial attempts and unclear/unattested flags remain counted. These extraction totals leave the historical attempt denominator unknown. [Coverage](pdf-2026-10-09-v1/reading-coverage-v5.json).

The canonical field rule gives **942 clean, 349 conflicting and 1,178 indeterminate** texts out of 2,469, against **419.87** clean on average under shuffling. On the 100 clear Mayig lines it gives **42/12/46**. Compound-aware fish adjacency is **142**, against **55.72** on average (95% range **44–66**). Wider field templates remain outside this canonical endpoint. [Fields](pdf-2026-10-09-v1/field-test.json); [Mayig](pdf-2026-10-09-v1/mayig-fields.json); [fish](pdf-2026-10-09-v1/fish-units.json).

The frozen expanded lexical set covers **640/859 attempts** and gives **84/228 exact type matches**, null mean **27.83**, tail **0.0005**. The post-outcome explicit-caption sensitivity gives **83/206**, mean **28.75**, tail **0.0005**. Restricting to clear derivations outside dictionary-context search and removing fitted alternatives leaves **2/5**, with **24/120 = 0.20** exact and **70/120 = 0.5833** normalized tails. Later extensions lack a separable lexical construction history; **zero historical held-out entries** are individually identifiable. [Full calculation](pdf-2026-10-09-v1/lexical-test.json); [sensitivity](pdf-2026-10-09-v1/lexical-caption-sensitivity.json).

The earlier panel still has **9/10 exact matches**. All **13** permutations scoring at least nine normalized hits keep PU; **0/600** moving it reaches nine. **Eight of ten** strings contain PU/PATI, values derived by searching that dictionary against the same contexts. Its tail is close to circular for those signs. Normalization exceeds Table 18’s lists, and all nine observed hits are exact. Holding PU/PATI fixed gives tails **2/24 exact, 8/24 normalized**; dropping their eight strings gives **4/24, 8/24**. [Review census](review/role-pair-census.json); [response sensitivity](response-2026-10-08-v2/lexical-sensitivities.json).

The jar is final **838/1,196 (70.07%)**, with **358 non-final** tokens and **241** followed by 400/090. The arrow is final **192/225 (85.33%)**, with **33 non-final**. Strong final tendencies reproduce while the categorical positional form fails. The old zero-repeat/maximum-three fish observation remains withdrawn as structural support. The PDF audit finds **68 ICIT-first labels**, **48 joined**, **eight confirmed MH links** and **one questioned alias**. The earlier three repeated objects retain their distinct uses: ICIT3656 is ICIT-first, ICIT3084 an MH-first alias and ICIT2816 an iconography remark; three false parser overlaps stay corrected. Physical quantity joins remain **zero**. [Exceptions](response-2026-10-08-v2/terminal-exceptions.json); [PDF audit](pdf-2026-10-09-v1/validation-audit-v4.json).

The [ledger](claims.md) has **1,021 records**: 130 retained, 32 new source claims and 859 reading annotations. The PDF phase changed **90** retained records, chiefly page locators and glyph identities. This phase updates **930 evaluation annotations**, including all 58 Table 18 value claims, while preserving source paraphrases, quotations and locators. [Second-coding annotations](two-coder-2026-10-09-v1/ledger-changes-v2.json). The catalogue erratum remains M212/M898 to **M-1688/M-958**: only M-1688 shows PU plus full-height 033; M-958/M-979 have short 003. [PDF changes](pdf-2026-10-09-v1/ledger-changes.json); [erratum](response-2026-10-08-v2/selection-errata.json).

## Reproduce from the repository root

System Python with PyMuPDF, Pillow and NumPy was used. Inputs are local pinned sources. Choose new output directories; scripts reject existing endpoints. Both roots must remain inside this package’s owned and local raw trees.

```powershell
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_lexical.py score --output-root experiments/2026-10-08-bonta-review/pdf-replay-2026-10-09-03 --raw-output-root data/raw/2026-10-08-bonta-review/pdf-replay-2026-10-09-03
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_lexical.py score --caption-only --output-root experiments/2026-10-08-bonta-review/pdf-replay-2026-10-09-03 --raw-output-root data/raw/2026-10-08-bonta-review/pdf-replay-2026-10-09-03
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_fields.py --output-root experiments/2026-10-08-bonta-review/pdf-replay-2026-10-09-03 --raw-output-root data/raw/2026-10-08-bonta-review/pdf-replay-2026-10-09-03
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_validation.py --output-root experiments/2026-10-08-bonta-review/pdf-replay-2026-10-09-03
python -B -X utf8 experiments/2026-10-08-bonta-review/verify_pdf_followup.py --full-replay pdf-replay-2026-10-09-03 --caption-replay pdf-replay-2026-10-09-03 --output pdf-checks-replay-2026-10-09-03.json
python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write
```

The computational replays read the frozen selections and mapping. Source extraction and editorial scripts record the staged work: `pdf_followup.py`, `pdf_readings.py`, `pdf_supplement.py`, `pdf_mapping_extension.py`, `pdf_source_checks.py`, `pdf_final_census.py`, `pdf_metadata.py` and `pdf_write_report.py`. Annotation stages preserve versioned outputs and are separate from score replay. The validation replay reproduces v3; v4 qualifies ICIT3355 through the inspected PDF source. Both are retained.

The original numerical run, original selection, registered protocol, review and response calculations remain preserved. Historical checks (review **54/54**, response **110/110**) apply to those earlier states. The PDF checks and replay comparison are recorded in [pdf-checks-2026-10-09-v3.json](pdf-checks-2026-10-09-v3.json). [PDF-FILES.json](PDF-FILES.json) lists every created or changed path; [FILES.json](FILES.json) inventories current package contents. Old response inventories remain unchanged.

The [report](REPORT.md), [protocol](PROTOCOL.md), [retrospective](RETROSPECTIVE.md), [sources](sources.json) and [registry proposal](registry-entry.json) give methods and limits. Specialist adjudication of disputed mappings, manual adjudication of remaining source attachments, the historical ICIT batch, wider field rules, explicit phonological/multiword acceptance and physical quantity joins remain unfinished. Kalyanaraman’s substantive content stays unverified after HTTP 403. [Completion scope](COMPLETION.md).

Reviewer sampling should cover Table 18 pp. 79–82; the DAna label reversal on pp. 132/134; source variants U149 on pp. 159/170; ICIT3355 p. 92; ICIT3656 pp. 193/213; and Table 21 pp. 249–251. Repeat lexical/field replays, confirm mapping hashes precede packets and verify packet neutrality.
