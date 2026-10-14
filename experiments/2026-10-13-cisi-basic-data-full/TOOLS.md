# Commands and outputs

Run these commands from the repository root with Python 3.13. The scripts use the standard library and import the inventory's usable-value and grouping functions. The shared helper is `cisi_common.py`. Every value-bearing output is checked to be beneath `data/raw/`.

## Run order

First test the code without opening this run's readings:

```text
python experiments/2026-10-13-cisi-basic-data-full/selftest.py
```

The test generates its readings and decisions at run time in a new `data/raw/2026-10-13-cisi-basic-data-full/codex/selftest-<timestamp>/` directory. It also reads the pilot's final JSONL and final text files, Lipi, the older export and the dated museum source sets. The tracked `selftest.json` records individual check results and the pilot coverage regression. It contains no transcribed values.

Once the readers have finished, compare their files:

```text
python experiments/2026-10-13-cisi-basic-data-full/compare_passes.py
```

Give the local `compare/<block>.todo.json` files to the adjudicators. Each record names the CISI identifier, column, both readings and estimated strip paths. Strip locations use the entry's relative position in each pass, with a neighbouring strip on either side. They are location estimates; the code does not inspect images. Adjudicators write `adjudication/<block>.adjudication.json` using the records specified in the prompt. The code accepts `col1` through `col5` and the pilot's longer field aliases.

After all disagreements have decisions, build and merge:

```text
python experiments/2026-10-13-cisi-basic-data-full/build_finals.py
python experiments/2026-10-13-cisi-basic-data-full/merge_volumes.py
python experiments/2026-10-13-cisi-basic-data-full/crosscheck.py
```

Re-read the cells listed in local `recheck/todo.json` against the page and record `recheck/recheck.json`, as a list or an object with an `items` list. Use `confirmed`, `corrected`, `ambiguous` or `source-defect`. Each record supplies `cisi`, `column`, `outcome` and `final`; an optional `pass1` is checked against the current blind final. Confirmed and source-defect records preserve the current reading. Ambiguous records contain brackets. Rechecks cannot change row presence or identity.

Rebuild from the original passes, retaining every blind decision, then check again and join:

```text
python experiments/2026-10-13-cisi-basic-data-full/crosscheck.py --rebuild
python experiments/2026-10-13-cisi-basic-data-full/join_full.py
```

`--rebuild` invokes the final builder and merge in that order before producing a new cross-check list. The pilot remains its frozen input. A recheck that targets a blind-adjudicated cell, including an undecidable cell or a whole-row decision, is blocked and counted. Cross-check mismatches alone never supply a correction.

The parser can also run separately:

```text
python experiments/2026-10-13-cisi-basic-data-full/cisi_parse.py --volume cisi1 --out data/raw/2026-10-13-cisi-basic-data-full/codex/parsed.jsonl <input.txt>
```

All pipeline commands accept `--raw`, `--out` and `--blocks` for isolated fixtures, and `--block <id>` to select a block. `--allow-partial` explicitly permits interim work. The default build refuses missing passes or decisions before writing any finals; the default merge requires every selected entry block. Reports identify missing blocks and partial selections. Use the full commands above for the complete run. `join_full.py` and `crosscheck.py` accept alternate local `--lipi`, `--website` and `--table-join` paths; the join also accepts `--source-sets`. These two scripts operate on merged volumes, so block-selection options affect their rebuild step only.

## Output map

All local paths below are relative to `data/raw/2026-10-13-cisi-basic-data-full/`. Tracked paths are relative to this experiment directory. The commands write these files; this session does not stage files in Git.

| Command | Local, with values | Tracked, without values |
|---|---|---|
| `cisi_parse.py` | Chosen JSONL path and `.parse-report.json` sidecar | None |
| `compare_passes.py` | `compare/<block>.todo.json` | `accuracy/<block>.compare.json`, `compare-summary.json` |
| `build_finals.py` | `final/<block>.final.txt`, `final/<block>.final.jsonl`, `final/<block>.changes.json`, `final/<block>.parse-report.json` | `accuracy/<block>.accuracy.json`, `accuracy-summary.json` |
| `merge_volumes.py` | `cisi1-basic-data.jsonl`, `cisi2-basic-data.jsonl`, `merge-gaps.json` | `merge-summary.json` |
| `crosscheck.py` | `recheck/todo.json` | `crosscheck-summary.json` |
| `join_full.py` | None | `coverage.json`, `object-flags.csv`, `combined-coverage.json`, `predictions.json` |
| `selftest.py` | `codex/selftest-<timestamp>/`: fixtures, command logs, isolated reports, pilot merge and failure details if needed | `selftest.json` |

