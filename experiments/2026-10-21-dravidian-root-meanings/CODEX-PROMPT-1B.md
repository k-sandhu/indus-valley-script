# Dravidian root meanings, run 1b: one parser repair after review (follow-up for GPT-6.1-Sol)

This continues run 1 in the same session. The coordinating session reviewed your final outputs. The tree reader, the tip map, the coder, the reference pools, the driver and the tests are accepted, including your repair of language labels that follow a gloss ending in a period: an independent count of language sigla at line starts agrees with your parse for every chosen entry except the one case below. Gondi `(Ko.)` is accepted as Koya, the S4 search recoveries need no change (an independent scan of every S4 page finds homophonous star forms only in entry 4876), and the burn-in handling stays as the protocol states. All owned paths, invariants and rules of `CODEX-PROMPT.md` still apply: no commits or other Git writes, no edits outside the owned paths, raw material local, and no ancestral-state probability, parsimony score or reference statistic computed on real codings.

## Disk space

Drive C: filled completely during your run and now has only about 350 MB free, shared with other sessions. Do not extract archives again, write no large intermediate files, and keep the log short. If a write fails for lack of space, stop and say so in the final message.

## The defect

In entry 5496 (a) the Brahui line ends with a cross-reference in parentheses, "(cf. s.v. 3338 Ta. …)". The parser opens a second Tamil language line at the siglum inside those parentheses and creates a Tamil form whose gloss is inherited from the Brahui line. It adds a spurious Tamil form to the entry and a spurious Tamil value to one reference head of the WHITE pool.

## What to do

1. Repair the parser so that nothing inside parentheses opens a language line or creates a form: a siglum inside parentheses is either a dialect label (as in "(Mu. Ko.)") or part of a cross-reference ("cf.", "s.v.", "see", an entry number) and is dropped with the cross-reference.
2. Extend the parse audit in `validate_run1.py`: no language line may begin inside parentheses, for every chosen entry and every S4 entry.
3. Add a regression test on synthetic text you write yourself.
4. Rebuild the parsed entries, `run1/parse-summary.json`, all codings, the reference pools and `run1/pool-sizes.json`, the rights scan, `run1/selftest.json` (so that every recorded code hash is that of the final file), `run1/created-paths.json` and `run1/verification.json`. Rerun `compute.py --synthetic` into a new directory under `codex-run1/` and delete your older synthetic output directories there to save space.
5. Append a short section "Run 1b" to `CODEX-NOTES-RUN1.md`.

## Final message

The audit result for every chosen and S4 entry; every tip whose state changed in any coding variant (meaning code, variant, tip, old and new state) and every pool whose size changed; the new selftest totals; the final SHA-256 of every file in `code/`; and anything to decide before freezing.
