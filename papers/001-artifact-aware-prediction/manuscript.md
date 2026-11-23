# Artifact-aware evaluation of Indus sign prediction: local dependencies, annotation uncertainty, and restoration limits

Publication status: complete private working manuscript, originally frozen 2 October 2026 and updated 22 November 2026 with pre-registered full-corpus alias-clean and near-variant-clean restoration refits; submission and peer review are pending. All original 2 October 2026 frozen results remain preserved and dated separately from the post-audit refits. Authorship, affiliations, acknowledgements and the target venue remain to be assigned. We used AI assistance for the computational analyses and for preparing the manuscript. Independent epigraphic review of the transcriptions and source inspections remain tasks before submission; see [SUBMISSION-CHECKLIST.md](SUBMISSION-CHECKLIST.md).

## Abstract

We measure how much neighbouring signs help predict Indus signs in held-out texts, controlling for related artifacts, repeated texts, the granularity of sign codes and the design of restoration tests. A selected derivative transcription has 2,107 complete, single-line, right-to-left records of at least three signs, with 1,596 distinct strings; linking records that share an artifact or a string, transitively, gives 1,526 components, which cross-validation never splits. With five-fold cross-validation and training-only model selection, the preceding sign adds 0.890 bits per noninitial sign (each sign after the first) to a baseline using length, position, site and object type (component-bootstrap interval 0.817–0.965, conditional on the fitted models). Counting each string once, with the artifact identifiers of all its copies, gives 0.848 bits. No gain among 1,000 refitted corpora with signs shuffled within length, position, site and object type reached the observed value; the same holds in a post-pilot sensitivity analysis on distinct strings whose shuffles keep every string distinct. An independent second transcription, with related records removed from training, gives 0.725 bits per noninitial sign position on 74 scored faces (0.551–0.899). With one sign hidden at a known position, the original is ranked first in 16.99% of cases from position and length, 33.81% with the neighbouring signs and 34.59% with a conventional first-order Markov model. A later second-order model reaches 37.27%, 2.684 percentage points above first order (1.990–3.397), but its log loss rises by 0.128 bits (0.096–0.159); selecting its smoothing by held-out loss returns the first-order model in every fold. Estimating how many signs an internal gap lost succeeds in 46.30% of cases after matching the random procedure that made the gaps, below the 51.07% of always guessing one.

A later full-corpus audit across all 5,680 observed faces found that transitive links through shared short faces and normalized site identifiers still bridged 9.43% of known-slot queries across the original folds, while direct near variants (one sign edit away or sharing a graphic base-shape sequence) connected 27.34%. Refitting all models from scratch under zero full-corpus alias leakage (Split 2, 1,361 components) lowers second-order Markov accuracy by 0.974 percentage points to 36.30%, while bidirectional modified Kneser–Ney combined with graphic-base-family and skip-bigram predictors holds 40.42% top-one accuracy, 62.38% top-five inclusion, 4.497 bits per slot and 1.28% expected calibration error. Under a near-variant-clean split with zero alias, one-edit and base-shape crossings (Split 3, 964 components), the second-order Markov lead over first order shrinks from 2.684 to 0.887 percentage points with worse log loss, whereas modified Kneser–Ney pooled with graphic base-shape families holds 37.71% top-one accuracy, 60.38% top-five inclusion and 4.690 bits per slot (+4.56 percentage points and −0.603 bits over first order, cutting calibration error by more than half relative to ungrouped modified Kneser–Ney). These measurements concern synthetic prediction on the transcribed sign codes of this selected population and do not transfer directly to physically damaged gaps of unknown length.

## 1. Introduction

The Indus inscriptions are short sign sequences whose order we can observe, while their linguistic status, language or languages, segmentation and referents remain disputed. A model could predict them well by learning a recurring administrative formula, a family of production templates or the constraints of a language. Prediction therefore measures distributional structure; a reading needs other evidence.

We ask whether neighbouring signs improve held-out prediction once we account for exact text length, the sign's position (its slot), site and object type, and known relationships among artifacts. We also separate two restoration problems that are often discussed together: predicting a missing sign at a known slot, and inferring how many signs an internal gap of unknown length lost.

Both questions depend on the unit of evidence. Two photographs may show one artifact, two catalogue numbers may name one object, and separate artifacts may carry identical inscriptions. Splitting such records between training and test rewards memorization, while removing all repeated strings changes the population measured and can discard the artifact identifiers that keep related records together. We therefore keep, for each retained string, the identifiers of every artifact that carries it (its physical aliases), and report results for all records and for one record per distinct string.

We also test whether the result depends on one transcription. An independent manual transcription of the same published sources labels signs with coarser classes, each compatible with a set of our sign codes; the sets can overlap. We score each position as the event that the true code lies in its candidate set, summing over compatible sequences with a forward recursion, after removing the shared source objects and compatible strings from training.

Some safeguards were added after exploratory analysis or audits of code and sources, and each result records the stage at which it was specified. Detailed procedures are in [methods.md](methods.md), and each principal claim has a [claim–evidence entry](claim-evidence-map.md).

## 2. Related work

Rao et al. (2009) already fitted a Markov model with modified Kneser–Ney smoothing, examined functional interchangeability of signs and predicted missing signs on a corpus with repeated inscriptions removed [R1]; Yadav et al. (2010) evaluated n-grams with Witten–Bell smoothing and Katz backoff using a 90%-probability candidate-set criterion [R11]. Because Markov restoration, modified Kneser–Ney smoothing and simple deduplication come from that earlier work, we focus instead on how evaluation design and model pooling change the measured performance: isolating related artifacts and short shared faces transitively across all 5,680 observed faces, nesting hyperparameter tuning strictly inside each training set, comparing exact first-guess accuracy against probability loss and calibration, and pooling modified Kneser–Ney with graphic base-shape classes under zero-leakage and near-variant-clean splits. On 2 October 2026 we added conventional first-order and second-order Markov comparators using unigram-prior smoothing on our hidden slots; in the 6 October and 22 November 2026 refits (Section 5.6) we added finite-vocabulary interpolated bidirectional modified Kneser–Ney [R10] under the shared protocol.

