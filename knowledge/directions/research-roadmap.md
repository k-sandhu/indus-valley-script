# Research roadmap

Reviewed 2 October 2026. The order follows the dependencies in the evidence: a reliable observation can support several tests, while a fitted reading may be difficult to distinguish from its alternatives.

## First decisions

The first investigation produced a working predictive benchmark, source-linked audits, and several failures worth preserving. Its unique-string model gained approximately 0.848 bits per noninitial sign under the declared filters. The gap-count estimator scored 46.3%, compared with 51.1% for always guessing one. The frozen fresh-20 image evaluation recovered two compatible first-candidate complete rows. These results identify two immediate needs: source-reviewed observations and a clear separation between a known-slot prediction task and recovering a damaged inscription. [Experiment registry ROOT-02, ROOT-08, ROOT-17](../experiments/registry.json), [methods findings](../../research/methods/FINDINGS.md).

Choose one primary target for the next cycle: **predict an externally observed use or quantity on a new artifact family**. Run image/identity work and one cheap known-system control alongside it. Reserve a new object block before looking at its inscriptions or measured quantities.

## Ranked work

| Rank | Project and expected result | Inputs | Decision and stopping rule | Effort |
|---|---|---|---|---|
| 1 | Source-reviewed feature and identity set | Permitted original images, accession/excavation joins, independent feature annotation | Retain disagreements and alternate segmentations. Release an annotation block for testing only after its rules and exclusions are fixed. | Days for a small existing-image set; access-dependent for new photographs. |
| 2 | Physical-use prediction | Reverse attachment traces, object form, find units and dates, externally assigned use categories | Text features must improve held-out prediction over context and production baselines. A same-die-only gain calls for broader observations. | Several weeks if specimen records are available. |
| 3 | Manufacture versus meaningful variation | Fine glyph and animal features, tool marks, material and carving groups | Test whether modifiers follow a production group or transfer with an independently observed category to a different group. Stop interpretation where features cannot be reliably seen. | Small feature pilot first. |
| 4 | Paired-surface constraints | Complete opposing faces, mould/copy relationships, fine identity | Freeze a relation graph and predict an unseen variant. Compare workshop, owner, commodity and entitlement explanations with explicit exceptions. | Feasible with selected published families; expert image review needed. |
| 5 | An external quantity anchor | A separately measured complete vessel or independently counted contents in a specified module/class | Freeze units, graphic coefficients and the physical reconstruction before opening the target measurement. Keep failed and ambiguous cases. | Highest potential semantic value; depends on access. |
| 6 | Secure chronology and regional transfer | Independently dated strata, mixed-context flags, comparable recovery methods | Predict a held-out cohort/site; measure sensitivity to residual objects, genre and material. | Longer archaeological data work. |
| 7 | Controlled unfamiliar-artifact study | Constructed objects with concealed answer keys | Test whether dimensions, operation and paired outputs improve functional recovery; record incorrect confident interpretations. | Low acquisition cost; participant work requires an appropriate research process. |
| 8 | Cross-civilisation account/mark comparison | Source-preserved layout and identity from Proto-Elamite, khipu, Gulf or later coins | Match the property under test and retain spatial/hierarchical structure. Choose a defined diagnostic to assess. | Pilot possible with permitted existing resources. |
| 9 | Historical continuity assay | Dated intermediate samples, rare compound features and contact/practice evidence | Compare transmission with independently invented shapes; hold out a region or period. Publish the intermediate evidence and missing intervals. | Months; sample access determines feasibility. |
| 10 | Frozen language/reading comparison | Complete candidate rules, linguistic reconstructions, independent anchor or risky external prediction | Score all withheld cases under matched degrees of freedom. Increase freedom only in a separately labelled model. | Prepare in parallel; decisive evidence may take longer. |

The ranking favours experiments that improve the observation set and then predict evidence outside a selected transcription. A verified bilingual or independently counted object would change the order immediately.

## A bounded next cycle

### Observation block

