# Submission gaps and publication plan

Date: 2 October 2026. The [manuscript](manuscript.md) is a complete private draft; the work below remains open. One focused paper should combine artifact-aware prediction, the test on an independent second transcription and the negative gap-count result.

## Required work for the current claims

| Gap | Concrete work | Completion evidence |
|---|---|---|
| Independent reproduction | Rerun the frozen principal models and shuffled-corpus references from pinned inputs in a clean environment. Preserve the present results and compare generated values, folds and hashes. | Dated reproduction manifest, environment, discrepancy log and signed reviewer account. |
| Source and mapping review | An independent reviewer, ideally an epigraphist, checks a declared sample covering sites, object types, aliases, the division of compound signs and ambiguity in mapping coarse classes to fine codes. Include disagreements and the sample selection rule. | Source-linked adjudication table, reviewer identity and role, uncertainty bounds and revised coding decisions if necessary. |
| Premises of the archaeological reference distributions | Exact sample-space, uniqueness, copying, imperfect-face, quality and fitting-domain studies are complete in [Paper 002](../002-conditional-reference-laws/manuscript.md). For a new archaeological population, establish how its records depend on one another physically, its selection history and its observation quality. | Completed synthetic and finite audits; a source-backed observation law, the rule by which the intended sample was observed. |
| Fresh evaluation | Freeze a model and a new, source-certified block of artifacts before their reference transcriptions are inspected. Retain unsupported candidates and exclusions. Choose the population and scoring rule before sampling. | Timestamped protocol, blinded reference, complete denominators and dated predictions. |
| Published-model reproduction | The first-order Markov model added on October 2 now matches all original hidden slots and folds, but its smoothing differs from Rao et al.'s. A faithful reproduction needs their published modified Kneser–Ney rule under the same evaluation. | [Completed conceptual baseline and verification](../../experiments/2026-10-02-six-hour/markov-baseline/README.md); a separately dated implementation of the published smoothing and paired scores are still required. |
| Input and release access | Read the repository's redistribution record, establish a lawful reproducible access route, and decide which files can accompany submission. The bulk Lipi export and source copies with unresolved rights remain local until their status is resolved. | Permissions or licence record for each source, acquisition scripts and a manifest of files permitted for release. |
| Publication priority | Update the comparison of our exact procedure with Rao 2009, the historical method for identifying duplicates, Khanna and Merriam 2025 and recent 2026 code and preprints. Distinguish publication status and code version. | Revised related-work table with inspected source locations and remaining overlap. |
| Authorship and editorial completion | Assign human authors and affiliations; state contributions and AI use; acknowledge sources; complete the reference metadata. Select a venue and meet its reproducibility and data requirements. | Approved manuscript and venue-specific checklist. |

The fresh evaluation and the expert review of sources are the largest evidence gaps for claims that the results generalize. The current exploratory measurements can be described in a preprint or technical report that states their status. Submission readiness depends on the chosen venue and the scope of the claims.

## Result-specific checks

A rerun of the gap-count benchmark becomes informative only with a newly specified predictor or physical evidence about gaps; the matched-law result already answers the question for the artificial design. If geometry is added, first define what a gap width measures, how sign spacing varies with material and layout, and how originals of known text are sampled. Keep count recovery separate from ranking signs at a known position.

The evaluation on the second transcription should preserve the five unmapped and seven wholly unsupported exclusions, the 20 partially unsupported faces, the subset of 54 fully supported faces and the candidate-set sizes. A crosswalk review can change the scored events; such a change needs a new result file rather than a rewrite of the frozen score.

Known-slot results should include slot-weighted (micro) and equal-text accuracy, out-of-vocabulary coverage, summaries by sign type and frequency, and calibration. The headline accuracy alone cannot support a working tool for eroded inscriptions. Evaluating such a tool would need source-verified eroded specimens, a protocol for counting and segmenting lost signs, and reference uncertainty.

## Separate publication candidates

The numerical equality audit could become a short source-critical note once the historical tablet identifier and the context and assumed range for M1383 are resolved. Its full solution set and parity correction are ready to inspect; the proposed equations and selected values come from earlier work. Its most valuable extension would predict an independently measured quantity under frozen premises.

The chart atlas, our coded image crops of the cells of a published sign chart, is a resource candidate with uncertainty labels and provenance. Before a recognition paper, obtain an independent reference, freeze the source geometry before scoring, and sample a new block of rows, since the geometry was repaired after the reference was released. Preserve the failed result on twenty fresh rows (fresh20). The present geometry diagnostic is useful development evidence.

Substitution examples belong in the current discussion and retrospective. A separate paper on substitution classes would require source-certified graphic identity, checks of physical independence, a priority review and pair-level evaluation adjusted for selection. Aggregate transfer and a single striking pair answer different questions.

## Proposed submission package

Keep [manuscript.md](manuscript.md), [methods.md](methods.md), [claim-evidence-map.md](claim-evidence-map.md), a frozen numeric review and a manifest of permitted data and code together. Figures should show the predictive gain, known-slot against unknown-count restoration, and calibration or rare-sign coverage. Put further explorations in the original report rather than expanding this paper into a catalogue of every attempted reading.

Register every further experiment in `knowledge/experiments/registry.json` with a dated output directory and a reason that distinguishes it from an already completed path. This submission plan needs no workflow, deployment service or recurring run.
