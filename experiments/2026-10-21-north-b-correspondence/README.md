# Northern *b-* against Tamil *m-* and *v-* (NORTH-B-CORRESPONDENCE-2026-10-21)

Prediction P5 of conjecture [C-0011](../../knowledge/conjectures/C-0011-proto-dravidian-min-fish-and-star.md). We counted, across the *Dravidian Etymological Dictionary*, the initial of every Kurukh and Malto word in entries whose Tamil word begins with *m-* or *v-*, to learn whether the North Dravidian star words *bīnkō* and *bínḍke* can continue **mīn-*. The study reads no Indus text and spends no part of the corpus.

| File | Content |
|---|---|
| [PROTOCOL.md](PROTOCOL.md), [PROTOCOL.sha256](PROTOCOL.sha256) | Population, units, doubt and borrowing rules, secondary counts and pass rule, hashed before any entry was read |
| [PARSE-CHECK.md](PARSE-CHECK.md) | Boundary check of the parser against the source text and the five parse corrections made before the freeze |
| [FREEZE.json](FREEZE.json) | SHA-256 of the protocol, the corrections, the code and the input pages at the freeze |
| [REPORT.md](REPORT.md) | Results, credence and the boldest supported reading |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approach, problems and repairs |
| [CARD-PROPOSAL.md](CARD-PROPOSAL.md) | Proposed record entry, credence change and new prediction P6 for C-0011, for maintainers |
| [results-v1/results.json](results-v1/results.json) | The frozen counts: tables, pass rule, crossing entries, secondary counts S1–S7 |
| [verify/](verify/) | Second implementation written from the protocol alone, its notes and output |
| [exploratory-v1/exploratory.json](exploratory-v1/exploratory.json) | Tables computed after the frozen count |
| [parse-check/](parse-check/) | Parse summary and boundary-check output of the frozen code |
| [selftest-v1/selftest.json](selftest-v1/selftest.json), [bench-selftest-v1.json](bench-selftest-v1.json) | Synthetic checks of this code and of the shared harness |
| [code/](code/) | Parser, counter, self-test, boundary check and exploratory script |

## Data

No new source was acquired. The study reads the 514 DSAL pages of DEDR fetched by REBUS-BASE-RATE-2026-10-21 (`data/raw/2026-10-21-rebus-base-rate/sources-v1/dedr/`, request log SHA-256 `1452cfcf…`) and checks each page against its logged hash. It derives one local table, `data/raw/2026-10-21-north-b-correspondence/derived-v1/dedr-parts.jsonl`: every entry part with its language lines, forms, doubt and borrowing flags, initial class and vowel context. The table covers 5,627 entries (5,623 numbers, four of which DSAL uses for two different entries) and 5,715 parts. It stays local because DEDR is all rights reserved. For `knowledge/DATA.md`, the coverage facts are that 3,580 parts have a Tamil line, 374 with Tamil *m-* and 278 with Tamil *v-*, and that DSAL prints entries 1287, 1288, 2835 and 5282 twice with different content.

Run from the repository root with Python 3.13, standard library only:

```text
python -I experiments/2026-10-21-north-b-correspondence/code/selftest.py --out <new path>
python -I experiments/2026-10-21-north-b-correspondence/code/dedr_parts.py
python -I experiments/2026-10-21-north-b-correspondence/code/check_parse.py --out <new path>
python -I experiments/2026-10-21-north-b-correspondence/code/count.py --out <new path>
```
