# Registry records

Each attempt lives in `attempts/<ID>.json`. Copy an existing entry’s field structure or run `python tools/kb.py new attempt --title "Your question" --area data`, then complete its outcome, evidence, authors and retry condition. Read [VOCABULARY.md](VOCABULARY.md) before choosing its area and status class.

Original entries retain every field and a zero-based `registry_order`. New entries omit that field and sort after the originals by ID. `metadata.json` preserves the registry’s top-level schema and scope. Maintainers run `python tools/kb.py build` after merging entries; contributors do not hand-edit the [generated registry](../experiments/registry.json) or [map](../MAP.md).

The [status mapping](STATUS-MAPPING.md) records the classifications of the preserved entries. To find prior work use `python tools/kb.py search <terms>` and read the linked retrospective before starting a new run.
