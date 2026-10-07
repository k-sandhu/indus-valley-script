# Package B3: synthesis of the evidence census

Owned directory: `experiments/2026-10-06-evidence-census/synthesis/`. Local raw directory: `data/raw/2026-10-06-evidence-census/synthesis/`. Use live web search only to resolve specific conflicts.

## Question

Answer the user's question directly: is all evidence for the Indus script that can be found anywhere indexed, and with as much metadata as possible? If not, how much is missing, where is it, and what would a complete index require?

## Inputs

Read the two finished census packages and their reviews: `experiments/2026-10-06-evidence-census/sites-and-publications/` and `experiments/2026-10-06-evidence-census/collections-and-datasets/` (each with `REVIEW.md`). Read the earlier uncommitted dataset landscape in `experiments/2026-10-02-dataset-landscape/` (README, `landscape.json`, `SCHEMA.md`, `DATASET_PLAN.md`) without editing it. Where a review lists required fixes, apply the correction in your synthesis and say so.

## Steps

1. Join the site, publication, collection and dataset registers on shared identifiers (CISI numbers, excavation and accession numbers, site names). Keep candidate joins separate from confirmed joins.
2. Estimate coverage with explicit count bases: inscribed objects reported in primary publications versus objects present in accessible indexes (ICIT's published counts, CISI, IM77, Lipi, Mayig, museum catalogues), by site and region. Give ranges where sources disagree and say why.
3. Measure metadata completeness for each field (findspot, stratum or phase, absolute date, dimensions, material, photographs, registration numbers, licence) across indexes, using the local corpus fields as one measured case.
4. Rank the largest unindexed or under-described pools by the evidence they would add, with the route to obtain each (publication, museum request, excavator contact, archive), and the rights constraints.
5. Compare the result with the October 2 `SCHEMA.md` and propose concrete changes to the schema and pilot plan if the census shows missing entity types or fields. Write the proposal as a new file in your owned directory; do not edit the earlier files.

## Outputs

`coverage.json` and `coverage.csv`, `field-completeness.csv`, `priority-gaps.json`, `SCHEMA-AMENDMENTS.md`, and a `REPORT.md` that answers the question with numbers, bases and the remaining uncertainty.
