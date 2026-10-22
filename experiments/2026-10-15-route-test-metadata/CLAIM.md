# Claim text for the Q-0009 issue (not posted)

The repository had no GitHub issues on 15 October 2026, so there was no issue for Q-0009 to check or comment on. This is the text for a new issue opened with the "Claim a question" form (`.github/ISSUE_TEMPLATE/claim-question.yml`). It was prepared for the route test and not posted.

**Title:** [Q-0009] Claim: check the empty motif values on seals against the CISI photographs

**Question ID and card**

Q-0009, `knowledge/questions/Q-0009-distinguish-missing-motif-from-no-motif.md`

**Planned work and owned paths**

A pilot on seals: count every motif label in the pinned Lipi export by object type, draw a fixed hash-ordered sample of seal faces in six strata (square and rectangular seals marked `None`, square and unshaped seals marked `-`, all `?` and `Unknown`, and four controls with a named motif), read each face's CISI crop as motif present, absent or not decidable, and write a versioned mapping from label and seal type to a value status. Inputs are local-only (`data/normalized/lipi_observed_faces.jsonl`, `data/lipi/public/seal_images/`) and the tracked face-image index of 13 October. Owned paths: `experiments/2026-10-15-route-test-metadata/` and `knowledge/registry/attempts/ATTEMPT-0001.json`. Deliverable: the mapping, the coverage change for `symbol` on seals, and proposed updates to DATA.md, the manifest and the Q-0009 card. Expected update: 16 October 2026.

**Contributor or agent details**

Agent: Claude Code (Claude Opus 5.5), Claude desktop app, working for the repository maintainer.
