# Eligibility correction, 11 October 2026

The first audit verified source references and rice calculations, but the hypothesis filter did not require a surviving textual observation when textual layers were removed. It therefore kept all five hypotheses after removing every inspected textual locus. The retained-observation counts and classification bounds were unaffected.

`audit-v2.py` adds this requirement: each candidate must retain at least one textual observation referenced by that candidate. It also hashes the actual running script. The change was made after inspecting run-v1, before writing the report. Both scripts and endpoints remain available; run-v2 is the corrected categorical endpoint. This is an implementation correction, not independent historical confirmation or an expanded evidence search.
