# Launch of directions 1, 2 and 7

Recorded 22 October 2026 before this run's builds and repairs. Contributors: Codex (GPT-6, desktop harness), with three parallel worker agents. This is a data and tooling contribution. It does not register or score a new linguistic prediction.

We begin by joining the evidence already held into an object register. Two parallel streams identify and repair the inputs needed to test reusable inscription units and competing readings. The register is their shared source of physical identities, faces, evidence and missingness. Each stream owns a separate dated package.

## Work and acceptance gates

| Direction | First execution block | Acceptance gate | Owned package |
|---|---|---|---|
| 1. Object register | Extend schema v2 to the full held population; attach source-qualified identifiers, face images and metadata assertions; retain conflicts and uncertain joins. | One command rebuilds every base record into a new local output; schema and relational checks pass; coverage differences from the inventory are explained. Every omitted source adapter is named. | `experiments/2026-10-22-object-register/` |
| 2. Reusable inscription units | Audit every catalogued divided face and the available layout labels; generate an acquisition and adjudication queue; inventory readable-script boundary controls. | Every divided face has an evidence disposition. Positive line-break labels and complete word-boundary labels have separate scoring contracts. Synthetic scorer checks pass; real evaluation blockers are explicit. | `experiments/2026-10-22-unit-readiness/` |
| 7. Common evaluation of readings | Trace lexical matching and dictionary-parsing defects; implement conservative matching repairs and tests; specify comparable participant inputs and controls. | Exact matching and ambiguous forms are tested; unresolved dictionary evidence is identified; relevant synthetic bench runs pass. A participant contract fixes the allowed choices and predictions before any new confirmation read. | `experiments/2026-10-22-reading-eval-readiness/` |

The coordinating contributor owns this launch package, the new Q-0039 card and its coordination registry entry. Workers own their packages, their local `data/raw/2026-10-22-.../` directories and one new attempt record each. Existing plans, frozen results, shared bench code, generated knowledge files and unrelated working changes remain intact. GitHub claims follow Q-1030, Q-0027 and Q-0039. Q-1031 remains a dependency; this launch does not claim to finish all 881 side assignments.

## Shared register interface

The first build writes `data/raw/2026-10-22-object-register/run-v1/register-v2.json`, validated with the pilot's schema v2, plus local `objects.jsonl`, `faces.jsonl` and `assertion-values.jsonl`. The base object key is `LIPI:` plus the source family ID; a face key is `LIPI:` plus its record ID. These are provisional physical families. Confirmed physical identity links and repeated-text dependence are distinct relations.

The exports retain source aliases, raw and normalized values, assertion status, missing-value reasons, source hashes, join status and face-specific image evidence. Exposure starts as `unreviewed`. A missing record in a spending log does not establish that an object is unexamined. The two downstream streams can work from held inputs while the register is built, then check their joins against its exports.

## Dependency order

1. **This run:** freeze the implementation scope; build the register and the two blocker inventories in parallel; repair deterministic lexical matching; run synthetic controls and package checks.
2. **Integrate held evidence:** reconcile register coverage with the dated inventories; attach source locators to remaining claims; join unit-study queue records to the register. Preserve every disputed value and explain source-specific exclusions.
3. **Close source gaps:** work first through existing photographs and catalogue captions, then obtain missing CISI 3 plates and the exact post-catalogue reports identified by the queues. Reconcile candidates to the full identity graph before treating them as additional objects. Resolve compound parses against dictionary pages and obtain specialist review where lexical or epigraphic judgment is needed.
4. **Qualify evaluation cohorts:** document each candidate's provenance and prior exposure. Freeze object and repeated-text groups, the eligible source blocks, participant list and all discovery/confirmation rules. Discovery work can proceed on historically examined data; confirmation requires a defensible unexamined population.
5. **Run the substantive tests:** units must predict independently adjudicated layout and transfer on readable scripts; each reading must beat its prespecified controls on predictions it did not help select. Use the shared bench and shots loader, preserve failed predictions and record statistic-family spending.

Blocks 1 and 2 are the present execution scope. Later blocks depend on the measured source gaps. Source acquisition requiring contact, purchases or unavailable institutional access remains a named dependency; no contact or publication is part of this run.

## Decisions fixed before results

The base completeness target is all 4,695 held provisional object families and 5,680 faces. The historical baselines of 4,075 objects with a CISI reference and 3,598 with a usable dimension must either reproduce under the same definitions or have a documented reason for their difference. A full base population alone does not complete Q-1030: the adapter inventory must show which held sources have been integrated.

For direction 2, the existing 118 divided faces and the 75-face plate audit define an accounting check, not an independent new sample. The inherited segmentation model and its frozen prospective predictions stay fixed. Any model redesign uses a separately recorded discovery protocol. Word-boundary precision and F1 require complete word labels; an obligatory line-break reference supports its declared break-recall and extra-cut measurements.

For direction 7, we repair input matching before comparing readings. Synthetic known-answer checks establish that the implementation detects a planted answer under its own assumptions. Publication-level validation additionally needs real known-script controls and comparable freedom across proposals. A repaired score on examined material is a retrospective result.

The decision after this run is whether each next step has usable inputs, passes implementation checks and has a named owner and stopping condition. No new archaeological or linguistic claim follows merely from passing a data validator.

## Evidence and handling

Starting sources are [DATA](../../knowledge/DATA.md), the [source manifest](../../data/MANIFEST.json), [Q-1030](../../knowledge/questions/Q-1030-object-register-build.md), the [object pilot](../2026-10-07-object-ledger/README.md), the [seal-unit study](../2026-10-20-seal-legend-units/REPORT.md), the [novelty review](../2026-10-22-field-novelty-review/REPORT.md), the [shared bench](../../bench/README.md) and its [spending ledger](../../bench/spent.json). The prior registry and corpus, methods and published-claim retrospectives define the failed paths and retry conditions.

Detailed source-derived records stay under ignored `data/` paths. Tracked files contain our code, protocols, source pointers and hashes, aggregate outputs, validation and proposed inventory updates. Each package records the exact inputs it used and writes a retrospective. Maintainers integrate shared inventory and generated-map changes after review.

The strongest claim this launch can establish is that our held evidence can support reproducible, explicitly bounded tests. The deciding evidence is a complete accounting of the input population, source joins and unresolved cases, followed by independent known-answer and prospective checks.
