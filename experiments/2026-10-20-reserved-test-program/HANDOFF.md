# Before the reserved collection is scored

The [readiness audit](run-v1/readiness.json) found matching hashes for every listed seal-structure and fish-model artifact. The [generated-data loader check](shots-synthetic-v1.json) passed all guards. Neither operation read a new inscription. The acquisition collection remains reserved.

## Existing predictions

| Candidate participant | Existing evidence | What must be fixed for an external collection |
|---|---|---|
| Seal opening and closing structure | [Frozen predictions](../2026-10-20-seal-legend-units/PREDICTIONS.md), [hash list](../2026-10-20-seal-legend-units/PREDICTIONS.sha256), and frozen scorer | A shared-loader registration that cites the unchanged rules, eligibility and joint credence rule; source and identity eligibility review |
| Fish order | [Predictions](../2026-10-20-fish-context/PREDICTIONS.json), [freeze](../2026-10-20-fish-context/freeze-v1.json), and [C-0007](../../knowledge/conjectures/C-0007-fish-compound-designations.md) | An explicit external-population protocol, fixed grouping and comparator, minimum support, and an interpretation rule for overlap with other participants |
| Unicorn affiliation | [C-0003](../../knowledge/conjectures/C-0003-unicorn-affiliation.md) | Whether the collection meets the prospective prediction's defined assemblage and site conditions; it calls for at least 30 seals |

These are candidate uses of the collection. No participating test has been registered on its new objects in this package.

## Two details to resolve before release

The seal-structure `predictions.json` holds numeric bounds and power tables. Its human-readable companion holds the named predictions and joint credence rule. The JSON does not directly satisfy the shared shots registration schema. The standalone scorer checks its hashes and writes a private access log, but reads its supplied JSONL directly. A later study must register a wrapper that preserves the frozen rules and routes access through the shared loader. It must not treat the standalone hash check as a record that every other participating model froze before access.

The population prose says that a legend already transcribed in the export is excluded, and also says that a new legend identical to a known text counts and is flagged. These can be reconciled by distinguishing an already represented physical object from a different object bearing a repeated text, but that distinction needs an explicit, pre-release eligibility statement. The current scorer flags equality with its build corpus and removes duplicates within its input; it does not establish physical identity or a complete project exposure history. The custodian's alias and exposure records supply the necessary source review. This package leaves the original files unchanged and does not decide eligibility by observing a future score.

## Release record

The eventual release should identify the collection hash, its full disposition table, the exact eligible components, source and transcription uncertainties, prior exposures, all registered participants and their immutable artifacts. Use a versioned ledger that includes the existing exposure history. Register every test sharing the confirmation data before any read. State how old discovery material and the new external collection relate to the shared loader's split; creating a new seed is not evidence of freshness.

If the eligible set is too small, retain it for an acquisition extension under the same rule. Do not silently remove difficult objects or add attractive examples. A reserved collection with images and context remains a data contribution even when a particular prediction cannot yet be tested.
