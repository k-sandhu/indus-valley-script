# Root investigation: approaches, failures and durable lessons

Scope: the four-hour October 1 investigation and October 2 repository/direction work. This account summarizes observable work and links to preserved records. It is not an exhaustive internal reasoning transcript.

## Task framing and integration

The user asked for sustained work toward substantive decipherment. We divided source/corpus work, primary-literature/novelty review and statistical methods among three agents. Root integrated their outputs and built additional restoration, independent-annotation, context and image experiments. The final deliverable was a reproducible technical report and tools; no defensible reading was established. A later publication assessment converged on a methods/benchmark paper as the strongest candidate.

See [the original work log](../../research/WORK_LOG.md), [original plan](../../PLAN.md), [report review](../../research/methods/FINAL_REPORT_REVIEW.md), and [novelty matrix](../../research/literature/evidence_and_novelty_matrix.md). The completed run lasted four hours, two minutes, twenty seconds; manuscript preparation is a later task, not part of the historical four-hour claim.

## Restoration: useful prediction, insufficient interpretation

**Attempt.** Hide one known fine-coded graphic in each eligible text and rank candidates using left/right context and available metadata. Compare with position/metadata baselines. Preserve physical and identical-string relationships in train/test splitting.

**Challenge.** An early unique-string implementation discarded aliases while choosing a representative. That loses physical links and can let related faces cross folds. The old output is retained at [superseded results](../../results/restoration_superseded_lost_aliases/SUPERSEDED.md). The remedy preserved complete alias information before constructing transitive groups, then reran and retained the corrected endpoint separately.

**Outcome.** Exact top-one improved from 17.0% to 33.8% on 8,009 masked positions. This is useful candidate ranking on deliberately hidden known signs. Rare/unseen codes failed disproportionately; macro accuracy and confidence calibration were much poorer than the headline micro score. Source/context or paired surfaces did not provide a validated meaning for the predicted sign.

**Lesson.** Keep weighted micro performance, rare-code coverage, calibration, equal-text weighting and site transfer separate. A confident graphic suggestion does not establish a word. An erased span requires an independent count constraint. [Code](../../src/restoration.py), [sensitivity](../../research/RESTORATION_SENSITIVITY.md), [frequency audit](../../research/methods/restoration_frequency_audit.json).

## Unknown gap length: the extension failed

**Attempt.** Infer both the erased sign count and its contents rather than assuming one slot.

**Challenge.** The artificial masking law differs from the natural text-length prior. A prior fitted to source texts can be wrong for a deliberately sampled gap benchmark. An initial advantage over one baseline did not survive comparison to always-one. The methods agent implemented a prior matched to the declared masking design.

**Outcome.** The design-matched count estimator reached 46.3%; always-one reached 51.1%. The tested extension did not improve missing-count recovery. This does not prove historical gap recovery impossible; physical space, edge geometry or other external constraints may help.

**Lesson.** Match the comparator to the observation/sampling mechanism. Keep count recovery separate from known-count glyph ranking. Retry with genuinely new physical gap evidence or a different frozen method, not the same prior under a renamed score. [Plan](../../research/GAP_RESTORATION_PLAN.md), [code](../../src/gap_restoration.py), [matched analysis](../../src/methods/gap_design_matched.py), [saved outputs](../../results/gap_restoration/).

## Another annotation: useful replication with dependence limits

**Attempt.** Score Mayig manual annotations after excluding Lipi source families and compatible whole texts. Map uncertain P classes to candidate sets of fine codes; keep unsupported events rather than silently dropping them.

**Challenges and remedies.** A crosswalk is not a unique identity map. Summing compatible fine-code probabilities defines a candidate event, not necessarily a normalized classifier over overlapping P labels. Source objects and catalogue photographs are shared across annotations. The methods audit clarified this estimand, tested exclusion behavior, verified probability recursion and retained five unmapped plus seven entirely unsupported events.

**Outcome.** The specified 74-face evaluation retained approximately +0.725 bits per candidate event. A later source-quality exclusion was exploratory; it was not promoted to independent confirmation. This supports robustness to a transcription change while leaving archaeological dependence and mapping uncertainty visible.

**Lesson.** Another annotation retains shared excavation sources. Candidate-event likelihood and exact fine-sign accuracy measure different outcomes. [Plan](../../research/INDEPENDENT_ANNOTATOR_PLAN.md), [code](../../src/independent_annotator.py), [audit](../../research/methods/independent_annotator_audit.json), [outputs](../../results/independent_annotator/).

## Context and paired surfaces: no authenticated semantic anchor

**Attempt.** Examine object type, site, motif and paired faces; look for a reproducible relationship that could constrain function. Test selected graphic contexts conservatively and review the source identity of promising objects.

**Challenges.** Broad site/type labels, fine findspot context, whole-object dependence and motif associations are distinct. Catalogue fields can conflict with a published physical description. Numeric IDs from different inventories can refer to entirely different objects. One highlighted substitution pair already appeared in prior literature.

