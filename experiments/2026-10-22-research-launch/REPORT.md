# Directions 1, 2 and 7: first execution block

We have built the base object register, connected it to the unit-study work queue, and repaired the lexical input operations needed for a comparison of readings. Three agents worked in separate packages. The [execution plan](PLAN.md) and [scope record](SCOPE.json) preceded the builds. This completes the first implementation block; source adjudication and prospective evaluation remain the next work.

## What now exists

| Direction | Completed work | Evidence |
|---|---|---|
| 1. Object register | The final run contains 4,695 provisional object families, 5,680 faces and 225,223 attributed assertions. The existing 4,075-object CISI and 3,598-object dimension baselines reproduce. | [Coverage](../2026-10-22-object-register/run-v2/coverage.json), [schema and relationship checks](../2026-10-22-object-register/run-v2/validation.json), [independent interface check](register-interface-v2.json) |
| 2. Inscription units | All 118 divided-face records join the new register. The integrated queue carries image-conflict flags and identifies three faces needing image-identity review. The queues account for layout, acquisition, side-assignment and candidate-exposure work. | [Report](../2026-10-22-unit-readiness/REPORT.md), [integrated audit](../2026-10-22-unit-readiness/readiness-register-v2.json) |
| 7. Competing readings | Exact lexical matching preserves vowel marks, length and gemination, exposes homographs and requires evidence for variants. Participant checks reject incomplete declarations, altered inputs, unresolved exposure and unsupported scorers. | [Report](../2026-10-22-reading-eval-readiness/REPORT.md), [participation contract](../2026-10-22-reading-eval-readiness/PARTICIPANT-CONTRACT.json), [independent test rerun](reading-tests-reproduced.json) |

The register's final local directory is `data/raw/2026-10-22-object-register/run-v2/`; the original plan's `run-v1` is preserved. The integrated unit queues are in `data/raw/2026-10-22-unit-readiness/run-register-v2/`. The register keeps aliases and provisional physical families distinct. Its 2,596 objects with unreconciled field variants and 1,348 unresolved join-queue rows remain work items. Multiple source spellings can produce a variant; these counts do not establish that the sources are wrong.

The CISI reader-decision table contains 2,870 automatic merges. The register retains the candidate values and excludes automatic, undecidable and bracketed cells from accepted fields. It also retains a reported 3,000 mm dimension while withholding that implausible value from accepted measurements. Source assertions remain available for review.

The lexical audit used the same 162,399-token stream for both matching rules. *Kā* changed from 22,287 prefix matches to 9 complete written tokens, and *ā* from 4,458 to 24. Across 24 proposed forms, eight have one exact dictionary record, fifteen have multiple records and one has none. These are input diagnostics; the rebus effect has not been recomputed.

## Next work in dependency order

| Order | Concrete work | Completion evidence |
|---|---|---|
| 1 | Review the three flagged image identities, then adjudicate the 29 already imaged divided faces without accepted reading order. Begin side assignment for the 378 queued multi-face objects with linked images in parallel. | Independent source-coordinate annotations, retained disagreements and agreed physical-side assignments. |
| 2 | Obtain crops for 32 CISI 3 divided faces and resolve primary locators for eleven divided faces without CISI numbers. Work through the other 503 multi-face objects requiring image acquisition or a source join. | Every selected face has an identified image, source locator, transform and layout record. |
| 3 | Extend the register adapters to the deferred museum fields, alternate face concordances and catalogue-only or post-catalogue objects. Resolve the candidate identity queue. | Source-qualified assertions and a reviewed physical identity graph, with all unresolved joins retained. |
| 4 | Extract line-addressable poetry text from the seventeen held files; review meaning-dependent lexical choices; validate the Winslow compound parser on a stratified source sample; rebuild features for both proposals and controls. | Reviewed text, forms, senses and compound labels; measured parser errors and complete matching inputs. |
| 5 | Review the 358 candidate inventory rows against source-page, object, participant and statistic-family exposure; validate known-script controls and calibrate each scorer. | A justified eligible cohort, documented dependence groups and prespecified error and power checks. |
| 6 | Freeze every participant and prediction through the shared shots loader, then run the substantive unit and reading tests. | One versioned confirmation record with all predictions, failures and spending retained. |

All 358 candidate rows cite sources with access-log entries. Those entries need object- and participant-specific interpretation. This run certifies no fresh object and opens no new confirmation cohort. The [unit release decision](../2026-10-22-unit-readiness/release-decision.json) and [reading blockers](../2026-10-22-reading-eval-readiness/BLOCKERS.json) state the evidence needed at each gate.

## Verification and claims

Our independent interface check uses the source IDs directly and imports no builder helpers. It reproduces both populations, every face-to-family relationship, the canonical value statuses and the explicit unreviewed exposure states. The integrated unit audit passes all its checks. We independently reran all 21 lexical and participant tests during integration. The two unit and three reading synthetic bench runs pass; these controls do not establish scientific calibration on real data.

Work claims remain open: [Q-1030, object register](https://github.com/k-sandhu/indus-valley-script/issues/3), [Q-0027, unit evidence](https://github.com/k-sandhu/indus-valley-script/issues/4), and [Q-0039, reading evaluation](https://github.com/k-sandhu/indus-valley-script/issues/5). Raw and detailed source-derived outputs remain local. Shared inventory and map changes are proposed in the worker packages for maintainer integration. [Validation](VALIDATION.md) records the final repository checks.

Our strongest supported claim is that the three directions now share executable evidence accounting and explicit input gates. The deciding scientific evidence will come from reviewed source observations and calibrated predictions on an eligible, frozen object cohort.
