# Parpola's word assignments on sign pairs he did not choose (REBUS-BLIND-TEMPLATES-2026-10-22)

Prediction P1 of [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md). We gave 38 Indus sign pairs that Asko Parpola never published the Dravidian words he assigns to their pictures, and counted how often the two words form an attested compound of the Madras *Tamil Lexicon*, against random words matched on compounding productivity and frequency. His words succeed on 9 pairs against 4.97 expected (ratio 1.81, 95% interval 0.93–2.72), so P1 passes its frozen rule; his own twelve published pairs succeed seven times against 1.15 expected.

| File | Content |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Source check, identifications, template rules, null and decision rules, frozen before the confirmation read |
| [PREDICTIONS.json](PREDICTIONS.json), [PREDICTIONS.sha256](PREDICTIONS.sha256) | The registered shot with its joint credence rule |
| [round.json](round.json), [split-summary.json](split-summary.json) | The split of the pinned corpus and its frozen shot with artifact hashes |
| [identifications-v1.json](identifications-v1.json) | 16 signs, their ICIT codes, Tamil words and evidence; what was left out and why |
| [templates-v1.json](templates-v1.json) | The frozen template list: 38 primary, 24 gapped and 12 published pairs |
| [FREEZE.json](FREEZE.json) | SHA-256 of protocol, predictions, identifications, templates, code and input tables before scoring |
| [REPORT.md](REPORT.md) | Results, decision and the boldest supported reading |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approach, problems and repairs |
| [CARD-UPDATE.md](CARD-UPDATE.md) | Proposed record line and credence for C-0014 |
| [SOURCES.json](SOURCES.json), [DATA-RECORDS.md](DATA-RECORDS.md) | Acquired papers with URL, bytes, SHA-256 and rights; records for `knowledge/DATA.md` |
| [discovery-v1/pairs.json](discovery-v1/pairs.json), [confirmation-v1/pairs.json](confirmation-v1/pairs.json) | Pair counts by half, read through `bench.shots` |
| [power-v1/power.json](power-v1/power.json) | Power of the decision rules, simulated before the outcome |
| [selftest-v1/selftest.json](selftest-v1/selftest.json), [bench-selftest-v1.json](bench-selftest-v1.json), [shots-synthetic.json](shots-synthetic.json) | Synthetic checks of this code and of the shared harness |
| [results-v1/templates.json](results-v1/templates.json) | Frozen outcome with sensitivities, per-template rates and provenance |
| [verification-v1.json](verification-v1.json) | Independent reimplementation |
| [exploratory-v1/exploratory.json](exploratory-v1/exploratory.json) | Post-outcome comparisons, labelled as such |
| [code/](code/) | Acquisition, pair counts, template build, scorer, freeze, power, selftest, verification and exploratory scripts |

The acquired papers, the extraction records, the listing of cited objects and the word-level detail of each hit stay local in `data/raw/2026-10-22-rebus-blind-templates/`. The scorer imports `rebus.py` and `run_interlocks.py` from [REBUS-BASE-RATE-2026-10-21](../2026-10-21-rebus-base-rate/README.md) and needs that package's local tables.
