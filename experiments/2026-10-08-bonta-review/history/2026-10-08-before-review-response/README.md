# Package Q: Steven Bonta review

Bonta proposes an early Indo-Aryan logosyllabic script with separate asset/metrological fields. The positional tests reproduce the jar’s final preference, **838/1,196 = 70.07%**, and the arrow’s, **192/225 = 85.33%**, on **2,469 objects**. The elementary fish proxy has **757 runs**, with **zero** repeats and **zero** runs longer than three. [Report](REPORT.md); [distributions](run-2026-10-08-v1/distributions.json), `populations.longest_eligible_object_faces`, `fish_proxy`.

The selected six-role lexical panel matches **9/10** whole dictionary headwords. **13/720** value permutations score at least as well under normalization, a conditional fraction of **0.0180556**. Exact headword matching among fixed variants gives **3/720 = 0.0041667**. The consistency intersection retains **35** prefix classes. Bonta selected the examples during development; these are fixed conditional tests with no reconstruction of his entire lexical search. [Lexical output](run-2026-10-08-v1/lexical.json); [selection](selection.json).

The manual source-history audit confirms **three** repeated catalogue objects, finds **one** conflicting label and rejects **two** parser overlaps. Eight ICIT examples have explicit MH references in the same entry, including one uncertain reference. The claimed **12–15** validation readings and attempted/failed denominators remain unidentified. There are **zero** usable inscription-to-physical-quantity joins for the M-field proposal. [Audit](validation-audit.json); [metrology gate](run-2026-10-08-v1/metrology.json).

[claims.jsonl](claims.jsonl) and [claims.md](claims.md) contain **126** scoped claim records. [Coverage](ledger-coverage.json) records the unfinished exhaustive reading audit; [reading locators](reading-locators.json) contain **410** primary source labels from **734** parser occurrences. The [concordance](run-2026-10-08-v1/concordance.json) supplies **17** candidate mappings, with no certified Helsinki 1979 codes. The missing manuscript figures prevent the full field grammar and sign inventory tests. [Sources](sources.json) records **47** source entries and access failures. The supplied lecture durations total **33,133 seconds**, or **9:12:13**.

## Repeat from the repository root

System Python 3.13.5 with NumPy 2.2.6 was used. PyMuPDF is needed only for optional source extraction/rendering. No installation, CI/CD, scheduled work or repository-history change was performed. Numerical scripts refuse existing output names. A checkout without the local pinned corpora, supplied page text and dictionary cannot reproduce the computations.

```powershell
python -B -X utf8 experiments/2026-10-08-bonta-review/prepare_inputs.py --raw-directory reviewer-derived-01 --output reviewer-input-checks.json
python -B -X utf8 experiments/2026-10-08-bonta-review/analyze-v1-frozen.py --run reviewer-replay-01
python -B -X utf8 experiments/2026-10-08-bonta-review/audit_validation.py --output reviewer-validation-audit.json
python -B -X utf8 experiments/2026-10-08-bonta-review/extend_distributions.py --output reviewer-distribution-sensitivities.json
python -B -X utf8 experiments/2026-10-08-bonta-review/verify.py --replay reviewer-replay-01 --output reviewer-verification.json
python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write
```

The verifier compares numerical aggregates and local derivatives, checks pinned input hashes against [PROTOCOL-registered.md](PROTOCOL-registered.md), recomputes positional counts and Monte Carlo tails, and independently enumerates all 720 lexical permutations. A replay reads the amended current protocol for its manifest; that manifest’s protocol field is expected to differ. Other input fields and all scored outputs must agree.

The completed fresh replay is [run-replay-2026-10-08-01](run-replay-2026-10-08-01/manifest.json). The final verifier passed **54/54** checks in [verification-final.json](verification-final.json); [verification-v2.json](verification-v2.json) preserves the first corrected check. The original [verification.json](verification.json) is a preserved Failed verifier-format attempt, **47/54**; it does not indicate failed analysis scores. The compound-fish sensitivity absorbs **67** pairs with **one** ambiguous-neighbour case, giving **751** runs and still zero repeats/longer runs. Its independent repeat is [distribution-sensitivities-replay.json](distribution-sensitivities-replay.json). The [package checks](package-checks.json) passed **24/24**, including local links and the manual prose scan.

The source-acquisition script can make a fresh public witness directory with `python -B -X utf8 experiments/2026-10-08-bonta-review/acquire.py --name reviewer-acquisition-01`. It resolves the then-current dictionary commit; the evaluation must continue using the pinned v1 dictionary. Later source downloads are recorded in `sources.json`; they are not required for numerical replay. `curate.py` builds authored annotations and normally refuses replacement; `source_updates.py` adds the later source checks. The final annotations are already delivered for source sampling.

## Reviewer source checks and remaining work

Repeat the computations above, inspect letter PDF pages 2 and 4 against the six candidate graphic roles, and sample the source segments in `validation-audit.json`. In particular, inspect M-1714’s inconsistent ICIT label, the adjacent example after ICIT1802, and the H-1832/H-642 reverse conflict. Check Lecture 7 at 22:12–24:37 and Lecture 5 at 29:39–29:48 against the machine captions and original audio. Verify the Cologne licence at the pinned commit.

The next source-dependent work is the full manuscript PDF, an exact historical ICIT validation list with rejected attempts, per-inscription field boundaries, a complete manual reading audit and independent quantity/object joins. [Retrospective](RETROSPECTIVE.md) records approaches, failures and fixes. [Registry proposal](registry-entry.json) is for the coordinator; shared registry and index files were not edited. [FILES.json](FILES.json) lists every created/changed file and local-only derivative with hashes.
