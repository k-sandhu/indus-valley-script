# Validation record

The saved segmentation scorer was replayed with the original reference and prediction files. The JSON equals the original endpoint, and all eight recorded provenance hashes match the files on disk. The replay establishes computational scoring consistency. It does not retrain the predictor or adjudicate physical boundaries.

`python tools/kb.py check` passed with 539 items, zero errors and zero warnings. Its two maintainer notes concern generated registry and map files awaiting the normal maintainer rebuild.

`python tools/verify_knowledge_repo.py --output experiments/2026-10-22-field-novelty-review/repository-verification.json` failed with 58 existing link errors outside this package. The saved output lists them. It reported no error in this review package. Those unrelated source files were preserved.

The prose scan was reviewed. Slashes in the original protocol and literal file paths are retained. Slash constructions in the new report were rewritten. Source titles and frozen evidence were preserved. Direct checks found that the readable-script comparison's 0.557 baseline means cutting everywhere; the report now also gives the stronger branching-entropy result, 0.692, alongside the proposed model's 0.618.

Changed paths are confined to this experiment directory and knowledge/registry/attempts/FIELD-NOVELTY-REVIEW-2026-10-22.json. Existing experiment results, shared spending ledgers, manuscript drafts and generated indexes were not edited.
