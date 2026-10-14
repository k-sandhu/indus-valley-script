# Research roadmap

Reviewed 2 October 2026. The order follows the dependencies in the evidence: a reliable observation can support several tests, while a reading fitted to the existing texts can be hard to tell apart from its alternatives.

## Completed controls and the next required inputs

Our follow-up experiments of 2 October tested the main computational ideas behind this roadmap. The table shows what each result allows next without repeating the same controls.

| Completed line | Result | New input needed |
|---|---|---|
| Restoring a sign hidden at a known position | Using the two preceding signs (second order) raises top-one accuracy, the share of signs ranked first, to 37.27%; using one (first order) gives the better probability score | A new block of reviewed images and transcriptions, or a specified predictor that handles segmentation and an unknown number of missing signs |
| Conditional references: chance comparisons built by shuffling records | In simulated populations with known dependence, shuffling whole objects or paired face readings rejects at close to the declared rate; shuffling individual records inflates rejections for copies and for faces of one object | Independently established object dependence, selection history and groups of similar recording quality |
| Symbol mapping: matching encoded symbols one-to-one with those of a known reference system | Choosing the record model from the reference alone recovers 309/384 generated maps; mixtures of same-length record forms improve several conditions, with exact identification checks on the generating populations and the search failures kept | A justified external reference, a rule fixed in advance for the number of record forms, estimated form mixtures in the encoded records, or new systems with uncertain record boundaries |
| Numerical observations | Physical relations (what a container or account holds) identify ratios; counts fix scale; an independent inventory of the whole pool corrects many wrong local assignments | A source-joined physical inventory or count with independently recorded completeness and units |
| Artifact operation | Object lists from the Harappa, Lothal and Kanmer publications restore object–context joins; a flat stamp on curved clay can bias which graphics are seen | Measured groove geometry, original bore and wear observations, replica results or specimen-level context |

Exact outputs, failures and retry conditions are in the [experiment registry](../experiments/registry.json). [Paper 002](../../papers/002-conditional-reference-laws/manuscript.md), [Paper 003](../../papers/003-physical-observations/manuscript.md) and [Paper 004](../../papers/004-reference-model-selection/manuscript.md) give the methods for shuffled comparisons, physical observations and symbol mapping. The remaining archaeological work depends chiefly on better linked observations.

The final controls narrow the next computational choices. Extra shrinkage for two-sign histories, chosen by probability loss, returns the first-order model in every fold. When recording quality is shared across an object's signs, the original prediction statistic barely separates a broad shuffle from a quality-conditioned one, while a fresh statistic of agreement between adjacent signs separates them strongly. In the saved cases of a surviving wrong numerical decoder, checking counts first needs fewer checks than choosing checks by coefficient rank (how many new independent equations each adds). Three-form mixtures help when the reference keeps the forms distinct; heavy overlap and small references still fail. Each result has its own frozen output and names the changed premise that would justify another run.

## First decisions

Our first investigation produced a working prediction benchmark, source-linked audits and several failures worth keeping. With repeated whole texts removed, a model that uses the preceding sign predicted each non-initial sign about 0.848 bits better than the best model without it, under the declared filters. Our estimate of how many signs a gap has lost was right 46.3% of the time, compared with 51.1% for always guessing one. A frozen image-reading pipeline tested on 20 new printed inscription rows returned a fully compatible first-choice reading for two complete rows. These results point to two immediate needs: source-reviewed observations, and a clear separation between predicting a sign hidden at a known position and recovering a damaged inscription, where the number and boundaries of lost signs are unknown. [Experiment registry ROOT-02, ROOT-08, ROOT-17](../experiments/registry.json), [methods findings](../../research/methods/FINDINGS.md).

The next cycle should have one primary target: predicting an externally observed use or quantity on a new artifact family, a group of physically linked objects such as the impressions of one seal. Run image and identity work, and one cheap control on a known system, alongside it. Set aside a new block of objects before looking at their inscriptions or measured quantities.

## Ranked work

| Rank | Project and expected result | Inputs | Decision and stopping rule | Effort |
|---|---|---|---|---|
| 1 | Source-reviewed feature and identity set | Permitted original images, accession and excavation joins, independent feature annotation | Keep disagreements and alternative segmentations. Release an annotation block for testing only after its rules and exclusions are fixed. | Days for a small existing-image set; access-dependent for new photographs. |
| 2 | Physical-use prediction | Attachment traces on sealing backs, object form, find units and dates, externally assigned use categories | Text features must predict withheld objects better than context and production baselines. A gain found only among impressions of one die calls for broader observations. | Several weeks if specimen records are available. |
| 3 | Manufacture versus meaningful variation | Fine glyph and animal features, tool marks, material and carving groups | Test whether modifiers follow a production group or move with an independently observed category into a different group. Stop interpreting where features cannot be reliably seen. | Small feature pilot first. |
| 4 | Paired-surface constraints | Complete opposite faces, mould and copy relationships, fine sign identity | Fix a graph of related faces and copies, then predict an unseen variant. Compare workshop, owner, commodity and entitlement explanations, with explicit exceptions. | Feasible with selected published families; needs expert image review. |
| 5 | An external quantity anchor | A separately measured complete vessel, or independently counted contents, in a specified module or class | Fix the units, the value of each graphic and the physical reconstruction before opening the target measurement. Keep failed and ambiguous cases. | Highest potential value for meaning; depends on access. |
| 6 | Secure chronology and regional transfer | Independently dated strata, mixed-context flags, comparable recovery methods | Predict a withheld cohort or site; measure sensitivity to residual objects (older material in later layers), genre and material. | Longer archaeological data work. |
| 7 | Controlled study of unfamiliar artifacts | Constructed objects with concealed answer keys | Test whether dimensions, operation and paired outputs improve recovery of function; record confident wrong interpretations. | Low acquisition cost; work with participants needs an appropriate research review. |
| 8 | Comparing accounts and marks of other civilisations | Source-preserved layout and identity from Proto-Elamite, khipu, Gulf seals or later coins | Match the property under test and keep spatial and hierarchical structure. Choose a defined diagnostic to assess. | Pilot possible with permitted existing resources. |
| 9 | Test of historical continuity | Dated intermediate samples, rare compound features, evidence of contact or shared practice | Compare transmission with independent invention of shapes; hold out a region or period. Publish the intermediate evidence and the missing intervals. | Months; access to samples decides feasibility. |
| 10 | Frozen comparison of languages or readings | Complete candidate rules, linguistic reconstructions, an independent anchor or a risky external prediction | Score all withheld cases with matched degrees of freedom. Add freedom only in a separately labelled model. | Prepare in parallel; decisive evidence may take longer. |

