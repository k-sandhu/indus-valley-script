# Retrospective: publication screen, 13 October 2026

Claude Opus 5.5, working as a subagent for the coordinator, screened the untracked research packages and modified tracked files before their first public commit. It changed no existing file and committed nothing. The outcome is three files kept local, one file to edit, 3,572 files to track, and six conditions on notices, the reuse statement and the payload audit tool, recorded in [decisions.json](decisions.json).

## Approach

The protocol was written before any file was opened for screening. The file list was then frozen with sizes and hashes, and three scanners ran over it: Lipi sequence windows, the Lipi key and readings, and a payload scan for credentials, addresses, embedded images, record fields, quotations, earlier omissions and size. Each package's own asset statement was read, and files were opened by hand wherever a scan fired or an asset's origin was not recorded: the large anchor-expansion outputs, the Bronze Age acquisition and census files, the satellite exports and notices, the settlement PDF's embedded images, the review packets, the plate-check observations and the Claude CLI records. A rule table then assigned every frozen file to exactly one decision; the build stops if a file matches no rule.

## Problems and repairs

The first sequence run found only two files with matches, so the scanner was checked against known material before its result was trusted. It recovered 21 distinct complete texts from the quarantined plate-audit comparisons and none from the published catalogue windows. Two discovery passes were added after that run, for `W`-prefixed codes and underscore joins and for context windows split across JSON fields; both are marked as post-protocol additions in the scanner. The proximity pass produced fifteen matches that were all dictionary keys or prose lists.

The sequence scan did not cover a second kind of Lipi content. While reading the Sanskrit-key tests, it became clear that the key under test is the Lipi repository's own `xlits.csv`. A further scanner for key entries and Lipi readings found the allograph pair tables reproducing most of the key, which led to the only keep-local decision.

The first email check ran over binary files and reported thirty random strings from the PDF's compressed streams; the repaired check reads text files only. The owner's personal address differs from the configured Git noreply address, so it was supplied through an environment variable at run time; an intermediate output recorded a masked form, which was replaced with a count. A search for the address's local part across the published tree found it inside five already-published privacy-scan scripts, which is reported for the owner.

Parallel contributors added 41 files and changed 83 within twelve minutes of the first freeze, and later changed `REUSE.md` to dedicate project material to CC0. The scans were rerun on a final inventory frozen at 05:18 UTC, and the conditions were revised for components that cannot carry a CC0 dedication. Files added after that freeze are outside the decisions and are listed in the report to the coordinator. A glob rule meant for satellite coordinates first captured the vendored Natural Earth files because `fnmatch` lets `*` cross directories; reordering the rules fixed it.

## What a later screen should reuse

The scanners take an inventory name and an output name, so a later screen can rerun them on a new freeze. The key-and-reading scan should run alongside the sequence scan whenever a package works with the Lipi export, since its key and readings are as unlicensed as its texts.
