# Independent controls for the transmission study

12 October 2026. This package examines the route alternatives in the [integrated manuscript](../MANUSCRIPT.md). Its positive controls concern inherited professional verbal roles, separately aged textual organization and represented practical-to-conceptual incorporation. Its counterexamples identify stronger conclusions that those observations cannot establish.

| Read or reproduce | Artifact and scope |
|---|---|
| Historical assessment | [REVIEW.md](REVIEW.md) |
| New observations that could change a route | [FALSIFIERS.md](FALSIFIERS.md), nine prospective tests |
| Primary-source controls | [sources-v2.json](sources-v2.json) and [observations-v2.json](observations-v2.json): seven targets, six works read at declared scopes, 19 observations |
| Selected integrated anchors | [additional-anchor-review-v2.json](additional-anchor-review-v2.json): four material works and one complete hymn, with exact witness and derivative pins |
| Documentary source audit | [source-checks-v2/checks.json](source-checks-v2/checks.json): 174 integrity, locus and scope checks |
| Assigned logical countercases | [counterexamples-v1/results.json](counterexamples-v1/results.json): six hypothetical cases, ten simple consistency assertions |
| Actual validator limit | [validator-scope-v2/interpretation.json](validator-scope-v2/interpretation.json): an unsupported teaching interpretation passes 21 declaration checks |
| Independent comparison reconstruction | [comparison-checks-v1/checks.json](comparison-checks-v1/checks.json): 260 checks of seven comparisons, 35 rival records and reference joins |
| Exact final review scope | [reviewer-final-v1/checks.json](reviewer-final-v1/checks.json), including reviewed file hashes |
| Observable work and preservation | [RETROSPECTIVE.md](RETROSPECTIVE.md); the review wrote no changed-path inventory |

The source frame was fixed in [PROTOCOL.md](PROTOCOL.md) and [CONTROL-LOCI.md](CONTROL-LOCI.md). The added comparative essay and transport exception are recorded in the access amendment. Pollock’s inaccessible target remains in the ledger without a substantive observation. Identical Old Avestan mirrors and overlapping excerpts retain their dependencies.

Use the repository root as the working directory. Python source tools use `requests`, BeautifulSoup and PyMuPDF; the final comparison and claim checks use the standard library. Raw publications, extracted source-language passages and rendered pages remain ignored local files. A checkout alone therefore lacks the acquired inputs. Source paths, acquisition metadata and exact reading scopes are in the canonical ledgers.

Run a reconstruction only into a fresh output directory:

```powershell
C:\Python313\python.exe experiments/2026-10-12-transmission-hypothesis/review/check_comparisons.py --out experiments/2026-10-12-transmission-hypothesis/review/reproduction-comparisons-new
C:\Python313\python.exe experiments/2026-10-12-transmission-hypothesis/review/audit_sources_v2.py --out experiments/2026-10-12-transmission-hypothesis/review/reproduction-sources-new
C:\Python313\python.exe experiments/2026-10-12-transmission-hypothesis/review/counterexamples.py --out experiments/2026-10-12-transmission-hypothesis/review/reproduction-countercases-new
C:\Python313\python.exe experiments/2026-10-12-transmission-hypothesis/review/check_final_review.py --out experiments/2026-10-12-transmission-hypothesis/review/reproduction-final-new
```

The validator-fixture scripts and acquisition scripts preserve their original fixed endpoints and refuse existing outputs. Further fixture or source experiments require new code/output versions. The original wrapper failure, literal-anchor failure, first render manifest and editorial predecessors remain available.

Software checks assess reference integrity and declarations. Historical support rests on the inspected source claims and manual rival comparison. The hypothetical countercases have assigned conditions and do not estimate route likelihoods. The final assessment is limited to the pinned argument and declared source scopes.
