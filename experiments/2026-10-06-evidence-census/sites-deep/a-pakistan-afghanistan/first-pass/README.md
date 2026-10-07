# Pakistan and Afghanistan site census

This exploratory census contains 33 in-scope site rows, 90 source records and 126 dated query records. Seven sites have at least one machine-readable numeric count claim. Those claims use incompatible units, so this package does not publish a summed inscription total. The detailed records are in [site-rows.json](site-rows.json), [site-rows.csv](site-rows.csv), [site-count-comparison.json](site-count-comparison.json), [sources.json](sources.json) and [searches.json](searches.json).

The local Lipi snapshot matches 27 rows: 4,832 faces, 3,903 object-family records and 3,634 distinct CISI identifiers. These are database figures, not verified physical-object totals. The highest CISI sequence number is retained as a coverage clue, not proof of completeness. See [aggregate.json](aggregate.json) and the site-level `local_corpus` and `local_coverage_judgment` fields.

Five India-side local labels were excluded from the Pakistan-Afghanistan rows and documented in [scope-exclusions.json](scope-exclusions.json). Karanpura is listed there and in the aggregate as a source-attested Inter-Riverine cross-reference in Rajasthan, not a full row. The regional search did not establish another in-scope Pakistan or Afghanistan site to add.

## Reproduce

From the repository root, run:

```powershell
python experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/build_site_rows.py
```

The script combines the three research slices, maps their source and search identifiers, joins the supplied local-site snapshot by site label and writes the JSON/CSV aggregates listed above. Source payloads remain in the local-only raw directory where available; the source ledger gives URLs and access state.

## Scope and limits

The package completes site metadata and bibliography coverage unevenly. Count records explicitly distinguish objects, faces, texts, marks and report-level claims. Many class totals, page ranges, custody statements, reuse terms and artifact-level context fields remain unresolved. The row field `open_problems` and linked search IDs specify what was not recovered. See [PROTOCOL.md](PROTOCOL.md), [REPORT.md](REPORT.md) and [RETROSPECTIVE.md](RETROSPECTIVE.md).
