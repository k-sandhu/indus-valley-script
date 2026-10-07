# Package D1: chronological and regional sub-corpora, and non-canonical inscriptions

Owned directory: `experiments/2026-10-06-chronology-region/`. Local raw directory: `data/raw/2026-10-06-chronology-region/`. Use live web search for precedents and period definitions.

## Background

In a recorded lecture (https://youtu.be/1i9q17ld_jU), Dennys Frenez argued that statistical work treats the Indus script as one monolithic system and that chronological and regional sub-corpora would give a sounder framework. He also pointed to "non-canonical" inscriptions found outside the Indus Valley, which may encode different languages or social roles, for example patronymics. The local corpus can test parts of both ideas. `data/normalized/lipi_observed_faces.jsonl` has 5,680 faces with `site`, `region` (Inter-Riverine 2,950; Lower Indus 2,098; Gujarat/Kutch 489; Eastern Headwaters 65; Persian Gulf 17; Mesopotamia 11; Iranian Plateau 11; Central Asia 3; Upper Indus 6; South India 2; Other 28), `object_type`, `symbol` (motif) and a `metadata` block whose `time` field carries Harappa excavation periods for about 3,000 faces (for example "Period 3B/C", "Period 3C-2", "Period 4"), plus `period`, `phase`, `depth` and stratum fields for other sites. Sign codes follow the ICIT/Wells numbering; `000` marks an unreadable sign.

## Questions

1. Does sign usage change over time at Harappa? Map the period labels to the published Harappa Archaeological Research Project chronology (cite the source of the period definitions and dates), treating spans such as "3B/C" as interval-censored. Compare sign frequencies, text length, initial and terminal sign distributions and sequence statistics across periods. Report signs that first or last appear in particular periods with uncertainty that reflects sample size and interval censoring.
2. Do regions differ in sign usage after accounting for object type and site? Compare the regional sub-corpora with frequency divergence under rarefaction, positional distributions and cross-entropy of each region's texts under a sequence model trained on the other regions, against within-region held-out cross-entropy.
3. Are the inscriptions found outside the Indus region statistically distinct from core texts of the same length and object type? Assemble the external set from the region field, and check it against the literature on West Asian, Gulf and Central Asian finds (for example Parpola's discussion of West Asian Indus-type seals, Laursen 2010 on Gulf-type seals, Frenez's publications). Measure per-sign surprisal and n-gram novelty under core-region models relative to matched core texts.

## Method requirements

Object type confounds time and region (inscribed tablets, for example, cluster in some Harappa periods), so stratify or reweight by object type in every comparison and report both raw and adjusted results. Keep physically related records together: permute labels among whole object families or transitive alias components, within object-type blocks, never among individual faces. The repository's Paper 002 (`papers/002-conditional-reference-laws/`) shows why record-wise permutation inflates rejection rates under copying; reuse its approach. Exclude `000` from frequency tables but report how many unreadable signs each stratum contains. Report effect sizes with intervals alongside p-values, correct for multiple comparisons where you test many signs, and say how many records each comparison uses.

Write the period and region mapping, exclusions and test statistics into `PROTOCOL.md` before computing any outcome. Search for precedents before claiming anything new: Yadav 2013, "Sensitivity of Indus Script to Site and Type of Object"; Kenoyer and Meadow's Harappa reports on the chronology of writing and inscribed tablets; Fuls's ICIT-based studies; Oakes 2017/2019; any 2020–2026 diachronic or regional study. State which of your results repeat, refine or go beyond them.

## Outputs

Stratified count tables, test results, plots if useful, the code that produces them, and a `REPORT.md` that answers each question with numbers and states what additional dated or contextual records would sharpen the answer.
