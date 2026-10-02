# Review record

The task was a read-only integration review of the conditional-reference and physical-observation manuscripts. The review compared saved output fields with the stated sample sizes, intervals, support counts, scaling conditions and consensus outcomes. It also traced source exposure and observation availability back to contributor methods and protocols. KHI-05 was added during review and included in the pinned manuscript version.

The first terminal read used an explicit UTF-8 file decoder but inherited Windows's CP1252 output encoder. It stopped when printing the product symbol in Paper 002. The same read was retried with `sys.stdout.reconfigure(encoding='utf-8')`. A code-point check found no replacement characters or mojibake in the manuscript files; the initial rendering artifact did not reflect their stored bytes.

Large JSON arrays initially obscured relevant summary fields. The review then selected exact fields for rates, intervals, population counts and verification totals. The saved helper makes 106 arithmetic and field checks across sixteen source files without calling a fitting routine. The source hashes and manuscript hashes identify this review's inputs.

The main numerical statements matched. Six corrections concern metric labels, local equality assumptions, collective operation/availability, independent units and the equal-budget wording around KHI-05's minimum required checks. Two further wording changes distinguish within-row reversal and reused held-out observations. Shared manuscripts and source endpoints were left untouched.
