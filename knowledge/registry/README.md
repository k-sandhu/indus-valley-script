# Registry records

An attempt is one recorded try at a research question, whatever its outcome. Each attempt lives in `attempts/<ID>.json`. To add one, copy the field structure of an existing entry or run `python tools/kb.py new attempt --title "Your question" --area data`, then complete its outcome, evidence, authors and the condition under which it should be retried. Read [VOCABULARY.md](VOCABULARY.md) before choosing its area and status class.

Original entries keep every field and a zero-based `registry_order`. New entries omit that field and sort after the originals by ID. `metadata.json` preserves the registry’s top-level schema and scope. Maintainers run `python tools/kb.py build` after merging entries; contributors do not edit the [generated registry](../experiments/registry.json) or [map](../MAP.md) by hand.

The [status mapping](STATUS-MAPPING.md) records how the preserved entries were classified. To find prior work, run `python tools/kb.py search <terms>` and read the linked retrospective before starting a new run.
