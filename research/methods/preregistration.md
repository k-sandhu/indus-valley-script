# Conditional structure and substitution protocol

Prepared 2026-10-01 before inspecting corpus-level outcomes. These tests can advance structural decipherment; they cannot by themselves assign a sound, word, language, or translation.

## Data contract and analysis units

Input records must provide an artifact ID, side/line ID, an ordered list of sign IDs, source inventory, completeness/uncertainty flags, source reference, and any independently recorded site or object-type metadata. Keep metadata missingness explicit. Never interpret source numeric IDs as shared across sign inventories without a published concordance.

Primary corpus: complete, confidently transcribed, direction-normalized text lines of length 3 or greater, with no restoration, unknown, or damage token. A separate sensitivity analysis includes length 2. Preserve object and side identity. Do not fuse unrelated lines into invented long texts.

Group by the transitive closure of physical artifact and identical normalized whole sequence. No group may cross a train/test boundary. Report group sizes before analysis. If a component contains more than 20% of eligible records, report an additional unique-sequence analysis and acknowledge that component-level precision cannot be well estimated. Original token-weighted results are sensitivity analyses, not independent replication.

Direction is fixed by epigraphic metadata, never chosen to maximize a statistic. Repeat structure diagnostics after globally reversing all sequences; this measures orientation sensitivity, not evidence for physical reading direction. Treat seal/impression reversal according to source documentation.

## Test 1: dependence beyond position and known metadata

Compare four explicitly probabilistic models on five reproducible group folds:

1. U: training unigram distribution.
2. P: independent symbols conditional on exact inscription length and index.
3. PM: P further conditioned on the site/object-type stratum where available.
4. PMB: PM plus a previous-sign conditional distribution, with a shared bigram backoff.

All probabilities use training data only. Unknown test sign types map to one training-vocabulary UNKNOWN category. Fix the primary Dirichlet/backoff strength at 20; strengths 5 and 100 are declared sensitivities. Fit no parameter on the outer test folds. First symbols have identical scores in PM and PMB; the primary contrast uses indices after the first.

Primary endpoint: held-out mean log2 probability improvement of PMB over PM, in bits per noninitial sign. Report the corresponding relative perplexity, total signs, fold-level estimates, and a physical/sequence-group bootstrap confidence interval. A sign's local predictability is a structural property, not proof that it represents a phoneme, syllable, morpheme, or linguistic unit.

Two null checks:

- Independently shuffle each length/index column across records. This preserves exact marginal position counts and inscription lengths while removing cross-position dependencies.
- Shuffle within length/index/site/object-type cells where support permits. Report sparse cells and how many tokens can actually move. Failure to reject an overly sparse null is not evidence of independence.

Rerun the full modeling procedure on null corpora, including vocabulary construction and folds. Report the null distribution of the same held-out improvement. Do not compare in-sample conditional entropy to an out-of-sample baseline. An internal shuffle that preserves each inscription's inventory is only a weak supplementary null because it destroys position restrictions.

## Test 2: recurring substitution families

A one-slot frame is the entire sequence with exactly one sign replaced by a wildcard. Two complete equal-length inscriptions demonstrate a substitution only when all other signs match. Deduplicate whole sequences before counting. Distinct frames, distinct artifacts, and distinct sites are separate support counts; ten impressions of one seal do not supply ten independent contexts.

Enumerate sign pairs sharing a frame, and rank by the number of distinct frames. No minimum support threshold converts an association into semantic equivalence. Substitution can reflect different names, quantities, titles, grammatical categories, sign variants, commodities, or arbitrary administrative code fields.

Discovery uses the training partition only. Validation requires a predicted pair to recur in a different frame absent from training. Report aggregate transfer and each candidate's evidence; do not select a candidate on validation evidence and call it a preregistered prediction.

For positional-null comparisons, preserve exact length/index marginals; a stronger null also conditions on known metadata. Compare the aggregate transfer count for the fixed discovered pair set to held-out permutations. Exploratory per-pair p-values must be labeled and corrected for the full declared candidate family. A conservative maximum-count permutation statistic can test whether any pair exceeds the positional null without post-hoc selection.

Connected substitution graphs may have hubs that join unrelated classes. Publish direct edges and their contexts before proposing a merged class. Semantic sameness is not transitive merely because the graph is connected.

## Semantic and functional discriminants

Sequence-only evidence cannot identify semantic labels: any permutation of proposed meanings leaves an unlabeled sequence model's likelihood unchanged. A phonetic assignment additionally needs an independently justified language and writing-system model, and predictions that survive held-out inscriptions and external anchors.

Potential external tests, provided the corpus supplies independent measurements:

- Quantity field: independently annotated tally glyphs form serial alternations in identical contexts; predicted numeric magnitudes correlate with independently measured weights or quantities. The measured object cannot be the same graphic feature used to assign the number.
- Commodity field: a substitution class predicts independently recorded container contents/residue, commodity find context, or sealing package class after controlling site, period, object type, and duplication.
- Owner/title field: a putative identity segment stays invariant across independently linked impressions from one seal while a separate field changes in externally evidenced administrative contexts. Identical whole-seal repetitions alone do not distinguish owner from commodity or office.
- Terminal function: terminal modules predict object use or iconography in artifact/sequence-held-out tests beyond length, site, material, and period. Association can ground a functional hypothesis; it does not select a spoken reading.

