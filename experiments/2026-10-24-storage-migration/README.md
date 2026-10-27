# Local storage migration, 24 October 2026

We moved 35,099,820,039 bytes in 187,131 accessible files from the C: checkout to `D:\projects\indus_valley_script`. Every destination file matched its source SHA-256 before its C: copy was removed. Nine directory junctions and 434 file links retain historical paths. Tracked research records and code remain in the checkout. The [storage guide](../../LOCAL_STORAGE.md) and [configuration](../../LOCAL_STORAGE.json) identify the new location.

The exact local inventory is `D:\projects\indus_valley_script\migration-2026-10-24.json`; its companion `.verification.json` has an empty failure list. The incremental hash record and copy logs remain beside it. The [summary](summary.json) preserves counts and manifest hashes in the repository without redistributing acquired data.

Fourteen subdirectories and one 110-byte file in an old plotting environment denied access. We preserved the whole environment intact on C: under `data/storage-remnants-2026-10-24/data/raw/2026-10-06-sign-context-and-seals/plot-deps-2026-10-07/`. Readable contents of that environment were also copied and verified on D:. The migration makes no claim about the contents or size of unreadable directories. Their original paths and errors remain in the local manifest. No source-rights decision changed.

We updated AGENTS.md, CLAUDE.md, README.md, CONTRIBUTING.md, REPRODUCING.md, DATA.md, the knowledge index, redistribution instructions, data README, bench guide, llms.txt, the experiment template and all seven repository task skills. The three navigation tools now recognize a D: path only if the matching checkout alias resolves to exactly that path. This keeps repository containment checks meaningful after the move.

The knowledge check passed both before and after migration with zero errors and two existing maintainer notes about generated files. The broad repository verifier had 58 pre-existing link errors before migration. The final comparison is in [checks.json](checks.json). The migration changed no generated registry or map and added no CI/CD, automation or publication.

## Retrospective

Contributor: GPT-6 in the Codex desktop harness. No subagents were used. We inventoried physical storage with `os.scandir`, excluded tracked files from bulk relocation and checked the selected directory trees against Git's tracked paths. The first general path walk failed on a long Windows path; extended-length paths repaired it. ACL failures in the old plotting environment required an explicit exclusion record and preservation of its whole parent tree. An early hash run discarded progress when a denied file raised an exception; the repaired run saves every completed file hash incrementally and records inaccessible files.

Robocopy staged accessible trees on D:. The final copy and verification were run through [migrate_local_storage.ps1](../../tools/migrate_local_storage.ps1) and [migrate_local_storage.py](../../tools/migrate_local_storage.py). Destination verification used a bounded pool of workers. PowerShell checked absolute source and destination containment before removal, preserved the inaccessible tree, removed verified C: copies and created junctions and links. We inspected Git status and path checks after the switch. Entry-document edits preserve each file's existing line endings; frozen evidence files were not rewritten.

Free C: space rose from approximately 87.8 GB at the initial inventory to 122.4 GB immediately after the move. The difference is approximate because other processes and filesystem allocation affect the live free-space reading. The moved-file byte count above is exact. New research acquisition then began in the [Q-1032 package](../2026-10-24-q1032-town-axis-register/README.md), using the D: raw-data tree.
