# Indus civilisation and script research knowledge base

The Indus, or Harappan, civilisation flourished from about 2600 to 1900 BCE across what is now Pakistan and northwest India. It spread one material culture, planned towns, standard weights and an undeciphered writing system across hundreds of thousands of square kilometres. The largest database of its writing lists about 4,700 inscribed objects: nearly half are carved stamp seals, and most of the rest are small tablets, marked pottery and clay tags. The texts are short, usually three or four signs, drawn from roughly 400 to 700 signs depending on how variants are counted. No bilingual text has been found, and the language of the script is unknown.

This project began with the undeciphered script (hence the repository name `indus-valley-script`) and expanded into a wider source-linked knowledge base covering five connected areas: the script and inscribed-object corpus, Indus archaeology and urban landscapes, post-urban continuity and farming systems, comparative Bronze Age societies and societal persistence theory, and statistical evaluation methods. Most of the work is done by AI agents working from shared sources, and we are testing whether many agents can make verifiable progress on hard archaeological and historical problems. We count as progress only results that someone else can check: facts tied to named sources, datasets and audits that preserve unresolved conflicts, patterns that hold on unseen data, and proposals that beat shuffled or matched controls. Every attempt stays on record, including failures, so later contributors start from what is already known.

## Where things stand

The [findings guide](knowledge/findings/README.md) groups carded results by subject, and the [knowledge index](knowledge/INDEX.md) records every dated research programme. Many script results come from held-out tests: we fit a model on some inscriptions, score it on the rest, and compare the score with chance. Each link opens a card or report with exact counts, populations and comparisons. A p-value says how often chance alone would produce a result at least this strong.

### Script and inscribed objects

- The object register covers all 4,695 provisional Lipi objects and 5,680 exported faces in the held sources (225,223 assertions in the base build; 230,697 after review integration), while preserving uncertain identities and source assertions. [Register report](experiments/2026-10-22-object-register/REPORT.md), [Paper 007](papers/007-object-reconciliation-register/manuscript.md)
- The digital corpus we work from is incomplete. Of 493 numbers in 19 sections of volume 1 of the *Corpus of Indus Seals and Inscriptions* (CISI), the main printed catalogue, 166 have no matching entry, and a 503-row census of post-catalogue publications identifies 301 later inscribed finds, leaving 55 to 291 absent from the local corpus under strict matching. [Finding](knowledge/findings/F-0007-catalogue-identifiers-missing-from-export.md), [Post-catalogue census](experiments/2026-10-21-post-catalogue-finds/README.md)
- Of 114 original museum records inspected in the initial census, 68 could be linked with confidence to objects in the corpus; later museum harvests and CISI basic-data transcriptions raised museum-accession coverage to 1,979–2,450 objects depending on certainty rules. [Finding](knowledge/findings/F-0008-museum-joins-are-a-lower-bound.md), [Paper 007](papers/007-object-reconciliation-register/manuscript.md)
- An excavators' caption places H-1657 on the floor of Room 591 in Trench 43 at Harappa and assigns it to late Period 3C; image review confirmed fourteen catalogue-view links in held images, including links for L-163 and L-207 absent from the earlier image index. [Source review](experiments/2026-10-24-harappa-context-pass2-review/REPORT.md), [Independent review](experiments/2026-10-26-object-pilot-review/REPORT-v2.md)
- No two of the 445 seals with six or more signs carry the same full text. Of 16 sealings or tags whose text matches a known seal, 13 match only seals found at other sites. [Long seal texts](knowledge/findings/F-0027-long-seal-texts-do-not-repeat.md), [Cross-city sealings](knowledge/findings/F-0030-sealings-match-seals-from-other-cities.md)
- Line breaks fall between recurring units. On 69 seals where the catalogue shows how the text was split across lines, whole lines recur elsewhere more often than stretches crossing the break: 23 seals favour the lines, 4 favour crossing stretches and 42 tie (p = 0.0003). [Finding](knowledge/findings/F-0018-lines-recur-more-than-crossing-windows.md)
- Signs follow each other predictably. On 1,596 distinct complete texts, a model that knows the previous sign gives the correct next sign about 1.8 times the probability of a position, site and type baseline (a gain of 0.848 bits per sign). When one sign is hidden, two signs of context restore it exactly in 37.3% of 8,009 trials, against 34.6% for one sign. [Prediction](knowledge/findings/F-0001-sequential-prediction-on-unique-texts.md), [Restoration](knowledge/findings/F-0002-second-order-known-slot-restoration.md)
- Grouping sign variants that share a base shape improves held-out prediction by 0.022 bits per sign over random groups of the same sizes (p = 0.005). [Finding](knowledge/findings/F-0010-graphic-base-families-improve-prediction.md)
- Groups of short strokes take 3.61 different values on average before a given sign, fewer than counted commodities take in matched samples from Mesopotamian accounts of about 2100–2000 BCE (4.53 to 5.15). [Finding](knowledge/findings/F-0024-stroke-values-are-tied-to-following-items.md)
- Some methods fail. Our estimate of how many signs are lost in a damaged gap was right 46.3% of the time, worse than always guessing one sign (51.1%). [Finding](knowledge/findings/F-0005-gap-count-estimator-loses-to-constant-one.md)

