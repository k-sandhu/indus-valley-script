# Completion checks

The [separate arithmetic verification](verification-v1.json) passed all eighteen checks. It independently reconstructs the 306 primary probabilities and the bootstrap interval, checks components and source counts, and verifies the frozen files. It is an author-side computation check. A separate contributor's reproduction and archaeological review remain open.

The final [knowledge check](checks-v2/kb-command.json) passes: 482 items, zero errors, zero warnings and two maintainer notes for the generated registry and map. The initial [check](checks-v1/kb-command.json) ran while the fish findings preceded their new attempt entry; its two missing-ID errors were resolved by concurrent work. We left the generated files unchanged.

The [prose scan](checks-v2/prose-command.json) completes with exit code zero. Remaining flags concern the exact timezone name and slash wording in the frozen protocol. The frozen protocol is preserved, including its fish-cutoff rationale error, which is corrected explicitly in [SCOPE-CORRECTION.md](SCOPE-CORRECTION.md). Unfrozen prose was reviewed and edited.

The full [repository integrity check](checks-v1/repository-result.json) reports sixty broken links in other packages and flags the tracked `data/MANIFEST.json` under its distributed-data rule. It therefore exits with status one. No error names this package or its attempt entry, and no unrelated file was changed. The [scoped checks](checks-v2/scoped-checks.json) pass: every evidence path exists, JSON parses, Python syntax is valid, all frozen artifacts are unchanged, and the primary score contains zero fish targets.

The bench shots [synthetic checks](bench-shots-synthetic-v1.json) pass their freeze, tamper, alias, spending and split guards. The [actual round](bench-inspect-v1.json) records a spent exploratory population. Full source rows, complete texts, detailed scores and images remain local; the tracked package contains source locators, aggregate results, code, generated controls and our prose.