Select 30 objects for source review from more than one production/context group, with all available faces. Separate a development subset from a reserved subset by physical family. Resolve matrix/impression orientation, repeated photographs, stroke height and compounds. Record feature-level disagreements and retain unreadable marks as missing observations. Use the stored sources and [catalogue caveats](../provenance/catalogue-caveats.md) to choose the first cases.

The deliverable is an identity/feature table, source locators and an uncertainty report. A new glyph recognition model can then use a genuinely new reserved block. Its segmentation, row-count and fine-code outcomes should be reported separately. The earlier corrected-reference development improvements remain available for choosing a method, while the new block supplies its evaluation.

### Context block

Audit one assemblage whose attachment traces or context are recoverable. Lothal's sealings are a candidate because a recent study re-examines their possible archive setting. Acquire the specimen-level account before defining the classifier. [Frenez 2024](https://www.tandfonline.com/doi/full/10.1080/02666030.2024.2401206). Label observed attachments independently of inscription. Include an uncertain category and a record of each dating basis.

Start with a descriptive test of whether the proposed categories are observable by different annotators. If they are, freeze a comparison of context-only, text-only and joint predictions. Entire dies and related artifacts stay together during fitting and testing. Repeat on a second assemblage when it becomes available.

### Anchor block

Resolve two documented joins: the author's historical tablet 3786 against H904's original photographs/register, and the bangle context of the source-captioned M-1383. The current 017–031 overlap is useful for locating the latter, while its tag/pot context needs the author figure and artifact account. [Numerical source audit](../../research/literature/metrology/numerical_source_audit.md).

Once a physical candidate is settled, write the full mathematical claim including all relevant signs, face roles, unit and commodity assumptions. Obtain a new measured/countable case, then test that fixed claim. Compare it with the preserved conditional 10/8/6 calculation and report the new physical observation alongside the algebra.

## A hypothesis sheet for each run

Use the repository's experiment template and fill these fields before the outcome:

- Target observation and population, including uncertain or missing cases.
- Predictions from at least two specified models.
- Source identity, exact versions and permitted uses.
- Training/test grouping, exclusions and the measured outcome.
- Model-selection freedom, negative controls and planned sensitivities.
- What result would change the next action, and what result would stop this path.

After the run, preserve the output and add its status to the registry. A repair goes into a new dated directory with a comparison to the old endpoint. This permits later researchers to reproduce both the problem and the correction.

## Retry rules from the completed work

| Existing path | Evidence that makes a retry useful |
|---|---|
| Markov order and finite templates | A specified new diagnostic, comparison system or independent corpus, with the full selection/null procedure repeated. |
| Exact substitution families | Fresh fine-photo confirmation and a family-specific prediction. The earlier aggregate weighting result remains relevant when choosing that test. |
| Known-slot restoration | New reviewed transcriptions or a fixed new method; include frequency, confidence and whole-text outcomes. |
| Unknown gap count | Physical gap geometry or a new frozen predictor that can beat the sampling-matched constant control. |
| Printed-row image decoding | A repaired segmentation/acquisition method frozen before new reference-withheld examples. |
| Volume-to-stroke mapping | A separate known quantity/unit within the stated commodity/module scope. |
| Later cultural parallels | A dated intermediate observation or a predicted rare compound that distinguishes transmission from convergence. |

## Access and review

Collection access, photographic permissions and external annotation will determine the speed of the archaeological work. Keep third-party inputs local according to [redistribution review](../provenance/REDISTRIBUTION.md). The proposed human-participant studies need a suitable consent and research-review process before recruitment. Those requirements do not block writing protocols, constructing example tasks or reviewing existing permitted sources.

The four direction memos contain the detailed hypotheses: [archaeology](archaeology-and-iconography.md), [cross-disciplinary tests](cross-disciplinary-and-alien.md), [community proposals](community-proposals.md) and [cryptography](cryptography.md). Their source status and prerequisites should travel with each experiment when it enters the registry.
