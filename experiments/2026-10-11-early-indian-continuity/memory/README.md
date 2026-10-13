# Practical memory and changing origin accounts

The [report](REPORT.md) examines Manu's flood and Iḍā procedure, Sarasvatī and the river studies, and DN27's rice/property/authority account. It develops a practical-retention mechanism and tests that can separate local inheritance, diffusion, reconstruction and doctrinal origin stories. No Harappan transmission route was identified in these inspected cases.

The frozen package contains 18 source records and 17 observations. The typed claim graph has 16 nodes and 11 edges; 10 challenged composition-dating routes are blocked, and two controls permit a witness to attest its own text's presence. An explicitly invented rewrite maps 10,368 histories to one coherent operation account after historical attribution is removed. These counts describe a documentary audit and logical construction, with no estimated historical probabilities. Source and arithmetic checks passed 96 checks.

| File | Use |
| --- | --- |
| [PROTOCOL.md](PROTOCOL.md) | Frozen design, source targets, typed dating rules and constructive test. |
| [METHODS.md](METHODS.md) | Inspected source scope, data handling and exact meaning of the executable results. |
| [TESTS.md](TESTS.md) | Prospective comparison units, controls and rejection conditions. |
| [sources.json](sources.json) | Bibliographic metadata, access scope, local witness hashes, failures and rights observations. |
| [observations.json](observations.json) | Our source-qualified paraphrases with exact loci and limits. |
| [claim-graph.json](claim-graph.json) | Typed observations, supported/proposed links and specified routes. |
| [source-checks.json](source-checks.json) | Locus/token controls plus the declared manual reading scope. |
| [run-v1/summary.json](run-v1/summary.json) | Frozen descriptive counts and input hashes. |
| [run-v1/graph-audit.json](run-v1/graph-audit.json) | Each challenged route and each permitted presence control. |
| [run-v1/compression-demo.json](run-v1/compression-demo.json) | Complete finite-space counts, equivalence classes and invented examples. |
| [verification.json](verification.json) | Independent pin, locus, type and arithmetic checks. |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Source problems, fixes, outcomes and limits. |
| [changed-paths.json](changed-paths.json) | Owned tracked/local-only changes, recorded after package completion. |

Run the constructive analysis from the repository root with a fresh output name:

```powershell
C:/Python313/python.exe -X utf8 experiments/2026-10-11-early-indian-continuity/memory/analyze.py --out run-v2
C:/Python313/python.exe -X utf8 experiments/2026-10-11-early-indian-continuity/memory/verify.py --run run-v2 --out verification-v2.json
```

The analysis uses standard-library Python and the frozen tracked inputs. Verification also requires the locally preserved raw witnesses and extracts listed by the ledgers, including two sources acquired by the independent reviewer. It fails when those hashes or files differ. All output writers refuse overwrite. A new run preserves earlier endpoints; a substantive source correction needs a separately dated input amendment before a new outcome is generated.

`acquire.py` records the initial bounded HTTPS acquisitions and their failures. Follow-up target URLs and exact hashes are in the local acquisition ledgers; these include correction of the initially wrong Śatapatha target. `extract.py` derives local text from source HTML/JSON/PDF and requires BeautifulSoup and PyMuPDF. `build_inputs.py` records our editorial coding and builds the four frozen input JSON files only when they do not already exist. Extracted text is a convenience for inspected loci, not an automated interpretation. The two selected rendered PDF pages were also visually checked.

Raw downloaded texts, PDFs, web-search responses, extracts and source-page renders remain under `data/raw/2026-10-11-early-indian-continuity/memory/`, with reviewer-supplied witnesses referenced read-only. Only our prose, bibliographic metadata, hashes, code and invented construction are prepared as research contents. The package makes no new publication or redistribution decision. The [independent review](../review/) checks the sources and reconstructs the graph and finite enumeration separately.
