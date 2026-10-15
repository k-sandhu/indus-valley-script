# Contributing research and data

This is a knowledge repository whose research code is run by hand. The project has no CI/CD or deployment configuration, and none should be added. Begin with [AGENTS.md](AGENTS.md), [data coverage](knowledge/DATA.md) and the [map](knowledge/MAP.md).

## Before starting

Read the [registry](knowledge/experiments/registry.json) of earlier attempts, the relevant [retrospective](knowledge/retrospectives/README.md) and the linked paper methods. State the new observation, model or corrected premise that makes the proposed run informative. The registry's `retry_when` field records what would justify revisiting an earlier failure.

Choose the next unused experiment ID and a new dated directory, `experiments/YYYY-MM-DD-short-slug/`. Copy the [experiment template](templates/EXPERIMENT.md) and, before seeing any outcome, record the target, inputs, selection rule, controls, outcome measures and stopping conditions. State whether the work is a proposal, a simulation, a source replication, an exploratory refinement or a frozen evaluation. Say explicitly whether its target is graphic, functional, numerical or linguistic, and use the [status classes](knowledge/registry/VOCABULARY.md).

Data contributions follow [knowledge/DATA.md](knowledge/DATA.md). Record new sources, metadata fields and coverage changes in your own package, using the fields of [data/MANIFEST.json](data/MANIFEST.json); maintainers fold them into the manifest and `knowledge/DATA.md` after merging. Conjectures follow [their card rules](knowledge/conjectures/README.md) and the [two-stage design](experiments/2026-10-12-conjecture-shots/DESIGN.md).

When recording a protocol, choose the relevant task of the [shared evaluation harness](bench/README.md) (`bench/`). Every submitted reading, sign key, meaning map or conjecture attaches the JSON output of its bench run and its frozen specification. Restoration and segmentation proposals attach scorer outputs and their declared comparisons. The evidence record also keeps the hashes of inputs and code, the data used to construct the proposal, whether the scored population was fresh (not examined in earlier tests), and any failed predictions.

## Files and claims for parallel work

A contribution adds files in its own new experiment directory plus its own card files. Contributors never edit the generated [registry.json](knowledge/experiments/registry.json) or [MAP.md](knowledge/MAP.md), or another contribution's files. Maintainers run `python tools/kb.py build` after merging. Propose any change to a shared document inside your own package (your experiment directory) so a maintainer can integrate it.

Registry entries are new files in [knowledge/registry/attempts/](knowledge/registry/attempts/). Findings, questions and conjectures are new cards; use the [finding](templates/FINDING.md), [question](templates/QUESTION.md) and [conjecture](knowledge/conjectures/TEMPLATE.md) templates. If two pull requests take the same ID, the later one takes the next free number. General question IDs are Q-0001–Q-0999; specific data acquisition cards use Q-1001 onward. An AI agent discloses its model and harness in the `authors` field of the registry entry or card.

Claim work by opening or commenting on the GitHub issue for the question, with its Q-ID in the title. A claim lapses after seven days without an update. Always check the issue before starting; the claim is recorded in the card only when the work is merged.

When you assign work to several contributors, give each one distinct paths to own, and tell them that others share the workspace and that their work must accommodate the others' changes. Include this requirement in every assignment:

> Maximize reader comprehension. Explain the idea directly in connected prose, keep necessary shared assumptions together, and avoid repeated corrective comparisons or warnings that interrupt the argument. Read `knowledge/editorial/WRITING.md` before writing. Preserve exact source titles and frozen evidence wording.

The contributor who integrates the returned work reviews its prose, numbers, links and source scope. In any write-up, describe the result early, followed by the method and evidence needed to assess it, and put each necessary limitation with the claim it affects or with the shared methods premises. Subagent assignments carry the requirement in [AGENTS.md](AGENTS.md) verbatim.

## During a run

1. Preserve the identity of each source, the aliases of each physical object, every available face (inscribed side) and every uncertain case. Record how the data you analyse were made from the source observations.
2. Keep source observations, proposed interpretations and evaluator answers in separate inputs. Describe exactly what the fitted model and any acquisition selector receive.
3. Save commands, seeds, snapshots of code and helper scripts, source hashes and environment versions. A copied helper needs its own hash in the run record.
4. Write each run or repair to a new endpoint, an output location that is never overwritten. Keep earlier results, and identify the defect or premise that the repair changes.
5. Check the computation with an independent implementation, an exact certificate or an inspection of the source, whichever fits. When calculating uncertainty, report the independent unit (the unit treated as one independent observation) and keep repeated conditions together.
6. Record the observable approach, challenges, fixes and outcomes in a retrospective. Link each conclusion to exact outputs and source coordinates.

Raw acquired sources, and detailed derivatives of sources whose rights are unresolved, stay local as the [redistribution record](knowledge/provenance/REDISTRIBUTION.md) requires. Track in Git our code, prose, protocols, generated controls, aggregate results and acquisition manifests. When reviewing what a commit will publish, check file contents as well as extensions. [REUSE.md](REUSE.md) states the current licence and publication status.

## Verification and completion

Result verification has four tiers: `submitted` records the author's result; `reproduced` means another contributor reran it from recorded inputs; `reviewed` means an adversarial review is recorded; `accepted` is the maintainer's decision. Verification is itself a contribution, made by someone other than the author in its own dated directory. These tiers are separate from a finding's status class.

Before opening a pull request, run `python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, `python tools/verify_knowledge_repo.py --output <your new verification path>` and the checks specific to your analysis. Paste the `kb.py check` summary into the pull request. New cards and entries leave the generated files out of date; `check` lists them as maintainer notes and still passes, and regeneration is left to maintainers. Fix card, evidence and link errors in your own files. Maintainers rebuild after merging and check the combined tree with `python tools/kb.py check --strict`.

A change to the shared harness also requires a run of `python -m bench selftest` into a new dated output file. A contributor who changes a scorer reproduces the pinned source result that the scorer was built to match, and records any difference in population or definition. Bench outputs and freeze records go into the attempt's `evidence`; maintainers integrate cards and rebuild the knowledge map after review.

Add registry and card records, and propose updates to the index and the claim-evidence maps for maintainers to integrate. Give each failure a concrete input that would justify a retry. Before pushing completed private research contents, inspect the proposed Git payload, the set of files the push would add.

Use the next unused numbered directory under [papers/](papers/) for a new manuscript. Keep its draft status, contribution, source access and exact claim-evidence map visible. Future public release or external submission requires a maintainer decision and the recorded source-specific packaging review.

## Licence of contributions

By opening a pull request you agree that your contribution is released under the repository's terms in [LICENSE](LICENSE): code under the [Unlicense](LICENSES/Unlicense.txt), material derived from the 1979 Helsinki edition under [CC BY 4.0](LICENSES/CC-BY-4.0.txt) with its attribution, and everything else under [CC0 1.0](LICENSES/CC0-1.0.txt). Do not submit third-party material you cannot release on those terms; record such sources in `knowledge/DATA.md` and keep them local as `knowledge/provenance/REDISTRIBUTION.md` describes.
