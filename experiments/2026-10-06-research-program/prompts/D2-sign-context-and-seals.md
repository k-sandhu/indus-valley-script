# Package D2: sign frequency in context, motif concentration and seal standardization

Owned directory: `experiments/2026-10-06-sign-context-and-seals/`. Local raw directory: `data/raw/2026-10-06-sign-context-and-seals/`. Use live web search for site data and precedents.

## Background

In a recorded lecture (https://youtu.be/1i9q17ld_jU), Dennys Frenez asked why certain signs dominate, such as sign 740 (the "jar"), which he put at about 10% of all occurrences, and how their usage relates to the size or type of site. He also described Indus seals as an "unbalanced oligopoly": most seals carry the common unicorn motif while many rare motifs and signs occur, which he read as regulated competition or cooperation rather than one central authority. He treats the script as serving identification, property control and administrative regulation, with seals as a kind of corporate badge.

In `data/normalized/lipi_observed_faces.jsonl` (5,680 faces, ICIT/Wells sign codes, `000` for unreadable), sign 740 is 1,928 of 19,946 token positions (9.67%; about 10.7% of readable signs). Faces carry `site`, `region`, `object_type` (for example SEAL:S, TAB:B, TAB:I, POT:T:g), `symbol` (motif codes such as Bull1 with suffixes for the unicorn variants, Gaur, Elep, Zebu, Rhin, Tigr, Scene) and a `metadata` block with Harappa periods in `time`, material, and seal dimensions (`h`, `v`, `th`, and millimetre fields where nonzero; zero is a placeholder, not a measurement).

## Questions

1. Does the frequency of sign 740, and of the other most frequent signs, vary with site size, site type and object type? Compile site areas and site types (urban centre, town, port, craft or rural settlement) from published sources with exact citations, recording the range where sources disagree. Fit models that separate object-type composition from site effects (for example binomial models with site-level random effects and object-type fixed effects, or exact stratified permutation), grouping physically related records. Report per-site frequencies with intervals and say how many sites the size comparison rests on.
2. Can the "unbalanced oligopoly" description be turned into testable predictions? Measure motif concentration (shares, rank–abundance, Herfindahl–Hirschman index) by site, region and Harappa period. Test whether texts on rare-motif seals differ from texts on unicorn seals (sign inventory, initial and terminal signs, text uniqueness rate, text length) beyond what grouped permutation produces, and whether any motif–text association is site-specific. State which observations support, contradict or cannot distinguish the description from alternatives such as a few dominant workshops or uneven excavation.
3. Do seal dimensions show standardization? Compare the coefficient of variation and the distribution of seal sizes by motif, site and Harappa period, and test the relation between seal face size and text length. Treat zero dimensions as missing and report the remaining sample sizes.

## Method requirements

Write `PROTOCOL.md` before computing outcomes, including the site-size sources, model specifications, grouping rules and the comparisons. Keep physically related records together in every resampling step: permute among whole object families or alias components, within object-type blocks. Paper 002 (`papers/002-conditional-reference-laws/`) explains why. Correct for multiple comparisons across signs. Search for precedents before claiming anything new: Yadav 2013; Oakes 2017/2019; Rao et al. on motif–text association; Kenoyer's work on seal production and standardization; Frenez 2018, "Private person or public persona? Use and significance of standard Indus seals as markers of formal socio-economic identities"; Green 2021 on Indus seals and social organization; Ameri on seal carving styles; Mahesh T C's 2026 commercial-network preprint (arXiv 2604.23582); Mukhopadhyay 2019 and 2023. State how each result relates to them.

## Outputs

Site table with sources, model outputs, concentration and association tests, dimension analyses, code, and a `REPORT.md` that answers each question with numbers and names the data that would resolve what remains open.
