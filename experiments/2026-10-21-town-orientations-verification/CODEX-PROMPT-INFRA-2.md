# Codex assignment: finish the imagery, plan library and tools within a full disk

You are resuming an unfinished assignment in a research knowledge base about the Indus civilisation, at the repository root `C:\Users\sandh\OneDrive\Projects\indus_valley_script`. Read `AGENTS.md`, `knowledge/editorial/WRITING.md`, the original assignment `experiments/2026-10-21-town-orientations-verification/CODEX-PROMPT-INFRA.md`, the measurement rules `experiments/2026-10-21-town-orientations-verification/MEASUREMENT-RULES.md`, and the first run's notes `experiments/2026-10-21-town-orientations-verification/infra-v1/RUN-NOTES.md`. The first run wrote the tools and acquired imagery for eleven towns and many plan sources before the C: drive filled. Everything in the original assignment still applies, including its owned paths, invariants, deliverables and final-message specification, with the changes below.

## The disk

The C: drive has a few hundred megabytes free and other agents are writing to it. Check free space (for example with `shutil.disk_usage`) before every write larger than 1 MB. Never let free space fall below 250 MB because of your writes. Start no imagery download unless at least 1.5 GB is free at that moment, and stop downloading as soon as free space falls below 1.2 GB. You may delete only files that you or the first infra run created under `data/raw/2026-10-21-town-orientations-verification/infra/` and that are truncated, corrupt, duplicated or regenerable scratch; list every deletion with its size and reason in the run notes. Do not touch any other directory's files to make space.

## Work, in this order

1. **Verify what is on disk.** Open every GeoTIFF under `infra/imagery/` and `infra/validation/runway-imagery/` and read every band in full. Files that fail, or whose size or array disagrees with their record, were truncated when the disk filled: delete them and record them. Recompute SHA-256 for every surviving file and source scan.

2. **Recompress the imagery losslessly.** Rewrite each surviving GeoTIFF with DEFLATE and a horizontal predictor, one file at a time, confirm that every band is identical to the original, then replace it. Record the old and new hashes. This is to save space; it must not change a pixel.

3. **Write the final manifests.** `infra-v1/imagery-manifest-v1.json` with every town's scenes and composite as the original assignment specifies, and the runway imagery record. Mark towns without a composite.

4. **Write the plan library** `infra-v1/plan-library-v1.json` from the sources already acquired and the held literature, with every field the original assignment lists. Do not pre-render pages: give the PDF page and printed page, so measurers render what they need with `render_plan.py`. Inspect pages at low resolution in a temporary directory that you delete afterwards. Download a further plan source only if it is under 30 MB and the free-space rules allow; record towns without a plan.

5. **Run the selftest to a final pass.** Use small synthetic rasters in a temporary directory under `infra/` (keep the total under 50 MB), delete them after the run, and keep `infra-v1/selftest-v1.json`. Fix the tools if a check fails, recording each fix.

6. **Run the runway validation** with the runway imagery already held, as the original assignment specifies, and write `infra-v1/validation-v1/summary.json` and its README. Use the official AAI eAIP bearings and thresholds where held; flag or exclude references of doubtful precision, including Hisar unless the official record resolves it.

7. **Acquire the missing imagery only if the free-space rules allow**, in this order: Kanmer and Shikarpur first, then the optional towns in the listed order, up to five scenes each, written with DEFLATE compression. Record towns left without imagery because of space.

8. **Update the run notes** with a dated section for this run, the final rights table and the list of new sources and fields, and update `tools/README.md` with the validation results and the final paths.

## Verification and final message

Verify and report as the original assignment specifies. Add to the final message the free space at the end, every deletion with its size, and which towns still lack imagery or plans.
