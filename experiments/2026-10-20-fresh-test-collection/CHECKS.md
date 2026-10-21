# Verification record

The author checks reconcile all 36 candidate rows and verify a stable report hash, source coordinates and an image locator for every row. The frozen payload check verified 88 local files, found no hash differences and found no unlisted payload files. The local hash manifest excludes itself; the reservation manifest anchors its hash.

`python tools/review_prose.py --path experiments/2026-10-20-fresh-test-collection --no-write` scanned four prose files and reported no flags. `python tools/kb.py check` failed on an unrelated missing H912 retrospective and a duplicate C-0010 card ID. It also noted that generated registry and MAP files need a maintainer rebuild. This contribution leaves generated files untouched.

`python tools/verify_knowledge_repo.py --output experiments/2026-10-20-fresh-test-collection/repository-verification.json` failed on repository-wide links outside this package; its exact output is preserved. Neither repository-wide check establishes archaeological eligibility. The acquisition and hash checks pass; independent identity and script review remain outstanding.
