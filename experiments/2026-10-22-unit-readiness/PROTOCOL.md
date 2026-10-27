# UNIT-READINESS-01: data needed to test reusable inscription units

Date: 22 October 2026. Status class: source-review. Target: graphic boundaries and recurring units. Contributor: OpenAI Codex agent, GPT-6 family, Codex desktop collaboration harness; the exact served model identifier is not exposed to this agent.

We will make the missing evidence for a new unit test explicit and executable. This run audits existing metadata and the availability of labels. It acquires no source images, views no candidate new inscription and estimates no new segmentation effect. The earlier plate audit and scores remain unchanged.

## Inputs and selection

We use all 118 rows of the 20 October divided-face audit, every row of the corrected 13 October image index, the normalized Lipi face metadata, and all 503 rows of the 21 October post-catalogue inventory. We inventory the already held readable-script controls and inspect their existing sampling code. Source hashes identify each dependency. We read the shared spending ledger and the earlier segmentation spending proposal. Every post-catalogue row retains its source identity, uncertain matches and possible duplicates. An absent match never establishes a new physical object or an unexamined inscription.

The object-register agent supplies an optional metadata-only interface at `data/raw/2026-10-22-object-register/run-v1/`: `objects.jsonl` and `faces.jsonl`, with `LIPI:` object and face identifiers. We check the availability and consistency of that interface without requiring a final physical-identity adjudication.

## Outputs and stopping rules

Before computing coverage, we specify these outputs: an ordered local queue for missing divided-face crops and unresolved layout labels; an object-level queue for uncertain image-side assignments; a post-catalogue identity and exposure checklist; an inventory of complete and partial boundary labels; and a machine-readable aggregate readiness decision. Detailed rows stay under `data/raw/2026-10-22-unit-readiness/`. Code, aggregate counts, source hashes and our protocol remain tracked. Outputs refuse to replace an existing path.

Queue priority follows evidence needs. Correct known image-identity problems and adjudicate existing ambiguous layout labels first; acquire missing divided-face crops next; resolve the wider image-side queue and post-catalogue identities in parallel. A priority is a work order, not a claim that a case is informative for the model. We retain all rows, including cases unsuitable for the current clean right-to-left model.

A new confirmation cohort is blocked unless every selected object has positive documentation of its exposure history, a reviewed alias graph, all related faces, a frozen text-dependence graph and a complete list of participants. Existing export records remain historically examined or exposure-unreviewed. We do not create a new shots split or open confirmation in this audit.

## Computation checks

The shared task is `python -m bench segmentation --synthetic`. We also exercise `bench shots --synthetic` in this package. Expected scorer behavior is complete-boundary precision, recall and F1, with required-line recall and null precision/F1 for partial labels. Synthetic shots must reject premature or changed confirmation reads and respect spending. These controls test procedures; they provide no Indus evidence.

The audit checks unique source row keys, source-face joins, all 118 plate rows, conservation of priority queues and the distinction between face-side links and other-side or unassigned links. A register check fails on duplicate IDs, missing parent objects or malformed source IDs. A missing register is reported as pending, allowing the held-source audit to finish. No benchmark implementation is edited.

## Next study, after the data gates

Two independent readers will record image identity, surface, mirror transform, sign locations, line and spatial groups, damage, and confidence without seeing a proposed model boundary. They will distinguish a visible line division from a linguistic word division. A third reader will adjudicate disagreements with source coordinates and a retained disagreement history. The training set may use confirmed physical divisions. Complete word divisions are available only in the readable-script controls and require verified source tokenization.

We will compare a frozen unit model with branching entropy, frequent-fragment segmentation, a Dirichlet-process model, layout-only prediction, and cutting everywhere or nowhere. Models receive the same discovery records. Hyperparameters and any unit inventory are selected entirely within discovery groups. Physical aliases and repeated complete texts remain together; connected groups are formed from the full source register before exclusions. Source blocks are held out as an additional transfer test. A source-specific failure remains visible even if the pooled average passes.

For readable controls, the primary measure is boundary F1 on complete labels. The preregistration will require a paired gain over the strongest discovery-selected baseline with the lower 95% group-bootstrap bound above zero in at least three of the four existing readable cohorts, and no cohort with an upper bound below zero. Exact-word span F1 is secondary. Failure stops a general word-segmentation claim. Before any confirmation read, simulations on discovery and generated data must show at least 80% power for an absolute F1 gain of 0.05; otherwise we acquire more independent groups or state the test is underpowered.

For Indus partial labels, the primary measure is required-division recall minus cut rate at other positions, reported with both components. The latter positions are unlabelled. A claim that units explain physical divisions requires a positive paired gain over the strongest frozen baseline, a lower 95% group-bootstrap bound above zero, and a one-sided randomization p-value at most 0.025. The reference reallocates the observed number of line divisions within texts matched by length and layout; each replicate repeats all fitting and selection. If layout groups cannot support exchangeability, the test is blocked. No precision or word-boundary F1 is estimated from partial labels.

The reusable-unit prediction is separate: units learned on discovery must recur in frozen held objects beyond length-, site-, type- and position-matched rearrangements, with an effect threshold chosen from discovery power simulations before the freeze. These are prospective rules awaiting a cohort and a complete specification. A future PREDICTIONS.json must name all statistic families, exact exchangeability groups, seeds, eligibility decisions, baselines, multiplicity handling and the joint credence rule for shared objects. The shots loader must freeze every registered participant and artifact before the first confirmation read.