Earlier distributional studies describe initial and terminal classes, recurrent clusters and the interchangeability of modified "fish" signs. Yadav's 2019 overview reports both M267 and M391 before M99 as predominantly initial pairs. Mahadevan's 1982 and 1986 studies discuss similar terminal environments and replacement among modified fish. Khanna and Merriam (2025) use shared contexts and substitution-resistant pairs. Our substitution frames, texts identical except at one position, recover these broad classes, and we test the classes under different weighting and transfer rules [R2–R4].

Koskenniemi and Parpola (1980) distinguish strict and loose duplicate relationships, including uncertainty and fragments. For the present export we link records with identical intact strings or a shared physical artifact, and follow these links transitively. The retained audit of the primary source supplies their definitions and page locations [R5].

Sproat (2010) tests whether structural statistics are specific to writing, using comparison systems. Nair's April 2026 unreviewed preprint compares generators of administrative templates with attested symbol corpora, with inference limited to the tested model families. We use a constructed office-routing code to test whether our held-out predictive and template comparisons are specific to language [R6–R7].

## 3. Data and observational scope

### 3.1 Derivative transcription corpus

The main input is [lipi_clean_rtl_singleline.jsonl](../../data/normalized/lipi_clean_rtl_singleline.jsonl), from a fixed version of a derivative transcription export. Its SHA-256 is `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`. The export accompanies a disputed decipherment; we used only its transcriptions and observational metadata, and excluded its proposed sounds, Sanskrit readings and translations. The retained [normalization code](../../research/corpus/normalize_lipi.py) and [source definitions](../../data/normalized/source_definitions.json) document acquisition and normalization.

Each record is one transcribed face, and its string is its complete sequence of the export's sign codes, which we call fine codes. The cleaned input has 2,930 complete, single-line records explicitly read right to left, with at least two signs and 1,859 distinct sequences. The main structural analysis requires at least three signs, leaving 2,107 records and 1,596 distinct sequences. Codes for missing signs and blank space are excluded from the sign alphabet.

The catalogue stores strings as visual left-to-right lists, which we reverse into reading order following its documented conventions. Fuls's explicit example begins with the rightmost sign; the source catalogue shows seals as impressions, so its direction metadata describe the impression. The [orientation clarification](../../research/corpus/orientation_clarification.json) keeps the primary examples. We also evaluate reversed sequences as a sensitivity check.

### 3.2 Dependence and unique-string populations

We link eligible records that share a physical artifact identifier or an identical complete string and take the transitive closure: if A is linked to B and B to C, all three form one connected component. The main population has 1,526 components, the largest with 36 records. Cross-validation keeps every component whole, and we call such folds component-held-out. This removes the leakage we know about; links through a shared mould, workshop, deposit or catalogue history may remain undetected.

The unique-string population keeps one representative per whole string, chosen by a fixed rule, together with the physical aliases of all its copies. It has 1,596 strings in 1,526 components, the largest with nine strings. The representative carries one site and object type, so unique-string weighting measures a different population. Earlier runs that lost aliases during deduplication are superseded.

Including two-sign records creates a component containing 804 of the 2,930 records, which makes fold balance and independence harder to assess. The unique-string version of that analysis accompanies the short-text analysis in the [result index](../../research/methods/RESULT_INDEX.json).

### 3.3 Coding compatibility and independent annotation

The MIT-licensed Mayig corpus [R8] is an independent manual transcription of faces from the same historical sources. Its annotator labels each sign with a class beginning with P (a P label), and a [crosswalk](../../data/normalized/mayig_wells_class_crosswalk.json) lists the fine codes compatible with each class; a class can cover several codes, and classes can overlap. Shared class membership is weaker than photographic identity of signs, and pairwise compatibility is not transitive.

Of the 86 faces marked clear, single-line and at least three signs long, five contain a class missing from the crosswalk and seven a position with no candidate code seen in training. The remaining 74 faces form 73 groups linked by shared artifacts or identical P-label sequences, with 315 noninitial candidate events (positions after the first, each represented by its candidate set). Twenty scored faces include some candidates absent from training; a sensitivity analysis uses the other 54. The test output keeps every excluded face and reason.

### 3.4 Access and source uncertainty

The derivative export has unresolved redistribution terms and remains a private research input. The linked files carry their own licences and local preservation records. Submission needs a reproducible access route and explicit decisions on what to release.

The check of the transcriptions against photographs is incomplete. Source audits found differences in how compound signs are divided, uncertain class assignments, and problems with identifiers and catalogue versions. The main numbers describe these transcriptions under the stated filters; claims about the ancient signs need photographic review even where the computations on the frozen codes are correct.

## 4. Methods

### 4.1 Predictive models and training-only selection

Each model's vocabulary is the set of fine codes seen in training plus one `UNKNOWN` state, which receives test signs unseen in training (out of vocabulary, OOV). All likelihood models share this alphabet. Exact restoration is scored against the original fine code, so an unseen code counts as a failure.

The independent models ignore neighbouring signs: a smoothed unigram model (U), a model of text length and slot (P), and a model of length, slot, site and object type (PM). Position counts shrink toward U and metadata counts toward P. The dependent model PMB multiplies PM by the ratio of the smoothed probability of the sign after its predecessor, pooled over positions, to its unigram probability, then normalizes over the vocabulary. At the first position PMB equals PM, so the noninitial gain measures what the preceding sign adds to the selected independent baseline.

The main evaluation has five outer and three inner component-held-out folds. Within each outer training set, the inner folds select the independent model, its smoothing strength (the weight of the prior) and the strength of PMB by noninitial log likelihood, from 5, 20, 100, 500 and 2,000. The main fit with all records selects PM with strength 500 and PMB with strength 100 in all five outer folds. This nested comparison supersedes an earlier fixed-strength pilot whose metadata baseline was smoothed too weakly.

The main statistic is the summed held-out log-likelihood difference, in bits, divided by the number of noninitial test signs. Five thousand bootstrap draws of components from the already fitted outer-fold scores give its interval, which is conditional on the fitted procedure and the selected corpus (a conditional component bootstrap).

### 4.2 Full-procedure conditional references

For a reference distribution we shuffle signs among records with the same length, slot, site and object type, keeping each cell's sign counts and the record metadata; this breaks the order of neighbouring signs and preserves what the independent models use. For each shuffled corpus we rebuild the string-dependent components, reallocate folds, repeat inner selection and predict the held-out texts. Earlier references that kept the observed groups, folds or substitution findings fixed are archived as conditional diagnostics.

