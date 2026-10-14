# Pipeline retrospective, 13 October 2026

The implementation provides the seven requested executable scripts and `cisi_common.py` for shared file, identity, uncertainty and join rules. [TOOLS.md](TOOLS.md) gives the command sequence and the local and tracked output paths. The plan was written in [PLAN-CODEX.md](PLAN-CODEX.md) before code changes. This Codex session performed the code assignment and used generated fixtures and the pilot's final files for testing. It did not open the full run's active readings, crops or strips, acquire sources, edit shared records or execute a Git mutation.

## Implementation

The parser retains the pilot's row fields and adds volume, site headings, excavation provenance markers, separate numbers, generic museum codes and local parser-review details. A year-shaped number in CISI 1 remains a registration number; the NMP-accession convention is applied to CISI 2. Piece FC cells derive a number only when their nonempty readings give one distinct number. Unknown institution codes keep their printed code, pending a sourced expansion.

Comparison aligns catalogue identifiers, normalizes whitespace and preserves the reader's punctuation. It collapses identical overlap rows and combines explicitly numbered pieces, including a piece marker on its own line. Conflicting duplicate readings and one-sided entries require whole-row adjudication. Estimated strip locations use entry order, with neighbouring strips supplied for orientation. Corrigenda use positional text-line comparison and have separate counts and final text.

Final building validates all selected disagreements and the recorded readings before writing a block. Missing adjudications are listed; changed input readings invalidate the decision. Both pass error rates use candidate matching and have an upper figure for definite readings left undecidable. Omissions and spurious rows are counted separately because an omitted row supplies no definite cell reading. The tracked report states the union-row denominator and the whole-row outcome convention. Every blind decision protects its cells from the subsequent recheck, including undecidable decisions.

The merge validates each block's input and final-output hashes, refuses duplicate identifiers and reports integer gaps by site prefix. The CISI 2 pilot is added once. Cross-check details remain local and include missing printed numbers when another source supplies a number. FC brackets are flagged when their candidates exclude the table rule. Source comparisons request a page recheck and do not supply replacement readings.

Coverage uses the inventory's field, type and site rules and the pilot's raw-key museum baseline. It reports the whole corpus and unique joined families, including separate volume groups and modes with and without brackets. The source-set union reproduces the dated verifier's museum-token convention. Prediction 1 counts unique entries satisfying the stated OR rule and separately reports conflicting catalogue checks and the stricter all-rows share. Prediction 2 retains extensions with an unresolved FC in its denominator, supplies bounds and states the extension normalization in its output.

## Problems found in testing

The initial report-content check mistook the `pass1` and `pass2` labels in count and provenance dictionaries for transcribed values. A revised string check also caught the status value `final`. The test now inspects dictionary keys and their value types, allowing count labels while rejecting value-bearing fields. Failure details from those runs remain in their local fixture directories.

Repeated individual pieces after their entry had been combined initially looked like conflicting duplicates. Component signatures now deduplicate those repetitions. Tests also cover a new area code on an unpunctuated excavation continuation and a spaced slash separating numbers while preserving a slash within an area code. These changes retain the printed cells and produce additional parsed number records.

The coordinator will still need to resolve any ambiguous catalogue identity before alignment, consolidate entries continued across block boundaries before merging, review unknown codes in the local parser reports and record evidence explaining FC exceptions. The complete comparison and final build require separate corrigenda files for both volumes. The pilot's sampled and full-reading accuracy endpoints remain in its package; the new volume accuracy summary covers the new blocks.

## Validation and result

[selftest.json](selftest.json) records 53 passing checks with no failed check, hashes of the tested code and pilot inputs, and the local fixture directory. Tests exercise the command-line pipeline, incomplete and stale adjudication refusal, edited-final hash refusal, whole-row additions and removals, overlap and piece handling, error and upper-rate counts, recheck precedence, family ambiguities, source checks and both numerical predictions. The rebuild command was executed against isolated fixtures. Each run writes into a new local directory; the final passing run also retains its own result file there.

Merging and joining the frozen pilot reproduces all four requested coverage fields for 283 joined objects from 327 entries. Museum number rises from 74 to 276, holding institution from 74 to 283, FC number from 0 to 283 and excavation remains 278. Re-parsing the pilot's two final text files with the extended parser reproduces the same coverage. The combined museum union also reproduces 542 objects including bracketed cells, 519 with wholly unbracketed cells and 534 with at least one definite number.

The pipeline is ready for coordinator review and execution after the readers and adjudicators finish. Full-run accuracy, coverage gains and prediction results will come from that execution; this implementation session establishes the synthetic behavior and the pilot regression.
