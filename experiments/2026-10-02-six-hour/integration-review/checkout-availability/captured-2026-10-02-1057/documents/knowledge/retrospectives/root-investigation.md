# Root investigation: approaches, failures and durable lessons

Scope: the four-hour October 1 investigation and October 2 repository/direction work. This account summarizes observable work and links to preserved records. It is not an exhaustive internal reasoning transcript.

## Task framing and integration

The user asked for sustained work toward substantive decipherment. We divided source/corpus work, primary-literature/novelty review and statistical methods among three agents. Root integrated their outputs and built additional restoration, independent-annotation, context and image experiments. The final deliverable was a reproducible technical report and tools; no defensible reading was established. A later publication assessment converged on a methods/benchmark paper as the strongest candidate.

See [the original work log](../../research/WORK_LOG.md), [original plan](../../PLAN.md), [report review](../../research/methods/FINAL_REPORT_REVIEW.md), and [novelty matrix](../../research/literature/evidence_and_novelty_matrix.md). The completed run lasted four hours, two minutes, twenty seconds; manuscript preparation is a later task, not part of the historical four-hour claim.

## Restoration with a known missing slot

**Attempt.** Hide one known fine-coded graphic in each eligible text and rank candidates using left/right context and available metadata. Compare with position/metadata baselines. Preserve physical and identical-string relationships in train/test splitting.

**Challenge.** An early unique-string implementation discarded aliases while choosing a representative. That loses physical links and can let related faces cross folds. The old output is retained at [superseded results](../../results/restoration_superseded_lost_aliases/SUPERSEDED.md). The remedy preserved complete alias information before constructing transitive groups, then reran and retained the corrected endpoint separately.

**Outcome.** Exact top-one improved from 17.0% to 33.8% on 8,009 deliberately masked positions. Rare and unseen codes failed disproportionately; macro accuracy and confidence calibration were much poorer than slot-weighted accuracy.

**Lesson.** Report slot-weighted performance alongside rare-code coverage, calibration, equal-text weighting and site transfer. An erased span also needs a count estimate, which the next experiment tests. [Code](../../src/restoration.py), [sensitivity](../../research/RESTORATION_SENSITIVITY.md), [frequency audit](../../research/methods/restoration_frequency_audit.json).

## Unknown gap length: the extension failed

**Attempt.** Infer both the erased sign count and its contents rather than assuming one slot.

**Challenge.** The artificial masking law differs from the natural text-length prior. A prior fitted to source texts can be wrong for a deliberately sampled gap benchmark. An initial advantage over one baseline did not survive comparison to always-one. The methods agent implemented a prior matched to the declared masking design.

**Outcome.** The design-matched count estimator reached 46.3%; always-one reached 51.1%. A next attempt could incorporate measured gap width, edge geometry or surviving strokes.

**Lesson.** Match the comparator to the observation mechanism and evaluate count recovery separately from known-count glyph ranking. A retry needs a new predictor or measured gap evidence. [Plan](../../research/GAP_RESTORATION_PLAN.md), [code](../../src/gap_restoration.py), [matched analysis](../../src/methods/gap_design_matched.py), [saved outputs](../../results/gap_restoration/).

## Another annotation: useful replication with dependence limits

**Attempt.** Score Mayig manual annotations after excluding Lipi source families and compatible whole texts. Map uncertain P classes to candidate sets of fine codes; keep unsupported events rather than silently dropping them.

**Challenges and remedies.** The crosswalk supplies sets of compatible codes. Summing their fine-code probabilities defines a candidate event; overlapping P labels need a separate rule if used as classifier categories. Both annotations share source objects and catalogue photographs. The methods audit clarified the score, tested exclusions, verified probability recursion and retained five unmapped plus seven entirely unsupported events.

**Outcome.** The specified 74-face evaluation retained approximately +0.725 bits per candidate event. A later source-quality exclusion was exploratory; it was not promoted to independent confirmation. This supports robustness to a transcription change while leaving archaeological dependence and mapping uncertainty visible.

**Lesson.** Another annotation retains shared excavation sources. Candidate-event likelihood and exact fine-sign accuracy measure different outcomes. [Plan](../../research/INDEPENDENT_ANNOTATOR_PLAN.md), [code](../../src/independent_annotator.py), [audit](../../research/methods/independent_annotator_audit.json), [outputs](../../results/independent_annotator/).

## Context and paired surfaces

**Attempt.** Examine object type, site, motif and paired faces; look for a reproducible relationship that could constrain function. Test selected graphic contexts conservatively and review the source identity of promising objects.

**Challenges.** Broad site/type labels, fine findspot context, whole-object dependence and motif associations are distinct. Catalogue fields can conflict with a published physical description. Numeric IDs from different inventories can refer to entirely different objects. One highlighted substitution pair already appeared in prior literature.

**Outcome.** The work produced contextual and provenance diagnostics. Source review connected a modern tablet record to Vats's object and retained unresolved joins with their missing witnesses. The observed associations now supply targets for a source-reviewed context test.