The main reference has 1,000 corpora. A post-pilot sensitivity analysis starts from the unique-string population and rejects shuffles that repeat any whole string, sampling the same reference conditional on distinct strings; 1,000 accepted corpora took 6,569 proposals. Each accepted corpus is fitted afresh. With an exceedance defined as a shuffled gain at least as large as the observed one, the probability is `(1 + exceedances)/(1 + accepted trials)`; the detailed methods state the exchangeability assumptions.

### 4.3 Candidate-event evaluation

Training for the second-transcription test removes every full component touched by source objects M1–M199 of the *Corpus of Indus Seals and Inscriptions* or by a fine-code string compatible with an eligible test face. This removes 170 strings and leaves 1,426 training strings in 1,362 components, which are used for all model selection.

For candidate sets A1,…,AL, the dependent score sums the probabilities of all compatible fine-code paths with a forward recursion. No unsupported fine code receives credit by being relabelled `UNKNOWN`. Because candidate sets can overlap across P labels, the score is the probability of the specified fine-code event, not a normalized predictor over P labels. Test faces are scored as site Mohenjo-daro and object type `SEAL:S`; a sensitivity analysis leaves the seal subtype unspecified. Ten thousand bootstrap draws over groups of faces condition on the fitted training models.

### 4.4 Known-slot restoration

The known-slot benchmark hides each of the 8,009 slots of the 1,596 distinct strings (aliases retained, 1,526 components) in turn, with the text length known, and asks each model to rank candidates. The independent restorer ranks by PM. The local restorer computes the normalized PMB posterior given the surviving neighbours and fixed length, including the following transition's candidate-dependent normalizer. Inner component-held-out selection maximizes exact top-one accuracy, the share of slots whose top-ranked candidate is the original fine code; all outer folds select strength 20 for both models. An OOV target is never counted correct through `UNKNOWN`.

We report exact top-one accuracy and top-k inclusion weighted by slot, with a conditional component-bootstrap interval for the paired difference. Summaries that weight each text equally, and summaries by sign frequency, show which texts and signs drive the aggregate.

A [conventional Markov comparison](../../experiments/2026-10-02-six-hour/markov-baseline/PROTOCOL.md), specified afterwards, recreates every saved query (hidden slot) and outer fold before fitting. It learns one position-independent transition matrix, a start distribution and an end-of-text state; interior queries use the transitions into and out of the candidate, boundary queries the start or end factor. Three inner component-held-out folds select strength from 20, 100, 500 and 2,000, choosing 20 in every outer fold. The independent and local predictions are reused unchanged. Ten thousand paired component-bootstrap draws summarize the new differences, and a second count implementation verifies every candidate ranking and target loss.

A further [second-order protocol](../../experiments/2026-10-02-six-hour/markov-order2/PROTOCOL.md) predicts each sign from the two preceding signs, shrinking toward the first-order probability after the latest sign (strength 20). Inner folds choose the second-order strength from 5, 20, 100, 500, 2,000 and backoff-only, which uses first order alone. The posterior includes the hidden sign's own factor and both later factors containing it, including end-of-text factors. Top-one selection and a later loss selection have separate frozen protocols. These models were developed after inspecting earlier benchmark results. An independent full-record likelihood implementation checks all 8,009 queries; exact rational calculations resolve the recorded floating-point ties.

### 4.5 Unknown-count gaps

Each intact unique string receives one artificial internal gap: the erased count k is drawn uniformly from 1,…,min(3,L−2), for text length L, and the start uniformly among positions leaving a sign on each side. With both surviving sides fixed, a dynamic program sums over the missing fine codes for candidate counts 1–3. Models use a training-derived full-length prior and frozen smoothing 20. The constant-one control always guesses one erased sign.

The original prototype omitted part of the observation law, the probability that this masking procedure yields the observed text. For m surviving signs and candidate length L=m+k, the law contributes `1/[min(3,L−2)(m−1)]`. The second factor cancels across count candidates, leaving the term from the cap at three. A post-audit sensitivity analysis, which we call design-matched, reweights the same saved posteriors by `1/min(3,m+k−2)`, with models and queries fixed. We preserve both results.

### 4.6 Template and specificity checks

For each text length we fit a finite mixture of independent-slot templates, in which each text comes from one template and each template slot has its own sign distribution, selecting among 16, 32 and 64 templates on training data only. We compare it with the selected independent baseline and PMB. We repeat the comparison on a constructed office-routing code with a known nonphonetic mechanism, in which each sign names an office and a sequence records a route of handoffs; this tests whether dependence the templates leave unexplained indicates language. Totem-pole and weather-icon corpora from other authors, in published order and with simultaneous composite figures kept as single units, supply further feasibility checks.

## 5. Results

### 5.1 Local dependence remains under the stated controls

| Population | Records or strings | Components | Gain, bits per noninitial sign | Conditional 95% interval |
|---|---:|---:|---:|---:|
| Main eligible records | 2,107 | 1,526 | 0.890 | 0.817–0.965 |
| Unique whole strings, all aliases retained | 1,596 | 1,526 | 0.848 | 0.807–0.890 |
| Main records after three compatible-class merges | 2,107 | 1,506 | 0.930 | 0.862–0.997 |

The main noninitial cross entropy falls from 6.307 bits under the baseline to 5.417 bits under PMB, a relative perplexity of 0.540. The merge row joins three pairs of codes with compatible classes: 861→817, 405→390 and 706→705. Reversed sequences also give a positive gain.

None of the 1,000 regrouped and refitted shuffles in the main reference reached the observed gain, giving p=0.000999. The shuffled gains have mean −0.1033 bits and central 95% range −0.1274 to −0.0800. The reference conditioned on distinct strings also has no exceedances, with mean 0.0071 and central 95% range −0.0065 to 0.0214. Shuffled gains can be negative because a fitted dependent model loses held-out likelihood through estimation and smoothing. The inference therefore rests on the reference distribution rather than on comparison with zero alone.

The result files are [main nested prediction](../../research/methods/results/nested_primary/nested_results.json), [alias-preserving unique prediction](../../research/methods/results/nested_unique_preserved_aliases/nested_results.json), [merged prediction](../../research/methods/results/nested_collapsed/nested_results.json), [full main null](../../research/methods/results/joint_nested_primary_1000/joint_nested_results.json), and [uniqueness-conditioned null](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json).

### 5.2 The gain is also positive on an independent transcription

