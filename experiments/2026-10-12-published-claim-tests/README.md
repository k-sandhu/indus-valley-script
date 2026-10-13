# Tests of published Indus decipherment and usage claims

12 October 2026. Claude Opus 5.5 ran this package unattended, with two subagents for Studies B and C and a third for the adversarial review of Study A, while Codex continued its own October 12 packages. The [protocol](PROTOCOL.md) was recorded before outcomes. Each study keeps its scripts, frozen outputs, amendments and verification together.

| Study | Question | Report |
|---|---|---|
| A | Does Yajnadevam's Sanskrit key, or its unicity-distance argument, show that the inscriptions record Sanskrit? | [Sanskrit key](sanskrit-key/REPORT.md) |
| B | Do Indus-script inscriptions found in Mesopotamia, Iran, the Gulf and Central Asia follow South Asian sequence statistics? | [Foreign finds](foreign-finds/REPORT.md) |
| C | Do the key's allograph and homophone groups behave as interchangeable signs in the corpus? | [Allographs](allographs/REPORT.md) |

**Study A.** A lexical emulation of Yajnadevam's acceptance criterion (Sanskrit words with free vowels, division and compounding) accepts 92% to 100% of random consonant strings, so his unicity-distance argument gives no bound for it; his key's dictionary fit is real but reaches between a third and a half of what rearranging its own values can reach. Under an order-5 Sanskrit model, his key's consonant sequences score −0.39 bits per consonant of order gain against +0.29 to +0.42 for held-out Sanskrit, and 1.2 to 2.4 standard deviations above rearrangements of its own values, depending on training text and projection; their order adds nothing over the rearrangements. On synthetic Indus-shaped homophonic encodings of four languages, the true key sits 27 to 72 standard deviations above its rearrangements. Keys fitted to half the corpus transfer to the other half equally well under Sanskrit, Latin, Old Tamil and Sumerian models, also after near-duplicate texts are removed. An [adversarial review](sanskrit-key/review/REVIEW.md) led to the revisions listed in its [response](sanskrit-key/review/RESPONSE.md).

**Study B.** West Asian finds are much less predictable under South Asian statistics than matched South Asian texts (Ū = 0.770, 2.11 extra bits per transition), above the variation among South Asian regions (0.49 to 0.57). Round Gulf-type seals carry most of the excess (Ū = 0.870), and round seals found in South Asia are atypical too (0.704), so the deviation follows the seal type as well as the findspot.

**Study C.** The key's variant groups substitute and share neighbours beyond frequency, at about the level of other graphically related signs such as the stroke numerals. Its homophone groups, the part that carries the Sanskrit reading, do not (p = 0.13 and 0.21).

Raw sources (the DCS Sanskrit texts, Monier-Williams, Latin, Old Tamil, both preprints) and every file containing full inscription sequences are under the ignored `data/raw/2026-10-12-decipherment-claim-tests/`. The [retrospective](../../knowledge/retrospectives/2026-10-12-published-claim-tests.md) records the approach, failures and repairs.