No sign has an established sound or meaning, and the language of the script remains unknown.

### Archaeology, cities, continuity and comparative society

- A register of 34 candidate Harappan towns preserves 1,380 line and system records, 118 dated-part assertions and 620 radiocarbon assertions; published Mohenjo-daro surveys show both nearly cardinal and turned street systems, and a comparative urban study records 287 assertions across twelve core towns showing shared streets, drains and enclosures persisting across local rebuilding. [Town register](experiments/2026-10-24-q1032-town-axis-register/REPORT.md), [Urban form study](experiments/2026-10-24-urban-form-and-inscription-ecology/REPORT.md)
- A review of excavation coverage compiles 72 sources and 21 regions of interest where later cities, alluvium, piedmont sediment and changing coasts obscure Indus settlements, documenting why historical counts such as "100 of 1,000 excavated" mix distinct frames and area units. [Paper 005](papers/005-settlement-survey-gaps/manuscript.md)
- The Indus living atlas preserves 115 place entities (112 located), seven source-linked 3D city and building reconstructions, and an 18-case town-history review that finds regional persistence through urban reorganization without establishing an uninterrupted Indus-to-present town sequence. [Indus living atlas](experiments/2026-10-26-indus-living-atlas/README.md)
- Placing the Mature Harappan civilisation beside 21 contemporary Bronze Age societies (2600–1900 BCE) shows a material culture spread over 650,000–1,000,000 km² and second-rank cities (200–250 ha at Mohenjo-daro) as the only coded literate society with planned streets, drainage and standard weights that lacks an identified palace or royal tomb. [Contemporary civilisations](experiments/2026-10-20-contemporary-civilisations/README.md)
- Across 938 Greater Indus entries parsed from Ascalone (2022), Dholavira's 90 intact certain weights of 5–100 g fit a 13.716 g unit (CV 1.591%), while smaller 1.3–5 g weights fit 14.280 g and western assemblages show no Indus-standard excess over chance controls. [Weight metrology](experiments/2026-10-06-weight-metrology/REPORT.md)
- An archaeobotanical audit of Jognakhera and nine recalculated phase summaries across five sites in Petrie and Bates (2017) show survival of the Indus crop repertoire after 1900 BCE alongside shifting seasonal shares (at Bahola, winter crops rise from 6.87% to 17.29% between Late Harappan and Painted Grey Ware levels). [Crop continuity](experiments/2026-10-25-crop-continuity/REPORT.md)
- Separate historical and theoretical studies examine selective inheritance and intellectual recombination in early Indian institutions and texts (47 source-linked observations across farming, craft and textual memory) and formalize minimum capacities for long societal persistence across 32 baseline and 16 paired repair-and-learning finite models. [Early Indian continuity](experiments/2026-10-11-early-indian-continuity/REPORT.md), [Societal persistence](experiments/2026-10-11-societal-persistence/REPORT.md)

## What we currently think

We write our working ideas as plain claims, each with a credence (our probability that it is right), predictions that could fail and a kill condition, the result that would make us drop it. The [working model](knowledge/WORKING-MODEL.md) integrates both parts of our current account:

- **The script and inscribed objects:** the script did three different jobs: seals carry identity legends, Harappa's tablets are standard tokens made in series, and marks on pottery label contents or owners (credence 0.6). A seal legend is a name followed by a title (0.45), and short legends recurring across cities name shared offices (0.55).
- **Cities, institutions and post-urban continuity:** shared urban routes and services survived local rebuilding under common rules (0.55), plains cities aligned near true north while regional towns followed local landforms (0.30), local farming and craft networks carried practical knowledge past urban decline (0.65), and language contact carried regional farming knowledge into early Indo-Aryan communities (0.50).

Each claim under test has its own [conjecture card](knowledge/conjectures/README.md). For inscription claims we test in two stages: free exploration on a discovery half, then one frozen shot on a confirmation half. Archaeological, urban and continuity conjectures freeze comparable prospective or withheld-sample rules before opening new material.

Early and subsequent tests moved several script and town claims:

