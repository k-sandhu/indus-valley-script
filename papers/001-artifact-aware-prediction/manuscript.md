# Artifact-aware evaluation of Indus sign prediction: local dependencies, annotation uncertainty, and restoration limits

**Publication status:** complete private working manuscript, 2 October 2026; submission and peer review pending. Authorship, affiliations, acknowledgements and target venue remain to be supplied by the project owner. Computational analyses and manuscript preparation used AI assistance. Independent epigraphic review of the transcriptions and source inspections is an open submission task.

## Abstract

We evaluate local predictive dependencies in Indus transcriptions while accounting for correlated artifacts, repeated texts, annotation granularity and the sampling of restoration tasks. A selected derivative corpus contains 2,107 complete, single-line, right-to-left records of at least three signs, representing 1,596 distinct strings and 1,526 connected artifact/text components. Five-fold component-held-out prediction with training-only model selection yields a local-dependency gain of 0.890 bits per noninitial sign over a position/length/metadata baseline; the conditional component-bootstrap interval is 0.817–0.965. The gain remains 0.848 bits after retaining one representative per whole string while preserving every physical alias. Full-procedure metadata-conditioned permutation references produce no exceedances in 1,000 trials, both for the multi-record population and for a post-pilot uniqueness-conditioned sensitivity. An independently encoded, source-excluded candidate-event test yields 0.725 bits per noninitial event on 74 scored faces, with an interval of 0.551–0.899. In a separate benchmark, exact known-slot restoration improves from 16.99% to 33.81%. Unknown-count internal-gap inference achieves 46.30% after matching the artificial masking law, below a constant-one control at 51.07%. The study contributes measured predictive constraints and a negative count-recovery result for this selected transcription population. Its outcomes concern graphic-code prediction and restoration under specified observation laws.

## 1. Introduction

The short Indus inscriptions present an unusually difficult inference problem. Their graphic sequences are observable, but their linguistic status, underlying language or languages, segmentation, and semantic referents remain disputed. A model can predict an inscription accurately by learning a recurring administrative formula, a family of production templates, or linguistic constraints. Prediction is therefore useful evidence about distributional structure, but insufficient evidence for a reading.

This study asks a narrower question: does local sign context improve out-of-sample prediction after accounting for exact text length, slot position, available archaeological metadata, and known relationships among artifacts? A second question separates two restoration problems that are often discussed together. How well can a model predict a missing glyph when one slot is specified, and how well can it infer how many glyphs disappeared when the length of an internal gap is unknown?

These questions require care about the unit of evidence. Two photographs may show one artifact; two numbered records may be aliases; two separate artifacts may contain identical inscriptions. Keeping such observations in separate training and test folds can reward memorization. Conversely, globally removing repeated strings changes the population being measured and can silently discard physical identifiers needed to prevent leakage. We therefore retain physical aliases and evaluate both the multi-record population and a unique-string sensitivity.

We also test annotation dependence. Compatible historical coding classes can contain several fine codes and overlap. We score these candidate-set events using a forward recursion. This test uses an independent manual encoding of shared archaeological sources, with source families and compatible whole strings excluded from training.

Our evaluation combines observational filters, transitive component grouping, training-only tuning, full-procedure conditional nulls, uncertain-event scoring and separate restoration tasks. Exploratory analysis and code/source audits led to later refinements, whose status is recorded with each endpoint. Detailed procedures are in [methods.md](methods.md), and each principal claim has a [claim–evidence entry](claim-evidence-map.md).

## 2. Related work

Rao et al. (2009) fitted a Markov model, examined functional interchangeability and predicted missing signs using a corpus with identical inscriptions removed. The present study extends this line of work with transitive artifact/string grouping, nested selection and explicit observation laws. Comparing their restoration accuracy with ours requires a common corpus, coding inventory, masking task and split rule. That reproduction is a submission gap [R1].

Historical distributional studies describe initial and terminal classes, recurrent clusters and modified-fish interchangeability. Yadav's 2019 overview reports both M267 and M391 before M99 as predominantly initial pairs. Mahadevan's 1982 and 1986 studies discuss similar terminal environments and replacement among modified fish. Khanna and Merriam (2025) use shared contexts and substitution-resistant pairs. Our frame searches recover these broad classes and evaluate their behavior under different weighting and transfer rules [R2–R4].

