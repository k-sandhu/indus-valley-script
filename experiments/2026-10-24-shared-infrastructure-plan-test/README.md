# Shared infrastructure against excavation evidence

We measured original excavation plans and audited dated seal and tablet contexts in a fixed six-town source frame, with Mohenjo-daro as a declared supplementary control. The evidence supports retention or renewal of some connections while access changed locally. It leaves the proposed institutional explanation undecided: no complete persistence comparison or matched documentary pair meets the frozen entry requirements.

Start with [REPORT.md](REPORT.md) for the argument and [RESULTS.md](RESULTS.md) for the quantities, positive context joins, missing links and source conflicts. [DECISION.md](DECISION.md) gives the strongest reading and the observations that could defeat it. [TEST-DESIGN.md](TEST-DESIGN.md) specifies the next acquisition and comparison, including rival explanations.

## Illustrated outputs

All large products stay local under `D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/`. Their manifests retain physical paths and hashes. The C: checkout reaches that root through the existing `data/raw/` junction.

| Output | Contents | Record |
|---|---|---|
| Illustrated report | 59 pages, complete source-use bibliography, 30 figures and deciding tests | [book-manifest-v2.json](book-manifest-v2.json) |
| Offline explorer | Thirty embedded display images, town and evidence filters, source search and plan magnification; no remote assets | [explorer-manifest-v2.json](explorer-manifest-v2.json) |
| Figure atlas | Thirty full-resolution PNGs and nine SVG charts, with captions, source manifest and contacts | [release-run-v2.json](modules/visuals/release-run-v2.json) |
| PowerPoint | Twenty-six slides with actual source plans, measured comparisons, context chains and counterexamples; three editable charts and eight tables | [artifact-manifest.json](modules/presentation/artifact-manifest.json) |
| Complete local package | Final illustrated products, source-linked figure archive, authored research records and reproduction code | [CHECKS.md](CHECKS.md) |

Fifteen atlas figures contain actual plans or context maps. Other source boards preserve sections, a photograph, original text excerpts and an explicitly labelled isometric reconstruction. Nine charts and diagrams are authored from recorded quantities or prospective predictions. The full-resolution originals remain in the atlas and PDF; the explorer uses documented display derivatives for reliable opening.

The products contain attributed third-party source excerpts with unresolved redistribution rights. Keep the illustrated files and archives local. Raw publications, acquired imagery, detailed coordinates, OCR and catalogue-row derivatives are not tracked in this package. No publication or deployment was performed.

## Data and provenance

[run-v1.json](run-v1.json), SHA-256 `1217731e249aa6cb51eaeebc9a7346a2ec291dccbbdd6fff7616847d199ddd3d`, joins 42 source-use records, 18 quantities, 29 architectural source cases, 32 context assessments and 78 dating entries. Their denominators differ. Seventy-six dating entries contain a reported determination or TL result; two Kanmer rice entries preserve paragraph ages without inventing raw BP values. No source-row total is promoted into independent repair episodes.

The protocol, amendment, feature inventories and context prejoin freeze record the order of work. Each quantity retains scale, north reference, source locator, uncertainty and a reason for missing fields. Source uncertainty is additional to endpoint-reading sensitivity. The one independently grid-registered Harappa pair is descriptive because its earlier partition exposure is incomplete.

[SOURCES.md](SOURCES.md) and the four source modules preserve source titles, editions, routes, hashes and exact locators. [DATA-UPDATE.md](DATA-UPDATE.md) records coverage gains and proposed integration. [POSTJOIN-LEAD-01.json](POSTJOIN-LEAD-01.json) preserves the Kanmer floor-sealing lead discovered during integration outside the frozen 32 assessments. [REVIEW-RESPONSE.md](REVIEW-RESPONSE.md) explains the repairs, and [RETROSPECTIVE.md](RETROSPECTIVE.md) preserves failed paths and outcomes.

## Verification and reproduction

The independent arithmetic review passes all eighteen quantities, the alternative Mackay edge and both grid fits. The separate visual audit confirms the historical scale calibration and keeps the unresolved fifth street chord missing. The root independently recounts all 93 Lothal provenance rows; the source's table and prose disagreement remains explicit.

The atlas passes 407 checks and individual inspection of every final figure. The final root study check passes 304 checks covering frozen inputs, source hashes, prior-file preservation, denominators, local storage and illustrated products. PowerPoint rendered all 26 slides, and all three native charts passed editing, resizing, saving and reopening in a test copy. The final PDF was rendered in full and reviewed through five contact sheets, with dense text checked at full size. Browser testing covers filters, search, empty results, modal opening and closing, magnification and console errors. The earlier large explorer exceeded a browser-control transport limit; its lighter successor passed. Both versions are preserved. [CHECKS.md](CHECKS.md) records the final versions and verification limits.

Run from the repository root with Python 3.13 and the installed scientific libraries. New tags preserve existing results:

```text
python experiments/2026-10-24-shared-infrastructure-plan-test/check_measurements.py --tag review-2
python experiments/2026-10-24-shared-infrastructure-plan-test/recount_lothal.py --tag review-2
python experiments/2026-10-24-shared-infrastructure-plan-test/validate_study.py --figures experiments/2026-10-24-shared-infrastructure-plan-test/modules/visuals/manifest-run-v2.json --tag review-2
```

The acquisition and rendering scripts require their pinned local sources. `write_results.py` made initial data tables and a prose draft; the final report text incorporates the recorded source review. The book archives the exact authored inputs used for each version. No script should replace a frozen version to improve its result.

`kb.py check` passes with no errors or warnings. Its generated-map and registry notes remain for maintainers. The broader repository verifier reports 58 pre-existing errors outside this contribution; `repository-check-summary-v1.json` records that scope. This study changes its owned package and one new registry entry, preserving prior work.

## Exposure and interpretation

The study is exploratory and reuses examined sources. The synthetic benchmark checks generated workflow guards only. No archaeological confirmation half was opened, the spending ledger is unchanged, and the prior conjecture credences remain 0.55, 0.35 and 0.10. The exact serving model variant is unavailable; contributors are recorded as GPT-6 family using the Codex desktop collaboration harness.

The strongest reading is selective continuity: some connections were retained or renewed while buildings and access changed. A powered comparison of complete phase windows, matched preservation and independently dated operational contexts can decide whether shared routes had the predicted advantage. Its disappearance under those controls, or a documentary association fully explained by manufacture and discard, defeats the relevant shared-infrastructure extension.