The ranking favours experiments that first improve the observations and then predict evidence other than the transcribed signs. A verified bilingual or an independently counted object would change the order at once.

## A bounded next cycle

### Observation block

Select 30 objects for source review from more than one production or context group, with all available faces of each. Split them into a development subset and a reserved subset, keeping each physical family on one side. Settle whether each image shows the seal (the matrix) or its impression, which photographs repeat, stroke heights and compound signs. Record disagreements about individual features, and keep unreadable marks as missing observations. Use the stored sources and the [catalogue caveats](../provenance/catalogue-caveats.md) to choose the first cases.

The result is a table of identities and features, source locations and an uncertainty report. A new glyph-recognition model can then be evaluated on a reserved block it has never seen, scoring segmentation, signs per row and fine sign codes separately. Earlier improvements made on development data against a corrected reference remain available for choosing a method; the new block supplies the evaluation.

### Context block

Audit one assemblage whose attachment traces or find context can be recovered. Lothal's sealings are a candidate because a recent study re-examines their possible setting in an archive. Obtain the specimen-by-specimen account before defining the classifier. [Frenez 2024](https://www.tandfonline.com/doi/full/10.1080/02666030.2024.2401206). Label the observed attachments without reference to the inscriptions, include an uncertain category, and record how each object was dated.

Start with a descriptive test of whether different annotators can observe the proposed categories consistently. If they can, fix in advance a comparison of predictions from context alone, from text alone and from both. All impressions of one die and other related artifacts stay together, in fitting or in testing. Repeat on a second assemblage when one becomes available.

### Anchor block

Resolve two documented joins in Fuls's numerical proposal. The first is whether his tablet 3786, numbered in the older ICIT database, is H904; H904's original photographs and register can decide it. The second is the bangle context of M-1383, named in his figure caption. The current catalogue's M-1383 record contains the proposal's sign pair 017–031, which helps locate the object, but calls it a clay tag, so the author's figure and the artifact account are needed. [Numerical source audit](../../research/literature/metrology/numerical_source_audit.md).

Once a physical candidate is settled, write out the full mathematical claim with all relevant signs, face roles, and unit and commodity assumptions. Obtain a new case that can be measured or counted, then test that fixed claim. Compare it with the preserved conditional calculation that selects the values 10/8/6, and report the new physical observation alongside the algebra.

## A hypothesis sheet for each run

Use the repository's experiment template and fill these fields before the outcome is known:

- Target observation and population, including uncertain or missing cases.
- Predictions from at least two specified models.
- Source identity, exact versions and permitted uses.
- How records are grouped into training and test sets, exclusions and the measured outcome.
- How freely the model may be chosen, negative controls and planned sensitivity analyses.
- What result would change the next action, and what result would stop this path.

After the run, preserve the output and add its status to the registry. A repair goes into a new dated directory with a comparison to the old frozen output, so that later researchers can reproduce both the problem and the correction.

## Retry rules from the completed work

| Existing path | Evidence that makes a retry useful |
|---|---|
| Markov order (how many preceding signs help prediction) and finite template models | A specified new diagnostic, comparison system or independent corpus, with the full model-selection and shuffled-corpus procedure repeated. |
| Exact substitution families (signs that replace one another in otherwise identical texts) | New confirmation from detailed photographs and a prediction specific to one family. The earlier aggregate weighting result remains relevant when choosing that test. |
| Restoring a sign hidden at a known position | New reviewed transcriptions or a fixed new method; report frequency, confidence and whole-text outcomes. |
| Estimating how many signs a gap has lost | Physical gap geometry, or a new frozen predictor that beats always guessing one sign under the same gap-sampling design. |
| Reading printed inscription rows from images | A repaired segmentation and image-capture method, frozen before testing on new examples whose transcriptions are withheld. |
| Mapping vessel volume to stroke counts | A separate known quantity and unit within the stated commodity and module. |
| Later cultural parallels | A dated intermediate observation, or a predicted rare compound that distinguishes transmission from convergence. |

## Access and review

Collection access, photographic permissions and external annotation will set the pace of the archaeological work. Keep third-party inputs local according to the [redistribution review](../provenance/REDISTRIBUTION.md). The proposed studies with human participants need a suitable consent and research-review process before recruitment. Those requirements do not prevent writing protocols, constructing example tasks or reviewing existing permitted sources.

The four direction memos contain the detailed hypotheses: [archaeology](archaeology-and-iconography.md), [cross-disciplinary tests](cross-disciplinary-and-alien.md), [community proposals](community-proposals.md) and [cryptography](cryptography.md). Their source status and prerequisites should travel with each experiment when it enters the registry.