Koskenniemi and Parpola (1980) distinguish strict and loose duplicate relationships, including uncertainty and fragments. We implement exact intact-string links and transitive physical aliases for the present export. The retained primary-source audit supplies the historical definitions and page locations [R5].

Sproat (2010) examines the specificity of structural statistics using comparison systems. Nair's April 2026 unreviewed preprint compares administrative template generators and attested symbol corpora, with inference limited to the tested model families. We use an office-routing control to examine the specificity of our held-out predictive/template assay [R6–R7].

## 3. Data and observational scope

### 3.1 Derivative transcription corpus

The main input is [lipi_clean_rtl_singleline.jsonl](../../data/normalized/lipi_clean_rtl_singleline.jsonl), obtained from a pinned derivative export. Its SHA-256 is `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`. The export is associated with a disputed decipherment; proposed sounds, Sanskrit readings and translations were excluded from the analysis. Only observational transcription and metadata fields were used. Acquisition and normalization are documented by the retained [normalization code](../../research/corpus/normalize_lipi.py) and [source definitions](../../data/normalized/source_definitions.json).

The clean input contains 2,930 complete, explicitly right-to-left, single-line records with at least two signs and 1,859 distinct sequences. The principal structural analysis requires at least three signs, leaving 2,107 records and 1,596 distinct sequences. Missing and blank-space codes are excluded from the sign alphabet.

The stored catalogue strings are visual left-to-right lists. We reverse them into computational reading order using documented catalogue conventions. Fuls's explicit example begins with the rightmost sign; the source catalogue represents seals using impressions, so its direction metadata reflects that representation convention. The [orientation clarification](../../research/corpus/orientation_clarification.json) preserves the primary examples. We also evaluate reversed sequences as a model sensitivity.

### 3.2 Dependence and unique-string populations

We connect eligible records if they share a physical artifact identifier or an identical complete string, then take transitive closure. The main population has 1,526 components; its largest contains 36 records. Components remain intact in cross-validation. This closure reduces known leakage without proving that all mould, workshop, depositional or historical aliases have been identified.

The unique-string sensitivity retains one deterministic representative per whole string and the union of every physical alias attached to its copies. It contains 1,596 strings in 1,526 components, with a largest component of nine retained strings. The representative's metadata can differ from the metadata distribution of all copies; unique-string weighting therefore measures a different population. Earlier runs that lost aliases during deduplication are explicitly superseded.

Including two-sign records creates a component containing 804 of the 2,930 records, making fold balance and independence harder to assess. The corresponding unique-string sensitivity accompanies the short-text analysis in the [result index](../../research/methods/RESULT_INDEX.json).

### 3.3 Coding compatibility and independent annotation

The MIT-licensed Mayig corpus provides an independently encoded set of faces from shared historical sources. Its compatible-class crosswalk is [retained separately](../../data/normalized/mayig_wells_class_crosswalk.json). Sharing a historical coding class is weaker than photo-certified fine-glyph identity, and pairwise class intersection is not transitive equivalence.

For the independent-annotator test, 86 faces are marked clear, single-line and at least three glyphs long. Five lack a mapped class and seven have at least one event with no training-supported fine code. The remaining 74 faces represent 73 artifact/P-text groups and 315 noninitial candidate events. Twenty scored faces contain some unsupported alternatives; a fully supported sensitivity includes 54 faces. The test output retains every excluded face and reason.

### 3.4 Access and source uncertainty

The large derivative export has unresolved redistribution terms and remains a private research input. Source-specific licenses and local preservation records govern the linked files. A submission package needs a reproducible access route and explicit release decisions.

Photographic adjudication is incomplete. Source audits exposed compound segmentation differences, uncertain coding classes and identifier/version problems. Such discrepancies limit claims about ancient glyphs even when computations on the frozen codes are correct. The main numbers describe these transcriptions under their declared filters.

## 4. Methods

### 4.1 Predictive models and training-only selection