**Lesson.** A future context experiment needs source-verified findspots, object function, independently recorded contexts and matched controls. Preserve alternative explanations and publication priority. [Context code](../../src/context_study.py), [microcontext code](../../src/microcontext.py), [paired code](../../src/paired_surfaces.py), [plans](../../research/MICROCONTEXT_PLAN.md), [results](../../results/context/), [source review](../../research/MICROCONTEXT_REVIEW_SENSITIVITY.md).

## Numerals and metrology: expose conditional assumptions

**Attempt.** Examine proposed count equalities and vessel capacities as external anchors. Construct scale alternatives and request an exact integer audit.

**Challenge.** A capacity fit can trade off the count value and the unit. A numerical bound cited from a bangle context was not securely established by the original chapter. Historical software/corpus numbers required physical-object joins, not arithmetic coincidence.

**Outcome.** The scale demonstration shows identical capacity fits under rescaling. Exact algebra gives four positive solutions to the published two equations; the published 10/8/6 selection requires additional constraints. The audit identifies the source observations needed to distinguish those solutions.

**Lesson.** Identify parameters that are fixed by actual observations and those fixed by an assumption. Keep the premise and the exact proof separately reviewable. [Demo](../../src/identifiability_demo.py), [integer audit](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md), [metrology sources](../../research/literature/metrology/README.md).

## Printed-graphic recognition: preserve blind failure and post-reference repair

**Attempt.** Create a 687-cell numeric chart reference and test graphical recognition on original printed rows. Retain code ambiguity and compare against withheld references.

**Challenges.** Raster print texture, uncertain row boundaries, touching forms, editorial marks and clipped neighboring rows harmed segmentation. Some errors were acquisition geometry, not a mismatch between chart inventories. Manual AI-made numeric references were useful but not expert-certified.

**Outcome.** The frozen fresh20 endpoint yielded 14 matching row counts and two compatible first-candidate whole rows. Geometry repair improved the same development rows after their references had been inspected. Its accuracy needs a new withheld block. The original predictions, references and geometry overlays remain separate.

**Lesson.** Freeze crops, chart, parser and scoring before evaluation; record row identity and uncertainty. Printed chart rows provide a development task, while artifact photographs need a separately specified evaluation. [Frozen endpoint](../../research/visual_digitization/font_fresh20/evaluation_frozen_endpoint.json), [geometry audit](../../research/methods/results/font_geometry_sensitivity/), [atlas](../../output/chart_atlas/index.html), [chart builder](../../src/chart_atlas.py).

## Report production and evidence integrity

The report builder enforced the minimum-duration condition and completion of the strongest 1,000-draw unique-conditioned reference. It produced an 18-page PDF. Every page was rendered and visually reviewed; numerical and source reviews led to wording corrections. The final selected evidence manifest contained 1,568 files and was verified without missing or changed files at completion. Twenty-three root and eight methods integrity checks passed in the original environment.

The relocated project received a separate verification. Its local source inputs and selected Git files have different scopes, recorded in the reproduction guide. [Build record](../../output/report_build.json), [visual QA](../../output/report_visual_qa.json), [verification](../../output/verification.json), [manifest](../../output/evidence_manifest.json).

## October 2: durable repository and additional direction review

The private GitHub repository was created with `gh`, its privacy checked, and GitHub Actions disabled. We retained original analysis paths to avoid rewriting frozen evidence. The import script refuses to overwrite changed files and records hashes; third-party bulk inputs and unresolved-rights witnesses remain local-only. The source-specific rights review determines what can later become public.

Practical challenge: steering messages interrupted the original copy commands. On resume, the copier found data-image hash mismatches. Existing variants were preserved in a local quarantine before restoring the original source bytes. The final import covers 16,284 files and 1,523,734,911 bytes; its manifest records the detected variants. The copier now writes to a temporary file before replacing the final path. The cause of a hash mismatch is not established by the hash alone. Runtime caches and nested Git internals were excluded. A separate registry-builder error arose from a missing design field; the parser now records a source-reference placeholder instead of joining a null value as text.

The 23 root and eight methods checks passed again in the relocated project. Source and publication dates were checked in the new direction review. A verified Enigma account, a model benchmark preprint and a disputed historical-cipher report were kept as different evidence categories.

Root wrote and executed an exact synthetic permutation-identifiability illustration: 720 consistent six-symbol relabellings give equal structural scores; two fixed sign identities leave 24 maps. It supplies a starting point for the new anchored mapping benchmark. Cryptography, numerical, contextual, cross-civilizational, human-symbol, community and alien-artifact directions are captured in separate memos and ranked by testability.

The first push was rejected by GitHub's email-privacy protection. The repository now uses the account's GitHub noreply address; the unpublished initial commit was amended and pushed successfully. A byte-preserving `.gitattributes` rule prevents Git's automatic line-ending conversion from changing recorded source and code-snapshot hashes. The initial selected payload was checked for local-only source exclusions and known credential patterns.

## Integration and next questions

The investigation combined artifact closure, alternative annotation, matched gap design, full-procedure controls, source-first numerical audit and uncertainty-preserving image transcription. Related work records their established components. The project adds inspectable implementations, measured outcomes and a record of the defects that changed the evaluations.

The next questions concern physical context, independently reviewed transcriptions, anchored known-system recovery and a fresh image evaluation. Each has a specific evidence requirement in the [ranked roadmap](../directions/research-roadmap.md).