A strong next claim is therefore an explicit restriction such as 'these signs alternate in this slot across several independent frames and contexts' plus a risky external prediction. 'This sign means king/grain/fish' without an independent test is not a decipherment advance.

## Failure and reporting rules

Publish excluded records and reasons, random seeds, input hashes, normalization code, orientation rules, group assignment, direct candidate contexts, and all primary/null results. Distinguish replication of known order/terminal effects from a new robustness result. Describe a null, nonreplication, or confounded result plainly. Avoid replacing an unsuccessful primary endpoint with a favorable exploratory result.

## Added template robustness test, before its outcomes

The original position-null test does not control latent template identity. A further post-pilot robustness analysis therefore fits a mixture of independent categorical slot distributions for each exact inscription length. A template is a latent component, not an assigned grammatical or semantic category. The component mixture weights can vary by observed site/object type with fixed backoff strength 20. Given a component, the sign positions are independent; after marginalizing the unknown component, adjacent and distant signs can nevertheless become dependent.

Use the original five artifact/sequence-group folds. Select maximum component count from {1,2,4,8,16}, and slot smoothing from {5,20,100}, by three inner group folds using mean held-out noninitial log probability. Restrict actual components for a length to at most floor(training records at that length/10), with a minimum of one. Each component's slot prior is the training-only length/position distribution smoothed toward the training unigram with strength 100. Fit two seeded starts for at most 40 EM iterations, retaining the better training likelihood. No outer test row participates in initialization, fitting, vocabulary construction, or selection.

For next-sign scoring, update the mixture component posterior using only earlier observed signs in that inscription. Compare the selected template model against the training-only selected U/P/PM baseline and PMB model. Report paired group-bootstrap intervals. If a slot-template mixture explains the Markov gain, do not claim a dependency beyond templates. If it does not, the result concerns this declared template family and finite capacity, not all possible nonlinguistic systems or an identification of language.

## Primary literature anchors

- Rao et al. (2009), *A Markov model of the Indus script*, PNAS, DOI [10.1073/pnas.0906237106](https://doi.org/10.1073/pnas.0906237106). Probabilistic sequencing, restoration, and examples of functional interchangeability precede this project; these alone are not novel.
- Recchia and Louwerse (2016), *Archaeology Through Computational Linguistics*, Cognitive Science, DOI [10.1111/cogs.12311](https://doi.org/10.1111/cogs.12311). Provenance prediction provides a precedent for external metadata grounding. Geography association alone does not identify place-name signs.
- Sproat (2010), [*Reply to Rao et al. and Lee et al.*](https://aclanthology.org/J10-4017/). A poorly chosen random/rigid comparison class cannot establish a linguistic/nonlinguistic distinction.
- [*On the Non-Specificity of Statistical Measures Used in Script Decipherment*](https://arxiv.org/abs/2608.02999) (2026 preprint, not peer reviewed). An explicit nonlinguistic compositional generator motivates calibrated administrative nulls and warns against dictionary-coverage claims.

## Post-audit implementation corrections, 2026-10-02 00:18 UTC

This is a local declared analysis protocol, not a registration in an external registry. The original implementations kept the observed physical/sequence groups and outer folds fixed while shuffling signs. That differs from Test 1's stated instruction to rerun folds. The archived fixed-partition nulls are therefore reference diagnostics; `nested_joint_null.py` now reruns grouping, outer folds, inner training-only model choice, and prediction on every shuffled corpus. The observed statistic is unchanged.

Test 2's fixed-discovery held-out permutations are valid conditional diagnostics for one fold, but the five overlapping training sets complicate their aggregate joint interpretation. `substitution_joint_null.py` therefore repeats grouping, fold allocation, training discovery, and entirely-new-frame transfer for every full-corpus null. It is a stricter post-audit sensitivity and must not be retroactively described as the original endpoint. Raw whole-corpus maximum-support tests already included the candidate search.

Unique-sequence deduplication initially retained only the first record's physical artifact identity. The repaired loader preserves all original artifact aliases on every retained unique string, and grouping takes their transitive union. The six integrity tests include an explicit example where two otherwise different texts share an artifact through a dropped duplicate. Results named `nested_unique` and `classaware_unique` are superseded by `*_preserved_aliases`. Full-corpus analyses and full-graph unique frame counts do not depend on this repair. Site-transfer filters now exclude intersection with any preserved alias, and separate alias-safe outputs retain the earlier results for audit.

The office-routing generator is an assay-specific nonphonetic control: its signs denote office entities and its routes obey legal handoffs, without encoding speech. It does not propose a historical Indus system. Conceptual nonspecificity is established prior, including [Sproat's 2010 *Last Words*](https://aclanthology.org/J10-3012/); the present control evaluates that limitation against this project's selected latent-template model.

## Additional site-transfer correction, 2026-10-02 00:52 UTC

Direct exact-string/physical-alias removal does not always remove every member of a transitive physical/string component. The original full-record site transfer left 21 such relatives in Mohenjo-daro training and 33 in Lothal training. The repaired function removes every entire component touching the held-out site. Separate `transitive_site_transfer.json` outputs preserve superseded numbers for audit. Revised full-record gains are 0.71527, 0.89300, and 1.01438 bits for Mohenjo-daro, Harappa, and Lothal; the current unique sensitivity is unchanged at the stated precision. Eight integrity tests now include both physical-alias and transitive-component exclusion examples. This correction does not change ordinary grouped cross-validation or the probability model.
