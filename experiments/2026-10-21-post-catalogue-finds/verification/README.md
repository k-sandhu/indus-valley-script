We independently checked the object list and preserved the results in final.md and VERIFICATION.md. The review remains unresolved. report-summary.json gives the main outcomes; the CSV and JSON ledgers retain individual comparisons, objections and search coordinates.

The initial blind observations are frozen in blind-observations-frozen.csv. Do not regenerate that endpoint, sampling.json or blind-freeze.json. initial-results-2026-10-21 preserves outputs available when external input changes were detected. revised-input-2026-10-21 contains the four revised CSV inputs used for the final structural checks. input-revision.json records their hashes and confirms that the sampled source fields did not change.

From the repository root, these commands replay the structural computations against the revised snapshot:

```text
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/audit.py . counts
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/audit.py . locators
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/joins.py .
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/containment.py .
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/search_and_content.py . unnamed
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/search_review.py .
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/search_and_content.py . content
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/build_reports.py .
python -I -B experiments/2026-10-21-post-catalogue-finds/verification/selftest.py .
```

run-manifest.json hashes the audit code, source registers, historical context inputs and sampled text witnesses. The source text and the approved corpus identity fields are required locally. The exposure records distinguish source-only token displays, mechanical searches and the initial display-filter failure. RETROSPECTIVE.md records the repairs and the service interruption.
