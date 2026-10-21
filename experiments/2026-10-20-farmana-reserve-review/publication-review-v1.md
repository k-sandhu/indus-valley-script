# Publication packaging review v1

We recommend including the project-authored reports, protocols, acquisition and review code, aggregate coverage, bibliographic source records and hash manifests listed in `publication-review-v1.json`. The review inspected only the three proposed experiment packages. No raw source or new object content was opened. File hashes pin the reviewed versions; later edits require a new packaging check.

Exclude `experiments/2026-10-20-fresh-test-collection/freeze.py`: it embeds reserved object measurements. Preserve that frozen file locally. Exclude both acquisition packages' `repository-verification.json` files from this bounded push because their repository-wide diagnostics contain unrelated frozen-protocol and document contexts outside the review scope. A separate review can decide their release.

The remaining reviewed files contain our prose and code, identity metadata, source routes, coordinates, aggregate counts, paths or hashes. No acquired text, OCR, image files or detailed source-derived object-row payload was found among those included files. The credential and signed-URL pattern scan returned no hits. Public source links and ordinary Drive file identifiers are bibliographic routes.

All raw sources and detailed derivatives remain local. The parent receives filenames, classifications and reasons. The review changes no frozen record and grants no test eligibility.
