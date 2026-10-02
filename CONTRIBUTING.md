# Adding durable research knowledge

This is a knowledge repository. Do not add CI/CD, deployment configuration or workflows.

1. Search `knowledge/experiments/registry.json`, `knowledge/retrospectives/`, `research/` and existing paper references before starting. Record why the new work is not a duplicate.
2. Copy the [experiment template](templates/EXPERIMENT.md) into `experiments/YYYY-MM-DD-short-name/`. Assign an ID, source snapshots, question, test, exclusions and failure conditions before looking at new outcomes where practical.
3. State whether the work is a proposal, simulation, exploratory analysis, frozen evaluation, failed test, source audit, or replication. State the level of inference: graphic, structural, functional, numerical, phonetic, lexical or historical.
4. Preserve physical-object aliases and source identity. A second drawing, catalogue label, face or transcription does not automatically create a new independent ancient object.
5. Keep observations separate from interpretations. Record uncertainty and unmapped cases. Do not silently merge inventory numbers, assume an erased section is one glyph, equate later iconography with an ancient word, or treat a plausible story as verification.
6. Keep old failed and superseded outcomes. A corrected run goes in a new directory with the defect, change and relationship recorded. Do not select the best endpoint across incompatible populations.
7. Save commands, seeds, source/code hashes, dependencies and exact result paths. Write a short challenges-and-remedies account grounded in observable actions and outputs. Do not reconstruct unrecorded intentions as facts.
8. Update the registry, knowledge index and claim-evidence maps. Add the future experiment to the roadmap with a stopping condition and required new evidence.
9. Add primary citations for factual claims. Community suggestions are attributed hypotheses. Check that a claimed novelty is not already in the literature.
10. Run the relevant manual checks. Use `python tools/verify_knowledge_repo.py` for repository integrity; run analysis-specific checks only when the changed analysis requires them.

Use `papers/002-descriptive-title/` for a genuinely new manuscript. Keep draft status, unresolved claims, contribution declarations and references visible. Public release should occur only after an explicit decision and the documented source-specific review.
