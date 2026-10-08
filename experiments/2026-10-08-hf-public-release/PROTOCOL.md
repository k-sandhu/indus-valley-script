# Protocol: local Hugging Face release candidate

Recorded 8 October 2026 before packaging or score computation. Package O owns this directory and `data/raw/2026-10-08-hf-public-release/`. The task is local preparation. Uploads, repository creation and visibility changes are outside this run.

The question is whether the attributed 1979 chart, two row-reading benchmarks, selected census tables and small study aggregates can form a documented, locally loadable release without unresolved-rights records. The existing `ksaw008/indus-research-data` backup remains private because it includes Lipi-derived predictions and models.

## Inputs and selection

Read the repository instructions, README, knowledge index, writing rules, reuse record, source and redistribution records, experiment registry, October 6 contribution assessment and program report. Reuse the chart's numeric reference and atlas; Package M's frozen 60-row and repaired v2 80-row references, predictions, crops, conventions and scoring functions; and the evidence census synthesis v6 endpoint and trimmed registers. Read Package N's available records to identify changes in verification status. Preserve all parent files and failed endpoints.

Each consulted candidate file receives a path, SHA256 where available, rights status, decision, basis and selected-field or transformation description in `rights-audit.json`. Helsinki-derived crops and readings require the official CC BY 4.0 attribution. Own code and compilations receive proposed MIT and CC BY 4.0 terms, awaiting the user's confirmation. Allow only facts, identifiers, counts, citations and authored assessments from the census. Select columns explicitly; exclude source quotations, museum descriptions and images, Lipi sequences and record-level payloads, Mayig, Ascalone catalogue rows, third-party PDFs and the provisional full 1979 transcription. Aggregate results may include numerical outcomes derived from those inputs when they cannot reconstruct records.

## Method and comparisons

Build a new `release/` folder with one named YAML configuration for each table, stable Parquet schemas, relative PNG paths, dataset card, field definitions, notices, proposed licences, citation and release checklist. Stage both original and adjudicated benchmark readings with provenance; retain reference ambiguities and process departures. Keep original benchmark metrics distinct from later exploratory corrections. Write a separate private-store card from the hosting manifest and read the restore implementation before documenting its scope.

Load every configuration through `datasets.load_dataset` using the local release folder. Compare table counts and selected fields with their pinned source inputs, resolve and decode every staged PNG, and score staged predictions against staged references using the frozen scoring functions or a portable equivalent. Compare every reproduced numerical metric that the scorer covers with Package M, stating any uncovered metric. Record software versions, hashes, schemas, checks and limitations in `validation.json`.

Review all staged text and table fields for copied prose and prohibited record payloads. Use an explicit input allowlist, a record-field denylist, source-content comparisons and a scan for sign-sequence overlap with local unlicensed derivatives. Matching short sequences can occur independently in the licensed benchmark; inspect provenance rather than treating an overlap as proof of copying. Raw comparison matches and temporary downloads stay in the local raw directory. Record failures, including failed source access or validation attempts.

## Negative results and amendments

A component fails staging if its redistribution basis is unverified, a required asset is absent, source fields cannot be separated safely, schemas fail loading, image paths fail resolution, or benchmark scores differ without an explained source change. Exclude that component or retain an explicitly incomplete local candidate and identify the missing work. Local loading does not verify the future hosted viewer or confer expert certification. No outcome licenses the owner's work without the requested confirmation. Changes after results must be recorded in a dated amendment and affected analyses labelled Exploratory. Package N work in progress is described from the observed snapshot, without substituting it for Package M's frozen endpoints.

## Amendment: 8 October 2026, review and owner decisions

The reviewer accepted the loading, image provenance and score reproduction. This amendment authorizes packaging changes after that review; it does not change the frozen benchmark endpoints. The earlier checker repairs corrected Windows cache paths, an encoding name, Arrow list-child names and the CISI1-1987 filter. Their failed and passed validation reports remain preserved. Those checker repairs should have been recorded here when made; this amendment records them retrospectively.

The owner assigns CC0 1.0 to project data, annotations, readings, compilations and documentation, and the Unlicense to project code. Edition-derived images, inscription identifiers, classifications and sign numbering retain CC BY 4.0. Mixed configurations state both layers. The author is k-sandhu. Hosted examples use ksaw008/indus-reference-benchmarks; a single build constant supplies the proposed public issues URL.

Remove the 19 museum joins supported only by the Lipi excavation-number comparison, retain the 49 independently cited published-catalogue correspondences, and record the exclusions locally. Replace placeholder identifiers with null and document each identifier's source. Public provenance uses portable source labels; the full rights audit, source-path mapping and owner checklist stay outside the upload folder. The public exclusions note contains no private paths or file hashes.

Require unit-level confidence in [0, 1] in benchmark predictions and a valid section for v2. Test incomplete and complete prediction files and retain unchanged score comparisons. Add embedded Image columns for chart and benchmark row crops, storing each PNG once; retain logical path columns and supply an extraction helper for users needing loose files. Review scripts may run against a temporary materialized copy under this package's raw directory, with their output paths redirected in memory and the private parent-image mapping restored for the image audit. Preserve the reviewer scripts unchanged and record these adaptations.

Rewrite hosted usage, task definitions, pass criteria, source attribution and public method notes. Validate official licence texts and CFF structure, scan all public files for privacy and placeholders, load every configuration, compare source fields and recompute both scores. Write a new dated validation report; preserve every earlier report. Packaging choices after review have Exploratory status; reproduced arithmetic has Verified computation status. A negative revision result is a failed load, mismatched source/image/score, incomplete field documentation, invalid prediction accepted silently, private disclosure or unresolved redistribution basis. No upload or visibility change is authorized.

### Checker amendment: 8 October 2026, revision validation

The first revised loading attempt again exceeded Windows' filename limit because both the build folder and raw cache name were longer. A short cache and the final release folder fixed loading. The first completed revised validation loaded all 19 configurations and matched all images and benchmark scores, but reported a metrology parent comparison failure: portable JSON serialization removed spaces from the two simulation-interval strings. The numerical endpoints were unchanged. Compare those intervals as parsed JSON, preserving every numerical value. Preserve the failed revision reports and write the repaired check to a new dated report. These are checker repairs; no frozen source or analysis endpoint changes.

### Rebuild check: 8 October 2026

A final command review found that a relative --records argument was being tested after the checker changed its working directory to the raw cache. Resolve this argument before the directory change, so fresh rebuilds use their own source map and pins instead of the final-release fallback. Verify with an explicit relative records argument from the repository root and a fresh short build folder. This is a checker-path repair; no release payload or frozen metric changes.

### Privacy and methods amendment: 8 October 2026

An extended screen for parent-directory links found one bibliography URL to an unshipped local project report. It contained two ../ segments that the earlier private-ID/absolute-path expressions did not test. Null non-HTTP bibliography/access URLs and point the authored access assessment to the public method description. Extend the strict privacy expression to ../ and preserve the earlier reports as checks of their stated scope. Also define a geometric metrology hit explicitly as a smaller absolute log residual for the Indus reference than for the best local standard, as implemented in the reused metrology code. Rebuild and validate under fresh version labels. Benchmark references, scores and aggregate values are unchanged.
