# The base rate of a rebus (REBUS-BASE-RATE-2026-10-21)

Study 1 of the [Parpola direction note](../../knowledge/directions/parpola-forward-2026-10-20.md). We encoded Asko Parpola's homophone procedure as a program and measured how often it finds a rebus homophone, and how often his compound interlocks appear, when the words he started from are replaced by random words of the same kind. The study reads no Indus text.

| File | Content |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Question, encoding, inputs, pools, measurements and decision rules, frozen before the real runs |
| [FREEZE.json](FREEZE.json) | SHA-256 of the protocol, every script and every input table at the freeze |
| [REPORT.md](REPORT.md) | Results, decisions and the boldest supported reading |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approaches, problems and repairs |
| [SOURCES.json](SOURCES.json) | Provenance of every acquired file: URL, bytes, SHA-256, retrieval time, rights |
| [DATA-RECORDS.md](DATA-RECORDS.md), [MANIFEST-PROPOSAL.json](MANIFEST-PROPOSAL.json) | New sources and fields for maintainers to fold into `knowledge/DATA.md` and `data/MANIFEST.json` |
| [pools-v1.json](pools-v1.json) | The two concept pools (Concepticon IDs, glosses, classes) |
| [AMENDMENT-1.md](AMENDMENT-1.md) | The two code repairs made after the freeze, with hashes before and after |
| [selftest-v1](selftest-v1/selftest.json), [selftest-v2](selftest-v2/selftest.json), [bench-selftest-v1.json](bench-selftest-v1.json) | Synthetic checks of this code (before and after the amendment) and of the shared harness |
| [results-v1/](results-v1/), [results-v2/](results-v2/) | `homophones.json` and `interlocks.json` computed with the frozen code and with the repaired code; the report reads v2 |
| [verification-v1.json](verification-v1.json), [verification-v2.json](verification-v2.json) | Independent reimplementation of the main numbers; v1 found the defect, v2 agrees on all checks |
| [exploratory-v1/exploratory.json](exploratory-v1/exploratory.json) | Post-outcome analyses, labelled as such |
| [repo-verification-v1.json](repo-verification-v1.json) | Repository-wide structure and link check at submission |
| [code/](code/) | Acquisition, parsers, the procedure (`rebus.py`), runners, selftest, verification, manifest and freeze scripts |

Acquired pages, archives and every derived table stay local in `data/raw/2026-10-21-rebus-base-rate/`. Run the scripts from the repository root with Python 3.13 and NumPy; `code/acquire.py` restores the sources and `SOURCES.json` lets a reader check them.
