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