- A working reading that gave roles such as name, household or office to the 118 commonest signs did no better than shuffled versions of itself at predicting where seals were found or how large they were. [Report](experiments/2026-10-12-conjecture-shots/shot-b-reading/REPORT.md)
- Seals whose legend ends in one of four signs were predicted to be larger than comparable seals, and they were (p = 0.021). An independent review found that three very large seals ending in sign 820 carry most of the result, so we hold the idea at a credence of 0.15. [Report](experiments/2026-10-12-conjecture-shots/shot-a-rank/REPORT.md), [review and response](experiments/2026-10-12-conjecture-shots/REVIEW-RESPONSE.md)
- A check of the published photographs found that ten clay sealings from Lothal, in Gujarat, carry the same four-sign legend as the seal M-895 from Mohenjo-daro, but were stamped by a different seal. [Plate check](experiments/2026-10-13-plate-checks/README.md)
- Both fixed-pattern stratigraphy conjectures met their kill conditions ([Mohenjo-daro](knowledge/conjectures/C-0006-closing-stock-fixed-from-lowest-levels.md), [Harappa](knowledge/conjectures/C-0010-seal-legend-fixed-pattern.md)). The [fish-order test](knowledge/conjectures/C-0007-fish-compound-designations.md) passed its joint rule while the [asterism coverage test](knowledge/conjectures/C-0008-fish-numerals-asterism-coverage.md) failed. The [Proto-Dravidian fish-and-star test](knowledge/conjectures/C-0011-proto-dravidian-min-fish-and-star.md) passed its frozen rule and sits at 0.20 after review. The [town-axis star test](knowledge/conjectures/C-0015-towns-laid-out-on-star-settings.md) was undecided under its frozen rule and its Pleiades prediction failed, lowering its credence to 0.04 after secondary analysis. These results retain the exposure limits recorded in the cards and [bench ledger](bench/spent.json).

## Start exploring

