# Validation of the second evidence pass

The [package audit](package-audit-v1.json) passes for all eight contributions. Required files and registry evidence exist, package JSON parses, and no research image, PDF or database is stored in a checkout package. All 223 protected shared and first-pass files match their starting hashes. The raw-data junction and all eight new raw-data directories resolve to D:.

The [separate review audit](separate-review-audit-v1.json) also passes. It checks the review's documents, evidence links, JSON and D: raw directory. The [syntax check](syntax-check-v1.json) parses all 32 Python files in the research, review and coordination packages. These results were recorded by `final_checks.py` and `audit.py`.

Four parent source-byte reviews pass: [office seals](byte-review-v1.json), [object identities and lexical evidence](byte-review-v2.json), [units, Harappa, tablets and readable controls](byte-review-v3.json), and [town phases and the separate Harappa review](byte-review-v4.json). Their 316 declared bindings all match. Repeated bindings count as repeated checks; this is not a count of distinct source documents.

The [integration review](REVIEW.md) records interpretation scope, returned prose, accounting and repairs. Worker-specific checks remain in each package. The separate Harappa review verifies its narrow source chain; the other structural and byte checks do not provide specialist archaeological or linguistic adjudication.

The [knowledge check](knowledge-check-v1.json) passes with 617 items, zero errors, zero warnings and two maintainer notes for generated files. Regeneration remains with maintainer integration. The [prose scan](prose-review-v1.json) examined 45 Markdown files and returned 22 slash-related flags. We inspected them: they concern paths, original assignment and frozen protocol wording, source-format shorthand and search bounds. The final reports were read for clarity, scope and numerical accounting.

The broader [repository verifier](repository-check-v1.json) reports 63 errors. The [baseline comparison](repository-comparison-v1.json) identifies the 58 errors present before dispatch and five added broken links from the concurrent C-0017, C-0018 and C-0019 conjecture files to the urban-form package. None of the added errors refers to a file owned by this pass. That work remains outside this contribution; we do not claim that the global repository check passes. The [worktree comparison](worktree-review-v1.json) separately records concurrent paths without changing them.
