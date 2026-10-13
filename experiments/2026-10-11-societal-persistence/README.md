# Societal persistence and renewal

11 October 2026. A literature survey, conditional theory, exact finite constructions and Harappan application developed in parallel with independent adversarial review.

Start with [REPORT.md](REPORT.md) for the findings and [MANUSCRIPT.md](MANUSCRIPT.md) for the argument. [THEORY.md](THEORY.md) defines the persistence unit, minimum functions, admissible paths, accounting bound and work-window constraint. [MODEL-RESULTS.md](MODEL-RESULTS.md) explains every numerical claim's scope. The empirical comparison is [prospective](EMPIRICAL-PROTOCOL.md).

| Package | Contents |
|---|---|
| [Literature survey](literature/SURVEY.md) | Primary theoretical and archaeological research, actual reading scope, query history and an explicit predecessor assessment |
| [Harappan application](evidence/APPLICATION.md) | Source-linked drainage, water, provisioning and craft observations, with [tests](evidence/TESTS.md) |
| [Independent review](review/REVIEW.md) | An independently written finite-model checker, law sensitivities, six counterexamples and [rejection criteria](review/FALSIFIERS.md) |
| [Claim map](CLAIM-EVIDENCE.json) | Joins from coordinator claims to observation IDs, source records and exact JSON outputs |
| [Review response](REVIEW-RESPONSE.md) | Accepted changes to horizon, output units, action timing, implementation and prospective testing |
| [Retrospective](RETROSPECTIVE.md) | Observable research choices, challenges, source repairs and outcomes |
| [Manifest](manifest.json), [verification](verification.json) | Final file pins, reference checks, raw disposition and preservation of prior records |

## Reproduction and source access

The coordinator's [renewal model](coordinator/renewal_model.py) and the review's numerical programs use the Python standard library. Use fresh output directories; the CLIs refuse to replace an endpoint. Commands are given in [MODEL-RESULTS.md](MODEL-RESULTS.md) and [the review README](review/README.md). The numerical results do not require downloaded ancient corpora or calibrated archaeological parameters.

Source audits and extraction tools additionally require their pinned local witnesses and the dependencies named in each branch. The [coordinator source ledger](coordinator/SOURCES.json), literature ledger and evidence ledger record public URLs, inspected pages, hashes, rights and access failures. Acquired publications, complete extracts, OCR and rendered pages are kept under ignored `data/raw/2026-10-11-societal-persistence/`. Downloading an article does not imply that every page was read; an alternate access route to the same report does not create independent field evidence.

The [starting inventory](baseline-v1.json) hashes 16,316 pre-existing tracked or unignored files and preserves 12 selected exact-byte snapshots locally. Current navigation bytes are separately saved immediately before integration. The final check reports observed changes outside this program's ownership without restoring over other work. Earlier manifest hashes for shared navigation describe their own integration versions and remain unchanged.

The [protocol](PROTOCOL.md) was written before the new calculations and source coding. Previous familiarity and later exploratory additions remain identified. This package adds no CI/CD, deployment, automation, commit, push or external publication.