The [project website](https://k-sandhu.github.io/indus-valley-script/) presents the findings, open questions and working model as web pages. Interactive tools and visual summaries in the repository include:

- The [Indus living atlas](experiments/2026-10-26-indus-living-atlas/index.html) maps 115 places and their phases, shows seven 3D city and building reconstructions and reviews settlement persistence.
- The [contemporary civilisations explorer](experiments/2026-10-20-contemporary-civilisations/README.md) compares the Mature Harappan civilisation with 21 Bronze Age contemporaries across area, city size, population and institutions.
- The [sign catalogue](experiments/2026-10-11-bonta-adversarial/run-v6/catalogue.html) shows signs with example inscriptions and proposed meanings, each with its evidence.
- The [chart atlas](output/chart_atlas/index.html) shows the 687 sign drawings and numbers in Koskenniemi and Parpola's 1979 *Corpus of Texts in the Indus Script*, each linked to its page and marked where the reading of the chart is uncertain.
- [Presentations](presentations/README.md) hold visual decks and animations built from recorded studies, including the town-axis visual atlas, the renewal animation for societal persistence, and findings slide decks.
- The [repository map](knowledge/MAP.md) lists every finding, question, conjecture, paper, attempt and retrospective.

| Manuscript draft | Question |
|---|---|
| [001](papers/001-artifact-aware-prediction/manuscript.md) | How well can a model predict the next sign or restore a missing one, when copies of the same inscription are kept apart? |
| [002](papers/002-conditional-reference-laws/manuscript.md) | How do statistical tests go wrong when one inscription is counted several times? |
| [003](papers/003-physical-observations/manuscript.md) | What physical evidence would a numerical reading need? Tested against Inca khipu records |
| [004](papers/004-reference-model-selection/manuscript.md) | How should a model of the records be chosen before matching signs to another system? Tested on simulated scripts |
| [005](papers/005-settlement-survey-gaps/manuscript.md) | Why have so few Indus sites been excavated, and how could surveys find hidden settlements? |
| [006](papers/006-sanskrit-key-calibration/manuscript.md) | Does a published Sanskrit decipherment do better than shuffled versions of its own key? |
| [007](papers/007-object-reconciliation-register/manuscript.md) | How complete is the digital Indus corpus, and how can object identities and conflicts be reconciled across catalogues and museums? |
| [008](papers/008-seal-legend-segmentation/manuscript.md) | What do graphic base families, physical line breaks and cross-city circulation show about how seal legends are built? |
| [009](papers/009-rebus-interlock-calibration/manuscript.md) | How often do proposed Dravidian rebus interlocks arise by chance, and do they outperform an unrelated language on unselected sign pairs? |
| [010](papers/010-harappa-stratigraphic-drift/manuscript.md) | Did Indus seal legends stay fixed across excavated strata at Mohenjo-daro and Harappa, or did their body drift? |

PDFs of the [original research report](output/pdf/indus_script_research_report.pdf) and the [settlement paper](output/pdf/indus_settlement_survey_gaps_2026-10-11.pdf) are also available.

## Data

Acquired inputs stay outside Git; [REPRODUCING.md](REPRODUCING.md) and [LOCAL_STORAGE.md](LOCAL_STORAGE.md) explain how to obtain or restore them.

Our first data priority is a complete record of every inscribed object: all of its catalogue numbers, every face and photograph, its size and material, where and in which layer it was found, its date, its museum number and where it has been published. Alongside the object corpus, we maintain source-linked registers for town axes and radiocarbon dates, comparative urban architecture, archaeobotanical crop assemblages, settlement survey coverage, weight metrology, contemporary civilisations and 3D city reconstructions. [DATA.md](knowledge/DATA.md) lists what we hold across all of these datasets, what exists elsewhere and what is still missing.

Much of the source material belongs to others. A copy of this repository contains our text, code, protocols, summary results and pointers to the sources, together with some third-party material we are allowed to share. The digital corpora, most photographs and the downloaded publications have to be obtained separately under their own terms. [REPRODUCING.md](REPRODUCING.md) explains how to obtain them and rerun a study, and the [rights records](knowledge/provenance/REDISTRIBUTION.md) say what can be shared.

To download only the documents and tools, without the experiment outputs:

```text
git clone --filter=blob:none --sparse https://github.com/k-sandhu/indus-valley-script.git
cd indus-valley-script
git sparse-checkout set knowledge papers tools templates
```

Add the experiment directories and their inputs later if you want to inspect outputs or rerun a study.

## Contribute

You can [open an issue](https://github.com/k-sandhu/indus-valley-script/issues/new/choose), take up one of the [open questions](knowledge/questions/) or check a recorded result yourself. Corrections to the data and metadata help most. [CONTRIBUTING.md](CONTRIBUTING.md) explains how to claim a question, which files you own, how work is reviewed and what to check before a pull request. Discussion takes place in [GitHub Discussions](https://github.com/k-sandhu/indus-valley-script/discussions).

For agents: Clone https://github.com/k-sandhu/indus-valley-script, read AGENTS.md and follow it.

## Repository layout

| Directory | Contents |
|---|---|
| `knowledge/` | Findings, open questions, conjectures, the working model, the data page and the record of every attempt |
| `experiments/` | One dated folder per research study, with its plan, outputs, review and retrospective |
| `presentations/` | Slide decks, maps and visual summaries of recorded results |
| `maintenance/` | Records of earlier work on the repository itself: releases, publication screens, the website generator, storage and restructuring |
| `papers/` | Manuscript drafts with their methods and the evidence behind each claim |
| `output/` | Reports, the chart atlas and summaries |
| `src/` | Analysis code |
| `bench/` | The shared harness that scores proposed readings and keys |
| `tools/` | Scripts for the knowledge base, checks and the website, all run by hand |
| `data/` | Records of where each input came from; the large inputs are kept out of Git |
| `site/` | Website assets and source material |
| `LICENSES/` | Licence texts |
| `templates/` | Templates for experiments, findings, questions and source reviews |
| `research/`, `results/`, `archive/` | Earlier plans, outputs and documentation, kept unchanged |
| `.claude/skills/` | Short task guides for agents, linked from AGENTS.md |
| `.github/ISSUE_TEMPLATE/` | Forms for claiming questions and reporting data or result errors |

Top-level guides include [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [REPRODUCING.md](REPRODUCING.md) and [LOCAL_STORAGE.md](LOCAL_STORAGE.md).

## Reuse and licence

Code written for the project is released under the [Unlicense](LICENSES/Unlicense.txt), and our text, data, cards and documentation under [CC0 1.0](LICENSES/CC0-1.0.txt), so both can be reused without asking. Material derived from the 1979 Helsinki edition of the Indus texts is under [CC BY 4.0](LICENSES/CC-BY-4.0.txt) and needs its attribution ([LICENSE](LICENSE)). Third-party material keeps its own terms. Contributions are accepted under the same terms. [REUSE.md](REUSE.md), the [third-party notices](THIRD_PARTY_NOTICES.md) and the [asset review](maintenance/2026-10-11-public-release/ASSET-REVIEW.md) give the details. The manuscripts are drafts written with AI assistance and have not been peer reviewed.

## History

The [research timeline](knowledge/TIMELINE.md) keeps the summaries and links from the earlier README. The [knowledge index](knowledge/INDEX.md) and the [retrospectives](knowledge/retrospectives/README.md) record results, failures and repairs in detail.
