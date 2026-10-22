# The veḷ search in Winslow's dictionary (REBUS-WINSLOW-2026-10-22)

A test of prediction P2 of [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md). We reran the *veḷ* interlock search of the [21 October base-rate study](../2026-10-21-rebus-base-rate/REPORT.md) in Winslow's Tamil-English dictionary of 1862, with the frozen code of that study and random replacement words matched on compounding productivity and Sangam frequency. Winslow has no compound beginning with *muruku*, so the frozen chance rate is zero and P2 fails. The study reads no Indus text.

| File | Content |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Source review, parsing rule, parser checks, reused code, measurement and decision rule, frozen before the run |
| [FREEZE.json](FREEZE.json) | SHA-256 of the protocol, our code, the reused code and every input at the freeze |
| [REPORT.md](REPORT.md) | Results, the two dictionaries side by side, the boldest supported reading and the test that would decide it |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approaches, problems and repairs |
| [C-0014-RECORD-PROPOSAL.md](C-0014-RECORD-PROPOSAL.md) | Proposed record line, credence change and new prediction for the card |
| [SOURCES.json](SOURCES.json) | Every acquired page with URL, bytes, SHA-256, retrieval time and log file |
| [DATA-RECORDS.md](DATA-RECORDS.md), [MANIFEST-PROPOSAL.json](MANIFEST-PROPOSAL.json) | The new source and table for `knowledge/DATA.md` and `data/MANIFEST.json` |
| [parser-validation-v1.json](parser-validation-v1.json) | Transliteration, agreement and coverage checks of the parser against the *Tamil Lexicon* |
| [check-reuse-v1.json](check-reuse-v1.json) | The wrapper reproduces the 21 October results-v2 from the Lexicon table |
| [selftest-v1](selftest-v1/selftest.json), [selftest-base-v1](selftest-base-v1/selftest.json), [bench-selftest-v1.json](bench-selftest-v1.json) | Synthetic checks of this package, of the reused code and of the shared harness |
| [results-v1/interlocks.json](results-v1/interlocks.json) | The frozen result |
| [verification-v1.json](verification-v1.json) | Independent recomputation of the main numbers |
| [exploratory-v1/exploratory.json](exploratory-v1/exploratory.json) | Post-outcome analyses, labelled as such |
| [code/](code/) | Acquisition, parser, parser checks, run wrapper, reuse check, selftest, verification, manifest, freeze and post-outcome scripts |

Acquired pages and the parsed table stay local in `data/raw/2026-10-22-rebus-winslow/`; `code/acquire.py` restores them and `SOURCES.json` lets a reader check them. The run also needs the local DEDR table and Sangam texts of the 21 October study. Run the scripts from the repository root with Python 3.13 and NumPy.