The 74 scored faces give 0.725 bits per noninitial candidate event, with a conditional interval of 0.551–0.899. One face per distinct P-label sequence gives 0.719 bits on 73 faces. Leaving the seal subtype unspecified gives 0.777 bits, and the 54 fully supported faces give 0.878 bits. Each figure keeps its own event population and metadata assumption. The [test output](../../results/independent_annotator/candidate_event_test.json) keeps the exclusions, candidate sets, scores and training removals.

The gain transfers across the two encodings. The candidate sets rest on shared catalogue compatibility, the second encoding covers a non-random block of objects, and wholly unsupported events were removed, so the result measures transfer between encodings of shared sources for faces with training support.

### 5.3 Neighbouring signs improve known-slot restoration; rare signs and calibration remain weak

| Metric | Independent restorer | Local restorer | Conventional Markov |
|---|---:|---:|---:|
| Exact top-one | 16.99% | 33.81% | 34.59% |
| Target included in top five | 35.50% | 55.34% | 58.46% |
| Target included in top ten | 45.57% | 62.70% | 65.43% |

The paired top-one improvement is 16.82 percentage points (conditional component-bootstrap interval 15.64–17.98). Weighting each text equally gives approximately 17.4% and 32.6%. Correct predictions concentrate on frequent signs: all 205 codes that occur only once fail when hidden, and accuracy averaged over sign types is much lower than accuracy averaged over slots. Merging the three compatible pairs raises local exact accuracy to 35.90%, showing the effect of target granularity.

The conventional Markov model's 34.59% top-one score is 17.59 points above the independent restorer (interval 16.38–18.83). Local-minus-Markov is −0.774 points (−1.596 to +0.050) for top-one and −3.121 points (−3.859 to −2.376) for top-five. Weighting texts equally gives 32.60% for local and 33.35% for Markov. Averaged over codes, top-one slightly favours local, 5.13% against 4.80%; both models recover rare codes poorly. The [Markov result](../../experiments/2026-10-02-six-hour/markov-baseline/main/results.json) and its [independent verification](../../experiments/2026-10-02-six-hour/markov-baseline/verification.json) keep the common-query checks and paired outcomes.

The local restorer is overconfident. Where the probability of its top candidate lies in the 0.4–0.6 bin, that probability averages 0.492 and the share correct is 0.384; in the 0.8–1.0 bin they are 0.896 and 0.838. The benchmark and all calibration bins are in [benchmark.json](../../results/restoration/benchmark.json).

The Markov model's expected calibration error over five confidence bins is 2.56%, against 8.05% for the local restorer. Its bucket log loss, the negative log2 probability of the true sign with unseen signs pooled as `UNKNOWN`, is 5.119 bits per slot, against 5.748. Local-minus-Markov loss is 0.628 bits (0.579–0.679). These measurements favour keeping the conventional model in future comparisons and studying how boundary terms, metadata multiplication and smoothing affect prediction.

Conditioning on two preceding signs raises top-one accuracy to 37.27%, 2.684 percentage points above first order (1.990–3.397), with top-five and top-ten scores of 58.87% and 65.45%. Bucket loss rises to 5.247 bits per slot, an increase of 0.128 bits (0.096–0.159), and calibration error to 4.35%. Equal-text top-one is 35.67%, and the mean top-one over code types is 6.12%. The added context improves the first guess while lowering the probability given to the target. See the [matched results](../../experiments/2026-10-02-six-hour/markov-order2/main/results.json) and the [independent review](../../experiments/2026-10-02-six-hour/markov-order2/review-ties/verification.json).

Selecting the second-order strength by loss instead chooses backoff-only in all five folds and reproduces every first-order query outcome, with 34.59% top-one and 5.119 bits per slot. The trade-off therefore lies in the inner selection objective, on a reused benchmark. See the [loss-selection protocol and result](../../experiments/2026-10-02-six-hour/markov-order2/loss-selected/PROTOCOL.md) and the [all-query review](../../experiments/2026-10-02-six-hour/markov-order2/loss-selected/review/verification.json).

A further comparison shrinks rarely seen two-sign histories more strongly. The first-order strength stays at twenty, and the second-order weight for a history seen N times in training is multiplied by `N/(N+κ)`, giving an effective strength of `α+κ+ακ/N`. Removing grid pairs that give the same model leaves seventeen finite candidates and pure backoff. All five inner selections again choose backoff; the closest finite candidate is .00846–.00929 bits worse. The 8,009 predictions equal first order exactly, as independent complete-chain and rational-factor checks confirm. The [adaptive protocol, complete candidate table and audit](../../experiments/2026-10-02-six-hour/markov-adaptive/README.md) document this separately specified follow-up, run after the earlier outcomes on the same hidden slots.

Cross-site tests hold out one site and exclude from training every component touching any of its records, including copies removed by deduplication. Improvements are 14.94 points at Mohenjo-daro on 866 unique texts, 15.48 at Harappa on 496, and 17.93 at Lothal on 51. These are separate test populations with different vocabulary coverage, and the small Lothal sample gives an imprecise estimate. The [cross-site output](../../results/restoration_crosssite/crosssite.json) records intervals and removals. Site-transfer results for the structural gain must use the separate corrected [transitive transfer file](../../research/methods/results/nested_primary/transitive_site_transfer.json), not older fields that excluded only directly overlapping records.

### 5.4 Estimated gap counts fall below always guessing one

| Count predictor | Original prototype | Design-matched sensitivity |
|---|---:|---:|
| Independent | 41.92% | 45.61% |
| Local | 43.05% | 46.30% |
| Constant one | 51.07% | 51.07% |

In the original prototype the local-minus-independent improvement is 1.13 points, with an interval spanning zero. After matching the observation law it is 0.689 points (−0.569 to 1.940). The matched local model is 4.762 points below the constant-one control (interval −7.775 to −1.726), so its count estimates are less accurate than always guessing one. The results are [the original benchmark](../../results/gap_restoration/gap_benchmark.json) and [the matched-law sensitivity](../../research/methods/results/gap_design_matched/gap_design_matched.json).

### 5.5 A constructed office code shows a similar residual gain

The template mixture improves on the independent baseline by 0.142 bits per noninitial sign, and PMB exceeds it by 0.748 bits (0.688–0.809). On the office-routing control, whose sequences are ordered but nonphonetic, PMB exceeds the same template family by 0.631 bits (0.588–0.677). The Indus transcription and this constructed control share dependence that the templates leave unexplained.

