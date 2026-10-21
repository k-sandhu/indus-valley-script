# Retrospective: seal-legend units, 20 October 2026

The package was built in one session by Claude Opus 5.5 in Claude Code, working as a side session of the project's main session in the shared checkout, with five subagents. This record covers what was done, what went wrong and how it was repaired, in the order it happened.

## Approach

We read the orientation files, the prior segmentation code and the bench, and found that line divisions are positive labels only: cutting everywhere finds every division, so recall alone could not show a margin over it. We chose J, recall at the divisions minus the cut rate elsewhere, on which cutting everywhere, cutting nowhere and random cutting all score zero, and a conditional-logit model of a scribe choosing one break position, with a layout term to absorb where lines end. Corpus statistics leave out each scored text's group of related objects. The Ur III seal records keep ORACC line numbers, which let the same model be trained on line divisions alone in a script whose words are known.

The plate audit went to three subagents with a written brief, in parallel with writing the code. The protocol was hashed before the audit verdicts arrived and before any scoring. The readers took 40 to 65 minutes each. Two of them reported early that the code's first segment was almost always the lower line, which the third then qualified with six upper-line cases. We traced the pattern to the export: its reading-order field is the exact reversal of its visual code on all 118 divided faces.

## Problems and repairs

- **Testing without seeing outcomes.** To debug `run_cv.py` before the audit was complete, we ran it in the scratchpad on faces whose divisions were moved to random positions. It ran end to end, the supervised J came out at 0.04 to 0.08, and the worse-order set came out at −0.19. That showed the worse-order set is biased below zero under the null, which matters for reading the table in REPORT.md section 2. The test also exposed a path helper that failed outside the repository, fixed before the real run.
- **Directory collision.** The Ur III calibration, run first, created the raw run directory that `run_cv.py` also tried to create. We moved the Indus raw files to a subdirectory before the real run.
- **Editing a module during a run.** `held_components` was added to `legend_units.py` while the calibration was running. The functions the calibration used did not change, and the frozen hashes are of the final file.
- **A degenerate inventory.** The protocol's inventory rule cut only 4.5% of positions in single-line texts and gave a closing stock of one formula. The Ur III calibration had already shown why: a threshold learned from line divisions keeps the strongest boundary of a text and little else. [Amendment 1](AMENDMENT-1.md) added the model's highest-scoring position as the junction. We kept version 1 and its hashes, looked only at the build corpus before choosing, and tried no other variant.
- **Divided legends.** The held-set calibration showed that only 6 of 32 divided faces, joined top line first, ended in a stock formula. Inspection showed why: their top line ends in the closing formula and the short second line follows. [Amendment 2](AMENDMENT-2.md) scored divided legends separately, before any prediction was hashed. It also dropped a draft statistic, the share of closings among the ten commonest, which had no power.
- **Agreement bookkeeping.** The agreement script recorded the hash of RULES.md (version 1) where the agent had used RULES-v2.md. Its internal comparison also first used the version 1 definition of the model's cuts. We fixed the hash in the code, kept the outputs as written, and recorded the version 2 comparison in a second file.
- **Line endings.** Edits made through Python wrote Windows line endings into `PROTOCOL.md` and `run_cv.py`. The protocol hash is of that file as it stands, so it was left alone; the files written afterwards use LF.
- **Shared ledger.** `bench/spent.json` shows a change in the working tree from another session's fish-context shot. This package did not edit it and proposes its own entry in [spent-entry.json](spent-entry.json).

## What we would do differently

Choose the inventory rule on the readable script before freezing the protocol. The calibration showed the threshold's behaviour hours before the inventory was built, and an amendment would then have been unnecessary. Measure the reading-order question on a few faces before writing the protocol, so that the plate order and the catalogue's reading order could be one reference set. Write subagent output folders inside the package's raw directory from the start; the plate readers shared a scratchpad and one overwrote another's crop script.

## Outcome

The segmenter passed both pre-stated rules on held-out divisions (J = 0.718 against 0.348 for the Dirichlet process). The readable calibration passed narrowly. The rules reached complete agreement with an independent agent, and four predictions are hashed with their power. Nothing in the fresh pools has been read.
