# Repository restructure, phase 1

Started 12 October 2026; verification continued on 13 October. This package adds a navigation and contribution layer to the existing working tree. It changes no research endpoint, manuscript, source witness or acquired corpus. The coordinator reviews the tree before committing.

## Approach and preserved content

The first edit was [PLAN.md](PLAN.md). Local snapshots of the working registry, README, INDEX and tracked/nonignored file hashes were saved under `data/raw/2026-10-12-repo-restructure/`. The earlier uncommitted content supplied the baseline. Git reads used a per-command ownership exception; no Git settings, history, index or repository visibility were changed.

Each of the 165 registry entries was read through its status, question and outcome, then assigned a primary area and status class in [classification-decisions.json](classification-decisions.json). [STATUS-MAPPING.md](../../knowledge/registry/STATUS-MAPPING.md) explains every decision. The original fields remain in individual entry files. The standard-library CLI generates the registry in its original order and adds new entries after those by ID.

The finding layer contains 33 cards. [finding-number-audit.json](finding-number-audit.json) checks 87 scalar source fields and records derived count checks. Display precision follows the retained reports. Original-root measurements use the UTC dates recorded in the work log; later cards use their dated package endpoints. The sealings card uses the review recount of 13 of 16, because the original summary’s other-site count was corrected. Source paths and JSON fields remain visible in each card.

The question layer adds 38 general cards, including 12 starter tasks. Object identity, complete faces, metadata availability, source joins, images and dating receive priority 1 or 2. Questions about held witnesses and analytical checks remain separate from the other contributor’s external acquisition cards numbered Q-1001 onward. Seven short skills route contributors to the rules; four issue forms record claims, data corrections, result errors and conjectures.

The human README links ten measured results and the six manuscript drafts. [TIMELINE.md](../../knowledge/TIMELINE.md) retains every former README section, grouped by date, with only relative link prefixes changed. [readme-link-map.json](readme-link-map.json) accounts for all 62 old link occurrences. [index-preservation.json](index-preservation.json) checks that INDEX’s earlier bytes remain intact after one added paragraph. The [llms.txt format](https://llmstxt.org/) was checked against its published H1, blockquote and file-list structure.

## Problems and fixes

The Windows system encoding could not read a Unicode registry with the default Python encoding. Authoring and verification commands use explicit UTF-8, and the CLI configures redirected output as UTF-8. Long repository paths use the same extended-path convention as the preserved repository verifier.

Registry status strings often mixed endpoint timing, computation checks and subject matter. Classification follows the primary endpoint and keeps the original wording. Frozen tests with exploratory additions retain that distinction in their mapping reasons. Checked simulations remain synthetic; source censuses are source reviews.

Historical integrated package entries lack the added classification fields. The adapted registration tool accepts an identical existing subset as a no-op and refuses a conflicting value. It validates a whole supplied batch before creating new entry files, then calls the build.

Two temporary bytecode files created while authoring were removed from the locations where this run created them. Subsequent commands use `-B`; the earlier `review_prose` cache remains untouched. No pre-existing repository file was removed or moved.

The data contributor was writing DATA, the manifest and Q-1001 onward during verification. Their incomplete cross-references were reported without edits to those paths. The generated map reads the shared working tree, so newly added cards can require another maintainer build. Contributors report expected generated-file drift in their pull-request check summary; maintainers build and check the combined tree after merging.

The preserved public-checkout verifier checks the current Git index. New files in this phase are deliberately untracked for coordinator review, so index availability errors must be assessed alongside the working-tree verification and the knowledge-base check. No files were staged to make that check pass.

## Verification record

The [registry preservation report](registry-preservation.json) proves equality of the IDs, order, top-level metadata and every original field for all 165 entries. [Timeline preservation](timeline-preservation.json) checks the inherited section wording. Eight isolated CLI behavior tests cover parsing, discovery, generation, ID ranges, registration and both positive and negative validation cases.

Final command outputs, build hashes, knowledge-base validation, repository availability checks, skill validation, issue-form validation, prose review and file-preservation results are recorded in this directory. [CHANGES.json](CHANGES.json) inventories every durable path written by this run, including local baseline snapshots.

The recorded second build changed no bytes. All eight CLI tests, seven skill validations and five issue YAML files passed. After the data contributor completed the remaining references, the [final knowledge-base check](kb-check-final.json) passed with 438 items, zero errors and 12 reviewed local-only targets. The [final prose scan](prose-review-final.json) checked 125 files with no flags. The earlier check is preserved with its six then-unfinished data references.

[verification-error-review.json](verification-error-review.json) classifies the public verifier’s 316 errors: 270 pre-existing untracked/local targets, 33 new-layer files awaiting selection and 13 concurrent/local targets. The initial working-tree verifier reported 26 missing targets outside this run’s ownership and one legacy rule rejecting the authorized `data/MANIFEST.json`; the subsequent data completion resolved its source-register link. The [final working-tree verification](repository-working-tree-final.json) retains 25 earlier missing targets and that one legacy rule. The rule requires a separate maintainer-reviewed change to the verifier, which this phase cannot edit.

The baseline hash comparison covers 18,871 tracked and then-untracked nonignored files, with zero missing files. It excludes acquired local corpora and runtime caches. Three pre-existing paths changed concurrently outside this run’s ownership: `.gitignore`, the conjecture shot’s `shot-a-rank/seal_table.py` and `knowledge/conjectures/README.md`. They were left to their owners. The final hash record and check outputs preserve any later changes separately.

## Coordinator review

Review the primary-endpoint classifications for mixed studies, particularly failed frozen image tests, source census syntheses and the Bronze Age controls. Review the finding cards against their numeric audit, including UTC measurement dates and the corrected sealing counts. Review question priorities and the boundary between held-source verification and the acquisition cards. Confirm the contributor convention for reporting generated-file drift and assess the Git-index verification errors after selecting the intended new payload. Review the verifier’s manifest exception and earlier studies’ unresolved links before recording an overall repository pass.

The new route is AGENTS, then the map or CLI, then a card and its experiment package. An independent contributor should test that route on one metadata task and one reproduction task, record any missing prerequisite and propose the correction in an owned package.