In the totem-pole corpus about 43.7% of noninitial tokens are out of vocabulary, and the fitted gain lies within the shuffled-corpus reference. Linking weather forecasts by station and identical string joins the whole weather corpus into one component, so component-held-out cross-validation is impossible. The outputs are [Indus templates](../../research/methods/results/templates_extended/template_results.json), [office templates](../../research/methods/results/workflow_templates/template_results.json), and the [comparison-data documentation](../../research/literature/nonlinguistic_controls/README.md).

### 5.6 Full-corpus alias-clean and near-variant-clean refits (22 November 2026)

All results in Sections 5.1 through 5.5 remain the frozen 2 October 2026 endpoints. An independent [6 October audit](../../experiments/2026-10-06-modern-restoration/REVIEW.md) then showed that building transitive components from the 1,596 benchmark strings alone left residual cross-fold links visible only when all 5,680 observed faces of the export are included. On 22 November 2026 we completed a pre-registered refit ([PROTOCOL.md](../../experiments/2026-11-22-restoration-leak-free/PROTOCOL.md), [REPORT.md](../../experiments/2026-11-22-restoration-leak-free/REPORT.md)) over the exact same 1,596 unique strings and 8,009 known-slot queries under three progressively stricter component partitions, refitting every model from scratch with nested three-fold inner selection respecting each split's component boundaries and computing 10,000-draw paired component-bootstrap intervals.

