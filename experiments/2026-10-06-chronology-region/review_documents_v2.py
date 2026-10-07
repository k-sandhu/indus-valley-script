"""Build the five authorized D1 documents from preserved and amended aggregates.

Use --output-dir FRESH_DIR to review generated documents elsewhere. The explicit
--update-authorized-documents flag permits only the five coordinator-approved
document updates in this package. Scientific endpoints are read-only inputs.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
OWN=Path(__file__).resolve().parent
ENDPOINT='review-response-2026-10-07-v1'
SOURCE='review-response-sources-2026-10-07-v1'
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def f(value): return f'{value:.6f}'
def interval(values): return f'[{values[0]:.3f}, {values[1]:.3f}]'
def markdown(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',*['| '+' | '.join(map(str,row))+' |' for row in rows]])

def documents():
    data=read(OWN/ENDPOINT/'permutation_tests.json')['tests']
    select=lambda theme,name,unit='physical_component',seed=21:next(r for r in data if r['theme']==theme and r['comparison']==name and r['unit']==unit and r['seed']==seed)
    def frequency_rows(theme,names,unit='physical_component'):
        rows=[]
        for name in names:
            a,b=select(theme,name,unit),select(theme,name,unit,22)
            rows.append([name.replace('__',' / ').replace('_',' '),f"{a['a']['faces']} / {a['b']['faces']}",
                f(a['effect_js_bits']),f(a['null_js_mean']),f(a['excess_js_bits']),f"{a['holm_p']:.5f} / {b['holm_p']:.5f}"])
        return rows
    columns=['Comparison','Faces A / B','Observed JS bits','Null mean, seed 21','Excess, seed 21','Holm p, seeds 21 / 22']
    time_table=markdown(columns,frequency_rows('time',['2__3C','3B__3C'])+frequency_rows('subset',['period_labelled','mound_e']))
    time_closure=markdown(columns,frequency_rows('time',['3B__3C'],'full_text_closure')+frequency_rows('subset',['period_labelled','mound_e'],'full_text_closure'))
    names=[r['comparison'] for r in data if r['seed']==21 and r['theme']=='region' and r['unit']=='physical_component']
    region_table=markdown(columns,frequency_rows('region',names))
    region_closure=markdown(columns,frequency_rows('region',names,'full_text_closure'))
    raw_rows=[]
    for theme,name in [('time','3B__3C'),('subset','period_labelled'),('subset','mound_e')]:
        r=select(theme,name); stat=r['statistics']['raw_frequency_js_bits']
        raw_rows.append([name.replace('__',' / ').replace('_',' '),f(stat['observed']),f(stat['null_mean']),f(stat['excess_over_null'])])
    raw_table=markdown(['Frequency frame','Raw JS bits','Null mean, seed 21','Excess, seed 21'],raw_rows)
    positional_rows=[]
    for theme,name in [('time','3B__3C'),('subset','period_labelled')]:
        r=select(theme,name)
        for position in ['initial','terminal']:
            stat=r['statistics'][position+'_js_bits']
            positional_rows.append([name.replace('__',' / ').replace('_',' '),position,f(stat['observed']),f(stat['null_mean']),f(stat['excess_over_null'])])
    position_table=markdown(['Frame','Position','Equal-type JS bits','Null mean, seed 21','Excess, seed 21'],positional_rows)
    length=read(OWN/ENDPOINT/'length_comparisons.json')['comparisons']
    length_table=markdown(['Frame','Common faces 3B / 3C','Raw length change, slots','Equal-type change, slots','Conditional 95% interval'],
        [[r['subset'].replace('_',' '),f"{r['common_a']['faces']} / {r['common_b']['faces']}",f(r['raw_length_difference_slots']),f(r['equal_type_length_difference_slots']),interval(r['length_interval95'])] for r in length])
    media=read(OWN/ENDPOINT/'media_comparisons.json')['comparisons']; media_rows=[]
    for name in ['all','period_labelled','mound_e']:
        a,b=[next(r for r in media if r['subset']==name and r['seed']==s) for s in [21,22]]
        rich=a['effects']['rarefied_richness_difference']; shannon=a['effects']['rarefied_shannon_difference_bits']
        media_rows.append([name.replace('_',' '),f"{a['families_3B']} / {a['families_3C']}",f"{a['faces_3B']} / {a['faces_3C']}",a['family_budget'],
            f"{f(rich['effect'])} {interval(rich['interval95'])}",f"{f(shannon['effect'])} {interval(shannon['interval95'])}",
            f"{rich['holm_p']:.4f} / {b['effects']['rarefied_richness_difference']['holm_p']:.4f}",
            f"{shannon['holm_p']:.4f} / {b['effects']['rarefied_shannon_difference_bits']['holm_p']:.4f}"])
    media_table=markdown(['Frame','Families 3B / 3C','Faces 3B / 3C','Budget','Rarefied richness change [interval]','Shannon change, bits [interval]','Richness Holm 21 / 22','Shannon Holm 21 / 22'],media_rows)
    report=f'''# Chronology, region and external inscriptions

Harappa's 3B–3C sign-frequency comparison exceeds its physical-family permutation reference in the full sample and among period-labelled faces. On Mound E the corrected p-value exceeds .05. The length increase is much smaller in the restricted excavation frames. Regional results retain four of six physical-family rejections; larger runs give two of six under copied-text closure. The seven matched external objects provide little coverage of the non-canonical circular-seal class. Exact estimates and populations follow below.

The first-pass endpoint is **Frozen evaluation**. Its support repairs, caption-led assays and this review response are **Exploratory**. The [Sonnet review](REVIEW.md) reproduced all 60 aggregate files and 380 quoted numbers, then identified interpretation problems. The [second amendment](REVIEW-AMENDMENT-2026-10-07.md), appended to [PROTOCOL.md](PROTOCOL.md), specifies the response after those problems were known. Old endpoints, source manifests and review files are unchanged. [Document snapshots](review-response-baseline-2026-10-07-v1/) retain the earlier wording.

## Shared inputs and reference assumptions

The observational input has 5,680 faces, 4,695 physical families, 3,477 transitive complete-text components, 19,946 observed slots, 18,067 known tokens and 1,879 unreadable `000` slots. Its vocabulary has 713 known codes. Frequency calculations omit `000` and retain partially readable faces with at least one known token. Ordered analyses require complete, single-line R/L texts without blanks or `000`, giving 2,930 faces. [Original audit](main-2026-10-07-v1/audit.json), `population`, `vocabulary_known_signs`; [new audit]({ENDPOINT}/audit.json), `population`.

Physical families join object-family identifiers and catalogue aliases before selection. The family reference permutes complete physical components within exact object-type and selected-face-count blocks. Text closure adds transitive links through identical complete known texts over the full corpus, before orientation filtering. Mixed-label or mixed-type components are excluded from a comparison. The largest physical component contains seven faces; the largest text component contains 1,038. Thus closure tests can use a different population. These procedures reuse [Paper 002](../../papers/002-conditional-reference-laws/) and [conditional_structure.py](../../src/methods/conditional_structure.py). They condition on recorded objects and assume exchangeable labels within blocks; excavated area, preservation and production-batch selection are absent from the input.

Equal-type frequencies average supported type-specific distributions. Common support requires ten physical families per arm and type. Region is fixed by site in every input row; equal-site weighting describes the sampled site frame, and a region effect conditional on fixed site is unidentifiable. Sequence folds keep complete text components together. [Original selection rules](PRECOMPUTATION_CLARIFICATION.md); [audit](main-2026-10-07-v1/audit.json), `site_region_multimapping=0`; [actual fold counts](exploratory-2026-10-07-v1/actual_fold_counts.json).

The new runs use seeds 21 and 22, 19,999 allocations for time and restricted-time tests, and 9,999 for the other permutation references. Frequency p-values have separate Holm families for time, region and the two excavation subsets, within each dependence reference. Sign tests use BH across the original 24 time or 314 regional hypotheses. The tables print each observed divergence, its own null mean and their difference. Means shown are seed 21; [divergence_baselines.csv]({ENDPOINT}/divergence_baselines.csv) also gives seed 22, finite-draw counts and raw/positional statistics. Null excess describes this conditional permutation reference. No usable confidence interval is supplied for JS magnitudes: both earlier bootstrap constructions exclude the observed time divergence, and no replacement with demonstrated coverage was obtained. [Interval withdrawal]({ENDPOINT}/permutation_tests.json), `statistics.*.magnitude_interval95` and `interval_status`.

## 1. Harappa through time

The calendar mapping follows J. Mark Kenoyer and Richard H. Meadow, *Inscribed Objects from Harappa Excavations 1986–2007* (2010), *Corpus of Indus Seals and Inscriptions* 3(1), xliv–lviii, printed xlv/Table 1, physical PDF page 4. It assigns Period 1 approximately 3700–2800 BCE, 2 to 2800–2600, 3A to 2600–2450, 3B to 2450–2200 and 3C to 2200–1900. Period 4 has questioned 1900–1800 boundaries; Period 5 extends from approximately 1800 to later than 1300. Labels such as 3C-2 are mapped by prefix. The source does not provide an independently checked calendar ordering of those numbered export subphases. Only Harappa receives HARP ages. [Primary PDF](https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf); [label mapping](main-2026-10-07-v1/period_mapping.json); [boundary notes](mapping-notes.json).

| Harappa assignment | Faces | Known tokens | Unreadable slots | Clear faces |
|---|---:|---:|---:|---:|
| 1 | 2 | 4 | 1 | 0 |
| 2 | 30 | 36 | 8 | 2 |
| 3A | 1 | 1 | 0 | 0 |
| 3B | 201 | 461 | 57 | 82 |
| 3C | 574 | 1,849 | 151 | 321 |
| 4 | 27 | 89 | 13 | 14 |
| 5 | 9 | 32 | 2 | 5 |
| Interval: 3B/C or broad 3 | 1,095 | 2,691 | 268 | 589 |
| Undated | 778 | 2,015 | 296 | 348 |

The table sums [original major/type strata](main-2026-10-07-v1/harappa_major_type_strata.csv). Current presentation copies suppress sparse cells as described below; total denominators above include them. A span 3B/C admits both periods, and broad Period 3 admits 3A, 3B and 3C. Primary comparisons use unambiguous assignments. Earlier whole-family extreme assignments and 100 uniform admissible-period allocations are preserved in [interval_sensitivity.json](main-2026-10-07-v1/interval_sensitivity.json). They describe sensitivity to specified date allocations.

### Excavation composition and frequency

| Composition of unambiguous faces | 3B | 3C |
|---|---:|---:|
| Period-field labels | 192 | 169 |
| Stratum labels | 9 (4.48%) | 405 (70.56%) |
| Mound E | 180 (89.55%) | 74 (12.89%) |
| Mound F | 13 (6.47%) | 413 (71.95%) |
| Mound AB | 2 | 61 |
| Mound J | 0 | 5 |
| Unknown mound | 6 | 21 |

A stratum label has `Stratum` in `metadata.phase`; other dated rows have an explicit period field. Mound is the prefix of `area-section`. The HARP 2010 contents page, physical PDF page 2, assigns H-1020–H-1520 and H-2590 to old excavations, and H-1521–H-2583 to HARP. All nine 3B stratum faces have earlier-range H-numbers. Of the 405 3C stratum faces, 392 have such numbers, ranging H-1–H-1517; 13 have no catalogue number. This sharpens the review's group-level count: 405 is the stratum total, while 392 is the directly numbered earlier-catalogue subset. Catalogue ranges are proxies for source composition, without supplying manufacture dates. [Composition]({ENDPOINT}/excavation_composition.csv), `period`, `label_source`, `mound`, `faces`; [catalogue check]({ENDPOINT}/catalogue_number_ranges.csv), `faces_earlier_proxy`, `faces_with_H_number`; [source check]({SOURCE}/sources.json), `stored_source_checks`.

The full known-token comparison shares SEAL:S, TAB:B and TAB:I; restricted physical comparisons share TAB:B and TAB:I. Whole-family restrictions lose no mixed-origin or mixed-mound families because none occurs in the Harappa input. The following frequency tests use physical families; raw and adjusted distributions share each row's retained population.

{time_table}

{raw_table}

[Tests]({ENDPOINT}/permutation_tests.json), `theme=time/subset`, `unit=physical_component`, `a/b`, `common_types`, `statistics`. The full 3B–3C row uses 110/335 physical families and 455/1,547 known tokens, including 44/102 unreadable slots. Period-labelled support has 97/60 families, 414/269 known tokens and 40/20 unreadable slots; Mound E has 93/34 families, 398/156 known tokens and 38/11 unreadable slots. The pottery-only Period 2–3C row has 29/13 families and 35/23 known tokens. Its updated Holm values exceed .05. Period 2–3B has no supported common type.

Text closure gives the following separate populations and references:

{time_closure}

Full closure drops 262 mixed-label and nine mixed-type faces. Its 89/148 faces belong to 142 retained text components. The restricted closure rows also fail Holm .05. The two seeds agree on all frequency decisions. [Seed agreement]({ENDPOINT}/seed_agreement.json), `frequency_tests`; [component exclusions]({ENDPOINT}/permutation_tests.json), `excluded`, `components`. The positive full-sample family result and the weaker closure/subset results support a graphic difference in the observed frame, with incomplete separation of chronology from excavation and copying.

### Length, positions and sequences

{length_table}

[Length results]({ENDPOINT}/length_comparisons.json), `comparisons`, with within-type means in [length_type_means.csv]({ENDPOINT}/length_type_means.csv). Raw changes use all faces with a known sign in each selected excavation frame. The all-tablets row retains the full raw frame and restricts its adjusted estimate to TAB:B/TAB:I. Intervals resample 999 whole physical families within observed exact-type/face-count signatures. The full adjusted increase of 0.724 slots falls to 0.162 among period-labelled tablets and 0.116 on Mound E, with restricted intervals spanning zero. The original full-sample estimate should therefore not be read as a uniform temporal increase.

{position_table}

[Positional baselines]({ENDPOINT}/divergence_baselines.csv), `statistic=initial_js_bits/terminal_js_bits`, `theme=time/subset`, `unit=physical_component`. These are descriptive positional effects with the same conditional null construction; frequency Holm values do not test them. The full shared tablet support has 77/198 clear faces. Mound E has no type reaching ten clear families in both periods, so its type-adjusted positional comparison is unsupported. Internal-bigram conditional entropy on all clear texts rises from 0.89853 to 1.88940 bits; averaging the two tablet types gives 0.59844 to 0.83227. The sample grows from 82 to 321 clear texts, which also raises empirical sequence diversity. [Preserved sequence summary](exploratory-2026-10-07-v1/sequence_summary.json), `periods.raw`, `equal_type_mean_conditional_bigram_entropy_bits`.

Sign 034 changes by −2.34048 percentage points on the full equal-type frame. The historical linear-frequency family-bootstrap interval is [−3.8178, −0.9469] points. Larger time-family tests give p=.00180/.00185 and BH q=.0432/.0444 for seeds 21/22. It passes both seeds; every other time sign and all 314 regional signs fails BH .05. The old statement of zero time-sign passes is superseded. [New sign tests]({ENDPOINT}/sign_tests.csv), `theme=time`, `sign=034`, `p`, `bh_q`; [historical frequency interval](main-2026-10-07-v1/sign_tests.csv), `ci95_low/high`. This interval is conditional on the recorded family sample and supplies no independent archaeological dating evidence.

### Observed first and last occurrences

The attestation table covers 368 signs; interval labels leave 209 earliest and 89 latest bounds unresolved. Eighty-eight signs first occur unambiguously in 3C in this sample. Five last occur in 3B: 062, 074, 222, 242 and 327, borne by 1, 1, 2, 2 and 1 families. For 015, one family supplies the first 3C occurrence. Zero recorded occurrences in 115 3B families permits a one-sided 95% presence bound of 2.5713%; the single 3A family permits 95%, under independent-family sampling. Unreadable slots and interval assignments widen the evidence beyond these readable bounds. [Attestation bounds](main-2026-10-07-v1/harappa_attestation_bounds.csv), `earliest_observed_lo/hi`, `latest_observed_lo/hi`; [presence](main-2026-10-07-v1/harappa_component_presence.csv), `zero_count_one_sided95_upper`; [type-specific bounds](exploratory-2026-10-07-v1/attestation_by_type.csv). Secure early objects, stratum-to-period source documentation and narrower context dates would sharpen introduction/disappearance bounds.

## 2. Regional usage and sequence transfer

The eligible regional pairs retain the original common-type selections. Their physical-family references are:

{region_table}

Complete-text closure changes those selections:

{region_closure}

Both seeds give four physical-family and two closure rejections. Inter-Riverine–Gujarat/Kutch now joins Lower Indus–Eastern Headwaters under closure; the original 499-draw result had only the latter. No regional individual sign passes BH, with minimum q=.0785/.0942. [Updated tests]({ENDPOINT}/permutation_tests.json), `theme=region`, `a/b`, `common_types`, `statistics`; [seed/sign summary]({ENDPOINT}/seed_agreement.json). Each printed JS has its matching null mean and excess; none has a usable magnitude interval.

Original raw, equal-type and equal-site/type frequencies, positions and token rarefactions are retained in [region_comparisons.json](main-2026-10-07-v1/region_comparisons.json) and [rarefaction.json](main-2026-10-07-v1/rarefaction.json). Rarefaction equalizes known-token effort by type. Eastern Headwaters shares only 29 pottery and 79 square-seal tokens in the relevant rarefaction cells. Its small population and the lack of site-crossed regions limit inference beyond those sampled sites. The new [baseline table]({ENDPOINT}/divergence_baselines.csv) supplies raw and positional null summaries on each retained component population; the site-balanced descriptive estimand has no fixed-site regional test.

The fixed first-order sequence model uses half-count unigram smoothing and transition shrinkage 20. It compares other-region and within-region models on identical held-out faces, with complete text components confined to folds. Equal-type/site test weighting gives:

| Region | Test faces / families | Within / other bits per sign | Other-minus-within [conditional 95% interval] | Equal training-component excess [interval] |
|---|---:|---:|---:|---:|
| Inter-Riverine | 861 / 668 | 6.65469 / 7.29329 | 0.63860 [0.53459, 0.75535] | 0.26346 [0.09530, 0.37548] |
| Lower Indus | 1,037 / 1,008 | 7.10144 / 7.37572 | 0.27428 [0.11884, 0.44392] | 0.18223 [0.03222, 0.33147] |
| Gujarat/Kutch | 114 / 114 | 7.58400 / 6.51644 | −1.06756 [−1.48527, −0.62911] | −0.03030 [−0.18635, 0.15856] |

[Preserved models](main-2026-10-07-v1/regional_models.json), regional `adjusted.test`, `adjusted.losses`, `training`; [conditional test-loss intervals](exploratory-2026-10-07-v1/model_intervals.json), `losses.type_excess/size_excess`. Intervals resample saved test losses while holding fitted models fixed. Matching training-component budgets removes most of Gujarat/Kutch's apparent transfer advantage. Eastern Headwaters and Upper Indus lack a type with 20 training faces in every fold. Additional independently sampled sites per region, production groups and training-refit uncertainty would make regional generalization more informative.

## 3. External and non-canonical inscriptions

The external field set contains 42 faces/families, 149 known tokens and 19 unreadable slots: Persian Gulf 17 faces, Mesopotamia 11, Iranian Plateau 11 and Central Asia 3. Sixteen faces pass the ordered-text filter; nine lack exact type/length support. Matching retains seven objects, from those regions in counts 3/1/1/2. Seven of the eleven Iranian Plateau rows are Baluchistan/Makran sites in the package mapping, and the matched row is from Nindowari-damb. The retained types are mostly standard Indus square seals, with an incised tablet and pottery graffiti. Parpola's 2018 section I.C describes Gonur/Shortughai examples as classical Indus seals. This endpoint consequently gives little coverage of the non-canonical circular class. [Original external selection](main-2026-10-07-v1/external_models.json), `external_all`, `external_eligible`, `matched_faces`, `by_region`; [reviewed site counts](review/external_codes_and_sites.json); [mapping](mapping-notes.json).

Each external text is scored against a core model excluding its test fold and all external-touched text components. Comparator texts share exact type, observed length and fold. The external exact-type loss is 7.87617 bits/sign, versus 7.22528 for matches: excess 0.65090, family-bootstrap interval [−0.37986, 1.85719]. A pooled model gives excess −0.08632. Exact-type bigram novelty excess is 0.05269 [−0.17347, 0.27994] on seven objects; trigram excess is 0.10629 [−0.10270, 0.26747] on four. The enlarged six-statistic sign-flip family gives Holm 1.000 in both seeds for every score. Exact enumeration of the seven-family type-loss reference gives p=.359375; Monte Carlo p=.3650/.3628. [Fixed-model results](main-2026-10-07-v1/external_models.json), `results`; [new flips]({ENDPOINT}/other_permutation_references.json), `external_score_sign_flips`. These conditional intervals do not represent excluded types or refitted-model uncertainty.

The [corrected literature checklist]({SOURCE}/external_literature_check.csv) replaces Ur's erroneous Parpola 2018 attribution with the Frenez Harappa.com image 1 caption, a secondary site lead. Ra's al-Junayz is a general Oman lead rather than a named caption location. Individual object identities and non-canonical classifications still need original plates and find contexts. Regional field membership alone supplies neither a language class nor evidence for patronymics.

## Published precedents and the scope of the contribution

Nisha Yadav, *Sensitivity of Indus Script to Site and Type of Object* (2013), *SCRIPTA* 5:67–103, directly compares site/type usage and lengths; printed 85 reports frequent West Asian Mahadevan signs including sign 1. Michael Philip Oakes, *Statistical Analysis of the Tables in Mahadevan’s Concordance of the Indus Valley Script* (2019, online 2017), *Journal of Quantitative Linguistics* 26:22–47, studies positional and metadata associations. These establish regional/type/position precedents. [Yadav PDF, printed 79–85 and 91](https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf); [Oakes manuscript, abstract](https://wlv.openrepository.com/bitstreams/8f84dd81-ba40-4036-86aa-992596cf289c/download).

Ayuha Suga, *Diachronic Changes in the Indus Script Based on the Proposed Arrangement of the Indus Seal* (2024), *Journal of General Linguistics* 26–27:25–65, analyzes 1,137 seals in proposed 3A/3B/3C arrangements. Its exact title has no colon. Gregg Jamison, Akinori Uesugi and Yuji Yamaguchi, *Unicorns and seals: New multivariate approaches to exploring patterned stylistic variation in the Indus Civilization* (2023), *Archaeological Research in Asia* 36:100486, supplies a recent stylistic precedent at abstract/bibliographic scope. Andreas Fuls, *Corpus of Indus Inscriptions* (2022), *Mathematica Epigraphica* 3, is retained as a catalogue bibliography only. The earlier section 1.3/1.4 content attribution is withdrawn: the reviewer could not reproduce it, and direct downloads again returned 403. A current cached web excerpt is distinguished from a preserved PDF witness. [Suga PDF, title page and printed 32–34](https://www.lingua.tsukuba.ac.jp/ippan/JGL/2024/GL26-27_3_paper2.pdf); [Jamison author record](https://okayama.elsevierpure.com/en/publications/unicorns-and-seals-new-multivariate-approaches-to-exploring-patte/); [Fuls author record](https://www.researchgate.net/publication/373522666_Corpus_of_Indus_Inscriptions); [corrected access record]({SOURCE}/sources.json), `sources`.

Rajesh P. N. Rao, Nisha Yadav, Mayank N. Vahia, Hrishikesh Joglekar, R. Adhikari and Iravatham Mahadevan, *A Markov model of the Indus script* (2009), *PNAS* 106:13685–13690, Table 2 compares eight West Asian strings with Indus texts. Asko Parpola, *Indus Seals and Glyptic Studies: An Overview* (2018), in *Seals and Sealing in the Ancient World*, 127–143, provides external seal context. D1 repeats the broad questions and refines their observational tests through physical/copying groups, explicit interval labels, exact object-type/length support and excavation-frame sensitivity. Publication priority is not established. [Rao PDF, page 5/Table 2](https://homes.cs.washington.edu/~rao/PNASIndus.pdf); [Parpola proof, section I.C](https://tuhat.helsinki.fi/ws/portalfiles/portal/127255979/Parpola_Asko_2018_Indus_Seals_and_Glyptic_Studies_An_Overview_final_proof_2016_.pdf). Original [sources.json](sources.json), [sources-post-launch.json](sources-post-launch.json) and the [correction manifest]({SOURCE}/sources.json) preserve exact bibliographies, access scopes and failed routes.

## Caption-led post-launch assays

These assays follow the coordinator's [caption check](../2026-10-06-research-program/frenez-talk-check.md) and [7 October protocol](POST-LAUNCH-PROTOCOL-2026-10-07.md). The candidates preceded the matched-frequency computation according to file times; broad per-region frequencies already existed. Their nomination cannot be characterized as independent of all earlier counts. Exact lecture-slide identifications were not inspected.

### Human and paired-human signs

| Candidate | Wells / Mayig | Finnish chart IDs, column 0 | Graphic scope |
|---|---|---|---|
| Simple human | 090 / P013 | 133/535, rows 26–27 | Primary man candidate; Mayig M001 |
| Paired humans | 091 / P016 | 110/692, rows 31–32 | Primary twins candidate; Mayig M002 |
| Modified human | 093 / P014 | 394, row 28 | Declared single-figure alternative |
| Bracketed human | 097 / P015 | 518/150, rows 29–30 | Alternative sharing Mayig M002 |

The atlas index `pdf_page=20` is zero-based, physical PDF page 21. Its source is Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), University of Helsinki Research Reports 1. The Mayig compatibility arrays and their derived Wells crosswalk are one annotation source. The review's independent positional join agrees at nine of eleven relevant 090/093/P013/P014 positions, while no position tests 091/097. Wells 091 therefore still lacks an independent code check. [Identification output](post-launch-2026-10-07-v1/sign_identifications.json); [schema](../../data/normalized/mayig_sign_schema.json), `signs.P013/P016/P014/P015`; [crosswalk](../../data/normalized/mayig_wells_class_crosswalk.json), `by_wells_id`; [alignment check](review/lipi_mayig_alignment.json); [chart source](https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/).

Raw 090 usage is 7/149 external known tokens (4.69799%) versus 184/17,792 core (1.03417%); 091 is 5/149 (3.35570%) versus 22/17,792 (0.12365%). All twelve external target tokens occur on the eighteen circular seals. Every 090 occurrence fails the ordered-text filter. Four 091 occurrences pass but have zero or one core family in their exact cells, below the minimum two. The matched frequency frame retains seven external faces/30 tokens against 958 core faces/881 families/3,042 tokens, and contains no external target occurrence. Equal-type matched excesses are −0.28739 and −0.01228 percentage points, with historical grouped intervals [−0.55029, −0.06202] and [−0.07366, 0.00000]. Both seeds give enrichment Holm 1.000 for all six candidate sets under physical and text references. [Raw/matched counts](post-launch-2026-10-07-v1/external_target_counts.csv); [matched effects/intervals](post-launch-2026-10-07-v1/external_frequency.json), `results`; [selection](post-launch-coverage-2026-10-07-v1/external_selection_counts.csv); [new references]({ENDPOINT}/other_permutation_references.json), `external_targets`. The published circular-class observation remains unsupported by exact matching here; reviewed direction metadata and same-type/length core circular comparators are the missing inputs.

Massimo Vidale, *Growing in a Foreign World: For a History of the “Meluhha Villages” in Mesopotamia in the 3rd Millennium BC* (2004), *Melammu Symposia* 4:261–280, printed 270 discusses man and variants and cites Parpola 1986:411 for the patronymic hypothesis. It does not discuss twins there. Vidale's *The Short-Horned Bull on the Indus Seals: A Symbol of the Families in the Western Trade?* (2005), *South Asian Archaeology 2003*:147–158, Figure 5, printed 155, supplies the separate graphic/distribution precedent. Steffen Terp Laursen, *The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC* (2010), *Arabian Archaeology and Epigraphy* 21:96–134, explicitly discusses prefixed twins in its abstract, printed 96. The newly acquired primary PDF confirms that passage. [Vidale 2004 PDF](https://www.harappa.com/sites/default/files/201402/Vidale-Indus-Mesopotamia.pdf); [Vidale 2005 PDF](https://publications.dainst.org/books/dai/catalog/view/2043/2440/4491); [Laursen primary PDF](https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf). These frequency observations leave the proposed patronymic meaning untested. Parpola 1983/1986/1994 full underlying analyses remain bibliographic leads in the source manifests.

### Inscribed-media diversity around the 3C date bin

Harappa has 1,921 physical families and 2,717 faces. Media counting includes unreadable inscribed objects because their type is observed. In the full 3B/3C sample there are 115/444 families, five/fourteen exact types and Shannon diversity 1.56323/2.53051 bits. Period-labelled families have five/nine types; Mound E has four/eight. Equal-family rarefaction and 999 whole-family bootstrap summaries give:

{media_table}

[New comparisons]({ENDPOINT}/media_comparisons.json), `comparisons.*.effects`; [type counts]({ENDPOINT}/media_type_counts.csv), `subset`, `period`, `type`, `families`, `faces`; [all-period counts/diversity](post-launch-2026-10-07-v1/media_period_summary.csv). Both seeds retain positive rarefied richness and entropy effects and Holm values below .05 in every frame. The period-labelled frame removes the 9/405 stratum-labelled faces; Mound E compares 180/74 faces from that mound. These restrictions reduce the specific excavation imbalance shown above, while excavated area and preservation remain unmeasured.

All 200 earlier sampled admissible-date allocations give positive rarefied differences. [Preserved allocation results](post-launch-2026-10-07-v1/media_interval_allocations.csv). The bin covering 2100 BCE is 3C, spanning 2200–1900; the data do not locate a change at a specific year. Jonathan Mark Kenoyer, *Origin and Development of the Indus Script: Insights from Harappa and other sites* (2020), in Kaleemullah Lashari (ed.), *Studies on Indus Script*, 217–236, Table 2 at printed 221–223 already describes wider inscribed media in 3B/3C. This assay quantifies a published chronology observation within the exported sampling frame. [Kenoyer primary PDF](https://www.harappa.com/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script-2.pdf). Additional area/volume denominators and consistent object recovery across excavations would sharpen the temporal interpretation.

### Earliest dated sign inventory

Unambiguous Periods 2/3A, 2800–2450 BCE, supply 31 readable families, 37 known tokens, eight unreadable slots and eighteen signs. Later 3B/3C supplies 557 readable families/773 faces and 2,310 known tokens. A sample of 31 later families averages 63.01051 signs and 128.97599 known tokens, so equal object counts leave unequal text effort. Exact type-only support has 29 early/17 later pottery families, common budget 17, and expected inventories 12.61970/20.00000. Exact type/observed-length support has 27 early/12 later families, budget 12, and expected inventories 10.12019/10.00000. [Original inventory endpoint](post-launch-2026-10-07-v1/early_inventory.json), `raw_family_reference`, `adjusted`; [cell denominators](post-launch-coverage-2026-10-07-v1/early_adjusted_denominators.csv).

The new type-only difference is −7.38030 signs with Holm .0422/.0420; copied-text closure gives .1700/.1632. Type/length adjustment gives +0.12019 with Holm .5046/.5077, and closure .6571/.6414. Both seeds agree. [Larger references]({ENDPOINT}/other_permutation_references.json), `early_inventory`. This adjusted result concerns one/two-slot pottery graffiti; the twelve later families contain ten signs in total. It offers little coverage of an early seal repertoire.

The old type-only inventory bootstrap has mean −3.67576 against observed −7.38030, a shift of +3.70455 signs; type/length has mean 1.21571 against 0.12019, a shift of +1.09552. Resampling families with replacement reduces the distinct objects/sign union differently on each side. This explains why the old bootstrap interval and permutation decision looked discordant: the bootstrap distribution is not centred on the observed union statistic. Those historical intervals are retained as resampling diagnostics and are not usable population confidence intervals here. [Bias diagnostics]({ENDPOINT}/early_interval_diagnostics.json), `bootstrap_mean`, `observed`, `mean_minus_observed`. Securely dated early seals/sealings and richer same-type/length later comparator populations are needed to test the lecture's proposed early graphic repertoire. The full Kenoyer–Meadow 2008 chapter remains unchecked; its exact bibliography is recorded from Kenoyer 2020, printed 233.

## Disclosure and computation checks

The immutable original tables contain 96 single-face site/type cells and 25 single-face region/type cells. The review finds sixteen clear site/type singleton cells of at most three slots whose complete sequence can be reconstructed. New [presentation copies]({ENDPOINT}/disclosure_safe/) suppress cells with fewer than five faces, including their sign, position and length rows. Site/type suppression removes 157 cells/261 faces and retains 64 cells; region/type removes 52/104 and retains 49. [Suppression totals]({ENDPOINT}/disclosure.json). Historical private outputs are explicitly retained under the instruction to preserve endpoints; they require a disclosure/rights decision before redistribution. Count-only composition/media tables do not contain individual sign sequences, and the five-face threshold supplies no general anonymity guarantee.

The accelerated implementation matched the preserved permutation function on nineteen supported 31-draw schedules, including 650 sign p-values. The new run completed in 267.12 seconds with 1.53 MB aggregates and 34.64 MB local memberships/draws at completion. Verification checks 38 enlarged frequency rows, 676 sign-test rows, exact combinatorial media expectations, saved tails/corrections, 114 independently recounted label draws, 280 immutable archival pins and five archived documents. [Acceleration checks]({ENDPOINT}/acceleration_checks.json); [run audit]({ENDPOINT}/audit.json); [verification](review-response-checks-2026-10-07-v1/verification.json). Full independent regeneration of every draw and archaeological authentication remain reviewer tasks. [README](README.md) gives fresh-output commands and source checks.
'''
    readme=f'''# Package D1: chronology, region and external inscriptions

The first-pass questions were tested on 5,680 faces with 18,067 known tokens and 1,879 unreadable slots. The preserved primary endpoint is **Frozen evaluation**. The caption-led follow-up and review-response endpoint are **Exploratory**; counting and replay checks have **Verified computation** status. [Full report](REPORT.md); [protocol and dated amendment](PROTOCOL.md); [review](REVIEW.md).

The enlarged 3B–3C test has equal-type JS 0.190483 bits, null mean 0.157180 and excess 0.033303 for seed 21, with Holm p=.0392/.0358 for seeds 21/22. A **family reference** permutes whole physical object/alias components within exact-type and selected-face-count blocks. **Text closure** also joins identical complete known texts transitively before selection; it drops mixed-label/type components and uses a smaller population. The 3B–3C closure Holm p=.06500/.06265. Every displayed divergence has its matching baseline in [permutation_tests.json]({ENDPOINT}/permutation_tests.json); no usable magnitude interval is available.

The review's excavation restriction changes the interpretation of length. Stratum-labelled faces comprise 9/201 in 3B and 405/574 in 3C; Mound E contributes 180/201 in 3B, while Mound F contributes 413/574 in 3C. The equal-type length increase falls from 0.723952 slots to 0.162414 on period-labelled faces and 0.115848 on Mound E. Restricted intervals span zero. Period 2–3C pottery now has Holm .06075/.06305. Sign 034 passes time-family BH at q=.0432/.0444; all 314 regional signs fail. [Composition]({ENDPOINT}/excavation_composition.csv), `faces`; [length]({ENDPOINT}/length_comparisons.json), `equal_type_length_difference_slots`; [seed agreement]({ENDPOINT}/seed_agreement.json).

Four of six regional family-reference tests and two of six closure tests pass Holm .05 in both seeds. Region is determined by site, so a fixed-site regional effect cannot be identified. Regional other-minus-within sequence losses are 0.63860, 0.27428 and −1.06756 bits/sign for Inter-Riverine, Lower Indus and Gujarat/Kutch; equal training-component budgets reduce them to 0.26346, 0.18223 and −0.03030. Exact type/length matching retains seven of 42 external objects, mostly standard types, with type-model surprisal excess 0.65090 bits/sign [−0.37986, 1.85719]; pooled-model excess is −0.08632. Both seeds give external score-family Holm 1.000. [Regional models](main-2026-10-07-v1/regional_models.json), `adjusted.losses`; [external model](main-2026-10-07-v1/external_models.json), `results`; [new score references]({ENDPOINT}/other_permutation_references.json).

## Caption-led follow-up results

Wells 090/091 are graphic candidates for man/paired humans; 093/097 are declared alternatives. Raw external frequencies are 7/149 and 5/149 known tokens, versus core 184/17,792 and 22/17,792. All twelve external target tokens are on circular seals. None enters the seven-object matched frame; both candidate enrichment Holm values remain 1.000 in both seeds. Exact lecture-slide identification and an independent 091 code check are missing. [Graphic identification](post-launch-2026-10-07-v1/sign_identifications.json); [counts](post-launch-2026-10-07-v1/external_target_counts.csv); [selection](post-launch-coverage-2026-10-07-v1/external_selection_counts.csv).

At equal family budgets, rarefied object-type richness rises 4.598459 in the full 3B/3C sample, 3.742102 among period-labelled families and 4.361847 on Mound E. Both seeds give richness and Shannon Holm values below .05 in all three frames. The 3C bin spans 2200–1900 BCE and includes 2100; its width prevents locating a year-specific transition. Early 2/3A has eighteen signs, 31 families and 37 known tokens. Exact type/length support leaves 27 early/twelve later pottery families: expected-inventory difference +0.120190 signs, Holm .5046/.5077. Historical inventory-bootstrap intervals are now treated as biased union-resampling summaries. [Media comparisons]({ENDPOINT}/media_comparisons.json); [early references]({ENDPOINT}/other_permutation_references.json), `early_inventory`; [interval diagnostics]({ENDPOINT}/early_interval_diagnostics.json).

## Preservation, sources and disclosure

The [amendment](REVIEW-AMENDMENT-2026-10-07.md) preceded new computations, after the review had exposed relevant results. All 280 files pinned as immutable at the archival step and five original document snapshots passed checks. The [current source manifest]({SOURCE}/sources.json) corrects Ur's source lead, Vidale 2004's man/variant scope, Suga's title punctuation and the unrepeatable Fuls excerpt attribution. Laursen's primary PDF was newly recovered; the Fuls retry returned HTTP 403. Exact titles, authors, years, venues, URLs, opened/snippet scopes and failed routes are recorded there and in the two preserved source manifests. [Retrospective](RETROSPECTIVE.md); [proposed registry entry](registry-entry.json).

The frozen site/type tables contain 96 single-face cells and region/type tables 25. Current [presentation tables]({ENDPOINT}/disclosure_safe/) suppress cells under five faces, including their signs, positions and lengths: 64 site/type and 49 region/type cells remain. Old private disclosures are preserved and require review before redistribution. Third-party payloads and record-level draws remain under the assigned `data/raw/` path. [Suppression accounting]({ENDPOINT}/disclosure.json). [Complete response path inventory](FILES_REVIEW_RESPONSE_2026-10-07-v2.json) lists every new file and the five authorized document updates.

## Reproduce from the repository root

Required input is `data/normalized/lipi_observed_faces.jsonl`, SHA256 `1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db`. Dependencies are already recorded in [environment.json](environment.json); no installation was needed. Reused code and input hashes are in [audit.json]({ENDPOINT}/audit.json). Use fresh directories. The commands below place every new reviewer output outside the package directory, within the assigned local raw root.

```powershell
python -B experiments/2026-10-06-chronology-region/review_response.py --output-dir data/raw/2026-10-06-chronology-region/reviewer-response-aggregates-v1 --raw-dir data/raw/2026-10-06-chronology-region/reviewer-response-details-v1
python -B experiments/2026-10-06-chronology-region/verify_review_response.py --input-dir data/raw/2026-10-06-chronology-region/reviewer-response-aggregates-v1 --raw-dir data/raw/2026-10-06-chronology-region/reviewer-response-details-v1 --output-dir data/raw/2026-10-06-chronology-region/reviewer-response-checks-v1
```

The new schedule took 267.12 seconds and generated about 36 MB. Compare numerical fields with `{ENDPOINT}/`, ignoring paths and elapsed time. The primary and first-follow-up code is unchanged. [run_with_output.py](run_with_output.py) reuses the review's module-redirection approach, stages the archived pre-response protocol and supplies those scripts an output-directory argument:

```powershell
python -B experiments/2026-10-06-chronology-region/run_with_output.py analyze --output-dir data/raw/2026-10-06-chronology-region/reviewer-legacy-aggregates-v1 --run reviewer-main-v1
python -B experiments/2026-10-06-chronology-region/run_with_output.py verify --output-dir data/raw/2026-10-06-chronology-region/reviewer-legacy-aggregates-v1 --run reviewer-main-v1 --output main-check.json
python -B experiments/2026-10-06-chronology-region/run_with_output.py supplement --output-dir data/raw/2026-10-06-chronology-region/reviewer-legacy-aggregates-v1 --main reviewer-main-v1 --run reviewer-supplement-v1
python -B experiments/2026-10-06-chronology-region/run_with_output.py verify_supplement --output-dir data/raw/2026-10-06-chronology-region/reviewer-legacy-aggregates-v1 --main reviewer-main-v1 --supplement reviewer-supplement-v1 --output supplement-check.json
python -B experiments/2026-10-06-chronology-region/run_with_output.py post_launch --output-dir data/raw/2026-10-06-chronology-region/reviewer-legacy-aggregates-v1 --run reviewer-post-launch-v1
python -B experiments/2026-10-06-chronology-region/review_source_checks.py --output-dir data/raw/2026-10-06-chronology-region/reviewer-source-aggregates-v1 --raw-dir data/raw/2026-10-06-chronology-region/reviewer-source-payloads-v1
python -B experiments/2026-10-06-chronology-region/replay_legacy_coverage.py --output-dir data/raw/2026-10-06-chronology-region/reviewer-legacy-coverage-v1 --raw-dir data/raw/2026-10-06-chronology-region/reviewer-post-launch-v1
python tools/review_prose.py --path experiments/2026-10-06-chronology-region --no-write
```

Legacy record-level outputs retain their fresh run names under the assigned raw directory. The adapter also supports `check_catalogue_join`, `acquire_sources` and `acquire_post_launch_sources`; acquisition uses its supplied raw output root. Its wrapper disables option abbreviation so a legacy `--output` is not consumed as `--output-dir`. The original follow-up preservation checker/finalizer assumes the pre-response protocol and document wording; the new checker supersedes that preservation assumption. Existing [original verification](verification-2026-10-07-v1.json), [follow-up verification](verification-post-launch-2026-10-07-v1.json) and [review replay](review/) remain readable historical records. `review_response_setup.py` is a one-time archival step and refuses repetition.

## Reviewer checks

Repeat both seeds and verify the 19,999/9,999 budgets, exact margins, time sign 034, the pottery Holm correction and all seed decisions. Recount label/mound composition, the thirteen missing 3C stratum catalogue references, common types and restricted length effects. The new checker independently recounts 114 saved label draws and verifies 676 sign rows, media combinations, tails/corrections and prior hashes; full regeneration of every draw is the reviewer's rerun.

Sample HARP physical PDF pages 2 and 4, Suga page 1, Vidale 2004 printed 270, Vidale 2005 Figure 5 and Laursen printed 96. Inspect the corrected Ur row and Fuls failure witness, the atlas column-0 rows 26/31 at zero-based page 20, and the independent alignment's missing 091 support. Check sparse-cell suppression against the old totals. Archaeological row authentication, lecture slides, securely dated early seals and core circular-seal matches remain the missing evidence.
'''
    retrospective=f'''# D1 retrospective

This record separates the first pass, the caption-led extension and the review response. The five earlier documents are archived in [review-response-baseline-2026-10-07-v1/](review-response-baseline-2026-10-07-v1/); the original primary and exploratory endpoints, source manifests and reviewer files are unchanged. All completed writes stayed inside the two assigned directories. Shared indexes, registry, manuscripts, other contributors' files and Git history were untouched.

## First pass and caption-led extension

The first pass read repository instructions, the registry, relevant corpus/method/literature retrospectives, the contribution assessment and redistribution rules. ROOT-02, ROOT-05, METHODS-nested_unique_preserved_aliases and CONTEXT-01 supplied earlier alias, copying and short-record lessons. It reused the pinned Lipi corpus and `group_records`/`make_folds` from [conditional_structure.py](../../src/methods/conditional_structure.py), following [Paper 002](../../papers/002-conditional-reference-laws/). Existing earlier experiments were not repeated.

Live source searches found Yadav, Suga, Oakes, Rao and the HARP chronology. Source inspection corrected the Rao DOI, the Jamison coauthors/year and the distinction between Suga's 2024 issue and 2025 repository release. Six PDFs and two useful HTML pages downloaded; Wiley and ResearchGate returned 403. Windows console encoding initially interrupted non-ASCII inspection; UTF-8 console output resolved it without changing payloads. The 3,067 time-labelled faces included only 1,939 at Harappa, so HARP mapping was restricted to that site. The single 3A face prevented a separately supported comparison. [Original sources](sources.json); [mapping](main-2026-10-07-v1/period_mapping.json).

The original main run took 375.22 seconds. Physical/text closure produced a 1,038-face component, reducing supported held-out cells. Sparse site-balanced bootstrap intervals retained only one to three draws; the first exploratory amendment preserved sampled signatures and all 499 replicates. It left point estimates unchanged but did not establish coverage for sparse divergence. Actual fold totals were added because the allocator's recorded lengths were proxies. Original independent checks rebuilt three count tables, 23 effects and 104 regional plus fourteen external predictions. [Primary verification](verification-2026-10-07-v1.json); [supplement verification](verification-supplement-2026-10-07-v1.json).

The coordinator's caption summary led to a separate dated protocol and three added assays. Graphic references nominated Wells 090/091 with 093/097 alternatives before the matched-frequency computation; broad regional counts were already available. This ordering is evidenced by file times only. Circular seals carried every external target token and had insufficient exact comparators. The early equal-family comparison also left unequal known-token effort; type/length adjustment reduced it to small pottery cells. [Caption protocol](POST-LAUNCH-PROTOCOL-2026-10-07.md); [matched coverage](post-launch-coverage-2026-10-07-v1/); [original follow-up](post-launch-2026-10-07-v1/).

Four primary PDFs were recovered in that extension. Poppler page images supplied the Parpola 2005 scan title and bibliography when extraction gave no text. A source-ID mismatch stopped its first final audit before writing an audit endpoint; the corrected acquisition ID was then checked. Full 1983/1986/1994/2008 chapters were not inspected. The extension ran in 51.10 seconds; its checker made 395,653 assertions, chiefly about admissible dates, and retained 81 earlier immutable files. [Original audit failure](final-audit-attempt-2026-10-07-v1.json); [follow-up verification](verification-post-launch-2026-10-07-v1.json).

## Review response, 7 October 2026

The [Sonnet review](REVIEW.md) reproduced all sixty aggregate files and 380 numbers. It identified an excavation-source imbalance, unstable low-budget decisions, unusable divergence intervals, source-attribution mistakes and sparse-cell disclosure. Its existing subset and permutation results were known before the new amendment, so all response analyses are Exploratory. [REVIEW-AMENDMENT-2026-10-07.md](REVIEW-AMENDMENT-2026-10-07.md) was written and appended before computation. Five documents were copied and 285 files pinned; 280 of those were required to remain unchanged.

Composition checks found 9/201 stratum-labelled 3B faces and 405/574 stratum-labelled 3C faces. Mound E contributes 180/201 in 3B, while Mound F contributes 413/574 in 3C. The direct catalogue-number check refines the review's wording: 392 of the 405 3C stratum faces have earlier-range H-numbers, and thirteen lack a catalogue number. Restricting to period-field labels or Mound E changes both sample size and common-type support. The length increase shrinks to 0.162414/0.115848 slots, with intervals spanning zero. Media rarefied differences stay positive in both frames. [Composition]({ENDPOINT}/excavation_composition.csv); [catalogue ranges]({ENDPOINT}/catalogue_number_ranges.csv); [length]({ENDPOINT}/length_comparisons.json); [media]({ENDPOINT}/media_comparisons.json).

A sparse component-count engine made the larger schedule small enough for the available disk and fast enough to complete. Before large runs it matched the preserved permutation function on nineteen supported 31-draw schedules, including 650 sign p-values. It preserved the review's physical RNG order and two bootstrap-advancement draws so seed 21 reproduces the time-sign resolution check. Both seeds used 19,999 time allocations and 9,999 other-reference allocations. The complete run took 267.12 seconds, generating 1.53 MB aggregates and 34.64 MB local draws/memberships. [Acceleration checks]({ENDPOINT}/acceleration_checks.json); [audit]({ENDPOINT}/audit.json).

The larger schedule corrected Period 2–3C pottery to Holm .06075/.06305 and time sign 034 to BH .0432/.0444. It retained four regional physical-family rejections and gave two under closure, adding Inter-Riverine–Gujarat/Kutch to the original sole closure rejection. Every frequency .05 decision agrees across seeds. Full and restricted media results remain positive with corrected p below .05; exact type/length early-inventory and matched external score families retain their negative evidence. Null means/excesses accompany the JS effects. Earlier percentile/basic JS intervals are withdrawn from magnitude interpretation, while their immutable values remain accessible. The inventory-bootstrap diagnostic measured shifts of +3.70455 and +1.09552 signs, explaining its uncentred union statistic. [Seed record]({ENDPOINT}/seed_agreement.json); [other references]({ENDPOINT}/other_permutation_references.json); [inventory diagnostic]({ENDPOINT}/early_interval_diagnostics.json).

Source inspection corrected Ur to a secondary Frenez image-caption lead, separated Vidale 2004's man/variants from twins, removed the spurious colon in Suga's title and withdrew the Fuls section-content attribution. A current web tool still opens a cached Fuls excerpt, but a direct retry again returned HTTP 403. Search found Laursen's primary PDF on Harappa.com; it downloaded successfully (1,391,234 bytes, 39 pages), and its first-page abstract was inspected. Stored HARP, Suga, Yadav, Vidale and Parpola passages were reopened, with hashes and raw extraction witnesses. [Current source correction manifest]({SOURCE}/sources.json); [corrected checklist]({SOURCE}/external_literature_check.csv). Old source manifests and failed-download witnesses are preserved.

The review found 96 single-face site/type and 25 region/type cells. New presentation copies suppress all cells below five faces and their sign/position/length rows, retaining 64 and 49 cells respectively. The old private tables remain disclosive under the endpoint-preservation instruction. Count-only composition and media outputs retain aggregate small-cell counts without sign sequences. [Disclosure accounting]({ENDPOINT}/disclosure.json); [filtered tables]({ENDPOINT}/disclosure_safe/).

## Implementation failures, fixes and checks

The first output-adapter check mistakenly abbreviated the legacy `--output` option as `--output-dir`; the sandbox rejected the resulting write attempt before creating a file. Setting `allow_abbrev=False` fixed argument forwarding. A repeat wrote the catalogue-join result only beneath the assigned raw directory. The new verifier's first preflight attempted subtraction from a missing positional estimate; its handling now preserves `None` for unsupported observed statistics. No verification endpoint was created by that failed preflight. The final audit initially compared the dated append byte-for-byte without allowing Windows text-mode newline conversion; the check now preserves the original prefix exactly and normalizes only the appended line endings. That attempt wrote no audit endpoint. The first completed final audit counted 56 legacy files, while its description included four coverage diagnostics that had not yet been rerun. Those diagnostics were then reproduced separately; the first audit and inventory are preserved, and the version-2 audit records all sixty. A console inspection also failed on a Unicode character and was repeated with UTF-8 output. These failures changed no scientific endpoint.

[run_with_output.py](run_with_output.py) adapts the preserved analyzer, supplement, caption analysis and associated primary checks; it stages the archived protocol rather than editing frozen code. The new analyzer, verifier, source checker and document builder take explicit output directories. The original caption preservation finalizer's protocol/wording assumptions precede this authorized review revision; the new preservation check supersedes those assumptions. The baseline/setup step is deliberately one-time and refuses repetition. The output adapter was tested by rerunning all sixty legacy aggregate files outside the package directory; its primary and supplemental independent checks passed.

Independent verification checks 38 frequency rows, 676 sign rows, exact combinatorial media expectations, saved tails and corrections, 114 independently recounted label draws, 280 archival file hashes and five document archives. It does not regenerate every random allocation. Source hashes, document links, registry schema, code syntax and the required prose scan are recorded in [final checks](review-response-final-2026-10-07-v2/final_checks.json). Full random regeneration, independent 091 identification, archaeological object authentication, securely dated early seals and matched circular-seal support are the next reviewer checks. [Complete response inventory](FILES_REVIEW_RESPONSE_2026-10-07-v2.json).
'''
    registry=read(OWN/'review-response-baseline-2026-10-07-v1/registry-entry.json')
    registry.update(
        theme='chronological/regional graphic variation; matched external inscriptions; caption-led media/inventory; excavation-composition review response',
        status='Exploratory',
        question='Does Harappa sign usage change across recorded HARP periods after object-type and excavation-frame controls; do sampled regions differ; and do exact type/length-matched external texts differ? Caption-led amendments test graphic human candidates, media diversity and early inventory. The second amendment reruns references at larger budgets and checks label-source/mound composition.',
        outcome='Primary endpoint: Frozen evaluation; later amendments: Exploratory; arithmetic and replay checks: Verified computation. On 5680 faces, full 3B–3C equal-type JS=.190483 bits, seed-21 null=.157180 and excess=.033303, Holm=.0392/.0358 (seeds 21/22); closure=.06500/.06265 on its smaller population. Period-labelled JS=.219445, null=.176564, excess=.042881, Holm=.0342/.0310. Mound-E JS=.244466, null=.206696, excess=.037770, Holm=.06545/.06555. No usable JS magnitude interval is supplied. Period 2–3C pottery Holm=.06075/.06305. Sign 034 has BH=.0432/.0444; all other time signs and all 314 regional signs fail .05. Four of six regional physical tests and two closure tests pass in both seeds. Length increase .723952 slots falls to .162414 for period-labelled and .115848 for Mound-E frames, with restricted intervals spanning zero. External matching retains 7/42 objects, type-model surprisal excess=.650896 [-.379864,1.857194], pooled excess=-.086317, score-family Holm=1 in both seeds. Raw external 090/091 counts are 7/149 and 5/149 versus core 184/17792 and 22/17792, entirely on circular seals; supported matches contain neither target, enrichment Holm=1. Full/period-labelled/Mound-E rarefied media richness increases 4.598459/3.742102/4.361847; all richness and Shannon Holm values below .05 in both seeds. Early 2/3A has 18 signs and 37 known tokens in 31 families; exact type/length support retains 27 early/12 later pottery families, expected-inventory difference=.120190, Holm=.5046/.5077. Every frequency threshold decision agrees across seeds. Existing endpoints unchanged.',
        challenge='Excavation sources differ: 9/201 3B versus 405/574 3C stratum labels; 180/201 3B from Mound E versus 413/574 3C from F. Only 392/405 3C stratum faces have parseable earlier-range catalogue numbers; 13 are missing. Region is fixed by site; copying reduces supported populations. Sparse JS bootstrap intervals are unusable; early inventory union bootstraps are shifted. Circular seals lack exact comparators and matched external objects are mostly standard types, including Baluchistan/Makran context. Earliest support is small pottery, rather than a representative seal repertoire. The 3C bin cannot locate a 2100 BCE breakpoint. 96 site/type and 25 region/type singleton cells disclose source-derived data in immutable private outputs. Full underlying Parpola 1983/1986/1994 and Kenoyer–Meadow 2008 chapters, exact lecture glyphs, independent 091 mapping and archaeological row identities remain unchecked. Fuls excerpt attribution is withdrawn; direct retry returned 403.',
        remedy='Keep complete physical aliases and transitive text components before selection; permute exact-type/multiplicity blocks and report each reference population. Use seeds 21/22 with 19999 time and 9999 other allocations, Holm/BH correction, Monte Carlo errors and null mean/excess. Restrict separately to period-labelled and Mound-E families and report raw/adjusted length and media effects. Candidates and alternatives were specified before the matched-frequency computation, with earlier broad counts available; timing is evidenced by file times only. Preserve interval allocation assumptions, model training-size sensitivities and unsupported circular classes. Suppress under-five-face cells in new presentation copies; retain old private endpoints pending disclosure review. Archive the five authorized documents, preserve 280 immutable archival pins, and accept output-directory arguments through new scripts and a frozen-code adapter.',
        retry_when='New consistent excavation area/volume denominators, narrower secure dates or authenticated stratum mappings, early seal/sealing comparators, matched core circular seals, independent 091/lecture glyph identification, row-level external plates/contexts, additional independently sampled sites per region, sparse-interval coverage evidence, or readable full primary sources become available.')
    for path in ['REVIEW.md','REVIEW-AMENDMENT-2026-10-07.md',f'{ENDPOINT}/audit.json',f'{ENDPOINT}/permutation_tests.json',f'{ENDPOINT}/sign_tests.csv',f'{ENDPOINT}/seed_agreement.json',f'{ENDPOINT}/excavation_composition.csv',f'{ENDPOINT}/catalogue_number_ranges.csv',f'{ENDPOINT}/length_comparisons.json',f'{ENDPOINT}/media_comparisons.json',f'{ENDPOINT}/other_permutation_references.json',f'{ENDPOINT}/disclosure.json',f'{SOURCE}/sources.json',f'{SOURCE}/external_literature_check.csv','review-response-checks-2026-10-07-v1/verification.json','review-response-final-2026-10-07-v2/final_checks.json','FILES_REVIEW_RESPONSE_2026-10-07-v2.json']:
        target='experiments/2026-10-06-chronology-region/'+path
        if target not in registry['evidence']: registry['evidence'].append(target)
    return {'README.md':readme,'REPORT.md':report,'RETROSPECTIVE.md':retrospective,'registry-entry.json':json.dumps(registry,indent=2,ensure_ascii=False)+'\n'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True); parser.add_argument('--update-authorized-documents',action='store_true')
    args=parser.parse_args(); output=Path(args.output_dir).resolve()
    if args.update_authorized_documents:
        if output!=OWN: raise ValueError('The update flag permits only this package’s authorized documents.')
    else:
        if output.exists(): raise FileExistsError('Choose a fresh document output directory.')
        output.mkdir(parents=True)
    for name,text in documents().items(): (output/name).write_text(text,encoding='utf-8')
    print(json.dumps({'documents_written':4,'protocol_handling':'Earlier content and dated append preserved by the setup step','output_directory':str(output)}))

if __name__=='__main__': main()
