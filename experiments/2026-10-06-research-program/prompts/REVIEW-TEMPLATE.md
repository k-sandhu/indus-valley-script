# Review instructions for a finished work package

You are reviewing work produced by another model in a private Indus research repository at `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. Read the repository's `AGENTS.md` and `knowledge/editorial/WRITING.md`, the shared package instructions `experiments/2026-10-06-research-program/COMMON.md`, and the package prompt named below. Then review the package directory named below.

You may write only `REVIEW.md` and files inside a `review/` subdirectory of the package directory, plus temporary files under the package's local raw directory. Do not edit the package's own files, any shared file, or any other directory. Do not run git commands that change anything.

## Checks

1. Deliverables: confirm the required files exist (`README.md`, `PROTOCOL.md`, `REPORT.md`, `RETROSPECTIVE.md`, code, aggregate outputs, `registry-entry.json`, and `sources.json` where literature was used).
2. Reproduction: run the package's stated commands or verification scripts from the repository root where feasible within about 30 minutes of compute, directing any new output into `review/` or the local raw directory. Report what you ran, what matched and what did not. If a full rerun is too expensive, rerun a declared subset or recompute key aggregates from the saved intermediate files.
3. Numbers: compare every headline number in `README.md` and `REPORT.md` with the saved output files and fields. List each number checked and its result.
4. Sources: open at least eight cited sources (or all, if fewer) with WebFetch or the local copy and check that titles, authors, years and the attributed content are accurate. Check that snippet-only sources are marked as such.
5. Method: check that the protocol preceded the outcomes it governs (file timestamps, amendments), that exploratory refinements are labelled, that resampling keeps physically related records together where relevant, that counts keep their bases, and that limitations sit next to the claims they affect.
6. Scope: flag any claim of decipherment, sound or meaning assignment, resemblance presented as fact, novelty beyond the precedent search, or rights problems with material placed in the owned (tracked) directory.
7. Writing: flag stock phrases, promotional wording, repeated caveats, rhetorical contrasts and unclear passages, and run `python tools/review_prose.py --path <package directory> --no-write`.
8. Boundaries: run `git status --porcelain` and report any changed path outside the package's owned directory and the expected program files.

## Output

Write `REVIEW.md` in the package directory. Start with a one-paragraph verdict: whether the main results stand, and the most important problem if any. Then give a table of checked claims (claim, evidence path, result: confirmed, discrepancy or unverifiable, note), the reproduction log, source checks, method and scope findings, and a ranked list of required fixes and optional improvements. Be specific and brief.

Writing requirement: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.

Your final reply should summarize the verdict, the confirmed headline numbers, every discrepancy found, and the required fixes.
