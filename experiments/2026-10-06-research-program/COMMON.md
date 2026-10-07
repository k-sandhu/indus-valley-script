# Shared instructions for every work package

You are one of several parallel contributors to a private Indus research repository at `C:\Users\sandh\OneDrive\Projects\indus_valley_script` (the repository root below). Today is 7 October 2026 (the program began on 6 October). A coordinating agent planned this work; a separate reviewer will check your outputs, rerun your scripts and sample your sources.

## Before you start

Read the repository's `AGENTS.md`, `README.md`, `knowledge/INDEX.md`, `knowledge/editorial/WRITING.md` and the parts of `knowledge/experiments/registry.json` and `knowledge/retrospectives/` relevant to your package. Search the registry before repeating an earlier path; reuse earlier code and outputs where they fit, and say which ones you reused. The October 6 contribution assessment, `experiments/2026-10-06-contribution-assessment/REPORT.md`, summarizes the project's current standing and newly found precedents.

## Files you may write

Write only inside the two paths named in your package as "owned directory" and "local raw directory". The local raw directory sits under `data/`, which Git ignores; put downloaded third-party pages, PDFs, images, API responses, extracted third-party rows, per-query predictions and temporary files there. Put code, protocols, aggregate outputs and written reports in the owned directory. Set `TMP`, `TEMP` and `MPLCONFIGDIR` to a subdirectory of your local raw directory if a library needs a writable temporary location. Use `pip --no-cache-dir` for any installation.

Do not edit, move or delete any other file, including the shared registry, indexes, manuscripts and other packages' directories. Propose your registry entry as `registry-entry.json` in your owned directory, using the registry's existing fields (`id`, `theme`, `status`, `question`, `outcome`, `challenge`, `remedy`, `evidence`, `retry_when`). Do not run `git commit`, `git push`, `git checkout`, `git reset`, `git stash`, `git clean` or any command that changes repository history or other files. Do not contact anyone, submit forms, create accounts, publish anything or change repository visibility.

## Evidence rules

Write `PROTOCOL.md` before computing an outcome, stating the question, inputs, method, comparisons, selection rules and what would count as a negative result. If you change the plan after seeing results, add a dated amendment and label the affected outputs exploratory. Never overwrite a frozen endpoint or another package's output.

Link every claim to an exact source location or an output file and field. For literature, give exact titles, authors, year, venue and URL, and record in `sources.json` whether you opened the source or saw only a search snippet. Quote at most one short passage under 15 words per source. Record failed searches and failed downloads; they are part of the record.

Use the repository's status vocabulary: Proposed, Synthetic, Exploratory, Frozen evaluation, Failed, Superseded, Verified computation. Do not claim that the script is deciphered, assign sounds or meanings, present resemblance or later cultural continuity as archaeological fact, or describe a result as novel beyond what your precedent search supports. A resemblance or continuity idea is a hypothesis with a test.

Respect source rights. Raw acquired corpora and unresolved-rights material stay in the local raw directory. Review `knowledge/provenance/REDISTRIBUTION.md` before deciding that a third-party payload can sit in the owned directory.

## Writing requirement

Maximize reader comprehension. Explain the idea directly in connected prose. Keep necessary shared assumptions together. Avoid repeated corrective comparisons or warnings that interrupt the argument. Follow `knowledge/editorial/WRITING.md`: give the finding early, use concrete observations, methods and numbers, and avoid stock phrases, promotional adjectives, rhetorical contrasts, repeated caveats and closing recaps. Preserve exact source titles and the original wording of frozen evidence. Run `python tools/review_prose.py --path <your owned directory> --no-write` from the repository root on your Markdown and fix real problems.

## Deliverables

Your owned directory must contain `README.md` (what was done and the main results with numbers and links), `PROTOCOL.md`, `REPORT.md` (findings, methods, limitations kept close to the claims they affect), `RETROSPECTIVE.md` (approaches tried, problems, fixes and outcomes, without an invented reasoning transcript), `sources.json` where literature was used, the code you wrote, machine-readable aggregate outputs and `registry-entry.json`. Make scripts rerunnable from the repository root and state the command in `README.md`.

Keep the scope bounded. Aim to finish within about three hours of work. If part of the package cannot be completed, preserve what was done, say exactly what is missing and why, and finish the deliverables for the completed part.

## Final message

End with a plain summary: every path you created or changed; the main results with exact numbers and the files that contain them; what failed or remains unverified; and the specific checks you want the reviewer to repeat.