We use a train-only fine-code vocabulary plus one `UNKNOWN` state. All likelihood models use this same test alphabet. Exact restoration evaluates the original fine code separately, including unseen-code failures.

The independent models are a smoothed unigram model (U), a length/slot model (P), and a length/slot/site/type model (PM). Position counts shrink toward U; metadata counts shrink toward P. The dependent model (PMB) combines PM with a smoothed global predecessor distribution divided by U, then normalizes across the entire vocabulary. At the initial position PMB equals PM. Thus the noninitial gain measures the added local dependency relative to the selected independent baseline.

The principal evaluation has five outer component-held-out folds and three inner component-held-out folds. Within each outer training set, independent model/strength and dependent smoothing are selected using noninitial log likelihood. The candidate smoothing grid is 5, 20, 100, 500 and 2,000. The main multi-record fit selects PM with strength 500 and PMB with strength 100 in all five outer folds. The stronger nested comparison supersedes an earlier fixed-strength pilot whose metadata baseline was too weakly regularized.

Our primary statistic is the summed held-out log-likelihood difference divided by the number of noninitial test signs. Five thousand component-bootstrap draws summarize variation in the already fitted outer-fold scores, conditional on the fitted procedure and selected corpus.

### 4.2 Full-procedure conditional references

We independently shuffle each exact length/slot column within site/type strata, retaining its sign counts and the record metadata. For each shuffled corpus we repeat sequence-dependent grouping, fold allocation, inner selection and held-out prediction. Earlier references retained data-derived groups or discoveries and remain archived as conditional diagnostics.

The main metadata-conditioned reference contains 1,000 corpora. A separate post-pilot sensitivity starts from the unique-string population and rejects shuffled corpora that create any repeated whole string. It samples the exact-column reference conditional on whole-string uniqueness; 1,000 accepted corpora required 6,569 proposals. Each accepted corpus is fitted afresh. The finite-simulation probability is `(1 + exceedances)/(1 + accepted trials)`; the exchangeability assumptions are specified in the detailed methods.

### 4.3 Candidate-event evaluation

Training for the second-annotator test removes every full component touched by source objects M1–M199 or by a fine-code whole string compatible with an eligible test event sequence. This excludes 170 strings and leaves 1,426 training strings in 1,362 components. Model selection uses only those training strings.

For candidate sets A1,…,AL, the dependent score sums compatible fine-code paths using a forward recursion. No unsupported fine code receives credit by being relabelled `UNKNOWN`. Candidate sets can overlap across P labels; the resulting score is the probability of the specified fine-code event, not a normalized predictor over a disjoint P-label alphabet. Main test metadata assumes Mohenjo-daro and `SEAL:S`; a subtype-unspecified sensitivity is reported separately. Ten thousand group-bootstrap draws condition on the fitted training models.

### 4.4 Known-slot restoration

This benchmark uses all 1,596 distinct strings with aliases retained, partitioned into 1,526 components. Each of their 8,009 glyph slots is masked in turn. The independent restorer uses length/position/metadata probabilities; the local restorer computes the normalized Markov posterior given the surviving neighboring signs and fixed full length. It includes the successor transition's candidate-dependent normalizer. Inner component-held-out selection maximizes exact top-one restoration; all outer folds select smoothing 20 for both models. An OOV fine target is not counted correct through `UNKNOWN`.

We report slot-weighted exact top-one and top-k inclusion, plus a conditional component-bootstrap interval for the paired accuracy difference. Equal-text weighting and frequency-stratified summaries reveal which populations drive the aggregate result.

### 4.5 Unknown-count gaps

Each intact unique string receives one internal artificial gap. The erased count k is drawn uniformly from 1,…,min(3,L−2); its start is drawn uniformly among the valid internal starts. A dynamic program marginalizes the missing fine states for candidate counts 1–3, with fixed surviving sides. Models use a training-derived full-length prior and frozen smoothing 20. We compare them with a constant-one count control.