In Split 1 (exact reproduction of Paper 001's 1,526 benchmark-only components), zero direct benchmark aliases cross folds, yet transitive links across all 5,680 observed faces in `data/normalized/lipi_observed_faces.jsonl` bridge 194 benchmark strings and 755 queries (9.43% of the benchmark, 13,476 cross-fold benchmark pairs across six merged components). Sixteen identical one-sign and two-sign texts shared across faces of different objects account for 192 strings and 748 queries, and normalized site and excavation identifiers connect 2 more strings and 7 queries. Direct near-variant overlap is broader: 509 strings (2,016 queries, 25.17%) have a training neighbour at Levenshtein distance 1 (differing by one sign substitution, insertion or deletion), 243 strings (983 queries, 12.27%) share an identical sequence of graphic base shapes under the 77-class [F-0010](../../knowledge/findings/F-0010-graphic-base-families-improve-prediction.md) base-shape table across folds, and 548 strings (2,190 queries, 27.34%) satisfy at least one of those two direct near-variant relations.

Split 2 builds transitive components across all 5,680 observed faces before filtering, joining shared physical family identifiers, normalized CISI base keys, normalized site and excavation identifiers, and identical nonempty reading-order strings of any length. This merges 1,526 benchmark components into 1,361 full-corpus components (largest: 184 strings, 715 slots) across five balanced outer folds, leaving 0.00% full-corpus alias leakage in both outer and inner folds while 519 strings (2,040 queries, 25.47%) still have a direct near-variant neighbour across folds. Split 3 further merges Split 2's components across all 876 Levenshtein-1 pairs and 295 `F-0010` base-shape pairs among benchmark strings, yielding 964 components (largest: 493 strings, 1,872 slots, held intact inside outer fold 0 and inside one inner fold whenever fold 0 enters training), leaving 0.00% alias, Levenshtein-1 and base-family leakage in all outer and inner folds.

| Split | Components | Largest component (strings, slots) | Fold slot loads | Full-corpus alias queries (%) | Levenshtein-1 queries (%) | Base-family queries (%) | Direct near-variant queries (%) |
|---|---:|---|---|---:|---:|---:|---:|
| Split 1 (Baseline Paper 001) | 1,526 | 9 strings, 49 slots | 1603, 1600, 1602, 1602, 1602 | 755 (9.43) | 2,016 (25.17) | 983 (12.27) | 2,190 (27.34) |
| Split 2 (Alias-clean) | 1,361 | 184 strings, 715 slots | 1602, 1602, 1602, 1602, 1601 | 0 (0.00) | 1,887 (23.56) | 869 (10.85) | 2,040 (25.47) |
| Split 3 (Near-variant-clean) | 964 | 493 strings, 1,872 slots | 1872, 1535, 1534, 1534, 1534 | 0 (0.00) | 0 (0.00) | 0 (0.00) | 0 (0.00) |

Across all three splits we evaluate six models: the independent metadata baseline (`PM`), first-order Markov (`M1`), top-one-selected second-order Markov (`M2`), bidirectional interpolated modified Kneser–Ney (`MKN`), a log-linear mixture of `MKN` with an exact generative first-order Markov model over `F-0010` graphic base-shape classes (`MKN-GF`), and a three-way log-linear mixture adding a distance-2 skip-bigram and position-slot predictor (`MKN-GF-SB`). Split 1 reproduces all four prior frozen baselines (`PM`, `M1`, `M2` from 2 October and `MKN` from 6 October) across all 8,009 queries with zero top-one or top-five mismatches and maximum metric difference `0.0`.

| Split | Model | Top-1 (%) | Top-5 (%) | Top-10 (%) | Log loss (bits) | ECE (%) | OOV (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| Split 1 (Baseline) | `PM` | 16.9934 | 35.4976 | 45.5737 | 7.135412 | 2.0441 | 3.134 |
| Split 1 (Baseline) | `M1` | 34.5861 | 58.4592 | 65.4264 | 5.119435 | 2.5564 | 3.134 |
| Split 1 (Baseline) | `M2` | 37.2706 | 58.8713 | 65.4514 | 5.247171 | 4.3506 | 3.134 |
| Split 1 (Baseline) | `MKN` | 39.7178 | 61.6806 | 68.7601 | 4.581891 | 5.2751 | 3.134 |
| Split 1 (Baseline) | `MKN-GF` | 40.5918 | 62.0552 | 69.0973 | 4.516653 | 2.0047 | 3.134 |
| Split 1 (Baseline) | `MKN-GF-SB` | 40.6418 | 62.2175 | 69.2471 | 4.504110 | 1.6098 | 3.134 |
| Split 2 (Alias-clean) | `PM` | 16.2068 | 35.6474 | 45.0119 | 6.817929 | 1.8576 | 3.221 |
| Split 2 (Alias-clean) | `M1` | 33.9743 | 58.5466 | 65.7011 | 5.121386 | 2.6420 | 3.221 |
| Split 2 (Alias-clean) | `M2` | 36.2967 | 59.0461 | 65.6012 | 5.255718 | 4.9901 | 3.221 |
| Split 2 (Alias-clean) | `MKN` | 39.8926 | 62.0552 | 69.0223 | 4.563180 | 4.8841 | 3.221 |
| Split 2 (Alias-clean) | `MKN-GF` | 40.3047 | 62.4423 | 69.3220 | 4.506267 | 1.5156 | 3.221 |
| Split 2 (Alias-clean) | `MKN-GF-SB` | 40.4170 | 62.3798 | 69.4219 | 4.496628 | 1.2794 | 3.221 |
| Split 3 (Near-variant-clean) | `PM` | 14.7085 | 33.9368 | 43.4386 | 6.800761 | 0.8026 | 3.446 |
| Split 3 (Near-variant-clean) | `M1` | 33.1502 | 56.9734 | 64.3776 | 5.292911 | 2.6802 | 3.446 |
| Split 3 (Near-variant-clean) | `M2` | 34.0367 | 56.9484 | 63.8157 | 5.442750 | 5.4275 | 3.446 |
| Split 3 (Near-variant-clean) | `MKN` | 37.0958 | 59.9451 | 67.2119 | 4.750645 | 5.6069 | 3.446 |
| Split 3 (Near-variant-clean) | `MKN-GF` | 37.7076 | 60.3821 | 67.3617 | 4.689897 | 2.1674 | 3.446 |
| Split 3 (Near-variant-clean) | `MKN-GF-SB` | 37.5952 | 60.3571 | 67.4616 | 4.683723 | 1.9207 | 3.446 |

Removing full-corpus alias leakage in Split 2 lowers `M1` by 0.612 top-one percentage points (95% CI [−1.989, +0.595]) and `M2` by 0.974 points ([−2.164, +0.150]) to 36.30%, closely matching the −0.75 and −0.84 point bounds estimated by fixed-hyperparameter deletion in the 6 October review. By contrast, `MKN` moves by +0.175 points ([−0.861, +1.186]) to 39.89% and 4.563 bits, while `MKN-GF-SB` holds 40.42% top-one accuracy, 62.38% top-five inclusion, 4.497 bits per slot and 1.28% five-bin expected calibration error (−0.225 points [−1.330, +0.845] relative to Split 1). For `PM`, inner selection switches from strength 20 to 100 in three folds of Split 2 (and all five folds of Split 3), lowering top-one by 0.787 points while reducing bucket log loss by 0.3175 bits because stronger shrinkage protects sparse metadata cells.

Isolating near variants in Split 3 lowers every sequential model by 1.44 to 3.23 top-one points relative to Split 1 (0.82 to 2.82 points relative to Split 2) and adds 0.169 to 0.196 bits of held-out log loss. Because the out-of-vocabulary target rate rises only from 3.134% in Split 1 to 3.221% in Split 2 and 3.446% in Split 3, vocabulary loss explains only a small fraction of the drop; roughly 2.6 to 3.2 top-one points and 0.17 to 0.20 bits of Split 1 headline performance come from generalizing across near-variant inscriptions differing by one sign or sharing a base-shape skeleton. Two structural results stand out across the within-split paired contrasts below.

| Pairwise contrast (B minus A) | Split 1 Top-1 [95% CI] / Bits [95% CI] | Split 2 Top-1 [95% CI] / Bits [95% CI] | Split 3 Top-1 [95% CI] / Bits [95% CI] |
|---|---:|---:|---:|
| `M2 - M1` | +2.684 [+1.977, +3.402] / +0.1277 [+0.0963, +0.1596] | +2.322 [+1.643, +2.955] / +0.1343 [+0.0926, +0.1752] | +0.887 [+0.385, +1.623] / +0.1498 [+0.0903, +0.1944] |
| `MKN - M1` | +5.132 [+4.254, +6.030] / −0.5375 [−0.5826, −0.4920] | +5.918 [+5.055, +6.771] / −0.5582 [−0.6050, −0.5149] | +3.946 [+3.194, +4.984] / −0.5423 [−0.6073, −0.4981] |
| `MKN - M2` | +2.447 [+1.800, +3.092] / −0.6653 [−0.7150, −0.6162] | +3.596 [+2.968, +4.272] / −0.6925 [−0.7399, −0.6409] | +3.059 [+2.359, +3.783] / −0.6921 [−0.7395, −0.6355] |
| `MKN-GF - M1` | +6.006 [+5.165, +6.846] / −0.6028 [−0.6440, −0.5607] | +6.330 [+5.472, +7.153] / −0.6151 [−0.6546, −0.5762] | +4.557 [+3.829, +5.488] / −0.6030 [−0.6596, −0.5643] |
| `MKN-GF - MKN` | +0.874 [+0.470, +1.282] / −0.0652 [−0.0773, −0.0535] | +0.412 [−0.014, +0.806] / −0.0569 [−0.0717, −0.0406] | +0.612 [+0.117, +0.988] / −0.0607 [−0.0742, −0.0422] |
| `MKN-GF-SB - MKN-GF` | +0.050 [−0.202, +0.309] / −0.0125 [−0.0174, −0.0078] | +0.112 [−0.163, +0.405] / −0.0096 [−0.0155, −0.0044] | −0.112 [−0.408, +0.124] / −0.0062 [−0.0171, +0.0023] |

First, two-thirds of the conventional second-order Markov (`M2`) top-one advantage over `M1` vanishes once near variants are held out: `M2 - M1` shrinks from +2.684 points on Split 1 and +2.322 points on Split 2 to +0.887 points ([+0.385, +1.623]) on Split 3, while `M2` remains worse than `M1` on log loss (+0.1498 bits) and ties on top-five (−0.025 points). In contrast, `MKN` retains a +3.946 point and −0.5423 bit lead over `M1` (+3.059 points and −0.6921 bits over `M2`) on Split 3, showing that continuation-count discounting captures reusable higher-order syntax rather than memorized near duplicates. Second, pooling `MKN` with the `F-0010` graphic-base-family Markov model (`MKN-GF`) improves held-out probability estimation and cuts calibration error by more than half across every split (from 5.28% to 2.00% on Split 1, 4.88% to 1.52% on Split 2, and 5.61% to 2.17% on Split 3). Even on Split 3, where identical base-shape templates cannot cross folds, `MKN-GF` holds 37.71% top-one accuracy, 60.38% top-five inclusion and 4.690 bits per slot, beating `M1` by +4.557 points and −0.6030 bits and beating ungrouped `MKN` by +0.612 points ([+0.117, +0.988]) and −0.0607 bits ([−0.0742, −0.0422]). Adding the skip-bigram and position component (`MKN-GF-SB`) lowers calibration error further (to 1.28% on Split 2 and 1.92% on Split 3) and adds small log-loss gains on Splits 1 and 2, while its incremental difference over `MKN-GF` on Split 3 spans zero. Position ordering stays unchanged across splits: final slots remain easiest and initial slots hardest (`MKN-GF-SB` on Split 2: 22.62% initial, 40.56% internal, 57.77% final; `MKN-GF` on Split 3: 20.43% initial, 38.14% internal, 53.70% final). Resampling Split 1 pairwise contrasts over Split 2's 1,361 components shifts interval endpoints by at most 0.07 percentage points.

In the earlier [6 October exploratory run](../../experiments/2026-10-06-modern-restoration/REPORT.md) on Split 1, standalone three-seed recurrent and transformer networks did not beat `MKN` (38.09% and 34.20% top-one), while a log-linear ensemble of `MKN` and the neural networks reached 40.79% (41.17% with extra non-benchmark text, where 72–94% of the common-alphabet loss improvement came from 251 targets outside the benchmark-only alphabet). Because PyTorch was unavailable on the November workstation, neural refits on Splits 2 and 3 remain an open follow-up alongside the verified exact classical and graphic-family ladder reported here.

These Split 1–3 measurements evaluate synthetic single-slot deletion with exact sequence length known. They measure graphic prediction inside intact transcribed strings and must be separated from restoring genuinely damaged inscriptions, where the number of lost signs is unknown and our design-matched gap-count estimator still scores 46.30% against 51.07% for always guessing one (Section 5.4).

An independent verifier ([verify.py](../../experiments/2026-11-22-restoration-leak-free/code/verify.py), [verification-v1.json](../../experiments/2026-11-22-restoration-leak-free/verification-v1.json)) rebuilt the full-corpus alias graph by breadth-first search without importing the fitting code, confirmed zero outer and inner alias crossings in Splits 2 and 3 and zero Levenshtein-1 and base-family crossings in Split 3, verified exact Split 1 reproduction (`0.0` loss difference across all four prior baselines), recomputed all 18 cells within `8.88e-16`, and replayed brute-force complete-sequence likelihoods on 45 sampled queries (270 model evaluations) within `6.66e-16` with exact hidden-target invariance. Full aggregate tables are in [results-v1/summary.json](../../experiments/2026-11-22-restoration-leak-free/results-v1/summary.json).

## 6. Discussion

The local predictive constraint holds when each string counts once and on the second transcription. A proposed generative model can now be tested against these held-out gains, with the same component exclusions and target alphabet. The office-routing control also shows a limitation of the fitted template family: both systems keep dependence that it leaves unexplained.

Restoration separates two inference problems. At a known slot, local context ranks the candidate signs; an unknown count also needs a length model and a model of how gaps arise. The difference in outcomes suggests that count recovery needs further evidence or a different predictor. Damaged originals can supply gap width, surviving traces, line layout and spacing, with the uncertainty of the reference readings recorded in a new benchmark.

The conventional comparison also changes the target for model development. Both sequential predictors far exceed the independent restorer, and the conventional model has higher top-five coverage and lower bucket loss. A completed [mechanism study, with independent review](../../experiments/2026-10-02-six-hour/markov-ablation/README.md), used the same hidden slots to remove the end-of-text factor, change the start distribution and shuffle the interiors of training strings. Removing the end factor lowers final-slot accuracy from 53.95% to 48.25%; keeping each string's first and last signs while shuffling its interior lowers overall accuracy to 24.52%, averaged across twenty orders. Text boundaries and interior order are thus distinct sources of predictive information.

Related project experiments give mixed results. Predicting from the text whether an object is a seal or a tablet, counting each distinct text once, gives a positive gain; predicting the Bull1 (unicorn) motif code gives a negative one. For Mohenjo-daro seals of known period, a permutation test of whether seals from the same house carry more similar sequences than seals of the same area, period and length gives probabilities of 0.0560 to 0.0864 across weighting and merging variants. Aggregate substitution transfer changes with the weighting of repeated texts and the treatment of classes. The [retrospective](../../knowledge/retrospectives/methods.md) records these paths and their failed or superseded variants.

A separate audit finds four positive integer solutions to the equations Fuls proposed for numerical inscriptions [R9]. Selecting his 10/8/6 solution requires an additional range restriction. The [numerical directions](../../knowledge/directions/numerical-methods.md) identify the source joins still needed and propose tests that predict independently measured quantities on held-out objects.

The 22 November 2026 refits sharpen what known-slot restoration measures. Full-corpus alias isolation (Split 2) preserves both the model ranking and the absolute scale of `MKN` and `MKN-GF-SB` (40.42% top-one, 1.28% ECE), showing that short-face transitive links did not create the higher-order gain. Near-variant isolation (Split 3) separates memorization of single-sign variants from general sequence constraints: conventional second-order shrinkage (`M2`) loses two-thirds of its advantage over first order, whereas `MKN-GF` preserves a +4.56 point and −0.603 bit lead over `M1` while cutting calibration error by more than half.

Boldest supported reading: Indus sign sequences obey genuine higher-order combinatorial syntax and graphic-family class constraints that generalize across completely unseen inscription families, independent of physical object aliases, shared short faces, single-sign variants and base-shape template duplicates. Deciding test: refit the neural and ensemble comparators alongside `MKN-GF` on Splits 2 and 3 on a PyTorch-enabled workstation, then score the frozen recipes prospectively without retuning on newly acquired CISI 3.1 and post-catalogue inscriptions verified to have zero alias or near-variant overlap with the Lipi training set; if the +3 to +4 percentage point and −0.55 to −0.65 bit margin over `M1` survives on post-catalogue excavations, out-of-family combinatorial syntax is confirmed beyond the existing export.

## 7. Limitations

The main source is a derivative transcription that accompanies disputed interpretations and is only partly checked against primary photographs. Known aliases do not capture every dependence arising in production and excavation. Unique-string representatives change metadata weighting. The three compatible-class merges cover a small part of the uncertainty in sign identity and are not expert decisions on sign variants (allographs).

The likelihood alphabet pools unseen codes into `UNKNOWN`, while candidate events and exact restoration score different targets. Candidate-event exclusions favour cases with some training support. Neither bootstrap interval includes every source of curation and model uncertainty. The shuffled references assume exchangeability within the declared cells and do not represent every historical mechanism.

Several safeguards and sensitivity designs were added after pilots or after errors were found, and they keep their post-pilot status. The 2 October Markov models were specified after the original restoration outcomes and fitted under their own saved protocols. The 22 November 2026 refit pre-registered its three splits and six exact classical and graphic-family models before fitting, closing the full-corpus alias and near-variant leakage gaps identified on 6 October; refitting the 6 October neural models on Splits 2 and 3 remains pending on a PyTorch-enabled machine. Known-slot deletion with known length also remains distinct from restoring genuinely eroded gaps of unknown span.

Linking a predictive constraint to a sound or meaning requires an anchor fixed from outside the texts, such as a known word or a measured quantity. The likelihoods here are unchanged when the meanings in a freely fitted semantic model are relabelled, so they leave those assignments unidentified.

## 8. Reproducibility and publication status

The recorded environment for the structural analyses is Python 3.13.5 with NumPy 2.2.6 and standard-library modules. Audits of images and PDF sources need additional packages, documented in their retained scripts. Seeds, hashes of inputs and sources, model choices and permutation outcomes are embedded in the result JSON. Eight integrity checks cover normalization, OOV handling, leakage between components, alias retention, transitive site exclusion, preserved cell counts in the shuffled corpora, substitution-frame counting and synthetic specificity. Commands are in [the detailed methods](methods.md) and [the original reproduction guide](../../research/methods/REPRODUCING.md).

External reproduction, epigraphic source review, decisions on access and release, neural refits on Splits 2 and 3, and a fresh prospective evaluation with models frozen in advance remain open. The [submission checklist](SUBMISSION-CHECKLIST.md) tracks current preprint readiness and local-only data boundaries alongside the original 2 October [submission-gap register](submission-gaps.md).

## 9. References

**R1.** Rao, R. P. N., Yadav, N., Vahia, M. N., Joglekar, H., Adhikari, R., and Mahadevan, I. (2009). *A Markov model of the Indus script*. PNAS 106, 13685–13690. [DOI](https://doi.org/10.1073/pnas.0906237106); [author-hosted primary PDF](https://homes.cs.washington.edu/~rao/PNASIndus.pdf).

**R2.** Yadav, N. (2019). *Structure of Indus Script*. Indian Journal of History of Science 54(2), 125–134. [Yadav (2019) PDF](https://insa.nic.in/writereaddata/UpLoadedFiles/IJHS/Vol54_2_2019__Art01.pdf), Table 1, printed p.127. [DOI](https://doi.org/10.16943/ijhs/2019/v54i2/49656).

**R3.** Mahadevan, I. (1982), *Terminal ideograms in the Indus script*, in G. L. Possehl (ed.), *Harappan Civilization: A Contemporary Perspective*, New Delhi: Oxford & IBH; and (1986), *Towards a grammar of the Indus texts: 'Intelligible to the eye, if not to the ears'*, Tamil Civilization 4(3–4), 15–30. Primary scans, exact inspected pages and retained OCR are indexed in [the primary-evidence matrix](../../research/literature/evidence_and_novelty_matrix.md). Proposed meanings in these works are author interpretations.

**R4.** Khanna and Merriam (2025). *A Computational Analysis of the Indus Script: Identifying Sign Functions in Logo-Syllabic Writing Systems*. IJCA 187(64), 19–22. [Khanna and Merriam (2025) PDF](https://www.ijcaonline.org/archives/volume187/number64/khanna-2025-ijca-926075.pdf); [DOI](https://doi.org/10.5120/ijca2025926075).

**R5.** Koskenniemi, K., and Parpola, A. (1980). *Documentation and Duplicates of the Texts in the Indus Script*. Department of Asian and African Studies, University of Helsinki, Research Reports No. 2. Helsinki. Duplicate definitions on pp.54–56. [Public copy](https://tuhat.helsinki.fi/ws/portalfiles/portal/207886811/indus_duplicates_1980.pdf); [retained source](../../research/corpus/primary/koskenniemi_parpola1980.pdf).

**R6.** Sproat, R. (2010). *Last Words: Ancient Symbols, Computational Linguistics, and the Reviewing Practices of the General Science Journals*. Computational Linguistics 36(3), 585–594. [Sproat (2010) ACL record and PDF](https://aclanthology.org/J10-3012/).

**R7.** Nair, A. (2026). *How Non-Linguistic Is the Indus Sign System? A Synthetic-Baseline Scorecard*. arXiv:2604.17828v1, 20 April 2026. [Nair (2026) arXiv v1](https://arxiv.org/html/2604.17828v1), §§4.2 and 5.7. Unreviewed preprint as inspected.

**R8.** Mayig, *Digital corpus of Indus Valley Script*. [Repository](https://github.com/mayig/indus-valley-script-corpus). Pinned source, license and crosswalk provenance are retained in the corpus manifests.

**R9.** Fuls, A. (2020), *Ancient Writing and Modern Technologies – Structural Analysis of Numerical Indus Inscriptions*. In *Studies on Indus Script*, National Fund for Mohenjodaro, pp.57–90. Inspected in the 2023 author reprint, printed pp.15–48. [Exact source and premises](../../research/literature/metrology/numerical_source_premises.json); [conditional audit](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md).

**R10.** Chen, S. F., and Goodman, J. (1998). *An Empirical Study of Smoothing Techniques for Language Modeling*. Harvard University Computer Science Group, Technical Report TR-10-98, §§2.7 and 3 (eq. 26). [Author report PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-10-98.pdf).

**R11.** Yadav, N., Joglekar, H., Rao, R. P. N., Vahia, M. N., Adhikari, R., and Mahadevan, I. (2010). *Statistical Analysis of the Indus Script Using n-Grams*. PLoS ONE 5(3): e9506. [DOI](https://doi.org/10.1371/journal.pone.0009506); [publisher full text](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0009506).

The broader audit of publication priority, source identity and retrieval is [retained here](../../research/literature/evidence_and_novelty_matrix.md). References with unresolved metadata must be completed from their original title pages before journal submission.
