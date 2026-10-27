# Proposed data record

This package acquires no new source and changes no object coverage. It adds a local diagnostic derivative of already examined Tamil Lexicon, Winslow and Sangam inputs. Original source titles, access routes and rights remain in the [21 October source record](../2026-10-21-rebus-base-rate/SOURCES.json) and the [Winslow source record](../2026-10-22-rebus-winslow/SOURCES.json). The [new manifest](run-v1/source-manifest.json) pins every reused input, source page, historical helper and diagnostic code file.

The local derivative is `data/raw/2026-10-22-reading-eval-readiness/run-v1/lexical-audit-detail.json`. Its hash is in [input-audit.json](run-v1/input-audit.json). It contains lexical records and short source contexts, so it remains local under the existing unresolved digital-edition rights. Our code, protocols, input contracts and aggregates are tracked research outputs.

New fields are exact lookup status, stable lexical entry ID, all exact candidate records, reviewed-variant adjudication, exact written-form counts, historical prefix counts and explicit missing values. Of 24 proposed forms, eight have a unique exact record, fifteen have multiple records and one lacks an exact one-member record. The historical token denominator is 162,399 across seventeen files. Those files still need a poetry-only extraction and a reviewed inventory of inflections and sandhi forms before their counts can support a lemma-frequency or historical-attestation claim.

The object register dependency is a reviewed object and face identity, separate text-dependence grouping, source assertions with uncertainty, and exposure records for objects and outcome families. Provisional IDs and unreviewed exposure are retained as such. No new freshness or completeness figure is proposed for the shared data manifest.

Maintainers can link this package from the language-corpus and evaluation sections of `knowledge/DATA.md` after review. The ten named tasks in [BLOCKERS.json](BLOCKERS.json) give the inputs and acceptance evidence needed for the next run.