The historical prototype omitted part of the artificial observation law. For a survivor count m and candidate length L=m+k, this law contributes `1/[min(3,L−2)(m−1)]`. The second factor cancels across count candidates, leaving the clipping term. A separate post-audit sensitivity reweights the same saved posteriors by `1/min(3,m+k−2)`, with models and queries held fixed. We preserve both endpoints.

### 4.6 Template and specificity checks

A finite mixture of independent-slot templates is fitted with training-only selection over 16, 32 and 64 components. We compare it with the selected independent baseline and PMB. We also apply the assay to a generated nonphonetic office-routing system whose mechanism is known. This constructive check tests whether failure of this fitted template family uniquely indicates language. Source-ordered totem and weather datasets supply additional feasibility checks, with simultaneous composite units preserved.

## 5. Results

### 5.1 Local dependencies survive the declared controls

| Population | Records/strings | Components | Gain, bits per noninitial sign | Conditional 95% interval |
|---|---:|---:|---:|---:|
| Main eligible records | 2,107 | 1,526 | 0.890 | 0.817–0.965 |
| Unique whole strings, all aliases retained | 1,596 | 1,526 | 0.848 | 0.807–0.890 |
| Main records after three compatible-class merges | 2,107 | 1,506 | 0.930 | 0.862–0.997 |

The main noninitial cross entropy falls from 6.307 to 5.417 bits, a relative perplexity of 0.540. The three-merge sensitivity uses 861→817, 405→390 and 706→705. Reversed computational sequences also give a positive gain.

The full regrouped main reference has no exceedances among 1,000 metadata-conditioned shuffles, giving p=0.000999. Its null mean is −0.1033 bits and its central 95% range is −0.1274 to −0.0800. The uniqueness-conditioned sensitivity also has no exceedances, with null mean 0.0071 and central 95% range −0.0065 to 0.0214. Negative fitted-null gains are possible because dependent models can lose held-out performance through estimation and regularization. The reference comparison, rather than a comparison with zero alone, supports the inference.

Exact endpoints are [main nested prediction](../../research/methods/results/nested_primary/nested_results.json), [alias-preserving unique prediction](../../research/methods/results/nested_unique_preserved_aliases/nested_results.json), [merged prediction](../../research/methods/results/nested_collapsed/nested_results.json), [full main null](../../research/methods/results/joint_nested_primary_1000/joint_nested_results.json), and [uniqueness-conditioned null](../../research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json).

### 5.2 An independently encoded candidate-event test remains positive

The 74 scored faces yield 0.725 bits per noninitial candidate event, with a conditional interval of 0.551–0.899. One representative per P-text gives 0.719 bits on 73 faces. Unspecified seal subtype gives 0.777 bits, and the fully supported 54-face sensitivity gives 0.878 bits. Each sensitivity retains its event population and metadata assumption. The [test output](../../results/independent_annotator/candidate_event_test.json) preserves exclusions, candidate sets, scores and training removals.

The positive result supports transfer across the tested encodings. Shared catalogue compatibility, nonrandom source coverage and removal of wholly unsupported events prevent treating it as universal fine-sign accuracy or independent archaeological replication.

### 5.3 Known-slot prediction improves, with important frequency and calibration limits

| Metric | Independent restorer | Local restorer |
|---|---:|---:|
| Exact top-one | 16.99% | 33.81% |
| Target included in top five | 35.50% | 55.34% |
| Target included in top ten | 45.57% | 62.70% |

The paired top-one improvement is 16.82 percentage points, with a conditional component-bootstrap interval of 15.64–17.98 points. Equal-text means are approximately 17.4% and 32.6%. Exact prediction is concentrated among frequent signs: all 205 singleton types fail fine-code recovery when held out, and macro accuracy across types is much lower than slot-weighted accuracy. Compatible-class merging raises local exact accuracy to 35.90%, showing the effect of target-alphabet granularity.

Model mass is overconfident. In the 0.4–0.6 confidence bin, mean local mass is 0.492 and exact correctness is 0.384; in the 0.8–1.0 bin, they are 0.896 and 0.838. The benchmark and complete calibration bins are in [benchmark.json](../../results/restoration/benchmark.json).