Every final accuracy record hashes its inputs and final outputs. The merge checks those hashes and row counts before using the block. The source comparisons and join record hashes of the merged tables and other inputs. Unknown museum codes, unknown photograph codes and unparsed museum fragments appear in local parser reports, with a row count in accuracy reports. A generic code stays as its printed code when there is no sourced expansion. CISI 1's listed codes are recognized; its year-shaped registration numbers are retained as registration numbers, without applying CISI 2's NMP-accession convention.

## Row and accuracy rules

An identical overlap row counts once. Explicitly distinct piece markers are combined in printed order, preserving empty piece cells and deduplicating repeated pieces. A lone piece marker belongs to the preceding entry. A conflicting duplicate produces a `row` todo with the canonical first occurrence and all other variants. It needs one whole-row decision. A row seen in only one pass also needs a whole-row decision whose final is a five-cell line or `absent`. The CISI identifier in a retained row must match the todo identifier. An uncertain identity that cannot be aligned causes a refusal with the file and line number, for coordinator repair.

Per-column denominators use the union of aligned identifiers. Missing readings are counted separately from adjudicated wrong cells: an omission supplies no definite cell reading. Whole-row decisions count omissions and spurious rows and adjudicate the present cells. Error rates use bracket-candidate matching, including unreadable bracket wildcards. Upper figures add undecidable cells for which that pass gave an unbracketed reading. Both passes receive the same calculation. A duplicate-row adjudication can decide canonical cells that agreed, so outcome counts can exceed the number of disagreeing canonical cells. The report states this rule.

The volume accuracy summary covers the new blocks. The pilot's accuracy endpoints remain in its own package. The merged CISI 2 table and all coverage calculations include the pilot once. The source-set union retains the pilot's dated museum sets as well. This preserves the pilot's separate sampled and full-reading endpoints.

The full comparison and final build require both volumes' separate corrigenda readings. They can also be selected explicitly with `--block cisi1-corrigenda` or `--block cisi2-corrigenda`. They are compared by printed-line position, using `line-<n>` in the decision's `cisi` field and `column: row`. Their final text and change log remain local; their text-line accuracy is reported separately. They produce no entry JSONL and do not enter object counts. Corrections mentioned in that prose are preserved as source text and require an explicit decision before being applied to an entry.

The merge refuses duplicate CISI identifiers, including entries that continue across block boundaries. A coordinator must consolidate such an entry into one block and rebuild that block's decisions before merging. Missing integer numbers between each prefix's lowest and highest present are listed locally and counted. A letter suffix occupies its integer number. This gap list cannot establish coverage outside those observed endpoints.

## Coverage and predictions

The family join follows the pilot: match the CISI prefix and integer base, and exclude multiple families, multiple bases on one family and multiple table rows for the same family. Coverage supplies museum number, holding institution, FC number and excavation number. Baseline museum and institution coverage use a usable older-export `MUSEUM` for the identical raw Lipi CISI key; excavation uses inventory-usable Lipi metadata. Corpus denominators include all Lipi families. Volume denominators contain the unique families joined to rows of that volume. Each population is also grouped with the inventory's type and site functions. Both modes count baseline or supplied fields, with the second excluding square brackets anywhere in the corresponding cell. Object flags contain identifiers, join dispositions and field booleans.

The combined museum report reuses the dated verifier's number-token rule and source sets. It reports counts and family identifiers for any number, a wholly unbracketed cell and any unbracketed number within a mixed cell. It also gives the union with the website, census, museum package and dated pilot sets. This token-based union is kept distinct from parser-based field coverage, as in the verification package.

Prediction 1 counts unique Mohenjo-daro entries outside M-621 to M-947 with an exact or confirmed table join, at least one numeric catalogue number and an unbracketed four-digit FC number. An entry satisfies the stated OR rule when at least one joined row satisfies its arithmetic rule. The report also gives the stricter share where all scorable rows match and counts entries with conflicting checks. It reports the entry numerator and denominator, the catalogue-row counts, excluded cases and exceptions by CISI identifier. The coordinator must supply evidence for the frozen prediction's claim that exceptions are crossed records or corrected cells; the code does not infer those causes.

Prediction 2 examines unique joined Harappa entries with a definite printed excavation cell. It removes separators, case differences, leading area letters and the printed (o)/(t) markers, then requires numeric identifiers. An extension must begin with a printed numeric identifier and append at least one digit; with several printed numbers it uses the longest matching prefix. All distinct extensions on the family's faces must match the FC tail as integers, allowing zero padding. Uncertain or missing FC numbers leave extensions unresolved. The report gives matches over all extensions, the share among scorable extensions and lower and upper figures that account for unresolved FC cells. Threshold and kill decisions use those figures. The report records every numerator, denominator and exclusion count.
