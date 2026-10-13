# Four Bronze Age documentary comparisons

Completed exploratory source acquisition and analysis, 12 October 2026 UTC. The program follows the user's request to pursue Sumerian, Akkadian, Egyptian and Mycenaean Greek comparisons with IVS.

| Read or reuse | File |
|---|---|
| Findings in plain language | [REPORT.md](REPORT.md) |
| Research manuscript | [MANUSCRIPT.md](MANUSCRIPT.md) |
| All principal numbers | [TABLES.md](TABLES.md) |
| Exact claims and outputs | [CLAIM-EVIDENCE.json](CLAIM-EVIDENCE.json) |
| Sources, pins, scope and rights | [SOURCES.md](SOURCES.md), [observations.json](observations.json) |
| Methods and manual replay | [METHODS.md](METHODS.md), [requirements.txt](requirements.txt) |
| Starting protocol and cohort recipe | [PROTOCOL.md](PROTOCOL.md), [COHORT-SPEC.md](COHORT-SPEC.md) |
| Source repairs and additional control | [PARSER-AMENDMENT.md](PARSER-AMENDMENT.md), [SOURCE-MARKUP-AMENDMENT.md](SOURCE-MARKUP-AMENDMENT.md), [AMENDMENT-SIGN-CONTROL.md](AMENDMENT-SIGN-CONTROL.md) |
| Current structural/word endpoint | [run-v2](run-v2/manifest.json) |
| Current boundary-concealed endpoint | [sign-control-v2](sign-control-v2/manifest.json) |
| Challenges, fixes and outcome | [RETROSPECTIVE.md](RETROSPECTIVE.md) |
| Discriminating next observations | [NEXT-TESTS.md](NEXT-TESTS.md) |

## Scope

The study measures record ordering, known-category recovery and per-face lexical-pattern ambiguity. It supplies no authenticated IVS sounds, meanings or historical language identification. Source word categories, Greek writing-unit types, cuneiform reading units and Egyptian glyphs retain their separate definitions. The manuscript keeps their common inferential assumptions together.

## Verification

- [Primary arithmetic/source-group checks](run-v2/verification.json) independently reconstruct counts, observed position statistics, analytic permutation expectations, accuracy, split exclusions and ignored raw-input handling.
- [Sign-control checks](sign-control-v2/verification.json) validate source-label alignment, physical/text exclusions and saved-prediction recounts.
- [Separate category decision replay](category-replay-verification-v2.json) reconstructs sampled predictions from a Counter implementation.
- [Source-correction comparison](source-correction-comparison.json) confirms exact unchanged non-Greek cohort outcomes.
- [Final package checks](package-verification.json) cover source bytes, pointers, prose, endpoint preservation and research-memory integration.

## Preservation and source access

`normalized-v1` stopped before creating a dataset. Local normalized-v2 and normalized-v3 preserve successful earlier representations. [run-v1](run-v1/manifest.json) and [sign-control-v1](sign-control-v1/manifest.json) preserve calculations before the Greek display-markup correction. Exact code-byte snapshots are retained under [history](history/statistical-endpoint-v1/analyze.py); they assume their original module paths and should be replayed from that layout in a separate checkout. Baseline navigation bytes and named input hashes are in [baseline-v1.json](baseline-v1.json).

Raw/source-derived assets are under ignored data/raw/2026-10-12-bronze-age-comparison/. This includes corpora, TEI/HTML witnesses, dictionaries, anonymous-ID maps, rows, predictions and permutation details. The acquisition plans and request manifests retain exact hashes/routes. A public checkout can inspect aggregate results and code; replay needs those pinned local inputs. New outputs refuse overwrite. No CI/CD, deployment scaffold, scheduled automation, external publication or visibility change was added.