Cross-site known-slot sensitivities exclude entire components touching the raw held-out site. Improvements are 14.94 points at Mohenjo-daro on 866 unique texts, 15.48 at Harappa on 496, and 17.93 at Lothal on 51. These are separate transfer populations with different vocabulary coverage; small-site precision is limited. The [cross-site output](../../results/restoration_crosssite/crosssite.json) records intervals and removals. Structural site-transfer results must use the separate corrected [transitive transfer file](../../research/methods/results/nested_primary/transitive_site_transfer.json), not older direct-overlap fields.

### 5.4 Unknown erased counts are not reliably recovered

| Count predictor | Historical prototype | Artificial-design-matched sensitivity |
|---|---:|---:|
| Independent | 41.92% | 45.61% |
| Local | 43.05% | 46.30% |
| Constant one | 51.07% | 51.07% |

The historical local-minus-independent improvement is 1.13 points, with an interval spanning zero. After matching the observation law, it is 0.689 points (−0.569 to 1.940). The matched local model is 4.762 points below the constant-one control (interval −7.775 to −1.726). Count recovery therefore fails its design control. Endpoints are [the original benchmark](../../results/gap_restoration/gap_benchmark.json) and [the matched-law sensitivity](../../research/methods/results/gap_design_matched/gap_design_matched.json).

### 5.5 Residual predictive gain is not specific to language

The extended template model improves on the independent baseline by 0.142 bits per noninitial sign. PMB exceeds it by 0.748 bits (0.688–0.809). On the office-routing control, whose mechanism is ordered and nonphonetic, PMB exceeds the same template family by 0.631 bits (0.588–0.677). The residual dependence is shared by the Indus transcription and this constructed control.

The source-preserved totem test has approximately 43.7% noninitial OOV tokens. Its fitted gain lies within the conditional null reference. Station/text closure joins the weather corpus into one component, making grouped cross-validation infeasible. Outputs are [Indus templates](../../research/methods/results/templates_extended/template_results.json), [office templates](../../research/methods/results/workflow_templates/template_results.json), and the [comparison-data documentation](../../research/literature/nonlinguistic_controls/README.md).

## 6. Discussion

The local predictive constraint survives unique-string weighting and the tested alternate encoding. A proposed generative model can now be evaluated against these held-out gains, using the same component exclusions and target alphabet. The contrast with the office-routing control also identifies a limitation of the fitted independent-slot template family: both systems retain dependencies that it leaves unexplained.

Restoration separates two inference problems. A known slot allows local context to rank glyphs; an unknown count also requires a length model and an observation mechanism. The measured difference suggests that a count-recovery extension needs additional evidence or a different predictor. Historical specimens can supply gap width, surviving traces, line layout and spacing, with reference uncertainty recorded in a new benchmark.

Adjacent project experiments give mixed results. The independent-text seal/tablet contrast is positive; the Bull1 contrast is negative. Matched known-period microcontext probabilities range from 0.0560 to 0.0864 across weighting/merging variants. Aggregate substitution transfer changes with repeated-text weighting and class treatment. The [retrospective](../../knowledge/retrospectives/methods.md) records these paths and their failed or superseded variants.

A separate audit enumerates four positive integer solutions to Fuls's proposed equations. Selecting 10/8/6 requires the additional range restriction. The [numerical directions](../../knowledge/directions/numerical-methods.md) identify the required source joins and propose held-out externally measured quantity tests.

## 7. Limitations

The main source is a derivative transcription with disputed accompanying interpretations and incomplete primary photographic adjudication. Known aliases do not exhaust production and excavation dependencies. Unique-string representatives change metadata weighting. The three compatible-class merges cover only a small portion of graphic uncertainty and are not expert allograph decisions.

The likelihood alphabet pools unseen codes into `UNKNOWN`; candidate events and exact glyph restoration have different semantics. Candidate-event exclusions favor cases that have at least some training support. Neither bootstrap interval includes every source of curation and model uncertainty. The conditional references assume exchangeability within declared columns and do not represent every historical mechanism.

Several safeguards and sensitivity designs were added after pilots or errors were identified and retain their post-pilot status. A common-protocol reproduction remains necessary for performance comparisons with earlier publications or newer models.

