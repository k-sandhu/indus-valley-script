# Contributing research and data

This is a knowledge repository with manually run research code. It has no CI/CD or deployment configuration. Begin with [AGENTS.md](AGENTS.md), [data coverage](knowledge/DATA.md) and the [map](knowledge/MAP.md).

## Before starting

Read the [registry](knowledge/experiments/registry.json), the relevant [retrospective](knowledge/retrospectives/README.md) and the linked paper methods. State the new observation, model or corrected premise that makes the proposed run informative. The registry's `retry_when` field identifies useful reasons to revisit earlier failures.

Choose the next unused experiment ID and a new dated directory, `experiments/YYYY-MM-DD-short-slug/`. Copy the [experiment template](templates/EXPERIMENT.md), then record the target, inputs, selection rule, controls, outcomes and stopping conditions before outcomes. State whether the work is a proposal, simulation, source replication, exploratory refinement or frozen evaluation. Keep its graphic, functional, numerical or linguistic target explicit and use the [status classes](knowledge/registry/VOCABULARY.md).

Data contributions follow [knowledge/DATA.md](knowledge/DATA.md) and record sources, metadata fields and coverage changes in [data/MANIFEST.json](data/MANIFEST.json). Conjectures follow [their card rules](knowledge/conjectures/README.md) and the [two-stage design](experiments/2026-10-12-conjecture-shots/DESIGN.md).

## Files and claims for parallel work

A contribution adds files in its own new experiment directory plus its own card files. Contributors never edit generated [registry.json](knowledge/experiments/registry.json), [MAP.md](knowledge/MAP.md) or another contribution's files. Maintainers run `python tools/kb.py build` after merging. Propose any shared-document change in your own package so a maintainer can integrate it.

Registry entries are new files in [knowledge/registry/attempts/](knowledge/registry/attempts/). Findings, questions and conjectures are new cards; use [finding](templates/FINDING.md), [question](templates/QUESTION.md) and [conjecture](knowledge/conjectures/TEMPLATE.md) templates. A later pull request resolves an ID collision by taking the next free number. General question IDs are Q-0001–Q-0999; specific data acquisition cards use Q-1001 onward. Agents disclose model and harness in the registry entry or card `authors` field.

Claim work by opening or commenting on the GitHub issue for the question, with its Q-ID in the title. A claim lapses after seven days without an update. Record the claim in the card only when the work is merged; always check the issue before starting.

Assign each contributor distinct owned paths. Tell them that others share the workspace and that their implementation must accommodate those changes. Include this requirement in every assignment:

> Maximize reader comprehension. Explain the idea directly in connected prose, keep necessary shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the argument. Read `knowledge/editorial/WRITING.md` before writing. Preserve exact source titles and frozen evidence wording.

The integrating contributor reviews returned prose, numbers, links and source scope. Describe the result early, followed by the method and evidence needed to assess it. Necessary limitations belong together with the affected claim or shared methods premises. Follow the verbatim subagent requirement in [AGENTS.md](AGENTS.md).

## During a run

1. Preserve source identity, physical-object aliases, all available faces and uncertain cases. Record how the analytical representation was made from the source observations.
2. Keep source observations, proposed interpretations and evaluator answers in distinct inputs. Describe exactly what the fitted model and any acquisition selector receive.
3. Save commands, seeds, code/helper snapshots, source hashes and environment versions. A copied helper needs its own hash in the run record.
4. Write each run or repair to a new endpoint. Retain earlier results and identify the defect or premise changed by the repair.
5. Check the computation with an appropriate independent implementation, exact certificate or source inspection. Report the independent unit and keep repeated conditions together when calculating uncertainty.
6. Record the observable approach, challenges, fixes and outcomes in a retrospective. Link each conclusion to exact outputs and source coordinates.

Raw acquired sources and detailed unresolved-rights derivatives remain local under the [redistribution record](knowledge/provenance/REDISTRIBUTION.md). Track our code, prose, protocols, generated controls, aggregate results and acquisition manifests. Review payload contents as well as extensions. [REUSE.md](REUSE.md) states the current licence and publication status.

## Verification and completion

Result verification has four tiers: **submitted** records the author's result; **reproduced** means another contributor reran it from recorded inputs; **reviewed** means an adversarial review is recorded; **accepted** is the maintainer's decision. Verification is itself a contribution, done by someone other than the author, in its own dated directory. These tiers are separate from a finding's status class.

Before opening a pull request run `python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, `python tools/verify_knowledge_repo.py --output <your new verification path>` and the analysis-specific checks. Paste the `kb.py check` summary into the pull request. New cards and entries make the generated files stale: report that drift in the summary and leave generation to maintainers. Fix card, evidence and link errors in your owned files. Maintainers rebuild after merging and check the combined tree.

Add registry and card records, and propose index and claim-evidence-map updates for maintainer integration. Give each failure a concrete retry input. Inspect the proposed Git payload before pushing completed private research contents.

Use the next unused numbered directory under [papers/](papers/) for a new manuscript. Keep its draft status, contribution, source access and exact evidence map visible. Future public release or external submission requires the user's decision and the recorded source-specific packaging review.

## Licence of contributions

By opening a pull request you agree that your contribution is released under the repository's terms in [LICENSE](LICENSE): code under the [Unlicense](LICENSES/Unlicense.txt) and everything else under [CC0 1.0](LICENSES/CC0-1.0.txt). Do not submit third-party material you cannot release on those terms; record such sources in `knowledge/DATA.md` and keep them local as `knowledge/provenance/REDISTRIBUTION.md` describes.
