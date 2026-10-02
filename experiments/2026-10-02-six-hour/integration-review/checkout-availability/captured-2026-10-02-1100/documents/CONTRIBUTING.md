# Adding durable research knowledge

This is a knowledge repository with manually run research code. It has no CI/CD or deployment configuration.

## Before starting

Read the [registry](knowledge/experiments/registry.json), the relevant [retrospective](knowledge/retrospectives/README.md) and the linked paper methods. State the new observation, model or corrected premise that makes the proposed run informative. The registry's `retry_when` field identifies useful reasons to revisit earlier failures.

Choose the next unused experiment ID and a dated directory under `experiments/`. Copy the [experiment template](templates/EXPERIMENT.md), then record the target, inputs, selection rule, controls, outcomes and stopping conditions. State whether the work is a proposal, simulation, source replication, exploratory refinement or frozen evaluation. Keep its graphic, functional, numerical or linguistic target explicit.

## During a run

1. Preserve source identity, physical-object aliases, all available faces and uncertain cases. Record how the analytical representation was made from the source observations.
2. Keep source observations, proposed interpretations and evaluator answers in distinct inputs. Describe exactly what the fitted model and any acquisition selector receive.
3. Save commands, seeds, code/helper snapshots, source hashes and environment versions. A copied helper needs its own hash in the run record.
4. Write each run or repair to a new endpoint. Retain earlier results and identify the defect or premise changed by the repair.
5. Check the computation with an appropriate independent implementation, exact certificate or source inspection. Report the independent unit and keep repeated conditions together when calculating uncertainty.
6. Record the observable approach, challenges, fixes and outcomes in a retrospective. Link each conclusion to exact outputs and source coordinates.

Raw acquired sources and detailed unresolved-rights derivatives remain local under the [redistribution record](knowledge/provenance/REDISTRIBUTION.md). Track our code, prose, protocols, generated controls, aggregate results and acquisition manifests. Review payload contents as well as extensions.

## Parallel assignments and writing

Assign each contributor distinct owned paths. Tell them that others share the workspace and that their implementation must accommodate those changes. Include this requirement in every assignment:

> Maximize reader comprehension. Explain the idea directly in connected prose, keep necessary shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the argument. Read `knowledge/editorial/WRITING.md` before writing. Preserve exact source titles and frozen evidence wording.

The integrating contributor reviews returned prose, numbers, links and source scope. Describe the result early, followed by the method and evidence needed to assess it. Necessary limitations belong together with the affected claim or shared methods premises.

## After completion

Update the registry, index and claim-evidence maps. Give each failure a concrete retry input. Run `python tools/verify_knowledge_repo.py` for repository links and paths, plus the analysis-specific checks required by the change. Inspect the proposed Git payload before pushing completed private research contents.

Use the next unused numbered directory under `papers/` for a new manuscript. Keep its draft status, contribution, source access and exact evidence map visible. Future public release or external submission requires the user's decision and the recorded source-specific packaging review.