Connecting a predictive constraint to a sound or meaning requires an externally fixed lexical or numerical anchor. The present likelihoods remain invariant under relabelling of freely adapted semantic models, leaving those assignments unidentified.

## 8. Reproducibility and publication status

The retained environment for the structural analyses is Python 3.13.5 with NumPy 2.2.6 and standard-library modules. Image and PDF source audits require additional packages documented in their retained scripts. Seeds, input/source hashes, model choices and permutation outcomes are embedded in the result JSON. Eight integrity checks cover normalization, OOV handling, component leakage, alias retention, transitive site exclusion, null marginals, frame counting and synthetic specificity. Commands are in [the detailed methods](methods.md) and [the original reproduction guide](../../research/methods/REPRODUCING.md).

External reproduction, epigraphic source review, access/release decisions and a fresh frozen evaluation remain open. The [submission-gap register](submission-gaps.md) specifies those tasks and the required completion evidence.

## 9. References

**R1.** Rao, R. P. N., Yadav, N., Vahia, M. N., Joglekar, H., Adhikari, R., and Mahadevan, I. (2009). *A Markov model of the Indus script*. PNAS 106, 13685–13690. [DOI](https://doi.org/10.1073/pnas.0906237106); [author-hosted primary PDF](https://homes.cs.washington.edu/~rao/PNASIndus.pdf).

**R2.** Yadav, N. (2019). *Structure of Indus Script*. Indian Journal of History of Science 54(2), 125–134. [Primary PDF](https://insa.nic.in/writereaddata/UpLoadedFiles/IJHS/Vol54_2_2019__Art01.pdf), Table 1, printed p.127. [DOI](https://doi.org/10.16943/ijhs/2019/v54i2/49656).

**R3.** Mahadevan, I. (1982), *Terminal ideograms in the Indus script*, and (1986), *Towards a grammar of the Indus texts*. Primary scans, exact inspected pages and retained OCR are indexed in [the primary-evidence matrix](../../research/literature/evidence_and_novelty_matrix.md). Proposed meanings in these works are author interpretations.

**R4.** Khanna and Merriam (2025). *A Computational Analysis of the Indus Script: Identifying Sign Functions in Logo-Syllabic Writing Systems*. IJCA 187(64), 19–22. [Primary PDF](https://www.ijcaonline.org/archives/volume187/number64/khanna-2025-ijca-926075.pdf); [DOI](https://doi.org/10.5120/ijca2025926075).

**R5.** Koskenniemi, K., and Parpola, A. (1980). Primary documentation, pp.54–56. [Retained source](../../research/corpus/primary/koskenniemi_parpola1980.pdf); exact bibliographic and duplicate definitions are preserved in the corpus source audit. Complete reference metadata requires editorial verification before submission.

**R6.** Sproat, R. (2010). *Last Words: Ancient Symbols, Computational Linguistics, and the Reviewing Practices of the General Science Journals*. Computational Linguistics 36(3), 585–594. [Primary record and PDF](https://aclanthology.org/J10-3012/).

**R7.** Nair, A. (2026). *How Non-Linguistic Is the Indus Sign System? A Synthetic-Baseline Scorecard*. arXiv:2604.17828v1, 20 April 2026. [Primary version](https://arxiv.org/html/2604.17828v1), §§4.2 and 5.7. Unreviewed preprint as inspected.

**R8.** Mayig, *Digital corpus of Indus Valley Script*. [Repository](https://github.com/mayig/indus-valley-script-corpus). Pinned source, license and crosswalk provenance are retained in the corpus manifests.

**R9.** Fuls, A. (2020), *Ancient Writing and Modern Technologies – Structural Analysis of Numerical Indus Inscriptions*. Inspected in the 2023 author reprint, printed pp.15–48. [Exact source and premises](../../research/literature/metrology/numerical_source_premises.json); [conditional audit](../../research/methods/NUMERICAL_CONSTRAINT_AUDIT.md).

The broader publication-priority, source-identity and retrieval audit is [retained here](../../research/literature/evidence_and_novelty_matrix.md). References with unresolved metadata must be completed from their original title pages before journal submission.
