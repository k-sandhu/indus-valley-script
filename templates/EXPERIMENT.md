# EXP-ID: descriptive question

Status class: choose from `knowledge/registry/VOCABULARY.md`.

Date and contributors (agents disclose model and harness):

Owned directory: `experiments/YYYY-MM-DD-short-slug/`. Create your registry entry in `knowledge/registry/attempts/<ID>.json`; maintainers regenerate the registry and map after merging. Claim a question through its issue and use new card files for your contribution.

Data dependencies and gaps: read `knowledge/DATA.md`; record source, metadata and coverage changes there and in `data/MANIFEST.json` under the data contribution rules.

## Why this is new work

Closest registry entries and prior publications; new evidence or changed assumption that justifies the run.

## Observation and competing explanations

Source-grounded observation; hypotheses and the inference level being tested.

Local storage: read [LOCAL_STORAGE.md](../LOCAL_STORAGE.md). On this workstation raw inputs live at `D:\projects\indus_valley_script\data\raw\YYYY-MM-DD-slug\`; record their logical checkout paths, physical paths and hashes.

## Inputs and dependence

URLs, version/commit, hashes, inventory, physical aliases, date/context uncertainty, exclusions and missing cases; source terms and local-only inputs.

## Protocol before outcome

Estimand, split/group rule, baselines, sampling/masking law, tuning, null/negative controls, success and failure conditions, budget and stopping rule.

## Commands and outputs

Code/environment snapshot, command, seed, exact output paths and verification results.

## Results and scope

All relevant endpoints, uncertainty, exploratory deviations, conditional assumptions and limits. Separate prediction from interpretation.

## Challenges, failed paths and remedies

Observable errors, what changed, what remained unresolved; references to preserved superseded outputs.

## Decision and next evidence

What is now ruled out or supported within this protocol, what should not be rerun unchanged, and which new evidence would justify a revisit.

End with the boldest reading supported by this result and the test that would decide it. Working meanings and functions belong in conjecture cards, with a credence, predictions and kill condition. Use `experiments/2026-10-12-conjecture-shots/DESIGN.md` for a conjecture test.

## Review and verification

Record submitted, reproduced, reviewed and accepted tiers separately from status class. Another contributor records reproduction or adversarial review in their own dated package. Run `python tools/kb.py check`, `python tools/review_prose.py --path <your directory> --no-write`, repository integrity checks and the analysis-specific checks. Preserve commands, summaries and unresolved omissions.
