# Root archaeological-context tests

Timestamp: 2026-10-01 23:12 UTC, before modeling outcomes.

## Main question

Do observed sign sequences carry reproducible information about an independent archaeological label beyond the known effects of inscription length and site?

This asks about contextual constraints relevant to decipherment, not sound values or a language assignment. A successful predictor does not show that the predicted object or motif is what an inscription says.

## Primary outcomes

1. Artifact register: seal versus tablet, using source object-type metadata.
2. Iconographic association: one-horned bull family versus other independently named animal motifs among seals, where enough examples exist.

Outcomes will be reported separately. Associations with site alone cannot establish semantics.

## Unit and preprocessing

- Use observed transcription and archaeological fields only. Ignore every proposed Sanskrit/English translation, `words` file, and inferred decipherment mapping.
- Primary population: source reports complete text, explicit right-to-left direction, no unknown or uncertain signs, single text part. Alternative inclusion sets are sensitivity analyses.
- Select one principal usable surface per physical object (longest inscription, ties broken by source identifier) for predictive tests. Retain all surfaces in a separate paired-surface investigation.
- Keep numbering systems distinct.
- Group exact identical principal sequences in all train/evaluation splits. Group physical artifacts by source identifier even if inscriptions differ.
- Document transitive connected components and any giant-group exclusions; no silent weakening of grouping.

## Models

- Baseline: site and length features.
- Sign augmentation: occurrence of signs, first and final signs, and adjacent sign pairs.
- Regularized logistic regression with fixed standard settings; tuning, if necessary, happens only within training folds.
- Report grouped out-of-fold log loss, balanced accuracy, and ROC AUC for binary outcomes. The primary statistic is baseline minus augmented log loss in nats per object.
- Report cluster-bootstrap uncertainty on paired per-object losses, using identical-sequence/physical-artifact groups as clusters.
- Test site transfer with training and evaluation at distinct sites where class counts permit.
- Compare observed improvement with labels permuted within site and length strata; preserve grouping and repeat the entire fitting/evaluation procedure. The null is conditional independence of observed signs and label within these strata, not a proof of a causal relationship.

## Interpretability and falsification

List high-weight signs and complete inscription frames with source IDs. Audit top findings against glyph shapes and primary archaeological descriptions. Test whether effects survive dominant-site restriction, unique-sequence weighting, and exclusion of frequent duplicate families. Do not interpret model coefficients causally.

## Candidate advance threshold

An association must survive appropriate controls and independent source checks, offer a constraint not already demonstrated in the literature, and yield concrete falsifiable predictions. Otherwise present it as replication, a method improvement, or a negative result.

## Paired-surface extension

Explore physical objects sharing principal text but differing in reverse-side glyphs or motifs. Build explicit equality/inequality constraints with catalog IDs. A matching motif/text set can constrain function without identifying the text as the depicted animal's name. New semantic claims require discrimination from ownership, institution, denomination, deity, or emblem alternatives.
