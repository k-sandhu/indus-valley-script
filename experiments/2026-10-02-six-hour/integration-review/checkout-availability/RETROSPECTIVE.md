# Availability review record

The existing repository checker tests whether a linked target exists in the local project. This review added a captured Git-selection check so a reader can see which links also open after cloning. It retained the source rights policy and counted selected-directory prefixes separately from individual file selection.

The initial capture found 18 unique local-only targets and no missing targets. The independent review then found that three documents had changed during other contributors' work. Their ten additional links broke the initial syntax-count comparison and three live-document hash checks. That review remains preserved with 810 of 814 checks passing.

The refinement reads each document's bytes once, stores a project-authored snapshot and derives its hash and link inventory from that same payload. Its independent review reads the stored bytes and records later live changes separately. The first snapshot-based review passed 823 checks. A final capture after the parent completed core manuscript edits added one selected link. That accepted capture has 747 local occurrences, and all 824 review checks pass. Every earlier endpoint remains preserved.

Copied Markdown retains links relative to its original document location. The capture's `document_snapshots` field maps each original path to its preserved copy, while `document_hashes` supplies the byte identity. The integrating repository checker can use that source context to resolve snapshot links. Checking those copies against their new storage directory would instead report artificial missing targets.

Every excluded target received selected source or transformation pointers. Exact restoration of manually coded definition files can require the local imported file; the acquisition records and page assessments still let a reader document a new source transcription. The normalizers also need their pinned upstream inputs and careful source-commit resolution. These dependencies are recorded beside the target rather than hidden in a general clone instruction.

The latent-model endpoint was checked through its authored chunk package. Decompression, individual compressed/uncompressed hashes and the complete stream hash preserve its exact bytes. A separate known-pattern scan found no credential matches in that authored stream. No acquired source, corpus derivative, Git index entry or rights exclusion was changed by this review.
