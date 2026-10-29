# Clean-clone verification diagnosis

The failed [first clean-clone verification](../clean-clone-verification-v1.json) comes from the Windows path API used by Python in the longer nested checkout. The inspected evidence is present and its bytes match the preserved working tree and filtered Git objects. The clone sits 59 path characters deeper than the original workspace, which makes several previously accessible paths cross the ordinary Windows path limit.

Python reports 46 indexed clone paths absent when they are addressed through ordinary absolute paths. Their lengths range from 260 to 278 characters. All 46 are readable through the extended Windows `\\?\` path form, and every one matches both its clone HEAD blob and the original working-tree bytes. Forty-four are captured knowledge/manuscript documents; the other two are the preserved Frenez retrospective and its registry entry. Git already has `core.longpaths=true`. The files were checked out successfully; the subsequent Python access checks produce the apparent omissions.

## Exact witness comparisons

The captured-2026-10-02-1057 copy of `knowledge/directions/archaeology-and-iconography.md` has 12,217 bytes and SHA256 `7746c23a2ac4ef1c7af15014a648dd6ce29f76b9e5801efb10b8f5c5e9080733`. The capture summary records that same hash. The original working file, original HEAD blob, filtered clone HEAD blob and extended-path clone file are identical. Its ordinary clone path is 271 characters long, and `Path.is_file()` reports false there. The verifier labels either an unavailable file or a different hash as a captured-document hash mismatch, so that label alone cannot distinguish the two conditions.

The Frenez file at `experiments/2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections/documentation-before/amendment-2026-10-07-frenez/RETROSPECTIVE.md` has 7,333 bytes and SHA256 `d00663fbbecccd7c5240558d0ef5942532acb89b9ad14acc9af4b0f8a6c0cf4a`. This matches its entry in [navigation-contexts-v3.json](../navigation-contexts-v3.json) and all four byte witnesses. Its ordinary clone path has exactly 260 characters and encounters the same access failure.

These two files contain mixed historical line endings: the captured document has 83 CRLF pairs among 86 LF bytes, and the retrospective has 26 CRLF pairs among 35 LF bytes. Git marks their `text` attribute unset. Their stored and checked-out bytes are identical despite the host's `core.autocrlf=true`. Line-ending normalization would change the frozen hashes and would not address the observed failure.

## Link failures and the bounded correction

All 42 reported broken-link destinations exist. Each fails when checked through the long unnormalized path containing its original `..` components. Resolving those components first gives a shorter canonical path whose ordinary existence check succeeds. For example, the Harappa short-records report's gallery link is checked through a 269-character path; its resolved target is 190 characters long and exists. The Lothal selected-trace link contracts from 272 to 215 characters and also exists.

The original `available(path)` function resolved a path to check Git selection, then called `exists()` on the longer input path. The correction resolves the path before the existence test. It also gives the verifier's repository root an extended Windows prefix, using `\\?\UNC\` for a network root and `\\?\` for a drive root. This allows the snapshot hash checks to read long filenames without changing the documents, context mappings or expected hashes. Systems outside Windows keep their ordinary paths.

I reviewed that correction in the current verifier and imported it read-only. Its extended root reads both sampled frozen documents and retains their correct repository-relative paths after resolution. The sampled Harappa gallery destination resolves and exists through the corrected path handling. The UNC construction was reviewed as code; this session did not test a network share. A fresh clone running the corrected verifier should supply the final whole-package check.

The diagnosis preserves the first failed verification as a record of the platform limitation. It supplies no reason to replace frozen source hashes, edit copied documents, add local-omission exceptions or alter the navigation contexts. This subreview changed only this report.