**Outcome.** The work produced contextual and provenance diagnostics, not authenticated commodity/place/name readings. Source review resolved some joins (including a modern tablet record to Vats's object) but left others conditional. Initial candidate significance or pictorial plausibility was not enough for a semantic claim.

**Lesson.** A future context experiment needs source-verified findspots, object function, independently recorded contexts and matched controls. Preserve alternative explanations and publication priority. [Context code](../../src/context_study.py), [microcontext code](../../src/microcontext.py), [paired code](../../src/paired_surfaces.py), [plans](../../research/MICROCONTEXT_PLAN.md), [results](../../results/context/), [source review](../../research/MICROCONTEXT_REVIEW_SENSITIVITY.md).

## Numerals and metrology: expose conditional assumptions

**Attempt.** Examine proposed count equalities and vessel capacities as external anchors. Construct scale alternatives and request an exact integer audit.

**Challenge.** A capacity fit can trade off the count value and the unit. A numerical bound cited from a bangle context was not securely established by the original chapter. Historical software/corpus numbers required physical-object joins, not arithmetic coincidence.

**Outcome.** The scale demonstration shows identical capacity fits under rescaling. Exact algebra gives four positive solutions to the proposed two equations; 10/8/6 requires additional constraints. The selected values and equations were already published. This is a logical/source audit, not a new numeral reading.

**Lesson.** Identify parameters that are fixed by actual observations and those fixed by an assumption. Keep the premise and the exact proof separately reviewable. [Demo](../../src/identifiability_demo.py), [integer audit](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md), [metrology sources](../../research/literature/metrology/README.md).

## Printed-graphic recognition: preserve blind failure and post-reference repair

**Attempt.** Create a 687-cell numeric chart reference and test graphical recognition on original printed rows. Retain code ambiguity and compare against withheld references.

**Challenges.** Raster print texture, uncertain row boundaries, touching forms, editorial marks and clipped neighboring rows harmed segmentation. Some errors were acquisition geometry, not a mismatch between chart inventories. Manual AI-made numeric references were useful but not expert-certified.

**Outcome.** The frozen fresh20 endpoint yielded 14 matching row counts and two compatible first-candidate whole rows. Geometry repair improved development results, but the same references had already been inspected. That repair is not a fresh blind validation. The original predictions, references and geometry overlays remain separate.

**Lesson.** Freeze crops, chart, parser and scoring before evaluation; record row identity and uncertainty. Source-only repair can be technically justified while its performance still needs a fresh test. Do not turn a small printed-row pilot into a full ancient-inscription recognition claim. [Frozen endpoint](../../research/visual_digitization/font_fresh20/evaluation_frozen_endpoint.json), [geometry audit](../../research/methods/results/font_geometry_sensitivity/), [atlas](../../output/chart_atlas/index.html), [chart builder](../../src/chart_atlas.py).

## Report production and evidence integrity

The report builder enforced the minimum-duration condition and completion of the strongest 1,000-draw unique-conditioned reference. It produced an 18-page PDF. Every page was rendered and visually reviewed; numerical and source reviews led to wording corrections. The final selected evidence manifest contained 1,568 files and was verified without missing or changed files at completion. Twenty-three root and eight methods integrity checks passed in the original environment.

These historical checks remain historical. A relocated project requires new verification, and a Git checkout excludes some inputs. The preserved report is not evidence that a journal has accepted the results. [Build record](../../output/report_build.json), [visual QA](../../output/report_visual_qa.json), [verification](../../output/verification.json), [manifest](../../output/evidence_manifest.json).

## October 2: durable repository and additional direction review

The private GitHub repository was created with `gh`, its privacy checked, and GitHub Actions disabled. We retained original analysis paths to avoid rewriting frozen evidence. The import script refuses to overwrite changed files and records hashes; third-party bulk inputs and unresolved-rights witnesses remain local-only. The source-specific rights review determines what can later become public.

Practical challenge: steering messages interrupted the original copy commands. On resume, the copier found data-image hash mismatches. Existing variants were preserved in a local quarantine before restoring the original source bytes. The final import covers 16,284 files and 1,523,734,911 bytes; its manifest records the detected variants. The copier now writes to a temporary file before replacing the final path. The cause of a hash mismatch is not established by the hash alone. Runtime caches and nested Git internals were excluded. A separate registry-builder error arose from a missing design field; the parser now records a source-reference placeholder instead of joining a null value as text.

The 23 root and eight methods checks passed again in the relocated project. Source and publication dates were checked in the new direction review. A verified Enigma account, a model benchmark preprint and a disputed historical-cipher report were kept as different evidence categories.

Root wrote and executed an exact synthetic permutation-identifiability illustration: 720 consistent six-symbol relabellings give equal structural scores; two fixed sign identities leave 24 maps. This explains the need for grounded constraints but is not an Indus finding. Cryptography, numerical, contextual, cross-civilizational, human-symbol, community and alien-artifact directions are captured in separate memos and ranked by testability.

## Useful combinations attempted, and the limit of novelty

The investigation combined conservative artifact closure, explicit alternative annotation, matched gap design, full-procedure controls, source-first numerical audit and uncertainty-preserving image transcription. Each has established components. The specific implementations and measured outcomes are original project work; first invention of Markov prediction, deduplication, administrative controls or contextual substitution is not supported.

Future work should maximize discriminating evidence, not the number of plausible narratives. The strongest next moves are better physical/contextual records, independently reviewed transcriptions, an anchored known-system benchmark and a genuinely fresh evaluation. [Ranked roadmap](../directions/research-roadmap.md).
